# Work binder, player work layout and player, group, area, chara and debug native contracts

[`manifests/work_binder_native_call_contract.json`](../manifests/work_binder_native_call_contract.json)
records how the retail client binds an actor work table to Lua, the work layout
that a `MyPlayer` declares while it initializes, and the static Lua call
contracts of fifteen native registrations that carry twelve Lua names, plus the
shadowed `_turnDir` registration at order 60 that no script reaches. The twelve
names are the natives. Two further Lua names are script helpers over the work
binder (`_bindWork` and `_bindWorkNestingArray`) and are not counted among them.
The twelve names are `_setTouchAttribute`, `_isTouching`, `_updateWork` in four classes, `_lockLockonControl`, `_unlockLockonControl`,
`_getGMRank`, `_getOrientation`, `_getMemberLocalizedDisplayName`,
`_getOccupancyGroup`, `_getRegion`, `_getInstanceName` and `_turnDir`. Each row
gives the registration site, the receiver type check, the declared argument and
return lists, the reads, the effects on client state, the failure behavior and
whether the call yields. The contracts describe client marshalling and state,
not work member values, touch states, region ids or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `MEASURED` is counted or parsed by the method named in
the fact, from the executable or from the Lua 5.1 bytecode of the installed
client scripts. `INFERRED` is a name or role taken from the surrounding
instructions that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
The listings, the caller scan and the reproduction route are the ones of the
[binding map contracts](binding-map-native-contract.md#binary-and-method).
`V`, `W`, `X`, `Y` and `R` name the world object chain of the
[fade contracts](fade-actor-group-native-contract.md#fade-natives). The new
fields of that chain are listed in the manifest `framework.worldObject`.

The script facts come from the Lua 5.1 bytecode of the installed client
scripts, decoded with [`tools/decode_lpb.py`](../tools/decode_lpb.py). The
declaration lists of the work layout were produced by running the declaration
functions on a small bytecode interpreter that replaces the native work members
with recorders. The interpreter shows what the scripts declare. It shows nothing
about the client behavior around the declarations. The script sources are not
redistributed. The member names, types and counts below are metadata of those
scripts. The tracked metadata of `xivl-client-scripts:lua/registry.json` and
`lua/napi_index.json` holds names and line numbers only.

## Work binder

`xivl-decomp:docs/script/widget-work-members.md` records the work userdata. A script reads `self.charaWork` or
`self.playerWork` and the instance `__index` creates a userdata for the work
object on first use. The members exist only after a script assigns a
declaration list to `_save`, `_temp` or `_sync`, or to `_nesting` on a nested
member. This section adds the `_bind` key, the bind route of a write, the member
widths and the behavior of an object without storage.

### Script helpers

`_bindWork` and `_bindWorkNestingArray` are not natives. `actorbaseclass_u`
assigns the descriptors `_bindWork_inl` and `_bindWorkNestingArray_inl`, which
return the selector `self` and the keys `_bindWork_lua` and
`_bindWorkNestingArray_lua` (`MEASURED`). Those keys name Lua functions of the
embedded `/prog/ActorBaseClass` chunk, which
`xivl-decomp:docs/script/lua-bootstrap-chunks.md`
records as follows.

| Call | Effect |
| --- | --- |
| `self:_bindWork(value, workName, key, ...)` | Sets `w = self[workName]` and `w._bind = true`. Walks `w` by `key` and by every trailing key except the last, assigns `value` under the last key, or under `key` when there are no trailing keys, and sets `w._bind = false`. |
| `self:_bindWorkNestingArray(a, workName, member, key, b)` | Sets `w._bind = true`, assigns the list `{a, b}` to `w[member][1][key]` and sets `w._bind = false`. |

The corpus uses `_bindWorkNestingArray` once, in `group/communitygroup/companygroup`.
Every `_bindWork` call of the player chain is in the [bind id table](#bind-ids).

### The write path

The `__newindex` function of a work userdata is `0x00D2F000`. It calls
`0x00D175B0`, which first looks the key up as a declared member through
`0x00D16CD0` (`0x00D17673`). A hit calls the write routine `0x00D272D0` with the
member descriptor as receiver (`0x00D176B2`). A miss compares the key with six
literals in order and stores nothing for the last.

| Key | Literal | Handler | Call site |
| --- | --- | --- | --- |
| `_save` | `0x0110F234` | `0x00D163A0` | `0x00D176E1` |
| `_temp` | `0x0110F240` | `0x00D16610` | `0x00D17707` |
| `_sync` | `0x0110F24C` | `0x00D16840` | `0x00D1772D` |
| `_tag` | `0x0110F258` | `0x00D26B10` and `0x00D26EA0` | `0x00D1779B` |
| `_bind` | `0x0110F264` | `0x00D12200` | `0x00D17859` |
| `_debug` | `0x0110F270` | none | `0x00D17869` |

The pool kind bytes are `0x0130D422` (temp, the value 1 in the file) and
`0x0130D423` (sync, the value 2). The save kind byte `0x01377FB9` is in
uninitialized data, and no instruction of the image stores to it by absolute
address, so it reads 0. The kinds are save 0, temp 1 and sync 2. The code only
reads it, and passes its address as a kind pointer argument. The lookup order of
the pools is temp, save, sync. The dwords at `0x0130D788`, `0x0130D78C`,
`0x0130D798` and `0x0130D79C` hold -1 and are the "no value" sentinels of the
index cells and of the bind record word below.

### The bind route

The `_bind` branch pushes stack index 3 and converts it with `0x00CF35E0`. It
calls `0x00D12200` with the pointer from the second closure upvalue
(`0x00D20490`). That pointer addresses a dword that holds the storage object of
the instance record. `0x00D12200` stores the converted byte at `+0x48` of the
storage object and `0x00D12210` reads it back. The flag is therefore shared by
every work member of one instance.

The write routine `0x00D272D0` starts with `cmp dword ptr [ebx],0` on the same
pointer. A zero dword ends the call with no store. Otherwise it reads the flag
through `0x00D12210` (`0x00D27308`). Its first argument is the key record, which
is the work object `+0x04` (`0x00D176AE`). Byte `+0x2C` of the key record is the
pool kind that `0x00D16CD0` stored for the matched member (`0x00D16CF0`,
`0x00D16D20`, `0x00D16D30`), and byte `+0x14` is a class level index (see
[bind records](#bind-records)).

| Flag | Route |
| --- | --- |
| Clear | Descriptor slot `0x6C` at `0x00D27353` converts the Lua value on the stack top and writes it into the pool of the member (see [value coercion](#value-coercion)). When the key record kind byte at `+0x2C` equals the byte at `0x01377FB9` (save, 0) and slot `0x6C` answered true, descriptor slot `0x04` (`0x00D27400` for every type, a jump to `0x00CE4250`) then runs as a change notification. |
| Set | Descriptor slot `0x64` at `0x00D27337` receives the key record, the pointer, three index cells and the sentinel `0x0130D788`. No value is stored. |

Slot `0x6C` is therefore the store of the Clear route for every pool kind, and
the save kind test gates only the notification of slot `0x04` (`STATIC`). The
slot `0x6C` bodies pass the key record `+0x2C` kind byte, the key record `+0x14`
level byte, the member start and the converted value to the shared record
(`0x00D11BC0` to `0x00CE4450` for a boolean, `0x00D11C30` and its siblings for
the integer widths), and the shared record writes through the pool object found
by kind. `0x00CE4250` dispatches through the engine object at engine `+0x218`
(vtable `+0x08`) and then, when the storage dword at `+0x14` is set, through
`0x00D1A900`. That this is the save change notification to the script engine is
`INFERRED`. When the key record dword `+0x00` is nonzero it is an object
pointer, and the notification instead calls virtual slot `+0x04` of that object
with the sentinel
`0x0130D78C` and the key record dword `+0x28` (`0x00D273A6..0x00D273D3`).

Slot `0x64` is `0x00D27480` for every member type except `timer`, whose slot is
`0x00D25C50` (`ret 0x1C`). The routine tests whether stack index -1 is a table
(`0x00CF3740`). A table supplies two ints from its elements 1 and 2. Any other
value supplies one int and the second int is -1. The three index cells reduce to
one element index: -1 when the first cell holds -1, the first cell when the
third holds -1, and otherwise `third + first * second` (`0x00D274F3..0x00D27519`).
A `_bindWork` write passes the sentinel cells, so its element index is -1. The
routine converts the element index through `0x00D25900`, which returns the
member start (descriptor `+0x08`, in bits) plus the element index times the
member width in bits when the index is not negative. It takes the member width
from slot `0x0C` divided by 8 and calls `0x00D12220`, which jumps to
`0x00CE67F0`, with the first int as its first argument.

`0x00CE67F0` takes seven arguments: the id, a pointer to the kind byte
(key record `+0x2C`), a pointer to the level byte (key record `+0x14`), a
pointer to the member start in bits, the second int, a pointer to the word
source and the span in bytes. It looks the id up in the hash table at
`0x01377F20` through `0x00CE6E30`, which hashes the key as the key xor
`0xDEADBEEF`. An existing entry whose dword at `+0x10` equals the new start ends
the call. An id with no entry is stored in that table
(`0x00CE6A6B..0x00CE6A7B`) as a 12 byte [bind record](#bind-records). An id
whose entry holds a different start leaves that entry untouched. The routine
instead looks up or creates an entry in the table at `0x01377F48` through
`0x006D1170`, keyed by the receiver dword that the routine takes in `ecx`, and
inserts the same record into the hash table that this entry holds at `+0x0C`
(`0x00CE68CE..0x00CE6A0B`). `0x00CE5040` looks a key up through that second table
and the hash table that its entry holds at `+0x0C`, and otherwise in the table
at `0x01377F20`. Eight accessors call it: `0x00CE5290`, `0x00CE53D0`,
`0x00CE5490`, `0x00CE5540`, `0x00CE5600`, `0x00CE56E0`, `0x00CE57D0` and
`0x00CE58B0`. Seven engine wrappers at `0x00CC7B90`, `0x00CC7BE0`, `0x00CC7C30`,
`0x00CC7CD0`, `0x00CC7DE0`, `0x00CC8580` and `0x00CC85C0` call six of them.

`0x00D12220` has one caller, the body of slot `0x64`, so every record of both
tables comes from a `_bindWork` style write.

So the first bind of an id is a global default, and a bind of the same id to a
different start is a per-receiver override that the reader prefers (`STATIC`
from the lookup order of `0x00CE5040`). The override is keyed on the start
alone: a second bind of the same id to the same start in another pool or class
level leaves the first record (`STATIC`, `0x00CE6873..0x00CE687F`). That the
receiver key is the work storage object of one actor, so that layouts with
different nesting sizes under the same ids coexist per instance, is `INFERRED`.
The producer of the key at the callers of the wrappers was not traced. The
callers of the wrappers and the packets that use bind ids were not traced.

### Bind records

A bind record is 12 bytes, copied as three dwords at `0x00CE6A80..0x00CE6A94`
(global table) and `0x00CE6A07..0x00CE6A1B` (receiver table) from a frame
record. The bytes at `+0x02` and `+0x03` are not written by the routine and hold
stack contents.

| Offset | Size | Field | Source |
| ---: | ---: | --- | --- |
| `+0x00` | 1 | pool kind | key record `+0x2C`: 0 save, 1 temp, 2 sync |
| `+0x01` | 1 | class level | key record `+0x14` |
| `+0x04` | 4 | member start in bits | descriptor `+0x08` plus the element index times the width, see below |
| `+0x08` | 2 | word | `0xFFFF` whenever the source cell equals the sentinel `0x0130D788`, which the bind route always passes |
| `+0x0A` | 1 | second int | the second int, `0xFF` when negative |
| `+0x0B` | 1 | span | member width in bits divided by 8, so 0 for a boolean |

`0x00CE5290` shows how a record is read. It takes the receiver, the id and two
indexes. It starts from the dword at record `+0x04`. When the signed word at
`+0x08` is not negative it adds the byte at `+0x0B` times the first index times
8. When the second index is above 0 it adds the byte at `+0x0A` times the second
index times 8. A switch on the span byte (1 to 4) then reads 1, 2, 3 or 4 bytes
through `0x00D11C70`, `0x00D11CF0`, `0x00D11DB0` and the 32 bit sibling, passing
the kind byte, the level byte and the bit position as pointers (`0x00CE533E`,
`0x00CE5356`, `0x00CE536E`, `0x00CE5383`). A missing record answers -1. The word
at `+0x08` is -1 for every record, so the first index never applies and the
only element stride a record can carry is the second int, in bytes. All 26
`_bindWork` calls of the MyPlayer chain pass one int, so their second int byte is
`0xFF`. The role of the second index and the engine callers are `INFERRED` or
untraced.

The address of a member is therefore a pool base plus the bit start. The shared
record keeps a vector of vectors at `+0x2C`, one per kind. `0x00CE5BF0`, called
when a list is declared, resizes the vector of the kind to the level plus 2
entries, sets the entry of level plus 1 to the declared byte size plus the sum
of all entries of the vector, and passes the size to the pool object through
pool slot 1 (`0x00CCB3F0`). The base of a level is its entry in that vector, and
the reader adds the byte part of the bit start to it (`0x00CE4550..0x00CE45B0`).
The bases of levels 0 to 2 are the plain prefix sums of the declared sizes. From
level 3 each entry also adds the earlier entries again, because the loop at
`0x00CE5C60..0x00CE5C67` sums every entry of the vector.

### Member offsets

`0x00D1E0F0` lays out one declaration list. It keeps a running offset in bits
and visits the entries in list order. It builds the descriptor of an entry with
the running offset as its start. Every descriptor class except `boolean` rounds
that start up to a multiple of 8 bits with `0x00D1F4F0` in its constructor and
stores it at descriptor `+0x08`. The calls precede the vftable stores at
`0x00D28BF9`, `0x00D29099`, `0x00D295B9`, `0x00D299E9`, `0x00D29F29`,
`0x00D2A3FD`, `0x00D2AD59`, `0x00D2B57D`, `0x00D2B6A9`, `0x00D23D52` and
`0x00D23DE6` (integer8 to uinteger64, string, actor, timer and the
`nesting` and `reserve` constructors). The boolean constructor `0x00D28390`
stores it unrounded. After the descriptor exists the
routine adds the width of slot `0x0C` to the running offset and, when that width
is a multiple of 8, rounds the running offset up to a byte first
(`0x00D1E59F..0x00D1E5CD`). So booleans pack to one bit each in declaration
order, every other member starts on the next byte boundary, and a member's start
is the declaration-order bit sum with that rounding (`STATIC`). The result
record holds the total bits at `+0x00`, the start of an `_assignForChild` entry
at `+0x04` and its width at `+0x08` (`0x00D1E616..0x00D1E632`).

The offset added to the running offset is an origin pointer that the caller
passes. The nested list call at `0x00D1CA4A` passes the nested record `+0x40`,
which the nested record constructor `0x00D1C100` fills from its third argument
pointer (`0x00D1C151`). The reader adds nothing but the record start to the level
base, so a nested member's recorded start must already include the start of its
nesting member. That the origin is the start of the nesting member is therefore
`INFERRED`. The top level call at `0x00D166FF` starts its origin at 0 and
replaces it with eight times the sizes that `0x00D125F0` returns when the work
object already has a declaration in that pool (`0x00D166A9..0x00D166DE`, not
traced further).

The array count rule is not settled. A numeric third operand does not reach the
scalar creators (`0x00D25640` and siblings read one argument, the start), and
`0x00D1E0F0` adds one width per entry. The count rule is `INFERRED` from the
capacities: `eventTemp` holds `linkshellIcon` as integer16 x 4 and three
booleans, which is 67 bits and an operand of 9 bytes, and `eventSave` holds a
boolean and two integer8 members, which is 24 bits with byte alignment and an
operand of 3 bytes.

### Value coercion

The slot `0x6C` bodies read the Lua stack top as the C API does. A boolean uses
`0x00CF35E0`, which wraps `lua_toboolean` (`0x00DCDF50`, false for nil and for
`false`). An integer width and a float use `0x00CF35C0`, which wraps
`lua_tonumber` (`0x00DCDED0`): a number is used as is, a string goes through the
string to number conversion `0x00DDE8B0` and `0x00DDE360`, and a value that is
neither converts to 0.0 (`0x00DCDEF7`). An integer width then truncates toward
zero with the CRT routine at `0x009D6636` (`fistp` with the correction for
rounding) and stores the low 8, 16, 24 or 32 bits at the member start. A float
stores the converted number. A string member reads the value through
`0x00CF3600`. A numeric string written to an integer member therefore stores its
number, and a non numeric string stores 0 (`STATIC` for the call chain). The exact
low bit masks follow the width of the store routines `0x00D11C30`, `0x00D11CB0`,
`0x00D11D60` and `0x00D11E10`, whose bodies were not read byte by byte).

### Initial values

The Lua layer holds no member values. A reader of the integer, float and boolean
descriptors (`0x00D28890`, `0x00D28D10`, `0x00D291B0`, `0x00D29660`,
`0x00D29B00`, `0x00D29FD0`) returns the pool bytes at the member start through
the shared record and the pool object of the member's kind. Nothing in the
reader substitutes a default: a member of an object with storage reads whatever
the pool holds, and nil appears only for an object without storage (see below).
A boolean answers the pushed bool of the bit, an integer width answers the sign
extended value of its bytes (`0x00CE5290..0x00CE539B`), so a pool that is zero
filled reads 0 and false. The pool objects are reached through a vector at
container `+0x0C` indexed by kind (`0x00CCB3F0` resizes with pool slot 1,
`0x00CCB430` reads with slot 2, `0x00CCB480` and `0x00CCB510` write through slots
3 and 5, `0x00CCB4D0` reads a bit through slot 4). Their class, their
allocation and whether a resize zero fills were not found: a scan of the image
vftables for the slot return signatures (slot 1 `ret 4`, slot 2 `ret 0xC`,
slot 3 `ret 0x10`) found no class whose slot 1 calls the allocator `0x009D1B35`
or holds a `rep stos`. So the
value of a member before the first write is open. The sizes that the pools are
resized to are known: a top level list registers its laid out bytes
(`0x00D16706..0x00D1672B`) and the shared record sums the levels (see
[bind records](#bind-records)).

### An object without storage

The reader at slot `0x1C` of the boolean, integer8, integer16, integer24,
integer32, float and uinteger64 descriptors begins with `cmp dword ptr [edi],0` on
the dword that its second argument addresses and pushes nil through
`0x00CF33A0` when it is zero (`0x00D28895`, `0x00D29B08`). `0x00D16D40` passes the
pointer from the second closure upvalue as that argument. A declared member of an
object with no installed storage therefore reads nil, and a write to it is
dropped by the zero test of the write routine. The string, actor and timer
readers were not compared.

### Member widths

Descriptor slot `0x0C` stores the width of a member in bits. The string width is
the dword at descriptor `+0x10` added to itself three times, so eight times that
dword. The factory `0x00D260D0` maps the type names to the constructors.

| Tag | Descriptor vftable | Width slot target | Bits |
| --- | --- | --- | --- |
| `boolean` | 0x0110FBC4 | 0x00D2DDE0 | 1 |
| `integer8` | 0x0110FC3C | 0x00D2DE10 | 8 |
| `integer16` | 0x0110FCB4 | 0x00D2DE20 | 16 |
| `integer24` | 0x0110FD2C | 0x00D2DE30 | 24 |
| `integer32` | 0x0110FDA4 | 0x00D2DE40 | 32 |
| `float` | 0x0110FE1C | 0x00D2DE40 | 32 |
| `string` | 0x0110FE94 | 0x00D25960 | operand * 8 |
| `actor` | 0x0110FF0C | 0x00D2DE40 | 32 |
| `timer` | 0x0110FF84 | 0x00D2DE90 | 40 |
| `uinteger64` | 0x0110FFFC | 0x00D2DEA0 | 64 |

The shared record keeps a per-pool vector of layout offsets and no member
values. `0x00CE4550` forwards a read to `0x00CCB430`, which indexes a vector at
`+0x0C` of its receiver by the pool kind byte and calls virtual slot 2 of the pool
object found there. `0x00CE48C0` forwards a write by pool kind to the virtual slot
at `+0x28` (save), `+0x2C` (temp) or `+0x30` (sync) of the object at receiver
`+0x08`. The work userdata holds no member values.

### Nested capacity

A `nesting` entry carries a number. The width slot of the `nesting` and `reserve`
descriptors (vftable `0x0110F8F4` and its derived `0x0110F974`) is `0x00D25960`,
the string slot, which returns eight times the dword at descriptor `+0x10`. That
dword is the operand (`0x00D23D58`, `0x00D23DEC`), so the operand is a byte
capacity (`STATIC`) and the nested member occupies operand times 8 bits of the
list that declares it. The nested members of `charaWork` give the following
figures for the local player, where the sums apply the [member offsets](#member-offsets)
rule: booleans one bit, other members byte aligned, arrays counted at count times
the element width (`INFERRED`).

| Nested member | Operand | Laid out bits | Rounded up, bytes |
| --- | ---: | ---: | ---: |
| `parameterSave` | 512 | 2056 | 257 |
| `parameterTemp` | 256 | 880 | 110 |
| `battleSave` | 512 | 3410 | 427 |
| `battleTemp` | 128 | 632 | 79 |
| `eventSave` | 3 | 24 | 3 |
| `eventTemp` | 9 | 67 | 9 |

`eventSave` and `eventTemp` fill their operand exactly. For a receiver that is
not the local player the operands are 64 and 16 for `parameterSave` and
`parameterTemp`, which lay out to 336 and 48 bits, so the operand cannot be a bit
count. No operand is smaller than its laid out size. With the capacities as
widths the `_sync` list of `charaWork` lays out to 18800 bits (2350 bytes) for the
local player and 8816 bits (1102 bytes) for another player, and the `_sync` list
of `playerWork` to 6952 bits (869 bytes). The `_temp` list of `playerWork` lays
out to 4648 bits (581 bytes).

### Derived bind starts

The starts below apply the [member offsets](#member-offsets) rule and the
nested origin rule to the declared lists, with the tier `INFERRED` because the
array count rule and the nested origin are. A nested member's start includes the
start of its nesting member. Another player binds only the ids 1010 to 1012,
3006, 4001, 4002 and 2002, so the other columns stay empty. The ids after a
nested member move for another player because the nested operands are smaller.

| Id | Member | Start, local player | Start, other player |
| ---: | --- | ---: | ---: |
| 1010 | `charaWork.parameterSave.hp` | 776 | 776 |
| 1011 | `charaWork.parameterSave.hpMax` | 904 | 904 |
| 1012 | `charaWork.parameterSave.state_mainSkillLevel` | 1096 | 1096 |
| 1001 | `charaWork.parameterSave.state_mainSkill` | 1064 | |
| 1003 | `charaWork.parameterSave.giftCommandSlot_commandId` | 2464 | |
| 1002 | `charaWork.parameterSave.constanceCommandSlot_commandId` | 2624 | |
| 1004 | `charaWork.parameterSave.abilityCostPoint_used` | 2784 | |
| 1005 | `charaWork.parameterSave.abilityCostPoint_max` | 2792 | |
| 1008 | `charaWork.parameterSave.giftCostPoint_used` | 2800 | |
| 1009 | `charaWork.parameterSave.giftCostPoint_max` | 2808 | |
| 1006 | `charaWork.parameterSave.constanceCostPoint_used` | 2816 | |
| 1007 | `charaWork.parameterSave.constanceCostPoint_max` | 2824 | |
| 3006 | `charaWork.property` | 0 | 0 |
| 4001 | `charaWork.eventTemp.bazaarRetail` | 7008 | 1504 |
| 4002 | `charaWork.eventTemp.bazaarRepair` | 7009 | 1505 |
| 3001 | `charaWork.commandAcquired` | 7016 | |
| 3002 | `charaWork.command` | 11112 | |
| 3003 | `charaWork.commandCategory` | 13160 | |
| 3004 | `charaWork.commandBorder` | 13672 | |
| 2001 | `charaWork.battleSave.skillLevel` | 13760 | |
| 2002 | `charaWork.battleSave.potencial` | | 8176 |
| 100004 | `playerWork.variableCommandPlaceDriven` | 0 | |
| 100007 | `playerWork.initialTown` | 32 | |
| 100003 | `playerWork.variableCommandContent` | 352 | |
| 100005 | `playerWork.variableCommandEmoteSit` | 416 | |
| 100002 | `playerWork.variableCommandConfirmWarp` | 4904 | |
| 100001 | `playerWork.variableCommandConfirmRaise` | 5264 | |

That the same id gets a different start for the local player and for another
player is what the per receiver table is for. This supports, and does not prove,
that the receiver key is one actor's storage.

## Declared work of a MyPlayer

`PlayerBaseClass._onInit` calls `_callSuperClassFunc('_onInit', true, true)`.
`CharaBaseClass._onInit` therefore runs first with both flags set. The first
flag declares the sync layouts through `initCommonParameterSync`. The second
declares the battle layouts. `isMyPlayer` is
`worldMaster:_getMyPlayer() == self`, `CharaBaseClass.isPlayer` returns nil and
`PlayerBaseClass.isPlayer` returns true. `CharaBaseClass._onInit` sizes the
nested members by `isPlayer() and isMyPlayer()`. When both hold,
`parameterSave`, `parameterTemp`, `battleSave` and `battleTemp` get 512, 256, 512
and 128 bytes. Otherwise they get 64, 16, 64 and 16 bytes. A client that makes
`_getMyPlayer` return a different object than the receiver gets the second set of
declarations and none of the `MyPlayer` calls below (`MEASURED`).

All of the following is `MEASURED`. The order of the events for a `MyPlayer` is:

| Step | Event |
| ---: | --- |
| 1 | `charaWork._save` receives an empty list and `_temp` receives `gameParameter`. |
| 2 | `charaWork._sync` receives the 15 members listed below. |
| 3 | The six nested members of `charaWork` receive `_nesting` lists. |
| 4 | `charaWork._tag` receives 19 groups and `charaWork.gameParameter` is set to true. |
| 5 | `_setNameplate(1, nil, 10101)` and `_setNameplateVisible(false)`. |
| 6 | Six `_bindWork` calls of `CharaBaseClass`. |
| 7 | `playerWork._save`, `_temp`, `_sync` and `_tag` receive their lists. |
| 8 | Six `_setTouchAttribute` calls: (1, true), (1, false), (2, true), (2, false), (5, true) and (5, false). |
| 9 | Twenty `_bindWork` calls of `PlayerBaseClass`. |

`CharaBaseClass.hasGameParameter` returns `charaWork.gameParameter`, which step 4
sets.

### charaWork

`charaWork._save` is empty and `charaWork._temp` holds `gameParameter` (boolean).
`charaWork._sync` holds the following members.

| Member | Type |
| --- | --- |
| `property` | boolean x 32 |
| `additionalCommandAcquired` | boolean x 36 |
| `currentContentGroup` | integer32 |
| `depictionJudge` | actor |
| `statusShownTime` | integer32 x 20 |
| `parameterSave` | nesting, 512 bytes |
| `parameterTemp` | nesting, 256 bytes |
| `eventSave` | nesting, 3 bytes |
| `eventTemp` | nesting, 9 bytes |
| `commandAcquired` | boolean x 4096 |
| `command` | actor x 64 |
| `commandCategory` | integer8 x 64 |
| `commandBorder` | integer8 |
| `battleSave` | nesting, 512 bytes |
| `battleTemp` | nesting, 128 bytes |

The nested lists are the following. `parameterSave` and `parameterTemp` come from
`initCommonParameterSync`. The others come from `CharaBaseClass._onInit` and
`initBattleSync`.

| Nested member | Member | Type |
| --- | --- | --- |
| `parameterSave` | `hp` | integer16 x 8 |
|  | `hpMax` | integer16 x 8 |
|  | `mp` | integer16 |
|  | `mpMax` | integer16 |
|  | `state_mainSkill` | integer8 x 4 |
|  | `state_mainSkillLevel` | integer16 |
|  | `state_boostPointForSkill` | integer8 x 4 |
|  | `commandSlot_recastTime` | integer32 x 40 |
|  | `commandSlot_compatibility` | boolean x 40 |
|  | `giftCommandSlot_commandId` | integer16 x 10 |
|  | `constanceCommandSlot_commandId` | integer16 x 10 |
|  | `abilityCostPoint_used` | integer8 |
|  | `abilityCostPoint_max` | integer8 |
|  | `giftCostPoint_used` | integer8 |
|  | `giftCostPoint_max` | integer8 |
|  | `constanceCostPoint_used` | integer8 |
|  | `constanceCostPoint_max` | integer8 |
| `parameterTemp` | `tp` | integer16 |
|  | `targetInformation` | integer32 |
|  | `maxCommandRecastTime` | integer16 x 40 |
|  | `forceControl_float_forClientSelf` | float x 4 |
|  | `forceControl_int16_forClientSelf` | integer16 x 2 |
|  | `otherClassAbilityCount` | integer8 x 2 |
|  | `giftCount` | integer8 x 2 |
| `battleSave` | `potencial` | float |
|  | `physicalLevel` | integer16 |
|  | `physicalExp` | integer32 |
|  | `skillLevel` | integer16 x 52 |
|  | `skillLevelCap` | integer16 x 52 |
|  | `skillPoint` | integer32 x 52 |
|  | `negotiationFlag` | boolean x 2 |
| `battleTemp` | `castGauge_speed` | float x 2 |
|  | `timingCommandFlag` | boolean x 4 |
|  | `generalParameter` | integer16 x 35 |
| `eventSave` | `bazaar` | boolean |
|  | `bazaarTax` | integer8 |
|  | `repairType` | integer8 |
| `eventTemp` | `linkshellIcon` | integer16 x 4 |
|  | `bazaarRetail` | boolean |
|  | `bazaarRepair` | boolean |
|  | `bazaarMateria` | boolean |

### playerWork

`playerWork._save` holds one reserve entry of 16 bytes (`_assignForChild`).
`playerWork._temp` holds these members.

| Member | Type |
| --- | --- |
| `variableCommandPlaceDriven` | integer16 x 4 |
| `variableCommandPlaceDrivenSub` | integer32 x 4 |
| `variableCommandPlaceDrivenTarget` | actor x 4 |
| `variableCommandPlaceDrivenPriority` | integer8 x 4 |
| `variableCommandContent` | integer32 |
| `variableCommandContentSub` | integer32 |
| `variableCommandEmoteSit` | integer32 |
| `commandBurstBlocker` | timer, false |
| `requestBurstBlocker` | integer32 |
| `widgetCommandBurstBlocker` | integer32 |
| `_assignForChild` | reserve, 512 bytes |

`playerWork._sync` holds these members. A player that is not the local player
declares only the final reserve entry, with 128 bytes.

| Member | Type |
| --- | --- |
| `tribe` | integer8 |
| `guardian` | integer8 |
| `birthdayMonth` | integer8 |
| `birthdayDay` | integer8 |
| `initialTown` | integer8 |
| `questScenario` | actor x 16 |
| `questScenarioComplete` | boolean x 2048 |
| `questGuildleve` | actor x 8 |
| `questGuildleveComplete` | boolean x 2048 |
| `variableCommandConfirmWarp` | integer32 |
| `variableCommandConfirmWarpSender` | string, 32 bytes |
| `variableCommandConfirmWarpSenderByID` | integer32 |
| `variableCommandConfirmWarpSenderSex` | integer8 |
| `variableCommandConfirmWarpPlace` | integer32 |
| `variableCommandConfirmRaise` | integer32 |
| `variableCommandConfirmRaiseSender` | string, 32 bytes |
| `variableCommandConfirmRaiseSenderByID` | integer32 |
| `variableCommandConfirmRaiseSenderSex` | integer8 |
| `npcLinkshellChatCalling` | boolean x 64 |
| `npcLinkshellChatExtra` | boolean x 64 |
| `isContentsCommand` | boolean |
| `castEndClient` | integer32 |
| `castCommandClient` | integer32 |
| `comboNextCommandId` | integer32 x 2 |
| `comboCostBonusRate` | float |
| `isRemainBonusPoint` | boolean |
| `restBonusExpRate` | float |
| `_assignForChild` | reserve, 128 bytes |

### Tag groups

`_tag` takes a list of groups. A group is a name, an optional interval in
seconds, an optional receiver for groups that apply to the player itself, and a
list of member paths. The names and intervals are `MEASURED`. What the client
does with a group was not traced.

| charaWork group | Interval | Applies to | Members |
| --- | --- | --- | --- |
| `stateAtQuicklyForAll` | 0.3 |  | 5 |
| `stateForAll` | 1.5 |  | 3 |
| `potencial` | 1 |  | 1 |
| `exp` |  |  | 2 |
| `bazaar` | 1 |  | 6 |
| `linkshellIcon` | 1 |  | 1 |
| `stateAtQuicklyForSelf` | 1 | self | 1 |
| `commandDetailForSelf` | 1 | self | 5 |
| `commandEquip` | 1 | self | 3 |
| `battleStateForSelf` | 1 | self | 4 |
| `timingCommand` | 1 | self | 1 |
| `battleParameter` | 1 | self | 28 |
| `command` | 1 | self | 3 |
| `commandAcquired` |  |  | 1 |
| `additionalCommand` | 1 | self | 1 |
| `currentContentGroup` | 1 | self | 1 |
| `judge` | 1 | self | 1 |
| `status` | 1 |  | 1 |
| `property` | 1 |  | 1 |

| playerWork group | Interval | Applies to | Members |
| --- | --- | --- | --- |
| `profile` | 60 | self | 5 |
| `confirmWarpCommand` | 1 | self | 5 |
| `confirmRaiseCommand` | 1 | self | 4 |
| `journal` | 1 | self | 2 |
| `npcLinkshellChat` | 1 | self | 2 |
| `questCompleteS` |  |  | 1 |
| `questCompleteG` |  |  | 1 |
| `isContentsCommand` | 1 | self | 1 |
| `combo` | 1 | self | 2 |
| `consoleTray` | 1 | self | 1 |
| `expBonus` | 1 | self | 1 |
| `castState` | 1 | self | 2 |

The members of the `battleParameter` group are `battleTemp.generalParameter`
elements 4 to 19 and 24 to 35 (element 14 precedes 13 in the declaration). The
other groups list their members in the manifest.

### Bind ids

The bind calls of a `MyPlayer` are the following. Each call is
`self:_bindWork(id, work, key, ...)`.

| Id | Member | Declared by |
| --- | --- | --- |
| 1010 | `charaWork.parameterSave.hp` | `CharaBaseClass._onInit` |
| 1011 | `charaWork.parameterSave.hpMax` | `CharaBaseClass._onInit` |
| 1012 | `charaWork.parameterSave.state_mainSkillLevel` | `CharaBaseClass._onInit` |
| 4001 | `charaWork.eventTemp.bazaarRetail` | `CharaBaseClass._onInit` |
| 4002 | `charaWork.eventTemp.bazaarRepair` | `CharaBaseClass._onInit` |
| 3006 | `charaWork.property` | `CharaBaseClass._onInit` |
| 1001 | `charaWork.parameterSave.state_mainSkill` | `PlayerBaseClass._onInit` |
| 1002 | `charaWork.parameterSave.constanceCommandSlot_commandId` | `PlayerBaseClass._onInit` |
| 1003 | `charaWork.parameterSave.giftCommandSlot_commandId` | `PlayerBaseClass._onInit` |
| 1004 | `charaWork.parameterSave.abilityCostPoint_used` | `PlayerBaseClass._onInit` |
| 1005 | `charaWork.parameterSave.abilityCostPoint_max` | `PlayerBaseClass._onInit` |
| 1006 | `charaWork.parameterSave.constanceCostPoint_used` | `PlayerBaseClass._onInit` |
| 1007 | `charaWork.parameterSave.constanceCostPoint_max` | `PlayerBaseClass._onInit` |
| 1008 | `charaWork.parameterSave.giftCostPoint_used` | `PlayerBaseClass._onInit` |
| 1009 | `charaWork.parameterSave.giftCostPoint_max` | `PlayerBaseClass._onInit` |
| 2001 | `charaWork.battleSave.skillLevel` | `PlayerBaseClass._onInit` |
| 3001 | `charaWork.commandAcquired` | `PlayerBaseClass._onInit` |
| 3002 | `charaWork.command` | `PlayerBaseClass._onInit` |
| 3003 | `charaWork.commandCategory` | `PlayerBaseClass._onInit` |
| 3004 | `charaWork.commandBorder` | `PlayerBaseClass._onInit` |
| 100001 | `playerWork.variableCommandConfirmRaise` | `PlayerBaseClass._onInit` |
| 100002 | `playerWork.variableCommandConfirmWarp` | `PlayerBaseClass._onInit` |
| 100003 | `playerWork.variableCommandContent` | `PlayerBaseClass._onInit` |
| 100004 | `playerWork.variableCommandPlaceDriven` | `PlayerBaseClass._onInit` |
| 100005 | `playerWork.variableCommandEmoteSit` | `PlayerBaseClass._onInit` |
| 100007 | `playerWork.initialTown` | `PlayerBaseClass._onInit` |

A player that is not the local player makes seven bind calls, all in
`CharaBaseClass._onInit`: the ids 1010, 1011, 1012, 4001, 4002, 2002 and 3006.
The id 2002 binds `charaWork.battleSave.potencial` and appears only on that path.
It makes none of the `_setTouchAttribute` calls.

### Reading state_mainSkill

`getStateMainSkill` in `chara/charabaseclass_cliprog` returns
`charaWork.parameterSave.state_mainSkill[1]` and `[2]` (`MEASURED`).
`state_mainSkill` is an array of 4 integer8 values in the `parameterSave` list.
`CharaBaseClass.getMainSkillCategory` and `isBattleClass` call it, and
`DesktopWidget.craftCommand` reaches it through `getMainSkillCategory` of
`worldMaster:_getMyPlayer()`, which it compares with the number 29. The widget
chain of `ConsoleIconTrayWidget.init`, `update`, `updateCraftButton` and
`DesktopWidget.isExistCraftCommand` runs the same read.

Both reads return nil in two cases. The first is a receiver on which
`parameterSave` is not declared, which happens when `CharaBaseClass._onInit` did
not run to its `_nesting` assignment. That assignment needs the first argument of
`_onInit` to be true and comes before the nameplate, `_setTouchAttribute` and
`_bindWork` calls, so those calls do not decide whether `parameterSave` is
declared. The second is a
receiver without installed storage, where every declared member reads nil
([an object without storage](#an-object-without-storage)). The array is indexed
from 1 by the scripts. The index base inside the readers was not traced.

## Registration and dispatch

Seven classes register the fifteen rows and the shadowed `_turnDir`, each from the switchboard in slot 2 of its
vftable. The switchboard shape, the skip byte and the single `rel32` caller of
each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `PlayerBase` | `0x00753F90` | `0x00FD5E04` | `_lockLockonControl` (30), `_unlockLockonControl` (31), `_getGMRank` (41), `_setTouchAttribute` (42), `_isTouching` (43) |
| `CharaBase` | `0x007574A0` | `0x00FD5CAC` | `_getOrientation` (5), `_updateWork` (27), `_turnClientDir` (61), and the shadowed `_turnDir` (60), which is not a row |
| `GroupBase` | `0x00757B70` | `0x00FD53CC` | `_getOccupancyGroup` (7), `_getMemberLocalizedDisplayName` (10), `_updateWork` (15) |
| `ItemBase` | `0x00753DD0` | `0x00FD5484` | `_updateWork` (17) |
| `DirectorBase` | `0x00758260` | `0x00FD5D6C` | `_updateWork` (2) |
| `AreaBase` | `0x00753CF0` | `0x00FD63D4` | `_getRegion` (1) |
| `Debug` | `0x00757CE0` | `0x00FD51DC` | `_getInstanceName` (4) |

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_setTouchAttribute` | `0x007338A0` | `0x00754309` | `0x0071E420` | `0x00726720` |
| `_isTouching` | `0x007290E0` | `0x0075431E` | `0x0071E430` | `0x007267D0` |
| `_updateWork` (`CharaBase`) | `0x0073EB40` | `0x007576DE` | `0x006E7670` | `0x00726460` |
| `_updateWork` (`GroupBase`) | `0x0073EF30` | `0x00757CB2` | `0x006E8890` | `0x007265C0` |
| `_updateWork` (`DirectorBase`) | `0x0073FC50` | `0x00758291` | `0x006E85E0` | `0x00726D50` |
| `_updateWork` (`ItemBase`) | `0x00730810` | `0x00753F3C` | `0x006E2AF0` | `0x00726670` |
| `_lockLockonControl` | `0x00732A30` | `0x0075420D` | `0x006DE810` | `0x007267D0` |
| `_unlockLockonControl` | `0x00732B80` | `0x00754222` | `0x006DE820` | `0x007267D0` |
| `_getGMRank` | `0x0074F230` | `0x007542F4` | `0x00706C70` | `0x007267D0` |
| `_getOrientation` | `0x0074A760` | `0x00757510` | `0x006F9B20` | `0x00726460` |
| `_getMemberLocalizedDisplayName` | `0x0074D400` | `0x00757C49` | `0x00700110` | `0x007265C0` |
| `_getOccupancyGroup` | `0x00756B70` | `0x00757C0A` | `0x00709C80` | `0x007265C0` |
| `_getRegion` | `0x00749A40` | `0x00753D0C` | `0x006F96C0` | `0x0072CD40` |
| `_getInstanceName` | `0x007367E0` | `0x00757D3B` | `0x006DC6F0` | `0x00726930` |
| `_turnClientDir` | `0x0072FEE0` | `0x007579A8` | `0x006E47D0` | `0x00726460` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrappers build const holders except `0x00726720`, which builds
the non-const `PlayerBase` holder (vftable `0x00FD601C`). The other holder
vftables, invoke routines and cast targets are in the manifest
`framework.holders`. Each invoke routine casts the receiver with `0x009DA6CC`
from `LuaControl` (`0x01270B4C`) to the class of the holder.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_setTouchAttribute` | `PlayerBase` | `int`, `bool` | none | no |
| `_isTouching` | `PlayerBase` | `int` | `bool` | no |
| `_updateWork` | `CharaBase`, `GroupBase`, `DirectorBase` | two `Utf8String`, two `int` | none | no |
| `_updateWork` | `ItemBase` | none | none | no |
| `_lockLockonControl` | `PlayerBase` | none | none | no |
| `_unlockLockonControl` | `PlayerBase` | none | none | no |
| `_getGMRank` | `PlayerBase` | none | `int` or nil | no |
| `_getOrientation` | `CharaBase` | three `float` | `float` | no |
| `_getMemberLocalizedDisplayName` | `GroupBase` | `int` | `Utf8String` | no |
| `_getOccupancyGroup` | `GroupBase` | none | control or nil | no |
| `_getRegion` | `AreaBase` | none | `int` | no |
| `_getInstanceName` | `Debug` | control | `Utf8String` | no |
| `_turnDir` | `CharaBase` | `float` | none | no |

No callback body here calls the yield request `0x00CD2860`. The readers and
pushers are the ones of the [binding map contracts](binding-map-native-contract.md#contracts)
plus the float reader `0x0071BAC0`, the bool reader `0x0071BA00`, the string
reader `0x0071CE70` and the control reader `0x0071BEB0`, each identified by the
tag compare at its start. The new list builders are `0x0072B390` (one float),
`0x0072B5B0` (one `Utf8String`), `0x0072C260` (one control), `0x0072BDC0` (an int
and a bool) and `0x0073CF80` (two `Utf8String` and two int entries).

## Touch attributes

`_setTouchAttribute` and `_isTouching` are thunks through slots `0x148` and
`0x14C` of the receiver vftable. The `PlayerBase` cells `0x00FD5F4C` and
`0x00FD5F50` hold `0x00776340`, which is `ret 4`, so a `PlayerBase` receiver that
is not a `MyPlayer` does nothing and `_isTouching` pushes no value. The
`MyPlayer` cells `0x00FD79A4` and `0x00FD79A8` hold `0x006E6110` and
`0x00705320`.

`0x006E6110` reads the attribute as an int and keeps its low byte. It reads the
flag as a bool and selects the byte at `0x012D7C43` (the value 1 in the file) for
true or the byte at `0x01355297` (uninitialized data, 0) for false. On first use
it allocates `0x18` bytes at `MyPlayer +0x10C` and constructs two empty ordered
sets of byte keys at `+0x00` and `+0x0C` (`0x00895EF0`, `0x0089AE80`).
`0x00895790` then searches the attribute in both sets (`0x0089A1C0` is an
ordered set `find`). When it is in neither, it calls `0x0075C950`, which reaches
`0x00589720` on the object at `V +0x17838` with the second argument fixed to 1.
The routine finally inserts the attribute into the set at `+0x00` when the flag
byte equals the byte at `0x012D7C43` and into the set at `+0x0C` otherwise. The
insert runs on every call, found or not (`0x00895816..0x0089584F`).

The set bit is `1 << (attribute mod 32)` in a byte. The shift is `shl dl, cl`
(`0x00589728`) in `0x00589720` and `shl edx, cl` (`0x0058975B`) in `0x00589750`,
and the x86 shift count of a byte or dword shift is masked to 5 bits. The byte
holds 8 bits, so the exact behavior for the attribute low byte `a` is:

| `a` | Effect on the byte at `+0x45C` and on the read of `+0x45D` |
| --- | --- |
| 0 to 7 | bit `a` |
| 8 to 31 | none: the shifted value is 0, so the set ORs 0 and the read tests 0 and answers false |
| 32 to 39 | bit `a - 32`, the same bit as `a - 32` |
| 40 to 63 | none |
| 64 to 71, 96 to 103 and so on to 224 to 231 | bit `a mod 32` |
| other values up to 255 | none |

A value of 256 or more is first reduced to its low byte. An attribute whose
remainder modulo 32 is 8 or more changes no bit, and one whose remainder is 0 to
7 aliases bit `a mod 32` (`STATIC`). The clear path of
`0x00589720` (`not dl`, `and`) clears the same bit, but its only caller
`0x0075C950` passes the flag 1, so no path of the image clears the bit. A
`false` flag therefore never clears the bit. It only chooses the set that the
attribute joins, and the bit stays set for the object's life until the object
is reset.

`0x00705320` reads the attribute and calls `0x00894EE0`. For attribute 1 that
routine first calls `0x00763030` on `Y` and answers false when it returns true.
`0x00763030` returns the byte at `+0xBA` of the object in the first node of a list
at `Y +0x1C`, or 0 when the list at `+0x20` is empty. Otherwise `0x00894EE0`
reaches `0x00589750` and answers the bit of the attribute in the byte at
`+0x45D` of the object at `V +0x17838`. It does not read the sets.

The object at `V +0x17838` keeps three touch bytes, all cleared together by the
object's reset (`0x0058BB87..0x0058BB93`). The object is the `CharaElement`
whose async dispatcher is `0x0058E0C0`
(`docs/client-architecture.md`, "Pattern B"):

| Byte | Role | Writers |
| --- | --- | --- |
| `+0x45C` | armed attributes | `0x00589720` through `0x0075C950` (set only) |
| `+0x45D` | attributes currently touched | the async event dispatcher `0x0058E0C0`, opcode `0x60` (`0x0058E622`, stores the byte at the payload pointer) and the reset |
| `+0x45E` | attributes whose touch start was reported | `0x005893F0` |

`0x005893F0` visits bits 0 to 5 only. For a bit armed in `+0x45C` it compares the
other two bytes. When `+0x45D` holds the bit and `+0x45E` does not, it sets the
`+0x45E` bit and calls virtual slot `0x54` (`0x00574D50`) of the object at
`this +0x80`. When `+0x45E` holds the bit and `+0x45D` does not, it clears the
`+0x45E` bit and calls virtual slot `0x58` (`0x00574D60`). Bits 6 and 7 are
armed and read but raise no event. The byte writers `0x00588200`, `0x00588300` and `0x00588330`
have no caller and no vftable reference. None of the 91 direct callers of the
async enqueue `0x007CE7B0` pushes the opcode `0x60` as an immediate in the ten
instructions before the call, so the producer of the touch byte is untraced. The roles of `+0x45C` (armed), `+0x45D` (touching)
and `+0x45E` (reported) are `INFERRED` from the begin and end edge code. The
scripts pass the attribute numbers 1, 2 and 5 only. Their meaning is untraced.

## Work refresh

`_updateWork` has four registrations. The three that take arguments declare the
list `Utf8String`, `Utf8String`, `int`, `int`. The callback reads the two strings
as a work name and a member name and builds a request through `0x0070AA10`. When
the tag byte of the third cell is not 6 (nil) it reads the two ints, subtracts 1
from each, keeps 16 bits of each and adds the range through `0x0070AAA0` and
`0x006CE1C0`. The scripts pass one based element numbers, as in
`('charaWork', 'commandAcquired', first - 26000, last - 26000)`.

| Class | Hand off |
| --- | --- |
| `CharaBase` (`0x006E7670`) | Resolves `Y`, loads the object at `Y +0xEC` and calls `0x00767FC0` with `ExecuteParameters +0x04`, the receiver identity and the request. |
| `DirectorBase` (`0x006E85E0`) | The same call as `CharaBase`. |
| `GroupBase` (`0x006E8890`) | Calls `0x006C7A80` with the group data at receiver `+0x68`. That routine calls `0x006C72E0` on the object at `+0xA0` of the group data's first field. |
| `ItemBase` (`0x006E2AF0`) | Takes no argument and calls `0x0075EAC0`, which sends the record `0x0132` of `0x18` bytes through `0x004D6D30`. |

`0x00767FC0` resolves a record through `0x0071D420`. When the byte at record
`+0x29` is zero it calls `0x00767C00` directly. Otherwise it appends the request
to a deque at `this +0x24` through `0x007838C0` when the deque is empty and then
calls `0x00767C00`, or takes the path at `0x00768024` when the deque holds
entries. Whether `0x00767C00` emits a client packet was not traced.

The `ItemBase` record is the serverbound map opcode `0x0132`, which
`xivl-opcodes:opcodes.json` lists as `ItemWorkUpdatePacket` with the decomp anchor
`FUN_0075EAC0`. It stores the first dword of its first argument at record `+0x10`,
the low word of its third argument (the dword at receiver `+0x6C`) at `+0x14` and
the byte of its second argument (receiver `+0x68`) at `+0x1A`.

The scripts guard each call with `canRequestInformation()` on the local player and
follow it with `recordRequestInformation()` (`MEASURED`). That makes the native a
throttled request to refresh a work member. The role is `INFERRED`.

## Lock-on control

`_lockLockonControl` and `_unlockLockonControl` are thunks through slots `0x11C`
and `0x120`. The `PlayerBase` cells `0x00FD5F20` and `0x00FD5F24` hold bare
returns (`0x006DEA30`, `0x006DEA40`). The `MyPlayer` cells `0x00FD7978` and
`0x00FD797C` hold `0x006E3380` and `0x006E33A0`. Each loads the dword at
`Y +0x08` and calls `0x0075B2A0` or `0x0075B2B0`, which add `0x17758` to `V`
through `0x004D7580` and call virtual slot 7 or 8 of the
`RaptureUserControl` object at that address. Those slots, `0x0054B650` and
`0x0054B660`, add 1 to and subtract 1 from the dword at object `+0x40`. The
player control pair of the [binding map contracts](binding-map-native-contract.md#player-control)
uses the dword at `+0x18`. There is no floor test. Slots 7 and 8 return the new
value in `eax`. Slot 9 (`0x0054B670`) returns the dword, and its only caller
glue is `0x0075B2C0`, which `0x00705170` calls. `0x00705170` is the `MyPlayer`
vftable cell `0x00FD7980` (slot `0x124`, next to the lock pair) and pushes a bool
that is true when the dword is zero (`sete`, `0x0070518A..0x007051A0`). The name
of the native that owns that slot was not read. The dword is part of the
`RaptureUserControl` object embedded at `V +0x17758` (vftable `0x00F90F64`), so
`V +0x17758` plus `0x40` holds it, and its initial value comes from the object's
construction, which was not traced.

## Queries

`_getGMRank` (`0x00706C70`) loads the byte at receiver `+0xEC`. Zero pushes nil
and any other value is pushed as an int. The `PlayerBase` constructor
(`0x006ED740`, which stores the vftable `0x00FD5E04` at `0x006ED753`) zeroes the
dword at `+0xE8` and the bytes `+0xEC` to `+0xF1`. The only other store in
`PlayerBase` code is in the override of vftable slot 30 (`0x006F0220`, cell
`0x00FD5E7C`), which copies the dword at argument `+0x48` to `+0xE8`, the byte at argument `+0xB6` to
`+0xEC` (the GM rank) and the byte at argument `+0xC6` to `+0xF1` (`STATIC`).
A scan of the whole `.text` for byte stores to `[reg+0xEC]` finds 14 sites. Two
are the constructor (`0x006ED75F`) and the slot 30 override (`0x006F0263`). The
other twelve (`0x0058AAB0`, `0x0058AEE3`, `0x0058B493`, `0x0058B996`,
`0x0058BC3F`, `0x006C1356`, `0x006C1387`, `0x006C569D`, `0x008343C3`,
`0x00ACE998`, `0x00AECDFB`, `0x00AEE019`) lie in code that no `PlayerBase`
vftable slot starts, so that they belong to other classes is `INFERRED`. The
argument is the record that the sub stat status receiver hands to that slot
(`xivl-client-structs:manifests/symbols.json` row `0x006F0220`). A player the
server sends with a zero at that record byte reports no rank. Which packet
field fills the record byte was not traced.

`_getRegion` (`0x006F96C0`) resolves `W`, loads `V` and takes the object at
`V +0x4E0` through `0x004D7390`. It pushes the dword at `+0x94` of that object, or
the dword at `+0xAC` when the first is zero. The answer does not depend on the
receiver. The object keeps three slots of `0x10` bytes from `+0x8C`: a dword at
`+0x00`, `+0x04` and `+0x08` and a byte at `+0x0C`. The dword at `+0x94` is the
third dword of the first slot and `+0xAC` the first dword of the third slot.
The constructor `0x0060DD90` (`0x0060DDA9..0x0060DE08`) and the reset
`0x0060DBC6..0x0060DBD2` zero them, and a nonzero dword with a zero flag byte at
`+0xA8` or `+0xB8` is released through the engine object at `0x01328048`
(`0x0060DBA0..0x0060DBBE`). So the dwords are zero until the object is filled,
and the region answer is 0. The stores of nonzero values were not traced.

`_getOrientation` (`0x006F9B20`) reads the first and third float and never the
second. It builds the world position record of the receiver through `0x0075C230`
as `_getPosition` does, subtracts the record x from the first float and the
record z from the third, calls `0x009DAEBA` with the two differences and
subtracts the record heading from the result. It folds the angle into the range
around zero with the rule of `_getDirection` and pushes it as a float. The record
is read at the offsets `+0x00` (x), `+0x08` (z) and `+0x0C` (heading). The call
`0x009DAEBA` loads the descriptor `0x012EBB80`, whose name field is `atan2`, and
jumps to the two operand CRT dispatcher `0x009ECA10`. The routine that does the
work (`0x009EC97C`) takes the absolute values of both operands, runs `fpatan` and
corrects the quadrant from the signs. `fpatan` computes `atan(ST1 / ST0)`. The
callback loads the x difference first and the z difference second, so ST1 holds
the x difference and ST0 the z difference and the result is
`atan2(dx, dz)` with the numerator `dx` (`STATIC` for the name, the load order
and `fpatan`. The entry order of the dispatcher is the MSVC `_CIatan2`
convention, `INFERRED`). The angle is 0 for a target straight along +z and
grows toward +x. The record heading is subtracted unfolded. The result is the
bearing from the receiver to the point relative to its heading.

The fold reads the angle `a` as a float and computes, in doubles, `a + pi` for
`a` at or above 0 and `a - pi` below 0 (`0x00F62F48` holds
3.1415927410125732, the float pi widened). It divides by `0x00F62FE0`
(6.2831854820251465), truncates the quotient toward zero to an int `n` with
`cvttsd2si`, converts `n` to a float and back, and returns `a - n * 2pi`
rounded to a float (`0x006F9BF6..0x006F9C57`). An angle strictly between -pi and
pi comes out unchanged. The endpoints swap: `a = pi` returns -pi and
`a = -pi` returns +pi. A nonnegative angle lands in [-pi, pi) and a negative one
in (-pi, pi]. A NaN takes the below zero branch because the `fcompi` compare
sets the carry flag (`jb`) for an unordered result.

`_turnDir` is an alias that the `_turnDir_inl` descriptor of `charabaseclass_u`
maps to the key `_turnClientDir_cpp`. Scripts therefore reach the registration at
order 61 (`0x006E47D0`). The registration under the name `_turnDir` at order 60
(`0x006E4700`) runs an identical instruction sequence. Both fold the float with
the rule above and call `0x0075C300`, which resolves the chara and calls
`0x00587D40`. That routine stores the angle at chara `+0xAC` and ORs 2 into the
byte at `+0x26D` when the angle differs from the current heading or the bytes at
`+0x264` or `+0x265` are nonzero.

`_getMemberLocalizedDisplayName` (`0x00700110`) reads an int `n`, builds the
member display name record of member `n - 1` through `0x006C0D80` and pushes the
`Utf8String` at record `+0x04`. `_getMemberDisplayName` of the
[binding map contracts](binding-map-native-contract.md#group-natives) uses the
same builder and pushes an index or a string with a flag. This one never pushes
the index form.

`_getOccupancyGroup` (`0x00709C80`) calls `0x00700680` with the flag 0. The
sibling `_getExtendedTemporaryOccupancyGroup` (`0x00709C90`) passes the flag 1.
The routine reads the dword pair at group data `+0x68` and `+0x6C` through
`0x006BFD30` (the pair is the first two dwords of the group data sub object at
`+0x68`. The group constructors at `0x006DD038` and `0x006DD09E` either leave
it, because `0x006BFD00` is a bare return, or clear the dwords at `+0x68`,
`+0x70` and `+0x74` through `0x006BFCD0` and leave the dword at `+0x6C`.
`0x006E2240` copies the pair from the found registry record at `0x006E2915`.
The source of the registry records was not traced). The routine resolves `Y`
and searches the registry at `Y +0xE4` through
`0x006C2090`. `0x006CB950` tests the result against the identity. A failed test
pushes nil. Otherwise `0x006E2240` obtains a control through `0x00CC80A0` (flag
0) or `0x00CC8140`, casts it from `LuaControl` to `GroupBase` with `0x009DA6CC`
and copies the 16 bytes of the found record to object `+0x68` and `+0x70`. The
pusher `0x00748B30` pushes the control. Whether the control is new on every call
was not traced.

## Debug instance name

`system/debug_u` assigns the plain function `Debug._getInstanceName(self, value)`
and no `_inl` descriptor. Its body tail-calls `debug:_getInstanceName_cpp(value)`
on the global `debug` object (`MEASURED`). The registered native
(`0x006DC6F0`) reads a control, calls `0x00CC7520` and pushes the result as a
`Utf8String`. `0x00CC7520` finds the registration record of the control through
`0x00CD7A30` and copies the string at record `+0x50`, the field that the widget
work contract uses as the class name (`INFERRED` as the class name).

## Ledger rows

These rows of the unimplemented ledger have a registration or a script surface,
an argument list, a return list and a callback contract: `_setTouchAttribute`,
`_isTouching`, `_updateWork`, `_lockLockonControl`, `_unlockLockonControl`,
`_getGMRank`, `_getOrientation`, `_getMemberLocalizedDisplayName`,
`_getOccupancyGroup`, `_getRegion`, `_getInstanceName` and `_turnDir`. The names
`_bindWork` and `_bindWorkNestingArray` are script helpers over the `_bind` flag
of the work userdata and not functor natives. A client that implements the rows
still needs the pool objects behind the work accessors, the callers of the by-id
accessors, the readers of the touch attribute masks and the lock-on counter, and
the request service behind `_updateWork`, which this record does not supply.

## Open

- The class of the pool objects behind the read and write accessors, their
  allocation and whether they are zero filled, so the initial value of a
  declared member before its first write. The string, actor and timer readers.
- The code that applies a numeric third operand of a boolean or numeric tag as
  an element count, and the origin of a nested list (the nesting member's own
  start is inferred). Until those are read, the starts in
  [derived bind starts](#derived-bind-starts) are `INFERRED`.
- The index base of the member readers, which pass the index through `0x00D25900`
  without a visible subtraction, and the proxy that turns `a[i]` into an index
  cell.
- The role of the second int of a bind, the callers of the by-id accessors and
  the packets that carry bind ids.
- The origin of the class level byte (key record `+0x14`) beyond its use as a
  vector index.
- What the client does with a `_tag` group.
- The producer of the async opcode `0x60` that writes the touch byte at
  `+0x45D`, the meaning of the attribute numbers, the writers of the byte at
  `+0xBA` and the list at `Y +0x1C`, and the readers of the two touch attribute
  sets. The callers of the touch edge routine `0x005893F0` pass through the
  thunks `0x0058ABA0` and `0x0058ABB0` and two direct calls.
- Whether `0x00767C00` and `0x006C72E0` send a packet for `_updateWork`, and which.
- The construction of the `RaptureUserControl` object (initial value of the
  lock-on dword) and the name of the native behind `MyPlayer` slot `0x124`.
- The packet field that fills the sub stat status record byte at `+0xB6`, the
  stores of nonzero values into the area slots at `V +0x4E0 +0x8C`, and the
  source of the group registry records at `Y +0xE4`.
- Whether `_getOccupancyGroup` returns a new control on every call.
- The `DesktopWidget` pair `_lockTargetCursorControl` (order 17) and
  `_unlockTargetCursorControl` (order 18) and the `WorldMaster` tutorial natives
  (ranks 1 to 4 and 7 of the ranked list) were not traced. Their registrars,
  callbacks and yield behavior are open, and no byte evidence here says that any
  of them yields.

The next natives by value are ranked by the number of distinct scripts that
contain a call, with the call-site count as the tie break. Natives with a
contract in any manifest or a wire-level record in a contract page are left out,
and so are the script callbacks that begin with `_on`, the work keys and the
descriptor suffix identifiers. An alias takes the class of its descriptor.

| Rank | Native | Class | Scripts | Call sites | Why |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | `_runCharaSchedulerTutorial` | `WorldMaster` | 5 | 44 | Order 12 of the WorldMaster switchboard. |
| 2 | `_lookAtPlayerTutorial` | `WorldMaster` | 5 | 23 | Order 14 of the WorldMaster switchboard. |
| 3 | `_aimCameraTutorial` | `WorldMaster` | 5 | 22 | Order 16 of the WorldMaster switchboard. |
| 4 | `_cancelAimCameraTutorial` | `WorldMaster` | 5 | 22 | Order 17 of the WorldMaster switchboard. |
| 5 | `_lockTargetCursorControl` | `DesktopWidget` | 5 | 12 | Order 17 of the DesktopWidget switchboard. |
| 6 | `_unlockTargetCursorControl` | `DesktopWidget` | 5 | 12 | Order 18 of the DesktopWidget switchboard. |
| 7 | `_cancelLookAtPlayerTutorial` | `WorldMaster` | 5 | 11 | Order 15 of the WorldMaster switchboard. |
| 8 | `_commandDebug` | `Debug` | 5 | 8 | Order 7 of the Debug switchboard. |
| 9 | `_waitForMapLoaded` | `PlayerBaseClass` | 5 | 8 | Order 38 of the PlayerBase switchboard, a candidate yield native. |
| 10 | `_getAllCharacter` | `Debug` | 4 | 17 | Order 5 of the Debug switchboard. |
| 11 | `_getAllGroup` | `CharaBaseClass` | 4 | 10 | Order 43 of the CharaBase switchboard. |
| 12 | `_getGrandCompanyRank` | `PlayerBaseClass` | 4 | 9 | Order 52 of the PlayerBase switchboard. |
| 13 | `_setWeather` | `PlayerBaseClass` | 4 | 8 | Order 40 of the PlayerBase switchboard. |
| 14 | `_createVirtualItem` | `CharaBaseClass` | 4 | 6 | Order 76 of the CharaBase switchboard. |
| 15 | `_getNetStatUser` | `CharaBaseClass` | 4 | 6 | Order 19 of the CharaBase switchboard. |
| 16 | `_getAreaType` | `PrivateAreaBaseClass` | 4 | 5 | Order 1 of the PrivateAreaBase switchboard. |
| 17 | `_lockCameraControl` | `PlayerBaseClass` | 3 | 12 | Order 33 of the PlayerBase switchboard, next to the lock-on pair. |
| 18 | `_unlockCameraControl` | `PlayerBaseClass` | 3 | 12 | Order 34 of the PlayerBase switchboard, next to the lock-on pair. |
| 19 | `_getClassName` | `Debug` | 3 | 11 | Order 3 of the Debug switchboard, next to _getInstanceName. |
| 20 | `_waitForTargetTutorial` | `DesktopWidget` | 3 | 9 | Order 35 of the DesktopWidget switchboard, a candidate yield native. |

The manifest rows under `nextTranche` carry the same order. The
[Global native contracts](global-native-contract.md) cover ranks 1, 2 and 3 and the
nine `Global` natives that ranked below the twentieth row, and carry the refreshed
order.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes with the route of the
[binding map contracts](binding-map-native-contract.md#reproduction). The script
facts come from the `.le.lpb` files of an installed client decoded by
[`tools/decode_lpb.py`](../tools/decode_lpb.py) and read with a Lua 5.1 bytecode
parser. The declaration lists come from evaluating the bodies of
`CharaBaseClass._onInit`, `initCommonParameterSync`, `initBattleSync`,
`initEventSyncWork` and `PlayerBaseClass._onInit` on that parser with the work
members replaced by recorders. The function VAs for `$Addresses` are:

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Work binder | `0x00D2F000,0x00D175B0,0x00D16CD0,0x00D16D40,0x00D272D0,0x00D12200,0x00D12210,0x00D20490,0x00D27480,0x00D25C50,0x00D25900,0x00D12220,0x00CE67F0,0x00CE6E30,0x00CE5040,0x00CE48C0,0x00D260D0` |
| Descriptor slots | `0x00D2DDE0,0x00D2DE10,0x00D2DE20,0x00D2DE30,0x00D2DE40,0x00D25960,0x00D2DE90,0x00D2DEA0,0x00D28890,0x00D28D10,0x00D291B0,0x00D29660,0x00D29B00,0x00D29FD0,0x00D2B810` |
| Registrars | `0x007338A0,0x007290E0,0x0073EB40,0x0073EF30,0x0073FC50,0x00730810,0x00732A30,0x00732B80,0x0074F230,0x0074A760,0x0074D400,0x00756B70,0x00749A40,0x007367E0,0x0072FEE0,0x0072FD90` |
| Callbacks | `0x006E6110,0x00705320,0x006E7670,0x006E8890,0x006E85E0,0x006E2AF0,0x006E3380,0x006E33A0,0x00706C70,0x006F9B20,0x00700110,0x00709C80,0x00700680,0x006E2240,0x006F96C0,0x006DC6F0,0x006E47D0,0x006E4700` |
| Touch attributes | `0x00895EF0,0x00895790,0x0089A1C0,0x0089A780,0x0075C950,0x00589720,0x00894EE0,0x0075C970,0x00589750,0x00763030,0x004D72F0,0x005893F0,0x00574D50,0x00574D60,0x0058E0C0,0x00588200,0x00588300,0x00588330,0x007CE7B0` |
| Layout and bind records | `0x00D1E0F0,0x00D1F4F0,0x00D28390,0x00D28BE0,0x00D23DA0,0x00D1C100,0x00D15F70,0x00D174B0,0x00D25900,0x00CE5BF0,0x00CE5290,0x00CE4550,0x00CE4450,0x00CE4250,0x00CCB3F0,0x00CCB430,0x00D27450` |
| Value coercion | `0x00D28810,0x00D28C10,0x00D290B0,0x00D295D0,0x00D29A00,0x00D29F40,0x00D2A410,0x00CF35C0,0x00CF35E0,0x00DCDED0,0x00DCDF50,0x00DDE8B0,0x009D6636` |
| Orientation and queries | `0x009DAEBA,0x009ECA10,0x009EC97C,0x006F9B20,0x006ED740,0x006F0220,0x0075C7B0,0x0060DD90,0x006DD038,0x006BFCD0,0x0075B2C0,0x00705170` |
| Work refresh | `0x0070AA10,0x00767FC0,0x00767C00,0x006C7A80,0x006C72E0,0x0075EAC0` |
| Queries | `0x0075C7B0,0x004D7390,0x0075C300,0x00587D40,0x00CC7520,0x0078C550,0x0075B2A0,0x0075B2B0,0x0054B650,0x0054B660,0x0054B670` |
| Holders | `0x00726720,0x0071E760,0x0071E7D0,0x00726930,0x0071AAE0,0x0071AB50,0x0072CD40,0x0072C9A0,0x0072CAF0,0x00726D50,0x0071E290,0x0071E300` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
