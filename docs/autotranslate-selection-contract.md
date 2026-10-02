# FFXIV 1.23b auto-translate selection contract

This note records the retained static boundary for UI selection and chat
submission. The machine-readable record is
[manifests/autotranslate_wire_format_study.json](../manifests/autotranslate_wire_format_study.json).

The authenticated executable is 15996808 bytes with SHA256
9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9, image
base 0x00400000, and Ghidra 12.1.3. Its adjacent game.ver is 15 bytes with
SHA256 3DBEED87AE1F2805BEC69D63137E3DECA9DD444AD5CAA3EA5DEDB68B8A50BFEF
and contains 2012.09.19.0001. VerifyProgramFileBytes.java authenticated the
retained original, modified, and mapped bytes for seven loaded initialized
file-backed ranges, covering 15990784 bytes; the two excluded initialized
non-executable ranges are 0x01324000..0x0137C93F and
0xFFDFF000..0xFFDFFFFF. Addresses below are absolute Ghidra virtual
addresses.

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

No retained export edge connects an auto-translate selection callback or editor
writer to token insertion and the chat send boundary. The first missing edge is:

Auto-translate selection callback/editor write -> token serialization into a
caller-supplied string/control object -> FUN_006E91F0 and the channel wrappers.

Allocation, ownership, retention, and release of candidate UI token/editor state
remain unresolved in the retained exports.

The candidate class is
Application::Main::SqwtInterface::CustomControl::RaptureTextBox. The
targeted RTTI export authenticates vtables at 0x00FC1454 (4 slots),
0x00FC146C (72 slots), and 0x00FC1594 (99 slots), with vtable stores in
FUN_0066A5B0's destructor path and FUN_0066C1A0's constructor path. The
three vtable values occur at this+0x194, this+0xB4, and this+0 across those
paths; FUN_0066A5B0 frees fields at listing VAs 0x0066A619, 0x0066A66A,
and 0x0066A68E. These records do not map a slot to selection insertion. The
registry names setKeyboardFocusToChatControl, appendStringForChatControl,
startChatInputForPadMode, and appendTextIdForChatControl. Authenticated script
bodies corroborate appendStringForChatControl and appendTextIdForChatControl:
appendStringForChatControl concatenates the focused chat input
and calls setText("TextBox_ChatInput", value); appendTextIdForChatControl
calls setMacroText("TextBox_ChatInput", suppliedValue, ...). Numeric
setMacroText calls _setTextProperty(nil, controlName, "TextUI", value, ...),
whose _inl wrapper returns "self", "_setTextProperty_cpp". An exact
defined-string reference export found no native string references for the
method names, so the native callback or vtable slot remains unresolved. This
numeric TextUI bridge is an adjacent formatted-text candidate: setTellAddress
calls appendTextIdForChatControl(2256, 103, address), but the path is not
proven to encode auto-translate selection or to be mandatory for token insertion.

The verified candidate trace resolves 0x004C2A20, 0x004BBEA0, and
0x004BD170 as UI state and result handlers dispatched through FUN_004CDAD0
from FUN_004CDE10. They read named controls and parser-backed text but submit
separate event records, not chat tokens. FUN_004BBEA0 reaches
FUN_004B7A20, whose FUN_004CFD10 builder writes event 0x1C3 with size 0x1D0;
FUN_004BD170 reads Result_Maker fields such as purposeInt, placeInt,
socialInt, and skillInt, then FUN_004B7C10 uses FUN_004CFDA0 to write event
0x1C7 with size 0x48 after a TextBox_PersonName source length check below
0x20. FUN_004C2A20 reaches FUN_004B80E0 and FUN_004B82A0, whose builders
write events 0x1D2 with size 0x18 and 0x1D5 with size 0x898. The latter
copies a 0x20-dword block and a 0x200-dword block from its caller record.
Each event passes through FUN_004E0240 to FUN_00DAE010, but no exported edge
joins these records to FUN_006E91F0 or a token insertion writer.

The authenticated pointer read covers all 175 source slots across the three
RaptureTextBox vtables using the exact 0x00F3E000..0x01264FFF to
file-offset-11788288 mapping. It preserves 11 distinct 0x0066xxxx method
candidates with their source slots. FUN_0066C580 receives a candidate
property/input pointer and reaches FUN_00698400, FUN_006984B0, and
FUN_00684A70, but no static edge joins that slot to _setTextProperty_cpp,
token bytes, or the chat source object. FUN_00754A60 is the BCS-Y-0225
WidgetBase Lua dispatcher candidate at 0x00FD5A74; its verified body has 24
direct handler callsites and does not identify the _setTextProperty_cpp handler.

The verified 0x00548630 and 0x00548740 bodies are clipboard copy and paste
helpers around FUN_00C99E40. The paste body sanitizes clipboard UTF-16 and
passes local clipboard-derived source local_64 with caller object param_1 as
the destination to FUN_00C99E40. Their prior parser callsites
0x004C34E9, 0x004C361F, 0x004BC365, 0x004BF393, 0x00548687, and
0x005487F5 resolve to the three UI handlers or those clipboard helpers; they
do not establish a token producer role.

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
hashes, and the required environment names. The new targeted RTTI export
reports one target and three records with output SHA256
E13A818BBE9C8E197DCABB27E4F84C43E82A7C09500A11912B212FC420A571DB. The
candidate, helper, event, RTTI method-listing, and method DumpVAs exports contain
every requested section with no exporter error. The exact callback-string
export reports COMPLETE with four queries, zero defined string matches, and
zero references. The authenticated Lua source hashes and line spans, the
RaptureTextBox method-pointer mapping, and the native dispatcher candidate are
retained in the manifest; no token producer is promoted.
