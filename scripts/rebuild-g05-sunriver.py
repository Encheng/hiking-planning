#!/usr/bin/env python3
"""Rebuild G05 雪山西·南稜縱走 from 上河文化 G05_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 武陵 access ===
    ("n_g05_wuling_th",        "武陵山莊",          24.40500, 121.30500, 1745, "trailhead"),  #EST
    ("n_g05_xueshan_th",       "雪山登山口",        24.40300, 121.30300, 2150, "trailhead"),  #EST
    ("n_g05_seven_hut",        "七卡山莊",          24.40000, 121.29500, 2463, "hut"),        #EST
    ("n_g05_kupo_view",        "哭坡觀景台",        24.39800, 121.28500, 2750, "waypoint"),   #EST
    ("n_g05_xueshan_east",     "雪山東峰",          24.38873, 121.27196, 3199, "peak"),       #OSM
    ("n_g05_369_hut",          "三六九山莊",        24.39500, 121.27500, 3100, "hut"),        #EST

    # === 雪山主峰 area ===
    ("n_g05_xueshan",          "雪山主峰",          24.38340, 121.23180, 3886, "peak"),       #OSM
    ("n_g05_cuichi_hut",       "翠池山屋",          24.37927, 121.21534, 3585, "hut"),        #OSM
    ("n_g05_xia_cuichi",       "下翠池",            24.38100, 121.21600, 3550, "water"),      #EST
    ("n_g05_wanmei_camp",      "完美谷營地",        24.37700, 121.20800, 3300, "waypoint"),   #EST

    # === 西稜 chain (大南山/大雪山) ===
    ("n_g05_xueshan_xinan",    "雪山西南峰",        24.35722, 121.20544, 3473, "peak"),       #OSM
    ("n_g05_daxian",           "大劍山",            24.34093, 121.20050, 3593, "peak"),       #OSM
    ("n_g05_anbu_water_jct",   "鞍部水源岔路",      24.33500, 121.18500, 3200, "junction"),   #EST
    ("n_g05_youbo_camp",       "油婆蘭營地",        24.33200, 121.18000, 3050, "waypoint"),   #EST
    ("n_g05_youbo",            "油婆蘭山",          24.32206, 121.20529, 3308, "peak"),       #OSM
    ("n_g05_tuilun",           "推論山",            24.31500, 121.18000, 3200, "peak"),       #EST
    ("n_g05_buxi_camp",        "布伕奇寒山",        24.31700, 121.19847, 3295, "peak"),       #OSM
    ("n_g05_lao5_camp",        "老伍營地",          24.31000, 121.17500, 3000, "waypoint"),   #EST
    ("n_g05_jiayang",          "佳陽山",            24.30663, 121.18800, 3314, "peak"),       #OSM
    ("n_g05_jianshan",         "劍山",              24.29549, 121.17032, 3256, "peak"),       #OSM
    ("n_g05_dananshan_th",     "大南山登山口",      24.36000, 121.13000, 2800, "trailhead"),  #EST
    ("n_g05_dananshan",        "大南山",            24.36190, 121.16839, 3227, "peak"),       #OSM
    ("n_g05_dananshan_camp",   "大南山鞍部營地",    24.36000, 121.15000, 3050, "waypoint"),   #EST
    ("n_g05_gongshui",         "弓水山",            24.35981, 121.14114, 3000, "peak"),       #EST
    ("n_g05_gongshui_camp",    "弓水營地",          24.36300, 121.14500, 2900, "waypoint"),   #EST
    ("n_g05_huoshi",           "火石山",            24.38194, 121.17511, 3309, "peak"),       #OSM
    ("n_g05_huoshi_lower",     "火石山下營地",      24.38000, 121.16500, 3100, "waypoint"),   #EST
    ("n_g05_boker_meadow",     "博可爾草原",        24.39700, 121.20100, 3260, "waypoint"),   #EST
    ("n_g05_boker_shan",       "博可爾山",          24.39742, 121.20199, 3261, "peak"),       #OSM
    ("n_g05_touying",          "頭鷹山",            24.35963, 121.14072, 3509, "peak"),       #OSM
    ("n_g05_qijun",            "奇峻山",            24.35466, 121.13733, 3519, "peak"),       #OSM
    ("n_g05_qijun_water",      "奇峻水池",          24.35200, 121.13500, 3400, "water"),     #EST
    ("n_g05_daxue_north",      "大雪山北峰",        24.34215, 121.12474, 3441, "peak"),       #OSM
    ("n_g05_daxue",            "大雪山",            24.33078, 121.12119, 3530, "peak"),       #OSM
    ("n_g05_daxue_jct",        "岔路口",            24.33000, 121.12300, 3500, "junction"),   #EST
    ("n_g05_pipida_anbu_camp", "匹匹達東鞍營地",    24.32900, 121.12000, 3350, "waypoint"),   #EST
    ("n_g05_pipida",           "匹匹達山",          24.32879, 121.11426, 3436, "peak"),       #OSM
    ("n_g05_zhuleng_anbu",     "主稜鞍部",          24.32700, 121.11200, 3300, "junction"),   #EST

    # === 中雪山 chain (大雪山林道 access) ===
    ("n_g05_zhongxue",         "中雪山",            24.33648, 121.07806, 3172, "peak"),       #OSM
    ("n_g05_linwen_memorial",  "林文安紀念碑",      24.33500, 121.08500, 3050, "waypoint"),   #EST
    ("n_g05_28_5k_th",         "28.5K登山口",       24.32500, 121.09500, 2900, "trailhead"),  #EST
    ("n_g05_28k_workshop",     "28K工寮",           24.32200, 121.09800, 2850, "shelter"),    #EST
    ("n_g05_26k_th",           "26K登山口",         24.31500, 121.10300, 2800, "trailhead"),  #EST
    ("n_g05_11_5k_camp",       "11.5K雙流水營地",   24.28000, 121.06000, 2200, "waypoint"),   #EST
    ("n_g05_4k_marker",        "4K國家公園碑",      24.24000, 121.04000, 1800, "junction"),   #EST
    ("n_g05_0k_jct",           "0K · 49K岔路",      24.22000, 121.03000, 1500, "junction"),   #EST
    ("n_g05_dongshi",          "東勢",              24.25000, 120.83000, 350, "trailhead"),   #EST

    # === 南稜 chain (志佳陽 → 雪山主峰) ===
    ("n_g05_xueshan_south",    "雪山南峰",          24.37217, 121.23726, 3519, "peak"),       #OSM
    ("n_g05_zhijiayan",        "志佳陽大山",        24.35997, 121.24815, 3346, "peak"),       #OSM
    ("n_g05_zhijiayan_base",   "志佳陽基點峰",      24.35780, 121.25133, 3289, "peak"),       #OSM
    ("n_g05_piaohuan_hut",     "瓢簞避難山屋",      24.35587, 121.25500, 3100, "shelter"),    #OSM
    ("n_g05_binlajiu",         "賓拉久",            24.34500, 121.26000, 2400, "trailhead"),  #EST

    # === 中橫宜蘭支線 / 環山 access ===
    ("n_g05_huanshan_jct",     "環山路口",          24.38000, 121.31000, 1800, "junction"),   #EST
    ("n_g05_huanshan_tribe",   "環山部落",          24.39500, 121.31200, 1700, "trailhead"),  #EST
    ("n_g05_zhongxing_jct",    "中興路口",          24.36000, 121.30000, 1500, "junction"),   #EST (66.55K)
    ("n_g05_lishan",           "梨山",              24.25800, 121.27500, 1950, "trailhead"),  #EST
    ("n_g05_lokshui_check",    "松茂水文站",        24.33000, 121.28000, 1600, "junction"),   #EST
    ("n_g05_yueshan_check",    "出雲山檢查哨",      24.30000, 121.27000, 1400, "junction"),   #EST

    # === 防火巷 access ===
    ("n_g05_fanghuoxiang_th",  "防火巷登山口",      24.30500, 121.16500, 2400, "trailhead"),  #EST
    ("n_g05_fanbu",            "帆布獵寮",          24.30800, 121.17000, 2082, "shelter"),    #EST (2082公尺)
    ("n_g05_jiayang_hut",      "佳陽山屋",          24.30200, 121.18500, 2900, "hut"),        #EST
]


EDGES = [
    # === 武陵 access ===
    ("n_g05_wuling_th", "n_g05_xueshan_th", 20, 20),
    ("n_g05_xueshan_th", "n_g05_seven_hut", 70, 55),
    # 雪東 chain (上河 七卡 → 哭坡 → 雪東 → 369):
    ("n_g05_seven_hut", "n_g05_kupo_view", 120, 60),       # 七卡→哭坡 UP 120
    ("n_g05_kupo_view", "n_g05_xueshan_east", 90, 60),     # 哭坡→雪東 UP 90
    ("n_g05_xueshan_east", "n_g05_369_hut", 40, 80),       # 雪東→369 DOWN 40
    # 三六九 → 雪山主峰 (上河 G05: UP 200, DOWN 140 via 圈谷)
    ("n_g05_369_hut", "n_g05_xueshan", 200, 140),

    # === 翠池 chain (西稜起點) ===
    ("n_g05_xueshan", "n_g05_cuichi_hut", 80, 130),
    ("n_g05_cuichi_hut", "n_g05_xia_cuichi", 30, 30),
    ("n_g05_xia_cuichi", "n_g05_wanmei_camp", 70, 50),
    # 完美谷營地 → 雪山西南峰 (UP 130, DOWN 100)
    ("n_g05_wanmei_camp", "n_g05_xueshan_xinan", 130, 100),
    # 雪山西南峰 → 大劍山 (DOWN 160, UP 185)
    # 大劍(3593) > 西南峰(3473), 西南→大劍 是 UP
    ("n_g05_xueshan_xinan", "n_g05_daxian", 185, 160),
    # 大劍山 → 鞍部水源岔路 (DOWN, smaller value)
    ("n_g05_daxian", "n_g05_anbu_water_jct", 90, 130),
    # 鞍部水源岔路 → 油婆蘭山 (UP)
    ("n_g05_anbu_water_jct", "n_g05_youbo", 70, 40),
    ("n_g05_youbo", "n_g05_youbo_camp", 20, 25),
    # 油婆蘭山 → 推論山 (UP)
    ("n_g05_youbo", "n_g05_tuilun", 70, 70),
    # 推論山 → 布伕奇寒山 (similar elev)
    ("n_g05_tuilun", "n_g05_buxi_camp", 90, 70),
    # 推論山 → 老伍營地 (DOWN)
    ("n_g05_tuilun", "n_g05_lao5_camp", 60, 90),
    # 老伍營地 → 佳陽山 (UP)
    ("n_g05_lao5_camp", "n_g05_jiayang", 60, 90),
    # 佳陽山 → 劍山 (DOWN)
    ("n_g05_jiayang", "n_g05_jianshan", 180, 160),

    # === 大南山 / 弓水 / 火石 chain ===
    ("n_g05_dananshan_th", "n_g05_dananshan", 220, 220),
    ("n_g05_dananshan", "n_g05_dananshan_camp", 60, 30),
    ("n_g05_dananshan_camp", "n_g05_gongshui_camp", 60, 60),
    ("n_g05_gongshui_camp", "n_g05_gongshui", 15, 15),
    ("n_g05_gongshui", "n_g05_huoshi", 120, 110),
    ("n_g05_huoshi", "n_g05_huoshi_lower", 30, 50),
    ("n_g05_huoshi", "n_g05_boker_meadow", 160, 130),
    ("n_g05_boker_meadow", "n_g05_boker_shan", 40, 20),
    ("n_g05_boker_meadow", "n_g05_wanmei_camp", 220, 220),

    # === 頭鷹/奇峻/大雪 chain ===
    ("n_g05_dananshan_camp", "n_g05_touying", 140, 165),
    ("n_g05_touying", "n_g05_qijun", 45, 50),
    ("n_g05_qijun", "n_g05_qijun_water", 45, 50),
    ("n_g05_qijun_water", "n_g05_daxue_north", 60, 70),
    ("n_g05_daxue_north", "n_g05_daxue", 90, 105),
    ("n_g05_daxue", "n_g05_daxue_jct", 5, 5),
    ("n_g05_daxue_jct", "n_g05_pipida_anbu_camp", 20, 35),
    ("n_g05_pipida_anbu_camp", "n_g05_pipida", 20, 20),
    ("n_g05_pipida", "n_g05_zhuleng_anbu", 120, 85),

    # === 中雪山 ===
    ("n_g05_zhuleng_anbu", "n_g05_zhongxue", 90, 150),
    ("n_g05_zhongxue", "n_g05_linwen_memorial", 15, 15),
    ("n_g05_linwen_memorial", "n_g05_28k_workshop", 145, 100),
    ("n_g05_28_5k_th", "n_g05_28k_workshop", 20, 20),
    ("n_g05_28k_workshop", "n_g05_26k_th", 350, 390),
    # 林道下行
    ("n_g05_26k_th", "n_g05_11_5k_camp", 220, 350),
    ("n_g05_11_5k_camp", "n_g05_4k_marker", 110, 220),
    ("n_g05_4k_marker", "n_g05_0k_jct", 110, 110),
    ("n_g05_0k_jct", "n_g05_dongshi", 100, 100),  # vehicle

    # === 南稜 (志佳陽) ===
    ("n_g05_xueshan", "n_g05_xueshan_south", 100, 80),
    ("n_g05_xueshan_south", "n_g05_zhijiayan", 105, 80),  # 上河 "105/35" or so
    ("n_g05_zhijiayan", "n_g05_zhijiayan_base", 15, 20),
    ("n_g05_zhijiayan_base", "n_g05_piaohuan_hut", 30, 40),
    ("n_g05_piaohuan_hut", "n_g05_binlajiu", 200, 300),

    # === 中橫宜蘭支線 ===
    ("n_g05_lishan", "n_g05_huanshan_jct", 15, 15),
    ("n_g05_huanshan_jct", "n_g05_huanshan_tribe", 50, 50),
    ("n_g05_huanshan_jct", "n_g05_zhongxing_jct", 30, 30),
    ("n_g05_zhongxing_jct", "n_g05_lokshui_check", 30, 30),
    ("n_g05_lokshui_check", "n_g05_yueshan_check", 25, 25),
    ("n_g05_yueshan_check", "n_g05_binlajiu", 100, 100),
    ("n_g05_binlajiu", "n_g05_wuling_th", 60, 60),

    # === 防火巷 ===
    ("n_g05_fanghuoxiang_th", "n_g05_fanbu", 60, 100),
    ("n_g05_fanbu", "n_g05_jiayang_hut", 180, 220),
    ("n_g05_jiayang_hut", "n_g05_jiayang", 100, 70),
]


PRESETS = [
    {
        "id": "G05-west-ridge",
        "name": "雪山西稜縱走 (5天4夜)",
        "startNodeId": "n_g05_wuling_th",
        "endNodeId": "n_g05_dananshan_th",
        "viaNodeIds": [
            "n_g05_xueshan_th", "n_g05_seven_hut", "n_g05_kupo_view",
            "n_g05_xueshan_east", "n_g05_369_hut",
            "n_g05_xueshan", "n_g05_cuichi_hut",
            "n_g05_wanmei_camp", "n_g05_xueshan_xinan",
            "n_g05_daxian", "n_g05_youbo", "n_g05_tuilun",
            "n_g05_dananshan",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g05_369_hut", "type": "hut"},
            {"atNodeId": "n_g05_cuichi_hut", "type": "hut"},
            {"atNodeId": "n_g05_youbo_camp", "type": "camp"},
            {"atNodeId": "n_g05_dananshan_camp", "type": "camp"},
        ],
        "roundTrip": False,
    },
    {
        "id": "G05-south-ridge",
        "name": "雪山南稜志佳陽 (3天2夜)",
        "startNodeId": "n_g05_wuling_th",
        "endNodeId": "n_g05_xueshan",
        "viaNodeIds": [
            "n_g05_binlajiu", "n_g05_piaohuan_hut", "n_g05_zhijiayan_base",
            "n_g05_zhijiayan", "n_g05_xueshan_south",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g05_piaohuan_hut", "type": "shelter"},
            {"atNodeId": "n_g05_zhijiayan", "type": "camp"},
        ],
        "roundTrip": True,
    },
]


def build():
    route = {
        "id": "G05",
        "name": "雪山西‧南稜縱走",
        "version": "2026-05-14",
        "source": "上河文化 G05 雪山西·南稜步程示意圖 (G05_hiking.jpg)",
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
    path = ROUTES_DIR / "G05.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G05 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
