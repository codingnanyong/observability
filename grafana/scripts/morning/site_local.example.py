"""Site-specific Morning dashboard values (EXAMPLE — copy to site_local.py).

  cp grafana/scripts/morning/site_local.example.py \
     grafana/scripts/morning/site_local.py

site_local.py is gitignored. Do not commit real hostnames or internal IPs.
"""
from __future__ import annotations

# Kubernetes node names used by host occupancy dashboards.
HOST_NODES: list[str] = ["worker-01", "worker-02"]

# Optional markdown fragment for API docs links (leave empty to omit).
# Prefer internal DNS / Ingress paths — never hardcode RFC1918 IPs here in git.
# Example (local only):
#   API_DOCS_MARKDOWN = (
#       "[portal docs](https://api-portal.example.internal/docs) · "
#       "[core docs](https://api-core.example.internal/api/docs)"
#   )
API_DOCS_MARKDOWN: str = ""
