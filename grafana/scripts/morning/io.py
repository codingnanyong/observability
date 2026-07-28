"""Serialize Morning dashboards to JSON + Grafana sidecar ConfigMaps."""
from __future__ import annotations

import json

from .constants import CM, FOLDER_DEFAULT, OUT


def dash(uid, title, panels, links, *, tags=None, templating=None, time_from="now-1h", folder=FOLDER_DEFAULT):
    return {
        "annotations": {"list": []},
        "editable": True,
        "graphTooltip": 1,
        "id": None,
        "links": links,
        "panels": panels,
        "refresh": "30s",
        "schemaVersion": 39,
        "tags": tags or ["morning"],
        "templating": {"list": templating or []},
        "time": {"from": time_from, "to": "now"},
        "timepicker": {},
        "timezone": "Asia/Seoul",
        "title": title,
        "uid": uid,
        "version": 1,
        "_folder": folder,
    }


def write(d):
    OUT.mkdir(parents=True, exist_ok=True)
    CM.mkdir(parents=True, exist_ok=True)
    folder = d.pop("_folder", FOLDER_DEFAULT)
    name = d["uid"] + ".json"
    path = OUT / name
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    body = path.read_text(encoding="utf-8").rstrip() + "\n"
    indented = "\n".join(("    " + line if line else "") for line in body.splitlines())
    cm_name = f"grafana-dashboard-{d['uid']}"
    (CM / f"{cm_name}.yaml").write_text(
        f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {cm_name}
  namespace: observability
  labels:
    grafana_dashboard: "1"
  annotations:
    grafana_folder: {json.dumps(folder, ensure_ascii=False)}
data:
  {name}: |-
{indented}
""",
        encoding="utf-8",
    )
    print("wrote", d["uid"], "folder", folder, "panels", len(d["panels"]))



def write_static(uid: str, folder: str):
    """Re-emit ConfigMap for a hand-maintained dashboard JSON (e.g. morning-k8s)."""
    path = OUT / f"{uid}.json"
    if not path.exists():
        print("skip missing", uid)
        return
    body = path.read_text(encoding="utf-8").rstrip() + "\n"
    indented = "\n".join(("    " + line if line else "") for line in body.splitlines())
    cm_name = f"grafana-dashboard-{uid}"
    (CM / f"{cm_name}.yaml").write_text(
        f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {cm_name}
  namespace: observability
  labels:
    grafana_dashboard: "1"
  annotations:
    grafana_folder: {json.dumps(folder, ensure_ascii=False)}
data:
  {uid}.json: |-
{indented}
""",
        encoding="utf-8",
    )
    print("wrote", uid, "folder", folder, "(static)")


