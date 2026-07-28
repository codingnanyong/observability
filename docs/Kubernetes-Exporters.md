# Kubernetes Exporters

Manifests live under `exporters/` and `base/`.

## Base

- `base/namespace.yaml` — observability namespace
- `base/node-labeling.md` — pin workloads with `observability=true`
- `base/networkpolicy-metrics.yaml` — restrict metrics scrape where CNI supports NetworkPolicy

## Exporters

| Path | Purpose |
|------|---------|
| `node-exporter` | Host OS metrics (hostNetwork, port 9101) |
| `cadvisor-docker` | Non-K8s Docker metrics (read-only docker.sock) |
| `kafka-exporter` / `kafka-connect-exporter` | Kafka / Connect health |
| `postgres-exporter` | K8s Postgres + optional Docker Endpoints example |
| `api/` | ServiceMonitors for `api-portal` / `api-core` |
| `airflow-statsd` | Airflow statsd scrape |

Helm starter values: `prometheus/helm-values.yaml` (Prometheus/Grafana as **ClusterIP**).
