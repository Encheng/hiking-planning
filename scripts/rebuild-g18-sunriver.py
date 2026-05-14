#!/usr/bin/env python3
"""Rebuild G18 新康橫斷縱走 from 上河文化 G18_hiking.jpg.

Coverage: 向陽 → 嘉明湖 → 戒茂斯 → 布拉克桑 → 新康山 → 瓦拉米 → 南安
"""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 向陽進場 (與 G17 共用) ===
    ("n_g18_xiangyang_forest",  "向陽森林遊樂區",    23.24779, 120.98572, 2370, "trailhead"),  #OSM
    ("n_g18_xiangyang_th",      "林道登山口",        23.25538, 120.98375, 2500, "trailhead"),  #OSM
    ("n_g18_xiangyang_hut",     "向陽山屋",          23.26269, 120.98438, 2880, "hut"),        #OSM
    ("n_g18_xiangyang_west_th", "西側登山口",        23.24764, 120.98278, 3000, "trailhead"),  #OSM
    ("n_g18_xiangyang_peak",    "向陽山",            23.28436, 120.99245, 3602, "peak"),       #OSM
    ("n_g18_jiaminghu_hut",     "嘉明湖避難山屋",    23.28397, 120.99697, 3350, "hut"),        #OSM
    ("n_g18_sanchaa_jct",       "嘉明三岔路口",      23.28800, 121.00200, 3380, "junction"),   #EST (G18 specific name)
    ("n_g18_north_peak_signs",  "北峰下解說牌",      23.29178, 121.00896, 3435, "junction"),   #OSM
    ("n_g18_sanchashan_th",     "三叉山登山口",      23.29425, 121.02291, 3450, "trailhead"),  #OSM
    ("n_g18_sanchashan",        "三叉山",            23.29719, 121.02866, 3495, "peak"),       #OSM
    ("n_g18_jiaminghu_jct",     "嘉明湖岔路口",      23.29589, 121.03306, 3380, "junction"),   #OSM
    ("n_g18_jiaminghu",         "嘉明湖",            23.29339, 121.03411, 3310, "water"),      #OSM
    ("n_g18_jiamingmei_pool",   "嘉明妹池",          23.28271, 121.02872, 3380, "water"),     #OSM

    # === 新康岔路 → 布拉克桑 chain ===
    ("n_g18_xinkang_jct",       "新康岔路口",        23.29695, 121.05463, 3450, "junction"),   #OSM
    ("n_g18_buxin_jct",         "布新岔路口",        23.29500, 121.06000, 3350, "junction"),   #EST
    ("n_g18_3035",              "3035公尺峰",        23.29800, 121.06500, 3035, "peak"),       #EST
    ("n_g18_lianli_east_camp",  "連理東峰前營地",    23.30000, 121.07000, 3100, "waypoint"),   #EST
    ("n_g18_lianli",            "連理山",            23.30600, 121.07430, 3160, "peak"),       #OSM-est

    # === 戒茂斯chain (從南端進場) ===
    ("n_g18_litou",             "利稻",              23.13000, 121.07000, 1100, "trailhead"),  #EST (往海端)
    ("n_g18_xinwu_camp",        "新武呂溪",          23.13500, 121.07500, 1200, "waypoint"),   #EST
    ("n_g18_football_camp",     "足球場營地",        23.14500, 121.08500, 1400, "waypoint"),   #EST
    ("n_g18_jiemou_th",         "戒茂斯登山口",      23.15500, 121.08000, 1450, "trailhead"),  #EST
    ("n_g18_jiemou_front",      "戒茂斯山前峰",      23.16000, 121.08500, 2700, "peak"),       #EST
    ("n_g18_jiemou",            "戒茂斯山",          23.16500, 121.09000, 2934, "peak"),       #EST
    ("n_g18_jiemou_jct",        "戒茂斯岔路口",      23.16300, 121.08700, 2800, "junction"),   #EST
    ("n_g18_bulakesang",        "布拉克桑山",        23.23312, 121.07871, 3022, "peak"),       #OSM
    ("n_g18_2835_an",           "2835鞍部",          23.21000, 121.07500, 2835, "junction"),   #EST
    ("n_g18_grassland_basin",   "草原大窪地",        23.25000, 121.07500, 3000, "waypoint"),   #EST
    ("n_g18_3leng_xia",         "三稜下疊地",        23.27000, 121.07500, 3050, "waypoint"),   #EST

    # === 新康山 chain (主峰) ===
    ("n_g18_xinkang",           "新康山",            23.31660, 121.12760, 3331, "peak"),       #OSM
    ("n_g18_xinxian",           "新仙山",            23.30500, 121.10500, 3210, "peak"),       #EST
    ("n_g18_xinxian_camp",      "新仙山營地",        23.30300, 121.10000, 3150, "waypoint"),   #EST
    ("n_g18_xinxian_front",     "新仙山前營地",      23.30200, 121.09800, 3100, "waypoint"),   #EST
    ("n_g18_xinxian_3jct",      "新仙山三岔路口",    23.30400, 121.10300, 3120, "junction"),   #EST
    ("n_g18_low_an",            "新康最低鞍部",      23.31000, 121.11500, 3050, "junction"),   #EST
    ("n_g18_tiangong_fort",     "天宮堡壘",          23.32200, 121.13000, 3200, "waypoint"),   #EST
    ("n_g18_an_blackpool",      "鞍部黑水塘",        23.30700, 121.09500, 3100, "water"),     #EST
    ("n_g18_taoyuan_camp",      "桃源營地",          23.30500, 121.09000, 3050, "waypoint"),   #EST
    ("n_g18_plane_wreck",       "飛機殘骸",          23.30800, 121.08500, 3000, "waypoint"),   #EST
    ("n_g18_west_east_ridge",   "西峰東稜平台",      23.30500, 121.08000, 2950, "waypoint"),   #EST
    ("n_g18_wall_water",        "山壁水源",          23.30600, 121.09200, 2950, "water"),     #EST

    # === 新康下山 → 瓦拉米 → 南安 ===
    ("n_g18_xiaqiedian",        "下切點",            23.32500, 121.13500, 2700, "junction"),   #EST
    ("n_g18_songzhen_camp",     "松針營地",          23.32800, 121.13800, 2500, "waypoint"),   #EST
    ("n_g18_xinkang_th",        "新康山登山口",      23.33000, 121.14500, 2400, "trailhead"),  #EST
    ("n_g18_baoyai_hut",        "抱崖山屋",          23.33500, 121.16500, 1700, "hut"),        #EST
    ("n_g18_walami_hut",        "瓦拉米山屋",        23.34000, 121.19000, 1300, "hut"),        #EST
    ("n_g18_walami_th",         "瓦拉米步道起點",    23.34500, 121.23000, 700, "trailhead"),   #EST
    ("n_g18_nanan",             "南安遊客中心",      23.34600, 121.25000, 500, "trailhead"),   #EST
    ("n_g18_yuli",              "往玉里",            23.33000, 121.31500, 130, "trailhead"),   #EST
    ("n_g18_to_daxia",          "往大分",            23.36000, 121.18000, 1200, "junction"),   #EST
]


EDGES = [
    # === 向陽 進場 (與 G17 共用 - 統一時間) ===
    ("n_g18_xiangyang_forest", "n_g18_xiangyang_th", 80, 50),
    ("n_g18_xiangyang_th", "n_g18_xiangyang_hut", 70, 40),
    ("n_g18_xiangyang_hut", "n_g18_xiangyang_west_th", 180, 130),
    ("n_g18_xiangyang_west_th", "n_g18_xiangyang_peak", 35, 25),
    ("n_g18_xiangyang_peak", "n_g18_jiaminghu_hut", 45, 60),
    ("n_g18_xiangyang_west_th", "n_g18_jiaminghu_hut", 45, 40),

    # === 嘉明湖 area ===
    ("n_g18_jiaminghu_hut", "n_g18_sanchaa_jct", 15, 15),
    ("n_g18_sanchaa_jct", "n_g18_north_peak_signs", 40, 35),
    ("n_g18_north_peak_signs", "n_g18_sanchashan_th", 80, 55),
    ("n_g18_sanchashan_th", "n_g18_sanchashan", 25, 15),
    ("n_g18_sanchashan_th", "n_g18_jiaminghu_jct", 25, 30),
    ("n_g18_jiaminghu_jct", "n_g18_jiaminghu", 15, 20),
    ("n_g18_jiaminghu_jct", "n_g18_xinkang_jct", 40, 30),
    ("n_g18_jiaminghu", "n_g18_jiamingmei_pool", 20, 20),

    # === 新康橫斷 connection chain ===
    ("n_g18_xinkang_jct", "n_g18_buxin_jct", 30, 20),
    ("n_g18_buxin_jct", "n_g18_3035", 70, 50),
    ("n_g18_3035", "n_g18_lianli_east_camp", 40, 35),
    ("n_g18_lianli_east_camp", "n_g18_lianli", 50, 40),

    # === 戒茂斯 access from 利稻 ===
    ("n_g18_litou", "n_g18_xinwu_camp", 25, 25),  # vehicle
    ("n_g18_xinwu_camp", "n_g18_football_camp", 100, 60),
    ("n_g18_football_camp", "n_g18_jiemou_th", 120, 100),
    ("n_g18_jiemou_th", "n_g18_jiemou_front", 210, 120),
    ("n_g18_jiemou_front", "n_g18_jiemou", 80, 40),
    ("n_g18_jiemou", "n_g18_jiemou_jct", 10, 15),

    # === 戒茂斯 → 布拉克桑 → 三稜下 chain ===
    ("n_g18_jiemou_jct", "n_g18_bulakesang", 120, 100),
    ("n_g18_bulakesang", "n_g18_2835_an", 90, 60),
    ("n_g18_2835_an", "n_g18_grassland_basin", 120, 90),
    ("n_g18_grassland_basin", "n_g18_3leng_xia", 140, 110),
    ("n_g18_3leng_xia", "n_g18_lianli_east_camp", 100, 80),

    # === 連理 → 新仙山 ===
    ("n_g18_lianli", "n_g18_an_blackpool", 110, 90),
    ("n_g18_an_blackpool", "n_g18_xinxian_front", 65, 45),
    ("n_g18_xinxian_front", "n_g18_xinxian_camp", 45, 25),
    ("n_g18_xinxian_camp", "n_g18_xinxian_3jct", 15, 20),
    ("n_g18_xinxian_3jct", "n_g18_xinxian", 1, 1),

    # === 飛機殘骸 / 西峰東稜 side trips ===
    ("n_g18_taoyuan_camp", "n_g18_plane_wreck", 60, 70),
    ("n_g18_plane_wreck", "n_g18_west_east_ridge", 80, 40),
    ("n_g18_an_blackpool", "n_g18_taoyuan_camp", 130, 90),
    ("n_g18_taoyuan_camp", "n_g18_wall_water", 30, 20),

    # === 新仙山 → 新康山 ===
    ("n_g18_xinxian", "n_g18_low_an", 70, 90),
    ("n_g18_low_an", "n_g18_xinkang", 75, 60),
    ("n_g18_xinkang", "n_g18_tiangong_fort", 25, 25),

    # === 新康山 → 瓦拉米 → 南安 ===
    ("n_g18_xinkang", "n_g18_xiaqiedian", 140, 280),
    ("n_g18_xiaqiedian", "n_g18_songzhen_camp", 40, 60),
    ("n_g18_songzhen_camp", "n_g18_xinkang_th", 70, 120),
    ("n_g18_xinkang_th", "n_g18_baoyai_hut", 50, 55),
    ("n_g18_baoyai_hut", "n_g18_walami_hut", 305, 345),
    ("n_g18_walami_hut", "n_g18_walami_th", 295, 335),
    ("n_g18_walami_th", "n_g18_nanan", 20, 20),
    ("n_g18_nanan", "n_g18_yuli", 20, 20),  # vehicle
    ("n_g18_xinkang_th", "n_g18_to_daxia", 140, 50),  # arrow only
]


PRESETS = [
    {
        "id": "G18-traverse",
        "name": "新康橫斷縱走 (7天6夜)",
        "startNodeId": "n_g18_xiangyang_forest",
        "endNodeId": "n_g18_nanan",
        "viaNodeIds": [
            "n_g18_xiangyang_hut", "n_g18_xiangyang_west_th",
            "n_g18_jiaminghu_hut", "n_g18_sanchashan", "n_g18_xinkang_jct",
            "n_g18_lianli", "n_g18_xinxian_camp", "n_g18_xinxian",
            "n_g18_low_an", "n_g18_xinkang",
            "n_g18_xiaqiedian", "n_g18_songzhen_camp",
            "n_g18_baoyai_hut", "n_g18_walami_hut",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g18_xiangyang_hut", "type": "hut"},
            {"atNodeId": "n_g18_jiaminghu_hut", "type": "hut"},
            {"atNodeId": "n_g18_lianli_east_camp", "type": "camp"},
            {"atNodeId": "n_g18_xinxian_camp", "type": "camp"},
            {"atNodeId": "n_g18_baoyai_hut", "type": "hut"},
            {"atNodeId": "n_g18_walami_hut", "type": "hut"},
        ],
        "roundTrip": False,
    },
]


def build():
    route = {
        "id": "G18",
        "name": "新康橫斷縱走",
        "version": "2026-05-14",
        "source": "上河文化 G18 新康橫斷步程示意圖 (G18_hiking.jpg)",
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
    path = ROUTES_DIR / "G18.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G18 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
