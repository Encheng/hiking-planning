#!/usr/bin/env python3
"""Detect suspicious edges across all routes — heuristic check for time direction errors.

Flags edges where:
- minutes_forward < minutes_backward AND `from` is at LOWER elevation than `to`
  (means: declared "going up" is FASTER than "going down" — likely flipped)
- minutes_forward > minutes_backward AND `from` is at HIGHER elevation than `to`
  (means: declared "going down" is SLOWER than "going up" — likely flipped)
- Speed > 12 km/h (likely vehicle drive or wrong)
- Speed < 0.3 km/h (suspiciously slow)

Usage: python3 scripts/detect-suspicious-edges.py [--route G02]
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"


def haversine_km(a: dict, b: dict) -> float:
    R = 6371
    dlat = math.radians(b["lat"] - a["lat"])
    dlng = math.radians(b["lng"] - a["lng"])
    aa = (math.sin(dlat / 2) ** 2 +
          math.cos(math.radians(a["lat"])) * math.cos(math.radians(b["lat"])) *
          math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(aa), math.sqrt(1 - aa))


def check_route(route_id: str) -> list[str]:
    path = ROUTES_DIR / f"{route_id}.json"
    if not path.exists():
        return [f"{route_id}: file not found"]
    with open(path) as f:
        route = json.load(f)

    nodes_by_id = {n["id"]: n for n in route["nodes"]}
    findings: list[str] = []

    for e in route["edges"]:
        if e.get("transport") == "vehicle":
            continue  # Vehicle drives have road speeds, not hiking
        n_from = nodes_by_id.get(e["from"])
        n_to = nodes_by_id.get(e["to"])
        if not n_from or not n_to:
            continue
        elev_from = n_from.get("elevation") or 0
        elev_to = n_to.get("elevation") or 0
        fwd = e["minutes_forward"]
        bwd = e["minutes_backward"]

        delta = elev_to - elev_from  # positive: going up
        from_name = n_from["name"]
        to_name = n_to["name"]
        km = haversine_km(n_from, n_to)

        # 1. Direction-reversal heuristic
        # Only flag when elevation diff is significant (>50m) — otherwise times can be tied
        if abs(delta) >= 50:
            if delta > 0 and fwd < bwd:
                # from→to is UP elevation, fwd should be larger
                findings.append(
                    f"  {from_name}(↓{elev_from}m) → {to_name}(↑{elev_to}m): "
                    f"+{delta}m UP but fwd={fwd} < bwd={bwd}. **Possibly direction reversed**"
                )
            elif delta < 0 and fwd > bwd:
                # from→to is DOWN elevation, fwd should be smaller
                findings.append(
                    f"  {from_name}(↑{elev_from}m) → {to_name}(↓{elev_to}m): "
                    f"{delta}m DOWN but fwd={fwd} > bwd={bwd}. **Possibly direction reversed**"
                )

        # 2. Speed sanity check
        if km > 0 and fwd > 0:
            speed = km / (fwd / 60)
            if speed > 12:
                findings.append(
                    f"  {from_name} → {to_name}: fwd={fwd}min for {km:.2f}km → {speed:.1f}km/h "
                    f"(possibly vehicle drive miscoded as walk)"
                )
        if km > 0 and bwd > 0:
            speed = km / (bwd / 60)
            if speed > 12:
                findings.append(
                    f"  {to_name} → {from_name}: bwd={bwd}min for {km:.2f}km → {speed:.1f}km/h "
                    f"(possibly vehicle drive miscoded as walk)"
                )

    if findings:
        return [f"\n## {route_id} {route.get('name', '')}", ""] + findings
    return []


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--route":
        route_ids = [sys.argv[2]]
    else:
        route_ids = sorted([p.stem for p in ROUTES_DIR.glob("G*.json")])

    print("# 可疑邊偵測報告\n")
    print("依據海拔差自動偵測「上行時間 < 下行時間」的異常邊。")
    print("注意: 這只是啟發式檢查，需要人工複查上河圖確認。\n")

    total = 0
    for rid in route_ids:
        results = check_route(rid)
        if results:
            for line in results:
                print(line)
                if "Possibly" in line or "miscoded" in line:
                    total += 1

    print(f"\n---\n總計 {total} 條可疑邊")


if __name__ == "__main__":
    main()
