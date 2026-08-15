#!/usr/bin/env python3
"""Enrich the canonical GAM hash-name catalog with full-corpus profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verify_murmur2 import murmur2_backward

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "manifests" / "gam_hash_names.json"

SCRIPT_CONSUMERS = {
    "playerWork.castCommandClient": ["PlayerBaseClass.getCastCommand", "ActionMenuWidget.updateCastInfo"],
    "playerWork.castEndClient": ["PlayerBaseClass.getCastEndTime", "ActionGaugeWidget.update"],
    "charaWork.battleTemp.castGauge_speed[0]": ["CharaBaseClass.getCastSpeed"],
    "charaWork.battleTemp.castGauge_speed[1]": ["CharaBaseClass.getCastSpeed"],
}
SCRIPT_CONSUMER_REFS = [
    "xivl-client-scripts:lua/scripts/chara/player/playerbaseclass.lua",
    "xivl-client-scripts:lua/scripts/chara/charabaseclass_battle.lua",
    "xivl-client-scripts:lua/scripts/widget/actionmenuwidget.lua",
    "xivl-client-scripts:lua/scripts/widget/actiongaugewidget.lua",
    "manifests/cast_chant_presentation.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wire_type(widths: dict[str, int]) -> str:
    keys = {int(key) for key in widths}
    if keys == {1}:
        return "u8_bits"
    if keys == {2}:
        return "u16_le_bits"
    if keys == {4}:
        return "u32_or_f32_le_bits"
    return "opaque_variable_width"


def build(accounting_path: Path, source_commit: str) -> dict:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    accounting = json.loads(accounting_path.read_text(encoding="utf-8"))
    profiles = {row["property_hash"]: row for row in accounting["hash_profiles"]}
    if len(profiles) != 263 or accounting["record_count"] != 8918:
        raise ValueError("capture accounting is not the pinned full property corpus")
    total = 0
    for entry in catalog["resolved"]:
        profile = profiles.get(entry["idHex"])
        if profile is None:
            raise ValueError(f"missing observed hash {entry['idHex']}")
        for name in entry["names"]:
            got = murmur2_backward(name.encode("ascii"))
            if got != int(entry["idHex"], 16):
                raise ValueError(f"hash mismatch: {name}")
        if profile["occurrences"] != entry["count"] or profile["widths"] != entry["sizes"]:
            raise ValueError(f"capture profile drift: {entry['idHex']}")
        entry["wireValueType"] = wire_type(profile["widths"])
        entry["observedProfile"] = {
            key: profile[key] for key in ("occurrences", "captures", "scenarios",
                                          "source_actors", "destination_actors",
                                          "widths", "distinct_values",
                                          "value_u_le_min", "value_u_le_max", "top_values")
        }
        consumers = sorted({consumer for name in entry["names"]
                            for consumer in SCRIPT_CONSUMERS.get(name, [])})
        entry["consumingScriptGetters"] = consumers
        entry["resolutionEvidence"] = {
            "method": "exact_backward_murmurhash2_seed_0",
            "candidateNames": entry["names"],
            "verifiedBy": "tools/verify_murmur2.py",
        }
        total += entry["count"]
    unresolved = catalog.get("unresolved", [])
    unresolved_occurrences = sum(row.get("count", 0) for row in unresolved)
    catalog["coverage"] = {
        "distinctHashes": accounting["distinct_hashes"],
        "resolvedHashes": len(catalog["resolved"]),
        "unresolvedHashes": len(unresolved),
        "totalOccurrences": accounting["record_count"],
        "resolvedOccurrences": total,
        "unresolvedOccurrences": unresolved_occurrences,
        "occurrenceWeightedResolvedShare": total / accounting["record_count"],
    }
    catalog["provenance"]["fullCorpusProfile"] = {
        "repository": "XIVLegacy/xivl-captures",
        "commit": source_commit,
        "path": "studies/property-stream-hash-catalog/derived/accounting.json",
        "sha256": sha256(accounting_path),
        "derivation": "tools/extractors/extract_property_stream_catalog.py decoded all s2c 0x0137 records",
    }
    catalog["provenance"]["candidateBoundary"] = (
        "The 263 candidate names predate the exact-hash verification recorded here. "
        "Every exact hash is verified; similarity and contextual guesses are not promoted."
    )
    catalog["provenance"]["consumerContextRefs"] = SCRIPT_CONSUMER_REFS
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures-accounting", type=Path, required=True)
    parser.add_argument("--captures-commit", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(args.captures_accounting, args.captures_commit)
    data = (json.dumps(result, indent=2) + "\n").encode("ascii")
    if args.check:
        if CATALOG.read_bytes() != data:
            print("stale manifests/gam_hash_names.json")
            return 1
        print("property hash catalog verified")
        return 0
    CATALOG.write_bytes(data)
    print("property hash catalog written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
