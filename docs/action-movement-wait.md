# Retail 1.23b movement wait boundary

Static analysis of the retail 1.23b client identifies the movement-wait setters,
the countdown code, and the action-like paths that set the timer. The remaining
eligibility question is recorded below. These findings do not establish live
acceptance or classify every action kind.

## Evidence identity and method

The analyzed PE32 `ffxivgame.exe` is retail 1.23b build `2012.09.19.0001`,
with image base `0x00400000`, file size `15,996,808`, and SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Both input copies were independently checked to have this same length and
digest. The addresses below are image VAs; subtract `0x00400000`
for RVAs.

The producing read-only tool sources were checked at committed revision
`51be90574ef0e76da4fa432b8e095c5fe9fc574e`, using Ghidra
12.1.3_PUBLIC, Java 21.0.11+10, and LLVM objdump 22.1.4. The Ghidra scripts
were `ghidra/DumpVAs.java` and `ghidra/DumpFunctionListing.java`; the PE
vtable and instruction checks used LLVM objdump. `symbols.json` was read with
`tools/_symbols_io.py`. Every used `DumpVAs` section had its requested entry,
exactly one `Name` line, exactly one decompilation marker, and no `ERROR` or
`DECOMP FAILED`; the boundary listing completed 4/4 targets, the related
listing completed 10/10, the caller export completed 8/8, and the update
export completed 5/5. The field-reference scan covered 3,174,303
instructions, reporting 453 hits in 242 functions. Function names are
analysis labels, not recovered source names.

The reproducible target recipe follows the host
[`ghidra/README.md`](../ghidra/README.md) setup
contract and uses the committed `tools/ghidra/run-headless.ps1` read-only
wrapper. Resolve the required Ghidra and Java environment variables from the
host, set `BCS_GHIDRA_PROGRAM` to `ffxivgame.exe` when needed, and run one
invocation per target list. The boundary list is
`0x007B0700,0x0065ED30,0x007AFD90,0x008283D0`; the related list contains
`0x007AA710`, `0x0065EDC0`, `0x007B0720`, `0x007B1420`, `0x007A4B60`,
`0x007A7570`, `0x007B04A0`, and `0x0065A500`. LLVM objdump covers
`0x00669650`, `0x00844110`, `0x00844130`, and `0x008286A0`. The output names
below are placeholders, not evidence citations.

```powershell
tools\ghidra\run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -Out tools\ghidra\logs\movement-wait-listing.txt `
    -ScriptEnv @{ XIVL_TARGET_VAS = '0x007B0700,0x0065ED30,0x007AFD90,0x008283D0' } `
    -ScriptPath @('ghidra')
```

The narrow field-reference recipe is:

```powershell
tools\ghidra\run-headless.ps1 -Script FindFieldRefs.java -ReadOnly `
    -Out tools\ghidra\logs\movement-wait-field-refs.txt `
    -ScriptEnv @{ IMPLEMENTATION_OFFSET_QUERY = '0x1CC,0x1D4' } `
    -ScriptPath @('ghidra')
```

`FindFieldRefs` scans instruction displacements in the analyzed database. Its
reported 3,174,303 instructions, 453 hits, and 242 functions are candidate
scan coverage, not exhaustive references: computed, indirect, and dynamic
accesses can be absent. Its `READ` and `WRITE` labels describe operand
position only, so comparisons require instruction-level interpretation.

## Native boundary

`FUN_007B0700` at image VA `0x007B0700` is the movement-controller setter.
The fresh instruction listing is:

```text
0x007B0700  CVTSI2SS XMM0,dword ptr [ESP + 0x4]
0x007B0706  MOVSS dword ptr [ECX + 0x1cc],XMM0
0x007B070E  CALL 0x007afd90
0x007B0713  RET 0x4
```

The supported ABI observation is x86 `thiscall`: `ECX` is the
movement-controller receiver, the function-entry argument at `[ESP+0x4]` is
one signed integer duration, the value is converted to single precision and
stored at receiver `+0x1CC`, the setter calls `FUN_007AFD90`, and it returns no
value while callee-popping that one stack argument. The setter has no null
check of its receiver. `FUN_007B0720` is the parallel setter for `+0x1D4`.

`FUN_0065ED30` is the actor-facing gate and wrapper. Its explicit function-entry
arguments are an object pointer at `[ESP+0x4]` and a signed integer duration at
`[ESP+0x8]`, and it returns with `RET 0x8`. Because its first instruction is
`PUSH ESI`, the post-push listing reads the same arguments as `[ESP+0x8]` and
`[ESP+0xC]`; those post-push offsets are not entry offsets. The wrapper returns
early for a null object, calls the object's virtual slot at byte offset
`+0x268`, and invokes `FUN_007B0700` only when that virtual call returns zero.
The setter receiver is then `object + 0xBF0`. The wrapper's entry `ECX` is not
consulted by the shown instructions.

`FUN_0065ED60` has the same entry ABI, null check, `+0x268` gate, and `RET 0x8`,
but reaches `FUN_007B0720` and therefore the alternate `+0x1D4` timer. These
gated wrappers and setters are candidate reduction boundaries only; static
evidence does not support treating either as an eligible movement effect.

The `+0x268` target can be traced mechanically for the primary CharaActor
vtable. The cataloged CharaActor vtable is `0x00FC0D34` (BCS-Y-1846), so slot
`+0x268` is the pointer at `0x00FC0F9C`. The verified PE bytes there resolve
to `FUN_00669650`; its fresh instructions at `0x00669650-0x0066965C` load
`[ECX+0x2B70]`, shift right by 6, mask with 1, and return that bit. This
resolves the gate's primary-vtable mechanics, not its semantic reason. A
successful CharaActor-compatible dynamic cast does not prove that the live
object uses this primary vtable rather than a derived override. The bit's
meaning and derived overrides remain static questions; the launcher must also
qualify the live vptr and gate result before adopting an effect.

The paired action-controller wrapper `FUN_0065EDC0` repeats the same entry
argument correction and `+0x268` gate, then passes `object + 0x2858` as the
receiver to `FUN_00844110` at `0x0065EDDE-0x0065EDE4`. `FUN_00844110` converts
its signed integer argument with `CVTSI2SS`, stores it at action-controller
`+0x22C`, and returns with `RET 0x4`; `FUN_00844130` reads that field and
returns one only when it is positive (`0x00844130-0x00844149`). This is a
direct action-controller duration side effect and read boundary, not proof of
animation admission.

## Consumer, countdown, and reset

`FUN_007AFD90` is the consumer and transition routine. It receives the
movement controller in `ECX`, reads the actor pointer from the controller's
first word, and invokes the identity predicate `FUN_0065A500` at
`0x007AFE7D-0x007AFE84`.

For the non-identity branch, the selected timer is compared with
`DAT_00FA4460`, whose retail image bytes are `00 00 00 00` (`0.0f`):

| Branch | Instruction evidence | Static result for finite values |
|---|---|---|
| Controller flag bit `0x4` set | `0x007AFE95-0x007AFEAC` reads `+0x1D4`, `COMISS`, then `JA 0x007AFEBF` | Positive timer takes the block flag; zero or negative reaches the allow path. |
| Controller flag bit `0x4` clear | `0x007AFEAE-0x007AFEBD` reads `+0x1CC`, `COMISS`, then `JBE 0x007AFEC4` | Zero or negative reaches the allow path; positive falls through to the block flag. |

The following transition code can clear controller flag bit `0x8` and field
`+0x1A0` (`0x007AFEC4-0x007AFEE9`), so the setter is an operation with side
effects rather than a passive field write. These comparisons do not label zero
as a sentinel. They show only that finite nonpositive values bypass this
non-identity positive-timer block; unordered floating-point values follow the
x86 compare flags and are not part of a supported duration contract.

For the identity-true, local-player-like branch, `FUN_007AFD90` calls
`FUN_007AA710` at `0x007AFE88-0x007AFE91`. A true helper result takes the same
block write at `0x007AFEBF`; a false result continues at `0x007AFEC4`.
`FUN_007AA710` first checks owner flag `+0x2B70` bit `0x200` and an owner
virtual slot at byte offset `+0x258` (`0x007AA710-0x007AA731`). It selects
`+0x1D4` or `+0x1CC` using controller flag bit `0x4`, and its positive test is
at `0x007AA733-0x007AA752`. A positive selected timer returns the blocking
true value at `0x007AA721`; a zero or negative value proceeds into additional
identity, controller-state, owner-byte, and virtual gates before the final
return at `0x007AA7C5`. Thus nonpositive alone does not prove a free
movement result or a sentinel meaning on this branch.

`FUN_0065A500` is an exact structural identity predicate. With the actor in
`ECX`, it returns true when the pointer at `[ECX+0x118]` has a pointer at
`+0xD0` equal to `ECX` (`0x0065A500-0x0065A513`). The movement consumer uses
this as a local-player-like branch selector, but the static slice does not
prove that the owning object is the live local-player singleton.

`FUN_007A4B60` is the per-update countdown operation. It accepts a float delta
at function-entry `[ESP+0x4]` and, independently for `+0x1CC` and `+0x1D4`,
subtracts `controller + 0xF8` multiplied by that delta only while the stored
timer is positive (`0x007A4B60-0x007A4BC5`). It returns with `RET 0x4`, and
`FUN_006679C0` calls it from the actor update. `FUN_007A7570` initializes
`+0xF8` to `1.0f` and both timer fields to `0.0f`.

`FUN_006679C0` declares that delta as its float `param_2`, passes it unchanged
to `FUN_007A4B60`, and has no recovered direct caller in the bounded export.
The exact missing duration-unit edge is therefore the unresolved callback or
indirect provider of `param_2`: static evidence does not determine whether it
is seconds, frames, milliseconds, or another tick fraction, and does not tie
it to a Present cadence.

`FUN_007B1420` is an actor-level reset path. It reaches the embedded controller
at actor `+0xBF0`, stores `-1.0f` into `+0x1CC`, calls the consumer, then stores
`-1.0f` into `+0x1D4` and calls the consumer again (`0x007B1490-0x007B14C1`).
This proves a reset input and an already-started wait cancellation candidate;
its user-facing cancellation meaning is not established. The observed paths
mutate embedded countdown fields and synchronously call `FUN_007AFD90`, while
the qualified identity helper `FUN_007AA710` remains a separate consumer
branch.

The stored fields are single-precision floats. Their external unit is not
established as milliseconds, frames, or seconds. The direct setters use
`CVTSI2SS`, whose integer-to-float result is subject to the active MXCSR
rounding mode; the source instructions do not establish that mode, and large
signed integers need not be exactly representable as floats. The action-like
producers first use `CVTSI2SS` for the integer source, scale in double
precision, then use `CVTTSD2SI` to truncate toward zero before calling an
integer wrapper (`0x0082848E-0x008284A5` and
`0x00828756-0x00828771`). The producer truncation and the setter's later
integer-to-float conversion are distinct steps. No zero or nonpositive clamp
occurs in either setter.

## Action-like producers and caller limits

`FUN_008283D0` is the sole direct caller reported for `FUN_0065ED30`.
Its action-like path checks a virtual predicate, requests a dynamic cast using
the retail `IActor` and `CharaActor` RTTI descriptors, and requires a non-null
cast result (`0x00828401-0x00828425`). It reads an integer at `+0x10` from the
object reached through its `+0x14` field, applies either `1.0f` or a positive
reciprocal scale, truncates the scaled value toward zero, and passes that
integer with the cast result to `FUN_0065ED30` at `0x008284A1-0x008284A9`.
It then passes the same duration and object to `FUN_0065EDC0` at
`0x008284C1-0x008284C9`, producing the paired action-controller write above.
The caller export also reports `FUN_00828D70` as a direct caller of
`FUN_0065EDC0`; its caller role was not classified in this bounded slice.

`FUN_008286A0` is a parallel action-like producer that performs the same RTTI
cast and conversion pattern and calls the alternate `FUN_0065ED60` at
`0x00828771-0x00828775`, selecting the `+0x1D4` movement timer. These two
producer paths are source-backed action-like paths, but neither identifies the
action as recovery, engagement, casting, or forced/server-imposed movement.

`FUN_00844130` is not exclusive to the paired producer path. A direct PE call
scan found a positive-read call at `0x007ADF0C` inside `FUN_007ADEB0` after
adding `0x2858` to the receiver, and another at `0x007C2868` after the same
receiver adjustment. The first caller tests the returned `AL`; the containing
function for the second call was not resolved by the bounded exports. These
are still-untraced action-state callers, while indirect dispatch remains
possible, so their recovery, engagement, cast, forced, and unrelated roles
remain exact missing edges pending a source-backed discriminator.

The consumer has broad non-producer callers. `FUN_007B04A0` changes the
controller auto-run flag bit `0x8` and calls `FUN_007AFD90` when clearing it;
`FUN_007B1420` is a state-machine reset path. These are evidence that the
consumer is shared movement state machinery, not evidence that either caller
is action recovery. The static caller slice supplies no instruction-backed
distinction for recovery, engagement, casting, forced/server restrictions, or
unrelated locks. The untraced callers above remain static follow-ups, and live
qualification is required before adopting an eligible-action discriminator.
Unknown contexts must retain normal movement.

The paired `+0x2858` action-controller storage and its positive read at
`FUN_00844130` establish an indirect action-state relation. No static path in
this slice proves that the movement wait admits or blocks animation playback,
recast, action admission, or cast interruption. No synchronization or thread
check is present. The actor, movement controller, embedded action controller,
and vtable targets must remain valid for the synchronous calls, and the
owning-thread requirement remains unresolved by static evidence.

## Adoption map

The public observation boundary is the actor's embedded controller at
`+0xBF0`: read the flag-selected positive countdown (`+0x1CC` or `+0x1D4`),
the local-player-like identity predicate, the `+0x268` gate result, and the
paired action-controller field at `+0x22C` when the action-like path is
present. These observations are tied to `FUN_007AFD90`, `FUN_007AA710`, and
`FUN_00844130` above.

The candidate operation boundary is the gated wrappers
`FUN_0065ED30(object, duration)` and `FUN_0065ED60(object, duration)`. They
remain reduction candidates only. The exact blocker is the unresolved
eligibility discriminator: the semantic meaning of the `+0x268` return bit,
the live object's actual vtable or derived override, the caller taxonomy, and
the identity of the live local-player object. Launcher-owned observations must
compare baseline and reduced waits for action recovery, ordinary movement,
casting, forced restrictions, manual cancellation, and unrelated locks before
adopting an effect.

## Confidence and unresolved edges

- High confidence: binary identity, image base, function VAs, corrected
  function-entry stack arguments, receiver offsets, callee-popped returns,
  `+0x268` primary-vtable target mechanics, field offsets, positive-only
  countdown, initialization, reset writes, and the action-controller
  `+0x22C` write/read. These are instruction-backed in fresh retail listings
  or direct PE/LLVM inspection.
- Medium confidence: the two producer paths are action-like because of the
  CharaActor RTTI cast, duration source, and paired CharaActionController
  storage; the successful cast does not prove a primary CharaActor vptr at
  the call site.
- Unresolved: external duration units and MXCSR rounding configuration, zero
  sentinel meaning, user-facing cancellation, the semantic reason for the
  `+0x268` bit, derived-vtable overrides, complete caller taxonomy, live
  local-player singleton equivalence, thread affinity, and relations to
  animation playback, recast, action admission, or cast interruption.

The coverage is a bounded static slice around the setters, both producer
families, their direct consumers, field references, and the primary CharaActor
vtable slot. It does not claim exhaustive xrefs, runtime state coverage, or
runtime acceptance.
