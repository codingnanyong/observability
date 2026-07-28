# 📊 Enterprise Observability Stack

[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/) [![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/) [![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/) [![Helm](https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=white)](https://helm.sh/) [![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/) [![AlertManager](https://img.shields.io/badge/AlertManager-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/docs/alerting/latest/alertmanager/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Kubernetes-first observability stack: scrape hosts and platforms with Prometheus, visualize with Grafana Morning dashboards, and deploy the control plane via **Helm** (`kube-prometheus-stack`) plus in-cluster exporters/ServiceMonitors.

## 🏗️ **Architecture Overview**

```text
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Targets                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Infrastructure│    Applications │      Services           │
│                 │                 │                         │
│ • Linux Servers │ • Airflow       │ • API / OpenAPI         │
│ • Windows Hosts │ • Databases     │ • Web Applications      │
│ • K8s Nodes     │ • Kafka         │ • Custom Exporters      │
└─────────────────┴─────────────────┴─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Deployment (Kubernetes + Helm)                 │
├─────────────────────────────────────────────────────────────┤
│ • Helm: kube-prometheus-stack (Prometheus / Grafana / AM)   │
│ • Values: prometheus/helm-values.yaml                       │
│ • Manifests: base/, exporters/, grafana/configmaps, rules/  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Exporters Layer                            │
├─────────────────────────────────────────────────────────────┤
│ • node-exporter / cAdvisor   • Kafka / Connect exporters    │
│ • postgres-exporter          • API ServiceMonitors          │
│ • Airflow statsd             • Host / app metrics           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Prometheus Stack                            │
├─────────────────────────────────────────────────────────────┤
│ • Metrics Collection    • Time Series Database              │
│ • Recording / Alert Rules • ServiceMonitor discovery        │
│ • AlertManager          • ClusterIP (port-forward / Ingress)│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Grafana Dashboards                         │
├─────────────────────────────────────────────────────────────┤
│ • Morning L1–L3 hierarchy   • Hosts / DBs / Pipeline / APIs │
│ • Sidecar ConfigMaps        • Observability folder          │
└─────────────────────────────────────────────────────────────┘
```

## 📁 **Project Structure**

```text
observability/
├── base/                         # Namespace, NetworkPolicy, node labeling
├── exporters/                    # K8s DaemonSets / Deployments / ServiceMonitors
├── grafana/
│   ├── configmaps/               # Morning dashboard ConfigMaps
│   ├── dashboards/               # JSON sources
│   └── scripts/morning/          # Dashboard generator
├── prometheus/
│   └── helm-values.yaml          # kube-prometheus-stack Helm values
├── rules/                        # Prometheus recording rules
└── docs/                         # Project docs (Wiki source)
```

## ⚡ **Key Features**

- **Kubernetes + Helm**: control plane via `kube-prometheus-stack`
- **In-cluster exporters**: node, cAdvisor, Kafka, Postgres, API, Airflow
- **Morning dashboards**: hierarchical Grafana views with ConfigMap sidecar
- **Secure by default**: ClusterIP services, templated secrets, no committed inventory IPs

## 🚀 **Quick Start**

```bash
# 1) Label nodes and apply base + exporters
kubectl label node <node-name> observability=true --overwrite
kubectl apply -f base/
kubectl apply -f exporters/

# 2) Install / upgrade kube-prometheus-stack
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n observability --create-namespace \
  -f prometheus/helm-values.yaml

# 3) Dashboards + recording rules
kubectl apply -f grafana/configmaps/
kubectl apply -f rules/

# 4) Access Grafana (ClusterIP)
kubectl -n observability port-forward svc/kube-prometheus-stack-grafana 3000:80
```

Optional site overrides for Morning dashboards:

```bash
cp grafana/scripts/morning/site_local.example.py grafana/scripts/morning/site_local.py
python grafana/scripts/build_morning_hierarchy.py
kubectl apply -f grafana/configmaps/
```

## 📚 **Documentation**

| Component | Documentation |
| --------- | ------------- |
| **[Docs home](./docs/README.md)** | Getting started, architecture, security |
| **[Grafana dashboards](./grafana/dashboards/README.md)** | Morning hierarchy & rebuild |
| **[Wiki](https://github.com/codingnanyong/observability/wiki)** | Same content as `docs/` |

## 🛡️ **Security Considerations**

- Keep Prometheus/Grafana as **ClusterIP**; use port-forward, VPN, or authenticated Ingress
- Do not commit real IPs, `site_local.py`, or secret env files
- Prefer `sslmode=require` for Postgres exporter DSNs

## 📄 **License**

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
