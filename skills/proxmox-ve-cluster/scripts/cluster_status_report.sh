#!/usr/bin/env bash
set -euo pipefail

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

if [[ -f "$HOME/.config/openclaw/openclaw.env" ]]; then
  # shellcheck disable=SC1090
  source "$HOME/.config/openclaw/openclaw.env"
fi

: "${OPENCLAW_PROXMOX_HOST:?missing OPENCLAW_PROXMOX_HOST}"
: "${OPENCLAW_PROXMOX_USER:?missing OPENCLAW_PROXMOX_USER}"
: "${OPENCLAW_PROXMOX_TOKEN_NAME:?missing OPENCLAW_PROXMOX_TOKEN_NAME}"
: "${OPENCLAW_PROXMOX_TOKEN_VALUE:?missing OPENCLAW_PROXMOX_TOKEN_VALUE}"
: "${OPENCLAW_PROXMOX_SSH_HOST:?missing OPENCLAW_PROXMOX_SSH_HOST}"
: "${OPENCLAW_PROXMOX_SSH_USER:?missing OPENCLAW_PROXMOX_SSH_USER}"

AUTH_HEADER="Authorization: PVEAPIToken=${OPENCLAW_PROXMOX_USER}!${OPENCLAW_PROXMOX_TOKEN_NAME}=${OPENCLAW_PROXMOX_TOKEN_VALUE}"
BASE_URL="https://${OPENCLAW_PROXMOX_HOST}:8006/api2/json"
SSH_OPTS=(-i "$HOME/.ssh/id_jt_ed25519" -o BatchMode=yes -o ConnectTimeout=10)

fetch() {
  local path="$1"
  curl -ksS -H "$AUTH_HEADER" "$BASE_URL$path"
}

ssh_proxmox() {
  ssh "${SSH_OPTS[@]}" "${OPENCLAW_PROXMOX_SSH_USER}@${OPENCLAW_PROXMOX_SSH_HOST}" "$@"
}

fetch '/cluster/status' > "$TMPDIR/cluster_status.json"
fetch '/cluster/resources' > "$TMPDIR/cluster_resources.json"
fetch '/cluster/ha/resources' > "$TMPDIR/ha_status.json" || echo '{"data":[]}' > "$TMPDIR/ha_status.json"
fetch '/cluster/backup' > "$TMPDIR/backup_jobs.json" || echo '{"data":[]}' > "$TMPDIR/backup_jobs.json"

if ssh_proxmox "sudo pvesh get /cluster/ceph/status --output-format json" > "$TMPDIR/ceph_status.json" 2>/dev/null; then
  :
else
  echo '{}' > "$TMPDIR/ceph_status.json"
fi

python3 - "$TMPDIR/cluster_resources.json" "$TMPDIR/nodes.txt" "$TMPDIR/stopped_guests.json" "$TMPDIR/top_consumers.json" <<'PY1'
import json
import sys

with open(sys.argv[1]) as f:
    resources = json.load(f).get('data', [])

nodes = []
stopped = []
guests = []
for item in resources:
    if item.get('type') == 'node' and item.get('node'):
        nodes.append(item['node'])
    if item.get('type') in ('qemu', 'lxc'):
        guests.append(item)
        if item.get('status') == 'stopped':
            stopped.append({
                'type': item.get('type'),
                'vmid': item.get('vmid'),
                'name': item.get('name'),
                'node': item.get('node'),
            })

with open(sys.argv[2], 'w') as f:
    for node in nodes:
        f.write(node + '\n')

with open(sys.argv[3], 'w') as f:
    json.dump(stopped, f)

def topn(key):
    vals = [x for x in guests if isinstance(x.get(key), (int, float))]
    vals.sort(key=lambda x: x.get(key, 0), reverse=True)
    return [{
        'type': x.get('type'),
        'vmid': x.get('vmid'),
        'name': x.get('name'),
        'node': x.get('node'),
        key: x.get(key),
    } for x in vals[:5]]

with open(sys.argv[4], 'w') as f:
    json.dump({
        'cpu': topn('cpu'),
        'mem': topn('mem'),
        'diskwrite': topn('diskwrite'),
        'netin': topn('netin'),
    }, f)
PY1

python3 - "$TMPDIR/nodes.txt" "$TMPDIR/zfs_status.json" <<'PY2'
import json
import subprocess
import sys
from pathlib import Path

nodes = [line.strip() for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
rows = []
for node in nodes:
    cmd = [
        'ssh', '-i', str(Path.home() / '.ssh' / 'id_jt_ed25519'),
        '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
        f"{__import__('os').environ['OPENCLAW_PROXMOX_SSH_USER']}@{__import__('os').environ['OPENCLAW_PROXMOX_SSH_HOST']}",
        f"sudo pvesh get /nodes/{node}/disks/zfs --output-format json",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        data = json.loads(out)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item['node'] = node
                    rows.append(item)
    except Exception:
        pass
Path(sys.argv[2]).write_text(json.dumps(rows))
PY2

python3 - "$TMPDIR/cluster_status.json" "$TMPDIR/cluster_resources.json" "$TMPDIR/ha_status.json" "$TMPDIR/backup_jobs.json" "$TMPDIR/ceph_status.json" "$TMPDIR/zfs_status.json" "$TMPDIR/stopped_guests.json" "$TMPDIR/top_consumers.json" <<'PY3'
import json
import sys
from collections import defaultdict

with open(sys.argv[1]) as f:
    cluster_status = json.load(f).get('data', [])
with open(sys.argv[2]) as f:
    cluster_resources = json.load(f).get('data', [])
with open(sys.argv[3]) as f:
    ha_status = json.load(f).get('data', [])
with open(sys.argv[4]) as f:
    backup_jobs = json.load(f).get('data', [])
with open(sys.argv[5]) as f:
    raw_ceph = json.load(f)
    if isinstance(raw_ceph, dict) and 'data' in raw_ceph:
        ceph_status = raw_ceph.get('data', {})
    elif isinstance(raw_ceph, dict):
        ceph_status = raw_ceph
    else:
        ceph_status = {}
with open(sys.argv[6]) as f:
    zfs_status = json.load(f)
with open(sys.argv[7]) as f:
    stopped_guests = json.load(f)
with open(sys.argv[8]) as f:
    top_consumers = json.load(f)

cluster = next((x for x in cluster_status if x.get('type') == 'cluster'), {})
nodes = [x for x in cluster_status if x.get('type') == 'node']
node_resources = [x for x in cluster_resources if x.get('type') == 'node']
vms = [x for x in cluster_resources if x.get('type') == 'qemu']
lxcs = [x for x in cluster_resources if x.get('type') == 'lxc']
storages = [x for x in cluster_resources if x.get('type') == 'storage']
networks = [x for x in cluster_resources if x.get('type') == 'network']

vm_running = sum(1 for x in vms if x.get('status') == 'running')
vm_stopped = sum(1 for x in vms if x.get('status') != 'running')
lxc_running = sum(1 for x in lxcs if x.get('status') == 'running')
lxc_stopped = sum(1 for x in lxcs if x.get('status') != 'running')

node_index = {n.get('node'): n for n in node_resources}
vm_by_node = defaultdict(list)
lxc_by_node = defaultdict(list)
storage_by_node = defaultdict(list)
for vm in vms:
    vm_by_node[vm.get('node')].append(vm)
for ct in lxcs:
    lxc_by_node[ct.get('node')].append(ct)
for st in storages:
    storage_by_node[st.get('node')].append(st)

print(f"Cluster: {cluster.get('name', 'unknown')}")
print(f"Quorum: {'yes' if cluster.get('quorate') else 'no'}")
print(f"Nodes: {cluster.get('nodes', len(nodes))}")
print(f"VMs: {len(vms)} total ({vm_running} running / {vm_stopped} stopped)")
print(f"LXCs: {len(lxcs)} total ({lxc_running} running / {lxc_stopped} stopped)")
print(f"Storage entries: {len(storages)}")
print(f"Network entries: {len(networks)}")
print(f"HA resources: {len(ha_status)}")
print(f"Backup jobs: {len(backup_jobs)}")
if ceph_status and isinstance(ceph_status, dict):
    health = ceph_status.get('health', {})
    print(f"Ceph: {health.get('status', 'unknown')}")
else:
    print('Ceph: not available')
print(f"Stopped guests: {len(stopped_guests)}")
print()

all_node_names = [x.get('name') for x in sorted(nodes, key=lambda x: x.get('name', ''))]

print('Node summary:')
for node in sorted(nodes, key=lambda x: x.get('name', '')):
    name = node.get('name')
    nr = node_index.get(name, {})
    status = 'online' if node.get('online') else 'offline'
    cpu = nr.get('cpu')
    mem = nr.get('mem')
    maxmem = nr.get('maxmem')
    disk = nr.get('disk')
    maxdisk = nr.get('maxdisk')
    cpu_txt = f"{cpu * 100:.1f}%" if isinstance(cpu, (int, float)) else 'n/a'
    mem_txt = f"{mem / maxmem * 100:.1f}%" if maxmem else 'n/a'
    disk_txt = f"{disk / maxdisk * 100:.1f}%" if maxdisk else 'n/a'
    print(f"- {name}: {status}, cpu {cpu_txt}, mem {mem_txt}, disk {disk_txt}, VMs {len(vm_by_node[name])}, LXCs {len(lxc_by_node[name])}, storage {len(storage_by_node[name])}")

attention = []
if not cluster.get('quorate'):
    attention.append('- Cluster is not quorate')
for node in nodes:
    if not node.get('online'):
        attention.append(f"- Node offline: {node.get('name')}")
for st in storages:
    if st.get('status') not in ('available', 'active', 'ok'):
        attention.append(f"- Storage {st.get('id')} status {st.get('status')}")
for vm in vms:
    if vm.get('status') not in ('running', 'stopped'):
        attention.append(f"- VM {vm.get('vmid')} ({vm.get('name')}) unexpected status {vm.get('status')}")
for ct in lxcs:
    if ct.get('status') not in ('running', 'stopped'):
        attention.append(f"- LXC {ct.get('vmid')} ({ct.get('name')}) unexpected status {ct.get('status')}")
if ceph_status and isinstance(ceph_status, dict):
    ceph_health = ceph_status.get('health', {}).get('status')
    if ceph_health and ceph_health != 'HEALTH_OK':
        attention.append(f'- Ceph health is {ceph_health}')
for row in zfs_status:
    pool_name = row.get('pool') or row.get('name')
    if row.get('health') != 'ONLINE':
        attention.append(f"- ZFS pool {pool_name} on {row.get('node')} health {row.get('health')}")

if ceph_status and isinstance(ceph_status, dict):
    print()
    print('Ceph summary:')
    health = ceph_status.get('health', {})
    checks = health.get('checks', {}) if isinstance(health, dict) else {}
    print(f"- Health: {health.get('status', 'unknown')}")
    mons = ceph_status.get('monmap', {}).get('mons', [])
    print(f"- MONs: {len(mons)}")
    osdmap = ceph_status.get('osdmap', {}) if isinstance(ceph_status.get('osdmap'), dict) else {}
    print(f"- OSDs: {osdmap.get('num_osds', 'n/a')} total, {osdmap.get('num_up_osds', 'n/a')} up, {osdmap.get('num_in_osds', 'n/a')} in")
    fsmap = ceph_status.get('fsmap', {})
    if isinstance(fsmap, dict) and fsmap.get('filesystems'):
        filesystems = fsmap.get('filesystems', [])
    elif isinstance(fsmap, dict) and fsmap.get('id'):
        filesystems = [fsmap]
    else:
        filesystems = []
    print(f"- CephFS filesystems: {len(filesystems)}")
    if checks:
        print('- Active health checks:')
        for key, val in list(checks.items())[:10]:
            summary = val.get('summary', {}).get('message', key) if isinstance(val, dict) else key
            print(f"  - {summary}")

print()
print('ZFS pools:')
if zfs_status:
    by_node = defaultdict(list)
    for row in zfs_status:
        by_node[row.get('node')].append(row)
    for node_name in all_node_names:
        rows = by_node.get(node_name, [])
        if not rows:
            print(f"- {node_name}: none detected")
            continue
        seen = set()
        for row in rows:
            pool_name = row.get('pool') or row.get('name')
            ident = (row.get('node'), pool_name)
            if ident in seen:
                continue
            seen.add(ident)
            print(f"- {node_name}: {pool_name} health {row.get('health')}, alloc {row.get('alloc')}, free {row.get('free')}, cap {row.get('cap', 'n/a')}, frag {row.get('frag', 'n/a')}")
else:
    for node_name in all_node_names:
        print(f"- {node_name}: unavailable")

if stopped_guests:
    print()
    print('Stopped guests:')
    for guest in stopped_guests:
        print(f"- {guest['type']} {guest['vmid']} ({guest['name']}) on {guest['node']}")

if top_consumers:
    print()
    print('Top consumers:')
    for metric, entries in top_consumers.items():
        print(f"- {metric}:")
        for item in entries:
            print(f"  - {item['type']} {item['vmid']} ({item['name']}) on {item['node']}: {item.get(metric)}")

print()
print('Attention items:')
if attention:
    print('\n'.join(attention))
else:
    print('- No immediate issues detected from cluster-wide read-only telemetry')
PY3
