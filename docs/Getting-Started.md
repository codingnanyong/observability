# Getting Started

## Prerequisites

- Kubernetes cluster + `kubectl`
- Helm 3
- Python 3.12+ (only if regenerating Morning dashboards)

## 1. Clone

```bash
git clone https://github.com/codingnanyong/observability.git
cd observability
```

## 2. Base + exporters

```bash
kubectl label node <node-name> observability=true --overwrite
kubectl apply -f base/
kubectl apply -f exporters/
```

## 3. kube-prometheus-stack (Helm)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n observability --create-namespace \
  -f prometheus/helm-values.yaml
```

## 4. Dashboards + rules

```bash
kubectl apply -f grafana/configmaps/
kubectl apply -f rules/
```

## 5. Access Grafana

```bash
kubectl -n observability port-forward svc/kube-prometheus-stack-grafana 3000:80
# http://127.0.0.1:3000/d/morning-overview
```

Optional Morning site overrides:

```bash
cp grafana/scripts/morning/site_local.example.py \
   grafana/scripts/morning/site_local.py
python grafana/scripts/build_morning_hierarchy.py
kubectl apply -f grafana/configmaps/
```
