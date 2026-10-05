# ZoneClient RaptureChannelManager layout

The Windows 1.23b `Application::Network::ZoneClient::RaptureChannelManager`
has an allocation-backed extent of `0x94`. Its RTTI inheritance chain matches
ARR's named chain, but ARR declares size `0xB0` and different member offsets.
The retail catalog records a partial layout: supported storage and access
roles are explicit, and unlisted bytes remain unknown. Listed widths describe
observed storage accesses, not recovered original C++ member declarations. ARR member names and
enum meanings are comparison leads, not recovered retail declarations.

## Inputs and method

| Build | Identity |
|---|---|
| Windows 1.23b | `ffxivgame.exe`, 15,996,808 bytes, image base `0x00400000`, SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9` |
| ARR PS3 | `USRDIR/game/ffxivgame.ppu.self`, SHA-256 `1ab7bc671288463bc312fe1aa8da63742fd48a757bcf7d64715237f44c8c5321`; boot `2014.06.12.0000.0001`, game `2014.06.13.0000.0000` |

ARR's readable ELF is the exact SELF slice at `0x980`, length `0xC12B01C`,
SHA-256 `99ed4e57ea8d7a05c691c843e996ab85a9df51c239b2adc9d10ffe1acaa01537`.
DWARF2 CU `0x72B65A0` has address size 4 and source path
`C:/ffxiv/ffxiv_nightly_win/trunk/prog/server/Application/Rapture/source/Network/ZoneClient/RaptureChannelManager.cpp`.
DIE offsets here are section-relative `.debug_info` offsets. References and
`DW_OP_plus_uconst` member and inheritance expressions were parsed directly.
ARR code used Capstone 5.0.7 PPC64 big-endian decoding; retail used x86
32-bit decoding and pefile VA-to-file translation. ELF64 is not a member-width
rule. The observed pointer loads, stores, RTTI and vtable entries are four bytes.

Retail exports used Ghidra 12.1.3, JDK 21 and the committed read-only
scripts `ghidra/VerifyProgramFileBytes.java`, `ghidra/DumpVAs.java`,
`ghidra/DumpFunctionListing.java`, and
`tools/ghidra/export-references.ps1`. Authentication checked the retained
original/modified FileBytes and all loaded initialized file-backed ranges;
excluded unbacked non-executable ranges do not support these claims.
Decompilation signatures were checked against instruction bytes and register
flow. No client executable was run.

For reproduction, configure the explicit project/runtime environment described
in [Ghidra](../../../../ghidra/README.md), authenticate the identified binary,
and run the following from the repository root with a new ignored output
directory assigned to `$EvidenceOutput`:

```powershell
$Targets = '0x004E00E0,0x00DAE5E0,0x00DB1A40,0x00DAFC80,0x00DC1FC0,0x00DAFDB0,0x00DAFE50,0x00DB7C50,0x00DB7640,0x00DAE010,0x004E4C10,0x00DAE520,0x00DB1960,0x00DB11A0,0x00DB11C0,0x00DADF80,0x00DB1C00'
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'layout-decomp.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly -ScriptPath @('ghidra') -Out (Join-Path $EvidenceOutput 'layout-listing.txt') -ScriptEnv @{ XIVL_TARGET_VAS = $Targets }
tools/ghidra/export-references.ps1 -Addresses '0x00DAE5E0','0x00DB1A40','0x01129094' -Out (Join-Path $EvidenceOutput 'layout-references.txt')
```

Require one successful decompilation per target, complete listing counts and a
verified reference-export terminal marker. Direct bytes recover `add esp, 4`
at `0x00DB1C15`, omitted by Ghidra's deleting-destructor listing after the
free call. The pinned full body is 30 bytes, 11 instructions. This omitted
instruction does not change the named destructor or constructor anchors.
RTTI facts below are independently readable from the listed PE data VAs.

## Retail object and inheritance anchors

Vtable `0x01129094` has 25 slots. Its word at `-4` points to complete-object
locator `0x011A2570`, whose type descriptor is `0x0131BD10` and hierarchy
descriptor is `0x011A2584`. The exact type name is
`.?AVRaptureChannelManager@ZoneClient@Network@Application@@`.
The hierarchy's five-entry base array is `0x011A2594`.

| Class in inheritance order | Retail base descriptor | Retail type descriptor | ARR type DIE and declared size |
|---|---|---|---|
| Application::Network::ZoneClient::RaptureChannelManager | `0x011A25AC` | `0x0131BD10` | `0x72EA0BE`, `0xB0` |
| Component::Network::IpcChannel::ChannelManagerOnSingleConnectionTmpl<ZoneProtoUp, ZoneProtoDown> | `0x011A24B4` | `0x0131BB68` | `0x72C856A`, `0xA8` |
| Component::Network::IpcChannel::ChannelManagerTmpl_LF<ZoneProtoUp, ZoneProtoDown> | `0x011A2460` | `0x0131BAD8` | `0x72C83BD`, `0xA4` |
| Component::Network::IpcChannel::ChannelManagerCoreTmpl<ZoneProtoUp, ZoneProtoDown> | `0x011A2298` | `0x0131B7D0` | `0x72C7741`, `0x5C` |
| Component::Network::IpcChannel::ChannelManagerBase | `0x011A1B80` | `0x0131AB88` | `0x72C76A5`, 8 |

ZoneProtoUp and ZoneProtoDown above denote
`Application::Network::ZoneProtoChannel` types. Every retail base descriptor
has PMD `(mdisp=0, pdisp=-1, vdisp=0)`. The hierarchy flags are zero: this
observed chain has no nonzero base adjustment or virtual-base displacement.
ARR inheritance DIEs `0x72EA0D1 / 0x72C858F / 0x72C83E2 / 0x72C7766`
also place the bases at zero; the manager's ARR base is declared public.
RTTI does not supply retail base sizes, access
specifiers or original field names; those ARR base sizes are not promoted.

Factory `0x004E00E0`, complete extent 107 bytes, pushes allocation size
`0x94` at `0x004E0104` and calls `0x009D1B35` at `0x004E0109`. On non-null
return it moves that allocation to ECX and invokes `0x00DAE5E0` at
`0x004E0124`, then publishes the constructor result to its owner's `+0x70`.
This ties the extent to the named manager rather than its connection object.
The complete reference export records that single constructor call site.

Manager constructor `0x00DAE5E0`, 161 bytes, calls base constructor
`0x00DB1A40` at `0x00DAE611`, stores the manager vtable at `0x00DAE625`,
initializes dwords `+0x88/+0x8C` and byte `+0x90` at
`0x00DAE616 / 0x00DAE62B / 0x00DAE631`, and returns the same object.
It separately allocates `0x100` bytes at `0x00DAE61C..0x00DAE637` for
ServiceConsumerConnectionManager, constructor `0x00DB7C50`. That constructor
stores vtable `0x01129768`, locator `0x011A2FA8`, whose RTTI names
`Application::Network::ZoneProtoChannel::ServiceConsumerConnectionManager`.
The manager stores its result at `+8` at `0x00DAE663`.
`0x00DB7640` is called with that connection pointer in ECX, so its `+0xF4`
access is not an access beyond the manager's allocation.

Slot zero is deleting destructor `0x00DB1C00`, which calls `0x00DADF80`.
That destructor stores the manager vtable at `0x00DADFA8`, reads manager
`+8`, and restores a base vtable before calling `0x00DB0390`.
This corroborates owner identity, without claiming a complete lifetime model.

## Supported retail storage

The machine layout is in [the struct catalog](../../../../manifests/structs.json).
Neutral field names retain the distinction between verified retail storage and
ARR source declarations. Pointer targets below describe observed objects;
the catalog uses void pointers where original retail field declarations are absent.

| Offset | Width | Verified retail access or initialization |
|---|---|---|
| `+0x00` | 4 | Manager vptr; named store at `0x00DAE625` |
| `+0x04` | 4 | Base dword cleared by `0x00DC1FC8`; no retail identifier meaning assigned |
| `+0x08` | 4 | Connection-manager pointer stored at `0x00DAE663`; read at `0x00DADFAE` and on the empty-queue path at `0x00DB19A3` |
| `+0x2C` | 1 | Third core-constructor argument stored at `0x00DAFCF5`; no boolean or field-name declaration inferred |
| `+0x30` | 4 | Primary factory pointer stored at `0x00DAFD20`, then dereferenced for its virtual `+4` call at `0x00DAFD56..0x00DAFD68` |
| `+0x34` | 4 | Target factory pointer stored at `0x00DAFD48`; its default allocation is initialized with vtable `0x01128E78` at `0x00DAFD39` |
| `+0x3C` | 4 | Queue sentinel pointer stored at `0x00DAFD50`, loaded and traversed at `0x00DB1969..0x00DB1973` |
| `+0x40` | 4 | Queue count cleared at `0x00DAFD53`; unsigned positive-count test at `0x00DB1963..0x00DB1967` |
| `+0x48` | 4 | Embedded ZoneProtoUp NetBufferFactoryTmpl_LF vptr, store `0x00DB1AB3`, table `0x01128F74` |
| `+0x68` | 4 | Embedded ZoneProtoDown NetBufferFactoryTmpl_LF vptr, store `0x00DB1AC8`, table `0x01128F84` |
| `+0x88` | 4 | Zero-initialized lookup key used by `0x004E4C10`; a nonzero value is required before its two lookups |
| `+0x8C` | 4 | Signed outbound state; zero-initialized, writes 2 on special-send completion and 3 on the inspected receive condition |
| `+0x90` | 1 | Zero-initialized byte; its meaning and additional access widths remain unresolved |

Base constructor `0x00DB1A40` supplies the original object in ECX to core
constructor `0x00DAFC80`. It supplies addresses `this+0x48` and `this+0x68`
to factory constructors `0x00DAFDB0 / 0x00DAFE50`. The final vtable stores
are independently named by the corresponding retail RTTI. Only their vptr
words are declared here; the factory interiors and complete type sizes remain
outside this partial manager layout. Other unlisted constructor writes remain
evidence leads rather than fully identified fields.

State behavior has multiple retail anchors. Existing outbound function
`0x00DAE010` (`BCS-Y-0304`) checks signed `+0x8C`, requires input value 2
in states 1/2, accepts the general path in state 3, and writes 2 at
`0x00DAE17D`. Receive function `0x00DAE520` calls `0x00DB1960` with the
manager still in ECX, and on success reads the buffer pointer at output `+8`
and data pointer at buffer `+0x24`. If the word at data `+2` is 2, it writes
state 3 at `0x00DAE58E`. Slot-5 method `0x00DB11A0` writes 5 unless the
state was 4; slot-6 method `0x00DB11C0` writes 4 unconditionally.
These numeric roles do not recover the retail enum's source names or prove
wire packet meanings. No other state transition or complete dequeue behavior
is implied.

## ARR correspondence and contradictions

| Comparison lead | ARR declaration/access | Retail observation and limit |
|---|---|---|
| Connection pointer | pMyConnectionManager_ `+8`, member DIE `0x72C77CA` | Named connection object stored at `+8`; original member name unproved |
| Constructor control byte | entityGenerate_ `+0x38`, DIE `0x72C7829` | Third core-constructor argument at `+0x2C`; narrower storage/argument correspondence only |
| Primary/target factories | `+0x3C/+0x44`, DIEs `0x72C783C / 0x72C7862` | Factory pointers at `+0x30/+0x34`; field names and deletion flags not transferred |
| Receive queue | receivedBufferList_ `+0x4C`, DIE `0x72C7888` | Traversal rooted at `+0x38`, with observed sentinel/count at `+0x3C/+0x40`; full container type unproved |
| Embedded buffer factories | sendBufferFactory_ `+0x5C`, recvBufferFactory_ `+0x7C`, DIEs `0x72C83EC / 0x72C83FF` | Named Up/Down factory starts at `+0x48/+0x68`; no general offset translation rule |
| Lookup key | mySelf_ `+0xA4`, DIE `0x72C8599`; outbound lookup | Nonzero-key lookup at `+0x88`; retail field name and all writers unproved |
| State | currentStatus_ CLIENT_STATUS enum `+0xA8`, DIE `0x72EA125`; outbound and receive | State at `+0x8C`, with independently recovered retail transitions |
| Option | uint16_t packetOptionParam_ `+0xAC`, DIE `0x72EA139` | Only a byte initialization at `+0x90`; same meaning or a 16-bit retail field is not established |

ARR's single-connection base constructor at `0x17015E4`, size `0xD0`,
52 PPC instructions, receives the manager's bool in r8. It passes the low
byte to core constructor `0x16FCFD0` in r6 at `0x170163C..0x170164C`.
That core body, size `0x238`, 142 instructions, saves r6 in r28 and writes
it to `+0x38` at `0x16FD0FC`. This corroborates the constructor-argument
relationship with retail's byte at `+0x2C`; it does not recover the retail
field's source name. The ARR base also places the factories at
`+0x5C/+0x7C`, stores separate interface arguments at `+0x9C/+0xA0`
(`0x170168C / 0x17016A0`), and clears its key at `+0xA4`
(`0x17016A4`). The retail constructor uses different factory locations;
no separate interface-pointer fields are established by this retail layout.

ARR receive body `popReceievedPacket` at `0x10575CC`, size `0xB4`,
45 PPC instructions, tests the halfword at data `+0` against `0x19A` at
`0x1057640..0x1057648`. Its successful condition writes state 3 to `+0xA8`
and the halfword from data `+6` to `+0xAC` at `0x1057650..0x1057658`.
Retail's complete 181-byte, 54-instruction receive body tests data `+2`
against 2 and only writes state in that condition. Its forwarding body also
lacks ARR's option copy. This is a concrete contradiction to transferring
ARR's option declaration to the retail byte merely because both follow state.
The two input values and header offsets are not a demonstrated opcode mapping.

The canonical outbound functional comparison remains
`xivl-decomp:docs/arr-debug-comparison.md`, ZoneClient outbound packet forwarding.
Confidence is high in the retail owner, allocation extent, inheritance shape
and listed accesses, and in the narrower cross-build member-role relationships.
Only that retail partial layout is promoted. Base sizes, unlisted bytes,
original member names, complete container layouts, the byte's meaning,
exceptions, complete function equivalence and runtime behavior remain unresolved.

The strongest next layout target is the two embedded buffer factories:
retail starts `+0x48/+0x68`, constructors `0x00DAFDB0 / 0x00DAFE50`,
against ARR's named NetBufferFactoryTmpl_LF declarations. Their constructor
and RTTI anchors can establish the interior layout independently of ARR sizes.
