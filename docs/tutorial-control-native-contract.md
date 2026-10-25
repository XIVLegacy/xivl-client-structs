# Tutorial, camera and player control native contracts

[`manifests/tutorial_control_native_call_contract.json`](../manifests/tutorial_control_native_call_contract.json)
records the static Lua call contracts of thirteen natives. Five set or read the
input counters of the `RaptureUserControl` (`_lockCameraControl`,
`_unlockCameraControl`, `_isCameraControlEnabled`, `_isPlayerControlEnabled`,
`_isLockonControlEnabled`). One forces the camera mode (`_forceCameraTPSMode`).
Two undo the aim and look-at state of the tutorial natives in the
[global contracts](global-native-contract.md#tutorial-natives)
(`_cancelAimCameraTutorial`, `_cancelLookAtPlayerTutorial`). Two aim or release
the camera for a Chocobo actor (`_aimCameraChocobo`, `_cancelAimCameraChocobo`).
Three wait for a tutorial step (`_waitForCharaSchedulerTutorialFinished`,
`_waitForTargetTutorial`, `_waitForCameraTutorial`). Each row gives the
registration site, the receiver type check, the declared argument and return
lists, the reads, the effects on client state, the failure behavior and whether
the call yields. The contracts describe client marshalling and state, not
camera presentation, tutorial content or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `INFERRED` is a name or role taken from the
surrounding instructions that the bytes do not state. `unknown` was not
traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The instruction listings were decoded directly
from the PE bytes through the section table after the size and hash were
checked. Callers were found by scanning `.text` for `rel32` `call` and `jmp`
instructions, so virtual and indirect callers are not covered.

The native set and the script bindings come from
[`manifests/bulk_napi_classification.json`](../manifests/bulk_napi_classification.json)
and the script metadata. The per-row `corpusCallSites` records carry the
call-site counts from `xivl-client-scripts:lua/napi_index.json`. They show that
a script contains a call, not that a script reaches it at run time.

## Registration and dispatch

Three classes register the thirteen natives, each from the switchboard in slot 2
of its vftable. The switchboard shape, the skip byte and the single `rel32`
caller of each registrar are the ones recorded for `SpreadSheet` in the
[SpreadSheet contracts](spreadsheet-native-contract.md#registration-and-dispatch).
The order is the position among the registrar calls of the switchboard.

| Class | Switchboard | Vftable | Natives (order) |
| --- | --- | --- | --- |
| `PlayerBase` | `0x00753F90` | `0x00FD5E04` | `_isPlayerControlEnabled` (29), `_isLockonControlEnabled` (32), `_lockCameraControl` (33), `_unlockCameraControl` (34), `_isCameraControlEnabled` (35), `_forceCameraTPSMode` (95) |
| `WorldMaster` | `0x00754C70` | `0x00FD5864` | `_waitForCharaSchedulerTutorialFinished` (13), `_cancelLookAtPlayerTutorial` (15), `_cancelAimCameraTutorial` (17), `_aimCameraChocobo` (21), `_cancelAimCameraChocobo` (22) |
| `DesktopWidget` | `0x00757EA0` | `0x00FD5B8C` | `_waitForTargetTutorial` (35), `_waitForCameraTutorial` (36) |

| Native | Registrar | Caller | Callback | Wrapper |
| --- | --- | --- | --- | --- |
| `_isPlayerControlEnabled` | `0x007328E0` | `0x007541F8` | `0x006DE800` | `0x007267D0` |
| `_isLockonControlEnabled` | `0x00732CD0` | `0x00754237` | `0x006DE830` | `0x007267D0` |
| `_lockCameraControl` | `0x00732E20` | `0x0075424C` | `0x006DE840` | `0x007267D0` |
| `_unlockCameraControl` | `0x00732F70` | `0x00754261` | `0x006DE850` | `0x007267D0` |
| `_isCameraControlEnabled` | `0x007330C0` | `0x00754276` | `0x006DE860` | `0x007267D0` |
| `_forceCameraTPSMode` | `0x00735970` | `0x00754762` | `0x0071E700` | `0x007267D0` |
| `_waitForCharaSchedulerTutorialFinished` | `0x0073B400` | `0x00754D88` | `0x006E6C20` | `0x00726CA0` |
| `_cancelLookAtPlayerTutorial` | `0x0073B6A0` | `0x00754DB2` | `0x006E6E90` | `0x00726CA0` |
| `_cancelAimCameraTutorial` | `0x0073B940` | `0x00754DDC` | `0x006E7050` | `0x00726CA0` |
| `_aimCameraChocobo` | `0x0073BD30` | `0x00754E30` | `0x006E7130` | `0x00726CA0` |
| `_cancelAimCameraChocobo` | `0x0073BE80` | `0x00754E45` | `0x006E71F0` | `0x00726CA0` |
| `_waitForTargetTutorial` | `0x0073A6E0` | `0x00758186` | `0x006E5710` | `0x00726B40` |
| `_waitForCameraTutorial` | `0x0073A830` | `0x0075819B` | `0x006E1C50` | `0x00726BF0` |

Every registrar builds the return list first and the argument list second and
installs the functor through `0x00CCCAD0` under the name literal with the
adjustment 0. The wrappers `0x007267D0` and `0x00726CA0` are recorded in the
[fade contracts](fade-actor-group-native-contract.md#registration-and-dispatch)
and the [zone-in contracts](zone-in-native-contract.md#registration-and-dispatch).
Two more wrappers appear. Each constructs the `0x58` byte functor in place and
the holder invoke routine `0x0071B4D0` casts the receiver with `0x009DA6CC` from
`LuaControl` to the owner class. A null cast returns false without calling the
callback.

| Wrapper | Owner class | Qualifier | Holder vftable | Invoke | Target type descriptor |
| --- | --- | --- | --- | --- | --- |
| `0x00726B40` | `DesktopWidget` | non-const | `0x00FD5C28` | `0x0071B4D0` | `0x012C2108` |
| `0x00726BF0` | `DesktopWidget` | const | `0x00FD5C34` | `0x0071B4D0` | `0x012C2108` |

The readers are `0x005819A0` for an int and `0x0071BA00` for a bool. The return
pusher for a bool is `0x00748870`. The list builders are `0x0072B440` for none,
`0x00728C20` for an int, `0x00728B70` for a bool and `0x00583CE0` for two ints.

## Contracts

| Native | Class | Arguments | Returns | Yields |
| --- | --- | --- | --- | --- |
| `_lockCameraControl` | `PlayerBase` | none | none | no |
| `_unlockCameraControl` | `PlayerBase` | none | none | no |
| `_isCameraControlEnabled` | `PlayerBase` | none | `bool` | no |
| `_isPlayerControlEnabled` | `PlayerBase` | none | `bool` | no |
| `_isLockonControlEnabled` | `PlayerBase` | none | `bool` | no |
| `_forceCameraTPSMode` | `PlayerBase` | `bool` | none | no |
| `_cancelAimCameraTutorial` | `WorldMaster` | `int` | none | no |
| `_cancelLookAtPlayerTutorial` | `WorldMaster` | `int` | none | no |
| `_waitForCharaSchedulerTutorialFinished` | `WorldMaster` | two `int` | none | yes |
| `_aimCameraChocobo` | `WorldMaster` | `int` | none | no |
| `_cancelAimCameraChocobo` | `WorldMaster` | `int` | none | no |
| `_waitForTargetTutorial` | `DesktopWidget` | `int` | none | yes |
| `_waitForCameraTutorial` | `DesktopWidget` | none | none | yes |

The three waits call the yield request `0x00CD2860` after they build a resume
checker. No instruction between the construction and the request tests a
condition, so the wait always begins. An int of 0 to `_waitForTargetTutorial`
stays 0 at checker `+0x08`, so its poll reports done at once. Whether the request polls the checker once
before it suspends was not traced. The manifest rows carry each name literal,
name reference, install call, callback load and list builder.

## Control counters

The five player natives share the `RaptureUserControl` of the
[player control record](binding-map-native-contract.md#player-control). It sits at
`V +0x17758` (vftable `0x00F90F64`, constructor `0x004DECF0`) and holds four
channels. Each channel is a dword counter with three virtual slots that add 1,
add -1 and read. The lock-on pair of the
[work binder contracts](work-binder-native-contract.md#lock-on-control) uses
slots 7 and 8, and that record left the owner of slot 9 unnamed. Slot 9 is the
read of `_isLockonControlEnabled`.

| Channel | Counter | Add 1 | Add -1 | Read | Lua natives |
| --- | --- | --- | --- | --- | --- |
| Player | `+0x18` | slot 1, `0x0054B440` | slot 2, `0x0054B600` | slot 3, `0x0054B610` | `_lockPlayerControl`, `_unlockPlayerControl`, `_isPlayerControlEnabled` |
| Target cursor | `+0x2C` | slot 4, `0x0054B620` | slot 5, `0x0054B630` | slot 6, `0x0054B640` | `_lockTargetCursorControl`, `_unlockTargetCursorControl`, `_isTargetCursorControlEnabled` |
| Lock-on | `+0x40` | slot 7, `0x0054B650` | slot 8, `0x0054B660` | slot 9, `0x0054B670` | `_lockLockonControl`, `_unlockLockonControl`, `_isLockonControlEnabled` |
| Camera | `+0x54` | slot 10, `0x0054B680` | slot 11, `0x0054B8C0` | slot 12, `0x0054B8D0` | `_lockCameraControl`, `_unlockCameraControl`, `_isCameraControlEnabled` |

The callbacks are thunks of three instructions through the receiver vftable.
The `PlayerBase` cell of each slot holds a bare `ret 4`. `MyPlayer` (vftable
`0x00FD785C`) holds the override and registers nothing. A `PlayerBase` receiver
that is not a `MyPlayer` does nothing, and the bool natives push no value for it.

| Native | Slot | `PlayerBase` cell | `MyPlayer` cell | `MyPlayer` routine | Glue |
| --- | --- | --- | --- | --- | --- |
| `_isPlayerControlEnabled` | `0x118` | `0x00FD5F1C` | `0x00FD7974` | `0x00705130` | `0x0075B260` |
| `_isLockonControlEnabled` | `0x124` | `0x00FD5F28` | `0x00FD7980` | `0x00705170` | `0x0075B2C0` |
| `_lockCameraControl` | `0x128` | `0x00FD5F2C` | `0x00FD7984` | `0x006E33C0` | `0x0075B2D0` |
| `_unlockCameraControl` | `0x12C` | `0x00FD5F30` | `0x00FD7988` | `0x006E33E0` | `0x0075B2E0` |
| `_isCameraControlEnabled` | `0x130` | `0x00FD5F34` | `0x00FD798C` | `0x007051B0` | `0x0075B2F0` |
| `_forceCameraTPSMode` | `0x200` | `0x00FD6004` | `0x00FD7A5C` | `0x006E6570` | none |

Each `MyPlayer` routine resolves the world chain of the
[scheduler contracts](scheduler-item-native-contract.md#world-object-and-identity-lookup),
loads the dword at `Y +0x08` and calls the glue routine, which loads `V`, takes
the `RaptureUserControl` through `0x004D7580` and tail jumps through a slot. The
three enabled natives push the bool pusher byte from `SETE` after a `TEST` of the
counter, so each is true only for a counter of exactly 0 and a negative counter
pushes false. Nothing floors the counters. An unlock without a lock leaves the
camera counter at -1.

Slot 10 (`0x0054B680`) does more than count. It looks up
the object registered under the identity `0xC0000004` through `0x004D9910` on the
container stored at object `+0x04`. When the lookup returns an object, it takes
the address object `+0x08` and, for each of the command names
`RaptureCommands.MoveCamera`, `RaptureCommands.ForwardCameraOff` and
`RaptureCommands.BackwardCameraOff`, finds the command object through
`0x00928F90` and calls its virtual slot 2 with three arguments: a temporary
built by `0x0052D3A0` from 0 and 0, that address and 0. It then adds 1 to
the counter whether or not the lookup found an object. The player channel add
of the binding map contracts does the same for `RaptureCommands.MoveCharacter` and
`ShiftMoveCharacter`. The effect of the command objects was not traced. That the
counters are lock depths follows from the native names and from the readers.

## Camera mode

`_forceCameraTPSMode` (`0x006E6570`) declares one bool. A `Nil` cell leaves the
value false and any other cell is read through `0x0071BA00`. The routine resolves
the world chain and jumps to `0x0075C740` on `W` with the value. A true value
takes the camera object `K` at `V +0x4C4` through `0x004D7320` and calls
`0x0055C560`, which sends the record number `0x2D` with a 4 byte payload holding 1
through `0x004D7980`. That routine adds `0x15` to the record number, so the scene
packet type is `0x42`. A false value takes the object `E` at `V +0x17838`
through `0x004D72F0` and calls `0x00586F20`, which loads the dword at `E +0x7C`,
takes its dword at `+0x4C4` and, when that is nonzero, calls `0x0055F230`. That
routine sends the record number `0x10` with a 4 byte zero payload, scene packet
type `0x25`. That the dword at `E +0x7C` is `V` is `INFERRED` from the shared
`+0x4C4` accessor. The consumers of the two records were not traced.

## Aim and look-at cancellation

`_cancelAimCameraTutorial` and `_cancelLookAtPlayerTutorial` run the prelude and
the name number walk of the [tutorial natives](global-native-contract.md#tutorial-natives).
The callback reads its int, calls `0x0075D120` on the object at `Y +0x110`,
builds the `0x10` byte iterator `0x007176C0` with `ExecuteParameters` `+0x04` and
the int, and walks the node list at `V +0x4E4` through `0x00764150`. The found
identity sits at iterator `+0x0C`.

`_cancelAimCameraTutorial` (`0x006E7050`) then calls three routines and never
reads the found identity. `Z` is the target cursor receiver, the dword at `Y +0x04`.

| Step | Call | Effect |
| --- | --- | --- |
| 1 | `0x0075F070` on `Z` with 0 | Takes the cursor state `S` from `V +0x4C0` through `0x004D7310`, walks the cursor vector at `S +0xA8` and calls `0x00563510` on each non-null cursor with the flag. This is the worker of `_setAllTargetCursorMask`. |
| 2 | `0x0075C720` on `W` | Takes `S` and, when the dword at `S +0xC0` is not `0xC0000000`, calls `0x00561BB0` on `S` with 0. `_aimCameraTutorial` calls the same routine with 1. |
| 3 | `0x0075B700` on `Z` with 0 | Takes `S` and calls `0x00562D30` with the cursor index 0 and a null chara. That is the worker of `_setTargetCharacter`. |

`_cancelLookAtPlayerTutorial` (`0x006E6E90`) calls `0x0075C560` on `W` with the
found identity. That routine resolves the identity through `0x004D9970` without a
null test and calls `0x00589240`, which calls `0x00587EF0` with 0.
`_lookAtPlayerTutorial` reaches `0x00587F80` through `0x00589260`. That the cancel
natives undo the set natives is `INFERRED` from the pairing. The bodies of
`0x00561BB0`, `0x00563510` and `0x00587EF0` were not traced.

## Chocobo camera

`_aimCameraChocobo` (`0x006E7130`) and `_cancelAimCameraChocobo` (`0x006E71F0`)
read one int and build the iterator `0x007178D0` (vftable `0x00FD590C`, RTTI
`s_CharaIterateActorClass`) from `ExecuteParameters` `+0x04` and the int. They run
no prelude. Slot 1 of the iterator, `0x007179A0`, resolves each identity, casts it
to `NpcBase` (type descriptor `0x012709E4`) and accepts a chara whose byte at
`+0x5C` is nonzero. It reads the work value with the key `0x1389` through
`0x00CC7B90` with the default -1 and compares it with the int at iterator `+0x08`.
A match stores the identity at iterator `+0x0C` and stops the walk.

After the walk each callback calls a routine on `W` with the address of the found
identity.

| Native | Routine | Effect |
| --- | --- | --- |
| `_aimCameraChocobo` | `0x0075CDE0` | Takes `E` from `V +0x17838`, calls `0x00586E80` on it with the identity and then `0x004D7890` on it with 0. `0x00586E80` takes the dword at `E +0x7C`, reads its dword at `+0x4C4` and, when it is nonzero, calls `0x0055F2B0`. That sends the record number 9 with a `0x14` byte payload that holds the identity, the dword 2 and floats, then the record number `0x12` with the payload `0x0A`. The scene packet types are `0x1E` and `0x27`. |
| `_cancelAimCameraChocobo` | `0x0075CE10` | Calls `0x00586EC0` on `E`, which jumps to `0x0055F320` and sends the record number `0x12` with the payload `0x0B`, then `0x004D7890` on `E` with 1. The routine does not read the found identity. |

`0x004D7890` stores its argument in the byte at `E +0x90` and builds a message of
type `0x11` for the argument 0 and `0x10` for any other argument through
`0x004EC080`. It hands the message to virtual slot 3 of the object at `E +0x84`.
A walk that finds nothing leaves iterator `+0x0C` at 0, and the aim native then
sends the identity 0. That the aim native points the camera at the actor class is
`INFERRED` from the name. The consumers of the records and the class of `E` were
not traced.

## Waits

`_waitForCharaSchedulerTutorialFinished` (`0x006E6C20`) reads two ints, runs the
prelude and the walk with the first int and calls `0x0075C400` on `W` with the
found identity and the second int. That routine resolves the identity through
`0x004D9970` and stores the chara and the int in a result slot. The callback
allocates `0x0C` bytes, constructs the `s_WaitForCharaSchedulerTutorialFinishedResumeChecker`
(vftable `0x00FD58FC`) with `0x007177B0` and requests the yield. The poll slot
`0x00717880` calls `0x0058AB60` on the chara with the second int and stores the
waiting result `0x0130CECC` for a returned 1 and the done result `0x01377ECC`
otherwise. `0x0058AB60` asks `0x00585800` for a group number from the constant 5
and the int, then `0x00589F60` searches the table of lists at chara `+0x878`, in
groups 1 to `0x19`, for an entry whose dword at `+0x10` equals the int. That the
wait ends when the scheduler entry that `_runCharaSchedulerTutorial` started is
gone is `INFERRED`. A null chara from the walk reaches `0x0058AB60` without a
test.

`_waitForTargetTutorial` (`0x006E5710`) runs the prelude, reads one int and
allocates `0x0C` bytes for a `TargetTutorialResumeChecker` (vftable `0x00FD5350`)
built by `0x00713A50` from the `DesktopWidget` receiver and the int. It stores the
checker pointer at the receiver `+0x6C` and requests the yield. The poll slot
`0x00713AC0` stores the done result when the dword at checker `+0x08` is 0.
`0x00718EF0` clears it. It reads the first dword of the
record at chara `+0x60`, maps -1 to 0 and, when it equals the checker int, clears
the widget `+0x6C`, checker `+0x04` and checker `+0x08`. Its only `rel32` caller,
`0x006FEAF2`, lies in the routine at `0x006FE960`. That routine passes a
`Utf8String` built from the literal `_onTargetChanged` (`0x00FD47D8`) to
`0x00CC7A90`, and its only `rel32` caller is `0x008A3EB3`. That the wait ends
when the player targets the chara with that name number is `INFERRED`. The trampoline
holding `0x008A3EB3` is reached from `LuaActorImpl` vftable slot 25 through `0x0075D750`
(see the [target cursor record](target-cursor-native-contract.md#widget-fields-and-their-writers)).
The callers of that slot were not traced.

`_waitForCameraTutorial` (`0x006E1C50`) takes no argument and runs the prelude.
It calls `0x0075B470` on the dword at `Y +0x08`, which takes `K` from `V +0x4C4`,
stores it in a result slot and calls `0x0055CF00` on `K` with 0. That routine
stores 1 in the byte at `K +0x17D` for an argument of 0. The callback allocates 8
bytes for an `s_CameraTutorialResumeChecker` (vftable `0x00FD538C`) built by
`0x00713E70` and requests the yield. The poll slot `0x00713F30` calls
`0x00758D50`, which calls `0x0055CEE0` on `K` with 0. That routine returns whether
bit 0 of the byte at `K +0x17C` is set. A set bit stores the done result and a
clear bit the waiting result. The writers of the bit and the class of `K` were not
traced.

## Ledger rows

These rows of the unimplemented ledger have a registration, argument list,
return list, receiver check and callback contract:
`_lockCameraControl`, `_unlockCameraControl`, `_isCameraControlEnabled`,
`_isPlayerControlEnabled`, `_isLockonControlEnabled`, `_forceCameraTPSMode`,
`_cancelAimCameraTutorial`, `_cancelLookAtPlayerTutorial`,
`_waitForCharaSchedulerTutorialFinished`, `_aimCameraChocobo`,
`_cancelAimCameraChocobo`, `_waitForTargetTutorial` and
`_waitForCameraTutorial`. A client that implements them still needs the target
cursor and look-at workers behind `0x00561BB0`, `0x00563510` and `0x00587EF0`,
the consumers of the camera records, the writers of the camera tutorial bit at
`K +0x17C` and the engine path that reports the targeted chara to the
`DesktopWidget`.

## Open

- The bodies of `0x00561BB0`, `0x00563510`, `0x00587EF0` and the effects of the
  three camera command objects.
- The consumers of the scene records `9`, `0x10`, `0x12` and `0x2D`, and the
  class of `K` and `E`.
- The writers of the bit at `K +0x17C` and of the byte at `K +0x17D`.
- The engine path behind `0x008A3EB3` and any other writer of checker `+0x08`.
- The scheduler table behind `0x00589F60` and the group number that
  `0x00585800` returns.
- Whether the yield request `0x00CD2860` polls the checker once before it
  suspends.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone x86-32 decode of the file through its section table
and the `rel32` caller scan of `.text` described in the
[binary and method](#binary-and-method) section. With explicit project and JDK
bindings and a new absolute output path, the repository route for function
listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboards and registrars | `0x00754C70,0x00757EA0,0x007328E0,0x00732CD0,0x00732E20,0x00732F70,0x007330C0,0x00735970,0x0073B400,0x0073B6A0,0x0073B940,0x0073BD30,0x0073BE80,0x0073A6E0,0x0073A830` |
| Wrappers | `0x00726B40,0x00726BF0,0x00724CE0,0x00724DB0,0x0071B380,0x0071B460,0x0071B4D0` |
| Player callbacks | `0x006DE800,0x006DE830,0x006DE840,0x006DE850,0x006DE860,0x0071E700,0x00705130,0x00705170,0x006E33C0,0x006E33E0,0x007051B0,0x006E6570` |
| Control counters | `0x0075B260,0x0075B2C0,0x0075B2D0,0x0075B2E0,0x0075B2F0,0x004D7580,0x004DECF0,0x0054B440,0x0054B600,0x0054B610,0x0054B680,0x0054B8C0,0x0054B8D0,0x004D9910,0x00928F90` |
| Camera mode | `0x0075C740,0x0055C560,0x00586F20,0x0055F230,0x004D7980,0x004D7320,0x004D72F0` |
| Aim and look-at cancellation | `0x006E7050,0x006E6E90,0x0075D120,0x007176C0,0x00764150,0x0075F070,0x0075C720,0x0075B700,0x0075C560,0x00589240,0x00587EF0,0x004D7310,0x00562D30,0x00561BB0` |
| Chocobo camera | `0x006E7130,0x006E71F0,0x007178D0,0x007179A0,0x0075CDE0,0x0075CE10,0x00586E80,0x00586EC0,0x0055F2B0,0x0055F320,0x004D7890,0x004EC080` |
| Waits | `0x006E6C20,0x0075C400,0x007177B0,0x00717880,0x00758CE0,0x0058AB60,0x00585800,0x00589F60,0x006E5710,0x00713A50,0x00713AC0,0x00718E90,0x00718EF0,0x006FE960,0x006E1C50,0x0075B470,0x0055CF00,0x00713E70,0x00713F30,0x00758D50,0x0055CEE0` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body is a dependency of this record.
