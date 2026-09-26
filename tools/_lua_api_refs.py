"""Read explicit symbol-owned Lua references without promoting prose mentions."""

from __future__ import annotations

import re

LUA_NAME_RE = re.compile(r"_[A-Za-z][A-Za-z0-9_]*")
SOURCES = frozenset({"name-luaactorimpl", "name-other", "notes"})


def lua_api_refs(symbol: dict) -> list[dict] | None:
    """Return validated references, or None for an unstructured symbol."""
    if "luaApiRefs" not in symbol:
        return None
    refs = symbol["luaApiRefs"]
    label = f"{symbol.get('id', '<symbol>')}.luaApiRefs"
    if not isinstance(refs, list):
        raise ValueError(f"{label} must be a list")
    seen = set()
    for row in refs:
        if not isinstance(row, dict) or set(row) != {
            "luaName",
            "slot",
            "source",
            "bindsOpcode",
        }:
            raise ValueError(f"{label} requires luaName, slot, source, bindsOpcode")
        if not isinstance(row["luaName"], str) or not LUA_NAME_RE.fullmatch(
            row["luaName"]
        ):
            raise ValueError(f"{label} has an invalid Lua name")
        if type(row["slot"]) is not int or row["slot"] < 0:
            raise ValueError(f"{label} slot must be a nonnegative integer")
        if not isinstance(row["source"], str) or row["source"] not in SOURCES:
            raise ValueError(f"{label} has an invalid source category")
        if type(row["bindsOpcode"]) is not bool:
            raise ValueError(f"{label} bindsOpcode must be a boolean")
        if row["bindsOpcode"] and row["source"] != "name-luaactorimpl":
            raise ValueError(f"{label} only LuaActorImpl references may bind opcodes")
        key = row["luaName"], row["source"]
        if key in seen:
            raise ValueError(f"{label} repeats {key}")
        seen.add(key)
    return refs
