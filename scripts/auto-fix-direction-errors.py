#!/usr/bin/env python3
"""Auto-fix edges where fwd/bwd are clearly reversed based on elevation.

Rule: when an edge connects two nodes with significant elevation difference (>=50m),
the UP direction must take MORE time than the DOWN direction (hiking physics).

For each edge:
- If from→to is UP (to higher elev) and fwd < bwd: swap (fwd should be larger)
- If from→to is DOWN (to lower elev) and fwd > bwd: swap (fwd should be smaller)

Skip edges where:
- Elevation difference < 50m (small enough that UP/DOWN can have similar times)
- Source is already "上河圖" (already verified)

Usage: python3 scripts/auto-fix-direction-errors.py [--route G02] [--dry-run]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"


def fix_route(route_id: str, dry_run: bool) -> tuple[int, list[str]]:
    path = ROUTES_DIR / f"{route_id}.json"
    if not path.exists():
        return 0, [f"{route_id}: file not found"]
    with open(path) as f:
        route = json.load(f)

    nodes_by_id = {n["id"]: n for n in route["nodes"]}
    changes: list[str] = []
    n_swapped = 0

    for e in route["edges"]:
        # NOTE: do not skip 上河圖-sourced — many were my own readings that
        # may have wrong elevation assumptions; heuristic is still valid.
        n_from = nodes_by_id.get(e["from"])
        n_to = nodes_by_id.get(e["to"])
        if not n_from or not n_to:
            continue

        elev_from = n_from.get("elevation") or 0
        elev_to = n_to.get("elevation") or 0
        delta = elev_to - elev_from
        if abs(delta) < 50:
            continue  # Too close to tell

        fwd = e["minutes_forward"]
        bwd = e["minutes_backward"]
        if fwd == bwd:
            continue

        # delta > 0: from→to is UP. fwd should be the LARGER value.
        # delta < 0: from→to is DOWN. fwd should be the SMALLER value.
        needs_swap = False
        if delta > 0 and fwd < bwd:
            needs_swap = True
        elif delta < 0 and fwd > bwd:
            needs_swap = True

        if needs_swap:
            direction = "UP" if delta > 0 else "DOWN"
            changes.append(
                f"  {n_from['name']}({elev_from}m) → {n_to['name']}({elev_to}m) "
                f"[{direction} {abs(delta)}m]: fwd {fwd}↔{bwd} bwd"
            )
            e["minutes_forward"], e["minutes_backward"] = bwd, fwd
            n_swapped += 1

    if n_swapped and not dry_run:
        with open(path, "w") as f:
            json.dump(route, f, ensure_ascii=False, indent=2)
        with open(path, "a") as f:
            f.write("\n")

    return n_swapped, changes


def main():
    dry_run = "--dry-run" in sys.argv
    if "--route" in sys.argv:
        idx = sys.argv.index("--route")
        route_ids = [sys.argv[idx + 1]]
    else:
        route_ids = sorted([p.stem for p in ROUTES_DIR.glob("G*.json")])

    print(f"# Auto-fix direction errors {'(DRY-RUN)' if dry_run else ''}\n")
    total = 0
    for rid in route_ids:
        n, changes = fix_route(rid, dry_run)
        if n > 0:
            print(f"\n## {rid}: {n} edge(s) swapped\n")
            for c in changes:
                print(c)
            total += n

    print(f"\n---\n總計修正 {total} 條邊")


if __name__ == "__main__":
    main()
