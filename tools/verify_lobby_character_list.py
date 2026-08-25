#!/usr/bin/env python3
"""Validate or reproduce the sanitized lobby character-list fixture."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import ipaddress
import json
import re
import struct
import sys
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "manifests/lobby_character_list_capture_correlation.json"
SOURCE_SHA256 = "28e06b54fe559870031f077f8549b9244caafa7e5177dbca08a7feae6c2b1b62"
FORMAT = "xivl-lobby-character-list-correlation-v1"
REDACTED_CLASSES = [
    "raw payload bytes",
    "character and session names",
    "tickets, tokens, and cryptographic material",
    "network addresses and ports",
    "pointer-like and opaque scalar values",
]
HEX_SECRET_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{32,}(?![0-9a-f])")
IPV4_RE = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")


def _expected_fixture() -> dict:
    return {
        "format": FORMAT,
        "source": {
            "id": "pcap-1.23b",
            "artifact": "login.pcapng",
            "sha256": SOURCE_SHA256,
            "retainedSessionCount": 2,
        },
        "sessions": [
            {"id": "session-a", "characterListOccurrenceCount": 0},
            {"id": "session-b", "characterListOccurrenceCount": 1},
        ],
        "characterList": {
            "direction": "s2c",
            "opcode": 13,
            "clearSubrecordType": 3,
            "occurrenceCount": 1,
            "subrecordLength": 976,
            "packetHeaderLength": 16,
            "bodyLength": 944,
            "entryStride": 464,
            "entryCapacityFromBodyLength": 2,
            "recordCountReadByClient": 1,
            "unusedCapacityEntryIsZero": True,
            "controlFlags": {
                "upperSevenBitsAreZero": True,
                "returnControlBitIsSet": True,
            },
            "record": {
                "slotKeyUpperBitsAreZero": True,
                "appendCStringTerminatesWithinRecordWindow": True,
                "appendCStringTerminatesWithinCopySource": True,
                "copySourceFitsBody": True,
            },
        },
        "comparison": {
            "type000dComparableAcrossSessions": False,
            "reason": "opcode 0x000D occurs only in deterministic session-b; labels do not assert chronology",
            "bothType3SequencesBeginWithOpcode000c": True,
        },
        "redactedClasses": REDACTED_CLASSES,
    }


def _all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _validate_sanitization(fixture: dict) -> None:
    forbidden_keys = {"payload", "payloadHex", "plaintext", "key", "ticket", "token", "address"}

    def walk(value) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in forbidden_keys:
                    raise ValueError(f"fixture contains forbidden sensitive key: {key}")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(fixture)
    for text in _all_strings(fixture):
        if not text.isascii():
            raise ValueError("fixture contains non-ASCII text")
        if any(ord(character) < 0x20 and character not in "\t\n\r" for character in text):
            raise ValueError("fixture contains a C0 control character")
        if HEX_SECRET_RE.search(text) and text != SOURCE_SHA256:
            raise ValueError("fixture contains a token-like hexadecimal string")
        for candidate in IPV4_RE.findall(text):
            try:
                ipaddress.ip_address(candidate)
            except ValueError:
                continue
            raise ValueError("fixture contains an IPv4 address")


def validate_fixture(fixture: dict) -> None:
    _validate_sanitization(fixture)
    if fixture != _expected_fixture():
        raise ValueError("lobby character-list fixture shape changed")


def _normalized_key(client_number: int, credential: bytes) -> bytes:
    if len(credential) != 16:
        raise ValueError("login credential extent changed")
    material = struct.pack("<III", 0x12345678, client_number, 1000)
    material += credential + bytes(16)
    digest = hashlib.md5(material).digest()
    normalized = bytearray()
    for offset in range(0, len(digest), 4):
        word = 0
        for value in digest[offset : offset + 4]:
            signed = value if value < 0x80 else value - 0x100
            word = ((word << 8) | (signed & 0xFFFFFFFF)) & 0xFFFFFFFF
        normalized.extend(word.to_bytes(4, "big"))
    return bytes(normalized)


def _decrypt(payload: bytes, client_number: int, credential: bytes) -> bytes:
    try:
        from Crypto.Cipher import Blowfish
    except ImportError as exc:
        raise RuntimeError("PyCryptodome is required for restricted reproduction") from exc
    cipher = Blowfish.new(_normalized_key(client_number, credential), Blowfish.MODE_ECB)
    output = bytearray()
    for offset in range(0, len(payload), 8):
        block = payload[offset : offset + 8]
        swapped = block[:4][::-1] + block[4:][::-1]
        clear = cipher.decrypt(swapped)
        output.extend(clear[:4][::-1] + clear[4:][::-1])
    return bytes(output)


def _reconstruct_connections(source: Path) -> list[dict]:
    try:
        warnings.filterwarnings("ignore")
        from scapy.all import IP, TCP, rdpcap
    except ImportError as exc:
        raise RuntimeError("Scapy is required for restricted reproduction") from exc

    grouped: dict[tuple, list[tuple[tuple, int, bytes]]] = defaultdict(list)
    for packet in rdpcap(str(source)):
        if not packet.haslayer(IP) or not packet.haslayer(TCP):
            continue
        payload = bytes(packet[TCP].payload)
        if not payload:
            continue
        source_endpoint = (packet[IP].src, packet[TCP].sport)
        destination_endpoint = (packet[IP].dst, packet[TCP].dport)
        key = tuple(sorted((source_endpoint, destination_endpoint)))
        grouped[key].append((source_endpoint, packet[TCP].seq, payload))

    sessions = []
    for endpoints, segments in sorted(grouped.items()):
        server = next((endpoint for endpoint in endpoints if endpoint[1] == 54994), None)
        if server is None:
            continue
        streams = {}
        for direction in ("c2s", "s2c"):
            selected = [
                (sequence, payload)
                for source_endpoint, sequence, payload in segments
                if (source_endpoint == server) == (direction == "s2c")
            ]
            selected.sort(key=lambda item: item[0])
            initial = selected[0][0]
            buffer = bytearray(max(sequence + len(payload) - initial for sequence, payload in selected))
            for sequence, payload in selected:
                start = sequence - initial
                buffer[start : start + len(payload)] = payload
            clean_length = 0
            while clean_length + 16 <= len(buffer):
                frame_length = struct.unpack_from("<H", buffer, clean_length + 4)[0]
                if frame_length < 16 or clean_length + frame_length > len(buffer):
                    break
                clean_length += frame_length
            streams[direction] = bytes(buffer[:clean_length])
        sessions.append(streams)
    return sessions


def _decrypted_type3_records(
    stream: bytes, client_number: int, credential: bytes
) -> list[bytes]:
    records = []
    frame_offset = 0
    while frame_offset < len(stream):
        if frame_offset + 16 > len(stream):
            raise ValueError("stream ends inside an outer header")
        frame_length, subrecord_count = struct.unpack_from("<HH", stream, frame_offset + 4)
        if frame_length < 16 or frame_offset + frame_length > len(stream):
            raise ValueError("stream ends inside an outer frame")
        cursor = frame_offset + 16
        for _ in range(subrecord_count):
            declared_length, clear_type = struct.unpack_from("<HH", stream, cursor)
            if declared_length < 16 or cursor + declared_length > frame_offset + frame_length:
                raise ValueError("outer frame ends inside a subrecord")
            payload = stream[cursor + 16 : cursor + declared_length]
            if clear_type == 3:
                encrypted_length = len(payload) & 0xFFE0
                plaintext = (
                    _decrypt(payload[:encrypted_length], client_number, credential)
                    + payload[encrypted_length:]
                )
                records.append(plaintext)
            cursor += declared_length
        if cursor != frame_offset + frame_length:
            raise ValueError("subrecords do not cover their outer frame")
        frame_offset += frame_length
    return records


def build_fixture(captures_repo: Path) -> dict:
    source = captures_repo / "sources/pcap-1.23b/objects/login.pcapng"
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("login.pcapng identity mismatch")
    sessions = _reconstruct_connections(source)
    if len(sessions) != 2:
        raise ValueError("expected two retained lobby sessions")

    occurrences = []
    per_session_counts = []
    opcode_sequences = []
    for streams in sessions:
        client_number = struct.unpack_from("<I", streams["c2s"], 0x84)[0]
        credential = streams["c2s"][0x44:0x54]
        records = _decrypted_type3_records(
            streams["s2c"], client_number, credential
        )
        opcodes = [struct.unpack_from("<H", record, 2)[0] for record in records]
        opcode_sequences.append(opcodes)
        selected = [record for record, opcode in zip(records, opcodes) if opcode == 0x000D]
        per_session_counts.append(len(selected))
        occurrences.extend(selected)
    if per_session_counts != [0, 1]:
        raise ValueError("type 0x000D occurrence boundary changed")
    if any(not opcodes or opcodes[0] != 0x000C for opcodes in opcode_sequences):
        raise ValueError("shared pre-character-list opcode boundary changed")

    packet = occurrences[0]
    body = packet[16:]
    if len(packet) != 960:
        raise ValueError("type 0x000D wire length changed")
    count = body[9]
    if count != 1:
        raise ValueError("type 0x000D record count changed")
    entry_capacity = (len(body) - 16) // 0x1D0
    unused = body[16 + count * 0x1D0 : 16 + entry_capacity * 0x1D0]
    record = body[:0x1D0]
    append_start = 0x50
    terminator = record.find(0, append_start)
    if terminator < append_start:
        raise ValueError("append C string lacks a terminator in the record window")

    fixture = _expected_fixture()
    observed = fixture["characterList"]
    observed["entryCapacityFromBodyLength"] = entry_capacity
    observed["unusedCapacityEntryIsZero"] = bool(unused) and not any(unused)
    observed["controlFlags"] = {
        "upperSevenBitsAreZero": (body[8] & 0xFE) == 0,
        "returnControlBitIsSet": (body[8] & 1) == 1,
    }
    observed["record"] = {
        "slotKeyUpperBitsAreZero": (record[0x18] & 0xC0) == 0,
        "appendCStringTerminatesWithinRecordWindow": terminator < 0x1D0,
        "appendCStringTerminatesWithinCopySource": terminator < 0x1E0,
        "copySourceFitsBody": len(body) >= 0x10 + 0x1D0,
    }
    validate_fixture(fixture)
    return fixture


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures-repo", type=Path, help="explicit xivl-captures checkout")
    parser.add_argument("--write", action="store_true", help="write the reproduced fixture")
    args = parser.parse_args()

    committed = json.loads(FIXTURE.read_text(encoding="utf-8"))
    validate_fixture(committed)
    if args.captures_repo is None:
        if args.write:
            parser.error("--write requires --captures-repo")
        print("lobby character-list fixture: public shape valid")
        return 0

    reproduced = build_fixture(args.captures_repo)
    rendered = json.dumps(reproduced, indent=2, sort_keys=True) + "\n"
    if args.write:
        FIXTURE.write_text(rendered, encoding="utf-8", newline="\n")
        print("lobby character-list fixture: wrote sanitized reproduction")
        return 0
    if FIXTURE.read_text(encoding="utf-8") != rendered:
        print("lobby character-list fixture: deterministic regeneration drift", file=sys.stderr)
        return 1
    print("lobby character-list fixture: restricted reproduction matched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
