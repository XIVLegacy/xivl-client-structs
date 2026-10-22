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
uninitialized data. The lookup order of the pools is temp, save, sync.

### The bind route

The `_bind` branch pushes stack index 3 and converts it with `0x00CF35E0`. It
calls `0x00D12200` with the pointer from the second closure upvalue
(`0x00D20490`). That pointer addresses a dword that holds the storage object of
the instance record. `0x00D12200` stores the converted byte at `+0x48` of the
storage object and `0x00D12210` reads it back. The flag is therefore shared by
every work member of one instance.

The write routine `0x00D272D0` starts with `cmp dword ptr [ebx],0` on the same
pointer. A zero dword ends the call with no store. Otherwise it reads the flag
through `0x00D12210` (`0x00D27308`).

| Flag | Route |
| --- | --- |
| Clear | Descriptor slot `0x6C` at `0x00D27353` validates the value. When it answers true and the key record kind byte at `+0x2C` equals the byte at `0x01377FB9`, descriptor slot `0x04` stores it. |
| Set | Descriptor slot `0x64` at `0x00D27337` receives the pointer, the key record and the sentinel `0x0130D788`. No value is stored. |

Slot `0x64` is `0x00D27480` for every member type except `timer`, whose slot is
`0x00D25C50` (`ret 0x1C`). The routine tests whether stack index -1 is a table
(`0x00CF3740`). A table supplies two ints from its elements 1 and 2. Any other
value supplies one int and the second int is -1. It converts the element index
through `0x00D25900`, takes the member width from slot `0x0C` divided by 8 and
calls `0x00D12220`, which jumps to `0x00CE67F0`, with the first int as its first
argument.

`0x00CE67F0` looks the first int up in the hash table at `0x01377F20` through
`0x00CE6E30`, which hashes the key as the key xor `0xDEADBEEF`. An existing entry
whose dword at `+0x10` equals the new element offset ends the call. An id with no
entry is stored in that table (`0x00CE6A6B..0x00CE6A7B`) as a record of two member
bytes, the element offset dword, a 16 bit value from the sixth argument (`0xFFFF`
when it equals the sentinel), one byte from the second int (`0xFF` when negative)
and the span byte. An id whose entry holds a different element offset leaves that
entry untouched. The routine instead looks up or creates an entry in the table at
`0x01377F48` through `0x006D1170`, keyed by the receiver dword that the routine
takes in `ecx`, and inserts the same record into the hash table that this entry
holds at `+0x0C` (`0x00CE68CE..0x00CE6A0B`). `0x00CE5040` looks a key up through that
second table and the hash table that its entry holds at `+0x0C`, and otherwise in
the table at `0x01377F20`. Eight accessors call it: `0x00CE5290`, `0x00CE53D0`,
`0x00CE5490`, `0x00CE5540`, `0x00CE5600`, `0x00CE56E0`, `0x00CE57D0` and
`0x00CE58B0`. Seven engine wrappers at `0x00CC7B90`, `0x00CC7BE0`, `0x00CC7C30`,
`0x00CC7CD0`, `0x00CC7DE0`, `0x00CC8580` and `0x00CC85C0` call six of them.

So the first bind of an id is a global default, and a bind of the same id to a
different element offset is a per-receiver override that the reader prefers
(`STATIC` from the lookup order of `0x00CE5040`). That the receiver key is the
work storage object of one actor, so that layouts with different nesting sizes
under the same ids coexist per instance, is `INFERRED`; the producer of the key
at the callers of `0x00D12220` was not traced. The role of the second int, the
callers of the wrappers and the packets that use bind ids were not traced.

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

A `nesting` entry carries a number. The six nested members of `charaWork` give
the following figures for the local player, where the sums count every element
at its tag width.

| Nested member | Operand | Sum of widths, bits | Rounded up, bytes |
| --- | ---: | ---: | ---: |
| `parameterSave` | 512 | 2056 | 257 |
| `parameterTemp` | 256 | 880 | 110 |
| `battleSave` | 512 | 3410 | 427 |
| `battleTemp` | 128 | 628 | 79 |
| `eventSave` | 3 | 17 | 3 |
| `eventTemp` | 9 | 67 | 9 |

The operand is a byte capacity (`INFERRED`). `eventSave` and `eventTemp` equal the
byte rounded sums exactly. For a receiver that is not the local player the
operands are 64 and 16 for `parameterSave` and `parameterTemp`, which hold 336
and 48 bits, so the operand cannot be a bit count. An array member counts `count`
times its element width in these sums. The layout routine `0x00D1E0F0` adds the
width of each member to a running offset in declaration order. The alignment of
byte sized members is not settled.

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
true or the byte at `0x01355297` (uninitialized data) for false. On first use it
allocates `0x18` bytes at `MyPlayer +0x10C` and constructs two empty ordered sets
of byte keys at `+0x00` and `+0x0C` (`0x00895EF0`, `0x0089AE80`). `0x00895790`
then searches the attribute in both sets. When it is in neither, it calls
`0x0075C950`, which reaches `0x00589720` on the object at `V +0x17838` and sets
the bit of the attribute in the byte at `+0x45C`. An attribute of 8 or more
changes no bit, because the shift runs in an 8 bit register. The routine finally
inserts the attribute into the set at `+0x00` when the flag byte equals the byte
at `0x012D7C43` and into the set at `+0x0C` otherwise.

`0x00705320` reads the attribute and calls `0x00894EE0`. For attribute 1 that
routine first calls `0x00763030` on `Y` and answers false when it returns true.
`0x00763030` returns the byte at `+0xBA` of the object in the first node of a list
at `Y +0x1C`, or 0 when the list at `+0x20` is empty. Otherwise `0x00894EE0`
reaches `0x00589750` and answers the bit of the attribute in the byte at
`+0x45D` of the object at `V +0x17838`. It does not read the sets. The bytes
`+0x45C` and `+0x45D` are different bytes of that object.

The roles are `INFERRED` from the names and the call chains. The scripts pass the
attribute numbers 1, 2 and 5 only. The writers of the byte at `+0x45D`, the
readers of the two sets and of the byte at `+0x45C`, and the meaning of the
numbers were not traced.

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
uses the dword at `+0x18`. There is no floor test
and the readers of `+0x40` were not traced. Slot 9 (`0x0054B670`) returns it.

## Queries

`_getGMRank` (`0x00706C70`) loads the byte at receiver `+0xEC`. Zero pushes nil
and any other value is pushed as an int.

`_getRegion` (`0x006F96C0`) resolves `W`, loads `V` and takes the object at
`V +0x4E0` through `0x004D7390`. It pushes the dword at `+0x94` of that object, or
the dword at `+0xAC` when the first is zero. The answer does not depend on the
receiver.

`_getOrientation` (`0x006F9B20`) reads the first and third float and never the
second. It builds the world position record of the receiver through `0x0075C230`
as `_getPosition` does, subtracts the record x from the first float and the
record z from the third, calls `0x009DAEBA` with the two differences and
subtracts the record heading from the result. It folds the angle into the range
around zero with the rule of `_getDirection` and pushes it as a float. The call
`0x009DAEBA` is `INFERRED` to be the MSVC arctangent of two values. The result is
then the bearing from the receiver to the point relative to its heading.

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
`0x006BFD30`, resolves `Y` and searches the registry at `Y +0xE4` through
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

- The pool objects behind the read and write accessors, the initial value of a
  declared member before its first write, and the string, actor and timer
  readers.
- The index base of the member readers, which pass the index through `0x00D25900`
  without a visible subtraction.
- The role of the second int of a bind, the callers of the by-id accessors and
  the packets that carry bind ids.
- What the client does with a `_tag` group.
- The writers of the byte at `+0x45D`, the byte at `+0xBA` and the list at
  `Y +0x1C`, and the readers of the two touch attribute sets.
- Whether `0x00767C00` and `0x006C72E0` send a packet for `_updateWork`, and which.
- The readers of the dword at `+0x40` of the `RaptureUserControl` object.
- The writers of `PlayerBase +0xEC`, of the area dwords at `+0x94` and `+0xAC`,
  and of the group id pair at `+0x68` and `+0x6C`.
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
| Touch attributes | `0x00895EF0,0x00895790,0x0089A1C0,0x0089A780,0x0075C950,0x00589720,0x00894EE0,0x0075C970,0x00589750,0x00763030,0x004D72F0` |
| Work refresh | `0x0070AA10,0x00767FC0,0x00767C00,0x006C7A80,0x006C72E0,0x0075EAC0` |
| Queries | `0x0075C7B0,0x004D7390,0x0075C300,0x00587D40,0x00CC7520,0x0078C550,0x0075B2A0,0x0075B2B0,0x0054B650,0x0054B660` |
| Holders | `0x00726720,0x0071E760,0x0071E7D0,0x00726930,0x0071AAE0,0x0071AB50,0x0072CD40,0x0072C9A0,0x0072CAF0,0x00726D50,0x0071E290,0x0071E300` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
