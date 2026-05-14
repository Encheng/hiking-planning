#!/usr/bin/env python3
"""Rebuild G03 郡大山‧西巒大山 from 上河文化 G03_hiking.jpg.

G03 contains two separate routes:
1. 郡大山 (top)
2. 西巒大山 (bottom)
"""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 郡大山 ===
    ("n_g03_shuili",         "水里",            23.81000, 120.85000, 280, "trailhead"),    #EST
    ("n_g03_18duo",          "十八重溪橋",      23.79000, 120.95000, 700, "trailhead"),    #EST
    ("n_g03_checkpoint",     "檢查哨",          23.78000, 120.97000, 800, "junction"),    #EST
    ("n_g03_23k_workshop",   "23K望鄉工作站",   23.71000, 121.05000, 2200, "trailhead"),  #EST
    ("n_g03_32k_th",         "32K登山口",       23.69000, 121.06500, 2900, "trailhead"),  #EST
    ("n_g03_wangxiang",      "望鄉山",          23.68500, 121.06800, 2900, "peak"),       #EST
    ("n_g03_junda_north",    "郡大山北峰",      23.68000, 121.07000, 3200, "peak"),       #EST
    ("n_g03_junda",          "郡大山",          23.66000, 121.07500, 3263, "peak"),       #EST

    # === 西巒大山 ===
    ("n_g03_xinyi",          "新山",            23.78000, 120.91000, 1100, "trailhead"),  #EST
    ("n_g03_17_1k_lan",      "17.1K欄柵",       23.73000, 120.96000, 2200, "junction"),   #EST
    ("n_g03_8_workshop",     "人造工作站",      23.72500, 120.96500, 2300, "shelter"),    #EST
    ("n_g03_yixiluan_1st",   "玉山第一登山口",  23.72000, 120.97000, 2400, "trailhead"),  #EST
    ("n_g03_xiluan_camp",    "森林營地",        23.71500, 120.97500, 2600, "waypoint"),   #EST
    ("n_g03_xiluan_view",    "瞭望台營地",      23.70500, 120.98000, 2800, "waypoint"),   #EST
    ("n_g03_xiluan_obs",     "展望點",          23.69500, 120.98500, 2900, "waypoint"),   #EST
    ("n_g03_xiluan",         "西巒大山",        23.69000, 120.99100, 3081, "peak"),       #EST
]


EDGES = [
    # === 郡大山 chain ===
    ("n_g03_shuili", "n_g03_18duo", 60, 60),     # vehicle
    ("n_g03_18duo", "n_g03_checkpoint", 80, 80),  # vehicle
    ("n_g03_checkpoint", "n_g03_23k_workshop", 65, 65), # vehicle
    ("n_g03_23k_workshop", "n_g03_32k_th", 80, 80),  # vehicle 林道
    ("n_g03_32k_th", "n_g03_wangxiang", 40, 25),
    ("n_g03_wangxiang", "n_g03_junda_north", 100, 60),
    ("n_g03_junda_north", "n_g03_junda", 65, 55),

    # === 西巒大山 chain ===
    ("n_g03_xinyi", "n_g03_17_1k_lan", 30, 30),  # 新箱及人造林道
    ("n_g03_17_1k_lan", "n_g03_8_workshop", 5, 5),
    ("n_g03_8_workshop", "n_g03_yixiluan_1st", 30, 5),
    ("n_g03_yixiluan_1st", "n_g03_xiluan_camp", 120, 80),
    ("n_g03_xiluan_camp", "n_g03_xiluan_view", 60, 45),
    ("n_g03_xiluan_view", "n_g03_xiluan_obs", 20, 15),
    ("n_g03_xiluan_obs", "n_g03_xiluan", 50, 30),
]


PRESETS = [
    {
        "id": "G03-junda",
        "name": "郡大山單登 (1日)",
        "startNodeId": "n_g03_32k_th",
        "endNodeId": "n_g03_junda",
        "viaNodeIds": ["n_g03_wangxiang", "n_g03_junda_north"],
        "roundTrip": True,
    },
    {
        "id": "G03-xiluan",
        "name": "西巒大山單登 (1-2日)",
        "startNodeId": "n_g03_17_1k_lan",
        "endNodeId": "n_g03_xiluan",
        "viaNodeIds": [
            "n_g03_8_workshop", "n_g03_yixiluan_1st", "n_g03_xiluan_camp",
            "n_g03_xiluan_view", "n_g03_xiluan_obs",
        ],
        "roundTrip": True,
    },
]


def build():
    r = {
        "id": "G03", "name": "郡大山‧西巒大山",
        "version": "2026-05-14",
        "source": "上河文化 G03 (G03_hiking.jpg)",
        "nodes": [{"id": nid, "name": n, "lat": lat, "lng": lng, "elevation": e, "category": c}
                  for (nid, n, lat, lng, e, c) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fw, "minutes_backward": bw,
                   "source": "上河圖", "confirmed": True} for (f, t, fw, bw) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G03.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G03: {len(NODES)} nodes, {len(EDGES)} edges")


if __name__ == "__main__":
    build()
