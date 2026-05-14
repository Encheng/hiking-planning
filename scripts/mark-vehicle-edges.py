#!/usr/bin/env python3
"""Mark vehicle drive edges with transport='vehicle' to suppress speed warnings.

A vehicle drive is identified by:
- haversine distance > 5 km
- minutes_forward < (km * 10)  i.e. speed > 6 km/h average
  (hiking is typically 2-5 km/h; vehicle drives are 20+ km/h)
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"


def haversine_km(a: dict, b: dict) -> float:
    R = 6371
    dlat = math.radians(b["lat"] - a["lat"])
    dlng = math.radians(b["lng"] - a["lng"])
    aa = (math.sin(dlat / 2) ** 2 +
          math.cos(math.radians(a["lat"])) * math.cos(math.radians(b["lat"])) *
          math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(aa), math.sqrt(1 - aa))


def main():
    total = 0
    for path in sorted(ROUTES_DIR.glob("G*.json")):
        with open(path) as f:
            route = json.load(f)
        nodes_by_id = {n["id"]: n for n in route["nodes"]}
        changed = 0
        for e in route["edges"]:
            if e.get("transport") == "vehicle":
                continue
            n_from = nodes_by_id.get(e["from"])
            n_to = nodes_by_id.get(e["to"])
            if not n_from or not n_to:
                continue
            km = haversine_km(n_from, n_to)
            fwd = e["minutes_forward"]
            if km > 5 and fwd > 0:
                speed = km / (fwd / 60)
                if speed > 8:  # > 8 km/h = clearly not hiking
                    e["transport"] = "vehicle"
                    changed += 1
                    print(f"  {route['id']}: {n_from['name']} → {n_to['name']} "
                          f"({km:.1f}km, {fwd}min, {speed:.0f}km/h)")
        if changed:
            with open(path, "w") as f:
                json.dump(route, f, ensure_ascii=False, indent=2)
            with open(path, "a") as f:
                f.write("\n")
            total += changed
    print(f"\nTotal: {total} edges marked as vehicle")


if __name__ == "__main__":
    main()
