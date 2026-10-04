# FFXIV 1.23b auto-translate selection contract

The retained static evidence covers UI selection and chat submission.
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
and document-to-getter reconstruction are recovered below. AT-ENTER-008 pins
the retail LogWidget owner/child declarations. AT-ENTER-009 joins their Text2
Enter action to reconstruction/cache access, formatting and routed-event string
production; AT-ENTER-006 and AT-ENTER-007 supply the conditional native
dispatch and conversion to Lua A4_2. AT-ENTER-013/014 recover the allocated
FormElement key, callback writer and
value-1 LogWidget initialization. AT-ENTER-017/018 recover the first-request
loaded-record publication, namespace installation and conditional dispatch
selection. AT-ENTER-019 joins the textual root/TextBox builder, special Name
application and same-container name map under their guards. Resource branch,
property acceptance, name/cache selection and installed actor remain qualified. The
submitted chat source -> FUN_006E91F0 and channel-wrapper joins remain unproved.
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
X+0x30 fallback is distinct. The alternative compiled-resource builder through
FUN_009C9250 -> FUN_009808C0 and the Name binding/deferred branches remain
static targets. This pass does not establish which resource branch runs.

Fresh AT-ENTER-012 corroboration recovers the readiness writer at 0x00767028
in FUN_00766F00. The owner-state and resolved-handle/type gates precede the
+0x5C store and FUN_00574830. Its generic writer is documented in
[the readiness study](../manifests/actor_5c_readiness_gate.json). The specific
resolved object has not been joined to this LogWidget's C, and the write has
not been ordered against C+0x64 form completion.

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
caller or join the reconstructed text to packet submission. AT-ENTER-009
recovers the indirect Text2 read for the declared Enter action. Loaded-child,
namespace and actor selection, cache invalidation, selected record family/key and
Map/World source-object joins remain open static work.

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
