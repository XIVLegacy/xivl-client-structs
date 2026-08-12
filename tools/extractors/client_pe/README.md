# Client PE Toolkit

## What it is

A stdlib-only Python toolkit that reads `ffxivgame.exe` directly (no
Ghidra, no IDA, no disassembler library), scans the PE byte-by-byte
for RTTI markers + MSVC opcode patterns, and emits class catalogs,
vtable layouts, struct field extractions, and string xrefs.

## Role

These standalone CLI extractors need no Ghidra: the RTTI extractor walks the
whole class catalog in one raw PE read. Interactive analysis uses the
headless workflow under `tools/ghidra/` (`analyzeHeadless` plus Java scripts).

xivl-client-structs already has parallel surfaces under
`tools/ghidra/` (analyzeHeadless + Java scripts) and
`manifests/symbols.json` (the curated BCS-Y catalog). These client PE
tools are **additive**: fast bulk extraction without Ghidra startup
cost, especially for new-class discovery or struct-shape sanity
checks.

## Audited output quality

The reliability audit re-ran `--rtti` against the retail executable and
diffed it against the Ghidra COL-walk in the gitignored local
`manifests/rtti_extraction_OUR.txt` dump:

- 3877 rows here against the COL-walk's 5623, intersecting on 3874
  vftable VAs (3 pe-only, 1749 ours-only);
- every vftable VA, slot count and TypeDescriptor spot-checked by
  that audit agreed;
- but 1318 of the 3874 shared rows (34%) disagree on the demangled
  name, 1311 of them templated or function-local forms that the
  hand-rolled demangler garbles.

So: trust the addresses, slot counts and TypeDescriptors. Treat a
demangled name from this tool as a lead and confirm it against a
freshly regenerated `manifests/rtti_extraction_OUR.txt`. This local dump is
gitignored; regenerate it via `tools/extractors/client_pe` before it reaches
the catalog.

## Usage

```powershell
# from xivl-client-structs root
$clientExe = $env:FFXIV_CLIENT_EXE
python -m tools.extractors.client_pe --exe $clientExe --rtti
python -m tools.extractors.client_pe --exe $clientExe --imports
python -m tools.extractors.client_pe --exe $clientExe --search Receiver
python -m tools.extractors.client_pe --exe $clientExe --vtable CharaActor
python -m tools.extractors.client_pe --exe $clientExe --vtfuncs CharaActor
python -m tools.extractors.client_pe --exe $clientExe --analyze CharaActor
python -m tools.extractors.client_pe --exe $clientExe --hierarchy CharaActor
python -m tools.extractors.client_pe --exe $clientExe --strings CharaActor
python -m tools.extractors.client_pe --exe $clientExe --findstr "rlrq5"
```

Outputs land in the current working directory:
- `ffxiv_1.0_rtti.txt` (the full dump)
- `ffxiv_1.0_imports.txt`
- `vtable_<class>.txt`, `vtfuncs_<class>.txt`, `struct_<class>.txt`,
  `hierarchy_<class>.txt`, `strings_<class>.txt`

## Confidence levels per surface

| Tool | Algorithm | Confidence |
|------|-----------|------------|
| `rtti_dumper` | RTTI walk via `.?AV` markers -> TypeDescriptor -> COL -> vtable | H for VA / slot count / TypeDescriptor; L for the demangled name on templated and function-local classes (34% of shared rows disagree with the COL-walk - see the audited-output section above) |
| `vtable_analyzer` | RET/RET-imm16/INT3 + prologue pattern detection | H - byte-pattern only, no disasm needed |
| `import_table_dumper` | PE optional-header import directory walker | H - standard PE format |
| `string_extractor` | PUSH imm32 / MOV reg, imm32 / MOV [mem], imm32 scan | M - limited opcode coverage |
| `struct_analyzer` | MOV imm/reg + LEA+CALL pattern scan in ctor body | M - byte-pattern only; misses LEA-store-via-EAX patterns and instructions that use SIB byte. Sufficient for keystone structs (CharaActor etc.) but may under-report on complex constructors |

`struct_analyzer` is the only one with a meaningful precision gap vs
Ghidra-driven extraction. For field-offset claims, prefer
the Ghidra workflow at `tools/ghidra/*.java`; use this as a fast
first pass.

## File layout

```
client_pe/
  __init__.py              shared PE constants
  __main__.py              CLI dispatcher
  rtti_dumper.py           RTTI extractor
  vtable_analyzer.py       vtable analyzer
  import_table_dumper.py   import-table extractor
  string_extractor.py      string-reference extractor
  struct_analyzer.py       struct-pattern analyzer
  README.md                this file
```

## Integration with xivl-client-structs

Nothing this tool has emitted is in the catalog today, and a raw dump
row is not promotable on its own. To evaluate a candidate:

1. Run `python -m tools.extractors.client_pe --rtti` against your local
   `ffxivgame.exe` to produce a fresh dump.
2. Diff against `manifests/symbols.json` by mangled name.
3. For each candidate, take the class name from a locally regenerated
   `manifests/rtti_extraction_OUR.txt` (gitignored dump; regenerate
   via `tools/extractors/client_pe`) rather than from this dump - the
   demangler here is unreliable on templated and function-local
   forms. If the VA is absent from `manifests/rtti_vftable_index.json`,
   the candidate needs a Ghidra pass before it goes anywhere.
4. Promote through `tools/_symbols_io.py` with `sourceRefs` naming
   both this dump and the COL-walk, and a `confidence` drawn from
   the enum in `tools/validate_catalog.py`. There is no
   `provenance` field and no `rtti-grounded` confidence.
5. Use `--analyze <class>` as a fast struct sanity check before
   opening Ghidra, and `--findstr "<literal>"` for string-based
   xref tracing without loading Ghidra at all.

The headless CLI workflow (`tools/ghidra/*.java` via `run-headless.ps1`)
handles navigation, renaming, comments, and virtual dispatch chains. These
CLI tools are the offline complement.
