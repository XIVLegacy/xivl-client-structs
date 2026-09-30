# Actor vtable structural entries

These function addresses have structural catalog identities. Their instructions
and vtable pointers establish the observations below, without establishing Lua
API names, complete prototypes, or runtime behavior.

## Binary and method

The input is retail 1.23b `ffxivgame.exe`, size 15,996,808 bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
with PE image base `0x00400000`. All function and vtable addresses below are
VAs. Subtract the image base for RVAs.

Ghidra 12.1 produced exact-entry decompilations and defined instruction listings
through the committed `ghidra/DumpVAs.java` and
`ghidra/DumpFunctionListing.java`, with `-noanalysis` and `-ReadOnly`.
Each requested VA had exactly one successful decompilation section whose
`Entry` matched the target. The listing completed with
`COMPLETE: requested=6 completed=6`. The source executable's size and SHA-256
matched the identity above. Instruction anchors and the listed vtable pointers
were also checked against that PE, using its section table to translate RVAs
to file offsets. No decompiled bodies or raw analysis reports are retained here.

With the Ghidra dispatcher environment configured and an explicit new output
directory in `XIVL_EVIDENCE_OUT`, reproduce the address observations with:

```powershell
$targets = '0x005E36E0,0x006DC350,0x006DC360,0x006DE9F0,0x0071E750,0x00776340'
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -Out (Join-Path $env:XIVL_EVIDENCE_OUT 'actor-vtable-functions.txt') `
    -ScriptEnv @{ XIVL_TARGET_VAS = $targets } -ScriptPath @('ghidra')
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -Out (Join-Path $env:XIVL_EVIDENCE_OUT 'actor-vtable-listings.txt') `
    -ScriptEnv @{ XIVL_TARGET_VAS = $targets } -ScriptPath @('ghidra')
```

The vtable relationship source is
`xivl-decomp:config/ffxivgame.vtable_slots.jsonl`, revision
`5056cb87a9f741038e848ff94a6b8efca53279ec`. Its metadata pins the same
binary and names Ghidra 12.1 `tools/ghidra_scripts/DumpRtti.java` as producer.
Its slot runs stop at the first null or non-executable pointer, which does not
prove semantic slot boundaries. The table below retains only the needed rows.
Class names abbreviate `Application::Lua::Script::Client::Control::`.

| Class | Primary vtable VA |
| --- | --- |
| CharaBase | `0x00FD5CAC` |
| PlayerBase | `0x00FD5E04` |
| NpcBase | `0x00FD647C` |
| MyPlayer | `0x00FD785C` |

Read a slot pointer at `vtable VA + 4 * slot`. These selected pointers matched
the pinned PE. A shared pointer does not imply identical class semantics.

## Observations and dispositions

All six addresses were absent from `manifests/symbols.json` at revision
`683075b60c7fb46925b2df9f4efef950c8ae334b` and are promoted as `function`
entries with `structural` confidence.
Their `FUN_` identities and empty `luaApiRefs` preserve the naming boundary.

| Function VA | Selected vtable locators | Instruction observation | Evidence limit |
| --- | --- | --- | --- |
| `0x005E36E0` | CharaBase, PlayerBase, NpcBase, MyPlayer slot 20, byte offset `0x50`; source lines 26889, 26970, 27218, 27344 | Six-byte body. Sets EAX to 8 at the entry and returns at `0x005E36E5`. | The meaning of 8 is unresolved. |
| `0x006DC350` | CharaBase and PlayerBase slot 35, byte offset `0x8C`; source lines 26904, 26985 | Fifteen-byte body. Pushes zero and the incoming ECX value, loads ECX from the stack, and calls `0x00CC73E0` at `0x006DC357`. Returns with four-byte stack cleanup at `0x006DC35C`. | The callee's purpose and full parameter types are unresolved. |
| `0x006DC360` | CharaBase, PlayerBase, NpcBase, MyPlayer slot 26, byte offset `0x68`; source lines 26895, 26976, 27224, 27350 | Fifteen-byte body. Loads a destination pointer from `[ESP+0x4]`, reads the byte at `0x012BFB64`, and stores it through that pointer at `0x006DC36A`. Returns with eight-byte stack cleanup at `0x006DC36C`. | This is an output-pointer store, not evidence for a field on the actor object. The global's meaning and complete prototype are unresolved. |
| `0x006DE9F0` | PlayerBase slot 67, byte offset `0x10C`; source line 27017 | Three-byte return-only stub with four-byte stack cleanup at the entry. | No Lua name is established. No return value is explicitly assigned. |
| `0x0071E750` | PlayerBase and MyPlayer slot 25, byte offset `0x64`; source lines 26975, 27349 | Seven-byte body. Reads one byte from `[ECX+0xEC]` into AL at the entry and returns at `0x0071E756`. | The field's meaning and complete prototype are unresolved. |
| `0x00776340` | PlayerBase slots 89 and 90, byte offsets `0x164` and `0x168`, and MyPlayer slot 2, byte offset `0x8`; source lines 27039, 27040, 27326 | Three-byte return-only stub with four-byte stack cleanup at the entry. | Shared by multiple slots and classes. No single API identity or defined return value is established. |

## N-API and snapshot limits

In [the enhanced N-API snapshot](../../manifests/napi_field_access_enhanced.json),
joining the selected class and slot through `directVtableSlots / 4` supplies no
Lua-name match for the first five addresses. This is a bounded absence in that
snapshot, not proof that no Lua-facing route exists. It has no MyPlayer class
inventory. No Lua name is assigned to PlayerBase slot 67.

The same snapshot's PlayerBase rows for `_countEnableEntrustItem`,
`_getEnableEntrustItem`, `_countEntrustItem`, and `_getEntrustItem` all have
`implVa: 0x00776340` and empty `directVtableSlots`.
[The resolved-vtable snapshot](../../manifests/vtable_resolved_evidence.json)
also lists `perFn[fnVa=0x00776340]` through multiple CharaBase, PlayerBase,
and NpcBase offsets. Its historical `status: no_function` records an analysis
state, not absence of executable code: the current exact-entry exports
succeeded. Its empty access arrays do not establish API-specific behavior.

Those snapshots establish catalog relationships at their retained confidence.
The current instruction evidence establishes a shared return-only body. It
does not select one of the N-API names as the function's identity, determine
runtime dispatch, or establish wire behavior. No direct-call absence is
interpreted as absence of virtual callers.
