#!/usr/bin/env python3
"""Rebuild G10 太魯閣山列 from 上河文化 G10_hiking.jpg."""
import json
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "public" / "data" / "routes"

NODES = [
    # === 進場 (中橫西側 / 大禹嶺 / 中橫霧社支線) ===
    ("n_g10_dayuling",        "大禹嶺",          24.18550, 121.30460, 2565, "trailhead"),  #EST
    ("n_g10_zhongheng_jct",   "中橫霧社支線",    24.18000, 121.30000, 2500, "junction"),   #EST
    ("n_g10_heshui_ridge",    "黑水塘山屋",      24.14762, 121.34230, 2400, "hut"),        #EST
    ("n_g10_chenggong_hut",   "成功山屋",        24.12200, 121.32400, 3000, "hut"),        #EST

    # === 太魯閣山列 主稜 ===
    ("n_g10_zhuling_3jct",    "主稜三岔路口",    24.15000, 121.34500, 3300, "junction"),   #EST
    ("n_g10_qilai_lodge",     "奇萊山莊",        24.10871, 121.32692, 3200, "hut"),        #OSM
    ("n_g10_yuexing_camp",    "月形池營地",      24.11754, 121.34544, 2900, "waypoint"),   #OSM
    ("n_g10_qixinlong_pond",  "驚嘆號池營地",    24.10950, 121.35710, 3000, "waypoint"),   #EST
    ("n_g10_pingshi_west",    "磐石山西峰",      24.10993, 121.35783, 3337, "peak"),       #OSM
    ("n_g10_pingshi_mid",     "磐石山中峰",      24.10482, 121.37075, 3149, "peak"),       #OSM
    ("n_g10_pingshi",         "磐石山",          24.10471, 121.38827, 3105, "peak"),       #OSM
    ("n_g10_pingshi_camp",    "磐石中峰營地",    24.10500, 121.37500, 3100, "waypoint"),   #EST
    ("n_g10_lihuo_main",      "立霧主山",        24.12480, 121.44563, 3071, "peak"),       #OSM
    ("n_g10_lihuo_camp",      "立霧主山營地",    24.12300, 121.44300, 3000, "waypoint"),   #EST
    ("n_g10_2687",            "2687峰三岔口",    24.11500, 121.43500, 2687, "junction"),   #EST
    ("n_g10_paturu",          "帕托魯山",        24.09946, 121.46653, 3102, "peak"),       #OSM
    ("n_g10_pingan_camp",     "平安池",          24.09000, 121.46500, 3000, "water"),      #EST
    ("n_g10_3en_camp",        "三宕營地",        24.08500, 121.46200, 2950, "waypoint"),   #EST
    ("n_g10_taluge_main",     "太魯閣大山",      24.07907, 121.42100, 3282, "peak"),       #OSM
    ("n_g10_yueya_pool",      "月牙池營地",      24.08500, 121.41800, 3100, "waypoint"),   #EST
    ("n_g10_yueya_pool_2",    "月牙池",          24.08000, 121.41500, 3050, "water"),      #EST
    ("n_g10_pangsha_temp",    "磐中營地",        24.08500, 121.40000, 3000, "waypoint"),   #EST
    ("n_g10_pangmu",          "磐木中峰營地",    24.08800, 121.39500, 2900, "waypoint"),   #EST
    ("n_g10_paturu_main_jct", "三岔三叉路口",    24.10000, 121.40000, 2900, "junction"),   #EST
    ("n_g10_taige_3jct",      "太閣大山三岔路口", 24.07500, 121.42000, 3150, "junction"),  #EST

    # === 出口 (太魯閣方向) ===
    ("n_g10_wang_taige",      "往太魯閣",        24.10000, 121.50000, 1000, "junction"),   #EST (arrow)
    ("n_g10_tianxiang",       "天祥",            24.18000, 121.50000, 500, "trailhead"),   #EST
    ("n_g10_taluge_park",     "太魯閣國家公園",  24.15800, 121.60000, 100, "trailhead"),   #EST
    ("n_g10_wangwang_pavilion","岳王亭",         24.16500, 121.52000, 800, "trailhead"),   #EST
    ("n_g10_qilai_main_lodge","奇萊主山往",      24.08646, 121.32326, 3562, "junction"),   #EST (arrow)
    ("n_g10_to_qilai",        "往奇萊主山",      24.08000, 121.32000, 3500, "junction"),   #EST
    ("n_g10_qingjing",        "往清境霧社",      23.99000, 121.20000, 1100, "junction"),   #EST
]


EDGES = [
    # === 進場 ===
    ("n_g10_dayuling", "n_g10_zhongheng_jct", 5, 5),
    ("n_g10_zhongheng_jct", "n_g10_qingjing", 60, 60),  # vehicle
    ("n_g10_dayuling", "n_g10_heshui_ridge", 30, 25),
    ("n_g10_heshui_ridge", "n_g10_chenggong_hut", 120, 80),

    # === 成功 → 主稜 → 月形池 → 磐石 ===
    ("n_g10_chenggong_hut", "n_g10_zhuling_3jct", 100, 70),
    ("n_g10_zhuling_3jct", "n_g10_qilai_lodge", 70, 90),
    ("n_g10_qilai_lodge", "n_g10_to_qilai", 30, 30),
    ("n_g10_qilai_lodge", "n_g10_yuexing_camp", 130, 100),
    ("n_g10_yuexing_camp", "n_g10_qixinlong_pond", 90, 70),
    ("n_g10_qixinlong_pond", "n_g10_pingshi_west", 60, 50),
    ("n_g10_pingshi_west", "n_g10_pingshi_camp", 60, 50),
    ("n_g10_pingshi_camp", "n_g10_pingshi_mid", 60, 50),
    ("n_g10_pingshi_mid", "n_g10_pingshi", 80, 70),

    # === 立霧主山 ===
    ("n_g10_pingshi", "n_g10_lihuo_camp", 110, 70),
    ("n_g10_lihuo_camp", "n_g10_lihuo_main", 40, 25),
    ("n_g10_lihuo_main", "n_g10_2687", 70, 110),

    # === 帕托魯山 ===
    ("n_g10_2687", "n_g10_paturu", 100, 110),
    ("n_g10_paturu", "n_g10_pingan_camp", 50, 70),
    ("n_g10_pingan_camp", "n_g10_3en_camp", 60, 50),

    # === 太魯閣大山 ===
    ("n_g10_paturu", "n_g10_paturu_main_jct", 100, 110),
    ("n_g10_paturu_main_jct", "n_g10_pangmu", 70, 50),
    ("n_g10_pangmu", "n_g10_pangsha_temp", 60, 70),
    ("n_g10_pangsha_temp", "n_g10_yueya_pool_2", 80, 60),
    ("n_g10_yueya_pool_2", "n_g10_yueya_pool", 30, 20),
    ("n_g10_yueya_pool", "n_g10_taige_3jct", 60, 50),
    ("n_g10_taige_3jct", "n_g10_taluge_main", 40, 30),
    ("n_g10_3en_camp", "n_g10_taluge_main", 130, 110),

    # === 出口 ===
    ("n_g10_3en_camp", "n_g10_wang_taige", 360, 480),
    ("n_g10_wang_taige", "n_g10_tianxiang", 60, 60),  # vehicle
    ("n_g10_tianxiang", "n_g10_taluge_park", 30, 30),
    ("n_g10_tianxiang", "n_g10_wangwang_pavilion", 20, 20),
]


PRESETS = [
    {
        "id": "G10-traverse",
        "name": "太魯閣山列縱走 (8天7夜)",
        "startNodeId": "n_g10_dayuling",
        "endNodeId": "n_g10_taluge_park",
        "viaNodeIds": [
            "n_g10_heshui_ridge", "n_g10_chenggong_hut", "n_g10_qilai_lodge",
            "n_g10_pingshi", "n_g10_lihuo_main", "n_g10_paturu",
            "n_g10_taluge_main", "n_g10_tianxiang",
        ],
        "suggestedDayBreaks": [
            {"atNodeId": "n_g10_chenggong_hut", "type": "hut"},
            {"atNodeId": "n_g10_qilai_lodge", "type": "hut"},
            {"atNodeId": "n_g10_pingshi_camp", "type": "camp"},
            {"atNodeId": "n_g10_lihuo_camp", "type": "camp"},
            {"atNodeId": "n_g10_pingan_camp", "type": "water"},
            {"atNodeId": "n_g10_yueya_pool_2", "type": "water"},
        ],
        "roundTrip": False,
    },
]


def build():
    r = {
        "id": "G10", "name": "太魯閣山列",
        "version": "2026-05-14",
        "source": "上河文化 G10 太魯閣山列步程示意圖 (G10_hiking.jpg)",
        "nodes": [{"id": nid, "name": n, "lat": lat, "lng": lng, "elevation": e, "category": c}
                  for (nid, n, lat, lng, e, c) in NODES],
        "edges": [{"from": f, "to": t, "minutes_forward": fw, "minutes_backward": bw,
                   "source": "上河圖", "confirmed": True} for (f, t, fw, bw) in EDGES],
        "presets": PRESETS,
    }
    path = ROUTES_DIR / "G10.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")
    print(f"G10: {len(NODES)} nodes, {len(EDGES)} edges")


if __name__ == "__main__":
    build()
