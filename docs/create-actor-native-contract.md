# _createActor native contract

[`manifests/create_actor_native_call_contract.json`](../manifests/create_actor_native_call_contract.json)
records the static Lua call contract of the Global native `_createActor` for every class kind that the shipped
scripts create. The native builds a control from a class name, registers it under a name, runs the class
`_onInit` and returns the control to a Lua thread that it parks until the control is ready. The record gives the
registration, the argument handling, the reuse branch, the class kind dispatch through the class prototype, the
objects that each kind allocates, the resume checker, the thread ownership record and the failure paths. It also
gives the contract of the script method `AreaBaseClass._loadSpreadSheetPermanently`, which consumes the sheet
controls that `_createActor` makes. The record does not describe sheet content, widget layout or server
behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data at the cited addresses. `MEASURED`
is counted from the call-site index or read from the decoded installed client scripts. `INFERRED` is a role taken
from the surrounding instructions that the bytes do not state. `unknown` was not traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image base `0x00400000`, `15996808` bytes,
SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned by
[`manifests/retail_inputs.json`](../manifests/retail_inputs.json). The registrar shape, the type registry and the
argument marshaller are the ones of the [widget contracts](widget-native-call-contract.md#registration). The
receiverless call convention is the one of the [Global contracts](global-native-contract.md). The result cells
of the resume checker are the ones of the [scheduler contracts](scheduler-item-native-contract.md). The class
registry vocabulary is the one of the [Lua class system](lua-class-system.md).

A script decoded each address of the record from the executable bytes and asserted it. Callers and stores come
from a linear decode of the `.text` section, so virtual and indirect references are not covered.

The `MEASURED` script facts come from the call-site index `xivl-client-scripts:lua/napi_index.json` and from the
Lua 5.1 bytecode of the installed client scripts. [`tools/decode_lpb.py`](../tools/decode_lpb.py) decodes the
chunks and the facts are read from their constants and instructions. The script bodies are not tracked.

## Registration and signature

`_createActor` is registered by `0x00757350`, which pushes the name literal `0x00FD85DC` at `0x00757439` and
loads the callback `0x00709640` at `0x00757387`. Its only caller is `0x00758326` in the Global switchboard
`0x007582E0`, slot 2 of the Global vftable `0x00FD60AC`. The callback is a direct member function of the Global
holder. The script descriptor `_createActor_inl` in `global_u` returns the receiver selector `global` and the
name `_createActor_cpp`, so a script call is receiverless. The Lua arguments start at native-frame position 2,
which is cell 0 of the ExecuteParameters argument list. The table indexes the cells.

| Cell | Operator | Role |
| ---: | --- | --- |
| 0 | `Utf8String` | Instance name. A nil cell becomes the empty string object at `0x01377E78`. |
| 1 | `Utf8String` | Class name looked up in the class registry. |
| 2 | `bool` | Reuse an existing control of that name. A nil cell counts as false. |
| 3 | `Variable` | Payload that the creation hands to `_onInit`. |

The return list holds one `LuaControl*`. The marshaller pads a missing argument with a nil cell, so
`_createActor("desktopUtil", "DesktopUtil")` reads cell 2 as nil and takes the creation branch.

## Call sequence

The callback keeps the ExecuteParameters pointer in ESI. Its `+0x04` field is the engine context C, `+0x08` the
thread context T, `+0x10` the argument cell holder and `+0x1C` the return container. C holds the manager M as
its first dword.

1. The callback reads cells 0 and 1, the name and the class name. It resolves the control registered under the
   fixed identity `0xC0000024`. It keeps a probe byte that is 1 unless that control is missing or its byte at `+0x5C` is 0.
   The local player actor apply creates the selector `0x1A` form element under that identity, as the
   [Rapture selector record](../manifests/rapture_selector_0d_clientwork.json) shows.
2. A false or nil reuse flag, or a name that the registry does not hold, takes the creation branch.
3. A true reuse flag and a registered name take the reuse branch. The control is ready when the probe byte is
   set and the control byte at `+0x5C` is set, or when the probe byte is clear and the valid byte at `+0x7D` of
   the control record is set. A ready control is pushed at once and the call returns without a yield. The class
   of the control and the payload are not examined. A control that is not ready takes the wait path below.
4. The creation branch copies the cells from 3 on, converts them and looks up the class record. It makes
   one virtual call through slot `+0x6C` of the class prototype with C, the address of the name, the class name,
   the address of the converted payload and the address of the thread identifier word.
5. The result is used without a null test. The wait path builds the identity of the result, records it in the
   Global ownership map, allocates the 16 byte `OnInitResumeChecker` and yields.

## Class kinds

The record of a class name holds a prototype control. The native class table registrar `0x0075F9B0` builds the
prototypes. For each native class it allocates the object, runs the constructor and registers the name, the
parent name and the object with `0x00CC9700`. A class without its own object registers through `0x00CC9760`
and `_defineClass` clones the parent prototype for the child through `0x00CE2D50`. A script class therefore
takes the native kind of its nearest ancestor that has a prototype. Creating an instance calls virtual slot `+4`
of the prototype, which allocates a new object of that type.

Slot `+0x6C` of the prototype decides what `_createActor` can create. Four implementations exist.

| Kind | Class names | Prototype vftable | New object | Create slot | Identity |
| --- | --- | --- | --- | --- | --- |
| SpreadSheet | `SpreadSheet` | `0x00FD7744` | `0x00747CD0`, `0xDC` bytes | `0x006E3650` | allocated, selector 0 |
| WidgetBase | `WidgetBaseClass`, `DesktopWidgetBaseClass` and the Lua classes defined from them | `0x00FD5A74` | `0x0071B320`, `0x68` bytes | `0x006E3920` | allocated, selector `0x1A` |
| DesktopUtil | `DesktopUtil` | `0x00FDFC9C` | `0x00776CF0`, `0x68` bytes | `0x006E3920` | allocated, selector `0x1A` |
| CutScene | `CutScene` | `0x00FD597C` | `0x0071B210`, `0xC4` bytes | `0x006E19D0` | fixed `0xC0000005` |

The shipped scripts define 182 distinct classes that descend from `WidgetBaseClass`, counting `AskBaseClass`
itself (`MEASURED`). A transitive closure over the parent names of the 2435 `_defineClass` and 139
`_defineBaseClass` calls splits them into `AskBaseClass` (1), 128 below `WidgetBaseClass` only, 44 below
`AskBaseClass` only and 9 that different chunks define under both. 53 therefore descend from `AskBaseClass` and 138
are direct children of `WidgetBaseClass`. `AskBaseClass` is defined with `_defineBaseClass`, so it is not creatable
(see Creation). No defined class has `SpreadSheet`, `CutScene`, `DesktopUtil` or `DesktopWidget` as its parent.

The 24 other native control vftables that were read hold `0x0060CFC0` in the slot, which is `xor eax, eax` and
`ret 0x14`. They are `ActorBase`, `CharaBase`, `PlayerBase`, `MyPlayer`, `NpcBase`, `AreaBase`,
`PrivateAreaBase`, `DirectorBase`, `DesktopWidget`, `GroupBase`, `ItemBase`, `Debug`, `DebugBase`,
`CommandDebuggerBase`, `CommandBase`, `StatusBase`, `JudgeBase`, `QuestBase`, `Global`, `Math`, `String`,
`Table`, `WorldMaster` and `WidgetHandle`. A class that descends from one of them inherits the null creator.
The server spawn path creates these controls, not `_createActor`. The manifest lists each slot cell.

## Creation

The SpreadSheet and WidgetBase routines have the same instruction sequence. They resolve the service object Y
through `0x00CC7510` and the chain that starts at C `+0x220`. The Rapture container X is the first dword of Y.
They call slot `+0x50` of the prototype for a selector, which is 0 for SpreadSheet and `0x1A` for WidgetBase
and DesktopUtil, allocate an identity on X with `0x0075BE10`, call the creation function `0x0078BBB0` and
register the new control under the identity with `0x0075BE30`.

The CutScene routine pushes the fixed identity `0xC0000005` instead. After `0x0078BBB0` it casts the control to
`CutScene`, hands the cast pointer to `0x00768680` on the object at Y `+0x104`, clears the object registered under
`0xC0000005` with `0x0075BE80` and registers the new control there.

`0x0078BBB0` calls the creation core `0x00CC7800` with the name, the class name and the identity. A sixth
argument that is nonzero receives a call through its slot 1 with the new control. `_createActor` passes 0.
Then it calls `0x00CD0910` with the control, the literal `_onInit` at `0x00FE04F0` and the converted payload,
and returns the control.

The creation core `0x00CDCBA0` applies these rules:

- It looks up the class record with create set to 1. A kind tag from `0x00010008` to `0x0001000A` reports
  through `0x00CD51A0` and returns 0. A record whose byte at `+0x7B` is 0 reports through `0x00CD5220` and
  returns 0. The 24 BaseClass registrations of `0x0078E3A0` clear that byte, so those names cannot be created.
  The `_defineBaseClass` implementation `0x0078C330` clears it too: it calls `0x00CC71E0` at `0x0078C3AA`, which
  jumps to the clearing routine `0x00CD9BC0`. Every class that a script defines with `_defineBaseClass` is therefore
  not creatable, `AskBaseClass` among them. `_defineClass` (`0x0078C2A0`) reaches `0x00CD9C10` through
  `0x00CC71F0` and clears the byte at `+0x7C` instead.
- An empty name calls `0x00CD7690` with the kind tag cell `0x0130D4FC` to obtain an identity. A name equal to
  the empty string object goes through `0x00CDC940` with the same cell.
- An explicit name has its first character tested against a to z and underscore. A failure reports through
  `0x00CD55A0` and the core goes on. `0x00CD7970` takes the kind tag cell and the name and returns an identity,
  or 0 on failure. It also publishes the control as a Lua global (see Global publication).
- A registration that returns 0 takes the failure tail. A name found with a kind tag from `0x00010008` to
  `0x0001000A` reports through `0x00CD54A0` and the core returns the found record. Any other result reports
  through `0x00CD5620` and returns 0.
- A nonzero identity clones the prototype through `0x00CE2D50`. That routine allocates a `0x84` byte record, links
  the class record at `+0x0C` and sets the byte at `+0x7A`. `0x00CE1CC0` stores the identity at `+0x70`,
  `0x00CD9160` inserts the record in the registry map and `0x00CE2440` sets the byte at `+0x7E`.

`0x00CD0910` resolves the control record and passes it to `0x00CCF9B0`. That routine does nothing when the byte at
`+0x08` of the reporter object at M `+0x1CC` is nonzero or when the byte at record `+0x7F` is zero. Otherwise it
asks `0x00CCCD80` whether the method exists and runs `0x00CCEE30` with the payload. Whether `0x00CCEE30` runs the
`_onInit` body inside the call or on a separate Lua thread was not traced. `0x0078BBB0` also runs `0x00CC7AD0` at
`0x0078BC17` before this hand-off, which calls the thread registry Lua routine `0x00CF1060`.

### Global publication

The explicit-name step `0x00CD7970` works in two parts around the call to `0x00CD7690`. `0x00CF3A50` passes
`0xFFFFD8EE`, the globals index, to `0x00DCE460`, which has the `lua_rawget` shape. The step pushes the name,
reads the globals slot and returns 0 when the slot is not nil (`0x00CD7985` to `0x00CD79AF`), so the core takes its
failure tail. Otherwise `0x00CD7690` creates the instance table and stores it in the registry pool under the new
identity. The step fetches that table from the pool (`0x00CF3AB0` passes the registry index `0xFFFFD8F0`) and
sets `globals[name]` to it through `0x00CF3A70`, which passes the globals index to `0x00DCE680`, the `lua_rawset`
shape that pops the key and the value (`0x00CD79CE` to `0x00CD7A13`). The raw set bypasses the `__newindex` only
metatable of the globals table. A name whose first byte is 0 skips the test and the store, and `0x00CD7690` stores
nothing in the globals table, so an empty name publishes no global.

The route for a name equal to the empty string object, `0x00CDC940`, builds a generated name and publishes it by
the same sequence at `0x00CDCA6F` to `0x00CDCAF4`. When the global is already set it calls `0x00CDE860` with 0 in
place of the identity. Whether a Lua call can reach that route was not examined. The relation between the
instance table in the global and the `LuaControl*` that the return pushes through `0x00748B30` was not compared.

## Resume checker and thread ownership

The wait path calls `0x00CD27D0`, which is true when the byte at thread implementation `+0x138` equals the byte
at `0x01377FBA`. When it is true the callback builds a key from the owner identity at thread implementation
`+0x10` and the word at `+0x14`, stores the control identity in the Global map at `+0x6C` through `0x00726040` and
registers the thread end listener at Global `+0x68`. The yield through `0x00CD2860` and `0x00CCD390` happens in
both cases. The yield routine raises its error route when the thread state byte differs and its own flag is
clear, so a host parks the thread only from a yieldable coroutine.

The checker has the vftable `0x00FD539C`. Its constructor `0x00713FE0` stores the Global pointer at `+0x04`, the
control identity at `+0x08` and the probe byte at `+0x0C`. Slot 1 at `0x007140C0` polls. It stores the cell
`0x0130CED0`, the value 2, when no control has that identity. With a control it reads the byte at control `+0x5C`
when the probe byte is set and calls `0x00CC72A0` when it is clear. A true answer stores the done cell
`0x01377ECC` and a false answer stores the waiting cell `0x0130CECC`. The checker reads the control byte or
the ready byte at record `+0x7D`. Whether that waits for `_onInit` to finish is open. The only writer of `+0x7D` is
`0x00CE1DD0`, which the traced creation path does not call. Its callers are `0x00CC72D9` through `0x00CC72C0`,
`0x00CD988F` in the record routine `0x00CD9360`, and `0x00CE26D4` through `0x00CE26C0`. The thread teardown
`0x00CCE1C0` calls `0x00CE26C0` at `0x00CCE23E` for the owner record at thread `+0x10`. The resume may therefore
depend on an `_onInit` thread that the control owns.

The update loop `0x00CF1B50` compares the poll result with the waiting cell and leaves the thread parked on
equality. It compares any other result with the cell `0x0130CED0` at `0x00CF1D0C`. That value goes to `0x00CCE1C0`
at `0x00CF1D16` and every other value, the done result, goes to `0x00CCF290` at `0x00CF1D1D`, as the
[scheduler contracts](scheduler-item-native-contract.md) record.

Slot 2 at `0x007493A0` runs only on the done result, because `0x00CCF290` is the one routine that calls
`[vftable + 8]` (`0x00CCF31E`, `0x00CCF332`). It resolves the identity again and pushes the pointer as a
`LuaControl*` through `0x00748B30`, which stores the value tag 4 without a null branch. It then calls
`0x006ED960` on the Global receiver to erase the ownership map entries that hold the identity.

A control that is gone at the poll makes the poll answer 2, so the thread takes `0x00CCE1C0`. That routine deletes
the checker through slot 0 with 1 (`0x00CCE1E8` to `0x00CCE1F8`), runs the thread cleanup `0x00CCDED0` and
`0x00CCD910` and, for an owner record, `0x00CE26C0`. Slot 2 does not run and no value is pushed. The rest of
`0x00CCE1C0` is open in the scheduler record.

The thread end handler `0x006ED840` is slot 2 of the Global subobject vftable `0x00FD6090`. It erases the entry of
the ending thread, resolves the stored identity and, when a control is still registered, calls `0x0075BEC0`. That
routine looks up the Rapture element under the identity and calls slot 0 of the element with 1. The effect is
`INFERRED` as the destruction of a control whose creating thread ends before the wait completes. The bytes do
not tie the element destructor to the Lua control.

## Failure paths

- A class kind without a creator makes the virtual call return 0. The callback has no null test. `0x00CD7A30`
  returns 0 for the null control and `0x00CC7030` reads the dword at `+0x70` of a null pointer. Whether the
  process faults or a handler recovers it was not run.
- A creation that the core refuses returns 0 into the same tail. The refusals are an uninstantiable class record
  and a registration that returns 0 because the global of an explicit name is already set, unless the failure
  tail finds a record of the kind tags `0x00010008` to `0x0001000A`, which it returns. `0x0078BBB0` passes the 0
  on, the slot routine registers it under the identity and the callback meets the unchecked null tail.
- A class name that is not registered makes the lookup call `0x00CD5320` on the reporter object, which creates a
  tentative record. The creation core tests the class object by cast against `LuaTentativeControl`, whose vftable
  `0x0110E360` holds three slots before string data. Slot `+0x6C` of such an object lies outside its table. The
  prototype type of a tentative record is `INFERRED` from those casts.
- A name collision, an unregistered name or a class record that is not instantiable reports through the reporter
  object at M `+0x1CC` and the creation core returns 0 or the found record.

## Script side

`AreaBaseClass._onInit` runs `loadCommonTableData(region, zoneName, nil)` and then `_loadSpreadSheetPermanently()`
when `_isExistActor("desktopWidget")` is false. When `_isInn()` is true and `_isExistActor("cutReplaySheet")` is
false it assigns `cutReplaySheet = _createActor("cutReplaySheet", "SpreadSheet", true, "cutReplay")` (`MEASURED`).

`loadCommonTableData` calls `prepareSpreadSheet` for 22 paths and discards every result (`CALL` with C equal
to 1): `tribe`, `quest`, `quest_reward`,
`quest_new_reward`, `guildleve`, `guildleve_UI`, `passiveGL_craft`, `passiveGL_icon`, `shopBase`, `shopItem`,
`marketItem`, `gcSealShopItem`, `gcRank`, `blackMarket`, `itemGcExSupply`, `itemHamletSupply`, `materia`,
`compatibility`, `mapNavi_data`, `aetheryte_2Dmap`, `guildlevePack` and `achievement` (`MEASURED`).
`prepareSpreadSheet(path, name)` builds the name from the path tail split on underscores, joined in lower camel
case, followed by `Sheet`. It returns `_getActorByName(name)` when `_isExistActor(name)` is true and otherwise
`_createActor(name, "SpreadSheet", name ~= nil, path)`.

The shipped scripts read 44 distinct names that end in `Sheet` with `GETGLOBAL`, one of which is the class name
`SpreadSheet`. Of the 22 names that `prepareSpreadSheet` derives, these 20 are read by some script: `tribeSheet`,
`materiaSheet`, `compatibilitySheet`, `questSheet`, `questNewRewardSheet`, `guildleveSheet`, `guildleveUISheet`,
`passiveGLIconSheet`, `shopBaseSheet`, `shopItemSheet`, `marketItemSheet`, `gcSealShopItemSheet`, `gcRankSheet`,
`blackMarketSheet`, `itemGcExSupplySheet`, `itemHamletSupplySheet`, `mapNaviDataSheet`, `aetheryte2DmapSheet`,
`guildlevePackSheet` and `achievementSheet`. `questRewardSheet` and `passiveGLCraftSheet` are not read. The only
`SETGLOBAL` of a name that ends in `Sheet` is `cutReplaySheet` in `area/areabaseclass`. Because
`loadCommonTableData` discards the returns, the later reads reach the sheets only through the global that
`_createActor` publishes (`MEASURED`).

`_loadSpreadSheetPermanently` is not a native. It is a script method of `AreaBaseClass` in `area/areabaseclass_u`.
The registry lists it among the methods of that chunk and the native call-site index has no entry for it. Its
body reads the globals `tribeSheet`, `materiaSheet` and `compatibilitySheet` and calls the yielding native
`_loadAllKeyPermanently` of the [SpreadSheet contracts](spreadsheet-native-contract.md) on each in that order. The
call lines 68, 72 and 76 agree with the call-site index. The method does not check that the globals exist.

`SpreadSheet._onInit` calls `_callSuperClassFunc("_onInit")` and then `_setFilename` with its first payload value.
`DesktopUtil._onInit` takes no payload value. `QuestBaseClass._onInit` creates `questSheet` with the payload
`quest` when the sheet is absent and then calls `_loadKeySemipermanently` on it.

## Corpus call sites

The call-site index lists 16 sites in 11 scripts, and every site reads the function with `GETGLOBAL`
(`MEASURED`). The first argument is a literal name at 4 sites, nil at 8 sites and a computed or caller supplied
name at 4 sites. The class name is the literal `SpreadSheet` at 9 sites, `CutScene` at 1 and `DesktopUtil` at 1,
the tail of a widget path at 3 sites and a caller supplied value at 2 sites. The manifest gives the line and the
argument shape of every site. No decoded script chunk calls the `create` method of `AreaBaseClass`, which
forwards its arguments to `_createActor`.

## What a host must do

All kinds:

1. Read the name (nil or empty means generate one), the class name, the reuse flag (nil means false) and the
   payload from the fourth cell on.
2. Run only from a yieldable coroutine and park it on every branch except a ready existing control.
3. With the reuse flag true and a registered name, return that control without examining its class or the
   payload. Park first when it is not ready.
4. Look up the class prototype by class name. Refuse a class whose record has `+0x7B` clear: the 24 native
   BaseClass names and every class a script defines with `_defineBaseClass`, `AskBaseClass` among them. A class
   defined with `_defineClass` is creatable.
5. Fail the creation when an explicit name is already non-nil in the Lua globals table or already registered.
   Retail returns a null control from the core and then meets the unchecked null tail (`CALIBRATION`). Failing
   the call cleanly is `AUTHORED` host policy.
6. Create a control of the native kind of the prototype. Refuse the kinds without a creator as `AUTHORED` host
   policy.
7. Register the control under its name and an identity. For a nonempty name set `globals[name]` to the instance
   table of the control by a raw set. Call the class `_onInit` on it with the payload.
8. Resume the parked thread with the control as the single result when the poll answers done. When the control is
   gone at the poll, end the thread without a result.
9. Remove the wait record when the thread resumes and destroy the control when the creating thread ends before
   the resume.

SpreadSheet:

1. Allocate a SpreadSheet object. Its state is the one that the
   [SpreadSheet contracts](spreadsheet-native-contract.md) record.
2. Call `SpreadSheet._onInit` with the payload so that `_setFilename` receives the sheet name.
3. Resolve the resume when the readiness test passes: the byte at `+0x5C` of the control when the probe byte is
   set, otherwise the byte at `+0x7D` of the control record. The writer of `+0x7D` on the creation path was not
   traced (`CALIBRATION`), so whether the resume waits for `SpreadSheet._onInit` is open. The sheet rows load
   later through the yielding load natives.
4. Publish the control under its name as a Lua global by a raw set into the globals table, as `0x00CD7970` does.
   The loader scripts read `tribeSheet`, `materiaSheet` and `compatibilitySheet` with `GETGLOBAL`. Creation fails
   when that global is already non-nil.

WidgetBase classes and DesktopUtil:

1. Allocate a widget object of the prototype type and register it under an identity of selector `0x1A`.
2. Call the class `_onInit` with the payload that follows the reuse flag.

CutScene:

1. Replace whatever control is registered under the fixed identity `0xC0000005` and register the new CutScene
   there.
2. Hand the new CutScene to the object at Y `+0x104`.

Other kinds:

1. Retail dereferences the null creator result at `0x00CC7031` (outcome `CALIBRATION`, not run). A host refuses
   these kinds as `AUTHORED` policy.

## Open

- What sets the byte at `+0x5C` of a widget or sheet control when the probe byte is set. The constructor of
  `ActorBase` clears it and the store of 1 that was found belongs to the actor record apply `0x00766F00`. The ready
  byte `+0x7D` has no writer on the creation path, and the callers of `0x00CE1DD0` (`0x00CC72D9`, `0x00CD988F`,
  `0x00CE26D4`) with `0x00CE26C0` and the thread teardown `0x00CCE1C0` are untraced.
- Whether `0x00CCEE30` runs `_onInit` inline or on a separate Lua thread, and whether the resume waits for it.
  `0x00CC7AD0` and `0x00CF1060`, which `0x0078BBB0` runs before the hand-off, are untraced.
- The outcome of the null creator result and of a refused creation in a running client.
- Which object is registered under `0xC0000024` and whether it has a byte at `+0x5C`. The Rapture selector record
  shows that `0x00774AD0` creates the element only when it is absent and then obtains the Lua class table
  `DesktopWidget`, and `AreaBaseClass._onInit` tests `_isExistActor("desktopWidget")`, so the object is likely the
  `desktopWidget` control. That was not traced.
- Which native caller reaches `AreaBaseClass.create` and with which class name.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using the procedure in
[`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava). With explicit project and JDK bindings and a
new absolute output path, use:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Registration | `0x00757350,0x007407A0,0x0072C260,0x00726EB0,0x007582E0` |
| Callback | `0x00709640` |
| Create slots | `0x006E3650,0x006E3920,0x006E19D0,0x0060CFC0` |
| Creation core | `0x0078BBB0,0x00CC7800,0x00CDCBA0,0x00CE2D50,0x00CE2BC0,0x00CD0910,0x00CCF9B0,0x00CC7AD0,0x00CF1060` |
| Global publication | `0x00CD7970,0x00CD7690,0x00CDC940,0x00CF3A50,0x00CF3A70,0x00CF3AB0,0x00DCE460,0x00DCE680` |
| Creatability | `0x0078C2A0,0x0078C330,0x00CC71E0,0x00CC71F0,0x00CD9BC0,0x00CD9C10` |
| Ready byte writers | `0x00CE1DD0,0x00CC72C0,0x00CD9360,0x00CE26C0` |
| Registry helpers | `0x00CC7A00,0x00CC7200,0x00CC7A50,0x00CC73B0,0x00CC72A0,0x00CD8870,0x00CE16C0` |
| Checker and ownership | `0x00713FE0,0x007140C0,0x007493A0,0x006ED840,0x006ED960,0x00726040,0x00CD27D0,0x00CD2860,0x00CCD390,0x00CF1B50,0x00CCF290,0x00CCE1C0` |
| Prototype table | `0x0075F9B0,0x00CC9700,0x00CC9760,0x00CD91E0` |
| New object slots | `0x00747CD0,0x0071B320,0x00776CF0,0x0071B210` |

The script facts are reproduced by decoding the named chunks with `tools/decode_lpb.py` and reading their
constants and instructions. No decompiled body or ignored export is a tracked evidence dependency.
