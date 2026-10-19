# Chocobo naming native checks

The lender's dialogue operands and event-return values are canonical in
`xivl-client-scripts:docs/chocobo-lender-client-contract.md`. The naming
widget's language branches, configured ranges, length formula and conversion
are canonical in
`xivl-client-scripts:docs/chocobo-mount-script-contracts.md#naming-widget`.
This record establishes the native string counter and the named
first-character property's update path. These are client checks, not an
issuance, payment or server name-admission policy.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`.
Addresses are absolute VAs. Ghidra `12.1.3` used the committed read-only
exporters. `VerifyProgramFileBytes.java` ended with
`COMPLETE: program-file-bytes-v1`: retained original and modified FileBytes
and every loaded initialized file-backed range matched that executable.
The program reported `x86:LE:32:default`, compiler spec `windows`.
Excluded unbacked data and actual runtime initialization are not authenticated.

## UTF-8 sequence count

`FUN_0073C900` registers the exact `_getUTF8StringLength` name at literal
`0x00FD73B8`, referenced at `0x0073C9E9`, with callback `FUN_006DCED0`.
The callback reaches `FUN_0078CF80`, which reads argument `0` as a string
through `FUN_0071CE70`, passes that string object to `FUN_00445E50`, and
returns the integer result through `FUN_00584F70`
(`0x0078CFB0-0x0078CFCD`).

`FUN_00445E50` returns an already cached count when string byte `+0x10` is
set. Otherwise it walks the NUL-terminated byte buffer, advances by the
leading-byte sequence size, increments once per sequence, stores the count
at string `+0x0C` and marks the cache. A null buffer returns `0`.
On well-formed UTF-8 this counts encoded characters, not bytes, grapheme
clusters or visual width. The routine also contains legacy five/six-byte
branches; this observation does not establish a general malformed-input
validation contract.

The Lua widget combines this count `C` with Lua byte length `B` as
`(B + C) / 2`. Its explicit Chinese Decide condition is a result from `3`
through `4`. The native counter therefore does not itself implement a
four-character maximum. The widget's separate `MaxLength = "10b"` property
and configured acceptance description remain distinct inputs.

## IsValidFirst

The exact literal `IsValidFirst` is at `0x0106EBB4`. Startup instructions
`0x00F23AF0-0x00F23B13` pass that literal and descriptor address
`0x0135A4A4` to `FUN_009108E0`, then assign descriptor index `0x0F` and
flags `0x80` at `+0x14/+0x18`. This is an encoded initialization path,
not an observation of the descriptor's live contents.

`FUN_00959920` obtains the current text string from control `+0x1758`, or
the shared empty-string object when absent. It reads character index `0`
through `FUN_004461D0` at `0x0095993C`. That helper advances by UTF-8
sequences and decodes the selected character through `FUN_00445850`.
The comparisons at `0x00959941`, `0x00959946` and `0x0095994B` compute
false for `0x2D`, `0x3F` and `0x5F` (`-`, `?`, `_`) and true otherwise.
This predicate is not an alphabet-only or digit-rejection check.

The property state is packed at control `+0x1791`. The update resolves a
pending state when bit `0x10` is set. When either low state bit is set and
the computed result differs from bit `0x20`, it stores the new result in
that bit and calls `FUN_0099C680` with descriptor `0x0135A4A4`
(`0x00959983-0x009599B5`). The flags qualify this update; the routine does
not unconditionally overwrite every control instance's property.

The `Sqwt::Controls::TextBox` constructor `FUN_0095C300` installs primary
vftable `0x0106EDB4` and initializes this result bit to true at
`0x0095C514-0x0095C51F`. It initializes the two low state bits from the
descriptor flags at `0x0135A4BC`. The encoded `0x80` startup flags yield
low bits `2` before later overrides. This is a constructor/default contract,
not an observed live widget state.

The Lua consumer reads `getControlProperty("TextBox_Name", "IsValidFirst")`
only in its Chinese branch and disables Decide only for Boolean false.
`WidgetBaseClass.getControlProperty` forwards
`_getProperty(nil, controlName, propertyName)`; the corresponding
three-input native callback registered by `FUN_00744990` is
`FUN_006EBA80`. Its nil-first-argument route reaches `FUN_0075B870`,
`FUN_00538500` and `FUN_00538130`. That route resolves the named control
and property. Its Boolean property conversion is case `6` in
`FUN_00538130`. The separate `_getProperty` registration in
`FUN_0074D940`, with callback `FUN_00700450`, is a different argument shape
and is not substituted for this widget route.

The naming class obtains its Chinese acceptance description from control
user-work slot `1`. Neither this first-character predicate nor the sequence
counter establishes that description's complete character set. The client
checks do not establish reserved-name, profanity, uniqueness or server
acceptance rules.

## Reproduction

Authenticate the exact input through
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java), using
the explicit-input procedure and required size/hash/base values in
[`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
With explicit project/JDK bindings, use a new absolute output path:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Counter registration, input and sequence count | `0x0073C900,0x006DCED0,0x0078CF80,0x00445E50` |
| First-character calculation, constructor and descriptor initialization helper | `0x00959920,0x004461D0,0x009108E0,0x0095C300` |
| Widget property registration and typed read | `0x00744990,0x0074D940,0x006EBA80,0x00700450,0x0075B870,0x00538500,0x00538130,0x00537FA0,0x00537AF0` |

Each promoted section had a named exact-entry function and decompilation,
without an error or failed-decompilation marker. Corroborate callback
installation, hidden register receivers and flag comparisons with
`DumpFunctionListing.java` using:

```text
0x0073C900,0x006DCED0,0x0078CF80,0x00445E50,0x00959920,0x006EBA80,0x0075B870,0x00538500,0x00744990,0x0095C300
```

The listing runs ended with matching completion counts (`9/9` and `3/3`);
the second also inspected two exploratory helpers. The exact-name
reference trace used:

```powershell
tools/ghidra/export-references.ps1 `
    -Strings '_getUTF8StringLength','IsValidFirst','InputMethod.AcceptChars', `
             '_getProperty','_setProperty' -Out $Output
```

The verified report scanned `28414` defined strings and ended with five
queries, six matches and seven references. Both property registrations and
both `InputMethod.AcceptChars` literal candidates were retained. An address
trace for `0x0135A4A4,0x01360370` ended with two targets and fifteen recorded
references. These queries locate candidates; body/instruction inspection
establishes the facts above. They do not exclude computed, indirect, dynamic
or unanalyzed references.

`FindFieldRefs.java` with `IMPLEMENTATION_OFFSET_QUERY = '0x1791'`
located the positive field accesses in `FUN_00959920` and `FUN_0095C300`
and the property-binding block at `0x00959444`. Its destination-operand
labels are not semantic write classifications. No absence claim relies on
this scan.

Tiny reads of the identified PE corroborated the startup descriptor
instructions at `0x00F23AF0` and property table entry at `0x012E33E8`.
The primary vftable's `-4` points to COL `0x0117BE78`, whose `+0x0C`
points to TypeDescriptor `0x0126D2C0`; its name at `+8` is
`.?AVTextBox@Controls@Sqwt@@`.
They used the PE section table and
`tools/extractors/client_pe/import_table_dumper.py:rva_to_file_offset`, with
Capstone `5.0.7` in x86-32 mode for the instruction span. No client body,
ignored export or machine-local path is a tracked evidence dependency.
