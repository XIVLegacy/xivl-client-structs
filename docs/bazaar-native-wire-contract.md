# Bazaar command and item-package contract

This record separates Bazaar command construction and completion from the
item-package updates consumed by the seller and buyer. The exact
Lua operands and script identities are recorded in
`xivl-client-scripts:docs/bazaar-retainer-client-contracts.md`. A command
submission result is not a listing acknowledgement.

## Binary and method

The input is retail `ffxivgame.exe`, version `2012.09.19.0001`, size
`15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
PE32 x86, image base `0x00400000`. The observations used Ghidra `12.1.3`
with the committed read-only exporters. Addresses below are absolute VAs.
Recovered types are analysis representations.

Focused instruction and table reads also used pefile `2024.8.26` and
Capstone `5.0.7` against that exact PE. These are static observations. The
sale-price UI is canonical in
`xivl-client-scripts:docs/bazaar-price-modes.md`; the actor sign is canonical
in [Bazaar appearance](bazaar-appearance-contract.md).

`VerifyProgramFileBytes.java` ended with
`COMPLETE: program-file-bytes-v1`. It reported language
`x86:LE:32:default`, compiler spec `windows`, one retained FileBytes source,
matching retained original and modified layers, and matching loaded
initialized file-backed ranges. This authenticates the identified code and
file-backed data, not runtime state or excluded unbacked data.

## Request identities and ordered operands

| Route | Command-sheet ID | Lua command name | Ordered tail operands |
| --- | ---: | --- | --- |
| Deal, ordinary sale modes including `0`, `11`, `12`, `13` | `24214` | `commandRequest` | `I, 1000001, mode, nil, B, Q, R, nil, nil` |
| Deal, mode `20` or `30`, numeric reward | `24214` | `commandRequest` | `1000001, I, mode, nil, B, R, Q, nil, nil` |
| Deal, mode `20` or `30`, item reward | `24214` | `commandRequest` | `rewardItem, I, mode, nil, B, rewardCount, Q, nil, nil` |
| Undeal | `24216` | `commandRequest` | `I, nil, mode, nil, B, itemStack, attachedCount, nil, nil` |
| Buy from a sale listing, edit-widget mode `6` | `24227` | `commandRequest` | `I, TotalGil, nil, nil, B, chosenQuantity, catalog, nameIndex1, nameIndex2` |
| Check | `24215` | `commandContent` | `nil, nil, nil, nil, target, nil, nil, nil, nil` |
| Deal, melding service | `24214` | `commandRequest` | `equipmentItem, materiaItem, 40, nil, localPlayer, nil, nil, nil, nil` |
| Undeal, melding service | `24216` | `commandRequest` | `nil, nil, 40, nil, localPlayer, nil, nil, nil, nil` |

`I` is an item control reference, `B` is the Bazaar actor control reference,
`Q` is the chosen quantity and `R` is the numeric reward/price. Numbers in
the table are ordinary Lua numeric operands. The connector's fixed wrapper
supplies the trailing nil positions. Numeric zero remains zero. Nil quantity
defaults to the item's stack before command submission. Mode and reward
branches are fixed by the original connector bytecode, not the ambiguous
decompiled conditional. The Lua record owns those exact PCs and offsets.

The command-sheet ID resolves the command control object; it is not a network
opcode or an extra scalar inserted in this tail. `FUN_0070A010` looks up the
named descriptor through `FUN_0071CA50`, validates the command binding and
control operands, then dispatches through `FUN_00898480`. The installed
descriptor determines whether `_onCommandRequest` or `_onCommandEvent`
executes. Lua preserves the tail through its fallback call.

`FUN_006E8C90` (`_doServerOnCommand`) and `FUN_006E8B30`
(`_callServerOnCommand`) both reach `FUN_006E2FB0`. That helper serializes
from argument index `2`: name and command control are envelope inputs,
while all nine remaining operands keep their positions. The resulting
serverbound `0x012D` construction and descriptor/send gates are canonical in
[`player_command_wire_contract.json`](../manifests/player_command_wire_contract.json).
The selected runtime descriptor and a successfully transmitted Bazaar
invocation are not established by these static paths.

## Conditional wire encoding

The `0x012D` application payload is `184` bytes after the 16-byte
game-message header. It contains self actor fields at `+0x00` and `+0x08`,
the command binding reference at `+0x04`, a CRC32 of the 128-byte argument
area at `+0x0C`, descriptor type at `+0x10`, inline descriptor name at
`+0x11`, and the typed argument area at `+0x31`. The native manifest owns
the field locators and the unresolved seven-byte remainder.

| Operand | Encoding in the typed area |
| --- | --- |
| Signed32 integral quantity, price, mode or currency catalog | `00` followed by four big-endian bytes |
| Nonintegral number | `01` followed by float32 bits |
| Explicit nil | `05` |
| Non-item control reference | `06 R:u32be`, with resolved binding reference `R` |
| Single item control reference | `07 R:u32be S:u16be P:u8`, with owner binding reference, native slot and native package |
| Consecutive items with equal owner reference | May coalesce to tag `08`, preserving order; see the native manifest's `serializer.item` |
| Optional final item metadata | `09 M1:u64be M2:u64be` |
| End | `0F`; untouched zero padding does not represent nil |

The ordinary Deal price and quantity are separate scalar operands, not
members of the item reference tuple. Currency catalog `1000001` takes the
ordinary integer path. `FUN_006F5260` obtains item owner/package/slot and
passes them to `FUN_00790BA0`. It copies the resolved item's `+0x10/+0x14`
pair for the optional metadata collector. `FUN_00790400` emits tag `09`
only when the writer's flags permit it. The zero-sentinel collection rule is
not a materia-count test or a strict count of item operands.

That pair comes from the first eight bytes of the incoming item record.
`FUN_0076B760` copies wire `+0/+4` to decoded record `+0/+4`
(`0x0076B791-0x0076B799`). `FUN_006F4490` passes that pair by address
to `FUN_006EF520` (`0x006F4555-0x006F4589`), whose base constructor
`FUN_006DF580` stores it at item `+0x10/+0x14`
(`0x006DF5BB-0x006DF5C9`). The serializer reads those same fields at
`0x006F52CB/0x006F52D0`. Thus `M1/M2` collect item-record identities in
encounter order subject to the zero-sentinel rule, rather than the two
halves of the `0x40`-byte modifier block. Uniqueness or a catalog-ID meaning
for the eight-byte field is not established by this copy chain.

### Purchase freshness and the amount echo

There is no fresh purchase-attempt discriminator in the reconstructed
direct `24227` request. No sequence, request ID or listing-version counter
is generated by this path. Repeating the same item, target, chosen quantity
and price produces the same semantic application fields. This is a bounded
statement about the Lua caller and direct native construction, not a claim
about an observed runtime descriptor or a server replay policy.

There is an amount echo. Edit-widget mode `6` passes its `TotalGil` input
as the second operand and its `ItemSource` quantity as the sixth. Connector
prototype `0.418`, PCs `13-22` at decoded offsets `0x2709B-0x270BF`,
forwards them without adding a counter. Its time and delay writes are after
that call, PCs `25-31`, `0x270CB-0x270E3`, and stay local.

For the ordinary integral buy shape with one tag-`07` item and a tag-`06`
target, the following offsets are application-relative:

| Field | Tag offset | Value offset | Encoding and source |
| --- | --- | --- | --- |
| Total amount | `0x39` | `0x3A` | Four big-endian integer bytes from `TotalGil`. |
| Chosen quantity | `0x45` | `0x46` | Four big-endian integer bytes from `ItemSource`. |

These offsets follow the item tuple at `0x31`, amount, two nils and target
tuple in order. They are conditional on those scalar/reference encodings.
The amount can expose a stale-price mismatch to a server, but an identical
second attempt echoes it again. It is not a nonce.

Envelope `+0x08` copies self actor `+0x14` through `FUN_0075D460`;
`FUN_0075E1C0` passes it unchanged. It is not incremented on submission.
Envelope `+0x0C` is the deterministic typed-tail CRC, not an event sequence.
The optional tag-`09` values come from received item identities as described
above, not from a purchase counter. No semantic write is established for
the seven-byte remainder at `+0xB1`. These observations supply no fresh ID
hidden in padding. The separate event-continuation builders
`FUN_0075E230/FUN_0075E3A0` do use event-context state; their fields must
not be substituted for this initial direct request.

### Dealing fields read by Lua

The incoming item record and Lua getter outputs use different field domains.
`FUN_0076B760` supplies wire tags `+0x20`, tag values `+0x24`, mode `+0x13`,
attached1 `+0x14`, value byte `+0x12` and attached2 `+0x18` to
`FUN_00769760`. That constructor stores mode/value/attached1/attached2 at
its subobject `+0x20/+0x21/+0x24/+0x28`. `FUN_007698E0` copies them into
the item subobject installed at item `+0x8C` by `FUN_006DF580`.

| Lua getter | Native observation |
| --- | --- |
| `_getDealingInfo()` | Registration `FUN_0074EBA0` binds `FUN_00701E90`. It calls `FUN_00763460 -> FUN_007633D0` to find tag `0xC9` and return the corresponding tag-value byte, or nil. It does not return the wire `dealingValue` byte. |
| `_getDealingAttached()` | Registration `FUN_0074ECF0` binds `FUN_00701F20`. After the `0xC9` presence check in `FUN_00764DC0`, `FUN_00764EA0` supplies the four subobject fields above. Native mode `2` returns `(attached1, valueByte, attached2)` as numbers. Mode `1` resolves the packed package/slot in attached1 and returns `(item, nil, nil)` when it resolves. Otherwise it returns nils. |

Wire attached3 `+0x1C` follows a different path: the decoder stores it at
decoded record `+0x0C`, which reaches item `+0x1C` through
`FUN_006EF520/FUN_006DF580`. It is not the third numeric result of
`_getDealingAttached`. The price-mode record owns how the row builder and
buy dialog consume the getter results for each sale kind.

### Package and slot numbering

`FUN_0078BC90` subtracts one from a Lua package number and `FUN_0078BCD0`
subtracts one from a Lua slot number. `FUN_00702400`, reached from
`_getExtendedTemporaryItem` at `FUN_00708840`, performs both conversions
before resolving the item. Item lookup can follow a linked slot through
`FUN_006EE3E0` or `FUN_006EE480`; a linked package/slot is not a new item
catalog identity. The serializer uses the resolved control's native indices.

For a package refresh, `_updateItemPackage` at `FUN_006E79D0` reaches
`FUN_006E5AD0`, converts the package through `FUN_0078BC90`, and calls
`FUN_0075EA50`. That builder requests c2s `0x0131`, internal message size
`0x18`, with an eight-byte application extent: actor u32 at `+0`, package
u8 at `+4`, and no semantic write established for the other three bytes.
Thus Lua package `8` requests native/wire package code `7`. A field described
as a package dword must not erase the builder's one-byte store.

## Incoming package operations and publication

`FUN_004DC690` dispatches the following s2c families. These are shared item
updates, not reply opcodes selected by the Bazaar command IDs.

| Wire input | Native path and observed operation |
| --- | --- |
| `0x016D` | `FUN_005763C0` -> `FUN_0076BAD0` -> `FUN_0075F720`: queues `UpdateStartCommand`, constructed by `FUN_0089B630`, carrying the input's first byte. |
| `0x0146` | `FUN_005764C0` -> `FUN_0076BC20` -> `FUN_0075F860`: queues `ItemPackageUpdateStartCommand`, constructed by `FUN_0089B320`, carrying actor u32, capacity u16 and package u8. |
| `0x0148..0x014C` | Item-record variants. The single-record path is `FUN_00576560` -> `FUN_00580E70` -> `FUN_00771350` -> `FUN_0076B760`; `FUN_00764A30` appends to an adjacent compatible item command or queues `ItemUpdateCommand` through `FUN_0089BE00`. |
| `0x014D..0x0151` | Linked-slot variants. The single-record path is `FUN_00576790` -> `FUN_005810F0` -> `FUN_00768CF0`; `FUN_00764B30` appends or queues `ItemLinkUpdateCommand` through `FUN_0089BD90`. |
| `0x0152..0x0156` | Removal variants. The single-record path is `FUN_005769C0` -> `FUN_00581370` -> `FUN_00769050`; `FUN_00764C30` appends or queues `ItemClearCommand` through `FUN_0089BD20`. |
| `0x016E` | `FUN_00576430` -> `FUN_0076BB00` -> `FUN_0075F7C0`: queues `UpdateEndCommand`, constructed by `FUN_0089B540`. |

The item command list uses `FUN_0089BCA0` to append operations. The receiver
does not inspect Deal, Undeal or Check IDs to choose a different item decoder.
`FUN_0076B950` and `FUN_0076BA10` retrieve or create map entries for command
and publication state; the latter alone does not apply item records or fire
Lua. `FUN_00CC9330` is a one-byte `RET`, followed by alignment `INT3`s.
This wrapper teardown neither unlocks an item nor delivers an update callback.

`FUN_0089BBA0` drains the command list from its front, invokes each command's
vftable `+0x24`, removes it, and preserves the remaining order if its
per-call limit is reached. The receiver queue therefore preserves the
received operation order rather than sorting item updates by package or
command ID. The execution slots for Start, End and PackageStart are
`0x010571D8`, `0x010571AC` and `0x01057154`, pointing to
`FUN_0089B6F0`, `FUN_0089B5F0` and `FUN_0089B3F0` respectively.

`UpdateStartCommand` execution at `FUN_0089B6F0` reaches
`FUN_006DD8C0`, which clears the selected destination, resets the defer flag
at item manager `+0x61`, and retains the update mode byte at `+0x68`.
Package-start execution at `FUN_0089B3F0` reaches `FUN_006F41A0`, which
selects the package named in the record. For an existing package, it creates
a fresh staged package when update mode is `2`, or clones the existing
package otherwise. Subsequent item operations therefore depend on package
selection and the retained update mode.

For the ordinary Bazaar package, these handlers apply full item records and
removals. Item-update
execution `FUN_0089B4F0` reaches `FUN_006F4490`, materializes the decoded
item records for the selected package and marks changed slots. Clear
execution `FUN_0089B220` reaches `FUN_006F4800`. In contrast, link execution
`FUN_0089B2D0` reaches `FUN_006F46C0`, whose only update branches compare
the selected package code to `0xFD` and `0xFE`, the initialized values at
`0x00FE0510` and `0x00FE050C`. It returns without applying links for code
`7`. Consequently `0x014D..0x0151` are not a substitute for full item
records in Lua Bazaar package `8`. A slot's ability to resolve a link in
the general item cache does not establish a Bazaar linked-packet route.

`UpdateEndCommand` execution at `FUN_0089B5F0` reaches `FUN_00703700`.
When manager `+0x61` is zero, it integrates staged packages through
`FUN_006F7880`, processes dirty package/slot sets through `FUN_007034E0`,
and sets `+0x60`. When the flag is nonzero, it queues a continuation through
`FUN_00714310` and `FUN_006F1B70` instead. This is a publication dependency,
not proof that a received end packet immediately refreshed a widget.

The normal package branch of `FUN_007034E0` reaches `FUN_00702E30`.
That function constructs `_onUpdateItemPackage(package, changedSlots)` only
for a nonempty changed-slot set. Its recorded string reference is
`0x00FD49C8`, used at `0x00703013`. Package and slot numbers are converted
back to Lua numbering by `FUN_0078BCA0` and `FUN_0078BCE0`. The Lua contract
owns the subsequent actor/package-specific seller list rebuild.

### Settlement update dependencies

A client-compatible per-connection update has this order:

```text
0x016D UpdateStart
  0x0146 PackageStart(actor, capacity, package)
    0x0148..0x014C full item updates and/or 0x0152..0x0156 removals
  [another 0x0146 and its item/removal records for each other package]
0x016E UpdateEnd
```

This is a dependency derived from the handlers, not a captured Bazaar sale
sequence. PackageStart selects the destination for following records.
UpdateEnd integrates staged packages before publishing changed-slot callbacks,
or waits for deferred materialization. No handled package-end packet is
needed between sections: `0x0147` is absent from these dispatch paths.
Omitting selection risks addressing a stale or absent destination; omitting
UpdateEnd omits this publication path. Update mode `2` starts a fresh staged
package, so it must not be used as a delta that expects unmentioned rows to
survive. The other existing-package branch clones the current package.

The seller's changed listing is in wire package `7`, Lua package `8`.
A remaining listing uses a full record with its new count/state; an exhausted
listing can use a removal. The buyer's ordinary bag item or stack change uses
the same full-record family in that buyer's selected bag package. A link
record does not materialize a Bazaar item.

Gil is a stack in Lua package `100`, wire package `99` (`0x63`), selected by
catalog `1000001`. `CharaBaseClass.getMoneyOnHand` in
`xivl-client-scripts:lua/scripts/chara/charabaseclass_cliprog.lua:272-312`
enumerates that package and returns the matching stack count. The native
package conversion subtracts one as documented above. Updating that item's
full record supplies the new balance through the same package publication
path. A capacity/money label text ID is not a sale notice.

For example, a sender can put seller package `7` then package `99` in one
bracket, and buyer bag then buyer package `99` in a separate bracket. The
consumer requires package selection before each section and End after its
records. It establishes no requirement that Bazaar precede gil, or that the
seller connection be updated before the buyer connection. These are separate
connections, without a shared client ordering primitive. Publishing notices
after the relevant End avoids describing an unpublished balance; that order
is a sender design inference, not an observed retail receipt sequence.

No required sale-notice text ID is tested by the traced Bazaar command,
listing or buy-dialog paths. They react to item/work state and local call
results. The bounded Lua search and callback trace do not recover which
optional retail sale message was sent. A chosen message is not a substitute
for the package updates, and no historical message ID is established here.

### Removal of a slot never received

`FUN_006F4800` calls `FUN_006EE220` for each slot and records the ordinary
package's dirty slot. `FUN_0052F7F0` first checks the allocated vector's
extent. For a valid index whose element is null, `FUN_006EE220` branches at
`0x006EE253-0x006EE255` to its return at `0x006EE2BF`: no item is required
to have been received in that slot. For a nonnull element it destroys/frees
the item and clears the entry. Thus a removal of an empty valid slot is an
item-storage no-op, although the caller still marks that slot dirty.

An index outside the vector extent is different. `FUN_0052F7F0` reaches
`FUN_005CF390`, which raises the `invalid vector<T> subscript` path. Package
selection and capacity therefore matter even when the item itself is absent.
The storage no-op alone does not promise a visible Bazaar row rebuild, which
has the independent Lua guards described in the script contract.

## Command completion and item locks

The following table assumes the documented retained descriptor definitions
and zero selector global: `commandRequest` constructs `CommandNonBlock`,
and `commandContent` constructs `CommandBlock`. The actual first-match
runtime descriptor remains unobserved, as recorded in
[`command_descriptor_registration.json`](../manifests/command_descriptor_registration.json).

| Command | Client completion requirement on that route |
| --- | --- |
| Deal `24214` and Undeal `24216` | No Bazaar result call, text ID or server EndEvent is awaited by their Lua command path. Inherited `command` and `fire` return false; `_onCommandRequest` invokes `_doServerOnCommand` and returns. The nonblocking submission result is separate from later package publication. |
| Check `24215` | `_onCommandEvent` invokes `_callServerOnCommand`. It marks the current blocking execution as waiting. The matching generic s2c `0x0131` EndEvent reaches the block cleanup described below. The separate `processChackBazaar` or setup method opens the widget; displaying the widget is not that cleanup. |

Lua sources are `xivl-client-scripts:lua/scripts/command/commandbaseclass.lua:231-246`
for the inherited false returns, the named Bazaar command classes, and
`xivl-client-scripts:lua/scripts/chara/player/playerbaseclass.lua:1820-1908`
for the two fallback callbacks. CommandBase original prototypes `0.19/0.20`
are the `fire/command` definitions; their decoded payload identity is in the
script contract's source table. The callbacks add no Bazaar result-text test.

`FUN_006E8C90` sends through `FUN_006E2FB0` and returns. In contrast,
`FUN_006E8B30` continues through `FUN_00893380/FUN_00893400` and the
Lua continuation bridge `FUN_00CD2860`. For the client-side block execution
vtable `0x01057030`, virtual `+0x18` is `FUN_00892700`, which sets execution
byte `+0x28` to `1`. Virtual `+0x10`, `FUN_008926F0`, reads that byte.
This is native event state, not an item lock or a Bazaar success flag.

For EndEvent, `FUN_0076C3B0` reads source actor at application `+0x00`,
one-byte end selector at `+0x04`, event type at `+0x08` and event name at
`+0x09`. Bytes `+0x05..+0x07` are not read by this decoder. The byte
wrappers `FUN_0078DDA0/FUN_0078DE00` and constructor `FUN_0089D070`
retain the selector and type separately. `FUN_0089E2D0` dispatches first
by type through `FUN_008A13A0`, then by selector through the raw instruction
range `0x008A09E0-0x008A0A3A` and jump table `0x008A0A3C`.

For the type-`0` command family, selectors `0` and `1` reach
`FUN_006E1080 -> FUN_008934A0` and
`FUN_006E10A0 -> FUN_00893520`. Both require the current event-name match,
invoke virtual `+0x1C` and can destroy the current completed block. That
virtual is `FUN_00892710`, which clears execution `+0x28`. The selectors
take different post-event branches; this trace does not label them as sale
success and failure. A matching `commandContent` EndEvent is consequently
a client completion mechanism for Check. An arbitrary EndEvent name or a
sale text ID is not equivalent. This does not establish which selector was
sent for a retail Bazaar Check.

The display call can arrive through the generic s2c `0x0130` named-function
route, whose transport is recorded in
`xivl-decomp:docs/event/start-event-fn-receiver.md#trade-routing-through-generic-runeventfunction`.
The Check class exposes `processChackBazaar`, `processSetupBazaar`, and
`processSetupRetainerBazaar`. No command-specific result or notice-text test
appears in those methods. A server driving a yielding named function must
also respect that generic function's continuation/result protocol.

Neither Deal nor Undeal sets a local item tag while submitting the request,
and Check supplies no item operand. `_isLockingItem` binds through
`FUN_00756390` to `FUN_00708C00 -> FUN_00702920`. That path resolves the
item and calls `FUN_00763360` on item `+0x8C`. It returns true if the
received tag vector contains a tag other than `0`, `0xC9` or `0xCA`.
The latter two are dealing and attachment tags, so a listing tag alone does
not produce this lock result. The submit paths do not write that vector.
Command/event waiting, editor `waitupdate`, and an item locking tag are
different state. None establishes an optimistic item lock lasting until a
Bazaar reply.

## Materia-bearing items and retail reply limits

`FUN_0076B760` consumes the same `0x70`-byte item record regardless of
materia count. It reads the modifier-present flag at wire record `+0x29`
and, when nonzero, copies `0x40` bytes from `+0x2A` into the modifier
vector. The fixed record also carries dealing/tag/attachment fields.
The command serializer does not copy that modifier vector into the item
reference tuple and does not select a different Deal opcode for it.

An ordinary sale of already melded equipment remains the ordinary Deal
route. The separate mode `40` is a request for a melding service, with
equipment and materia item operands. Its Lua callers and eligibility tests
are recorded in the script contract.

The seller Lua list reads package `8`. Its package update can rebuild the
list when the update counter and actor/editor state permit it; callback
delivery alone does not guarantee a rebuild.
Remote inspection also polls that package, while the local seller skips
the polling request. These facts constrain the state and notification the
UI consumes; they do not identify a unique sequence of received packets
after each Deal, Undeal or Check. The client command return and the shared
receive queue provide no route-specific receipt-to-mutation correlation.

| Route | Seller-side dependency established | Reply order remaining unresolved |
| --- | --- | --- |
| Deal | A changed listing is read from package `8`; a matching package callback can rebuild it when widget-state guards permit. The edit's true command return closes the editor before any named acknowledgement. | Which item, removal and event-call records were sent, and whether other inventory packages changed first. |
| Undeal | The same package/list callback route consumes a removed or changed dealing row. | Whether withdrawal used a removal or replacement record, and its ordering against physical inventory and event calls. |
| Check | Display methods select inspect/setup mode. Remote inspection requests package `8`; self inspection skips that request. | Which incoming event selected a display method, whether a package refresh followed, and the ordering of either on the seller connection. |

The unresolved retail evidence is a seller trace covering a known item,
package/slot, mode, quantity and price through successful Deal, Undeal and
self-Check, plus a synchronized inspector trace for remote Check. It must
retain complete c2s `0x012D`/`0x0131`, s2c event calls and item-family
operations in per-connection order, final seller rows, and modifier/key
records for a plain and a materia-bearing item. A paired callback trace
would distinguish package publication from wire receipt. This describes
the missing specimen and evidence ceiling in the frozen retail corpus;
new retail acquisition is unavailable.

## Reproduction

Authenticate the existing program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java), the
binary identity above, and the explicit-input procedure in
[`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
With explicit project/JDK bindings and a new absolute output path, run:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

Use these groups for `$Addresses`:

| Observation | Function VAs |
| --- | --- |
| Command dispatch and item serialization | `0x0070A010,0x006E8B30,0x006E8C90,0x006E2FB0,0x006F5260,0x0075AFA0,0x00790BA0,0x00790400` |
| Lua/native index conversion and package requests | `0x00708840,0x00702400,0x0078BC90,0x0078BCD0,0x0078BCA0,0x0078BCE0,0x006E79D0,0x006E5AD0,0x0075EA50,0x006EE3E0,0x006EE480,0x006E2770` |
| Receive dispatch and single-record decoding | `0x004DC690,0x005763C0,0x00576430,0x005764C0,0x0076BAD0,0x0076BB00,0x0076BC20,0x00576560,0x00580E70,0x00771350,0x0076B760,0x00576790,0x005810F0,0x00768CF0,0x005769C0,0x00581370,0x00769050` |
| Operation queue and record grouping | `0x0076B950,0x0076BA10,0x0075F720,0x0075F7C0,0x0075F860,0x0089BCA0,0x0089BBA0,0x00764A30,0x00764B30,0x00764C30,0x0089BE00,0x0089BD90,0x0089BD20,0x0089B630,0x0089B540,0x0089B320` |
| Operation execution and publication | `0x0089B6F0,0x0089B5F0,0x0089B3F0,0x0089B4F0,0x0089B2D0,0x0089B220,0x006DD8C0,0x006F41A0,0x006F4490,0x006F46C0,0x006F4800,0x00703700,0x006F7880,0x007034E0,0x00702E30` |
| Item metadata identity | `0x006EF520,0x006DF580,0x0076B850,0x006F3FE0,0x006EE2E0,0x006EE220` |
| Purchase envelope and amount-echo construction | `0x0075D460,0x0075E1C0,0x0089E0D0,0x00776760,0x0075E230,0x0075E3A0` |
| Dealing getters and received field copies | `0x0074EBA0,0x0074ECF0,0x00701E90,0x00701F20,0x007633D0,0x00763460,0x00764DC0,0x00764EA0,0x00769760,0x007698E0,0x0076B760,0x006EF520,0x006DF580` |
| Empty-slot bounds and item locking predicate | `0x0052F7F0,0x005CF390,0x006EE220,0x006F4800,0x00756390,0x00708C00,0x00702920,0x00763360` |
| Blocking versus nonblocking command dispatch | `0x00898480,0x00896510,0x008963F0,0x00897310,0x008962C0,0x008920F0,0x00892200,0x006E8B30,0x006E8C90,0x00893380,0x00893400,0x008926F0,0x00892700,0x00892710,0x00CD2860` |
| Check's generic EndEvent cleanup | `0x0076C3B0,0x0078DDA0,0x0078DE00,0x0089D070,0x0089E2D0,0x008A13A0,0x006E1080,0x006E10A0,0x008934A0,0x00893520` |

Every promoted decompilation section had a named function and no error or
failed-decompilation marker. Corroborate the hidden register receivers,
vftable installs, typed fields, index conversion and branch comparisons with
the same invocation using `-Script DumpFunctionListing.java` and these
exact function entries:

```text
0x0089B630,0x0089B540,0x0089B320,0x00764A30,0x0076BB00,0x0076BC20,0x0076B760,0x006F5260,0x00790BA0,0x00790400,0x007036E0,0x0075F860,0x0089BE00,0x0089BD90,0x0089BD20,0x0089B8D0,0x0089B6F0,0x0089B5F0,0x0089B3F0,0x006F41A0,0x00703700,0x00702E30,0x00702400,0x0078BC90,0x0078BCD0,0x0078BCA0,0x0078BCE0,0x0089BBA0,0x006F4490,0x006F46C0,0x006F4800,0x006EF520,0x006DF580,0x0076B850
```

The listing runs ended with matching requested/completed counts. The callback
string trace used:

```powershell
tools/ghidra/export-references.ps1 -Strings '_onUpdateItemPackage' -Out $Output
```

Its verifier accepted the terminal completion marker: one exact defined
string at `0x00FD49C8` and one recorded reference at `0x00703013` in
`FUN_00702E30`, after scanning `28414` defined strings. That reference
located the candidate; the function body established argument construction
and dispatch. A reference-database query does not exclude computed,
indirect, dynamic or unanalyzed references.

Tiny PE reads of the same pinned executable corroborated the operation
vftables, their execution pointers and MSVC RTTI identities by following
vftable `-4` to the COL, then COL `+0x0C` to the TypeDescriptor and its
name at `+8`. The corresponding VAs are in the operation table and listing
locators above. The initialized package comparison dwords at `0x00FE050C`
and `0x00FE0510` were `0xFE` and `0xFD`. These reads used the PE header's
image base and section table with
`tools/extractors/client_pe/import_table_dumper.py:rva_to_file_offset`.
No raw decompiled body, ignored export, or runtime observation is a public
evidence dependency.

The dealing/lock registrar trace also used exact named-string queries for
`_getDealingInfo`, `_getDealingAttached` and `_isLockingItem` with the same
verified reference wrapper. The complete report resolved one defined string
and one recorded reference for each: `0x00FD7EC0 -> 0x0074EC89`,
`0x00FD7ED0 -> 0x0074EDD9`, and `0x00FD84E8 -> 0x00756479`.
The containing registrars and their function-pointer construction were then
inspected, rather than attributing implementations from string proximity.

The direct PE instruction checks additionally covered `0x00CC9330`, the
blocking flag accessors at `0x008926F0/0x00892700/0x00892710`, EndEvent's
one-byte read at `0x0076C43A`, and the inner EndEvent dispatch range
`0x008A09E0-0x008A0A3A`. The latter is reached by jumps and is not a separate
function entry in this analysis database. Read it as instructions and read
the six dwords at `0x008A0A3C` as its jump table, rather than requesting a
separate decompilation at that address. The block execution vtable cells at
`0x01057030` fix the flag-accessor slot identities. These checks used the PE
image base and raw-backed section mapping, with Capstone in 32-bit x86 mode.
