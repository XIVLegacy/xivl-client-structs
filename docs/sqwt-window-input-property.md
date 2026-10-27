# Sqwt Window input-property contract

`SqwtIsEnableInput` selects a `Sqwt::Window` property descriptor and a
packed cell at object `+0x3E0`. The selected text parser can turn a reached
`False` value into native setter arguments `(V,P,N)=(0,0,1)`. An admitted
changed-value update clears cell bit 5 and sets bit 2. Lookup, preprocessing,
property flags and the actual receiver remain conditions; this does not
establish input-event suppression for a particular widget.

## Binary and method

The input is retail `ffxivgame.exe`, build `2012.09.19.0001`, PE32 i386,
image base `0x00400000`, size `15996808`, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
All addresses are VAs; subtract `0x00400000` for RVA. Static PE section
mapping and Capstone `5.0.7` x86 decoding supplied the observations.
Retained symbol extents and instruction listings corroborated the complete
initializer, constructor and native wrapper/helper ranges. The text parser
was framed by its complete reachable control flow and bounded switch table.

`O` denotes the complete Window receiver on the selected construction path,
`D` its selected property-info object, and `R=O+0x3E0` the packed cell.
These names describe native argument roles, not an observed Lua instance.

## Descriptor, info object and owner

The exact name at `0x01069DBC` identifies descriptor `0x013572E0` and
descriptor index `0x10`. The name initializer at
`0x00F20CE0..0x00F20CEF` is recorded in
[the enable-property finding](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/input/game-controller-startup.md#enable-properties-and-remaining-barrier).

Initializer `0x00F20D50` supplies table `0x012E0310` and count `0x13`
to common info constructor `0x0098B250`, with `D=0x01357350`. The
raw-backed table is `[0x012E0310,0x012E035C)`. Its ordinal `0x10`
entry at `0x012E0350` equals `0x013572E0`. A table ordinal and the
descriptor's stored index are separate values; they coincide here.

The descriptor and `D` lie in virtual-only `.data`, beyond raw end RVA
`0x00F24000` and within virtual end RVA `0x00F7C940`. Their initialized
contents follow from the initializer instructions, not file-backed zeroes.
The pointer table supplies original raw data independently of that state.

The initializer installs info vtable `0x01069F60` and these fields:

| Info field | Selected value | Store VA |
|---|---|---|
| `D+0x20` | Accessor candidate `0x00922300` | `0x00F20D82` |
| `D+0x24` | Zero paired adjustment | `0x00F20D88` |
| `D+0x28` | Text parser `0x00925700` | `0x00F20D8E` |
| `D+0x2C` | Zero parser receiver adjustment | `0x00F20D94` |

The accessor candidate's body and return contract are uninspected.
Info locator `0x01179018` has complete-object offset zero and
TypeDescriptor `0x012E02CC`, named
`.?AV?$DependencyPropertyInfo@VWindow@Sqwt@@@Sqwt@@`. Its virtual
`+4` selects lookup `0x00965FF0`; virtual `+0x0C` selects parser adapter
`0x0091B440`.

Constructor `0x009246F0` captures `O` in ESI at `0x00924717` and
installs primary Window vtable `0x0106A0BC` at `0x00924724`. Its
locator `0x01179064` has offset zero and TypeDescriptor `0x01269E20`,
named `.?AVWindow@Sqwt@@`. At `0x00924B34..0x00924B45` the
constructor supplies this exact `D` and `O` to `0x0098B400`. That call
dominates its sole normal return. The
[common registration-helper proof](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/sqwt-markup-font-numeric-properties.md#fm-01-named-descriptors-and-selected-registration)
records conditional list work and retention of `D+0x0C` at `O+0x10`.
Successful insertion and effective runtime list membership remain conditions.

The constructor locally sets bit `0x20` in `O+0x3E0` at
`0x009249EC..0x009249F7`. Uninspected callee effects and later writes
prevent a universal effective default or lifetime claim. This does not pin
the property's metadata type or a source-level declaration.

## Conditional Lua false to text-parser arguments

The published
[setInputEnable helper](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/content-director-ui-contracts.md#nominal-setinputenable-forwarding)
forwards the exact key and value unchanged. With the nominal
[setProperty helper](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/content-director-ui-contracts.md#nominal-setproperty-forwarding),
the one-false request becomes the saved call
`F(receiver,nil,widgetName,"SqwtIsEnableInput",false)`, where `F` was
looked up as `receiver._setProperty` before the dynamic widget-name reads.
Both helpers discard results and return zero values on normal completion.
The native
[WidgetBase property-access contract](widget-native-call-contract.md#property-access)
records the optional leading name, Nil route and typed-value pickup. It
does not identify an actual callable, receiver or resolved part.

On the reached native bool path, processor slot `0x00542680` formats
`True` or `False`. Form setter `0x00537DE0` resolves the part and key,
then can call string property engine `0x00912850` with flag zero. The
[typed-value and form-setter contract](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/sqwt-anime-property.md#route-to-the-setter)
owns those gates and the special `Anime` handling.

For an unqualified name, the
[registered-info lookup and dispatch](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/sqwt-markup-font-numeric-properties.md#fm-02-attribute-shaped-node-to-property-parser)
searches the owner's info list in reverse order and calls info virtual
`+4`. Successful selection of this `D` and descriptor supplies the
descriptor's `+0x14` index, value wrapper and incoming zero flag to info
virtual `+0x0C`. Adapter `0x0091B440` uses `D+0x28` and adds
`D+0x2C=0` to the receiver. Collision behavior, effective precedence and
successful name selection remain conditions.

Window virtual `+0x34`, selected entry `0x0106A0F0`, is `0x00910B50`.
The published false-return proof for that exact target closes the selected
interception step, conditional on the installed Window table. The generic
engine's nonbinding path must also be reached.

Parser `0x00925700` bounds its unsigned index by `0x12`. Jump table
`0x00925A54` entry `0x10` at `0x00925A94` selects case
`0x009259CC`. At `0x009259ED` that case calls `0x009321D0` with
`R=O+0x3E0` and these explicit arguments:

| Position | Argument |
|---:|---|
| 1 | Incoming value wrapper, parser argument 2 |
| 2 | Owner `O` |
| 3 | Callback pointer `0x009238A0` |
| 4 | Zero receiver adjustment |
| 5 | Descriptor `0x013572E0` |
| 6 | Incoming engine flag, parser argument 3 |
| 7 | Literal 1 |

The parser's `0x2C` local allocation and saved ESI make its load
`[ESP+0x3C]` at `0x009259CC` the third argument. After five pushes,
`[ESP+0x4C]` at `0x009259E1` supplies argument 2. The case ends with
`RET 0x0C`. It calls the typed text parser directly, rather than native
wrapper `0x009245C0`.

The shared
[boolean conversion and packed-store proof](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/sqwt-font-edge-property-bridge.md)
owns `0x009321D0` preprocessing, its sentinel exit, conversion through
`0x00988F90`, and the call to `0x0099C780`. With an unchanged valid
non-sentinel `False` wrapper, non-null comparison pointers and global
`0x01363F24=0`, ASCII-folding comparison with `True` yields normalized
`q=0`. Other preprocessing and the nonzero-global locale path remain
conditions. The typed path supplies `q`, owner, callback, adjustment,
descriptor, incoming flag and 1 to `0x0099C780`, retaining `R`.
Thus the reached zero-flag path supplies `(V,P,N)=(0,0,1)` below.

## Native byte-storage contract

Native wrapper `0x009245C0` takes three native arguments `(V,P,N)`,
selects the same descriptor and adds `0x3E0` to its own incoming object
pointer. It forwards that owner, callback `0x009238A0` and zero adjustment
to `0x0099C780`. Its actual object identity is unproved. This is a separate
descriptor-using wrapper, not a proved registered setter entry. The selected
text-parser path reaches the shared helper through `0x009321D0`.

Let `C` be the byte at `R`. The helper observes the low bytes of `V`,
`P` and `N`; `P` describes its local policy role, not an established
source-level parameter name.

1. If `C` bit 4 is set, `0x0099C794` calls `0x009157C0` with owner
   and descriptor, then clears bit 4. The callee's effects are uninspected.
2. The store is refused with `AL=0` when bit 1 is set and `low8(P)=0`,
   or when bit 1 is clear, `low8(P)=1` and bit 0 is clear. These checks
   use the cell after the preceding call and clear. Refusal can follow
   side effects. Accepted `low8(P)=0` clears bit 0 first.
3. At `0x0099C7D1..0x0099C7DF`, the helper compares `(C>>5)&1`
   with the entire low byte of `V`. On inequality, its inline write puts
   `V` bit 0 into cell bit 5 and sets bit 2, retaining the other local bits.
   The comparison is byte-wide; storage uses only `V` bit 0. Arbitrary
   nonzero-to-true normalization is not the observed rule.
4. Only that unequal branch with `low8(N)=1` calls `0x0099C680` at
   `0x0099C806`. It forwards cell, owner, callback pointer `0x009238A0`,
   zero, descriptor and literal 1, with ECX equal to the cell. It does not
   call the callback pointer directly. Downstream effects, including later
   cell mutation, are outside this result.
5. Accepted normal paths return `AL=1`, including equal-value paths.
   `AL=1` does not prove a changed value or consumed input. Neither native
   result establishes a Lua return value.

For admitted `(0,0,1)`, a previously set bit 5 is cleared, bit 2 is set,
and the notification helper is called. If bit 5 was already zero, the
comparison causes no value write or notification call. Preparatory and
policy-related changes remain possible in either case. These statements
describe the inline write before any uninspected downstream call.

## Reproduction and limits

Authenticate the pinned original, map VAs through its PE section table, and
decode these complete start-inclusive, end-exclusive code intervals:

| Source | VA interval |
|---|---|
| Descriptor-using wrapper | `[0x009245C0,0x009245EE)` |
| Packed-byte helper | `[0x0099C780,0x0099C813)` |
| Window info initializer | `[0x00F20D50,0x00F20DA7)` |
| Window constructor | `[0x009246F0,0x00924DBC)` |
| Window text parser | `[0x00925700,0x00925A53)` |

The parser's unsigned guard, all 19 switch targets, default path and 17
terminal returns cover its complete contiguous reachable body. Its table
is `[0x00925A54,0x00925AA0)`. Exclude the one-byte gap at
`0x00925A53`; the next catalogued function starts at `0x00925AA0`.

Selected data reads are table `0x012E0310+76`, info locator pointer and
six slots `0x01069F5C+28`, locator `0x01179018+20`, bounded info name
`0x012E02D4+60`, Window primary locator pointer `0x0106A0B8+4`,
locator `0x01179064+20`, Window name `0x01269E28+18`, interception
slot `0x0106A0F0+4`, and parser table `0x00925A54+76`. Read pointer
data as little-endian dwords and account for stack changes and receiver
adjustments. The reusable native source pages above are pinned by decomp
revision `d56c7606e0bdf7d9964067834e9caf9129134baf`.
The Lua helper contract is pinned by scripts revision
`b1bfc909b4093b5e1c65dbc1a57113e567db1b6e`.

This joins the static descriptor, selected Window registration, parser and
conditional stored bit. It leaves actual Lua/native callable and receiver
binding, part and name resolution, effective list membership, preprocessing
outcome, object/table lifetime and input-routing or visible effects unproved.
It does not establish SceneActor ownership or an actual `_getProperty`
read contract.
