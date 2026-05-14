#!/usr/bin/env python3
"""Generate a markdown verification report for a route — used to systematically
cross-check edge times against 上河圖 step diagrams.

Usage:
    python3 scripts/gen-verification-report.py G02

Output: docs/verification/G02.md
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"
OUT_DIR = ROOT / "docs" / "verification"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def gen(route_id: str) -> Path:
    route_path = ROUTES_DIR / f"{route_id}.json"
    if not route_path.exists():
        sys.exit(f"Route file not found: {route_path}")

    with open(route_path) as f:
        r = json.load(f)

    nodes_by_id = {n["id"]: n for n in r["nodes"]}

    lines: list[str] = []
    lines.append(f"# {r['id']} {r['name']} — 上河圖時間驗證報告")
    lines.append("")
    lines.append(f"**Source**: `public/data/routes/{r['id']}.json`")
    lines.append(f"**Generated nodes**: {len(r['nodes'])}")
    lines.append(f"**Generated edges**: {len(r['edges'])}")
    lines.append("")
    lines.append("## 驗證說明")
    lines.append("")
    lines.append("- **方向慣例**: `minutes_forward` 是「from → to」方向的時間，"
                 "`minutes_backward` 是反向時間")
    lines.append("- **上河圖判讀**: 兩個數字中**較小的是下行**（順海拔下降），"
                 "**較大的是上行**（順海拔上升）")
    lines.append("- **核對方式**: 對每條邊，從上河圖找到對應段落，記下 UP/DOWN 兩個值，"
                 "比較程式裡的 fwd/bwd")
    lines.append("- 如果 `from` 較低、`to` 較高（fwd 為上行）：fwd 應為較大值")
    lines.append("- 如果 `from` 較高、`to` 較低（fwd 為下行）：fwd 應為較小值")
    lines.append("")
    lines.append("## 節點列表")
    lines.append("")
    lines.append("| ID | 名稱 | 類型 | 海拔 | 緯度 | 經度 |")
    lines.append("|---|---|---|---|---|---|")
    for n in r["nodes"]:
        lines.append(
            f"| `{n['id']}` | {n['name']} | {n['category']} | "
            f"{n.get('elevation', '?')} | {n['lat']:.4f} | {n['lng']:.4f} |"
        )

    lines.append("")
    lines.append("## 邊（步程時間）對照表")
    lines.append("")
    lines.append("依目前程式裡的 `from → to` 方向列出。請於右側兩欄填入上河圖數值，"
                 "並於最後一欄標記 ✅/❌/?。")
    lines.append("")
    lines.append("| # | From 節點 | → | To 節點 | 高差 | fwd | bwd | 上河 UP | 上河 DOWN | 狀態 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for i, e in enumerate(r["edges"], 1):
        n_from = nodes_by_id.get(e["from"], {})
        n_to = nodes_by_id.get(e["to"], {})
        from_name = n_from.get("name", e["from"])
        to_name = n_to.get("name", e["to"])
        elev_from = n_from.get("elevation")
        elev_to = n_to.get("elevation")
        if isinstance(elev_from, (int, float)) and isinstance(elev_to, (int, float)):
            delta = elev_to - elev_from
            delta_str = f"{'+' if delta >= 0 else ''}{int(delta)}m"
        else:
            delta_str = "?"
        fwd = e["minutes_forward"]
        bwd = e["minutes_backward"]
        source = e.get("source", "?")
        # Pre-fill expected direction hint
        if isinstance(elev_from, (int, float)) and isinstance(elev_to, (int, float)):
            direction_hint = "↑ UP" if elev_to > elev_from else "↓ DOWN" if elev_to < elev_from else "→"
        else:
            direction_hint = "?"
        lines.append(
            f"| {i} | {from_name} | {direction_hint} | {to_name} | {delta_str} | "
            f"**{fwd}** | {bwd} | _填_ | _填_ | _待核_ |"
        )

    lines.append("")
    lines.append("## 來源標記")
    lines.append("")
    sources = {}
    for e in r["edges"]:
        sources[e.get("source", "unknown")] = sources.get(e.get("source", "unknown"), 0) + 1
    for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
        lines.append(f"- `{src}`: {cnt} 條邊")

    out = OUT_DIR / f"{route_id}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: gen-verification-report.py <route_id> [route_id ...]")
    for rid in sys.argv[1:]:
        path = gen(rid)
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
