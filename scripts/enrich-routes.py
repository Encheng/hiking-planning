#!/usr/bin/env python3
"""Enrich route data with missing peaks (OSM-verified coordinates)."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "public" / "data"
ROUTES_DIR = DATA_DIR / "routes"


def load(gid):
    with open(ROUTES_DIR / f"{gid}.json") as f:
        return json.load(f)


def save(r):
    path = ROUTES_DIR / f"{r['id']}.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"  Saved {r['id']}")


def node_by_id(r, nid):
    return next((n for n in r["nodes"] if n["id"] == nid), None)


def remove_edge(r, from_id, to_id):
    before = len(r["edges"])
    r["edges"] = [e for e in r["edges"] if not (e["from"] == from_id and e["to"] == to_id)]
    return before - len(r["edges"])


def add_node(r, node):
    if not any(n["id"] == node["id"] for n in r["nodes"]):
        r["nodes"].append(node)
        return True
    return False


def add_edge(r, edge):
    exists = any(e["from"] == edge["from"] and e["to"] == edge["to"] for e in r["edges"])
    if not exists:
        r["edges"].append(edge)
        return True
    return False


def fix_coord(r, nid, lat, lng, elev=None):
    n = node_by_id(r, nid)
    if n:
        n["lat"] = lat
        n["lng"] = lng
        if elev is not None:
            n["elevation"] = elev
        return True
    return False


# ──────────────────────────────────────────────
# G09 合歡‧奇萊縱走
# ──────────────────────────────────────────────
def enrich_g09():
    r = load("G09")
    print("=== G09 ===")

    # 1. Fix existing node coordinates (vs OSM)
    # 合歡主峰: was 24.1490, 121.279 → OSM 24.1426062, 121.2711951
    fix_coord(r, "n_g09_hehuan_main", 24.1426062, 121.2711951, 3417)
    print("  Fixed 合歡主峰 coordinates")

    # 合歡北峰: was 24.156, 121.275 → OSM 24.1815125, 121.2815943
    fix_coord(r, "n_g09_hehuan_north", 24.1815125, 121.2815943, 3422)
    print("  Fixed 合歡北峰 coordinates")

    # 2. Add missing peaks
    added = 0
    added += add_node(r, {
        "id": "n_g09_hehuan_west",
        "name": "合歡西峰",
        "lat": 24.1776441, "lng": 121.2445400, "elevation": 3144,
        "category": "peak",
    })
    added += add_node(r, {
        "id": "n_g09_shimen_th",
        "name": "石門山登山口",
        "lat": 24.1473, "lng": 121.2870, "elevation": 3275,
        "category": "trailhead",
    })
    added += add_node(r, {
        "id": "n_g09_shimen",
        "name": "石門山",
        "lat": 24.1524223, "lng": 121.2845461, "elevation": 3236,
        "category": "peak",
    })
    added += add_node(r, {
        "id": "n_g09_hehuan_east",
        "name": "合歡東峰",
        "lat": 24.1356665, "lng": 121.2811125, "elevation": 3421,
        "category": "peak",
    })
    print(f"  Added {added} nodes (合歡西峰, 石門山登山口, 石門山, 合歡東峰)")

    # 3. Add edges
    # 合歡西峰 from trailhead (hehuan_th ← 管理站, NW direction to 西峰)
    add_edge(r, {"from": "n_g09_hehuan_th", "to": "n_g09_hehuan_west",
                 "minutes_forward": 110, "minutes_backward": 80,
                 "source": "estimated", "confirmed": True})
    # Also accessible from 合歡北峰 direction along ridge
    add_edge(r, {"from": "n_g09_hehuan_north", "to": "n_g09_hehuan_west",
                 "minutes_forward": 95, "minutes_backward": 100,
                 "source": "estimated", "confirmed": True})

    # 石門山登山口 ↔ 管理站 (short road connection, enables path-finding)
    add_edge(r, {"from": "n_g09_hehuan_th", "to": "n_g09_shimen_th",
                 "minutes_forward": 15, "minutes_backward": 15,
                 "source": "estimated", "confirmed": True})
    # 石門山登山口 → 石門山 (easy trail, ~0.8km)
    add_edge(r, {"from": "n_g09_shimen_th", "to": "n_g09_shimen",
                 "minutes_forward": 20, "minutes_backward": 15,
                 "source": "estimated", "confirmed": True})
    # 石門山 → 合歡東峰 (ridge south, ~1.9km)
    add_edge(r, {"from": "n_g09_shimen", "to": "n_g09_hehuan_east",
                 "minutes_forward": 40, "minutes_backward": 50,
                 "source": "estimated", "confirmed": True})
    # 合歡主峰 ↔ 合歡東峰 (ridge connection, ~1.3km)
    add_edge(r, {"from": "n_g09_hehuan_main", "to": "n_g09_hehuan_east",
                 "minutes_forward": 35, "minutes_backward": 40,
                 "source": "estimated", "confirmed": True})
    print("  Added edges for 合歡西峰/石門山/合歡東峰")

    # 4. Add preset for 石門山+合歡東峰 area hike
    preset_ids = [p["id"] for p in r["presets"]]
    if "G09-shimen-east" not in preset_ids:
        r["presets"].append({
            "id": "G09-shimen-east",
            "name": "石門山‧合歡東峰 (當日來回)",
            "startNodeId": "n_g09_shimen_th",
            "endNodeId": "n_g09_hehuan_east",
            "viaNodeIds": ["n_g09_shimen"],
            "roundTrip": True,
        })
        print("  Added preset: 石門山‧合歡東峰")

    save(r)


# ──────────────────────────────────────────────
# G04 聖稜 Y 型縱走 — 補北稜角
# ──────────────────────────────────────────────
def enrich_g04():
    r = load("G04")
    print("=== G04 ===")

    # 北稜角: OSM 3882m, lat 24.3875106, lon 121.2311408
    add_node(r, {
        "id": "n_g04_beling",
        "name": "北稜角",
        "lat": 24.3875106, "lng": 121.2311408, "elevation": 3882,
        "category": "peak",
    })
    print("  Added 北稜角")

    # Insert 北稜角 between 雪北山屋 and 雪山主峰
    # Route order going south: 穆特勒布 → 雪北山屋 → 北稜角 → 雪山主峰 → 雪山山屋
    # Remove direct 雪北山屋 → 雪山山屋 edge (was 88 min, incorrect shortcut)
    removed = remove_edge(r, "n_g04_xuebei_hut", "n_g04_xueshan_hut")
    if removed:
        print("  Removed shortcut edge 雪北山屋 → 雪山山屋")

    # Add: 雪北山屋 → 北稜角 (main ridge traverse, ~2.6km south)
    add_edge(r, {"from": "n_g04_xuebei_hut", "to": "n_g04_beling",
                 "minutes_forward": 65, "minutes_backward": 80,
                 "source": "estimated", "confirmed": True})
    # Add: 北稜角 → 雪山主峰 (very close, ~0.46km)
    add_edge(r, {"from": "n_g04_beling", "to": "n_g04_xueshan",
                 "minutes_forward": 20, "minutes_backward": 25,
                 "source": "estimated", "confirmed": True})
    # Add: 北稜角 → 雪山山屋 (descent via 翠池, ~1.5km)
    add_edge(r, {"from": "n_g04_beling", "to": "n_g04_xueshan_hut",
                 "minutes_forward": 45, "minutes_backward": 60,
                 "source": "estimated", "confirmed": True})
    print("  Added edges: 雪北山屋→北稜角, 北稜角→雪山主峰, 北稜角→雪山山屋")

    save(r)


# ──────────────────────────────────────────────
# G07 北一段縱走 — 補南湖大山北峰、陶塞峰
# ──────────────────────────────────────────────
def enrich_g07():
    r = load("G07")
    print("=== G07 ===")

    # Add 南湖大山北峰 (OSM 3563m, lat 24.3740058, lon 121.4417124)
    add_node(r, {
        "id": "n_g07_nanhu_north",
        "name": "南湖大山北峰",
        "lat": 24.3740058, "lng": 121.4417124, "elevation": 3563,
        "category": "peak",
    })
    # Add 陶塞峰 (OSM 3519m, lat 24.3590926, lon 121.4600372)
    add_node(r, {
        "id": "n_g07_taosei",
        "name": "陶塞峰",
        "lat": 24.3590926, "lng": 121.4600372, "elevation": 3519,
        "category": "peak",
    })
    print("  Added 南湖大山北峰, 陶塞峰")

    # Insert 南湖大山北峰 between 南湖北山附近營地 and 南湖大山
    # Current: 南湖北山附近營地 → 南湖大山 (71 min)
    # New: 南湖北山附近營地 → 南湖大山北峰 (40 min) → 南湖大山 (35 min)
    removed = remove_edge(r, "n_g07_nanhu_north_camp", "n_g07_nanhu_main")
    if removed:
        print("  Removed direct 南湖北山附近營地 → 南湖大山 edge")
    add_edge(r, {"from": "n_g07_nanhu_north_camp", "to": "n_g07_nanhu_north",
                 "minutes_forward": 40, "minutes_backward": 50,
                 "source": "estimated", "confirmed": True})
    add_edge(r, {"from": "n_g07_nanhu_north", "to": "n_g07_nanhu_main",
                 "minutes_forward": 35, "minutes_backward": 45,
                 "source": "estimated", "confirmed": True})

    # Insert 陶塞峰 between 南湖大山東峰 and 馬比杉山
    # Current: 南湖大山東峰 → 馬比杉山 (111 min)
    # New: 南湖大山東峰 → 陶塞峰 (30 min) → 馬比杉山 (70 min)
    removed = remove_edge(r, "n_g07_nanhu_east", "n_g07_mabisan")
    if removed:
        print("  Removed direct 南湖大山東峰 → 馬比杉山 edge")
    add_edge(r, {"from": "n_g07_nanhu_east", "to": "n_g07_taosei",
                 "minutes_forward": 30, "minutes_backward": 35,
                 "source": "estimated", "confirmed": True})
    add_edge(r, {"from": "n_g07_taosei", "to": "n_g07_mabisan",
                 "minutes_forward": 70, "minutes_backward": 60,
                 "source": "estimated", "confirmed": True})
    print("  Added edges for 南湖大山北峰 and 陶塞峰")

    save(r)


if __name__ == "__main__":
    enrich_g09()
    enrich_g04()
    enrich_g07()
    print("\nDone.")
