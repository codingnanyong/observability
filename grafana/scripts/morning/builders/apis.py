"""Morning dashboard builders."""
from __future__ import annotations

from ..constants import (
    API_DOCS_MARKDOWN, DS, INTRO_H, MORNING_NAV_TAG, SOFT_CPU, HARD_CPU, SOFT_CTM, HARD_CTM,
    SOFT_CONN, HARD_CONN, SOFT_IDLE_XACT, HARD_IDLE_XACT, DB_CLUSTERS,
)
from ..io import dash, write
from ..nav import nav
from ..panels import host_stat, link, row, stat, table, text, th, thresh_note, timeseries, up_map
from ..metrics import (
    ACTION, ACTION_GATE, AF_DAG_FAIL, AF_FAIL, AF_OK, AF_SCHED, BAD_PODS, BROKEN, CTM, CPU, DEPLOY_GAPS,
    DISK, KF_BROKERS, MEM, PG_CONN_MAX, PG_EXPORTERS_UP, PG_PVC, cpu_by_inst, disk_by_inst, mem_by_inst,
    pg_conn, pg_idle_xact, pg_lag, pg_up,
)


def build_apis():
    p, pid, y = [], 1, 0
    docs = f" · {API_DOCS_MARKDOWN}" if API_DOCS_MARKDOWN else ""
    p.append(text(pid, (
        "**APIs** · [← Status](/d/morning-overview) · "
        "[portal](/d/morning-api-svc?var-job=api-portal) · "
        "[core](/d/morning-api-svc?var-job=api-core)\n\n"
        f"클릭 → EP/성능{docs}"
    ), y)); pid += 1; y += INTRO_H
    p.append(row(pid, "서비스 (클릭 → EP 상세)", y)); pid += 1; y += 1
    for i, (name, ns, dep, job) in enumerate([
        ("api-portal", "api-portal", "api-portal", "api-portal"),
        ("api-core", "api-core", "api-core", "api-core"),
    ]):
        url = f"/d/morning-api-svc?var-job={job}&var-ns={ns}&var-deploy={dep}"
        x = i * 12
        p.append(stat(pid, f"{name}", x, y, 6, 5,
            f'(max(kube_deployment_status_replicas_available{{namespace="{ns}",deployment="{dep}"}}) > bool 0) or vector(0)',
            mappings=up_map(), links=link(url)))
        p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
            "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
        pid += 1
        p.append(stat(pid, f"{name} Ready", x + 6, y, 6, 5,
            f'max(kube_deployment_status_replicas_available{{namespace="{ns}",deployment="{dep}"}}) or vector(0)',
            soft=0, hard=1, invert=True, links=link(url),
            description="가용 replica 수. 1 이상이면 정상.")); pid += 1
    write(dash("morning-apis", "Morning · APIs", p,
               nav(back=("← Status", "/d/morning-overview")), tags=["morning", "apis", MORNING_NAV_TAG]))

    # L3 service
    excl = r'handler!~"/health|/info|^/$|/api/healthz|.*/health.*|/metrics|.*/docs|.*/redoc|.*/openapi.json"'
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**API · ${job}** · [← APIs](/d/morning-apis) · [← Status](/d/morning-overview)\n\n"
        "① 상태 → ② Error/RPS/p95 → ③ Endpoints\n\n"
        "Error Soft 1% · Hard 5%"
    ), y)); pid += 1; y += INTRO_H
    p.append(row(pid, "① 상태", y)); pid += 1; y += 1
    p.append(stat(pid, "Scrape", 0, y, 8, 4, 'max(up{job="$job"}) or vector(0)', mappings=up_map()))
    p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
        "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
    pid += 1
    p.append(stat(pid, "Error %", 8, y, 8, 4,
        f'(sum(rate(http_requests_total{{job="$job",status=~"[45]..",{excl}}}[5m])) or vector(0)) / clamp_min(sum(rate(http_requests_total{{job="$job",{excl}}}[5m])) or vector(0), 1e-9)',
        unit="percentunit", soft=0.01, hard=0.05, decimals=2)); pid += 1
    p.append(stat(pid, "RPS", 16, y, 8, 4,
        f'sum(rate(http_requests_total{{job="$job",{excl}}}[5m])) or vector(0)', decimals=2)); pid += 1
    y += 4
    p.append(row(pid, "② 성능 (트렌드)", y)); pid += 1; y += 1
    p.append(timeseries(pid, "Error %", 0, y, 8, 7, [
        (f'(sum(rate(http_requests_total{{job="$job",status=~"[45]..",{excl}}}[5m])) or vector(0)) / clamp_min(sum(rate(http_requests_total{{job="$job",{excl}}}[5m])) or vector(0), 1e-9)', "error"),
    ], unit="percentunit", soft=0.01, hard=0.05)); pid += 1
    p.append(timeseries(pid, "RPS", 8, y, 8, 7, [
        (f'sum by (method) (rate(http_requests_total{{job="$job",{excl}}}[5m]))', "{{method}}"),
    ])); pid += 1
    p.append(timeseries(pid, "p95", 16, y, 8, 7, [
        (f'histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{{job="$job",{excl}}}[5m])))', "p95"),
    ], unit="s", soft=0.2, hard=1)); pid += 1
    y += 7
    p.append(row(pid, "③ Endpoints", y)); pid += 1; y += 1
    p.append({
        "id": pid, "type": "table", "title": "API endpoints",
        "gridPos": {"h": 12, "w": 24, "x": 0, "y": y},
        "datasource": DS,
        "targets": [
            {"refId": "A", "format": "table", "instant": True,
             "expr": f'(sum by (handler, method) (rate(http_requests_total{{job="$job",{excl}}}[5m])) * on(handler, method) group_left(tag) max by (handler, method, tag) (http_endpoint_info{{job="$job",{excl}}})) or (max by (handler, method, tag) (http_endpoint_info{{job="$job",{excl}}}) * 0)'},
            {"refId": "B", "format": "table", "instant": True,
             "expr": f'(histogram_quantile(0.95, sum by (handler, le) (rate(http_request_duration_seconds_bucket{{job="$job",{excl}}}[5m])))) or (max by (handler) (http_endpoint_info{{job="$job",{excl}}}) * 0 / 0)'},
            {"refId": "C", "format": "table", "instant": True,
             "expr": f'(sum by (handler) (rate(http_requests_total{{job="$job",status=~"5..",{excl}}}[5m])) / clamp_min(sum by (handler) (rate(http_requests_total{{job="$job",{excl}}}[5m])), 1e-9)) or (max by (handler) (http_endpoint_info{{job="$job",{excl}}}) * 0)'},
            {"refId": "D", "format": "table", "instant": True,
             "expr": f'(sum by (handler) (increase(http_requests_total{{job="$job",{excl}}}[5m]))) or (max by (handler) (http_endpoint_info{{job="$job",{excl}}}) * 0)'},
        ],
        "transformations": [
            {"id": "joinByField", "options": {"byField": "handler", "mode": "outer"}},
            {"id": "organize", "options": {
                "excludeByName": {"Time": True, "Time 1": True, "Time 2": True, "Time 3": True, "Time 4": True},
                "renameByName": {
                    "method": "Method", "tag": "Tag", "handler": "EP",
                    "Value #A": "RPS", "Value #B": "p95", "Value #C": "Error%", "Value #D": "Count 5m",
                },
            }},
        ],
        "fieldConfig": {"defaults": {"custom": {"align": "left"}}, "overrides": []},
        "options": {"showHeader": True, "cellHeight": "sm", "footer": {"show": False}},
    })
    write(dash("morning-api-svc", "Morning · API service", p,
               nav(back=("← APIs", "/d/morning-apis")), tags=["morning", "apis"], templating=[{
        "name": "job", "type": "custom", "label": "Service",
        "query": "api-portal,api-core",
        "current": {"text": "api-portal", "value": "api-portal"},
        "options": [
            {"text": "api-portal", "value": "api-portal", "selected": True},
            {"text": "api-core", "value": "api-core", "selected": False},
        ],
        "includeAll": False, "multi": False,
    }], time_from="now-6h"))


