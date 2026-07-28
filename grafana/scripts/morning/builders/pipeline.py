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


def build_datapipeline():
    """L2: Airflow + Kafka occupancy → L3 charts directly (no duplicate status page)."""
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**DataPipeline** · [← Status](/d/morning-overview) · "
        "[Airflow](/d/morning-airflow-perf) · [Kafka](/d/morning-kafka-perf)\n\n"
        "클릭 → **바로 차트/상세** · CTM Soft 150k · Task fail Soft ≥5"
    ), y)); pid += 1; y += INTRO_H

    af_url = "/d/morning-airflow-perf"
    p.append(row(pid, "Airflow · 클릭 → 차트/상세", y)); pid += 1; y += 1
    for i, (t, e, maps, soft, hard, desc) in enumerate([
        ("StatsD", 'max(up{job="airflow-statsd"}) or vector(0)', up_map(), None, None, "Airflow StatsD exporter scrape."),
        ("Scheduler", AF_SCHED, up_map(), None, None, "Scheduler Pod Ready."),
        ("Task fail 5m", AF_FAIL, None, 5, 20, "최근 5분 TI 실패 수."),
        ("Task OK 5m", AF_OK, None, None, None, "최근 5분 TI 성공 수."),
    ]):
        thn = thresh_note(soft, hard)
        if thn:
            desc = f"{desc} {thn}"
        p.append(stat(pid, t, i * 6, y, 6, 5, e, soft=soft, hard=hard, mappings=maps,
                      links=link(af_url), description=desc))
        if maps:
            p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
        pid += 1
    y += 5

    kf_url = "/d/morning-kafka-perf"
    p.append(row(pid, "Kafka · 클릭 → 차트/상세", y)); pid += 1; y += 1
    for i, (t, e, soft, hard, inv, desc) in enumerate([
        ("Brokers", KF_BROKERS, 2, 3, True, "Ready broker Pod 수."),
        ("Broken", BROKEN, 1, 2, False, "Running이 아닌 connector 수."),
        ("CTM Lag", CTM, SOFT_CTM, HARD_CTM, False, "CTM sink consumergroup lag 합."),
        ("Workers", 'count(kube_pod_status_ready{namespace="kafka",pod=~"kafka-connect-connect-.*",condition="true"}==1) or vector(0)', 1, 2, True, "Connect worker Ready 수."),
    ]):
        thn = thresh_note(soft, hard, invert=inv)
        if thn:
            desc = f"{desc} {thn}"
        p.append(stat(pid, t, i * 6, y, 6, 5, e, soft=soft, hard=hard, invert=inv,
                      links=link(kf_url), description=desc))
        pid += 1

    write(dash("morning-datapipeline", "Morning · DataPipeline", p,
               nav(back=("← Status", "/d/morning-overview")), tags=["morning", "datapipeline", MORNING_NAV_TAG]))


def build_airflow():
    # L3 only — status strip + charts (DataPipeline links here directly)
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**Airflow** · [← DataPipeline](/d/morning-datapipeline) · [← Status](/d/morning-overview)\n\n"
        "① 상태 → ② Duration/Delay/Active → ③ DAG 그룹\n\n"
        "DAG fail Soft ≥1"
    ), y)); pid += 1; y += INTRO_H
    p.append(row(pid, "① 상태", y)); pid += 1; y += 1
    for i, (t, e, soft, hard, desc) in enumerate([
        ("Scheduler", AF_SCHED, None, None, "Scheduler Pod Ready."),
        ("DAG fail 5m", AF_DAG_FAIL, 1, 3, "최근 5분 DAG run 실패 수."),
        ("Task fail 5m", AF_FAIL, 5, 20, "최근 5분 TI 실패 수."),
        ("Queued", 'sum(airflow_pool_queued_slots) or vector(0)', 20, 50, "pool queued slot 합."),
    ]):
        thn = thresh_note(soft, hard)
        if thn:
            desc = f"{desc} {thn}"
        p.append(stat(pid, t, i * 6, y, 6, 4, e, soft=soft, hard=hard, description=desc))
        if t == "Scheduler":
            p[-1]["fieldConfig"]["defaults"]["mappings"] = up_map()
            p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
        pid += 1
    y += 4
    p.append(row(pid, "② 성능 (트렌드)", y)); pid += 1; y += 1
    p.append(timeseries(pid, "DAG run duration (avg s)", 0, y, 12, 7, [
        ('avg(airflow_dagrun_duration) or vector(0)', "avg duration"),
    ], soft=300, hard=600, description=thresh_note(300, 600))); pid += 1
    p.append(timeseries(pid, "Schedule delay (avg s)", 12, y, 12, 7, [
        ('avg(airflow_dagrun_schedule_delay) or vector(0)', "delay"),
    ], soft=60, hard=180, description=thresh_note(60, 180))); pid += 1
    y += 7
    p.append(timeseries(pid, "Active DAG runs / TI fail", 0, y, 24, 7, [
        ('sum(airflow_dagrun_running) or vector(0)', "running DAGs"),
        (AF_FAIL, "TI fail 5m"),
        (AF_DAG_FAIL, "DAG fail 5m"),
    ])); pid += 1
    y += 7
    p.append(row(pid, "③ DAG 그룹 (형제)", y)); pid += 1; y += 1
    # Fail top by dag_id — StatsD may expose dag_id label on failures
    p.append(table(pid, "DAG fail Top (5m)", 0, y, 12, 10,
        'topk(15, sum by (dag_id) (increase(airflow_dagrun_failed_count[5m])) > 0) or topk(15, sum by (dag_id) (increase(airflow_ti_failures[5m])) > 0)',
        rename={"dag_id": "DAG", "Value": "Fails"}, sort_field="Fails",
        description="최근 5분 DAG/Task 실패가 있는 dag_id 상위.")); pid += 1
    p.append(table(pid, "DAG fail Top (1h)", 12, y, 12, 10,
        'topk(15, sum by (dag_id) (increase(airflow_dagrun_failed_count[1h])) > 0) or topk(15, sum by (dag_id) (increase(airflow_ti_failures[1h])) > 0)',
        rename={"dag_id": "DAG", "Value": "Fails"}, sort_field="Fails")); pid += 1
    write(dash("morning-airflow-perf", "Morning · Airflow", p,
               nav(back=("← Pipe", "/d/morning-datapipeline")), tags=["morning", "airflow", "datapipeline"], time_from="now-6h"))


def build_kafka():
    # L3 only — status strip + charts (DataPipeline links here directly)
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**Kafka** · [← DataPipeline](/d/morning-datapipeline) · [← Status](/d/morning-overview)\n\n"
        "① 상태 → ② 트렌드 → ③ Broker | Connect | CTM\n\n"
        "CTM Soft 150k · Hard 500k"
    ), y)); pid += 1; y += INTRO_H
    p.append(row(pid, "① 상태", y)); pid += 1; y += 1
    for i, (t, e, soft, hard, inv, desc) in enumerate([
        ("Brokers", KF_BROKERS, 2, 3, True, "Ready broker Pod 수."),
        ("Workers", 'count(kube_pod_status_ready{namespace="kafka",pod=~"kafka-connect-connect-.*",condition="true"}==1) or vector(0)', 1, 2, True, "Connect worker Ready 수."),
        ("Broken", BROKEN, 1, 2, False, "Running이 아닌 connector 수."),
        ("CTM Lag", CTM, SOFT_CTM, HARD_CTM, False, "CTM sink consumergroup lag 합."),
    ]):
        thn = thresh_note(soft, hard, invert=inv)
        if thn:
            desc = f"{desc} {thn}"
        p.append(stat(pid, t, i * 6, y, 6, 4, e, soft=soft, hard=hard, invert=inv, description=desc))
        pid += 1
    y += 4
    p.append(row(pid, "② 성능 (트렌드)", y)); pid += 1; y += 1
    p.append(timeseries(pid, "CTM Lag", 0, y, 12, 7, [
        ('sum by (consumergroup) (kafka_consumergroup_lag{consumergroup=~"connect-ctm-sink-.*"})', "{{consumergroup}}"),
    ], soft=SOFT_CTM, hard=HARD_CTM, description=thresh_note(SOFT_CTM, HARD_CTM))); pid += 1
    p.append(timeseries(pid, "Connect restarts / task failed", 12, y, 12, 7, [
        ('sum(increase(kube_pod_container_status_restarts_total{namespace="kafka",pod=~"kafka-connect-.*"}[1h])) or vector(0)', "restarts 1h"),
        ('sum(kafka_connect_connector_task_status{status="FAILED"}) or vector(0)', "tasks FAILED"),
    ])); pid += 1
    y += 7
    p.append(row(pid, "③ 구성요소 (형제)", y)); pid += 1; y += 1
    p.append(table(pid, "Brokers", 0, y, 8, 10,
        'max by (pod, phase) (kube_pod_status_phase{namespace="kafka",pod=~"kafka-cluster-combined-.*"} == 1)',
        rename={"pod": "Broker", "phase": "Phase", "Value": "V"}, sort_field="Broker",
        description="kafka broker Pod phase.")); pid += 1
    p.append(table(pid, "Connect · connectors", 8, y, 8, 10,
        'sum by (connector, state) (kafka_connect_connector_state == 1)',
        rename={"connector": "Connector", "state": "State", "Value": "Active"}, sort_field="Connector",
        description="현재 활성 state=1 인 connector만 표시.")); pid += 1
    p.append(table(pid, "CTM · consumergroup lag", 16, y, 8, 10,
        'sum by (consumergroup) (kafka_consumergroup_lag{consumergroup=~"connect-ctm-sink-.*"})',
        rename={"consumergroup": "Group", "Value": "Lag"}, sort_field="Lag")); pid += 1
    write(dash("morning-kafka-perf", "Morning · Kafka", p,
               nav(back=("← Pipe", "/d/morning-datapipeline")), tags=["morning", "kafka", "datapipeline"], time_from="now-6h"))


