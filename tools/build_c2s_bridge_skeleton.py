#!/usr/bin/env python3
"""Build the c2s outbound bridge skeleton.

Combines the outbound bridge inputs:
  - serverboundGap entries not yet class-attributed
  - operationClasses with vtable-mapped emissions
  - pcap_validation c2sOpcodeHistogram observations
  - lua_api_index Lua N-API names

Output: manifests/c2s_bridge_skeleton.json with per-opcode rows:
  - opcode
  - observedInPcaps (count + capture names)
  - anchor names from the pinned outbound catalog and local decomp anchors
  - candidateLuaApis (Lua names whose token matches the anchor name)

This is a SKELETON, not a confirmed binding map. Each row is a hypothesis
that requires decompilation evidence. The matching is token-based on the
anchor names, so false positives are expected. The output prioritizes likely
targets for follow-up analysis.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from _regen_guard import add_force_arg, check_regen_safe  # noqa: E402
OUTBOUND_MAP = REPO_ROOT / "manifests" / "operation_opcode_map_outbound.json"
PCAP_VALIDATION = REPO_ROOT / "manifests" / "pcap_validation.json"
LUA_INDEX = REPO_ROOT / "manifests" / "lua_api_index.json"
OUT_JSON = REPO_ROOT / "manifests" / "c2s_bridge_skeleton.json"


def tokens_from_anchor(anchor: str | None) -> list[str]:
    """Split CamelCase/snake_case into normalized tokens."""
    if not anchor:
        return []
    base = anchor.split("::")[-1] if "::" in anchor else anchor
    base = base.replace("Opcode", "").replace("Packet", "").replace("Handler", "")
    base = base.replace("OP_RX_", "").replace("OP_TX_", "")
    parts = re.findall(r"[A-Z][a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|$)|\d+|[a-z]+", base)
    return [p.lower() for p in parts if p and p.lower() not in (
        "opcode", "packet", "handler", "request", "response", "map", "client"
    )]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_force_arg(ap)
    args = ap.parse_args()

    outbound = json.load(OUTBOUND_MAP.open(encoding="utf-8"))
    pcap = json.load(PCAP_VALIDATION.open(encoding="utf-8"))
    lua = json.load(LUA_INDEX.open(encoding="utf-8"))

    gap_entries = outbound.get("serverboundGap", [])
    op_classes = outbound.get("operationClasses", [])
    observed_c2s = pcap.get("c2sOpcodeHistogram", {})
    c2s_per_pcap = {
        name: data.get("c2s", {})
        for name, data in pcap.get("perPcap", {}).items()
    }

    witnesses: dict[int, list[str]] = defaultdict(list)
    for pcap_name, c2s_ops in c2s_per_pcap.items():
        for op_hex, cnt in c2s_ops.items():
            try:
                op = int(op_hex, 16)
            except (ValueError, TypeError):
                continue
            if cnt:
                witnesses[op].append(pcap_name)

    lua_names: list[str] = []
    if isinstance(lua, dict) and "apis" in lua:
        apis_field = lua["apis"]
        if isinstance(apis_field, dict):
            lua_names = list(apis_field.keys())
        elif isinstance(apis_field, list):
            lua_names = [a["luaName"] for a in apis_field if "luaName" in a]

    lua_name_tokens: dict[str, set[str]] = {}
    for name in lua_names:
        stripped = name.lstrip("_")
        parts = re.findall(r"[A-Z][a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|$)|\d+|[a-z]+", stripped)
        lua_name_tokens[name] = {p.lower() for p in parts if p}

    def candidate_lua_apis(anchor_tokens: list[str]) -> list[str]:
        if not anchor_tokens:
            return []
        anchor_set = set(anchor_tokens)
        scored = []
        for name, toks in lua_name_tokens.items():
            overlap = len(toks & anchor_set)
            if overlap >= 1:
                scored.append((overlap, len(toks ^ anchor_set), name))
        scored.sort(key=lambda x: (-x[0], x[1], x[2]))
        return [s[2] for s in scored[:5]]

    classed_opcodes: set[int] = set()
    for c in op_classes:
        for op in c.get("opcodes", []):
            classed_opcodes.add(op["opcode"])
        for em in c.get("confirmedEmissions", []):
            classed_opcodes.add(em["opcode"])

    rows = []
    for entry in gap_entries:
        op = entry["opcode"]
        op_hex = entry["opcodeHex"]
        anchor_b = entry.get("implementationAnchor")
        anchor_d = entry.get("decompAnchor")
        tokens = list(set(tokens_from_anchor(anchor_b) + tokens_from_anchor(anchor_d)))
        pcap_count = observed_c2s.get(op_hex, 0)
        rows.append({
            "opcode": op,
            "opcodeHex": op_hex,
            "name": entry.get("name"),
            "bucket": entry.get("bucket"),
            "implementationAnchor": anchor_b,
            "decompAnchor": anchor_d,
            "confidence": entry.get("confidence"),
            "observedInPcaps": {
                "count": pcap_count,
                "captures": sorted(set(witnesses.get(op, []))),
            },
            "alreadyClassAttributed": op in classed_opcodes,
            "anchorTokens": tokens,
            "candidateLuaApis": candidate_lua_apis(tokens),
        })

    rows.sort(key=lambda r: (
        -1 if r["observedInPcaps"]["count"] > 0 else 1,
        -r["observedInPcaps"]["count"],
        r["opcode"],
    ))

    intersect_count = sum(1 for r in rows if r["observedInPcaps"]["count"] > 0)

    out = {
        "version": "1",
        "gameVersion": "1.23b",
        "description": (
            "c2s bridge skeleton. Inverse of the s2c bridge: rather "
            "than 'receiver writes X, Lua reader sees X', the c2s direction "
            "is 'Lua setter triggers emission of opcode Y'. This skeleton "
            f"joins serverboundGap (the {len(gap_entries)} unbound c2s opcodes) with "
            "pcap_validation observation counts and proposes "
            "candidate Lua N-API names by token overlap with each opcode's "
            "anchor names from the pinned outbound catalog and local decomp "
            "anchors. Token matching is "
            "heuristic; each row "
            "is a hypothesis for decomp-based verification, not a confirmed "
            "binding."
        ),
        "method": (
            "1. For each serverboundGap entry, tokenize implementationAnchor and "
            "decompAnchor (split CamelCase, drop generic suffixes like "
            "'Packet'/'Handler'/'Opcode'/'Request'). "
            "2. For each Lua name in lua_api_index, tokenize the same way. "
            "3. Score Lua candidates by token overlap with the opcode anchor. "
            "4. Tag each row with observed pcap count + capture witnesses."
        ),
        "totals": {
            "serverboundGap": len(rows),
            "observedInPcaps": intersect_count,
            "alreadyClassAttributed": sum(
                1 for r in rows if r["alreadyClassAttributed"]
            ),
        },
        "rows": rows,
        "nextSteps": [
            "Pick the 5-10 highest-EV rows (observed pcap + clear "
            "anchor) and decomp the emission site to verify candidateLuaApis. "
            "Likely first targets: 0x00ca (PositionUpdate), 0x012d (EventStart), "
            "0x012e (EventUpdate), 0x00cd (SetTarget), 0x00cc (LockTarget), "
            "0x0133 (GroupCreated), 0x0003 (ChatMessage).",
            "Extend the bridge model with outboundOpcodeBindings - "
            "the inverse of confirmedIndirectBindings.",
        ],
    }
    if not check_regen_safe(OUT_JSON, out, args.force):
        return 1

    OUT_JSON.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(f"wrote {OUT_JSON}")
    print(f"  serverboundGap: {len(rows)}")
    print(f"  observed in pcaps: {intersect_count}")
    print(f"  already class-attributed: {sum(1 for r in rows if r['alreadyClassAttributed'])}")

    print()
    print("=== Top 10 high-EV outbound targets ===")
    for r in rows[:10]:
        cands = r["candidateLuaApis"][:3]
        print(f"  {r['opcodeHex']} ({r['observedInPcaps']['count']:6d}x) "
              f"{r['name']:30s} "
              f"candidates={cands}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
