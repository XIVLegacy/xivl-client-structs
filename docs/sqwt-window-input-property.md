# Sqwt Window input-property contract

`SqwtIsEnableInput` selects a `Sqwt::Window` property descriptor and a
packed cell at object `+0x3E0`. The selected text parser can turn a reached
`False` value into native setter arguments `(V,P,N)=(0,0,1)`. An admitted
changed-value update clears cell bit 5 and sets bit 2. Lookup, preprocessing,
property flags and the actual receiver remain conditions; this does not
establish input-event suppression for a particular widget.

The selected indexed read samples that stored bit as one byte and uses an
existing string object to choose text output. Native completion flags do not
establish an effective property value, a present result or a Lua return.

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
| `D+0x20` | Indexed read target `0x00922300` | `0x00F20D82` |
| `D+0x24` | Zero paired adjustment | `0x00F20D88` |
| `D+0x28` | Text parser `0x00925700` | `0x00F20D8E` |
| `D+0x2C` | Zero parser receiver adjustment | `0x00F20D94` |

The [indexed stored-read contract](#indexed-stored-read) qualifies this
target's native operation. Its actual info dispatcher and Lua binding remain
unproved.
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

## Indexed stored read

In `0x00922300`, incoming ECX supplies `O`, entry `[ESP+4]` supplies
numeric index `I`, and `[ESP+8]` supplies `W`. An unsigned `I>0x12`
reaches `0x009224DA`, sets only `AL=0`, and returns with `RET 8`.
That path dereferences neither `O` nor `W` and makes no call or inline W
assignment. It does not zero full EAX. Valid indices use a 19-entry table
directly; this body performs no name or descriptor lookup.

Table slot `0x10` at `0x00922520` selects `0x00922493`. It forwards
`W` and calls `0x0093E220` with ECX equal to `O+0x3E0`. After normal
callee return, `0x009224A3` overwrites AL with 1 and returns with
`RET 8`; upper EAX remains unnormalized. Other valid cases also return
AL=1, including case 7 when a null stored pointer skips its output call.
This is native branch completion, not result presence or truth.

The accepted `D+0x24=0` is paired metadata. This body reads neither D nor
that adjustment; its own receiver addition is exactly `+0x3E0`. Invocation
through D, the incoming native receiver, and an actual Lua `_getProperty`
call remain separate conditions.

At `0x0093E221`, the selected callee samples byte `C` at that cell before
any helper call. Its shifts and mask produce `q=(C>>5)&1`. Only one local
byte is initialized: at callee entry ESP=S, it occupies `S-1`, the highest
byte of a four-byte stack reservation. CALL `0x0093E236` supplies its
address as explicit argument 1 and W as argument 2 to `0x00989060`, with
ECX also equal to W. No q dword is established. There is no inline property
flag, missing-state, sentinel, presence or preprocessing check before this
sample and no inline write back to the cell.

### W-dependent text output

In `0x00989060`, entry `[ESP+4]` is Q, the address of that byte, and
`[ESP+8]` is W. The prologue lowers ESP by `0x7C`, making the load at
`0x00989085` from `[ESP+0x84]` W. Incoming ECX is unused and is replaced
with W before the first receiver call. W must already support the reached
string operations; this is not construction of an arbitrary destination.

Q is reloaded from `[ESP+0x80]` on the reached balanced call frames.
Comparisons at `0x009890A3`, `0x00989159` and `0x0098919D` read
exactly one byte and classify zero versus nonzero. They read no adjacent
uninitialized dword. W-dependent calls precede these comparisons, so the
operation observes Q at comparison time, rather than freshly reading the
original cell. Relating it to that cell requires the same actual object,
retained q storage and no intervening cell change. Uninspected helper alias
or reentrant effects remain outside this result.

The adapter uses the published `0x00445D60`
[equality contract](native-input-ui-boundaries.md) and `0x00445E50`
[character-count contract](chocobo-naming-native-contract.md). The exact
literal supplied to equality is `Not`. No case-sensitivity rule is inferred.
The selected text operations are:

| Reached condition | q=0 | q nonzero, including q=1 | Operation |
|---|---|---|---|
| Equality against `Not` returns AL nonzero | `True` | `False` | C-string assignment `0x004489C0` |
| Equality AL zero, character count unsigned below 1 | `False` | `True` | Same assignment |
| Equality AL zero, count at least 1, first byte returned through `0x00445060(W,0)` differs from `?` | `False` | `True` | Same assignment |
| `?` branch with a valid local container containing at least two tokens | Token index 1 | Token index 0 | Indexed string assignment |
| `?` branch with zero local begin or unsigned quotient below 2 | No output assignment call | No output assignment call | Local cleanup and return |

Insufficient token data does not fall back to `False`/`True`. No output
assignment call does not imply that earlier helpers had no effect on W.
The character-count helper's cached/null/UTF-8 conditions remain part of
its own contract; count and first-byte tests are distinct operations.

The `?` branch passes literal source bytes ` ?:` and the dword read from
`0x00F67298` to local constructor `0x00447260`. It passes that local object
to `0x0044F770`, whose
[tokenization and indexing contract](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/sqwt-command-parameter-grammar.md)
owns delimiter-set splitting and `0x00444CB0`'s `0x54`-byte entry stride.
The constructor and global dword are uninspected here. Confirmed source
literal bytes do not alone prove the effective constructed delimiter set.

The adapter subtracts local begin from end, computes signed truncation of
the wrapped difference divided by `0x54`, then tests the quotient with
unsigned `JB 2`. Valid container pointers remain a condition: a negative
quotient can pass this comparison. On the admitted path, it supplies index
1 for zero or 0 for nonzero to `0x00444CB0`, then passes the returned entry
to `0x00447450`. The published
[Utf8String assignment contract](autotranslate-selection-contract.md)
qualifies the copy for distinct valid objects and successful capacity/copy
operations before local cleanup. Its success and lifetime are not inferred
from the adapter's later return.

### Assignment and result boundary

The selected `0x004489C0`
[C-string assignment](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/resource/sqwt-anime-property.md)
scans its source T to NUL, obtains length N excluding the terminator, and
calls `0x00447010` with ECX=W and arguments `(N+1,1)`. After return it
reads dword[W], calls `0x009D5110(dword[W],T,N)`, reloads dword[W],
and writes NUL at byte[dword[W]+N]. `True` requests extent 5 and transfer
length 4; `False` requests extent 6 and transfer length 5.

Its only inline memory store is that terminator. It does not inline a W
constructor, tag/bool store, dword[W] assignment, null test or failure-result
check. Capacity, initialization, failure, aliasing and ownership remain
behind `0x00447010` and the transfer helper. The
[limited byte-copy proof](https://github.com/XIVLegacy/xivl-decomp/blob/main/docs/net/guildleve-initializer-route.md)
for `0x009D5110` covers selected aligned nonoverlapping small ranges; it
does not establish every arbitrary C-string transfer here.

Neither selected body directly forwards or saves Q's address in W. Downstream
calls receive selected literal or local-entry pointers. This does not prove
arbitrary helper alias effects or universal output ownership.

The adapter normal epilogues normalize neither AL nor full EAX. The literal
path leaves the value from `0x004489C0`, which leaves EAX from the transfer
helper; the local/no-assignment path leaves EAX from cleanup `0x004042A0`.
The indexed reader's later AL=1 overwrites that low byte. None of these
observations establishes a native bool return, result count or Lua result.

For the same unchanged stored cell, the read supplies the stored bit to a
W-dependent text operation. It does not establish an inherited, default or
effective-value rule. Prior write notifications, later writes, q-storage
aliasing, object lifetime, W initialization and assignment success remain
conditions.

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
| Indexed stored read | `[0x00922300,0x009224DF)` |
| Single-byte sample forwarder | `[0x0093E220,0x0093E241)` |
| Byte-to-text adapter | `[0x00989060,0x009891C5)` |
| Selected C-string assignment | `[0x004489C0,0x00448A03)` |

The parser's unsigned guard, all 19 switch targets, default path and 17
terminal returns cover its complete contiguous reachable body. Its table
is `[0x00925A54,0x00925AA0)`. Exclude the one-byte gap at
`0x00925A53`; the next catalogued function starts at `0x00925AA0`.

The indexed reader's unsigned guard, all 19 switch cases and out-of-range
default cover its complete body with 20 terminal returns. Its table is
`[0x009224E0,0x0092252C)`. Exclude byte `0x009224DF` and the trailing
interval `[0x0092252C,0x00922530)` before the next catalogued function.
The sample forwarder has one straight path. The byte-to-text adapter has
two normal returns and the assignment helper has one loop and `RET 4`.
Calls and exception handling remain outside these normal-flow claims.

Selected data reads are table `0x012E0310+76`, info locator pointer and
six slots `0x01069F5C+28`, locator `0x01179018+20`, bounded info name
`0x012E02D4+60`, Window primary locator pointer `0x0106A0B8+4`,
locator `0x01179064+20`, Window name `0x01269E28+18`, interception
slot `0x0106A0F0+4`, and parser table `0x00925A54+76`. Read pointer
data as little-endian dwords and account for stack changes and receiver
adjustments. The setter/form/lookup/conversion source pages are pinned by decomp
revision `d56c7606e0bdf7d9964067834e9caf9129134baf`.
The Lua helper contract is pinned by scripts revision
`b1bfc909b4093b5e1c65dbc1a57113e567db1b6e`.

For the read, inspect its 19-dword table at `0x009224E0` and these exact
first-NUL records in `.rdata`:

| VA | Source bytes before NUL | Size including NUL |
|---|---|---:|
| `0x010772FC` | `Not` | 4 |
| `0x01077300` | `False` | 6 |
| `0x01077308` | `True` | 5 |
| `0x01077310` | ` ?:` - space, question mark, colon | 4 |
| `0x01077314` | `True` | 5 |
| `0x0107731C` | `False` | 6 |

Each literal is NUL-framed within its PE section, with a 64-byte upper cap.
The read's additional structs helper contracts are pinned at revision
`c9b394f22bbe005edc9cb62a5a374b4aa52a7d2c`; its decomp helper contracts
are pinned at `ad483c8b6d441396e70a3faf310f1021f58a6d07`.

This joins the static descriptor, selected Window registration, parser and
conditional stored bit. It leaves actual Lua/native callable and receiver
binding, part and name resolution, effective list membership, preprocessing
outcome, object/table lifetime and input-routing or visible effects unproved.
It does not establish SceneActor ownership, actual `_getProperty` dispatch,
or the Lua representation and presence of a returned value.
