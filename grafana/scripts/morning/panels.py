"""Grafana panel constructors for Morning dashboards."""
from __future__ import annotations

from .constants import DS, INTRO_H

def link(url, title="Detail"):
    return [{"title": title, "url": url, "targetBlank": False, "keepTime": True}]


def th(soft=None, hard=None, invert=False):
    """Threshold steps.

    Normal (higher worse): green → orange@soft → red@hard
    Invert (higher better / expected count): red → orange@soft → green@hard
    No soft/hard: neutral green only (avoid false red on healthy counters).
    """
    if soft is None and hard is None:
        return {"mode": "absolute", "steps": [{"color": "green", "value": None}]}
    if invert:
        steps = [{"color": "red", "value": None}]
        if soft is not None:
            steps.append({"color": "orange", "value": soft})
        if hard is not None:
            steps.append({"color": "green", "value": hard})
        return {"mode": "absolute", "steps": steps}
    steps = [{"color": "green", "value": None}]
    if soft is not None:
        steps.append({"color": "orange", "value": soft})
    if hard is not None:
        steps.append({"color": "red", "value": hard})
    return {"mode": "absolute", "steps": steps}


def text(id_, content, y=0, h=INTRO_H):
    return {
        "id": id_, "type": "text", "title": "",
        "gridPos": {"h": h, "w": 24, "x": 0, "y": y},
        "options": {"mode": "markdown", "content": content},
        "transparent": False,
    }


def row(id_, title, y, *, repeat=None):
    r = {
        "id": id_, "type": "row", "title": title, "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y}, "panels": [],
    }
    if repeat:
        r["repeat"] = repeat
    return r


def thresh_note(soft=None, hard=None, *, invert=False):
    """Short Soft/Hard note for panel descriptions (i icon)."""
    if soft is None and hard is None:
        return ""
    if invert:
        if soft is not None and hard is not None:
            return f"경고 <{soft} · 정상 ≥{hard}"
        if hard is not None:
            return f"정상 ≥{hard}"
        return f"경고 <{soft}"
    if soft is not None and hard is not None:
        return f"Soft ≥{soft} · Hard ≥{hard}"
    if soft is not None:
        return f"Soft ≥{soft}"
    return f"Hard ≥{hard}"


def stat(id_, title, x, y, w, h, expr, *, unit="short", decimals=0, soft=None, hard=None,
         mappings=None, links=None, description="", max_v=None, min_v=0, invert=False):
    defaults = {
        "unit": unit, "decimals": decimals, "min": min_v,
        "thresholds": th(soft, hard, invert=invert),
        "mappings": mappings or [],
        "links": links or [],
    }
    if max_v is not None:
        defaults["max"] = max_v
    panel = {
        "id": id_, "type": "stat", "title": title,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": DS,
        "targets": [{"expr": expr, "refId": "A", "instant": True, "range": False, "queryType": "instant"}],
        "fieldConfig": {"defaults": defaults, "overrides": []},
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "colorMode": "background", "graphMode": "none",
            "justifyMode": "center", "textMode": "value",
            "text": {"titleSize": 13, "valueSize": 36},
        },
    }
    if description:
        panel["description"] = description
    return panel


def up_map():
    # Range maps are more reliable than value maps for float 0/1 in Grafana 13.
    return [
        {"type": "range", "options": {
            "from": 0, "to": 0,
            "result": {"text": "DOWN", "color": "red", "index": 0},
        }},
        {"type": "range", "options": {
            "from": 1, "to": 1,
            "result": {"text": "UP", "color": "green", "index": 1},
        }},
        {"type": "special", "options": {
            "match": "null+nan",
            "result": {"text": "NO DATA", "color": "orange", "index": 2},
        }},
    ]


def health_map():
    """0=OK · 1=WARN (Soft) · 2=CRIT (Hard) — Overview section rollup."""
    return [
        {"type": "range", "options": {
            "from": 0, "to": 0,
            "result": {"text": "OK", "color": "green", "index": 0},
        }},
        {"type": "range", "options": {
            "from": 1, "to": 1,
            "result": {"text": "WARN", "color": "orange", "index": 1},
        }},
        {"type": "range", "options": {
            "from": 2, "to": 2,
            "result": {"text": "CRIT", "color": "red", "index": 2},
        }},
        {"type": "special", "options": {
            "match": "null+nan",
            "result": {"text": "NO DATA", "color": "orange", "index": 3},
        }},
    ]


def timeseries(id_, title, x, y, w, h, targets, *, unit="short", soft=None, hard=None, description="", max_v=None):
    tgts = [{"expr": e, "refId": chr(65 + i), "legendFormat": leg} for i, (e, leg) in enumerate(targets)]
    if soft is not None:
        tgts.append({"expr": f"vector({soft})", "refId": "SOFT", "legendFormat": "Soft"})
    if hard is not None:
        tgts.append({"expr": f"vector({hard})", "refId": "HARD", "legendFormat": "Hard"})
    overrides = []
    for name, color in (("Soft", "orange"), ("Hard", "red")):
        overrides.append({
            "matcher": {"id": "byName", "options": name},
            "properties": [
                {"id": "color", "value": {"mode": "fixed", "fixedColor": color}},
                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 5]}},
                {"id": "custom.fillOpacity", "value": 0},
                {"id": "custom.lineWidth", "value": 2},
            ],
        })
    defaults = {
        "unit": unit, "min": 0,
        "custom": {"lineWidth": 2, "fillOpacity": 15, "spanNulls": True, "showPoints": "never"},
    }
    if max_v is not None:
        defaults["max"] = max_v
    panel = {
        "id": id_, "type": "timeseries", "title": title,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": DS, "targets": tgts,
        "fieldConfig": {"defaults": defaults, "overrides": overrides},
        "options": {
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "multi", "sort": "desc"},
        },
    }
    if description:
        panel["description"] = description
    return panel


def table(id_, title, x, y, w, h, expr, *, rename=None, sort_field=None, description="", unit_overrides=None):
    rename = rename or {}
    transforms = [
        {"id": "organize", "options": {
            "excludeByName": {"Time": True, "__name__": True},
            "renameByName": rename,
            "indexByName": {v: i for i, v in enumerate(rename.values())} if rename else {},
        }},
    ]
    if sort_field:
        transforms.append({"id": "sortBy", "options": {"sort": [{"field": sort_field, "desc": True}]}})
    panel = {
        "id": id_, "type": "table", "title": title,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": DS,
        "targets": [{"refId": "A", "expr": expr, "format": "table", "instant": True}],
        "transformations": transforms,
        "fieldConfig": {"defaults": {"custom": {"align": "left"}}, "overrides": unit_overrides or []},
        "options": {"showHeader": True, "cellHeight": "sm", "footer": {"show": False}},
    }
    if description:
        panel["description"] = description
    return panel



def host_stat(id_, title, x, y, w, h, expr, *, unit="percent", soft=None, hard=None,
              description="", link_url="/d/morning-hosts"):
    """Stat: MAX value + node name under it. Click → Hosts L2 (not node L3)."""
    note = description or "노드 중 최대값. 숫자 아래는 해당 노드명."
    thn = thresh_note(soft, hard)
    if thn:
        note = f"{note} {thn}"
    p = stat(id_, title, x, y, w, h, expr, unit=unit, soft=soft, hard=hard, max_v=100,
             description=note)
    p["targets"] = [{
        "expr": expr, "refId": "A",
        "instant": True, "range": False, "queryType": "instant",
        "legendFormat": "{{instance}}",
    }]
    # Keep panel title (CPU %); series name under value = instance. Do NOT set displayName
    # (it replaces the title and makes value/name look wrong in Grafana 13).
    p["fieldConfig"]["defaults"].pop("displayName", None)
    p["fieldConfig"]["defaults"]["decimals"] = 1
    p["fieldConfig"]["defaults"]["links"] = [{
        "title": "Hosts",
        "url": link_url,
        "targetBlank": False,
        "keepTime": True,
    }]
    # value on top (center), instance name below — not side-by-side
    p["options"]["textMode"] = "value_and_name"
    p["options"]["justifyMode"] = "center"
    p["options"]["wideLayout"] = False
    p["options"]["text"] = {"titleSize": 13, "valueSize": 40, "nameSize": 16}
    return p


