#!/usr/bin/env python3
"""Rebuild G04 大霸·聖稜·武陵四秀 from 上河文化 G04_hiking.jpg.

Coverage: 大霸 + 聖稜 Y 縱走 + 武陵四秀
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"

NODES = [
    # === 觀霧 / 大霸 進場 ===
    ("n_g04_guanwu",          "觀霧",              24.50500, 121.10500, 2100, "trailhead"),  #EST
    ("n_g04_check_0_3k",      "0.3K檢查哨",        24.50300, 121.11000, 2120, "junction"),   #EST
    ("n_g04_dabajian_th",     "大霸尖山登山口",    24.49000, 121.18000, 2200, "trailhead"),  #EST
    ("n_g04_jiujiu_hut",      "九九山莊",          24.47000, 121.20000, 2700, "hut"),        #EST
    ("n_g04_jiali_th",        "加利山登山口",      24.47000, 121.22000, 3000, "trailhead"),  #EST
    ("n_g04_jiali",           "加利山",            24.46500, 121.21500, 3112, "peak"),       #EST
    ("n_g04_yize_th",         "伊澤山第二登山口",  24.46500, 121.23000, 3150, "trailhead"),  #EST
    ("n_g04_yize_8_8k_jct",   "8.8K岔路",          24.46300, 121.23500, 3200, "junction"),   #EST
    ("n_g04_yize",            "伊澤山",            24.46139, 121.24269, 3297, "peak"),       #EST
    ("n_g04_camp_2",          "第二營地",          24.46000, 121.24800, 3200, "waypoint"),   #EST
    ("n_g04_mayang_shan",     "馬洋山",            24.45000, 121.25000, 3220, "peak"),       #EST
    ("n_g04_mayang_chi",      "馬洋池",            24.45200, 121.25500, 3050, "water"),      #EST
    ("n_g04_zhongba_jct",     "中霸坪叉路",        24.45500, 121.25800, 3380, "junction"),   #EST
    ("n_g04_xiaoba_jct_th",   "小霸岔路登山口",    24.45700, 121.25700, 3450, "junction"),   #EST
    ("n_g04_xiaoba",          "小霸尖山",          24.46160, 121.25180, 3445, "peak"),       #OSM
    ("n_g04_banan_hut",       "霸南山屋",          24.45400, 121.26000, 3300, "hut"),        #EST
    ("n_g04_dabajian",        "大霸尖山",          24.45844, 121.25653, 3492, "peak"),       #OSM
    ("n_g04_basha_hut_ruins", "巴紗拉雲山屋(毀損)",24.44700, 121.26200, 3200, "shelter"),    #EST
    ("n_g04_basha",           "巴紗拉雲山",        24.43869, 121.25812, 3407, "peak"),       #OSM
    ("n_g04_takejin_river",   "塔克金溪源頭",      24.43500, 121.26000, 3100, "waypoint"),   #EST

    # === 鎮西堡 alternative access ===
    ("n_g04_zhenxibao",       "鎮西堡",            24.65000, 121.40000, 1700, "trailhead"),  #EST
    ("n_g04_shenmu_th",       "神木區登山口",      24.62000, 121.38000, 1750, "trailhead"),  #EST
    ("n_g04_shenmu_jct",      "A.B區神木岔路",     24.60000, 121.36000, 2000, "junction"),   #EST
    ("n_g04_zhenxi_jct",      "鎮西堡岔路口",      24.55000, 121.32000, 2500, "junction"),   #EST
    ("n_g04_mayang_jct",      "往馬洋山岔路口",    24.50000, 121.27000, 2800, "junction"),   #EST
    ("n_g04_lieliao_camp",    "獵寮營地",          24.47000, 121.26500, 2900, "waypoint"),   #EST
    ("n_g04_camp_1",          "第一營地",          24.46500, 121.26000, 3000, "waypoint"),   #EST

    # === 聖稜縱走 (大霸→雪山) ===
    ("n_g04_susmida",         "素密達山",          24.42510, 121.25355, 3517, "peak"),       #OSM
    ("n_g04_susmida_hut",     "素密達山屋",        24.42300, 121.25200, 3450, "hut"),        #EST
    ("n_g04_susmida_jct",     "素密達岔路",        24.42400, 121.25100, 3480, "junction"),   #EST
    ("n_g04_mutele",          "穆特勒布山",        24.42496, 121.24927, 3623, "peak"),       #OSM
    ("n_g04_susmida_water",   "水源",              24.42200, 121.25400, 3400, "water"),     #EST
    ("n_g04_xinda_hut",       "新達山屋·水池",     24.42500, 121.27500, 3220, "hut"),        #EST
    ("n_g04_pinta_qianfeng",  "品田山前峰",        24.42758, 121.26923, 3442, "peak"),       #OSM
    ("n_g04_pinta",           "品田山",            24.42830, 121.26677, 3524, "peak"),       #OSM
    ("n_g04_buxiulan",        "布秀蘭山",          24.42889, 121.25921, 3452, "peak"),       #OSM
    ("n_g04_chiyou",          "池有山",            24.43110, 121.28815, 3303, "peak"),       #OSM
    ("n_g04_chiyou_th",       "池有山登山口",      24.43200, 121.28600, 3250, "junction"),   #EST
    ("n_g04_yancai_falls",    "煙聲瀑布",          24.43800, 121.29000, 2300, "water"),     #EST
    ("n_g04_sanchayingdi",    "三叉營地",          24.43200, 121.29500, 3250, "waypoint"),   #EST
    ("n_g04_toushan_hut",     "桃山山屋",          24.43317, 121.30260, 3175, "hut"),        #OSM
    ("n_g04_toushan",         "桃山",              24.43264, 121.30489, 3325, "peak"),       #OSM
    ("n_g04_shilun",          "詩崙山",            24.43000, 121.31000, 3149, "peak"),       #EST
    ("n_g04_kalaye",          "喀拉業山",          24.43500, 121.31500, 3133, "peak"),       #EST (詩崙山附近)

    # === 雪北 chain ===
    ("n_g04_xueshan_north",   "雪山北峰",          24.41471, 121.24040, 3703, "peak"),       #OSM
    ("n_g04_xuebei_th",       "雪北登山口",        24.41500, 121.24300, 3680, "junction"),   #EST
    ("n_g04_xuebei_hut",      "雪北山屋",          24.41168, 121.24293, 3585, "hut"),        #OSM (estimate)
    ("n_g04_munan_camp",      "穆南鞍部營地",      24.41800, 121.24700, 3450, "waypoint"),   #EST
    ("n_g04_kailan_north",    "凱蘭特崑山北峰",    24.39843, 121.23498, 3707, "peak"),       #OSM
    ("n_g04_anbu_jct",        "鞍部叉路",          24.39500, 121.23500, 3650, "junction"),   #EST
    ("n_g04_kailan",          "凱蘭特崑山",        24.39534, 121.23413, 3731, "peak"),       #OSM
    ("n_g04_beling",          "北稜角",            24.38751, 121.23114, 3882, "peak"),       #OSM
    ("n_g04_xueshan_jct",     "岔路口",            24.38500, 121.23200, 3850, "junction"),   #EST
    ("n_g04_xueshan",         "雪山主峰",          24.38340, 121.23180, 3886, "peak"),       #OSM (主峰)
    ("n_g04_cuichi_hut",      "翠池山屋",          24.37927, 121.21534, 3585, "hut"),        #OSM (翠池三叉山)

    # === 雪東 chain ===
    ("n_g04_xueshan_east",    "雪山東峰",          24.38873, 121.27196, 3199, "peak"),       #OSM
    ("n_g04_369_hut",         "三六九山莊",        24.39500, 121.27500, 3100, "hut"),        #EST
    ("n_g04_circle_bottom",   "圈谷底部",          24.38800, 121.24000, 3400, "waypoint"),   #EST
    ("n_g04_kupo_view",       "哭坡觀景台",        24.39800, 121.28500, 2750, "waypoint"),   #EST
    ("n_g04_seven_hut",       "七卡山莊",          24.40000, 121.30000, 2463, "hut"),        #EST
    ("n_g04_xueshan_admin",   "雪山登山口",        24.40300, 121.30300, 2150, "trailhead"),  #EST
    ("n_g04_wuling_admin",    "武陵山莊",          24.40500, 121.30500, 1745, "junction"),   #EST
    ("n_g04_farm_jct",        "農場岔路",          24.41000, 121.31000, 1800, "junction"),   #EST
    ("n_g04_wuling_farm",     "武陵農場·遊客中心", 24.40800, 121.31700, 1745, "trailhead"),  #EST
    ("n_g04_toushan_th",      "桃山登山口",        24.41500, 121.31000, 1900, "trailhead"),  #EST
    ("n_g04_toushan_2k",      "桃山2K",            24.42000, 121.30800, 2400, "junction"),   #EST
    ("n_g04_helipad",         "停機坪",            24.42500, 121.30700, 2900, "junction"),   #EST
    ("n_g04_chiyou_jct",      "桃山岔路口",        24.43000, 121.30800, 2950, "junction"),   #EST

    # === 志佳陽 (Y traverse 第二翼) ===
    ("n_g04_zhijiayan",       "志佳陽大山",        24.35997, 121.24815, 3346, "peak"),       #OSM
    ("n_g04_piaohuan_hut",    "瓢簞避難山屋",      24.35587, 121.25501, 3100, "shelter"),    #OSM-ish
    ("n_g04_zhijiayan_th",    "志佳陽登山口",      24.30650, 121.22400, 1700, "trailhead"),  #EST
]


EDGES = [
    # === 大霸 進場 ===
    ("n_g04_guanwu", "n_g04_check_0_3k", 10, 10),
    # 0.3K → 大霸登山口 (UP 430, DOWN 400 — 林道)
    ("n_g04_check_0_3k", "n_g04_dabajian_th", 430, 400),
    # 大霸登山口 → 九九山莊 (UP 130, DOWN 210)
    # Wait: 九九山莊 (2700) > 大霸登山口 (2200)? 上河 130/210
    # 130 < 210, so 130=DOWN, 210=UP. But 九九山莊 higher → 登山口→山莊 (UP) = 210
    ("n_g04_dabajian_th", "n_g04_jiujiu_hut", 210, 130),
    # 九九山莊 → 加利山登山口 (UP 80, DOWN 50)
    # 加利山登山口 (3000) > 九九山莊 (2700), so UP=80
    ("n_g04_jiujiu_hut", "n_g04_jiali_th", 80, 50),
    # 加利山登山口 → 加利山 (30/30)
    ("n_g04_jiali_th", "n_g04_jiali", 30, 30),
    # 加利山登山口 → 伊澤山第二登山口 (UP 50, DOWN 40)
    ("n_g04_jiali_th", "n_g04_yize_th", 50, 40),
    # 伊澤山第二登山口 → 8.8K岔路 (UP 30, DOWN 20)
    ("n_g04_yize_th", "n_g04_yize_8_8k_jct", 30, 20),
    # 8.8K岔路 → 伊澤山 (10/15)
    ("n_g04_yize_8_8k_jct", "n_g04_yize", 15, 10),
    # 8.8K岔路 → 中霸坪叉路 (60/45)
    ("n_g04_yize_8_8k_jct", "n_g04_zhongba_jct", 60, 45),
    # 伊澤山 → 第二營地 (10/15)
    ("n_g04_yize", "n_g04_camp_2", 15, 10),
    # 第二營地 → 馬洋山 (10/15)
    ("n_g04_camp_2", "n_g04_mayang_shan", 15, 10),
    # 馬洋山 → 馬洋池 (DOWN 100, UP 110)
    # 馬洋池(3050) < 馬洋山(3220), so 山→池 是 DOWN
    ("n_g04_mayang_shan", "n_g04_mayang_chi", 100, 110),
    # 馬洋池 → 中霸坪叉路 (UP 180, DOWN 100)
    # 中霸坪(3380) > 馬洋池(3050)
    ("n_g04_mayang_chi", "n_g04_zhongba_jct", 180, 100),
    # 中霸坪叉路 → 小霸岔路登山口 (UP 45, DOWN 40)
    ("n_g04_zhongba_jct", "n_g04_xiaoba_jct_th", 45, 40),
    # 小霸岔路登山口 → 小霸尖山 (DOWN 35, UP 50)
    # 小霸尖山(3445) < 登山口(3450), 差距小, 估
    ("n_g04_xiaoba_jct_th", "n_g04_xiaoba", 50, 35),
    # 小霸岔路登山口 → 霸南山屋 (UP 100, DOWN ... only one shown)
    ("n_g04_xiaoba_jct_th", "n_g04_banan_hut", 100, 70),
    # 霸南山屋 → 大霸尖山 (60/?)
    ("n_g04_banan_hut", "n_g04_dabajian", 50, 70),

    # === 鎮西堡 access ===
    ("n_g04_zhenxibao", "n_g04_shenmu_th", 10, 10),  # vehicle drive
    ("n_g04_shenmu_th", "n_g04_shenmu_jct", 40, 35),
    ("n_g04_shenmu_jct", "n_g04_zhenxi_jct", 50, 40),
    ("n_g04_zhenxi_jct", "n_g04_mayang_jct", 130, 70),
    ("n_g04_mayang_jct", "n_g04_lieliao_camp", 120, 80),
    ("n_g04_lieliao_camp", "n_g04_camp_1", 45, 25),
    ("n_g04_camp_1", "n_g04_camp_2", 25, 45),

    # === 大霸 → 巴紗拉雲 → 素密達 ===
    ("n_g04_dabajian", "n_g04_basha_hut_ruins", 60, 80),
    ("n_g04_basha_hut_ruins", "n_g04_basha", 60, 80),
    ("n_g04_basha", "n_g04_susmida", 130, 140),  # 巴紗 → 素密達

    # === 素密達 / 穆特勒布 ===
    ("n_g04_susmida", "n_g04_susmida_hut", 70, 90),
    ("n_g04_susmida_hut", "n_g04_susmida_jct", 10, 10),
    ("n_g04_susmida_jct", "n_g04_mutele", 20, 30),  # 穆特勒布 higher
    ("n_g04_susmida_hut", "n_g04_susmida_water", 15, 25),

    # === 武陵四秀 / 新達 / 池有 / 桃山 ===
    ("n_g04_susmida_jct", "n_g04_xinda_hut", 50, 60),  # 估
    ("n_g04_xinda_hut", "n_g04_pinta", 120, 80),  # 新達 → 品田
    # 池有山登山口 ↔ 新達: 50/60
    ("n_g04_xinda_hut", "n_g04_chiyou_th", 50, 60),
    ("n_g04_chiyou_th", "n_g04_chiyou", 20, 15),
    ("n_g04_chiyou_th", "n_g04_sanchayingdi", 5, 5),
    ("n_g04_sanchayingdi", "n_g04_toushan_hut", 140, 150),
    ("n_g04_toushan_hut", "n_g04_toushan", 10, 10),
    ("n_g04_toushan", "n_g04_shilun", 90, 70),
    ("n_g04_shilun", "n_g04_kalaye", 30, 30),

    # === 品田 → 布秀蘭 ===
    ("n_g04_pinta", "n_g04_buxiulan", 200, 240),  # 品田 → 布秀蘭 (along ridge)
    ("n_g04_buxiulan", "n_g04_basha", 140, 110),

    # === 池有山登山口 → 武陵 ===
    ("n_g04_chiyou_th", "n_g04_yancai_falls", 10, 10),
    ("n_g04_chiyou_th", "n_g04_chiyou_jct", 180, 280),  # 大下坡到武陵
    ("n_g04_chiyou_jct", "n_g04_wuling_admin", 20, 20),

    # === 桃山 → 武陵 ===
    ("n_g04_toushan", "n_g04_helipad", 90, 160),
    ("n_g04_helipad", "n_g04_toushan_2k", 30, 50),
    ("n_g04_toushan_2k", "n_g04_toushan_th", 100, 180),
    ("n_g04_toushan_th", "n_g04_wuling_admin", 3, 5),

    # === 武陵 vehicle area ===
    ("n_g04_wuling_admin", "n_g04_farm_jct", 10, 10),  # vehicle
    ("n_g04_farm_jct", "n_g04_wuling_farm", 10, 10),   # vehicle

    # === 七卡 / 雪山東稜 / 三六九 / 雪山主峰 ===
    ("n_g04_wuling_farm", "n_g04_xueshan_admin", 20, 20),  # vehicle
    ("n_g04_xueshan_admin", "n_g04_seven_hut", 70, 55),
    ("n_g04_seven_hut", "n_g04_kupo_view", 120, 60),
    ("n_g04_kupo_view", "n_g04_xueshan_east", 90, 60),
    ("n_g04_xueshan_east", "n_g04_369_hut", 40, 80),
    ("n_g04_369_hut", "n_g04_circle_bottom", 100, 140),
    ("n_g04_circle_bottom", "n_g04_xueshan", 110, 55),
    # 三六九 ↔ 主峰 (上河 G05 200/140: UP 200, DOWN 140)
    ("n_g04_369_hut", "n_g04_xueshan", 200, 140),

    # === 雪北 ↔ 主峰 chain (聖稜南段) ===
    ("n_g04_xueshan", "n_g04_xueshan_jct", 20, 15),
    ("n_g04_xueshan_jct", "n_g04_beling", 15, 10),
    ("n_g04_beling", "n_g04_kailan", 70, 40),
    ("n_g04_kailan", "n_g04_anbu_jct", 10, 5),
    ("n_g04_anbu_jct", "n_g04_kailan_north", 5, 5),
    ("n_g04_anbu_jct", "n_g04_circle_bottom", 100, 50),  # 鞍部叉 → 溪源 → 圈谷底
    ("n_g04_kailan_north", "n_g04_xuebei_hut", 90, 75),
    ("n_g04_xuebei_hut", "n_g04_xuebei_th", 25, 35),
    ("n_g04_xuebei_th", "n_g04_munan_camp", 95, 65),
    ("n_g04_xuebei_th", "n_g04_xueshan_north", 5, 5),
    ("n_g04_munan_camp", "n_g04_susmida", 100, 85),

    # === 翠池 ===
    ("n_g04_xueshan_jct", "n_g04_cuichi_hut", 80, 110),

    # === 志佳陽 (Y型 alternative) ===
    ("n_g04_zhijiayan_th", "n_g04_piaohuan_hut", 300, 200),  # long climb
    ("n_g04_piaohuan_hut", "n_g04_zhijiayan", 60, 40),
    ("n_g04_zhijiayan", "n_g04_xueshan", 240, 180),  # 志佳陽 → 主峰 (long ridge)
]


PRESETS = [
    {
        "id": "G04-sheng-leng-Y",
        "name": "聖稜Y縱走 (4天3夜，武陵進出)",
        "startNodeId": "n_g04_wuling_admin",
        "endNodeId": "n_g04_wuling_admin",
        "viaNodeIds": [
            "n_g04_xueshan_admin", "n_g04_seven_hut", "n_g04_kupo_view",
            "n_g04_xueshan_east", "n_g04_369_hut", "n_g04_xueshan",
            "n_g04_beling", "n_g04_kailan", "n_g04_kailan_north",
            "n_g04_xuebei_hut", "n_g04_munan_camp", "n_g04_susmida",
            "n_g04_mutele", "n_g04_xinda_hut", "n_g04_pinta",
            "n_g04_chiyou_th", "n_g04_chiyou", "n_g04_sanchayingdi",
            "n_g04_toushan_hut", "n_g04_toushan", "n_g04_helipad",
            "n_g04_toushan_2k", "n_g04_toushan_th",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g04_369_hut", "type": "hut"},
            {"atNodeId": "n_g04_xuebei_hut", "type": "hut"},
            {"atNodeId": "n_g04_xinda_hut", "type": "hut"},
        ],
        "roundTrip": False,
    },
    {
        "id": "G04-daba",
        "name": "大霸群峰 (4天3夜)",
        "startNodeId": "n_g04_guanwu",
        "endNodeId": "n_g04_dabajian",
        "viaNodeIds": [
            "n_g04_check_0_3k", "n_g04_dabajian_th", "n_g04_jiujiu_hut",
            "n_g04_jiali_th", "n_g04_jiali", "n_g04_yize_th",
            "n_g04_yize_8_8k_jct", "n_g04_yize", "n_g04_zhongba_jct",
            "n_g04_xiaoba_jct_th", "n_g04_xiaoba",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g04_jiujiu_hut", "type": "hut"},
            {"atNodeId": "n_g04_jiujiu_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G04-wuling-four",
        "name": "武陵四秀 (4天3夜)",
        "startNodeId": "n_g04_wuling_admin",
        "endNodeId": "n_g04_pinta",
        "viaNodeIds": [
            "n_g04_toushan_th", "n_g04_toushan_2k", "n_g04_helipad",
            "n_g04_toushan", "n_g04_toushan_hut", "n_g04_kalaye",
            "n_g04_sanchayingdi", "n_g04_chiyou", "n_g04_xinda_hut",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g04_toushan_hut", "type": "hut"},
            {"atNodeId": "n_g04_xinda_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
]


def build():
    route = {
        "id": "G04",
        "name": "大霸‧聖稜‧武陵四秀",
        "version": "2026-05-14",
        "source": "上河文化 G04 大霸·聖稜·武陵四秀步程示意圖 (G04_hiking.jpg)",
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
    path = ROUTES_DIR / "G04.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G04 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
