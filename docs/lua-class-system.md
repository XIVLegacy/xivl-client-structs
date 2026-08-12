# Lua Game Engine (LGE) class system

Reference for the FFXIV 1.23b Lua-side class system behind `_defineClass`,
`_defineBaseClass`, and `_onLoop.Method = function()...end`.

## Model

The LGE class system is a script-facing wrapper around the C++ type
`Component::Lua::GameEngine::Work::MetamethodArray2D::Impl` (RTTI-confirmed).
At engine init, `FUN_0078E3A0` registers 36 named classes (12 utility + 24
BaseClass) statically.

Script code declares new subclasses dynamically via `_defineClass(C, P)` /
`_defineBaseClass(C, P)`, which call the same C++ registration helpers. Methods
and callbacks attach via `_onLoop.MethodName = function()...end`, which fires a
Lua N-API that pushes a 2-upvalue cclosure into the class's global table.

At instantiation, each class instance carries 3
`MetamethodArray2D::Impl*` pointers at struct offsets `+0x60` (save), `+0x64`
(own), and `+0x68` (sync). The 3 scopes form the first dimension of a 2D array
of member descriptors. Descriptors are the second dimension. Member reads
dispatch through scopes in priority order `own > save > sync`.

Writes go through one polymorphic chokepoint (`FUN_00d272d0`). Five Lua
metatables expose different facets of this substrate to script: instance,
member descriptor, indexed container, cursor, and memory pool.

## Pipeline diagram

```text
Engine startup
   |
   v
FUN_0078FC90 (engine init)
   |
   v
FUN_0078E3A0 (BCS-Y-0398) - LuaClassRegistry, 1986 bytes
   |  registers 36 named classes via per-type shim:
   |    FUN_00CC71F0 -> FUN_00CD9C10  (utility,  12 entries)
   |    FUN_00CC71E0 -> FUN_00CD9BC0  (BaseClass, 24 entries)
   v
[class names + paths populated in registry]
   |
   v
Script load: ./Lua chunk runs
   |
   +-- `_defineClass(Child, Parent)` (BCS-Y-0484)
   |     -> FUN_006DCC30 shim
   |     -> FUN_0078C2A0 inner impl
   |        - reads arg-vector at *(state+0x10)+4 (16-byte stride)
   |        - FUN_0071CE70 pulls arg[0]=Child, arg[1]=Parent
   |        - FUN_00CC7050 links parent->child
   |        - FUN_00CC71F0 registers as utility (same shim as static path)
   |
   +-- `_defineBaseClass(Child, Parent)` (BCS-Y-0487)
   |     -> FUN_006DCCA0 shim
   |     -> FUN_0078C330 inner impl (byte-identical to FUN_0078C2A0)
   |        - same arg unpack + FUN_00CC7050 link
   |        - FUN_00CC71E0 registers as BaseClass (same shim as static path)
   |
   +-- `_onLoop.MethodName = function() ... end`  (BCS-Y-0513)
         -> FUN_00d07eb0 (`_onLoop.__newindex` Lua N-API wrapper)
         -> FUN_00d07bb0 dynamic-method register
            - FUN_00cd77d0 (BCS-Y-0514) resolves engine context from Lua state
            - FUN_00cd77d0(state, 1) returns class registration record
            - FUN_00d07890 tests if name already registered
              - handles "self"-prefix (instance method via FUN_00cd7a50)
              - handles "_inl"-suffix (inlined dispatch via PTR_DAT_01266b10)
            - allocates 8-byte upvalue: [class_ctx_ptr, method_slot]
            - pushes 2-upvalue cclosure (FUN_00d07f20 or FUN_00d07f90 selected
              by FUN_00cf49a0 condition) into global table
                                  |
                                  v
[methods now bound to class as cclosures]
                                  |
                                  v
Instantiation: Lua code creates an instance of the class
   |
   v
FUN_00d1ce10 ("BaseClass" path, called from
              FUN_00d085b0 = _onLoop.__index)
   |  walks the class declaration table
   |  for each declared member, allocates and registers
   v
FUN_00D20B00 metatable (BCS-Y-0505) installed on the new instance
   |  class instance struct hypothesis (BCS-S-0041):
   |    +0x30 = active-dispatch slot (member name + tag byte)
   |    +0x34 = lua-state / engine context ref
   |    +0x60 = MetamethodArray2D::Impl*   (save scope)
   |    +0x64 = MetamethodArray2D::Impl*   (own scope)
   |    +0x68 = MetamethodArray2D::Impl*   (sync scope)
   v
[instance usable from Lua]
```

## The 5 Lua metatables

The catalog models all five as views over the `MetamethodArray2D::Impl`
storage substrate. BCS-S-0041 through BCS-S-0045 remain `hypothesis-strong`.

| Lua role | C++ name (where known) | Metatable | Inner | BCS-Y | BCS-S |
|---|---|---:|---|---|---|
| Class instance | (anonymous wrapper) | `FUN_00D20B00` | varies, +0x68 min | BCS-Y-0505 | BCS-S-0041 LGEClassInstanceInner |
| Memory pool wrapper | (view onto Impl) | `FUN_00D208A0` | 0x28 | BCS-Y-0506 | BCS-S-0042 LGEMemoryPoolInner |
| Member descriptor | (per-method record) | `FUN_00D207A0` | 0x54 | BCS-Y-0507 | BCS-S-0043 LGEMemberDescriptorInner |
| Indexed container | (member-table view) | `FUN_00D20540` | 0x5c | BCS-Y-0508 | BCS-S-0044 LGEIndexedContainerInner |
| Cursor / scope view | `Component::Lua::GameEngine::Work::MetamethodArray2D::Impl` | `FUN_00D20670` | 0x08 outer | BCS-Y-0509 | BCS-S-0045 LGECursorInner + BCS-S-0046 LGE_MetamethodArray2D_Impl |

BCS-Y-0506 exposes `_save`, `_temp`, `_sync`, and nine size fields from a
wrapped `MetamethodArray2D::Impl`. BCS-Y-0509 delegates operations through
that wrapped object's vtable.

## The 6 special fields on class instances

D20B00's `__index` (`FUN_00d16d40`) and `__newindex` (`FUN_00d175b0`) special-case these names before falling through to member lookup:

| Field | Read returns | Write effect |
|---|---|---|
| `_save` | D208A0-wrapped Impl* at struct +0x60 | (read-only) |
| `_temp` | D208A0-wrapped Impl* at struct +0x64 | (read-only) |
| `_sync` | D208A0-wrapped Impl* at struct +0x68 | (read-only) |
| `_tag` | (dispatch to member lookup) | Allocates a new 0x54-byte member descriptor (BCS-S-0043) via FUN_009d1b35 and routes through FUN_00d26b10 / FUN_00d26ea0 to attach it dynamically |
| `_bind` | (dispatch) | Network-binding hook |
| `_debug` | (dispatch) | Instrumentation hook |

The allocator role of `_tag` is the bridge between D20B00 (instance) and D207A0 (member descriptor) - both Lua metatables wrap the same 0x54-byte inner struct.

## The 15 special fields on D208A0 (memory pool wrapper)

D208A0's `__index` (`FUN_00d2ea60`, 1349 bytes) is one large if/else cascade. All read-only (`__newindex` is a 3-byte empty stub):

| Field | Reads |
|---|---|
| `_save`, `_temp`, `_sync` | Pool table pointer at struct +0x1c / +0x20 / +0x24 (non-null = real allocator attached) |
| `_reserve`, `_nesting`, `_name` | Pool metadata fields |
| `_saveAllocatedSize` / `_tempAllocatedSize` / `_syncAllocatedSize` | Per-scope: `FUN_00d1dca0(struct+0x10/+0x14/+0x18)` if table-ptr non-null, else 0 |
| `_saveAssignedSize` / `_tempAssignedSize` / `_syncAssignedSize` | Per-scope: `FUN_00d1ddc0(...)` if table-ptr non-null |
| `_saveAvailableSize` / `_tempAvailableSize` / `_syncAvailableSize` | Per-scope: `FUN_00d1dee0(...)` if table-ptr non-null, else inline `(x & 7 != 0) + (x >> 3)` bit-count |

## Storage substrate: MetamethodArray2D

`Component::Lua::GameEngine::Work::MetamethodArray2D` is the C++ type that backs all per-instance member storage. RTTI-confirmed via three vftable references:

- `::Impl` (polymorphic base, set by `FUN_00d2e4d0` row populator)
- `::ImplArray` (derived, 0x60 bytes, allocated by `FUN_00d2e2d0` - the D20670 6-param ctor path)
- `::ImplArray2D` (derived, 0x64 bytes - extra dword at +0x18 for 2nd-dim width, allocated by `FUN_00d2e360` - the D20670 7-param ctor path)

Each class instance has 3 of these (BCS-S-0041 fields `save_pool`/`temp_pool`/`sync_pool` at struct +0x60/+0x64/+0x68). The 3 scopes are the FIRST dimension. Member descriptors keyed by name are the SECOND dimension.

### 2D index calculation (FUN_00d211e0, BCS-Y-0518)

```c
int index_2d(int *width, int *row, int *col) {
    if (*row == DAT_0130d78c)  return -1;      // invalid-row sentinel
    if (*col == DAT_0130d79c)  return *row;    // invalid-col sentinel
    return (*width) * (*row) + (*col);
}
```

### Member lookup priority (FUN_00d16cd0, BCS-Y-0516)

Tries the 3 scope arrays in order, first hit wins. Sets active-dispatch marker byte at instance+0x30:

| Scope | Struct field | Hit marker at +0x30 |
|---|---|---|
| Own  | +0x64 | `DAT_0130d422` |
| Save | +0x60 | `DAT_01377fb9` (default marker, also = miss) |
| Sync | +0x68 | `DAT_0130d423` |
| Miss | -     | `DAT_01377fb9` |

Scripts can shadow inherited members by redeclaring them in the own scope.
The sync scope is checked last and overrides nothing.

### Write chokepoint (FUN_00d272d0, BCS-Y-0515)

9-parameter polymorphic dispatcher. ALL three cluster `__newindex` paths funnel here (D207A0, D20540, D20B00):

1. `vtable +0x6c` on the class context validates the write target (`FUN_00d12210`).
2. If validate succeeds AND tag byte at `param_2+0xb` matches `DAT_01377fb9`:
   - if `*param_2 == 0`: `FUN_00d211e0` 2D-index + `vtable+4` of class
   - else: `vtable+4` of `*param_2` (the member descriptor's writer) with engine ref-pair `FUN_00cd2af0`/`00cd2b00`
3. Else (validate fails): `vtable +0x64` of class with `DAT_0130d788` sentinel.

This is the single chokepoint where Lua-side mutation crosses into
class-instance state.

## Engine-context resolver (FUN_00cd77d0, BCS-Y-0514)

Reads reserved registry key `DAT_0130d4e0` from the Lua state and returns the
first dword of the matched userdata as the engine context pointer. The 21
observed callers use this resolver across the LGE namespace.

## The 36 statically-registered classes

Source: the `FUN_0078E3A0` decompilation.

### 12 utility classes (via `FUN_00CC71F0`)

`Global`, `Debug`, `Math`, `String`, `Table`, `WorldMaster`, `OtherArea`, `SpreadSheet`, `CutScene`, `CommandDebuggerGM`, `CommandDebuggerDEV`, `CommandDebuggerTEST`

### 24 BaseClasses (via `FUN_00CC71E0`)

`SystemBaseClass`, `ProgDebugBaseClass`, `ActorBaseClass`, `CharaBaseClass`, `PlayerBaseClass`, `NpcBaseClass`, `WorldBaseClass`, `AreaBaseClass`, `PrivateAreaBaseClass`, `ZoneBaseClass`, `DebugBaseClass`, `JudgeBaseClass`, `CommandBaseClass`, `StatusBaseClass`, `QuestBaseClass`, `DirectorBaseClass`, `CommandDebuggerBaseClass`, `CommandDebuggerFUNCBaseClass`, `ItemBaseClass`, `ImportantItemBaseClass`, `MoneyItemBaseClass`, `NormalItemBaseClass`, `GameDataBaseClass`, `GroupBaseClass`

The source records C++ vtables for eight classes, including `ActorBaseClass`
at `0xbd4fe4`. Shipped scripts subclass these through `_defineClass` and
`_defineBaseClass`.

## Lua stdlib overrides relevant to the class system

The FFXIV 1.23b client replaces four Lua standard-library functions alongside
the LGE root namespace (BCS-Y-0501). `_pcall` preserves the original `pcall`:

| Name | Impl | Behavior |
|---|---|---|
| `assert` | FUN_00d08ed0 | Override |
| `error` | FUN_00d090c0 | Override |
| `type` | FUN_00d09240 | Override |
| `pcall` | FUN_00d093b0 | Override |
| `_pcall` | (preserved alias) | Stock Lua 5.1 pcall behavior |

Any script-behavior analysis that assumes stock Lua 5.1 stdlib semantics for `assert`/`error`/`pcall`/`type` is incorrect.

## Special string-dispatch table

The `__index` / `__newindex` dispatchers compare against these reserved field names at `.rdata 0x0110f034..0x0110f278`:

| String | Address | Used by |
|---|---|---|
| `self` | 0x0110f034 | FUN_00d07890 (instance-method prefix marker) |
| `_inl` | 0x0110f03c | FUN_00d07890 (inlined-dispatch suffix marker) |
| `:` | 0x0110f044 | FUN_00d07bb0 (fully-qualified method name separator) |
| `_save` | 0x0110f234, 0x011100b8 | D20B00 `__index`/`__newindex`, D208A0 `__index` |
| `_temp` | 0x0110f240, 0x011100c0 | (same) |
| `_sync` | 0x0110f24c, 0x011100c8 | (same) |
| `_tag` | 0x0110f258 | D20B00 `__newindex` (dynamic member alloc branch) |
| `_bind` | 0x0110f264 | D20B00 `__newindex` |
| `_debug` | 0x0110f270 | D20B00 `__newindex` |
| `__lge_returnNil` | 0x0110f048 | LGE bootstrap stdlib (BCS-Y-0501) |
| `__lge_getWork` | 0x0110f058 | LGE bootstrap stdlib (BCS-Y-0501) |
| `_isAlive` | 0x0110f068 | IndividualRef metatable (BCS-Y-0503) |
| `__lge_isAlive` | 0x0110f074 | LGE bootstrap stdlib (BCS-Y-0501) |

Two parallel `_save`/`_temp`/`_sync` string blocks exist (0x0110f234 and 0x011100b8) - different metatables use different copies for their dispatchers.

## Lifecycle methods

Standard Lua-side lifecycle hooks visible in the binary:

- `_onInit` - constructor
- `_onFinalize` - destructor
- `_onTimer` - tick callback

Superclass calls use `self:_callSuperClassFunc("methodName")`. The engine
manages the chain instead of using Lua's `Parent.method(self, ...)` form.

## Class definition vs reference

A class becomes defined when registrar `FUN_00CD9360` (BCS-Y-1806) runs its
method table and invokes the `+0x7d=1` valid-state writer `FUN_00CE1DD0`
(BCS-Y-1805). A reference keyed by name that is not defined has `+0x7e=1`, set
by tentative-state writer `FUN_00CE2880` (BCS-Y-1807).

The observed definition path starts when a Lua chunk loaded through the
`.lpb`/`.lcb` `require()` chain executes `_defineClass`. `FUN_00D08A10` is
BCS-Y-1809 and the same entry point as BCS-Y-0480;
BCS-Y-1809..BCS-Y-1813 record
the chain. It has no direct code cross-reference, so static evidence does not
exclude an unresolved indirect caller.

The binary registers 57 native base-class path strings (BCS-Y-1819). Lua
`_defineClass` creates derived classes at runtime. Zone and actor id-to-path
bindings live in gamedata sheet string columns, not the binary.

## BCS-Y entries indexed by role

| BCS-Y | Role |
|---|---|
| BCS-Y-0398 | LuaClassRegistry_FUN_0078E3A0 (static registry, 36 classes) |
| BCS-Y-0480 | LuaNApi__luaGameEngineRequire (FUN_00D08A10; same function as BCS-Y-1809) |
| BCS-Y-0484 | LuaNApi__defineClass |
| BCS-Y-0487 | LuaNApi__defineBaseClass |
| BCS-Y-0491 | LuaEnginePathTableInit (57 .prog and BaseClass path strings) |
| BCS-Y-0500 | LuaUserdataMetatableCluster_d2fXXX (structural) |
| BCS-Y-0501 | LuaEngine_LGEBootstrap_FUN_00cd8990 (13 named globals + _onLoop) |
| BCS-Y-0502 | LuaBindingTemplates_Phase36d_RemainingSweep |
| BCS-Y-0505 | LGEClassInstanceMetatable_FUN_00D20B00 |
| BCS-Y-0506 | LGEMemoryPoolWrapperMetatable_FUN_00D208A0 |
| BCS-Y-0507 | LGEMemberDescriptorMetatable_FUN_00D207A0 |
| BCS-Y-0508 | LGEIndexedContainerMetatable_FUN_00D20540 |
| BCS-Y-0509 | LGECursorMetatable_FUN_00D20670 |
| BCS-Y-0510 | LuaClassRegistry_BaseClassRegisterPath |
| BCS-Y-0511 | LuaClassRegistry_UtilityClassRegisterPath |
| BCS-Y-0512 | LuaNApi__defineClassInner+_defineBaseClassInner |
| BCS-Y-0513 | LuaLGE_OnLoopNewindex_DynamicMethodRegister_Cluster |
| BCS-Y-0514 | LuaEngineContextLookup_FUN_00cd77d0 |
| BCS-Y-0515 | LGEMetamethodArray2D_WriteChokepoint_FUN_00d272d0 |
| BCS-Y-0516 | LGEMetamethodArray2D_MemberLookup_FUN_00d16cd0 |
| BCS-Y-0517 | LGEMetamethodArray2D_GenericLookup_FUN_00d1df90 |
| BCS-Y-0518 | LGEMetamethodArray2D_IndexCalculator_FUN_00d211e0 |
| BCS-Y-0519 | LGEMetamethodArray2D_ImplInit_Cluster |
| BCS-Y-0520 | LGEMetamethodArray2D_SmallHelpers_Cluster |
| BCS-Y-1805 | LuaClassEntry_SetValid_clearTentative_plus0x7d_writer_FUN_00CE1DD0 |
| BCS-Y-1806 | LuaClassDefine_Registrar_promote_FUN_00CD9360 |
| BCS-Y-1809..BCS-Y-1813 | `.lpb`/`.lcb` `require()` loader chain: `FUN_00D08A10` -> `FUN_00D0CFB0` -> `FUN_00D08180` -> `FUN_00CF4680` -> `_defineClass` -> `FUN_00CD9360`; registered by `FUN_00CD8990` |

## BCS-S entries

| BCS-S | Type | Confidence |
|---|---|---|
| BCS-S-0041 | LGEClassInstanceInner | hypothesis-strong |
| BCS-S-0042 | LGEMemoryPoolInner | hypothesis-strong |
| BCS-S-0043 | LGEMemberDescriptorInner | hypothesis-strong |
| BCS-S-0044 | LGEIndexedContainerInner | hypothesis-strong |
| BCS-S-0045 | LGECursorInner | hypothesis-strong |
| BCS-S-0046 | LGE_MetamethodArray2D_Impl | confirmed (RTTI) |

## Known limits

- BCS-S-0046 does not enumerate the vtable slots between the observed
  destructor at slot 0, write at `+0x04`, read at `+0x1c`, length at `+0x50`,
  and validate at `+0x6c`.
- The descriptor table's on-heap layout remains unknown. The proposed
  `+0x54..+0x5c` row fields in BCS-S-0046 remain unconfirmed.
- `FUN_00D20540` and `FUN_00D207A0` share `FUN_00d272d0` and
  `FUN_00d16080`, but their exact relationship remains inferred.
- `FUN_00d07890` binds `_inl` names through `FUN_00d077b0` and
  `PTR_DAT_01266b10`. The resulting dispatch behavior is unresolved.
- `FUN_00d2e760` also calls `FUN_00d272d0`, but its role is unknown.

## References

- `manifests/lua_api_index.json` - the catalogued N-API name index (see the manifest's `apis` count for the live total)
