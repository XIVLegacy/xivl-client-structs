# Soul of the Warrior armoire eligibility

The retained retail `MyPlayer._canStoreItem` returns false for catalog
`2000203`, Soul of the Warrior, for each ordinary category input from 1
through 4. This is a static result of the client eligibility native with a
valid `MyPlayer` receiver and two correctly typed integer arguments.

| Category argument | Catalog argument | Boolean result |
| ---: | ---: | --- |
| 1 | 2000203 | false |
| 2 | 2000203 | false |
| 3 | 2000203 | false |
| 4 | 2000203 | false |

## Evidence and method

The item identity comes from
`xivl-decomp:docs/script/equipment-soulstones.md`, the Important-item backing
table row `2000203`, at revision
`9289922570b30fbca503ae97202216809d8d4eb8`. That source names the catalog as
Soul of the Warrior and records its important-item backing. It supplies the
label, not the armoire eligibility result.

The [published native contract](player-world-native-contract.md#stored-item-lists)
and its
[`_canStoreItem` manifest row](../manifests/player_world_native_call_contract.json)
supply the registration, integer argument order, receiver dispatch and
decision rule. The `MyPlayer` routine at `0x007064D0` starts with false.
It asks `0x00714440` for catalog membership. A negative answer preserves
false. Only a nonnegative answer reaches `0x007153D0`, whose class result
is compared with category minus 1. Those published wrapper and caller
contracts were adopted rather than decoded again for this case.

The additional original-client check followed only catalog `2000203` through
the membership helper. The input was retail `ffxivgame.exe`, version
`2012.09.19.0001`, PE32 x86, image base `0x00400000`, size `15996808`
bytes and SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
matching [the input manifest](../manifests/retail_inputs.json).

An in-memory Capstone 5.0.7 decode with pefile 2024.8.26 established that
`0x00714440` loads the 32-bit argument from entry stack offset `+4` into
`EAX`. The selected compare path reaches `0x0071499A`, which sets every bit
of `EAX`. The plain return at `0x0071499D` therefore returns signed -1 and
performs no callee stack cleanup. The result follows from the authenticated
terminal operands, independently of the published negative-block locator.
Every selected operation and branch target was bound. There was no call or
nonstack memory read on the path after the argument load.

The decode was confined to the selected path inside
`0x00714440..0x00714E40`. The upper address is a next-entry bound, not a
claim about the helper's complete extent. The terminal check covered only
the two sequential instructions from `0x0071499A` through the first return.
No item set or other catalog path was enumerated. Since the result is
negative, the class helper is unreached and its body was not read.

## Interpretation boundary

False is the native's eligibility answer for these inputs. The native reads
neither the stored-item vectors nor a category range. The answer does not
depend on their current contents. The wider `PlayerBase` registration can
return no Lua values for a receiver that is not a `MyPlayer`.

This case does not establish an observed armoire interaction, a storage
transaction, server acceptance or an explanation for a click outcome.
Recordings that supplied an input do not prove those retail behaviors.
