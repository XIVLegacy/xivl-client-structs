# Ghidra

This directory contains small Ghidra scripts and import/export helpers that
produce evidence for the client-structure manifests.

Use `tools/ghidra/run-headless.ps1` for headless runs. Machine-local project
settings come from its required environment variables. Project databases and
decompiled function bodies stay out of the repository.

Manifest evidence locators name their decomp log through the same variables:
`%BCS_GHIDRA_PROJECTS%\<log>.txt` is the log under whatever project directory
`BCS_GHIDRA_PROJECTS` points at, and `<ghidra-scripts>` marks a script that
predates `run-headless.ps1`. Both are locations, not tracked files. The logs
regenerate on demand.

Commit only compact exports containing names, symbols, signatures, offsets, or
comments needed by a manifest.

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
function and instruction. It also reports whether the field was operand 0
(destination) or another operand (source). Set `XIVL_BASE_REGS` to a register
list to narrow beyond the ESP/EBP-excluded default.

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
