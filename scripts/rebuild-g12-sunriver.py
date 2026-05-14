#!/usr/bin/env python3
"""Rebuild G12 能高安東軍縱走 from 上河文化 G12_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 北端進場 (能高越嶺道) — 與 G11 共用 ===
    ("n_g12_wushe",          "霧社",            23.97000, 121.16000, 1150, "trailhead"),  #EST
    ("n_g12_lushan_tribe",   "廬山部落",        23.99000, 121.20000, 1100, "trailhead"),  #EST
    ("n_g12_tunyuan_th",     "屯原登山口",      24.05200, 121.21500, 2050, "trailhead"),  #EST
    ("n_g12_yunhai",         "雲海保線所",      24.04200, 121.25500, 2360, "hut"),        #EST
    ("n_g12_tianchi_hut",    "天池山莊",        24.04500, 121.27931, 2860, "hut"),        #OSM
    ("n_g12_xianjie",        "縣界埡口",        24.04800, 121.28800, 2800, "junction"),   #EST
    ("n_g12_kahuanguan",     "卡賀爾山",        24.05000, 121.30000, 3010, "peak"),       #EST
    ("n_g12_nenggao_main",   "能高主峰",        23.99232, 121.26024, 3262, "peak"),       #OSM
    ("n_g12_nenggao_south",  "能高山南峰",      23.96537, 121.27811, 3348, "peak"),       #OSM

    # === 安東軍 chain ===
    ("n_g12_old_hut",        "能高小屋舊址",    23.95000, 121.27500, 3000, "shelter"),    #EST
    ("n_g12_taiwan_pool",    "台灣池營地",      23.94500, 121.27300, 2900, "waypoint"),   #EST
    ("n_g12_dalu_pool",      "大陸池營地",      23.94000, 121.27200, 2880, "waypoint"),   #EST
    ("n_g12_rope_cliff",     "垂直岩壁拉繩",    23.93500, 121.27000, 2950, "waypoint"),   #EST
    ("n_g12_nenggao_southnorth","能高南峰北嶺", 23.93000, 121.27000, 3100, "peak"),       #EST
    ("n_g12_southpeak_jct",  "南峰岔路口",      23.93800, 121.27500, 3200, "junction"),   #EST
    ("n_g12_southpeak_camp", "南峰南鞍營地",    23.92800, 121.27300, 3050, "waypoint"),   #EST
    ("n_g12_3039",           "3039鞍營地",      23.92300, 121.27600, 3039, "waypoint"),   #EST
    ("n_g12_guangtou",       "光頭山",          23.93908, 121.27310, 3077, "peak"),       #OSM
    ("n_g12_baishichi",      "白石池",          23.92500, 121.27800, 2900, "water"),     #EST
    ("n_g12_baishi",         "白石山",          23.91500, 121.27500, 3110, "peak"),       #EST
    ("n_g12_wanlichi",       "萬里池",          23.90500, 121.27500, 2780, "water"),     #EST
    ("n_g12_tunluchi",       "屯鹿池",          23.89500, 121.27500, 2700, "water"),     #EST
    ("n_g12_3jct",           "三岔路口",        23.88500, 121.27500, 2950, "junction"),   #EST
    ("n_g12_andong",         "安東軍山",        23.88105, 121.28072, 3068, "peak"),       #OSM

    # === 南端下山 chain (奧萬大 / 萬大南溪 → 霧社) ===
    ("n_g12_visitor_park",   "遊客中心停車場",  23.96500, 121.18500, 1100, "trailhead"),  #EST
    ("n_g12_aowanda_bridge", "奧萬大吊橋",      23.95500, 121.21000, 1000, "waypoint"),   #EST
    ("n_g12_3rd_ridge_pinguai","第三越嶺點/松風嶺", 23.92000, 121.22000, 1800, "waypoint"),  #EST
    ("n_g12_2nd_ridge",      "第二越嶺點",      23.91500, 121.22500, 2000, "waypoint"),   #EST
    ("n_g12_1st_ridge",      "第一越嶺點",      23.91000, 121.23000, 2100, "waypoint"),   #EST
    ("n_g12_4_tributary",    "第四支流合匯點",  23.90500, 121.23500, 1800, "waypoint"),   #EST
    ("n_g12_3_tributary",    "第三支流合匯點",  23.90000, 121.24000, 1700, "waypoint"),   #EST
    ("n_g12_jianan_camp",    "建安下三支流會合點", 23.89500, 121.24500, 1650, "waypoint"),  #EST
    ("n_g12_2_tributary",    "第二支流合匯點",  23.89000, 121.25000, 1600, "waypoint"),   #EST
    ("n_g12_wanda_river",    "萬大南溪合匯點",  23.88500, 121.25500, 1500, "waypoint"),   #EST
    ("n_g12_jinxin_jct",     "金杏真路岔路口",  23.88000, 121.26000, 1700, "junction"),   #EST
    ("n_g12_xichuan_camp",   "溪床營地",        23.87500, 121.26200, 1800, "waypoint"),   #EST
    ("n_g12_dabengbi",       "大崩壁",          23.87800, 121.27000, 2200, "waypoint"),   #EST
    ("n_g12_2nd_liaoshe",    "第二獵寮",        23.88200, 121.27500, 2500, "shelter"),    #EST
    ("n_g12_hongxiao",       "紅檜巨木",        23.88500, 121.27700, 2700, "waypoint"),   #EST
    ("n_g12_1st_creek_cross","第一次過溪",      23.88800, 121.27800, 2750, "waypoint"),   #EST
    ("n_g12_1st_liaoshe_camp","第一獵寮營地",   23.88300, 121.27600, 2600, "waypoint"),   #EST
    ("n_g12_to_buling",      "往埔里",          23.97500, 121.14000, 600, "junction"),   #EST
]


EDGES = [
    # 公路駁接
    ("n_g12_wushe", "n_g12_to_buling", 30, 30),
    ("n_g12_wushe", "n_g12_lushan_tribe", 30, 30),
    ("n_g12_lushan_tribe", "n_g12_tunyuan_th", 50, 50),
    ("n_g12_wushe", "n_g12_visitor_park", 40, 40),
    # === 西段 (與 G11 共用) ===
    ("n_g12_tunyuan_th", "n_g12_yunhai", 208, 66),
    ("n_g12_yunhai", "n_g12_tianchi_hut", 257, 90),
    # === 天池→能高 chain ===
    ("n_g12_tianchi_hut", "n_g12_xianjie", 50, 55),
    ("n_g12_xianjie", "n_g12_kahuanguan", 170, 140),
    ("n_g12_kahuanguan", "n_g12_nenggao_main", 160, 140),
    ("n_g12_nenggao_main", "n_g12_nenggao_south", 30, 20),
    # === 安東軍 chain ===
    ("n_g12_nenggao_south", "n_g12_old_hut", 20, 15),
    ("n_g12_old_hut", "n_g12_taiwan_pool", 30, 20),
    ("n_g12_taiwan_pool", "n_g12_dalu_pool", 35, 30),
    ("n_g12_dalu_pool", "n_g12_rope_cliff", 100, 80),
    ("n_g12_rope_cliff", "n_g12_nenggao_southnorth", 60, 70),
    ("n_g12_nenggao_southnorth", "n_g12_southpeak_jct", 85, 60),
    ("n_g12_southpeak_jct", "n_g12_southpeak_camp", 60, 80),
    ("n_g12_southpeak_camp", "n_g12_3039", 90, 80),
    ("n_g12_3039", "n_g12_guangtou", 70, 70),
    ("n_g12_guangtou", "n_g12_baishichi", 20, 40),
    ("n_g12_baishichi", "n_g12_baishi", 100, 130),
    ("n_g12_baishichi", "n_g12_wanlichi", 60, 90),
    ("n_g12_wanlichi", "n_g12_tunluchi", 110, 120),
    ("n_g12_tunluchi", "n_g12_3jct", 45, 45),
    ("n_g12_3jct", "n_g12_andong", 35, 80),

    # === 萬大南溪下山 chain (long descent) ===
    ("n_g12_visitor_park", "n_g12_aowanda_bridge", 80, 70),
    ("n_g12_aowanda_bridge", "n_g12_3rd_ridge_pinguai", 55, 35),
    ("n_g12_3rd_ridge_pinguai", "n_g12_2nd_ridge", 40, 55),
    ("n_g12_2nd_ridge", "n_g12_1st_ridge", 60, 55),
    ("n_g12_1st_ridge", "n_g12_4_tributary", 40, 35),
    ("n_g12_4_tributary", "n_g12_3_tributary", 70, 45),
    ("n_g12_3_tributary", "n_g12_jianan_camp", 55, 40),
    ("n_g12_jianan_camp", "n_g12_2_tributary", 35, 40),
    ("n_g12_2_tributary", "n_g12_wanda_river", 35, 55),
    ("n_g12_wanda_river", "n_g12_jinxin_jct", 100, 120),
    ("n_g12_jinxin_jct", "n_g12_xichuan_camp", 25, 35),
    ("n_g12_xichuan_camp", "n_g12_dabengbi", 110, 60),
    ("n_g12_dabengbi", "n_g12_2nd_liaoshe", 60, 50),
    ("n_g12_2nd_liaoshe", "n_g12_hongxiao", 70, 110),
    ("n_g12_hongxiao", "n_g12_1st_creek_cross", 50, 70),
    ("n_g12_1st_creek_cross", "n_g12_1st_liaoshe_camp", 80, 150),
    ("n_g12_1st_liaoshe_camp", "n_g12_3jct", 80, 80),
]


PRESETS = [
    {
        "id": "G12-andong-traverse",
        "name": "能高安東軍縱走 (5天4夜)",
        "startNodeId": "n_g12_tunyuan_th",
        "endNodeId": "n_g12_andong",
        "viaNodeIds": [
            "n_g12_yunhai", "n_g12_tianchi_hut", "n_g12_kahuanguan",
            "n_g12_nenggao_main", "n_g12_nenggao_south",
            "n_g12_taiwan_pool", "n_g12_guangtou", "n_g12_baishichi",
            "n_g12_wanlichi", "n_g12_tunluchi",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g12_tianchi_hut", "type": "hut"},
            {"atNodeId": "n_g12_taiwan_pool", "type": "camp"},
            {"atNodeId": "n_g12_baishichi", "type": "water"},
            {"atNodeId": "n_g12_tunluchi", "type": "water"},
        ],
        "roundTrip": False,
    },
]


def build():
    route = {
        "id": "G12", "name": "能高安東軍縱走",
        "version": "2026-05-14",
        "source": "上河文化 G12 能高安東軍步程示意圖 (G12_hiking.jpg)",
        "nodes": [{"id": nid, "name": name, "lat": lat, "lng": lng, "elevation": elev, "category": cat}
                  for (nid, name, lat, lng, elev, cat) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fwd, "minutes_backward": bwd,
                   "source": "上河圖", "confirmed": True} for (f, t, fwd, bwd) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G12.json"
    with open(path, "w") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G12 rebuilt: {len(NODES)} nodes, {len(EDGES)} edges, {len(PRESETS)} presets")


if __name__ == "__main__":
    build()
