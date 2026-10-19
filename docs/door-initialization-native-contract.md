# Door initialization native contract

This record supplies the native boundaries for
`xivl-client-scripts:docs/map-object-door-client-contract.md`. The script
record owns the authenticated Lua prototypes, instruction offsets and complete
DoorStandard tail. The observations here came from the retail 1.23b
`ffxivgame.exe`, size 15,996,808 bytes, image base `0x00400000`, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).

## Superclass dispatch

`FUN_0075F9B0` registers the native control classes with explicit Lua parent
names. Its NpcBase row constructs `"CharaBaseClass"` from `0x00FDEBB0` at
`0x0075FC91` and `"NpcBaseClass"` from `0x00FDEBC0` at `0x0075FCB1`, creates
the NpcBase control through `FUN_006F3650`, and calls `FUN_00CC9700` at
`0x0075FD30` with that control, the child name and the parent name. This is a
Lua registry relationship, independent of MSVC RTTI inheritance.

`FUN_00CC9700` forwards the child and parent arguments unchanged at
`0x00CC9720..0x00CC9749` and invokes `FUN_00CD9F30`. Its parent-name argument
is forwarded to `FUN_00CD9160` at `0x00CDA01C..0x00CDA034` after constructing the child
record. `FUN_00CD9160` resolves that name with `FUN_00CD8870` at
`0x00CD9193`, then calls `FUN_00CE1600` at `0x00CD919F` on the child record.
The instruction at `0x00CE1606` writes the resolved parent to child `+0x0C`.
Thus the registered parent of NpcBaseClass is CharaBaseClass.

The ActorBase registrar `FUN_0072DF60` binds `_callSuperClassFunction` to
`FUN_006DBC40`, which invokes `FUN_0078D520`. The latter reads the requested
method name, copies arguments after that name using `FUN_00753B90`, converts
them into the Lua argument sequence through `FUN_00791030`, and invokes
`FUN_00CD25F0` -> `FUN_00CCF950` -> `FUN_00CCCF90`.
`FUN_00CCCF90` carries the retained name
`Component::Lua::GameEngine::LuaThreadImpl::PrepareStackForCallBaseClassFunction_`.
It obtains the caller's class from the call frames through `FUN_00CFFC50`,
follows class-record `+0x0C` at `0x00CCD04C`, and looks up the requested method
through `FUN_00CD7A50` and `FUN_00CD7B00`. The latter can continue up the
parent chain if the method is absent. `FUN_00CCECB0` executes the prepared
call. The class name is not an extra argument to the Lua method.

The ActorBaseClass `_callSuperClassFunc_inl` descriptor returns
`"self", "_callSuperClassFunction_cpp"`. `FUN_00D07890` resolves that pair
and copies the existing native function into the alias. It does not create a
Lua forwarding frame. On the native registration path, `FUN_00CCCAD0` invokes
`FUN_00CE1750`, which copies the installing class record's name reference at
`+0x50` to native descriptor `+0x34` at `0x00CE17CA..0x00CE17D9`, and the
method name to `+0x44` at `0x00CE17DE..0x00CE17E6`. `FUN_00CD29D0` preserves
the reference's pool and key. `FUN_00CD7670` -> `FUN_00D07820` installs that
descriptor as upvalue 1 of `FUN_00D08000` in that same class table. The alias
therefore retains the native function's ActorBaseClass reference.

The native dispatcher `FUN_00D04DA0` calls `FUN_00D04FE0` before native
execution. The latter passes descriptor `+0x34` and `+0x44` to
`FUN_00CCD1B0`, whose diagnostic name is `PushCallStack`. The ordinary Lua
method path `FUN_00D04F10` supplies its defining class and method references
to the same helper. `FUN_00D01EE0` and `FUN_00D007D0` construct a 0x3C-byte
frame with class reference at `+0x04` and method reference at `+0x14`, then
`FUN_00D03250` appends it. The frame's `+0x08` is the class-reference key.
`FUN_00CFFC50` walks backward past frames whose class key matches the last
frame's key, then returns the preceding different class reference from
`+0x04` (`0x00CFFD0B..0x00CFFD3E`). Thus the ActorBase native alias frame
does not hide the preceding NpcBaseClass Lua `_onInit` frame. With no differing
frame it returns an empty reference, and `FUN_00CCCF90` keeps the supplied
class instead. `FUN_00CCDED0` pops completed calls through `FUN_00D00CF0`.

For the authenticated NpcBaseClass `_onInit` call with method name `_onInit`
and trailing `A2, A3`, this selects the CharaBaseClass `_onInit` body and
preserves those two values as its first two post-receiver arguments. The Lua
record identifies their `gameParameter` and battle-work gate uses. DoorStandard's
own initializer is reached separately through NpcBaseClass's child-method call.

## Method argument positions and work schemas

The dynamic-method registrar `FUN_00D07BB0` stores the class context and method
slot in one upvalue, and the original Lua function in the other. Its ordinary
closure `FUN_00D07F20` invokes `FUN_00D04BF0`. At `0x00D04D20..0x00D04D57`,
that helper pushes upvalue 2, copies original Lua argument 1, copies original
arguments 2 through the original stack count, then calls with that same count.
It preserves the receiver and every trailing argument without inserting a
class context or another positional value. The context is maintained outside
the Lua argument list by `FUN_00D04B70` and `FUN_00D04F10`.

`FUN_00CF3380` calls `FUN_00DCDCB0`, which copies one 16-byte Lua stack slot;
`FUN_00CF34C0` calls `FUN_00DCDAF0`, which calculates the stack count at that
stride. `FUN_00CF3530(n)` produces upvalue index `-10002-n`.
`FUN_00CF3DB0` invokes the ordinary VM call through `FUN_00DCE8A0`.
The alternate registered closure `FUN_00D07F90` calls `FUN_00D04BE0`, which
returns zero results; it does not insert arguments either.

Combined with DoorStandard `root/proto0` PC 37 / payload offset 425 and
NpcBaseClass `root/proto13` PCs 4 and 9 / offsets 3299 and 3319, the call is
exactly `initWork(self, firstDummyTable, secondSixEntryTable)`. The unused
helper `A1` receives the dummy table. Helper `A2` receives the six-entry table
and assigns it to `work._temp`. Missing `A3` defaults `work._sync` to `{}`.
The `layout`, `instance`, `count`, timers and `serverTimeAnimation` declarations
therefore belong to the temporary schema. DoorServer's two-entry second table
occupies the same `_temp` position. These declarations do not determine the
types of the arguments passed to a native reaction-box binding.

## Reaction-box arguments

The NpcBase registrar `FUN_007428B0` binds `_setReactionTriggerBox` to
`FUN_006F23F0`, not to the registrar itself. The implementation consumes five
post-receiver arguments from a vector of 16-byte typed values:

| Index | DoorStandard value | Native read and meaning |
| ---: | --- | --- |
| 0 | `"in"` or `"out"` | String tag 3 through `FUN_0071CE70` at `0x006F2448`; reaction name retained in the reaction record. |
| 1 | child `A1`, called `layout` | Integer tag 0 through `FUN_005819A0` at `0x006F2480`; reads a full four-byte integer. Its low 16 bits select the map layout for the BG attachment. |
| 2 | child `A2`, called `instance` | Integer tag 0 through `FUN_005819A0` at `0x006F24BA`; reads a full four-byte integer retained as the layout-object instance selector. |
| 3 | `"door"` | String tag 3 through `FUN_0071CE70` at `0x006F24F4`; named trigger box retained with the reaction record. |
| 4 | `nil` or `true` | Tag 6 maps directly to false at `0x006F251D..0x006F2528`; otherwise Boolean tag 2 through `FUN_0071BA00` at `0x006F2559`, reading one byte. The flag is retained with the reaction record. |

`FUN_005819A0` requires tag 0 and returns the pointer to the integer storage;
`FUN_0071CE70` requires tag 3 and returns the string pointer;
`FUN_0071BA00` requires tag 2 and returns the Boolean storage. A mismatched
tag reaches `FUN_00CCA730`'s invalid-argument path. The integer reads are not
16-bit schema reads and do not accept the float tag 1 on these paths.

`FUN_006F23F0` appends the reaction through `FUN_006F0330` and, if the actor
has no BG attachment, calls `FUN_0075C7D0` at `0x006F2602`. That helper passes
the second integer as the four-byte value and the first as the type/layout
argument to `FUN_0058BF60`. The MapObjectForChara constructor
`FUN_00590230` explicitly zero-extends the low word of the latter at
`0x00590282`, then calls `FUN_0059F2A0` with that layout and the full instance
value. `FUN_0059DF90` resolves the layout through `FUN_0079ACF0`, comparing
the requested selector to layout entry `+0x58`, with `FUN_0079B660` as its
child-layout fallback. `FUN_0059F190` retains the instance at object `+0x2C`
and uses it with the resolved layout name in `FUN_0059D310`. This is the
native meaning and narrowing boundary of the two initializer values. If the
BG attachment already exists, the creation call is skipped.

## Reproduction and limits

The observations used Ghidra 12.1.3 with the committed read-only exporters.
First authenticate the existing program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java), using
the executable identity above and the procedure in
[`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava). The
verified program reported `x86:LE:32:default`, compiler spec `windows`, one
retained FileBytes source matching the input in both original and modified
layers, and matching loaded initialized file-backed ranges. Its terminal
marker was `COMPLETE: program-file-bytes-v1`. Excluded unbacked non-executable
ranges were not used for these function or string observations.

With explicit project/JDK bindings and a new absolute output path, use:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

For `$Addresses`, the supporting function groups are:

| Observation | Function VAs |
| --- | --- |
| Parent construction and dispatch | `0x0075F9B0,0x00CC9700,0x00CD9F30,0x00CD9160,0x00CD8870,0x00CE1600,0x00CE2BC0,0x0072DF60,0x006DBC40,0x0078D520,0x00753B90,0x00791030,0x00CD25F0,0x00CCF950,0x00CCCF90,0x00CFFC50,0x00CD7A50,0x00CD7B00,0x00CCECB0` |
| Native alias and call frames | `0x00D07890,0x00CCCAD0,0x00CE1750,0x00CD29D0,0x00CD7670,0x00D07820,0x00D04DA0,0x00D04FE0,0x00CCD1B0,0x00D01EE0,0x00D007D0,0x00D03250,0x00CFFC20,0x00CCDED0,0x00D00CF0,0x00CD2A90` |
| Lua argument preservation | `0x00D07BB0,0x00D07F20,0x00D04BF0,0x00D04B70,0x00D04F10,0x00CF3380,0x00DCDCB0,0x00CF34C0,0x00DCDAF0,0x00CF3530,0x00CF3DB0,0x00DCE8A0,0x00D07F90,0x00D04BE0` |
| Reaction arguments and selectors | `0x007428B0,0x006F23F0,0x005819A0,0x0071CE70,0x0071BA00,0x00CCA730,0x006F0330,0x0075C7D0,0x0075C800,0x0058BF60,0x00590230,0x0059F2A0,0x0059DF90,0x0079ACF0,0x0079B660,0x0059F190,0x0059D310` |

Every requested target had one named decompilation section without an error
or failed-decompilation marker. Corroborate the critical calls and narrowing
instructions with the same invocation using `-Script DumpFunctionListing.java`
and this exact-entry VA list:

```text
0x0075F9B0,0x00CC9700,0x00CD9F30,0x00CD9160,0x00CE1600,0x00D04BF0,0x006F23F0,0x0075C7D0,0x0058BF60,0x00590230,0x0059F2A0,0x00CCCF90,0x0078D520,0x00CCD1B0,0x00D01EE0,0x00CFFC50,0x00D007D0,0x00D04FE0,0x00D04DA0,0x00CE1750,0x00CCCAD0,0x00CD7670,0x00D07820
```

The listing runs completed all 23 requested functions. The named-string
registration locators were checked with
`tools/ghidra/export-references.ps1 -Strings 'NpcBaseClass','CharaBaseClass'
-Out $Output`; its verifier accepted the terminal completion marker and the
13 matched strings with 13 recorded references. A separate verified address
query, `tools/ghidra/export-references.ps1 -Addresses '0x00D08000' -Out $Output`,
located the dispatcher installation at `0x00D0786C`. Reference coverage does not
establish the absence of dynamic overrides. The conclusions describe the
identified shipped class definitions and native paths, not observed door
placement, rendering, collision or reaction timing in a session. No raw
decompiled body or ignored export is a public evidence dependency.
