# Prometheus Targets

This directory contains target configuration templates for Prometheus monitoring.

## Security Notice

**Do not commit real IP addresses or production hostnames.**

Committed files use `*.template.json` with `host-*.example` placeholders.
Local `*.json` copies are gitignored.

## Setup

```bash
# Example
cp infrastructure/linux.template.json infrastructure/linux.json
# Edit linux.json — replace host-*.example with real hosts
```

Placeholders:

| Label / field | Template meaning |
|---------------|------------------|
| `host-*.example` | Target host (never a real IP in git) |
| `corporation` | `site-a` … `site-d` (generic sites) |
| `server` | Role name (`warehouse-01`, `collector-01`, …) |

## Directory Structure

```text
targets/
├── infrastructure/      # OS-level exporters
├── platform/            # Database / Airflow exporters
├── service/             # Application services
└── observability/       # Monitoring tools
```
