# Retail 1.23b movement wait boundary

Static analysis of the retail 1.23b client identifies the movement-wait setters,
the countdown code, and the action-like paths that set the timer. The primary
bit-6 writer, clip-vtable provenance, actor-owner construction edge, update
callback edge, and reset writer/caller are recorded below. Semantic action
taxonomy, units, thread ownership, and live qualification remain bounded
below. These findings do not establish live acceptance.

## Evidence identity and method

The analyzed PE32 `ffxivgame.exe` is retail 1.23b build `2012.09.19.0001`,
with image base `0x00400000`, file size `15,996,808`, and SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
The complete `VerifyProgramFileBytes.java` check (`COMPLETE:
program-file-bytes-v1`) matched the input,
retained-original, retained-modified, and mapped file-backed hashes and
verified 15,990,784 loaded file-backed bytes; unbacked non-executable and TLS
ranges were explicitly excluded. The addresses below are image VAs; subtract
`0x00400000` for RVAs.

The producing read-only `ghidra/VerifyProgramFileBytes.java` source was checked
at revision `08de0f7428a133a689627ac0cbf60d97daed2a71`; the other exporters,
including `ExtractRtti`, `FindFieldRefs`, and the raw-PE toolkit, were checked
at baseline revision `51be90574ef0e76da4fa432b8e095c5fe9fc574e`. The tools used
Ghidra 12.1.3_PUBLIC, Java 21.0.11+10, LLVM objdump 22.1.4, and the committed
`tools/extractors/client_pe` toolkit (`python -m tools.extractors.client_pe
--exe $Executable --rtti`). The Ghidra scripts were
`ghidra/VerifyProgramFileBytes.java`, `ghidra/DumpVAs.java`,
`ghidra/DumpFunctionListing.java`, `ghidra/FindReferences.java`,
`ghidra/FindFieldRefs.java`, `ghidra/FindCompoundOffsetWriters.java`, and
`tools/ghidra/ExtractRtti.java`; `symbols.json` was read with
`tools/_symbols_io.py`. DumpVAs reports were checked per requested VA for the
expected entry, name, and decompilation with no `ERROR` or `DECOMP FAILED`.
DumpFunctionListing, FindReferences, and FindCompoundOffsetWriters reports
used below were accepted only with their explicit `COMPLETE` markers. The
RTTI export recorded 5,623 rows. The complete direct-literal `+0x2B70` writer
scan swept 3,174,303 defined and 791,580 pseudo instructions, evaluating
1,209,144 stores and reporting 44 direct-literal hits. The complete
`+0x118/+0xD0` writer scan used the same sweep and yielded the positive writer
and clear rows cited below. Direct, indirect, computed, and unanalyzed
references can still be absent. Function names are analysis labels, not
recovered source names.

The reproducible target recipe follows the host
[`ghidra/README.md`](../ghidra/README.md) setup
contract and uses the committed `tools/ghidra/run-headless.ps1` read-only
wrapper. Resolve the required Ghidra and Java environment variables from the
host, set `BCS_GHIDRA_PROGRAM` to `ffxivgame.exe` when needed, and run one
invocation per target list. The boundary list is
`0x007B0700,0x0065ED30,0x007AFD90,0x008283D0`; the related list contains
`0x007AA710`, `0x0065EDC0`, `0x007B0720`, `0x007B1420`, `0x007A4B60`,
`0x007A7570`, `0x007B04A0`, and `0x0065A500`. The owner/lifecycle list is
`0x0079FAE0,0x0065A500,0x0065A520,0x0065A580,0x0065F180,0x006329C0,0x007CEF80,
0x007D1C20,0x00669E20,0x00666130,0x007CEF20,0x007C93C0,0x007C9740`;
the gate/reset list is `0x007AFD90,0x007AA710,0x007A4060,0x007A4080,
0x007A3EA0,0x007A8170,0x007A4100,0x007C0E10,0x007B1420`. Reference exports
used the bit-6 targets `0x00669630,0x00669650,0x00FC0F9C,0x00FC0D34`, the
admission targets `0x008283D0,0x008286A0,0x00828D70,0x00844110,0x00844130,
0x007ADEB0,0x007C21B0,0x007AFD90,0x007AA710,0x007B1420,0x007B0700,
0x007B0720`, and the update targets `0x006679C0,0x007A4B60,0x0065A500,
0x007AFD90,0x007AA710`. Compound writer queries were `0x2B70` and
`0x118,0xD0`. The full RTTI target was the executable, with rows read at
`0x00FC0D34`, `0x00FEA50C`, `0x01028CD0`, `0x01028CDC`, `0x01029728`,
`0x01029734`,
`0x0102ABD8`, and `0x0102ABE4`; clip vtable entries were read at
`0x01028CE0`, `0x01029738`, and `0x0102ABE8`. LLVM objdump covers
`0x00669630`, `0x00669650`, `0x00844110`, `0x00844130`,
`0x008283D0`, `0x008286A0`, `0x00828D70`, `0x007B1420`, `0x007C0E10`, and
`0x007CEF20`. The output names below are placeholders, not evidence
citations.

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
The instruction listing is:

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
`+0x264` is the pointer at `0x00FC0F98` and slot `+0x268` is the pointer at
`0x00FC0F9C`. The verified PE bytes resolve these slots to
`FUN_00669630` and `FUN_00669650`. The setter at
`0x00669630-0x0066964A` sets `[ECX+0x2B70]` bit 6 to its bit-0 argument; the
getter at `0x00669650-0x0066965C` shifts `[ECX+0x2B70]` right by 6, masks with
1, and returns that bit. The complete direct-literal writer scan found this
dedicated setter among 44 direct-literal `+0x2B70` hits, alongside whole-word
and other-bit writers. The supported meaning is therefore a per-object bit-6
gate/latch, not a recovered recovery, cast, engagement, or forced-lock label.

The reference export found the setter and getter only in the primary vtable
data slots above. No derived override was established in the recorded PE
references; computed vtable construction, indirect calls, and unanalyzed
derived types remain outside that ceiling. A successful CharaActor-compatible
dynamic cast does not prove that the live object uses this primary vtable, so
the launcher must qualify the live vptr and gate result before adopting an
effect.

The paired action-controller wrapper `FUN_0065EDC0` repeats the same entry
argument correction and `+0x268` gate, then passes `object + 0x2858` as the
receiver to `FUN_00844110` at `0x0065EDDE-0x0065EDE4`. `FUN_00844110` converts
its signed integer argument with `CVTSI2SS`, stores it at action-controller
`+0x22C`, and returns with `RET 0x4`; `FUN_00844130` reads that field and
returns one only when it exceeds the authenticated `0.0f` value at
`DAT_01086650` (`0x00844130-0x00844149`). This is a positive action-controller
duration test and read boundary, not proof of animation admission.

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
`FUN_007AA710` first requires owner `+0x2B70` mask `0x200` and a nonzero
owner virtual call at byte offset `+0x258`; either failure returns the
blocking true value (`0x007AA710-0x007AA731`). It selects controller
`+0x1D4` or `+0x1CC` using controller flag bit `0x4`, and a positive selected
timer also returns true (`0x007AA733-0x007AA752`). A zero or negative selected
timer only passes that one comparator. The structural identity-true branch then
requires controller `+0x34` to be at or below the threshold, while the
identity-false branch bypasses that comparison; both branches require
controller `+0x1EC` to be zero and owner byte `+0xB7D` bit `0x2` to be clear
(`0x007AA75B-0x007AA76B`). The
`FUN_007A4060` and `FUN_007A4080` then test the state-byte pair at their
`+0x5A9/+0x5AA` receiver offsets: the first returns one only for `(0,2)`, and
the second only for `(2,0)` (`0x007A4060-0x007A4097`). If both return zero,
the caller compares that pair and blocks on a mismatch. `FUN_007A3EA0` returns
one when its `+0x5AC` byte is nonzero or either state byte is `1` or `3`
(`0x007A3EA0-0x007A3ED0`). When it returns zero, `FUN_007A8170` performs the
remaining owner virtual calls and float comparison; the helper returns the
inverse of that call's boolean (`FUN_007AA710` at `0x007AA7AB-0x007AA7C5`;
`FUN_007A8170` at `0x007A8170-0x007A81B4`). These exact byte and virtual
predicates close the static gate mechanics, but their domain labels are not
supported. Thus nonpositive alone does not prove a free movement result or a
sentinel meaning on this branch.

`FUN_0065A500` is an exact structural identity predicate. With the actor in
`ECX`, it returns true when the pointer at `[ECX+0x118]` has a pointer at
`+0xD0` equal to `ECX` (`0x0065A500-0x0065A513`). The movement consumer uses
this as a local-player-like branch selector, but the static slice does not
prove that the owning object is the live local-player singleton. The
constructor path supplies a bounded lifetime edge: `FUN_0079FAE0` allocates
`0x2BB0` bytes and calls `FUN_0065F180`; that constructor calls
`FUN_006329C0`, whose `FUN_007CEF80` base constructor stores its
constructor-selected pointer in RaptureActor word `0x46` (`+0x118`). The
CharaActor constructor then constructs the embedded movement controller at
`+0xBF0` (`0x0065F2FA-0x0065F301`) and uses `[actor+0x118]+0xD8` while calling
`FUN_007D1C20` with the actor (`0x0065F7E4-0x0065F81B`).

`FUN_0065A520` performs the corresponding RaptureActor-to-CharaActor RTTI
cast through the owner `+0xD0` pointer. `FUN_00669E20` calls
`FUN_00666130` for CharaActor teardown and can then free the allocation; the
destructor still uses the stored owner pointer while releasing child state.
The RaptureActor vtable `0x00FEA50C` resolves its `+0x260` destructor slot at
`0x00FEA76C` to `FUN_007CEF20`. The teardown path reaches it from
`FUN_00666130` at `0x00666545`; `FUN_007CEF20` loads `[actor+0x118]` and
passes the actor to
`FUN_007C9740` (`0x007CEF2F-0x007CEF3A`), whose case-specific clear writes
owner `+0xD0 = 0` at `0x007C977D` when it equals that actor. A separate
case-`0xF` update in `FUN_007C93C0` writes its receiver `+0xD0` at
`0x007C9676` (caller `FUN_0060C140`); the current slice does not bind that
receiver or assigned pointer to this exact CharaActor. The joined teardown
edge therefore closes invalidation for the matched actor while leaving the
writer's dynamic receiver identity and local-player singleton equivalence
unresolved. The exports also show no named OS thread.

`FUN_007A4B60` is the per-update countdown operation. It accepts a float delta
at function-entry `[ESP+0x4]` and, independently for `+0x1CC` and `+0x1D4`,
subtracts `controller + 0xF8` multiplied by that delta only while the stored
timer is positive (`0x007A4B60-0x007A4BC5`). It returns with `RET 0x4`, and
`FUN_006679C0` calls it from the actor update. `FUN_007A7570` initializes
`+0xF8` to `1.0f` and both timer fields to `0.0f`.

`FUN_006679C0` is the primary CharaActor vtable callback at slot `+0x238`
(`0x00FC0F6C`). It declares the callback delta as float `param_2`, loads the
embedded controller at `actor+0xBF0`, and calls `FUN_007A4B60` with that delta
at `0x00667F80-0x00667F88`. Its prologue also reads the active x87 control
word and temporarily sets the rounding-control bits for an accumulator
conversion at `0x00667A00-0x00667A51`; this is not an MXCSR or duration-unit
declaration. The callback has no recovered direct caller in the bounded
export. The missing provider edge therefore includes the indirect vtable
dispatcher, external units, cadence, owning update thread, and invalidation
ordering. This is a static callback dependency, not proof of a named OS
thread or a Present cadence.

`FUN_007B1420` receives a state-machine object whose first word is the actor
pointer. Before the exact field writes, it makes an indirect virtual call
through the first-word actor's `+0x114` object at slot `+0x8`
(`0x007B1425-0x007B1432`); that call's side effects are not identified. It
then releases and clears three receiver-owned handles at `+0x348..+0x350`,
sets receiver `+0x598` to `0.0f`, assigns receiver `+0x59C` the authenticated
`2700.0f` value `DAT_00FE7EC8`, and clears receiver byte `+0x5AC`. It stores
the authenticated `-1.0f` value `DAT_00F62F80` into the first-word actor's
embedded controller at `+0x1CC` and `+0x1D4`, calling `FUN_007AFD90` after
each store (`MOVSS` stores at `0x007B149C` and `0x007B14B9`, calls at
`0x007B14A4` and `0x007B14C1`). After those calls it invokes
`FUN_008BF770(0)` on receiver `+0x4` (`0x007B14C6-0x007B14CC`); its side
effects are also not identified. The reset has one recorded direct caller,
`FUN_007C0E10` at `0x007C1BE3`; that state-machine receiver tests its own
`+0x5B4` bit `0x400` after `FUN_007A4100`
(`0x007C1BC4-0x007C1BE3`). This is instruction-backed cancellation of the
two countdown fields, while the receiver handles and state fields show that
the operation also resets broader movement state. It does not write the
paired action field `+0x22C`; exact user-facing cancellation remains a live
state observation.

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

The RTTI-backed vtable data references classify the three clip entry points at
the native boundary: `0x01028CE0 -> FUN_008283D0` is the
`RaptureClientMoveStopClip` vtable entry, `0x01029738 -> FUN_008286A0` is the
`RaptureServerMoveStopClip` entry, and `0x0102ABE8 -> FUN_00828D70` is the
`RaptureActionKeepClip` entry. These are class names recovered from the retail
RTTI descriptors; they are not proof of an action taxonomy.

`FUN_008283D0` checks a clip virtual predicate, requests an `IActor` to
`CharaActor` RTTI cast, and on a valid result scales and truncates the clip
duration before calling `FUN_0065ED30` for movement `+0x1CC` and
`FUN_0065EDC0` for action-controller `+0x22C`
(`0x00828401-0x008284C9`). `FUN_008286A0` follows the same cast and scaling
shape but calls `FUN_0065ED60` for movement `+0x1D4`
(`0x00828771-0x00828775`). `FUN_00828D70` calls `FUN_0065EDC0` for the
paired action-controller field. This closes the source-backed producer and
storage relation while leaving the user-facing clip meaning unresolved.

`FUN_00844130` reads action-controller `+0x22C` and is not exclusive to the
producer path. At `0x007ADF0C`, `FUN_007ADEB0` adds `+0x2858` to its actor
receiver and uses the read only for clips whose byte `+0x6E` bit 1 is set;
other clips use their own word `+0x6C` masks before the shared transition
logic. At `0x007C2868`, `FUN_007C21B0` uses the same read only when its state
word has high byte `0x19`; other states use `FUN_007A45D0`. The result is
combined with another state predicate before the transition continues. These
instructions establish an action-state admission relation, not whether the
state is recovery, engagement, casting, forced/server restriction, or an
unrelated lock. Those are exact missing discriminators for runtime checks.

The consumer has broad non-producer callers. `FUN_007B04A0` changes the
controller auto-run flag bit `0x8` and calls `FUN_007AFD90` when clearing it;
`FUN_007B1420` resets both countdown fields and related state-machine receiver
state. These
callers show shared movement state machinery, not an action taxonomy. Unknown
contexts must retain normal movement until the launcher observes the native
state and resulting action/cast behavior.

## Adoption map

The public observation boundary is the actor's embedded movement controller at
`+0xBF0`: read the flag-selected countdown (`+0x1CC` or `+0x1D4`), the
structural identity predicate, the live `+0x268` gate result, and paired
action-controller `+0x22C` when the action-like path is present. The candidate
operation boundary remains `FUN_0065ED30(object, duration)` or
`FUN_0065ED60(object, duration)`. The following five dispositions record the
smallest promoted claim and the exact next discriminator.

1. **Virtual `+0x268` and bit 6 - promoted mechanics, semantic ceiling.** The
   primary CharaActor vtable has `+0x264 -> FUN_00669630` and
   `+0x268 -> FUN_00669650`; the setter and getter operate on
   `[actor+0x2B70]` bit 6. No derived override was established by the complete
   recorded reference export. The missing discriminator is the bit's domain
   meaning and any computed or indirect derived-vptr override. The launcher
   must record live vptr, both virtual results, and before/after bit 6 for
   eligible actions and ordinary movement.

2. **Clip producers and action admission - promoted relation, taxonomy
   ceiling.** Client-move, server-move, and action-keep RTTI vtable entries
   reach `FUN_008283D0`, `FUN_008286A0`, and `FUN_00828D70`; these write the
   movement timers and/or action-controller `+0x22C`. `FUN_00844130` is read
   from the clip loop and the state-`0x19` action pump. The missing
   discriminator is a source-backed separation of recovery, engagement,
   casting, forced/server restrictions, and unrelated locks. The launcher must
   compare baseline and reduced waits while observing action admission, cast
   start/interruption, forced movement, cancellation, and unrelated locks.

3. **Actor `+0x118` owner candidate - promoted lifecycle edge, joined
   teardown, identity ceiling.** The CharaActor allocation and constructor
   chain stores a constructor-selected pointer in `+0x118`, constructs
   movement at `+0xBF0`, and tears down through
   `FUN_00669E20 -> FUN_00666130`; `FUN_0065A500` and `FUN_0065A520` consume
   the owner `+0xD0` relation. The teardown path joins the actor to the
   matching owner clear in `FUN_007C9740` at `0x007C977D`; the separate
   `FUN_007C93C0` case-`0xF` writer is recorded at `0x007C9676`, but its
   receiver and assigned pointer are not bound to this actor statically. The
   missing discriminator is that writer's dynamic receiver identity,
   local-player singleton equivalence, and lifetime synchronization. A runtime
   check must pin owner, actor, controller, and vptr identity and record owner
   `+0xD0` before and after the case-`0xF` update and teardown across
   construction, use, reset, and destruction.

4. **Update delta - promoted callback dependency, provider ceiling.** Primary
   vtable slot `+0x238` dispatches `FUN_006679C0`, which calls
   `FUN_007A4B60` on `+0xBF0` with the callback float. The missing discriminator
   is the indirect provider, external units, cadence, update-thread identity,
   and invalidation ordering. This static dependency does not prove a named OS
   thread. Runtime must capture the callback delta and executing thread while
   checking countdown progression; no Present or 60fps assumption is allowed.

5. **Identity-true admission and reset - promoted gates and writer, outcome
   ceiling.** `FUN_007AA710` requires owner mask `0x200`, virtual `+0x258`,
   the selected timer at or below the observed threshold, controller `+0x34`
   only on the identity-true branch, controller `+0x1EC` conditions, owner
   byte `+0xB7D` bit `0x2`, and the recorded state-byte and nested virtual
   predicates. The sole recorded direct caller of `FUN_007B1420` is
   `FUN_007C0E10` at `0x007C1BE3`; the reset receiver owns the handle/state
   offsets, while its first-word actor owns the countdown controller. The
    reset writes `-1.0f` to both countdown fields, calls the consumer after
    each, assigns receiver `+0x59C` to `2700.0f`, and has calls with unresolved
    side effects before and after those writes, including direct
    `FUN_008BF770(0)` after them. The missing discriminator is the
   semantic result of the dynamic gates, the indirect reset side effects, and
   whether the reset represents user cancellation or a broader state
   transition. Runtime must observe every gate, receiver/actor identity,
   receiver `+0x5B4`, and all three fields (`+0x1CC`, `+0x1D4`, `+0x22C`)
   across that state transition.

## Confidence and unresolved edges

- High confidence: binary identity, image base, function VAs, corrected
  function-entry stack arguments, receiver offsets, callee-popped returns,
  primary-vtable `+0x264/+0x268` mechanics, direct bit-6 writer, countdown
  arithmetic, initialization, owner `+0xD0` writer/clear mechanics, reset
  stores, and action-controller `+0x22C` write/read. These are
  instruction-backed in retail listings or direct PE/LLVM inspection.
- Medium confidence: RTTI class-to-vtable provenance, the three producer
  paths, and actor construction/teardown relationships. The class names and
  lifecycle edges are source-backed, but they do not supply user-facing
  action labels or local-player singleton identity.
- Unresolved: external duration units, active MXCSR and x87 conversion
  context, zero/nonpositive sentinel meaning, dynamic admission-gate labels,
  derived-vtable overrides outside recorded references, complete caller
  taxonomy, the dynamic receiver identity of the `FUN_007C93C0` owner writer,
  live local-player equivalence, indirect reset side effects, named OS thread,
  and relations to animation playback, recast, cast interruption, and forced
  movement.

The coverage is a bounded static slice around the setters, both producer
families, their direct consumers, field references, and the primary CharaActor
vtable slot. It does not claim exhaustive xrefs, runtime state coverage, or
runtime acceptance.
