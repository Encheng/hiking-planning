#!/usr/bin/env python3
"""Rebuild G16 馬博拉斯橫斷縱走 from 上河文化 G16_hiking.jpg.

Coverage: 東埔→八通關古道→中央金礦→秀姑巒→馬博拉斯→馬西→玉里林道
"""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 八通關古道進場 (與 G02 共用) ===
    ("n_g16_dongpu_hotspring",  "東埔溫泉",          23.51000, 120.87300, 1150, "trailhead"),  #EST
    ("n_g16_8tongguan_th",      "八通關登山口",      23.50500, 120.88000, 1200, "trailhead"),  #EST
    ("n_g16_sansheng_temple",   "三聖宮",            23.49500, 120.89500, 1600, "junction"),   #EST
    ("n_g16_lele_hotspring_jct","樂樂溫泉岔路",      23.49000, 120.90000, 1700, "junction"),   #EST
    ("n_g16_yunlong_falls",     "雲龍瀑布",          23.48500, 120.91000, 1950, "water"),     #EST
    ("n_g16_lele_hut",          "樂樂山屋",          23.48000, 120.92000, 2150, "hut"),        #EST
    ("n_g16_yinv_falls",        "乙女瀑布",          23.47500, 120.93000, 2350, "water"),     #EST
    ("n_g16_duiguan",           "對觀",              23.47000, 120.94000, 2500, "waypoint"),   #EST
    ("n_g16_guangao_ping",      "觀高坪",            23.46500, 120.95000, 2520, "junction"),   #EST
    ("n_g16_guangao_service",   "觀高登山服務站",    23.46300, 120.95200, 2530, "junction"),   #EST
    ("n_g16_8tongguan",         "八通關",            23.46500, 120.97500, 2790, "junction"),   #EST (草原)
    ("n_g16_8tongguan_grass",   "八通關草原",        23.46300, 120.97200, 2780, "waypoint"),   #EST
    ("n_g16_8tongguan_shan",    "八通關山",          23.47000, 120.98000, 3335, "peak"),       #EST
    ("n_g16_8tongguan_jct",     "八通關岔路口",      23.46500, 120.97800, 2900, "junction"),   #EST
    ("n_g16_8tongguan_3jct",    "八通關三岔路口",    23.46500, 120.97600, 2850, "junction"),   #EST
    ("n_g16_8tongguan_west",    "八通關山西峰",      23.46800, 120.97700, 3263, "peak"),       #EST

    # === 中央金礦 → 白洋 chain ===
    ("n_g16_zhongyang_mine",    "中央金礦山屋",      23.48653, 121.02746, 2820, "hut"),        #OSM
    ("n_g16_baiyang_mine",      "白洋金礦山屋",      23.48789, 121.04743, 3378, "hut"),        #OSM
    ("n_g16_xiugu_ping",        "秀姑坪",            23.48000, 121.03500, 3550, "waypoint"),   #EST
    ("n_g16_xiugu_hut",         "秀姑巒山屋",        23.47500, 121.03500, 3450, "hut"),        #EST
    ("n_g16_xiugu",             "秀姑巒山",          23.47570, 121.04136, 3805, "peak"),       #OSM-est
    ("n_g16_xiugu_jct",         "秀姑巒岔路",        23.47700, 121.03700, 3700, "junction"),   #EST

    # === 馬博 chain ===
    ("n_g16_mabolasi",          "馬博拉斯山",        23.49170, 121.05690, 3785, "peak"),       #OSM-est
    ("n_g16_mabolasi_jct",      "馬博拉斯岔路",      23.49000, 121.05000, 3650, "junction"),   #EST
    ("n_g16_mabolasi_hut",      "馬博拉斯山屋",      23.49500, 121.06500, 3320, "hut"),        #EST
    ("n_g16_mabolasi_east_camp","馬博拉斯東鞍營地",  23.49500, 121.06000, 3550, "waypoint"),   #EST
    ("n_g16_mayalwenlu_east",   "馬利亞文路山東峰",  23.50500, 121.06500, 3580, "peak"),       #EST
    ("n_g16_makaran",           "馬加蘭帝山峰",      23.51000, 121.07500, 3450, "peak"),       #EST

    # === 馬西 / 馬利加南 chain (連到 G15) ===
    ("n_g16_maxi",              "馬西山",            23.48380, 121.17400, 3443, "peak"),       #OSM (from G15)
    ("n_g16_maxi_jct",          "馬西山岔路口",      23.49500, 121.10000, 3300, "junction"),   #EST
    ("n_g16_majiagan_jct",      "加幹岔路口",        23.49500, 121.10500, 3350, "junction"),   #EST
    ("n_g16_3819",              "3819公尺峰",        23.49300, 121.11500, 3819, "peak"),       #EST
    ("n_g16_lushipanan",        "路西帕南山",        23.49500, 121.12500, 3585, "peak"),       #EST
    ("n_g16_taluna_north",      "太魯那斯北山",      23.49800, 121.13000, 3500, "peak"),       #EST
    ("n_g16_taluna",            "太魯那斯山",        23.50500, 121.13500, 3528, "peak"),       #EST
    ("n_g16_taluna_jct",        "太魯那斯岔路口",    23.50300, 121.13200, 3480, "junction"),   #EST
    ("n_g16_malijianan",        "馬利加南山",        23.52157, 121.11717, 3561, "peak"),       #OSM
    ("n_g16_malijianan_east",   "馬利加南東側營地",  23.52000, 121.12000, 3200, "waypoint"),   #EST
    ("n_g16_yixi",              "義西請馬至山(接G15)", 23.58672, 121.15326, 3252, "peak"),     #OSM
    ("n_g16_buqian",            "布干山",            23.49000, 121.06500, 3250, "peak"),       #EST

    # === 大水窟 area ===
    ("n_g16_dashuiku",          "大水窟山",          23.47398, 121.03848, 3643, "peak"),       #OSM (shared with G17)
    ("n_g16_dashuiku_hut",      "大水窟山屋",        23.45934, 121.05625, 3227, "hut"),        #OSM
    ("n_g16_dashuiku_pool",     "大水窟池",          23.46027, 121.05635, 3220, "water"),      #OSM
    ("n_g16_dujuan_camp",       "杜鵑營地",          23.47447, 121.02739, 3050, "waypoint"),   #OSM
    ("n_g16_dujuan_jct",        "稜線岔路",          23.47000, 121.02500, 3200, "junction"),   #EST

    # === 玉里林道 下山 chain ===
    ("n_g16_yuli_44k",          "44K林道盡頭",       23.49000, 121.16000, 2400, "junction"),   #EST
    ("n_g16_yuli_43k",          "43K萊葉工寮",       23.49000, 121.16500, 2300, "shelter"),    #EST
    ("n_g16_yuli_36k",          "36K萊葉工寮",       23.50000, 121.18500, 1900, "shelter"),    #EST
    ("n_g16_yuli_35k",          "35K萊葉工寮",       23.50500, 121.19000, 1850, "shelter"),    #EST
    ("n_g16_jiejing",           "捷徑下切點",        23.50500, 121.18000, 2200, "junction"),   #EST
    ("n_g16_abandoned_gen",     "廢棄發電機",        23.50200, 121.19200, 1700, "waypoint"),   #EST
    ("n_g16_xiagu",             "下切溪床點",        23.51000, 121.19500, 1500, "waypoint"),   #EST
    ("n_g16_yuli_engineer",     "玉里林道下切點",    23.51500, 121.20000, 1400, "junction"),   #EST
    ("n_g16_xiakou_camp",       "下切溪谷營地",      23.51200, 121.20500, 1300, "waypoint"),   #EST
    ("n_g16_dashibing_camp",    "大石柄布稜營地",    23.52000, 121.20800, 1200, "waypoint"),   #EST
    ("n_g16_xikou_2",           "溪谷下切處",        23.52500, 121.21500, 1100, "junction"),   #EST
    ("n_g16_lindao_west",       "林道朋安處",        23.53000, 121.22000, 1100, "junction"),   #EST
    ("n_g16_heguworkshop",      "河谷工寮",          23.53000, 121.22500, 1050, "shelter"),    #EST
    ("n_g16_stoneside_camp",    "林道石壁營地",      23.53500, 121.23000, 1000, "waypoint"),   #EST
    ("n_g16_miaopu",            "苗圃工寮",          23.54000, 121.24000, 900, "shelter"),     #EST
    ("n_g16_road_end",          "林道車輛終點",      23.54500, 121.25000, 800, "trailhead"),   #EST
    ("n_g16_zhongping",         "中坪",              23.55000, 121.26000, 700, "trailhead"),   #EST
    ("n_g16_yuli",              "玉里",              23.33000, 121.31000, 130, "trailhead"),   #EST
    ("n_g16_ruisui",            "瑞穗",              23.50000, 121.37000, 100, "trailhead"),   #EST

    # === 最低鞍部 (馬博 area) ===
    ("n_g16_low_an",            "馬博最低鞍部",      23.47500, 121.05000, 3300, "junction"),   #EST
]


EDGES = [
    # === 八通關古道 進場 ===
    ("n_g16_dongpu_hotspring", "n_g16_8tongguan_th", 10, 10),
    # 八通關登山口 → 三聖宮 (UP 25, DOWN 15)
    ("n_g16_8tongguan_th", "n_g16_sansheng_temple", 25, 15),
    # 三聖宮 → 樂樂溫泉岔路 (UP 50, DOWN 45)
    ("n_g16_sansheng_temple", "n_g16_lele_hotspring_jct", 50, 45),
    # 樂樂溫泉岔路 → 雲龍瀑布 (UP 45, DOWN 45)
    ("n_g16_lele_hotspring_jct", "n_g16_yunlong_falls", 45, 45),
    # 雲龍瀑布 → 樂樂山屋 (UP 60, DOWN 55)
    ("n_g16_yunlong_falls", "n_g16_lele_hut", 60, 55),
    # 樂樂山屋 → 乙女瀑布 (UP 25, DOWN 25)
    ("n_g16_lele_hut", "n_g16_yinv_falls", 25, 25),
    # 乙女瀑布 → 對觀 (UP 100, DOWN 80)
    ("n_g16_yinv_falls", "n_g16_duiguan", 100, 80),
    # 對觀 → 觀高坪 (UP 150, DOWN 110)
    ("n_g16_duiguan", "n_g16_guangao_ping", 150, 110),
    # 觀高坪 → 觀高登山服務站 (5/5)
    ("n_g16_guangao_ping", "n_g16_guangao_service", 5, 5),
    # 觀高坪 → 八通關 (草原) (UP 80, DOWN 70)
    ("n_g16_guangao_ping", "n_g16_8tongguan", 80, 70),
    # 八通關 → 八通關草原 (very close)
    ("n_g16_8tongguan", "n_g16_8tongguan_grass", 5, 5),
    # 八通關 → 八通關岔路口 (5/5)
    ("n_g16_8tongguan", "n_g16_8tongguan_jct", 5, 5),
    # 八通關岔路口 → 八通關山 (UP 30, DOWN 20)
    ("n_g16_8tongguan_jct", "n_g16_8tongguan_shan", 30, 20),
    # 八通關草原 → 八通關山西峰 (UP)
    ("n_g16_8tongguan_grass", "n_g16_8tongguan_west", 50, 30),
    # 八通關山西峰 → 三岔路口 (50/50)
    ("n_g16_8tongguan_west", "n_g16_8tongguan_3jct", 50, 50),

    # === 八通關 → 中央金礦 → 白洋 → 秀姑巒 ===
    ("n_g16_8tongguan_3jct", "n_g16_zhongyang_mine", 60, 45),  # 八通關三岔路 → 中央金礦 (DOWN)
    ("n_g16_zhongyang_mine", "n_g16_baiyang_mine", 90, 60),    # 中央金礦 → 白洋金礦 (UP)
    ("n_g16_baiyang_mine", "n_g16_xiugu_ping", 80, 50),        # 白洋 → 秀姑坪 (UP)
    ("n_g16_xiugu_ping", "n_g16_xiugu_jct", 30, 20),
    ("n_g16_xiugu_jct", "n_g16_xiugu", 60, 30),                # 秀姑巒岔路 → 秀姑巒山 (UP)
    ("n_g16_xiugu_jct", "n_g16_xiugu_hut", 25, 30),
    ("n_g16_xiugu_hut", "n_g16_xiugu", 70, 50),

    # === 馬博 chain ===
    ("n_g16_xiugu_jct", "n_g16_mabolasi_jct", 60, 50),
    ("n_g16_mabolasi_jct", "n_g16_mabolasi", 45, 30),
    ("n_g16_mabolasi_jct", "n_g16_mabolasi_east_camp", 40, 50),
    ("n_g16_mabolasi_east_camp", "n_g16_mabolasi_hut", 40, 70),
    ("n_g16_mabolasi_hut", "n_g16_mayalwenlu_east", 60, 50),
    ("n_g16_mayalwenlu_east", "n_g16_makaran", 90, 70),
    ("n_g16_mabolasi", "n_g16_buqian", 70, 60),
    ("n_g16_mabolasi_hut", "n_g16_buqian", 50, 70),

    # === 馬西 chain ===
    ("n_g16_makaran", "n_g16_maxi_jct", 80, 60),
    ("n_g16_maxi_jct", "n_g16_maxi", 100, 70),
    ("n_g16_maxi_jct", "n_g16_majiagan_jct", 60, 50),
    ("n_g16_majiagan_jct", "n_g16_3819", 20, 20),
    ("n_g16_3819", "n_g16_lushipanan", 60, 50),
    ("n_g16_lushipanan", "n_g16_taluna_north", 30, 30),
    ("n_g16_taluna_north", "n_g16_taluna", 30, 30),
    ("n_g16_taluna", "n_g16_taluna_jct", 20, 25),
    ("n_g16_taluna_jct", "n_g16_malijianan", 130, 100),
    ("n_g16_malijianan", "n_g16_malijianan_east", 40, 45),
    ("n_g16_malijianan", "n_g16_yixi", 180, 150),  # 連 G15

    # === 大水窟 area (G17 共用) ===
    ("n_g16_baiyang_mine", "n_g16_dujuan_camp", 60, 80),
    ("n_g16_dujuan_camp", "n_g16_dashuiku_hut", 80, 60),
    ("n_g16_dashuiku_hut", "n_g16_dashuiku_pool", 5, 5),
    ("n_g16_dashuiku_hut", "n_g16_dashuiku", 80, 120),  # 統一與 G17/G18

    # === 玉里林道 下山 chain ===
    ("n_g16_taluna_jct", "n_g16_yuli_44k", 80, 60),
    ("n_g16_yuli_44k", "n_g16_yuli_43k", 25, 20),
    ("n_g16_yuli_43k", "n_g16_jiejing", 60, 80),
    ("n_g16_jiejing", "n_g16_abandoned_gen", 25, 35),
    ("n_g16_abandoned_gen", "n_g16_yuli_35k", 25, 30),
    ("n_g16_yuli_35k", "n_g16_yuli_36k", 30, 30),
    ("n_g16_yuli_35k", "n_g16_xiagu", 30, 45),
    ("n_g16_xiagu", "n_g16_yuli_engineer", 120, 75),
    ("n_g16_yuli_engineer", "n_g16_xiakou_camp", 45, 60),
    ("n_g16_xiakou_camp", "n_g16_dashibing_camp", 70, 80),
    ("n_g16_dashibing_camp", "n_g16_lindao_west", 70, 50),
    ("n_g16_lindao_west", "n_g16_heguworkshop", 25, 20),
    ("n_g16_heguworkshop", "n_g16_stoneside_camp", 30, 30),
    ("n_g16_stoneside_camp", "n_g16_miaopu", 80, 70),
    ("n_g16_miaopu", "n_g16_road_end", 20, 20),
    ("n_g16_road_end", "n_g16_zhongping", 15, 15),
    ("n_g16_zhongping", "n_g16_yuli", 90, 90),   # vehicle
    ("n_g16_zhongping", "n_g16_ruisui", 75, 75), # vehicle
]


PRESETS = [
    {
        "id": "G16-mabolasi-traverse",
        "name": "馬博拉斯橫斷縱走 (7天6夜)",
        "startNodeId": "n_g16_dongpu_hotspring",
        "endNodeId": "n_g16_ruisui",
        "viaNodeIds": [
            "n_g16_8tongguan_th", "n_g16_sansheng_temple", "n_g16_lele_hotspring_jct",
            "n_g16_yunlong_falls", "n_g16_lele_hut", "n_g16_yinv_falls",
            "n_g16_duiguan", "n_g16_guangao_ping", "n_g16_8tongguan",
            "n_g16_zhongyang_mine", "n_g16_baiyang_mine",
            "n_g16_xiugu_ping", "n_g16_xiugu",
            "n_g16_mabolasi", "n_g16_mabolasi_hut",
            "n_g16_mayalwenlu_east", "n_g16_makaran",
            "n_g16_maxi", "n_g16_taluna", "n_g16_malijianan",
            "n_g16_taluna_jct", "n_g16_yuli_44k",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g16_lele_hut", "type": "hut"},
            {"atNodeId": "n_g16_baiyang_mine", "type": "hut"},
            {"atNodeId": "n_g16_xiugu_hut", "type": "hut"},
            {"atNodeId": "n_g16_mabolasi_hut", "type": "hut"},
            {"atNodeId": "n_g16_taluna_jct", "type": "camp"},
            {"atNodeId": "n_g16_xiakou_camp", "type": "camp"},
        ],
        "roundTrip": False,
    },
]


def build():
    route = {
        "id": "G16",
        "name": "馬博拉斯橫斷縱走",
        "version": "2026-05-14",
        "source": "上河文化 G16 馬博拉斯橫斷步程示意圖 (G16_hiking.jpg)",
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
    path = ROUTES_DIR / "G16.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G16 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
