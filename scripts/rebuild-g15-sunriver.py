#!/usr/bin/env python3
"""Rebuild G15 丹大東郡橫斷 from 上河文化 G15_hiking.jpg.

Coverage: 丹大林道→丹大山→東郡大山→馬西山→馬利加南山 (接 G16)
"""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 進場 (與 G14 共用) ===
    ("n_g15_lindao_th",      "丹大林道登山口",  23.74500, 121.21700, 1400, "trailhead"),  #EST
    ("n_g15_qixinhu_jct",    "七彩湖岔路",      23.72200, 121.22000, 2800, "junction"),   #EST
    ("n_g15_43_workshop",    "43工寮",          23.71000, 121.21500, 2200, "shelter"),    #EST
    ("n_g15_29_6k_camp",     "29.6K擴稜營地",   23.69000, 121.20500, 2400, "waypoint"),   #EST
    ("n_g15_29_6k_water",    "最後水源",        23.69100, 121.20300, 2380, "water"),     #EST
    ("n_g15_29_4k_camp",     "29.4K擴稜營地",   23.69200, 121.20400, 2410, "waypoint"),   #EST
    ("n_g15_33_5k_park",     "33.5K大圓圈",     23.67500, 121.20000, 2580, "junction"),   #EST
    ("n_g15_23_uba_lujian",  "23K螺旋路徑",     23.70000, 121.20800, 2300, "junction"),   #EST
    ("n_g15_haematitla",     "海諾螺絲山",      23.71500, 121.21000, 2500, "peak"),       #EST
    ("n_g15_3kshigao",       "3K石膏礦",        23.74000, 121.21300, 1500, "junction"),   #EST
    ("n_g15_18_dongo_creek", "十八重溪谷",      23.79000, 121.30000, 700, "trailhead"),   #EST

    # === 丹大山 area ===
    ("n_g15_danda_hut",      "丹大山屋",        23.61600, 121.22800, 2900, "hut"),        #EST
    ("n_g15_danda_camp",     "丹大溪源頭營地",  23.61800, 121.21800, 3000, "waypoint"),   #EST
    ("n_g15_danda",          "丹大山",          23.60040, 121.21340, 3329, "peak"),       #OSM
    ("n_g15_danda_west_an",  "丹大山西鞍營地",  23.60100, 121.20000, 3100, "waypoint"),   #EST

    # === 東郡 chain ===
    ("n_g15_dongjun",        "東郡大山",        23.62681, 121.09187, 3619, "peak"),       #OSM-est (郡東山近似)
    ("n_g15_dongjun_south",  "東郡大山南鞍營地", 23.62000, 121.09500, 3350, "waypoint"),  #EST
    ("n_g15_dongjun_east",   "東郡大山東峰",    23.62500, 121.10000, 3500, "peak"),       #EST
    ("n_g15_dongjun_nean",   "東北鞍營地",      23.62800, 121.09800, 3300, "waypoint"),   #EST
    ("n_g15_yixiqiu",        "義西請馬至山",    23.58672, 121.15326, 3252, "peak"),       #OSM
    ("n_g15_tianranxin",     "天南可蘭山",      23.60863, 121.13036, 3412, "peak"),       #OSM
    ("n_g15_central_ridge_jct","中央山脈稜線岔路", 23.61300, 121.15500, 3300, "junction"), #EST

    # === 馬西山 / 馬利加南 chain (接 G16) ===
    ("n_g15_maxi",           "馬西山",          23.48380, 121.17400, 3443, "peak"),       #OSM
    ("n_g15_maxi_base",      "馬西山基地營",    23.49000, 121.16800, 3000, "waypoint"),   #EST
    ("n_g15_maxi_approach",  "馬西山接近路",    23.51000, 121.17800, 3050, "junction"),   #EST
    ("n_g15_malijianan",     "馬利加南山",      23.52157, 121.11717, 3561, "peak"),       #OSM
    ("n_g15_malijianan_east","馬利加南東側營地", 23.52000, 121.12000, 3200, "waypoint"),  #EST
    ("n_g15_3jct",           "丹大東郡南北岔路", 23.60000, 121.17500, 3050, "junction"),   #EST
    ("n_g15_south_camp",     "南稜營地",        23.54500, 121.18500, 2950, "waypoint"),   #EST
]


EDGES = [
    # 進場
    ("n_g15_lindao_th", "n_g15_43_workshop", 90, 80),
    ("n_g15_43_workshop", "n_g15_29_4k_camp", 240, 180),
    ("n_g15_29_4k_camp", "n_g15_29_6k_camp", 30, 30),
    ("n_g15_29_6k_camp", "n_g15_29_6k_water", 10, 10),
    ("n_g15_29_6k_camp", "n_g15_33_5k_park", 180, 130),
    ("n_g15_33_5k_park", "n_g15_danda_hut", 120, 90),

    # 丹大 chain
    ("n_g15_danda_hut", "n_g15_danda_camp", 60, 40),
    ("n_g15_danda_camp", "n_g15_danda", 130, 90),
    ("n_g15_danda", "n_g15_danda_west_an", 60, 40),

    # 東郡 chain
    ("n_g15_danda_west_an", "n_g15_central_ridge_jct", 150, 100),
    ("n_g15_central_ridge_jct", "n_g15_dongjun", 180, 130),
    ("n_g15_dongjun", "n_g15_dongjun_south", 60, 40),
    ("n_g15_dongjun", "n_g15_dongjun_east", 40, 30),
    ("n_g15_dongjun_east", "n_g15_dongjun_nean", 30, 25),
    ("n_g15_dongjun_nean", "n_g15_central_ridge_jct", 120, 90),
    ("n_g15_central_ridge_jct", "n_g15_yixiqiu", 240, 180),
    ("n_g15_central_ridge_jct", "n_g15_tianranxin", 90, 60),

    # 馬西山 chain
    ("n_g15_danda_west_an", "n_g15_3jct", 70, 60),
    ("n_g15_3jct", "n_g15_south_camp", 120, 100),
    ("n_g15_south_camp", "n_g15_maxi_approach", 110, 80),
    ("n_g15_maxi_approach", "n_g15_maxi", 100, 70),
    ("n_g15_maxi", "n_g15_maxi_base", 60, 40),
    ("n_g15_maxi", "n_g15_malijianan", 240, 180),
    ("n_g15_malijianan", "n_g15_malijianan_east", 40, 45),

    # 七彩湖 共用
    ("n_g15_lindao_th", "n_g15_qixinhu_jct", 120, 100),
]


PRESETS = [
    {
        "id": "G15-danda-dongjun",
        "name": "丹大東郡橫斷 (8天7夜)",
        "startNodeId": "n_g15_lindao_th",
        "endNodeId": "n_g15_dongjun",
        "viaNodeIds": [
            "n_g15_43_workshop", "n_g15_29_6k_camp", "n_g15_33_5k_park",
            "n_g15_danda_hut", "n_g15_danda", "n_g15_danda_west_an",
            "n_g15_central_ridge_jct",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g15_43_workshop", "type": "shelter"},
            {"atNodeId": "n_g15_29_6k_camp", "type": "camp"},
            {"atNodeId": "n_g15_danda_hut", "type": "hut"},
            {"atNodeId": "n_g15_danda_west_an", "type": "camp"},
            {"atNodeId": "n_g15_dongjun_south", "type": "camp"},
        ],
        "roundTrip": False,
    },
]


def build():
    r = {
        "id": "G15", "name": "丹大東郡橫斷縱走",
        "version": "2026-05-14",
        "source": "上河文化 G15 丹大東郡步程示意圖 (G15_hiking.jpg)",
        "nodes": [{"id": nid, "name": n, "lat": lat, "lng": lng, "elevation": e, "category": c}
                  for (nid, n, lat, lng, e, c) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fw, "minutes_backward": bw,
                   "source": "上河圖", "confirmed": True} for (f, t, fw, bw) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G15.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G15: {len(NODES)} nodes, {len(EDGES)} edges")


if __name__ == "__main__":
    build()
