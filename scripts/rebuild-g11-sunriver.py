#!/usr/bin/env python3
"""Rebuild G11 能高越嶺 from 上河文化 G11_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 西端 (霧社進) ===
    ("n_g11_wushe",          "霧社",            23.97000, 121.16000, 1150, "trailhead"),  #EST
    ("n_g11_lushan",         "廬山部落",        23.99000, 121.20000, 1100, "trailhead"),  #EST
    ("n_g11_tunyuan_th",     "屯原登山口",      24.05200, 121.21500, 2050, "trailhead"),  #EST
    ("n_g11_yunhai",         "雲海保線所",      24.04200, 121.25500, 2360, "hut"),        #EST
    ("n_g11_tianchi_jct",    "天池岔路口",      24.05500, 121.28700, 3150, "junction"),   #EST
    ("n_g11_tianchi_hut",    "天池山莊",        24.04500, 121.27931, 2860, "hut"),        #OSM
    ("n_g11_nanhua",         "南華山",          24.03935, 121.28593, 3182, "peak"),       #OSM
    ("n_g11_kahuanguan",     "卡賀爾山",        24.05000, 121.30000, 3010, "peak"),       #EST
    ("n_g11_nenggao",        "能高主峰",        23.99232, 121.26024, 3262, "peak"),       #OSM
    ("n_g11_xianjie",        "縣界埡口",        24.04800, 121.28800, 2800, "junction"),   #EST
    ("n_g11_kuilin",         "檜林保線所",      24.06500, 121.30500, 2900, "hut"),        #EST
    ("n_g11_5jia_north",     "五甲崩山",        24.07000, 121.31500, 2780, "peak"),       #EST
    ("n_g11_qilai",          "奇萊保線所",      24.07500, 121.32500, 2670, "hut"),        #EST
    ("n_g11_tongmen",        "銅門",            24.08000, 121.55000, 200, "trailhead"),   #EST
    ("n_g11_renshou",        "仁壽橋",          24.08500, 121.57000, 150, "trailhead"),   #EST
    ("n_g11_liyutan",        "鯉魚潭",          24.08000, 121.55500, 150, "trailhead"),   #EST
    ("n_g11_hualian",        "花蓮",            23.99000, 121.61000, 50, "trailhead"),    #EST
    ("n_g11_to_buling",      "往埔里",          23.97500, 121.14000, 600, "junction"),   #EST

    # 奇萊南華 area
    ("n_g11_qilai_south",    "奇萊主山南峰",    24.06130, 121.27997, 3357, "peak"),       #OSM
    ("n_g11_south_peak_th",  "南峰登山口",      24.06500, 121.28500, 3100, "junction"),   #EST
]


EDGES = [
    # === 公路駁接 ===
    ("n_g11_wushe", "n_g11_to_buling", 30, 30),  # vehicle
    ("n_g11_wushe", "n_g11_lushan", 30, 30),     # vehicle
    ("n_g11_lushan", "n_g11_tunyuan_th", 50, 50), # vehicle

    # === 西段: 屯原 → 雲海 → 天池 ===
    ("n_g11_tunyuan_th", "n_g11_yunhai", 208, 66),  # 統一 G09 值
    ("n_g11_yunhai", "n_g11_tianchi_hut", 257, 90), # 統一 G09 值

    # === 天池 area ===
    ("n_g11_tianchi_hut", "n_g11_tianchi_jct", 60, 40),  # 統一
    ("n_g11_tianchi_jct", "n_g11_nanhua", 40, 30),       # 統一
    ("n_g11_tianchi_jct", "n_g11_south_peak_th", 20, 15),
    ("n_g11_south_peak_th", "n_g11_qilai_south", 60, 40),
    ("n_g11_tianchi_hut", "n_g11_xianjie", 50, 55),
    ("n_g11_xianjie", "n_g11_nanhua", 120, 80),
    # 天池山莊 → 能高主峰 (south)
    ("n_g11_tianchi_hut", "n_g11_kahuanguan", 170, 140),
    ("n_g11_kahuanguan", "n_g11_nenggao", 160, 140),

    # === 東段: 天池 → 檜林 → 五甲 → 奇萊保線所 → 銅門 ===
    ("n_g11_tianchi_hut", "n_g11_kuilin", 240, 170),
    ("n_g11_kuilin", "n_g11_5jia_north", 180, 170),
    ("n_g11_5jia_north", "n_g11_qilai", 260, 180),
    ("n_g11_qilai", "n_g11_renshou", 120, 120),
    ("n_g11_renshou", "n_g11_tongmen", 5, 5),  # vehicle
    ("n_g11_tongmen", "n_g11_liyutan", 10, 10),  # vehicle
    ("n_g11_liyutan", "n_g11_hualian", 30, 30),  # vehicle
]


PRESETS = [
    {
        "id": "G11-traverse",
        "name": "能高越嶺道 (3天2夜，屯原→奇萊)",
        "startNodeId": "n_g11_tunyuan_th",
        "endNodeId": "n_g11_qilai",
        "viaNodeIds": [
            "n_g11_yunhai", "n_g11_tianchi_hut", "n_g11_kuilin", "n_g11_5jia_north",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g11_tianchi_hut", "type": "hut"},
            {"atNodeId": "n_g11_kuilin", "type": "hut"},
        ],
        "roundTrip": False,
    },
    {
        "id": "G11-nanhua",
        "name": "能高南華 (2天1夜)",
        "startNodeId": "n_g11_tunyuan_th",
        "endNodeId": "n_g11_nanhua",
        "viaNodeIds": [
            "n_g11_yunhai", "n_g11_tianchi_hut",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g11_tianchi_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
]


def build():
    route = {
        "id": "G11", "name": "能高越嶺",
        "version": "2026-05-14",
        "source": "上河文化 G11 能高越嶺步程示意圖 (G11_hiking.jpg)",
        "nodes": [{"id": nid, "name": name, "lat": lat, "lng": lng, "elevation": elev, "category": cat}
                  for (nid, name, lat, lng, elev, cat) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fwd, "minutes_backward": bwd,
                   "source": "上河圖", "confirmed": True} for (f, t, fwd, bwd) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G11.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G11 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
