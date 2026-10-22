# Generic _progFunc native contract

[manifests/progfunc_native_call_contract.json](../manifests/progfunc_native_call_contract.json)
records the generic wrapper representation, the Lua type handling of each
argument position, the installed callback with its operation ids, and the
failure behavior.

Each fact carries a tier. `STATIC` is read directly from instructions or data
at the cited addresses. `INFERRED` is a name or role taken from surrounding
instructions or from a tracked catalog that the bytes do not state. `unknown`
was not traced.

## Metadata

FINAL FANTASY XIV 1.23b, build
`2012.09.19.0001`. The identified `ffxivgame.exe` is `15996808` bytes,
SHA-256 `9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`,
with image base `0x00400000`. These are static client observations.

The wrapper representation facts used bounded read-only ghidra-cli instruction
listings and decompilation from the identified analyzed program. The callback,
Lua type handling and failure facts were read from instruction listings decoded
directly from the PE bytes through the section table, after the executable size
and full SHA-256 were verified. Callers were found by scanning `.text` for
`rel32` `call` and `jmp` instructions, so virtual and indirect callers are not
covered. Addresses are absolute VAs.

The output-table recipe maps VA `0x00D09F90` through the authenticated PE32
section table and reads exactly four little-endian DWORDs. It rechecks the
full executable size and hash before the fixed metadata read. No raw bytes,
retained logs or decompiled bodies are public evidence dependencies.

## Locators

The tracked catalog associates `_progFunc` with registration `0x00CD7920`,
implementation `0x00D09CD0`, and name pointer `0x0130D520`:
`xivl-client-structs:manifests/remaining_templates_attribution.json`,
`templates[regVa=0x00CD7920]`. The catalog relationship is also recorded in
`xivl-client-structs:manifests/lua_to_opcode.json`, `_progFunc`.

## Observations

Registration writes two DWORDs into an eight-byte payload and captures that
payload with implementation `0x00D09CD0`. Invocation selects capture 1 through
index `-0x2713`, then calls payload offset 4 with payload offset 0 and local
marshalling storage. Locators: `0x00CD7931..0x00CD7950`,
`0x00DCE2EF..0x00DCE356`, `0x00D09E19..0x00D09E3B`, and
`0x00DCD93C..0x00DCD95A`.

The input loop examines positions 1 through the smaller of the stack-slot
count and 8. Zero positions still reach dispatch. The local initializer gives
eight input records and four result records internal tag 1. Each 12-byte
record points from offset 4 to its own zero byte at offset 0. Result records
begin at local base `+0x60`. Locators: `0x00D09D3D..0x00D09D6B`,
`0x00D09E0B..0x00D09E19`, and `0x00D09FFC..0x00D0A0C1`.

The four-DWORD table at `0x00D09F90` selects these output cases:

| Internal tag | Case | Emitted VM representation |
|---|---|---|
| 0 | `0x00D09E57` | VM tag 1 with normalized 0-or-1 DWORD payload |
| 1 | `0x00D09E72` | VM tag 0 with no payload write |
| 2 | `0x00D09E7D` | VM tag 3 with signed-32 payload converted to double |
| 3 | `0x00D09E96` | VM tag 3 with float32 payload widened to double |

Each supported case advances the stack top by 16 bytes. The verified push
cores are `0x00DCE150..0x00DCE162`, `0x00DCE170..0x00DCE188`, and
`0x00DCE360..0x00DCE37D`. Untouched result defaults therefore emit four
VM-tag-0 slots on the normal path. A tag outside 0 through 3 skips insertion
for that record. The normal native return still declares 4 results:
`0x00D09E47..0x00D09E50`, `0x00D09EB6..0x00D09EBF`, and
`0x00D09F0E..0x00D09F36`.

### Lua type handling per position

VM tags are the Lua 5.1 type codes. `0x00DCDCE0` returns the tag of a stack
index, with `-1` for an index past the stack, and `0x00DCD900` resolves the
index. Tags 0 and 1 are nil and boolean through the push core `0x00DCE150` and
the boolean core `0x00DCE360`. Tags 3, 4, 5, 6 and 7 are number, string, table,
closure and userdata by the stores at `0x00DCE170`, `0x00DCF0EF`, `0x00DCD972`,
`0x00DCE349` and `0x00DCED22`. Tags 2 and 8 are light userdata and thread by
the Lua 5.1 code assignment (`INFERRED`).

The marshaller classifies each position by these steps, all `STATIC`:

1. The first predicate `0x00CF36E0` calls `0x00DCDD50`. That returns 1 for VM
   tag 3 and otherwise returns 1 when `FUN_00DDE8B0` succeeds on the slot.
   `FUN_00DDE8B0` returns the slot for tag 3, runs the string conversion for
   tag 4 and returns zero for every other tag. It writes its result into a
   16-byte local, not into the Lua stack, so no stack value is mutated.
2. A position the first predicate accepts takes the classifier `0x00CF3670`.
   It is true only when the raw VM tag is 3 and the number equals its 64-bit
   truncation. True stores a signed 32-bit payload with internal tag 2. False
   stores a float32 narrowing with internal tag 3.
3. A position the first predicate rejects takes `0x00CF3700`, which is true
   only for VM tag 1. True stores the normalized 0-or-1 byte with internal
   tag 0. False leaves the initialized record, internal tag 1.

| Lua value | Record |
|---|---|
| nil, light userdata, table, function, userdata, thread | unset, internal tag 1 |
| `true`, `false` | internal tag 0, byte 1 or 0 |
| number with an integral value inside the int64 range | internal tag 2, signed 32-bit |
| other number, including fractions, NaN and infinities | internal tag 3, float32 |
| string that `FUN_00DDE8B0` converts, such as `"7"` or `"7.5"` | internal tag 3, float32, never tag 2 |
| string that `FUN_00DDE8B0` rejects, such as `"abc"` or `""` | unset, internal tag 1 |

The classifier tests the raw VM tag, so a numeric string is never an integer
record. The string `"7"` is the float32 `7.0` with internal tag 3, and a
callback that requires internal tag 2 rejects it. Arguments past position 8 are
never examined. A nil in the middle keeps its position and stays unset.

### String conversion

`FUN_00DDE8B0` (`0x00DDE8B0..0x00DDE8F3`) is the Lua 5.1 value-to-number
conversion in shape. It returns a tag-3 slot unchanged, converts a tag-4 slot
through `0x00DDE360` and rejects every other tag. The string bytes start at
the string object `+0x10`.

`0x00DDE360..0x00DDE408` is the Lua 5.1 string-to-number routine in shape. It
calls the CRT floating-point parser `0x009DBB7B` on the string and takes the
stop pointer. A stop pointer equal to the start rejects the string. When the
stop character is `x` or `X` it reparses the whole string through the CRT
integer parser `0x009D8B4C` with base 16, adds 2^32 to a result that is
negative as a signed 32-bit value, and takes the stop pointer from that call.
It then accepts the string when the stop character is the terminator. Otherwise
it skips characters that the CRT class helper `0x009D825A` accepts, taken as
white space (`INFERRED`), and accepts the string only when the stop character
is then the terminator. Leading white space handling, the decimal and exponent
grammar, and `inf` or `nan` text belong to the CRT parser and are not traced.

### Integer record conversion

The truncation helper `0x009D6636` runs for the classifier comparison and the
CRT helper `0x009D6600` produces the 32-bit payload. `0x009D6600` branches on
the CRT flag at `0x0137B8E8`. A nonzero flag selects `cvttsd2si`, which returns
`0x80000000` for any value outside the signed 32-bit range. A zero flag falls
through to `0x009D6636`, whose `EAX` result is the payload. The flag gates the
CRT `memset` and the floating-point helpers that reference it and is taken as
the SSE2 availability flag (`INFERRED`). The initial value is not traced. The
classifier compares with an ordered equality, so NaN, infinities and
magnitudes beyond the int64 range are float32 records.

## Callback

The registration site passes object `0` and function `0x0075CE70` through the
thunk `0x00CC9B00` to `0x00CD7920`, so the payload holds `0` and `0x0075CE70`.
Locators: `0x00CC9B00..0x00CC9B02` and `0x0057AAC5..0x0057AACE`.

`0x0075CE70` is a `cdecl` function that ignores its first argument. It loads
the global pointer at `0x0134BB00`, takes the sub-object at `+0x54C` through
`0x004D7480`, and calls `0x0059F680` on it with the marshalling storage. The
setter `0x0075CE90` writes the global and is called from the registration
function at `0x0057AABB`. The sub-object constructor `0x0059F600` stores its
owner at `+4`. The object constructor `0x004DBF40` builds the sub-object at
`+0x54C` (`0x004DC04E`) and stores two constructor arguments at `+0x4F4` and
`+0x4F8` (`0x004DC013`, `0x004DC007`). The global is therefore an object of the
class that `0x004DBF40` constructs (`INFERRED`).
`xivl-client-structs:manifests/0x00D6_state_flag_pipeline.json`, `step4`
records `FUN_004D73B0` as the getter of the `+0x4F4` field.

`0x0059F680..0x0059F783` is the installed callback. It reads the first input
record as an integer operation id and dispatches on it:

| Id | Behavior |
|---|---|
| 0 | Needs a second integer record. A third integer record is optional and defaults to `-1`. Calls `0x0066ECA0` on the table at owner `+0x4DC` with those two values. |
| 1 | Needs a second integer record. Calls `0x0066F620` on the same table with it. |
| 3 | Writes the signed 32-bit DWORD at `+0x20` of the object stored at owner `+0x4F4` into result record 0 with internal tag 2. Reads no other input. |
| any other value | Returns without touching a result record. |

Every integer read checks the record's internal tag against 2 first. The first
record is checked at `0x0059F69A`, the second at `0x0059F6FF` for id 1 and
`0x0059F74C` for id 0, and the optional third at `0x0059F738`. A failed check
on the first or second record throws, see below. A third record whose tag is not
2 is treated as absent. Because the check is on the internal tag, an integral
Lua number is accepted, while a float32 record, a boolean, an unset record or a
numeric string is not. Only operation 3 writes a result record, so the call
returns one number and three nils for id 3 and four nils for every other id.

Operations 0 and 1 act on a per-kind slot table. `0x0066ECA0` allocates an
object of the requested kind through the factory `0x0066DD00`, which switches on
kinds `0` through `0x73`, constructs it through `0x004FFCF0`, stores it at table
`+0xC4 + 4 * kind` and sets bit 0 of the object field `+0x224`. When the third
value is not `-1` it passes the object already in that slot to the constructor.
`0x0066F620` returns without effect when the slot is empty (`0x0066F62C..0x0066F632`).
Otherwise it clears the slot, clears the bit, hands the object to the list at
table `+0x2A8` through `0x0066FF30` and destroys it through `0x005065B0`. The
factory range-checks the kind (`cmp ecx, 0x73; ja` at `0x0066DD26`), and its
default arm at `0x0066E7E4` for kinds above `0x73` is not traced. The existing-slot
load at `0x0066ECB1`, the table store at `0x0066ECCE` and the slot load in
`0x0066F620` do not bounds-check the index. The role of the table and the kinds is `INFERRED`
as an object manager and is not traced further.

The only recorded script call site is the single `_progFunc` call of
`global_u`, line 268 (`xivl-client-scripts:lua/napi_index.json`, `_progFunc`),
which sits in the `_getLanguage` inline wrapper
(`xivl-client-structs:manifests/lua_engine_callback_registry_findings.json`,
`callbackDeclarationSurvey.binaryOnlyResolution.luaCorpusLiteralSearch`). The
operation id that call passes is
not decoded here, because the script body is excluded. Operation 3 is the only
operation that writes a result, which is the shape a getter needs. Operations 0
and 1 have no recorded Lua call site.

### Operation 3 value

The DWORD that operation 3 returns is a field at `+0x20` of an object that
`0x004B2DF0` receives as its second argument and passes through `0x004DC3A0` to
the constructor `0x004DBF40`. The same function reads that field through the
getter at `0x004B2E59`. The field has the getter `0x004B68A0`, the setter
`0x004B6890` and the predicate `0x004B68B0`, which is true when the field is 4
or 5. The setter has one caller, at `0x00402D63` inside `FUN_00402B30`. That
caller reads the user-config lookup `0x00443E40` with group `0`, key `0x19` and
default `0`. A nonzero result minus 1 becomes the field. Otherwise the field is
the return of `0x004055D0`. That function reads a five-byte file and accepts
its first byte when it is below 6, then falls back to a registry lookup and a
further path (`INFERRED` from the size and read calls). The file, registry key
and final path are not traced.

The values 4 and 5 match `DesktopWidget.isChinese`, which tests
`_getLanguage()` for the same two values
(`xivl-client-scripts:docs/chocobo-mount-script-contracts.md`, Naming widget).
That the field is the language selector is therefore `INFERRED` from the
predicate, the script check and the `_getLanguage` name. That the object at
`+0x4F4` is the one `0x00402D63` writes is `INFERRED` from the shared class
accessors. The enumeration of the other values is not traced.

## Failure behavior

A failed integer check in the callback builds a `std::bad_cast` with the
message `bad cast` (string `0x00F91C08`, throw info `0x011B31F8`, catchable types
`std::bad_cast` and `std::exception`) and throws it through `0x009D1B9F`, taken
as the CRT throw routine (`INFERRED`). The throw sites are
`0x0059F6A1..0x0059F6B9` for the first record, `0x0059F704..0x0059F71C` for the
second record of id 1 and `0x0059F751..0x0059F769` for the second record of
id 0.

The wrapper frame `0x00D09CD0` has a function info with zero try blocks. The
Lua protected-call primitive `0x00DCF140` has one try block whose only handler
type is the pointer type `lua_longjmp` (type descriptor `0x0131DF00`, handler
`0x00DCF18F`, function info `0x0125F128`). The thrown `std::bad_cast` does not
match it, so a Lua `pcall` around the call does not catch the exception and it
unwinds past the Lua VM (`INFERRED` from the primitive's use by the protected
call entry points). Whether a frame of the engine above the VM catches it is not
traced.

The wrapper's own output-tag mismatch checks at `0x00D09F37`, `0x00D09F54` and
`0x00D09F71` throw the same exception. The record setter `0x0052EB70` writes
tag 2 together with the value, so the callback does not reach them.

## Inferences

The inspected wrapper instructions use a captured native dispatch identity.
Those instructions perform neither positional-string operation selection nor
operation-specific closure construction. The operation is selected by the
callback from the first integer argument. The capture join remains conditional
on the current closure header permitting capture 1.

## Unknowns

- The CRT parsers `0x009DBB7B` and `0x009D8B4C`, the class helper `0x009D825A`
  and the truncation helper `0x009D6636` are named by call shape and not traced
  internally. The decimal and exponent grammar, `inf` and `nan` text, and the
  initial value of the flag at `0x0137B8E8` are open.
- The kinds that operations 0 and 1 accept, the role of the slot table at owner
  `+0x4DC` and the classes the factory builds are not traced beyond the factory
  switch range.
- Signed or negative hex strings such as `"-0x10"` are undetermined, because the
  CRT integer parser's sign and prefix handling is not traced. A parser for
  anything beyond plain unsigned `0x<hex>` is a CALIBRATION question.
- The language enumeration, the sources behind `0x004055D0` and the writers of
  the user-config record at group 0, key `0x19` are not traced.
- Whether an engine frame above the Lua VM catches the `std::bad_cast`, and
  what the client does when none does, is not traced.
- `FUN_00DD6040` capture-header semantics and global installation internals
  remain unknown.
- No target execution or live retail, network, or client acceptance was tested.
