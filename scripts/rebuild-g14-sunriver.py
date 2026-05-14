#!/usr/bin/env python3
"""Rebuild G14 丹大山列 (七彩湖‧六順山) from 上河文化 G14_hiking.jpg.

Actual 上河 G14 covers 丹大山列縱走: 七彩湖→六順山→丹大山→關門山→大石公山→
小石公山→鞍山→3255公尺峰→3265公尺峰→2761最低鞍部→2613裝箱地→2917公尺峰
"""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 進場 ===
    ("n_g14_thuiyuan",       "水里",            23.81000, 120.85000, 280, "trailhead"),    #EST
    ("n_g14_dongguanbridge", "瑞穗",            23.50000, 121.37000, 100, "trailhead"),    #EST (花蓮端進場)
    ("n_g14_lindao_admin",   "林道管制",        23.74000, 121.21500, 1400, "junction"),    #EST
    ("n_g14_lindao_th",      "林道登山口",      23.74500, 121.21700, 1400, "trailhead"),   #EST (約70公里)
    ("n_g14_linji_th",       "林道入口",        23.74700, 121.21800, 1450, "junction"),    #EST
    ("n_g14_lindao_xiaohu",  "彩湖",            23.72000, 121.21500, 2820, "water"),      #EST (七彩湖)
    ("n_g14_qixin_jct",      "看雲樹下岔路",    23.72200, 121.22000, 2800, "junction"),    #EST
    ("n_g14_lindao_dongkou", "林道盡頭",        23.72500, 121.22500, 2800, "junction"),    #EST
    ("n_g14_qixin_lake",     "七彩湖",          23.72000, 121.21500, 2820, "water"),      #EST
    ("n_g14_yundao_bridge",  "運煤之橋",        23.72500, 121.22500, 2820, "waypoint"),   #EST

    # === 六順山 + 周邊 ===
    ("n_g14_liushun",        "六順山",          23.72450, 121.23957, 3006, "peak"),       #OSM
    ("n_g14_2917",           "2917公尺峰",      23.72000, 121.23500, 2917, "peak"),       #EST
    ("n_g14_2897",           "2897公尺峰",      23.71800, 121.24000, 2897, "peak"),       #EST
    ("n_g14_2813_camp",      "2813裝箱地",      23.71600, 121.23700, 2813, "waypoint"),   #EST
    ("n_g14_2761_low_an",    "2761最低鞍部",    23.71500, 121.23500, 2761, "junction"),   #EST
    ("n_g14_3265",           "3265公尺峰",      23.70000, 121.23500, 3265, "peak"),       #EST
    ("n_g14_anshan",         "鞍山",            23.69500, 121.23500, 3260, "peak"),       #EST
    ("n_g14_3255",           "3255公尺峰",      23.69000, 121.23800, 3255, "peak"),       #EST
    ("n_g14_2833",           "2833公尺峰",      23.68500, 121.24000, 2833, "peak"),       #EST
    ("n_g14_xiaoshigong",    "小石公山",        23.63200, 121.22480, 2940, "peak"),       #OSM
    ("n_g14_dashigong",      "大石公山",        23.63360, 121.22426, 3054, "peak"),       #OSM
    ("n_g14_guanmen_west",   "關門山西峰",      23.67710, 121.22797, 2912, "peak"),       #OSM
    ("n_g14_guanmen_jct",    "關門西山口",      23.67500, 121.23000, 2900, "junction"),   #EST
    ("n_g14_guanmen_north",  "關門北山",        23.69378, 121.23922, 3044, "peak"),       #OSM
    ("n_g14_guanmen",        "關門山",          23.67661, 121.23233, 2992, "peak"),       #OSM
    ("n_g14_danda",          "丹大山",          23.60040, 121.21340, 3329, "peak"),       #OSM
    ("n_g14_danda_east",     "丹大山東峰",      23.60230, 121.22454, 3143, "peak"),       #OSM
    ("n_g14_danda_west_an",  "丹大山西鞍營地",  23.60100, 121.20000, 3100, "waypoint"),   #EST
    ("n_g14_taken_chizu",    "塔可機停機坪",    23.62000, 121.21000, 2900, "junction"),   #EST
    ("n_g14_qiyu_workshop",  "七矽工寮",        23.65000, 121.20000, 2700, "shelter"),    #EST
    ("n_g14_3jct",           "三岔路口",        23.65500, 121.21500, 2900, "junction"),   #EST
    ("n_g14_to_danda",       "往丹大東郡橫斷",  23.59000, 121.21000, 3200, "junction"),   #EST (arrow to G15)
]


EDGES = [
    # 進場
    ("n_g14_lindao_admin", "n_g14_lindao_th", 5, 5),   # vehicle
    ("n_g14_lindao_th", "n_g14_linji_th", 5, 5),
    ("n_g14_linji_th", "n_g14_lindao_dongkou", 120, 100),
    ("n_g14_lindao_dongkou", "n_g14_qixin_jct", 70, 70),
    ("n_g14_qixin_jct", "n_g14_qixin_lake", 26, 30),

    # 看雲樹下 → 六順山
    ("n_g14_qixin_jct", "n_g14_liushun", 62, 55),
    ("n_g14_liushun", "n_g14_2917", 50, 50),
    ("n_g14_2917", "n_g14_2897", 60, 50),
    ("n_g14_2897", "n_g14_2813_camp", 100, 80),
    ("n_g14_2813_camp", "n_g14_2761_low_an", 100, 80),

    # 鞍山 chain
    ("n_g14_2761_low_an", "n_g14_3265", 100, 80),
    ("n_g14_3265", "n_g14_anshan", 100, 80),
    ("n_g14_anshan", "n_g14_3255", 100, 80),
    ("n_g14_3255", "n_g14_2833", 240, 260),

    # 大小石公 / 關門
    ("n_g14_2833", "n_g14_dashigong", 60, 50),
    ("n_g14_dashigong", "n_g14_xiaoshigong", 20, 20),
    ("n_g14_dashigong", "n_g14_guanmen_north", 130, 110),
    ("n_g14_guanmen_north", "n_g14_guanmen", 100, 100),
    ("n_g14_guanmen", "n_g14_guanmen_west", 30, 30),
    ("n_g14_guanmen_west", "n_g14_guanmen_jct", 15, 15),

    # 丹大山
    ("n_g14_guanmen", "n_g14_qiyu_workshop", 60, 90),
    ("n_g14_qiyu_workshop", "n_g14_3jct", 60, 50),
    ("n_g14_3jct", "n_g14_taken_chizu", 90, 70),
    ("n_g14_taken_chizu", "n_g14_danda_west_an", 60, 60),
    ("n_g14_danda_west_an", "n_g14_danda", 60, 40),
    ("n_g14_danda", "n_g14_danda_east", 40, 30),
    ("n_g14_danda", "n_g14_to_danda", 60, 90),

    # 水里端進場
    ("n_g14_thuiyuan", "n_g14_lindao_admin", 240, 240),  # vehicle long drive
    ("n_g14_dongguanbridge", "n_g14_lindao_admin", 360, 360),  # vehicle 花蓮端
]


PRESETS = [
    {
        "id": "G14-qicaihu-liushun",
        "name": "七彩湖六順山 (2天1夜)",
        "startNodeId": "n_g14_lindao_th",
        "endNodeId": "n_g14_liushun",
        "viaNodeIds": [
            "n_g14_linji_th", "n_g14_lindao_dongkou", "n_g14_qixin_jct", "n_g14_qixin_lake",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g14_qixin_jct", "type": "water"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G14-danda-traverse",
        "name": "丹大山列縱走 (5天4夜)",
        "startNodeId": "n_g14_lindao_th",
        "endNodeId": "n_g14_danda",
        "viaNodeIds": [
            "n_g14_liushun", "n_g14_anshan", "n_g14_dashigong", "n_g14_guanmen",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g14_2813_camp", "type": "camp"},
            {"atNodeId": "n_g14_xiaoshigong", "type": "camp"},
            {"atNodeId": "n_g14_guanmen", "type": "camp"},
            {"atNodeId": "n_g14_danda_west_an", "type": "camp"},
        ],
        "roundTrip": False,
    },
]


def build():
    r = {
        "id": "G14", "name": "丹大山列縱走 (七彩湖‧六順山)",
        "version": "2026-05-14",
        "source": "上河文化 G14 丹大山列縱走步程示意圖 (G14_hiking.jpg)",
        "nodes": [{"id": nid, "name": n, "lat": lat, "lng": lng, "elevation": e, "category": c}
                  for (nid, n, lat, lng, e, c) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fw, "minutes_backward": bw,
                   "source": "上河圖", "confirmed": True} for (f, t, fw, bw) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G14.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G14: {len(NODES)} nodes, {len(EDGES)} edges")


if __name__ == "__main__":
    build()
