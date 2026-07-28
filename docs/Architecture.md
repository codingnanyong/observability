# Architecture

High-level layers:

1. **Targets** — infrastructure hosts, platforms (Airflow/DB), services
2. **Exporters** — node, Windows, blackbox, DB, Kafka, custom
3. **Prometheus** — scrape, TSDB, rules, Alertmanager
4. **Grafana** — Morning hierarchy + Kubernetes folders

## Kubernetes layout (generic names)

| Area | Namespace / name |
|------|------------------|
| Observability stack | `observability` |
| Kafka | `kafka` |
| Postgres | `postgres` |
| Airflow | `airflow` |
| APIs | `api-portal`, `api-core` |

Host placeholders in dashboards: `worker-01`, `worker-02` (override via `site_local.py`).
