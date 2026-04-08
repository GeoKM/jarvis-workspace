# Proxmox VE API Reference

## Base URL

```
https://<proxmox-host>:8006/api2/json/
```

## Authentication

### Ticket (Cookie-Based)
```bash
curl -k -F "username=<user>@pam" -F "password=<pass>" \
  https://<proxmox>:8006/api2/json/access/ticket
```
Returns: `{ "data": { "ticket": "...", "token": "..." } }`

### API Token (Preferred)
```bash
curl -k -H "Authorization: PVEAPIToken=<user>!<tokenid>=<secret>" \
  https://<proxmox>:8006/api2/json/cluster/resources
```

Tokens are created via `pveum token add`.

## Common Endpoints

### Cluster

```
GET /cluster/status              # Cluster quorum and node membership
GET /cluster/resources           # CPU, memory, disk usage all nodes
GET /cluster/log                 # Cluster log (last 50 entries)
GET /cluster/cluster-options     # Cluster-wide options
GET /cluster/ha/status           # HA resource status
```

### Nodes

```
GET /nodes/{node}/status        # Node status (uptime, CPU, memory, disk)
GET /nodes/{node}/qemu           # All QEMU VMs on node
GET /nodes/{node}/lxc            # All LXC containers on node
GET /nodes/{node}/network        # Network interfaces
GET /nodes/{node}/storage        # Storage attached to node
```

### VMs (QEMU/KVM)

```
GET  /cluster/resources?type=qemu        # All QEMU VMs across cluster
POST /nodes/{node}/qemu                  # Create VM
GET  /nodes/{node}/qemu/{vmid}/status   # VM status
POST /nodes/{node}/qemu/{vmid}/status/start
POST /nodes/{node}/qemu/{vmid}/status/stop
POST /nodes/{node}/qemu/{vmid}/status/shutdown
GET  /nodes/{node}/qemu/{vmid}/config    # VM config
PUT  /nodes/{node}/qemu/{vmid}/config    # Update VM config
POST /nodes/{node}/qemu/{vmid}/snapshot  # Create snapshot
DELETE /nodes/{node}/qemu/{vmid}/snapshot/{snapname}  # Delete snapshot (DESTRUCTIVE)
POST /nodes/{node}/qemu/{vmid}/clone     # Clone VM
```

### LXC

```
GET  /cluster/resources?type=lxc
POST /nodes/{node}/lxc                   # Create LXC
GET  /nodes/{node}/lxc/{vmid}/status
POST /nodes/{node}/lxc/{vmid}/status/start
POST /nodes/{node}/lxc/{vmid}/status/stop
GET  /nodes/{node}/lxc/{vmid}/config
PUT  /nodes/{node}/lxc/{vmid}/config
```

### Storage

```
GET  /cluster/resources?type=storage     # All storage
GET  /nodes/{node}/storage               # Storage on specific node
GET  /storage                            # Storage config
POST /storage                            # Add storage
PUT  /storage/{storage-id}               # Update storage
DELETE /storage/{storage-id}            # Remove storage (DESTRUCTIVE)
```

### Users & Permissions

```
GET  /access/users
POST /access/users
DELETE /access/users/{userid}            # Delete user (DESTRUCTIVE)
GET  /access/acl
PUT  /access/acl                        # Modify ACLs
GET  /access/tokens
POST /access/tokens
DELETE /access/tokens/{userid}/{tokenid}
```

### Backup

```
GET  /cluster/backup
POST /cluster/backup                     # Create backup job
DELETE /cluster/backup/{id}             # Remove backup job
POST /nodes/{node}/qemu/{vmid}/backup   # Trigger one-shot backup
```

### HA

```
GET  /cluster/ha/resources              # HA resource status
POST /cluster/ha/resources             # Add HA resource
DELETE /cluster/ha/resources/{sid}    # Remove HA resource (DESTRUCTIVE)
```

## JSON Response Envelope

All responses are wrapped:
```json
{
  "data": { ... }       // success
  "errors": { ... }     // validation errors
}
```

## Task Tracking

Create operations return a task ID:
```json
{
  "data": {
    "upid": "UPID:proxmox:...",
    "node": "pve1",
    "task_id": "..."
  }
}
```

Poll task:
```
GET /nodes/{node}/tasks/{upid}/status
```

## Error Responses

```json
{
  "errors": {
    "parameter_name": ["error message"]
  },
  "message": "explanation"
}
```

HTTP status codes: 200 OK, 400 Bad Param, 401 Unauth, 403 Forbidden, 500 Server Error

## curl Examples

```bash
# Cluster resources
curl -k -H "Authorization: PVEAPIToken=$PVE_TOKEN" \
  https://proxmox:8006/api2/json/cluster/resources | jq .

# All VMs with status
curl -k -H "Authorization: PVEAPIToken=$PVE_TOKEN" \
  "https://proxmox:8006/api2/json/cluster/resources?type=qemu" | jq '.data[] | {vmid, name, status, node}'

# Start a VM
curl -k -X POST -H "Authorization: PVEAPIToken=$PVE_TOKEN" \
  https://proxmox:8006/api2/json/nodes/pve1/qemu/100/status/start

# Node disk usage
curl -k -H "Authorization: PVEAPIToken=$PVE_TOKEN" \
  https://proxmox:8006/api2/json/nodes/pve1/status | jq '.data["disk","cpu","memory"]'
```
