# ItemBase query and extended temporary item native contracts

[`manifests/item_native_call_contract.json`](../manifests/item_native_call_contract.json)
records the static Lua call contracts of fourteen native registrations. Thirteen
belong to `ItemBase` and read an item reference or the item record behind it:
`_getMaxStack`, `_isStackable`, `_isRare`, `_getOwner`, `_isLocking`,
`_getLockingInfo`, `_isDealing`, `_isAttached`, `_getDealingInfo`,
`_getDealingAttached`, `_isTrading`, `_isEquipping` and `_getEquippingSlot`. The
fourteenth is `_getExtendedTemporaryItem` on `CharaBase`. Each full row gives the
registration site, the receiver type check, the declared argument and return
lists, the Lua pushes of every branch including an absent item record, the item
record fields it reads, the failure behavior and whether the call yields. The
contracts describe client marshalling and state, not item data, lock tags,
dealing values, package numbers or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at
the cited addresses. `MEASURED` is counted by the method named in the fact from
the call-site index of the installed client scripts. `INFERRED` is a name or role
taken from the surrounding instructions or script names that the bytes do not
state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method). A
second pass re-read the bytes and compared every cited call target, immediate,
vftable cell, data cell and name literal with the claims below. The registrar
shape, the type registry, the cell tags and the invalid-parameter route are the
ones of the [nameplate, actor and group contracts](nameplate-group-native-contract.md)
and the [work binder contracts](work-binder-native-contract.md#binary-and-method).
The package model, the item lookup and the item record builders are the ones of
the [scheduler and item contracts](scheduler-item-native-contract.md#item-packages).
`R`, `X` and `Y` name the world object chain of the
[fade contracts](fade-actor-group-native-contract.md#fade-natives).

The call-site and script counts agree with
`xivl-client-scripts:lua/napi_index.json` and are `MEASURED`. They show that a
script contains a call, not that a script reaches it at run time. The argument
counts, the return counts and the constants come from a local Lua 5.1 bytecode
scan of the installed client scripts, decoded with
[`tools/decode_lpb.py`](../tools/decode_lpb.py). The script sources are not
redistributed and no tracked artifact carries those values, so they are
`INFERRED`.

## Registration

Every native is declared by a `_u` script descriptor named `<name>_inl` that
returns the selector `self` and the target `<name>_cpp`. The thirteen `ItemBase`
descriptors sit in `item/itembaseclass_u` and the `CharaBase` descriptor in
`chara/charabaseclass_u` (`MEASURED`). The order of a native is its position
among the rel32 calls of its switchboard.

| Native | Switchboard | Order | Registrar | Caller | Callback |
| --- | --- | ---: | --- | --- | --- |
| `_getMaxStack` | `ItemBase` | 2 | `0x0074DBE0` | `0x00753E01` | `0x00701870` |
| `_isStackable` | `ItemBase` | 3 | `0x0074DD30` | `0x00753E16` | `0x007018C0` |
| `_isRare` | `ItemBase` | 5 | `0x0074DFD0` | `0x00753E40` | `0x00701970` |
| `_getOwner` | `ItemBase` | 8 | `0x0074E3C0` | `0x00753E7F` | `0x00701AD0` |
| `_isLocking` | `ItemBase` | 11 | `0x0074E660` | `0x00753EBE` | `0x00701C40` |
| `_getLockingInfo` | `ItemBase` | 12 | `0x0074E7B0` | `0x00753ED3` | `0x00701CB0` |
| `_isDealing` | `ItemBase` | 13 | `0x0074E900` | `0x00753EE8` | `0x00701DD0` |
| `_isAttached` | `ItemBase` | 14 | `0x0074EA50` | `0x00753EFD` | `0x00701E30` |
| `_getDealingInfo` | `ItemBase` | 15 | `0x0074EBA0` | `0x00753F12` | `0x00701E90` |
| `_getDealingAttached` | `ItemBase` | 16 | `0x0074ECF0` | `0x00753F27` | `0x00701F20` |
| `_isTrading` | `ItemBase` | 18 | `0x0074EE40` | `0x00753F51` | `0x00702120` |
| `_isEquipping` | `ItemBase` | 19 | `0x0074EF90` | `0x00753F66` | `0x00702280` |
| `_getEquippingSlot` | `ItemBase` | 20 | `0x0074F0E0` | `0x00753F7F` | `0x00702330` |
| `_getExtendedTemporaryItem` | `CharaBase` | 65 | `0x00755BB0` | `0x007579FC` | `0x00708840` |

The `ItemBase` switchboard is `0x00753DD0`, stored at slot 2 of the vftable
`0x00FD5484`. The other seven calls of its 20 are `_getCatalogID` (1),
`_countStack` (4), `_getKind` (6), `_getPackage` (7), `_getNameIndex` (9),
`_bindSpreadSheetData` (10) and `_updateWork` (17), which other contracts record.
The `CharaBase` switchboard is `0x007574A0`. The `ItemBase` registrars use the
wrapper `0x00726670`, a const holder with the invoke routine `0x0071A910` and the
target type descriptor `0x012C0864`. `_getExtendedTemporaryItem` uses `0x00726510`,
the non-const `CharaBase` holder. Each invoke routine casts the receiver from
`LuaControl` (`0x01270B4C`) to the target class and returns without calling the
callback when the cast gives a null pointer. A receiver that is not an item
control therefore reaches no item callback (`STATIC`).

## Item reference and lookup

Twelve of the thirteen `ItemBase` callbacks repeat one prologue. They load the
variant byte at receiver `+0x70`, the slot dword at `+0x6C`, the key address
`+0x68` and the owner dword at `+0x64`. They call `0x006F51A0` on the owner, which
returns the package manager at owner `+0xD8`. A variant byte of 1 selects
`0x006EE480` on the tree at manager `+0x14` and any other value selects
`0x006EE3E0` on the tree at manager `+0x08`. Both return the item record or 0. The
scheduler item contract gives the lookup body. `_getOwner` is the exception. It
reads the key and the owner field and never looks a record up.

The four fields are written by `0x006E2770`, which builds the control that
`_getItem` and `_getExtendedTemporaryItem` return. The record it receives holds a
descriptor pointer at `+0x08`. The descriptor holds a target pointer and a slot
dword. The first dword of the target becomes the owner at `+0x64`, the dword at
target `+0x04` becomes the key at `+0x68` and the slot dword becomes `+0x6C`. The
variant byte at `+0x70` is 1 when the byte at target `+0x21` is 0 (`STATIC`,
`0x006E28F9..0x006E291B`). The variant byte therefore follows the package that
the item came from and not the native that created the control. Which packages
carry the byte 0 was not traced.

A lookup result of 0 is not tested by any callback that dereferences it. The
loops of `_isTrading`, `_isEquipping` and `_getEquippingSlot` compare each slot
record with the result and skip zero slot records, so they answer false or nil for
a missing record. Every other callback reads at a small address and its run-time
effect was not run.

## Item record fields

The record is the `Item` derived object of the scheduler item contract. The
offsets below are record relative. The static data object at `+0x28` is built by
`0x006DD700`, which zeroes its dwords at `+0x54`, `+0x58` and the bytes at `+0x60`
and `+0x61`, and sets its dword at `+0x5C` to -1. `0x006DD7B0` copies it. The
attribute object at `+0x8C` is built by `0x007698E0` and the record stores a byte
0 at `+0xB8` (`STATIC`, `0x006DF5E2..0x006DF607`).

| Record offset | Width | Read by | Role |
| --- | --- | --- | --- |
| `+0x18` | dword | `_countStack` | Stack count, `INFERRED` |
| `+0x1C` | dword | `_isTrading` | Pushed with a true result, `INFERRED` |
| `+0x20` | byte | `_getNameIndex` | Name sheet index, `INFERRED` |
| `+0x24` | dword | `_getCatalogID` | Catalog id, `INFERRED` |
| `+0x7C` | dword | `_getMaxStack`, `_isStackable` | Maximum stack count, `INFERRED` |
| `+0x80` | dword | `_getKind` | Kind, `INFERRED` |
| `+0x88` | byte | `_isRare` | Rare flag, `INFERRED` |
| `+0x89` | byte | `_isLocking`, `_getLockingInfo` | Flag read for the key `0xFF`, `INFERRED` |
| `+0x8C` | 0x2C bytes | the lock and dealing natives | Attribute object, `STATIC` |

The attribute object holds two byte vectors and four scalars. The tag vector has
its begin pointer at object `+0x04` and its end pointer at `+0x08`, which are
record `+0x90` and `+0x94`. The value vector has its pointers at `+0x14` and
`+0x18`, which are record `+0xA0` and `+0xA4`. The mode byte is at object `+0x20`,
the value byte at `+0x21`, attached1 at `+0x24` and attached2 at `+0x28`, which
are record `+0xAC`, `+0xAD`, `+0xB0` and `+0xB4`. `0x0076B760` decodes the wire
record and calls `0x00769760`, which fills four entries of each vector from the
wire bytes at `+0x20` and `+0x24` and stores the scalars from the wire byte at
`+0x13`, the dword at `+0x14`, the byte at `+0x12` and the dword at `+0x18`. The
[Bazaar contract](bazaar-native-wire-contract.md#dealing-fields-read-by-lua)
names the same fields as tags, tag values, mode, attached1, value byte and
attached2.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_getMaxStack` | `ItemBase` | none | `int` | no |
| `_isStackable` | `ItemBase` | none | `bool` | no |
| `_isRare` | `ItemBase` | none | `bool` | no |
| `_getOwner` | `ItemBase` | none | `LuaControl*` or nil | no |
| `_isLocking` | `ItemBase` | none | `bool` | no |
| `_getLockingInfo` | `ItemBase` | `int` | `int` or nil | no |
| `_isDealing` | `ItemBase` | none | `bool` | no |
| `_isAttached` | `ItemBase` | none | `bool` | no |
| `_getDealingInfo` | `ItemBase` | none | `int` or nil | no |
| `_getDealingAttached` | `ItemBase` | none | `Which<int,LuaControl*>`, `int`, `int` | no |
| `_isTrading` | `ItemBase` | none | `bool`, `int` | no |
| `_isEquipping` | `ItemBase` | none | `bool` | no |
| `_getEquippingSlot` | `ItemBase` | none | `int` or nil | no |
| `_getExtendedTemporaryItem` | `CharaBase` | `int`, `int` | `LuaControl*` or nil | no |

The list builders are `0x0072B440` for none, `0x00728C20` for an int,
`0x00728B70` for a bool, `0x0072C260` for a `LuaControl*` and `0x00583CE0` for two
ints. `0x0072BCA0` builds the bool and int of `_isTrading` through `0x00727E60`,
which selects the registry entries 2 and 0. `0x00742AE0` builds the three
returns of `_getDealingAttached`. Its first entry is a `Which` that
`0x0073E0B0` builds from `0x0072C680` over the registry entries 0 and 4, and the
other two are ints. The pushers are `0x00584F70` for an int, `0x00748870` for a
bool, `0x00748920` for nil and `0x00748B30` for a control. None of the natives
calls the yield request `0x00CD2860`.

## Stack and rare queries

`_getMaxStack` (`0x00701870`) pushes the dword at record `+0x7C` as an int.
`_isStackable` (`0x007018C0`) compares the same dword with 1 by an unsigned
compare and pushes whether it is above 1. The values 0 and 1 push false and
`0xFFFFFFFF` pushes true. `_isRare` (`0x00701970`) pushes the byte at record
`+0x88` through the bool pusher, which copies one byte. The callback does not
normalize it. That the dword is the largest stack size and the byte the rare flag
is `INFERRED` from the native names and from the shared comparison. The static
data object that holds both is zeroed by its constructor and the code that fills
it was not traced.

## Owner

`_getOwner` (`0x00701AD0`) selects its push by the key at receiver `+0x68`.

| Key | Push | Source |
| --- | --- | --- |
| `0xFF`, the dword at `0x00FE0508` | nil | `0x00701AF2..0x00701B23` |
| `0xFC`, the dword at `0x00FE0514` | the `CharaBase` control that identity `[[Y+0x124]+0x04]` resolves to | `0x00701B26..0x00701BB8` |
| any other | the control stored at receiver `+0x64` | `0x00701BBB..0x00701BCB` |

The `0xFC` branch reads `R` from `0x00CC7510` on `ExecuteParameters` `+0x04`,
takes `Y` as `[[R]+0x04]` and reads the object pointer stored at `Y +0x124`. The
dword at that object `+0x04` goes through `0x00714270`, then `0x00CC7A50` resolves
it on `ExecuteParameters` `+0x04` and `0x009DA6CC` casts the result from
`LuaControl` to `CharaBase` (`0x012709A4`). An identity that resolves to nothing
casts to a null control. Whether a null control reaches Lua as nil was not traced,
which is the boundary that the
[fade contracts](fade-actor-group-native-contract.md#fade-natives) also record.
The default branch hands the address of receiver `+0x64` to `0x00748B30`, which
dereferences it, so it pushes the same owner dword that every other callback gives
to `0x006F51A0`. That the key `0xFC` marks an item held for another party is
`INFERRED` from its use in `_isTrading`. The writer of `Y +0x124` was not traced.

## Equipment and trade queries

`_isEquipping` (`0x00702280`) looks the record up and then walks the slots 0 to
`0x22` of the package key `0xFE` at `0x00FE050C`. The count is the dword `0x23` at
`0x00FE052C`. Each pass calls the owner lookup for the key and the index. A
nonzero slot record that equals the item record pushes true. No match pushes
false. `_getEquippingSlot` (`0x00702330`) runs the same loop. A match passes the
index to `0x0078BCE0`, which adds 1, and pushes the sum as an int. No match pushes
nil. The result is the one-based slot (`STATIC`) and its role as the equipment
slot is `INFERRED`.

`_isTrading` (`0x00702120`) looks the record up and walks the slots 0 to 3 of the
key `0xFD` at `0x00FE0510` and then the slots 0 to 3 of the key `0xFC` at
`0x00FE0514`. The count is the dword 4 at `0x00FE0530`. A match in either loop
pushes true and then the dword at record `+0x1C` as an int. No match pushes false
and the int 0. The two lists are `INFERRED` to be the two sides of a trade from the
native name. The dword at `+0x1C` is the one that the scheduler item contract
records as copied from wire `+0x1C`.

An absent record answers false and 0 here, because a zero slot record is skipped
and a nonzero one never equals a zero item record. The lookup of a slot past the
end of a package vector reaches the invalid vector subscript throw of the
scheduler item contract. The vector sizes were not traced, so that path was not
shown to be reachable.

## Lock and dealing queries

All six callbacks work on the attribute object at record `+0x8C`.

| Native | Callback | Answer |
| --- | --- | --- |
| `_isLocking` | `0x00701C40` | `0x00763360` is true when a tag byte is not 0, `0xC9` or `0xCA`. A key of `0xFF` ORs the byte at record `+0x89` into the result. |
| `_getLockingInfo` | `0x00701CB0` | `0x007633D0` finds the low byte of the int argument in the tag vector. A hit pushes the value byte at the same index. A miss pushes the int 0 for key `0xFF`, tag 3 and a byte 1 at record `+0x89`, otherwise nil. |
| `_isDealing` | `0x00701DD0` | `0x00764DC0` is true when the tag vector holds `0xC9`. |
| `_isAttached` | `0x00701E30` | `0x00764E30` is true when the tag vector holds `0xCA`. |
| `_getDealingInfo` | `0x00701E90` | `0x00763460` runs the `0x007633D0` scan with the tag `0xC9`. A hit pushes the value-vector byte at the index of the `0xC9` tag, a miss pushes nil. |
| `_getDealingAttached` | `0x00701F20` | See below. |

The scans are bounds checked and call `0x009D22B4` on a broken iterator. An empty
tag vector gives false or nil. `_getLockingInfo` tests the cell vector size and
calls `0x009D22B4` for an empty one. The Bazaar contract reads the `0xC9` and
`0xCA` tags as the dealing and attachment tags, and that reading is `INFERRED`
here from the native names. A lock reading of the other tags is `INFERRED` from
`_isLocking` skipping exactly those two tags.

`_getDealingAttached` first calls `0x00764EA0`, which answers 0 when the tag
vector has no `0xC9` and otherwise copies the mode byte, attached1, the value byte
and attached2. The mode is compared with the bytes at `0x00FE049D`, `0x00FE049F`
and `0x00FE049E`, which hold 0, 2 and 1.

| Case | Pushes |
| --- | --- |
| No `0xC9` tag, mode 0, or a mode other than 1 and 2 | nil, nil, nil |
| Mode 2 | attached1 as an int, the value byte as an int, attached2 as an int |
| Mode 1 and the packed reference resolves | a new `ItemBase` control, nil, nil |
| Mode 1 and the packed reference does not resolve | nil, nil, nil |

Mode 1 takes bits 16 to 23 of attached1 as the package key and bits 0 to 15 as the
slot. Neither is decremented. The lookup runs on the package manager of the
receiver owner with the receiver variant byte. The control comes from
`0x006E2770` with the flag 0. The [Bazaar contract](bazaar-native-wire-contract.md#dealing-fields-read-by-lua)
gives the same mode 2 order. That mode 1 carries an item reference and mode 2
carries numbers is `STATIC`. What the numbers mean is `INFERRED`.

## Extended temporary item

`_getExtendedTemporaryItem` (`0x00708840`) builds a stack `ItemBase` with
`0x006DD450`, calls the helper `0x00702400` with the receiver and the flag 1 and
destroys the object through `0x006DD4D0`. `_getItem` calls the same helper with
the flag 0. The helper tests the cell vector size before each of the two int
reads and calls `0x009D22B4` for fewer than one or two cells. It subtracts 1 from
the package and from the slot with no range test. It calls `0x006F51A0` on the
receiver, finds the package with `0x006E5BA0` at `0x0070249D` and discards the
result with no branch on it, calls `0x006F51A0` again and then calls `0x006EE3E0`
with the key address and slot. It never calls `0x006EE480`, whatever the flag. A result of 0 pushes nil. Otherwise it passes the
record and the flag to `0x006E2770` and pushes the control it returns.

The flag only selects among three thin wrappers of `0x00CD9360`. The value 0 calls
`0x00CC80A0` and a nonzero value calls `0x00CC81E0` or `0x00CC8140` as
`0x00758EC0` decides. The fields stored in the control do not depend on the flag.
What differs for a script between the two natives is therefore not visible in the
Lua pushes and was not traced. A package number of 0 becomes the key
`0xFFFFFFFF`, which goes to the tree find and gives nil unless such a package
exists. A slot number of 0 becomes the index `0xFFFFFFFF`, which reaches the
invalid vector subscript throw when the package exists.

## Script call sites

| Native | Index sites | Scripts | Direct calls | Debug console |
| --- | ---: | ---: | ---: | ---: |
| `_getMaxStack` | 12 | 7 | 11 | 1 |
| `_isStackable` | 42 | 30 | 41 | 1 |
| `_isRare` | 1 | 1 | 1 | 0 |
| `_getOwner` | 2 | 1 | 2 | 0 |
| `_isLocking` | 1 | 1 | 0 | 1 |
| `_getLockingInfo` | 6 | 2 | 1 | 5 |
| `_isDealing` | 4 | 3 | 3 | 1 |
| `_isAttached` | 3 | 3 | 2 | 1 |
| `_getDealingInfo` | 2 | 2 | 1 | 1 |
| `_getDealingAttached` | 8 | 5 | 7 | 1 |
| `_isTrading` | 5 | 3 | 5 | 0 |
| `_isEquipping` | 44 | 19 | 43 | 1 |
| `_getEquippingSlot` | 3 | 2 | 2 | 1 |
| `_getExtendedTemporaryItem` | 10 | 3 | 10 | 0 |

The first three columns are `MEASURED` against the call-site index and total 143
sites. The direct call column is the count of method calls that the bytecode scan
resolves and the last column counts index sites in `commanddebugger/commanddebuggerdev`.
That script holds the native names as string constants and the scan does not
resolve how it calls them. The two columns add up to the index sites.

The scan also shows these call shapes (`INFERRED`). The `ItemBase` natives take no
argument at every direct site except one `_getLockingInfo` call from
`item/itembaseclass_common`, which passes the constant 3, the tag that the callback
special cases for the key `0xFF`. All 10 `_getExtendedTemporaryItem` sites pass
two arguments and two of them pass the package 1. The five `_isTrading` sites
take both results and five of the seven `_getDealingAttached` sites take all
three. `_isRare` and one `_isAttached` site are tail calls. Widget scripts
hold 116 of the 143 sites.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list,
return list, receiver check and callback contract: `_getMaxStack`,
`_isStackable`, `_isRare`, `_getOwner`, `_isLocking`, `_getLockingInfo`,
`_isDealing`, `_isAttached`, `_getDealingInfo`, `_getDealingAttached`,
`_isTrading`, `_isEquipping`, `_getEquippingSlot` and
`_getExtendedTemporaryItem`. A client that implements them needs the item record
store behind the package manager at owner `+0xD8`, the record fields above and the
attribute object. The values of those fields come from the server.

## Open

- The code that fills the static data object at record `+0x28`, which supplies
  `+0x7C`, `+0x80`, `+0x88` and `+0x89`, and the values that the shipped item
  data gives them.
- The package records of the keys `0xFD`, `0xFC` and `0xFE`, their slot counts
  and the code that installs an item into a slot.
- The roles of the keys `0xFF`, `0xFE`, `0xFD` and `0xFC`, the writer of
  `Y +0x124` and the packages whose record has the byte 0 at `+0x21`.
- The tag numbers other than `0xC9` and `0xCA` that a server may send, and the
  mode byte values.
- Whether a null control reaches Lua as nil.
- The run-time effect of an absent item record in the callbacks that read it and of
  the invalid vector subscript throw.
- How `commanddebugger/commanddebuggerdev` calls the natives it names.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The script
call shapes come from the `.le.lpb` files of an installed client, decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser over the `SELF` and `TAILCALL` call sites. They are `INFERRED` because no
tracked artifact carries them. The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registrars | `0x0074DBE0,0x0074DD30,0x0074DFD0,0x0074E3C0,0x0074E660,0x0074E7B0,0x0074E900,0x0074EA50,0x0074EBA0,0x0074ECF0,0x0074EE40,0x0074EF90,0x0074F0E0,0x00755BB0` |
| Switchboards and holders | `0x00753DD0,0x007574A0,0x00726670,0x00726510,0x0071A910` |
| Callbacks | `0x00701870,0x007018C0,0x00701970,0x00701AD0,0x00701C40,0x00701CB0,0x00701DD0,0x00701E30,0x00701E90,0x00701F20,0x00702120,0x00702280,0x00702330,0x00708840` |
| Lookup and control | `0x006F51A0,0x006E5BA0,0x006EE3E0,0x006EE480,0x00702400,0x006E2770,0x00CD9360,0x00CC80A0,0x00CC8140,0x00CC81E0,0x00758EC0` |
| Attribute object | `0x00763360,0x007633D0,0x00763460,0x00764DC0,0x00764E30,0x00764EA0,0x00769760,0x0076B760,0x007698E0,0x006DF580,0x006DD700,0x006DD7B0` |
| Owner | `0x00CC7510,0x00714270,0x00CC7A50,0x009DA6CC` |
| Lists and pushers | `0x00728C20,0x00728B70,0x0072B440,0x0072C260,0x00583CE0,0x0072BCA0,0x00727E60,0x00742AE0,0x0073E0B0,0x0072C680,0x007270B0,0x00584F70,0x00748870,0x00748920,0x00748B30,0x0078BC90,0x0078BCD0,0x0078BCE0` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
