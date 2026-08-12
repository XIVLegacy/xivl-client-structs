#!/usr/bin/env python3
"""PCAP validation pass for the s2c bridge bindings.

Explicit-path research command, non-gating: run it against an
operator-named capture corpus via --captures-dir. For each of the 14
distinct opcodes referenced by the 23 confirmed indirect bindings in
`data_dependency_catalog.json`, search the supplied pcap corpus for
observed game-message sub-packets and report which opcodes appear in
which captures.

The parser expects this packet framing:

  BasePacketHeader (16 bytes):
    u8  isAuthenticated
    u8  isCompressed
    u16 connectionType
    u16 packetSize
    u16 numSubpackets
    u64 timestamp

  SubPacketHeader (16 bytes):
    u16 subpacketSize
    u16 type        # 0x03 = game-message
    u32 sourceId
    u32 targetId
    u32 unknown1

  GameMessageHeader (16 bytes, only when subpacket type == 0x03):
    u16 unknown4    # always 0x14
    u16 opcode
    u32 unknown5
    u32 timestamp
    u32 unknown6

The captures are unencrypted 1.x packet captures.
Server-bound traffic flows from RFC 1918 client IP (192.168.1.101) to the
game server; client-bound is the reverse direction.

Direction inference: we tag a stream as `s2c` if the destination IP matches
the RFC 1918 client (192.168.1.101) and `c2s` if the source IP matches it.
This is a heuristic that's robust against capture-direction asymmetry.

Output: stdout report always; the JSON sidecar
`manifests/pcap_validation.json` is (re)written only with `--write`.
Default is validate-only so running it as an audit invariant never mutates the
committed manifest (whose numbers are referenced across downstream ledgers).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from collections import defaultdict
from pathlib import Path

# Defer scapy import so CLI errors remain usable when scapy is unavailable.
try:
    from scapy.all import rdpcap
    from scapy.layers.inet import IP, TCP
    _SCAPY_IMPORT_ERROR: Exception | None = None
except ImportError as exc:  # pragma: no cover - exercised only w/o scapy
    rdpcap = None  # type: ignore[assignment]
    IP = TCP = None  # type: ignore[assignment]
    _SCAPY_IMPORT_ERROR = exc

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "manifests" / "data_dependency_catalog.json"
OPCODE_MAP = REPO_ROOT / "manifests" / "receiver_opcode_map_inbound.json"
OUT_JSON = REPO_ROOT / "manifests" / "pcap_validation.json"

CLIENT_IP = "192.168.1.101"

BASE_HEADER_FMT = "<BBHHHQ"
BASE_HEADER_SIZE = struct.calcsize(BASE_HEADER_FMT)
SUB_HEADER_FMT = "<HHIII"
SUB_HEADER_SIZE = struct.calcsize(SUB_HEADER_FMT)
GAME_HEADER_FMT = "<HHIII"
GAME_HEADER_SIZE = struct.calcsize(GAME_HEADER_FMT)


def reassemble_tcp_streams(pcap_path: Path) -> dict[tuple, bytes]:
    """Return dict keyed by (src_ip, src_port, dst_ip, dst_port) -> reassembled bytes.

    Per-direction reassembly that respects TCP sequence numbers: each
    segment is placed at offset `(seq - initial_seq)` in a pre-sized byte
    buffer. This correctly resolves retransmits, zero-window probes, and
    out-of-order delivery; duplicates that share a TCP SEQ overwrite the
    same offset rather than double-counting.

Ported from `xivl-captures/tools/extractors/extract_streams.py:78-112`
    (`reconstruct()`).
    """
    segs: dict[tuple, list[tuple[int, bytes]]] = defaultdict(list)
    pkts = rdpcap(str(pcap_path))
    for p in pkts:
        if TCP not in p or IP not in p:
            continue
        if not p[TCP].payload:
            continue
        payload = bytes(p[TCP].payload)
        if not payload:
            continue
        key = (p[IP].src, p[TCP].sport, p[IP].dst, p[TCP].dport)
        segs[key].append((p[TCP].seq, payload))
    streams: dict[tuple, bytes] = {}
    for key, items in segs.items():
        items.sort(key=lambda x: x[0])
        initial_seq = items[0][0]
        max_end = max(seq + len(payload) - initial_seq for seq, payload in items)
        buf = bytearray(max_end)
        for seq, payload in items:
            offset = seq - initial_seq
            buf[offset:offset + len(payload)] = payload
        streams[key] = bytes(buf)
    return streams


def parse_base_packets(stream: bytes) -> list[tuple[bool, bytes, int]]:
    """Yield (isCompressed, body_bytes, packetSize) tuples from a stream.

    Walks forward. When a header looks invalid, advances by 1 byte and tries
    again (resync) rather than stopping. Real BasePacket boundaries are
    distinctive enough (isAuth/isComp both in [0,1], plausible packetSize,
    bounded numSubpackets) that false positives are rare.
    """
    out = []
    i = 0
    n = len(stream)
    while i + BASE_HEADER_SIZE <= n:
        try:
            (is_auth, is_comp, conn_type, pkt_size,
             num_sub, ts) = struct.unpack_from(BASE_HEADER_FMT, stream, i)
        except struct.error:
            break
        valid = (
            BASE_HEADER_SIZE <= pkt_size <= 0x40000
            and is_comp in (0, 1)
            and is_auth in (0, 1)
            and num_sub <= 1024
            and i + pkt_size <= n
        )
        if not valid:
            i += 1
            continue
        body = stream[i + BASE_HEADER_SIZE: i + pkt_size]
        out.append((is_comp == 1, body, pkt_size))
        i += pkt_size
    return out


def parse_subpackets(body: bytes) -> list[tuple[int, int]]:
    """Yield (subpacket_type, opcode_or_none) for each subpacket in the body."""
    out = []
    i = 0
    n = len(body)
    while i + SUB_HEADER_SIZE <= n:
        try:
            (sub_size, sub_type, src_id, tgt_id,
             unk1) = struct.unpack_from(SUB_HEADER_FMT, body, i)
        except struct.error:
            break
        if sub_size < SUB_HEADER_SIZE or i + sub_size > n:
            break
        opcode = None
        if sub_type == 0x03 and i + SUB_HEADER_SIZE + GAME_HEADER_SIZE <= n:
            (_unk4, opcode, _unk5, _ts,
             _unk6) = struct.unpack_from(
                 GAME_HEADER_FMT, body, i + SUB_HEADER_SIZE)
        out.append((sub_type, opcode))
        i += sub_size
    return out


def extract_opcodes(pcap_path: Path) -> dict[str, dict]:
    """Per pcap: { 's2c': {opcode: count}, 'c2s': {opcode: count}, 'errors': int }."""
    result = {
        "s2c": defaultdict(int),
        "c2s": defaultdict(int),
        "errors": 0,
        "streams": 0,
        "basePackets": 0,
        "gameMessageSubpackets": 0,
        "subpackets": 0,
        "compressedSkipped": 0,
    }
    streams = reassemble_tcp_streams(pcap_path)
    result["streams"] = len(streams)
    for (src_ip, src_port, dst_ip, dst_port), payload in streams.items():
        if src_ip == CLIENT_IP:
            direction = "c2s"
        elif dst_ip == CLIENT_IP:
            direction = "s2c"
        else:
            continue

        for is_comp, body, pkt_size in parse_base_packets(payload):
            result["basePackets"] += 1
            if is_comp:
                # Accept both raw-deflate and zlib-wrapped payloads.
                try:
                    body = zlib.decompress(body)
                except zlib.error:
                    try:
                        body = zlib.decompress(body, -15)  # raw deflate
                    except zlib.error:
                        result["compressedSkipped"] += 1
                        continue
            subs = parse_subpackets(body)
            result["subpackets"] += len(subs)
            for sub_type, opcode in subs:
                if sub_type == 0x03 and opcode is not None:
                    result["gameMessageSubpackets"] += 1
                    result[direction][opcode] += 1
    result["s2c"] = dict(result["s2c"])
    result["c2s"] = dict(result["c2s"])
    return result


def _inbound_opcodes(rcv_map: dict) -> set[int]:
    """Collect every opcode carried by the map's confirmed inbound receivers.

    Schema is ``inboundReceivers[].opcodes[]`` with each opcode an
    ``{opcodeInt, opcodeHex}`` pair; a receiver may carry several.
    """
    out: set[int] = set()
    for rcv in rcv_map.get("inboundReceivers", []):
        for opc in rcv.get("opcodes", []):
            n = opc.get("opcodeInt")
            if isinstance(n, int):
                out.add(n)
                continue
            hexs = opc.get("opcodeHex")
            if isinstance(hexs, str):
                try:
                    out.add(int(hexs, 16))
                except ValueError:
                    pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--captures-dir", type=Path, required=True,
        help="path to the pcap capture corpus to scan (operator-supplied; "
             "no default). Expects *.pcapng files.")
    ap.add_argument(
        "--write", action="store_true",
        help="regenerate the committed manifests/pcap_validation.json "
             "sidecar; default is validate-only (no file writes). Its numbers "
             "are referenced across downstream ledgers - regenerate only when "
             "deliberately refreshing the corpus scan.")
    args = ap.parse_args()

    if _SCAPY_IMPORT_ERROR is not None:
        print(f"ERROR: scapy import failed: {_SCAPY_IMPORT_ERROR}", file=sys.stderr)
        return 2

    pcap_dir: Path = args.captures_dir
    # sourceCorpusDir is curated provenance (an immutable citation of the
    # canonical corpus), never the operator's local path. Preserve the
    # committed value on rewrite; update it manually if the corpus changes.
    pcap_dir_source = "(unrecorded corpus provenance - set manually)"
    if OUT_JSON.is_file():
        try:
            prev_source = json.load(OUT_JSON.open(encoding="utf-8")).get("sourceCorpusDir")
            if prev_source:
                pcap_dir_source = prev_source
        except (OSError, json.JSONDecodeError):
            pass

    cat = json.load(CATALOG.open(encoding="utf-8"))
    bindings = cat.get("confirmedIndirectBindings", [])
    bridge_opcodes: set[int] = set()
    for b in bindings:
        opc_str = b.get("writingOpcode") or b.get("opcode")
        if opc_str:
            bridge_opcodes.add(int(opc_str, 16))
    print(f"validating {len(bridge_opcodes)} distinct bridge opcodes: "
          f"{[f'0x{o:04x}' for o in sorted(bridge_opcodes)]}")

    inbound_opcodes = _inbound_opcodes(json.load(OPCODE_MAP.open(encoding="utf-8")))
    if not inbound_opcodes:
        print(f"ERROR: no inbound opcodes parsed from {OPCODE_MAP.name}; "
              "the receiver-map schema has changed", file=sys.stderr)
        return 2

    if not pcap_dir.is_dir():
        print(f"ERROR: pcap corpus not found: {pcap_dir}", file=sys.stderr)
        return 2
    pcaps = sorted(pcap_dir.glob("*.pcapng"))
    if not pcaps:
        print(f"ERROR: no .pcapng files in {pcap_dir}", file=sys.stderr)
        return 2
    print(f"scanning {len(pcaps)} pcaps in {pcap_dir}")
    per_pcap: dict[str, dict] = {}
    s2c_global: dict[int, int] = defaultdict(int)
    c2s_global: dict[int, int] = defaultdict(int)
    s2c_witnesses: dict[int, list[str]] = defaultdict(list)
    for p in pcaps:
        try:
            res = extract_opcodes(p)
        except Exception as e:
            print(f"  {p.name}: ERROR {e}")
            per_pcap[p.name] = {"error": str(e)}
            continue
        per_pcap[p.name] = res
        for o, c in res["s2c"].items():
            s2c_global[o] += c
            if o in bridge_opcodes:
                s2c_witnesses[o].append(p.name)
        for o, c in res["c2s"].items():
            c2s_global[o] += c

    failed = [n for n, r in per_pcap.items() if r.get("error")]
    if len(failed) == len(pcaps):
        print(f"ERROR: all {len(pcaps)} captures failed to parse; "
              "nothing was validated", file=sys.stderr)
        return 1

    bridge_observed = {o for o in bridge_opcodes if o in s2c_global}
    bridge_missing = bridge_opcodes - bridge_observed
    inbound_observed = {o for o in inbound_opcodes if o in s2c_global}

    print()
    print(f"=== Bridge opcode validation ({len(bridge_opcodes)} opcodes) ===")
    for o in sorted(bridge_opcodes):
        cnt = s2c_global.get(o, 0)
        wits = s2c_witnesses.get(o, [])
        mark = "OBSERVED" if cnt else "MISSING "
        print(f"  [{mark}] 0x{o:04x}  count={cnt:4d}  "
              f"captures={len(wits)}/{len(pcaps)}  "
              f"sample={','.join(wits[:3])}")

    print()
    print("=== Summary ===")
    print(f"  bridge opcodes total:        {len(bridge_opcodes)}")
    print(f"  bridge opcodes OBSERVED s2c: {len(bridge_observed)}")
    print(f"  bridge opcodes MISSING  s2c: {len(bridge_missing)}")
    print(f"  all inbound opcodes total:   {len(inbound_opcodes)}")
    print(f"  all inbound opcodes OBSERVED:{len(inbound_observed)}")
    if failed:
        print(f"  captures that FAILED parse:  {len(failed)}/{len(pcaps)}")
    print(f"  distinct s2c opcodes seen:   {len(s2c_global)}")
    print(f"  distinct c2s opcodes seen:   {len(c2s_global)}")

    out = {
        "version": "1",
        "gameVersion": "1.23b",
        "method": (
            "Static PCAP scan: TCP-reassembled BasePacket/SubPacket parse "
            "across 54 unencrypted 1.x captures. Direction tagged by client "
            f"IP {CLIENT_IP}. Game-message subpackets (type 0x03) are the "
            "validation unit."
        ),
        "sourceCorpusDir": pcap_dir_source,
        "bridgeOpcodes": [f"0x{o:04x}" for o in sorted(bridge_opcodes)],
        "bridgeOpcodesObservedS2C": [f"0x{o:04x}" for o in sorted(bridge_observed)],
        "bridgeOpcodesMissingS2C": [f"0x{o:04x}" for o in sorted(bridge_missing)],
        "s2cOpcodeHistogram": {f"0x{o:04x}": c for o, c in sorted(s2c_global.items())},
        "c2sOpcodeHistogram": {f"0x{o:04x}": c for o, c in sorted(c2s_global.items())},
        "bridgeWitnesses": {
            f"0x{o:04x}": sorted(set(s2c_witnesses[o]))
            for o in sorted(bridge_observed)
        },
        "perPcap": {
            name: {
                "s2c": {f"0x{o:04x}": c for o, c in sorted(res.get("s2c", {}).items())},
                "c2s": {f"0x{o:04x}": c for o, c in sorted(res.get("c2s", {}).items())},
                "streams": res.get("streams", 0),
                "basePackets": res.get("basePackets", 0),
                "subpackets": res.get("subpackets", 0),
                "gameMessageSubpackets": res.get("gameMessageSubpackets", 0),
                "compressedSkipped": res.get("compressedSkipped", 0),
                "error": res.get("error"),
            }
            for name, res in per_pcap.items()
        },
    }
    if args.write:
        OUT_JSON.write_text(
            json.dumps(out, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
        print(f"\nwrote {OUT_JSON}")
        print(f"  sourceCorpusDir kept as: {pcap_dir_source}")
        print("  (curated provenance - edit it manually if this run used a "
              "different corpus)")
    else:
        print(f"\n(validate-only; pass --write to regenerate {OUT_JSON.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
