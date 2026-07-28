# Morning Dashboards

Folder: **Observability** (Grafana sidecar annotation `grafana_folder`).

```
L1 morning-overview
├─ Hosts → morning-hosts → morning-host-node / morning-k8s
├─ DBs → morning-dbs → morning-db
├─ DataPipeline → … → airflow-perf / kafka-perf
├─ APIs → morning-apis → morning-api-svc
└─ Observability → … → observability-detail
```

## Rebuild

```bash
python grafana/scripts/build_morning_hierarchy.py
kubectl apply -f grafana/configmaps/
```

Package: `grafana/scripts/morning/` (`constants`, `panels`, `metrics`, `nav`, `io`, `builders/*`).

Recording rules: `rules/morning-host-occupancy.yaml`.
