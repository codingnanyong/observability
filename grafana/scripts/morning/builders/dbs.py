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


def build_dbs():
    """L2: one occupancy strip per DB cluster → L3 morning-db?var-job=…"""
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**DBs** · [← Status](/d/morning-overview) · "
        + " · ".join(f"[{c['id']}](/d/morning-db?var-job={c['job']})" for c in DB_CLUSTERS)
        + "\n\n클러스터별 점유율 · 클릭 → DB 상세 · Conn Soft 70 · Hard 85"
    ), y)); pid += 1; y += INTRO_H
    for c in DB_CLUSTERS:
        job, title = c["job"], c["title"]
        url = f"/d/morning-db?var-job={job}"
        p.append(row(pid, f"{title} · 클릭 → 상세", y)); pid += 1; y += 1
        cards = [
            ("Exporter", pg_up(job), "short", None, None, None, True),
            ("Conn %", pg_conn(job), "percent", SOFT_CONN, HARD_CONN, 100, False),
            ("Replica Lag", pg_lag(job), "s", 30, 120, None, False),
        ]
        if c["runtime"] == "k8s":
            cards.append(("PVC %", PG_PVC, "percent", 75, 90, 100, False))
        else:
            cards.append((
                "Backends",
                f'sum(pg_stat_database_numbackends{{job="{job}",datname!~"template.*|postgres"}}) or vector(0)',
                "short", None, None, None, False,
            ))
        w = 24 // len(cards)
        db_desc = {
            "Exporter": "pg_up ∧ scrape UP.",
            "Conn %": "max_connections 대비 backend 사용률.",
            "Replica Lag": "복제 lag(초).",
            "PVC %": "K8s PVC 사용률.",
            "Backends": "현재 backend 연결 수.",
        }
        for i, (t, e, u, s, h, m, is_up) in enumerate(cards):
            desc = db_desc.get(t, "")
            thn = thresh_note(s, h)
            if thn:
                desc = f"{desc} {thn}".strip()
            p.append(stat(pid, t, i * w, y, w, 5, e, unit=u, soft=s, hard=h, max_v=m,
                          links=link(url), description=desc))
            if is_up:
                p[-1]["fieldConfig"]["defaults"]["mappings"] = up_map()
                p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                    "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
            pid += 1
        y += 5
    write(dash("morning-dbs", "Morning · DBs", p,
               nav(back=("← Status", "/d/morning-overview")), tags=["morning", "dbs", MORNING_NAV_TAG]))


def build_db():
    """L3: single DB cluster detail (job variable)."""
    job = "$job"
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**DB · ${job}** · [← DBs](/d/morning-dbs) · [← Status](/d/morning-overview)\n\n"
        "① 점유 → ② TPS/Cache/Idle-in-xact → ③ database별\n\n"
        f"Conn Soft {SOFT_CONN} · Idle-in-xact Soft {SOFT_IDLE_XACT}s · 드롭다운으로 클러스터 전환"
    ), y)); pid += 1; y += INTRO_H
    p.append(row(pid, "① 점유/상태", y)); pid += 1; y += 1
    cards_x = [0, 5, 10, 15, 20]
    cards_w = [5, 5, 5, 5, 4]
    for i, (t, e, u, s, h, m, desc) in enumerate([
        ("Exporter", pg_up(job), "short", None, None, None, "pg_up ∧ scrape UP."),
        ("Conn %", pg_conn(job), "percent", SOFT_CONN, HARD_CONN, 100, "max_connections 대비 backend 사용률."),
        ("Idle-in-xact", pg_idle_xact(job), "s", SOFT_IDLE_XACT, HARD_IDLE_XACT, None,
         "idle in transaction 최장 시간. 길면 락/연결 누수 의."),
        ("Replica Lag", pg_lag(job), "s", 30, 120, None, "복제 lag(초)."),
        ("PVC % (K8s)", PG_PVC, "percent", 75, 90, 100, "K8s PVC 사용률 (Docker PG는 해당 없음 가능)."),
    ]):
        thn = thresh_note(s, h)
        if thn:
            desc = f"{desc} {thn}"
        p.append(stat(pid, t, cards_x[i], y, cards_w[i], 4, e,
                      unit=u, soft=s, hard=h, max_v=m, description=desc))
        if t == "Exporter":
            p[-1]["fieldConfig"]["defaults"]["mappings"] = up_map()
            p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}]}
        pid += 1
    y += 4
    p.append(row(pid, "② 성능 (트렌드)", y)); pid += 1; y += 1
    p.append(timeseries(pid, "Connections %", 0, y, 12, 7, [(pg_conn(job), "Conn%")],
                        unit="percent", soft=SOFT_CONN, hard=HARD_CONN, max_v=100,
                        description=thresh_note(SOFT_CONN, HARD_CONN))); pid += 1
    p.append(timeseries(pid, "Idle in transaction (max s)", 12, y, 12, 7, [
        (f'max by (datname) (pg_stat_activity_max_tx_duration{{state="idle in transaction",job="{job}",datname!~"template.*|postgres"}})', "{{datname}}"),
    ], unit="s", soft=SOFT_IDLE_XACT, hard=HARD_IDLE_XACT,
       description="DB별 idle-in-xact 최장. Soft 2m · Hard 5m")); pid += 1
    y += 7
    p.append(timeseries(pid, "TPS (xact commit/s)", 0, y, 12, 7, [
        (f'sum(rate(pg_stat_database_xact_commit{{job="{job}",datname!~"template.*|postgres"}}[5m])) or vector(0)', "commit/s"),
        (f'sum(rate(pg_stat_database_xact_rollback{{job="{job}",datname!~"template.*|postgres"}}[5m])) or vector(0)', "rollback/s"),
    ])); pid += 1
    p.append(timeseries(pid, "Cache Hit % (높을수록 좋음)", 12, y, 12, 7, [
        (f'(sum(rate(pg_stat_database_blks_hit{{job="{job}",datname!~"template.*|postgres"}}[5m])) / '
         f'clamp_min(sum(rate(pg_stat_database_blks_hit{{job="{job}",datname!~"template.*|postgres"}}[5m])) + '
         f'sum(rate(pg_stat_database_blks_read{{job="{job}",datname!~"template.*|postgres"}}[5m])), 1e-9) * 100) or vector(0)', "hit%"),
        ("vector(95)", "Warn <95"),
        ("vector(99)", "Good ≥99"),
    ], unit="percent", max_v=100,
       description="공유 버퍼 캐시 적중률. 99% 이상이면 양호, 95% 미만이면 점검.")); pid += 1
    p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
        "mode": "absolute",
        "steps": [{"color": "red", "value": None}, {"color": "orange", "value": 95}, {"color": "green", "value": 99}],
    }
    p[-1]["fieldConfig"]["overrides"].extend([
        {"matcher": {"id": "byName", "options": "Warn <95"},
         "properties": [
             {"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}},
             {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 5]}},
             {"id": "custom.fillOpacity", "value": 0}, {"id": "custom.lineWidth", "value": 2}]},
        {"matcher": {"id": "byName", "options": "Good ≥99"},
         "properties": [
             {"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}},
             {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 5]}},
             {"id": "custom.fillOpacity", "value": 0}, {"id": "custom.lineWidth", "value": 2}]},
    ])
    y += 7
    p.append(timeseries(pid, "Deadlocks", 0, y, 12, 7, [
        (f'sum(increase(pg_stat_database_deadlocks{{job="{job}",datname!~"template.*|postgres"}}[5m])) or vector(0)', "deadlocks 5m"),
    ], soft=1, hard=3)); pid += 1
    y += 7
    p.append(row(pid, "③ database별 (형제)", y)); pid += 1; y += 1
    p.append(table(pid, "Connections by Database", 0, y, 12, 10,
        f'sum by (datname) (pg_stat_database_numbackends{{job="{job}",datname!~"template.*|postgres"}})',
        rename={"datname": "Database", "Value": "Backends"}, sort_field="Backends")); pid += 1
    p.append(table(pid, "Database Size", 12, y, 12, 10,
        f'sum by (datname) (pg_database_size_bytes{{job="{job}",datname!~"template.*|postgres"}})',
        rename={"datname": "Database", "Value": "Size"}, sort_field="Size",
        unit_overrides=[{"matcher": {"id": "byName", "options": "Size"},
                         "properties": [{"id": "unit", "value": "bytes"}]}])); pid += 1
    job_opts = [{"text": c["job"], "value": c["job"], "selected": i == 0} for i, c in enumerate(DB_CLUSTERS)]
    write(dash("morning-db", "Morning · DB", p,
               nav(back=("← DBs", "/d/morning-dbs")), tags=["morning", "dbs"], templating=[{
        "name": "job", "type": "custom", "label": "DB cluster (job)",
        "query": ",".join(c["job"] for c in DB_CLUSTERS),
        "current": {"text": DB_CLUSTERS[0]["job"], "value": DB_CLUSTERS[0]["job"]},
        "options": job_opts,
        "includeAll": False, "multi": False,
    }], time_from="now-6h"))


