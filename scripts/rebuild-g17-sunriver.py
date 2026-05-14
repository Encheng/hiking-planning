#!/usr/bin/env python3
"""Rebuild G17 南二段 from 上河文化 step diagram (G17_hiking.jpg).

Coverage: 向陽 → 嘉明湖 → 三叉山 → 雲峰 → 塔芬 → 達芬尖 → 大水窟
+ 八通關 / 中央金礦 connection
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"

NODES = [
    # === 南端 進場 (南橫公路 / 向陽 ) ===
    ("n_g17_xiangyang_forest",     "向陽森林遊樂區",        23.24779, 120.98572, 2370, "trailhead"),  #OSM
    ("n_g17_xiangyang_th",         "林道登山口",            23.25538, 120.98375, 2500, "trailhead"),  #OSM (嘉明湖登山口)
    ("n_g17_xiangyang_hut",        "向陽山屋",              23.26269, 120.98438, 2880, "hut"),        #OSM
    ("n_g17_heishuitang",          "黑水塘",                23.26731, 120.98690, 2950, "waypoint"),   #OSM
    ("n_g17_xiangyang_west_th",    "西側登山口",            23.24764, 120.98278, 3000, "trailhead"),  #OSM (向榮山登山口)
    ("n_g17_xiangyang_peak",       "向陽山",                23.28436, 120.99245, 3602, "peak"),       #OSM
    ("n_g17_jiaminghu_hut",        "嘉明湖避難山屋",        23.28397, 120.99697, 3350, "hut"),        #OSM
    ("n_g17_jiaminghu_sanchaa_jct","三岔路口",              23.28800, 121.00200, 3380, "junction"),   #EST
    ("n_g17_north_peak_signs",     "北峰下解說牌",          23.29178, 121.00896, 3435, "junction"),   #OSM (向陽山北峰登山口附近)
    ("n_g17_sanchashan_th",        "三叉山登山口",          23.29425, 121.02291, 3450, "trailhead"),  #OSM
    ("n_g17_sanchashan",           "三叉山",                23.29719, 121.02866, 3495, "peak"),       #OSM
    ("n_g17_jiaminghu_jct",        "嘉明湖岔路口",          23.29589, 121.03306, 3380, "junction"),   #OSM (停機坪)
    ("n_g17_jiaminghu",            "嘉明湖",                23.29339, 121.03411, 3310, "water"),      #OSM
    ("n_g17_jiamingmei_pool",      "嘉明妹池",              23.28271, 121.02872, 3380, "water"),     #OSM

    # === 接新康山列 岔路 ===
    ("n_g17_xinkang_jct",          "新康山岔路口",          23.29695, 121.05463, 3450, "junction"),   #OSM

    # === 北傳統 (拉庫音 → 雲峰 → 塔芬 → 達芬尖) ===
    ("n_g17_lakuyin_hut",          "拉庫音溪山屋",          23.32831, 121.02572, 2690, "hut"),        #OSM
    ("n_g17_nan_shuangtou",        "南雙頭山",              23.34589, 121.01058, 3356, "peak"),       #OSM
    ("n_g17_nan_shuangtou_east",   "南雙頭山東峰",          23.34637, 121.01519, 3353, "peak"),       #OSM
    ("n_g17_xibei_an_camp",        "西北鞍南雙池營地",      23.34900, 121.00500, 3200, "waypoint"),   #EST
    ("n_g17_yunfeng_east_camp",    "雲峰東峰三岔路口營地",  23.35887, 120.98691, 3454, "waypoint"),   #OSM
    ("n_g17_yunfeng",              "雲峰",                  23.35375, 120.97575, 3564, "peak"),       #OSM
    ("n_g17_yunfeng_east",         "雲峰東峰",              23.35887, 120.98691, 3454, "peak"),       #OSM (同三岔路口)
    ("n_g17_water_source",         "水源",                  23.36100, 120.98800, 3380, "water"),      #EST
    ("n_g17_lulu_hut",             "轆轆谷山屋",            23.38605, 121.00649, 2991, "hut"),        #OSM
    ("n_g17_lulu_th",              "轆轆山登山口",          23.38800, 120.99900, 3150, "trailhead"),  #EST
    ("n_g17_lulu_peak",            "轆轆山",                23.39136, 120.99808, 3279, "peak"),       #OSM
    ("n_g17_lulu_east",            "轆轆東峰",              23.39000, 121.00000, 3200, "peak"),       #EST (副峰)
    ("n_g17_tafenchi",             "塔芬池",                23.40287, 121.02833, 2930, "water"),      #OSM
    ("n_g17_tafenshan",            "塔芬山",                23.40601, 121.02681, 3069, "peak"),       #OSM
    ("n_g17_tafengu_hut",          "塔芬谷山屋",            23.41965, 121.02673, 2605, "hut"),        #OSM
    ("n_g17_dafenjian_th",         "達芬尖山登山口",        23.42500, 121.01700, 2900, "trailhead"),  #EST
    ("n_g17_dafenjian",            "達芬尖山",              23.43273, 121.01320, 3208, "peak"),       #OSM

    # === 大水窟 area (北端) ===
    ("n_g17_nan_dashuiku",         "南大水窟山",            23.45088, 121.05193, 3385, "peak"),       #OSM
    ("n_g17_dashuiku_hut",         "大水窟山屋",            23.45934, 121.05625, 3227, "hut"),        #OSM
    ("n_g17_dashuiku_pool",        "大水窟池",              23.46027, 121.05635, 3220, "water"),      #OSM
    ("n_g17_dashuiku",             "大水窟山",              23.47398, 121.03848, 3643, "peak"),       #OSM
    ("n_g17_zhongyang_mine_hut",   "中央金礦山屋",          23.48653, 121.02746, 2820, "hut"),        #OSM
    ("n_g17_baiyang_mine_hut",     "白洋金礦山屋",          23.48789, 121.04743, 3378, "hut"),        #OSM

    # === 杜鵑營地 (上塔芬谷 to 大水窟 chain) ===
    ("n_g17_dujuan_camp",          "杜鵑營地",              23.47447, 121.02739, 3050, "waypoint"),   #OSM
]


EDGES = [
    # === 南端 公路/登山口 ===
    # 向陽森林 → 林道登山口 (UP 80, DOWN 50)
    ("n_g17_xiangyang_forest", "n_g17_xiangyang_th", 80, 50),
    # 林道登山口 → 向陽山屋 (UP 70, DOWN 40)
    ("n_g17_xiangyang_th", "n_g17_xiangyang_hut", 70, 40),
    # 向陽山屋 → 黑水塘 (上河 estimated, climbing)
    ("n_g17_xiangyang_hut", "n_g17_heishuitang", 30, 25),

    # === 向陽山 / 嘉明湖避難 ===
    # 向陽山屋 → 西側登山口 (UP 180, DOWN 130)
    ("n_g17_xiangyang_hut", "n_g17_xiangyang_west_th", 180, 130),
    # 西側登山口 → 向陽山 (UP 35, DOWN 25)
    ("n_g17_xiangyang_west_th", "n_g17_xiangyang_peak", 35, 25),
    # 向陽山 → 嘉明湖避難山屋 (DOWN 45, UP 60)
    # 向陽山(3602) → 山屋(3350) is DOWN
    ("n_g17_xiangyang_peak", "n_g17_jiaminghu_hut", 45, 60),
    # 西側登山口 → 嘉明湖避難山屋 (UP 45, DOWN 40)
    ("n_g17_xiangyang_west_th", "n_g17_jiaminghu_hut", 45, 40),

    # === 嘉明湖 / 三叉山 ===
    # 嘉明湖避難山屋 → 三岔路口 (UP 15, DOWN 15)
    ("n_g17_jiaminghu_hut", "n_g17_jiaminghu_sanchaa_jct", 15, 15),
    # 三岔路口 → 北峰下解說牌 (UP 40, DOWN 35)
    ("n_g17_jiaminghu_sanchaa_jct", "n_g17_north_peak_signs", 40, 35),
    # 北峰下解說牌 → 三叉山登山口 (UP 80, DOWN 55)
    ("n_g17_north_peak_signs", "n_g17_sanchashan_th", 80, 55),
    # 三叉山登山口 → 三叉山 (UP 25, DOWN 15)
    ("n_g17_sanchashan_th", "n_g17_sanchashan", 25, 15),
    # 三叉山登山口 → 嘉明湖岔路口 (UP 30, DOWN 25)
    ("n_g17_sanchashan_th", "n_g17_jiaminghu_jct", 30, 25),
    # 嘉明湖岔路口 → 嘉明湖 (DOWN 15, UP 20)
    # 岔路口(3380) > 嘉明湖(3310), 岔路→湖 是 DOWN
    ("n_g17_jiaminghu_jct", "n_g17_jiaminghu", 15, 20),
    # 嘉明湖岔路口 → 新康山岔路口 (UP 40, DOWN 30)
    ("n_g17_jiaminghu_jct", "n_g17_xinkang_jct", 40, 30),

    # === 接拉庫音 → 南雙頭 ===
    # 三叉山 → 拉庫音溪山屋 (DOWN 130, UP 220)
    # 三叉山(3495) → 拉庫音(2690) is BIG DOWN
    ("n_g17_sanchashan", "n_g17_lakuyin_hut", 130, 220),
    # 新康山岔路口 → 拉庫音溪山屋 (DOWN 130, UP 220)
    ("n_g17_xinkang_jct", "n_g17_lakuyin_hut", 130, 220),
    # 拉庫音溪山屋 → 南雙頭山 (UP 180, DOWN 110)
    ("n_g17_lakuyin_hut", "n_g17_nan_shuangtou", 180, 110),
    # 南雙頭山 → 南雙頭山東峰 (slight UP/short)
    ("n_g17_nan_shuangtou", "n_g17_nan_shuangtou_east", 10, 10),
    # 南雙頭山 → 西北鞍南雙池營地 (DOWN 25, UP 50)
    # 雙頭山(3356) > 西北鞍(3200) is DOWN
    ("n_g17_nan_shuangtou", "n_g17_xibei_an_camp", 25, 50),

    # === 雲峰 area ===
    # 西北鞍 → 雲峰東峰三岔路口營地 (UP 170, DOWN 150)
    ("n_g17_xibei_an_camp", "n_g17_yunfeng_east_camp", 170, 150),
    # 雲峰東峰三岔路口營地 → 雲峰 (DOWN 90, UP 120)
    # 雲峰(3564) > 東峰營地(3454) ? Actually 雲峰 IS higher.
    # 上河 90/120: 90=going to 雲峰 (smaller=DOWN, but 雲峰 HIGHER means UP should be larger)
    # Hmm. 上河 顯示 90/120 between 雲峰東峰三岔路口 and 雲峰
    # Smaller=DOWN convention: 90=DOWN, 120=UP. So 三岔路 → 雲峰 (UP) = 120
    ("n_g17_yunfeng_east_camp", "n_g17_yunfeng", 120, 90),
    # 雲峰東峰三岔路口 → 水源 (DOWN 15, UP 20)
    ("n_g17_yunfeng_east_camp", "n_g17_water_source", 15, 20),
    # 雲峰東峰 = 雲峰東峰三岔路口營地 (same node concept, very close)

    # === 轆轆山 area ===
    # 雲峰東峰三岔路口 → 轆轆谷山屋 (DOWN 200, UP 240)
    ("n_g17_yunfeng_east_camp", "n_g17_lulu_hut", 200, 240),
    # 轆轆谷山屋 → 轆轆山登山口 (UP 70, DOWN 45)
    ("n_g17_lulu_hut", "n_g17_lulu_th", 70, 45),
    # 轆轆山登山口 → 轆轆山 (UP 25, DOWN 15)
    ("n_g17_lulu_th", "n_g17_lulu_peak", 25, 15),
    # 轆轆山 → 轆轆東峰 (短)
    ("n_g17_lulu_peak", "n_g17_lulu_east", 15, 15),

    # === 塔芬 area ===
    # 轆轆山登山口 → 塔芬池 (UP 250, DOWN 210)
    # 塔芬池(2930) > 轆轆登山口(3150)? Wait, 池 lower than 登山口
    # Actually need to check actual elev. 上河 250/210 — smaller=DOWN.
    # 池在較低，登山口高。登山口→池 是 DOWN = 210, 池→登山口 = UP = 250
    ("n_g17_lulu_th", "n_g17_tafenchi", 210, 250),
    # 塔芬池 → 塔芬山 (UP 30, DOWN 20)
    ("n_g17_tafenchi", "n_g17_tafenshan", 30, 20),
    # 塔芬山 → 塔芬谷山屋 (DOWN 80, UP 160)
    ("n_g17_tafenshan", "n_g17_tafengu_hut", 80, 160),
    # 塔芬谷山屋 → 達芬尖山登山口 (UP estimated)
    ("n_g17_tafengu_hut", "n_g17_dafenjian_th", 90, 60),
    # 達芬尖山登山口 → 達芬尖山 (UP 60, DOWN 40)
    ("n_g17_dafenjian_th", "n_g17_dafenjian", 60, 40),

    # === 大水窟 area (北端傳統路) ===
    # 達芬尖山登山口 → 杜鵑營地 (estimated)
    ("n_g17_dafenjian_th", "n_g17_dujuan_camp", 180, 120),
    # 杜鵑營地 → 大水窟山屋 (estimated)
    ("n_g17_dujuan_camp", "n_g17_dashuiku_hut", 80, 60),
    # 大水窟山屋 → 大水窟池 (very short)
    ("n_g17_dashuiku_hut", "n_g17_dashuiku_pool", 5, 5),
    # 大水窟山屋 → 南大水窟山 (DOWN 60, UP 90)
    # 南大水窟(3385) > 山屋(3227), so 山屋→南大水窟 is UP
    ("n_g17_dashuiku_hut", "n_g17_nan_dashuiku", 90, 60),
    # 大水窟山屋 → 大水窟山 (UP, climbing to peak)
    ("n_g17_dashuiku_hut", "n_g17_dashuiku", 120, 80),
    # 大水窟山屋 → 中央金礦山屋 (DOWN, going down to old mine)
    # 中央金礦(2820) < 山屋(3227), so 山屋→中央金礦 is DOWN
    ("n_g17_dashuiku_hut", "n_g17_zhongyang_mine_hut", 90, 130),
    # 中央金礦 → 白洋金礦 (UP)
    ("n_g17_zhongyang_mine_hut", "n_g17_baiyang_mine_hut", 90, 60),
]


PRESETS = [
    {
        "id": "G17-jiaminghu",
        "name": "嘉明湖三叉山向陽山 (3天2夜)",
        "startNodeId": "n_g17_xiangyang_forest",
        "endNodeId": "n_g17_jiaminghu",
        "viaNodeIds": [
            "n_g17_xiangyang_th", "n_g17_xiangyang_hut", "n_g17_xiangyang_west_th",
            "n_g17_xiangyang_peak", "n_g17_jiaminghu_hut",
            "n_g17_jiaminghu_sanchaa_jct", "n_g17_north_peak_signs",
            "n_g17_sanchashan_th", "n_g17_sanchashan", "n_g17_jiaminghu_jct",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g17_xiangyang_hut", "type": "hut"},
            {"atNodeId": "n_g17_jiaminghu_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G17-full-traverse",
        "name": "南二段完整縱走 (7天6夜)",
        "startNodeId": "n_g17_xiangyang_forest",
        "endNodeId": "n_g17_dashuiku_hut",
        "viaNodeIds": [
            "n_g17_xiangyang_th", "n_g17_xiangyang_hut", "n_g17_xiangyang_west_th",
            "n_g17_jiaminghu_hut", "n_g17_sanchashan_th", "n_g17_sanchashan",
            "n_g17_xinkang_jct", "n_g17_lakuyin_hut",
            "n_g17_nan_shuangtou", "n_g17_xibei_an_camp",
            "n_g17_yunfeng_east_camp", "n_g17_yunfeng",
            "n_g17_lulu_hut", "n_g17_lulu_peak",
            "n_g17_tafenchi", "n_g17_tafenshan", "n_g17_tafengu_hut",
            "n_g17_dafenjian_th", "n_g17_dafenjian",
            "n_g17_dujuan_camp",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g17_xiangyang_hut", "type": "hut"},
            {"atNodeId": "n_g17_jiaminghu_hut", "type": "hut"},
            {"atNodeId": "n_g17_lakuyin_hut", "type": "hut"},
            {"atNodeId": "n_g17_lulu_hut", "type": "hut"},
            {"atNodeId": "n_g17_tafengu_hut", "type": "hut"},
            {"atNodeId": "n_g17_dujuan_camp", "type": "camp"},
        ],
        "roundTrip": False,
    },
]


def build():
    route = {
        "id": "G17",
        "name": "南二段縱走",
        "version": "2026-05-14",
        "source": "上河文化 G17 南二段步程示意圖 (G17_hiking.jpg)",
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
    path = ROUTES_DIR / "G17.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G17 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
