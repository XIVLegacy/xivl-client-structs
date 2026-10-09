# FFXIV 1.23b auto-translate selection contract

The retained static evidence recovers selected Completion records, native
category/key production and conditional chat submission paths. An admitted
fixed control reaches the message field unchanged when the copied prefix
includes it completely. Generic Lua argument packing, earlier pronoun
replacement, a selected external CSV table/key and receive lookup remain
qualified.
[manifests/autotranslate_wire_format_study.json](../manifests/autotranslate_wire_format_study.json)
contains the structured record.

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

## Enter-to-Lua contract

AT-ENTER-032 consolidates the conditional static path for the pinned textual
LogWidget resources. The owner is the key-selected FormElement E, its loaded
XamlControlContainer X, and the named complete RaptureTextBox P. Successful
name registration and lookup connect P to that container. The matching
namespace/type-8 dispatch uses the installed actor holder H at E+0x80.

| Stage | Recovered contract | Selection limit |
| --- | --- | --- |
| Owner/control | E -> loaded X -> named P -> actor holder H | Load, name/cache selection, namespace and actor readiness remain guards. |
| Enter source | The declared Return action reads P's Text2 through the reconstruction/cache getter. | The current document, source, retained records and cache flags select the value. |
| Native event | Formatting and type-8 parsing supply routed event+0x28, then native event+0x104. | Formatting is bounded and parsing removes the final byte without validating it. |
| Lua argument | The UTF-8 string operator pushes the NUL-terminated prefix of that parsed string as A4_2. | Callback resolution and event admission must succeed. |

For an intact formatted value with its expected final delimiter, this path
preserves the Text2 string through to A4_2 up to NUL termination. It does not
recover a particular execution's control state or actual submitted bytes.
The later convertPronouns operation changes the MyPlayer._chat input and is
downstream of this Enter-to-A4_2 contract.

AT-ENTER-033 pins the source default and getter return. The base constructor
sets P+0x1758 to null, and its generic initializer receives a zero default
string, so that call leaves the pointer null. The getter can reconstruct a
working string, but cache refresh requires its flag and changed-value
guards; it returns P+0x1980 or fallback even when refresh is skipped. Other
pointer-mediated source assignments are not universally recovered, and
candidate scans do not prove their absence.

The compiled resource alternative has a separate static gap: installation of
CustomTextBoxFactor and ownership of its two constructor inputs remain
unresolved. That gap does not invalidate the conditional textual path, and
the pinned resource bytes alone do not select a historical loaded instance.

## Recovered chat boundary

AT-LUA-005 establishes that chatDirect passes `convertPronouns(input)` as
the first explicit MyPlayer._chat argument. AT-CHAT-001 resolves the native
submission source. Registration FUN_00743D80 binds `_chat` to thunk
0x006DE7D0, whose MyPlayer slot 67 selects FUN_006E91F0. The native method
extracts ExecuteParameters elements 0 and 1, then dispatches by mode. Tag 3
returns the stored string value; alternate value conversions remain separate.
These Lua and native observations do not prove every generic argument-packing
path or actual execution.

The extracted element-0 text is the third explicit stack argument to the
channel wrappers. Say, shout and emote use FUN_0075BEF0, FUN_0075BFD0 and
FUN_0075C0B0 with owner-path markers 1,2,0x19. Their owner path reaches
FUN_004D8160. Tell reaches FUN_004D83E0 through FUN_0075C190, and selected
group reaches FUN_004D82E0 through FUN_0075C1A0. Each owner calls
FUN_00C99E40 with its TextCleaner at +0x7F8, that input string, a local
output string and flags 0,0,1. Parser success supplies the local output to the
packet builder. The conditional FUN_004CE760 call uses separate metadata and
local strings; its inspected body does not establish a packet-string rewrite.

AT-CHAT-002 joins the fixed control to this parser. FUN_004DBF40 constructs
the cleaner through FUN_00C99F40 with table 0x01269998. Authenticated bytes
`2E 02` map selector 0x2E to handler index 2, thunk 0x00C9A130. Its
vtable+0xA8 jump resolves through the RTTI-authenticated TextCleaner table
0x01108C74, slot 42, to FUN_00C99AF0.

That handler checks two numeric encodings and accepts only when their combined
width equals the payload length. Short prefixes 01..D7 consume one byte;
extended F0..FE use FUN_00CB2020. Zero, D8..EF and FF are rejected. On a
nonzero result and a following 03, FUN_00C99B80 copies the original source
from opening 02 through closing 03, byte for byte, into the output string.
Plain segments have separate validation and transformations. This preserves
admitted fixed controls without proving whole-message identity.

The output string reaches FUN_004E0320 for Map opcode 0x0003, FUN_004DF810
for World tell opcode 0x00C8, or FUN_004DF6D0 for selected-group opcode
0x00C9. [The chat wire contract](../manifests/chat_wire_contract.json) owns
World destination field layouts. Map uses record size 0x230 and a fixed
0x200-byte message field. These destination sizes do not establish the source
object's size. FUN_00447BC0 selects a counted prefix under a 0x200-byte cap,
backing over trailing UTF-8 continuation bytes and checking the final character
width. A complete admitted fixed control included in this copied prefix reaches
the message field unchanged.
AT-CHAT-003 records earlier pronoun replacement. Its marker-aware branch
initially searches for 02 twice, then uses 02/03 for later intervals. Needle
and marker positions determine each splice, so it does not establish universal
fixed-control protection. Truncated controls, NUL termination and historical
runtime state remain qualifications.

The selected-group value from FUN_006C0590 is separate metadata. It is not
identified as a fixedPhrase, item or place token. External family/table meaning
and matching receive/render lookup remain unresolved.

The native Completion reader, formatter, event consumers, document insertion,
and document-to-getter reconstruction are recovered below. AT-ENTER-008 pins
the retail LogWidget owner/child declarations. AT-ENTER-009 joins their Text2
Enter action to reconstruction/cache access, formatting and routed-event string
production; AT-ENTER-006 and AT-ENTER-007 supply the conditional native
dispatch and conversion to Lua A4_2. AT-ENTER-013/014 recover the allocated
FormElement key, callback writer and
value-1 LogWidget initialization. AT-ENTER-017/018 recover the first-request
loaded-record publication, namespace installation and conditional dispatch
selection. AT-ENTER-019 joins the textual root/TextBox builder, special Name
application and same-container name map under their guards. AT-ENTER-020
qualifies the pinned payload format; AT-ENTER-021 joins the conditional compiled
factor to the same container's name map. AT-ENTER-022 separates element and
Name-property mapping. Resource selection, actual metadata IDs/cache order,
factor registration, property acceptance, name/cache selection and installed
actor remain qualified. The
native submission and channel-wrapper source joins are in AT-CHAT-001/002.
Generic Lua argument packing, earlier conversion and actual submitted bytes
remain qualified. External family/table identity of the selected Completion
record remains unresolved.

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
LogWidget.processUICommandDefault. AT-ENTER-009 recovers the resource-selected
native string producer; loaded-child, namespace and actor selection remain
qualified.

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
is assigned a PressEnter-specific meaning. AT-ENTER-007 joins the generic
event string to Lua A4_2; AT-ENTER-009 supplies the resource-selected Text2
production path.

The indirect +0x34 call in FUN_0091E1C0 pushes one event pointer. The adapter
FUN_0075D5D0 takes three stack arguments and returns with RET 0xC. Matching
slot offsets do not establish a common interface or handler instance. The
TextBoxBase.Paste branch and Completion carriage-return acceptance are also
distinct from the chat Enter producer. Loaded child, namespace and actor
selection remain recoverable static targets; the trace has not reached a
runtime-only boundary.

AT-ENTER-003 traces _setUICommandCondition through its callback
FUN_006EB6A0 -> FUN_0075B7B0 -> FUN_004D9910 -> FUN_0053AB80. The lookup
key comes from the input container's +0xC value. The next argument is the
control name; the command name belongs to the separately constructed condition
object. The nonmatching branch of FUN_0053AB80 resolves the control name through
FUN_0053A970 and, on success, reaches the relation update FUN_0053A720.
AT-ENTER-006 recovers the stored condition fields and their dispatch reader.
AT-ENTER-008 identifies the named resource owner and child; AT-ENTER-013/014 join
the allocated key and initialization. Loaded receiver and actor selection
remain conditional.


AT-ENTER-010 follows the declared form into its script initialization path.
LogWidget.getFormName returns "LogWidget". WidgetBaseClass._onInit calls
initCommon and then init on the same self; initCommon calls loadFormData with
that form name. loadFormData calls self:_setFilename(name) and self:_loadForm().
The two native callbacks resolve the same copied input-container+0xC key through
FUN_004D9910 as condition registration. FUN_00533EF0 stores the filename at
the selected complete FormElement E+0x110. FUN_00537D50 appends .form and
requests loading through FUN_005377C0 when E+0x98 is negative, storing the
returned request identifier there. This joins the LogWidget form request and
Enter-condition registration to the same key-selected owner. Successful loading,
the loaded child and installed actor remain unproved. initCommon can also rename
the root from its instance-name argument; "Window_LogWidget" is a declaration,
not proof of every final instance name.


AT-ENTER-011 closes the registration side of that lookup. The FormElement
constructor calls FUN_004DAB50, which stores its key at E+0x88 and submits
(key, E) through FUN_004DA9A0 to the owner+0x17804 map. A duplicate preserves
the existing entry. FUN_004D9910 searches the same map by the complete unsigned
key and returns node+0x10 on success. Thus a registered FormElement is selected
by its E+0x88 key. AT-ENTER-013 recovers the upstream callback-key writer;
a live numeric K is not a static constant. The base constructor also stores
the initial actor
holder at E+0x80. The LuaActorImpl replacement path writes through its own
receiver+0x8 holder; AT-ENTER-012 recovers the alias for guarded construction
paths while preserving actual instance-selection limits.


AT-ENTER-012 joins a guarded actor installation to that holder. FUN_0075BE30
looks up the supplied widget key and calls FUN_004D87C0 on the selected E with
an actor-init record. The latter loads H=[E+0x80] and passes H to
FUN_00574970. Its nonzero-record branch calls FUN_00774700 with record as the
first explicit argument and H as the second. When record+0x5C is nonzero,
FUN_0076C8D0 constructs LuaActorImpl and FUN_00774700 stores it through H.
The nonready branches pass the same H into FUN_005745F0, which stores it at
record R+0x8. This recovers the holder alias for these construction paths.
AT-ENTER-013 identifies the creation caller and actor-init record. Readiness,
loaded child and dispatch namespace/actor selection remain conditional.

AT-ENTER-013 closes the callback owner-key writer. WidgetBase table
0x00FD5A74 slot +0x6C selects FUN_006E3920. Its slot +0x50 returns selector
0x1A; FUN_0075BE10 -> FUN_004D7C10 creates a FormElement and
FUN_004D6750 returns its E+0x88 key K. The registry constructor installs
FUN_0053B1B0 at callback-vector+0x68 (selector 0x1A times four); that factory
allocates 0x280 and forwards K through FUN_0053AF60 -> FUN_004DAB50.
On the fresh-object path,
FUN_0078BBB0 -> FUN_00CC7800 -> FUN_00CDCBA0 passes K to FUN_00CE1CC0,
which stores it at Lua object O+0x70. FUN_00D19B70 retrieves O from the Lua
receiver and copies O+0x70 through FUN_00CC7030 into ExecuteParameters+0xC.
The WidgetBase function-holder adapter FUN_0071AD50 preserves that parameter
block for FUN_006EB6A0. Its successful registered lookup therefore selects E
by the allocated K. Equality with the newly constructed owner requires its
map insertion; a duplicate preserves an existing owner. The separate guarded
adjusted-object+0xC write is not
needed to establish this callback parameter coordinate.

FUN_006E3920 also calls FUN_0075BE30(&K,C) with the returned native control C.
This supplies the actor-init record to AT-ENTER-012 for the same E+0x80 holder.
The record+0x5C readiness guard remains explicit. Scheduling _onInit through
FUN_00CD0910 does not prove its completion before actor installation.

AT-ENTER-014 selects the first declared LogWidget instance. DesktopWidget's
setDefaultWidgetLocation creates script index 2 with default name LogWidget
and initialization value 1, then index 3 named LogWidget2 with value 2.
createStaticWidget forwards these through createWidget and _createActor;
LogWidget.init registers chat Enter only for value 1. These indices are not K.
The authenticated native registration constructs WidgetBase for
WidgetBaseClass. The fresh _defineClass branch clones its native slot +0x4,
which constructs another WidgetBase; the fresh _createActor branch then uses
slot +0x6C above. Thus the script inheritance and native creation/key writer
are joined on their successful branches. AT-LUA-006 pins the script sources;
AT-ID-015/016 pin the program, native tables and class-name literals.

AT-ENTER-015 resolves the registration namespace. The authenticated
initializer constructs global string 0x01336A30 from "_widget"; TextBox_ChatInput
therefore takes FUN_0053AB80's nonmatching branch. That branch retains complete
E in ECX and passes E+0x164 as a namespace argument to FUN_0053A970. The latter
uses E+0xEC to resolve the namespace name, then passes controlName and the
namespace identifier to the E+0x1DC child cache. A successful child
cast allows callback setup on child+0xB4 and relation update with ECX=E+0xF8.
E+0x164 is not the child-cache receiver. This proves registration coordinates;
load success, the resolved child pointer, final namespace value and the separate
routed-event dispatch namespace/actor branch remain qualified.

AT-ENTER-016 follows the form wait. _loadForm constructs checker P with K
at P+0x4 and the address C+0x64 at P+0x8, then queues it at Lua-thread+0xE8. Its predicate
selects E by K and tests FUN_00535690(E,0): the loaded-record map referenced
by E+0xD4 must return a nonzero record for identifier 0. Its completion method
writes C+0x64 and calls a key-selected bridge ending at the authenticated
RET 0x4 fragment at 0x00533EC0. This is separate from the C+0x5C actor-readiness
guard. AT-ENTER-017/018 recover the indexed-record writer and namespace
installation. Actual load/resume, root/child construction and name/cache
selection remain qualified; no runtime-only ceiling is asserted.

AT-ENTER-017 joins the pending form request to indexed publication. The
constructor binds handler B at E+0x208 to complete E, FUN_005387F0 and zero
receiver adjustment. The request registers B with a newly constructed
XamlReader R and records (R,identifier) in E+0x1F8. E+0x94 starts at zero and
increments after an accepted request, so the fresh owner's first accepted
request has identifier 0. FUN_00537D50 stores its result at E+0x98. Failed
requests remove their pending entry and return -1.

The guarded timer notification supplies R and an event argument pointing to
R+0xE0, its XamlControlContainer AutoPtr. Collection slot +0x4 selects
FUN_0096C1B0, which invokes handler slot +0x8. The authenticated handler selects
FUN_0095D1F0 and tail-jumps to FUN_005387F0 with complete E unchanged. The
callback finds the pending R entry, takes X from AutoPtr+0x4, zeros that storage
and calls FUN_00538760(E,X,identifier). The registrar finds or inserts a node
in [E+0xD4] and writes X into node+0x10. This supplies AT-ENTER-016's record-0
predicate on the first-request branch. A nonzero X does not prove a populated
root or named child, and the store does not lease a returned control.

AT-ENTER-018 joins namespace installation and inverse dispatch selection.
For identifier 0 with a nonnull X+0x2C root, publication copies the root's
slot-+0x8 name into E+0x164. When the completed identifier equals E+0x98, the
callback inserts (E+0x164,identifier) into the E+0xEC namespace-name map through
FUN_00537C60. A duplicate name preserves its existing identifier. Under the
first-request, absent-name and unchanged-name guards, AT-ENTER-015's
TextBox_ChatInput registration resolves namespace identifier 0 and selects X.
Its cache-hit, name-map and X+0x30 fallback branches remain explicit.

The dispatch reader casts source P to FrameworkElement and tries P+0x298's
registered container, then P+0x240 ancestors. FUN_00535700 finds that exact
container pointer in [E+0xD4]; FUN_00535450 recovers the namespace name from
E+0xEC by identifier. FUN_00536280 separately constructs that namespace and P's
name. It replaces the source name with _widget only when the source name equals
the root name. For a selected condition, it compares the namespace with the
refreshed E+0x164. Equality and event type 8 select FUN_00574BE0 on H=[E+0x80]
with three arguments, including event+0x28 as the third. The other namespace
branch selects FUN_00574BF0 with four arguments. Thus a source registered in
the published record-0 container can select AT-ENTER-006/007's Lua A4_2 path
under the name, condition, admission and actor guards. Actual child construction,
names after collisions or replacement, cache freshness and actor readiness
remain qualified.

AT-ENTER-019 follows the textual builder with the same loaded container X.
FUN_0096A7A0 -> FUN_0096A580 -> FUN_0096A4C0 constructs MarkupObject D with
D+0x4=X and D+0x8=R. Its authenticated slots reach FUN_0094AD90, which first
tries the element-extension registry. The TextBox registration made by
FUN_005463E0 selects CustomControlExtension slot +0x4 -> FUN_00549330 under
the current registry-hit and lifetime guards. A Name containing _ChatInput
selects the RaptureTextBox constructor FUN_0066C1A0. Its temporary markup
object inherits X and passes the new control to FUN_00947040.

AT-ENTER-027 recovers the textual constructor inputs. MainModule M's
constructor passes M+0x10 and byte offset M+0x17CE0 as explicit arguments 2
and 7 to FUN_0054E190 on successful allocation of RaptureSqwtInterface I.
That constructor supplies hidden ECX=U=I+0x2E0 to FUN_005463E0, with those
two values as its explicit inputs. They become U+0x10 and U+0x14. The
extension registers U for CustomControl, TextBox and KeyConfigControl.
With the retained TextBox association, the textual slot-+0x4 handler
FUN_00549330 passes M+0x10 and M+0x17CE0 as explicit inputs 1 and 2 to
FUN_0066C1A0, with the newly allocated control in ECX. AT-ID-039 pins the
raw RTTI names and handler slot; the listing joins the tables to their
constructor stores. These inputs retain allocation, registry and lifetime
guards. This does
not recover the separate compiled factor's installer or input owners.

AT-ENTER-029 identifies the second input as RaptureTextService
T=M+0x17CE0. Its constructor stores C=M+0x10 at T+0x8 and installs the
raw-RTTI-identified primary and secondary tables at T and T+0x4.
FUN_0066C1A0 retains C at control+0x1990 and T at control+0x1998.
It also stores embedded addresses C+0x664 and C+0x554 at control+0x1994
and +0x199C. The inspected control branches use T's slots +0x10/+0x30
under retained-table and branch guards. These observations preserve the
separate compiled factor owners and Enter/string identity boundaries.

AT-ENTER-031 follows the retained service into candidate-event production.
Its base constructor writes T to the shared receiver cell 0x0132CF40.
The inspected selection calls reload that cell and forward source pointer
0x0132CF60 and an index through slots +0x44/+0x48. With the retained T
table these reach FUN_0054B400/FUN_0054B420 and then FUN_00548DB0,
which constructs CandidateEventArgs with mode byte, source pointer and index
at event+0x1C/+0x20/+0x24. It dispatches the local event through
ECX=[T+0x8]+0xB4, the retained parent's secondary callback receiver.
The constructor retains the source pointer. Shared-state retention, routing,
recipient state and actual string content still qualify this path.

Before registration, FUN_00947040 obtains the DOM Name value and calls
FUN_00912D50 with complete control P and arguments value,0,1. Its wrapper uses
P+0x8 as the property receiver. On the permitted direct-value branch,
FUN_009CB580 -> FUN_009CB460 assigns the resulting string value into [P+0x8].
Rejected, binding and deferred branches remain guards. The later slot-+0x1C
attribute hook is separate from this pre-registration Name path.

FUN_00947040 registers a nonnull, unregistered control through FUN_0096E580.
That function stores its pointer in X+0x4's
name-map node+0x60 and X in control+0x298. Empty names receive a generated
name; collisions add (n). Thus successful, unchanged and collision-free
TextBox_ChatInput naming supplies the lookup and inverse-container path in
AT-ENTER-018. The Window factory separately stores its root at X+0x2C; the
X+0x30 fallback is distinct. AT-ENTER-020 qualifies the pinned payloads against
the format test, and AT-ENTER-021 follows conditional compiled construction.
Name binding/deferred branches and actual resource selection remain guards.

AT-ENTER-020 joins filename selection, decoded-buffer publication and the
format test. The request helper inserts FUN_0090F950's selected string before
the final .form or .tpl extension, preserving that extension. It probes the
candidate, then falls back to the unrewritten normalized filename when the
first probe fails. It copies
the accepted name to R+0xEC. Configured path prefixes and the selected suffix
remain guards; request acceptance alone does not identify the original file.

The queued-reader body uses complete R and a local buffer owner. It reads the
selected file, decodes an SQEX body through FUN_0090FD10 and stores the returned
pointer and decoded length at R+0x140/+0x144. A skipped mode or null buffer
does not enter either builder. FUN_00981050 compares the leading word with
0x70DD. Equality selects the compiled reader and FUN_009C9250 -> FUN_009808C0;
inequality passes that same buffer and X=[R+0xE4] to AT-ENTER-019's textual path.

The four pinned LogWidget source and exact decoded payloads were rechecked.
The form/SD-form leading word is 0x573C and the template/SD-template word is
0x523C. Those decoded payloads therefore select the textual branch when
supplied unchanged. The filename candidate, mode, actual read/decode and
successful construction remain conditional. This is a static comparison of
identified bytes with the loader test.

AT-ENTER-021 follows conditional compiled construction. The parser S retains
the same X at S+0xC. FUN_009808C0 loads the indexed factor F as ECX and passes
S explicitly to its virtual predicate and creation slots. The authenticated
CustomTextBoxFactor table 0x00FA2864 has FUN_0054D180 at slot +0xC. Its loaded
element-type index and installation in the factor table remain unjoined;
AT-ENTER-022 identifies the separate Name-property lookup used below.

That creation function retains F separately from S, compares a dynamically
mapped Name-property ID and tests its value for the pinned _ChatInput substring.
On a match, FUN_005556C0 allocates 0x1AC8 bytes and calls FUN_0066C1A0 with
F+0x4/F+0x8, constructing the same RaptureTextBox family. The actual factor
values and nonmatching/default branch remain qualified.

AT-ENTER-022 separates the element and property mappings. FUN_00981C80
expands supplied metadata into two lists of 16-byte descriptors and calls
FUN_009816F0 with ECX=M=0x0135E790 and the two table/count pairs. The mapper
compares names and stores each first matching loaded row index. TextBox is
builtin element ordinal 0x11; Name is auxiliary ordinal 1. Their getters
return u16[M+2*ordinal] and u16[M+0x94+2*ordinal], respectively. These builtin
ordinals do not establish numeric loaded IDs. The authenticated initializer
calls FUN_00981660, which fills all 74 element and 33 auxiliary entries with
0xFFFF; unmatched names retain that sentinel along this initialization path.

AT-ENTER-026 identifies the sentinel initializer's startup caller. The PE
entry at 0x009D4BAA reaches FUN_009D49CA, which calls FUN_009D8F9A before
the application function. After its C-initializer pass returns zero, the
latter walks nonnull u32 function pointers from 0x00F3E66C to exclusive
0x00F53CE4. Slot 0x00F511DC selects 0x00F25F50, whose body supplies
M=0x0135E790 to FUN_00981660. The earlier slot 0x00F50A94 selects the
resource-suffix initializer at 0x00F20520. This orders the two writes on
successful traversal with retained table entries; it does not establish
later metadata replacement, suffix selection or property-cache timing.
Neither startup table directly lists the custom factor constructor or
compiled table helpers. Other initializer calls and dispatch paths remain
qualified, and the custom-factor installer remains unresolved.

The compiled creation function caches FUN_00981F30(1), the mapped Name ID.
With B=[S+0x8] and the current section index at u16[S+0x410], FUN_00981160
returns Z=[B+0xC]+0x10*index. The count reader uses the signed byte pointed to by
[Z+0x8]; the property reader returns A=[Z+0xC]+0xC*k. FUN_009810A0 reads
the u16 pointed to by [A] as the property ID and FUN_009810C0 returns its value pointer at
[A+0x4]. The first matching Name property's value supplies the _ChatInput
test. Actual metadata row positions, mapping/cache order and the current
Name value remain guards.

AT-ENTER-023 binds the factor fields to constructor argument positions.
FUN_0054BA80 receives F in ECX. It passes its first explicit argument to
FUN_0054BA10, which stores it at F+0x4; the outer constructor stores its
second explicit argument at F+0x8 and installs table 0x00FA2864. The caller
and concrete native producers of those values remain unjoined.

FUN_009C4B40 allocates and zeroes the global element-factor table; its
exported body contains no CustomTextBoxFactor installation. FUN_009C4AD0
writes a supplied pointer at a supplied index unless that index is 0xFFFF,
which takes the nonnull pointer's virtual destructor path. The verified
reference export supplies no direct caller for the factor constructor or
these table helpers. Computed, indirect, dynamic and unanalyzed callers
remain candidates; these bounded references do not establish their absence.

FUN_00557600 receives S and the created child P. It uses X=[S+0xC], retains
the first nonnull child at X+0x30 while empty, and attaches children through
the prior parent's +0x194 receiver at slot +0x4. This candidate is distinct
from the textual Window root at X+0x2C. It applies the extracted or generated
name through FUN_00912D50 with ECX=P, then calls FUN_0096E580 with ECX=X and
explicit name,P. The shared registrar joins the same name map and P+0x298
container backpointer used by AT-ENTER-018/019. Name acceptance, collisions,
cache/fallback choice and readiness instance/order remain guards.

AT-ENTER-012 corroboration recovers the readiness writer at 0x00767028
in FUN_00766F00. The owner-state and resolved-handle/validity gates precede the
+0x5C store and FUN_00574830. Its generic writer is documented in
[the readiness study](../manifests/actor_5c_readiness_gate.json). AT-ENTER-024
follows the supplied control handle and original actor holder
through the deferred queue. Current registry association, readiness admission
and allocation remain guards; the write is not ordered against C+0x64 form
completion.

AT-ENTER-024 joins the ordinary deferred actor path. FUN_00774700 receives
the C and H=[E+0x80] supplied by AT-ENTER-012/013. On the nonready branch
whose control name differs from DesktopWidget, it constructs D with its
context API J, a control-handle pointer and H. FUN_005745F0 stores [J] at
D+0x4 and H at D+0x8. The queue receives C,D separately and stores the
derived control identifier at node+0x8 and D at node+0xC. The identifier
and record context are distinct fields.

For an ordinary control, the handle comes from G+0x70 where G=[C+0x4].
The registration branch for ordinary identifiers stores G under that
identifier in the engine registry.
With the registration preserved, the queue's resolver returns the same C.
The reached state-10 list pass checks a derived-state validity byte, stores
C+0x5C=1, then calls FUN_00574830 with ECX=D and C explicitly. The installer
writes the replacement through H=[D+0x8], the holder used by Enter dispatch.
Special control and alternate handle categories remain qualified, along
with current registration, admission, validity and allocation. The flag store
precedes the installation call and does not establish form-completion order.

AT-ENTER-004 identifies the generic adapter's string member. Its third
incoming stack argument becomes the fifth explicit argument to FUN_00713830,
which assigns vtable 0x00FD5330 and copies that string value to object+0x104.
AT-ENTER-006 recovers a conditional routed-event string producer for this
argument, and AT-ENTER-007 joins the member to Lua A4_2. AT-ENTER-009 recovers
the Text2 action source while preserving the owner/actor selection boundary.

AT-ENTER-005 identifies the _ChatInput construction branches. The markup
TextBox/_ChatInput branch in FUN_00549330 and the CustomTextBoxFactor registry
branch through FUN_0054D180/FUN_005556C0 allocate 0x1AC8 bytes and call
FUN_0066C1A0. Authenticated RTTI and constructor assignments identify the
complete RaptureTextBox table 0x00FC1594, its +0xB4 table 0x00FC146C, and its
+0x194 table 0x00FC1454. Complete-object slot +0x30 selects FUN_0066C540;
its property branch can call FUN_0066C410. These are type/property joins;
AT-ENTER-013 recovers the allocated key path. The loaded TextBox_ChatInput
child remains qualified; AT-ENTER-008 pins its resource declaration.

AT-ENTER-006 joins condition storage to a FormElement dispatch consumer.
FUN_0053D700 stores the copied condition at linked node+0x8, including its
string and bytes +0x54/+0x55. FUN_0053AF60 constructs an E+0xA0 callback
with complete FormElement receiver E and FUN_00536280. The callback reads
the E+0xF8 relation through FUN_00535B70, comparing the stored condition
string with incoming command+0x24. In its selected namespace branch for
event type 8, it passes routed event+0x28 as the third stack argument through
FUN_00574BE0 to actor slot +0x34. A LuaActorImpl receiver with table
0x00FDFB2C selects FUN_0075D5D0 there. This is a conditional dispatch join;
the actual command 0x01344D44, namespace branch, and installed actor instance
have not been selected for LogWidget.

AT-ENTER-007 identifies table 0x00FD5330 as UICommandEventParameterWithString
and slot +0x8 as FUN_00749340. It serializes members +0x4, +0x58, +0xAC,
and +0x104 in order. An empty first member still pushes one Lua nil. The
guarded invocation reaches FUN_00CD0940 -> FUN_00CCF9B0, then callback
resolution and FUN_00CCEE30 -> FUN_00CCFFE0. Successful callback setup
replaces the nil placeholder with the function, leaving the retained Lua
receiver after it. The forward operator walk pushes the four values and
invokes Lua with the push count plus one. The fourth value therefore occupies
A4_2 after receiver A0_2. Its UTF-8 operator consumes one native value,
calls FUN_00CF3340, and
pushes one Lua value. FUN_00DCE1F0 scans to NUL when creating that Lua string.
The generic event+0x104 -> Lua A4_2 join does not prove embedded-NUL
preservation or bypass AT-LUA-005's convertPronouns boundary. AT-ENTER-009
joins the resource-selected Enter action to this conditional conversion.

AT-ENTER-008 pins four named SQEX resources: LogWidget.form, LogWidget.tpl,
LogWidget.sd.form and LogWidget.sd.tpl. Both forms declare Window_LogWidget,
merge the corresponding template and give TextBox_ChatInput the Style_TextBox
style. Its Return KeyBinding names UILuaCommands.PressEnterTrigger. The style's
CommandTrigger handles that name with ExecuteCommandAction using
UILuaCommands.PressEnter, the format {CommandParameter String,%s} and
PropertyName1=Text2. These are distinct trigger and action command names.
Source replay and exact decoded-byte hashes are retained in AT-ID-013.

AT-ENTER-009 traces that action's native string production. The markup
ExecuteCommandAction branch in FUN_009498D0 allocates 0x90 bytes and calls
FUN_009B2D00. Authenticated RTTI and constructor instructions identify the
complete action table 0x0107D7F4 and its DependencyObject table 0x0107D7B8
at action+0x18. Complete slot +0x8 selects FUN_009B28C0. Attribute assignment
reaches FUN_00955010 with the complete action receiver after the property
adapter subtracts 0x18 from the DependencyObject receiver. Command index 0
looks up the exact registered name and stores the result at action+0x44;
AT-ENTER-001 supplies the registered PressEnter object. CommandParameter
index 2 retains the original format at action+0x78 and parses a parameter
at action+0x54. PropertyName1 supplies the name held at action+0x80.

FUN_009B28C0 casts context+0x8 to DependencyObject and reads that object's
Text2 property through FUN_00911020. The Text2 key at 0x0133F4FC has index 0
in descriptor 0x0133F548. With the complete RaptureTextBox receiver, the
property-read hook selects FUN_0066C540 and calls FUN_0066C410 before the
descriptor read. Descriptor table 0x00FC1724 slot +0x8 then selects
FUN_009A71C0, which invokes read function 0x0066A540 with adjustment zero,
index 0 and the destination string. That read copies TextBox+0x1980 or
fallback 0x01266B10. Thus AT-COMP-008's reconstruction/cache branch precedes
the Enter action's Text2 read. The separate function 0x0066C6D0 is the setter.

AT-ENTER-030 resolves the separate setter's descriptor adapter and cache
guards. Descriptor slot +0xC invokes 0x0066C6D0 with the complete TextBox,
selector, source and writer input. Selector 0 chooses Text2 at +0x1980;
selector 1 chooses TextExtract at +0x1988. Source resolution and low flag
bits gate the cache write and notification. The matching property-change
hook can copy an accepted nonempty source to +0x1A74. Under its notification
guard, callback 0x0066C0D0 synchronizes completion state and clears that
string before requesting a TextExtract reset. These are concrete set/clear
writers for the state tested by AT-COMP-008. They do not select the actual
retained control's branch or establish callback order or message bytes.

The action formats Text2 through %s into {CommandParameter String,%s} with
FUN_0097FD10. Its 0x400-byte local buffer has a final NUL and a 0x3FF-byte
__vsnprintf limit. FUN_0099DDF0 reparses the result as type 8, copying the
string after the comma excluding the final character into parameter+0x4.
It does not validate that byte, normally the resource format's closing brace.
At 0x009B2B74..0x009B2B7E, the action pushes context, target InputElement and
the local parsed parameter, sets ECX to its command pointer and calls command
slot +0x8. The default target is context+0x8 cast to FrameworkElement, then
adjusted by +0xB4. This command receiver is distinct from the property receiver.

RoutedCommand table 0x0106A78C slot +0x8 selects FUN_00927FA0. Its event
constructor FUN_00929100 copies type to routed event+0x24 and string to +0x28.
The selected FormElement type-8/namespace branch then supplies that string as
the third FUN_0075D5D0 argument, which reaches event+0x104 and Lua A4_2 through
AT-ENTER-004 and AT-ENTER-007. This recovers the resource-selected static
production path. AT-ENTER-013/014 join the callback key and initialization.
Loaded child, dispatch namespace/actor selection and runtime cache state
remain qualified. NUL termination,
bounded formatting and convertPronouns prevent an unrestricted byte-identity
claim.

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
macro expression branches and malformed/truncated controls remain qualified.
AT-COMP-010 joins the selected vector, and AT-CHAT-002 joins admitted fixed
controls to the native message source. External table meaning and complete
receive/render behavior remain unresolved, so a full wire decoder is not justified.

FUN_00C9D550 reaches candidate preparation at FUN_00C9D0D0, which packs
`(index << 7) | 0x7E` into a Completion record. AT-COMP-010 joins that
prepared vector to the handler's selected vector. Its special -2 low marker
does not identify the index as a fixedPhrase, item, place or wire key.

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
The conditional Enter path is AT-ENTER-032. AT-CHAT-001/002 recover the
later native parser/builder sources under separate conversion and state guards.

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
caller or join the reconstructed text to packet submission. AT-ENTER-009
recovers the indirect Text2 read for the declared Enter action. Loaded-child,
namespace and actor selection, remaining cache/source-state writers, selected
external record family/key and generic Lua argument packing remain qualified.
AT-CHAT-001/002 recover the native Map/World sources and admitted controls.

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
generic parser alone does not assign external table meaning to its controls.
AT-CHAT-002 joins admitted selector-0x2E controls to the copied message prefix.

## Selected candidate production

AT-COMP-010 joins the prepared records to RaptureTextBox selection. Here P is
the complete CompletionModule at container+0x664 and B is the complete
RaptureTextBox. FUN_00C9D0D0 appends `(index << 7) | 0x7E` to P+0x38 and
inserts an associated tuple into P+0x58. Its low marker sign-extends to -2,
so this special entry returns the upper value rather than a fixed expression.

The ordinary producer FUN_00C9C550 maps P+0x4C's signed byte through
FUN_00C9DAE0 to a category object. Direct FUN_00CB3C60 reads category+0x88.
The producer packs `(upper argument << 7) | (category byte & 0x7F)` into a
tree entry. Its virtual call at +0x10 only gates insertion. AT-ID-050
authenticates the CategoryData and CategoryDataCache RTTI tables at
0x0110C7F8 and 0x0110C818, with slot 4 pointing to FUN_00CB4060 and
FUN_00CB4500. Those bodies use the same upper argument as their row/cache
key. This is an internal native key argument; its external table meaning
requires a separate population join.

FUN_00C9D1C0 returns P+0x38's element-zero pointer for an empty filter. For
a nonempty filter it copies matching P+0x58 node+0x14 packed dwords into
P+0x74, then returns that vector's element-zero pointer. FUN_0066A730
writes the selected pointer through B+0x1A60. FUN_0066AB10 passes it and the
selected index to FUN_00C9BC40. The byte map at P+0x4C is distinct from this
dword vector.

AT-COMP-011 identifies the provider in this constructed path as ExcelModule.
The application constructor forwards it through MainModule and the element
container to CompletionModule P+0xC. AT-ID-054 authenticates its table at
0x01108C00. Its guarded slot-1 lookup returns a populated sheet from map
node+0x60. The inspected population path constructs an ExcelSheet through
FUN_00CB04B0, whose table 0x0110C6D4 is authenticated by AT-ID-055.

The xtx/_fixedPhrase path reaches this lookup. D550 initializes its upper
argument through ExcelSheet slot +0x20, FUN_00CAF310, reading byte zero at
sheet+0xC. Its row call at +0x30, FUN_00CAF2A0, forwards the iteration index
and upper-argument output address to sheet+0x40 backend slot +0x1C. On the
ready path, FUN_00CB0140 constructs CacheAll<ExcelEntry*> through
FUN_00CB16D0; AT-ID-056 authenticates its table at 0x0110C670. Slot +0x1C,
FUN_00CB1AF0, writes FUN_00CB1870(index) through that output address. The
mapper returns the original index for an empty range vector, otherwise the
containing range's base plus the remaining index. Thus an admitted row replaces
the initial byte with the mapped native key used by C9C550. The row supplies
field 0 minus one for the separate category byte.

This recovers native key production. AT-COMP-012 owns the cache construction
and population joins below. AT-COMP-016 establishes conditional fixedPhrase
native-key/CSV-row-key equality under named-source and cache-state conditions.
An actual selected backing-file row, external family and locale remain qualified.

## Native cache loading

AT-COMP-012 joins ExcelSubSheet construction to conditional row completion and
CacheAll installation. The constructor FUN_00CC3330 obtains the native range
values at subSheet+0x14/+0x1C from descriptor calls. Those values supply the
AT-COMP-011 range pairs. They are distinct from the payload words later copied
by FUN_00CC3590 into the sheet and subSheet vectors. AT-COMP-016 identifies
which source reaches CacheAll and keeps the enabled ordinal separate.

The stored provider at subSheet+4 supplies resource requests. The authenticated
ExcelSubSheet slot +0x4 dispatches successful completions through
FUN_00CC39F0. Its bulk handler FUN_00CC30C0 constructs rows from a positive
fixed stride or retained offset spans, skipping equal adjacent offsets. It
submits each constructed row under subSheet+0x14 plus the block slot index.
The indexed handler FUN_00CC3240 constructs a missing row from one payload.
Both use backend slot +0xC, authenticated as FUN_00CB1930, to install the row
pointer in CacheAll storage. FUN_00C9A6A0 consumes fields according to the
parent sheet's type bytes and sets the row readiness byte. These are sheet-row
decoding observations, not a chat control decoder.

The independent backing study is
`xivl-client-data:manifests/fixed_phrase_backing_rows.json` at revision
`5748ee862ae7610e513afb9a2587fd8f7c7a634f`. AT-COMP-012 pins its digest and
locators. Its sparse row keys, enabled ordinals and merged CSV iteration
indices remain separate from this native block slot index.

AT-COMP-013 identifies the static descriptor names and concrete request
owner below. AT-COMP-014 joins conditional named metadata/request keys and
pathname producers; its `missingEvidence` owns the remaining source, payload
and row-identity boundaries.

## Native descriptor and resource ownership

AT-COMP-013 recovers the constructor inputs for begin, count, offset and
enable at globals 0x013778A0, 0x013778F8, 0x01377950 and 0x013779A8.
AT-ID-060 authenticates each initializer body, complete literal, constructor
call and destructor registration. The file-backed length cell at 0x00F67298
initially contains 0xFFFFFFFF; FUN_00447260 uses strlen for that sentinel.
The bodies therefore establish static name construction, while actual
initializer execution, later retention and attribute values remain qualified.

The same evidence separates mode and lang in FUN_00C98580. Its module+0x38
checks compare the mode query result with server/client. The later lang query
passes through FUN_00D34D20 and compares against module+0x14. Those are
separate admission conditions; mode is not a locale identifier.

The application owner constructs ResourceModule through FUN_00C99090 at
owner+0x50 and supplies it to ExcelModule+0x8 through FUN_00C98C30.
FUN_00C98580 passes it to FUN_00CB04B0 as explicit argument 1, which forwards
it to FUN_00CC3330 as explicit argument 1. CC3330 stores it at subSheet+4.
The child DOM metadata is explicit argument 2 in both constructors and
supplies descriptor queries. These ordinals exclude hidden ECX and distinguish
the two objects.

AT-ID-060 authenticates ResourceModule table 0x01108C3C and its request cells:
+0x4 selects FUN_00C99130 for numeric IDs; +0x8 selects FUN_00C992D0 for
pathnames. CC3330's converted child value remains the numeric request/cache
key through lookup, registration and request storage at +0x58. Lookup also
requires its range/readiness guards. That key is separate from the mapped
Completion row key.

The numeric branch derives a pathname through FUN_0044B3A0. Its flag-zero
branch uses loaded table inputs; its other branch formats a data path from
the key's four bytes. Both combine with prefix object 0x0132CB98. The explicit
pathname method also uses that prefix and supplies numeric key 0xFFFFFFFF on
a miss. Static key preservation does not establish the selected flag, prefix,
table, actual file-open result or payload identity.

## Native metadata and pathname inputs

AT-COMP-014 joins the infofile request to the source callback. C98580 queries
the infofile descriptor and requests either a numeric ID or pathname through
ResourceModule. Both branches supply ExcelModule+4 as the ResourceEvent
receiver. On success, C98A90 obtains the source buffer and length, transforms
and parses XML, queries sheet descendants and passes them to C98580. Actual
request completion and source bytes remain conditions.

AT-ID-062 independently verifies the fixedPhrase metadata against the pinned
backing report. Master 0x01030000 names xtx/_fixedPhrase with infofile
0x0B4508E6. The definition declares client/all sheets for five locales, four
types u32/str/str/str and one block per locale with begin 100 and count 2926.
Its English block carries data 0x0B4508EA, enable 0x0B4508EB and offset
0x0B4508EC. The other locale tuples remain in AT-ID-062.

If C98580 receives that authenticated master DOM and its infofile value,
the numeric branch requests definition 0x0B4508E6. If the authenticated
definition supplies the English data child and the client/lang gates admit
it, CC3330 stores 0x0B4508EA at subSheet+0xC; CC3730 passes it unchanged to
the numeric resource method. These are conditional resource associations.
The definition ID, data ID and mapped Completion row key are distinct.

The initial request members expose caller inputs. ExcelModule slot 2,
FUN_00C98110, requests its first explicit argument as a pathname; slot 3,
FUN_00C980D0, requests it as a numeric key. Slot 5, FUN_00C983E0, updates
language from its pointer argument and can request stored module+0xC or
delegate to FUN_00C98010's pathname setup. AT-COMP-015 identifies the
guarded application-owner master input and its stored numeric key below;
other caller inputs and actual delivered source bytes remain qualified.

Pathname state also has identified producers. FUN_004B2D30 copies its supplied
prefix into 0x0132CB98. B2DF0 supplies it from configuration/owner inputs;
one configuration branch writes mode 1. Its alternate branch calls
FUN_0044B690 with a derived filename and writes mode 0 after successful table
loading. That loader opens the supplied file and populates table 0x0132CB8C.
AT-ID-062 separately pins the raw initial mode byte and the formatted DAT
literal. The actual configuration, retained prefix/mode, table contents and
delivered resource payloads remain unobserved.

AT-COMP-016 owns the conditional fixedPhrase block-key association and remaining
payload and selection boundaries. Enable ordinals, native block slots and
merged CSV iteration remain separate.
Item/place producers, generic Lua packing, earlier pronoun inputs and
receive/render lookup retain their existing qualifications.

## Native master-source input

AT-COMP-015 identifies the guarded application-owner input to the initial
master request. In B2DF0, FUN_00443E40(2,8,0) supplies a configuration value;
the unsigned condition `(value - 4) > 2` selects resource key 0x01030000.
The other branch supplies 0x27950000, whose resource identity is not assigned
here. The exact predicate is recovered; its executed configuration is unobserved.

The retained stack trace joins the selected key to C97FC0's first explicit
argument. Its two occurrences of ESP+0x30 refer to the same logical local
because both occur with two arguments on the stack. The caller supplies
hidden ECX from owner+0x58 and explicit arguments `(key, 0, pointer to
owner+0x38, 0)`. Its separate owner+0x5C store precedes loading the key.
AT-ID-064 independently authenticates the guard, literal stores and call span.

C97FC0 stores the key at ExcelModule+0xC, mode 0 at +0x38, state 0 at +0x3C
and the dereferenced owner language at +0x14. It submits that same key through
ResourceModule numeric slot +0x4, with the adjusted event receiver module+4.
AT-COMP-013 identifies the concrete numeric method as C99130. The stored key
also supplies C983E0's conditional language-refresh request.

Under this owner branch, the initial request therefore names master
0x01030000. If formatted-DAT mode is admitted, its key bytes derive
data/01/03/00/00.DAT combined with the supplied prefix. AT-ID-064 verifies the
preserved installed master against the pinned backing report. If that source
reaches the successful C98A90 callback, AT-COMP-014's metadata path requests
fixedPhrase definition 0x0B4508E6 and admitted locale resources.

Actual path selection, delivered payloads and historical instance/locale remain
qualified. AT-COMP-016 joins the child-block range source and conditional
fixedPhrase row-key identity below. Its `missingEvidence` owns the remaining
selection-family and payload boundaries.

## Native block slots and conditional CSV keys

AT-COMP-016 identifies CacheAll's range source. On a CB0140 transition to
sheet+0x3C cache state zero, sheet+8 becomes backend kind zero. CB0140 walks
the child pointers at sheet+0x30/+0x34 and reads each child's begin/count at
+0x14/+0x1C through CC26E0/CC26F0. CB16D0 copies these pairs through CB1530
into the backend vector at +0x14/+0x18. The separate enable words copied into
sheet+0x44 and subSheet+0x40 do not supply these pairs. This cache state is
distinct from ExcelModule's client/server mode.

The offset and enable descriptors select completion discriminators -1 and -2,
respectively. This establishes request/handler identity, without asserting
asynchronous completion order. Offset completion CC3850 can update the child
count from the payload size divided by four. The definition declares 2926
slots beginning at 100, while the chs offset file has 2036 entries. A retained
backend's count depends on child state at its construction.

Bulk row completion CC30C0 submits native key `begin + blockSlot`, skipping
equal adjacent offsets on the offset path. CB1930 maps that key through
CB17C0 and stores the row pointer at `storageBase + storageIndex * 8 + 4`.
AT-ID-066 supplements the shorter retained listing with an independent raw
PE read through CB17C0's return. A matching pair yields prior counts plus
key minus base. Its upper comparison admits `key == base + count`, and
exhaustion returns the accumulated counts. These branches do not establish
a safe general inverse or bounds contract.

For a successfully constructed row from the authenticated fixedPhrase locale
payloads, with one CacheAll pair `(100,N)` and `blockSlot < N`, the writer
maps key `100 + blockSlot` to storage index `blockSlot`. The admitted iteration
mapper CB1870 returns that same key. The backing report identifies the
corresponding nonempty offset span as CSV row key `100 + blockSlot`. This is
conditional row-key equality, without an observed historical selection.

Row 974 has block slot 874 and enabled ordinal 278 in ja/en/de/fr or 247 in
chs. Row 1255 has block slot 1155. Row 3025 has block slot 2925, enabled
ordinal 755 and merged CSV iteration index 757 in ja/en/de/fr. The block begin
is separate from each anchor's sparse enable-range base. Under this cache
path, the admitted D550 iteration index is the storage/block slot.

An arbitrary selected control still needs an external family association.
Actual delivered payloads, retained cache state, selected locale and item/place
producers remain qualified. Generic Lua packing, earlier pronoun inputs and
receive/render lookup retain their separate limits. No complete semantic
control resolver follows from this block association.

## Selection-family boundary

The fixedPhrase table path
FUN_004DAA10 -> FUN_004DA680 -> FUN_00447260("xtx/_fixedPhrase") ->
FUN_00C9D550 reaches Completion candidate preparation at FUN_00C9D0D0. That
candidate vector and ordinary tree entries join the selected RaptureTextBox
vector through AT-COMP-010. External family/table-key identity and the
receive-side lookup through generic renderer FUN_007906C0 remain unresolved.
The choice between rendering and forwarding is not established by the selected
record join.

The producer classifications are therefore:

- fixedPhrase: native candidate and conditional send paths recovered by
  AT-COMP-010/011 and AT-CHAT-001/002; selected external table/key unresolved;
- item selection: unresolved lookup and serialization producer;
- place selection: unresolved lookup and serialization producer;
- unsupported families: no family is classified unsupported by this pass;
- row key versus field 0/category: the native upper key argument and category
  byte are separated by AT-COMP-010; external table identity remains qualified.

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
retained in the manifest. AT-COMP-010 joins selected-record production and
AT-CHAT-001/002 recover conditional native packet-source joins.

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

Recipes AT-GH-088 through AT-GH-096 and identities AT-ID-011 through
AT-ID-014 support AT-ENTER-008 through AT-ENTER-012. The pass authenticated the
program, checked all 60 decompilation targets and all 41 listing targets,
read the required PE/RTTI cells, and retained bounded disassembly for
unanalyzed property adapters. The four named resource extraction replays
passed; all 2671 Lua bodies matched the immutable and current manifest pins
under the documented CRLF-pair-to-LF normalization.

The optional passive observation checklist is retained in the manifest. It
requests the identified client and locale, exact UI selection, repeated sparse
keys, token-only and literal/token/literal examples, raw source/message bytes,
direction, and independently observed rendering. Any owner-supplied local
preserved-client test remains non-retail corroboration.

Recipes AT-GH-097 through AT-GH-100 and identities AT-ID-015/016 support AT-ENTER-013/014.
Both consolidated exports contain all 33 requested exact-entry sections; the
listing reports COMPLETE. The selector/factory exports complete six exact-entry
targets each. All 2671 normalized Lua bodies matched their
immutable and current manifest pins. Failed or containing-entry exploratory
requests remain private and are not promoted as exhaustive negative evidence.

AT-GH-101/102 cover ten exact-entry child/namespace targets each. AT-ID-017
pins the bounded special-name initializer; AT-ID-016 pins its literal and
the WaitLoadFormResumeChecker table. AT-ENTER-015 uses these initializer and
receiver instructions instead of inferring an excluded global value.

AT-GH-103/104 cover ten exact-entry form-wait targets each. AT-ID-018
authenticates the shared return fragment, avoiding a containing-function
misidentification. AT-ENTER-016 preserves separate Lua object, native control,
FormElement, checker and thread coordinates.

AT-GH-105 through AT-GH-116 and identities AT-ID-019 through AT-ID-022
support AT-ENTER-017 through AT-ENTER-019. The consolidated exports cover
72 exact-entry decompilation targets and 72 listing targets. Each listing
reports COMPLETE. PE reads authenticate the handler/collection, markup,
extension, Window and TextBox tables and factory literals; bounded LLVM
disassembly verifies the callback tail and load-cleanup return. AT-GH-117/118
and fresh separate-project identity AT-ID-023 corroborate 18 readiness targets
each. All 2671 normalized Lua bodies again matched immutable and current pins.
AT-GH-119/120 add six exact-entry Name-property/substring targets each and
AT-ID-021 authenticates the separate Name callback jump fragment.
Failed and containing-entry exploratory requests remain private, outside these
promoted recipes.

AT-GH-121 through AT-GH-132 and identity AT-ID-024 authenticate the resource
selection and buffer path. Each exporter covers 26 exact-entry targets;
all six listings report COMPLETE. AT-GH-133 verifies the suffix-object
reference candidates. AT-ID-025 rechecks the four AT-ID-013 source/decoded
identities and leading-word comparison. AT-ID-026 pins loader literals and
the bounded suffix-object initializer. No excluded global bytes are used as
runtime string values. All 2671 normalized Lua bodies matched their immutable
and current pins.

AT-GH-134/135 and fresh worker-project identity AT-ID-027 cover 19 compiled
builder entries each; the listing reports COMPLETE. AT-ID-028 authenticates
the backed CustomTextBoxFactor table and _ChatInput literal. Together the
new pairs cover 45 decompilation and 45 listing entries, plus AT-GH-133's
one reference target. PE evidence identifies backed cells; populated global
state remains conditional.

AT-GH-138/139, AT-GH-140/141 and AT-GH-143/144 cover 15 decompilation and 15
listing entries in total for mapping, property readers and initialization; each listing reports
COMPLETE. AT-GH-142 verifies two mapping-global reference targets.
AT-ID-029 authenticates the primary project and AT-ID-030 pins the two
literals and bounded initializer disassembly. Populated IDs remain conditional.

AT-GH-136/137 cover 14 exact-entry registrar and owner-candidate functions
per modality; the listing reports COMPLETE. AT-GH-145 verifies eight
reference targets and AT-ID-031 authenticates the worker project. Together
this pass covers 29 decompilation and 29 listing entries and ten reference
targets. Constructor parameter positions do not establish their input owners.

AT-GH-146/147 cover 34 exact-entry owner-readiness and registry functions
per modality; the listing reports COMPLETE. AT-ID-032 authenticates the
primary project and AT-ID-034 pins the complete DesktopWidget branch literal.

AT-ENTER-025 joins the compiled metadata lifecycle. FUN_009C4B40 loads the
authenticated /Data.win32.tbin path and passes the returned pointer and
stack-derived length to FUN_00981C80. After parsing, it allocates and clears
the factor table at global 0x0136358C. The initializer's direct constructor
candidate uses table 0x01084FD0, distinct from CustomTextBoxFactor, and its
explicit element selectors omit TextBox ordinal 0x11. The compiled consumers
index the same factor table and dispatch its virtual methods. This qualifies
the remaining installer edge: no recovered indirect or data-driven dispatch
places CustomTextBoxFactor in the loaded TextBox slot or supplies its two
constructor values. Loaded IDs, load success and execution remain guards.

AT-GH-148/149 cover 36 matched exact-entry metadata lifecycle functions;
the listing reports COMPLETE. AT-GH-150/151 cover eight and six recorded
reference targets. AT-ID-033 authenticates the separate project; AT-ID-035
pins the loader literal and thunk. Script bytes match both observed milestone
revisions. The producing revision was reconstructed from output timestamps
and the host reflog; it was not captured at invocation.

AT-GH-152/153 cover six matched exact-entry startup, mapping and suffix
functions; the listing reports COMPLETE. AT-ID-036 authenticates the project.
AT-ID-038 pins both startup table intervals, their selected slots and the
bounded initializer bodies. These table identities establish direct member
selection, not the effects of every indirect initializer.

AT-GH-156/157 cover 15 matched exact-entry extension, textual and compiled
consumer functions; AT-GH-158 is a verified complete 16-target reference
export. AT-ID-037 authenticates that separate project before its exports.
AT-ID-039 pins the raw constructor type identities and registration keys.
AT-ENTER-027 keeps textual inputs separate from compiled factor ownership.

AT-GH-162/163 and AT-GH-164/165 cover matched exact-entry owner, TextBox
and service-consumer functions; both listings report COMPLETE. AT-ID-041
authenticates the project before these exports. AT-ID-042 pins the raw
RaptureTextService RTTI name, subobject offsets and selected service slots.

AT-GH-169..178 cover matched service-state, forwarding and candidate-event
functions, with COMPLETE listings. AT-ID-044 authenticates the primary
project before the exports. AT-ID-045 pins the selected service slots and
CandidateEventArgs raw RTTI identity; it does not assert full table extents.

AT-GH-166/167 and AT-GH-179/180/181/182 cover matched state/cache functions.
AT-GH-168/183 verify recorded-reference exports. AT-GH-184..189 cover
matched property adapters and the clear helper. AT-ID-043 authenticates the
worker project; AT-ID-044 authenticates the primary project. AT-ID-046 pins
the bounded untyped bodies, descriptor slots, property array and TextExtract
literal. The exports establish positive static joins under the recorded
branch, receiver and retention guards.

AT-GH-231 through AT-GH-249 and fresh identity AT-ID-057 support AT-COMP-012.
The exports cover 32 exact-entry decompilation targets and 32 listing targets;
each listing reports COMPLETE. The reference export verifies three recorded
reference targets. AT-ID-058 authenticates the selected ExcelSubSheet,
CacheData and CacheAll cells and their raw RTTI identities. The record claims
the row writer's call and store, without promoting the decompiler's full
FUN_00CB17C0 inverse-map or bounds behavior from its shorter retained listing.

AT-GH-250 through AT-GH-259 and fresh identity AT-ID-059 support AT-COMP-013's
string constructor, concrete request methods, numeric key cache and conditional
pathname derivation. AT-ID-060 independently pins the raw initializer/literal
inputs, length sentinel, ResourceModule RTTI and
selected request cells. These static joins preserve the selected-input and
runtime limits in the record.

AT-GH-260 through AT-GH-272 and fresh identity AT-ID-061 support AT-COMP-014.
The paired exports cover 19 exact-entry targets per modality; each listing
reports COMPLETE. The reference export verifies seven recorded address targets.
AT-ID-062 independently authenticates the raw mode/format, ExcelModule table
cells and selected master/locale metadata. Recorded-reference coverage and
table membership do not classify uninspected methods as absent producers.

AT-GH-273/274 and fresh identity AT-ID-063 authenticate the exact C97FC0 entry
and paired complete listing. The retained AT-GH-136/137 owner exports supply
its guarded caller input and stack relationship. AT-ID-064 independently pins
the raw configuration guard, both immediate stores, final call span and the
preserved master file's size/hash. This recovers a conditional source request;
actual callback payload and selected locale remain qualified.
