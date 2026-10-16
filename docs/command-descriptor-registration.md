# Command descriptor registration

Clientbound `0x0132` supplies named command definitions. The first two
application bytes are a priority input and a selector, followed by a 32-byte
name field. The native receiver consumes them separately. Treating them as
one u16 command number loses that distinction.

The [native manifest](../manifests/command_descriptor_registration.json)
owns the exact retail binary identity, authenticated instruction extents,
field sources and constructor rules. The retained wire census and exact
capture locators are in
`xivl-captures:studies/command-registration/README.md` and its derived products.

## Definitions and construction

The table joins observed wire definitions to the native factory's branch
rule. Its class and callback columns require the selector global at
`0x0134C3FE` to be zero when the record is constructed.

| Name | Priority input | Selector | Conditional class | Callback |
| --- | ---: | ---: | --- | --- |
| `commandForced` | 11 | 0 | CommandBlock | `_onCommandEvent` |
| `commandDefault` | 10 | 0 | CommandBlock | `_onCommandEvent` |
| `commandWeak` | 6 | 0 | CommandBlock | `_onCommandEvent` |
| `commandContent` | 4 | 0 | CommandBlock | `_onCommandEvent` |
| `commandJudgeMode` | 6 | 0 | CommandBlock | `_onCommandEvent` |
| `commandRequest` | 0 | 1 | CommandNonBlock | `_onCommandRequest` |
| `widgetCreate` | 0 | 1 | CommandNonBlock | `_onCommandRequest` |
| `macroRequest` | 0 | 1 | CommandNonBlock | `_onCommandRequest` |

The route reaches implementation slot 49. With the `NullActorImpl` table
installed, `0x0076CA90` reads application byte 0 through `0x0075AEE0`, which
replaces zero with the default-priority byte at `0x01355296`. It copies byte 1
unchanged. Producer `0x00767B40` stores the name and the two resulting bytes
at record offsets `+0`, `+0x54` and `+0x55` in a pending owner vector. The
`LuaActorImpl` slot 49 is a no-op, so receiving a packet alone does not prove
that this producer ran.

During conditional player initialization, `0x006F3420` calls the record walk
at `0x00762CA0`. It passes each 0x58-byte record to `0x006F1C20`.
Equality of the selector with byte `[0x0134C3FE]` constructs `CommandBlock`
and stores the priority at descriptor `+0x5c`; inequality constructs
`CommandNonBlock` with only the name. Thus the request definition's zero
priority input does not become a nonblock scheduling priority. It is also
distinct from command-sheet priority -1, which selects the Lua name.

The selector and default-priority globals lie in the PE's virtual zero-fill,
as does event-type byte `0x0134C3FF`. Loading supplies initial zeros; these
are not raw file bytes or observed values at execution time. A targeted scan
of explicit absolute references found reads and comparisons, but does not
exclude writes through computed aliases.

## Remaining boundary

The first unresolved native input is the selected runtime descriptor returned
by `0x0071CA50` from the later player's `+0xfc` vector. That lookup returns
the first equal name without checking its vtable. The retained evidence does
not observe the receiving implementation, same-instance owner handoff,
runtime global values, completed initialization, insertion history, lifetime
or installed table for a particular later invocation. A separate compiled receiver body
at `0x0089D4F0` also calls the factory, but its wire-instantiation route is
unestablished.

This resolves the named input definitions and conditional class rules. It
does not prove an invocation selected one of those objects or passed the
execution and send gates. The [player command wire contract](player-command-wire-contract.md)
still owns the shared direct fallback and typed tail. Its first unresolved
server boundary is server consumption of the `0x012d` record queued through
`0x00DB06A0`.
