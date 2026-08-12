#!/usr/bin/env python3
"""Build a Lua-API-name -> BCS-Y-entry index from manifests/symbols.json.

Step 3 of the Lua-name to opcode bridge. The 270+ BCS-Y entries written during MDI-019 record
Lua API names (e.g. `_setNameplate`, `_onCheckTargetable`) inline in
their `notes` prose, backtick-quoted. This tool extracts every such
mention and emits a queryable index so downstream stages can resolve
"which receiver/dispatcher fires this Lua name?".

Outputs:
    manifests/lua_api_index.json - the index. Schema:
            version, gameVersion, luaApiCount, totalRefs,
            apis: { luaName -> [ { bcsId, name, kind, address, slot? } ] }

Run:
    python tools\\extract_lua_api_index.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _symbols_io import load_symbols  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SYMBOLS_JSON = REPO_ROOT / "manifests" / "symbols.json"
OUT_JSON = REPO_ROOT / "manifests" / "lua_api_index.json"

LUA_NAME_NOTES_RE = re.compile(
    r"`(?P<bt>_[A-Za-z][A-Za-z0-9_]*)`"
    r"|"
    r"(?P<bare>_[a-z]+[A-Z][A-Za-z0-9_]{2,})"
)

LUA_NAME_IN_SYMNAME_RE = re.compile(
    r"_slot\d+_([a-z][A-Za-z0-9]*)(?:_FUN_|_fn_|$)"
)

# Only LuaActorImpl vftable names contribute to opcode binding; other vftables use orthogonal slots.
LUA_NAME_IN_LUAACTORIMPL_RE = re.compile(
    r"LuaActorImpl::vftable_slot\d+_([a-z][A-Za-z0-9]*)(?:_[A-Za-z0-9]+)*_FUN_"
)

# Bare prose prefixes are excluded to avoid false-positive Lua method names.
PROSE_PREFIX_NOISE = frozenset({
    "_on", "_set", "_get", "_is", "_has", "_will", "_did", "_init",
    "_update", "_create", "_destroy", "_load", "_save", "_can", "_should",
})

SLOT_RE = re.compile(r"\bslot\s+(\d+)\b", re.IGNORECASE)

VFTABLE_SLOT_RE = re.compile(r"vftable(?:\[(\d+)\]|\s+slot\s+(\d+))", re.IGNORECASE)

# A slot encoded in the symbol name is authoritative.
SLOT_IN_SYMNAME_RE = re.compile(r"_slot(\d+)_", re.IGNORECASE)


def _extract_slot(name: str, notes: str) -> int | None:
    m = SLOT_IN_SYMNAME_RE.search(name)
    if m:
        return int(m.group(1))
    m = VFTABLE_SLOT_RE.search(notes)
    if m:
        return int(m.group(1) or m.group(2))
    m = SLOT_RE.search(notes)
    if m:
        return int(m.group(1))
    return None


def build_index(symbols: list[dict]) -> tuple[dict[str, list[dict]], int]:
    """Build { luaName -> [reference, ...] }. Returns (index, totalRefs).

    Pulls Lua names from two locations and tags each ref with a
    confidence source:
      - source='name': the camelCase token between `_slotN_` and `_FUN_`
        in the symbol NAME. High confidence - the symbol's identity
        names its Lua API.
      - source='notes': backtick-quoted or bare camelCase tokens in
        `notes` prose. Weaker - the symbol mentions the name but isn't
        necessarily its dispatcher.

    Downstream (build_lua_to_opcode.py) requires source='name' for
    opcode binding to avoid false positives from prose mentions.
    """
    index: dict[str, list[dict]] = {}
    total_refs = 0
    for sym in symbols:
        notes = sym.get("notes", "") or ""
        name_field = sym["name"]
        seen_in_sym: set[tuple[str, str]] = set()
        slot = _extract_slot(name_field, notes)

        def _record(lua_name: str, source: str):
            """source = 'name' for symbol-NAME-encoded, 'notes' for prose mention.

            name-encoded refs are higher confidence (the symbol's identity
            directly names the Lua API). notes-only refs are weaker - the
            symbol mentions the name but isn't necessarily its dispatcher.
            """
            nonlocal total_refs
            if lua_name in PROSE_PREFIX_NOISE:
                return
            seen_key = (lua_name, source)
            if seen_key in seen_in_sym:
                return
            seen_in_sym.add(seen_key)
            ref = {
                "bcsId": sym["id"],
                "symbolName": name_field,
                "kind": sym["kind"],
                "address": sym["address"],
                "confidence": sym.get("confidence", "unknown"),
                "source": source,
            }
            if slot is not None:
                ref["slot"] = slot
            index.setdefault(lua_name, []).append(ref)
            total_refs += 1

        # LuaActorImpl names are the high-confidence opcode-binding source.
        lua_actor_impl_names: set[str] = set()
        for match in LUA_NAME_IN_LUAACTORIMPL_RE.finditer(name_field):
            lua_actor_impl_names.add("_" + match.group(1))
            _record("_" + match.group(1), "name-luaactorimpl")
        # Other vftables remain indexed but are tagged separately.
        for match in LUA_NAME_IN_SYMNAME_RE.finditer(name_field):
            full = "_" + match.group(1)
            if full in lua_actor_impl_names:
                continue
            _record(full, "name-other")
        for match in LUA_NAME_NOTES_RE.finditer(notes):
            _record(match.group("bt") or match.group("bare"), "notes")

    return index, total_refs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed output matches a fresh build")
    args = ap.parse_args()

    if not SYMBOLS_JSON.is_file():
        print(f"error: {SYMBOLS_JSON} missing", file=sys.stderr)
        return 1
    manifest = load_symbols(SYMBOLS_JSON)

    symbols = manifest.get("symbols", [])
    print(f"scanned {len(symbols)} symbols from {SYMBOLS_JSON.name}")

    index, total_refs = build_index(symbols)
    print(f"found {len(index)} distinct Lua API names "
          f"({total_refs} total references)")

    out: dict = {
        "version": "1",
        "gameVersion": manifest.get("gameVersion", "unknown"),
        "source": "manifests/symbols.json notes-field scan",
        "luaApiCount": len(index),
        "totalRefs": total_refs,
        "apis": {k: index[k] for k in sorted(index)},
    }

    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT_JSON.is_file() or OUT_JSON.read_text(encoding="utf-8") != rendered:
            print(f"error: {OUT_JSON.name} does not match a fresh build", file=sys.stderr)
            return 1
        print(f"OK: {OUT_JSON.name} matches a fresh build")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(rendered, encoding="utf-8", newline="")
    print(f"wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
