---
name: proxmox-ve-cluster
description: "Fully operational Proxmox VE 9 cluster management. Use when managing or troubleshooting the Proxmox cluster, nodes, VMs, LXC containers, storage, networking, HA, or cluster-wide operations. Triggers on: Proxmox, cluster, VM, LXC, storage, networking, HA, quorum, fencing, replication, backup, PVE, pvesh, qm, pct, pveum."
---

# proxmox-ve-cluster

## Overview

Provides fully operational management of a Proxmox VE 9 cluster. Executes read operations and safe mutations directly. Destructive operations require explicit user approval before execution.

## Proxmox Host Access

Prefer Proxmox VE API token authentication using these environment variables:
- `OPENCLAW_PROXMOX_HOST`
- `OPENCLAW_PROXMOX_USER`
- `OPENCLAW_PROXMOX_TOKEN_NAME`
- `OPENCLAW_PROXMOX_TOKEN_VALUE`

Construct the authorization header as:
```text
Authorization: PVEAPIToken=<user>!<token-name>=<token-value>
```

Use the API first for cluster, node, VM, LXC, storage, HA, and user-management operations. Use SSH fallback for host-local CLI commands, console access, shell diagnostics, or when API coverage is awkward.

For SSH fallback, use the host alias defined in `TOOLS.md` (`### Proxmox`) or these environment variables:
- `OPENCLAW_PROXMOX_SSH_HOST`
- `OPENCLAW_PROXMOX_SSH_USER`

If an SSH identity file is recorded in `TOOLS.md`, use it. On this system the working path is:
- `~/.ssh/id_jt_ed25519`

For Proxmox CLI fallback, invoke commands through restricted sudo:
```bash
ssh -i ~/.ssh/id_jt_ed25519 ${OPENCLAW_PROXMOX_SSH_USER}@${OPENCLAW_PROXMOX_SSH_HOST} "sudo <proxmox-command>"
```

Do not assume direct non-root execution of `pvesh`, `qm`, `pct`, `pvesm`, or `pveum` will work correctly.

If neither host metadata nor environment variables are present, default to connecting to `proxmox` as `root` via SSH on port 22 using key-based auth.

## Approval Gate — Destructive Actions

The following operations are **destructive** and MUST NOT proceed without explicit user approval:

- Deleting, purging, or wiping a VM or LXC
- Formatting, removing, or resizing storage
- Stopping, restarting, or fencing a node
- Cluster leave/join operations
- Snapshot deletion (only snapshots, not creation)
- Stopping or restarting a running VM/LXC (graceful stop is informational only)
- Any `pveum` user or permission modification
- Storage content deletion (`pvesm remove`, `pvesm free`)
- HA resource remove/fence operations

When a destructive action is needed, present:
1. Exact command that will be run
2. What it affects
3. "Confirm with: /approve <description>" instruction

## Core Workflow

### 1. Determine target node

If the user does not specify a node and the cluster has more than one node, use `pvesh` to find the target VM's node before running node-specific commands.

### 2. Read operations — execute directly

Prefer Proxmox API reads without approval. Examples:
- `GET /cluster/resources` — cluster resource overview
- `GET /nodes/<node>/qemu` — VMs on a node
- `GET /cluster/ha/status` or `GET /cluster/ha/resources` — HA status
- `GET /cluster/status` — quorum and cluster membership
- `GET /access/users` — user list
- `GET /cluster/resources?type=storage` — storage overview

If API access is unavailable or insufficient, fall back to `pvesh`, `qm`, `pct`, `pveum`, or `pvesm` over SSH via restricted sudo.

### 3. Safe mutations — execute directly

Prefer Proxmox API writes for safe operational changes. The following are considered safe and may execute without approval:
- Starting a VM or LXC
- Creating snapshots
- Cluster health checks
- Viewing VM/container config
- Viewing storage content
- Viewing HA resource status

Use SSH fallback where API invocation is impractical, and invoke privileged Proxmox CLI through `sudo`.

Treat node reboot as approval-gated unless the user explicitly asks for it in the current turn.

### 4. Destructive mutations — gate behind approval

Follow the approval gate procedure above.

### 5. VM Console Access

To access a VM's console (`qm monitor`, `pct enter`), use SSH with a PTY shell to the Proxmox host and run the monitor/console command. Set `pty: true` on the exec call.

## Cluster Status & Reporting

When the user asks for a cluster health check, status audit, daily report, infrastructure summary, or a comprehensive Proxmox overview, run the bundled script:

```bash
bash skills/proxmox-ve-cluster/scripts/cluster_status_report.sh
```

Use this report for:
- quorum and cluster membership
- node online/offline state
- per-node resource summary
- VM and LXC counts and runtime state
- stopped guest listing
- storage inventory and abnormal storage states
- Ceph health specifics
- ZFS pool health
- HA resource count
- backup job count
- per-node or cluster-wide top consumers
- attention items requiring investigation

Prefer this script over ad-hoc one-off commands when the user wants a broad operational summary. It is read-only and API-first.

## Command Reference

- **Cluster-wide**: `pvesh ls /cluster/` — cluster tree
- **Nodes**: `pvesh ls /nodes/` — all nodes and their status
- **VMs**: `qm list` — all QEMU VMs cluster-wide
- **LXC**: `pct list` — all LXC containers cluster-wide
- **Storage**: `pvesm status` — all storage repositories and usage
- **HA**: `pvesh ls /cluster/ha` — HA resource status
- **API token**: `pveum token list` — current tokens
- **Backup jobs**: `pvesh ls /cluster/backup` — configured backup jobs

For detailed CLI flags and API usage, see `references/cli.md` and `references/api.md`.

## Execution Pattern

### API-first examples

```bash
curl -ksS -H "Authorization: PVEAPIToken=${OPENCLAW_PROXMOX_USER}!${OPENCLAW_PROXMOX_TOKEN_NAME}=${OPENCLAW_PROXMOX_TOKEN_VALUE}" \
  "https://${OPENCLAW_PROXMOX_HOST}:8006/api2/json/cluster/resources"
```

```bash
curl -ksS -X POST -H "Authorization: PVEAPIToken=${OPENCLAW_PROXMOX_USER}!${OPENCLAW_PROXMOX_TOKEN_NAME}=${OPENCLAW_PROXMOX_TOKEN_VALUE}" \
  "https://${OPENCLAW_PROXMOX_HOST}:8006/api2/json/nodes/<node>/qemu/<vmid>/status/start"
```

### SSH fallback examples

```bash
ssh -i ~/.ssh/id_jt_ed25519 ${OPENCLAW_PROXMOX_SSH_USER}@${OPENCLAW_PROXMOX_SSH_HOST} "sudo pvesh ls /cluster/resources"
```

```bash
ssh -t -i ~/.ssh/id_jt_ed25519 ${OPENCLAW_PROXMOX_SSH_USER}@${OPENCLAW_PROXMOX_SSH_HOST} "sudo qm monitor <vmid>"
```

## Scripts

### `scripts/cluster_status_report.sh`

Generate a comprehensive read-only cluster summary using Proxmox API token auth plus SSH+sudo fallback where needed for host-local storage health. The script aggregates cluster status, resources, HA objects, backup job counts, Ceph health, ZFS pool health, stopped guests, and top consumers, then emits a concise human-readable report.

If the user wants deeper investigation after the summary, follow up with targeted API reads or SSH+sudo fallback commands.

## Response Style

- Confirm success or report failure clearly
- Include relevant output (formatted, truncated if long)
- Flag if a node is offline or a VM is in an unexpected state
- Suggest next logical step when applicable
