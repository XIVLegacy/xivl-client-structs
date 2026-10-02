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
This identifies the first downstream routed pad-event path without command
admission. The shared router uses current source `0x01357020`, obtains a
route collection, assigns event source fields +8/+0xC, dispatches through
`FUN_0091E1C0`, and can stop on event+0x17. Descriptor names, the complete
focus/modal policy, and the gameplay recipient are not resolved here.

All these calls are synchronous within the invoking Rapture update.
The preprocessor uses that thread's TLS, so another thread cannot safely
substitute its own TLS state. A named OS thread, synchronization with UI
rebuild, and session generation require qualification. P and S are embedded
in M, and are usable only while that instance lives. PadEventArgs is local
to `FUN_00548160`; neither it nor its source pointers may be retained as
handles after the dispatch. Reacquisition is required after M is replaced.

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
`FUN_009157C0`, refuse a write according to flag bit 1 and argument 2,
clear flag bit 0 on one accepted path, mark bit 2 on a changed value,
and dispatch notification through `FUN_009BC9E0` when argument 3 equals 1.
This establishes full-state storage at complete UIElement+0x158 and
companion flags at +0x159, not permission to write either byte directly.
The property's resolution, precedence, and notification path must be
preserved. A cached-byte read alone has not been qualified as the current
native preference getter.

In `FUN_0093B700`, property index 1 reads that byte, compares it with 2,
calls `FUN_0093A3B0` and `FUN_009404A0`, and has additional work when
the value is 0. That is a concrete distinction between Hidden and
Collapsed in native processing. The helper effects and each target grid's
actual hit-test path remain unqualified. `FUN_0093CC70` also sets the
Visibility property through this engine and uses TLS+0x1C queues, providing
a direct thread-context dependency in native UI lifecycle processing.

The missing contract is the live ActionMenu instance -> each named grid's
complete UIElement receiver, plus a typed full-state getter/setter and
rebuild invalidation. Thread-local property operations and routed callbacks
also prevent treating this as a render-thread memory write. Visibility
conversion alone proves neither removal of each grid's mouse hit regions
nor isolation from saved HUD preferences. A session override must reconcile
native visibility changes while it owns presentation and restore the current
native preference only through a still-live receiver. ActionGaugeWidget
and unrelated HUD controls are outside that override.
