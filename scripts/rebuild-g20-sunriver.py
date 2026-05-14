#!/usr/bin/env python3
"""Rebuild G20 北大武山 from 上河文化 G20_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    ("n_g20_chaozhou",       "潮州",            22.55000, 120.55000, 50, "trailhead"),    #EST
    ("n_g20_wanluan",        "萬巒",            22.57000, 120.62000, 80, "trailhead"),    #EST
    ("n_g20_taiwu",          "泰武",            22.58000, 120.68000, 600, "trailhead"),   #EST
    ("n_g20_new_th",         "新登山口",        22.63000, 120.69500, 1500, "trailhead"),  #EST
    ("n_g20_old_th",         "舊登山口(0K)",    22.63500, 120.70000, 1700, "trailhead"),  #EST
    ("n_g20_ridge_pass",     "1.75K越嶺鞍部",   22.63800, 120.70500, 1850, "junction"),   #EST
    ("n_g20_lookout",        "3.8K展望平台",    22.64500, 120.71200, 2000, "waypoint"),   #EST
    ("n_g20_4k_jct",         "4K三岔路口",      22.64800, 120.71700, 2050, "junction"),   #EST
    ("n_g20_kuiku_hut",      "檜谷山莊",        22.65000, 120.72000, 2150, "hut"),        #EST
    ("n_g20_southview",      "南大武山展望點",  22.64900, 120.72200, 2200, "waypoint"),   #EST
    ("n_g20_5_5k_tree",      "5.5K大武神木",    22.65200, 120.72500, 2400, "waypoint"),   #EST
    ("n_g20_6_3k_water",     "6.3K最後水源",    22.65300, 120.73000, 2600, "water"),     #EST
    ("n_g20_main_ridge",     "主稜嶺線",        22.65700, 120.73500, 2850, "junction"),   #EST
    ("n_g20_8k_wushrine",    "8K大武祠",        22.62926, 120.74930, 3030, "waypoint"),   #OSM-est (大武祠 historic)
    ("n_g20_9k_north_dawu",  "9K北大武山",      22.62800, 120.75800, 3092, "peak"),       #OSM
    ("n_g20_to_wutu",        "往霧頭山",        22.66000, 120.74000, 2900, "junction"),   #EST (arrow only)
    ("n_g20_to_south_dawu",  "往南大武山",      22.64000, 120.74500, 2950, "junction"),   #EST (arrow only)
]


EDGES = [
    # === 接駁公路 (車) ===
    ("n_g20_chaozhou", "n_g20_wanluan", 10, 10),   # vehicle
    ("n_g20_wanluan", "n_g20_taiwu", 20, 20),      # vehicle
    ("n_g20_taiwu", "n_g20_new_th", 50, 50),       # vehicle (50分 顯示車輛圖示)
    # 新登山口 ↔ 舊登山口 (上河 100/70)
    # 新登山口 lower, 舊登山口 higher
    ("n_g20_new_th", "n_g20_old_th", 100, 70),
    # 舊登山口 → 1.75K越嶺鞍部 (UP 90, DOWN 60)
    ("n_g20_old_th", "n_g20_ridge_pass", 90, 60),
    # 1.75K越嶺鞍部 → 3.8K展望平台 (UP 90, DOWN 60)
    ("n_g20_ridge_pass", "n_g20_lookout", 90, 60),
    # 3.8K展望平台 → 4K三岔路口 (10/10)
    ("n_g20_lookout", "n_g20_4k_jct", 10, 10),
    # 4K三岔路口 → 檜谷山莊 (5/5)
    ("n_g20_4k_jct", "n_g20_kuiku_hut", 5, 5),
    # 4K三岔路口 → 南大武山展望點 (UP 60, DOWN 40)
    ("n_g20_4k_jct", "n_g20_southview", 60, 40),
    # 南大武山展望點 → 5.5K大武神木 (UP 30, DOWN 20)
    ("n_g20_southview", "n_g20_5_5k_tree", 30, 20),
    # 5.5K大武神木 → 6.3K最後水源 (UP 65, DOWN 50)
    ("n_g20_5_5k_tree", "n_g20_6_3k_water", 65, 50),
    # 6.3K最後水源 → 主稜嶺線 (UP 65, DOWN 40)
    ("n_g20_6_3k_water", "n_g20_main_ridge", 65, 40),
    # 主稜嶺線 → 8K大武祠 (DOWN 40, UP 65)
    # 大武祠(3030) > 主稜嶺(2850) - so 嶺線→大武祠 是 UP
    # 上河 "40/65" smaller=down: 40 DOWN (大武祠→主稜嶺), 65 UP
    # 但實際 主稜嶺(2850) → 大武祠(3030) UP, edge fwd should be 65
    ("n_g20_main_ridge", "n_g20_8k_wushrine", 65, 40),
    # 8K大武祠 → 9K北大武山 (UP 55, DOWN 65)
    # 上河 65/55: 55 down (北大武→大武祠), 65 up
    ("n_g20_8k_wushrine", "n_g20_9k_north_dawu", 55, 65),
    # 北大武山 → 往霧頭山 (arrow)
    ("n_g20_9k_north_dawu", "n_g20_to_wutu", 60, 60),
    # 主稜嶺線 → 往南大武 (arrow)
    ("n_g20_main_ridge", "n_g20_to_south_dawu", 60, 60),
]


PRESETS = [
    {
        "id": "G20-standard",
        "name": "北大武山標準行程 (2天1夜)",
        "startNodeId": "n_g20_new_th",
        "endNodeId": "n_g20_9k_north_dawu",
        "viaNodeIds": [
            "n_g20_old_th", "n_g20_ridge_pass", "n_g20_lookout",
            "n_g20_4k_jct", "n_g20_kuiku_hut", "n_g20_southview",
            "n_g20_5_5k_tree", "n_g20_6_3k_water", "n_g20_main_ridge",
            "n_g20_8k_wushrine",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g20_kuiku_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
]


def build():
    route = {
        "id": "G20",
        "name": "北大武山登峰",
        "version": "2026-05-14",
        "source": "上河文化 G20 北大武山步程示意圖 (G20_hiking.jpg)",
        "nodes": [
            {"id": nid, "name": name, "lat": lat, "lng": lng,
             "elevation": elev, "category": cat}
            for (nid, name, lat, lng, elev, cat) in NODES
        ],
        "edges": [
            {"from": f, "to": t,
             "minutes_forward": fwd, "minutes_backward": bwd,
             "source": "上河圖", "confirmed": True}
            for (f, t, fwd, bwd) in EDGES
        ],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G20.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G20 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
