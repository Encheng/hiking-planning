#!/usr/bin/env python3
"""Fix validation errors in G03-G20 route JSON files:
1. Set confirmed: true on all edges
2. Remove invalid hutId references not in huts.json
3. Convert dailyPlans-format presets to RoutePreset format
"""
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "public" / "data"
ROUTES_DIR = DATA_DIR / "routes"

# Load valid hut IDs
with open(DATA_DIR / "huts.json") as f:
    huts = json.load(f)
VALID_HUT_IDS = {h["id"] for h in huts}

VALID_BREAK_TYPES = {"hut", "camp", "shelter"}


def convert_preset(p: dict) -> dict:
    """Convert a dailyPlans-array preset to RoutePreset format."""
    if "dailyPlans" not in p:
        return p

    daily_plans = p["dailyPlans"]
    if not daily_plans:
        # Empty dailyPlans — can't determine endNodeId, skip conversion
        print(f"  WARNING: preset {p['id']} has empty dailyPlans, skipping")
        result = {k: v for k, v in p.items() if k not in ("dailyPlans", "notes", "endType")}
        return result

    via_nodes: list[str] = []
    suggested_breaks: list[dict] = []

    for i, day in enumerate(daily_plans):
        is_last = i == len(daily_plans) - 1
        day_vias = day.get("viaNodeIds", [])
        day_end = day["endNodeId"]
        end_type = day.get("endType", "manual")

        via_nodes.extend(day_vias)
        if not is_last:
            via_nodes.append(day_end)
            if end_type in VALID_BREAK_TYPES:
                suggested_breaks.append({"atNodeId": day_end, "type": end_type})

    final_end = daily_plans[-1]["endNodeId"]

    result = {
        "id": p["id"],
        "name": p["name"],
        "startNodeId": p["startNodeId"],
        "endNodeId": final_end,
    }
    if via_nodes:
        result["viaNodeIds"] = via_nodes
    if suggested_breaks:
        result["suggestedDayBreaks"] = suggested_breaks
    if "roundTrip" in p:
        result["roundTrip"] = p["roundTrip"]

    return result


def fix_route(path: Path) -> dict:
    with open(path) as f:
        route = json.load(f)

    route_id = route.get("id", path.stem)
    changes: list[str] = []

    # Fix 1: confirmed: true on all edges
    unconfirmed = 0
    for edge in route.get("edges", []):
        if edge.get("confirmed") is False:
            edge["confirmed"] = True
            unconfirmed += 1
    if unconfirmed:
        changes.append(f"confirmed {unconfirmed} edges")

    # Fix 2: remove invalid hutIds from nodes
    removed_hut_ids = 0
    for node in route.get("nodes", []):
        if "hutId" in node and node["hutId"] not in VALID_HUT_IDS:
            del node["hutId"]
            removed_hut_ids += 1
    if removed_hut_ids:
        changes.append(f"removed {removed_hut_ids} invalid hutId(s)")

    # Fix 3: convert dailyPlans presets
    converted = 0
    new_presets = []
    for preset in route.get("presets", []):
        if "dailyPlans" in preset:
            new_presets.append(convert_preset(preset))
            converted += 1
        else:
            new_presets.append(preset)
    if converted:
        route["presets"] = new_presets
        changes.append(f"converted {converted} preset(s) from dailyPlans format")

    if changes:
        print(f"  {route_id}: {', '.join(changes)}")
        with open(path, "w") as f:
            json.dump(route, f, ensure_ascii=False, indent=2)
        # Ensure trailing newline
        with open(path, "a") as f:
            f.write("\n")
    else:
        print(f"  {route_id}: no changes needed")

    return route


def main():
    routes = sorted(ROUTES_DIR.glob("G*.json"))
    # Skip G01 (skipped) and G02 (done, already correct)
    skip = {"G01.json", "G02.json"}
    routes = [r for r in routes if r.name not in skip]

    print(f"Fixing {len(routes)} route files...")
    for path in routes:
        fix_route(path)
    print("Done.")


if __name__ == "__main__":
    main()
