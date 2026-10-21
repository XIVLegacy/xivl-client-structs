# WorldMaster server-time native contract

[`manifests/world_master_native_call_contract.json`](../manifests/world_master_native_call_contract.json)
records the static Lua contract of `WorldMaster._getServerTime`. For a receiver
accepted as native `WorldMaster`, the call takes no post-receiver arguments
and returns one Lua number. The callback reads the cached dword at
`WorldMaster+0x60`. The return operator interprets that dword as signed
32-bit and converts it to a double for the Lua number.

The clock source, whole-second unit and cache initialization are canonical in
`xivl-decomp:docs/actor/cast-timing-clock.md`, Native clock model. This record
establishes the Lua receiver, argument list and return conversion.

## Binary and method

Input: retail `ffxivgame.exe`, build `2012.09.19.0001`, PE32 x86, image base
`0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Addresses are absolute VAs.

The executable's byte size and SHA-256 were verified. The analyzed program's
summary matched its name, image base and x86 little-endian 32-bit language.
The observations used bounded ghidra-cli decompilation and instruction listings.
The decisive instruction listings used explicit project and program selection.
The two vtable cells below were mapped through the authenticated PE's section
table. The current Ghidra FileBytes and loaded-image contents were not freshly
compared with that executable.

## Registration and receiver

| Observation | Exact locator |
| --- | --- |
| One builtin index-0 int return operator | Registrar call `0x007528E0` to `FUN_00728C20`, registry read and append at `0x00728C93..0x00728CA7` |
| Empty argument list | Registrar call `0x007528F7` to `FUN_0072B440`, empty builder `0x0072B476..0x0072B4AB` |
| Callback and adjustment | `0x007528D7` loads callback `0x007079A0`, wrapper call `0x0075291A` passes adjustment 0 |
| Exact Lua name | `_getServerTime` literal `0x00FD8254`, reference `0x00752989`, installation through `FUN_00CCCAD0` at `0x007529B9` |
| List ownership | `FUN_00726CA0` forwards to `FUN_00724E80`, argument copy at `0x00724EB7` targets functor `+0x14`, return copy at `0x00724ECC` targets `+0x24` |
| Holder identity | `FUN_0071AE00` installs `MemberFunctionHolder<WorldMaster, void (WorldMaster::*)(ExecuteParameters const&) const>` table `0x00FD5B70` at `0x0071AE3D` |
| Receiver adapter | Table cell `0x00FD5B74` selects `FUN_0071AE70` |

`FUN_00D19B70` obtains the Lua receiver from stack index 1 through
`FUN_00CD77D0` at `0x00D19BC0`. Its holder call is at `0x00D19D3B`.
`FUN_0071AE70` passes the receiver to `FUN_009DA6CC` with LuaControl
TypeDescriptor `0x01270B4C` and WorldMaster TypeDescriptor `0x012C1328`
at `0x0071AE75..0x0071AE86`. On a successful cast it adds the stored
adjustment and calls the saved callback with the native object in ECX
at `0x0071AE98..0x0071AEA5`. A null cast returns false, and the generic
invocation raises a Lua error on a false holder result.

The [common argument marshaller](widget-native-call-contract.md#argument-marshalling)
starts post-receiver arguments at Lua stack index 2 and raises a Lua error
for values beyond the declared list. The WorldMaster path calls that same
`FUN_00D19A20` routine at `0x00D19C16`. The accepted call therefore has one
receiver and zero post-receiver arguments. An extra nil argument also exceeds
the empty list. The callback performs no post-receiver argument access or
coercion.

## Return conversion

Callback instructions `0x007079A0..0x007079B5` pass the address of
`WorldMaster+0x60` to `FUN_00584F70`, using `[ExecuteParameters+0x1C]`
as the return-container receiver. They contain one unconditional builder
call and no yield request.

`FUN_00584F70` constructs a temporary value through `FUN_00583D90` at
`0x00584FB6` and appends through `FUN_00584EE0` at `0x00584FCB`.
`FUN_00583D90` copies four raw bytes at `0x00583DFA..0x00583DFC` and
writes internal tag 0 at `0x00583E09`. The callback preserves the cached
dword without combining the millisecond component.

The immediate-return path calls `FUN_00D196F0` at `0x00D19F42`.
That helper walks the return list and calls `FUN_00CF9630` at
`0x00D19771`. The latter calls operator slot `+8` at `0x00CF97A8`.
The int registry constructor installs table `0x0110DF38` at `0x00CC9DC9`,
and its slot cell `0x0110DF40` contains `0x00CF9940`.

`FUN_00CF9940` accepts internal tag 0, uses signed `FILD dword` at
`0x00CF99FA`, stores the result as double at `0x00CF9A03`, and calls
`FUN_00CF3300` at `0x00CF9A07`. That helper passes the double to
`FUN_00DCE170` at `0x00CF330F`. The final number/tag-3 stack write is
recorded at `0x00DCE17B..0x00DCE17D` in
[Handler arguments](native-input-ui-boundaries.md#handler-arguments).
The int operator increments the consumed-value index at `0x00CF9A0C`
and returns push count 1 at `0x00CF9A21`. The unconditional one-value
callback and single return operator establish exactly one Lua number for
this successful immediate invocation.

For raw dword `u`, the resulting number is `u` when `u < 0x80000000` and
`u - 0x100000000` otherwise. Every signed 32-bit value is exactly
representable in that double conversion. This signedness consequence is
static evidence.

## Reproduction and limits

Use `ghidra decompile 0xADDRESS --with-params` and
`ghidra disasm 0xADDRESS --instructions N` with explicit project and program
selection. Inspect the function spans named above. Instructions beyond a
function's return supply no claim here. Callback `0x007079A0` has no declared
function entry in the analyzed program. Its full instruction span supplies
the callback evidence.

These are static client observations. No live Lua call or retail-client walk
was performed. The contract does not establish packet timing, clock rate,
host clock source, host initialization or synchronization policy. Its scope
excludes the `_inl` descriptor to `_cpp` name mapping and the classification
of Lua values that fail the initial receiver lookup. No decompiled body or
ignored export is a public evidence dependency.
