# Retail 1.23b login state boundaries

Launcher login checks must distinguish UI labels, native operation results,
and the identity of a player ready in the world. A menu label, loading overlay,
or arbitrary actor does not establish login success. The native checks
described below support only the stated observations.

## Binary and method

The observations target `ffxivgame.exe`, retail 1.23b, build
`2012.09.19.0001`, image base `0x00400000`, file size `15996808`, and SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Both input copies were independently checked against this identity. Function
addresses below are absolute virtual addresses.

The reproducible static recipe is:

1. From the repository root, set the four `BCS_*` tool environment variables
   required by [the headless Ghidra setup](../tools/README.md#headless-ghidra),
   then run one read-only export for each target list:

   ```powershell
   & tools\ghidra\run-headless.ps1 -Script DumpVAs.java -ReadOnly `
       -Out '<ignored-output>\dump.txt' `
       -ScriptEnv @{ XIVL_TARGET_VAS = '0x006B0220,0x00DAA740' } `
       -ScriptPath @('ghidra')
   ```

2. Inspect the resulting instructions with portable `llvm-objdump` 22.1.4,
   using the same image and the stated absolute address ranges.
3. For Ghidra-backed facts, record a fact only when the instruction and the
   matching DumpVAs entry agree. The producing tool baseline was
   `51be90574ef0e76da4fa432b8e095c5fe9fc574e` with Ghidra 12.1.3. The
   follow-up scripts were read at checkout
   `xivl-client-structs@08de0f7428a133a689627ac0cbf60d97daed2a71`:
   `run-headless.ps1` and `FindReferences.java` at
   `a41f9d1be89c2752ef147c37f864e4f183717f8a`, `DumpVAs.java` and
   `FindFieldRefs.java` at `5213a74289d964c60aea1856b3a7082059f99a7b`,
   `DumpFunctionListing.java` at
   `6629ecba86714f783a510200c798ddeee29b4f96`, and
   `VerifyProgramFileBytes.java` at
   `dc4fdd98950337347be5f90885b8406161c19a0e`. The portable LLVM tool
   reports version 22.1.4. The fresh PE check again reported size `15996808`
   and SHA-256
   `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.

The current follow-up request lists are reproducible from these tracked
scripts: `ghidra/DumpFunctionListing.java`, `ghidra/DumpVAs.java`,
`ghidra/FindReferences.java`, `ghidra/FindFieldRefs.java`,
`ghidra/VerifyProgramFileBytes.java`, and
`tools/ghidra/run-headless.ps1`.

- `DumpFunctionListing.java` exact starts:

  ```text
  0x006B0220,0x00DAA740,0x00DA9880,0x00DA9EC0,0x00DAA070,0x00DAA950,
  0x00DAA9F0,0x00DA76B0,0x00DA5030,0x00DA5110,0x00DA64B0,0x00DAD7B0,
  0x004E0690,0x006B3D40,0x0088C810,0x0088B070,0x008838A0,0x00DA60C0,
  0x00DA4770,0x00DA4AE0,0x00DA5A00,0x00DA4660,0x00DA4390,0x00DA4370,
  0x00DA2BE0,0x00DA4840,0x00DA5C50,0x00DA5D60,0x00DA7190,0x00DA70A0,
  0x00DA79D0,0x00DAAC30,0x00DA8680,0x00891A00,0x00DA7510,0x00DA7220
  ```

- `DumpVAs.java` batches:

  ```text
  0x006B0220,0x00DA5C50,0x00DA5D60,0x00DA7190,0x00DA70A0,0x00DA76B0,
  0x00DA79D0,0x00DAAC30,0x00DA64B0,0x00DA5110,0x00DAA950,0x00DAA740,
  0x00DA8680

  0x00DBFD10,0x00DADCC0,0x00DE7B10,0x00DE9550,0x00DE9610

  0x00DA60C0,0x00DA5030,0x00DA4AE0,0x00DA5A00,0x00DA4660,0x00DA4390,
  0x00DA4370,0x00DA2BE0,0x00DA4840,0x00DA7510,0x00DA7220

  0x004DF0A0,0x00DAA9D0,0x004DFB20,0x004DFBA0,0x004DFCD0,0x004DFF10,
  0x004E0690,0x004E0890,0x004E09F0

  0x00DA9880,0x00DA9EC0,0x00DA4F80,0x00DA4660,0x00DA5190,0x00DA5300,
  0x00DA54D0,0x00DA55C0,0x00DA58F0,0x00DA5FD0,0x00DA60C0
  ```

- `FindReferences.java` batches:

  ```text
  0x006B0220,0x00DA5C50,0x00DA5D60,0x00DA7190,0x00DA70A0,0x00DA76B0,
  0x00DA79D0,0x00DAAC30,0x00DA64B0,0x00DA5110,0x00DAA950,0x00DAA740

  0x01128318,0x00DA64B0,0x00DA5110,0x00DAA950,0x00DAA9D0

  0x0088C810,0x0088B070,0x006B0220,0x006B5260,0x00DA76B0,
  0x00DA79D0,0x00DAAC30
  ```

- `FindFieldRefs.java` offset queries:

  ```text
  roster/world: 0x1d0,0x1d4,0x1d8,0x200,0x220,0x224,0x278,0x27a,0x27c
  operation:    0x8,0x14,0x18,0x34,0x8c,0x1a0,0x1a8
  ```

- `VerifyProgramFileBytes.java` uses the executable identity stated above and
  verifies original, modified, and mapped file-backed ranges.

The fresh follow-up Ghidra exports completed with these checks: the function
listing covered 36 exact function starts (`requested=36 completed=36`);
DumpVAs reported `sections=13 failures=0`, `sections=5 failures=0`,
`sections=11 failures=0`, `sections=9 failures=0`, and
`sections=11 failures=0`; FindReferences reported
`COMPLETE: FindReferences targets=12 references=18`,
`COMPLETE: FindReferences targets=5 references=6`, and
`COMPLETE: FindReferences targets=7 references=15`; FindFieldRefs scanned 3,174,303 instructions
for both offset sets and reported 1,652 hits in 733 functions for the
selected roster/world offsets and 73,849 hits in 22,384 functions for the
operation offsets. VerifyProgramFileBytes completed with
`COMPLETE: program-file-bytes-v1`. Each DumpVAs batch had one `Name` and one
decompilation section per entry, with zero `ERROR` or `DECOMP FAILED` entries.
These checks are static only; no runtime or connected-retail result is
implied.

The continuation also used fresh read-only `llvm-objdump` 22.1.4 exports and
direct-call scans on the same image. The operation-step, roster-consumer,
vector-helper, response, and bootup locators below are independently checked
against the stated file identity. These LLVM exports extend the Ghidra-backed
observations but do not assign names to unresolved indirect calls. The
GameLogin constructor join through `FUN_00DAD770` is an LLVM-only continuation
with field-reference corroboration; its instruction join is promoted below
without assigning a semantic name to that helper.

Evidence strength is explicit: direct Ghidra facts have instruction locators
and a matching DumpVAs entry, while the explicitly marked DAD770 continuation
is LLVM-only; projection facts describe mechanical parser behavior;
RTTI and event names are locator hints only; unresolved claims name the direct
caller or reader set that was inspected.

The read-only `tools/ghidra/export-references.ps1` wrapper also completed an
exact-string run for `OnSuccessfulLobbyLogin`, `NowLoading`, `Continue`,
`SelectCharacter`, and `ZoneLogin`: 28,414 defined strings, five queries, three
matches, two recorded references, and a `COMPLETE` marker. The only login
string reference was `OnSuccessfulLobbyLogin` at `0x00DA9FAA`, owned by
`0x00DA9EC0`; `NowLoading`, `SelectCharacter`, and `ZoneLogin` had no defined
native string match. This limits name-based native evidence and does not rule
out computed, indirect, dynamic, or script-side relationships.

## Native owners and readers

| Boundary | Native owner or reader | Supported observation | Operation boundary and limit |
| --- | --- | --- | --- |
| Title and start | `TitlePhase` RTTI/vftables `0x0105339C` and `0x010533AC`; `TitlePhase` and `InstallTitleMenu` event types | The title classes and routed event types exist in this image | RTTI and event names expose no title-visible flag, transition counter, or start operation. A title event is not a ready predicate. |
| Bootup owner | `BootupManager` vtable `0x00FD25E0`, slot 2 -> `0x006B0220` | Slot 2 is a native driver with a raw selector at `B+0x44` (`param_1[0x11]`) and counters at `B+0x1B78` and `B+0x1B7C` (`param_1[0x6DE]` and `[0x6DF]`) | These are switch and substate fields, not public UI labels. At `0x006B0D55`, one selector-10 path tests nested bytes at `+0x68/+0x69` and dispatches `0x004DFDF0`; that helper emits local operation state 3 through `0x00DA60C0` only after `0x00DA4660` accepts nested state 3, 4, or 5. |
| Service request | `ServiceLoginOperation::vtable[0]`, `0x00DAA070` | Allocates c2s opcode `0x0003`, size `0x20`, copies the request fields, writes expected s2c `0x000D` on the successful path, and returns success | The exact ABI is `ECX=O`, original stack arg 1 `P` is read at `0x00DAA0A7`, and original stack arg 2 `E` is the expected-opcode pointer. The success path stores `*E=0x000D` at `0x00DAA12E-0x00DAA136` and sets `AL=1` at `0x00DAA149`. Failure `AL=0` is set at `0x00DAA16D` without this function initializing `*E`; the two exits use `RET 8` at `0x00DAA15D` and `0x00DAA181`. This is a send boundary, not proof that a roster is loaded. |
| Roster response | `ServiceLoginOperation::vtable[1]`, `FUN_00DAA9F0`; ordinary parser callsite `0x00DAAA7D` | s2c `0x000D` reaches the `FUN_00DA76B0` roster parser with `packet+0x10` | At `0x00DAAA79`, the receiver loads `C=[O+0x08]` into `ECX` and calls `FUN_00DA76B0` at callsite `0x00DAAA7D`. On a false parser result, `0x00DAAA86-0x00DAAA8D` passes `ECX=C` and original stack arg 1 `[O+0x34]` to `0x00DA5030`; the receiver returns `AL=0` and `RET 4`. The callback is a failure boundary, not a populated-roster proof. |
| Roster projection | `0x00DA76B0`, with context `C=[O+0x08]` | The parser owns its vector at `C+0x1D0`, with begin/end at `C+0x1D4` and `C+0x1D8`; it reads the body count and inserts records in arrival order | `C` is the parser context, not `O`. The route proves projection mechanics and vector order only; it does not prove a full identity, selected record, or generation. |
| Lobby operation request | `0x00DA9880` | The nested state at `C+0x0C`, `state+4`, selects c2s `0x01F5`, `0x0005`, `0x0006`, or `0x01F6`; expected opcodes are `0x01F5` or `0x000C`, and the request sets nested `+0x8C=4` | This is a native request state machine with no statically resolved title-button caller. Its state values are operation data, not UI labels. |
| Lobby admission response | `0x00DA9EC0` | For s2c `0x000C`, `FUN_00DA4B80(packet+0x10)` returns the parser result. For s2c `0x01F5`, a nonzero ticket at `packet+0x14` and nonempty frontend at `packet+0x1C` reach `FUN_00DA4F80(0)` after the `OnSuccessfulLobbyLogin` log | The ticket/frontend check is an auth or lobby admission edge. It returns `AL=0` after the callback and does not establish world readiness. Other opcodes write `O+0x10=4` and return false. |
| Character selection request | `GameLoginOperation::vtable[0]`, `0x00DAA740` | Allocates c2s `0x0004`, size `0x28`, copies `O+0x0C`, and reads the selected-record candidate described below; it writes expected s2c `0x000F` only on the successful path | The exact ABI is `ECX=O`, original stack arg 1 `P` is read at `0x00DAA777`, and original stack arg 2 `E` is the expected-opcode pointer. The success path stores `*E=0x000F` at `0x00DAA806-0x00DAA80E` and sets `AL=1` at `0x00DAA821`. Failure `AL=0` is set at `0x00DAA845` without this function initializing `*E`; the two exits use `RET 8` at `0x00DAA835` and `0x00DAA859`. The fresh constructor join proves `O+0x08=C` for this GameLogin operation; the normal UI/input admission source remains unresolved. |
| Character selection response | `GameLoginOperation::vtable[1]`, `0x00DAA950` | s2c `0x000F` adds `packet+0x10` at `0x00DAA96C` and reaches `0x00DA64B0`; a nonzero parser result returns true | On false, `0x00DAA9B3-0x00DAA9BA` passes `ECX=C=[O+0x08]` and original stack arg 1 `[O+0x34]` to `0x00DA5110`, then returns `AL=0`. The response body is `packet+0x10`; a nonzero parser result is a lobby response result, not a world-ready identity result. |
| Separate CharaMake path | `CharaMakeOperation::vtable[0]`, `0x00DAA190`; sequence-gated response `0x00DAD7B0` | A separate step emits c2s `0x000F` and expects s2c `0x0010`; the ack compares response context `+0x10` with operation `+0x0C` before dispatching the operation callback | The reused wire opcode does not prove an ordinary roster select or confirm. The ack's operation state write and callback are a separate path. |
| Roster vector consumers | `FUN_006B3D40` and its analyzed-database direct-caller set `0x00889250`, `0x0088C4C0`, `0x0088BD50`, `0x00884CB0`, `0x006AD530`, `0x006B0220`, `0x0088B880`; ordinary response `FUN_00DAA9F0` calls `FUN_00DA76B0` at `0x00DAAA7D`, while `FUN_00DAAC30` calls `FUN_00DA79D0` on character-modify branches | The database reader set indexes the `0x2E0` vector and reads or copies entry fields such as `+0x04`, `+0x08`, `+0x10`, and `+0x40`; the fresh direct-call scan found only the ordinary parser callsite `0x00DAAA7D` and character-modify branches at `0x00DAAD8B`, `0x00DAAE16`, `0x00DAAEA1`, `0x00DAAF2C`, and `0x00DAAFB7` | The character-modify handlers do not establish an ordinary `0x000D` full-identity reader. No direct call to `0x00DAA740` was traced. Virtual or dynamic UI admission edges remain possible, so the normal selection source and admission caller remain unresolved. |
| Loading form | `NowLoading` RTTI and tracked Lua metadata names | The native RTTI type and script metadata expose form or API identifiers only; no direct ready reader is qualified in this slice | Showing or dismissing the form is not a native loading or ready predicate. |

Before the selector switch, a non-null queue node at `B+0x50` supplies the
raw selector to `B+0x44`, a peer value to `B+0x4C`, two dwords to
`B+0x1B78` and `B+0x1B7C`, and five qwords to `B+0x1B80` through `B+0x1BA0`
at `0x006B02AC-0x006B0328`; the node is released at
`0x006B0336-0x006B0352`. On the selector-1 jump-table path, the creation
branch at `0x006B07B0-0x006B0876` allocates `0x3C0`, `0x3D0`, and `0x860`
byte objects, invokes the `AccountSelectionPhase` and
`CharacterSelectionPhase` constructors (`0x0088C810` at
`0x006B082A`, `0x0088B070` at `0x006B0866`), and increments `B+0x1B78` at
`0x006B0876`. This closes queue consumption and one phase-creation edge only;
it does not map the selector to title, start, waiting, confirmation, or error
semantics, nor does it identify an invalidation callback.

The same fresh driver export shows the selector switch at
`0x006B0683-0x006B0692` dispatching values `1..0x3A`; the selector-1 branch
first initializes child objects and invokes their vtable `+0x24` methods at
`0x006B06B5-0x006B072C`, then creates the phase objects above when its counter
is zero. Several later selector branches explicitly reset `B+0x44`,
`B+0x1B78`, and `B+0x1B7C` before invoking a stored callback: the reset and
indirect-call edges are at `0x006B0B57-0x006B0B6A`,
`0x006B0C26-0x006B0C3E`, `0x006B0E16-0x006B0E37`, and
`0x006B0F42-0x006B0F61`. These are instruction-backed phase-reset and
callback boundaries, but their callback targets are computed from queue data;
the export does not assign them to a named phase, error, or cancellation
owner.

The expected-opcode outputs are both 32-bit dword stores on the success path:
the decoded `MOV dword ptr [EDX],0xD` at `0x00DAA136` writes `*E=0x0000000D`,
and decoded `MOV dword ptr [EAX],0xF` at `0x00DAA80E` writes `*E=0x0000000F`.
Each failure path returns `AL=0` without this function initializing `*E`.

The RTTI index also identifies `CharacterSelectionPhase`,
`AccountSelectionPhase`, `Waiting`, `BootupDialog`, and
`RaptureLobbyCallback`. Those type identities locate possible owners but do not
provide a field that distinguishes title, roster loading, populated roster,
selection, confirmation, world loading, world ready, or disconnect. Type names
remain UI or class labels. Parser returns, callback writes, and `O+0x10=4`
remain native operation observations.

At verified sibling revision `xivl-client-scripts@aeef43f9721b9b011cefe8bad5a88e6784263937`,
the tracked sidecar
`xivl-client-scripts:lua/scripts/command/system/logineventcommand.calls.json:1`
identifies `LoginEventCommand`; its API rows record identifier locations for
`_fadeIn` at `:19`, `_fadeInAfterWarp` at `:22`, `_lockPlayerControl` at `:32`,
`_runCharaScheduler` at `:35`, `_unlockPlayerControl` at `:38`, and `_wait` at
`:41`. The source manifest
`xivl-client-scripts:manifests/scripts.json:7503` pins the decoded source to
203 lines and SHA-256
`07340E0EDF4669E3842B7843EEDA59DBA314CD016B9E3B9476759E1C3EB13A75`.
The tracked corpus contract at `xivl-client-scripts:lua/README.md:11` and
`:34` says these sidecars record identifier references, not script statements,
guaranteed invocations, or runtime semantics. The
producing `lua_corpus.py annotate` step is specified at
`xivl-client-scripts:lua/README.md:66`; this is metadata provenance, not a
source-body or runtime trace. The
generated index row
`xivl-client-scripts:lua/napi_index.json:13698` similarly records the generic
`_fadeInNowLoadingForNoticeEventJustInArea` API with 16 indexed callsites at
`:13709`; none of these metadata rows exposes a selected identity, native ready
state, or disconnect/error owner.

## Roster ownership, count, and identity limits

The mechanical projection is documented in
[`character-list-record.md`](../structs/ffxiv/client/network/character-list-record.md)
and
[`lobby_character_list_projection.json`](../manifests/lobby_character_list_projection.json).
The parser reads the count byte at `body+0x09` and inserts new records in
arrival order. Its vector count is the byte span from `C+0x1D4` to `C+0x1D8`
divided by `0x2E0`, available to an observer that has already qualified the
owner thread and timing. A clear flag can empty the vector before processing;
zero count, cleared, and not-yet-received therefore remain distinct runtime
questions.

The route proves only these roster keys:

- `record+0x14` is copied to slot `+0x04` and compared by
  `FUN_00DA9550` with `+0x04` of a separate `0x30`-stride operation record.
- The low six bits of `record+0x18` are the lookup key; upper bits can cause
  slot key bytes to be masked with `0x3F`.
- `record+0x50` is an unbounded NUL-terminated append source for slot `+0x40`
  on a repeated key.
- Other copied bytes stay opaque in this route. No stable character ID, full
  name, world, restriction, account, or selection field is proven by the
  `0x000D` reader.

The separate character-modify response path joins `body+0x10` to a slot first
dword, copies 32 bytes from `body+0x20` to slot `+0x10` at
`0x00DA804B-0x00DA805A`, and passes the pointer at `body+0x40` to the
`MAKECHR[wld]` logger at `0x00DA7C3F-0x00DA7C56`. This qualifies a rename
field and a world-name logging argument in that response path; it does not
retroactively assign those meanings to the opaque `0x000D` projection or prove
that either field is a complete roster identity.

Fresh LLVM direct-call scanning found one direct caller of `FUN_00DA76B0`,
`0x00DAAA7D`, and five direct callers of `FUN_00DA79D0`, at
`0x00DAAD8B`, `0x00DAAE16`, `0x00DAAEA1`, `0x00DAAF2C`, and
`0x00DAAFB7`. The latter five are branches of `FUN_00DAAC30` for
character-modify response commands, not readers of the ordinary s2c `0x000D`
roster. `FUN_00DA79D0` walks `C+0x1D4..C+0x1D8` with `0x2E0` stride and, on
a matching response key, copies response `body+0x20` to slot `+0x10` and
`body+0x19` to slot `+0x09` at `0x00DA7FE2-0x00DA8074`; these fields are
qualified only in that character-modify path. For the character-modify `0x10`
case, `FUN_00DAAC30` passes `C+0x1D0` and `C+0x200` through callback vtable
slot `+0x48` at `0x00DAACD5-0x00DAACFF`. The ordinary `0x000D` path has no
fresh direct full-identity reader in this slice.

The vector mutation owner is also bounded. When `body+0x08` has no masked
bits, `FUN_00DA76B0` passes the existing `C+0x1D0` range to
`FUN_00891A00` at `0x00DA771D-0x00DA7728`; that helper erases and destroys
each entry through `FUN_006B4B60`, then updates the vector end at
`0x00891A6B`. It does not free the vector backing or update the begin pointer;
the stores at `0x00891A74-0x00891A77` return iterator output. The body-count
loop begins at `0x00DA7731-0x00DA7740`.
`FUN_00DA7220` also frees and zeroes that vector during context destruction at
`0x00DA736F-0x00DA73B0`, while `FUN_00DA7510` initializes
`C+0x1D4`/`C+0x1D8` to zero at `0x00DA7604-0x00DA7610`. These are
lifecycle and clear boundaries; they do not prove a generation or owner
thread.

Consequences for an autologin observer are:

- A copied vector is only a candidate snapshot. Static inspection does not
  prove owner-thread coherence, a generation value, or a mutation barrier.
- Exact-name uniqueness cannot be proved from this native snapshot. A stable
  native ID is preferred when a separate reader resolves one; otherwise a
  launcher must require a separate uniqueness observation.
- Restrictions and unavailable slots have no instruction-backed field in this
  route. Do not infer them from position, copied bytes, or upper key bits.
- The native account or session object is separate from a launcher username.
  No username-to-roster binding occurs in this chain.

## Request and response fragments

The static result is a set of request and response fragments, rather than a
proven normal continue/select/confirm chain:

1. `0x00DAA070` emits c2s `0x0003` and supplies expected s2c `0x000D`.
2. `0x00DAA9F0` dispatches s2c `0x000D` into `0x00DA76B0`, or to
   `0x00DA5030` on the parser-false path.
3. `0x00DA9880` emits one of the lobby state-machine requests, and
   `0x00DA9EC0` exposes the ticket/frontend admission edge.
4. `0x00DAA740` emits c2s `0x0004` and supplies expected s2c `0x000F`.
5. `0x00DAA950` dispatches s2c `0x000F` into `0x00DA64B0`, or to
   `0x00DA5110` on the parser-false path.

For the selection request, whole-pointer notation is required:

```text
R = *(*(O + 0x08) + 0x14)
payload dword = *(R + 0x0C)
payload byte  = *(u8 *)(R + 0x08)
```

The reads occur at `0x00DAA7A2-0x00DAA7A5` and
`0x00DAA7C0-0x00DAA7C6`. They prove an indirect selected-record input to the
packet builder. `R+0x0C` remains an untyped protocol value, and the normal UI
admission source is unresolved. Fresh LLVM tracing resolves the constructed
GameLogin owner flow: `FUN_004E0890` loads its receiver from `[ESI+0x240]` at
`0x004E0964-0x004E096A` and calls `FUN_00DA7190` at `0x004E0976`; that
function calls `FUN_00DA5D60` with the same receiver. `FUN_00DA5D60` builds
the Init/Lobby/Service/GameLogin step sequence and passes its `this` value as
the explicit owner to the first step's slot-22 call at
`0x00DA5F95-0x00DA5FA0`; the GameLogin step's slot-22 wrapper at
`0x00DA70A0` forwards that explicit owner to `FUN_00DA5C50` at
`0x00DA70B2-0x00DA70C7`. `FUN_00DA5C50` gates nested state, increments
`this+0x18`, releases the old `this+0x14` object through its vtable slot 0
with argument 1, clears the field at `0x00DA5CB7-0x00DA5CC3`, and replaces it
from an incoming object's first dword at `0x00DA5CC8-0x00DA5CCE`. Its
constructor continuation pushes that same ESI receiver as the first stack
argument to `FUN_00DAD770` at
`0x00DA5CF8-0x00DA5CFB`; the constructor stores it at the new operation's
`+0x08` at `0x00DAD787`, and `0x00DA5D00` installs vtable `0x01127FEC`, whose
slot 0 is `FUN_00DAA740`. Therefore this constructed GameLogin operation
proves `C=[O+0x08]`, and `0x00DA5CCE` is the direct C+0x14 replacement
writer. The join does not identify the normal UI/input source, validation,
owner thread or generation, or cancellation.

The smallest typed native candidate is therefore an observation boundary:

| Candidate | Owner and validation | Result | Lifetime and staleness limit |
| --- | --- | --- | --- |
| Service send | `O` is the operation; `P` and writable `uint32_t *E` are caller arguments. The owner thread and generation are unresolved. | `AL=1` writes `*E=0x000D`; `AL=0` leaves `*E` unwritten by this function; both exits use `RET 8`; response parser or `0x00DA5030` supplies the next observation | Do not retain `P`, vector pointers, or callback pointers across a generation change. |
| Game send | The constructed operation has `O+0x08=C`; `R=*(C+0x14)` is loaded by the builder; `P` and writable `uint32_t *E` are caller arguments. The normal UI/input source and validation are unresolved. | `AL=1` writes `*E=0x000F`; `AL=0` leaves `*E` unwritten by this function; both exits use `RET 8`; response parser or `0x00DA5110` supplies the next observation | The selected-record pointer and parser output can be replaced or invalidated asynchronously; copy only after a qualified owner boundary and reacquire after invalidation. |
| Nested operation gate | `FUN_00DA4660` accepts only nested `C+0x8C` values 3, 4, or 5; `FUN_004DFDF0` builds local state 3 before `FUN_00DA60C0`. | A native callback admission result, not a UI phase result | The helper has a timeout and callback queues; it does not establish a roster generation or world identity. |

No typed native continue or start operation is proven between the title/event
owners and these request boundaries. Normal UI/input admission, validation,
owner thread, generation, and cancellation remain blockers. Raw slot pointers,
embedded strings, and iterator positions cannot cross an asynchronous boundary
on the evidence here.

## Manual input and focus

[`native-input-ui-boundaries.md`](native-input-ui-boundaries.md) establishes
the native pad route, routed keyboard-focus token, ancestor-key lookup, and
modal/focus registration mechanics. These are borrowed same-thread pointers:
the route can stop on an event and focus objects can be replaced. The bounded
evidence does not identify a login-phase recipient or cancel callback. The
qualified generic route ends at the event dispatch call through
`[P+4]->vtable+0x34` (`0x00548160`); the pad route enters at `0x004D6570` and
keyboard dispatch at `0x00552DF0`. None of these edges names a login-phase
receiver, cancel mutation, modal owner, or receiver lifetime.
Keyboard focus, pad routing, a modal token, and an update serial are therefore
manual intervention or invalidation observations, not proof that a login
operation is active.

## World-ready boundary

The s2c `0x000F` result closes the lobby GameLogin response loop, but it does
not prove that the world has loaded or that the displayed actor matches the
selected roster identity. The loading form has script-side metadata, but no
bounded native reader links its dismissal to a selected character. A fresh
world-ready chain must resolve all of these on the same session generation:

1. the selected roster identity used by the `0x0004` request;
2. the world identity returned or stored by the world-entry path;
3. a ready state owned by that generation; and
4. a failure or disconnect reader that invalidates all three observations.

The inspected `FUN_00DA64B0` path only copies response fragments into
`C=[O+0x08]`. The caller sets `body=packet+0x10` at `0x00DAA96C`; the
parser stores `[body+0x56]` at `C+0x278`, clears `C+0x27A`, stores
`[body+0x08]` at `C+0x27C` (`0x00DA657B-0x00DA659B`), copies 0x40 bytes
from `body+0x14`, copies 0x20 bytes from `body+0x78`, and then
calls `0x00446F50` at `0x00DA65E2`. On the false-result path,
`FUN_00DA5110` receives `ECX=C`, checks `C+0x08`, and invokes the
caller-supplied callback pointer `[O+0x34]` through vtable slots `+0x30`
with `C+0x224` and `+0x2C(0)` at `0x00DA5146-0x00DA515F`. The successful
`FUN_00DA4F80` continuation checks `C+0x08`, sets nested `+0x8C=5`, and
invokes callback slots `+0x10` and `+0x14` with `C+0x1C0`; this is an
admission callback state, not a world-ready identity. The false callback
does not consume the three fields written above. Neither path statically
compares a selected identity with a world identity or invalidates a ready
result on disconnect, so the four-reader ceiling remains.

A fresh FindFieldRefs scan found the three C-offset writes above only in
`FUN_00DA64B0` among the `0x00DA` LobbyClient method region, and no direct
read of those offsets in that region. The same numeric displacements occur in
unrelated functions elsewhere, but the inspected references do not carry a
receiver chain back to C. The fresh reference export recorded the
LobbyClientMixin vtable initializer `0x01128318` only at the constructor
`0x00DA7510` and destructor `0x00DA7220`; it recorded no additional
pointer-level reference that closes a world identity reader. This bounds the
response-copy edge while leaving the world identity reader and disconnect
invalidator unresolved.

Until those readers are traced, dismissing a prompt, observing an arbitrary
actor, or seeing the loading form hidden is not success.

## Exact unresolved discriminators

The remaining static questions are concrete:

1. **Bootup transition:** Which callback or virtual edge maps the raw selector
   and counters to `TitlePhase`, `CharacterSelectionPhase`,
   `AccountSelectionPhase`, `Waiting`, and `BootupDialog`, and which entry,
   exit, or invalidation event owns each state?
2. **Selection admission:** The GameLogin construction proves `O+0x08=C` and
   `0x00DA5CCE` writes `C+0x14` from the incoming object's first dword. Which
   normal UI/input path supplies that object, what validation admits the
   operation, and what thread, generation, and cancellation event own it?
   `R+0x0C` remains an untyped protocol value.
3. **Roster identity:** The fresh direct-call slice closes `FUN_00DA79D0` as
   a character-modify response reader. `FUN_00DA76B0` is the ordinary `0x000D`
   parser, with `FUN_00DAA9F0` as its direct caller at `0x00DAAA7D`; the
   full-identity reader remains unresolved. Which remaining virtual or
   indirect reader turns the copied `0x000D` slots into a full name, world,
   stable ID, and restriction state, and what proves exact-name uniqueness,
   coherent ownership, and generation?
4. **World readiness:** Which world-entry reader supplies a selected-identity
   match and ready state, and which disconnect or error reader invalidates that
   match?
5. **Manual cancellation:** Which login-phase receiver consumes the routed
   keyboard/controller event, and which cancel or focus/modal mutation changes
   the pending selection or confirmation, including its receiver thread and
   lifetime?

## Adoption map

| Public source | Supported observation or boundary | Blocker |
| --- | --- | --- |
| [`character-list-record.md`](../structs/ffxiv/client/network/character-list-record.md) and [`lobby_character_list_projection.json`](../manifests/lobby_character_list_projection.json) | After a qualified s2c `0x000D` parser return, copy only the documented vector count, arrival order, and explicitly named keys | Full identity, restrictions, loading-versus-empty, owner thread, and generation are unresolved |
| This page's native-owner and request-fragment sections | Observe c2s `0x0003`/s2c `0x000D`, lobby admission fragments, and c2s `0x0004`/s2c `0x000F` results with the stated ABI and failure callbacks; selector-1 phase creation and the constructed GameLogin `O+0x08=C`, `C+0x14` replacement writer are qualified | No typed title admission, normal UI/input admission source, validation, cancellation owner, or world-ready match is closed |
| [`native-input-ui-boundaries.md`](native-input-ui-boundaries.md) | Observe the routed keyboard/pad dispatch edge and borrowed focus tokens as same-thread intervention or invalidation clues | Login-phase recipient, cancel mutation, and modal ownership are unresolved |
| This page's world-ready section | Require a fresh selected-identity plus matching world-ready observation before reporting success; the response copy and callback ceiling is qualified | No native world-ready identity chain is closed |

The launcher username remains an external account label until a native
account-binding reader is resolved.
