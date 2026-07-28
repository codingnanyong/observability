# Security Hygiene

## Do not commit

- Real IPs / production hostnames
- `prometheus/targets/**/*.json` (use templates)
- `grafana/scripts/morning/site_local.py`
- `exporters/postgres-exporter/secret.local.env`
- `exporters/postgres-exporter/servicemonitor-docker.yaml` (copy from `.example`)

## Safe patterns

- Templates: `*.template.json`, `secret.example.env`, `site_local.example.py`
- Postgres example DSN uses `sslmode=require` and `CHANGE_ME`
- Prometheus/Grafana exposed as ClusterIP; use port-forward or authenticated Ingress

## Residual ops risk

cAdvisor still needs elevated privileges + Docker socket for host Docker metrics — firewall host ports and pin to labeled nodes.
