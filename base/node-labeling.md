# Node Labeling

Use this label to pin observability workloads to dedicated nodes.

```bash
# Replace <node-name> with the target node (do not commit real hostnames).
kubectl label node <node-name> observability=true --overwrite
kubectl get nodes --show-labels | rg observability=true
```

If you want strict pinning, use this in workload specs:

```yaml
nodeSelector:
  observability: "true"
```
