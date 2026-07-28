# Security Hygiene

## Do not commit

- Real IPs / production hostnames
- `grafana/scripts/morning/site_local.py`
- `exporters/postgres-exporter/secret.local.env`
- `exporters/postgres-exporter/servicemonitor-docker.yaml` (copy from `.example`)

## Safe patterns

- Templates: `secret.example.env`, `site_local.example.py`
- Postgres example DSN uses `sslmode=require` and `CHANGE_ME`
- Prometheus/Grafana exposed as ClusterIP; use port-forward or authenticated Ingress
- Helm entrypoint: `prometheus/helm-values.yaml` only (no committed file_sd inventories)

## Residual ops risk

cAdvisor still needs elevated privileges + Docker socket for host Docker metrics — firewall host ports and pin to labeled nodes.
