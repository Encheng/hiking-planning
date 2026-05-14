#!/usr/bin/env python3
"""Check cross-route data consistency.

For nodes that appear in multiple routes (same name):
- Compare coordinates (should be very close, <100m)
- Compare elevations (should be identical or near identical)

For edges between common nodes:
- Compare times (should match if both routes describe the same trail)

Usage: python3 scripts/cross-route-consistency.py [G04 G05 ...]
"""
import json
import math
import sys
from pathlib import Path
from collections import defaultdict

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"


def haversine_km(a, b):
    R = 6371
    dlat = math.radians(b["lat"] - a["lat"])
    dlng = math.radians(b["lng"] - a["lng"])
    aa = (math.sin(dlat / 2) ** 2 +
          math.cos(math.radians(a["lat"])) * math.cos(math.radians(b["lat"])) *
          math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(aa), math.sqrt(1 - aa))


def load_route(rid):
    with open(ROUTES_DIR / f"{rid}.json") as f:
        return json.load(f)


def main():
    if len(sys.argv) > 1:
        route_ids = sys.argv[1:]
    else:
        route_ids = sorted([p.stem for p in ROUTES_DIR.glob("G*.json")])

    # Index: name → {route_id: node}
    nodes_by_name = defaultdict(dict)
    # Index: (low_name, high_name) → {route_id: (fwd, bwd, elev_change)}
    edges_by_pair = defaultdict(dict)

    for rid in route_ids:
        try:
            r = load_route(rid)
        except FileNotFoundError:
            continue
        node_by_id = {n["id"]: n for n in r["nodes"]}
        for n in r["nodes"]:
            nodes_by_name[n["name"]][rid] = n
        for e in r["edges"]:
            nf = node_by_id.get(e["from"])
            nt = node_by_id.get(e["to"])
            if not nf or not nt:
                continue
            n1, n2 = sorted([nf["name"], nt["name"]])
            key = (n1, n2)
            # Normalize direction: store time for n1→n2 direction
            if nf["name"] == n1:
                fwd_n1_to_n2 = e["minutes_forward"]
                bwd_n2_to_n1 = e["minutes_backward"]
            else:
                fwd_n1_to_n2 = e["minutes_backward"]
                bwd_n2_to_n1 = e["minutes_forward"]
            edges_by_pair[key][rid] = (fwd_n1_to_n2, bwd_n2_to_n1)

    print("# 跨路線資料一致性檢查\n")

    # Find nodes shared across routes
    shared_nodes = {n: rs for n, rs in nodes_by_name.items() if len(rs) > 1}
    print(f"共有 {len(shared_nodes)} 個節點出現在多條路線\n")

    # === Node coordinate/elev inconsistency ===
    print("## 節點座標 / 海拔不一致\n")
    node_issues = []
    for name, by_route in sorted(shared_nodes.items()):
        routes_list = sorted(by_route.keys())
        coords = [(rid, by_route[rid]["lat"], by_route[rid]["lng"],
                   by_route[rid].get("elevation")) for rid in routes_list]
        # Compare pairs
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                rid_a, lat_a, lng_a, elev_a = coords[i]
                rid_b, lat_b, lng_b, elev_b = coords[j]
                dist_km = haversine_km(
                    {"lat": lat_a, "lng": lng_a},
                    {"lat": lat_b, "lng": lng_b},
                )
                elev_diff = abs((elev_a or 0) - (elev_b or 0))
                if dist_km > 0.2 or elev_diff > 20:
                    node_issues.append({
                        "name": name, "a": rid_a, "b": rid_b,
                        "dist_m": dist_km * 1000, "elev_diff": elev_diff,
                        "lat_a": lat_a, "lng_a": lng_a, "elev_a": elev_a,
                        "lat_b": lat_b, "lng_b": lng_b, "elev_b": elev_b,
                    })
    if node_issues:
        for issue in node_issues:
            print(f"- **{issue['name']}**")
            print(f"  - {issue['a']}: ({issue['lat_a']:.4f},{issue['lng_a']:.4f}) "
                  f"elev={issue['elev_a']}")
            print(f"  - {issue['b']}: ({issue['lat_b']:.4f},{issue['lng_b']:.4f}) "
                  f"elev={issue['elev_b']}")
            print(f"  - **距離 {issue['dist_m']:.0f}m, 海拔差 {issue['elev_diff']}m**")
    else:
        print("✅ 所有共用節點座標/海拔一致\n")

    # === Edge time inconsistency ===
    print("\n## 邊時間不一致 (同樣兩個節點，不同路線給不同時間)\n")
    edge_issues = []
    for (n1, n2), by_route in sorted(edges_by_pair.items()):
        if len(by_route) < 2:
            continue
        routes_list = sorted(by_route.keys())
        # All times
        all_fwds = [by_route[r][0] for r in routes_list]
        all_bwds = [by_route[r][1] for r in routes_list]
        # Check variance
        if max(all_fwds) - min(all_fwds) > 5 or max(all_bwds) - min(all_bwds) > 5:
            edge_issues.append({
                "n1": n1, "n2": n2,
                "data": [(r, by_route[r][0], by_route[r][1]) for r in routes_list],
            })
    if edge_issues:
        for issue in edge_issues:
            print(f"- **{issue['n1']} ↔ {issue['n2']}**")
            for r, f, b in issue["data"]:
                print(f"  - {r}: {issue['n1']}→{issue['n2']} fwd={f}, bwd={b}")
    else:
        print("✅ 所有共用邊時間一致\n")

    # === Summary ===
    print("\n## 總結\n")
    print(f"- 共用節點: {len(shared_nodes)}")
    print(f"- 節點不一致: {len(node_issues)}")
    print(f"- 邊時間不一致: {len(edge_issues)}")


if __name__ == "__main__":
    main()
