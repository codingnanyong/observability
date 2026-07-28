# 🏗️ Architecture

End-to-end flow from workloads to dashboards.

```mermaid
flowchart TB
  subgraph Targets["🎯 Monitoring Targets"]
    H[Hosts / K8s nodes]
    APP[Airflow · Kafka · DBs]
    API[api-portal · api-core]
  end

  subgraph Deploy["☸️ Deployment"]
    BASE[base/]
    EXP[exporters/]
    HELM["⎈ helm-values.yaml<br/>kube-prometheus-stack"]
    CM[grafana/configmaps]
    RULES[rules/]
  end

  subgraph Plane["🔥 Control plane"]
    PROM[Prometheus]
    AM[Alertmanager]
    GRAF[Grafana]
  end

  Targets --> EXP
  BASE --> EXP
  HELM --> Plane
  EXP -->|ServiceMonitor| PROM
  CM --> GRAF
  RULES --> PROM
  PROM --> GRAF
  PROM --> AM
```

## 📦 Layers

| # | Layer | Role |
|---|--------|------|
| 1 | 🎯 **Targets** | Hosts, platforms (Airflow/DB/Kafka), APIs |
| 2 | 📡 **Exporters** | DaemonSets / Deployments + ServiceMonitors (`exporters/`) |
| 3 | 🔥 **Prometheus** | Helm chart via `prometheus/helm-values.yaml` |
| 4 | 📊 **Grafana** | Morning hierarchy via ConfigMap sidecar |

## 🗺️ Kubernetes layout (generic names)

```mermaid
flowchart LR
  OBS[observability]
  K[kafka]
  PG[postgres]
  AF[airflow]
  AP[api-portal]
  AC[api-core]
  OBS --- K
  OBS --- PG
  OBS --- AF
  OBS --- AP
  OBS --- AC
```

| Area | Namespace / name |
|------|------------------|
| 🔭 Observability stack | `observability` |
| 📨 Kafka | `kafka` |
| 🗄️ Postgres | `postgres` |
| 🌬️ Airflow | `airflow` |
| 🌐 APIs | `api-portal`, `api-core` |

Host placeholders in dashboards: `worker-01`, `worker-02` (override via `site_local.py`).
