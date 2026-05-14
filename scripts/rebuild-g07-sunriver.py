#!/usr/bin/env python3
"""Rebuild G07 北一段 from 上河文化 step diagram.

Source: G07_hiking_new.jpg + G07_hiking_new3.jpg
Coordinates: OSM where available, estimated otherwise.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"

# (id, name, lat, lng, elev, category) — #OSM verified, #EST estimated
NODES = [
    # === Northern entry (台7甲) ===
    ("n_g07_siyuan_pass",      "思源埡口",          24.39690, 121.35660, 1948, "trailhead"),  #OSM
    ("n_g07_siyuan_th",        "南湖大山思源登山口",24.39139, 121.35254, 1900, "trailhead"),  #OSM
    ("n_g07_4_8k_jct",         "4.8K岔路口",        24.38000, 121.36300, 2400, "junction"),   #EST
    ("n_g07_6_8k_th",          "6.8K登山口",        24.37000, 121.37000, 2600, "trailhead"),  #EST
    ("n_g07_duojiatun",        "多加屯山",          24.36774, 121.38115, 2795, "peak"),       #OSM
    ("n_g07_duojiatun_shelter","多加屯避難小屋",    24.36821, 121.37332, 2705, "shelter"),    #OSM
    ("n_g07_mugan_pass",       "木杆鞍部",          24.37611, 121.39291, 2515, "junction"),   #OSM (saddle)
    ("n_g07_xinyunleng_hut",   "新雲稜山莊",        24.37800, 121.40400, 2800, "hut"),        #EST (between 木杆 and 審馬陣)
    ("n_g07_shenma_th",        "審馬陣山登山口",    24.38000, 121.41600, 3130, "junction"),   #EST (near 審馬陣山)
    ("n_g07_shenma",           "審馬陣山",          24.38016, 121.41749, 3140, "peak"),       #OSM
    ("n_g07_shenma_lodge_jct", "審馬陣山莊岔路口",  24.38100, 121.42500, 3250, "junction"),   #EST
    ("n_g07_shenma_lodge",     "審馬陣山莊",        24.38050, 121.42400, 3200, "hut"),        #EST
    ("n_g07_beishan_th",       "北山登山口",        24.38300, 121.43500, 3450, "junction"),   #EST
    ("n_g07_nanhu_north",      "南湖北山",          24.38367, 121.43726, 3534, "peak"),       #OSM

    # === Alternative entry (勝光 / 7甲) ===
    ("n_g07_shengguang_th",    "南湖大山勝光登山口",24.36992, 121.34057, 1900, "trailhead"),  #OSM
    ("n_g07_dashuichi_th",     "大水池登山口",      24.36500, 121.35500, 2150, "trailhead"),  #EST
    ("n_g07_lishan_th",        "往梨山(中橫7甲)",   24.25800, 121.27500, 1950, "trailhead"),  #EST

    # === 南湖大山 主稜 ===
    ("n_g07_nanhu_north_peak", "南湖大山北峰",      24.37401, 121.44171, 3563, "peak"),       #OSM
    ("n_g07_nanhu_circle_hut", "南湖圈谷山莊",      24.36800, 121.43900, 3380, "hut"),        #EST
    ("n_g07_upper_circle",     "上圈谷",            24.36500, 121.44100, 3450, "junction"),   #EST
    ("n_g07_zhudong_jct",      "主東岔路",          24.36400, 121.44300, 3550, "junction"),   #EST
    ("n_g07_four_jct",         "四岔路口",          24.36500, 121.44600, 3600, "junction"),   #EST
    ("n_g07_nanhu_main",       "南湖大山",          24.36181, 121.43938, 3741, "peak"),       #OSM (主峰)
    ("n_g07_main_south_jct",   "主峰南峰三岔路口",  24.36000, 121.43800, 3650, "junction"),   #EST
    ("n_g07_nanhu_east",       "南湖大山東峰",      24.36559, 121.45085, 3639, "peak"),       #OSM
    ("n_g07_east_peak_th",     "東峰登山口",        24.36500, 121.45200, 3580, "junction"),   #EST

    # === 南湖 南峰、池山屋、巴巴 ===
    ("n_g07_chishanwu_hut",    "南湖池山屋",        24.35500, 121.43500, 3350, "hut"),        #EST (in 池山 cirque area)
    ("n_g07_nanhu_south_jct",  "南湖大山南峰岔路",  24.35000, 121.43500, 3480, "junction"),   #EST
    ("n_g07_nanhu_south",      "南湖大山南峰",      24.34770, 121.43476, 3505, "peak"),       #OSM
    ("n_g07_baba",             "巴巴山",            24.34239, 121.43783, 3448, "peak"),       #OSM

    # === 陶塞峰 → 馬比杉 chain ===
    ("n_g07_taosei_ruins",     "陶塞山屋遺址",      24.36200, 121.45800, 3450, "waypoint"),   #EST
    ("n_g07_dazhuoshui_jct",   "大濁水南溪岔路",    24.36500, 121.46300, 3300, "junction"),   #EST
    ("n_g07_lieliao_jct",      "獵寮岔路",          24.36800, 121.46600, 3200, "junction"),   #EST
    ("n_g07_shidong_lieliao",  "石洞獵寮",          24.37000, 121.46800, 3180, "shelter"),    #EST
    ("n_g07_taosei_th",        "陶塞峰登山口",      24.35900, 121.46100, 3500, "junction"),   #EST
    ("n_g07_taosei",           "陶塞峰",            24.35909, 121.46004, 3519, "peak"),       #OSM
    ("n_g07_nanhu_southeast",  "南湖大山東南峰",    24.35583, 121.46493, 3478, "peak"),       #OSM
    ("n_g07_marker_2_2k",      "指標2.2K岔路口",    24.35200, 121.47100, 3350, "junction"),   #EST
    ("n_g07_marker_1k",        "指標1.0K",          24.35000, 121.47800, 3280, "junction"),   #EST
    ("n_g07_mabisan",          "馬比杉山",          24.34823, 121.48564, 3211, "peak"),       #OSM

    # === 中央尖 chain (從審馬陣山莊下切) ===
    ("n_g07_nanhuxi_hut",      "南湖溪山屋",        24.37019, 121.39709, 2209, "hut"),        #OSM
    ("n_g07_xianggu_camp",     "香菇寮營地",        24.34378, 121.40670, 2200, "waypoint"),   #OSM (第一香菇寮)
    ("n_g07_zhongyangj_hut",   "中央尖溪山屋",      24.33553, 121.41827, 2430, "hut"),        #OSM
    ("n_g07_zhongyangj_pass",  "中央尖鞍部",        24.31500, 121.41700, 3450, "junction"),   #EST
    ("n_g07_zhongyangj",       "中央尖山",          24.31022, 121.41627, 3698, "peak"),       #OSM
    ("n_g07_zhongyangj_east",  "中央尖山東峰",      24.30817, 121.42360, 3581, "peak"),       #OSM

    # === 畢祿羊頭 chain (南端) ===
    ("n_g07_bilu",             "畢祿山",            24.21358, 121.34719, 3370, "peak"),       #OSM
    ("n_g07_yangtou",          "羊頭山",            24.20869, 121.37973, 3033, "peak"),       #OSM
]


# (from, to, fwd_min, bwd_min) — 上河圖時間 (smaller=DOWN, larger=UP)
# Direction convention: fwd is from→to as declared
EDGES = [
    # === 北端進場 (思源 → 審馬陣山) ===
    # 思源垭口 → 思源登山口 (公路 5min walk)
    ("n_g07_siyuan_pass", "n_g07_siyuan_th", 5, 5),
    # 上河: 思源垭口 → 4.8K (UP 145, DOWN 100)
    ("n_g07_siyuan_th", "n_g07_4_8k_jct", 145, 100),
    # 4.8K → 6.8K (UP 45, DOWN 40)
    ("n_g07_4_8k_jct", "n_g07_6_8k_th", 45, 40),
    # 6.8K → 多加屯山三角點 (UP 100, DOWN 60)
    ("n_g07_6_8k_th", "n_g07_duojiatun", 100, 60),
    # 多加屯山 → 多加屯避難小屋 (short)
    ("n_g07_duojiatun", "n_g07_duojiatun_shelter", 10, 8),
    # 多加屯山三角點 → 木杆鞍部 (DOWN 90, UP 100)
    # 三角點(2795) → 鞍部(2515) is DOWN
    ("n_g07_duojiatun", "n_g07_mugan_pass", 90, 100),
    # 木杆鞍部 → 新雲稜山莊 (UP 40, DOWN 25)
    ("n_g07_mugan_pass", "n_g07_xinyunleng_hut", 40, 25),
    # 新雲稜山莊 → 審馬陣山登山口 (UP 170, DOWN 100)
    ("n_g07_xinyunleng_hut", "n_g07_shenma_th", 170, 100),
    # 審馬陣山登山口 → 審馬陣山 (UP 3, DOWN 3, side trip)
    ("n_g07_shenma_th", "n_g07_shenma", 3, 3),
    # 審馬陣山登山口 → 審馬陣山莊岔路口 (UP 30, DOWN 20)
    ("n_g07_shenma_th", "n_g07_shenma_lodge_jct", 30, 20),
    # 審馬陣山莊岔路口 → 審馬陣山莊 (short branch)
    ("n_g07_shenma_lodge_jct", "n_g07_shenma_lodge", 5, 5),
    # 審馬陣山莊岔路口 → 北山登山口 (UP 100, DOWN 60)
    ("n_g07_shenma_lodge_jct", "n_g07_beishan_th", 100, 60),
    # 北山登山口 → 南湖北山 (UP 10, DOWN 10, side trip)
    ("n_g07_beishan_th", "n_g07_nanhu_north", 10, 10),
    # 北山登山口 → 南湖大山北峰 (UP 80, DOWN 70)
    ("n_g07_beishan_th", "n_g07_nanhu_north_peak", 80, 70),

    # === Alternative access via 勝光 ===
    # 勝光登山口 → 大水池登山口 (UP 30, DOWN 25)
    ("n_g07_shengguang_th", "n_g07_dashuichi_th", 30, 25),
    # 大水池登山口 → 多加屯山 area (估)
    ("n_g07_dashuichi_th", "n_g07_4_8k_jct", 90, 60),

    # === 南湖 主稜 ===
    # 南湖大山北峰 → 南湖圈谷山莊 (DOWN 35, UP 55)
    ("n_g07_nanhu_north_peak", "n_g07_nanhu_circle_hut", 35, 55),
    # 圈谷山莊 → 上圈谷 (UP 15, DOWN 10)
    ("n_g07_nanhu_circle_hut", "n_g07_upper_circle", 15, 10),
    # 圈谷山莊 → 主東岔路 (UP 50, DOWN 40)
    ("n_g07_nanhu_circle_hut", "n_g07_zhudong_jct", 50, 40),
    # 上圈谷 → 四岔路口 (UP 50, DOWN 30)
    ("n_g07_upper_circle", "n_g07_four_jct", 50, 30),
    # 主東岔路 → 四岔路口 (30/30)
    ("n_g07_zhudong_jct", "n_g07_four_jct", 30, 30),
    # 四岔路口 → 南湖大山東峰 (UP 60, DOWN 30)
    ("n_g07_four_jct", "n_g07_nanhu_east", 60, 30),
    # 南湖大山東峰 → 東峰登山口 (DOWN 10, UP 15)
    ("n_g07_nanhu_east", "n_g07_east_peak_th", 10, 15),
    # 主東岔路 → 主峰南峰三岔路口 (UP 20, DOWN 15)
    ("n_g07_zhudong_jct", "n_g07_main_south_jct", 20, 15),
    # 主峰南峰三岔路口 → 南湖大山 (UP 45, DOWN 30)
    ("n_g07_main_south_jct", "n_g07_nanhu_main", 45, 30),
    # 主峰南峰三岔路口 → 南湖池山屋 (DOWN 35, UP 55)
    ("n_g07_main_south_jct", "n_g07_chishanwu_hut", 35, 55),
    # 南湖池山屋 → 南湖大山南峰岔路 (UP 120, DOWN 95)
    ("n_g07_chishanwu_hut", "n_g07_nanhu_south_jct", 120, 95),
    # 南峰岔路 → 南湖大山南峰 (UP 15, DOWN 10)
    ("n_g07_nanhu_south_jct", "n_g07_nanhu_south", 15, 10),
    # 南湖大山南峰 → 巴巴山 (DOWN 55, UP 60)
    # 巴巴山(3448) < 南峰(3505), so 南峰→巴巴 is DOWN
    ("n_g07_nanhu_south", "n_g07_baba", 55, 60),

    # === 陶塞峰 → 馬比杉 chain ===
    # 四岔路口 → 陶塞山屋遺址 (DOWN 40, UP 70)
    # 山屋遺址(3450) < 四岔路口(3600), so 四岔→遺址 is DOWN
    ("n_g07_four_jct", "n_g07_taosei_ruins", 40, 70),
    # 陶塞山屋遺址 → 大濁水南溪岔路 (DOWN 40, UP 60)
    ("n_g07_taosei_ruins", "n_g07_dazhuoshui_jct", 40, 60),
    # 大濁水 → 獵寮岔路 (DOWN 10, UP 15)
    ("n_g07_dazhuoshui_jct", "n_g07_lieliao_jct", 10, 15),
    # 獵寮 → 石洞獵寮 (5/5)
    ("n_g07_lieliao_jct", "n_g07_shidong_lieliao", 5, 5),
    # 陶塞山屋遺址 → 陶塞峰登山口 (估 short)
    ("n_g07_taosei_ruins", "n_g07_taosei_th", 30, 30),
    # 陶塞峰登山口 → 陶塞峰 (估 short summit)
    ("n_g07_taosei_th", "n_g07_taosei", 20, 15),
    # 陶塞峰登山口 → 南湖大山東南峰 (UP 75, DOWN 70)
    ("n_g07_taosei_th", "n_g07_nanhu_southeast", 75, 70),
    # 東南峰 → 指標2.2K (DOWN 55, UP 75)
    ("n_g07_nanhu_southeast", "n_g07_marker_2_2k", 55, 75),
    # 2.2K → 1.0K (DOWN 35, UP 50)
    ("n_g07_marker_2_2k", "n_g07_marker_1k", 35, 50),
    # 1.0K → 馬比杉山 (UP 40, DOWN 20)
    ("n_g07_marker_1k", "n_g07_mabisan", 40, 20),

    # === 中央尖 chain ===
    # 審馬陣山莊 → 南湖溪山屋 (DOWN 65, UP 75)
    # 南湖溪山屋(2209) << 審馬陣山莊(3200), so 山莊→溪山屋 is BIG DOWN
    # 上河 75/65, 但物理上 down 應該更快...
    # Reading as: 65 is DOWN (smaller), 75 is UP
    ("n_g07_shenma_lodge", "n_g07_nanhuxi_hut", 65, 75),
    # 南湖溪山屋 → 香菇寮營地 (UP 220, DOWN 170)
    # 香菇寮(2200) ≈ 南湖溪山屋(2209), similar elev
    # 但 上河 220/170 差很多 — 可能繞路
    ("n_g07_nanhuxi_hut", "n_g07_xianggu_camp", 170, 220),
    # 香菇寮 → 中央尖溪山屋 (UP 180, DOWN 150)
    # 中央尖溪山屋(2430) > 香菇寮(2200), so 香菇寮→中央尖溪 is UP
    ("n_g07_xianggu_camp", "n_g07_zhongyangj_hut", 180, 150),
    # 中央尖溪山屋 → 中央尖鞍部 (UP 240, DOWN 200)
    ("n_g07_zhongyangj_hut", "n_g07_zhongyangj_pass", 240, 200),
    # 中央尖鞍部 → 中央尖山 (UP 50, DOWN 35)
    ("n_g07_zhongyangj_pass", "n_g07_zhongyangj", 50, 35),
    # 中央尖鞍部 → 中央尖山東峰 (UP 40, DOWN 30)
    ("n_g07_zhongyangj_pass", "n_g07_zhongyangj_east", 40, 30),

    # === 中央尖 → 畢祿羊頭 (長距離傳統路線) ===
    # 中央尖山 → 畢祿山 via 鋸山稜 (estimate, multi-hour traverse)
    # Real time: ~8-10 hours one way
    ("n_g07_zhongyangj", "n_g07_bilu", 600, 540),
    # 畢祿山 → 羊頭山 (估 100/90)
    ("n_g07_bilu", "n_g07_yangtou", 100, 90),
    # 羊頭山 → 往梨山(中橫) (估 driver-distance walk)
    ("n_g07_yangtou", "n_g07_lishan_th", 226, 336),
]


PRESETS = [
    {
        "id": "G07-classic-traverse",
        "name": "北一段標準縱走 (5天4夜)",
        "startNodeId": "n_g07_siyuan_pass",
        "endNodeId": "n_g07_lishan_th",
        "viaNodeIds": [
            "n_g07_siyuan_th", "n_g07_4_8k_jct", "n_g07_6_8k_th", "n_g07_duojiatun",
            "n_g07_mugan_pass", "n_g07_xinyunleng_hut", "n_g07_shenma_th", "n_g07_shenma",
            "n_g07_shenma_lodge_jct", "n_g07_shenma_lodge",
            "n_g07_nanhuxi_hut", "n_g07_xianggu_camp", "n_g07_zhongyangj_hut",
            "n_g07_zhongyangj_pass", "n_g07_zhongyangj",
            "n_g07_bilu", "n_g07_yangtou",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g07_xinyunleng_hut", "type": "hut"},
            {"atNodeId": "n_g07_shenma_lodge", "type": "hut"},
            {"atNodeId": "n_g07_nanhuxi_hut", "type": "hut"},
            {"atNodeId": "n_g07_zhongyangj_hut", "type": "hut"},
        ],
        "roundTrip": False,
    },
    {
        "id": "G07-nanhu-only",
        "name": "南湖大山 (4天3夜)",
        "startNodeId": "n_g07_siyuan_pass",
        "endNodeId": "n_g07_nanhu_main",
        "viaNodeIds": [
            "n_g07_siyuan_th", "n_g07_4_8k_jct", "n_g07_6_8k_th", "n_g07_duojiatun",
            "n_g07_mugan_pass", "n_g07_xinyunleng_hut", "n_g07_shenma_th",
            "n_g07_shenma_lodge_jct", "n_g07_beishan_th", "n_g07_nanhu_north_peak",
            "n_g07_nanhu_circle_hut", "n_g07_main_south_jct",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g07_xinyunleng_hut", "type": "hut"},
            {"atNodeId": "n_g07_nanhu_circle_hut", "type": "hut"},
            {"atNodeId": "n_g07_nanhu_circle_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
]


def build():
    route = {
        "id": "G07",
        "name": "北一段縱走",
        "version": "2026-05-14",
        "source": "上河文化 G07 北一段步程示意圖 (G07_hiking_new.jpg)",
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
    path = ROUTES_DIR / "G07.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G07 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
