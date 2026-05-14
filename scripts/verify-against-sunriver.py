#!/usr/bin/env python3
"""Cross-check route JSON edge times against 上河圖 reference data (YAML).

Usage: python3 scripts/verify-against-sunriver.py G02

Reads:
- docs/verification/<route>-sunriver-source.yaml   (上河 reference)
- public/data/routes/<route>.json                  (current data)

Writes:
- docs/verification/<route>-comparison.md          (verification report)

Reports each edge as: OK / MISMATCH / DIRECTION_FLIPPED / NOT_IN_SUNRIVER / NOT_IN_CODE
"""
import json
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROUTES_DIR = ROOT / "public" / "data" / "routes"
VER_DIR = ROOT / "docs" / "verification"


def load_route(route_id: str) -> dict:
    path = ROUTES_DIR / f"{route_id}.json"
    with open(path) as f:
        return json.load(f)


def load_sunriver(route_id: str) -> dict:
    path = VER_DIR / f"{route_id}-sunriver-source.yaml"
    if not path.exists():
        sys.exit(f"No sunriver reference: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: verify-against-sunriver.py <route_id>")
    route_id = sys.argv[1]

    route = load_route(route_id)
    ref = load_sunriver(route_id)

    nodes_by_id = {n["id"]: n for n in route["nodes"]}
    nodes_by_name = {n["name"]: n for n in route["nodes"]}

    # Build dict of (low_id, high_id) -> (fwd, bwd, from, to)
    code_edges: dict[tuple[str, str], dict] = {}
    for e in route["edges"]:
        a, b = e["from"], e["to"]
        # Use canonical key (sorted)
        key = tuple(sorted([a, b]))
        code_edges[key] = {
            "from": a, "to": b,
            "fwd": e["minutes_forward"], "bwd": e["minutes_backward"],
            "source": e.get("source", "?"),
        }

    lines = []
    lines.append(f"# {route_id} {route['name']} — 上河圖比對報告")
    lines.append("")
    lines.append(f"Reference: `docs/verification/{route_id}-sunriver-source.yaml`")
    lines.append(f"Code:      `public/data/routes/{route_id}.json`")
    lines.append("")
    lines.append("## 對照結果")
    lines.append("")
    lines.append("| # | 較低節點 | 較高節點 | 上河 UP | 上河 DOWN | 程式 from→to | 程式 fwd | 程式 bwd | 狀態 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    matched_keys: set[tuple[str, str]] = set()
    ok_count = 0
    mismatch_count = 0
    flipped_count = 0
    missing_count = 0

    for i, seg in enumerate(ref["segments"], 1):
        from_name = seg["from"]
        to_name = seg["to"]
        ref_up = seg["up_min"]
        ref_down = seg["down_min"]

        # Find nodes by name
        n_from = nodes_by_name.get(from_name)
        n_to = nodes_by_name.get(to_name)

        if not n_from or not n_to:
            missing = []
            if not n_from: missing.append(from_name)
            if not n_to: missing.append(to_name)
            lines.append(
                f"| {i} | {from_name} | {to_name} | {ref_up} | {ref_down} | — | — | — | "
                f"❓ 節點缺: {', '.join(missing)} |"
            )
            missing_count += 1
            continue

        # Determine which is higher elevation
        elev_from = n_from.get("elevation") or 0
        elev_to = n_to.get("elevation") or 0
        if elev_from > elev_to:
            high_id, low_id = n_from["id"], n_to["id"]
            high_name, low_name = from_name, to_name
        else:
            high_id, low_id = n_to["id"], n_from["id"]
            high_name, low_name = to_name, from_name

        key = tuple(sorted([high_id, low_id]))
        edge = code_edges.get(key)
        if not edge:
            lines.append(
                f"| {i} | {low_name} | {high_name} | {ref_up} | {ref_down} | — | — | — | "
                f"❌ 邊不存在於程式 |"
            )
            missing_count += 1
            continue

        matched_keys.add(key)
        code_from = edge["from"]
        code_to = edge["to"]
        code_fwd = edge["fwd"]
        code_bwd = edge["bwd"]

        # Determine code's fwd direction relative to elevation
        if code_from == low_id:
            # fwd is UP direction
            code_up = code_fwd
            code_down = code_bwd
        else:
            # fwd is DOWN direction
            code_up = code_bwd
            code_down = code_fwd

        # Compare
        if code_up == ref_up and code_down == ref_down:
            status = "✅ OK"
            ok_count += 1
        elif code_up == ref_down and code_down == ref_up:
            status = f"⚠️ 方向反了 (程式 UP={code_up}, DOWN={code_down})"
            flipped_count += 1
        else:
            status = f"❌ 不符 (程式 UP={code_up}, DOWN={code_down})"
            mismatch_count += 1

        code_dir = f"{nodes_by_id[code_from]['name']}→{nodes_by_id[code_to]['name']}"
        lines.append(
            f"| {i} | {low_name} | {high_name} | {ref_up} | {ref_down} | {code_dir} | "
            f"{code_fwd} | {code_bwd} | {status} |"
        )

    # Edges in code not covered by reference
    lines.append("")
    lines.append("## 程式中有但上河圖參考未列出的邊")
    lines.append("")
    lines.append("| From → To | fwd | bwd | source |")
    lines.append("|---|---|---|---|")
    code_only = []
    for key, e in code_edges.items():
        if key in matched_keys:
            continue
        from_name = nodes_by_id[e["from"]]["name"]
        to_name = nodes_by_id[e["to"]]["name"]
        lines.append(f"| {from_name} → {to_name} | {e['fwd']} | {e['bwd']} | {e['source']} |")
        code_only.append((from_name, to_name))

    lines.append("")
    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- ✅ 完全相符: {ok_count}")
    lines.append(f"- ⚠️ 方向反了: {flipped_count}")
    lines.append(f"- ❌ 時間不符: {mismatch_count}")
    lines.append(f"- ❓ 邊或節點缺失: {missing_count}")
    lines.append(f"- 程式中未對照: {len(code_only)} (上河圖參考檔未列出)")

    out = VER_DIR / f"{route_id}-comparison.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    print(f"  OK: {ok_count}, FLIPPED: {flipped_count}, MISMATCH: {mismatch_count}, MISSING: {missing_count}")


if __name__ == "__main__":
    main()
