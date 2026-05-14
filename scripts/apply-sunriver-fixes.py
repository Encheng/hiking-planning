#!/usr/bin/env python3
"""Apply 上河圖 reference times to a route JSON.

For each segment in the YAML reference where the edge exists in the route,
update minutes_forward and minutes_backward to match the 上河 values
(taking direction into account based on node elevations).

Usage: python3 scripts/apply-sunriver-fixes.py G02 [--dry-run]
"""
import json
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"
VER_DIR = ROOT / "docs" / "verification"


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: apply-sunriver-fixes.py <route_id> [--dry-run]")
    route_id = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    route_path = ROUTES_DIR / f"{route_id}.json"
    yaml_path = VER_DIR / f"{route_id}-sunriver-source.yaml"

    with open(route_path) as f:
        route = json.load(f)
    with open(yaml_path) as f:
        ref = yaml.safe_load(f)

    nodes_by_name = {n["name"]: n for n in route["nodes"]}
    edges_by_pair: dict[tuple[str, str], int] = {}
    for idx, e in enumerate(route["edges"]):
        key = tuple(sorted([e["from"], e["to"]]))
        edges_by_pair[key] = idx

    updates: list[str] = []
    for seg in ref["segments"]:
        n_from = nodes_by_name.get(seg["from"])
        n_to = nodes_by_name.get(seg["to"])
        if not n_from or not n_to:
            continue

        elev_from = n_from.get("elevation") or 0
        elev_to = n_to.get("elevation") or 0
        if elev_from < elev_to:
            low_id, high_id = n_from["id"], n_to["id"]
        else:
            low_id, high_id = n_to["id"], n_from["id"]

        key = tuple(sorted([low_id, high_id]))
        edge_idx = edges_by_pair.get(key)
        if edge_idx is None:
            continue

        edge = route["edges"][edge_idx]
        old_fwd = edge["minutes_forward"]
        old_bwd = edge["minutes_backward"]

        # Determine correct fwd/bwd based on edge.from
        if edge["from"] == low_id:
            new_fwd = seg["up_min"]
            new_bwd = seg["down_min"]
        else:
            new_fwd = seg["down_min"]
            new_bwd = seg["up_min"]

        if new_fwd != old_fwd or new_bwd != old_bwd:
            updates.append(
                f"{nodes_by_name[seg['from']]['name']} ↔ {nodes_by_name[seg['to']]['name']}: "
                f"fwd {old_fwd}→{new_fwd}, bwd {old_bwd}→{new_bwd}"
            )
            edge["minutes_forward"] = new_fwd
            edge["minutes_backward"] = new_bwd
            edge["source"] = "上河圖"
            edge["confirmed"] = True

    print(f"Updates: {len(updates)}")
    for u in updates:
        print(f"  {u}")

    if not dry_run:
        with open(route_path, "w") as f:
            json.dump(route, f, ensure_ascii=False, indent=2)
        with open(route_path, "a") as f:
            f.write("\n")
        print(f"Wrote {route_path}")
    else:
        print("(dry-run, no changes saved)")


if __name__ == "__main__":
    main()
