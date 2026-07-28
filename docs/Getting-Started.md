# Getting Started

## Prerequisites

- Docker / Kubernetes access as needed
- Prometheus + Grafana (kube-prometheus-stack or standalone)
- Python 3.12+ if regenerating Morning dashboards

## 1. Clone

```bash
git clone https://github.com/codingnanyong/observability.git
cd observability
```

## 2. Configure Prometheus targets (local only)

Committed files are templates. Do **not** commit real IPs.

```bash
cp prometheus/targets/infrastructure/linux.template.json \
   prometheus/targets/infrastructure/linux.json
# Edit host-*.example → real hosts
```

Repeat for other `*.template.json` files you need. Local `*.json` is gitignored.

## 3. Optional site overrides for Morning dashboards

```bash
cp grafana/scripts/morning/site_local.example.py \
   grafana/scripts/morning/site_local.py
# Set HOST_NODES / API_DOCS_MARKDOWN
python grafana/scripts/build_morning_hierarchy.py
kubectl apply -f grafana/configmaps/
```

## 4. Kubernetes exporters

```bash
kubectl apply -f base/
kubectl apply -f exporters/
# Helm values: prometheus/helm-values.yaml
```

Access Grafana via ClusterIP port-forward (see `grafana/dashboards/README.md`).
