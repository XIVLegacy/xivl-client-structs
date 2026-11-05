# Lua base-library arity and the LGE type override

The retained base-library `select` returns zero values when its selected tail
is exhausted. Both the retained base `type` and the LGE `type` override
distinguish a missing argument from one explicit nil. The
[LGE bootstrap](lua-class-system.md#lua-stdlib-overrides-relevant-to-the-class-system)
replaces global `type`, so the base registration table alone cannot identify
the function a script calls.

## Source and method

Source: the retained FFXIV 1.23b `ffxivgame.exe`, input
`ffxivgame-1.23b` in [the input manifest](../manifests/retail_inputs.json).
That record pins its exact size and SHA-256. Addresses below are virtual
addresses with PE image base `0x00400000`.

The observations came from the authenticated original PE mapped in memory,
decoded with Capstone 5.0.7 and checked through bounded instruction assertions
and synthetic Lua-state paths under Python 3.12. The controls distinguished
missing arguments, nil, Boolean and numeric tags, and selected result counts.
String allocation, diagnostic formatting, engine-context retrieval and cleanup
were substituted by normal-return boundaries. Integer selectors were supplied
at the integer-check boundary.
These are static native contracts, not client execution or runtime observations.

## Retained base functions

The selected name/function pairs are actual table data:

| Name | Table entry | Function |
| --- | --- | --- |
| `select` | `0x01133040` | `0x00DDDA00` |
| `type` | `0x01133068` | `0x00DDD5C0` |

This table observation does not by itself prove installation into a particular
Lua state or the value later read from a script environment.

Base `type` calls the argument guard `0x00DD0C10` at `0x00DDD5C8` for
argument 1. The guard uses type API `0x00DCDCE0`, whose positive-index path
uses `0x00DCD900`. A missing slot yields type code `-1` and reaches argument
error helper `0x00DD09A0`. A present nil has type code 0 and passes the guard.
The calls at `0x00DDD5D0`, `0x00DDD5D7` and `0x00DDD5DE` then obtain the
type, resolve its name through `0x00DCDD00`, and push that name through
`0x00DCE1F0`. The nil control returns one string, `"nil"`.

The selected `select` window is `0x00DDDA00..0x00DDDA7F`. Its returns at
`0x00DDDA44` and `0x00DDDA7D` belong to different paths. Stopping at the first
return omits the numeric selector path. The latter uses stack count
`0x00DCDAF0`, type API `0x00DCDCE0` and integer guard `0x00DD0DB0`.

For six Boolean tail values, the selected numeric-path controls give:

| Selector | Additional tail values | C result count |
| --- | --- | --- |
| 6 | none | 1 |
| 7 | none | 0 |
| 8 | none | 0 |
| -1 | none | 1 |
| 7 | one nil | 1 |
| 7 | two nils | 2 |

Zero results are distinct from one nil result. A caller that expands every
result of the exhausted `select` passes no argument to the outer call.

## LGE override

The selected registration in `0x00CD8990` loads the name `type` at
`0x00CD8FA7`, supplies function `0x00D09240` at `0x00CD8FB4`, creates its
closure at `0x00CD8FBB`, and installs it at `0x00CD8FC2` through
`0x00CF3A70`. That helper calls `0x00DCE680` with the globals pseudo-index
`-10002`. This corroborates the override recorded by BCS-Y-0501 in
[the symbol catalog](../manifests/symbols.json).

The override obtains argument count through `0x00CF34C0` and
`0x00DCDAF0`. With no arguments, it calls diagnostic helper `0x00CD4220`
at `0x00D092BC` instead of returning a type-name string. One explicit nil
follows the generic type-name path through `0x00CF35A0`, `0x00DCDCE0` and
`0x00DCDD00`. It pushes one `"nil"` string through `0x00CF3360` and returns
one result. Boolean and numeric controls return their corresponding names.

The missing-argument diagnostic path calls `0x00CF38A0` at `0x00CD432F`,
then `0x00DCEBC0` at `0x00CF38C6`, then `0x00DD1E60` at `0x00DCEBC5`.
There is no branch around either of the first two calls in the selected
straight-line paths. For a valid synthetic state with no configured Lua error
function, the latter dispatches to `0x00DCF9C0` with error status 2.
Diagnostic context ownership, error protection and propagation remain separate
from this argument-count result.

## Script boundary

The selected native paths support a missing-argument diagnostic when an
exhausted base `select` feeds the installed LGE `type` override. They do not
establish that a particular script invocation reads those exact global values.
Later assignment, a different script environment, the actual diagnostic
context and error handling remain unbound. No menu failure, hang, callback
invocation or server response follows from this static result alone.
