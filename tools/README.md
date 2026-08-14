# Tooling

This guide lists catalog generators, validators, and analysis tools. Commands
run from the repository root and use explicit local inputs where shown.

## Commands

The following commands are the supported entry points. Other scripts documented
below are implementation modules.

### Catalog and fixture commands

| Task | Command | Prerequisite or scope |
|---|---|---|
| Run CI-covered checks | See `.github\workflows\checks.yml` | Repository root |
| Build or check the canonical IR | `python tools\build_ir.py [--check]` | Repository catalog inputs |
| Refresh vendor fixtures | `python tools\refresh_vendor.py --repo NAME=PATH [...]` | Explicit source checkout names |

### Lua and bridge commands

| Task | Command | Prerequisite or scope |
|---|---|---|
| Decode and decompile LPB scripts | `python tools\lpb_pipeline.py [INSTALL_ROOT] [options]` | `unluac.jar` and Java are required for decompilation |
| Build decoded Lua callback contract | `python tools\extractors\build_lua_callback_contract.py --scripts-repo PATH` | Requires an explicit `xivl-client-scripts` checkout with its local corpus; emits metadata only |
| Inspect the client PE | `python -m tools.extractors.client_pe --exe PATH MODE` | Explicit path to `ffxivgame.exe` |
| Run a Ghidra post-script | `tools\ghidra\run-headless.ps1 -Script NAME [options]` | Configured Ghidra project and JDK |
| Query callers and callees | `python tools\callers.py TARGET` | Requires `build\callgraph.json`; generate it first with the documented `DumpCallGraph.java` -> `build_callgraph.py` pipeline |

## Layout

- `tools\` (this directory): reusable pipelines, audit invariants, and validators for catalog inputs.
- `tools\extractors\`: reusable Lua-bridge extractor pipelines (data-dependency catalog + apply-chain + substruct cross-ref) and the standalone `client_pe\` PE-extractor package (see `tools\extractors\client_pe\README.md`).
- `tools\ghidra\`: headless dispatcher (`run-headless.ps1`), the program-edit applier (`ApplyProgramEdits.java`), and the reusable RTTI exporter (`ExtractRtti.java`). Headless decomp logs under `logs/` are gitignored reproducible scratch. Decompiled bodies must not be committed; see README + AGENTS. Regenerate the logs from explicit target inputs.
- `data\vendor\`: vendored fixture promotions from first-party source projects, each under its own subdir (`opcodes\`, `captures\`) with a `PROVENANCE.json` recording source repo, source path, source license and URL, and the sha256 of the copied bytes. Fixtures are byte-identical promotions, not regenerated or relicensed. `tools\validate_vendor.py` re-hashes every file against its entry and `tools\refresh_vendor.py` restores or re-pins it from a named source checkout.

All scripts use only Python 3 standard library or PowerShell built-ins, except `validate_pcap_bridge.py` (requires the third-party `scapy` package for pcap parsing).

```powershell
powershell -ExecutionPolicy Bypass -File tools\validate-json.ps1
```

## Reusable pipelines

### Shared helpers

- `_regen_guard.py`: refuse-to-clobber check for partial manifest generators. `check_regen_safe()` compares the target manifest's on-disk top-level keys against the document about to be written and refuses the write if the file carries accumulated blocks the generator cannot reproduce. Used by `build_c2s_bridge_skeleton.py` and `extractors\build_data_dependency_catalog.py`; both exit 1 on refusal and take `--force` to override.
- `_symbols_io.py`: the single home for `manifests\symbols.json` I/O.
- `load_symbols()` always opens UTF-8 to avoid Windows cp1252 decoding.
- `next_bcsy_id()` allocates the next `BCS-Y-NNNN` from `max()` over the parsed ids (never array position, which is not globally sorted).
- `append_symbol()` appends and syncs `symbolCount`.
- `write_symbols()` writes the house style (indent 2, `ensure_ascii=False`, LF, trailing newline) via a temp file plus `os.replace()`, so an interrupted write cannot truncate the catalog.
- Writers must wrap the whole cycle in `symbols_transaction()`, which holds an exclusive lock file across the re-read and the write. Without it two concurrent processes allocate the same `BCS-Y-NNNN` and the later write silently drops the earlier writer's entry.
- Importing tools add `sys.path.insert(0, str(Path(__file__).resolve().parent))` then `from _symbols_io import load_symbols`.
- New readers or writers of symbols.json should use it rather than re-rolling the read / allocate / write.

### Vendor fixtures

- `refresh_vendor.py`: the only path for updating a vendored fixture. Re-fetches each declared file from its `PROVENANCE.json` source and restamps the entry's sha256. First-party source checkouts are named with repeatable `--repo NAME=PATH`; there is no workspace-layout default, and an entry whose repo is not named is skipped. `refreshMode: copy` reads the bytes from the source checkout's committed state (`git show HEAD:<path>`), not "<commit>:<path>"/"pinned to the commit". `--only <fixture> --promote` accepts a newer source state (add `--source-path` when the file moved).
- `validate_vendor.py`: the drift check, run by `validate-json.ps1`. Re-hashes every file under `data\vendor\` against its `PROVENANCE.json` entry and fails on a hash mismatch, a missing or undeclared file, a vendor subdir with no `PROVENANCE.json`, or an entry missing its source citation fields.
- `manifests\receiver_opcode_map_overlay.json` and `manifests\operation_opcode_map_overlay.json`: committed curated enrichment layers, hand-maintained plus written to by `analyze_outbound_emissions.py` (operation overlay only). `extract_receiver_opcode_map.py` and `extract_operation_opcode_map.py` deterministically merge these over the vendored-fixture base on every run.

### Bridge build pipeline

- `extract_lua_api_index.py`: harvests Lua API names from `symbols.json` (backtick-quoted prose + `_slotN_<name>_FUN_` patterns in symbol names). Emits `manifests\lua_api_index.json`; `--check` writes nothing and fails on drift.
- `extract_receiver_opcode_map.py`: normalizes the vendored `data\vendor\opcodes\client_receivers.json` fixture into BCS-Y-cross-referenced inbound + client-internal + strong / candidate buckets, then deterministically merges the curated `manifests\receiver_opcode_map_overlay.json` layer. Emits `manifests\receiver_opcode_map_inbound.json`; `--check` writes nothing and fails on drift.
- `extract_operation_opcode_map.py`: scaffolds the outbound side by inventorying the vendored `data\vendor\opcodes\opcodes.json` fixture's `retail_class_name` Operation classes, then deterministically merges the curated `manifests\operation_opcode_map_overlay.json` layer. Emits `manifests\operation_opcode_map_outbound.json`; `--check` writes nothing and fails on drift.
- `build_lua_to_opcode.py`: joins the bridge inputs into `manifests\lua_to_opcode.json`; `--check` writes nothing and fails on drift.
  The join excludes `_paired` and `_secondary` LuaActorImpl references: BCS-Y-0238 slot 63 is the SendLogReceiver path, while the real `_onUpdateDisplayName` fire is the slot 62 apply chain confirmed by the apply-chain evidence.
- `analyze_outbound_emissions.py`: parses the Ghidra `ScanOpcodeEmissions` output and writes per-opcode candidate emitter lists + high-confidence filters into `manifests\operation_opcode_map_overlay.json`. Re-run `extract_operation_opcode_map.py` afterward to fold the updated overlay into `manifests\operation_opcode_map_outbound.json`. The underlying Ghidra script is an external input to the research run.
- `build_c2s_bridge_skeleton.py`: builds the c2s side of the bridge from outbound-emission attribution.
- `extractors\build_data_dependency_catalog.py`: builds the data-dependency catalog (indirect bindings). `--normalize-citations` updates declared sibling path moves while preserving accumulated blocks that the base generator cannot reproduce.
- `extractors\build_apply_chain_firers.py`: aggregates the `receiver_apply_findings_*.json` snapshots into `lua_apply_chain_firers.json`; `--check` writes nothing and fails on drift.
- `extractors\build_substruct_cross_ref.py`: substruct chain-key cross-ref builder.

### LPB decode pipeline

- `decode_lpb.py`: decodes shipped `.le.lpb` Lua bytecode wrappers (rlu/rle) plus the script tree filename cipher.
- `test_decode_lpb.py`: unit tests for `decode_lpb.py` (rlu passthrough, rle XOR-0x73, filename cipher involution, known fixtures). Run with `python tools\test_decode_lpb.py`.
- `lpb_pipeline.py`: end-to-end orchestration of `.le.lpb` -> `.luac` (via `decode_lpb.py`) -> `.lua` (via external `unluac.jar`). Outputs to `build\lpb\` and `build\lua\`. `unluac.jar` location via env var `UNLUAC_JAR` or `--unluac-jar`. Stage 2 also requires `java` on PATH.

### Audit invariants

These checks should report 0 findings in a clean repository.

- `validate-json.ps1`: parses JSON files (explicit UTF-8) and checks manifest counts for `structs.json` and `symbols.json` against their array sizes.
- `validate_repo.py`: pins the tracked public surface and `.gitignore`, rejects every ignored private or scratch category even when force-added, scans tracked bytes for PE files, maintainer paths, and private-reference tokens, and checks JSON, IR schemas, documentation links/indexes, and vendor provenance.
- `validate_catalog.py`: semantic invariants over the catalog manifests (kind enum, confidence enum, address conventions, cross-refs, and role-refinement `evidenceKind`). The accepted evidence kinds are `pcap_observed`, `pcap_unobserved`, and `live_validated`; the last is reserved for behavior accepted by the retail 1.23b client in a live session. Should report 0 ERRORs in a clean repo (warnings and info are advisory). This is the single source of truth for the manifest enums. It does not read `schemas\`: that directory holds the C1 IR contracts only, which `validate_ir.py` loads and enforces. A schema that nothing loads and gates does not belong there.
- `validate_pcap_bridge.py`: optional explicit-path research command that requires `scapy` and is not part of repository validation. It requires `--captures-dir` with no workspace default and validates the pcap-grounded s2c bridge against that directory. It validates without writing by default; pass `--write` to regenerate the committed `manifests/pcap_validation.json` sidecar deliberately because downstream evidence records cite its numbers.
- `audit_catalog_xref.py`: detects notes-level paired-citation bugs of the form `FUN_XXXXXXXX (BCS-Y-NNNN)` where the cited id's address differs from `FUN_XXXXXXXX`. CLI: `--mismatch-only`, `--include-uncataloged`, `--json`.
- `audit_matrix.py`: combines the matrix attribution and downstream-drift audits over their shared inputs. `attribution` mode gates latent RTTI and case-handler findings while wire-name curation stays advisory; CLI: `--json`, `--invariant {rtti,case_handler,wire_name,all}`, `--apply` (reserved no-op). `drift` mode has HIGH/LOW review buckets plus the triaged SIBLING_CONTEXT, NEGATIVE_CONTEXT, and UBIQUITOUS_HELPER classes; CLI: `--high-only`, `--include-sibling`, `--json`.
- `hygiene_scan.py`: combined hygiene scan for the documentation and catalog surfaces.
- It checks wiki-link integrity and matrix-vs-symbols reconciliation.
- It also checks duplicate addresses, sourceRef form in `symbols.json` and `structs.json`, and embedded-manifest address drift.
- A3 validates citation form without leaving the checkout: `repository:path` citations and maintainer-record labels pass by shape, in-repo relative refs resolve on disk, and any live parent-dir path is a validation defect.
- It exits 1 on A1 cross-reference breaks, A3 live parent-dir refs, A4 broken wiki-links, and A5 embedded-address drift.
- A2 and missing in-repo refs such as ungenerated `build/` or local Ghidra logs stay advisory.
- Both `audit_matrix.py` modes likewise exit 1 on structural findings.

### Client-structure IR

The C1 normalization of the catalog into one versioned intermediate
representation. Reader's guide: `..\docs\ir-schema.md`.

- `build_ir.py`: builds `manifests\ir_catalog.json` from `structs.json`, `symbols.json`, `ir_overlay.json`, `manifests\rtti_vftable_index.json`, and the six relationship sources (the pcap opcode coverage matrix, the inbound receiver map, the outbound operation map, the Lua bridge, the c2s bridge skeleton, and the receiver field-write catalog). Generated, never hand-edited: `--check` rebuilds in memory and exits 1 on any drift. When a local `rtti_extraction_OUR.txt` dump (gitignored) is also present, it verifies the tracked index still matches that dump and fails on staleness. Refuses rather than guesses - an unrecognised size, offset, address, or opcode form raises instead of degrading to "unknown", a live sibling-checkout path is refused as a citation, and a relationship edge citing an uncataloged symbol is a build error.
- `build_rtti_index.py`: generates the tracked `manifests\rtti_vftable_index.json` as a sorted vftable VA column from a local `rtti_extraction_OUR.txt` dump. The dump is gitignored; regenerate it with `tools\extractors\client_pe` against your own client install.
- `validate_ir.py`: loads both schemas from `..\schemas\` and enforces them, plus thirteen invariants a schema cannot express: deferred dimensions stay empty, BCS identifiers survive unrenumbered, confidence is copied rather than moved, every sourceRef round-trips, parsed values preserve their raw string, layout byte arithmetic closes and no unknown span covers a declared field, every overlay entry reaches exactly one IR value, every relationship reference resolves in both directions, and opcode identity agrees with the summary counts.
- `test_ir_gates.py`: bite proofs. Plants one defect per gate and requires the named gate to fire. One case additionally asserts that no other invariant fires on the same plant. Its docstring records the two things it does not prove (the cross-talk check covers five of the thirteen invariants, and the determinism cases are single-process). Run with `python tools\test_ir_gates.py`.
- `_schema_check.py`: stdlib interpreter for the JSON Schema draft 2020-12 subset the in-repo schemas use, because CI installs no packages. It raises on any keyword it does not implement rather than passing it silently, and where a real `jsonschema` install exists it is consulted as a reported second opinion, never as the gate.
- `manifests\ir_overlay.json`: the curated companion, and the sole hand-maintained home for the two fields no source catalog records (type alignment, and the reading of a derived unknown span). Both populated and empty paths are bite-proved.

### Verification

- `verify_murmur2.py`: cross-checks backward-walking MurmurHash2 against the first-party `manifests\gam_hash_names.json` dataset and the vendored `data\vendor\captures\payload_samples.json` fixture. Fails loudly (exit 2) if either input is missing. 6/6 test vectors, 263/263 resolved (id, name) pairs, 60/60 s2c 0x0137 payload property ids.

### Headless Ghidra

- `ghidra\run-headless.ps1`: runs any post-script against the analyzed project, replacing hand-authored per-tier `.bat` wrappers. Install and project locations are machine-local and come from `BCS_GHIDRA_HOME`, `BCS_GHIDRA_PROJECTS`, `BCS_GHIDRA_PROJECT`, `BCS_JAVA_HOME` (plus optional `BCS_GHIDRA_PROGRAM`, default `ffxivgame.exe`); the script carries no path defaults and fails naming the missing variable. Defaults to `-noanalysis`. Pass `-ReadOnly` for every read-only script so an unexpected write cannot be saved, `-Out` for the `XIVL_DUMP_PATH` convention, and `-ScriptEnv` for per-script variables. Returns status plus elapsed seconds and exits 1 on script error or project lock.
- `ghidra\ExtractRtti.java`: read-only MSVC RTTI export. `XIVL_RTTI_OUT` writes the full RTTI index. For targeted structural details, set exact comma-separated mangled names in `XIVL_RTTI_DETAILS_TARGETS` and an output path in `XIVL_RTTI_DETAILS_OUT`; each detail row records the vftable, COL, TypeDescriptor, class hierarchy descriptor, executable slot count, base-array order, and code references that write or read the vftable.

  ```powershell
  tools\ghidra\run-headless.ps1 -Script DumpVAs.java -ReadOnly `
      -Out tools\ghidra\logs\c140.txt `
      -ScriptEnv @{ XIVL_TARGET_VAS = '0x00891F00' } `
      -ScriptPath @('ghidra')
  ```

  The project lock is exclusive: headless aborts with `LockException` rather than degrading, so a Ghidra GUI holding the project must be closed first. A `.lock` file left by a killed GUI is stale and reclaimed automatically.

- `ghidra\ApplyProgramEdits.java`: applies name / comment / prototype edits to the program database from a tab-separated file (`op<TAB>address<TAB>value`), so the annotation layer is reproducible from a tracked file rather than living only in a local `.gpr`. Ops: `rename` (function), `rename_data` (existing data symbol), `comment` (plate), `eol` (disassembly), `prototype` (C signature), `rename_local` (decompiler local). Values take `\t` / `\n` / `\\` escapes. Not covered: local variable types.

  Validation runs to completion before any transaction opens and reports every bad row at once. The apply transaction commits only if all rows succeed, so a malformed file cannot leave a partially annotated database. `BCS_EDITS_DRYRUN=1` validates without writing. `BCS_EDITS_UNDO` writes an inverse edit file that reverts the apply. It is emitted on dry runs too, where it doubles as a read-only dump of the current value of every targeted address.

  ```powershell
  # list the locals of two functions as an editable template
  tools\ghidra\run-headless.ps1 -Script ApplyProgramEdits.java -ScriptEnv @{
      BCS_LIST_LOCALS  = '0x00DA2AD0,0x005A4160'
      BCS_EDITS_REPORT = 'locals.tsv'
  }

  # apply an edit file
  tools\ghidra\run-headless.ps1 -Script ApplyProgramEdits.java -ScriptEnv @{
      BCS_EDITS        = 'edits.tsv'
      BCS_EDITS_REPORT = 'report.txt'
      BCS_EDITS_UNDO   = 'undo.tsv'
  }
  ```

  `rename_local` takes `currentName|storage|newName` (pipe-delimited because a storage string can itself contain commas, as in `EDX:4,EAX:4`). It matches on name AND storage because a decompiler local has no stable identifier across decompiles; a row whose pair no longer matches fails the batch rather than renaming the wrong variable. To author rows, set `BCS_LIST_LOCALS` to a CSV of function VAs: the script applies nothing and writes a ready-to-edit template to `BCS_EDITS_REPORT`, one `rename_local` row per local with the placeholder `<newName>`, parameters listed as comments, and unresolvable addresses noted inline. The placeholder is deliberately not a legal symbol name, so a row left unedited fails validation instead of renaming a variable to it. An unmatched row in a normal run also lists the candidate `name|storage` pairs it did find. Parameters are renamed through `prototype` and are rejected here. A file carrying both a `prototype` and a `rename_local` for the same function is refused: applying the signature re-runs the decompiler and can restorage the locals resolved during validation, so those renames belong in a second run.

  One caveat is inherent to Ghidra rather than to this script: renaming a local that the decompiler had given synthetic storage commits it to a permanent dynamic `HASH:` slot, so its storage changes on first rename and does not change back. Names revert exactly. An edit file written against a pristine decompile will not match a second time for such symbols, and fails loudly when it does not. Ordinary stack and register locals keep their storage and round-trip exactly. The emitted undo file re-resolves storage after the commit. If that post-commit decompile fails, the report says `APPLIED_UNDO_FAILED` and the run fails while stating that the edits already landed. It never presents the stale undo file as usable.

  Edit throughput is dominated by fixed startup, not by the edit count: 1200 edits commit in a ~270ms transaction inside a ~6s run, the same wall clock as a single-function read. `rename_local` is the one op with real per-target cost, since it needs a decompile per distinct function during validation and another after the commit to re-resolve storage - about 24ms per function on typical functions, seconds on the largest in the binary. 16 local renames across 16 functions still complete in ~6s end to end. The report's `status=` line is the authority on whether edits landed; `analyzeHeadless` runs its save step unconditionally without `-readOnly`, including after a script aborts.

  Addresses are Ghidra absolute VAs and must resolve in the program database. Three catalog distinctions matter: some `address` fields hold multiple semicolon-joined VAs (rejected by validation); a catalog name is research-side and is not necessarily applied in the `.gpr`, so `rename_data` against a cataloged data address commonly fails with "no symbol at"; and `rtti` / `data` / `global` addresses carry the catalog's dual shift convention, so they are not always feedable as-is the way `kind=function` addresses are.

### Ghidra RTTI

- `ghidra\ExtractRtti.java`: walks the program's symbol table for MSVC RTTI Complete Object Locator symbols and emits vftable VA, COL VA, mangled name, and demangled name as tab-separated records.

### Offline call graph

- `ghidra\DumpCallGraph.java` (headless post-script): iterates the FunctionManager and emits the full static direct-call edge list as TSV (one row per function: entryVA, maxBodyVA, name, comma-separated callee entry VAs via `Function.getCalledFunctions`). Run it like the RTTI extractor. Point `XIVL_CALLGRAPH_OUT` at `tools\ghidra\logs\callgraph_edges.tsv` (gitignored). Indirect / virtual (vtable) dispatch is NOT captured - that surface has its own snapshot manifests.
- `build_callgraph.py`: folds the TSV into `build\callgraph.json` (gitignored, regenerable) keyed by entry VA -> `{name, maxVA, callees, callers}` (callers are the inverted edges). A generated index, not a curated manifest: it lives in `build\`, not `manifests\`, and is not gated by `validate_catalog.py`.
- `callers.py <FUN_xxxxxxxx | 0xVA>`: resolves a raw / mid-function VA to its owning function via `[entryVA, maxVA]` and prints the function, its callees, and its callers, each annotated with the curated name + BCS-Y id from `symbols.json` (uncataloged -> `FUN_<va>`). `--json` for machine output. Turns the hand-built caller-tree snapshots (e.g. `manifests\fun_004d9910_callers_map.json`) into a one-liner from a Ghidra call-graph export.

Regenerate: dump the TSV (headless), then `python tools\build_callgraph.py`, then query with `python tools\callers.py FUN_004d9910`.

### Client PE toolkit

- `extractors\client_pe\`: stdlib-only toolkit that reads `ffxivgame.exe` directly (no Ghidra) for bulk RTTI / vtable / struct / string / import-table extraction. Additive to the Ghidra workflow. See `tools\extractors\client_pe\README.md`.

### Repository checks

The [checks workflow](../.github/workflows/checks.yml) is authoritative for
CI-covered checks. The [verification policy](../docs/ai_agents/verification.md)
documents the local research checks that require external evidence.
