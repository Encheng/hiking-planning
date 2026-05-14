#!/usr/bin/env python3
"""Rebuild G06 白姑大山 from 上河文化 G06_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    ("n_g06_wushe",         "霧社",            23.97000, 121.16000, 1150, "trailhead"),  #EST
    ("n_g06_hongxiang",     "紅香溫泉",        24.07000, 121.13000, 1500, "trailhead"),  #EST
    ("n_g06_last_farm",     "最後農家",        24.10000, 121.13500, 1800, "junction"),   #EST
    ("n_g06_park_lot",      "停車場",          24.15500, 121.14000, 2000, "trailhead"),  #EST (產業道路)
    ("n_g06_baigu_th",      "白姑大山登山口",  24.16000, 121.14500, 2100, "trailhead"),  #EST
    ("n_g06_water_pipe_jct","水管路岔路口",    24.17000, 121.13500, 2400, "junction"),   #EST
    ("n_g06_3cone",         "三錐山",          24.18560, 121.14718, 2572, "peak"),       #OSM
    ("n_g06_si_yan_camp",   "司晏池營地",      24.19000, 121.13000, 2800, "waypoint"),   #EST
    ("n_g06_baigu_east",    "白姑大山東南峰",  24.19500, 121.12000, 3000, "peak"),       #EST
    ("n_g06_jita_camp",     "吉他營地",        24.19800, 121.11500, 3050, "waypoint"),   #EST
    ("n_g06_yixian_cliff",  "一線天岩壁",      24.20000, 121.11000, 3150, "waypoint"),   #EST
    ("n_g06_caoqing_pool",  "草青池",          24.20200, 121.10500, 3200, "water"),     #EST
    ("n_g06_baigu",         "白姑大山",        24.20268, 121.10896, 3341, "peak"),       #OSM
]


EDGES = [
    # 公路駁接
    ("n_g06_wushe", "n_g06_hongxiang", 50, 50),       # vehicle
    ("n_g06_hongxiang", "n_g06_last_farm", 30, 30),   # vehicle
    ("n_g06_last_farm", "n_g06_park_lot", 5, 5),      # vehicle (產業道路 300公尺)
    ("n_g06_park_lot", "n_g06_baigu_th", 10, 5),
    # 主要登山路徑
    ("n_g06_baigu_th", "n_g06_water_pipe_jct", 25, 25),
    ("n_g06_water_pipe_jct", "n_g06_3cone", 110, 160),  # 上河 110/160 (smaller=DOWN, larger=UP)
    # 三錐山 to 司晏池 — 110/130 going up
    ("n_g06_3cone", "n_g06_si_yan_camp", 110, 130),
    ("n_g06_si_yan_camp", "n_g06_baigu_east", 50, 60),
    ("n_g06_baigu_east", "n_g06_jita_camp", 80, 60),
    ("n_g06_jita_camp", "n_g06_yixian_cliff", 70, 85),
    ("n_g06_yixian_cliff", "n_g06_caoqing_pool", 65, 75),
    ("n_g06_caoqing_pool", "n_g06_baigu", 45, 55),
]


PRESETS = [
    {
        "id": "G06-standard",
        "name": "白姑大山標準行程 (2天1夜)",
        "startNodeId": "n_g06_baigu_th",
        "endNodeId": "n_g06_baigu",
        "viaNodeIds": [
            "n_g06_water_pipe_jct", "n_g06_3cone", "n_g06_si_yan_camp",
            "n_g06_baigu_east", "n_g06_jita_camp", "n_g06_yixian_cliff",
            "n_g06_caoqing_pool",
        ],
        "suggestedDayBreaks": [{"atNodeId": "n_g06_si_yan_camp", "type": "camp"}],
        "roundTrip": True,
    },
]


def build():
    r = {
        "id": "G06", "name": "白姑大山",
        "version": "2026-05-14",
        "source": "上河文化 G06 白姑大山步程示意圖 (G06_hiking.jpg)",
        "nodes": [{"id": nid, "name": n, "lat": lat, "lng": lng, "elevation": e, "category": c}
                  for (nid, n, lat, lng, e, c) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fw, "minutes_backward": bw,
                   "source": "上河圖", "confirmed": True} for (f, t, fw, bw) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G06.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G06: {len(NODES)} nodes, {len(EDGES)} edges")


if __name__ == "__main__":
    build()
