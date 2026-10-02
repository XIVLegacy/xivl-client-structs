# Native pad routing and UI visibility boundaries

The retail pad updater and its first routed-event consumer are identifiable.
They do not establish a gameplay-context predicate. Native Visibility also
has three distinct states, but the named ActionMenu grids still need live
control identity, lifetime, and preference qualification before an override
can use them.

## Binary and method

All native observations on this page apply to this exact x86 executable:

| Identity | Value |
|---|---|
| Executable | `ffxivgame.exe`, retail 1.23b |
| Build | `2012.09.19.0001` |
| Image base | `0x00400000` |
| File size | `15996808` bytes |
| SHA-256 | `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9` |

Addresses below are VAs. Subtract `0x00400000` for RVAs. The observations
are static client evidence, not a runtime acceptance result.

The producing source tools were this repository at
`6acd56635b600129f0ff848d451994666849858e`:
`ghidra/DumpVAs.java`, `ghidra/FindReferences.java`,
`tools/ghidra/export-references.ps1`, and
`tools/verify_reference_export.py`. Read-only Ghidra 12.1.3 exports used the
explicit function addresses in the sections below. Every decompilation
section was checked for its function entry and successful body. Both the
analyzed program's source executable and the independently disassembled
input matched the identity above. The decompiler's recovered signatures
are provisional. ABI statements below use direct instruction inspection
with LLVM objdump 22.1.4, rather than its inferred parameter list.

Reproduce a function export with the environment documented in
[Ghidra](../ghidra/README.md):

```powershell
./tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out <new-local-report> `
    -ScriptEnv @{ XIVL_TARGET_VAS = '<comma-separated-function-VAs>' }
```

For exact references, use `tools/ghidra/export-references.ps1` with explicit
`-Addresses` or `-Strings` and a new output. The verified string export
queried `Visibility`, `Visible`, `Hidden`, `Collapsed`, `ActionMenuWidget`,
`Grid_ActionCommands`, and `Grid_UserMacro`. It scanned 28414 defined
strings, resolved 33 matches, and recorded 42 references. The last three
names had no defined-string match in this database. This excludes only
that analyzed string class, not external UI resources or runtime lookup.
Address references included `0x01356E34`, `0x013596BC`, `0x00914580`,
`0x009145F0`, `0x00914630`, and `0x0091AC80`.

For disassembly use `llvm-objdump -d --x86-asm-syntax=intel
--start-address=<function-entry-VA> --stop-address=<exclusive-end-VA>`
against the hash-checked file. Start at an instruction boundary. The
tracked observations here, not local decompiled output or assembly files,
are the durable evidence.

The focus and property-resolution continuations used the same committed
tools at `6f5fb7b31d51426d29c96202f555ebea5efec848`. Explicit reference
targets were `0x01357020`, `0x01359438`, `0x01359420`, `0x013593D8`,
`0x01359940`, `0x01359450`, `0x0135945C`, and `0x013595B4`. The exact string
queries `_getProperty` and `IsHitTestVisible` resolved two matches and three
references. `ghidra/FindFieldRefs.java` with offsets `0x158,0x159` supplied
instruction candidates only; matching a displacement does not establish
an object's type or a getter contract.

The route-membership, cache-lifecycle, and getter continuations used those
same read-only exporters at `9c8f95dc5af306791400ae81aa9647d0d67be18e`,
with the function and global VAs below. LLVM objdump 22.1.4 supplied the
instruction-level membership, teardown, and setter-policy observations.
These continuations preserve the binary identity and ABI limits above.

The LogicalFocus lookup continuation used the committed exporters and
`ghidra/FindFieldRefs.java` at
`9bfbdb316b5fd2663bab7b2b62c6150b2bdd2eba`. The +0x240 displacement scan
supplied candidates only; complete-object identity came from the constructor
and call paths below. An exact reference export for Parent descriptor
`0x01358B3C` completed with six recorded references. Direct instructions and
bounded PE data reads qualified its initializer and the Window vftable slots.

The child-range qualification used the same committed exporters at
`51be90574ef0e76da4fa432b8e095c5fe9fc574e`. The +0x1FC/+0x260/+0x294/+0x318
displacement scan supplied candidates only. Targeted RTTI covered
LogicalChildrenList, ResourceDictionary, Style, ControlTemplate,
TriggerCollection, TriggerBase, and its SharedItemContainer specialization;
constructor stores and independent PE COL offsets qualified the bases below.
Exact references to Style/Template descriptors `0x01358A30/0x01359118`
completed with nine recorded references. Initializer instructions and string
bytes supplied their names. Direct instructions corrected the decompiler's
removal-call receiver and truncated container-destructor recovery.

The trigger and Template ownership qualification used read-only function
exports and targeted RTTI at `fa7db65570393fb36a681392dbdaa953ca8d883f`.
The ten RTTI records covered Sqwt Trigger, MultiTrigger, CommandTrigger,
EventTrigger, and the TriggersMarkupObject/TemplateMarkupObject classes.
Constructor stores, independently mapped vftable/COL data, and direct
instructions qualified insertion, deleting overrides, and property replacement.

The default-root and name-lookup qualification used read-only function exports
and targeted RTTI at `27e7fdf154698503e6c013d60314c52edf3410fa`.
The exact `.?AVContentPresenter@Controls@Sqwt@@` query returned three records.
Independent PE COL/slot checks and direct instructions qualified the receiver
adjustments, deleting paths, fallback lookup, and cleanup collection below.

The indexed-container ownership qualification used read-only function exports
and targeted RTTI at `d1ca042b9e15a043afaf6a74ba987946552e5f33`.
Exact FormElement, XamlControlContainer, and CloseWindowListener queries returned
four records. Independent PE COL/deleting-slot checks and direct instructions
qualified map publication, ownership transfer, and conditional teardown below.

The name-registration qualification used the same read-only exporters at
`ef29730ca0b72e85bdd5d8efc5058b0b7f59b219`. The +0x298 displacement scan
supplied candidates only. Explicit function exports and direct instructions
qualified the name-map insertion, collision, removal, markup traversal, and
calling-thread collection paths below.

The factory-wrapper qualification used the same read-only exporters at
`455307eb123a2cd68b4ed65d1eb82cc38da7a8dc`. Explicit function targets were
`0x0068DB90`, `0x00536CE0`, `0x00536D20`, `0x005370D0`, and `0x00537350`.
The verified exact reference query for `0x0068DB90` returned no recorded
references. This excludes only references represented by the analyzed database,
not computed, indirect, dynamic, or unanalyzed callers. Direct instructions
qualified the unchanged receiver, original-name lookup, and return paths.

The namespace-owner qualification used read-only exports at
`9cd5fd7618ca2e86d2218b4901441cbec4b0e6c5`. The +0xB4 displacement scan
supplied positive candidates only. Explicit function targets included the
constructor, publication, loader, AutoPtr, and deleting paths below. Targeted
RTTI queried `.?AVXamlElement@Element@Main@Application@@` and
`.?AVLuaDebugOut@LuaDebug@Window@Element@Main@Application@@`.
Constructor instructions and independent PE COL/type/slot checks qualified
the complete and +8 receivers and owning storage.

The call-local route-container qualification used read-only exporters at
`51bf28c4c69a746f71323d9919493b0ad87c80f2`. The 12 explicit function
sections passed entry/body checks. Exact references to `0x01357060/64/68/6C`
completed with 124 recorded references; `0x00F35720` had one recorded
reference. These counts cover the analyzed reference database only.
`ghidra/VerifyProgramFileBytes.java` matched the imported program's retained
original/modified bytes and all seven loaded initialized file-backed ranges
to the executable above. Its excluded unbacked/mapped ranges include the
route globals; this check does not authenticate their runtime contents or
initialization. Direct instructions qualified the contracts below, including
the local destructor tail truncated by the decompiler's free-call annotation.

The TLS context qualification used the same read-only exporters and program
byte verifier at `537e28ecd1700751c51f16f7cf54870e32544a40`. Its 16 explicit
function sections passed entry/body checks. Exact references to
`0x01356E14/0x00919D60` completed with five recorded references, and
`0x009924E0/0x00992570` with three. A bounded byte-pattern search supplied
positive TLS-writer candidates only. Direct instructions qualified context
publication, teardown, and the free-call tails omitted by decompilation.
The same file-backed authentication limits apply to TLS/global runtime state.

The selected-update ownership qualification used those read-only tools at
`4482b53a1f49ceb320a46e09675521ad6aa28c4b`. Its 19 explicit function
sections passed entry/body checks. Exact references to `0x004B3C50`,
`0x004D6570`, `0x004DC3A0`, and `0x004DBE10` completed with four recorded
references. Seventeen assembly reports with 2287 instruction encodings and
receiver/call/data-pointer assertions matched the pinned executable. Direct
instructions qualified M's destructor tail omitted after an annotated free
call. A fresh program-byte verification preserved the authentication limits
above; no TLS/global runtime contents were authenticated.

The enclosing-owner qualification used those tools at
`f2c3e91f140080d2e74bd3ec9bc6b6009ca89d2f`. Its 17 explicit function
sections passed entry/body checks. Exact references to the two Rapture
vftables completed with four references, and four loop/shutdown targets with
seven. Targeted RTTI supplied three Rapture/IRapture records. Independent PE
COL/type/base checks also verified Main's identity and complete receiver.
Fifteen assembly reports with 3113 instruction encodings, receiver/call/table
assertions, and six USER32 import bindings matched the pinned executable.
Fresh program-byte authentication preserved the file-backed limits above.

The owned-module coordinate reconciliation reused the qualified construction
and initialization exports above. Independent PE reads matched all 1224
instruction encodings in their two bounded disassemblies and 28 targeted
receiver/field assertions, including the ten pointer stores listed below.
These checks authenticate static instructions, not initialized runtime objects.

The callback-lifetime qualification used the same read-only exporters at
`5c0935fb00c9a42b6d784484e310409b07682706` for the function entries below.
Independent PE/instruction checks qualified the callback crossings and the
map-erasure and cleanup tails omitted after annotated free calls. Fresh
program-byte authentication preserved the file-backed limits above.

The InputBinding qualification used those exporters at
`9e73ad53de40ef45dc1b23b5e6c68aaac8b5622f`. Field searches for
`0x2170/0x2174/0x2178/0x217C` supplied positive candidates only. Explicit
function exports, independent PE COL/type/base/slot reads, and constructor,
callback, removal, and deletion instructions established the contracts below.
Fresh program-byte authentication preserved the same file-backed limits.

The ancestor-key and Window continuations used the committed tools at
`4168c0faa5fb0f6e15d5d1d45360af0006b2c8f5`. Targeted read-only
`tools/ghidra/ExtractRtti.java` details queried `.?AVWindow@Sqwt@@` and
`.?AVDesktopWindow@Sqwt@@`; constructor stores and direct instructions
qualified the receiver bases below. Exact address references queried
`0x01357208`, `0x01069148`, and `0x0106914C`. Property initializer
instructions and their referenced string bytes supplied the names below.

## Pad receiver and first consumer

Let `M` be the complete `Application::Main::MainModule`, `C = M+0x10` its
embedded RaptureElementContainer, `P = M+0x17C80` its RapturePadDevice,
and `S = M+0xC4 = C+0xB4` its SQWT input interface. These are different
receiver bases. The existing layouts are
[structs.json](../manifests/structs.json), BCS-S-0053, BCS-S-0054,
and BCS-S-0145. The latter is a 0x60-byte embedded object with a 0x2C-byte
state at `P+8` and vftable `0x00FA2B28`.

| Entry VA / RVA | ABI and receiver | Static observation |
|---|---|---|
| `0x004D6570` / `0x000D6570` | ECX = M, three 32-bit stack pointers: pad, mouse, keyboard; `ret 0xC` | Calls the pad updater at `0x004D65B3`, returns to `0x004D65B8`, then calls the keyboard/dispatch helper at `0x004D65C9`. |
| `0x00548210` / `0x00148210` | ECX = P, stack argument 1 = borrowed pad record, argument 2 = M+8 value; `ret 8` | Reads the first record, updates derived state, and copies 44 bytes into P+8 when changed. Its body does not read stack argument 2. |
| `0x00552DF0` / `0x00152DF0` | ECX = M+0x179A8; five 32-bit stack arguments; `ret 0x14` | At the end of keyboard processing calls the common input preprocessors, then mouse and pad vtable slot 1 with the update serial and preprocessor result. |
| `0x00548160` / `0x00148160` | ECX = P; update serial and one-byte preprocessor result in two 32-bit stack slots; `ret 8` | When P+0x5D equals 1 and P+4 is non-null, constructs a stack PadEventArgs, dispatches through [P+4]->vtable+0x34, clears P+0x5D, and destroys the event. |
| `0x004D71C0` / `0x000D71C0` -> `0x0091AC80` / `0x0051AC80` | ECX = S; one borrowed event pointer; `ret 4` | Tail jump from the container's secondary slot 13 into the native event dispatcher. |

Supporting constructor instructions are `0x004DC4D5-0x004DC4E6` in
`FUN_004DC3A0`: pass S to `FUN_005480D0` with ECX=P. That pad constructor
stores S at P+4. `FUN_004DBF40` writes secondary vftable `0x00F911BC`
at C+0xB4, at `0x004DBFB1`. Its slot 13 at `0x00F911F0` contains
`0x004D71C0`. The pad's slot 1 at `0x00FA2B2C` contains `0x00548160`.

`FUN_00548210:0x0054821D-0x0054822D` clears the changed flag at P+0x5D
and copies incoming offsets +0x28 and +0x24 to P+0x5C and P+0x58 even
before its owner check. Those bytes are not gameplay context. Its only
changed-state check is `FUN_00546390`, which examines pad-state differences
through `FUN_00D35350/80/B0`. The updater maps source +0x10/+0x14/+0x1C/+0x18
to P+0x34/+0x38/+0x3C/+0x40, derives axis flags, and copies the record at
`0x005482EC-0x0054831F`. This supports the first copied pad record only.
It does not prove that the second Rapture pad record has no consumers.

### Update serial is not context

`FUN_004DC3A0:0x004DC40D` initializes M+8 to zero.
`FUN_004D6570:0x004D658C-0x004D65CE` passes its current value to mouse,
pad, and keyboard processing, then increments it. The pad updater ignores
that argument. `FUN_009824B0` places the later event argument at event+0x20.
The dispatcher copies it into S+0x3B8, including the pad branch at
`0x0091AD02-0x0091AD05`. These are update/event serial operations, not a
gameplay/chat/menu classification. The broader meaning and all uses of
M+8 are outside this bounded observation.

### Routing and ownership ceiling

`FUN_0091A1C0` delegates to `FUN_00981F50`. That function takes three
32-bit stack arguments and reads the current module TLS block through
`_tls_index`, then TLS+0x1C. It traverses a pointer collection with begin/end
at that context+0x2174/+0x2178, calls each entry's vtable+8, and stops when
one returns exactly 1. The preprocessor result reaches pad dispatch and
marks event bytes +0x14, +0x15, and +0x19 when it equals 1.
It is not a proved gameplay permission value.

`FUN_009824B0` supplies the concrete `Sqwt::Input::PadEventArgs` vftable
and snapshots the pad's getters at vtable offsets +8 through +0x28.
The native initializer `0x00F207E0-0x00F20803` initializes event descriptor
`0x01356E34` with kind 0x56 through `FUN_0097F6C0`. The 0x56 branch of
`FUN_0091AC80:0x0091AD02-0x0091AD2B` replaces event+4 with descriptors
`0x01359438`, then `0x01359420`, calling `FUN_0091EE90` for each.
Their initializers at `0x00F22FA0-0x00F22FF6` name them
PreviewPadChange and PadChange, using strings at `0x0106C11C` and
`0x0106C130`, respectively.
This identifies the first downstream routed pad-event path without command
admission. The shared router uses current source `0x01357020`, obtains a
route collection, assigns event source fields +8/+0xC, dispatches through
`FUN_0091E1C0`, and can stop on event+0x17. The complete focus/modal policy
and the gameplay recipient are not resolved here.

All these calls are synchronous within the invoking Rapture update.
The preprocessor uses that thread's TLS, so another thread cannot safely
substitute its own TLS state. A named OS thread, synchronization with UI
rebuild, and session generation require qualification. P and S are embedded
in M, and are usable only while that instance lives. PadEventArgs is local
to `FUN_00548160`; neither it nor its source pointers may be retained as
handles after the dispatch. Reacquisition is required after M is replaced.

### Selected update owner and context lifetime

Let A be complete `Main`, R=A+0x30 its embedded complete
`Application::Rapture`, and Q=R+4=A+0x34 its `Application::IRapture`
receiver. Main's constructor `FUN_00401750:0x0040177C-0x0040178E` calls
`FUN_004B3B50` with ECX=R. That constructor writes R's complete vftable
`0x00F8CC30` and Q's vftable `0x00F8CC1C` at
`0x004B3B96-0x004B3B9C`. Their COLs `0x01140B1C/0x01140BA4` and
type descriptor `0x012695C0` identify Rapture with complete offsets 0/4;
the base descriptor at `0x01140B88` places IRapture at +4.
Main's vftable `0x00F54A24` has COL `0x0113EB3C` and type descriptor
`0x0126511C`, identifying its complete receiver.

Q's slots +0/+4/+8/+0xC are `FUN_004B2DF0`, `FUN_004B3C50`,
`FUN_004B3830`, and `FUN_004B4380`. The first three use Q unchanged.
The deleting entry subtracts 4 from ECX before reaching complete-R deleting
entry `FUN_004B4390` (`0x004B4380-0x004B4383`).
The initialization slot calls M's
constructor `FUN_004DC3A0` at `0x004B3697` and stores its result at Q+0x64
at `0x004B36AD`. The allocation-failure branch stores zero there.
The update slot loads ECX=M from Q+0x64 at `0x004B3DBE`, passes borrowed
pad/mouse/keyboard records at Q+0x6C/+0xC4/+0xE4, and calls
`FUN_004D6570` at `0x004B3DCC`. This is the update's sole recorded direct
caller. These callback-relative coordinates translate to complete
R+0x68 for M and R+0x70/+0xC8/+0xE8 for the records. They do not validate
readability or lifetime.

`BCS-S-0134` uses complete-Rapture coordinates. Initialization preserves
Q in EDI at `0x004B2E39`; its owned-module result stores therefore translate
as follows. These stores can publish zero on allocation failure.

| Catalog field | Q offset | Complete R offset | Store in FUN_004B2DF0 |
|---|---|---|---|
| pad_device | +0x40 | +0x44 | 0x004B35F6 |
| mouse_device | +0x44 | +0x48 | 0x004B3627 |
| keyboard_device | +0x48 | +0x4C | 0x004B365B |
| file_thread | +0x4C | +0x50 | 0x004B3386 |
| resource_module | +0x50 | +0x54 | 0x004B33C8 |
| font_module | +0x54 | +0x58 | 0x004B351A |
| excel_module | +0x58 | +0x5C | 0x004B33FC |
| scene_module | +0x5C | +0x60 | 0x004B3585 |
| network_module | +0x60 | +0x64 | 0x004B36E7 |
| main_module | +0x64 | +0x68 | 0x004B36AD |

The complete-R constructor preserves R in ESI at `0x004B3B75`, writes
0xFFFFFFFF to R+0x40 at `0x004B3BB6`, and clears R+0x44 through R+0x6C
at `0x004B3BB9-0x004B3BD7`. R+0x40 and R+0x6C have unresolved semantic
roles; the latter is one dword before the unchanged R+0x70 input records.
The row remains fully byte-accounted through its 0x370-byte extent.

The admitted outer path in `FUN_00403640` publishes the constructed A at
`0x013232B8` (`0x004038C1-0x004038D1`), invokes initialization through
`FUN_00402B30`, repeats `FUN_004014B0`, then calls shutdown
`FUN_00401460` (`0x0040391E-0x00403941`). Initialization invokes Q's
slot +0 with ECX=A+0x34 at `0x00403537-0x0040354B`. The loop invokes
slot +4 with that same receiver at `0x00401599-0x004015A2` and
`0x004015BC-0x004015C5`. Its message branch instead calls TranslateMessage
and DispatchMessageW at `0x00401564/0x0040156E`. This connects selected
initialization, update, and normal shutdown to one invoking-thread path.
It does not identify every caller or keep A, M, or H alive across callbacks.

Shutdown invokes Q's slot +8 at `0x00401463-0x0040146C`.
`FUN_004B3830:0x004B38B4-0x004B38CF` passes nonnull M stored at Q+0x64 to
`FUN_004DA620`, reloads that field, conditionally invokes its current
deleting slot with argument 1, then clears it. The cleanup helper passes
C=M+0x10 to `FUN_004D9BC0` at `0x004DA623-0x004DA626` before further
callbacks. Complete R destruction also calls the shutdown implementation directly
with ECX=Q (`FUN_004B3AA0:0x004B3ACB-0x004B3AE4`). Neither field
reload nor the later clear retains the earlier M.

The loop also has a repeat-loop caller `FUN_00401810:0x00401813-0x0040181C`
and callback `FUN_00401730:0x00401730-0x0040173F`, which reloads global A
and enters the loop when nonnull (`ret 0x10`). `FUN_00401B70` requests
SetTimer with this callback at `0x00401BC6-0x00401BD0`, calls MessageBoxW
at `0x00401BE2`, then conditionally calls KillTimer at `0x00401BFE`.
`FUN_00401C20` also requests that timer at `0x004022F6-0x00402300`.
Both requests use timer ID 1 and interval 0x10; their return is not checked
before setting A+0xA to 1. This identifies publication, not timer success,
exact cadence, or gameplay permission during a native modal operation.
The loop's A+0xB byte increment and threshold 8 select message processing
or update (`0x004014F5-0x004014FC`); they are not an active-dispatch lease.

M's constructor calls `FUN_004DBF40` with ECX=C=M+0x10 at
`0x004DC401-0x004DC414`. Its base-constructor chain preserves that
complete C receiver:
`FUN_004DBF40 -> FUN_0091B020 -> FUN_009246F0 -> FUN_00936190 ->
FUN_00938C80 -> FUN_0092F640 -> FUN_0093C750 -> FUN_009405C0 ->
FUN_00912DB0`. At `0x0093C78B-0x0093C78C`, C+0xB4 is a stack
argument; ECX remains C. The last constructor reaches the empty-slot
`FUN_009924E0` initialization qualified under "Additional route membership
and precedence". This binds H initialization to this construction path's
calling thread. The outer path above does not establish an unchanged H
through callbacks, later route-container removal, and destruction.

M's destructor `FUN_004DBE10` passes C to `FUN_004D9BC0` at
`0x004DBE49-0x004DBE4E`; that helper calls `FUN_00919D60` at
`0x004D9BCF`, connecting the raw byte's write of 1 to this cleanup path
without session semantics. M's destructor then passes ECX=P=M+0x17C80 to
`FUN_00919C30` at `0x004DBE8F-0x004DBE9E`. That seven-byte stub writes
vftable `0x00FA2600` and returns; it does not clear P+4 or test active
dispatch. Later, `0x004DBF18-0x004DBF1A` passes C to `FUN_004DBAF0`,
whose normal tail calls `FUN_0091AE80` with ECX=C at
`0x004DBDEC-0x004DBDEE`, reaching the qualified H teardown. The complete
C and M vftables at `0x00F912E4` and `0x00F9142C` point to deleting
entries `0x004DEE50` and `0x004DEE70`, which call those destructors with
unchanged receivers before conditional complete-object free.

Normal M destruction therefore performs this pad base teardown before C/H
teardown. No active-event exclusion or recipient lease is established.
The callback's invoking thread, same-H lifetime, and reentrant effects of
preprocessor/recipient and message callbacks remain required before
using Q, M, P, S, or H across dispatch. In particular, the construction path
does not prove that H survives until the local route container unregisters.

### Callback crossings and context identity

Let H0 be the context initially read by `FUN_00981F50` from the invoking
thread's TLS+0x1C. It keeps the H0+0x2170 collection receiver and a raw entry
cursor. Each iteration reloads current H from TLS and reads H+0x2178 before
comparing H+0x2170 with the original receiver
(`0x00981F90-0x00981FB4`). A mismatch calls `FUN_009D22B4`; it does not
restore H0. The entry's vtable+8 callback at `0x00981FDF` returns in AL.
Exactly 1 exits at `0x00981FE3-0x00981FE6` without another H comparison.
Otherwise the original collection's end is read before the next TLS reload
(`0x00981FE8-0x00981FF9`). These checks require readable contexts and storage
before diagnosing identity drift; they do not retain H0 or its entries.

The diagnostic stub `FUN_009D22B4:0x009D22B4-0x009D22C3` calls
`FUN_009D2290` with five zero arguments and returns if that call returns.
The latter obtains an indirect target through `FUN_009DF187` and tail-jumps
to it when nonzero (`0x009D2293-0x009D22A4`). Its installed target and effects
remain unbound. The diagnostic is not a readable-object or lifetime contract.

`FUN_0091E1C0` receives the event, InputElement I, and three flag bytes in
five 32-bit caller-cleaned stack slots. It tests I+0x64 and can copy
I+0x64/+0x68 into zero event source fields. Descriptor
byte +4 equal to 1 directly invokes I's vtable+0x34 at `0x0091E229`.
Other admitted paths construct another registered stack pair container with
argument 0 (`0x0091E23F-0x0091E244`), collect raw ancestor pointers through
I+0x60, and dispatch through `FUN_0091D210` at `0x0091E32C` before its
normal container teardown at `0x0091E338`. A flag-dependent vtable+0xC
eligibility call at `0x0091E284` precedes the next ancestor read at
`0x0091E2A6`. The outer pad route supplies its third flag as 1; that path
skips this eligibility call. Neither path establishes a recipient lease.

`FUN_0091D210` takes the event and container in two caller-cleaned stack
slots. Descriptor byte +4 values 1/2 walk pairs forward; 0 walks backward.
It invokes each nonnull pair's first dword through vtable+0x34, and stops
when event+0x17 is nonzero (`0x0091D2A6-0x0091D2B0`,
`0x0091D2FC-0x0091D302`). The outer `FUN_0091EE90` instead tests that
byte for exactly 1 at `0x0091F1A1`. These are scoped stop rules, not a
modal or gameplay-precedence classification.

Context drain `FUN_00991160` calls `FUN_0095F2A0` on its first recorded
entry. The latter uses that object's +0x3C as H when nonzero, otherwise current
TLS+0x1C (`0x0095F2A6-0x0095F2BE`), erases a found entry from H+0x21B0,
then tail-jumps to `FUN_0095EC70` at `0x0095F30E`. The erasure's normal
tail decrements that map's count after freeing its node
(`0x0096009B-0x009600AD`). Cleanup invokes each nonzero stored node+0x10
pointer's vtable slot 0 with argument 1 before clearing it
(`0x0095ECC7-0x0095ECE0`). This reaches a virtual cleanup call while the drain
caller still holds its original H. Concrete slot-0 implementations and their
effects on H, TLS, M, and registered containers remain unqualified.

The pad dispatcher reuses its original S after PreviewPadChange returns to
call the PadChange route (`0x0091AD1A-0x0091AD24`). On dispatch return,
`FUN_00548160` writes zero to the original P+0x5D at `0x005481DC`.
Thus P/S must survive these callbacks, and each registered stack container
requires the same surviving H until unregistration. The inspected identity
checks and normal teardown ordering do not prove callback exclusion from
owner/context destruction or TLS replacement. The concrete selected
preprocessor, recipient, and cleanup implementations remain the missing edges;
no actual overlapping teardown is established by these static paths.

### InputBinding registration and inert preprocessor slots

Let B be the complete InputBinding receiver. Its primary vtable is
`0x01076C54`, COL `0x0117DF34`, complete-object offset 0, and type descriptor
`0x0126E36C`, `.?AVInputBinding@Input@Sqwt@@`. Its SharedItem bases have
displacement 0. Constructors `FUN_00982170` and `FUN_00982300` use ECX=B
and seven 32-bit stack arguments, ending in `ret 0x1C`. Both preserve the
upper bits of B+0x9C and pack the low bits of arguments 5/6/7 into masks
1/2/4 (`0x009821F7-0x0098223F`, `0x00982383-0x009823CC`).

When mask 4 is set, each constructor reads the invoking thread's TLS+0x1C
as H and calls `FUN_00813050` with ECX=H+0x2170 and the address of a local
dword containing B (`0x009822AF-0x009822DC`,
`0x0098243E-0x0098246C`). These sequences have no H-null guard. The helper's
available-capacity path copies that dword into the end entry and advances
the end by 4 (`0x00813079-0x0081308E`). Its growth path calls
`FUN_008CFC80` at `0x008130AC`; that helper calls `FUN_007A07C0` at
`0x008CFCD0`. Growth ownership effects remain unqualified here. The separate
SharedItem membership operations earlier in each constructor are not an H
registry retention contract. Registration records no H owner alongside B.

`FUN_00982010` uses ECX=B and tests the same mask at `0x00982043`.
When set, it searches the current thread's H+0x2170 collection for the first
dword equal to B (`0x00982058-0x009820BD`). It reloads H during the search
and removal, with identity diagnostics after dependent reads. A found entry
shifts later dwords at `0x00982110` and decrements the end by 4 at
`0x00982118`, before embedded-member and base teardown. It does not use a
saved registration H. Changing thread or TLS context before destruction is
therefore not qualified as safe. Slot-0 deleting entry `FUN_00982490` calls
this destructor on B and conditionally frees B when its argument's low bit
is set (`0x00982493-0x009824AB`).

The inspected concrete primary vtables share the same slot +8:

| Type / vtable | Complete receiver proof | COL / type descriptor | Slot 0 |
|---|---|---|---|
| InputBinding / `0x01076C54` | Constructors above | `0x0117DF34` / `0x0126E36C` | `0x00982490` |
| KeyBinding / `0x00FC49BC` | `FUN_0069BE80:0x0069BECB-0x0069BEDA` calls the base constructor on unchanged B, then stamps this vtable | `0x01158D10` / `0x012BB444` | `0x0068B660` |
| MouseBinding / `0x0106D658` | `FUN_00973190:0x009734FA-0x00973514` constructs B=ScrollViewer+0xB88, then stamps this vtable | `0x01179F5C` / `0x012E1430` | `0x0094C2F0` |

KeyBinding/MouseBinding type names are `.?AVKeyBinding@Input@Sqwt@@` and
`.?AVMouseBinding@Input@Sqwt@@`. Their COL offsets and InputBinding base
displacements are 0. All three slot +8 entries point to `FUN_00981F40`,
whose entire body is `xor al,al; ret 0xC` (`0x00981F40-0x00981F45`). It
reads no receiver or arguments, invokes no callback, and returns zero in AL.
Upper EAX bits are not a result contract. Thus this slot cannot produce
the preprocessor's exact-1 stop for these vtables. It does not classify text
entry, modality, session validity, or recipient slot +0x34 behavior.

ScrollViewer's primary vtable `0x010733D4` has COL `0x0117D30C`, offset 0,
and descriptor `0x012E45A4`, `.?AVScrollViewer@Controls@Sqwt@@`; its store
at `0x009731F3` anchors the enclosing complete receiver above.
The inspected ScrollViewer construction supplies zero for arguments 5/6/7
(`0x009734EC-0x009734EE`), so this MouseBinding instance does not take the
H registration branch. The KeyBinding and MouseBinding deleting entries
call `FUN_00982010` on the unchanged complete B and conditionally free B
(`0x0068B696-0x0068B6BD`, `0x0094C2F9-0x0094C311`). These normal teardown
paths do not retain H or exclude dispatch during destruction. The actual
selected entry's type, registration flags, invoking thread, readable storage,
and same-H lifetime remain required. Other derived slot +8 implementations
and recipient/cleanup callback effects are not established by these vtables.

### Borrowed native keyboard-focus recipient

The current source at `0x01357020`, RVA `0x00F57020`, is a native
InputElement keyboard-focus recipient. This identifies its UI role, not
whether gameplay is permitted. The focus transition in `FUN_0091E3E0`
uses PreviewGotKeyboardFocus (`0x01359450`), GotKeyboardFocus
(`0x0135945C`), and LostKeyboardFocus (`0x013595B4`). Their names and kinds
are initialized at `0x00F23180-0x00F23206`, using strings at
`0x0106C1B4`, `0x0106C1CC`, and `0x0106C1E0`.

Let `I` be the InputElement receiver. For the inspected UIElement, Window, and
DesktopWindow objects, `I = complete object+0xB4`. The DesktopWindow
constructor establishes that adjustment at `0x0091B05B` and invokes the
focus transition with it at `0x0091B38D-0x0091B38F`. Do not apply this
adjustment to an arbitrary InputElement type without its own layout proof.

| VA / RVA | ABI | Observation |
|---|---|---|
| `0x0091C4A0` / `0x0051C4A0` | ECX=I; no stack arguments; EAX=0 or 1; `ret` | Tests exact equality with the current recipient. |
| `0x0091C4B0` / `0x0051C4B0` | ECX=I; no stack arguments; boolean in AL; `ret` | Tests I against the current recipient and its +0x60 ancestor chain. Upper EAX bits are not a boolean contract. |
| `0x0091E3E0` / `0x0051E3E0` | ECX=I; no stack arguments | Validates native eligibility and focus routing; its accepted transition stores I at `0x0091E75C`. This is a mutating native operation, not a diagnostic reader. |
| `0x0091DBD0` / `0x0051DBD0` | ECX=I; no stack arguments | InputElement destruction clears the global at `0x0091DC8D` if it still equals I, then updates dependent focus state. |

`FUN_0093AC10:0x0093AC3B,0x0093ACAC-0x0093ACB3` supplies the
UIElement+0xB4 receiver to that destructor. A same-thread copy of the current
token can therefore identify the native focus recipient for one observation;
it cannot keep the object alive or make an asynchronous pointer usable.
There is no generation or synchronization proof for retained tokens.
The equality helpers neither validate their receiver's lifetime nor supply
chat, modal, or session semantics. A null token is not gameplay permission.

The recipient exists independently of command admissions. The remaining
classification requires the actual recipient/ancestor types and their native
roles across gameplay, chat, menus, modals, and invalid sessions, correlated
at the selected-pad boundary. Keyboard focus alone does not establish all
pad routing: `FUN_0091ED80` also constructs the route collection used by
`FUN_0091EE90` from `0x01357060` and the desktop root.

### Additional route membership and precedence

The collection at `0x01357060` has begin/end/capacity pointers at
`0x01357064/68/6C`. The membership paths traverse eight-byte entries,
using the first dword as a route key and entry+4 as a recipient pointer.

`FUN_0091C370:0x0091C370-0x0091C3AC` produces the key with ECX=I,
no stack arguments, EAX=pointer, and `ret`. It follows I+0x60 parents,
returning the ancestor immediately below the desktop root's InputElement;
the root itself returns itself. A null input returns null. With a root
present, a chain ending before reaching it returns null. With no root,
the last non-null ancestor returns as the key. The key is therefore a
pointer into the native input tree, not a role or session identifier;
a non-null key does not prove that a desktop root or gameplay session exists.

| Entry VA | ABI | Membership operation |
|---|---|---|
| `0x0091DDC0` | ECX=key, one 32-bit stack recipient; acceptance in AL; `ret 4` | Replaces entry+4 when the key exists; otherwise inserts the pair at the beginning. |
| `0x0091DEC0` | ECX=key, no stack arguments; result in AL; `ret` | Moves an existing pair to the beginning without changing its recipient; returns 0 if absent. |
| `0x0091DFB0` | ECX=I, no stack arguments; result in AL; `ret` | Derives the key, removes its existing pair if found, and inserts `{key,I}` at the beginning; returns 0 for a null key. |

The accepted focus transition in `FUN_0091E3E0:0x0091E6A4-0x0091E758`
tests key+0x70 mask `0x08`. When clear it removes any matching pair and
appends `{key,I}`. When set it inserts a missing pair at the beginning or
updates the existing recipient in place. The mask's semantic owner remains
unqualified; it is not a proved modal field.

`FUN_00CB1120` inserts through `FUN_00CB0EC0`; `FUN_00CB1530` appends.
Their pair-copy helpers `FUN_00965AD0`, `FUN_009873E0`, `FUN_006D0970`,
and `FUN_00965AA0` copy the two dwords without recipient calls or
retain/release operations. `FUN_00A76BE0` shifts later pairs and subtracts
eight from the end pointer. Growth copies into new storage, frees the old
begin pointer, and replaces begin/end/capacity at
`FUN_00CB0EC0:0x00CB1007-0x00CB1023`. These are raw borrowed pointers.
Neither an entry address nor a copied recipient is a lease: mutation can
shift entries or replace their buffer, and copying does not extend object life.

One concrete registration owner is `Sqwt::Window`. Its constructor
`FUN_009246F0:0x00924724-0x00924734` stores complete-object vftable
`0x0106A0BC`, InputElement vftable `0x01069F94` at +0xB4, and the
secondary +0x194 vftable `0x01069F7C`. It registers `FUN_009238A0`
as a property callback. LogicalFocus is descriptor `0x01357208`, index
`0x0A`, initialized at `0x00F20C20-0x00F20C39` from string `0x01069D44`.
That callback's index-0x0A branch at `0x00923AB8-0x00923ADD` registers
the Window's own I when its stored name is empty. Otherwise
`FUN_00922AC0:0x00922AC6-0x00922B04` resolves the name from Window+0x3C0
through `FUN_00910980` with fallback enabled, adds +0xB4 to the result,
and registers it under the Window's I key. This proves a Window key with a
name-resolved target with the mechanical lookup scope below. Concrete target
type, live role, and lease remain unqualified.

`FUN_00910980:0x00910980-0x00910A0B` takes a lookup receiver in ECX and
three 32-bit stack slots: a key-sequence pointer, a fallback byte, and an
excluded receiver. It returns a raw pointer or zero in EAX and ends in
`ret 0x0C`. The sequence count is at sequence+0x28; zero count returns zero.
For each key it invokes receiver vtable+0x20 with the key address and excluded
receiver, then uses the result as the next receiver. Only fallback byte 1
permits a failed sequence to restart through the current attempt's starting
receiver's vtable+0x0C. Zero or equality with global `0x01356B90` stops that
restart.
Otherwise it retries the full sequence on that pointer and passes the previous
receiver as the exclusion argument.
That global comparison is a lookup boundary, not session validation.

The Window complete-object vftable's +0x20 slot at `0x0106A0DC` is
`FUN_00910A10:0x00910A10-0x00910A6F`. It first compares the key dword with
receiver+0x1C and can return the receiver itself. Otherwise it enumerates
vtable+0x14 count and vtable+0x10 indexed results in increasing order,
skips the excluded pointer, tests result+0x1C, and recursively invokes that
result's +0x20 slot with exclusion zero. The first nonzero match wins.
Window's count/index slots are `FUN_00937170/140`. They enumerate the
`FUN_0092C2F0/0092D680` ranges before an optional stored pointer at +0x318.
`FUN_0092D680` returns stored pointers for its first two ranges and applies
+0x18 to a nonzero pointer from its third range. Thus these accessors do not
by themselves prove every result is a complete UIElement or that the search
is confined to the original Window's visual descendants.

For the inherited FrameworkElement/Control paths, let C be the complete
control, S its stored Style pointer, T its stored Template pointer, K a
collection, and P a stored entry. The indexed families are:

| Range | Storage and result | Qualified family |
|---|---|---|
| Logical children | C+0x264/+0x268 bound four-byte entries; returns P unchanged | FrameworkElement logical-child pointers; embedded LogicalChildrenList at C+0x258 has vftable `0x0106AB38` and IEnumerator<FrameworkElement &> RTTI. |
| Resources | K=[C+0x294], K+8/+0xC bound four-byte entries; returns P unchanged | Complete ResourceDictionary-derived pointers; the base's complete/shared-item receivers are P and P+0x24. |
| Style triggers | S=[C+0x1FC], S+0x2C/+0x30 bound four-byte entries; returns nonzero P+0x18 | Embedded TriggerCollection at S+0x24 stores TriggerBase pointers; +0x18 is DependencyObject in the qualified TriggerBase base layout. |
| Optional Template | T=[C+0x318]; returns T unchanged after the three ranges | A concrete ContentControl construction path supplies a ControlTemplate to the Template setter; the current stored instance still needs qualification. |

`FUN_0092F640:0x0092FA6D-0x0092FA86` initializes the logical-child list
and its range. Parent attach `FUN_009313C0:0x00931478-0x00931482`
appends the complete child through `FUN_00813050` on C+0x260. Detach
uses `FUN_0092CB70` on C+0x258 to compact entries and reduce the end
pointer. `FUN_009314E0:0x00931542-0x0093156B` frees the pointer buffer
and zeros its bounds. These establish mutable pointer storage, not ownership
of every child or a lease on an indexed child.
The resource collection's membership, conditional final-member deletion,
and FrameworkElement cleanup are already qualified in
[the presentation manifest](../manifests/s2c_018d_map_marker_presentation.json),
`resourceCollectionOwnership`. Those rules apply to the inherited collection;
they do not bind a particular LogicalFocus result.

Style descriptor `0x01358A30`, index `0x0F`, is initialized from string
`0x0106A998` at `0x00F21FE0-0x00F21FF9` and bound to C+0x1FC by
`FUN_0092F640:0x0092F835-0x0092F84E`. The index-0x0F branch in
`FUN_00930440:0x009307FD-0x00930842` constructs a Style through
`FUN_009A6230` (vftable `0x0107BFFC`) and passes it to `FUN_0092F220`.
This identifies a producer, not universal setter admission or the current S.
FrameworkTemplate constructors `FUN_0099B1C0/0099B3A0` initialize
TriggerCollection at receiver+0x24 through `FUN_009C27B0`, whose vftable
is `0x01082664`. TriggerBase constructor
`FUN_009C2620:0x009C2662-0x009C268E` constructs DependencyObject at
P+0x18 and stores complete/adjusted vftables `0x01082650/0x01082614`.
Their COLs `0x01182270/0x01182284` have offsets 0/+0x18. TriggerBase,
ResourceDictionary, Style, and ControlTemplate base RTTI includes
DependencyObject and contains no InputElement base. Their occurrence in a
name-search range cannot justify the registration site's mechanical +0xB4.

TriggerCollection teardown `FUN_009C2610 -> FUN_009C27E0` clears memberships
through `FUN_00557C70`, frees its entry buffer, and zeros the bounds.
Removal `FUN_005580F0:0x00558198-0x005581A2` calls stored P's vtable+4
with K; in the TriggerBase base vftable that slot is `FUN_0094C3A0`.
A matching membership decrements the word at P+0x14.
A zero result with P+0x16 mask 1 set invokes
P's deleting slot; the TriggerBase base vftable selects
`FUN_009C2890 -> FUN_009C25A0`, then frees P. Concrete markup-produced
families qualify that rule further:

| Sqwt class | Allocation / constructor | Complete / +0x18 vftables | Complete deleting slot |
|---|---|---|---|
| EventTrigger | `0x7C` / `FUN_009B1BD0` | `0x0107D554 / 0x0107D518` | `FUN_009B21D0` |
| CommandTrigger | `0xC4` / `FUN_009B1110` | `0x0107D2D4 / 0x0107D298` | `FUN_009B1490` |
| Trigger | `0x9C` / `FUN_009B0990` | `0x0107D0D8 / 0x0107D09C` | `FUN_009B0F10` |
| MultiTrigger | `0x9C` / `FUN_009AFE40` | `0x0107CE8C / 0x0107CE50` | `FUN_009B0330` |

`FUN_009495E0`, the +8 slot of TriggersMarkupObject vftable `0x0106D9F0`,
creates these four classes and inserts each result into K=T+0x24,
where T is loaded from markup receiver+0x74. The insertion calls are at
`0x00949698/0x0094973F/0x009497D0/0x00949856`. For these producer paths,
P is the complete allocation and P+0x18 is DependencyObject; the COL offsets
are 0/+0x18, and none of the four base hierarchies contains InputElement.
All four complete vftables share `FUN_0094C3A0` at +4. Their deleting slots
reach `FUN_009B1A00 -> FUN_009C25A0` through the respective derived
destructors (CommandTrigger also uses `FUN_009547D0`) and free complete P
when the deleting argument's low bit is set.

`FUN_0094E1D0` takes K in ECX and P in one stack slot, ending in `ret 4`.
At `0x0094E1E0-0x0094E202` it appends P through the K+4 vector receiver,
sets P+0x16 mask 1, appends K through the P+4 membership-vector receiver,
and increments the word at P+0x14. `FUN_0094ED00` then removes K's first
entry through K's +4 virtual slot when K+0x18 mask 2 is set and the resulting
count exceeds one. In the qualified TriggerCollection that is
`FUN_005580F0`, so insertion can release and delete an older final-member
trigger. These are owning memberships with conditional eviction; they provide
no external lease. The selected instance's class and other memberships remain
unbound, and copying P or P+0x18 does not extend its lifetime.

Template descriptor `0x01359118`, index `0x11`, is initialized from
`0x0106B994` at `0x00F22640-0x00F22659` and bound to C+0x318 by
`FUN_00938C80:0x00938E94-0x00938EAE`. ContentControl constructor
`FUN_00936190:0x009362E3-0x00936306` constructs FrameworkTemplate,
stamps ControlTemplate vftable `0x00FCB0BC`, and supplies it to
`FUN_00938140`. Its inherited count/index slots `FUN_0099B0C0/0099B4B0`
enumerate only the raw T+0xB0 root when nonzero; without that root they
enumerate the embedded trigger collection at +0x24 and return P+0x18.
The default constructor's root is qualified below; an arbitrary current root's
concrete type remains unbound. FrameworkTemplate destructor
`FUN_0099B0F0` conditionally invokes `FUN_0093CC70` on the root and destroys
its TriggerCollection. FrameworkElement and Control teardown can delete stored
Style/Template objects through their property flags
(`0x00931660-0x00931679`, `0x00936CB2-0x00936D35`).

Template setter `FUN_00938140` passes C+0x318 to `FUN_00926F10`, together
with C, descriptor `0x01359118`, and callback `FUN_00937A70`.
On an admitted changed value, `0x00926F6E-0x00926FA0` copies the previous
pointer to C+0x31C, copies the former ownership mask 8 to mask 0x20 in
C+0x320, marks the change, and stores the new pointer at C+0x318.
Notification byte 1 reaches the callback through `FUN_00926DA0` on the
calling thread. After notification, C+0x320 masks 0x10 and 0x20 with a
non-null previous pointer permit `FUN_00915680` deletion. Admission and pending
resolution are still part of the property engine; these observations authorize
no direct storage write or choice of override policy.

The callback's index-0x11 branch at `0x00937C3A-0x00937C7F` compares the
previous C+0x31C value with cached C+0x334. When they differ, mask 0x20
and a non-null previous value permit its deleting slot with argument 1.
When they match and the previous template has a root at +0xB0, it calls
`FUN_00940800` and Parent detach `FUN_0092FBE0` on that root. Both paths
then call `FUN_00936DF0` with C.
That helper uses the current C+0x318 value. Its two admitted cache-update
paths (`0x00936E5F-0x00936EAF`, `0x00936ECC-0x00936F2C`) dispatch C's
virtual +0x10C with old/new templates, conditionally delete the old cached
value under C+0x338 mask 1, store the new value at C+0x334, and copy
C+0x320 mask 8 to C+0x338 mask 1. The root path tests the raw dword at
root+0x240 for zero before calling `FUN_00940B30` and `FUN_009313C0`.
The latter's pending resolution and conditional Parent-store rules below
still apply; the raw-zero check does not establish a resolved unattached state.
A null current Template returns without clearing the cached value.
Thus C+0x334 is not an unconditional current-template reader. Property changes
can invalidate both a searched subtree and its holder; their concrete current
identity, virtual overrides, and same-thread lifetime still need qualification.

The default ContentControl path allocates a 0x2C4-byte root R and calls
`FUN_0099D650`, which first constructs FrameworkElement and stamps the
ContentPresenter vftables at `0x0099D6A0-0x0099D6B0`. RTTI identifies
`Sqwt::Controls::ContentPresenter`, TypeDescriptor `0x012E0C74` and CHD
`0x0117FF04`, with FrameworkElement/UIElement and InputElement bases.

| Receiver | Vftable | COL / complete-object offset | Deleting entry |
|---|---|---|---|
| R | `0x0107A9B4` | `0x0117FEF0` / 0 | `FUN_0099D8E0` |
| R+0xB4, input interface | `0x0107A88C` | `0x0117FF60` / 0xB4 | `FUN_0099D8D0` |
| R+0x194, secondary interface | `0x0107A878` | `0x0117FF74` / 0x194 | `FUN_0099D8C0` |

The secondary deleting entries subtract their listed offsets before reaching
`FUN_0099D8E0`. That entry calls destructor `FUN_0099C890`, whose base teardown
calls `FUN_009314E0` at `0x0099C965`. The deleting entry then frees complete R
when its argument's low bit is set. R's +0x20 lookup slot is `FUN_00910A10`.
`FUN_0099B1C0`, with ECX=T and owner/root in two stack slots (`ret 8`), stores
a supplied non-null R at T+0xB0 and sets T+0xCD to 1 at
`0x0099B287-0x0099B28E`. This qualifies this constructor path, not the current
ActionMenu root or a markup-selected root. For markup-selected roots,
`FUN_0099AF80` and TemplateMarkupObject's +8 slot `FUN_0094AD90` are producer
candidates; concrete factory results and root publication remain unqualified.
ContentPresenter's name and interfaces do not establish a gameplay or
text-entry role.

Root cleanup `FUN_0093CC70` takes R in one caller-cleaned stack slot and reads
the current thread's TLS context at +0x1C. A null context returns immediately.
Otherwise it invokes the Visibility engine, then, when raw R+0x240 is nonzero,
calls `FUN_00940800` and `FUN_0092FBE0` using that stored parent. It searches
the context's +0x2028/+0x202C pointer range and appends R through the +0x2024
container when absent (`0x0093CCDC-0x0093CD83`). It does not directly invoke
R's deleting slot. Its callbacks, the collection's later consumer, and the
selected root's lifetime remain unqualified. This establishes a calling-thread
dependency, not a named UI thread or a lease through deferred work.

The Window +0x0C slot at `0x0106A0C8` is `FUN_0092B5D0`, which returns
the stored dword at complete object+0x240 without resolving property flags.
The FrameworkElement constructor `FUN_0092F640:0x0092F992-0x0092F9B0`
registers that storage with descriptor `0x01358B3C`; initializer
`0x00F21D50-0x00F21D73` names it Parent from string `0x0106A8F4`.
`FUN_009313C0` receives a parent in ECX and a child in its one stack slot
(`ret 4`); its admitted update stores the parent in child+0x240 at
`0x0093145B`. Detach `FUN_0092FBE0` can clear that storage at `0x0092FCC0`.
Both paths resolve pending mask 0x80 at child+0x248 and gate their direct
storage updates on mask 0x03. These are mutation edges, not a lifetime lease.
The raw lookup result is registered with +0xB4 at
`0x00922AF8-0x00922B04` without a concrete-type check there. Qualifying each
selected result's vftable, complete-object base, virtual lookup override,
replacement/destruction, and same-thread lifetime remains necessary before
reading it or using it to classify pad recipients. Captured tokens remain
opaque.

IsModal is descriptor `0x0135722C`, index `0x0B`, initialized at
`0x00F20C40-0x00F20C59` from string `0x01069D54`. Its Window callback
branch at `0x00923AE2-0x00923AFD` checks I's vtable+0x5C result before
calling the mutating focus-selection helper `FUN_00923190`.
`FUN_00922C20` and `FUN_00922E10`, reached through `FUN_00923020`,
select/count registered Window candidates using complete object+0x3C8
mask `0x20` together with that virtual result equaling 1. These paths
narrow the modal-selection investigation, but do not qualify a resolved
IsModal reader or connect the selected Window to each pad recipient.
The registration containers and virtual eligibility contract also need
construction, invalidation, and same-thread lifetime qualification.

`FUN_0091D930` locates entries by their first dword and passes a matching
entry to `FUN_00A76BE0`. `FUN_0091DBD0` zeros the first matching entry+4
recipient when found, and clears the current-focus token when it equals
the destroyed object. Global teardown `FUN_00F35720`
releases the collection's begin pointer and zeros begin/end/capacity.
When the TLS+0x10 dword is nonzero, the InputElement child-detach path
`FUN_0091D9D0` removes a detached desktop child's key. For another parent,
it can replace entry+4 with the derived key when the removed child is the
recipient or its ancestor. `FUN_0091C3B0:0x0091C3B0-0x0091C3CA` tests
that relation by walking the stack recipient's +0x60 chain against ECX,
returning a boolean in AL and ending in `ret 4`. These are synchronous
cleanup paths; the local route snapshot used during dispatch does not retain
recipients. Concrete named-recipient construction/replacement and a recipient
lease remain unqualified. Do not traverse this collection asynchronously.

For this local-container contract, let L be the stack route container in
`FUN_0091EE90` and H the context pointer at the calling thread's TLS+0x1C.
At `0x0091EEDC`, the router constructs L through `FUN_00921450` with
ECX=L and one byte argument, 1 (`ret 4`). The constructor zeros L+4/+8/+0xC
(pair begin/end/capacity) and stores that byte at L+0x10. At
`0x0092149E-0x009214AC`, it calls `FUN_0096C140` with ECX=H and a
stack pointer to L's address. That helper appends a raw dword to H's
+4/+8 range, growing through `FUN_0096C090` when needed. Registration
stores L's address; it does not retain its borrowed recipients.

On the normal route exit at `0x0091F1BD-0x0091F1C1`, ECX=L reaches
`FUN_0091FAD0`. That destructor reads the calling thread's TLS+0x1C,
searches H's raw dword range for L, shifts later entries when found, and
decreases H+8 by four. It then frees nonnull L+4 and zeros L+4/+8/+0xC
(`0x0091FB8F-0x0091FBA9`, no stack argument). Neither constructor nor
destructor guards a null H. This requires a surviving calling-thread
context; it does not identify a named UI thread, prove cross-thread invalidation,
or supply a selected-recipient lease. The generic context paths below do not
prove that selected pad dispatch and context teardown cannot overlap.

`FUN_009924E0` takes one caller-cleaned pointer argument and uses the calling
thread's TLS+0x1C. If H is already nonnull it leaves that slot unchanged.
Otherwise it publishes a nonnull supplied pointer directly, without invoking
the constructor or checking its type. With a zero argument it requests 0x30B4
bytes through `FUN_009D1B35`, calls `FUN_00991AA0` with ECX=the nonnull
allocation, and publishes its result (`0x00992511-0x0099254A`). A zero
allocation publishes zero; this path supplies no nonnull-result guarantee.
The constructor returns the complete allocation and zeros its route-registry
begin/end/capacity at H+4/+8/+0xC (`0x00991ACD-0x00991AD3`). Recorded
constructor caller `FUN_00912DB0:0x00912E79-0x00912E8A` invokes this
factory with zero only when its calling-thread slot is empty, then reads H.

Teardown `FUN_00992570` first calls `FUN_00991160` with ECX=current H
before any H-null guard (`0x00992580-0x00992587`). That helper reads
H+0x21B8 and loops through `FUN_0095F2A0` while that dword is nonzero;
its drain and virtual-cleanup edges are qualified under "Callback crossings
and context identity", but concrete callback effects remain unqualified.
Teardown then reloads H from TLS, calls
`FUN_00991270` with ECX=nonnull H, frees H, and clears TLS+0x1C
(`0x0099258C-0x009925A6`). The destructor's route-registry tail frees
nonnull H+4 and zeros H+4/+8/+0xC (`0x00991A6F-0x00991A85`). That tail
does not iterate the registered L addresses. The recorded caller
`FUN_0091AE80:0x0091AEF6` reaches teardown before clearing the desktop-root
global at `0x0091AEFD`. This qualifies these storage teardown edges, not
dispatch exclusion or a lease across their earlier callbacks.

The other factory caller, `FUN_0096A7A0:0x0096A821-0x0096A828`, can
pass its receiver+0xE8 pointer when receiver+0x140 is nonzero. Its admitted
path later clears the calling thread's TLS+0x1C directly at `0x0096A8D3`,
without a context-free call at that store. Thus TLS publication can be
temporary; these paths alone do not establish ownership of every supplied
context, its caller/thread identity, or a lifetime bound for the selected route.

InputElement destruction passes its adjusted InputElement receiver I in a
caller-cleaned stack slot to `FUN_0091CE90` at `0x0091DC9F-0x0091DCA0`.
The callee returns early for null H only when `FUN_00919D30` returns AL=1.
That six-byte getter reads raw byte `0x01356E14` at `0x00919D30-0x00919D35`.
`FUN_00919D60` and `FUN_0091A1F0` write 1 before reaching
`FUN_0096A940`; this does not qualify a gameplay/session-validity meaning
or tie the byte to H's generation. With H present it walks H+4..H+8,
calling `FUN_0091F8D0` with ECX=each registered L and I in one stack slot
(`0x0091CEFA-0x0091CF01`, `ret 4` in the pair helper). The helper first
clears both dwords of the first pair whose key equals I
(`0x0091F94A-0x0091F94C`). Only without a key match and with L+0x10=1
does it search the first recipient equal to I. It looks up that pair's key
in global `0x01357060`: a found recipient differing from I replaces the
local recipient while preserving its key (`0x0091FA76-0x0091FA79`);
otherwise the local recipient becomes zero, retaining the key if the global
pair exists and clearing it if absent (`0x0091FA85-0x0091FA9A`). These
paths do not shrink the pair range or clear all duplicates. Thus the local
copy can be changed during synchronous destruction; registration is an
invalidation mechanism, not an immutable snapshot or lifetime lease.

The inspected Window destructor has the complete-object base-destructor
chain `FUN_00924DC0 -> FUN_00935660 -> FUN_00936C70 -> FUN_009314E0
-> FUN_0093AC10`, ending at the InputElement destructor with receiver
+0xB4 as qualified above. This connects that concrete type to focus cleanup;
it supplies no synchronization, retained handle, or login/logout generation.

`FUN_0091EE90` requires non-null current focus and event descriptor before
using this collection. `FUN_0091ED80` uses the desktop root's +0xB4
InputElement as its route sentinel when a root exists. Its copy helpers
`FUN_00921500/590` preserve pair order. When the source's first key differs
from the sentinel, the copy places a synthetic `{sentinel,sentinel}` first
and skips matching source keys; the sentinel is zero without a desktop root.
`FUN_0091EE90:0x0091EFFD-0x0091F00B` can move
the focused key's pair to the local snapshot's end. At `0x0091F01D`, a
zero event-descriptor byte +4 reverses that snapshot through `FUN_00932760`.
The iteration then advances from begin to end and skips null recipients
(`0x0091F17B-0x0091F1B8`). Front registration is therefore not a universal
first-consumer rule. None of these conditions proves a valid gameplay
session. `FUN_0091E1C0` dispatches through a
recipient's vtable+0x34 or +0x60 ancestor chain according to the event
descriptor, and the router can stop on event+0x17. The owner and meaning
of that stop byte must be resolved before assigning modal precedence.

The initial nonnull focus/descriptor tests do not prove a readable source
range. `FUN_0091ED80:0x0091EDC0-0x0091EDDE` calls `FUN_009D22B4`
on invalid/empty ranges and then reads the first key if that call returns;
the builder itself does not return an empty snapshot there. A readable,
nonempty source is required for that read. Before the later null-recipient
skips, `FUN_0091EE90:0x0091F0F0-0x0091F115` reads the matched focused
pair's recipient+0x64/+0x68 into event+0xC/+8 without a recipient-null
guard. That recipient's identity and readability must hold at those reads;
the offsets are not qualified gameplay/text-entry/session fields.

The same dispatcher handles kind `0x57` through PreviewTextInput
(`0x01359780`) and TextInput (`0x01359710`), conditional on two
`FUN_00445D60` string-equality queries for newline and carriage return at
`0x01069148` and `0x0106914C`. Its direct instructions at
`0x00445D60-0x00445D9E` compare the receiver's string bytes with the stack
string and return equality in AL. These are character-content checks,
not a readable text-entry mode or priority over pad routing.
Native InputElement/TextBox RTTI alone
does not connect a captured token to those types. The token remains opaque.

The exact classification blockers are the actual named-recipient/gameplay/text-entry
recipient construction and role relation, the resolved modal reader and its
registration-container lifetime, text-entry/modal precedence before the
selected-pad boundary, and a session-generation validity rule. Object
destruction clearing focus does not establish logout/login invalidation.
No role, precedence, or session field in these paths is qualified for pad
consumption. The supported receiver adjustments and synchronous lifetime
rules above still apply.

A safe gameplay-context reader remains unproved. The missing fact is a
readable, current native recipient/text-entry/modal/session classification
at or before pad consumption, with receiver identity and lifetime, on
command-free pad updates. Window focus, non-null S, M+8, preprocessor return,
and command admission cannot substitute for that classification.

## Visibility property path

The script identities and three-state wrapper behavior are promoted in
`xivl-client-scripts@aeef43f9721b9b011cefe8bad5a88e6784263937:docs/action-menu-grid-visibility.md`.
The source reproduction entries were inspected at that repository's
`ab479da8428991262ed2879a428c02ebd4277678`.

The native string-property construction lead is concrete:
`FUN_006E9AC0 -> FUN_0075B810 -> FUN_005355A0 -> FUN_005354D0`.
The last function resolves an element index, constructs a processor on the
stack through `FUN_0053BC30`, and synchronously invokes the supplied
callback with that processor. The constructor writes
`Application::Main::Element::SetPropertyProcessor::vftable` at
`0x00FA0BAC`, and retains four dwords at +4/+8/+0xC/+0x10.
This processor is not the live grid pointer or a stable handle.

| Processor vtable slot | VA / RVA | Operation |
|---|---|---|
| 1 | `0x005425B0` / `0x001425B0` | Formats the integer argument using `%d`, then reaches the property engine. |
| 2 | `0x00542680` / `0x00142680` | Converts a boolean to `True` or `False`. |
| 3 | `0x00542710` / `0x00142710` | Forwards the existing native string object without integer formatting. |

Each enters `FUN_00537DE0` at VA `0x00537DE0`, RVA `0x00137DE0`.
The string method uses ECX=processor and one stack pointer, ending in
`ret 4`. Its tail of argument setup at `0x00542710-0x00542729` loads
the engine receiver from processor+4 and passes processor+0xC,
processor+0x10, the string pointer, and processor+8. The engine resolves
the named control through `FUN_00537950`, parses the property name, and
enters `FUN_00912850`. That general engine can process bindings and
property-specific callbacks. It is not a typed Visibility-only setter.
The generic `0x006F4F70 -> 0x0073DF10` path supplies no replacement proof.

`FUN_00537950`, RVA `0x00137950`, uses ECX=the property engine, a native
control-name string object pointer and an element index in two stack slots,
and `ret 8`. `FUN_00535690`, RVA `0x00135690`, resolves that index through
the engine's map pointer at +0xD4. Let X be that returned indexed record.
The name resolver uses an index/name cache at engine+0x1DC; a miss first
consults `FUN_0053E480` with ECX=X. It searches X+4 and returns the name-map
node's +0x60 pointer. If this fails and X+0x30 is nonzero, that stored pointer
becomes the fallback lookup receiver at `0x00537A73-0x00537A98`.
`FUN_0053C310` forwards the constructed key sequence, fallback byte 1, and
excluded pointer 0 to `FUN_00910980`, preserving that ECX receiver, and copies
its raw result to the caller's output. This enters the generic virtual search
and fallback mechanism above. The fallback receiver's concrete type and
virtual overrides remain unbound. It does not apply the input-interface +0xB4
adjustment or acquire a lease.
These are index-scoped native lookups, not direct global string-to-grid
addresses. Cache insertion and a returned pointer do not supply a lifetime
lease. The actual ActionMenu index, concrete returned grid types, ActionMenu/grid
cache eviction, and replacement identity remain unqualified.

The constructor `FUN_0053AF60` identifies one property-engine producer as
`Application::Main::Element::FormElement`. Its complete receiver E has vftable
`0x00FA1200`, COL `0x01145194`, offset 0; its input receiver E+8 has vftable
`0x00FA10DC`, COL `0x011451F0`, offset 8. Deleting slot 0 is
`FUN_005455B0`; the input thunk `FUN_005455A0` subtracts 8 before entering it.
The constructor publishes the same allocated index map K at E+0xD0 and E+0xD4
at `0x0053B011-0x0053B017`, and initializes the separate cache at E+0x1DC.

`FUN_0096E4D0` constructs `Sqwt::Markup::XamlControlContainer`: complete
vftable `0x010724D4`, COL `0x0117D0C4`, offset 0, deleting slot 0
`FUN_0096EA30`. Its own name map begins at X+4; X+0x2C and fallback-root
storage X+0x30 start null. `FUN_0096B220` and `FUN_0096BCA0` allocate 0x48
bytes and call this constructor. This qualifies those producer paths, not every
raw record or either named grid returned from its map.

`FUN_0096E580` is the name-map registrar with ECX=X, a native name-string
object pointer and raw control pointer P in two stack slots, and `ret 8`.
If P+0x298 is nonzero, it first calls `FUN_0096DEF0` with that old container
as ECX and P unchanged. It searches for an unused key, adding `"(n)"` to the
supplied name on collisions, beginning at n=1. `FUN_0094D580` returns the
chosen node's +0x60 value cell. The registrar stores P there and X at P+0x298
at `0x0096E753-0x0096E75A`. Registration itself does not acquire a lease on P.
It also searches the calling thread's TLS+0x1C context collection at
+0x2108, whose +0x210C/+0x2110 fields bound raw X pointers, and appends X
when absent. This path assumes a nonnull context. It establishes a thread
dependency, not a named UI thread or an externally retainable control.

`FUN_0096DEF0` takes ECX=X, P in one stack slot, and uses `ret 4`.
It clears X+0x2C when that pointer equals P, then `FUN_0096E900` searches
the name map by node+0x60 pointer equality. Only a found entry is erased
through `FUN_009A0230`, after which P+0x298 is cleared at `0x0096DF5E`.
When the map becomes empty, it removes X from the same calling-thread
context collection. It does not directly clear fallback storage X+0x30.
`FUN_0096E290` repeats this removal until the name map is empty.
FrameworkElement cleanup `FUN_00931090:0x00931359-0x00931367`, reached
from `FUN_009314E0`, reads P+0x298 and calls the remover with complete P
unchanged. No +0xB4 input-interface adjustment is applied to the map value.

Markup traversal `FUN_00947040` uses the raw object P=[B+0x10] and
container X=[B+4]. For nonnull P with null P+0x298, it registers the
nonempty name stored at P+8 or a generated name from the calling thread's
TLS+0x18 counter through `FUN_0096E580`. The native factory helpers
`FUN_00534150`, `FUN_005341F0`, and `FUN_00534290` take a receiver Q and
pass [Q+0xB4] as the registrar receiver. Registration uses that loaded
pointer unchanged. Q's concrete type and complete-object base remain unbound.

One constructor-qualified namespace owner is
`Application::Main::Element::XamlElement`. Let U be its complete receiver.
`FUN_00539890` writes complete vftable `0x00FA1010`, COL `0x01144E5C`,
offset 0, and input vftable `0x00FA0EEC`, COL `0x01144EB8`, offset 8.
It constructs an embedded `Sqwt::AutoPtr<Sqwt::Markup::XamlControlContainer>`
at U+0xB0 through `FUN_0052CCB0` with null storage. The AutoPtr's vftable
is `0x00F9D444`; its +4 pointer cell is therefore U+0xB4.

`FUN_0068D510` constructs
`Application::Main::Element::Window::LuaDebug::LuaDebugOut` with complete
vftable `0x00FC60E0`, COL `0x0115993C`, offset 0, and input vftable
`0x00FC5FBC`, COL `0x0115999C`, offset 8. It calls `FUN_00539890` at
`0x0068D573` and namespace publication `FUN_00534350` at `0x0068D5F7`,
both with the complete receiver unchanged. This qualifies that producer's
XamlElement base and publication receiver, not Q in every factory path.

`FUN_00534350` uses ECX=U in that path, one stack argument, and `ret 4`.
`FUN_0096B8C0` returns a XamlControlContainer AutoPtr. Publication takes
its +4 pointer and zeros the temporary's storage at `0x00534391-0x00534394`.
If that pointer differs from the value at U+0xB4, a nonnull old pointer receives
deleting slot 0 with flag 1 before its storage is cleared. The new pointer is stored
at `0x005343BB`. The equality path skips replacement. Temporary cleanup
through `FUN_0052CD10` cannot delete the transferred pointer from its cleared
cell. The loader can also return an empty AutoPtr after failed allocation.
The publication return value does not establish a populated name map.

Complete deleting slot `FUN_005439D0` enters `FUN_00539210`; the input
thunk `FUN_00542C10` subtracts 8 first. Destruction calls `FUN_0052CD10`
on U+0xB0 at `0x0053929A-0x005392A0`. For a nonnull stored pointer, that
helper invokes deleting slot 0 with flag 1 and clears the cell. Replacement
and teardown can therefore destroy this owned namespace; they do not lease
a returned control. The selected factory receiver, readable thread/lifetime,
and association of U's namespace with the indexed FormElement and ActionMenu
remain unbound. These paths do not establish grid-cache invalidation.

`FUN_0068DB90` uses ECX=Q and two stack arguments, with `ret 8`.
At `0x0068DB9C` it calls `FUN_005341F0` with Q unchanged and the first
argument as the name. It does not test that factory's return status before
calling `FUN_00536CE0`, `FUN_00536D20`, `FUN_005370D0`, and `FUN_00537350`,
again with Q unchanged. `FUN_00536CE0:0x00536CE4-0x00536CF0` reloads
[Q+0xB4] and calls the qualified name-map lookup `FUN_0053E480` using the
original name, rather than the collision key selected by the registrar.
This lookup does not prove that the newly created pointer was selected.
The wrapper increments Q+0xBC at `0x0068DC0A` and returns zero without
checking those helpers' statuses. These observations do not establish control
identity, a lifetime lease, or rebuild invalidation.
Its caller, Q's constructor and +0xB4 publication, and the association with
the ActionMenu index remain unbound.

These publication and removal paths have no direct FormElement+0x1DC cache
clear. Their indirect calls do not qualify cache invalidation on a rebuild.
The actual builder result, name after collisions, factory receiver, namespace,
and its association with the ActionMenu index and two grids remain unbound.

`FUN_00538760` registers a raw record with ECX=E, X and integer index in two
stack slots, returns the index in EAX, and uses `ret 8`. It calls
`FUN_00542410` on K to find or insert the index, then stores X in that node's
+0x10 value cell at `0x0053877C`. The store itself neither releases a previous
value nor leases X. The pending-load callback `FUN_005387F0` takes the supplied
AutoPtr's stored pointer, zeros that storage, and passes it to this registrar
at `0x0053894C-0x00538963`. Its thread and the actual ActionMenu request/index
remain unbound. The registrar has no direct E+0x1DC cache-clear operation;
its calls and callbacks do not establish replacement-to-cache invalidation.

`FUN_0053AC10` has conditional index-map teardown. If index 0 is absent or
its record's X+0x2C is null, `FUN_00534FD0` invokes deleting slot 0 with flag
1 on each nonnull map value, clears the nodes, and the destructor destroys and
frees K through `FUN_00542010`. Otherwise it attempts to construct a 0x30-byte
`Application::Main::Element::CloseWindowListener` using K. The listener
constructor `FUN_0053A0E0` stores K at listener+0x2C, registers its embedded
handler through the root's +0xB4 input receiver, virtual slot +0x24, descriptor
`0x01336A84`, and calls `FUN_00921B00` on the root. Failure to resolve that
root deletes the listener immediately. Listener vftable `0x00FA1054`, COL
`0x01144ECC`, offset 0 has deleting slot `FUN_005441A0`; its destructor
`FUN_00539480` deletes nonnull K values, destroys K, and frees it.

For constructor-qualified X, deleting slot `FUN_0096EA30` calls
`FUN_0096E380`, which enters named-control cleanup `FUN_0096E030` and destroys
the name map. Independently of immediate or listener-mediated K teardown,
FormElement destruction calls `FUN_00542B30` on E+0x1DC at
`0x0053AE4D-0x0053AE5B`, destroying the cache nodes and sentinel. These are
conditional ownership paths, not a lease on E, X, a root, or a cached grid.

The cache-hit return at `0x005379F6-0x00537A00` neither re-reads X+0x30 nor
checks the cached result's Template or generation. The qualified Template
replacement and root-cleanup paths establish subtree mutation edges, but their
link to this engine cache is unresolved. The actual engine/index/container,
named-grid registration and destruction, fallback-root virtual overrides, and
invalidation of a cached grid result on index, scope, or Template replacement
remain necessary before retaining a receiver. The listener notification and
cleanup consumers do not establish a readable-thread or lifetime contract for
those selected instances.

The direct instructions at `0x00535690-0x005356F6` return the pointer
stored at map-node+0x10 without acquiring a lifetime lease.
Cache hits return the stored pointer
at `0x005379F6`; misses insert through `FUN_005408E0` at `0x00537A5E` or
`0x00537AD8`. The engine constructor initializes the cache at +0x1DC
at `0x0053B0BE-0x0053B0C8`. In `FUN_0053A630`, the path through
`0x0053A691` resolves a named element, tries a native FrameworkElement cast,
and invokes `FUN_0093CC70` on success. It then reaches cache clearing at
`0x0053A6D8-0x0053A704`, including the sentinel links and size reset.
`FUN_0053CB90` destroys cache tree nodes; it is not the search helper.
`FUN_0053EB20` erases a per-name record in the separate E+0xEC map and
decrements its count; it does not erase the E+0xD4 indexed-container node.
The recorded direct caller of `FUN_0053A630` is `FUN_0075B930`, which
first calls `FUN_004D9910` and then forwards its second argument to the
removal path. This identifies generic map/cache eviction, not ActionMenu
registration, the two grids' destruction, or a rebuild generation.

The exact `_getProperty` string at `0x00FD76B4` has registrations in
`FUN_00744990` and `FUN_0074D940`, with callbacks `0x006EBA80` and
`0x00700450`. The first callback reaches `0x0075B870` or `0x0075B8A0`,
then `0x00538500 -> 0x00538130` or `0x00538130` directly. That engine
selects an element index and obtains a value and type through
`FUN_00537FA0` and `FUN_00537AF0`. It supports several property types;
its string-result cases use the supplied processor's vtable+0xC. Those
helpers also contain the `Anime`/`UIElement.Execute` lookup path.
This is a concrete getter-bridge lead, not a typed Visibility reader or
proof that the returned string is the current native preference of either
grid. Its VM arguments and result processor are not stable control handles.

The first unresolved value-resolution edge is
`FUN_00537FA0 -> FUN_00911020`. Its registry lookup through
`FUN_00910ED0` returns the value stored at entry+0x20, after which
resolution depends on receiver vtable slots +0x30 or +0xC and handler
slot +8. The parallel
`FUN_00537AF0 -> FUN_00911180` type/default path reaches
`FUN_00910F60` and `FUN_009A2C90`. These are generic dynamic property
paths. A concrete Visibility handler for each live grid, resolved full-state
return, and native-writer precedence remain unproved. Even a resolved
effective Visibility value would not by itself supply a separate current
native preference while another caller owns presentation.

The Visibility name initializer at `0x00F22900-0x00F22923` associates
`"Visibility"` at `0x0106BEB8` with descriptor `0x013596BC`, property
index 1 and metadata value 5. `FUN_0093C750` constructs a
`Sqwt::UIElement`, registers that descriptor with initial value 2 through
`FUN_00973EF0`, and connects callback `FUN_0093B700`.

`FUN_00914580` decodes the string into one byte:
Collapsed or False -> 0, Hidden -> 1, other strings -> 2.
`FUN_009145F0` encodes byte 0/1/other as Collapsed/Hidden/Visible.
`FUN_00914630` encodes the corresponding dword values. Their disassembly
ranges are `0x00914580-0x009145EB`, `0x009145F0-0x00914626`, and
`0x00914630-0x00914665`. These are converters, not control getters or
setters. In particular, the decoder's fallback to Visible is not validation
of an arbitrary string. An adapter must preserve and validate the exact
three states before any native operation.

### Typed storage and setter candidate

`FUN_0093C2A0`, VA `0x0093C2A0`, RVA `0x0053C2A0`, is a Visibility-specific
wrapper: ECX is the complete UIElement, with three 32-bit stack arguments
and `ret 0xC`. Argument 1 supplies the state byte. Arguments 2 and 3 supply
policy/notification bytes whose safe override choices remain unqualified.
It passes descriptor `0x013596BC` and callback `FUN_0093B700` to
`FUN_009BCB50` with ECX adjusted to UIElement+0x158.

`FUN_009BCB50` uses the byte at property-state+0 as the value and
property-state+1 as flags. It may resolve pending property state through
`FUN_009157C0`. Its direct instructions at `0x009BCB58-0x009BCBA0`
establish the following policy for the wrapper's argument 2, after pending
mask `0x10` resolution and clearing:

| Argument 2 byte | Write admission | Accepted flag update |
|---|---|---|
| 0 | Rejected when flag mask `0x02` is set | Clears mask `0x01` |
| 1 | Requires either mask `0x02` or `0x01` | Preserves mask `0x01` |
| Other | Passes these admission tests | Preserves mask `0x01` |

An accepted changed value sets mask `0x04` and dispatches notification
through `FUN_009BC9E0` only when argument 3 byte equals 1. Other values
skip notification, as does an unchanged accepted value.
AL reports 0 for policy rejection and 1 for acceptance, including an
unchanged accepted value (`0x009BCB91-0x009BCBD7`). This mechanical policy
does not establish safe override arguments or an independent preference
channel. The wrapper preserves that low-byte return but has no full-EAX
boolean contract. This establishes full-state storage at complete UIElement+0x158 and
companion flags at +0x159, not permission to write either byte directly.
The property's resolution, precedence, and notification path must be
preserved. A cached-byte read alone has not been qualified as the current
native preference getter.

In `FUN_0093B700:0x0093B7E0-0x0093B804`, property index 1 compares the
state with 2, then passes that boolean to `FUN_0093A3B0` and
`FUN_009404A0` with policy/notification arguments 0 and 1. The former
updates IsVisible (descriptor `0x013593D8`, UIElement+0x135); the latter
updates VisualVisibility (descriptor `0x01359940`, UIElement+0x84).
Their name initialization calls are at `0x00F22A00-0x00F22A0A` and
`0x00F23350-0x00F2335A`, using strings `0x0106BF24` and `0x0106C534`.
Both receive false for Hidden and Collapsed. This native notification path
can reject the derived writes. The IsVisible path reaches
`FUN_0093E120`, which rejects policy 0 when packed-state mask `0x04`
is set (`0x0093E13F-0x0093E165`). VisualVisibility reaches
`FUN_0095E290`, which rejects policy 0 when its state mask `0x02`
is set (`0x0095E2AF-0x0095E2D3`). These are different property layouts.
Notification intent therefore does not prove that stored or effective
visibility changed. It does not authorize choosing those policy arguments
for an override.

IsHitTestVisible is a separate property: its initializer at
`0x00F22930-0x00F22949` associates string `0x0106BEC4` with descriptor
`0x01359354`, property index 2. The Visibility branch does not directly
assign that descriptor. Derived visibility may still affect hit testing;
the two grids' actual hit-test consumers remain unqualified.

Collapsed also has distinct layout effects. `FUN_009302F0` selects zero
layout values and a zero rectangle when UIElement+0x158 is 0.
`FUN_0093A870` substitutes a zero rectangle for that state while updating
layout through the current TLS context. This is not mouse-region exclusion
proof for Hidden. `FUN_009157C0`, RVA `0x005157C0`, is a cdecl helper with
two stack arguments, the complete object and property descriptor. When
TLS+0x1C exists, it either calls a thread-local provider's vtable+0x20 or
enqueues resolution through `FUN_009A3850` at context+0x2180. Calling it
from a different thread cannot qualify a current-preference read.

The missing contract is the live ActionMenu instance -> each named grid's
complete UIElement receiver, plus a typed full-state getter/setter and
rebuild invalidation. Thread-local property operations and routed callbacks
also prevent treating this as a render-thread memory write. Visibility
conversion alone proves neither removal of each grid's mouse hit regions
nor isolation from saved HUD preferences. A session override must reconcile
native visibility changes while it owns presentation and restore the current
native preference only through a still-live receiver. ActionGaugeWidget
and unrelated HUD controls are outside that override.
