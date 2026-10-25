# SpreadSheet native contracts

[`manifests/spreadsheet_native_call_contract.json`](../manifests/spreadsheet_native_call_contract.json)
records the static Lua call contracts of nine `SpreadSheet` natives. Three read
the row cache (`_getData`, `_isExistKey`, `_getAllKey`). Three are load
requests that yield the calling Lua thread (`_loadKeyTemporarily`,
`_loadKeySemipermanently`, `_loadAllKeyPermanently`). One releases rows
(`_unloadKey`). Two queue asynchronous loads without a yield (`_loadKeyAsync`,
`_loadMultiKeyAsync`). `_setFilename`, the tenth native of the class, is
recorded by the [widget contracts](widget-native-call-contract.md). Each row
gives the registration site, the receiver type check, the declared argument
and return lists, the reads, the effects on client state, the failure behavior
and whether the call yields. The contracts describe client marshalling and
state, not sheet content, the Lua wrapper logic or server behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `INFERRED` is a name or role taken from the
surrounding instructions that the bytes do not state. `unknown` was not
traced.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The instruction listings were decoded directly
from the PE bytes through the section table after the size and hash were
checked. Callers were found by scanning `.text` for `rel32` `call` and `jmp`
instructions, so virtual and indirect callers are not covered.

The native set comes from the script metadata. The per-row `corpusCallSites`
lists in the manifest carry the call-site lines from
`xivl-client-scripts:lua/napi_index.json`. They show that a script contains a
call, not that a script reaches it at run time. Every native here binds to the
`SpreadSheet` class through `gamedata/spreadsheet_u`. `_loadKeyAsync` has no
entry in the index and so no call site.

## Registration and dispatch

The registrars run from one switchboard, slot 2 of the `SpreadSheet` vftable
`0x00FD7744`, at `0x00758670`. It tests the byte at its argument `+0x0E` before
each step. A nonzero byte adds 1 to the word at `+0x0C` and skips the
registrar. The order and the single `rel32` caller of each registrar are:

| Order | Native | Registrar | Caller |
| ---: | --- | --- | --- |
| 1 | `_setFilename` | `0x00746E70` | `0x0075868C` |
| 2 | `_loadKeyTemporarily` | `0x00746FC0` | `0x007586A1` |
| 3 | `_getData` | `0x00758520` | `0x007586B6` |
| 4 | `_isExistKey` | `0x00750BC0` | `0x007586CB` |
| 5 | `_getAllKey` | `0x00750D10` | `0x007586E0` |
| 6 | `_loadKeySemipermanently` | `0x00747110` | `0x007586F5` |
| 7 | `_unloadKey` | `0x00747990` | `0x0075870A` |
| 8 | `_loadAllKeyPermanently` | `0x00747260` | `0x0075871F` |
| 9 | `_loadKeyAsync` | `0x007473B0` | `0x00758734` |
| 10 | `_loadMultiKeyAsync` | `0x00747600` | `0x0075874D` |

Every registrar builds the return list first and the argument list second. It
zeroes EDI, loads the callback into ESI, calls a wrapper and installs the
functor through `0x00CCCAD0` under the name literal. The adjustment is 0 in
every row. Registration, the type registry and argument marshalling follow the
[widget contract framework](widget-native-call-contract.md#registration).

Two wrappers appear. Each constructs the `0x58` byte functor in place at the
index held at wrapper `+0x10` of the vector at wrapper `+0x04`, with a bound
test that calls `0x009D22B4`, and increments the index.

| Wrapper | Owner class | Holder vftable | Used by |
| --- | --- | --- | --- |
| `0x00746CB0` | `SpreadSheet` | `0x00FD77D0` | the three load requests, `_unloadKey` |
| `0x00746D60` | `SpreadSheet`, const | `0x00FD77DC` | `_getData`, `_isExistKey`, `_getAllKey`, `_loadKeyAsync`, `_loadMultiKeyAsync` |

Both holders share the invoke routine `0x00746980`. It casts the receiver with
`0x009DA6CC` from `LuaControl` to `SpreadSheet`. A null cast returns false
without calling the callback, and the `0x00D19B70` failure path reports it as
in the [talk contracts](talk-native-contract.md#registration-and-dispatch).
A successful cast adds the adjustment stored at holder `+0x0C` and calls the
member function pointer at holder `+0x08` with `ExecuteParameters` on the
stack. A call on a Lua value that is not a sheet fails before any callback
code runs.

Every callback that reads arguments tests the cell vector size before each
index and calls `0x009D22B4` when it is too short. The
[target cursor record](target-cursor-native-contract.md#selection-and-the-failure-path)
records that routine as the invalid-parameter route that ends in a process
terminate. The same call guards an empty key vector and a cache find that
returns the head sentinel.

## Contracts

Argument indices count internal `ExecuteParameters` cells after the receiver.

| Native | Arguments | Returns | Callback | Registrar | Yields |
| --- | --- | --- | --- | --- | --- |
| `_getData` | `int`, `int` | `Which<int,float,bool,Utf8String>` | `0x0070A720` | `0x00758520` | no |
| `_isExistKey` | `int` | `bool` | `0x00707150` | `0x00750BC0` | no |
| `_getAllKey` | none | `IntegerArray` | `0x00707260` | `0x00750D10` | no |
| `_loadKeyTemporarily` | `int`, `int` | none | `0x006F0840` | `0x00746FC0` | yes |
| `_loadKeySemipermanently` | `int`, `int` | none | `0x006F0AD0` | `0x00747110` | yes |
| `_loadAllKeyPermanently` | none | none | `0x006F0C10` | `0x00747260` | yes |
| `_unloadKey` | `int`, `int` | none | `0x006F61F0` | `0x00747990` | no |
| `_loadKeyAsync` | `int` | none | `0x006E68B0` | `0x007473B0` | no |
| `_loadMultiKeyAsync` | `int`, `int`, `LuaControl*` | none | `0x006E6910` | `0x00747600` | no |

The manifest rows carry each name literal, name reference, install call,
callback load and list builder. The argument list builders are `0x00583CE0`
for two ints, `0x00728C20` for one int, `0x00747500` for two ints and a
control and `0x0072B440` for none. The return list builders are `0x00728B70`
for a bool, `0x0072BBF0` for an `IntegerArray`, `0x00747910` for the `Which`
and `0x0072B440` for none.

## Sheet state

The callbacks work on four objects. The offsets below are `STATIC` reads. The
roles are `INFERRED` except where the widget contracts record them.

| Object | Field | Role |
| --- | --- | --- |
| `SpreadSheet` | `+0x60` | Filename string, assigned by `_setFilename`. |
| `SpreadSheet` | `+0xB4` | Sheet handle, the result of manager slot 1. |
| `SpreadSheet` | `+0xB8`, `+0xBC` | Set of asynchronously requested keys and its head. |
| `SpreadSheet` | `+0xC4` | Row map. Head at `+0xC8`, count at `+0xCC`, notifier at `+0xD0`, second container at `+0xD4`. |
| `SpreadSheet` | `+0xD8` | Address passed as request `+0x70` by `_loadKeyTemporarily`. |

The sheet manager is reached by reading the dword at the address `0x00CC7510`
returns and then the dword at `+0x04` of it, and passing that value to
`0x0075F5A0`. The routine reads two dwords through its receiver and tail-calls
`0x004D74C0`, which returns the dword at `+0x174F8`. Manager slot 1 takes the
filename string and returns the handle. The handle is a
`Component::Excel::ExcelSheet` (vftable `0x0110C6D4`) and the manager is a
`Component::Excel::ExcelModule` (vftable `0x01108C00`), see
[Filename lookup](#filename-lookup).

The callbacks call these handle slots. The roles are `INFERRED` from use.

| Slot | Offset | Use |
| ---: | --- | --- |
| 1 | `+0x04` | Busy test in the load poll. |
| 2 | `+0x08` | Column type from a column id, the number of its schema name. |
| 14 | `+0x38` | Pointer to a dword vector of key ranges. |
| 16 | `+0x40` | Byte for a column id. The poll keeps the ids with a nonzero byte. |
| 17 | `+0x44` | Column id bound, the `column_max` attribute of the sheet node. |

The slot `+0x38` vector is a list of pairs. A pair is a start key and a key
count. `_isExistKey` tests `start <= key <= start + count - 1` with signed
compares, and that scan is the only reader that treats the dwords as pairs.
The pair reading of the other readers is `INFERRED` from it.

## Cached rows and _getData

The row map at `SpreadSheet` `+0xC4` is a tree keyed by a signed dword at node
`+0x0C`, with a nil byte at `+0x21`, a row counter at `+0x10` and a cell tree
at `+0x14`. The cell tree is keyed by a signed dword at `+0x0C` with a nil
byte at `+0x1D`. Its node holds a value pointer at `+0x14` and a tag byte at
`+0x18`. `0x0071CAC0` and `0x00CA73F0` are the finds. Each takes the lower
bound and returns it only when its key equals the argument, otherwise the head
sentinel.

`_getData` reads two ints, finds the first in the row map and the second in
the cell tree of the found row, and pushes the cell. It loads nothing and
requests no yield. A key that is absent from either tree reaches the
invalid-parameter route. The first int is a row key and the second a column
index, an `INFERRED` reading from the poll, which fills the outer tree by key
and the cell tree by a zero-based column counter.

`0x007584B0` pushes the cell by its tag.

| Tag | Cell | Push |
| ---: | --- | --- |
| 0 | int | `0x00584F70` |
| 1 | float | `0x007489D0` |
| 2 | bool | `0x00748870` |
| 3 | Utf8String | `0x007487C0` |
| 4 | Nil | `0x00748920`, a tag 6 cell |
| other | none | nothing is appended |

The return list is one `Which` over int, float, bool and `Utf8String`.
`0x00747910` calls `0x00747860`, which builds the four alternatives from
registry entries 0 to 3 through `0x00747750` and appends the `Which` through
`0x00CCA2D0`. The `Which` push slot `0x00CFA850` pushes nil for a tag 6 cell
and otherwise asks each alternative whether it matches the cell.

The poll converts a column of type `t` as follows. The table is the jump table
at `0x00748778` indexed by `t - 1` with an unsigned bound of 9.

| Column type | Schema name | Reader | Cell |
| ---: | --- | --- | --- |
| 1 | `bool` | `0x0078E280` | bool |
| 2 | `s8` | `0x0078E2A0`, sign-extended byte | int |
| 3 | `u8` | `0x0078E2C0`, zero-extended byte | int |
| 4 | `s16` | `0x0078E2E0`, sign-extended word | int |
| 5 | `u16` | `0x0078E300`, zero-extended word | int |
| 6 | `s32` | `0x0078E320`, dword | int |
| 7 | `u32` | none | Nil |
| 8 | `f16` | none | Nil |
| 9 | `float` | `0x0078E340` | float |
| 10 | `str` | `0x0078E360` | Utf8String |
| 0, 11, other | empty name, `bin` | none | Nil |

The schema names and their numbers come from the lookup `0x00CAF390`. It
builds twelve static `Utf8String` objects at `0x01376E98` with stride `0x54`
on first use. Their literals are the empty string, `bool`, `s8`, `u8`, `s16`,
`u16`, `s32`, `u32`, `f16`, `float`, `str` and `bin`, and the position in this
array is the column type. The lookup compares the schema parameter with each
object through `0x00445D20` and returns the position, or 0 for no match. The
sheet constructor `0x00CB04B0` calls it with the text value at `+0x68` of every
child of the `type` node of the sheet (static object `0x01377398`, literal
`type`) and stores the result as a byte at `+0x10` of the sheet, indexed by
column position. Handle slot 2 (`0x00CAF330`) reads that byte through the column
position map at sheet `+0x14`. The dword table at `0x0130BE4C` gives the stored
width of each type and the reader adds it to the row width at sheet `+0x18`.
The widths are 1 for types 1 to 3, 2 for types 4 and 5, 4 for types 6 and 7,
2 for type 8 and 4 for type 9. Type 8 is therefore the 16 bit `f16` and types
6 and 7 are the 32 bit `s32` and `u32`. The signedness and width of the readers
of types 1 to 5, 9 and 10 agree with their schema names. The dword reader is
type 6, so `s32` is the dword reader and `u32` and `f16` columns read Nil
through the shared jump table entry. This is `STATIC`.

## Key ranges

`_isExistKey` reads one int and calls slot `+0x38` on the handle at `+0xB4`
without a null test. A null or empty vector gives false. The result is pushed
through `0x00748870`.

`_getAllKey` takes no argument and calls the same slot. It pushes the dword
count through `0x00584F70` and then each dword of the vector. The declared
return is an `IntegerArray`. Its push slot `0x00CFA640` reads a tag 0 count
cell, calls `0x00CF3280` with it, and for each following int cell pushes the
index from 1 and the value through `0x00CF3300` and stores them through
`0x00CF3400`. Lua therefore receives one table that holds the raw vector under
the keys from 1. A Nil cell (tag 6) at the count position pushes nil and
advances the index by 1. Any other count cell that is not tag 0 throws the
literal `bad cast` through `0x009D1B9F`, and so does every element cell that
is not an int (tag 0). Nil applies to the count cell only. That the three
routines are table creation, number push and table store is `INFERRED` from
the use pattern.

## Load requests

The three load requests build a `LoadDataResumeChecker` and yield the calling
thread. `0x00725A50` constructs it in a `0x94` byte allocation from nine stack
arguments.

| Argument | Stored at | Content |
| ---: | --- | --- |
| 1 | `+0x04` | Filename, passed to `0x00447200`. |
| 2 | `+0x58` | Sheet manager from `0x0075F5A0`. |
| 3 | `+0x5C` | Address of `SpreadSheet` `+0xB4`. |
| 4 | `+0x60` | Address of `SpreadSheet` `+0xC4`, the row map. |
| 5 | `+0x64` | Low key. |
| 6 | `+0x68` | High key. |
| 7 | `+0x6C` | Function end callback, or null. |
| 8 | `+0x70` | Address of `SpreadSheet` `+0xD8`, or null. |
| 9 | `+0x90` | Flag byte. |

The vftable is `0x00FD6160` with the destructor at `0x00725C60`, the poll at
`0x00747FB0` and the slot 2 finish at `0x00725B20`. No slot reads the flag
byte at `+0x90`. The callbacks differ in these arguments.

| Native | Low key | High key | Callback `+0x6C` | `+0x70` | Flag |
| --- | --- | --- | --- | --- | --- |
| `_loadKeyTemporarily` | argument 0 | argument 1 | found or created | `+0xD8` address | 1 |
| `_loadKeySemipermanently` | argument 0 | argument 1 | null | null | 1 |
| `_loadAllKeyPermanently` | first dword of the key vector | last pair start plus last pair count | null | null | 0 |

Each callback then yields through `0x00CD2860` with the request on the Lua
thread at `ExecuteParameters` `+0x08` and returns at once. The yield protocol
is the one of the message pool checker in the
[talk contracts](talk-native-contract.md#message-and-log-pools). The poll ends
with the dword at `0x01377ECC` when the pending key count at request `+0x8C`
is 0 and with the dword at `0x0130CECC` otherwise.

The poll proceeds as follows.

1. A null handle at `+0xB4` is replaced by manager slot 1 called with the
   filename. A handle that is still null, or a nonzero result of handle slot 1
   on the new handle, ends the poll with the dword at `0x0130CECC`, `INFERRED`
   to be the not done result. A handle that was already set skips this test.
2. The column id list at request `+0x74` is built once. Each id from 0 below
   the column id bound is kept when slot `+0x40` returns a nonzero byte.
3. While the pending set at `+0x84` is empty, the poll scans the key vector.
   Each key `k` with low <= `k` <= high that lies inside a range is inserted
   into the pending set and, when request `+0x6C` is nonzero, into the key set
   at callback `+0x18`.
4. For each pending key the row map is searched. A found row has its counter
   at `+0x10` incremented and the key leaves the pending set. A missing row is
   read through a reader that `0x0078E220` builds from the handle and the key
   and `0x0078E270` tests. An available row is converted column by column with
   the type table above and inserted into the row map. A row that is not
   available stays pending.
5. A nonzero request `+0x70` makes the poll compute a size of the row through
   `0x006EE9B0` and call `0x00CD2BC0` and `0x00CD2BE0` on its third argument.
   The result of the size computation is not stored in the traced code.

The initial counter of an inserted row was not traced.

`_loadAllKeyPermanently` reads the key vector through slot `+0x38` and does
not null test the handle at `SpreadSheet` `+0xB4`. The high key is the last
dword plus the second last dword, which is one past the last key of the last
range. A null, empty or single-dword vector reaches `0x009D22B4`. The null and
empty tests at `0x006F0C4C` to `0x006F0C5D` catch the first two and the
unsigned bound check on the count minus 2 at `0x006F0C8A` rejects a one-dword
vector.

## Function end release

`_loadKeyTemporarily` also manages a `LoadDataFunctionEndCallback`. It builds a
finder with `0x00716EC0` and searches the callbacks registered on the Lua
thread through `0x00CD2630`. The finder match slot `0x00716F70` casts a
candidate to `LoadDataFunctionEndCallback` and compares the candidate dword at
`+0x04` with the finder dword at `+0x04`, so one callback exists per thread and
sheet. With no match the callback allocates `0x28` bytes, reads two thread
values through `0x00CD2680` and `0x00CD2660`, constructs the callback through
`0x0071DB70` and registers it through `0x00CD28C0`.

The constructor stores the sheet at `+0x04`, the row map address at `+0x08`,
the `+0xD8` address at `+0x0C`, the dword of the `0x00CD2680` value at `+0x10`
and the word of the `0x00CD2660` value at `+0x14`. It builds a key set at
`+0x18` and stores the byte 1 at `+0x24`. Slot 1 at `0x007462F0` finds each
key of that set in the row map and calls `0x006F6160` on it. That the engine
invokes slot 1 when the registering Lua function ends follows from the class
name and was not traced.

`0x006F6160` decrements the counter at row node `+0x10`. At 0 or below it
erases the node through `0x00745710`. When the row map is then empty, the
container at map `+0x10` is empty and a notifier at map `+0x0C` is set, it
calls slot 1 of the notifier with the sheet.

`_unloadKey` reads two ints and finds the callback through the same finder. For
each key from the first int to the second inclusive it finds the row. A key
with no row is skipped. A found row is released through `0x006F6160`. A
callback that exists then drops the key from its set through `0x0071E960`, which
also clears the callback byte at `+0x24`. A first int above the second runs no
iteration. `_unloadKey` neither yields nor returns a value.

## Asynchronous loads

`_loadKeyAsync` reads one int and calls `0x0075CF30` on the object
`[[[R]+0x04]+0xFC]`, where `R` is the address that `0x00CC7510` returns (bytes
`0x006E68E5` to `0x006E68FC`). The call passes the engine handle, the receiver
identity address and the key. The object keeps one pending request: an
identity dword, a key dword and a flag byte. A set flag resolves the stored
identity, casts it to `SpreadSheet` and releases the stored key through
`0x006F63A0`. The call then stores the new identity, key and flag and requests
the key through `0x006F0D80`.

`0x006F0D80` tests the key against the key vector. A cached row has its counter
incremented. An uncached key inside a range joins the set at `SpreadSheet`
`+0xB8` and is handed to `0x00CC73E0`. A key outside every range only runs the
empty cache notifier test. `0x006F63A0` removes the key from the set and
releases one counter of the cached row. Neither call yields.

`_loadMultiKeyAsync` reads two ints and a control, converts the control to an
identity through `0x00CC73B0` and calls `0x0076E620` on the same object. The
callee walks its list at `+0x0C` for a node whose receiver identity at `+0x08`
and control identity at `+0x0C` match and whose byte at `+0x2C` is 0. A match
releases every key in its vector through `0x006F63A0` and is erased through
`0x00783CD0`. A new node is then built through `0x00784FB0`. For each key from
the first int to the second inclusive, `0x006DFFC0` tests the key against the
key vector, and a passing key is requested through `0x006F0D80` and appended
to the node vector. The node is appended to the list.

## Filename lookup

`_setFilename` passes the filename to slot 1 of the manager. The manager is an
`ExcelModule`, `INFERRED` from its type and from the five handle slots of this
record, which match the bodies of `ExcelSheet`.

| Slot | Handle role in this record | `ExcelSheet` routine |
| ---: | --- | --- |
| 1 | Busy test | `0x00CAF650`, scans the deque at `+0x2C` |
| 2 | Column type from a column id | `0x00CAF330` |
| 14 | Key range vector | `0x00CAF350`, returns `this +0x44` |
| 16 | Byte for a column id | `0x00CAF360`, tests the position map byte against `0xFF` |
| 17 | Column id bound | `0x00CAF380`, returns the byte at `+0x09` that the constructor fills from the `column_max` attribute |

`ExcelModule` slot 1 (`0x00C981D0`) looks the filename up in the map at module
`+0x2C` through `0x00800EC0`, with the string itself as the key. An absent key
returns 0. A found entry holds the sheet at entry `+0x60`. The routine calls
handle slot 14 and returns the sheet only when the vector at sheet `+0x44` is
nonempty, otherwise 0. A sheet whose key ranges have not been read therefore
gives the null handle.

The map is filled by the node visitor `0x00C98580` of the module. For each node
it reads these attributes through slot 7 of the node object (`+0x1C`). The names
come from static `Utf8String` objects whose initializers hold the literals.

| Object | Literal | Use |
| --- | --- | --- |
| `0x01376258` | `name` | Map key of the sheet. |
| `0x01376200` | `param` | Passed on to the sheet constructor. |
| `0x01376150` | `mode` | With module `+0x38` equal to 0 a node whose mode is `server` (object `0x013760A0`) is skipped. With 1 a node whose mode is `client` (object `0x013760F8`) is skipped. |
| `0x013761A8` | `lang` | A nonempty value must match the language value at module `+0x14`, otherwise the node is skipped. |
| `0x013762B0` | `infofile` | A nonempty value takes a separate branch that calls slot 2 of the object at module `+0x08`. |

A node whose `name` is already in the map destroys the old sheet through its
vftable slot 0 and installs a new `ExcelSheet` from the node through
`0x00CB04B0`. A new name inserts a new entry. The filename therefore selects a
sheet by the exact `name` attribute of a schema node, after the `mode` and
`lang` filters, with no path or extension handling, and a later node of the
same name replaces an earlier one. That the empty static string at
`0x0137B248` is the comparand of the emptiness tests is `INFERRED`.

The set of documents the visitor reads and the load that feeds it were not
traced. The sheet inventory
`xivl-client-data:manifests/sheet_inventory.csv`
lists sheet names with a resource id and a source of `game_schema`,
`extrasheets` or `var_schema`. Its row `passiveGL_craft` gives the resource id
`0x01030068` with the source `game_schema`. The script metadata
`xivl-client-scripts:lua/scripts/gamedata/spreadsheet.calls.json` places the
only `_setFilename` call at line 11 of `gamedata/spreadsheet`. The filename
arrives from `AreaBaseClass.prepareSpreadSheet` through
`_createActor(name, "SpreadSheet", name~=nil, sheetName)` (see the
[_createActor contract](create-actor-native-contract.md)), and the one literal
that `xivl-client-scripts:docs/passivegl-craft-columns.md` records for it is
`passiveGL_craft`. The other filename strings are not in the tracked metadata.

## Related natives

`_loadKeyAsync` is registered ninth in the switchboard and has no entry in the
script index, so no script calls it. `_setFilename` is registered first and is
recorded by the widget contracts.

## Ledger rows

These rows of the unimplemented ledger now have a registration, argument list,
return list, receiver check and callback contract: `_getData`, `_isExistKey`,
`_getAllKey`, `_loadKeyTemporarily`, `_loadKeySemipermanently`,
`_loadAllKeyPermanently`, `_unloadKey` and `_loadMultiKeyAsync`. A client that
implements them still needs the manager, the key range vectors, the column
types and the cell values from decoded static client data, which this record
does not supply.

## Open

- The row reader bodies, the documents that the `ExcelModule` visitor reads and
  the object at module `+0x08`.
- The initial counter of a cached row, the object at `SpreadSheet` `+0xD8`,
  the notifier at `+0xD0`, and the flag byte at request `+0x90`.
- Whether the engine runs `LoadDataFunctionEndCallback` slot 1 at the end of
  the registering function, and the thread values behind `0x00CD2660` and
  `0x00CD2680`.
- The body of `0x00CC73E0` and the path from an asynchronous request to a
  cached row.
- Whether the Lua wrapper in `gamedata/spreadsheet_u` adjusts the key or
  column arguments before the native call.
- The process behavior of the invalid-parameter route for an absent key.

The ranked list of the next natives lives in the
[fade, actor and group contracts](fade-actor-group-native-contract.md#open).

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
Then decode listings from the verified PE bytes. The listings behind this
record came from a Capstone 5.0.7 x86-32 decode of the file through its
section table. With explicit project and JDK bindings and a new absolute
output path, the repository route for function listings is:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpFunctionListing.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Switchboard and registrars | `0x00758670,0x00746FC0,0x00758520,0x00750BC0,0x00750D10,0x00747110,0x00747990,0x00747260,0x007473B0,0x00747600` |
| List builders and wrappers | `0x00583CE0,0x0072B440,0x00728C20,0x00728B70,0x0072BBF0,0x00747910,0x00747860,0x00747750,0x00747500,0x00746E10,0x00746CB0,0x00746D60,0x00746B10,0x00746BE0,0x00746910,0x00746A30,0x00746980` |
| Callbacks | `0x006F0840,0x006F0AD0,0x006F0C10,0x006F61F0,0x0070A720,0x00707150,0x00707260,0x006E68B0,0x006E6910` |
| Cache reads | `0x0071CAC0,0x00CA73F0,0x007584B0,0x00758440,0x00748920,0x00583F70,0x00CFA640,0x00CFA850` |
| Load request | `0x00725A50,0x00747FB0,0x00725B20,0x00725C60,0x00747ED0,0x006EE9B0,0x0075F5A0,0x004D74C0` |
| Function end callback | `0x00716EC0,0x00716F70,0x0071DB70,0x007462F0,0x006F6160,0x0071E960,0x00CD2630,0x00CD2660,0x00CD2680,0x00CD28C0,0x00CD2860` |
| Asynchronous loads | `0x0075CF30,0x006F0D80,0x006F63A0,0x006DFFC0,0x0076E620` |

A callback address may not be a function entry in the analyzed program. Read
such a callback as an instruction listing from its address. Compare every
store, compare and call with the address named in the manifest facts. No
decompiled body or ignored export is a tracked evidence dependency.
