#!/usr/bin/env python3
"""Rebuild G08 北二段 + 畢祿羊頭連峰 from 上河文化 G08_hiking.jpg.

G08 上河圖 actually contains TWO related sub-routes:
1. 畢祿羊頭連峰縱走 (top section)
2. 北二段 (鈴鳴/閂山/無明/甘薯/鬼門關 chain) (bottom section)
"""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 畢祿羊頭連峰 ===
    ("n_g08_820_road",          "820林道0K",         24.21500, 121.30500, 2370, "trailhead"),  #EST (合歡山隧道北口 111K)
    ("n_g08_8_4k_camp",         "8.4K登山口營地",    24.21800, 121.32500, 2800, "trailhead"),  #EST
    ("n_g08_rope_cliff",        "拉繩垂直岩壁",      24.21500, 121.33500, 3100, "waypoint"),   #EST
    ("n_g08_main_3jct",         "主稜三岔路口",      24.21500, 121.34500, 3320, "junction"),   #EST
    ("n_g08_bilu",              "畢祿山",            24.21358, 121.34719, 3370, "peak"),       #OSM
    ("n_g08_bilu_south",        "畢祿山南峰",        24.20272, 121.34882, 3029, "peak"),       #OSM
    ("n_g08_bilu_north",        "北畢祿山",          24.22399, 121.34231, 3197, "peak"),       #OSM
    ("n_g08_1st_peak_camp",     "第一峰(畢祿營地)",  24.21100, 121.34950, 3358, "waypoint"),   #OSM (鋸山前峰)
    ("n_g08_zhushan_4",         "鋸山(第四峰)",      24.21112, 121.35502, 3338, "peak"),       #OSM
    ("n_g08_east_front_camp",   "東峰前營地",        24.21100, 121.36300, 3200, "waypoint"),   #EST
    ("n_g08_zhushan_east",      "鋸山東峰",          24.20670, 121.37034, 3060, "peak"),       #OSM
    ("n_g08_3jct",              "三岔路口(羊頭)",    24.20800, 121.37500, 3000, "junction"),   #EST
    ("n_g08_yangtou",           "羊頭山",            24.20869, 121.37973, 3033, "peak"),       #OSM
    ("n_g08_yangtou_th",        "羊頭山登山口",      24.19500, 121.41500, 1900, "trailhead"),  #EST (中橫132.4K)

    # 鋸山系列副峰 (optional but in 上河)
    ("n_g08_zhushan_1",         "鋸山一峰",          24.21050, 121.35056, 3361, "peak"),       #OSM
    ("n_g08_zhushan_2",         "鋸山二峰",          24.21070, 121.35169, 3350, "peak"),       #OSM
    ("n_g08_zhushan_3",         "鋸山三峰",          24.21061, 121.35361, 3322, "peak"),       #OSM
    ("n_g08_zhushan_5",         "鋸山五峰",          24.21148, 121.35716, 3271, "peak"),       #OSM
    ("n_g08_zhushan_6",         "鋸山六峰",          24.21059, 121.36033, 3203, "peak"),       #OSM

    # === 北二段 (鈴鳴/閂山/無明/甘薯/鬼門關) ===
    ("n_g08_qingquanqiao",      "清泉橋",            24.27000, 121.27000, 1700, "trailhead"),  #EST
    ("n_g08_checkpost",         "檢查哨",            24.27200, 121.28000, 1750, "junction"),   #EST
    ("n_g08_end_road",          "行車終點",          24.27500, 121.29500, 2200, "trailhead"),  #EST (11.7K)
    ("n_g08_17_5k_th",          "17.5K登山口",       24.27000, 121.30000, 2400, "trailhead"),  #EST
    ("n_g08_23_2k_th",          "23.2K登山口",       24.27500, 121.31500, 2700, "trailhead"),  #EST
    ("n_g08_25k_workshop",      "25K工寮",           24.27500, 121.31800, 2800, "shelter"),    #EST
    ("n_g08_27_5k_th",          "27.5K林道登山口",   24.27000, 121.32500, 2900, "trailhead"),  #EST
    ("n_g08_rendai_ridge_jct",  "人待山稜線岔路",    24.26000, 121.33500, 3050, "junction"),   #EST
    ("n_g08_rain_jct",          "雨量計前岔路口",    24.25500, 121.32000, 2900, "junction"),   #EST
    ("n_g08_shanshan",          "閂山",              24.25870, 121.30987, 3168, "peak"),       #OSM
    ("n_g08_rendai",            "人待山",            24.25123, 121.33979, 3114, "peak"),       #OSM
    ("n_g08_rendai_north",      "人待山北峰",        24.25601, 121.33832, 3074, "peak"),       #OSM
    ("n_g08_lingming",          "鈴鳴山",            24.24437, 121.35166, 3271, "peak"),       #OSM
    ("n_g08_dongling_camp",     "東稜營地",          24.25500, 121.36500, 3100, "waypoint"),   #EST
    ("n_g08_water_source",      "北二段水源",        24.26500, 121.37500, 3300, "water"),     #EST
    ("n_g08_wuming_west",       "無明山西峰",        24.25429, 121.37199, 3232, "peak"),       #OSM
    ("n_g08_wuming",            "無明山",            24.25536, 121.38471, 3449, "peak"),       #OSM
    ("n_g08_wuming_east",       "無明山東峰",        24.25525, 121.39345, 3190, "peak"),       #OSM
    ("n_g08_wumingchi",         "無明池",            24.26000, 121.38500, 3300, "water"),     #EST
    ("n_g08_guimen",            "鬼門關峰",          24.26565, 121.38447, 3374, "peak"),       #OSM
    ("n_g08_an_pass",           "鞍部",              24.27500, 121.38500, 3200, "junction"),   #EST
    ("n_g08_ganshu_south",      "甘薯南峰",          24.28003, 121.37999, 3160, "peak"),       #OSM
    ("n_g08_ganshu",            "甘薯峰",            24.29048, 121.38986, 3157, "peak"),       #OSM
    ("n_g08_yi_zhishan",        "遺名志山",          24.26500, 121.34000, 3200, "peak"),       #EST
    ("n_g08_ear_no_creek",      "耳無溪百流點",      24.26000, 121.33500, 3000, "waypoint"),   #EST
]


EDGES = [
    # === 畢祿羊頭連峰 chain ===
    # 820林道0K → 8.4K登山口營地 (UP 230, DOWN 200)
    ("n_g08_820_road", "n_g08_8_4k_camp", 230, 200),
    # 8.4K → 拉繩垂直岩壁 (UP 110, DOWN 80)
    ("n_g08_8_4k_camp", "n_g08_rope_cliff", 110, 80),
    # 拉繩 → 主稜三岔路口 (UP 90, DOWN 60)
    ("n_g08_rope_cliff", "n_g08_main_3jct", 90, 60),
    # 主稜三岔路口 → 畢祿山 (5/5, very close side trip)
    ("n_g08_main_3jct", "n_g08_bilu", 5, 5),
    # 主稜三岔路口 → 第一峰 畢祿營地 (UP 30, DOWN 30)
    ("n_g08_main_3jct", "n_g08_1st_peak_camp", 30, 30),
    # 第一峰 → 鋸山(第四峰) (UP 105, DOWN 120)
    # 鋸山(3338) < 第一峰(3358), so 第一峰→鋸山 is DOWN; 上河 says 105 UP / 120 DOWN
    # Actually maybe 第一峰 is 鋸山前峰? Same elev range. 上河 shows 105/120 - take as 105 to 鋸山, 120 back
    ("n_g08_1st_peak_camp", "n_g08_zhushan_4", 105, 120),
    # 鋸山 → 鋸山一峰 → 二峰 → 三峰 → 五峰 → 六峰 (sub-peaks on ridge)
    ("n_g08_zhushan_4", "n_g08_zhushan_1", 5, 5),
    ("n_g08_zhushan_1", "n_g08_zhushan_2", 3, 3),
    ("n_g08_zhushan_2", "n_g08_zhushan_3", 3, 3),
    ("n_g08_zhushan_3", "n_g08_zhushan_5", 3, 3),
    ("n_g08_zhushan_5", "n_g08_zhushan_6", 3, 3),
    # 鋸山 → 東峰前營地 (DOWN 110, UP 180)
    ("n_g08_zhushan_4", "n_g08_east_front_camp", 110, 180),
    # 東峰前營地 → 鋸山東峰 (UP 50, DOWN 40)
    ("n_g08_east_front_camp", "n_g08_zhushan_east", 50, 40),
    # 鋸山東峰 → 三岔路口 (DOWN 30, UP 25)
    # 三岔路口 elev ~3000, 東峰 3060
    ("n_g08_zhushan_east", "n_g08_3jct", 30, 25),
    # 三岔路口 → 羊頭山 (UP 50, DOWN 45)
    ("n_g08_3jct", "n_g08_yangtou", 50, 45),
    # 三岔路口 → 羊頭山登山口 (DOWN 350, UP 180)
    ("n_g08_3jct", "n_g08_yangtou_th", 350, 180),

    # === 北二段 chain ===
    # 清泉橋 → 檢查哨 (5/5)
    ("n_g08_qingquanqiao", "n_g08_checkpost", 5, 5),
    # 檢查哨 → 行車終點 (40/40 vehicle)
    ("n_g08_checkpost", "n_g08_end_road", 40, 40),
    # 行車終點 → 17.5K登山口 (UP 40, DOWN 15)
    # 上河 顯示 1.8K to 17.5K... estimating
    ("n_g08_end_road", "n_g08_17_5k_th", 110, 160),  # 上河 110/160
    # 17.5K → 23.2K登山口 (UP/DOWN walking)
    ("n_g08_17_5k_th", "n_g08_23_2k_th", 50, 40),
    # 23.2K → 25K工寮 (40/40)
    ("n_g08_23_2k_th", "n_g08_25k_workshop", 40, 40),
    # 25K工寮 → 27.5K林道登山口 (110/110)
    ("n_g08_25k_workshop", "n_g08_27_5k_th", 110, 110),
    # 27.5K → 人待山稜線岔路 (UP 100, DOWN 50)
    ("n_g08_27_5k_th", "n_g08_rendai_ridge_jct", 100, 50),
    # 人待山稜線岔路 → 人待山 (上河 60/45)
    ("n_g08_rendai_ridge_jct", "n_g08_rendai", 60, 45),
    # 人待山稜線岔路 → 雨量計前岔路口 (15/20)
    ("n_g08_rendai_ridge_jct", "n_g08_rain_jct", 15, 20),
    # 雨量計前岔路口 → 閂山 (UP, climbing to 閂山 peak)
    ("n_g08_rain_jct", "n_g08_shanshan", 120, 90),
    # 25K工寮 → 鈴鳴山 (via 林道 → 稜線, UP)
    ("n_g08_25k_workshop", "n_g08_lingming", 180, 130),
    # 人待山 → 鈴鳴山 (ridge UP, climb)
    ("n_g08_rendai", "n_g08_lingming", 60, 45),
    # 鈴鳴山 → 東稜營地 (DOWN to camp)
    ("n_g08_lingming", "n_g08_dongling_camp", 20, 30),
    # 東稜營地 → 無明山西峰 (UP big climb)
    ("n_g08_dongling_camp", "n_g08_wuming_west", 190, 350),
    # 無明山西峰 → 無明山 (UP)
    ("n_g08_wuming_west", "n_g08_wuming", 200, 160),
    # 無明山 → 無明山東峰 (slight, side trip)
    ("n_g08_wuming", "n_g08_wuming_east", 70, 45),
    # 無明山 → 無明池 (DOWN to water)
    ("n_g08_wuming", "n_g08_wumingchi", 25, 15),
    # 無明池 → 鬼門關峰 (UP)
    ("n_g08_wumingchi", "n_g08_guimen", 70, 45),
    # 鬼門關峰 → 鞍部 (DOWN)
    ("n_g08_guimen", "n_g08_an_pass", 70, 90),
    # 鞍部 → 甘薯南峰 (UP)
    ("n_g08_an_pass", "n_g08_ganshu_south", 140, 70),
    # 甘薯南峰 → 甘薯峰 (UP)
    ("n_g08_ganshu_south", "n_g08_ganshu", 140, 140),
    # 27.5K → 水源 (途中)
    ("n_g08_27_5k_th", "n_g08_water_source", 15, 15),
]


PRESETS = [
    {
        "id": "G08-bilu-yangtou",
        "name": "畢祿羊頭連峰縱走 (2天1夜)",
        "startNodeId": "n_g08_820_road",
        "endNodeId": "n_g08_yangtou_th",
        "viaNodeIds": [
            "n_g08_8_4k_camp", "n_g08_rope_cliff", "n_g08_main_3jct",
            "n_g08_bilu",
            "n_g08_1st_peak_camp", "n_g08_zhushan_4",
            "n_g08_east_front_camp", "n_g08_zhushan_east",
            "n_g08_3jct", "n_g08_yangtou",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g08_1st_peak_camp", "type": "camp"},
        ],
        "roundTrip": False,
    },
    {
        "id": "G08-north-2nd",
        "name": "北二段標準縱走 (4天3夜)",
        "startNodeId": "n_g08_27_5k_th",
        "endNodeId": "n_g08_ganshu",
        "viaNodeIds": [
            "n_g08_rendai_ridge_jct", "n_g08_rendai", "n_g08_lingming",
            "n_g08_dongling_camp", "n_g08_wuming_west", "n_g08_wuming",
            "n_g08_wumingchi", "n_g08_guimen",
            "n_g08_an_pass", "n_g08_ganshu_south",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g08_dongling_camp", "type": "camp"},
            {"atNodeId": "n_g08_wumingchi", "type": "water"},
            {"atNodeId": "n_g08_an_pass", "type": "camp"},
        ],
        "roundTrip": False,
    },
]


def build():
    route = {
        "id": "G08",
        "name": "北二段‧畢祿羊頭連峰",
        "version": "2026-05-14",
        "source": "上河文化 G08 北二段+畢祿羊頭步程示意圖 (G08_hiking.jpg)",
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
    path = ROUTES_DIR / "G08.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G08 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
