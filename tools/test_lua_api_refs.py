"""Prove structured Lua references preserve bindings independently of prose."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_lua_to_opcode as bridge
import extract_lua_api_index as indexer
import validate_catalog
from _lua_api_refs import lua_api_refs
from _symbols_io import load_symbols


class LuaApiReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = load_symbols()
        cls.symbols = {s["id"]: s for s in cls.document["symbols"]}
        cls.index = json.loads(indexer.OUT_JSON.read_text(encoding="utf-8"))
        cls.bridge = json.loads(bridge.OUT_JSON.read_text(encoding="utf-8"))

    def test_current_reference_and_binding_equivalence(self) -> None:
        index, count = indexer.build_index(self.document["symbols"])
        self.assertEqual(index, self.index["apis"])
        self.assertEqual(count, self.index["totalRefs"])
        for name, refs in index.items():
            self.assertEqual(
                sorted(bridge._bound_slots(name, refs, self.symbols)),
                self.bridge["bindings"][name]["observedSlots"],
                name,
            )

    def test_prose_and_symbol_renames_do_not_change_structured_bindings(self) -> None:
        symbols = copy.deepcopy(self.document["symbols"])
        renamed = {}
        for sym in symbols:
            if "luaApiRefs" not in sym:
                continue
            sym["name"] = (
                "renamed paired receiver"
                if sym["id"] == "BCS-Y-0238"
                else "Renamed::vftable_slot999_unrelated_paired_secondary_FUN_00000000"
            )
            sym["notes"] = "Unrelated `_inventedCallback` at vftable slot 999."
            renamed[sym["id"]] = sym["name"]
        self.assertTrue(renamed)
        expected = copy.deepcopy(self.index["apis"])
        for refs in expected.values():
            for ref in refs:
                if ref["bcsId"] in renamed:
                    ref["symbolName"] = renamed[ref["bcsId"]]
        index, _ = indexer.build_index(symbols)
        self.assertEqual(index, expected)
        by_id = {s["id"]: s for s in symbols}
        for name, refs in index.items():
            self.assertEqual(
                sorted(bridge._bound_slots(name, refs, by_id)),
                self.bridge["bindings"][name]["observedSlots"],
            )
        self.assertEqual(
            bridge._bound_slots(
                "_onUpdateDisplayName", index["_onUpdateDisplayName"], by_id
            ),
            {62},
        )

    def test_explicit_slot_edit_changes_binding_and_rejects_stale_index(self) -> None:
        symbol = copy.deepcopy(self.symbols["BCS-Y-0160"])
        for row in symbol["luaApiRefs"]:
            if row["source"] == "name-luaactorimpl":
                row["slot"] = 999
        by_id = {symbol["id"]: symbol}
        stale, _ = indexer.build_index([self.symbols[symbol["id"]]])
        with self.assertRaisesRegex(ValueError, "stale"):
            bridge._bound_slots(
                "_onUpdateDisplayName", stale["_onUpdateDisplayName"], by_id
            )
        index, _ = indexer.build_index([symbol])
        self.assertEqual(
            bridge._bound_slots(
                "_onUpdateDisplayName", index["_onUpdateDisplayName"], by_id
            ),
            {999},
        )

    def test_weaker_references_cannot_supply_opcode_slots(self) -> None:
        symbol = copy.deepcopy(self.symbols["BCS-Y-0160"])
        for source in ("notes", "name-other"):
            with self.subTest(source=source):
                symbol["luaApiRefs"] = [
                    {
                        "luaName": "_onUpdateDisplayName",
                        "slot": 62,
                        "source": source,
                        "bindsOpcode": False,
                    }
                ]
                index, _ = indexer.build_index([symbol])
                self.assertEqual(
                    bridge._bound_slots(
                        "_onUpdateDisplayName",
                        index["_onUpdateDisplayName"],
                        {symbol["id"]: symbol},
                    ),
                    set(),
                )
                symbol["luaApiRefs"][0]["bindsOpcode"] = True
                with self.assertRaisesRegex(ValueError, "only LuaActorImpl"):
                    lua_api_refs(symbol)

    def test_unstructured_luaactorimpl_name_requires_curation(self) -> None:
        symbol = copy.deepcopy(self.symbols["BCS-Y-0160"])
        del symbol["luaApiRefs"]
        with self.assertRaisesRegex(ValueError, "requires explicit luaApiRefs"):
            indexer.build_index([symbol])

    def test_receiver_prose_does_not_infer_missing_slot(self) -> None:
        receivers = json.loads(bridge.RECEIVER_JSON.read_text(encoding="utf-8"))
        receiver = next(
            r
            for r in receivers["inboundReceivers"]
            if r["luaActorImplSlot"] is not None
        )
        receiver["luaActorImplSlot"] = None
        receiver["bcsRefs"] = {
            "other": [
                {
                    "bcsId": "BCS-Y-0160",
                    "symbolName": "LuaActorImpl::vftable_slot62_onUpdateDisplayName_FUN_0076C4D0",
                }
            ]
        }
        receiver["notes"] = "LuaActorImpl::vftable slot 62"
        self.assertEqual(
            bridge._build_slot_to_receiver({"inboundReceivers": [receiver]}), {}
        )

    def test_catalog_validation_rejects_malformed_reference_fields(self) -> None:
        symbol = self.symbols["BCS-Y-0160"]
        for change in (
            {"slot": True},
            {"source": "confirmed"},
            {"bindsOpcode": "yes"},
            {"luaName": "invalid name"},
        ):
            with self.subTest(change=change):
                altered = copy.deepcopy(symbol)
                altered["luaApiRefs"][0].update(change)
                findings = validate_catalog.check_symbols(
                    {
                        "version": "1",
                        "gameVersion": "1.23b",
                        "symbolCount": 1,
                        "symbols": [altered],
                    }
                )
                self.assertTrue(
                    any(
                        f.severity == "ERROR" and "luaApiRefs" in f.message
                        for f in findings
                    )
                )
        duplicated = copy.deepcopy(symbol)
        duplicated["luaApiRefs"].append(copy.deepcopy(duplicated["luaApiRefs"][0]))
        with self.assertRaisesRegex(ValueError, "repeats"):
            lua_api_refs(duplicated)

    def test_cli_outputs_remain_byte_identical(self) -> None:
        for builder in (indexer, bridge):
            with (
                self.subTest(builder=builder.__name__),
                tempfile.TemporaryDirectory() as raw,
            ):
                expected = builder.OUT_JSON.read_bytes()
                output = Path(raw) / "output.json"
                with (
                    patch.object(builder, "OUT_JSON", output),
                    patch.object(sys, "argv", [builder.__file__]),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    self.assertEqual(builder.main(), 0)
                self.assertEqual(output.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
