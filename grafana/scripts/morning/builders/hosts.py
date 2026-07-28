"""Morning dashboard builders."""
from __future__ import annotations

from ..constants import (
    DS, HOST_NODES, INTRO_H, MORNING_NAV_TAG, SOFT_CPU, HARD_CPU, SOFT_CTM, HARD_CTM,
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


def build_hosts_l2():
    p, pid, y = [], 1, 0
    node_links = " · ".join(
        f"[{n}](/d/morning-host-node?var-node={n})" for n in HOST_NODES
    )
    p.append(text(pid, (
        "**Hosts** · [← Status](/d/morning-overview) · "
        f"[K8s](/d/morning-k8s) · {node_links}\n\n"
        "① **K8s 클러스터** → ② Host 점유율 → 클릭 시 OS · Pod · Docker · Soft 80 · Hard 90"
    ), y)); pid += 1; y += INTRO_H

    # ① Cluster K8s (legacy / cluster-wide) — top of Hosts
    k8s_url = "/d/morning-k8s"
    p.append(row(pid, "K8s 클러스터 · 클릭 → 상세 (legacy)", y)); pid += 1; y += 1
    for i, (t, e, soft, hard, inv, maps) in enumerate([
        ("Nodes Ready", 'sum(kube_node_status_condition{condition="Ready",status="true"}) or vector(0)', 1, 2, True, None),
        ("Nodes NotReady", 'sum(kube_node_status_condition{condition="Ready",status="false"} == 1) or vector(0)', 1, 2, False, None),
        ("Bad Pods", BAD_PODS, 1, 3, False, None),
        ("Deploy Gaps", DEPLOY_GAPS, 1, 3, False, None),
    ]):
        desc = {
            "Nodes Ready": "Ready=True 노드 수.",
            "Nodes NotReady": "Ready=False 노드 수.",
            "Bad Pods": "Failed/Unknown phase Pod 수.",
            "Deploy Gaps": "unavailable replica 합.",
        }.get(t, "")
        thn = thresh_note(soft, hard, invert=inv)
        if thn:
            desc = f"{desc} {thn}".strip()
        p.append(stat(
            pid, t, i * 6, y, 6, 5, e, soft=soft, hard=hard, invert=inv, mappings=maps,
            links=link(k8s_url, "K8s 상세"), max_v=2 if inv else None,
            description=desc,
        ))
        pid += 1
    y += 5

    # ② Per-host occupancy (HOST_NODES from site_local.py)
    for node in HOST_NODES:
        url = f"/d/morning-host-node?var-node={node}"
        p.append(row(pid, f"{node} · 클릭 → OS / Pod / Docker", y)); pid += 1; y += 1
        cards = [
            ("Ready", f'max(kube_node_status_condition{{node="{node}",condition="Ready",status="true"}})', "short", True),
            ("CPU %", f'max({cpu_by_inst(node)})', "percent", False),
            ("Memory %", f'max({mem_by_inst(node)})', "percent", False),
            ("Disk / %", f'max({disk_by_inst(node)})', "percent", False),
            ("Disk /media %", f'max({disk_by_inst(node, "/media")})', "percent", False),
        ]
        widths = [4, 5, 5, 5, 5]
        x = 0
        for (title, expr, unit, is_up), w in zip(cards, widths):
            if is_up:
                p.append(stat(pid, title, x, y, w, 4, expr, unit=unit, mappings=up_map(),
                              links=link(url), description=f"{node} 노드 Ready 조건."))
                p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                    "mode": "absolute",
                    "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}],
                }
            else:
                p.append(stat(pid, title, x, y, w, 4, expr, unit=unit, soft=SOFT_CPU, hard=HARD_CPU,
                              max_v=100, links=link(url),
                              description=f"{node} · {thresh_note(SOFT_CPU, HARD_CPU)}"))
            pid += 1; x += w
        y += 4
    write(dash("morning-hosts", "Morning · Hosts", p,
               nav(back=("← Status", "/d/morning-overview")), tags=["morning", "hosts", MORNING_NAV_TAG]))


def build_host_node():
    p, pid, y = [], 1, 0
    p.append(text(pid, (
        "**Host · ${node}** · [← Hosts](/d/morning-hosts) · [← Status](/d/morning-overview)\n\n"
        "① 점유율 (= Overview recording) → ② 같은 지표 트렌드 → ③ K8s|Docker\n\n"
        "Soft 80 · Hard 90 · Node 드롭다운으로 전환"
    ), y)); pid += 1; y += INTRO_H

    p.append(row(pid, "① 점유율", y)); pid += 1; y += 1
    for i, (title, expr, unit, soft, hard, mx, maps) in enumerate([
        ("Ready", 'max(kube_node_status_condition{node="$node",condition="Ready",status="true"})', "short", None, None, None, up_map()),
        ("CPU %", f'max({cpu_by_inst("$node")})', "percent", SOFT_CPU, HARD_CPU, 100, None),
        ("Memory %", f'max({mem_by_inst("$node")})', "percent", SOFT_CPU, HARD_CPU, 100, None),
        ("Disk / %", f'max({disk_by_inst("$node")})', "percent", SOFT_CPU, HARD_CPU, 100, None),
        ("Available GB", '(node_memory_MemAvailable_bytes{instance="$node",job="node-exporter"} / 1024 / 1024 / 1024)', "decgbytes", None, None, None, None),
    ]):
        w, x = 4 if i == 0 else 5, (0 if i == 0 else 4 + (i - 1) * 5)
        if i == 4:
            x, w = 19, 5
        p.append(stat(pid, title, x, y, w, 4, expr, unit=unit, soft=soft, hard=hard, max_v=mx, mappings=maps))
        if maps:
            p[-1]["fieldConfig"]["defaults"]["thresholds"] = {
                "mode": "absolute",
                "steps": [{"color": "red", "value": None}, {"color": "green", "value": 1}],
            }
        pid += 1
    y += 4

    p.append(row(pid, "② OS 성능 (지표 · 트렌드)", y)); pid += 1; y += 1
    # Trends use the same recording metrics as ① so the latest point matches the strip above.
    p.append(timeseries(pid, "CPU %", 0, y, 8, 7, [
        (cpu_by_inst("$node"), "CPU"),
        ('max(rate(node_cpu_seconds_total{instance="$node",job="node-exporter",mode="iowait"}[5m]) * 100)', "iowait"),
    ], unit="percent", soft=SOFT_CPU, hard=HARD_CPU, max_v=100)); pid += 1
    p.append(timeseries(pid, "Memory %", 8, y, 8, 7, [
        (mem_by_inst("$node"), "used"),
        ('max((node_memory_SwapTotal_bytes{instance="$node",job="node-exporter"} - node_memory_SwapFree_bytes{instance="$node",job="node-exporter"}) / clamp_min(node_memory_SwapTotal_bytes{instance="$node",job="node-exporter"}, 1) * 100)', "swap"),
    ], unit="percent", soft=SOFT_CPU, hard=HARD_CPU, max_v=100)); pid += 1
    p.append(timeseries(pid, "Disk / Load", 16, y, 8, 7, [
        (disk_by_inst("$node"), "/"),
        ('node_load1{instance="$node",job="node-exporter"}', "load1"),
    ], unit="short", soft=SOFT_CPU, hard=HARD_CPU)); pid += 1
    y += 7
    p.append(timeseries(pid, "Network / errors / drops", 0, y, 24, 7, [
        ('sum(rate(node_network_receive_bytes_total{instance="$node",job="node-exporter",device!~"lo|veth.*|cali.*|flannel.*|docker.*|br-.*"}[5m]))', "rx B/s"),
        ('sum(rate(node_network_transmit_bytes_total{instance="$node",job="node-exporter",device!~"lo|veth.*|cali.*|flannel.*|docker.*|br-.*"}[5m]))', "tx B/s"),
        ('sum(rate(node_network_receive_errs_total{instance="$node",job="node-exporter"}[5m]))', "rx err/s"),
        ('sum(rate(node_network_receive_drop_total{instance="$node",job="node-exporter"}[5m]))', "rx drop/s"),
    ], unit="short")); pid += 1
    y += 7

    p.append(row(pid, "③ 런타임 · Kubernetes (이 노드 Pod)", y)); pid += 1; y += 1
    p.append(table(pid, "K8s Pods · CPU", 0, y, 12, 9,
        'topk(12, sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{node="$node",container!="",container!="POD"}[5m])))',
        rename={"namespace": "Namespace", "pod": "Pod", "Value": "CPU cores"}, sort_field="CPU cores",
        description="이 노드에서 CPU 사용량 상위 Pod.")); pid += 1
    p.append(table(pid, "K8s Pods · Memory", 12, y, 12, 9,
        'topk(12, sum by (namespace, pod) (container_memory_working_set_bytes{node="$node",container!="",container!="POD"}))',
        rename={"namespace": "Namespace", "pod": "Pod", "Value": "Memory"}, sort_field="Memory",
        unit_overrides=[{"matcher": {"id": "byName", "options": "Memory"},
                         "properties": [{"id": "unit", "value": "bytes"}]}])); pid += 1
    y += 9

    p.append(row(pid, "③ 런타임 · Docker (이 노드 container)", y)); pid += 1; y += 1
    p.append(table(pid, "Docker · CPU", 0, y, 12, 9,
        'topk(12, sum by (name, image) (rate(container_cpu_usage_seconds_total{job="cadvisor-docker",instance="$node",name!="",name!="/"}[5m])))',
        rename={"name": "Container", "image": "Image", "Value": "CPU cores"}, sort_field="CPU cores",
        description="호스트 Docker(비-K8s) 컨테이너 CPU 상위.")); pid += 1
    p.append(table(pid, "Docker · Memory", 12, y, 12, 9,
        'topk(12, sum by (name, image) (container_memory_working_set_bytes{job="cadvisor-docker",instance="$node",name!="",name!="/"}))',
        rename={"name": "Container", "image": "Image", "Value": "Memory"}, sort_field="Memory",
        unit_overrides=[{"matcher": {"id": "byName", "options": "Memory"},
                         "properties": [{"id": "unit", "value": "bytes"}]}])); pid += 1

    first = HOST_NODES[0] if HOST_NODES else "worker-01"
    write(dash("morning-host-node", "Morning · Host node", p,
               nav(back=("← Hosts", "/d/morning-hosts")), tags=["morning", "hosts", "node"], templating=[{
        "name": "node", "type": "custom", "label": "Node",
        "query": ",".join(HOST_NODES),
        "current": {"text": first, "value": first},
        "options": [
            {"text": n, "value": n, "selected": i == 0}
            for i, n in enumerate(HOST_NODES)
        ],
        "includeAll": False, "multi": False,
    }], time_from="now-6h"))


