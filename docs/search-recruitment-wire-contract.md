# Search and recruitment wire contract

The client processes player-search results and recruitment responses through
an application dispatcher separate from the ZoneProtoDown callbacks. The no-op
callbacks for these opcodes do not make the packets inert. The canonical
[field and evidence record](../manifests/search_recruitment_wire_contract.json)
pins the retail PE, authenticated instructions, jump tables, Lua resources and
remaining unknowns.

## Two dispatch routes

`FUN_004E20A0` calls `FUN_004DC690` at `0x004E221D`. That function calls
`FUN_004CE190` at `0x004DC715`, before its remaining opcode processing.
`FUN_004CE190` reads the opcode at IPC `+0x02`, selects the PE jump table at
`0x004CE38C`, and passes IPC `+0x10` to the selected application consumer.
The table order must be read directly: it is not the order of the code blocks.
The invocation order relative to ZoneProtoDown callbacks is not established.

| Clientbound opcode | Application consumer | Proven use |
| --- | --- | --- |
| `0x01C6` | `0x004C9D60` | Recruitment acceptance answer |
| `0x01C7` | `0x004B5F50` | Recruitment result list |
| `0x01DF` | `0x004C77B0` | Player-search rows |
| `0x01E0` | `0x004C78A0` | Player-search comments and completion |

The separate `FUN_00DBFD10` route reaches `RET 0xC` callbacks through its
ZoneProtoDown interface and DummyCallback vtables. Both observations hold.
The application route above supplies the payload consumers. No LuaActorImpl
receiver slot or retail packet-class name is established by this finding.

## Outbound framing

A native builder record has opcode at `R+0`, IPC length `L` at `R+4`, and
application data at `R+0x18`. `FUN_00DAE010`, at `0x00DAE0A9..0x00DAE0B8`,
copies `L-16` application bytes into IPC `+0x10`. A captured subevent includes
another 16-byte header, so its extent is `L+16`.

| Serverbound opcode | Native IPC bytes | Application bytes | Construction |
| --- | ---: | ---: | --- |
| `0x01DC` | 568 | 552 | Player-search profile update |
| `0x01DD` | 280 | 264 | Player-search tagged filters |
| `0x01DE` | 80 | 64 | ItemSearchDirectPurchaseWidget request |
| `0x01DF` | 296 | 280 | ItemSearchListWidget request |
| `0x01C6` | 40 | 24 | Recruitment acceptance key |
| `0x01C7` | 72 | 56 | Recruitment search controls |

These native lengths are not capture observations. In particular, the
296-byte captured `0x01DD` subevent agrees with native IPC length 280.
Serverbound `0x01DF` and clientbound `0x01DF` have independent meanings.

## Player-search requests

`FUN_00693650` constructs the `0x104`-byte filter record, calls
`FUN_008746E0`, and reaches emitter `FUN_004C7300`. Application `+0x00` is
zero. Application `+0x04` is the little-endian u16 used length, `+0x06` is
zero, and `+0x08` is the 256-byte filter tail.

| Tag | Value | Native source |
| ---: | --- | --- |
| 7 | u16 | Selected Status rows |
| 1 | u8 | Selected Class rows |
| 3 | u8 value 1 | A checkbox state bit |
| 5 | u8 | Selected Region rows |
| 8 | u8, then zero | Selected GrandCompany rows |
| 6 | u16 | Expanded Location entries |
| 2 | u8, u8 | Low bytes of positive lower and upper level controls |

Each tag precedes its value. `FUN_004B5940` and `FUN_004B59A0` emit low bytes
first and reject an append whose resulting length is 256 or greater.
For tag 2, `0x00693A41..0x00693A54` first truncates the operands to u16,
then calls `FUN_004B59A0` with width 1. The wire values are consequently one
byte each. For example, bounds 1 and 50 encode as `02 01 32`.

`FUN_00691F30` binds the five named selectors, and `FUN_00693650` selects
and serializes their rows. These native controls own the filters. The
recovered `PcSearchWidget` Lua sets widget conditions, local status properties
and class information. It does not itself serialize this filter record.

`0x01DC` instead copies a `0x224`-byte profile record after a zero dword.
`FUN_00693290` reaches `FUN_00874570` and `FUN_004C7490`.
The profile serializer `FUN_0086F7F0` writes a status selector, Region mask,
class selectors and a text buffer. Its string helper accepts fewer than
512 source bytes and copies the terminator. The manifest gives the complete
native offset basis. A player name-prefix filter and client-selected paging
token are not established by the inspected construction. The extra value 30
passed by `FUN_008746E0` is outside the copied wire query.

## Player-search results and completion

Clientbound `0x01DF` has a 12-byte application header followed by rows with
stride `0x5C`. Application `+0x00` is the result-stream correlation token,
`+0x08` is the signed-byte row count and `+0x0A` contains stream flags.
Mask 1 permits latching the initial nonzero token. Mask 4 takes the request
to error state 4. Matching rows append to the request cache and leave it in
state 2. The native consumer does not enforce the fixed packet capacity.

The observed 936-byte application extent accommodates ten 92-byte rows and
four trailing bytes after the row region. A row contains a desired class at
`+0x00`, Region selectors at `+0x02/+0x03`, location at `+0x04`, GrandCompany
at `+0x06`, status at `+0x08`, current class at `+0x0A`, name at `+0x0C`,
class/level pairs at `+0x2C` and a sparse job-class list at `+0x54`.
`FUN_0086FA90` and `FUN_00690900` establish those display associations.
The status selector drives separate online, party, invitation and AFK
presentations. It is not a single online flag.

Clientbound `0x01E0` must match the same nonzero token. Its application header
has a signed-byte comment count at `+0x04` and flags at `+0x06`. The consumer
appends a fixed 600-byte stream block from `+0x0C`. Each comment entry is a
u8 cached-row index, a big-endian u16 length `N`, and `N` text bytes including
the terminal NUL. The cursor advances `3+N`. Each new block begins at the
current cursor, preserving completed strings. An unconsumed tail is overwritten
by the next block. The native cache stores the comment pointer at row `+0x5C`,
after the copied wire prefix.

Mask 4 takes the error path before copying. Mask 2 finishes the request in
state 3 after parsing. Without mask 2 it remains in state 2. Thus
`0x01DF` begins and populates the result stream, while `0x01E0` can complete
it. These state transitions do not by themselves prove that a packet opens
or closes the widget window. `PcSearchContractor` callback slot 1 at
`0x00874610` reaches `FUN_00693B50`, which projects cached rows and comments
into the native widget.

## Recruitment list and answer

Native `FUN_004BD170` reads `PcMatchingFindWidget` controls and constructs
serverbound `0x01C7` through `FUN_004B7C10` and `FUN_004CFDA0`. The application
record contains purpose, place, two rank values, rank-mode and skill bytes,
and a 32-byte person-name buffer. The six trailing application bytes have no
established write. Lua supplies the control values; the native widget path
emits the packet.

Clientbound `0x01C7` reaches `FUN_004B5F50`. Its fixed source region holds
30 rows of `0x50` bytes, followed by the returned count at `+0x960` and total
count at `+0x964`. This establishes a minimum application extent of `0x968`,
not an observed packet size. The consumer copies rows into operation `+0x98`
and sets operation state 10. No count clamp is visible in this function.

`FUN_004BD170` then writes `Result_Maker` properties `name`, `purposeInt`,
`placeInt`, `socialInt`, `skillInt`, `currentInt`, `demandInt` and `tableInt`.
It uses -1 for the displayed count when total exceeds returned count, publishes
an Update action and sets `Button_Operate` signal 4. The
[Lua boundary](https://github.com/XIVLegacy/xivl-client-scripts/blob/main/docs/search-recruitment-native-boundaries.md)
documents the resulting property-change and rendering path.

For acceptance, serverbound `0x01C6` copies selected cached-row key dwords
at offsets `+0x00`, `+0x04`, `+0x08`, `+0x10` and `+0x14`. Its application
`+0x0C` has no established write. Clientbound `0x01C6` reaches
`FUN_004C9D60`, which clears the eight-byte answer cache, stores the first
application byte and sets state 12. Zero emits text `0x0B8D`. The widget
consumer branches on answer value 1. Other nonzero values and the full
application extent remain unresolved.

The native retail client therefore has an actual recruitment-list and
acceptance-answer route on `0x01C7` and `0x01C6`. Server-side recruitment
rules and a live successful acceptance are outside this static contract.
