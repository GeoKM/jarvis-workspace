# Proxmox Cluster Reporting Guide

## Purpose

Use the cluster status report when the user asks for a broad operational view rather than a single command result.

## Report Structure

1. Cluster identity
2. Quorum status
3. Node count and node health
4. VM/LXC totals and running/stopped split
5. Storage and network inventory counts
6. Ceph health specifics
7. ZFS pool health
8. HA resource count
9. Backup job count
10. Stopped guest list
11. Top consumers
12. Attention items

## Attention Heuristics

Flag these clearly:
- cluster not quorate
- any offline node
- storage not in `available`, `active`, or `ok`
- Ceph not `HEALTH_OK`
- ZFS pool health other than `ONLINE`
- guest status other than `running` or `stopped`

## Follow-up Workflow

After presenting the summary, offer one of:
- drill into a specific node
- list stopped guests
- show storage utilisation by node
- inspect Ceph health details
- inspect ZFS pools on a node
- inspect HA resources
- inspect backup jobs
- investigate top consumers

## Style

Keep the report concise and operational:
- lead with the overall state
- then give node summary
- then attention items
- only include raw JSON when explicitly asked
