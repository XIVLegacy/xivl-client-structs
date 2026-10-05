# ZoneProtoUp NetBufferTmpl layout

The Windows 1.23b
`Component::Network::IpcChannel::NetBufferTmpl<Application::Network::ZoneProtoChannel::ZoneProtoUp>`
has an allocation-backed extent of `0x28`. Ten observed four-byte storage
cells cover that allocation. ARR declares the same object size and member
offsets, but uses a different backing capacity and allocation/release dispatch.
The promoted retail layout is `BCS-S-0501` in
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
are supported by these declarations and accesses, not inferred from ELF64.

Retail used Ghidra 12.1.3/JDK 21 and the committed read-only scripts below.
Configure the explicit environment in [Ghidra](../../../../ghidra/README.md),
authenticate the named binary with `ghidra/VerifyProgramFileBytes.java`, and
require `COMPLETE: program-file-bytes-v1`, matching retained original/modified
FileBytes and all loaded initialized file-backed ranges. Unbacked excluded
ranges do not support these claims. Set `$EvidenceOutput` to a new ignored
directory and run from the repository root:

```powershell
$Targets = '0x00DAE910,0x00DAE9D0,0x00DAEB90,0x00DC1E60,0x00DC1E70,0x00776340,0x009D5C88,0x00DAF080,0x00DAF1A0,0x00DAF850,0x00994A90,0x00DAE010'
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'buffer-decomp.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'buffer-listing.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/export-references.ps1 -Addresses '0x01128EA4','0x00DAE9D0','0x00DAE910','0x00DAEB90','0x01128F44' -Out (Join-Path $EvidenceOutput 'buffer-references.txt')
```

Require every requested decompilation section, complete listing counts and
the wrapper's verified reference terminal marker. Reference counts cover
Ghidra-recorded references only; computed, indirect, dynamic and unanalyzed
references may be absent. Direct bytes recover `add esp, 4` at
`0x00DAE9E6 / 0x00DAEA04`, omitted after free calls marked nonreturning.
The complete deleting destructor is 61 bytes, 20 instructions. Library free
internals are not a complete allocator-behavior proof. No client was run.

## Retail identity and allocation

Vtable `0x01128EA4` points at complete-object locator `0x011A212C`, type
descriptor `0x0131B5E8`, hierarchy `0x011A2140` and base array `0x011A2150`.
Its exact name is
`.?AV?$NetBufferTmpl@TZoneProtoUp@ZoneProtoChannel@Network@Application@@@IpcChannel@Network@Component@@`.
The three-entry hierarchy has flags zero:

| Class | Base descriptor | Type descriptor | PMD |
|---|---|---|---|
| Up NetBufferTmpl | `0x011A2160` | `0x0131B5E8` | `(0,-1,0)` |
| Component::Network::IpcChannel::NetBufferBase | `0x01142020` | `0x0126A47C` | `(0,-1,0)` |
| Sqex::Misc::NonCopyable | `0x0113FE38` | `0x012668F8` | `(4,-1,0)` |

Base constructor `0x00DC1E70` installs NetBufferBase table `0x01129B1C`;
base destructor `0x00DC1E60` restores it. Its own RTTI lists NonCopyable at
`+4`. RTTI supplies these offsets, not retail base sizes or access specifiers.
The buffer's three slots are deleting destructor `0x00DAE9D0` and shared
`ret 4` stub `0x00776340` twice. The next COL at `0x01128EB0` bounds the
table; that COL names the Down specialization and is not a fourth method.

Producer `0x00DAEB90`, complete 142 bytes, 50 instructions, increments its
factory's `+4` word at `0x00DAEBBE` between virtual `+4/+8` calls, saves the
new value at `0x00DAEBC5`, pushes allocation size `0x28` at `0x00DAEBCC`
and calls `0x009D1B35` at `0x00DAEBCE`. On non-null return it pushes
the sequence, requested capacity and factory pointer at
`0x00DAEBEA / 0x00DAEBEB / 0x00DAEBEC`, supplies the allocation in ECX
and calls named constructor `0x00DAE910` at `0x00DAEBEF`.
This ties the object extent and constructor arguments to the retail RTTI.
Complete sequence semantics and original identifier names remain unproved.

Constructor `0x00DAE910` is complete 182 bytes, 70 instructions. It calls
the base constructor at `0x00DAE916`, installs the named table, records the
arguments and allocates backing storage independently of the object.
For unsigned request `<=0x898`, it requests `0x898` bytes; otherwise it
requests that larger value. A successful allocation is zeroed for `0x898`
bytes in either branch, not necessarily the full larger capacity. A failed
backing allocation leaves a null pointer with capacity still recorded.
No guarantee of allocation success or complete initialization is inferred.

## Observed storage and consumers

| Offset | Width | Retail support |
|---|---|---|
| `+0x00` | 4 | Vptr installed at `0x00DAE92F` and restored by deleting destructor at `0x00DAE9D8` |
| `+0x04` | 4 | Third explicit constructor argument, sequence store `0x00DAE935`; tree callers read it as their key at `0x00DAF0D1 / 0x00DAF1CB` |
| `+0x08` | 4 | Factory argument stored at `0x00DAE938`; no ARR interface type transferred |
| `+0x0C` | 4 | Dword cleared at `0x00DAE93B`; original declaration unproved |
| `+0x10` | 4 | Dword cleared at `0x00DAE93E`; original declaration unproved |
| `+0x14` | 4 | Owner-selected dword stored by builder at `0x00DAF8A3` |
| `+0x18` | 4 | Owner-selected dword stored by builder at `0x00DAF8B5` |
| `+0x1C` | 4 | Backing capacity stored at `0x00DAE968 / 0x00DAE97C / 0x00DAE9B7`, tied to the malloc request |
| `+0x20` | 4 | Cleared by constructor; builder stores a zero-extended assignment halfword at `0x00DAF8C4` and uses that length for memset |
| `+0x24` | 4 | Backing-data pointer stored at `0x00DAE964 / 0x00DAE978 / 0x00DAE9B0`, read by builder, outbound copy and destructor |

Factory pickup body `0x00DAF080` reads the first sentinel at `+0x0C`, then
the node object pointer at `+0x10` at `0x00DAF0B1`. On an empty tree or null
object it calls producer `0x00DAEB90` with capacity zero. It reads buffer
`+4`, assembles the key/object pair and submits it to the tree-admission
helper `0x00994A90` with factory `this+0x14` at `0x00DAF0DE..0x00DAF0E9`.
That helper performs unsigned comparisons against node `+0x0C`; this does
not prove the complete insertion, release or pool lifecycle.

Allocation selector `0x00DAF1A0` forms its two-argument 32-bit sum. Above
`0x898` it calls the producer with that capacity and submits the resulting
key/object pair to the second tree; otherwise it calls pickup.
This connects the named allocation to the two-tree factory operations in
[the factory finding](buffer-factory.md). Complete pool roles and behavior
on every reused-object, allocation-failure or overflow path remain unresolved.

Builder `0x00DAF850`, complete 196 bytes, 90 instructions, obtains a factory
through an owner virtual call and calls `0x00DAF1A0`. On success it stores
the buffer in assignment `+0x0C`. It writes buffer `+0x14` from owner `+0x14`
or an object reached through owner `+0x18`, and `+0x18` from owner `+0x1C`
or an object reached through owner `+0x20`; both indirect cases read object
`+8`. Those copied dwords do not independently establish entity-ID domains.
The builder reads the assignment's virtual `+4` result, zero-extends its
halfword into buffer `+0x20`, uses that length to clear buffer `+0x24` storage
and passes the data pointer to assignment virtual `+8`.
Existing outbound `0x00DAE010` reads that buffer's `+0x24` and copies into
data `+0x10`. Its functional comparison remains
`xivl-decomp:docs/arr-debug-comparison.md`, ZoneClient outbound packet forwarding.

Deleting destructor `0x00DAE9D0` reads `+0x24`, conditionally calls free
`0x009D5C88`, clears the pointer at `0x00DAE9EB`, calls the base destructor,
and optionally frees the object through `0x009D1B17` when its flag bit is set.
This independently corroborates data ownership; complete allocator behavior
and the lifetime of every reused buffer are not established.

## ARR correspondence and limits

ARR Up type DIE `0x72C9216` declares size `0x28`. Its public NetBufferBase
base DIE `0x72C9232` is at zero; base type `0x72C6CF4` declares size 4 and
privately inherits NonCopyable `0x72EBF57`, size 1, at zero via `0x72C6D07`.
Retail's recorded NonCopyable placement at `+4` is a concrete ABI difference
despite the matching observed object storage offsets. Retail base sizes and
source access specifiers are not transferred.

| ARR member | DIE | Offset and type | Retail comparison limit |
|---|---|---|---|
| id_ | `0x72C923C` | `+4`, BufferID_t -> unsigned long, size 4 | Allocation-sequence/key role observed; original name unproved |
| pFactory_ | `0x72C924F` | `+8`, NetBufferFactoryInterface pointer | Factory argument observed; interface declaration not transferred |
| replaceParam_ | `0x72C9262` | `+0x0C`, NetBufferReplaceParam, size 8 | Two separate cleared dwords; compound declaration unproved |
| srcEntityId_ / dstEntityId_ | `0x72C9275 / 0x72C9288` | `+0x14/+0x18`, uint32_t aliases | Owner-selected dwords; original names and domains unproved |
| areaSize_ / dataSize_ | `0x72C929B / 0x72C92AE` | `+0x1C/+0x20`, size_t -> uint32_t | Independently observed capacity and data-length roles |
| pDataBlock_ | `0x72C92C1` | `+0x24`, NetBufferDataBlock pointer | Retail backing-data pointer; original declaration unproved |

ARR NetBufferReplaceParam `0x72C5A64` has keyValue/grpValue at `+0/+4`.
ARR data-block DIE `0x72C7E0D` declares `0xC18` bytes with DataArea_ at zero.
Those names and the data-block declaration are ARR facts only.

ARR allocation body `allocateateNewBuffer_` at `0x1700048`, size `0x118`,
70 PPC instructions, has body/declaration DIEs `0x72CBADC / 0x72C7F97`.
Its signature has the implicit factory object and one size_t parameter. It
increments factory `+4`, requests object size `0x28`, constructs the buffer
inline, stores the sequence/factory at `+4/+8`, clears `+0x0C/+0x10`, sets
capacity to unsigned max(request,`0xC18`) and obtains data through factory
virtual `+8`. Retail's producer calls an out-of-line three-argument constructor
and that constructor directly calls malloc with minimum `0x898`.
The allocation and storage sequences demonstrate a narrow correspondence;
complete function equivalence and failure behavior are not proved.

ARR vtable symbol `0x1A12238`, size `0x18`, has callable address point
`0x1A12240`: two leading zero words and four four-byte descriptor entries.
Each descriptor stores code at `+0`, TOC at `+4`. Descriptors
`0x1B938D0 / 0x1B938D8` resolve to destructors `0x170264C / 0x17026AC`;
`0x1B939D0 / 0x1B939D8` resolve to setDataHeader/fixDataHeader
`0x1703290 / 0x1703294`, both four-byte `blr` bodies. Their declaration
DIEs are `0x72C9402 / 0x72C9427` and body DIEs `0x72EAC74 / 0x72EACA2`.
Retail's shared `ret 4` slots resemble the two no-op hooks, but provide no
independent original names; the slot numbers are not transferable.

ARR's non-deleting destructor `0x170264C`, size `0x60`, calls factory virtual
`+0x0C` with the data pointer, then the base destructor. Its body/declaration
DIEs are `0x72CCE41 / 0x72C92FF`. Retail instead calls free directly,
clears the pointer and optionally deletes the object. Complete allocator,
virtual-hook and destructor correspondence therefore remains unproved.

Confidence is high in the retail owner, object extent, observed cells and
listed roles. Original member names, compound declarations, alignment, complete
identifier/pool semantics, packet meanings, opcodes, runtime behavior and
complete cross-build methods remain unresolved. No BCS-Y identity is promoted.

The [Down specialization](net-buffer-down.md) has independent retail allocation,
constructor and consumer support. Its larger backing capacity does not follow
from this Up layout.
