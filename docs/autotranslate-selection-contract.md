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

The native Completion reader, formatter, event consumers, document insertion,
and document-to-getter reconstruction are recovered below. The remaining edge
is the reconstructed/cached RaptureTextBox text -> native PressEnter event
argument -> submitted chat source -> FUN_006E91F0 and the channel wrappers.
The exact auto-translate UI origin and family/table identity of the selected
Completion record are also unresolved.

Complete ownership, release, invalidation, and serialization of retained
UI/editor state remain unresolved.

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
FUN_00684A70. Its this+0x1994 offset +0x20 call resolves to CompletionModule
slot 8 (FUN_00C9BBD0), but no static edge joins it to _setTextProperty_cpp,
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

The authenticated Lua submission trace (AT-LUA-002) wires
TextBox_ChatInput to PressEnter in logwidget.lua:85-143 and :213-245.
PressEnter calls processInputWordAnalyze; pending command target selection
stores the input in control user work slot 3, and the decided-subtarget handler
at :464-482 retrieves it for executeTextCommand. In
desktopwidget_connector.lua:7103-7115 and :20074-20110, this analysis route
reaches the native _parseTextCommand bridge. The chatDirect path at
:7290-7436 converts pronouns and calls the player's _chat bridge. These script
edges do not identify the native Completion selection or its token writer.
AT-LUA-003 distinguishes submission from property access. The PressEnter
handler receives text as its A4_2 event argument; it passes that value to
analysis, pending-target storage, and history. Separately, WidgetBaseClass
getText calls getControlProperty(controlName, "Text"), which calls
_getProperty(nil, controlName, propertyName); its _inl wrapper returns
"self", "_getProperty_cpp". These script surfaces do not establish which
native document read supplies the event argument or property value.
AT-LUA-004 pins command registration and Lua event forwarding.
setControlCommandCondition registers the control name and command string
through _setUICommandCondition(controlName, commandName, 5), whose bridge
pair is "self", "_setUICommandCondition_cpp". The value 5 is a registration
argument, without an authenticated PressEnter enum meaning.
WidgetBaseClass._onUICommandEvent forwards its arguments to
processUICommandEvent, whose default branch preserves them for
LogWidget.processUICommandDefault. This is the PressEnter handler named
by the script; its native argument producer remains to be joined.

AT-LUA-005 pins the parser-declined script path from PressEnter A4_2 through
processInputWordAnalyze and executeTextCommand to chat/chatDirect. The first
explicit MyPlayer._chat argument is the result of convertPronouns, which can
call the native _replaceMacroCodeString helper through replaceString. Byte
identity between A4_2 and the _chat input remains unproved. The broader ordinary
route is retained in manifests/text_command_ingress.json:ordinaryRoute.

AT-ENTER-001 pins the native UILuaCommands.PressEnter command at 0x01344D44.
FUN_00F141A0 supplies id 0x11 to FUN_00928D90, which stores it at command+0x78
and inserts the RoutedCommand into the registry. This identifies command
metadata without proving a chat wire field or the TextBox event argument.

AT-ENTER-002 recovers a separate generic event adapter:
FUN_0075D5D0 -> FUN_008A4050 -> FUN_006F5A90 -> FUN_006F5640. The adapter
uses event bytes +0x55 and +0x54 during argument packaging. The guarded branch
through FUN_00896AF0 invokes the literal _onUICommandEvent name. Neither byte
is assigned a PressEnter-specific meaning, and the buffers are not yet joined
to Lua A4_2 or reconstructed TextBox text.

The indirect +0x34 call in FUN_0091E1C0 pushes one event pointer. The adapter
FUN_0075D5D0 takes three stack arguments and returns with RET 0xC. Matching
slot offsets do not establish a common interface or handler instance. The
TextBoxBase.Paste branch and Completion carriage-return acceptance are also
distinct from the chat Enter producer. Control registration, actual handler
coordinates, and the TextBox-to-event argument remain recoverable static
targets; the trace has not reached a runtime-only boundary.

AT-ENTER-003 traces _setUICommandCondition through its callback
FUN_006EB6A0 -> FUN_0075B7B0 -> FUN_004D9910 -> FUN_0053AB80. The lookup
key comes from the input container's +0xC value. The next argument is the
control name; the command name belongs to the separately constructed condition
object. The nonmatching branch of FUN_0053AB80 resolves the control name through
FUN_0053A970 and, on success, reaches the relation update FUN_0053A720. The owner,
named child, condition fields, and PressEnter invocation remain unjoined to a
concrete chat TextBox.

AT-ENTER-004 identifies the generic adapter's string member. Its third
incoming stack argument becomes the fifth explicit argument to FUN_00713830,
which assigns vtable 0x00FD5330 and copies that string value to object+0x104.
The string producer and conversion of that member into Lua A4_2 remain
unresolved. This narrows the native argument target without joining the
reconstructed TextBox text to a submitted message.

A literal-name search over all 2671 authenticated Lua bodies found no matches
for the retained completion/phrase search terms; it does not exclude native,
indirectly named, or runtime handlers.

## Native Completion boundary

AT-COMP-001 resolves the CompletionModule provider stored at RaptureTextBox
this+0x1994 by FUN_0066C1A0. FUN_004D74F0 returns the container's embedded
module at +0x664, constructed by FUN_00C9CFA0. Six cells in its primary vtable
at 0x01108E40 were read from the authenticated executable; slot 5 points to
FUN_00C9BC40.

FUN_00C9BC40 reads a selected 32-bit Completion entry and interprets its
signed low 7 bits and unsigned upper 25 bits. Low value -2 returns the upper
value. Low value -1 copies an indexed string through this+0xD8 and returns -2.
Other low values construct `<fixed(%d,%d)>` with those two values, pass it to
the interface at this+0x10, copy the returned text, and return -1 after cleaning
up local string temporaries. This is an internal record and formatter-input
observation; neither the expression nor its bits are authenticated wire fields.
AT-COMP-005 resolves that formatter through the complete TextModule at
container+0x554: its vtable 0x01108F70 slot 5, cell 0x01108F84, points to
FUN_00C9EEC0. FUN_004DBF40 supplies this TextModule pointer as the second
explicit CompletionModule constructor argument, stored at module+0x10;
the other argument is stored separately at module+0x0C.
FUN_00C9EEC0 passes TextModule+0x4C to FUN_00CB6880 -> FUN_00CB6510.
AT-COMP-007 resolves its `fixed` registry entry: FUN_00CB68A0 declares
selector 0x2E and two numeric descriptors. The authenticated descriptor string
`nn` starts at 0x0110C9EC; the key `fixed` starts at 0x0110C9F0.
The constructor supplies the first `n` as literal 0x6E and reads the second
from 0x0110C9ED. The descriptor count does not prove arity rejection.

For successfully parsed literal numeric arguments, the internal control is
`02 2E E(payload byte count) payload 03`, with the two encoded arguments
concatenated in the payload. FUN_00CB2210 supplies E: unsigned values below
0xCF become one byte value+1. Larger values use prefix 0xEF+mask, where mask
marks the nonzero bytes of the 32-bit value, followed by those bytes from most
to least significant. FUN_00CB4CD0 appends the result; FUN_00CB6510 uses the
same helper for the payload byte count.

These literal examples come directly from the authenticated registry and
numeric-helper branches. They are internal formatter examples, without an
observed UI selection, table join, or retail message:

| Formatter input | Internal bytes |
| --- | --- |
| `<fixed(0,0)>` | `02 2E 03 01 01 03` |
| `<fixed(1,207)>` | `02 2E 04 02 F0 CF 03` |
| `<fixed(1,256)>` | `02 2E 04 02 F1 01 03` |

The argument values do not identify a table or row. Negative numeric conversion,
macro expression branches, malformed/truncated controls, exact selected UI
vector origin, and chat wire serialization remain unresolved. This internal
contract does not justify a wire decoder.

FUN_00C9D550 reaches candidate preparation at FUN_00C9D0D0, which packs
`(index << 7) | 0x7E` into a Completion record. The retained exports do not
join that prepared vector to the handler's selected vector or identify the
index as a fixedPhrase, item, place, or wire key.

AT-COMP-002 resolves FUN_0066AB10's call at 0x0066ABA8 to CompletionModule
slot 5. Its instruction listing preserves the two local pointers, incoming
argument, and this+0x1A60 field supplied on the stack; it does not identify the
local objects as editor buffers or packet sources. The -2/-1 branch reaches
FUN_0066A730 and FUN_0066A330. At 0x0066A399 the latter invokes the parent
pointer's +0xB4 interface through vtable offset +0x34. AT-COMP-004 resolves
the parent as the complete RaptureElementContainer C at MainModule M+0x10.
The constructor chain FUN_004DC3A0 -> FUN_0054E190 -> FUN_005463E0 stores
C in the extension field read by the _ChatInput branch of FUN_00549330.
The C+0xB4 vtable at 0x00F911BC has slot 13, cell 0x00F911F0, pointing
to thunk FUN_004D71C0 -> FUN_0091AC80. This callback dispatches on the
byte at `*(*(event+4)+5)` into UI/event consumers; nested event payload and
vector element types remain unclassified. This parent event path is distinct
from the accepted-text insertion below.

AT-COMP-006 resolves the insertion branch in FUN_0066AB10. On a -2/-1
result it copies the first output to CompletionDocument+0x60, constructs an
accepted-text event from the first output for -2 or the second output for -1,
and invokes the TextBox's +0xB4 interface slot 34 at 0x0066ACCE. The
authenticated cell 0x00FC14F4 points to FUN_0066B5F0. The event's source
pointer passes through FUN_00545CF0 and FUN_00545DD0 into event+0x1C;
FUN_0066B5F0 -> FUN_0097A570 invokes primary slot 72 (FUN_0095B3F0).
Its insertion route reaches slot 71 (FUN_00958C80) -> FUN_009586C0 ->
WrapTextDocument slot 5 (FUN_0098C180) -> CompletionDocument slot 5
(FUN_0066B400). These are guarded branches, not an unconditional write.

FUN_0066C1A0 stores the CompletionDocument factory result at TextBox+0x1A70
before wrapping it in FUN_0098DAA0. FUN_0066B400 delegates text insertion
to its +0x58 LineTextDocument's slot 5 (FUN_0098C8F0). When its +0x60
string is nonempty, it copies that string into a record in the +0xB4 vector
through FUN_0066DAE0, alongside insertion position and length. Thus the
formatted control and editor text have separate storage. FUN_0066AB10 clears
the +0x60 temporary after the event call at 0x0066ACDE. AT-COMP-008 recovers
retrieval of those stored controls through document-to-getter reconstruction.
The retained edge does not join the getter to FUN_006E91F0 or Map/World packet
source objects.

AT-COMP-008 resolves FUN_0066B0E0, called by FUN_0066C410 with the
CompletionDocument at TextBox+0x1A70 as ECX. It copies source text when the
retained vector is empty. Otherwise, it copies the source ranges around each
0x5C-byte retained record, appends that record's control string, advances past
its display range, and copies the final source tail. The getter supplies the
source at TextBox+0x1758 when the string at +0x1A74 is empty. Its other branch
uses cached text at +0x1980. Flag/comparison guards control the cache update
and callback; the getter returns +0x1980 or its fallback. This reconstructs
control-bearing text without proving a submitted retail message.

AT-COMP-009 bounds the examined direct getter callers. FUN_0052C3E0 reads
TextBox_ItemNameSearch_ChatInput, whose owner also binds
Button_ItemNameSearch. FUN_004F5220 reads one control plus ten other text
controls into a caller record. Its event-object match at owner+0x26C is not
authenticated as PressEnter. These routes do not identify every indirect
caller or join the reconstructed text to chat submission. The native
PressEnter event argument, cache invalidation, selected record family/key,
and Map/World source-object joins remain open static work.

AT-COMP-003 authenticates CompletionDocument's 23-slot vtable at 0x00FC1744
and its FUN_0066BA70 factory. The RaptureTextBox constructor wraps that
document through FUN_0098DAA0; FUN_0066BD00 uses CompletionModule slots 7 and
8 while synchronizing text and candidate ranges. Complete ownership,
retention, release, and callback registration remain unresolved.

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
FUN_00C9D550 reaches Completion candidate preparation at FUN_00C9D0D0. That
candidate vector is not joined to the selected RaptureTextBox vector, Map or World
senders, or generic renderer FUN_007906C0 in the retained target set. The
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

The manifest retains read-only Ghidra invocations, target lists, output
hashes, and the required environment names. The RaptureTextBox RTTI export
reports one target and three records with output SHA256
E13A818BBE9C8E197DCABB27E4F84C43E82A7C09500A11912B212FC420A571DB. The
candidate, helper, event, RTTI method-listing, and method DumpVAs exports contain
every requested section with no exporter error. The exact callback-string
export reports COMPLETE with four queries, zero defined string matches, and
zero references. The authenticated Lua source hashes and line spans, the
RaptureTextBox method-pointer mapping, and the native dispatcher candidate are
retained in the manifest; the document getter is recovered without a
packet-source join.

The Completion recipes AT-GH-014 through AT-GH-024 retain exporter revisions,
script hashes, sanitized reproduction invocations, and output hashes. The
targeted Completion RTTI export covers six names and eight records. The handler
listing reports COMPLETE with three requested and three completed entries.
The lifecycle dump preserves its repeated requests and all eleven sections;
those represent nine distinct function targets.

The indirect-target and fixed-macro recipes AT-GH-025 through AT-GH-051
support AT-COMP-004 through AT-COMP-007. Fresh owner listing and decompilation
exports cover all sixteen requested insertion-path functions. Eight pointer
cells and the required descriptor/key bytes were independently read from the
authenticated executable. Constructor, subobject, and complete-object
coordinates remain explicit in the manifest.

Recipes AT-GH-052 through AT-GH-056 and fresh identity AT-ID-004 support
AT-COMP-008 and AT-COMP-009. AT-LUA-003 pins the distinct event-argument and
property-getter script surfaces.

Recipes AT-GH-057 through AT-GH-066 and fresh identity AT-ID-005 support
AT-ENTER-001 and AT-ENTER-002. AT-ID-006 independently pins the three native
command/event literal strings to executable file offsets and byte hashes.
AT-LUA-004 pins command registration and
argument forwarding on the script side.

Recipes AT-GH-067 through AT-GH-072 and fresh identity AT-ID-007 support
AT-ENTER-003 and AT-ENTER-004. AT-LUA-005 retains the script argument path and
its macro-replacement boundary.

The optional passive observation checklist is retained in the manifest. It
requests the identified client and locale, exact UI selection, repeated sparse
keys, token-only and literal/token/literal examples, raw source/message bytes,
direction, and independently observed rendering. Any owner-supplied local
preserved-client test remains non-retail corroboration.
