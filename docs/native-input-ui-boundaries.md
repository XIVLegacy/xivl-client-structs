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

### Borrowed native keyboard-focus recipient

The current source at `0x01357020`, RVA `0x00F57020`, is a native
InputElement keyboard-focus recipient. This identifies its UI role, not
whether gameplay is permitted. The focus transition in `FUN_0091E3E0`
uses PreviewGotKeyboardFocus (`0x01359450`), GotKeyboardFocus
(`0x0135945C`), and LostKeyboardFocus (`0x013595B4`). Their names and kinds
are initialized at `0x00F23180-0x00F23206`, using strings at
`0x0106C1B4`, `0x0106C1CC`, and `0x0106C1E0`.

Let `I` be the InputElement receiver. For the inspected UIElement and
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
`FUN_0091E3E0` searches through `FUN_009456B0`, writes an accepted
recipient into entry+4, and also reaches collection mutation through
`FUN_00CB1120` with ECX=`0x01357060`. The DesktopWindow constructor
`FUN_0091B020` supplies one concrete focus-registration caller. This
is recipient membership, distinct from event-descriptor registration.

`FUN_0091D930` locates entries by their first dword and passes a matching
entry to `FUN_00A76BE0`. `FUN_0091DBD0` zeros the first matching entry+4
recipient when found, and clears the current-focus token when it equals
the destroyed object. Global teardown `FUN_00F35720`
releases the collection's begin pointer and zeros begin/end/capacity.
These operations identify removal paths, but do not establish the route-key
producer, the helpers' ownership/refcount contract, or a recipient lease.
Construction and replacement of each concrete route recipient remain
unqualified. Do not retain or traverse this collection asynchronously.

`FUN_0091EE90` requires non-null current focus and event descriptor before
using this collection. `FUN_0091ED80` uses the desktop root's +0xB4
InputElement as its route sentinel when a root exists. Neither condition
proves a valid gameplay session. `FUN_0091E1C0` dispatches through a
recipient's vtable+0x34 or +0x60 ancestor chain according to the event
descriptor, and the router can stop on event+0x17. The owner and meaning
of that stop byte must be resolved before assigning modal precedence.

The same dispatcher handles kind `0x57` through PreviewTextInput
(`0x01359780`) and TextInput (`0x01359710`), conditional on two
`FUN_00445D60` queries involving `0x01069148` and `0x0106914C`.
Those queries and ordered event names do not establish a readable text-entry
mode or priority over pad routing. Native InputElement/TextBox RTTI alone
does not connect a captured token to those types. The token remains opaque.

The exact classification blockers are the concrete focus/route-recipient
construction and type relation, text-entry/modal precedence before the
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
the engine's map pointer at +0xD4. The name resolver uses an index/name cache
at engine+0x1DC; a miss first consults `FUN_0053E480`, then, when the
resolved element's +0x30 is non-null, another name-scope lookup path.
These are index-scoped native lookups, not direct global string-to-grid
addresses. Cache insertion and a returned pointer do not supply a lifetime
lease. The live ActionMenu index, concrete returned type, ActionMenu/grid
cache eviction, and replacement identity remain unqualified.

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
`FUN_0053EB20` erases the owning map node and decrements its count.
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
`FUN_0093CC70` also sets the Visibility property through this engine and
uses TLS+0x1C queues, providing
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
