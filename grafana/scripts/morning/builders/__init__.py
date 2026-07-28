"""Assemble all Morning dashboards."""
from __future__ import annotations

from ..constants import FOLDER_OBSERVABILITY
from ..io import write_static
from .apis import build_apis
from .dbs import build_dbs, build_db
from .hosts import build_host_node, build_hosts_l2
from .obs import build_obs
from .overview import build_overview
from .pipeline import build_airflow, build_datapipeline, build_kafka


def build_all() -> None:
    build_overview()
    build_hosts_l2()
    build_host_node()
    build_dbs()
    build_db()
    build_datapipeline()
    build_airflow()
    build_kafka()
    build_apis()
    build_obs()
    write_static("morning-k8s", FOLDER_OBSERVABILITY)
