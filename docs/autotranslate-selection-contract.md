# FFXIV 1.23b auto-translate selection contract

The retained static evidence recovers selected Completion records, native
category/key production and conditional chat submission paths. An admitted
fixed control reaches the message field unchanged when the copied prefix
includes it completely. Generic Lua argument packing, earlier pronoun
replacement, a selected external CSV table/key and receive row lookup remain
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
Actual delivered payloads, retained cache state and selected locale remain
qualified. AT-COMP-017 recovers the conditional place producer below; item
production remains separate. Generic Lua packing, earlier pronoun inputs and
receive/render lookup retain their separate limits. No complete semantic
control resolver follows from this block association.

## Place descriptor and target-key production

AT-COMP-017 follows the data-driven place descriptor into ordinary Completion
records. In the authenticated English fixedPhrase backing report, row 2104
field 1 names `xtx/placeName` with ranges and suffix `#200`. When that row is
supplied, D550 reads field 1 through C9A480 and parses it through C9CA50.
The nonzero-suffix branch constructs CategoryDataCache through CB4420, which
stores the suffix at category+0x8C. This conditional source association does
not establish the delivered placeName payload or historical locale.

The descriptor candidate and target key have distinct roles:

| Value | Production | Consumer |
| --- | --- | --- |
| Descriptor category index | D550 subtracts one from field 0 and passes it to C9D0D0. | The special candidate `((field0-1)<<7)|0x7E` makes C9BC40 return its upper category index without constructing a fixed expression. |
| Target native key | Ready CacheAll CB1990 supplies the ordinal, or `pair.base + withinPairSlot` for a ranged backend. | C9DC80 forwards it as C9C670's third explicit argument for ordinary record production. |

C9DB10 counts the 0x58-byte descriptor vector, rather than external place rows.
For complete CompletionModule P, C9CFA0 installs primary table 0x01108E40 at
P, secondary table 0x01108E2C at P+4 and third table 0x01108E20 at P+8. The
ExcelModule pointer is at P+0xC. C9C190 is primary slot 1; C9C0A0 is secondary
slot 1, whose adjusted this+8 reaches that same provider pointer.

On P+0x14 readiness, C9C190 walks category objects and bounds each +0x89
descriptor index against the vector at P+0xDC. C9DB30 selects the descriptor
at `[P+0xE0] + index*0x58`. ExcelModule slot 1, C981D0, conditionally returns
the populated ExcelSheet from its map node+0x60. Sheet slot +0x1C, CAF300,
reads sheet+0xB; slot +0x34, CAF2F0, dispatches through sheet+0x40 backend
slot +0x20. C9C190 supplies a temporary CompletionCacheFunc and the descriptor
context to that iteration.

For the recovered ready CacheAll backend, slot +0x20 selects CB1990. With
range pairs, its row pointer comes from
`storageBase + 8*(priorCounts + withinPairSlot) + 4`. It supplies the separate
native key `pair.base + withinPairSlot` and forwards the descriptor context.
With no pairs, it uses each ordinal and corresponding storage pointer.

CompletionCacheFunc slot +4 selects C9DC80. A nonnull row pointer, the
sheet-selected field and its guarded TextModule branch supply text to primary
slot +8, C9C670. The callback's first explicit native-key argument becomes
C9C670's third explicit argument. The listing at C9C764 reads `[ESP+0x34]`
with ESP at entry-0x28, so this is entry+0xC. C9C768 shifts that key by seven
and combines it with category+0x88 masked to seven bits before C9E650 inserts
the packed ordinary record into P+0x58. The raw stack relationship governs
this key assignment where the decompiler's parameter label differs.

C9C670 also requires readiness, admitted text and category admission. It
resolves the category through the bounded byte-map accessor 006CE260 and
C9DAE0, then calls category slot +0x10. CategoryData and CategoryDataCache
select CB4060 and CB4500 respectively. CB4500's guarded cache record at +0x54
is separate from the ordinary P+0x58 tree record.

An admitted ordinary record follows the existing AT-COMP-010 selected-vector
join and C9BC40 formatter branch. AT-COMP-007 owns internal fixed-control
construction; AT-CHAT-001/002 own conditional chat-source preservation. The
descriptor category candidate alone does not establish a serialized place
control. AT-COMP-019 recovers the TextModule output handoff and category
admission guards below. Actual output bytes, selection and earlier pronoun
processing remain qualified.

AT-COMP-018 authenticates the named placeName payload and conditional CSV-key
association below. Actual delivery, child/backend state, selected locale and
target row remain qualified. Matching receive/render lookup remains unresolved.
A place-name association also does not choose a unique zone: the static
crosswalk associates placeName key 1051 with zone keys 133 and 230. It does
not justify using a native place key as a GM zone ID.

## Place backing and conditional CSV keys

AT-COMP-018 pins `xivl-client-data:manifests/place_name_backing_rows.json` at
revision `90d814d0642a12fa32fbaf5f78474bfe767bb00b`. The report authenticates
game master `0x01030000` to the named placeName definition `0x0B45087C`, then
each locale's data, enable and offset resources to `xtx_placeName.csv` rows.
Each definition has one block beginning at 0, with 8002 declared slots and
8002 offsets. The 30 sparse enable ranges name its nonempty spans; they are
separate from the child begin/count that supplies a CacheAll pair.

All declared fields match the corresponding authenticated CSV cells. The
ja/en/de/fr payloads each contain 923 rows; chs contains 883, with 40 empty
CSV-only cells in column 8. Their union equals the 923 merged CSV keys.
Rich controls are compared as opaque framing bytes, without evaluating their
expressions or establishing TextModule output.

For a successfully constructed row from these authenticated payloads, one
ready CacheAll pair `(0,8002)` and `blockSlot < 8002`, the AT-COMP-016 row
writer supplies key `blockSlot` and stores it at storage index `blockSlot`.
The AT-COMP-017 iterator supplies that same key and corresponding row pointer
to C9DC80. The report identifies the nonempty span by external CSV row key
`blockSlot`. This is conditional target-key equality. The mapper's inclusive
upper comparison and exhausted-range return do not establish a general safe
inverse or bounds contract.

Key 1051 is block slot 1051 and CSV iteration 101. Its enabled ordinal is 101
in the four main locales or 99 in chs; its enable-range base is 1051, while
the block begin is 0. None of those ordinal/range coordinates replaces the
native target key or the separate descriptor category marker.

This association does not identify an actual selected control. Historical
payload delivery, retained cache state and selected locale remain qualified.
AT-COMP-019 joins TextModule output ownership and guarded category admission
to ordinary record production. Selected field, retained state and actual output
bytes remain conditional. Generic Lua packing, earlier pronoun processing,
item production and receive/render lookup retain their separate limits.

## Place text output and admission

AT-COMP-019 resolves the descriptor mode writer. C9CA50 initializes its output
byte to zero and sets it to one only after a parsed record matches the
authenticated `noun` literal at 0x01108D98. The English fixedPhrase row 2104
numeric-range placeName descriptor has no noun marker and selects mode zero.
D550 copies that byte to +0x54 of its 0x58-byte descriptor, which C9ECD0
appends. C9C190 supplies the byte as CompletionCacheFunc+0xE. It is separate
from the category marker, suffix capacity and native target key.

For complete TextModule T, table 0x01108F70 selects C0EA60 at +4, CA1D60 at
+8, CA0930 at +0xC, CA00C0 at +0x18 and CA1D40 at +0x24. In mode zero,
C9DC80 constructs its output at the fixed stack base+0x64 and pushes that
address before C0EA60. The getter returns T+0x18 with no argument cleanup,
leaving the output address as CA1D60's third explicit argument. That method
passes the source character pointer, buffer and same output through CA1D40
to CB2760. CA1D40 adjusts this to T+4, so the parser's callback vector at
subobject+8/+0xC corresponds to complete T+0xC/+0x10.

CB2760 sends ordinary segments to the caller output through 00447CF0. At
opening byte 02 it looks up the selector callback under its bounds guards.
A null callback uses CB2D50 to obtain the length and copies the original
control sequence. A nonnull callback receives the buffer/output arguments;
a zero callback result fails. This recovers the output handoff, without
establishing every control's semantics or universal byte preservation.

C9DC80 requires a nonnull row and reads the sheet-selected field. Mode zero
calls C9C670 only on a positive parser result. Its pointer at C9DDBB is
stack base+0x64 after accounting for the preceding key push, so the constructed
output reaches ordinary Completion admission. The nonzero alternative uses
the same constructed base+0xB8 output for CA00C0 and C9C670, without testing
CA00C0's return. CA00C0 selects a typed source/conversion path or the
CB8AF0 backend. AT-COMP-022 below resolves its concrete provider and output
dispatch. The localized result remains qualified; that alternative is separate
from row 2104's mode zero.

C9C670 applies readiness, nonempty-text, leading-period and literal guards,
then calls the resolved category's +0x10 admission method. CategoryDataCache
selects CB4500. CB3D50 accepts an empty range vector or any inclusive unsigned
lower <= nativeKey <= upper pair. CB4500 also applies its last-byte string
guard. A matching nonnegative-key cache row is found by `(row+0x54)>>7`;
that branch calls CB4B80, marks +0x90 and returns zero, so it does not admit
a new ordinary record. Negative keys use a separate text comparison.

The new-slot path checks current count against suffix capacity, slot availability
and pin/eviction state. An obtained nonzero slot receives the output string,
packed key/category at row+0x54 and list publication. Only a nonzero category
result reaches C9C670's ordinary-tree insertion. The category cache row and
ordinary tree record remain distinct. Their admitted records use the completed
selection, formatter and conditional chat joins.

AT-COMP-020 below owns the selected-field writers and finite mode-zero
callback association. Delivered payloads, retained state and actual
locale/selection remain conditional. AT-COMP-022 owns CB8AF0's concrete methods
and guarded English destination write. This path does not establish
a receive/render resolver, unrestricted Lua/pronoun preservation or a unique
zone from a place key.

## Place field selection and mode-zero callbacks

AT-COMP-020 recovers the ExcelSheet selected-field writers. CB04B0 initializes
sheet+0xB to 0xFF. CAFA80 compares the first parsed SHEET record with the
authenticated `DEF` literal at 0x0110C558. Under its record-count guards,
an equal comparison admits decimal conversion of the second 0x54-byte record
and stores the low byte at sheet+0xB. The conversion argument 10 is the radix.
CB04B0's alternate child-index path fills that byte only while it remains 0xFF.
CAF300 reads it, and C9A480 maps the selected index through the row descriptor's
byte map at +0x14 to the corresponding four-byte row slot. A writer alone does
not establish the selected locale's numeric field or an observed instance.

The authenticated initializer at F2C990 constructs DAT_013773F0 from the
literal `index` at 0x0110C524 through 00447260. This identifies the child-index
branch without treating excluded global memory as an observed value. The pinned
placeName definition lists first indexes ja=0, en=1, de=4, fr=6 and chs=8.
CB04B0 calls CAFA80 after its child loop, allowing an admitted override to
replace the index default. AT-COMP-021 resolves that query for the pinned
definition's parameter bytes. For a successfully constructed sheet with
matching index children and parameters, the installed table and initial fallback
state retained, those first indexes remain selected on constructor return.
Actual delivery, selected locale and subsequent mutation remain conditions.

The installed ExcelSheet table 0x0110C6D4 has CAF7B0 at slot +0x24, cell
0x0110C6F8. The constructor initializes an empty parameter map at sheet+0x20.
CAFA80 splits its parameter string on `[]`, then each group on `|`, and inserts
only groups yielding two strings. The first string becomes the node+0xC key;
the second becomes the node+0x60 value. The insertion path
913B20 -> 913600 -> 913240 -> DA8390 copies these two 0x54-byte objects.

CAF7B0 consumes one key argument and returns the matching value string object
or empty object 0x01266B10. Both exits use RET 4. At CAFD6D, CAFA80 has already
pushed the output vector and semicolon delimiter below the `SHEET` key. The
query consumes only the key; CAFD6F pushes its returned source object, and
0044F770 separately splits that string into the vector. The query's return
is therefore a string object, with three cdecl arguments belonging to the
following splitter despite its incomplete decompiler signature.

CB0B90 -> 9130A0 compares node keys through 446EF0 -> 445B70. The comparator
uses the smaller stored byte count and signed byte differences, with no case
folding on this path. It distinguishes `NOUN` from `SHEET` at their first byte;
this does not establish general full-key equality. The English parameter
`[NOUN|SGL;2/PLR;2/VOW;=0/CNT;=0/DEF;3]` inserts one `NOUN` pair. Its `DEF;3`
is value content, and the other locale parameter attributes are absent. With
these inputs alone in the new map, `SHEET` lookup misses.

The fallback object's initial buffer is a NUL byte, its stored byte count is 1
and its cached character count is 0. For that empty source, 446B10 returns -1
before 0044F770 can append any records. CAFA80 clears its temporary vector before
the query, so the empty-result path fails the nonempty SHEET guard and never
reaches the override store at CAFE14. The English noun parameter therefore
does not select field 3 on this constructor-local path. This is a bounded
parameter/field association, without a historical instance or rendered output.

TextModule construction also establishes a finite callback association.
CB33A0 creates 0x37 callback slots with zero fill through
C9A390 -> C9A140 -> A54320 -> A542F0. CA0390 installs selector 0x09 at
`[T+0xC]+0x24` and has no stores for selectors 0x10, 0x16, 0x1A, 0x1D or 0x1F.
Those five slots therefore remain null in the constructor-populated vector.
Absent subsequent mutation or replacement, CB2760 copies their original valid
control sequences into its output. This is a conditional parser-output claim;
it does not establish universal preservation through earlier pronoun processing
or a received-message renderer.

The complete raw CA0390 span, 0x00CA0390..0x00CA0897, matched the retained
constructor listing's 30 callback stores; its 1288 bytes had SHA256
`765FC7AC409646D82979EA5C2DEABABA0EC282F0409CE6BABF50450BC5ADD347`.
The final call at 0x00CA087C passes separate destination T+0xB4 and selector
0x1D to CB25A0. Its raw 48-byte span, 0x00CB25A0..0x00CB25CF, had SHA256
`C78C3182F737C3186C36E9781A7E6A0BC16C8381BA51F8B3E08611265A968FB2`.
It supplies bytes 02, the selector, 01 and 03 to 447950 using that destination;
this call is not a callback-vector store. Bounded PE32/Capstone inspection
used the authenticated executable above and agreed with the retained listing.
Consequently the observed empty `02 1D 01 03` and one-byte-payload
`02 1A 02 01 03` / `02 1A 02 02 03` forms use CB2760's same null-slot
copy path under unchanged callback state. This identifies parser output,
without assigning space or italic rendering semantics.

Selector 0x09 takes a different path. Its installed target, B24230, loads the
vtable from ECX and jumps through slot +0xC. CB2760 supplies ECX=T+4;
the installed table 0x01108ECC has C9F140 at cell 0x01108ED8. C9F140 parses an
initial expression value through CB2D50. A zero consumed length fails. It
subtracts one from the decoded value, advances across that many expression
components using CB3290, then submits the resulting component to CB2AE0.
A nonzero final-helper result returns the outer control payload length;
otherwise it returns zero. The return is separate from the buffer and output
arguments. CB2760 rejects a zero callback result.

For CB2AE0's final 0xFF string component, the helper parses its length,
temporarily replaces the byte after the string with NUL, calls CB2760 on that
string with the same buffer/output, and restores the byte on both return
branches. This recovers recursive output and return guards. It does not decode
every expression, select a branch for an observed locale or prove arbitrary
malformed-input safety. The completed mode-zero handoff requires a positive
parser result before ordinary Completion admission; it does not test generated
output length.

## Alternative noun backend

AT-COMP-022 resolves CB8AF0's provider and concrete output dispatch. CA0390
constructs Localize at T+0x34 through CB8DE0 with its supplied Excel provider.
The member stores that provider at +4, initializes its attributive-sheet cache
at +8 to null and creates an empty map at +0xC. On a cache miss, CB8AF0 requires
a source sheet and CB89A0's successful `xtx/attributive` lookup. ExcelModule
slot +0x18 resolves to C98150, which returns receiver+0x14; the caller reads
the type word there. The actual word is not observed.

The authenticated type switch and installed output cells are:

| Type word | Constructor / class | Table | Output slot +4 |
| --- | --- | --- | --- |
| 1 | CC5A50 / NounEn | 0x0110DD2C | CC5860 |
| 2 | CC5460 / NounDe | 0x0110DD14 | CC5130 |
| 3 | CC4D00 / NounFr | 0x0110DCEC | CC4AA0 |
| 4 or 5 | CC47B0 / NounCh | 0x0110DCD4 | CC4630 |
| Other unsigned values | CC4380 / NounJa | 0x0110DCBC | CC41F0 |

The constructors retain the target and attributive sheets at noun+4/+8. They
query the target's `NOUN` parameter and split its records on `/`. CC6930 uses
the finite labels SET, SGL, SGG, PLR, PLG, GEN, VOW, CNT and DEF with `;`
components. Literal initializer inputs do not prove the runtime label objects
or a complete token grammar. Allocation, valid configuration selectors and
retained sheet/provider state remain conditions.

Both cached and freshly constructed objects receive a source object first and
a destination string second. English output CC5860 looks up source+0x58 in
the target sheet and source+0x60 in the attributive sheet. ExcelSheet slot
+0x18 resolves to CAF760; its ready branch calls backend slot +0x18 and admits
only nonnull, ready row data. The known CacheAll target is CB1AD0, which calls
the qualified CB17C0 inverse, loads the row-array pointer at backend+8 and adds
the returned index times 8.
This does not extend the completed inverse/bounds evidence or the pending branch.

For admitted rows and valid configuration, the English method writes its second
argument through 00447450. Its nonzero DEF branch copies the configured target
field; its zero branch copies an attributive field and calls the 004488F0 thunk
for the target field. CC6910 interprets negative selectors as `-1-selector`;
nonnegative selectors read a signed byte at C9A480's returned field-slot address.
CC5860 also calls 00447ED0 with a count-derived temporary and needle object
0x01377E00, then returns a guarded success byte in AL. AT-COMP-023 below owns
the needle initializer and named attributive payload identity. Selected
configuration/row inputs and retained state still qualify complete output.
Excluded global bytes are not treated as runtime string values.

This alternative does not change English descriptor row 2104's mode-zero
path. Actual loaded type/locale, selection, final output and receive/render
lookup remain qualified; no semantic zone/item resolver follows.

AT-COMP-023 authenticates the needle's bounded initializer at F2CE40..F2CE60.
It supplies the literal `[n]` at 0x0110DD44 and the file-backed length sentinel
0xFFFFFFFF at 0x00F67298 to the completed 00447260 constructor, with
ECX=0x01377E00. Under successful construction and retained state, the object
therefore contains `[n]`. The initializer also registers F3BCF0, which supplies
that object to 00446F50. Cell 0x00F53240 contains the initializer address.
These instructions and literal inputs establish the conditional initial string;
they do not observe initializer execution or later global contents.

The named backing identity is owned by
`xivl-client-data:manifests/attributive_backing_rows.json`. Game master resource
0x01030000 names `xtx/attributive` definition 0x0B4500CA. Its present locale
rows and declared fields match the authenticated merged CSV. The ja/en/de/fr
blocks contain keys 1..35; chs supplies only key 2, with its other mapped CSV
cells empty. These source rows are not observed Completion indices or selected
control identities. CB89A0's completed named request remains the native input,
with actual payload delivery, backend state and selected row/configuration
qualified. In particular, a named source key does not establish that the
corresponding noun row lookup was admitted.

## Alternative noun admission boundary

AT-COMP-024 joins the nonzero alternative branch to the provider retained by
the same TextModule. CA0390 stores its supplied Excel provider at T+0x30 and
constructs the Localize object at T+0x34 with that provider. CA00C0 reads a
type word from T+0x30, constructs metadata `[0,nativeKey,1,5,0]`, and calls
CB8AF0 with T+0x34. CB8AF0 first performs a cache comparison; a cached-object
path can return through its existing output without reading the current type.
The cache comparison is followed by JZ at 0x00CB8B4E; only the
fresh-construction path continues there, while the other path calls the cached
object's output through 0x00CB8B7B without reading the current type. The fresh
path, after the source
and readiness checks, reads the type again. If that later read remains 2,
allocation selects NounDe through CC5460 and its output slot selects CC5130.
Same-provider retention alone does not prove that the type word stayed
unchanged between the two reads.

The pinned placeName definition identifies resource 0x0B45087C and gives the
German locale an empty `param` value. On the fresh NounDe path, the constructor's
NOUN query therefore receives the authenticated empty fallback object; its
split produces no configuration records and returns with the noun configuration
unpopulated, leaving its noun+0x10 configuration pointer null. Under this
source, a fresh type-2 NounDe object is conditional,
and no German placeName noun configuration is populated. This does not prove
that CC5130 safely refuses the row lookup. Its listing first checks the source
offsets +0x58 and +0x60 for nonnull rows, then at 0x00CC51BD reads
`[EDX+ECX*4+0x8]`, where EDX is the object +0x10 configuration base and ECX is
derived from source +0x54; no configuration-null or count branch is shown
before that read. Actual provider type, cache path, loaded state, mutation,
output and receive/render lookup are unresolved.

## Conditional English noun identity

For a fresh type-1 dispatch, AT-COMP-022's CC5A50 constructor and CC5860
output admit a bounded singular identity case. The explicit source words at
offsets +0x54..+0x64 are `[0,nativeKey,1,5,0]`: configuration index, target
named-row key, count, attributive named-row key and retained word. CA00C0's
type-2 literal preset establishes the word layout, not an English caller.
Its non-type-2 branch uses TextModule slots +4/+0xC and does not call CB8AF0.

The separate CA13A0 wrapper supplies type preset 1 at 0x00CA13AF to CA1020.
CA1020 compares the retained provider's current type to that preset at
0x00CA11BF and reaches CB8AF0 at 0x00CA1272 on equality. A fresh NounEn
construction also requires type 1 at CB8AF0's later reread at 0x00CB8BB5.
CA1020 passes parsed source objects, so this join does not establish the
five words above for an English selector-0x2E control. The diagnostic context
supplies them explicitly.

Under successfully initialized label objects and parsing of the authenticated
English displayName parameter `[NOUN|SGL;1/PLR;2/VOW;3/CNT;4/DEF;5]`, record
zero contains selectors `[1,2,3,4,5]`. CC6930's two-component entries select
record zero. CC5A50 maps SGL, PLR, VOW, CNT and DEF to record offsets
+0, +4, +8, +0xC and +0x10. CC5860 uses source+0x54 to select that record,
reads VOW and DEF from the target row, and its nonzero DEF branch copies the
configured SGL field into the destination. The bounded case uses VOW=0,
CNT=0, DEF=1 and count 1. The separate zero-DEF branch is excluded.

Both target source+0x58 and attributive source+0x60 must yield nonnull, ready
rows through the retained sheet lookup before output. The attributive row
remains required even though the nonzero DEF branch does not copy its fields.
CC5860 then prepares the count-derived temporary and calls 00447ED0 with
AT-COMP-023's conditionally initialized `[n]` needle. When the copied SGL has
no occurrence of that needle, replacement leaves the complete output string
unchanged. The final success byte is set after the replacement sequence and
returned at 0x00CC5A21; the replacement helper's return is not a separate
success gate. Count display spelling is unnecessary for this no-match case.

The source identity is displayName definition 0x0B450000, 16987 bytes,
SHA256 `7C9B77F9E5989C1C85BBD8152162160CC423F1A6CA17B730F51B5DDC5E4FF866`.
Its English columns 1..5 are `str,str,s8,s8,s8`, with `cache=100,type=map`.
This is distinct from CacheAll. The conditional target map-key relation is
owned by English displayName map admission below; attributive named-row
admission remains an explicit condition. No runtime cache hit was observed.
Source key 1000001 has the bounded flags and a
token-free SGL without the needle. The target and attributive key-5 payload
identities, typed row checks and source-cell comparison are retained by
`xivl-tools:docs/formats/fixed-control.md`, Conditional English noun identity,
and `apps/cli/src/english_noun_inputs.json`.

No configuration-null or count guard is shown before CC5860's indexed
configuration reads. This case requires valid configuration and allocations;
safe rejection of other configurations belongs to a diagnostic implementation.
The automatic English fixed-control path below uses a sheet query rather
than this metadata. Actual provider state and row admission, later mutations
and receive/render behavior remain unresolved.

The authenticated executable has the identity recorded in AT-COMP-022.
Independent raw checks pin CC5A50's 758-byte interval with SHA256
`BEDCDBC4BE0095035348551C1E8003AF0AFEABFF7820F6EEBF291B15B765D437`,
CC5860's 481-byte interval with SHA256
`4AF628CD96A0110DA5562EE9B31ED9ABB423EF71072F2DFA1F57CB3CE9758501`,
and 00447ED0's 83-byte interval with SHA256
`0F492D47957226A6CBBB68917B82C4578A2C7F96BDC42AD8373F1003180B78FD`.
CA13A0's 35-byte wrapper is pinned by SHA256
`14A8E76BF3732945BA9615B42132633307251C5191E5362643D48DA4528D66F3`.
The selected CA1020 comparison and CB8AF0 call operands were checked against
the same executable. These are static instructions and source identities.

## Selection-family boundary

The fixedPhrase table path
FUN_004DAA10 -> FUN_004DA680 -> FUN_00447260("xtx/_fixedPhrase") ->
FUN_00C9D550 reaches Completion candidate preparation at FUN_00C9D0D0. That
candidate vector and ordinary tree entries join the selected RaptureTextBox
vector through AT-COMP-010. AT-COMP-016 supplies conditional fixedPhrase
row-key equality. AT-COMP-017 supplies conditional place record production,
and AT-COMP-018 supplies conditional placeName CSV-key equality.
An arbitrary control's external family/table-key identity and the
receive-side lookup through generic renderer FUN_007906C0 remain unresolved.
The choice between rendering and forwarding is not established by the selected
record join.

The producer classifications are therefore:

- fixedPhrase: native candidate and conditional send paths recovered by
  AT-COMP-010/011 and AT-CHAT-001/002, with conditional CSV row-key equality
  under AT-COMP-016's authenticated payload and range conditions;
- item selection: unresolved lookup and serialization producer;
- place selection: conditional descriptor, native-key and ordinary-record
  production recovered by AT-COMP-017, with named backing/CSV identity and
  conditional target-key equality in AT-COMP-018; actual selection remains
  qualified;
- unsupported families: no family is classified unsupported by this pass;
- row key versus field 0/category: the native upper key argument and category
  byte are separated by AT-COMP-010/017; the descriptor candidate's field0-1
  category index is distinct from the target key.

Conditional fixedPhrase/placeName CSV row-key equality does not assign
arbitrary controls a table family. Field 0/category values and resource identity
cannot establish a complete decoder or semantic resolver.

## Fixed-control registry lookup

The TextModule selector-0x2E handler supplies a conditional native lookup
algorithm. It uses the installed Completion registry to select a descriptor;
the two literal numbers alone do not identify a table or locale.

Let T be the complete TextModule and P the complete CompletionModule from the
existing constructor joins. CA0390 installs handler thunk 0x00CA15E0 in its
MacroDecoder handler vector at selector index 0x2E. The thunk dispatches through
the secondary object's vtable+0x84. Authenticated secondary table 0x01108ECC,
with RTTI subobject offset 4, has cell 0x01108F50 = FUN_00C9FEF0. Thus this
handler's receiver is T+4, distinct from AT-CHAT-002's TextCleaner copy handler.

The successful D550 installation branch at 0x00C9D915..0x00C9D923 calls T's
slot+0x20 with P+4. Cell 0x01108F90 selects FUN_00C9EFB0, whose complete
13-byte body stores its explicit pointer at T+0x108. CA0390 initially zeroes
that member. This proves the conditional FixedSheetInterface binding, without
asserting an arbitrary historical instance or unchanged retained state.

FUN_00C9FEF0 checks its adjusted receiver+0x104, which is T+0x108. With a
nonnull interface, it calls FUN_00CB2D50 twice to obtain the two arguments and
invokes the interface's slot+4 with the first value and a mode-byte output.
For the installed P+4 table 0x01108E2C, RTTI offset 4 and cell 0x01108E30
select FUN_00C9C0A0. Its existing body now has an identified fixed-control caller.
This does not extend the literal-numeric diagnostic to every expression accepted
by CB2D50.

C9C0A0 interprets the first value as a signed index into P+0x4C's byte map.
It requires a nonnegative index below the map length, reads the mapped signed
category-vector index, bounds that index and requires a nonnull category object.
CB3C70 reads the object's signed +0x89 descriptor index, which must be
nonnegative and below C9DB10's descriptor count. C9DB30 then returns the
0x58-byte descriptor at `[P+0xE0] + descriptorIndex*0x58`. These are the existing
AT-COMP-017 category and descriptor structures, rather than an external CSV
row-id lookup. The callback sets mode one only when the Excel provider's
returned type value is 2 and descriptor+0x54 is nonzero; otherwise it sets zero.

With a returned descriptor and mode zero, C9FEF0 passes the descriptor string
and second decoded value to T's slot+0x0C, cell 0x01108F7C = CA0930. Mode one
instead reaches slot+0x18, cell 0x01108F88 = CA00C0. AT-COMP-019..024 own those
guarded TextModule query and noun paths. The handler also obtains the interface's
slot+8/+0x0C values through C9BC20/C9BC30 around successful output; their complete
P+4 coordinates return P+0xEC and P+0x140. This proves the dispatch association,
without establishing a displayed phrase, fallback or render result.

Direct PE-section reads authenticated the executable against the size, SHA-256
and image base above. Capstone 5.0.7 x86-32 decoding checked all bytes of the
bounded spans C9FEF0..CA00B4, C9C0A0..C9C181, C9EFB0..C9EFBD and
C9D915..C9D923, alongside the thunk bytes, dispatch cells and secondary RTTI
offsets. The retained CA0390 and D550 listings supplied the constructor and
installation inputs; the complete receive/history and selection records remain
unchanged inputs to this finding.

An automatic external table lookup still needs the matching category map,
category objects, descriptor strings/modes and Excel provider/locale context.
No authenticated snapshot of that installed state is supplied by an arbitrary
control or the merged phrase CSV. The recovered algorithm therefore does not
justify a context-free family switch on either number. Reconstructing a declared
initial registry from authenticated metadata is a separate conditional case;
it requires the full-load assumptions below rather than a historical snapshot.

### Conditional initial registry

For a fresh CompletionModule, D550 clears the descriptor vector at P+0xDC,
copies its root sheet argument into descriptor zero and sets that record's
mode byte to zero at C9D610..C9D63D. The admitted root argument is
`xtx/_fixedPhrase` from AT-COMP-015. With the authenticated locale backing rows
supplied in ascending native-key order, its nonempty field-1 branches construct
categories in traversal order. An `@` header uses descriptor index zero;
an ordinary descriptor uses the current C9DB10 count, then appends its record.
A leading `#` constructs a category with descriptor index -1, so C9C0A0 cannot
return a descriptor for that initial object. Empty field 1 produces ordinary
entries rather than another category object.

C9D0D0's bounded body C9D0D0..C9D1BA writes the category-code map only inside
the vector-growth branch C9D0F7..C9D11F. It fills new bytes with -1 and writes
the current category ordinal at the supplied code. It then increments P+0x15
and appends the category object regardless of growth. Consequently an earlier
hole is not repaired, and an existing entry is not replaced by another call
below the current map length. Category codes, object ordinals and descriptor
indices must remain distinct.

The pinned ja/en/de/fr rows in
`xivl-client-data:manifests/fixed_phrase_backing_rows.json`, revision
`750eb59885752e1a4f6e69c00e87697fce6a2580`, supply the same initial metadata
for these branches. Reconstructing a complete successful traversal yields 41
category objects and 24 descriptors, including descriptor zero. Category 20
uses object ordinal 20, descriptor index 5 and source metadata key 2104, whose
descriptor names `xtx/placeName` in mode zero. Code 31 and codes 41..48 remain
unmapped. Code 49 maps to object ordinal 40, whose descriptor index is -1.
These are derived initial-state coordinates, not observed historical state.

This reconstruction assumes fresh vectors/counter, successful allocation,
ready named backing resources, successful descriptor parsing and target
preparation, and an uninterrupted full traversal. The zero-suffix target
preparation branch can abort D550; this model assumes it succeeds. Later
dynamic population, provider changes and locale reinitialization are outside
the case. The noun flag remains distinct from C9C0A0's provider-dependent
dispatch mode. A source-cell lookup under this model does not reproduce
TextModule expression evaluation, fallback, wrappers or rendering.

### Conditional item-name source keys

The conditional initial registry also maps code 22 to category ordinal 22,
descriptor 7 and fixedPhrase metadata key 2106. Its four main locale strings
name `xtx/itemName` without a noun flag. The selector-0x2E handler consequently
supplies the second number to the existing mode-zero query path under the
initial-load conditions above. Candidate ranges in that descriptor do not
replace the query key or prove admission of arbitrary supplied controls.

`xivl-client-data:manifests/item_name_backing_rows.json`, definitionLocales and
locales/blocks/sources, authenticates the named itemName definition and all its
backing blocks to keyed CSV cells. Its 386556 bytes have SHA-256
`D13CD40E4BBF4AC7BADECB262A185E3432F85AE787C48B978AC8854D897B5835`.
Each supported ja/en/de/fr definition has 50
disjoint blocks whose offset entry counts equal the declared counts.

Applying the completed AT-COMP-016 mapping to matching ready CacheAll pairs,
a key strictly inside a block `(begin,count)` has block slot `key - begin`
and storage index `priorCounts + key - begin`. Bulk completion CC30C0,
CB1930/CB17C0 storage and the admitted CB1870/CB1990 mapping therefore retain
the same native key `begin + slot`. The authenticated report identifies its
nonempty span as that CSV key. This application does not claim the mapper's
inclusive upper comparison or exhausted path is a safe general inverse.

For example, itemName key 1000002 is slot 2 of block `(1000000,204)`, with
prior declared counts 2 and conditional storage index 4. Its enabled ordinal
is 3, a separate coordinate. Key 10009506 is slot 9506 of block
`(10000000,13018)`; equal English text at key 12000016 in another block cannot
substitute for either key. These are conditional source-cell associations,
without a newly recovered item selection/production path. Historical delivery,
retained child/cache state, locale, TextModule output/admission, noun evaluation
and rendering retain their existing limits. Completed selection and
receive/history traces remain inputs.

### Conditional command-name source keys

The initial registry's codes 24..30 and 32..35 select `xtx/command`
descriptors without noun flags in each supported ja/en/de/fr locale. Under
the same full-load conditions, C9C0A0 returns mode zero and C9FEF0 passes
the second decoded number unchanged to CA0930's row query. Descriptor
candidate ranges do not filter this supplied query key.

The authenticated game master 0x01030000 names command definition
0x0B450017, 12993 bytes, SHA256
`99762442C38144D8AE82C83B24265C4B1AFE3050AAB769DC7AE2CADDEB12B3E5`.
Each supported locale declares `cache=0,type=all` and 23 disjoint blocks.
All offset counts equal their declared block counts. Applying AT-COMP-016's
completed mapping to matching ready CacheAll pairs identifies the native
key `begin + slot` strictly inside each block with its nonempty backing
span and authenticated CSV row. This conditional association does not use
an enabled ordinal or extend the inverse's upper/exhausted cases.

The definition's first indexes and explicit SHEET DEF parameters both select
ja1, en2, de8 and fr16. Under AT-COMP-020/021's successful constructor and
retained-state conditions, selector 0xFF therefore queries that default
string field. CA0930 forwards it to the existing TextModule evaluator.
Direct selector-0x2E command lookup and literal selector-0x28 command
references share the named row query, default and recursive string path.

`xivl-tools:docs/formats/fixed-control.md`, Initial registry inputs, owns
the master/definition identities, promoted locale layouts and 276 block
resource pins. Its Conditional command-name lookup section owns executable
diagnostic coverage. Those inputs were compared to the authenticated command
CSV identified by `xivl-client-data:manifests/manifest.json` at revision
`06f6687b4e0adc24e7f38f3105ae9fc237de3eda`. This establishes a conditional
source lookup, without a command selection producer, historical loaded state,
general expressions, output wrappers or rendering.

### Conditional status-name source keys

Initial category 23 selects descriptor `xtx/status#50` at source key 2107,
ordinal 23 and descriptor index 8 in ja/en/de/fr. It has no noun flag.
The established C9C0A0/C9FEF0 mode-zero path therefore sends the second
decoded number unchanged to CA0930's row query with default selector 0xFF.

The authenticated master names status definition 0x0B450073. Each supported
locale declares `cache=-1,type=none` and three blocks `(0,1)`,
`(220000,12016)` and `(251000,2004)`. This policy does not prove a ready
CacheAll backend. The diagnostic's source association assumes a completed
transition to local cache state zero, matching CacheAll block pairs and ready
rows. It does not claim those conditions followed from the shipped policy.

AT-COMP-016's CB0140 transition sets backend kind zero when the new cache
state is zero; its existing-state guard can skip reconstruction, and its
capacity branch can select a map instead. A bounded raw check of CB0140's
606 bytes at 0x00CB0140, SHA256
`4469A234440DA590E6C1A624A1CB5F6A383E88FB1B32EC687C6B0309BA0B443E`,
verified those guards, the child begin/count reads and the CB16D0 constructor
call. Under the stated matching ready CacheAll conditions, the existing
strict-interior mapping identifies `begin + slot` with the nonempty backing
span's source key. Enabled ordinals do not supply this join.

The explicit SHEET DEF parameters select ja1/en3/de8/fr15. English's first
index is 2; the admitted override selects 3 under AT-COMP-020/021's successful
constructor and retained-state conditions. NOUN parameters remain separate.
Each selected column is a string, forwarded through CA0930's existing
TextModule path. No noun evaluation is needed for this fixed-control descriptor.

`xivl-tools:docs/formats/fixed-control.md`, Initial registry inputs, owns the
definition identity, four locale layouts and 36 block resource pins. Its
Conditional status-name lookup section owns executable coverage. The backing
cells were checked against the authenticated `xtx_status.csv` table entry in
`xivl-client-data:manifests/manifest.json` at revision
`06f6687b4e0adc24e7f38f3105ae9fc237de3eda`. This is a conditional source
lookup; selected cache policy/state, selection production, output admission
and rendering remain unobserved.

### Conditional quest and leve source keys

Initial category 36 selects `xtx/guildleve` from metadata source key 2120,
category ordinal 35 and descriptor index 20. Categories 37/38 select
`xtx/quest` from source keys 2121/2122, ordinals 36/37 and descriptor indexes
21/22. All three descriptors have no noun flag in ja/en/de/fr. The established
mode-zero C9C0A0/C9FEF0 path sends the second decoded number unchanged to
CA0930's row query with default selector 0xFF. Descriptor candidate ranges
do not filter this supplied query key.

The authenticated master names quest definition 0x0B450459 and guildleve
definition 0x0B450013. Each supported locale declares `cache=-1,type=none`.
Quest has four blocks `(0,1)`, `(110000,1861)`, `(120000,1028)` and
`(180000,41)`; guildleve has two blocks `(0,13056)` and `(20000,3025)`.
All offset counts match the declared counts. Applying the completed
CacheAll relation assumes local cache state zero, matching block pairs and
ready rows, as in Conditional status-name source keys above. The shipped
none policy does not establish those conditions. Strictly inside a matching
pair, `begin + slot` identifies its nonempty backing span's source key;
enabled ordinals remain separate.

Neither definition supplies a parameter override. Under AT-COMP-020/021's
successful constructor and retained-state conditions, the first indexes
therefore select quest defaults ja1/en2/de3/fr4 and guildleve defaults
ja9/en10/de11/fr12. Each is a string field, forwarded by CA0930 through the
existing TextModule path. Other source fields do not supply the selected name.

`xivl-tools:docs/formats/fixed-control.md`, Initial registry inputs, owns the
configuration identities, four locale layouts per family and 72 block pins.
Its Conditional quest and leve lookup section owns executable coverage.
The backing fields were checked against the authenticated `xtx_quest.csv`
and `xtx_guildleve.csv` table entries in
`xivl-client-data:manifests/manifest.json` at revision
`06f6687b4e0adc24e7f38f3105ae9fc237de3eda`. This conditional name lookup
does not establish historical selection, cache state, journal evaluation,
client output admission or rendering.

### Conditional default fields

The completed AT-COMP-020/021 constructor rules apply to the authenticated
itemName index and parameter metadata as a separate conditional application.
`xivl-client-data:manifests/item_name_backing_rows.json`, definitionLocales,
at revision `06f6687b4e0adc24e7f38f3105ae9fc237de3eda`, supplies first indexes
ja4, en5, de11 and fr19. Each locale also has an explicit `SHEET|DEF` parameter
with that same index. The separate `NOUN` group does not supply the SHEET
selection. With matching constructor inputs, successful parsing and retained
sheet state, either the first-index initialization or admitted DEF override
therefore selects that index. Each selected index maps to a string field.

For placeName, AT-COMP-021's existing constructor-local result remains ja0,
en1, de4 and fr6. English `NOUN` value content `DEF;3` does not select field 3.
Both families have mode-zero descriptors under the conditional initial registry.
Reading the admitted row's selected string field gives a conditional default
text source. A token-free field preserves its decoded literal text, including
literal brackets and backslashes, without interpreting an expression.

This field association does not establish all CA0930 query/conversion paths,
fallback or empty-result behavior, Completion admission, client output wrappers
or rendering. Fields with controls still require their evaluation context;
noun dispatch still requires provider and configuration state. A diagnostic
that returns a token-free default field is bounded to that conditional source.

### English displayName fixed-control query

The recovered C9C0A0 predicate sets mode one only when the provider type is 2
and descriptor+0x54 is nonzero. At 0x00C9C137 it compares the type with 2;
0x00C9C13A branches to the zero-mode store at 0x00C9C163 on inequality.
Consequently a stable type-1 English provider sets mode zero even when the
selected displayName descriptor has a noun flag. C9FEF0's zero-mode branch
at 0x00C9FFD9 passes selector 0xFF to primary slot +0xC, CA0930. This path
does not construct or pass NounEn's five metadata words. The descriptor flag
alone does not select English noun dispatch.

The authenticated displayName definition from Conditional English noun
identity has ordered English indexes `[1,2,3,4,5]` and only a NOUN parameter
group. Applying AT-COMP-020/021's constructor rules initializes the first
index, 1, and finds no SHEET override. With matching constructor inputs and
retained state, CAF300 therefore returns default field 1. CA0930 checks for
selector 0xFF at 0x00CA09BA and calls sheet slot +0x1C at 0x00CA09CA.
After its named row lookup and field-type query, the string-field branch
reads that field through C9A480 and forwards it to TextModule slot +8.
For a token-free source this gives the conditional default text, without
applying NounEn's flags, attributive lookup or count replacement.

Independent bounded raw checks against the authenticated executable pinned
C9C0A0's 226-byte span with SHA256
`286BBDB332E7C3F175050DB5BEB9102A0098AC4493B3D1B8A79430A78D9DC646`,
C9FEF0's 453-byte span with SHA256
`66431F769584C961F27F4FAAA6DE35791168C2FCD1740FC5834DF060B7879D35`,
and CA0930's 1222-byte span with SHA256
`92960E665215C3D80D8F43C5B9A7BD343CBA0A9FB54F9F47F717517670AFB999`.
The installed query/conversion cells, CAF300 default-byte read, first-index
store and pinned definition indexes/parameter were checked separately.
These are conditional source and dispatch associations. Provider state,
cache readiness, wrapper output and receive/render behavior are not observed.

### English displayName map admission

The target definition's `type=map` is applied conditionally to a selected
native kind-1 sheet. CB1BF0 installs CacheMap vtable 0x0110C698; its writer
slot +0xC is CB1C90 and key lookup slot +0x18 is CA2B90. The distinct
+0x1C method CA2AE0 enumerates by ordinal and does not supply this key join.
CB1C90 searches and inserts using its supplied native key, storing the row
pointer in CacheData +0xC. CA2B90 searches with that same key and returns
the matching CacheData. This relation does not use the CacheAll inverse.

The bulk loader CC30C0 supplies `subSheet.begin + slot` to that writer:
0x00CC316B adds the begin value to the slot and 0x00CC316D pushes the key
before the backend +0xC call. The indexed loader CC3240 first looks up its
requested key through +0x18 and supplies that key to +0xC on a cache miss.
Thus a populated map associates each backing slot with its native key,
independently of enabled-row ordinal.

CAF760 requires the local sheet path, `sheet+0x3C == 0`, and requests the
exact native key through backend +0x18. It requires a nonnull CacheData and
row, then C9A5F0 requires `row+4 == 1`. C9A6A0 sets that ready byte at
0x00C9A7D8 after decoding the row. An installed map entry alone is insufficient.
For the authenticated target block `(1000000,601)`, source key 1000001 is
slot 1; under those map and readiness conditions it identifies the same
named target row. The 418 enabled source rows are not evidence of runtime
map population or readiness. Attributive row admission remains separate.

Against the same authenticated executable, bounded raw checks pinned the
constructor CB1BF0 (132 bytes, SHA256
`F24925ED55C0DCA3D26E0EDB9FC8F5D860CBB9A4990BE70C05955604E5A772B2`),
writer CB1C90 (186 bytes, SHA256
`AB3E8622929537431C75FF80D0F97482D9FB36644D3BF55BF331D35C76A3B7D8`)
and key lookup CA2B90 (100 bytes, SHA256
`3E1F34250A14D4CEF5DED82488B2C66CB6AE5914DC9C95A54300AFA842F5877C`).
The selected vtable cells were pinned in a 32-byte prefix with SHA256
`3EBF0E097793EFCD7C999092B405871D7B6E28028D841F7DB23D129E849F0BB4`;
this interval does not claim the full table extent. The distinct ordinal
method was checked separately.
The bulk/indexed loader spans are 377/189 bytes with SHA256
`7366F61B8371FEEBA9B1C1325933FD519426CE8BEEAF656BB9880FFFF67B2720`
and `729891C9C98ABC042B242ED70618F4E52B58D71FFA629AA5B8B2A5692C799FC5`.
CAF760's 78-byte span has SHA256
`1F8CEE0B93F3F6CE0A1AD2A47ECA83F7A50291311FAE1E0952DA2965D2A470FF`;
C9A5F0's 10-byte span has SHA256
`929920E84AE4E4EBE4928F32DD118957D6D337944E8AA2DF22C856084663F5EE`.
The row decoder C9A6A0's 321-byte span has SHA256
`CB68125528E6EA56A6C8F2C627C3A9F7CA36A7BD92AB3593149E139454A0F595`.
These checks establish a conditional static key association and admission
rule, without claiming an observed cache hit or historical provider state.

### Literal sheet references

For the authenticated executable identified above, CA0390's retained listing
at CA0698..CA06A5 installs thunk CA1590 in selector-0x28's vector cell +0xA0.
The thunk dispatches secondary table slot +0x6C; cell 0x01108F38 contains
CA0E20. A bounded PE32 raw-byte inspection with Capstone 5.0.7 verifies that
join and the handler at CA0E20..CA101D. The
509-byte handler has SHA-256
`4B5357E5DD5A1DE5D6E5317C590FC8516D95C81858E9747204235D30C11BC581`.

CA0E95 parses the first component through CB2AE0 into a temporary string.
CA0EB1 and CA0ECE parse the next two components through CB2D50 into separate
integers. Each requires nonzero consumed bytes. The stack at CA0F25..CA0F4C
passes that string, the first integer as row key, the second as column
selector, a remaining-argument context and a destination string to primary
slot +0xC. Installed primary table 0x01108F70 has CA0930 at cell 0x01108F7C.
With exactly those three components, CB3480's zero-length remainder fails
its entry loop condition at CB34FB..CB3506 and adds no arguments.

The retained CA0930 listing at CA0961..CA0991 requests the named sheet through
the retained provider's slot +4 and the row key through sheet slot +0x18,
requiring both results. CA099B..CA09CE uses a nonnegative column directly,
except 0xFF, which requests the sheet's selected default. Negative selectors
take a separate index mapping path. For a string type, the jump table's tenth
entry selects CA09EC: row slot +8 and C9A480 obtain the selected field,
then primary slot +8 evaluates it. Cell 0x01108F78 contains CA1D60, whose
primary +0x24 cell 0x01108F94 dispatches CA1D40, which adjusts the receiver to
T+4 for CB2760. Thus nested string
controls use the same evaluator. CA0F4E..CA0F5F requires query result 1 and
appends the temporary result to the outer destination; failure is separate.

This establishes the conditional literal-string/integer/integer association
for a ready admitted row and retained tables/provider. A diagnostic may
restrict it to exact three-component expressions, supported nonnegative string
columns or the promoted default, and independently authenticated named backing
blocks. Parameters, additional arguments, negative selectors, numeric field
conversions and other callbacks require their own evidence. Recursion budgets
are diagnostic limits, not recovered native behavior. Actual delivery, retained
or mutated state, Completion admission, output wrappers and rendering remain
outside this static association.

## Received World chat handoff

AT-RECV-001 recovers a bounded post-receive handoff for the authenticated World
chat paths. `FUN_004D8D10` builds the received sender/name and message strings
for the tell, selected-group and CB branches, then calls `FUN_004D8560` with
the branch selector. The selected-group branch first calls
`FUN_005754E0` on its packet context and drops a zero result. This dispatcher
is already owned by `chat_wire_contract.json`; this record follows its display
boundary only.

`FUN_004D8560` has distinct argument roles in its listing: EBX loaded from
`[ESP+0x1C]` is the message passed to the owner `+0x7F8` text-cleaner gate;
EDI loaded from `[ESP+0x14]` is the sender/name passed to
`FUN_00445C70` and the owner `+0x950` gate; EAX loaded from `[ESP+0x10]` is
the selector. When owner `+0x660` is nonnull, the call passes selector,
sender/name and message as arguments to `FUN_004CE760`. `FUN_004CE760`
formats the selector as `%04X`, concatenates the received fields, and passes
the local string only to vtable slot 7 on the callback object held at the
outer owner's `+0x660` through `FUN_00C9A8E0`. Its inspected body has no
direct call to generic parser `FUN_007906C0` or direct external table lookup.

The exact `FUN_004DC5D0` installer fills the remaining static gap around
owner `+0x660`: if the field is null it allocates `0x74` bytes and calls
`FUN_004DEE90`, whose listing writes vtable pointer `0x00F91434` to the new
object; if the field is already populated it calls the existing object's
slots `+0x8` and then `+0x4` when still nonnull. The installed vtable base is
therefore static, and authenticated cell `0x00F91450` resolves slot 7 to
`FUN_00C9AD40`. This resolution applies to the fresh-null constructor branch;
a cached object or later replacement may use another vtable.

`FUN_00C9AD40` calls `FUN_00C9BAE0` with its two input values, captures the
numeric pre-increment value from object `+0x10`, increments that counter,
advances `+0x14` when the captured value is at least `0x4B0`, and calls
`FUN_00C9AAE0` plus `FUN_00C9B0D0` when object `+0x30` is nonnull and the
unsigned dword-count condition `((object+0x34 - object+0x30) >> 2) > 0x3B`
holds, then returns the captured value. The helper's input storage,
semantic meaning of the returned count and counter/range state are resolved
within this bounded history path by AT-RECV-002. `FUN_00C9A8E0`
supplies the temporary UTF-8 data pointer through `FUN_00445210` and a count
from `FUN_004451F0`, whose body returns `[string+0x8] - 1`, so the count
excludes the source terminator. `FUN_00C9BAE0` appends exactly that byte count
to the `object+0x2c` aggregate byte range at relative `+0x14/+0x18`. It
requests `oldByteLength + count` through `FUN_00406280`, then checks that the
begin pointer is nonnull and `newEnd - begin > oldByteLength` before
`memcpy`-copying exactly the supplied count at the old end, without an
inspected NUL append. It computes `iVar1` as the cumulative byte end
(`oldByteLength + count`) and
passes `&iVar1` to `FUN_00813050`, whose vector receives byte-end offsets; this
is the same offset vector whose dword range is at relative `+0x4/+0x8`.
The slot-7 `object+0x2c` value is passed by address as this aggregate; the
later owner `+0x664` CompletionModule value is an inline object whose first
dword is a vtable pointer, not a pointer field.

When that byte-end offset vector contains at least 60 dwords, `FUN_00C9AAE0`
packages the two history values, offset dwords and raw bytes into a
`Component::Log::LogPage` object. The LogPage object's first dword is its
vtable; the payload begins with the two interval values, then the offset
dwords and raw bytes. It inserts the page into its four-pointer-per-block ring
and advances its separate history sequence. `FUN_00C9B0D0` passes the complete
offset-vector begin/end range to `FUN_0071CC50`, then computes
`_Src` as the current byte end, yielding zero remaining byte length, and sets
the byte end to the byte begin. The inspected path therefore clears the
aggregate ranges; it does not establish a nonzero remaining byte range. The `+0x10` value
is the returned history count/index and `+0x14` increments on every callback
whose old `+0x10` is at least `0x4B0`; no reset is shown, so it is a
mechanical history advance counter. `+0x30/+0x34` are the
byte-end offset-vector range; none is proven an external family, table key,
CSV row key, decoded token, rendered phrase or forwarding decision.

For successful tell and CB branches, a nonzero `DAT_0132F818` then calls
`FUN_004D6B40`. Its listing loads the inline object's first dword at outer
owner `+0x664` as a vtable pointer, reads slot `+0x8`, and calls that slot with
ECX set to `&owner+0x664`; it does not load a separate object pointer from
the field. The existing constructor evidence calls `FUN_00C9CFA0` with that
same inline address, and the raw CompletionModule identity includes table cell
`0x01108E48 = 0x00C9C670`. AT-RECV-003 resolves the callback's static inputs
and the known conditional ordinary-tree effect. The `FUN_004D8D10` listing
pushes its local `+0x10` message and then its local `+0x64` sender/name to
`FUN_004D8560`; after its success and nonzero `DAT_0132F818` guards it pushes
that same `+0x64` sender/name to `FUN_004D6B40`. The message is not the
callback source. The owner state read through `owner+0x174F8` virtual slot
`+0x18` is made twice: the first result selects state 4, otherwise a second
call selects state 5. States 4 and 5 call `FUN_00445470(0x20)`, which returns
the first-space byte offset or `-1`, then `FUN_00447A40` copies sender/name
source offset 0 with that count to a stack-local destination. Its `-1` fallback
uses stored length minus one before `FUN_00447260`; the delimiter is excluded
and a no-space source supplies its stored bytes. Other states call
`FUN_00445220` on sender/name with `(1,1,0,0,0)`, starting at offset 0 and
scanning its full stored length, retaining only the bounded normalization and
returning the same object. Both paths call inline `+0x664` vtable slot 2 with
`ECX = &owner+0x664` and explicit arguments
`(sign-extended DAT_0132F818, prepared sender/name object, -1)`. Existing
`FUN_00C9C670` evidence qualifies readiness, nonempty/leading-period/literal
guards, category-map/category-slot admission and ordinary-tree insertion with
known key `0xFFFFFF80 | (category byte & 0x7F)` from third argument `-1`.
`DAT_0132F818` is the bounded category-map selector, not the packed low
category. This mechanical admission/tree effect is not render or forward
proof. Cached-vtable/runtime category state, external row key and rendered
text remain qualified. The owner `+0x660` slot-7 target is resolved to
`FUN_00C9AD40`; its direct `FUN_00C9BAE0` helper and counter/range state are
now resolved as bounded storage and retention helpers.

AT-RECV-004 follows all seven direct callers of generic parser
`FUN_007906C0`. `FUN_0089FBF0` establishes a concrete SendLog
received-byte-span/parser edge: it prepares a received byte span and calls the
parser. `FUN_0089EB40` and `FUN_0089E320` are bounded buffer/parser helpers.
`FUN_00790AA0`, `FUN_00790B20` and `FUN_00790A30` are setup/parser/cleanup
wrappers. `FUN_00790BA0` is a stateful range wrapper with three named
post-parser branches. These caller bodies establish no received auto-translate
association or control grammar,
external family/table key, selected row, decoded token, or render-versus-forward
result. The parser's renderer-interface targets and computed, indirect and
dynamic routes remain unjoined, and the World AT-RECV-001/002/003 handoff to
`FUN_007906C0` remains unjoined.

AT-RECV-005 follows one concrete RaptureLogModule history-consumer path through
the fresh-null vtable branch. Its consumer object is not statically joined to
the same live World receiver instance installed through `+0x660`; the evidence
establishes only the shared method/storage shape. The authenticated vtable cells at
`0x00F91448`, `0x00F91454` and `0x00F91458` resolve slots 5, 8 and 9 to
`FUN_00C9A8D0`, `FUN_00C9A910` and `FUN_00C9A9F0`. Slot 5 returns the
`+0x10` count capped at `0x4B0`. Slot 9 first uses vtable `+0x0C` to replace
a negative index, then compares the index against the raw uncapped `+0x10`
dword; it uses the vtable `+0x0C` result in unsigned page arithmetic and
returns a data pointer in `EAX` while writing a byte count through its out
parameter. In the active-page branch, `FUN_00C9AEE0` supplies the byte length
from offset differences and `FUN_00C9AF60` returns the data pointer; the
selected 60-entry page branch calls `FUN_00CB38C0`/`FUN_00CB38F0` without
assigning their individual pointer/count roles here. Slot 5's capped getter
is separate and is not used by this body.
The cell map applies to the fresh-null constructor branch; cached objects and
later vtable replacements remain qualified.

`FUN_004C3F10` is the sole recorded direct caller of `FUN_00C9A9F0`. Its
listing saves the incoming `ECX` owner in `EBX` and passes `EBX` as the
history-consumer `ECX`; the helper returns the source pointer in `EAX` and
writes the byte count through its out parameter. The caller then passes that
pointer/count pair to `FUN_00404120` with a local string destination in `ECX`.
The bounded copy places the retrieved bytes in a local NUL-terminated string
object. It searches from offset 5 with `FUN_006BE5E0`, using the local string
length as the haystack end; the `0x004C4018..0x004C4021` loop NUL-scans the
`DAT_0132F330` string returned by `FUN_00445210` to derive the needle length.
When the delimiter is found, the prefix is `[5, match)` and the suffix is
`[match+1, end)`, skipping one byte regardless of the delimiter object's
stored length, passing each span through `FUN_00447260`. It then calls the
receiver at `param +0x5C` through vtable slot `+0x8` with the suffix,
`param +0x60` and the caller argument. Completed AT-RECV-001 owner/installer
evidence, AT-COMP-005, AT-COMP-019 and AT-ENTER-030 constrain this receiver
to the conditional TextModule `T=C+0x554` on the fresh installed branch.
Retained vtable `0x01108F70` slot `+0x8` resolves through cell `0x01108F78`
to `FUN_00CA1D60 -> FUN_00CA1D40 -> FUN_00CB2760`; the latter's ordinary
segment handoff and guarded selector-callback behavior are static, while the
actual widget/consumer `+0xB0` and World `+0x660` instance join, table
retention/population, external row and final render remain unresolved.
`FUN_00591F80` iterates through the consumer's `+0xB0` interface,
calls `FUN_004C3F10` with the current index+1, uses the 16-bit value at
`[ESP+0x14]` only as a membership filter against the configured vector from
`[[caller+0x70]+0x1A5C]` through end `[[caller+0x70]+0x1A60]` (the owner
pointer is loaded from caller `+0x70`), and conditionally passes the
current-index address to
the vector helper at caller `+0x3C`; `FUN_00592940` compares the consumer-side
slot `+0x0C` result, calls the same consumer, loads `[caller+0x70]`, then
`[[caller+0x70]+0x1B08]` as ECX for `FUN_004D74E0`, whose known return is
that input plus `0x554`, before invoking the returned subobject's vtable slot
`+0x8`. If that input owner is joined to `C` and retained table `0x01108F70`,
this is the same conditional `FUN_00CA1D60 -> FUN_00CA1D40 -> FUN_00CB2760`
route; that owner/table join is not established here. It selects one of the
`+0x19A0/+0x19A8` templates and performs bounded `{TEXT}`/`{NAME}` replacement
before its local output callbacks. These bodies establish byte retrieval and
local formatting/callback preparation only. The second callback's input
owner/table join, delimiter and template values, external family or row
lookup, and final render-versus-forward behavior remain unresolved.

AT-RECV-006 bounds the static owner/writer frontier behind the reader-side
`+0xB0` interface and the caller-side `+0x1B08` field. AT-GH-365 is a
candidate-only `FindFieldRefs` scan: its header states that `READ/WRITE` is
operand position only and gives no terminal completion marker, so the report
is not an exhaustive writer or common-owner proof. AT-GH-366/367 pin the exact
`FUN_00592300` constructor target reached from `FUN_00595A20` at `0x00595A9A`;
it writes `[ESI+0xB0] = EBX` at `0x005923AC`. This inspected constructor
writes zero to the reader-side field.

AT-GH-368/369 pin `FUN_00595A20` writing `[ESI+0x1B08] = EDX` at
`0x00595E65`. The preceding load from `[ESP+0xEC]` is the first explicit
stack argument, `param_2` after the implicit `this`; the exact caller list
names `FUN_00546EF0 @ 0x00546EF0` and `FUN_00555730 @ 0x00555730`.
AT-GH-370/371 export their bounded argument bodies and the concrete
publication path. `FUN_00546EF0` passes `[param_1+0x10]`, which AT-ENTER-027
constrains to `C=M+0x10` through retained LogControlExtension L and table
`0x00FA2A40`. `FUN_00555730` passes its `param_2`; AT-RECV-007 below
identifies that source as the FUN_0054E150 receiver `+0x4`, while receiver
identity, its initializer and actual retention remain qualified.

`FUN_005954D0` checks `control+0x1B0C`, calls `FUN_004D7590` with
`[control+0x1B08]`, and, on a nonzero result, stores it in `control+0x1B0C`
and dispatches the retained document `+0x28` virtual slot +4. Independent PE
cell mapping (AT-ID-102) pins `0x00FA9508 -> FUN_00593950`; that setter's
`ECX=complete-document+0x28` and `[ECX+0x88]` write publish the value at
complete-document `+0xB0`. AT-ENTER-027's retained LogControlExtension L
path establishes `L+0x10 = C = M+0x10` through FUN_00546E00 at
`0x00546E37..0x00546E41` and table `0x00FA2A40`, so FUN_00546EF0's
`[param_1+0x10]` is conditionally the completed World C input while that
registration and retention hold. AT-RECV-007 below identifies
FUN_00555730's `param_2` source as the FUN_0054E150 receiver `+0x4`; receiver
identity, its initializer and actual retention remain qualified.
Therefore the conditional static alias from World `C+0x660` to reader `+0xB0`
is established when the applicable input and guards pass.

This also conditionally supplies the owner identity used by AT-RECV-005's
second callback through control `+0x1B08`. That isolated trace did not
establish the owner join; actual table retention and live-instance selection
remain qualified. AT-RECV-007 below identifies the alternate source as
receiver `+0x4`, while receiver identity, its initializer and actual retention
remain qualified.

Independent review report SHA256
`3E4A25E1C2C5F9DFD2E4491C5A98A4435B63747B9F951C23744A1F401A0304E5` maps
vtable `0x00FA9504` to static type `LogDocument` and
`0x00FA935C`/`0x00FA9234`/`0x00FA921C` to static type `LogControl` through
pinned COL/type-descriptor locators. These are static identities only, not live
instance proof. The completed World branch independently installs its history
object through `FUN_004DC5D0`/`FUN_004DEE90` at receiver `C+0x660`.
AT-RECV-007 resolves the FUN_00555730 static constructor-callsite input to the
FUN_0054E150 receiver `+0x4`; retained-table/runtime state and live owner
selection remain unresolved, as do table retention/population and runtime
render/forward state.

AT-RECV-007 resolves the alternate constructor's static input source. The
completed AT-GH-136/137 `FUN_0054E150` sections show `ESI=ECX`, load
the receiver's second dword field `[ESI+0x4]` at `0x0054E159`, push it at
`0x0054E15C`, push the separate explicit argument at `0x0054E15D`, and call
`FUN_00555730` at `0x0054E15E`.
The receiver `+0x4` push is first in chronology and the explicit argument push
follows; right-to-left stack order and the callee-cleaned two-argument
`RET 0x8` therefore make the receiver `+0x4` value the second explicit
argument to `FUN_00555730`, while the separate
`FUN_0054E150` explicit argument is the first. AT-GH-370/371 then show
`FUN_00555730` calling the `0x1F10` allocator, testing
the result, loading its second explicit argument at `0x0055576E`, and passing
it to `FUN_00595A20` at `0x00555775`. With successful allocation,
`FUN_00595A20` therefore writes the alternate receiver `+0x4` value to the
new control's `+0x1B08` at `0x00595E65`.

This source is separate from the completed World path: AT-ENTER-027
conditionally supplies `C=M+0x10` through `FUN_00546EF0` and retained
LogControlExtension L. The alternate receiver producer and its `+0x4` writer
remain unresolved. Separately, the completed AT-ENTER-021 `FUN_00557600`
attachment shape is conditional on its S/X/name and live state;
`FUN_00558F60` post-construction effects, live owner selection, and equality to
C remain unresolved. Cached table/vtable/template state, table population,
external family/locale/row identity, and final rendering or forwarding remain
outside this static edge.

The registrar decompilation and listing pins remain the existing
AT-GH-136/137 outputs (SHA256
`0A9C1FA48C20F18FC1E41A04B565E82D481F898BC4FA421617F6EC72D947B2ED` and
`A2B2397D8C328D857B88EB07376220929DC49CC092321EC2772D6C9CDFE07F16`), and
the owner follow-up pins remain AT-GH-370/371 (SHA256
`FFBBFA00E570228B07911DA81E1C4F289DD26B6F0E9249DF82F6F202F4A80603` and
`CB12D388CE48B98BF833CF9A2CCC2F973AE2ABF1449B0CD7C055FFF152309315`).
The completed AT-GH-134/135 `FUN_00557600` outputs remain the existing
AT-ENTER-021 evidence (SHA256
`216DA7382E3DA0D254798464B296F1AC47A617D92DB86EF25B0098F84FE0C509` and
`69687ADE729BF8911E8CA4C45660121FBC7C75EC2A91A2BC0D544A73F266118B`).

The completed AT-GH-148/149 metadata lifecycle pair also includes
`FUN_0054E150`, but its decompilation Callers section is empty. AT-GH-145/150/151
identify existing registration, table and `FUN_00557600` callsite references,
not the receiver constructor or its `+0x4` initializer. The retained completed
exact-entry output set has no `FUN_00558F60` body export. The remaining static
evidence is the receiver producer or caller path, the `+0x4` writer, and that
body's post-construction effects. Those static gaps do not establish actual
live retention or equality to World C; cached table/vtable/template state,
table population, external family/locale/row identity, and final rendering or
forwarding remain separate state ceilings.

See `manifests/autotranslate_wire_format_study.json` record `AT-RECV-001`
and its `AT-RECV-002` storage trace, `AT-RECV-003` callback trace and
`AT-RECV-004` caller trace, `AT-RECV-005` history-consumer trace and
`AT-RECV-006` owner/writer trace and `AT-RECV-007` alternate-constructor
trace. AT-RECV-008 identifies `FUN_0054E150` as
`Application::Main::SqwtInterface::CustomLogControlFactor::vfunc3` through
method cell `0x00FA2A5C` in table `0x00FA2A50`. Direct PE identity pins
vtable[-1] COL `0x01145D30`, subobject offset `0x0`, TypeDescriptor
`0x0126E2E0` and raw name
`.?AVCustomLogControlFactor@SqwtInterface@Main@Application@@`.
The separate `LogControlExtension` table `0x00FA2A40` remains the
AT-ENTER-027 World C path.

The exact `FUN_0054BFA0` decompilation/listing resolves a
`RaptureSqwtInterface` teardown/base-cleanup path. It writes complete table
`0x00FA2D8C` at `[ESI]` (`0x0054BFCD`) and adjusted
`RaptureSqwtInterface` table `0x00FA2D6C` at `[ESI+0x4]`
(`0x0054BFD3`), installs `CustomControlExtension` at `+0x2E0`
(`0x00FA2808`, `0x0054C0C8`) and `LogControlExtension` at `+0x2CC`
(`0x00FA2A40`, `0x0054C0E8`), then writes `0x00F90F0C` to `[ESI+0x4]`
at `0x0054C127` after member cleanup. It does not install the
`CustomLogControlFactor` table `0x00FA2A50`. The factor's exact `+0x4`
initializer, outer creator/lifetime path and active field value at
`FUN_0054E150` remain qualified.

At `FUN_0054E150`, ESI is the factor receiver and EDI is the separate
explicit input. The receiver `+0x4` value is pushed first at `0x0054E15C`
and becomes `FUN_00555730`'s second explicit argument. Combined with
AT-RECV-007, this gives receiver `+0x4` -> `FUN_00555730` second argument
-> allocated control `+0x1B08` when the `0x1F10` allocator returns nonnull.
`FUN_00557600` receives the factor as this with the separate input and
allocated result as explicit arguments.

The later call at `0x0054E17A` unconditionally invokes `FUN_00558F60` with
the address of the explicit input's vector descriptor: `LEA ECX,[EDI+0x30]`
at `0x0054E173`. It supplies a pointer to the local allocated or null result
at `0x0054E172`. The available-capacity branch copies that result and
advances the vector current pointer. The full or null-begin branch calls
`FUN_00558720`, whose internals remain qualified.

AT-ID-106, AT-GH-376 and AT-GH-377 pin the teardown-store evidence.
The structured record retains executed checkout-CRLF and Git-LF script
hashes and producing revision `e852799a379b09c807a47e52bedeb8e7f2d1f357`.
Its authenticated outputs are:

- `tools/ghidra/logs/autotranslate-alternate-receiver-20261009-01-auth-009.txt`
  (3,777 bytes, SHA256
  `B50518341463B2DA0D7B5F16A18AD149D28AF33F08127570F7E8DF5B81B77722`).
- `tools/ghidra/logs/autotranslate-alternate-receiver-20261009-01-constructor-decomp-010.txt`
  (3,016 bytes, SHA256
  `C0DF6EA484A8F69E8D16CD76687C5877D3C4809BF6E3AF0E87BF18E2C60B4E35`).
- `tools/ghidra/logs/autotranslate-alternate-receiver-20261009-01-constructor-listing-011.txt`
  (3,894 bytes, SHA256
  `B91476CFC40E16006029C6DB0EFB6C14AAC4A4891F5877FF530128E6905C0653`).

Receiver identity and the conditional field-input edge do not establish the
factor's `+0x4` initializer or equality to World C. Live retention, active
selection, cached table/template state, external family/locale/row identity
and render-versus-forward behavior remain qualified.

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

AT-RECV-003 adds authenticated exact-entry `FUN_00447A40`, `FUN_00445220`,
`FUN_00445470` and `FUN_00447260` decompilation/listing exports. Fresh
authentication AT-ID-090 covers the same executable and seven loaded
initialized file-backed ranges for the initial pair, and fresh AT-ID-092
repeats that authentication before the adaptive pair; all four exports ran read-only with
`headlessSaved=false` and complete requested-target coverage. The callback
trace records exact sender/name source selection, two-call state guards,
preprocessing inputs and slot-2 arguments, plus the existing conditional
C9C670 ordinary-tree effect, without claiming runtime table population,
rendering or forwarding.

AT-RECV-004 adds authenticated exact-entry decompilation and listing exports
for all seven direct `FUN_007906C0` callers. AT-ID-093 authenticates the
project immediately before both exports. The caller trace confirms the
concrete SendLog received-byte-span/parser edge and records bounded
setup/parser/helper dispositions for the other six callers; it does not
promote a received auto-translate association or control grammar, an external family/table/row lookup or
a decoder. The World AT-RECV-001/002/003 handoff to `FUN_007906C0` remains
unjoined.

AT-RECV-005 adds three fresh authenticated export batches covering the
RaptureLogModule slots, the direct history consumer and its two concrete
callers. The exports establish bounded page/range selection, the
`FUN_00404120` byte copy, local delimiter handling, template selection and
callback preparation. Completed TextModule evidence resolves the conditional
`param +0x5C` slot `+0x8` chain through `FUN_00CA1D60 -> FUN_00CA1D40 ->
FUN_00CB2760`. The actual widget/consumer `+0xB0` and AT-RECV-001/002 World
receiver `+0x660` instance join, table retention/population, external family/
table row, final renderer and forwarding decision remain unresolved. The
adjacent cell report authenticates the slot-5, slot-8 and slot-9 values for
the fresh-null vtable branch.

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

AT-GH-275 through AT-GH-286 and fresh identity AT-ID-067 support AT-COMP-017.
The paired exports cover 18 exact-entry targets per modality; each listing
reports COMPLETE. AT-ID-068 independently authenticates the raw descriptor
field reads, cache construction, suffix store, ordinary upper-key stack span
and selected Complete Object Locator offsets/virtual cells. The existing
selected-record, formatter and chat traces remain inputs. AT-COMP-018 owns the
named backing/CSV association. Actual payload delivery, selected field/output
bytes and selected external family remain qualified. AT-COMP-019 owns the
output handoff and category-admission guards.

AT-COMP-018 uses the committed placeName backing report and the completed
AT-COMP-016/017 native joins as inputs. Its source pin identifies the report's
revision, byte count and SHA256. The association is conditional on matching
payload and backend inputs. Actual delivery, selected field/state and output
bytes, selected locale and receive/render lookup remain qualified.

AT-GH-287..294 cover 11 exact-entry targets per modality with COMPLETE
listings. AT-ID-069 authenticates both read-only export batches; AT-ID-070
independently pins the TextModule/category cells, descriptor writer, callback
stack spans and noun literal. AT-COMP-019 uses the completed descriptor,
ordinary-record and chat traces as inputs. These joins establish guarded output
ownership and admission, without observing a historical selection.

AT-GH-295..310 pin the finite field-conversion, string-construction,
callback-vector and selector-09 helper exports. AT-ID-071 authenticates their
read-only batches. AT-ID-072 independently verifies the raw writer, constructor,
thunk, callback argument/return, recursive string restore, index initializer and
call-order spans, plus the pinned definition's ordered index children. These
support AT-COMP-020's conditional field and callback association. Completed
producer, selection, formatter, category-admission and chat traces remain inputs.

AT-GH-311..322 pin six listing/decompilation pairs with 19 exact-entry targets
per modality and COMPLETE listings. AT-ID-073 authenticates each read-only
batch; AT-ID-074 independently verifies the query cell, complete bounded raw
instruction spans, delimiter/key literals, empty fallback object and pinned
definition. AT-COMP-021 uses the retained constructor and CAFA80 callers to
resolve the parameter query and guarded final first-index fields. Previous
records retain their evidence scope; actual delivery and subsequent state remain
qualified.

AT-GH-323..330 pin four listing/decompilation pairs with 19 exact-entry targets
per modality and COMPLETE listings. AT-ID-075 authenticates each read-only
batch. AT-ID-076 independently authenticates selected instruction operands,
function intervals, retained caller spans, dispatch/virtual cells, raw RTTI and
finite parameter literals. AT-COMP-022 resolves the alternative noun methods
under its recorded allocation, loaded-sheet and valid-selector preconditions.

AT-GH-331/332 retain verified complete recorded-reference exports for the
needle object, initializer, literal and destructor addresses. AT-ID-077
authenticates both read-only batches. AT-ID-078 independently pins complete
bounded initializer/destructor and retained string-constructor instructions,
the literal, length sentinel and selected initializer pointer cell.
AT-COMP-023 pins the separate attributive backing report by size and SHA256.
Recorded references and a pointer cell do not prove startup execution or
exclude computed/indirect mutations.
