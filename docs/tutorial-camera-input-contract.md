# Camera tutorial completion state

The camera tutorial wait observes bit 0 of `CameraElement +0x17C`.
An attributable native update sets that bit after a phase sequence involving
the float at `+0x124` and a saved float at `+0x180`. The concrete player input
that supplies the selected float remains unresolved.

The [wait contract](tutorial-control-native-contract.md#waits) owns callback
`0x006E1C50`, checker construction, yield and polling. This page owns the
selected completion producer and its input boundary. `STATIC` below means an
observation from the identified executable or a cited canonical publication.
Role names such as phase and baseline describe the observed operations.

## Source and owner

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
matching [the input manifest](../manifests/retail_inputs.json).
All addresses below are absolute VAs.

The wait obtains `K` through `0x004D7320`, the getter of container `V +0x4C4`.
The [registry/cache contract](client-architecture.md#raptureelementcontainer-embeds-an-anonymous-element-registry-at-0x4ac)
and [selector record](../manifests/rapture_selector_0d_clientwork.json),
`cacheMap` selector `0x02` and `installedSelectors` selector `0x02`, identify
that cache with `Application::Main::Element::System::CameraElement`.

Original PE data corroborates the class and complete-object base:

- Vftable `0x00FA47A0` has a Complete Object Locator with object offset zero
  and RTTI name `.?AVCameraElement@System@Element@Main@Application@@`.
- Constructor `0x00566380` installs that vftable at object `+0x00`
  (`0x005663FA`) and `0x00FA467C` at `+0x08` (`0x00566400`).
- Slot 6 of `0x00FA47A0`, cell `0x00FA47B8`, points to `0x005624D0`.
  Its tail at `0x00562823` reaches `0x0055F760` with the same object receiver.
- Slot 8, cell `0x00FA47C0`, points to the selected input writer
  `0x0055EFD0`.

These observations establish a class-compatible completion producer for the
cached camera object. Actual instance installation, invocation and ordering
remain runtime conditions.

## Installation and completion

`STATIC`: `0x0055CF00(K, 0)` stores 1 in the phase byte at `K +0x17D`
(`0x0055CF07`). It leaves the completion byte unchanged. The constructor
zeroes both bytes at `0x005666F2` and `0x005666F8`. Installation therefore
does not itself require a new completion transition when bit 0 was already
set.

`STATIC`: `0x0055F760` first calls `0x004D7240` on the owner at `K +0x7C`.
That accessor tests the owner's dword at `+0x500` for nonzero. A false result
returns through `0x0055F826` before the phase work. The wait's prelude refresh
of `V +0x500` remains owned by the
[original contract](tutorial-control-native-contract.md#waits).

With that guard satisfied, the selected phase sequence is:

| Entry phase at `+0x17D` | Selected effect | Locators |
|---|---|---|
| 1 | Save the float at `+0x124` into `+0x180`, then set phase 2. | `0x0055F77F`, `0x0055F812..0x0055F825` |
| 2 | Compare the current float with the saved baseline as described below. A qualifying difference saves the current float and sets phase 3. | `0x0055F788`, `0x0055F7A2..0x0055F810` |
| 3 | Union bit 0 into the byte at `+0x17C`, then clear the phase byte. | `0x0055F78D`, `0x0055F793..0x0055F79F` |
| Other | Return without those completion or baseline writes. | `0x0055F78D`, `0x0055F826` |

In phase 2, the two floats are promoted to double for their product. A
positive product preserves the saved baseline. A non-positive ordered
product replaces the baseline with the current float before the difference
test (`0x0055F7B2..0x0055F7D4`). Thus a sign crossing does not accumulate the
difference across zero on this path.

The difference is computed in double, its sign bit is cleared using the
mask at `0x00F62F50`, and it is converted to float. Advancement requires an
ordered result strictly greater than the original float at `0x00FA47E0`,
`1.3089969158172607` (`0x0055F7D5..0x0055F810`). Equality and unordered
comparison take the return edge at `0x0055F7FE`. The constant is a numeric
threshold here. This evidence assigns no angle unit or physical gesture.

Phase 2 advances to phase 3 without setting the completion bit. A later
invocation entering phase 3 performs that write. The
[poll](tutorial-control-native-contract.md#waits) then reports done when
bit 0 is set. This static sequence establishes neither a frame count nor
the ordering of updates, wait installation and polling in an actual tutorial.

This selected constructor, installation and update path does not establish
an exhaustive writer set for either tutorial byte.

## Selected input writer and remaining edge

`STATIC`: the compact switch in `0x0055EFD0` maps handler argument `0x16`
through selector byte `0x0055F08F` and table cell `0x0055F080` to
`0x0055F00B`. That case reads the first float from its supplied payload at
`0x0055F00F` and stores it at receiver `+0x124` at `0x0055F026`.
The selector/table relation and the float copy were checked directly in the
original PE. `0x16` is the handler argument at this boundary, with no wire
opcode assignment.

The first unbound input edge is the producer and delivery of that payload's
first float to this camera instance. The selected writer establishes no
keyboard, mouse, gamepad, yaw or pitch meaning. It also does not enumerate
other writes through aliases, enclosing vectors or bulk copies. Actual
input values, event delivery, selected-owner lifetime and historical server
progression remain unknown. A particular control gesture cannot be adopted
as the completion rule from this evidence.

## Verification boundary

The executable size and digest were authenticated before analysis. A
Capstone 5.0.7 x86-32 decode of selected original-file windows, mapped through
the PE section table, supplied the operand and branch observations above.
Independent encoded displacement, immediate and signed-branch checks
corroborated the completion store and threshold return. In-memory mutations
of the completion-field operand and threshold-branch displacement were
rejected by those checks. RTTI, vftable cells and the compact switch were
read directly from the same identified input.

The cited instruction windows are selected evidence ranges. They establish
neither complete function extents nor caller completeness.
No client execution or historical tutorial observation was performed.
