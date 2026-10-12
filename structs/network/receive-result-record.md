# Down receive-result record

The Windows 1.23b consumer `0x00DAF5B0` writes its result into a record
supplied by its only caller, `0x00DAFA30`. The record is a stack local of
that caller with a `0x29C`-byte storage window. Instruction-verified writes
reach `+0x298`. The promoted layout is `BCS-S-0503` in
[the catalog](../../manifests/structs.json). It records observed storage and
roles, not a recovered C++ declaration, class name or packet semantics.

## Inputs and method

The source is the 1.23b `ffxivgame.exe`, 15,996,808 bytes, image base
`0x00400000`, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Retail used Ghidra 12.1.3/JDK 21 and the committed read-only scripts below.
Configure the explicit environment in [Ghidra](../../ghidra/README.md),
authenticate the named binary with `ghidra/VerifyProgramFileBytes.java`, and
require `COMPLETE: program-file-bytes-v1`. Set `$EvidenceOutput` to a new
ignored directory and run from the repository root:

```powershell
$Targets = '0x00DAFA30,0x00DAF5B0'
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'record-decomp.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'record-listing.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/export-references.ps1 -Addresses '0x00DAFA30','0x00DAF5B0' -Out (Join-Path $EvidenceOutput 'record-references.txt')
```

Require every requested decompilation section, complete listing counts and
the wrapper's verified reference terminal marker. Capstone 5.0.7 decoded every
cited x86 32-bit instruction and both jump tables directly from the pinned
file bytes. A full scan of the file's executable sections for rel32 `CALL`
and `JMP` operands, plus every section for absolute dwords, found one
reference to `0x00DAF5B0`: the call at `0x00DAFAC4`. Computed targets are
outside that scan. No client was run.

## Construction and extent

`0x00DAFA30` aligns its frame with `AND ESP,0xfffffff8` at `0x00DAFA33`,
reserves `0x2EC` bytes at `0x00DAFA36` and stores its security cookie at
`[ESP+0x2E8]` at `0x00DAFA43`. After the three register pushes at
`0x00DAFA4D / 0x00DAFA50 / 0x00DAFA51`, the record starts at `[ESP+0x58]`
and the cookie sits at `[ESP+0x2F4]`, which `0x00DAFC35` reads. The
caller's listing makes no other stack access between them. The storage window is therefore
`0x29C` bytes.

The caller zeroes `+0x00`, `+0x08`, `+0x0A`, `+0x0C` and `+0x10` at
`0x00DAFA5F..0x00DAFA71`. It passes the record as the second explicit
argument at `0x00DAFABB / 0x00DAFABF` and calls the consumer at `0x00DAFAC4`,
with `ECX` set to its third explicit argument plus `0x1C`. The consumer
clears `+0x0A` again at `0x00DAF5B8`.

Only when at least `0x10` unread bytes remain (`0x00DAF5C2..0x00DAF606`)
does the consumer copy four dwords from its source cursor into `+0x08..+0x18`
(`0x00DAF60F / 0x00DAF619 / 0x00DAF620 / 0x00DAF627`). The halfword at `+0x08`
is a length that includes this 16-byte header: `0x00DAF62A..0x00DAF640`
bounds it against the remaining input. The halfword at `+0x0A` selects the
consumer's case through table `0x00DAF824` at `0x00DAF646..0x00DAF656`.
Selectors 1, 2, 7, 8, 9 and 10 copy the complete message from the header
start into `+0x08` only when the length equals the case's constant:

| Selector | Required length | Copy locator | Record bytes written |
|---|---|---|---|
| 1 | `0x38` | `0x00DAF65D..0x00DAF66F` | `+0x08..+0x40` |
| 2 | `0x38` | `0x00DAF6B7..0x00DAF6C9` | `+0x08..+0x40` |
| 7, 8 | `0x18` | `0x00DAF711..0x00DAF73C` | `+0x08..+0x20` |
| 9 | `0x278` | `0x00DAF68A..0x00DAF69C` | `+0x08..+0x280` |
| 10 | `0x290` | `0x00DAF6E4..0x00DAF6F6` | `+0x08..+0x298` |

Selector 3 allocates a [Down buffer](net-buffer-down.md), copies `+0x0C`
and `+0x10` into it at `0x00DAF789..0x00DAF792` and publishes it at record
`+0x00` at `0x00DAF7E7`. Selectors 4 to 6 and out-of-range values take the
default branch without a further record write. The deepest observed write, selector
10, ends at `+0x298`; no access to `+0x04` or `+0x298..+0x29C` was observed.

## Observed storage

| Offset | Width | Retail support |
|---|---|---|
| `+0x00` | 4 | Zeroed at `0x00DAFA5F`; selector 3 publishes the allocated Down buffer at `0x00DAF7E7` |
| `+0x04` | 4 | No observed access |
| `+0x08` | 2 | Zeroed at `0x00DAFA63`; header length read at `0x00DAF62A` |
| `+0x0A` | 2 | Zeroed at `0x00DAFA68` and `0x00DAF5B8`; written by the header copy at `0x00DAF60F`; selector read at `0x00DAF646` and by the caller at `0x00DAFAF1` |
| `+0x0C` | 4 | Zeroed at `0x00DAFA6D`; header dword copied at `0x00DAF619`, read at `0x00DAF789` and `0x00DAF7D9` |
| `+0x10` | 4 | Zeroed at `0x00DAFA71`; header dword copied at `0x00DAF620`, read at `0x00DAF78F` |
| `+0x14` | 4 | Header dword copied at `0x00DAF627`; not zeroed by the caller |
| `+0x18..+0x298` | variable | Selector-specific message bytes, per the copy table |

## Caller consumption

A nonzero consumer return, which only selector 3 produces, makes the caller
increment its receiver's `+0x24` at `0x00DAFAD1` and store the buffer at its
first explicit argument's `+0x08` at `0x00DAFAD5`. On a zero return the caller
reads selector `+0x0A` at `0x00DAFAF1` and dispatches through table
`0x00DAFC50` at `0x00DAFB02`:

| Selector | Target | Record use |
|---|---|---|
| 1 | `0x00DAFB09` | Passes `record+0x08` to `0x00DAF430` at `0x00DAFB16` |
| 2 | `0x00DAFB90` | Passes `record+0x08` to `0x00DB34A0` at `0x00DAFB9C` |
| 3 to 6 | `0x00DAFC35` | Returns zero |
| 7 | `0x00DAFC10` | Calls import cell `0x00F3E148` with the third explicit argument `+0x38` and 1 |
| 8 | `0x00DAFAD8` | Returns one |
| 9 | `0x00DAFB34` | Passes `record+0x08` to receiver `+0x78` virtual `+0x08` at `0x00DAFB4F` or to `0x00DA1BE0` at `0x00DAFB60`, then passes the `[ESP+0x20]` local to `0x00DAF430` at `0x00DAFB72` |
| 10 | `0x00DAFBBA` | Passes `record+0x08` to receiver `+0x78` virtual `+0x10` at `0x00DAFBD5` or to `0x00DA1C20` at `0x00DAFBE4`, then passes the `[ESP+0x20]` local to `0x00DB34A0` at `0x00DAFBF2` |

The caller's `[ESP+0x20]` local lies outside the record. These handlers read `record+0x08` as their input; their
internal field use is not part of this layout.

## Limits

Confidence is high in the storage window, the listed writes and the selector
dispatch. The `0x29C`-byte window bounds the record's storage; it does not
prove an original declared size, and the unaccessed `+0x04` and
`+0x298..+0x29C` bytes may be padding. Original member names, selector and
message meanings, the classes of the caller's receiver and arguments, and
runtime behavior remain unresolved. No BCS-Y identity is promoted.
