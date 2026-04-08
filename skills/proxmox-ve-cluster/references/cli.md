# Proxmox VE CLI Reference

## pvesh — Cluster & Node Management

```bash
# Cluster tree overview
pvesh ls /cluster/

# Node list with status
pvesh ls /nodes/

# Single node info
pvesh ls /nodes/<node>
pvesh get /nodes/<node>/status

# Cluster resources (CPU, memory, disk across all nodes)
pvesh ls /cluster/resources

# Cluster HA status
pvesh ls /cluster/ha
pvesh get /cluster/ha

# Quorum and cluster membership
pvesh ls /cluster/status
pvesh get /cluster/status

# Cluster log
pvesh ls /cluster/log

# All VMs and LXCs on a specific node
pvesh ls /nodes/<node>/qemu
pvesh ls /nodes/<node>/lxc

# Storage on a node
pvesh ls /nodes/<node>/storage

# Network interfaces on a node
pvesh ls /nodes/<node>/network

# Cluster firewall rules
pvesh ls /cluster/firewall/

# Pending migrations
pvesh ls /cluster/migrate

# Replication jobs
pvesh ls /cluster/replication
```

## qm — QEMU/KVM VM Management

```bash
# List all VMs on current node
qm list

# Start/stop a VM
qm start <vmid>
qm stop <vmid>        # graceful stop (may take time)
qm shutdown <vmid>    # ACPI shutdown request
qm reboot <vmid>

# VM status
qm status <vmid>
qm monitor <vmid>     # enter QEMU monitor console (use SSH PTY)

# VM config (read-only view)
qm config <vmid>

# VM config editor (interactive)
qm set <vmid> --<option> <value>

# Create snapshot
qm snapshot <vmid> <snapname>
qm snapshot-delete <vmid> <snapname>   # DESTRUCTIVE — requires approval
qm listsnapshot <vmid>

# Clone a VM
qm clone <vmid> <newvmid> --name <newname>

# Move a VM to another storage
qm move-disk <vmid> <disk> --target-storage <storage>

# Migrate a VM
qm migrate <vmid> <target-node> --online

# Reset a VM (force reboot)
qm reset <vmid>

# Remove a VM (DESTRUCTIVE — requires approval)
qm destroy <vmid> --purge

# Create a new VM from ISO
qm create <vmid> --name <name> --cdrom <iso> --net0 <model>=<bridge> --cores <n> --memory <mb>
```

## pct — LXC Container Management

```bash
# List all LXC on current node
pct list

# Start/stop LXC
pct start <vmid>
pct stop <vmid>
pct shutdown <vmid>

# Enter LXC console (use SSH PTY)
pct enter <vmid>

# LXC status
pct status <vmid>
pct monitor <vmid>

# LXC config
pct config <vmid>
pct set <vmid> --<option> <value>

# Snapshot LXC
pct snapshot <vmid> <snapname>
pct listsnapshot <vmid>
pct snapshot-delete <vmid> <spapname>   # DESTRUCTIVE — requires approval

# Clone LXC
pct clone <vmid> <newvmid> --name <newname>

# Remove LXC (DESTRUCTIVE — requires approval)
pct destroy <vmid>

# Create LXC
pct create <vmid> <template> --hostname <name> --memory <mb> --cores <n> --net0 <model>=<bridge>
```

## pvesm — Storage Management

```bash
# All storage status
pvesm status

# List storage content
pvesm list <storage-id>

# Storage config
pvesh ls /storage
pveum storage list

# Add storage (DESTRUCTIVE — requires approval for disk operations)
pvesm add <type> <storage-id> --<option> <value>

# Remove storage content
pvesm remove <storage-id>:<path>    # DESTRUCTIVE — requires approval

# Resize a disk
pvesm resize <vmid>/<disk> <size>

# Free a storage volume
pvesm free <volume>    # DESTRUCTIVE — requires approval
```

## pveum — User & Permission Management

```bash
# User list
pveum user list

# User details
pveum user list <userid>

# Add user (safe)
pveum user add <userid> --email <email>

# Modify user
pveum user modify <userid> --enable 0

# Add API token (safe)
pveum token add <userid>_<tokenid> --privsep 0

# Delete user or token (DESTRUCTIVE — requires approval)
pveum user delete <userid>
pveum token delete <userid>/<tokenid>

# Permission list
pveum permissions list

# ACLs
pveum acl list
```

## pvebackup — Backup Jobs

```bash
# List backup jobs
pvesh ls /cluster/backup

# View a specific job
pvesh get /cluster/backup/<job-id>

# Start a backup job
pvesm backup <job-id> --node <node>

# Start a one-shot backup
qm backup <vmid> --storage <storage> --mode <snapshot|suspend|stop>
```

## Common Patterns

```bash
# Get a specific VM's full status including node
qm status <vmid> --verbose

# Get node resource usage
pvesh get /nodes/<node>/status --benchmark

# Check cluster quorum
pvesh get /cluster/status

# List all VMs across cluster with their node
ssh proxmox "qm list" 2>/dev/null || ssh root@proxmox "qm list"

# Get HA resource configuration
pvesh ls /cluster/ha/resources

# Get fencing status
pvesh ls /cluster/fencing

# Check Corosync ring status
pvesh get /cluster/corosync

# Get replication status
pvesh ls /cluster/replication

# Pending guest config changes (need reboot)
pvesh ls /cluster/guestspending
```

## Node-Remote Operations

When the target VM is on a remote node, commands can be run remotely via SSH:

```bash
ssh root@proxmox "pvesh ls /nodes/<target-node>/qemu"
ssh root@proxmox "qm start <vmid> --node <target-node>"
```

Or set the environment:
```bash
export PVENODE=<node>
qm start <vmid>
```
