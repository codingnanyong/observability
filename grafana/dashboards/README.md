# Grafana Dashboards

Provisioned via ConfigMaps (`grafana_dashboard: "1"`) + sidecar.

## Folders (one per dashboard service)

| Folder | Source | Dashboards |
|--------|--------|------------|
| **Observability** | Morning ConfigMaps (`grafana_folder` annotation) | All `morning-*` (overview → L2/L3) |
| **Kubernetes** | kube-prometheus-stack chart CMs + `grafana_folder=Kubernetes` | alertmanager, apiserver, k8s-resources-*, prometheus, grafana-overview, … |

Hierarchy (click-through) lives **inside** Observability; folder ≠ L1/L2 level.

Rebuild / ConfigMaps:

```bash
python3 grafana/scripts/build_morning_hierarchy.py
kubectl apply -f grafana/configmaps/
```

Generator package: `grafana/scripts/morning/` (`constants`, `panels`, `metrics`, `nav`, `io`, `builders/*`).

## Hierarchy (Observability)

```
L1 Morning Status (morning-overview)
├─ Hosts → morning-hosts → morning-host-node / morning-k8s
├─ DBs → morning-dbs → morning-db
├─ DataPipeline → morning-datapipeline → morning-airflow-perf | morning-kafka-perf
├─ APIs → morning-apis → morning-api-svc
└─ Observability → morning-observability → morning-observability-detail
```

Access (ClusterIP — do not publish NodePort on untrusted networks):

```bash
kubectl -n observability port-forward svc/kube-prometheus-stack-grafana 3000:80
# open http://127.0.0.1:3000/d/morning-overview
```

Override host/API inventory locally via `site_local.py` (gitignored); see `site_local.example.py`.

## Helm (folder support)

`prometheus/helm-values.yaml`:

```yaml
grafana.sidecar.dashboards.folderAnnotation: grafana_folder
grafana.sidecar.dashboards.provider.foldersFromFilesStructure: true
```

After helm recreate of chart dashboard ConfigMaps, re-annotate samples:

```bash
kubectl -n observability get cm -l grafana_dashboard=1 -o name | grep -v morning | \
  xargs -r kubectl -n observability annotate --overwrite grafana_folder="Kubernetes"
```

## PostgreSQL community templates (manual import)

Import into a dedicated folder if you treat them as their own service (e.g. **PostgreSQL**):

- PostgreSQL Database (ID: 9628)
- PostgreSQL Overview (ID: 455)
