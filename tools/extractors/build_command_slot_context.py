#!/usr/bin/env python3
"""Join observed command-slot actor IDs to static command identities."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "manifests" / "command_slot_context.json"
PROPERTY_FIELDS = {
    "record_index",
    "capture",
    "lane_index",
    "source_actor_id",
    "property_hash",
    "value_width",
    "value_u_le",
}
STATIC_ACTOR_PREFIX = 0xA0F00000
STATIC_ACTOR_MASK = 0xFFFF0000
ROW_ID_MASK = 0x0000FFFF
EXPECTED_COMMAND_INDICES = frozenset(range(23)) | frozenset(range(32, 45)) | {51}
EXPECTED_CATEGORY_INDICES = {0, 1} | set(range(32, 49)) | {51}
EXPECTED_COMMAND_RECORDS = 394
EXPECTED_CATEGORY_RECORDS = 240


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _commit(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _load_names(path: Path) -> dict[str, str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    names: dict[str, str] = {}
    for row in document["resolved"]:
        if len(row["names"]) != 1:
            continue
        name = row["names"][0]
        if name.startswith("charaWork.command[") or name.startswith(
            "charaWork.commandCategory["
        ) or name == "charaWork.commandBorder":
            names[row["idHex"].lower()] = name
    return names


def _array_index(name: str, prefix: str) -> int:
    if not name.startswith(prefix) or not name.endswith("]"):
        raise ValueError(f"malformed indexed property name {name!r}")
    index = int(name[len(prefix):-1])
    if not 0 <= index < 64:
        raise ValueError(f"command slot index {index} is outside the Lua array")
    return index


def build(captures_repo: Path, client_data_repo: Path) -> dict:
    properties_path = (
        captures_repo
        / "studies/property-stream-hash-catalog/derived/property-records.csv"
    )
    names_path = REPO / "manifests/gam_hash_names.json"
    identity_path = REPO / "manifests/combat_command_emission.json"
    generator_path = Path(__file__).resolve()
    actors_path = client_data_repo / "manifests/staticactor_class_paths.json"
    commands_path = client_data_repo / "derived/command_battle_params.csv"

    names = _load_names(names_path)
    actors_doc = json.loads(actors_path.read_text(encoding="utf-8"))
    actors = {int(row["id"]): row["classPath"] for row in actors_doc["records"]}
    with commands_path.open(encoding="utf-8-sig", newline="") as handle:
        commands = {int(row["id"]): row for row in csv.DictReader(handle)}

    with properties_path.open(encoding="ascii", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not PROPERTY_FIELDS.issubset(reader.fieldnames):
            raise ValueError("property record header is missing required fields")
        source_rows = list(reader)

    states: dict[tuple[str, int, int], dict[int, int]] = defaultdict(dict)
    command_occurrences: Counter[int] = Counter()
    command_slot_occurrences: Counter[tuple[int, int]] = Counter()
    category_values: Counter[int] = Counter()
    command_indices: set[int] = set()
    category_indices: set[int] = set()
    category_hashes: set[str] = set()
    stateful_pairs: Counter[tuple[int, int, int]] = Counter()
    missing_current_command: Counter[int] = Counter()
    command_record_count = 0
    category_record_count = 0
    last_record_index = -1

    for row in source_rows:
        record_index = int(row["record_index"])
        if record_index <= last_record_index:
            raise ValueError("property rows are not in increasing record order")
        last_record_index = record_index
        name = names.get(row["property_hash"].lower())
        if name is None:
            continue
        width = int(row["value_width"])
        value = int(row["value_u_le"])
        lane = (
            row["capture"],
            int(row["lane_index"]),
            int(row["source_actor_id"]),
        )

        if name.startswith("charaWork.command["):
            if width != 4:
                raise ValueError(f"{name} has wire width {width}, expected 4")
            index = _array_index(name, "charaWork.command[")
            command_record_count += 1
            command_indices.add(index)
            states[lane][index] = value
            if value:
                command_occurrences[value] += 1
                command_slot_occurrences[(value, index)] += 1
        elif name.startswith("charaWork.commandCategory["):
            if width != 1:
                raise ValueError(f"{name} has wire width {width}, expected 1")
            index = _array_index(name, "charaWork.commandCategory[")
            category_record_count += 1
            category_indices.add(index)
            category_hashes.add(row["property_hash"].lower())
            category_values[value] += 1
            actor_id = states[lane].get(index)
            if actor_id:
                stateful_pairs[(actor_id, index, value)] += 1
            else:
                missing_current_command[index] += 1

    if (
        command_record_count != EXPECTED_COMMAND_RECORDS
        or category_record_count != EXPECTED_CATEGORY_RECORDS
        or command_indices != EXPECTED_COMMAND_INDICES
        or category_indices != EXPECTED_CATEGORY_INDICES
    ):
        raise ValueError("resolved command/category property coverage drifted")

    joined_rows = []
    prefix_misses = []
    actor_misses = []
    command_misses = []
    for actor_id, occurrences in sorted(command_occurrences.items()):
        if actor_id & STATIC_ACTOR_MASK != STATIC_ACTOR_PREFIX:
            prefix_misses.append(actor_id)
            continue
        command_id = actor_id & ROW_ID_MASK
        class_path = actors.get(command_id)
        command = commands.get(command_id)
        if class_path is None:
            actor_misses.append(actor_id)
        if command is None:
            command_misses.append(actor_id)
        slot_observations = []
        for (candidate, slot), slot_occurrences in sorted(
            command_slot_occurrences.items()
        ):
            if candidate != actor_id:
                continue
            categories = [
                {"value": category, "occurrences": count}
                for (pair_actor, pair_slot, category), count in sorted(
                    stateful_pairs.items()
                )
                if pair_actor == actor_id and pair_slot == slot
            ]
            slot_observations.append(
                {
                    "slot": slot,
                    "commandOccurrences": slot_occurrences,
                    "categoryObservations": categories,
                }
            )
        joined_rows.append(
            {
                "actorIdHex": f"0x{actor_id:08x}",
                "commandId": command_id,
                "classPath": class_path,
                "nameEnglish": command["name_en"] if command else None,
                "commandOccurrences": occurrences,
                "slotObservations": slot_observations,
            }
        )

    if prefix_misses or actor_misses or command_misses:
        raise ValueError(
            "command-slot identity join is incomplete: "
            f"prefix={len(prefix_misses)}, staticActor={len(actor_misses)}, "
            f"command={len(command_misses)}"
        )

    return {
        "schemaVersion": 1,
        "kind": "xivl-command-slot-context",
        "gameVersion": "1.23b",
        "status": "qualified-static-actor-identity-partial-category-observation",
        "sourceSnapshots": {
            "captures": {
                "repository": "XIVLegacy/xivl-captures",
                "commit": _commit(captures_repo),
                "artifact": "studies/property-stream-hash-catalog/derived/property-records.csv",
                "sha256": _sha256(properties_path),
            },
            "clientStructs": {
                "repository": "XIVLegacy/xivl-client-structs",
                "generatorArtifact": "tools/extractors/build_command_slot_context.py",
                "generatorSha256": _sha256(generator_path),
                "hashNamesArtifact": "manifests/gam_hash_names.json",
                "hashNamesSha256": _sha256(names_path),
                "actorIdentityArtifact": "manifests/combat_command_emission.json#commandIdRelationship",
                "actorIdentitySha256": _sha256(identity_path),
            },
            "clientData": {
                "repository": "XIVLegacy/xivl-client-data",
                "commit": _commit(client_data_repo),
                "staticActorArtifact": "manifests/staticactor_class_paths.json",
                "staticActorSha256": _sha256(actors_path),
                "commandCatalogArtifact": "derived/command_battle_params.csv",
                "commandCatalogSha256": _sha256(commands_path),
            },
        },
        "derivation": {
            "carrier": "s2c:0x0137",
            "statePartition": ["capture", "lane_index", "source_actor_id"],
            "stateOrder": "increasing record_index",
            "stateRule": "apply command slot writes in order; join a category write to the current nonzero command actor in the same slot",
            "staticActorTest": "(actorId & 0xffff0000) == 0xa0f00000",
            "commandIdDecode": "actorId & 0x0000ffff",
            "identityBoundary": "the prefix and low-16 transform is proven for qualifying EventStart owner IDs; applying it here is a qualified cross-artifact join over actor-typed command slots with 52/52 static-actor and command-catalog agreement",
        },
        "coverage": {
            "commandRecords": command_record_count,
            "nonzeroCommandOccurrences": sum(command_occurrences.values()),
            "uniqueNonzeroCommandActors": len(command_occurrences),
            "staticActorPrefixHits": len(command_occurrences),
            "staticActorCatalogHits": len(command_occurrences),
            "commandCatalogHits": len(command_occurrences),
            "categoryRecords": category_record_count,
            "categoryHashes": len(category_hashes),
            "categoryValueDistribution": [
                {"value": value, "occurrences": count}
                for value, count in sorted(category_values.items())
            ],
            "statefulCategoryObservations": sum(stateful_pairs.values()),
            "commandsWithCategoryObservations": len(
                {actor_id for actor_id, _, _ in stateful_pairs}
            ),
            "categoryWritesWithoutCurrentCommand": [
                {"slot": slot, "occurrences": count}
                for slot, count in sorted(missing_current_command.items())
            ],
        },
        "rowsSha256": _json_sha256(joined_rows),
        "rows": joined_rows,
        "unresolved": [
            "category 2 is not observed in the retained property corpus",
            "category value 1 has no promoted semantic label",
            "the retained corpus does not establish a complete category domain or assignment policy",
            "the native sync-cache-to-Lua-work-binding bridge remains unresolved",
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
        document = build(args.captures_repo.resolve(), args.client_data_repo.resolve())
        encoded = json.dumps(document, indent=2, ensure_ascii=True) + "\n"
        if args.check:
            if not args.out.is_file() or args.out.read_text(encoding="utf-8") != encoded:
                print(f"error: stale command-slot context: {args.out}", file=sys.stderr)
                return 1
            print("OK: command-slot context matches explicit evidence")
            return 0
        args.out.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"wrote {len(document['rows'])} command-slot rows to {args.out}")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
