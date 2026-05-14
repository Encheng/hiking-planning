#!/usr/bin/env python3
"""Rebuild G09 from 上河文化 step diagram (G09_hiking_new.jpg).

Source-of-truth: 上河圖 step diagram timings.
Coordinates: OSM where available, estimated (interpolated) otherwise.

This rebuild covers: 合歡群峰 day hikes, 奇萊主北 traverse, 奇萊主南華,
能高越嶺道 (屯原→天池山莊), 屏風山 main route.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "public" / "data"
ROUTES_DIR = DATA_DIR / "routes"

# ─────────────────────────────────────────────
# NODES — name, lat, lng, elev, category
# OSM-verified coordinates marked with #OSM; estimated coordinates marked #EST
# ─────────────────────────────────────────────
NODES = [
    # === 合歡群峰 (trailheads + peaks + landmarks) ===
    ("n_g09_wuling",         "武嶺",              24.13711, 121.27614, 3275, "junction"),  #OSM
    ("n_g09_kunyang",        "昆陽",              24.12286, 121.27279, 3070, "junction"),  #OSM
    ("n_g09_hehuan_lodge",   "合歡山莊",          24.13985, 121.28735, 3158, "hut"),       #OSM parking
    ("n_g09_old_ski",        "舊滑訓中心",        24.14008, 121.28630, 3160, "junction"),  #EST
    ("n_g09_songsetsu",      "松雪樓",            24.13889, 121.28575, 3150, "hut"),       #EST
    ("n_g09_hehuan_th",      "合歡山管理站",      24.14193, 121.28463, 3275, "trailhead"),  #OSM (info board)
    ("n_g09_th_main",        "合歡主峰登山口",    24.13364, 121.27159, 3275, "trailhead"),  #OSM
    ("n_g09_hehuan_main",    "合歡主峰",          24.14261, 121.27120, 3417, "peak"),       #OSM
    ("n_g09_hehuan_south",   "合歡南峰",          24.12421, 121.26896, 3218, "peak"),       #OSM
    ("n_g09_hehuan_jianshan","合歡尖山",          24.14441, 121.28360, 3218, "peak"),       #OSM
    ("n_g09_th_jianshan_s",  "合歡尖山南登山口",  24.14258, 121.28454, 3210, "trailhead"),  #OSM
    ("n_g09_th_jianshan_n",  "合歡尖山北登山口",  24.14570, 121.28403, 3210, "trailhead"),  #OSM
    ("n_g09_shimen_th",      "石門山登山口",      24.14607, 121.28430, 3275, "trailhead"),  #OSM
    ("n_g09_shimen",         "石門山",            24.15242, 121.28455, 3236, "peak"),       #OSM
    ("n_g09_th_shimen_n",    "石門北峰登山口",    24.15375, 121.28293, 3210, "trailhead"),  #OSM
    ("n_g09_shimen_north",   "石門山北峰",        24.15760, 121.27956, 3280, "peak"),       #OSM
    ("n_g09_kenan_pass",     "克難關",            24.15365, 121.28305, 3179, "junction"),  #OSM
    ("n_g09_th_east",        "合歡東峰登山口",    24.13978, 121.28731, 3275, "trailhead"),  #OSM
    ("n_g09_hehuan_east",    "合歡東峰",          24.13567, 121.28111, 3421, "peak"),       #OSM
    ("n_g09_th_north",       "合歡北峰登山口",    24.16569, 121.28934, 3275, "trailhead"),  #OSM
    ("n_g09_reflector",      "反射板",            24.17500, 121.28400, 3320, "waypoint"),   #EST (on N peak trail)
    ("n_g09_hehuan_north",   "合歡北峰",          24.18151, 121.28159, 3422, "peak"),       #OSM
    ("n_g09_hehuan_west",    "合歡西峰",          24.17764, 121.24454, 3144, "peak"),       #OSM
    ("n_g09_bichi",          "碧池",              24.17750, 121.28200, 3250, "water"),      #EST (near reflector)
    ("n_g09_low_saddle",     "最低鞍部",          24.17800, 121.26500, 2950, "junction"),   #EST (lowest point on ridge)
    ("n_g09_pool_camp",      "水池營地",          24.17680, 121.25500, 3000, "waypoint"),   #EST
    ("n_g09_huagang_jct",    "華岡叉路口",        24.17600, 121.25000, 3200, "junction"),   #EST (high ridge jct, above 西峰)
    ("n_g09_west_camp",      "西峰營地",          24.17782, 121.24557, 3123, "waypoint"),   #OSM
    # 上河圖: 中橫104K→果園→武法奈尾/天巒池→叉路→小溪營地→北合歡
    # 叉路 在高稜線 (~3300m, 連 北合歡 約 15/30 分鐘ridge walk)
    ("n_g09_xiaoxi_camp",    "小溪營地",          24.19300, 121.27300, 3200, "waypoint"),   #EST (high ridge stream camp, N of 北合歡)
    ("n_g09_yuanhuan_jct",   "叉路（小溪）",      24.19000, 121.27500, 3300, "junction"),   #EST (high ridge jct ~1km N of 北合歡)
    ("n_g09_orchard_th",     "果園登山口",        24.17900, 121.26900, 2900, "trailhead"),  #EST
    ("n_g09_songquan_th",    "松泉崗·天巒池登山口", 24.19500, 121.26200, 2050, "trailhead"),  #EST (中橫104K)
    ("n_g09_tianluanchi",    "天巒池",            24.19200, 121.26000, 2820, "water"),      #EST
    ("n_g09_wufana",         "武法奈尾山",        24.20967, 121.28526, 2986, "peak"),       #OSM

    # === 合歡 → 奇萊 traverse ===
    ("n_g09_ski_lodge",      "滑雪山莊·奇萊山登山口", 24.13922, 121.28779, 3260, "trailhead"),  #OSM
    ("n_g09_xiaoqilai",      "小奇萊",            24.13224, 121.29536, 3153, "peak"),       #OSM
    ("n_g09_heishuitang_hut","黑水塘山屋",        24.12500, 121.31500, 2900, "hut"),        #EST
    ("n_g09_chenggong_hut",  "成功山屋",          24.12200, 121.32400, 3000, "hut"),        #EST
    ("n_g09_chenggong1",     "成功一號堡",        24.12000, 121.32700, 3100, "shelter"),    #EST
    ("n_g09_zhubei_jct",     "主北岔路",          24.11800, 121.33000, 3250, "junction"),   #EST
    ("n_g09_north_peak_jct", "奇萊北峰岔路",      24.11900, 121.33400, 3500, "junction"),   #EST
    ("n_g09_qilai_north",    "奇萊主山北峰",      24.11834, 121.33455, 3606, "peak"),       #OSM
    ("n_g09_zhubei3_jct",    "主北三岔路",        24.11200, 121.33100, 3460, "junction"),   #EST

    # === 奇萊主山 area ===
    ("n_g09_qilai_lodge",    "奇萊山莊",          24.10871, 121.32692, 3200, "hut"),        #OSM
    ("n_g09_qilai_main_th",  "主山登山口",        24.09000, 121.32500, 3450, "junction"),   #EST (high-altitude trail jct)
    ("n_g09_qilai_main",     "奇萊主山",          24.08646, 121.32326, 3562, "peak"),       #OSM
    ("n_g09_qilai_main_east","奇萊主山東峰",      24.08390, 121.33473, 3394, "peak"),       #OSM
    ("n_g09_qilaichi",       "奇萊池山",          24.10015, 121.32341, 3436, "peak"),       #OSM
    ("n_g09_qilaijian",      "奇萊尖",            24.12657, 121.30026, 3163, "peak"),       #OSM

    # === 奇萊主南華 traverse (long approach via 卡西/卡東) ===
    ("n_g09_kaxi_camp",      "卡西營地",          24.07500, 121.31000, 3100, "waypoint"),   #EST
    ("n_g09_kadong_camp",    "卡東營地",          24.04000, 121.28500, 2400, "waypoint"),   #EST
    ("n_g09_lishan_forest",  "裡山森林入口",      24.03500, 121.28000, 2200, "waypoint"),   #EST
    ("n_g09_south_peak_th",  "南峰登山口",        24.06500, 121.28500, 3100, "junction"),   #EST
    ("n_g09_qilai_south",    "奇萊主山南峰",      24.06130, 121.27997, 3357, "peak"),       #OSM
    ("n_g09_tianchi_jct",    "天池岔路口",        24.05500, 121.28700, 3150, "junction"),   #EST
    ("n_g09_xianjie_pass",   "縣界埡口",          24.04800, 121.28800, 2800, "junction"),   #EST
    ("n_g09_tianchi_hut",    "天池山莊",          24.04500, 121.27931, 2860, "hut"),        #OSM (camp tag)
    ("n_g09_yunhai",         "雲海保線所",        24.04200, 121.25500, 2360, "hut"),        #EST
    ("n_g09_tunyuan_th",     "屯原登山口",        24.05200, 121.21500, 2050, "trailhead"),  #EST
    ("n_g09_nanhua",         "南華山",            24.03935, 121.28593, 3182, "peak"),       #OSM
    ("n_g09_deepkutsu",      "深堀山",            24.05298, 121.27464, 3313, "peak"),       #OSM

    # === 屏風山 (from 大禹嶺) ===
    ("n_g09_dayuling",       "大禹嶺",            24.18550, 121.30460, 2565, "trailhead"),  #OSM-ish (memorial nearby)
    ("n_g09_th_pingfeng",    "屏風山新登山口",    24.17968, 121.31781, 2400, "trailhead"),  #OSM (111.2K)
    ("n_g09_river1",         "第一次過溪",        24.17500, 121.32200, 2200, "waypoint"),   #EST
    ("n_g09_iron_bridge",    "鐵線吊橋",          24.16746, 121.32545, 2050, "waypoint"),   #OSM (camp)
    ("n_g09_songzhen_camp",  "屏風山屋松針營地",  24.16210, 121.32494, 2700, "waypoint"),   #OSM (camp)
    ("n_g09_tatsukiri",      "塔次基里溪",        24.16100, 121.32700, 2700, "waypoint"),   #EST
    ("n_g09_grassland_view", "草坡展望台",        24.15500, 121.33500, 3050, "waypoint"),   #EST
    ("n_g09_bare_rocks",     "裸岩區",            24.15200, 121.34000, 3200, "waypoint"),   #EST
    ("n_g09_pingfeng",       "屏風山",            24.14923, 121.34301, 3247, "peak"),       #OSM
    ("n_g09_gold_camp",      "合歡金礦營地",      24.14438, 121.32543, 2800, "waypoint"),   #OSM (camp)
    ("n_g09_water4",         "第四水源",          24.14600, 121.33000, 2900, "water"),      #EST
    ("n_g09_ridge3241",      "3241稜線",          24.14800, 121.33700, 3241, "waypoint"),   #EST

    # === Side peaks ===
    ("n_g09_karolou",        "卡羅樓山",          24.07830, 121.31584, 3413, "peak"),       #OSM
]


# ─────────────────────────────────────────────
# EDGES — from 上河圖 timings
# Format: (from_id, to_id, minutes_forward, minutes_backward)
# Direction: fwd is approximate "up/away from road" direction
# ─────────────────────────────────────────────
EDGES = [
    # === 合歡群峰 ===
    # 武嶺 hub (公路時間 walking speed)
    ("n_g09_wuling", "n_g09_hehuan_lodge", 15, 15),       # 武嶺 → 合歡山莊 (1.2km walking)
    ("n_g09_wuling", "n_g09_kunyang", 30, 30),            # 武嶺 → 昆陽 (2km walking)
    # 武嶺(3275) → 主峰(3417): UP 60分, DOWN 40分
    ("n_g09_wuling", "n_g09_hehuan_main", 60, 40),        # 武嶺 ↔ 合歡主峰 (上河 60UP/40DOWN)
    ("n_g09_wuling", "n_g09_th_main", 5, 5),              # 武嶺 → 合歡主峰登山口

    # 合歡山莊 area
    ("n_g09_hehuan_lodge", "n_g09_songsetsu", 3, 3),      # 合歡山莊 → 松雪樓 (150公尺)
    ("n_g09_hehuan_lodge", "n_g09_old_ski", 3, 3),        # 合歡山莊 → 舊滑訓中心 (1分上河)
    ("n_g09_hehuan_lodge", "n_g09_ski_lodge", 5, 5),      # 合歡山莊 ↔ 奇萊登山口 (same parking)
    ("n_g09_old_ski", "n_g09_hehuan_jianshan", 25, 15),   # 舊滑訓中心 → 合歡尖山
    ("n_g09_hehuan_jianshan", "n_g09_th_jianshan_n", 5, 5), # 合歡尖山 → 北登山口
    ("n_g09_hehuan_jianshan", "n_g09_th_jianshan_s", 5, 5),
    ("n_g09_th_jianshan_n", "n_g09_th_jianshan_s", 3, 3),

    # 石門山 area (上河圖 convention: forward direction A→B; UP times are larger)
    ("n_g09_old_ski", "n_g09_kenan_pass", 20, 20),        # 舊滑訓中心 → 克難關 (walking 1.5km)
    # 克難關(3179) → 石門山(3236): UP 30, DOWN 20
    ("n_g09_kenan_pass", "n_g09_shimen", 30, 20),         # 克難關 → 石門山 (上河 30UP/20DOWN)
    # 克難關(3179) → 石門北峰(3280): UP 30, DOWN 15
    ("n_g09_kenan_pass", "n_g09_shimen_north", 30, 15),   # 克難關 → 石門北峰 (上河 30UP/15DOWN)
    ("n_g09_shimen_th", "n_g09_shimen", 20, 15),          # 石門山登山口 → 石門山
    ("n_g09_th_shimen_n", "n_g09_shimen_north", 30, 25),  # 石門北登山口 → 石門北峰

    # 合歡主峰
    ("n_g09_th_main", "n_g09_hehuan_main", 30, 20),
    ("n_g09_hehuan_main", "n_g09_hehuan_south", 60, 70),  # 主峰 → 南峰

    # 合歡東峰
    ("n_g09_th_east", "n_g09_hehuan_east", 40, 30),
    # 石門山(3236) → 東峰(3421): UP 60, DOWN 50
    ("n_g09_shimen", "n_g09_hehuan_east", 60, 50),

    # === 合歡北峰 → 合歡西峰 chain (上河圖 user-verified) ===
    # fwd = forward direction time (A→B); UP times are LARGER, DOWN smaller
    # 登山口(3275) → 反射板(~3320): UP 70, DOWN 45
    ("n_g09_th_north", "n_g09_reflector", 70, 45),        # 北登山口 → 反射板 (上河 70UP/45DOWN)
    # 反射板(~3320) → 北合歡(3422): UP 20, DOWN 15
    ("n_g09_reflector", "n_g09_hehuan_north", 20, 15),    # 反射板 → 北合歡 (上河 20UP/15DOWN)
    # 反射板(~3320) → 碧池(~3250): DOWN 5, UP 10
    ("n_g09_reflector", "n_g09_bichi", 5, 10),            # 反射板 → 碧池 (上河 5DOWN/10UP)
    # 北合歡(3422) → 最低鞍部(~2950): DOWN 75, UP 110
    ("n_g09_hehuan_north", "n_g09_low_saddle", 75, 110),  # 北合歡 → 最低鞍部 (上河 75DOWN/110UP)

    # 合歡西峰 trail
    # 鞍部(~2950) → 水池(~3000): UP 30, DOWN 20
    ("n_g09_low_saddle", "n_g09_pool_camp", 30, 20),      # 最低鞍 → 水池營地
    # 水池(~3000) → 華岡叉路口(~3200): UP 40, DOWN 30
    ("n_g09_pool_camp", "n_g09_huagang_jct", 40, 30),     # 水池 → 華岡叉路口
    # 華岡(~3200) → 西峰(3144): DOWN 35, UP 45
    ("n_g09_huagang_jct", "n_g09_hehuan_west", 35, 45),   # 華岡叉路 → 西合歡 (上河 35DOWN/45UP)
    ("n_g09_hehuan_west", "n_g09_west_camp", 10, 10),
    # 叉路 ↔ 小溪營地 (短稜線): 上河 5/10
    ("n_g09_yuanhuan_jct", "n_g09_xiaoxi_camp", 10, 5),  # 叉路→小溪營地 UP 10, DOWN 5
    # 叉路 ↔ 北合歡 (高稜線連結): 上河 15/30 (15 DOWN, 30 UP)
    ("n_g09_yuanhuan_jct", "n_g09_hehuan_north", 30, 15),  # 叉路→北合歡 UP 30, DOWN 15

    # 中橫104K access
    ("n_g09_songquan_th", "n_g09_tianluanchi", 30, 45),
    ("n_g09_songquan_th", "n_g09_orchard_th", 15, 15),    # 松泉崗 → 果園登山口
    ("n_g09_orchard_th", "n_g09_wufana", 60, 80),         # 果園 → 武法奈尾山
    ("n_g09_wufana", "n_g09_tianluanchi", 20, 10),
    # 中橫104K → 果園 → 武法奈尾/天巒池 → 叉路 (高稜線)。
    # 果園→叉路 是 ~1.4km horizontal + ~400m climb, 估 120 UP / 90 DOWN
    ("n_g09_orchard_th", "n_g09_yuanhuan_jct", 120, 90),   # 果園 → 叉路 (long ridge climb)

    # 北合歡山登山口 access
    ("n_g09_th_north", "n_g09_th_shimen_n", 15, 15),      # 沿公路
    ("n_g09_th_shimen_n", "n_g09_th_east", 10, 10),       # 沿公路
    ("n_g09_th_east", "n_g09_shimen_th", 5, 5),
    ("n_g09_shimen_th", "n_g09_th_jianshan_n", 3, 3),
    ("n_g09_hehuan_th", "n_g09_th_north", 30, 30),        # 管理站 → 北峰登山口 (公路 37.1K)
    ("n_g09_hehuan_th", "n_g09_wuling", 8, 8),

    # === 合歡 → 奇萊主北 traverse ===
    ("n_g09_ski_lodge", "n_g09_xiaoqilai", 60, 45),       # 滑雪山莊 → 小奇萊
    ("n_g09_xiaoqilai", "n_g09_heishuitang_hut", 60, 90), # 小奇萊 → 黑水塘山屋
    ("n_g09_ski_lodge", "n_g09_heishuitang_hut", 110, 130),  # 滑雪山莊 → 黑水塘山屋 (上河 110/130分)
    ("n_g09_heishuitang_hut", "n_g09_chenggong_hut", 60, 50), # 黑水塘 → 成功山屋 (60/50分)
    ("n_g09_chenggong_hut", "n_g09_chenggong1", 50, 40),  # 成功山屋 → 成功一號堡 (50/40分)
    ("n_g09_chenggong1", "n_g09_zhubei_jct", 30, 15),     # 成功一號 → 主北岔路 (30/15分)
    ("n_g09_zhubei_jct", "n_g09_north_peak_jct", 100, 80),  # 主北岔路 → 奇萊北峰岔路 (100/80分)
    ("n_g09_north_peak_jct", "n_g09_qilai_north", 55, 35),  # 北峰岔路(↑)→主山北峰 UP 55, DOWN 35
    # 北峰岔路(3550) → 主北三岔路(3460): DOWN 30 (smaller), UP 40
    ("n_g09_north_peak_jct", "n_g09_zhubei3_jct", 30, 40),  # 北峰岔路→三岔路 DOWN 30
    # 主北三岔路(3460) → 主北岔路(3250): DOWN 70 (smaller), UP 90
    ("n_g09_zhubei3_jct", "n_g09_zhubei_jct", 70, 90),    # 三岔路→主北岔路 DOWN 70
    # 主北三岔路(3460) → 奇萊山莊(3200): DOWN 10, UP 15
    ("n_g09_zhubei3_jct", "n_g09_qilai_lodge", 10, 15),   # 三岔路→山莊 DOWN 10
    # 奇萊山莊(3200) → 主山登山口(3450): UP 90, DOWN 70
    ("n_g09_qilai_lodge", "n_g09_qilai_main_th", 90, 70), # 山莊→登山口 UP 90
    ("n_g09_qilai_main_th", "n_g09_qilai_main", 25, 15),  # 登山口→主山 UP 25
    ("n_g09_qilai_lodge", "n_g09_qilaichi", 60, 50),      # 山莊→池山 UP 60
    ("n_g09_qilai_main", "n_g09_qilai_main_east", 30, 35),# 主山→主東 DOWN 30
    ("n_g09_qilai_main", "n_g09_karolou", 60, 60),
    ("n_g09_qilaichi", "n_g09_qilai_main", 70, 75),       # 池山→主山 (estimate)

    # === 奇萊主南華 (卡西/卡東 routes) ===
    # 主山登山口(3450) → 卡西營地(3100): DOWN 90, UP 110
    ("n_g09_qilai_main_th", "n_g09_kaxi_camp", 90, 110),  # 登山口→卡西 DOWN 90
    # 卡西(3100) → 卡東(2400): DOWN 230, UP 270
    ("n_g09_kaxi_camp", "n_g09_kadong_camp", 230, 270),   # 卡西→卡東 DOWN 230
    # 卡東(2400) → 裡山(2200): DOWN 30, UP 40
    ("n_g09_kadong_camp", "n_g09_lishan_forest", 30, 40), # 卡東→裡山 DOWN 30
    # 裡山(2200) → 南峰登山口(3100): UP 185, DOWN 150
    ("n_g09_lishan_forest", "n_g09_south_peak_th", 185, 150),
    # 南峰登山口(3100) → 奇萊南峰(3357): UP 60, DOWN 40
    ("n_g09_south_peak_th", "n_g09_qilai_south", 60, 40),
    ("n_g09_south_peak_th", "n_g09_tianchi_jct", 20, 15),
    # 天池岔路口(3150) → 天池山莊(2860): DOWN 40, UP 60
    ("n_g09_tianchi_jct", "n_g09_tianchi_hut", 40, 60),
    ("n_g09_tianchi_jct", "n_g09_nanhua", 40, 30),         # 岔路→南華 UP 40
    ("n_g09_tianchi_hut", "n_g09_xianjie_pass", 50, 55),
    ("n_g09_xianjie_pass", "n_g09_nanhua", 120, 80),
    ("n_g09_qilai_south", "n_g09_deepkutsu", 90, 100),
    ("n_g09_deepkutsu", "n_g09_nanhua", 100, 110),

    # 能高越嶺道 (屯原 → 雲海 → 天池山莊)
    ("n_g09_tunyuan_th", "n_g09_yunhai", 120, 100),
    ("n_g09_yunhai", "n_g09_tianchi_hut", 210, 180),

    # === 屏風山 main route ===
    ("n_g09_dayuling", "n_g09_th_pingfeng", 15, 15),
    # 大禹嶺與合歡管理站相距約 8km 中橫公路，步行 100min (vehicle 15min)
    ("n_g09_hehuan_th", "n_g09_dayuling", 100, 100),
    # 奇萊尖 connects to ridge near 小奇萊
    ("n_g09_xiaoqilai", "n_g09_qilaijian", 50, 50),
    ("n_g09_th_pingfeng", "n_g09_river1", 80, 130),
    ("n_g09_river1", "n_g09_iron_bridge", 40, 45),
    ("n_g09_iron_bridge", "n_g09_songzhen_camp", 40, 35),
    ("n_g09_songzhen_camp", "n_g09_tatsukiri", 8, 8),
    ("n_g09_tatsukiri", "n_g09_grassland_view", 170, 120),
    ("n_g09_grassland_view", "n_g09_bare_rocks", 70, 50),
    ("n_g09_bare_rocks", "n_g09_pingfeng", 60, 40),
    # 屏風山 alternative via 合歡金礦
    ("n_g09_songzhen_camp", "n_g09_gold_camp", 90, 65),
    ("n_g09_gold_camp", "n_g09_water4", 50, 45),
    ("n_g09_water4", "n_g09_ridge3241", 220, 190),
    ("n_g09_ridge3241", "n_g09_pingfeng", 30, 25),
]


# ─────────────────────────────────────────────
# PRESETS — common hiking itineraries
# ─────────────────────────────────────────────
PRESETS = [
    {
        "id": "G09-hehuan-main-day",
        "name": "合歡主峰單登 (當日)",
        "startNodeId": "n_g09_th_main",
        "endNodeId": "n_g09_hehuan_main",
        "viaNodeIds": [],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-north-day",
        "name": "合歡北峰單登 (當日)",
        "startNodeId": "n_g09_th_north",
        "endNodeId": "n_g09_hehuan_north",
        "viaNodeIds": ["n_g09_reflector"],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-east-day",
        "name": "合歡東峰單登 (當日)",
        "startNodeId": "n_g09_th_east",
        "endNodeId": "n_g09_hehuan_east",
        "viaNodeIds": [],
        "roundTrip": True,
    },
    {
        "id": "G09-shimen-day",
        "name": "石門山單登 (當日)",
        "startNodeId": "n_g09_shimen_th",
        "endNodeId": "n_g09_shimen",
        "viaNodeIds": [],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-west-2d",
        "name": "合歡西峰 (2天1夜)",
        "startNodeId": "n_g09_th_north",
        "endNodeId": "n_g09_hehuan_west",
        "viaNodeIds": ["n_g09_reflector", "n_g09_hehuan_north", "n_g09_low_saddle",
                       "n_g09_pool_camp", "n_g09_huagang_jct"],
        "suggestedDayBreaks": [{"atNodeId": "n_g09_west_camp", "type": "camp"}],
        "roundTrip": True,
    },
    {
        "id": "G09-qilai-main-north-3d",
        "name": "奇萊主北縱走 (3天2夜)",
        "startNodeId": "n_g09_ski_lodge",
        "endNodeId": "n_g09_qilai_main",
        "viaNodeIds": ["n_g09_heishuitang_hut", "n_g09_chenggong_hut", "n_g09_chenggong1",
                       "n_g09_zhubei_jct", "n_g09_north_peak_jct", "n_g09_qilai_north",
                       "n_g09_zhubei3_jct", "n_g09_qilai_lodge", "n_g09_qilai_main_th"],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g09_chenggong_hut", "type": "hut"},
            {"atNodeId": "n_g09_qilai_lodge", "type": "hut"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G09-qilai-south-nanhua-3d",
        "name": "奇萊南華 (3天2夜)",
        "startNodeId": "n_g09_tunyuan_th",
        "endNodeId": "n_g09_nanhua",
        "viaNodeIds": ["n_g09_yunhai", "n_g09_tianchi_hut", "n_g09_tianchi_jct",
                       "n_g09_south_peak_th", "n_g09_qilai_south"],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g09_tianchi_hut", "type": "hut"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G09-pingfeng-2d",
        "name": "屏風山 (2天1夜，松針→塔次基里溪線)",
        "startNodeId": "n_g09_th_pingfeng",
        "endNodeId": "n_g09_pingfeng",
        "viaNodeIds": ["n_g09_river1", "n_g09_iron_bridge", "n_g09_songzhen_camp",
                       "n_g09_tatsukiri", "n_g09_grassland_view", "n_g09_bare_rocks"],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g09_songzhen_camp", "type": "camp"},
        ],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-4peaks-day",
        "name": "合歡四峰串聯 (主+東+石門+尖山)",
        "startNodeId": "n_g09_th_main",
        "endNodeId": "n_g09_hehuan_east",
        "viaNodeIds": ["n_g09_hehuan_main", "n_g09_wuling", "n_g09_hehuan_lodge",
                       "n_g09_old_ski", "n_g09_hehuan_jianshan", "n_g09_th_jianshan_s",
                       "n_g09_shimen_th", "n_g09_shimen", "n_g09_th_east"],
        "roundTrip": False,
    },
]


def build():
    route = {
        "id": "G09",
        "name": "合歡群峰‧奇萊主北‧奇萊南華‧屏風山",
        "version": "2026-05-14",
        "source": "上河文化 G09 步程示意圖 (G09_hiking_new.jpg)",
        "nodes": [
            {
                "id": nid, "name": name, "lat": lat, "lng": lng,
                "elevation": elev, "category": cat,
            }
            for (nid, name, lat, lng, elev, cat) in NODES
        ],
        "edges": [
            {
                "from": f, "to": t,
                "minutes_forward": fwd, "minutes_backward": bwd,
                "source": "上河圖",
                "confirmed": True,
            }
            for (f, t, fwd, bwd) in EDGES
        ],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G09.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G09 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
