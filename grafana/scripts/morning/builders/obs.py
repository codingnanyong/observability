"""Morning dashboard builders."""
from __future__ import annotations

from ..constants import (
    DS, INTRO_H, MORNING_NAV_TAG, SOFT_CPU, HARD_CPU, SOFT_CTM, HARD_CTM, SOFT_CONN, HARD_CONN,
    SOFT_IDLE_XACT, HARD_IDLE_XACT, DB_CLUSTERS,
)
from ..io import dash, write
from ..nav import nav
from ..panels import host_stat, link, row, stat, table, text, th, thresh_note, timeseries, up_map
from ..metrics import (
    ACTION, ACTION_GATE, AF_DAG_FAIL, AF_FAIL, AF_OK, AF_SCHED, BAD_PODS, BROKEN, CTM, CPU, DEPLOY_GAPS,
    DISK, KF_BROKERS, MEM, PG_CONN_MAX, PG_EXPORTERS_UP, PG_PVC, cpu_by_inst, disk_by_inst, mem_by_inst,
    pg_conn, pg_idle_xact, pg_lag, pg_up,
)


def build_obs():
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**Observability** · [← Status](/d/morning-overview) · "
        "[상세](/d/morning-observability-detail) · [Hosts · K8s](/d/morning-hosts)\n\n"
        "스택 UP · 클릭 → scrape/pods · 클러스터 K8s는 Hosts 최상단"
    ), y)); pid += 1; y += INTRO_H
    url = "/d/morning-observability-detail"
    p.append(row(pid, "스택 (클릭 → 상세)", y)); pid += 1; y += 1
    for i, (t, e) in enumerate([
        ("Prometheus", 'max(up{job="kube-prometheus-stack-prometheus"}) or vector(0)'),
        ("Grafana", 'max(up{job="kube-prometheus-stack-grafana"}) or clamp_max(count(kube_pod_status_ready{namespace="observability",pod=~"kube-prometheus-stack-grafana-.*",condition="true"}==1), 1) or vector(0)'),
        ("Alertmanager", 'max(up{job="kube-prometheus-stack-alertmanager"}) or vector(0)'),
        ("node-exporter", 'count(up{job="node-exporter"}==1) or vector(0)'),
    ]):
        if t == "node-exporter":
            p.append(stat(pid, t, i * 6, y, 6, 5, e, soft=1, hard=2, invert=True,
                          links=link(url), max_v=2,
                          description="node-exporter UP 수. 노드 2대면 2가 정상."))
        else:
            p.append(stat(pid, t, i * 6, y, 6, 5, e, mappings=up_map(), links=link(url),
                          description=f"{t} scrape/가용 상태."))
            p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
        pid += 1
    write(dash("morning-observability", "Morning · Observability", p,
               nav(back=("← Status", "/d/morning-overview")), tags=["morning", "observability", MORNING_NAV_TAG]))

    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**Observability · 상세** · [← Obs](/d/morning-observability) · [← Status](/d/morning-overview)\n\n"
        "① 스택 → ② scrape 건강 → ③ Targets | Obs Pods\n\n"
        "클러스터 K8s(Nodes/Bad Pods)는 [Hosts](/d/morning-hosts) 최상단"
    ), y)); pid += 1; y += INTRO_H
    p.append(row(pid, "① 스택 상태", y)); pid += 1; y += 1
    for i, (t, e) in enumerate([
        ("Prometheus", 'max(up{job="kube-prometheus-stack-prometheus"}) or vector(0)'),
        ("Grafana", 'max(up{job="kube-prometheus-stack-grafana"}) or vector(0)'),
        ("Alertmanager", 'max(up{job="kube-prometheus-stack-alertmanager"}) or vector(0)'),
        ("cadvisor-docker", 'count(up{job="cadvisor-docker"}==1) or vector(0)'),
    ]):
        if "cadvisor" in t:
            p.append(stat(pid, t, i * 6, y, 6, 4, e, soft=1, hard=2, invert=True,
                          max_v=2, description="cadvisor-docker UP 수. 노드 2대면 2가 정상."))
        else:
            p.append(stat(pid, t, i * 6, y, 6, 4, e, mappings=up_map(),
                          description=f"{t} scrape/가용 상태."))
            p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
        pid += 1
    y += 4
    p.append(row(pid, "② scrape 건강 (트렌드)", y)); pid += 1; y += 1
    p.append(timeseries(pid, "Scrape up by job", 0, y, 24, 7, [
        ('sum by (job) (up)', "{{job}}"),
    ])); pid += 1
    y += 7
    p.append(row(pid, "③ Targets | Obs Pods", y)); pid += 1; y += 1
    p.append(table(pid, "Prometheus jobs (up)", 0, y, 12, 10,
        'sum by (job) (up)', rename={"job": "Job", "Value": "Up series"}, sort_field="Up series")); pid += 1
    p.append(table(pid, "observability pods", 12, y, 12, 10,
        'max by (pod, phase) (kube_pod_status_phase{namespace="observability"} == 1)',
        rename={"pod": "Pod", "phase": "Phase", "Value": "V"}, sort_field="Pod")); pid += 1
    write(dash("morning-observability-detail", "Morning · Observability 상세", p,
               nav(back=("← Obs", "/d/morning-observability")), tags=["morning", "observability"], time_from="now-6h"))


