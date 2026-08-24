#!/usr/bin/env python3
"""Analyze c2s 0x012d owner IDs against static client command rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "manifests" / "combat_command_emission.json"
STATIC_ACTOR_PREFIX = 0xA0F00000
STATIC_ACTOR_MASK = 0xFFFF0000
OWNER_BODY_OFFSET = 0x14
COMBAT_CAPTURES = {
    "combat_autoattack.pcapng",
    "combat_skills.pcapng",
    "party_battle_leve.pcapng",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _commit(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _hex(value: int, width: int = 8) -> str:
    return f"0x{value:0{width}x}"


def _distribution(values: list[int], width: int = 8) -> list[dict[str, object]]:
    return [
        {"value": _hex(value, width), "count": count}
        for value, count in sorted(Counter(values).items())
    ]


def _all_event_starts(captures_repo: Path) -> list[dict[str, object]]:
    extractor_dir = captures_repo / "tools" / "extractors"
    extractor_path = extractor_dir / "extract_content_samples.py"
    sys.path.insert(0, str(extractor_dir))
    sys.path.insert(0, str(extractor_dir.parent))
    spec = importlib.util.spec_from_file_location("xivl_extract_content_samples", extractor_path)
    if spec is None or spec.loader is None:
        raise OSError(f"cannot load {extractor_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    events: list[dict[str, object]] = []
    for path in module.default_corpus_paths():
        if path.is_file():
            events.extend(module.walk_capture_content(path)["event_starts"])
    return events


def build(captures_repo: Path, client_data_repo: Path) -> dict:
    samples_path = captures_repo / "derived" / "payload_samples.json"
    actors_path = client_data_repo / "manifests" / "staticactor_class_paths.json"
    commands_path = client_data_repo / "csv" / "gameCommand.csv"
    samples_doc = json.loads(samples_path.read_text(encoding="utf-8"))
    actor_doc = json.loads(actors_path.read_text(encoding="utf-8"))

    sample_group = samples_doc["samples"]["c2s"]["0x012d"]
    samples = sample_group["samples"]
    if sample_group["sampleCount"] != len(samples):
        raise ValueError("c2s 0x012d sampleCount does not match retained rows")

    retained_owners: list[tuple[str, int]] = []
    for sample in samples:
        body = bytes.fromhex(sample["bytes"])
        if sample["sub_size"] != 216 or len(body) != 200:
            raise ValueError("c2s 0x012d retained sample framing drifted")
        retained_owners.append((sample["capture"], struct.unpack_from("<I", body, OWNER_BODY_OFFSET)[0]))

    event_starts = _all_event_starts(captures_repo)
    owners = [
        (str(event["capture"]), int(event["ownerActorId"]))
        for event in event_starts
    ]
    if len(owners) != 126:
        raise ValueError(f"c2s 0x012d raw replay found {len(owners)} events, expected 126")

    static_actors = {row["id"]: row["classPath"] for row in actor_doc["records"]}
    with commands_path.open(encoding="utf-8-sig", newline="") as handle:
        command_ids = {
            int(row[0])
            for row in csv.reader(handle)
            if row and row[0].isdigit()
        }

    static_rows: list[dict[str, object]] = []
    for capture, owner in owners:
        if owner & STATIC_ACTOR_MASK != STATIC_ACTOR_PREFIX:
            continue
        row_id = owner & 0xFFFF
        class_path = static_actors.get(row_id)
        static_rows.append({
            "capture": capture,
            "ownerActorId": owner,
            "rowId": row_id,
            "classPath": class_path,
            "gameCommandHit": row_id in command_ids,
        })

    joined_distribution: list[dict[str, object]] = []
    joined_counts = Counter(
        (row["ownerActorId"], row["rowId"], row["classPath"], row["gameCommandHit"])
        for row in static_rows
    )
    for (owner, row_id, class_path, game_hit), count in sorted(joined_counts.items()):
        joined_distribution.append({
            "ownerActorId": _hex(owner),
            "low16RowId": row_id,
            "count": count,
            "staticActorClassPath": class_path,
            "gameCommandHit": game_hit,
        })

    scenario_groups: dict[str, dict[str, object]] = {}
    for name, is_combat in (("combatExamples", True), ("noncombatExamples", False)):
        rows = [(capture, owner) for capture, owner in owners if (capture in COMBAT_CAPTURES) == is_combat]
        static_count = sum(owner & STATIC_ACTOR_MASK == STATIC_ACTOR_PREFIX for _, owner in rows)
        retained_rows = [
            (capture, owner)
            for capture, owner in retained_owners
            if (capture in COMBAT_CAPTURES) == is_combat
        ]
        retained_static = sum(
            owner & STATIC_ACTOR_MASK == STATIC_ACTOR_PREFIX
            for _, owner in retained_rows
        )
        scenario_groups[name] = {
            "captures": sorted({capture for capture, _ in rows}),
            "sampleCount": len(rows),
            "staticActorBlockCount": static_count,
            "outsideStaticActorBlockCount": len(rows) - static_count,
            "ownerIdDistribution": _distribution([owner for _, owner in rows]),
            "retainedSampleCap": {
                "sampleCount": len(retained_rows),
                "staticActorBlockCount": retained_static,
                "outsideStaticActorBlockCount": len(retained_rows) - retained_static,
                "ownerIdDistribution": _distribution([owner for _, owner in retained_rows]),
            },
        }

    event_names: dict[str, dict[str, int]] = {}
    for event in event_starts:
        name = str(event["eventName"])
        owner = int(event["ownerActorId"])
        row_id = owner & 0xFFFF
        row = event_names.setdefault(name, {
            "count": 0,
            "staticActorHits": 0,
            "gameCommandHits": 0,
            "outsideStaticActorBlock": 0,
        })
        row["count"] += 1
        if owner & STATIC_ACTOR_MASK == STATIC_ACTOR_PREFIX:
            row["staticActorHits"] += row_id in static_actors
            row["gameCommandHits"] += row_id in command_ids
        else:
            row["outsideStaticActorBlock"] += 1

    command_static_ids = [
        row_id for row_id, class_path in static_actors.items()
        if class_path.startswith("/Command/")
    ]
    observed_command_ids = [row["rowId"] for row in static_rows]
    game_hits = sum(bool(row["gameCommandHit"]) for row in static_rows)
    static_hits = sum(row["classPath"] is not None for row in static_rows)
    command_path_hits = sum(
        isinstance(row["classPath"], str) and row["classPath"].startswith("/Command/")
        for row in static_rows
    )
    non_command_hits = static_hits - command_path_hits

    def mask_sweep(source: list[tuple[str, int]]) -> list[dict[str, int]]:
        rows: list[dict[str, int]] = []
        for bits in range(8, 33):
            mask = (1 << bits) - 1 if bits < 32 else 0xFFFFFFFF
            values = [owner & mask for _, owner in source]
            rows.append({
                "bits": bits,
                "staticActorHits": sum(value in static_actors for value in values),
                "gameCommandHits": sum(value in command_ids for value in values),
            })
        return rows

    return {
        "status": "resolved_owner_static_actor_identity",
        "summary": (
            "For owner IDs in the 0xa0f00000 static-actor block, application payload "
            "offset 0x04 carries a command static-actor identity in the low 16 bits. "
            "This relationship is general to EventStart, not combat-specific. Owners "
            "outside that block remain event-owner actor IDs and do not support the mask."
        ),
        "unresolvedBoundary": (
            "The conditional owner static-actor identity is resolved. Direct propagation "
            "of a gameCommand sheet row, including the separate application offset 0x08 "
            "field, remains unproven; 12 static command-owner occurrences have no "
            "gameCommand row."
        ),
        "sourceSnapshots": {
            "captures": {
                "repository": "XIVLegacy/xivl-captures",
                "commit": _commit(captures_repo),
                "rawCorpusArtifact": "sources/pcap-1.23b/manifest.yaml#members",
                "rawCorpusManifestSha256": _sha256(captures_repo / "sources" / "pcap-1.23b" / "manifest.yaml"),
                "extractorArtifact": "tools/extractors/extract_content_samples.py:73-144",
                "extractorSha256": _sha256(captures_repo / "tools" / "extractors" / "extract_content_samples.py"),
                "retainedSampleArtifact": "derived/payload_samples.json#samples.c2s.0x012d",
                "retainedSampleSha256": _sha256(samples_path),
            },
            "clientData": {
                "repository": "XIVLegacy/xivl-client-data",
                "commit": _commit(client_data_repo),
                "staticActorArtifact": "manifests/staticactor_class_paths.json#records",
                "staticActorSha256": _sha256(actors_path),
                "gameCommandArtifact": "csv/gameCommand.csv column 0",
                "gameCommandSha256": _sha256(commands_path),
            },
        },
        "derivation": {
            "direction": "serverbound",
            "service": "Map (client decomp attribution)",
            "opcodeHex": "0x012d",
            "framing": "216-byte wire subpacket -> 200-byte retained body -> 16-byte game-message prefix -> 184-byte application payload",
            "ownerOffset": "retained body +0x14 = application payload +0x04",
            "ownerDecode": "little-endian u32",
            "staticActorTest": "(ownerActorId & 0xffff0000) == 0xa0f00000",
            "rowDecode": "ownerActorId & 0x0000ffff",
        },
        "distribution": {
            "totalOccurrences": len(owners),
            "ownerIds": _distribution([owner for _, owner in owners]),
            "upper16Blocks": _distribution([owner >> 16 for _, owner in owners], 4),
            "retainedSampleCap": {
                "sampleCount": len(retained_owners),
                "ownerIds": _distribution([owner for _, owner in retained_owners]),
                "upper16Blocks": _distribution([owner >> 16 for _, owner in retained_owners], 4),
            },
        },
        "scenarioComparison": scenario_groups,
        "eventNameComparison": [
            {"eventName": name, **counts}
            for name, counts in sorted(event_names.items())
        ],
        "joins": {
            "eligibleStaticActorSamples": len(static_rows),
            "eligibleUniqueOwnerIds": len({row["ownerActorId"] for row in static_rows}),
            "staticActorHits": static_hits,
            "staticActorMisses": len(static_rows) - static_hits,
            "commandPathHits": command_path_hits,
            "nonCommandStaticActorHits": non_command_hits,
            "gameCommandHits": game_hits,
            "gameCommandMisses": len(static_rows) - game_hits,
            "sampleHitRates": {
                "staticActor": f"{static_hits}/{len(static_rows)}",
                "commandPath": f"{command_path_hits}/{len(static_rows)}",
                "gameCommand": f"{game_hits}/{len(static_rows)}",
            },
            "rows": joined_distribution,
            "retainedSampleCap": {
                "eligibleStaticActorSamples": sum(
                    owner & STATIC_ACTOR_MASK == STATIC_ACTOR_PREFIX
                    for _, owner in retained_owners
                ),
                "staticActorHits": sum(
                    (owner & 0xFFFF) in static_actors
                    for _, owner in retained_owners
                    if owner & STATIC_ACTOR_MASK == STATIC_ACTOR_PREFIX
                ),
                "gameCommandHits": sum(
                    (owner & 0xFFFF) in command_ids
                    for _, owner in retained_owners
                    if owner & STATIC_ACTOR_MASK == STATIC_ACTOR_PREFIX
                ),
            },
        },
        "maskWidth": {
            "verdict": "supports_16_bit_command_static_actor_row_id",
            "observedMaximumRowId": max(observed_command_ids),
            "commandStaticActorMaximumRowId": max(command_static_ids),
            "gameCommandMaximumRowId": max(command_ids),
            "observedOverflowCount": sum(row_id > 0xFFFF for row_id in observed_command_ids),
            "commandStaticActorOverflowCount": sum(row_id > 0xFFFF for row_id in command_static_ids),
            "gameCommandOverflowCount": sum(row_id > 0xFFFF for row_id in command_ids),
            "maskSweep": mask_sweep(owners),
            "retainedMaskSweep": mask_sweep(retained_owners),
            "boundary": (
                "The u32 owner field remains an actor ID. The 16-bit conclusion applies "
                "only after the 0xa0f00000 prefix test and does not truncate other actor IDs."
            ),
        },
        "scriptRoute": {
            "status": "command_object_supplied_as_event_owner",
            "evidence": "xivl-client-scripts:lua/scripts/chara/player/playerbaseclass.lua:1823-1840",
            "finding": (
                "PlayerBaseClass._onCommandEvent obtains getCommandId() from A2_2 and "
                "passes the same A2_2 command object to _callServerOnCommand. The native "
                "bridge preserves an object-owner route; this script fact does not by "
                "itself prove the actor-ID packing."
            ),
        },
        "rejectedValues": [
            "The 0xa0f00000 prefix is a tested partition, not evidence imported from a server reimplementation.",
            "Owners outside the 0xa0f00000 block are not masked into command rows.",
            "A staticactor /Command join does not imply that the row exists in gameCommand; 12 static command-owner occurrences use actors absent from that sheet.",
            "Client-data command names and parameters remain client-side metadata, not server validation semantics.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures-repo", type=Path, required=True)
    parser.add_argument("--client-data-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        out = args.out.resolve()
        manifest = json.loads(out.read_text(encoding="utf-8"))
        relationship = build(
            args.captures_repo.resolve(),
            args.client_data_repo.resolve(),
        )
        if args.check:
            if manifest.get("commandIdRelationship") != relationship:
                print("error: commandIdRelationship does not match fresh evidence", file=sys.stderr)
                return 1
            print("OK: EventStart owner-ID evidence matches the raw corpus and retained sample cap")
            return 0
        manifest["commandIdRelationship"] = relationship
        out.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {relationship['distribution']['totalOccurrences']} owner IDs to {out}")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
