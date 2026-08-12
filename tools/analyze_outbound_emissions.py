#!/usr/bin/env python3
"""Parse the Ghidra ScanOpcodeEmissions output + emit candidate
emitter map for the Lua-name to opcode bridge.

Reads the post-script's output file (path from the BCS_OUTBOUND_SCAN env
var or argv[1]), which records every `MOV [reg+disp], imm` write where imm is a
serverbound opcode. Aggregates by opcode -> distinct containing
functions, joins with the existing operation_opcode_map_outbound.json
and data/vendor/opcodes/opcodes.json metadata, and writes the candidate
emitters per opcode into manifests/operation_opcode_map_overlay.json (the
curated enrichment overlay) rather than the manifest itself.

NOT every hit is a true emitter - many opcodes are also common integer
literals (e.g. opcode 4 = decimal 4, appears in countless unrelated
instructions). Hits per opcode + distinct-function counts let the
reader judge confidence. Hits in functions named like "*Operation*",
"*::send_*", "*Builder*", "*Channel*", or in the existing
retail_class_name annotated set are higher confidence.

Output: manifests/operation_opcode_map_overlay.json (updated in place).
After running this, re-run tools/extract_operation_opcode_map.py to fold
the overlay into manifests/operation_opcode_map_outbound.json.

Run (after the Ghidra batch completes):
    python tools\\analyze_outbound_emissions.py path\\to\\outbound_scan.txt
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# The scan is machine-specific and external. Require BCS_OUTBOUND_SCAN or argv[1].
scan_output_arg = os.environ.get("BCS_OUTBOUND_SCAN") or (
    sys.argv[1] if len(sys.argv) > 1 else None
)
if scan_output_arg is None:
    print(
        "error: set BCS_OUTBOUND_SCAN or pass the scan-output path as argv[1]",
        file=sys.stderr,
    )
    sys.exit(2)
SCAN_OUTPUT = Path(scan_output_arg)
OPCODES_JSON = REPO_ROOT / "data" / "vendor" / "opcodes" / "opcodes.json"
MANIFEST_JSON = REPO_ROOT / "manifests" / "operation_opcode_map_outbound.json"
OVERLAY_JSON = REPO_ROOT / "manifests" / "operation_opcode_map_overlay.json"

# Lines like "  00401222  MOV dword ptr [ESP + 0x1c],0x1   in FUN_004011b0@004011b0"
HIT_RE = re.compile(
    r"^\s+([0-9a-fA-F]+)\s+(.+?)\s+in\s+(\S+)\s*$"
)
# Headline: "=== 0x0004 (decimal 4) - 142 hits, 38 distinct functions ==="
HEADER_RE = re.compile(
    r"^===\s+0x([0-9a-fA-F]+)\s+\(decimal\s+(\d+)\)\s+-\s+(\d+)\s+hits,\s+(\d+)\s+distinct"
)
# Within an insn, the [reg + 0xN] displacement.
DISP_RE = re.compile(r"\[\s*\w+\s*\+\s*0x([0-9a-fA-F]+)\s*\]")


def _parse_scan(path: Path) -> dict[int, list[dict]]:
    """Return { opcodeInt -> [ { va, insn, function, disp } ] }."""
    out: dict[int, list[dict]] = defaultdict(list)
    if not path.is_file():
        print(f"error: {path} missing - run the Ghidra batch first", file=sys.stderr)
        sys.exit(1)
    current_opcode: int | None = None
    with path.open(encoding="utf-8") as f:
        for line in f:
            mh = HEADER_RE.match(line)
            if mh:
                current_opcode = int(mh.group(2))
                continue
            mh2 = HIT_RE.match(line)
            if mh2 and current_opcode is not None:
                insn = mh2.group(2).strip()
                disp_m = DISP_RE.search(insn)
                disp = int(disp_m.group(1), 16) if disp_m else None
                out[current_opcode].append({
                    "va": "0x" + mh2.group(1),
                    "insn": insn,
                    "function": mh2.group(3).strip(),
                    "disp": disp,
                })
    return out


STACK_REG_RE = re.compile(r"\[\s*(ESP|EBP)\s*[+\-]", re.IGNORECASE)
SHORT_DISP_THRESHOLD = 0x40


def _is_high_confidence(hit: dict) -> bool:
    """A hit is high-confidence if it looks like a packet-buffer write:
       - the base register is NOT ESP/EBP (those are stack frames)
       - the displacement is small (<= 0x40)
    """
    insn = hit["insn"]
    if STACK_REG_RE.search(insn):
        return False
    disp = hit.get("disp")
    if disp is None or disp > SHORT_DISP_THRESHOLD:
        return False
    return True


def _summarize_per_function(hits: list[dict],
                            high_conf_only: bool = False) -> dict[str, int]:
    """function name -> hit count for this opcode."""
    counts: dict[str, int] = defaultdict(int)
    for h in hits:
        if high_conf_only and not _is_high_confidence(h):
            continue
        counts[h["function"]] += 1
    return dict(counts)


def _load_existing_manifest() -> dict:
    if MANIFEST_JSON.is_file():
        with MANIFEST_JSON.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_overlay() -> dict:
    if OVERLAY_JSON.is_file():
        with OVERLAY_JSON.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_opcodes_serverbound() -> dict[int, dict]:
    """opcodeInt -> opcode entry from opcodes.json (serverbound only)."""
    with OPCODES_JSON.open(encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, list):
        data = data[0]
    out: dict[int, dict] = {}
    for bucket, ops in data["lists"].items():
        for op in ops:
            if op.get("direction") == "serverbound" and isinstance(op.get("opcode"), int):
                out[op["opcode"]] = {**op, "bucket": bucket}
    return out


def _confidence_for_function(fname: str, hit_count: int,
                             retail_classes: set[str]) -> str:
    """Heuristic confidence tag for a candidate emitter."""
    low = fname.lower()
    for cls in retail_classes:
        if cls.split("::")[-1].lower() in low:
            return "strong"
    keywords = ("operation", "send_", "builder", "channel", "callback",
                "dispatcher", "emit", "pack", "writebody")
    if any(k in low for k in keywords):
        return "strong"
    if hit_count == 1:
        return "candidate"
    return "low"


EMITTER_SCAN_NOTES_APPENDIX = (
    "Added candidateEmitters per serverbound opcode from "
    "a MOV-write-imm scan across the binary. Hit counts and distinct-function "
    "counts indicate confidence; opcodes with low counts that hit "
    "Operation/Builder-named functions are the highest-confidence emitters."
)


def main() -> int:
    hits_by_opcode = _parse_scan(SCAN_OUTPUT)
    serverbound = _load_opcodes_serverbound()
    manifest = _load_existing_manifest()

    retail_classes: set[str] = set()
    for cls_entry in manifest.get("operationClasses", []):
        retail_classes.add(cls_entry.get("retailClass", ""))

    findings: list[dict] = []
    for opcode in sorted(serverbound.keys()):
        op_meta = serverbound[opcode]
        hits = hits_by_opcode.get(opcode, [])
        per_fn = _summarize_per_function(hits)
        per_fn_hc = _summarize_per_function(hits, high_conf_only=True)
        candidates = sorted(per_fn_hc.items(), key=lambda x: -x[1])
        findings.append({
            "opcode": opcode,
            "opcodeHex": f"0x{opcode:04x}",
            "name": op_meta.get("name"),
            "bucket": op_meta["bucket"],
            "existingRetailClass": op_meta.get("retail_class_name"),
            "totalHits": len(hits),
            "totalHighConfidenceHits": sum(
                1 for h in hits if _is_high_confidence(h)
            ),
            "distinctFunctions": len(per_fn),
            "distinctHighConfidenceFunctions": len(per_fn_hc),
            "candidateEmitters": [
                {
                    "function": fname,
                    "hitCount": count,
                    "confidence": _confidence_for_function(
                        fname, count, retail_classes
                    ),
                }
                for fname, count in candidates[:10]
            ],
        })

    emitter_scan = {
        "scanInput": f"XIVL_OPCODE_SET = {len(serverbound)} serverbound opcodes",
        "filter": "MOV with op0=[reg+disp<=64] and op1=imm in target set",
        "totalHits": sum(len(h) for h in hits_by_opcode.values()),
        "opcodesWithHits": sum(1 for o in serverbound if hits_by_opcode.get(o)),
        "opcodesWithoutHits": sum(1 for o in serverbound if not hits_by_opcode.get(o)),
        "perOpcode": findings,
    }

    overlay = _load_overlay()
    overlay.setdefault("_comment",
        "Curated enrichment overlay merged by extract_operation_opcode_map.py.")
    top_sections = overlay.setdefault("topLevelSections", {})
    top_sections["emitterScan"] = emitter_scan
    scan_source_note = "outbound_scan.txt (Ghidra ScanOpcodeEmissions)"
    existing_sources = top_sections.get("sources", "")
    if scan_source_note not in existing_sources:
        top_sections["sources"] = (
            f"{existing_sources} | {scan_source_note}" if existing_sources
            else scan_source_note
        )
    notes_appendices = overlay.setdefault("notesAppendices", [])
    if EMITTER_SCAN_NOTES_APPENDIX not in notes_appendices:
        notes_appendices.append(EMITTER_SCAN_NOTES_APPENDIX)
    overlay.setdefault("totalsExtras", {})
    overlay.setdefault("operationClassSlots", {})
    overlay.setdefault("serverboundGapExtras", {})

    OVERLAY_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OVERLAY_JSON.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(overlay, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"wrote {OVERLAY_JSON}")
    print(f"  total hits across all opcodes: "
          f"{emitter_scan['totalHits']}")
    print(f"  opcodes with at least one hit: "
          f"{emitter_scan['opcodesWithHits']} / {len(serverbound)}")
    print(f"  opcodes with NO hits:          "
          f"{emitter_scan['opcodesWithoutHits']} / {len(serverbound)}")
    print("re-run tools/extract_operation_opcode_map.py to fold this into "
          "manifests/operation_opcode_map_outbound.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
