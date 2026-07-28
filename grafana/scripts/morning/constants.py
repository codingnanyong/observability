"""Shared constants for Morning dashboard generation."""
from __future__ import annotations

from pathlib import Path

# scripts/morning/constants.py → grafana/{dashboards,configmaps}
_GRAFANA = Path(__file__).resolve().parents[2]
OUT = _GRAFANA / "dashboards"
CM = _GRAFANA / "configmaps"
DS = {"type": "prometheus", "uid": "prometheus"}

SOFT_CPU, HARD_CPU = 80, 90
SOFT_CTM, HARD_CTM = 150_000, 500_000
SOFT_CONN, HARD_CONN = 70, 85
# idle in transaction: 30s was too noisy (JDBC blips); Soft 2m / Hard 5m
SOFT_IDLE_XACT, HARD_IDLE_XACT = 120, 300
INTRO_H = 4

# One Grafana folder per dashboard *service* (not per hierarchy level).
FOLDER_OBSERVABILITY = "Observability"
# Alias used by dash()/write defaults.
FOLDER_DEFAULT = FOLDER_OBSERVABILITY

MORNING_NAV_TAG = "morning-nav"

DB_CLUSTERS = [
    {"id": "pg-primary", "title": "pg-primary (K8s)", "job": "postgres-exporter-k8s", "runtime": "k8s"},
    {"id": "pg-legacy", "title": "pg-legacy (legacy)", "job": "postgres-exporter-docker", "runtime": "docker"},
]
PG_JOBS = "|".join(c["job"] for c in DB_CLUSTERS)

# Site-specific hostnames / external doc links live in site_local.py (gitignored).
# Defaults are placeholders so committed dashboards do not leak real inventory.
try:
    from .site_local import API_DOCS_MARKDOWN, HOST_NODES  # type: ignore
except ImportError:
    HOST_NODES = ["worker-01", "worker-02"]
    API_DOCS_MARKDOWN = ""
