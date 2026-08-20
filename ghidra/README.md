# Ghidra

This directory contains small Ghidra scripts and import/export helpers that
produce evidence for the client-structure manifests.

Use `tools/ghidra/run-headless.ps1` for headless runs. Machine-local project
settings come from its required environment variables. Project databases and
decompiled function bodies stay out of the repository.

Manifest evidence locators name their decomp log through the same variables:
`%BCS_GHIDRA_PROJECTS%\<log>.txt` is the log under whatever project directory
`BCS_GHIDRA_PROJECTS` points at. `<ghidra-scripts>` marks an earlier external
script path whose producing script was not committed; the cited run therefore
cannot be reproduced from this checkout. Both are locations, not tracked files.
Historical ignored logs are not guaranteed regenerable. A 2026-08-17 audit
found that many logs named in manifest citations no longer existed.

For a new promotion that cites an ignored log, record the recipe in the owning
manifest's top-level `method` block. Include the producing script by its
committed path, the exact `tools\ghidra\run-headless.ps1` invocation, and its
inputs, such as the VA list, offset query, or targets. A citation naming a
script that is not committed is not a recipe.

Commit only compact exports that carry names, symbols, signatures, offsets,
or comments needed by a manifest.

## VerifyActorRebuild.java

`VerifyActorRebuild.java` is the fixed, decompiler-free exporter for check
`actor-rebuild-receiver-field-v1`. It inspects only the named instruction and
function addresses, validates program/language/compiler identity, and emits
deterministic structured observations to `XIVL_RETAIL_OBSERVATIONS_OUT`. A
usable output requires its explicit completion marker. The script must run
read-only against a newly imported project for retail-input reproduction.

The structured output is temporary private-analysis material. Pass it directly
to `tools/verify_retail_actor_rebuild.py`; do not commit or upload it.

## DumpVAs.java

Generic post-script: reads a comma-separated hex VA list from
`XIVL_TARGET_VAS`, decompiles each function with caller/callee lists, and
writes one combined report to `XIVL_DUMP_PATH`. Run it through the dispatcher
at `tools\ghidra\run-headless.ps1`. See `tools\README.md` for the environment
variables it requires:

```powershell
tools\ghidra\run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -Out tools\ghidra\logs\out.txt `
    -ScriptEnv @{ XIVL_TARGET_VAS = '0x00891F00,0x00DA76B0' } `
    -ScriptPath @('ghidra')
```

Addresses are Ghidra absolute VAs (image base `0x00400000`).

## FindFieldRefs.java

Scans every instruction for memory operands whose displacement matches one of
`IMPLEMENTATION_OFFSET_QUERY` (comma-separated hex) and reports the containing
function, the instruction, and whether the field was operand 0 (destination)
or a source. Set `XIVL_BASE_REGS` to a register list to narrow beyond the
ESP/EBP-excluded default.

```powershell
tools\ghidra\run-headless.ps1 -Script FindFieldRefs.java -ReadOnly `
    -Out tools\ghidra\logs\out.txt `
    -ScriptEnv @{ IMPLEMENTATION_OFFSET_QUERY = '0x92' } `
    -ScriptPath @('ghidra')
```

The WRITE/READ label is operand position only, so `CMP` and `TEST` are
reported as WRITE and must be read as comparisons.

## FindCompoundOffsetWriters.java

Finds stores whose effective address reaches one of `XIVL_OFFSET_QUERY`
after affine register arithmetic, indexed addressing, or an exact stack-local
spill and reload within a basic block. It also pseudo-disassembles undefined
bytes in executable ranges without modifying the program, so the report covers
defined instructions outside functions and can expose undisassembled tails.
Pseudo-decoded candidates remain labeled as undefined until their surrounding
code establishes identity. A usable report ends with `COMPLETE:`;
`INCOMPLETE:` output cannot support a negative.

```powershell
tools\ghidra\run-headless.ps1 -Script FindCompoundOffsetWriters.java -ReadOnly `
    -Out tools\ghidra\logs\out.txt `
    -ScriptEnv @{ XIVL_OFFSET_QUERY = '0x4d8,0x4e8' } `
    -ScriptPath @('ghidra')
```

Historical manifest records reference an earlier, unrelated `FindOffsetWriters.java`; they do not describe this script.

## FindReferences.java

Exports every reference recorded by Ghidra analysis to one or more addresses,
or resolves exact or substring queries against all defined-string data and
exports each match and its references. A usable report ends with `COMPLETE:`;
`INCOMPLETE:` output cannot support a negative. The reference database can omit
computed, indirect, dynamically dispatched, or unanalyzed-region references,
so zero results establish only the directly encoded reference class represented
by the analyzed database.

```powershell
tools\ghidra\run-headless.ps1 -Script FindReferences.java -ReadOnly `
    -Out tools\ghidra\logs\out.txt `
    -ScriptEnv @{ XIVL_REFERENCE_MODE = 'ADDRESS'; XIVL_REFERENCE_ADDRESSES = '0x0076C220,0x004E0240' } `
    -ScriptPath @('ghidra')
```

For string queries, set `XIVL_REFERENCE_MODE` to `STRING`, provide newline-
separated literals in `XIVL_REFERENCE_STRINGS`, and optionally set
`XIVL_STRING_MATCH` to `SUBSTRING`; its default is `EXACT`.
