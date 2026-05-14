#!/usr/bin/env python3
"""Comprehensive G09 expansion with all OSM-verified hiking features."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "public" / "data"
ROUTES_DIR = DATA_DIR / "routes"


def load(gid):
    with open(ROUTES_DIR / f"{gid}.json") as f:
        return json.load(f)


def save(r):
    path = ROUTES_DIR / f"{r['id']}.json"
    with open(path, "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    with open(path, "a") as f:
        f.write("\n")


def remove_edge(r, a, b):
    before = len(r["edges"])
    r["edges"] = [e for e in r["edges"] if not (e["from"] == a and e["to"] == b)]
    return before - len(r["edges"])


def add_node(r, **kwargs):
    if not any(n["id"] == kwargs["id"] for n in r["nodes"]):
        r["nodes"].append(kwargs)
        return True
    return False


def add_edge(r, a, b, fwd, bwd):
    if not any(e["from"] == a and e["to"] == b for e in r["edges"]):
        r["edges"].append({
            "from": a, "to": b,
            "minutes_forward": fwd, "minutes_backward": bwd,
            "source": "estimated", "confirmed": True,
        })


r = load("G09")

# ─────────────────────────────────────────────
# NODES — 20 new + update existing
# ─────────────────────────────────────────────

# Trailheads (登山口) - all from OSM
add_node(r, id="n_g09_wuling", name="武嶺",
         lat=24.13711, lng=121.27614, elevation=3275, category="junction",
         tags=["road_highest_point"])
add_node(r, id="n_g09_th_main", name="合歡主峰登山口",
         lat=24.13364, lng=121.27159, elevation=3275, category="trailhead")
add_node(r, id="n_g09_th_north", name="合歡北峰登山口",
         lat=24.16569, lng=121.28934, elevation=3275, category="trailhead")
add_node(r, id="n_g09_th_east", name="合歡東峰登山口",
         lat=24.13978, lng=121.28731, elevation=3275, category="trailhead")
add_node(r, id="n_g09_th_jianshan_s", name="合歡尖山南登山口",
         lat=24.14258, lng=121.28454, elevation=3210, category="trailhead")
add_node(r, id="n_g09_th_jianshan_n", name="合歡尖山北登山口",
         lat=24.14570, lng=121.28403, elevation=3210, category="trailhead")
add_node(r, id="n_g09_th_shimen_n", name="石門北峰登山口",
         lat=24.15375, lng=121.28293, elevation=3210, category="trailhead")
add_node(r, id="n_g09_th_pingfeng", name="屏風山登山口",
         lat=24.17968, lng=121.31781, elevation=2400, category="trailhead")
add_node(r, id="n_g09_th_qilai_main", name="奇萊主峰登山口",
         lat=24.08726, lng=121.32141, elevation=2350, category="trailhead")
add_node(r, id="n_g09_kenan_pass", name="克難關",
         lat=24.15365, lng=121.28305, elevation=3179, category="junction")

# New 合歡 peaks
add_node(r, id="n_g09_hehuan_south", name="合歡南峰",
         lat=24.12421, lng=121.26896, elevation=3218, category="peak")
add_node(r, id="n_g09_hehuan_jianshan", name="合歡尖山",
         lat=24.14441, lng=121.28360, elevation=3218, category="peak")
add_node(r, id="n_g09_shimen_north", name="石門山北峰",
         lat=24.15760, lng=121.27956, elevation=3280, category="peak")

# 合歡→奇萊 traverse waypoints
add_node(r, id="n_g09_xiaoqilai", name="小奇萊",
         lat=24.13224, lng=121.29536, elevation=3153, category="peak")
add_node(r, id="n_g09_heishuitang", name="黑水塘",
         lat=24.14762, lng=121.34230, elevation=2400, category="water")

# 奇萊 area peaks
add_node(r, id="n_g09_karolou", name="卡羅樓山",
         lat=24.07830, lng=121.31584, elevation=3413, category="peak")
add_node(r, id="n_g09_qilaichi", name="奇萊池山",
         lat=24.10015, lng=121.32341, elevation=3436, category="peak")
add_node(r, id="n_g09_qilai_main_east", name="奇萊主山東峰",
         lat=24.08390, lng=121.33473, elevation=3394, category="peak")
add_node(r, id="n_g09_qilaijian", name="奇萊尖",
         lat=24.12657, lng=121.30026, elevation=3163, category="peak")
add_node(r, id="n_g09_pingfeng", name="屏風山",
         lat=24.14923, lng=121.34301, elevation=3247, category="peak")
add_node(r, id="n_g09_deepkutsu", name="深堀山",
         lat=24.05298, lng=121.27464, elevation=3313, category="peak")

# Camps
add_node(r, id="n_g09_yuexing_camp", name="月形池營地",
         lat=24.11754, lng=121.34544, elevation=2900, category="waypoint")
add_node(r, id="n_g09_songzhen_camp", name="松針營地",
         lat=24.16210, lng=121.32494, elevation=2700, category="waypoint")
add_node(r, id="n_g09_west_camp", name="西峰營地",
         lat=24.17782, lng=121.24557, elevation=3123, category="waypoint")

# Fix existing 石門山登山口 coordinates to match OSM
shimen_th = next((n for n in r["nodes"] if n["id"] == "n_g09_shimen_th"), None)
if shimen_th:
    shimen_th["lat"] = 24.14607
    shimen_th["lng"] = 121.28430

# ─────────────────────────────────────────────
# EDGES — comprehensive trail network
# ─────────────────────────────────────────────

# === 武嶺 hub: connects to 合歡管理站 and most trailheads ===
add_edge(r, "n_g09_wuling", "n_g09_hehuan_th", 5, 5)         # 武嶺 ↔ 管理站 (same area, very close)
add_edge(r, "n_g09_wuling", "n_g09_th_main", 5, 5)            # 武嶺 → 主峰登山口 (along road)
add_edge(r, "n_g09_wuling", "n_g09_th_jianshan_s", 10, 10)    # 武嶺 → 尖山南登山口
add_edge(r, "n_g09_th_jianshan_s", "n_g09_th_jianshan_n", 3, 3)
add_edge(r, "n_g09_th_jianshan_n", "n_g09_shimen_th", 2, 2)   # 尖山北 ↔ 石門山登山口
add_edge(r, "n_g09_shimen_th", "n_g09_th_east", 3, 3)         # 石門山 ↔ 合歡東峰登山口
add_edge(r, "n_g09_th_east", "n_g09_th_shimen_n", 5, 5)       # 沿公路
add_edge(r, "n_g09_th_shimen_n", "n_g09_th_north", 15, 15)    # 公路至北峰登山口
add_edge(r, "n_g09_kenan_pass", "n_g09_th_north", 10, 10)     # 克難關 → 北峰登山口

# === 各登山口→各峰 (short connections) ===
add_edge(r, "n_g09_th_main", "n_g09_hehuan_main", 30, 20)     # 主峰登山口 → 合歡主峰
add_edge(r, "n_g09_th_north", "n_g09_hehuan_north", 150, 90)  # 北峰登山口 → 合歡北峰 (steep)
add_edge(r, "n_g09_th_east", "n_g09_hehuan_east", 40, 30)     # 東峰登山口 → 合歡東峰
add_edge(r, "n_g09_th_jianshan_s", "n_g09_hehuan_jianshan", 20, 15)
add_edge(r, "n_g09_th_jianshan_n", "n_g09_hehuan_jianshan", 25, 20)
add_edge(r, "n_g09_th_shimen_n", "n_g09_shimen_north", 30, 25)

# === 合歡 ridge connections ===
add_edge(r, "n_g09_hehuan_main", "n_g09_hehuan_south", 60, 70)        # 主峰 → 南峰 (south ridge)
add_edge(r, "n_g09_hehuan_jianshan", "n_g09_shimen", 25, 25)          # 尖山 → 石門
add_edge(r, "n_g09_shimen_north", "n_g09_shimen", 20, 20)             # 石門北 → 石門
add_edge(r, "n_g09_shimen_north", "n_g09_kenan_pass", 15, 15)         # 石門北 → 克難關

# === West Peak connections ===
add_edge(r, "n_g09_hehuan_west", "n_g09_west_camp", 10, 10)           # 西峰 ↔ 西峰營地

# === Traverse 合歡 → 奇萊 via 小奇萊 ===
# Existing n_g09_hehuan_north → n_g09_chenggong_hut (53min) was unrealistic.
# Real route is via 奇萊登山口 area → 小奇萊 → 黑水塘 → 成功山莊.
remove_edge(r, "n_g09_hehuan_north", "n_g09_chenggong_hut")
add_edge(r, "n_g09_th_east", "n_g09_xiaoqilai", 60, 45)               # 東峰登山口 → 小奇萊 (ridge ascent)
add_edge(r, "n_g09_xiaoqilai", "n_g09_heishuitang", 60, 90)           # 小奇萊 → 黑水塘 (descent)
add_edge(r, "n_g09_heishuitang", "n_g09_chenggong_hut", 120, 80)      # 黑水塘 → 成功山莊 (climb)

# === 奇萊 ridge connections (主峰群) ===
add_edge(r, "n_g09_qilai_main", "n_g09_qilai_main_east", 30, 35)      # 主 ↔ 主東
add_edge(r, "n_g09_qilai_main", "n_g09_karolou", 60, 60)              # 主 ↔ 卡羅樓
add_edge(r, "n_g09_karolou", "n_g09_qilai_south", 90, 100)            # 卡羅樓 ↔ 奇萊南 (long ridge)
add_edge(r, "n_g09_qilaichi", "n_g09_qilai_main", 70, 75)             # 奇萊池山 ↔ 奇萊主
add_edge(r, "n_g09_qilai_hut", "n_g09_qilaichi", 60, 50)              # 奇萊山屋 ↔ 池山

# === 屏風山 (separate trailhead) ===
add_edge(r, "n_g09_th_pingfeng", "n_g09_songzhen_camp", 180, 120)     # 屏風登山口 → 松針營地
add_edge(r, "n_g09_songzhen_camp", "n_g09_pingfeng", 80, 60)          # 松針 → 屏風山
add_edge(r, "n_g09_pingfeng", "n_g09_chenggong_hut", 240, 280)        # 屏風 → 成功山莊 (traverse)

# === 月形池 area ===
add_edge(r, "n_g09_qilai_main", "n_g09_yuexing_camp", 90, 100)        # 主 ↔ 月形池營地

# === 奇萊主峰登山口 (alternate access) ===
add_edge(r, "n_g09_th_qilai_main", "n_g09_qilai_hut", 240, 180)       # 主峰登山口 → 奇萊山屋 (long climb)

# === 深堀山 (between 奇萊南峰 and 南華山) ===
add_edge(r, "n_g09_qilai_south", "n_g09_deepkutsu", 90, 100)
add_edge(r, "n_g09_deepkutsu", "n_g09_nanhua", 100, 110)

# === 奇萊尖 ===
add_edge(r, "n_g09_xiaoqilai", "n_g09_qilaijian", 50, 50)             # 小奇萊 ↔ 奇萊尖

# ─────────────────────────────────────────────
# NEW PRESETS — 增加常用 day-hike 預設
# ─────────────────────────────────────────────
existing_preset_ids = {p["id"] for p in r["presets"]}

new_presets = [
    {
        "id": "G09-hehuan-north-day",
        "name": "合歡北峰單登 (當日來回)",
        "startNodeId": "n_g09_th_north",
        "endNodeId": "n_g09_hehuan_north",
        "viaNodeIds": [],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-main-day",
        "name": "合歡主峰單登 (當日來回)",
        "startNodeId": "n_g09_th_main",
        "endNodeId": "n_g09_hehuan_main",
        "viaNodeIds": [],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-west-day",
        "name": "合歡西峰單登 (當日往返)",
        "startNodeId": "n_g09_hehuan_th",
        "endNodeId": "n_g09_hehuan_west",
        "viaNodeIds": [],
        "roundTrip": True,
    },
    {
        "id": "G09-hehuan-4peaks",
        "name": "合歡四峰串連 (主+東+石門+尖山)",
        "startNodeId": "n_g09_th_main",
        "endNodeId": "n_g09_hehuan_east",
        "viaNodeIds": ["n_g09_hehuan_main", "n_g09_wuling", "n_g09_th_jianshan_s",
                       "n_g09_hehuan_jianshan", "n_g09_shimen", "n_g09_shimen_th"],
        "roundTrip": False,
    },
    {
        "id": "G09-pingfeng",
        "name": "屏風山單登 (2天1夜)",
        "startNodeId": "n_g09_th_pingfeng",
        "endNodeId": "n_g09_pingfeng",
        "viaNodeIds": ["n_g09_songzhen_camp"],
        "suggestedDayBreaks": [{"atNodeId": "n_g09_songzhen_camp", "type": "camp"}],
        "roundTrip": True,
    },
]
for p in new_presets:
    if p["id"] not in existing_preset_ids:
        r["presets"].append(p)

save(r)

print(f"G09 expanded:")
print(f"  Nodes: {len(r['nodes'])}")
print(f"  Edges: {len(r['edges'])}")
print(f"  Presets: {len(r['presets'])}")
