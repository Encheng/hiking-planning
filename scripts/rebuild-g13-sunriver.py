#!/usr/bin/env python3
"""Rebuild G13 干卓萬群峰縱走 from 上河文化 G13_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 進場 ===
    ("n_g13_puli",            "埔里",            23.97000, 120.97000, 450, "trailhead"),  #EST
    ("n_g13_wushe",           "霧社",            23.97000, 121.16000, 1150, "trailhead"),  #EST
    ("n_g13_wanwei_xiaoju",   "武界霸頭瀑",      23.90000, 121.10000, 800, "waypoint"),   #EST (武界吊橋)
    ("n_g13_liyuan_creek",    "栗園溪",          23.89500, 121.10500, 900, "waypoint"),   #EST
    ("n_g13_lindao_xishuiyuan","林道溪水源",      23.89000, 121.11000, 1100, "water"),     #EST
    ("n_g13_zuolin_dayuanjian","造林大圓圈",     23.88500, 121.11500, 1500, "waypoint"),   #EST
    ("n_g13_lindao_th",       "林道登山口",      23.88000, 121.12000, 1900, "trailhead"),  #EST
    ("n_g13_46k_brick",       "46K紅磚屋",       23.87000, 121.12500, 2400, "shelter"),    #EST
    ("n_g13_wanyou_lindao",   "武界林道",        23.87500, 121.12300, 2300, "junction"),   #EST
    ("n_g13_zhuoshe",         "卓社山",          23.84000, 121.09115, 2652, "peak"),       #OSM
    ("n_g13_zhuoshe_dayuxian","卓社大山",        23.83453, 121.11585, 3368, "peak"),       #OSM
    ("n_g13_28_camp",         "289鞍部營地",     23.83500, 121.10500, 2895, "waypoint"),   #EST

    # === 林道 → 干卓萬 ===
    ("n_g13_qireng",          "其儂", "23.86000", 121.13000, 2500, "junction"),  # placeholder

    ("n_g13_7_8k_park",       "7.8K停車處",      23.87000, 121.14000, 2400, "trailhead"),  #EST
    ("n_g13_v_xinhouwu",      "V型新箱屋",       23.86500, 121.14500, 2300, "shelter"),    #EST
    ("n_g13_5_3k_workshop",   "5.3K廢工寮",      23.86000, 121.15000, 2150, "shelter"),    #EST
    ("n_g13_lijiezi",         "理捷子",          23.87500, 121.14500, 2500, "waypoint"),   #EST
    ("n_g13_yingzhai_camp",   "螢寨營地",        23.88000, 121.15000, 2700, "waypoint"),   #EST
    ("n_g13_th",              "登山口",          23.87500, 121.15500, 2800, "trailhead"),  #EST
    ("n_g13_dengshan_jct",    "登山口岔路",      23.87800, 121.15800, 2850, "junction"),   #EST
    ("n_g13_7zhuo_lai_camp",  "七卓萊源營地",    23.88500, 121.16500, 2900, "waypoint"),   #EST
    ("n_g13_rope_camp",       "扁形營地",        23.88800, 121.16800, 3050, "waypoint"),   #EST
    ("n_g13_ganzhuowan_baseN","千卓萬山基地營北",23.88500, 121.16800, 3050, "waypoint"),   #EST
    ("n_g13_3198",            "3198公尺峰",      23.88200, 121.16800, 3198, "peak"),       #EST
    ("n_g13_ganzhuo",         "干卓萬山",        23.87605, 121.13896, 3282, "peak"),       #OSM
    ("n_g13_ganzhuo_3jct",    "干卓萬山三叉峰",  23.86510, 121.15394, 3244, "peak"),       #OSM
    ("n_g13_mushan",          "牧山",            23.86290, 121.16021, 3239, "peak"),       #OSM
    ("n_g13_mushan_east",     "東北鞍營地",      23.86300, 121.16500, 3100, "waypoint"),   #EST
    ("n_g13_mushan_chi",      "牧山池",          23.86200, 121.16700, 3100, "water"),     #EST
    ("n_g13_wanlishan_west",  "萬里山西峰",      23.86500, 121.17500, 3200, "peak"),       #EST
    ("n_g13_dongnan_camp",    "東南鞍營地",      23.86300, 121.17000, 3050, "waypoint"),   #EST
    ("n_g13_dongbei_camp",    "東北下營地",      23.86500, 121.16600, 3000, "waypoint"),   #EST
    ("n_g13_yufengshan_jct",  "卓社大山東峰交叉口", 23.83000, 121.11500, 3250, "junction"),  #EST
]


EDGES = [
    # 公路駁接
    ("n_g13_puli", "n_g13_wushe", 40, 40),  # vehicle
    ("n_g13_wushe", "n_g13_wanwei_xiaoju", 45, 45),  # vehicle
    # 進場 chain
    ("n_g13_wanwei_xiaoju", "n_g13_liyuan_creek", 60, 60),
    ("n_g13_liyuan_creek", "n_g13_lindao_xishuiyuan", 100, 65),
    ("n_g13_lindao_xishuiyuan", "n_g13_zuolin_dayuanjian", 100, 65),
    ("n_g13_zuolin_dayuanjian", "n_g13_lindao_th", 180, 80),
    ("n_g13_lindao_th", "n_g13_46k_brick", 120, 80),
    ("n_g13_46k_brick", "n_g13_28_camp", 180, 130),
    ("n_g13_28_camp", "n_g13_zhuoshe_dayuxian", 130, 80),
    ("n_g13_zhuoshe_dayuxian", "n_g13_zhuoshe", 240, 200),
    ("n_g13_zhuoshe_dayuxian", "n_g13_yufengshan_jct", 320, 200),

    # 干卓萬 chain
    ("n_g13_7_8k_park", "n_g13_v_xinhouwu", 65, 50),
    ("n_g13_v_xinhouwu", "n_g13_5_3k_workshop", 75, 50),
    ("n_g13_7_8k_park", "n_g13_lijiezi", 140, 50),
    ("n_g13_lijiezi", "n_g13_yingzhai_camp", 50, 30),
    ("n_g13_yingzhai_camp", "n_g13_th", 30, 30),
    ("n_g13_th", "n_g13_dengshan_jct", 50, 70),
    ("n_g13_dengshan_jct", "n_g13_7zhuo_lai_camp", 90, 70),
    ("n_g13_7zhuo_lai_camp", "n_g13_rope_camp", 50, 40),
    ("n_g13_rope_camp", "n_g13_ganzhuowan_baseN", 40, 35),
    ("n_g13_ganzhuowan_baseN", "n_g13_ganzhuo", 90, 60),
    ("n_g13_ganzhuo", "n_g13_ganzhuo_3jct", 60, 50),
    ("n_g13_ganzhuo_3jct", "n_g13_mushan", 50, 60),
    ("n_g13_mushan", "n_g13_mushan_east", 50, 65),
    ("n_g13_mushan_east", "n_g13_mushan_chi", 5, 5),
    ("n_g13_mushan_east", "n_g13_wanlishan_west", 200, 130),
    ("n_g13_mushan", "n_g13_dongnan_camp", 50, 35),
    ("n_g13_dongnan_camp", "n_g13_dongbei_camp", 40, 30),
    ("n_g13_dongbei_camp", "n_g13_3198", 40, 30),
]


PRESETS = [
    {
        "id": "G13-ganzhuowan",
        "name": "干卓萬群峰縱走 (4天3夜)",
        "startNodeId": "n_g13_7_8k_park",
        "endNodeId": "n_g13_mushan",
        "viaNodeIds": [
            "n_g13_lijiezi", "n_g13_yingzhai_camp", "n_g13_th",
            "n_g13_ganzhuo", "n_g13_ganzhuo_3jct",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g13_yingzhai_camp", "type": "camp"},
            {"atNodeId": "n_g13_7zhuo_lai_camp", "type": "camp"},
            {"atNodeId": "n_g13_mushan_east", "type": "camp"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G13-zhuoshe",
        "name": "卓社大山 (3天2夜)",
        "startNodeId": "n_g13_lindao_th",
        "endNodeId": "n_g13_zhuoshe_dayuxian",
        "viaNodeIds": [
            "n_g13_46k_brick", "n_g13_28_camp",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g13_46k_brick", "type": "shelter"},
        ],
        "roundTrip": True,
    },
]


def build():
    r = {
        "id": "G13", "name": "干卓萬群峰縱走",
        "version": "2026-05-14",
        "source": "上河文化 G13 干卓萬群峰步程示意圖 (G13_hiking.jpg)",
        "nodes": [{"id": nid, "name": n, "lat": lat, "lng": lng, "elevation": e, "category": c}
                  for (nid, n, lat, lng, e, c) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fw, "minutes_backward": bw,
                   "source": "上河圖", "confirmed": True} for (f, t, fw, bw) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G13.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G13: {len(NODES)} nodes, {len(EDGES)} edges")


if __name__ == "__main__":
    build()
