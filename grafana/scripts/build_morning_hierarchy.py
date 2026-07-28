#!/usr/bin/env python3
"""CLI entrypoint: build Morning hierarchical dashboards (L1 → L2 → L3)."""
from __future__ import annotations

from morning import build_all


def main() -> None:
    build_all()
    print("done")


if __name__ == "__main__":
    main()
