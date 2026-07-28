# ☀️ Morning Dashboards

Grafana folder: **Observability** (sidecar annotation `grafana_folder`).

```mermaid
flowchart TD
  L1[L1 morning-overview]
  L1 --> H[Hosts]
  L1 --> D[DBs]
  L1 --> P[DataPipeline]
  L1 --> A[APIs]
  L1 --> O[Observability]

  H --> HN[morning-host-node]
  H --> K8[morning-k8s]
  D --> DB[morning-db]
  P --> AF[morning-airflow-perf]
  P --> KF[morning-kafka-perf]
  A --> AS[morning-api-svc]
  O --> OD[morning-observability-detail]
```

## 🌳 Hierarchy

```text
L1 morning-overview
├─ 🖥️ Hosts → morning-hosts → morning-host-node / morning-k8s
├─ 🗄️ DBs → morning-dbs → morning-db
├─ 🔀 DataPipeline → airflow-perf / kafka-perf
├─ 🌐 APIs → morning-apis → morning-api-svc
└─ 🔭 Observability → observability-detail
```

## 🔄 Rebuild

```bash
python grafana/scripts/build_morning_hierarchy.py
kubectl apply -f grafana/configmaps/
```

| Piece | Path |
|-------|------|
| 🐍 Generator | `grafana/scripts/morning/` (`constants`, `panels`, `metrics`, `nav`, `io`, `builders/*`) |
| 📋 ConfigMaps | `grafana/configmaps/` |
| 📈 Recording rules | `rules/morning-host-occupancy.yaml` |

> 💡 Use `site_local.example.py` → `site_local.py` for host names (gitignored).
