# FFXIV 1.23b auto-translate selection contract

This note records the retained static boundary for UI selection and chat
submission. The machine-readable record is
[manifests/autotranslate_wire_format_study.json](../manifests/autotranslate_wire_format_study.json).

The two inspected executable candidates agree at size 15996808 and SHA256
9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9, with
image base 0x00400000 and Ghidra 12.1.3. The retained build value
2012.09.19.0001 comes from xivl-client-structs:manifests/input_stack_routing.json
(binary.build). No game.ver file was read in this pass, and matching candidates
do not authenticate the imported Ghidra program. Addresses below are absolute
Ghidra virtual addresses.

## Recovered chat boundary

FUN_006E91F0 dispatches a submitted string object by channel. Its group
branch obtains a 32-bit-sized value from FUN_006C0590 for the selected Group
entry and passes it through FUN_0075C1A0 after FUN_006C9690 accepts it. The
static evidence does not identify that value as a fixedPhrase, item, or place
token. This is a chat dispatch boundary, not a recovered auto-translate UI
selection producer.

The three channel wrappers FUN_0075BEF0, FUN_0075BFD0, and
FUN_0075C0B0 use markers 1, 2, and 0x19 on their owner path. Their
alternate path obtains this+0x7F8 through FUN_004D75A0 and passes it to
FUN_00C99E40. The retained function listing shows that
FUN_00C99E40 preserves ECX as parser context, obtains the source pointer from
its first stack argument through FUN_00445210, restores ECX for
FUN_00C99B80, and that parser reads context offsets +0x8, +0xC, and
+0x2C. The +0x7F8 value is therefore an unclassified parser/control
context pointer; it is not proven to be an edit buffer.

For Map chat, FUN_004D8160 validates the caller-supplied string/control
object and calls FUN_004E0320. The builder zero-fills a local 0x200-byte
area, copies the source string length derived through FUN_004451F0, then
copies a fixed 0x200-byte destination field into the Map record. It writes
c2s opcode 0x0003 with record size 0x230 and sends through
FUN_00DAE010. The source object is not proven to be a 0x200-byte buffer.

For World chat, FUN_004D82E0 reaches FUN_004DF6D0, which derives the source
string length, copies into a local source area, and copies a fixed destination
message field while writing c2s opcode 0x00C9 with record size 0x218.
FUN_004D83E0 reaches FUN_004DF810, which derives and copies source text into
local source areas before FUN_004E3750 copies a fixed source area into the
destination message field for c2s opcode 0x00C8 with record size 0x230.
Neither source object is proven to be a 0x200-byte buffer.

No retained export edge connects a UI selection callback or editor writer to
token insertion and the chat send boundary. The first missing edge is:

RaptureTextBox or LogWidget callback/editor write -> token insertion into a
caller-supplied string/control object -> FUN_006E91F0 and the channel wrappers.

Allocation, ownership, retention, and release of candidate UI token/editor state
remain unresolved in the retained exports.

The candidate class is
Application::Main::SqwtInterface::CustomControl::RaptureTextBox. Tracked
RTTI references in xivl-decomp:config/ffxivgame.rtti.json list vtables at
0x00FC1454 (4 slots) and 0x00FC146C (72 slots). The 0x00FC1594 (99 slot)
locator comes from the preserved local artifact; it is not authenticated
Ghidra evidence and no slot is tied to selection insertion. The methods
setKeyboardFocusToChatControl, appendStringForChatControl,
startChatInputForPadMode, and appendTextIdForChatControl in
xivl-client-scripts:lua/registry.json are declarations only; their native
callbacks remain unresolved.

Uncommitted local disassembly supplied candidate body locators 0x004C2A20, 0x004BBEA0,
0x004BD170, 0x00548630, and 0x00548740, with parser callsites
0x004C34E9, 0x004C361F, 0x004BC365, 0x004BF393, 0x00548687, and
0x005487F5. These are unsupported candidate locators only; they do not
authenticate behavior or a producer role.

## Adjacent control parser

FUN_00C99E40 calls FUN_00C99B80, whose static control grammar is bounded as
follows:

| Field | Static observation | Status |
| --- | --- | --- |
| Framing | A handled control segment begins with 0x02, then selector and length, and requires 0x03. Plain runs end at NUL or the next 0x02. | Observed for this parser |
| Discriminator | Selectors 0x00 through 0x36 reach the handler table; 0x37 and above reject. | Observed |
| Short length | 0x01 through 0xD7 consume one length byte and set payload length to code minus one. | Observed |
| Rejected length | 0xD8 through 0xEF and 0xFF reject. | Observed |
| Extended length | 0xF0 through 0xFE delegate to FUN_00CB2020, which returns a type-specific header width and decoded length. | Observed; no one-width rule |
| Width and byte order | The segment order is known, but extended forms use type-specific shift/add sequences. | No global byte order |
| Escaping | No literal-byte quoting or auto-translate escaping rule is shown. | Unresolved |
| NUL and UTF-8 | NUL ends the outer walk; plain runs go through FUN_00445C70 for UTF-8 validation. | Observed; locale semantics unresolved |
| Interleaving | The parser resumes after a handled segment and can process plain runs between control candidates. | Parser observed; producer behavior unresolved |
| Unknown and truncated input | Selectors at or above 0x37 and rejected lengths reject. For a handled selector, handler failure or missing 0x03 rejects. An accepted-range selector with no handler rejects in strict mode; when the parser parameter is nonzero it skips directly to the next outer walk without checking 0x03. There is no explicit input-length argument, so truncated extended input is unresolved. | Partial |
| Locale | No locale dispatch or locale-specific token field is proven. | Unresolved |

This grammar is an independent control-bearing text observation. The static
exports do not prove that 0x02, 0x03, selector values, or extended lengths
are auto-translate wire fields.

## Selection-family boundary

The fixedPhrase table path
FUN_004DAA10 -> FUN_004DA680 -> FUN_00447260("xtx/_fixedPhrase") ->
FUN_00C9D550 is independent of the selection dispatch, Map and World senders,
and generic renderer FUN_007906C0 in the retained target set. The
receive-side lookup from a token to a fixedPhrase row, and the choice between
rendering and forwarding, remain unresolved.

The producer classifications are therefore:

- fixedPhrase: unresolved lookup and serialization producer;
- item selection: unresolved lookup and serialization producer;
- place selection: unresolved lookup and serialization producer;
- unsupported families: no family is classified unsupported by this pass;
- row key versus field 0/category: no wire field join is proven.

The fixedPhrase CSV row key, field 0 values, display categories, and table
resource identity remain table evidence only. No decoder should be implemented
from those values.

## Evidence boundary

The manifest retains exact read-only Ghidra invocations, target lists, output
hashes, and the required environment names. The producer-anchor,
selection-control, and control-listing exports contain the requested target
sections and no exporter error; the function-listing export reports
COMPLETE: requested=6 completed=6.

The targeted RTTI export was stopped because the ffxivgame project was held
by another Ghidra instance. Its blocked query targeted
.?AVRaptureTextBox@CustomControl@SqwtInterface@Main@Application@@ for the
candidate class and its vtables, to resolve callback slots and code references
for the first missing edge. The export stopped on that project lock.
