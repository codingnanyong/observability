"""Top-bar navigation links for Morning dashboards."""
from __future__ import annotations

from .constants import MORNING_NAV_TAG


def nav(*, back=None, extra=None):
    """back=("← Hosts", "/d/morning-hosts") — previous level (required off Overview).

    Layout: [← parent] · Status(if parent≠Status) · 이동▾
    """
    links = []
    back_url = back[1] if back else None
    if back:
        title, url = back
        links.append({
            "title": title, "type": "link", "icon": "doc",
            "url": url, "tooltip": title,
            "targetBlank": False, "keepTime": True,
            "asDropdown": False, "includeVars": False, "tags": [],
        })
    if back_url != "/d/morning-overview":
        links.append({
            "title": "Status", "type": "link", "icon": "info",
            "url": "/d/morning-overview", "tooltip": "Morning Status",
            "targetBlank": False, "keepTime": True,
            "asDropdown": False, "includeVars": False, "tags": [],
        })
    links.append({
        "title": "이동", "type": "dashboards", "icon": "dashboard",
        "tags": [MORNING_NAV_TAG], "asDropdown": True,
        "tooltip": "Hosts · DBs · Pipe · APIs · Obs",
        "targetBlank": False, "keepTime": True,
        "includeVars": False, "url": "",
    })
    for t, u, icon in (extra or []):
        links.append({
            "title": t, "type": "link", "icon": icon, "url": u,
            "tooltip": t, "targetBlank": False, "keepTime": True,
            "asDropdown": False, "includeVars": False, "tags": [],
        })
    return links
