# Achievement rate consumer

Clientbound `0x019f` stores its second and third dwords in an achievement
cache, then reports a numerator and denominator to Lua. The third wire dword
is not passed to Lua as progress flags. The
[native contract](../manifests/achievement_rate_consumer.json) records the
authenticated instruction and script evidence.

The receiver copies application `+0`, `+4` and `+8`. The native update uses
the first as the achievement key, caches the other two, and looks up a client
maximum. `_onReceiveAchievementRate` receives the key, the progress count
clamped to that maximum using a signed comparison, and the maximum itself.
The list widget calculates `floor(numerator*100/denominator)` and formats
the progress text. The detail widget stores the same numerator and denominator.

The third dword supplies list-step completion bits through a separate native
predicate. It is not a generic completed/new/in-progress status field, and
overall achievement completion uses a separate bitmap. The closing dword at
`+0x0c` is not copied by this receiver and supplies no Lua argument; its
server purpose remains unresolved.

## List-step consumer

`_isDoneAchievementRateList(achievementId, step)` resolves through the native
registration at `0x0072A730`: callback thunk `0x0071E640` selects virtual
offset `+0x1D0` (slot 116). The observed MyPlayer table cell at `0x00FD7A2C`
contains `0x00706260`. The name string is at `0x00FD6328`.

The concrete body subtracts one from the supplied step at `0x007062DE`.
It first checks the overall achievement bitmap beneath `player+0x114`
(`0x007062E1..0x00706309`). A set overall bit returns true for ordinary
IDs, but IDs `0x3F2/0x3F3/0x3F4` take the list-cache path even then
(`0x0070630B..0x0070633F`). These are raw ID exceptions; this finding does
not assign their content meanings.

The cache path calls `0x006E3B90` at `0x00706346`, supplying the achievement
key and zero-based step. That helper uses the same map at context `+0x9C`
as the progress getter. A missing entry returns false. For a present entry,
`0x006E3BEB` reads node `+0x14`, the cached third wire dword (entry `+4`),
then tests it against `1 << (step - 1)` at `0x006E3BF3..0x006E3BFE`.
The x86 shift uses the low five count bits; that machine behavior does not
establish a supported out-of-range Lua step input.

The original `AchievementDetailWidget.setAchievementDetail` iterates steps
from 1 through `_countAchievementRateList(id)` and calls this predicate
with `(id, step)` (`root/proto4`, CALL PC 124; source 274-294). A true
result shows `IconControl_StepClear` and increments the cleared-step count
(PCs 127-134); false hides that icon (PCs 136-141). When the initially
computed percentage is at most zero and at least one step is clear, it
replaces its displayed numerator/denominator with
`(clearedStepCount, listCount)` and recalculates the progress presentation
(PCs 157-188; source 330-368). Thus the third dword can affect both step
icons and the detail widget's fallback progress display. It is not passed
as the native rate callback's third argument.

The separate `_isDoneAchievement` registration at `0x007298C0` selects
thunk `0x0071E550`, virtual offset `+0x194` (slot 101), table cell
`0x00FD79F0 -> 0x00705A70`. That body tests only the overall bitmap at
`0x00705AAA..0x00705AE5`; it does not read the rate map or step mask.
Setting list-step bits therefore does not by itself mark an achievement
earned or authorize a reward/title.

## Supported progress-response boundary

The existing single-direct-caller proof for outgoing `0x0135` is retained in
`xivl-decomp:config/retail_evidence/protocol-0x0135-single-direct-caller.json`;
its one-u32 sender is described by
`xivl-decomp:docs/net/wire-protocol.md#reviewed-outbound-builders`. It was
not rederived here.

For the `_getAchievementRate` branch that needs an uncached progress count,
`0x006E3B20` returns `-1` for no entry and otherwise the cached count.
`0x00706059..0x0070607F` accepts a nonnegative count, clamps it to the
client maximum, and returns it with that maximum. A negative cached count
takes the request path again. Maximum-zero, maximum-one and the overall
completion shortcuts in `0x00705EB0` remain separate branches.

One correctly routed `0x019F` application with the requested key at `+0`,
a nonnegative count at `+4`, and the desired list-step mask at `+8` is
sufficient for this cache/update consumer: `0x007046E9..0x007046F1` writes
both cached values before the ordinary Lua rate notification. A zero mask
means no set cache step bits on the predicate path; it is not a transaction
terminator. No completion marker, request serial or closing-dword test
appears in this update/getter path. This establishes a static consumer
contract, not a witnessed historical reply sequence or a claim that an
overall earned-state update is unnecessary elsewhere.

The remaining discriminator is a retained `0x0135`/`0x019F` transaction
establishing server publication policy and any additional accompanying
messages. No earn rules, database cardinality or title entitlement follow
from cache storage.

## Reproduction scope

The binary identity and range digests are in the native contract. New checks
used Python 3.12, pefile 2024.8.26 and Capstone 5.0.7 on the authenticated
original PE's raw-backed ranges. The Lua original, decoded payload and
canonical LF source matched both script manifests using the pinned
`unluac_2025_12_23.jar` (SHA-256
`98be0fa84ac73ca66dce2842a2e4512226f4c611b6500dc96415571fc5538fcc`).
The exact `_isDoneAchievementRateList` source query covered all 2,671
authenticated corpus members: one native-forwarding wrapper and this detail
widget caller. The native caller search covered direct relative E8/E9
references to `0x006E3B90` in executable PE sections and found the call at
`0x00706346`. Neither query excludes arbitrary indirect/dynamic callers.
