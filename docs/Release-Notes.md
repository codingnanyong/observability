# 🏷️ Release Notes

## v1.0.0

First tagged release (`develop` → `main` via #5).

```mermaid
flowchart LR
  F[✨ Features] --> S[🔒 Security]
  S --> D[📚 Docs]
  F --- F1[K8s + Helm + Morning]
  S --- S1[No IPs · secrets local]
  D --- D1[README · Wiki]
```

### ✨ Features
- ☸️ K8s exporters / base, Morning Grafana hierarchy + generator, host occupancy rules

### 🔒 Security
- Inventory scrub → generic placeholders; secret/local overlays gitignored

### 📚 Docs
- README badges; Wiki + `docs/`

➡️ [GitHub Release v1.0.0](https://github.com/codingnanyong/observability/releases/tag/v1.0.0)
