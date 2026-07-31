"""PromQL snippets and action-check expressions for Morning dashboards."""
from __future__ import annotations

from .constants import (
    HARD_CONN, HARD_CPU, HARD_CTM, HARD_IDLE_XACT, PG_JOBS,
    SOFT_CONN, SOFT_CPU, SOFT_CTM, SOFT_IDLE_XACT,
)

OCC_W = "10m"  # matches recording rule rate window


def cpu_by_inst(instance: str | None = None) -> str:
    if instance:
        return f'morning:node_cpu_util:percent{{instance="{instance}"}}'
    return "morning:node_cpu_util:percent"


def mem_by_inst(instance: str | None = None) -> str:
    if instance:
        return f'morning:node_mem_util:percent{{instance="{instance}"}}'
    return "morning:node_mem_util:percent"


def disk_by_inst(instance: str | None = None, mount: str = "/") -> str:
    metric = (
        "morning:node_disk_media_util:percent"
        if mount == "/media"
        else "morning:node_disk_root_util:percent"
    )
    if instance:
        return f'{metric}{{instance="{instance}"}}'
    return metric


def max_series(expr: str) -> str:
    """Keep only the MAX series and its instance label (value == max(expr))."""
    return f'({expr}) == on() group_left() max({expr})'


_CPU_BY = cpu_by_inst()
_MEM_BY = mem_by_inst()
_DISK_BY = disk_by_inst()
CPU = max_series(_CPU_BY)
MEM = max_series(_MEM_BY)
DISK = max_series(_DISK_BY)
# DB clusters (add entries here to scale). job = Prometheus scrape job.
def pg_conn(job: str) -> str:
    return (
        f'(sum(pg_stat_database_numbackends{{job="{job}",datname!~"template.*|postgres|airflow|openmetadata"}}) '
        f'/ clamp_min(max(pg_settings_max_connections{{job="{job}"}}), 1) * 100) or vector(0)'
    )


def pg_lag(job: str) -> str:
    return f'max(pg_replication_lag_seconds{{job="{job}"}}) or vector(0)'


def pg_idle_xact(job: str) -> str:
    return (
        f'max(pg_stat_activity_max_tx_duration{{state="idle in transaction",'
        f'job="{job}",datname!~"template.*|postgres|airflow|openmetadata"}}) or vector(0)'
    )


def pg_up(job: str) -> str:
    # Force 0/1 for Grafana value maps (scrape up ∧ pg_up).
    return (
        f'(max(up{{job="{job}"}}) >= bool 1) * (max(pg_up{{job="{job}"}}) >= bool 1)'
    )


PG_CONN_MAX = (
    f'max((sum by (job) (pg_stat_database_numbackends{{job=~"{PG_JOBS}",datname!~"template.*|postgres|airflow|openmetadata"}}) '
    f'/ clamp_min(max by (job) (pg_settings_max_connections{{job=~"{PG_JOBS}"}}), 1) * 100)) or vector(0)'
)
PG_EXPORTERS_UP = (
    f'count((pg_up{{job=~"{PG_JOBS}"}} == 1) and on(job, instance) (up{{job=~"{PG_JOBS}"}} == 1)) '
    f'or vector(0)'
)
PG_PVC = 'max((kubelet_volume_stats_used_bytes{namespace="postgres"} / kubelet_volume_stats_capacity_bytes{namespace="postgres"}) * 100) or vector(0)'
AF_FAIL = 'sum(increase(airflow_ti_failures[5m])) or vector(0)'
AF_OK = 'sum(increase(airflow_ti_successes[5m])) or vector(0)'
AF_DAG_FAIL = 'sum(increase(airflow_dagrun_failed_count[5m])) or vector(0)'
AF_SCHED = 'clamp_max(count(kube_pod_status_ready{namespace="airflow",pod=~"airflow-scheduler-.*",condition="true"}==1), 1) or vector(0)'
CTM = 'sum(kafka_consumergroup_lag{consumergroup=~"connect-ctm-sink-.*"}) or vector(0)'
BROKEN = 'sum(kafka_connect_connector_running == bool 0) or vector(0)'
KF_BROKERS = 'count(kube_pod_status_ready{namespace="kafka",pod=~"kafka-cluster-combined-.*",condition="true"}==1) or vector(0)'
BAD_PODS = 'sum(kube_pod_container_status_waiting_reason{namespace=~"kafka|airflow|postgres|observability|data|api-core|api-portal",reason=~"CrashLoopBackOff|ImagePullBackOff|ErrImagePull|CreateContainerConfigError|InvalidImageName"} == 1) or vector(0)'
DEPLOY_GAPS = 'sum(kube_deployment_status_replicas_unavailable{namespace=~"kafka|airflow|postgres|observability|data|api-core|api-portal"}) or vector(0)'

ACTION = rf'''
label_replace(((sum(kafka_consumergroup_lag{{consumergroup=~"connect-ctm-sink-.*"}}) or vector(0)) >= bool 150000), "check", "CTM Lag ≥ 150k", "", "")
or label_replace((({PG_CONN_MAX}) >= bool 70), "check", "DB Conn% ≥ 70", "", "")
or label_replace(((sum(increase(airflow_dagrun_failed_count[5m])) or vector(0)) >= bool 1), "check", "DAG fail 5m ≥ 1", "", "")
or label_replace(((sum(increase(airflow_ti_failures[5m])) or vector(0)) >= bool 5), "check", "Task fail 5m ≥ 5", "", "")
or label_replace(((sum(kube_pod_status_phase{{namespace=~"kafka|airflow|postgres|observability|data",phase=~"Failed|Unknown"}} == 1) or vector(0)) >= bool 1), "check", "Bad Pods ≥ 1", "", "")
or label_replace(((sum(kafka_connect_connector_state{{state="FAILED"}}) or vector(0)) >= bool 1), "check", "Connect FAILED ≥ 1", "", "")
or label_replace(((max(pg_stat_activity_max_tx_duration{{state="idle in transaction",job=~"{PG_JOBS}",datname!~"template.*|postgres|airflow|openmetadata"}}) or vector(0)) >= bool {SOFT_IDLE_XACT}), "check", "PG idle-in-xact age ≥ 2m", "", "")
or label_replace(((max(morning:node_mem_util:percent) or vector(0)) >= bool 80), "check", "Host Memory ≥ 80%", "", "")
or label_replace(((max(morning:node_cpu_util:percent) or vector(0)) >= bool 80), "check", "Host CPU ≥ 80%", "", "")
'''
# Series present only when ≥1 check is firing → hidden repeat gate (row hidden when empty).
# MUST be a single line: Grafana's query_result() variable regex does not match newlines,
# and then falls through to match[]/series API → parse error on "(".
ACTION_GATE = (
    'label_replace(count(('
    + " ".join(ACTION.split())
    + ') == 1) > 0, "gate", "발생", "", "")'
)


def _sev_high(expr: str, soft: float | int, hard: float | int) -> str:
    """Severity 0/1/2 when higher values are worse."""
    return (
        f"clamp_max("
        f"(({expr}) >= bool {soft}) + (({expr}) >= bool {hard})"
        f", 2)"
    )


def _sev_low(expr: str, soft: float | int, hard: float | int) -> str:
    """Severity 0/1/2 when lower values are worse (soft = warn below, hard = critical below)."""
    return (
        f"clamp_max("
        f"(({expr}) < bool {soft}) + (({expr}) < bool {hard})"
        f", 2)"
    )


def _sev_down(expr: str) -> str:
    """Binary availability: 0 if up (expr≥1), else Hard(2)."""
    return f"((({expr}) < bool 1) * 2)"

def _sev_down_ksm(expr: str) -> str:
    """Like _sev_down but ignore gaps when kube-state-metrics is down."""
    return (
        f"(((max(up{{job=\"kube-state-metrics\"}}) or vector(0)) >= bool 1) "
        f"* (({expr}) < bool 1) * 2)"
    )


def _max_sev(*parts: str) -> str:
    """max() over several severity vectors (PromQL max is unary — tag then aggregate)."""
    joined = " or ".join(
        f'label_replace(({p}), "s", "{i}", "", "")' for i, p in enumerate(parts)
    )
    return f"max(({joined}))"


# Health probe handlers excluded from API error/RPS (same as L3).
_API_EXCL = (
    r'handler!~"/health|/info|^/$|/api/healthz|.*/health.*|/metrics|.*/docs|.*/redoc|.*/openapi.json"'
)

API_PORTAL_UP = (
    '(max(kube_deployment_status_replicas_available'
    '{namespace="api-portal",deployment="api-portal"}) > bool 0) or vector(0)'
)
API_CORE_UP = (
    '(max(kube_deployment_status_replicas_available'
    '{namespace="api-core",deployment="api-core"}) > bool 0) or vector(0)'
)
PROM_UP = 'max(up{job="kube-prometheus-stack-prometheus"}) or vector(0)'
GRAFANA_UP = (
    'max(up{job="kube-prometheus-stack-grafana"}) or '
    'clamp_max(count(kube_pod_status_ready{namespace="observability",'
    'pod=~"kube-prometheus-stack-grafana-.*",condition="true"}==1), 1) or vector(0)'
)


def api_error_pct(job: str) -> str:
    """HTTP 4xx/5xx ratio as percent (0–100)."""
    return (
        f'((sum(rate(http_requests_total{{job="{job}",status=~"[45]..",{_API_EXCL}}}[5m])) or vector(0))'
        f' / clamp_min(sum(rate(http_requests_total{{job="{job}",{_API_EXCL}}}[5m])) or vector(0), 1e-9)'
        f" * 100)"
    )


PG_IDLE_MAX = (
    f'max(pg_stat_activity_max_tx_duration{{state="idle in transaction",'
    f'job=~"{PG_JOBS}",datname!~"template.*|postgres|airflow|openmetadata"}}) or vector(0)'
)
NODES_NOT_READY = (
    'sum(kube_node_status_condition{condition="Ready",status="false"} == 1) or vector(0)'
)
OBS_TARGETS_DOWN = 'count(up{namespace="observability",job=~"kube-prometheus-stack-prometheus|kube-prometheus-stack-grafana|kube-prometheus-stack-alertmanager"} == 0) or vector(0)'

# Section rollups for Overview (max severity across child signals).
HOSTS_HEALTH = _max_sev(
    _sev_high("max(morning:node_cpu_util:percent) or vector(0)", SOFT_CPU, HARD_CPU),
    _sev_high("max(morning:node_mem_util:percent) or vector(0)", SOFT_CPU, HARD_CPU),
    _sev_high("max(morning:node_disk_root_util:percent) or vector(0)", SOFT_CPU, HARD_CPU),
    _sev_high(NODES_NOT_READY, 1, 1),
)
DBS_HEALTH = _max_sev(
    _sev_low(PG_EXPORTERS_UP, 2, 1),
    _sev_high(f"({PG_CONN_MAX})", SOFT_CONN, HARD_CONN),
    _sev_high(f"({PG_PVC})", 75, 90),
    _sev_high(f"({PG_IDLE_MAX})", SOFT_IDLE_XACT, HARD_IDLE_XACT),
)
PIPELINE_HEALTH = _max_sev(
    _sev_down_ksm(AF_SCHED),
    _sev_high(f"({AF_FAIL})", 5, 20),
    _sev_high(f"({AF_DAG_FAIL})", 1, 3),
    _sev_high(f"({BROKEN})", 1, 2),
    _sev_high(f"({CTM})", SOFT_CTM, HARD_CTM),
)
APIS_HEALTH = _max_sev(
    _sev_down_ksm(API_PORTAL_UP),
    _sev_down_ksm(API_CORE_UP),
    _sev_high(api_error_pct("api-portal"), 1, 5),
    _sev_high(api_error_pct("api-core"), 1, 5),
)
OBS_HEALTH = _max_sev(
    _sev_down(PROM_UP),
    _sev_down(GRAFANA_UP),
    _sev_high(OBS_TARGETS_DOWN, 1, 3),
)


