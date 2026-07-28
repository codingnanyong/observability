"""Morning Overview — section health rollups + key occupancy metrics."""
from __future__ import annotations

from ..constants import (
    DS, SOFT_CPU, HARD_CPU, SOFT_CTM, HARD_CTM, SOFT_CONN, HARD_CONN,
    SOFT_IDLE_XACT, HARD_IDLE_XACT, DB_CLUSTERS,
)
from ..io import dash, write
from ..nav import nav
from ..panels import health_map, host_stat, link, row, stat, text, th, thresh_note, up_map
from ..metrics import (
    ACTION, ACTION_GATE, AF_FAIL, APIS_HEALTH, BROKEN, CTM, CPU, DBS_HEALTH, DISK,
    GRAFANA_UP, API_PORTAL_UP, HOSTS_HEALTH, MEM, OBS_HEALTH, OBS_TARGETS_DOWN, PG_CONN_MAX,
    PG_EXPORTERS_UP, PG_IDLE_MAX, PG_PVC, PIPELINE_HEALTH, PROM_UP, API_CORE_UP,
    api_error_pct,
)

# Keep Status column aligned across every section row.
_STATUS_W = 6


def _row_widths(n_metrics: int) -> list[int]:
    """Status fixed width; remaining width split evenly across metric cards."""
    rem = 24 - _STATUS_W
    base, extra = divmod(rem, n_metrics)
    metric_ws = [base + (1 if i >= n_metrics - extra else 0) for i in range(n_metrics)]
    return [_STATUS_W, *metric_ws]


def build_overview():
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**Morning Status**\n\n"
        "- Left **Status** = Soft / Hard rollup of child metrics (`OK` / `WARN` / `CRIT`)\n"
        "- Soft = orange · Hard = red\n"
        "- Use the top **Go** menu to switch sections"
    ), y, h=4)); pid += 1; y += 4

    # Row + table only when hidden var action_gate has a value (any CHECK firing).
    p.append(row(pid, "Action required", y, repeat="action_gate")); pid += 1; y += 1
    p.append({
        "id": pid, "type": "table", "title": "",
        "description": "Shows only checks past Soft. Hidden when none are firing.",
        "gridPos": {"h": 5, "w": 24, "x": 0, "y": y},
        "datasource": DS,
        "targets": [{"expr": ACTION, "refId": "A", "format": "table", "instant": True}],
        "transformations": [
            {"id": "labelsToFields", "options": {"mode": "columns", "keepLabels": ["check"]}},
            {"id": "organize", "options": {"excludeByName": {"Time": True},
                "renameByName": {"check": "Check", "Value": "Alert"},
                "indexByName": {"Check": 0, "Alert": 1}}},
            {"id": "filterByValue", "options": {
                "type": "include", "match": "all",
                "filters": [{"fieldName": "Alert", "config": {
                    "id": "equal", "options": {"value": 1}}}],
            }},
            {"id": "sortBy", "options": {"sort": [{"field": "Check", "desc": False}]}},
        ],
        "fieldConfig": {"defaults": {"decimals": 0, "custom": {"align": "left"}}, "overrides": [{
            "matcher": {"id": "byName", "options": "Alert"},
            "properties": [
                {"id": "mappings", "value": [
                    {"type": "value", "options": {"1": {"text": "CHECK", "color": "orange"}}},
                ]},
                {"id": "custom.cellOptions", "value": {"type": "color-background", "mode": "basic"}},
                {"id": "thresholds", "value": th(1)},
                {"id": "custom.width", "value": 120},
            ],
        }]},
        "options": {"showHeader": True, "cellHeight": "sm", "footer": {"show": False}},
    }); pid += 1; y += 5

    # card: name, expr, unit, soft, hard, max, host_stat?, invert?, health?, description
    sections = [
        ("Hosts · occupancy (click → Hosts L2)", "/d/morning-hosts", [
            ("Status", HOSTS_HEALTH, "short", None, None, None, False, False, True,
             "Rollup of CPU, Memory, Disk Soft/Hard and NotReady."),
            ("CPU %", CPU, "percent", SOFT_CPU, HARD_CPU, 100, True, False, False,
             "Max node CPU utilization."),
            ("Memory %", MEM, "percent", SOFT_CPU, HARD_CPU, 100, True, False, False,
             "Max node memory utilization."),
            ("Disk / %", DISK, "percent", SOFT_CPU, HARD_CPU, 100, True, False, False,
             "Max root (/) disk utilization."),
        ]),
        ("DBs · occupancy (click → per DB)", "/d/morning-dbs", [
            ("Status", DBS_HEALTH, "short", None, None, None, False, False, True,
             "Rollup of exporters, Conn %, PVC, and idle-in-xact Soft/Hard."),
            ("Conn % MAX", PG_CONN_MAX, "percent", SOFT_CONN, HARD_CONN, 100, False, False, False,
             "Max DB connection utilization."),
            ("Idle-in-xact", PG_IDLE_MAX, "s", SOFT_IDLE_XACT, HARD_IDLE_XACT, None, False, False, False,
             "Longest idle-in-transaction age."),
            ("K8s PVC %", PG_PVC, "percent", 75, 90, 100, False, False, False,
             "Max PVC utilization in postgres."),
        ]),
        ("DataPipeline · health (click → Airflow | Kafka)", "/d/morning-datapipeline", [
            ("Status", PIPELINE_HEALTH, "short", None, None, None, False, False, True,
             "Rollup of scheduler, AF fail, Broken connectors, and CTM Soft/Hard."),
            ("AF fail 5m", AF_FAIL, "short", 5, 20, None, False, False, False,
             "Task Instance failures in the last 5 minutes."),
            ("KF Broken", BROKEN, "short", 1, 2, None, False, False, False,
             "Connect connectors not in Running state."),
            ("CTM Lag", CTM, "short", SOFT_CTM, HARD_CTM, None, False, False, False,
             "Sum of CTM sink consumergroup lag."),
        ]),
        ("APIs · health (click → services)", "/d/morning-apis", [
            ("Status", APIS_HEALTH, "short", None, None, None, False, False, True,
             "Rollup of deployment availability and HTTP Error % Soft/Hard."),
            ("APIs UP", f"(({API_PORTAL_UP}) + ({API_CORE_UP}))", "short", 1, 2, 2, False, True, False,
             "Deployments available (expect 2: portal + core)."),
            ("portal Err%", api_error_pct("api-portal"), "percent", 1, 5, 100, False, False, False,
             "api-portal 4xx/5xx ratio (health probes excluded)."),
            ("core Err%", api_error_pct("api-core"), "percent", 1, 5, 100, False, False, False,
             "api-core 4xx/5xx ratio (health probes excluded)."),
        ]),
        ("Observability · health (click → detail)", "/d/morning-observability", [
            ("Status", OBS_HEALTH, "short", None, None, None, False, False, True,
             "Rollup of Prometheus/Grafana availability and scrape downs."),
            ("Targets DOWN", OBS_TARGETS_DOWN, "short", 1, 3, None, False, False, False,
             "Scrape targets down in the observability namespace."),
            ("Prometheus", PROM_UP, "short", None, None, None, False, False, False,
             "Prometheus scrape / availability."),
            ("Grafana", GRAFANA_UP, "short", None, None, None, False, False, False,
             "Grafana scrape / availability."),
        ]),
    ]
    for title, url, cards in sections:
        p.append(row(pid, title, y)); pid += 1; y += 1
        widths = _row_widths(len(cards) - 1)
        x = 0
        for (ct, expr, unit, soft, hard, mx, show_host, invert, is_health, desc), w in zip(cards, widths):
            soft_v, hard_v = soft, hard
            note = desc
            thn = thresh_note(soft_v, hard_v, invert=invert)
            if thn and not is_health:
                note = f"{note} {thn}".strip()
            if is_health:
                panel = stat(
                    pid, ct, x, y, w, 4, expr, unit=unit,
                    mappings=health_map(), links=link(url),
                    description=note,
                )
                panel["fieldConfig"]["defaults"]["thresholds"] = {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "orange", "value": 1},
                        {"color": "red", "value": 2},
                    ],
                }
                panel["options"]["text"] = {"titleSize": 13, "valueSize": 36}
                p.append(panel)
            elif show_host:
                p.append(host_stat(
                    pid, ct, x, y, w, 4, expr, unit=unit, soft=soft_v, hard=hard_v,
                    description=desc, link_url=url,
                ))
            elif ct in ("Prometheus", "Grafana"):
                panel = stat(
                    pid, ct, x, y, w, 4, expr, unit=unit,
                    mappings=up_map(), links=link(url), description=note,
                )
                panel["fieldConfig"]["defaults"]["thresholds"] = {
                    "mode": "absolute",
                    "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}],
                }
                p.append(panel)
            else:
                p.append(stat(
                    pid, ct, x, y, w, 4, expr, unit=unit, soft=soft_v, hard=hard_v,
                    links=link(url), max_v=mx, invert=invert,
                    description=note,
                    decimals=1 if unit == "percent" and "Err" in ct else 0,
                ))
            x += w
            pid += 1
        y += 4

    write(dash("morning-overview", "Morning Status", p, nav(), tags=["morning", "overview"], templating=[{
        "name": "action_gate",
        "type": "query",
        "label": "",
        "hide": 2,
        "refresh": 2,
        "datasource": DS,
        "query": f"query_result({ACTION_GATE})",
        "regex": r'/gate="([^"]+)"/',
        "definition": f"query_result({ACTION_GATE})",
        "current": {},
        "options": [],
        "includeAll": False,
        "multi": False,
        "sort": 0,
    }]))
