# ZoneProto buffer-factory partial layouts

Windows 1.23b has independently named Up and Down
`Component::Network::IpcChannel::NetBufferFactoryTmpl_LF` specializations.
Each has six verified four-byte storage cells within its first `0x20` bytes.
The catalog records `at least 0x20`, rather than a recovered complete sizeof.
ARR declares both specializations as `0x20`, with the same constructor storage
pattern, but has a different interface base and virtual dispatch surface.
Original member names and complete function equivalence are not promoted.

`ZoneProtoUp` and `ZoneProtoDown` below mean the types in
`Application::Network::ZoneProtoChannel`. The supported retail partial layouts
are `BCS-S-0499 / BCS-S-0500` in
[the catalog](../../../../manifests/structs.json). Their observed cells are also
recorded inside `BCS-S-0498` at manager-relative offsets in
[RaptureChannelManager](zone-channel-manager.md).

## Inputs and reproduction

| Build | Pinned identity |
|---|---|
| Windows 1.23b | `ffxivgame.exe`, 15,996,808 bytes, image base `0x00400000`, SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9` |
| ARR PS3 | `USRDIR/game/ffxivgame.ppu.self`, SHA-256 `1ab7bc671288463bc312fe1aa8da63742fd48a757bcf7d64715237f44c8c5321`; boot `2014.06.12.0000.0001`, game `2014.06.13.0000.0000` |

ARR's readable ELF is the exact SELF slice at `0x980`, length `0xC12B01C`,
SHA-256 `99ed4e57ea8d7a05c691c843e996ab85a9df51c239b2adc9d10ffe1acaa01537`.
DWARF2 CU `0x72B65A0`, address size 4, identifies
`C:/ffxiv/ffxiv_nightly_win/trunk/prog/server/Application/Rapture/source/Network/ZoneClient/RaptureChannelManager.cpp`.
DIE offsets are `.debug_info` section-relative. Types, references, signatures
and `DW_OP_plus_uconst` offsets were parsed directly. Capstone 5.0.7 decoded
PPC64 big-endian ARR code and x86 32-bit retail code; pefile translated retail
VAs to pinned file bytes. ELF64 does not establish object pointer widths.

Retail Ghidra 12.1.3/JDK 21 exports used the committed read-only scripts below.
First authenticate the named binary with `ghidra/VerifyProgramFileBytes.java`
under the explicit environment described in [Ghidra](../../../../ghidra/README.md).
Require `COMPLETE: program-file-bytes-v1`, matching input, retained
original/modified FileBytes and loaded initialized file-backed ranges.
Unbacked excluded ranges do not support these claims. Assign a new ignored
directory to `$EvidenceOutput`, then run from the repository root:

```powershell
$Targets = '0x00DAFDB0,0x00DAFE50,0x00DB1A40,0x00DB0960,0x00DB0980,0x00DB09B0,0x00DB09D0,0x006CE2E0,0x0095E590,0x00DB0070,0x00DB0200,0x00DB01F0,0x00DB0380,0x00DB0390'
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'factory-decomp.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'factory-listing.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/export-references.ps1 -Addresses '0x00DAFDB0','0x00DAFE50','0x01128F44','0x01128F54','0x01128F74','0x01128F84' -Out (Join-Path $EvidenceOutput 'factory-references.txt')
```

Require every target's successful decompilation, complete listing counts and
the reference wrapper's verified terminal marker. References cover Ghidra's
recorded database; computed, indirect, dynamic and unanalyzed references can
be absent. No client executable was run.

Ghidra treats the free call at `0x009D1B17` as nonreturning. Direct pinned bytes
recover the complete base destructors through their final returns:
`0x00DB0070..0x00DB01E3` and `0x00DB0200..0x00DB0373`, each 372 bytes,
133 instructions. Each listing stops at its first free call and omits the
last 78 bytes, including first-tree cleanup. Deleting-destructor listings
also omit `add esp, 4` at `0x00DB0975 / 0x00DB099B / 0x00DB09C5 / 0x00DB09EB`.
The raw bodies, rather than these truncated decompilations, support teardown.

## Retail identity and layout

| Specialization | Base ctor | Base table / COL / type descriptor | LF table / COL / type descriptor |
|---|---|---|---|
| Up | `0x00DAFDB0` | `0x01128F44 / 0x011A22B4 / 0x0131B860` | `0x01128F74 / 0x011A2394 / 0x0131B9D8` |
| Down | `0x00DAFE50` | `0x01128F54 / 0x011A22FC / 0x0131B8D8` | `0x01128F84 / 0x011A23E0 / 0x0131BA58` |

The exact LF RTTI strings are:

- `.?AV?$NetBufferFactoryTmpl_LF@TZoneProtoUp@ZoneProtoChannel@Network@Application@@@IpcChannel@Network@Component@@`
- `.?AV?$NetBufferFactoryTmpl_LF@TZoneProtoDown@ZoneProtoChannel@Network@Application@@@IpcChannel@Network@Component@@`

Their hierarchies `0x011A23A8 / 0x011A23F4` have two-entry arrays
`0x011A23B8 / 0x011A2404`: LF followed by the matching NetBufferFactoryTmpl.
The base descriptors are LF `0x011A23C4 / 0x011A2410` and base
`0x011A22E0 / 0x011A2328`. All have PMD `(0,-1,0)`, hierarchy flags zero.
The base's own hierarchy contains only itself. Retail RTTI does not list
ARR's NetBufferFactoryInterface; this does not recover a retail source-level
access specifier or prove the absence of every possible unlisted base.

Both base constructors are complete 152-byte, 52-instruction bodies. They
retain ECX as this, install the base table, clear `+4`, then initialize trees
rooted at `+8` and `+0x14`. Manager constructor `0x00DB1A40` passes
`this+0x48 / this+0x68` at `0x00DB1AAE / 0x00DB1AC3` and replaces the
tables with the LF tables at `0x00DB1AB3 / 0x00DB1AC8`. Manager teardown
`0x00DB0390` supplies those same addresses to the corresponding base
destructors at `0x00DB03D9 / 0x00DB03EC`, corroborating ownership and order.
The starts are `0x20` apart. No standalone allocation or array stride was
established, so that spacing is not used to promote a complete factory sizeof.

| Relative cell | Width | Up store | Down store | Supported role |
|---|---|---|---|---|
| `+0x00` | 4 | `0x00DAFDE1`, then `0x00DB1AB3` | `0x00DAFE81`, then `0x00DB1AC8` | Base then LF vptr |
| `+0x04` | 4 | `0x00DAFDE7` | `0x00DAFE87` | Cleared dword; [Up allocation sequence](net-buffer-up.md) independently observed |
| `+0x0C` | 4 | `0x00DAFDEF` | `0x00DAFE8F` | First tree sentinel pointer |
| `+0x10` | 4 | `0x00DAFE07` | `0x00DAFEA7` | Sentinel-adjacent cleared dword |
| `+0x18` | 4 | `0x00DAFE18` | `0x00DAFEB8` | Second tree sentinel pointer |
| `+0x1C` | 4 | `0x00DAFE30` | `0x00DAFED0` | Sentinel-adjacent cleared dword |

Allocator `0x0095E590` requests `0x18` bytes at `0x0095E590..0x0095E592`,
initializes node links `+0/+4/+8` and bytes `+0x14=1 / +0x15=0`, and returns
the pointer in EAX. Each factory constructor independently obtains two nodes,
sets byte `+0x15=1` and makes all three links point back to that node.
The `0x18` allocation belongs to a tree node, not the factory object.

The base destructors read the sentinel pointers at `0x00DB00A7 / 0x00DB0110`
and `0x00DB0237 / 0x00DB02A0`. They traverse both trees and conditionally
invoke the pointed object's slot zero with argument 1, using node `+0x10`
at `0x00DB00EA / 0x00DB0151` and `0x00DB027A / 0x00DB02E1`.
They then erase tree contents and free each sentinel. Raw tail stores clear
the second sentinel/adjacent dword at `0x00DB019B / 0x00DB019E` and
`0x00DB032B / 0x00DB032E`, and the first pair at
`0x00DB01CA / 0x00DB01CD` and `0x00DB035A / 0x00DB035D`.
This supports two owned tree collections; it does not distinguish free from
active buffers, recover insertion/update operations or name the retail cells.

Each partial factory has 24 observed bytes, two unknown four-byte spans
`+0x08..+0x0B / +0x14..+0x17`, and an unresolved trailing extent.
The corresponding manager cells add 40 observed bytes without overlapping
its retained vptrs. The manager allocation remains `0x94`; 86 bytes are now
observed and 62 remain unknown. Alignment and exact original declarations
remain unproved.

## ARR comparison and evidence ceiling

| ARR declaration | Up DIE | Down DIE | Observation |
|---|---|---|---|
| NetBufferFactoryTmpl_LF | `0x72C8042` | `0x72C831A` | Size `0x20`, no direct members; public base at zero |
| NetBufferFactoryTmpl | `0x72C7E3D` | `0x72C8115` | Size `0x20`; public interface base at zero |
| NetBufferFactoryInterface | `0x72C5D7F` | `0x72C5DEC` | Size 4, synthetic vptr at zero |
| currentMaxId_ | `0x72C7E81` | `0x72C8159` | `+4`, BufferID_t -> unsigned long, size 4 |
| freeBufferList_ | `0x72C7E94` | `0x72C816C` | `+8`, BufferMap -> map, size `0x0C` |
| activeBufferList_ | `0x72C7EA7` | `0x72C817F` | `+0x14`, same specialized map type |

ARR maps `0x72BE8D5 / 0x72BF88F` inherit _Tree
`0x72BE0B2 / 0x72BF06C`, with `_Myhead +4 / _Mysize +8` and allocator/
comparator bases in the first four bytes. These declarations explain the
constructor pattern but do not name the retail unknown spans or prove its
container implementation. Those names and the free/active roles stay ARR-only.

ARR constructors `0x16FFB78 / 0x170080C` are each `0x118` bytes, 70 PPC
instructions, with body DIEs `0x72CB9B4 / 0x72CBD25` and declaration DIEs
`0x72C7EBA / 0x72C8192`. The declarations have only the implicit object
parameter. Four-byte stores clear `+4`, publish the two independently
allocated `0x18`-byte nodes at `+0x0C/+0x18`, self-link the nodes and clear
`+0x10/+0x1C`. This demonstrates a narrower construction/storage correspondence
with retail, not identical allocation ABI, exception behavior or full methods.

Retail LF tables have three entries: deleting destructor
`0x00DB0980 / 0x00DB09D0`, followed by the shared one-byte `ret` stub
`0x006CE2E0` twice. Base tables also have three entries, with
`0x00DB0960 / 0x00DB09B0` followed twice by `0x009D364D`.
The next table's COL word bounds each three-entry table; it is not a method.

ARR LF vtable symbols start at `0x1A12480 / 0x1A12590`, each size `0x28`;
callable address points are `+8`. Their eight four-byte entries point to
eight-byte descriptors: code address at `+0`, TOC at `+4`. They contain two
destructors, AllocateDataBlock, DeallocateDataBlock, AllocateBuffer,
ReleaseBuffer, lockForBufferListUpdate_ and unlockForBufferListUpdate_. The
last two resolve to `0x1700804 / 0x1700808` and `0x1701498 / 0x170149C`,
each a four-byte `blr`. Their declaration DIEs are
`0x72C80A4 / 0x72C80C4 / 0x72C837C / 0x72C839C`; body DIEs are
`0x72CBCC9 / 0x72CBCF7 / 0x72CC03A / 0x72CC068`.
Their no-op behavior resembles the retail LF stubs, but the shared retail
target supplies no independent source names. Slot indices are not transferable.

Confidence is high in the retail identities, six storage cells, two sentinel
collections and zero-adjustment RTTI relationship. Complete sizeof, original
names, complete ID semantics, count updates, free/active meanings and complete
allocation/release correspondence remain unresolved. No new function identity, packet meaning,
opcode or runtime claim is promoted.

The [Up NetBufferTmpl layout](net-buffer-up.md) records the named allocation,
constructor, destructor and buffer/data-pointer accesses. Its observed factory
sequence is independently supported by retail bytes; complete pool and
identifier semantics remain unresolved.
