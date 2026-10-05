# ZoneProtoDown NetBufferTmpl layout

The Windows 1.23b
`Component::Network::IpcChannel::NetBufferTmpl<Application::Network::ZoneProtoChannel::ZoneProtoDown>`
has an allocation-backed extent of `0x28`. Ten observed four-byte storage
cells cover that allocation. ARR declares the same object size and member
offsets, but uses a different backing capacity and allocation/release dispatch.
The promoted retail layout is `BCS-S-0502` in
[the catalog](../../../../manifests/structs.json). It records observed storage
and roles, not recovered original C++ member declarations or names.

## Inputs and method

| Build | Pinned identity |
|---|---|
| Windows 1.23b | `ffxivgame.exe`, 15,996,808 bytes, image base `0x00400000`, SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9` |
| ARR PS3 | `USRDIR/game/ffxivgame.ppu.self`, SHA-256 `1ab7bc671288463bc312fe1aa8da63742fd48a757bcf7d64715237f44c8c5321`; boot `2014.06.12.0000.0001`, game `2014.06.13.0000.0000` |

ARR's readable ELF is the exact SELF slice at `0x980`, length `0xC12B01C`,
SHA-256 `99ed4e57ea8d7a05c691c843e996ab85a9df51c239b2adc9d10ffe1acaa01537`.
DWARF2 CU `0x72B65A0`, address size 4, identifies
`C:/ffxiv/ffxiv_nightly_win/trunk/prog/server/Application/Rapture/source/Network/ZoneClient/RaptureChannelManager.cpp`.
DIE offsets are `.debug_info` section-relative. Types, reference chains,
parameters and `DW_OP_plus_uconst` offsets were parsed directly. Capstone
5.0.7 decoded PPC64 big-endian ARR code and x86 32-bit retail code; pefile
translated retail VAs to pinned file bytes. Four-byte object-pointer widths
are supported by declarations and accesses, not inferred from ELF64.

Retail used Ghidra 12.1.3/JDK 21 and the committed read-only scripts below.
Configure the explicit environment in [Ghidra](../../../../ghidra/README.md),
authenticate the named binary with `ghidra/VerifyProgramFileBytes.java`, and
require `COMPLETE: program-file-bytes-v1`, matching retained original/modified
FileBytes and all loaded initialized file-backed ranges. Unbacked excluded
ranges do not support these claims. Set `$EvidenceOutput` to a new ignored
directory and run from the repository root:

```powershell
$Targets = '0x00DAEA10,0x00DAEAD0,0x00DAEC70,0x00DAF110,0x00DAF210,0x00DAF5B0,0x004E5CA0'
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'buffer-decomp.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'buffer-listing.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/export-references.ps1 -Addresses '0x01128EB4','0x00DAEAD0','0x00DAEA10','0x00DAEC70','0x01128F54','0x00DAF110','0x00DAF210','0x00DAF5B0' -Out (Join-Path $EvidenceOutput 'buffer-references.txt')
```

Require every requested decompilation section, complete listing counts and
the wrapper's verified reference terminal marker. Reference counts cover
Ghidra-recorded references only; computed, indirect, dynamic and unanalyzed
references may be absent. Direct bytes recover `add esp, 4` at
`0x00DAEAE6 / 0x00DAEB04`, omitted after free calls marked nonreturning.
The complete deleting destructor is 61 bytes, 20 instructions. Library free
internals are not a complete allocator-behavior proof. No client was run.

## Retail identity and allocation

Vtable `0x01128EB4` points at complete-object locator `0x011A217C`, type
descriptor `0x0131B658`, hierarchy `0x011A2190` and base array `0x011A21A0`.
Its exact name is
`.?AV?$NetBufferTmpl@TZoneProtoDown@ZoneProtoChannel@Network@Application@@@IpcChannel@Network@Component@@`.
The three-entry hierarchy has flags zero:

| Class | Base descriptor | Type descriptor | PMD |
|---|---|---|---|
| Down NetBufferTmpl | `0x011A21B0` | `0x0131B658` | `(0,-1,0)` |
| Component::Network::IpcChannel::NetBufferBase | `0x01142020` | `0x0126A47C` | `(0,-1,0)` |
| Sqex::Misc::NonCopyable | `0x0113FE38` | `0x012668F8` | `(4,-1,0)` |

RTTI supplies offsets, not retail base sizes or access specifiers. The buffer's
three slots are deleting destructor `0x00DAEAD0` and shared `ret 4` stub
`0x00776340` twice. The next COL at `0x01128EC0`, value `0x011A21CC`,
bounds the table and is not a fourth method.

Producer `0x00DAEC70`, complete 142 bytes, 50 instructions, increments its
factory's `+4` word at `0x00DAEC9E` between virtual `+4/+8` calls, saves the
new value at `0x00DAECA5`, pushes allocation size `0x28` at `0x00DAECAC`
and calls `0x009D1B35` at `0x00DAECAE`. On non-null return it pushes
the sequence, requested capacity and factory pointer at
`0x00DAECCA / 0x00DAECCB / 0x00DAECCC`, supplies the allocation in ECX
and calls named constructor `0x00DAEA10` at `0x00DAECCF`.
This independently ties the extent and constructor arguments to Down RTTI.
Complete sequence semantics and original identifier names remain unproved.

Constructor `0x00DAEA10` is complete 182 bytes, 70 instructions. It calls
the base constructor at `0x00DAEA16`, installs the named table, records the
arguments and allocates backing storage independently of the object.
For unsigned request `<=0x1C10`, it requests `0x1C10` bytes; otherwise it
requests that larger value. A successful allocation is zeroed for `0x1C10`
bytes in either branch, not necessarily the full larger capacity. A failed
backing allocation leaves a null pointer with capacity still recorded.
No guarantee of allocation success or complete initialization is inferred.

## Observed storage and consumers

| Offset | Width | Retail support |
|---|---|---|
| `+0x00` | 4 | Vptr installed at `0x00DAEA2F` and restored by deleting destructor at `0x00DAEAD8` |
| `+0x04` | 4 | Third explicit constructor argument, sequence store `0x00DAEA35`; tree callers read it as their key at `0x00DAF161 / 0x00DAF23B` |
| `+0x08` | 4 | Factory argument stored at `0x00DAEA38`; no ARR interface type transferred |
| `+0x0C` | 4 | Dword cleared at `0x00DAEA3B`; original declaration unproved |
| `+0x10` | 4 | Dword cleared at `0x00DAEA3E`; original declaration unproved |
| `+0x14` | 4 | Consumer copies its output record `+0x0C` dword at `0x00DAF78C` |
| `+0x18` | 4 | Consumer copies its output record `+0x10` dword at `0x00DAF792` |
| `+0x1C` | 4 | Backing capacity stored at `0x00DAEA68 / 0x00DAEA7C / 0x00DAEAB7`, tied to the malloc request |
| `+0x20` | 4 | Cleared by constructor; consumer stores copied-data length at `0x00DAF7C2` |
| `+0x24` | 4 | Backing-data pointer stored at `0x00DAEA64 / 0x00DAEA78 / 0x00DAEAB0`, read by consumer and destructor |

Factory pickup `0x00DAF110` reads the first sentinel at `+0x0C` and the
node object pointer at `+0x10` at `0x00DAF141`. On an empty tree or null
object it calls producer `0x00DAEC70` with capacity zero. It reads buffer
`+4`, assembles the key/object pair and submits it to tree-admission helper
`0x004E5CA0` with factory `this+0x14` at `0x00DAF16E..0x00DAF179`.
That helper performs unsigned comparisons against node `+0x0C`; this does
not prove the complete insertion, release or pool lifecycle.

Allocation selector `0x00DAF210` forms its two-argument 32-bit sum. Above
`0x1C10` it calls the producer with that capacity and submits the resulting
key/object pair to the second tree; otherwise it calls pickup.
This connects the named allocation to the two-tree factory operations in
[the factory finding](buffer-factory.md). Complete pool roles and behavior
on every reused-object, allocation-failure or overflow path remain unresolved.

Consumer `0x00DAF5B0`, complete 627 bytes, 218 instructions, selects the
allocation branch for its record halfword value 3. It obtains a factory
through owner virtual `+0x40`, then calls `0x00DAF210` with `0x1C10,0` at
`0x00DAF77A`. On success it stores buffer `+0x14/+0x18` from output record
`+0x0C/+0x10` at `0x00DAF78C / 0x00DAF792`. The output record's leading
halfword at `+8`, zero-extended and reduced by `0x10`, supplies the copy
length. The source is owner data pointer `+8` plus its halfword cursor `+0x0E`
plus `0x10`. It copies to buffer `+0x24` via `0x009D4600` at `0x00DAF7AD`,
stores that length in buffer `+0x20` at `0x00DAF7C2`, and publishes the buffer
in output record `+0` at `0x00DAF7E7`. These accesses establish storage roles;
they do not assign entity-ID domains, protocol names or opcodes, or prove
safety for every malformed input, reused object or callback.

Deleting destructor `0x00DAEAD0` reads `+0x24`, conditionally calls free
`0x009D5C88`, clears the pointer at `0x00DAEAEB`, calls base destructor
`0x00DC1E60` and optionally frees the object through `0x009D1B17` when its
flag bit is set. This independently corroborates data ownership; complete
allocator behavior and the lifetime of every reused buffer remain unproved.

## ARR correspondence and limits

ARR Down type DIE `0x72C954E` declares size `0x28`. Its public NetBufferBase
base DIE `0x72C956A` is at zero; base type `0x72C6CF4` declares size 4 and
privately inherits NonCopyable `0x72EBF57`, size 1, at zero via `0x72C6D07`.
Retail's recorded NonCopyable placement at `+4` is a concrete ABI difference
despite the matching observed storage offsets. Retail base sizes and source
access specifiers are not transferred.

| ARR member | DIE | Offset and type | Retail comparison limit |
|---|---|---|---|
| id_ | `0x72C9574` | `+4`, BufferID_t -> unsigned long, size 4 | Allocation-sequence/key role observed; original name unproved |
| pFactory_ | `0x72C9587` | `+8`, NetBufferFactoryInterface pointer | Factory argument observed; interface declaration not transferred |
| replaceParam_ | `0x72C959A` | `+0x0C`, NetBufferReplaceParam, size 8 | Two cleared dwords; compound declaration unproved |
| srcEntityId_ / dstEntityId_ | `0x72C95AD / 0x72C95C0` | `+0x14/+0x18`, uint32_t aliases | Copied record dwords; original names and domains unproved |
| areaSize_ / dataSize_ | `0x72C95D3 / 0x72C95E6` | `+0x1C/+0x20`, size_t -> uint32_t | Independently observed capacity and data-length roles |
| pDataBlock_ | `0x72C95F9` | `+0x24`, NetBufferDataBlock pointer | Retail backing-data pointer; original declaration unproved |

ARR data-block DIE `0x72C80E5` declares `0x12D8` bytes, DataArea_ at zero
via member `0x72C8101`. That declaration and name are ARR facts only.

ARR allocation body `allocateateNewBuffer_` at `0x1700CDC`, size `0x118`,
70 PPC instructions, has body/declaration DIEs `0x72CBE4D / 0x72C826F`.
Its signature has the implicit factory object and one size_t parameter. It
increments factory `+4` at `0x1700D24`, requests object size `0x28` at
`0x1700D4C`, constructs the buffer inline, stores the sequence/factory at
`0x1700D88 / 0x1700D94`, clears `+0x0C/+0x10`, sets capacity to unsigned
max(request,`0x12D8`) at `0x1700DB4` and obtains data through factory virtual
`+8`. Retail's producer calls an out-of-line three-argument constructor
and that constructor directly calls malloc with minimum `0x1C10`.
The allocation and storage sequences demonstrate a narrow correspondence;
complete function equivalence and failure behavior are not proved.

ARR vtable symbol `0x1A12288`, size `0x18`, has callable address point
`0x1A12290`: two leading zero words and four four-byte descriptor entries.
Each descriptor stores code at `+0`, TOC at `+4`. Descriptors
`0x1B938E0 / 0x1B938E8` resolve to destructors `0x1702720 / 0x1702780`;
`0x1B939E0 / 0x1B939E8` resolve to setDataHeader/fixDataHeader
`0x1703298 / 0x170329C`, both four-byte `blr` bodies. Their declaration
DIEs are `0x72C971A / 0x72C973F` and body DIEs `0x72EACE4 / 0x72EAD12`.
Retail's shared `ret 4` slots resemble the no-op hooks but provide no independent
original names; slot indices are not transferable.

ARR's non-deleting destructor `0x1702720`, size `0x60`, calls factory virtual
`+0x0C` with the data pointer, then the base destructor. Its body/declaration
DIEs are `0x72CCE6E / 0x72C9637`. Retail instead calls free directly,
clears the pointer and optionally deletes the object. Complete allocator,
virtual-hook and destructor correspondence therefore remains unproved.

Confidence is high in the retail owner, extent, observed cells and listed
roles. Original member names, compound declarations, alignment, complete
identifier/pool semantics, packet meanings, opcodes, runtime behavior and
complete cross-build methods remain unresolved. No BCS-Y identity is promoted.

The strongest next struct target is the receive-result record passed to
`0x00DAF5B0`, with caller `0x00DAFA30`. Its buffer publication at `+0` and
record accesses provide direct retail anchors for a separate layout pass.
