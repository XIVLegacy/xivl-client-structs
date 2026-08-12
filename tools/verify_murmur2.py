#!/usr/bin/env python3
"""Verify the 1.x client's backward-walking MurmurHash2 against pcap evidence.

Cross-checks:
    1. The six embedded known test vectors.
    2. The 263 resolved (idHex, name) pairs established in
       manifests/gam_hash_names.json.
    3. The first 4 bytes of every s2c 0x0137 sample in the vendored fixture
       data/vendor/captures/payload_samples.json,
       which are the SetActorPropertyPacket property id.

Usage:
    python tools\\verify_murmur2.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MASK32 = 0xFFFFFFFF
M = 0x5BD1E995
R = 24


def murmur2_backward(key: bytes, seed: int = 0) -> int:
    """1.x client variant of MurmurHash2, backward main loop, big-endian k.

    The main loop consumes 4-byte chunks from the end of the input. The tail
    is the unprocessed prefix at the start of the input.
    """
    length = len(key)
    h = (seed ^ length) & MASK32

    end = length
    while end >= 4:
        k = (
            (key[end - 4] << 24)
            | (key[end - 3] << 16)
            | (key[end - 2] << 8)
            | key[end - 1]
        ) & MASK32
        k = (k * M) & MASK32
        k ^= k >> R
        k = (k * M) & MASK32
        h = (h * M) & MASK32
        h ^= k
        h &= MASK32
        end -= 4

    # The tail length is end, and tail bytes are read from the input start.
    if end == 3:
        h ^= key[0] << 16
        h ^= key[1] << 8
        h ^= key[2]
        h = (h * M) & MASK32
    elif end == 2:
        h ^= key[0] << 8
        h ^= key[1]
        h = (h * M) & MASK32
    elif end == 1:
        h ^= key[0]
        h = (h * M) & MASK32

    h ^= h >> 13
    h = (h * M) & MASK32
    h ^= h >> 15
    return h & MASK32


TEST_VECTORS = [
    ("", 0x00000000),
    ("a", 0x92685F5E),
    ("hello", 0x08C5DAA9),
    ("charaWork.parameterSave.hp[0]", 0x4232BCAA),
    ("playerWork.activeQuest", 0x40E82419),
    ("/_init", 0x05C4C6B7),
]


def check_test_vectors() -> tuple[int, int]:
    matched = 0
    total = len(TEST_VECTORS)
    print("Embedded test vectors:")
    for s, expected in TEST_VECTORS:
        got = murmur2_backward(s.encode("ascii"))
        ok = got == expected
        matched += int(ok)
        marker = "OK " if ok else "FAIL"
        print(f"  [{marker}] {s!r:40s}  expected=0x{expected:08x}  got=0x{got:08x}")
    print(f"  Result: {matched}/{total} matched\n")
    return matched, total


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "manifests" / "structs.json").exists():
            return parent
    raise SystemExit(f"Could not locate xivl-client-structs root from {start}")


def check_resolved_names(gam_hash_names: dict) -> tuple[int, int, list]:
    matched = 0
    total = 0
    mismatches: list[tuple[str, str, str]] = []
    for entry in gam_hash_names["resolved"]:
        id_hex = entry["idHex"]
        expected = int(id_hex, 16)
        for name in entry["names"]:
            total += 1
            got = murmur2_backward(name.encode("ascii"))
            if got == expected:
                matched += 1
            else:
                mismatches.append((name, id_hex, f"0x{got:08x}"))
    return matched, total, mismatches


def check_payload_ids(payload_samples: dict, resolved_ids: set[int]) -> dict:
    """For every s2c 0x0137 sample, the first property-id is at byte 0x12 (18)
    little-endian. The two bytes at 0x10..0x11 are a per-record preamble
    (a property-type tag; not Murmur2-hashed). Confirm each id is in the
    resolved set.
    """
    bucket = payload_samples["samples"]["s2c"].get("0x0137")
    if bucket is None:
        return {"checked": 0, "in_resolved": 0, "missing_ids": []}
    PROP_ID_OFFSET = 0x12
    checked = 0
    in_resolved = 0
    missing: list[str] = []
    for s in bucket["samples"]:
        raw = bytes.fromhex(s["bytes"])
        if len(raw) < PROP_ID_OFFSET + 4:
            continue
        prop_id_le = int.from_bytes(raw[PROP_ID_OFFSET : PROP_ID_OFFSET + 4], "little")
        checked += 1
        if prop_id_le in resolved_ids:
            in_resolved += 1
        else:
            preamble = raw[0x10:0x12].hex()
            missing.append(
                f"capture={s['capture']} sub_size={s['sub_size']} "
                f"preamble=0x{preamble} id_le=0x{prop_id_le:08x}"
            )
    return {"checked": checked, "in_resolved": in_resolved, "missing_ids": missing}


def main() -> int:
    root = find_repo_root(Path(__file__).parent)
    gam_hash_path = root / "manifests" / "gam_hash_names.json"
    payload_path = root / "data" / "vendor" / "captures" / "payload_samples.json"

    tv_ok, tv_total = check_test_vectors()
    all_pass = tv_ok == tv_total

    if not gam_hash_path.exists():
        print(f"ERROR: {gam_hash_path} missing - first-party hash-name "
              "dataset required.", file=sys.stderr)
        return 2

    with gam_hash_path.open("r", encoding="utf-8") as f:
        gam_hash_names = json.load(f)

    matched, total, mismatches = check_resolved_names(gam_hash_names)
    print("Resolved (id, name) pairs from manifests/gam_hash_names.json:")
    print(f"  Matched: {matched}/{total}")
    if mismatches:
        print("  Mismatches (showing first 10):")
        for name, expected, got in mismatches[:10]:
            print(f"    name={name!r:50s} expected={expected} got={got}")
        all_pass = False
    print()

    if not payload_path.exists():
        print(f"ERROR: {payload_path} missing - vendored fixture required. "
              f"See tools/refresh_vendor.py to refresh it.", file=sys.stderr)
        return 2

    with payload_path.open("r", encoding="utf-8") as f:
        payload_samples = json.load(f)

    resolved_ids = {int(entry["idHex"], 16) for entry in gam_hash_names["resolved"]}
    payload_result = check_payload_ids(payload_samples, resolved_ids)
    print("s2c 0x0137 payload property-id check:")
    print(f"  Checked: {payload_result['checked']} samples")
    print(f"  In resolved set: {payload_result['in_resolved']}")
    if payload_result["missing_ids"]:
        print("  Missing ids (showing first 10):")
        for line in payload_result["missing_ids"][:10]:
            print(f"    {line}")
        all_pass = False
    print()

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
