// Applies TSV name, comment, and prototype edits to a Ghidra program.
// Validates the full batch before opening a transaction. Commits only when all
// rows succeed.
// Env:
//   BCS_EDITS         (required) TSV input: op<TAB>address<TAB>value
//   BCS_EDITS_REPORT  (required) report output path
//   BCS_EDITS_UNDO    (optional) write an inverse TSV that reverts this apply
//   BCS_EDITS_DRYRUN  (optional) "1" validates and reports, never writes
//   BCS_LIST_LOCALS   (optional) CSV of function VAs. Writes a rename_local
//                     template to BCS_EDITS_REPORT and applies nothing.
//                     Takes precedence over BCS_EDITS.
// Ops:
//   rename        function entry VA -> new function name
//   rename_data   data/label VA     -> new symbol name (symbol must exist)
//   comment       function entry VA -> plate comment
//   eol           any VA            -> end-of-line disassembly comment
//   prototype     function entry VA -> C signature, e.g. "int f(char * s)"
//   rename_local  function entry VA -> "currentName|storage|newName"
// Values use backslash escapes: \\t \\n \\\\ .
// rename_local matches current name and storage because locals have no stable
// identifier across decompiles. An unmatched pair aborts the batch. Parameters
// are renamed through prototype. Local variable types are unsupported.
//@category XIVLegacy

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.parser.FunctionSignatureParser;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.FunctionDefinitionDataType;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighFunctionDBUtil;
import ghidra.program.model.pcode.HighSymbol;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.util.task.ConsoleTaskMonitor;

public class ApplyProgramEdits extends GhidraScript {

    private static final Pattern ADDR = Pattern.compile("0[xX][0-9A-Fa-f]{1,16}|[0-9A-Fa-f]{1,16}");
    private static final Pattern NAME = Pattern.compile("[A-Za-z_$][A-Za-z0-9_$:<>~@?.]*");

    private static final String OP_RENAME = "rename";
    private static final String OP_RENAME_DATA = "rename_data";
    private static final String OP_COMMENT = "comment";
    private static final String OP_EOL = "eol";
    private static final String OP_PROTOTYPE = "prototype";
    private static final String OP_RENAME_LOCAL = "rename_local";

    private static final int MAX_CANDIDATES_REPORTED = 12;

    /** Validated edit plus prior value for inversion. */
    private static class Edit {
        int lineNo;
        String op;
        String rawAddr;
        Address addr;
        String value;
        String priorValue;
        Function func;
        Symbol symbol;
        FunctionDefinitionDataType parsedSig;
        String localName;
        String localStorage;
        String localNewName;
        HighSymbol highSym;
    }

    private final List<String> errors = new ArrayList<String>();
    private FunctionSignatureParser parser;
    private DecompInterface decomp;

    @Override
    public void run() throws Exception {
        String listVas = System.getenv("BCS_LIST_LOCALS");
        String reportPath = requireEnv("BCS_EDITS_REPORT");

        try {
            if (listVas != null && !listVas.isEmpty()) {
                listLocals(listVas, reportPath);
                return;
            }
            String editsPath = requireEnv("BCS_EDITS");
            String undoPath = System.getenv("BCS_EDITS_UNDO");
            boolean dryRun = "1".equals(System.getenv("BCS_EDITS_DRYRUN"));

            parser = new FunctionSignatureParser(currentProgram.getDataTypeManager(), null);
            applyAll(editsPath, reportPath, undoPath, dryRun);
        }
        finally {
            if (decomp != null) {
                decomp.dispose();
            }
        }
    }

    /** Writes rename_local rows; leaving <newName> unchanged fails validation. */
    private void listLocals(String vasCsv, String outPath) throws Exception {
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        ConsoleTaskMonitor monitor = new ConsoleTaskMonitor();

        int listed = 0;
        int functions = 0;
        BufferedWriter w = new BufferedWriter(
            new OutputStreamWriter(new FileOutputStream(outPath), StandardCharsets.UTF_8));
        try {
            w.write("# rename_local template. Replace <newName> on the rows you want;\n");
            w.write("# rows left unedited fail validation rather than applying.\n");

            for (String raw : vasCsv.split(",")) {
                raw = raw.trim();
                if (raw.isEmpty()) {
                    continue;
                }
                w.write("#\n");
                if (!ADDR.matcher(raw).matches()) {
                    w.write("# " + raw + ": not a single hex address\n");
                    continue;
                }
                Function func;
                try {
                    Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace()
                        .getAddress(Long.parseLong(stripHexPrefix(raw), 16));
                    func = currentProgram.getFunctionManager().getFunctionAt(addr);
                }
                catch (Exception ex) {
                    w.write("# " + raw + ": unresolvable address: " + ex.getMessage() + "\n");
                    continue;
                }
                if (func == null) {
                    w.write("# " + raw + ": no function starts here\n");
                    continue;
                }

                DecompileResults res = decomp.decompileFunction(func, 60, monitor);
                if (res == null || !res.decompileCompleted()) {
                    w.write("# " + raw + ": decompile failed\n");
                    continue;
                }
                functions++;

                List<HighSymbol> locals = new ArrayList<HighSymbol>();
                List<HighSymbol> params = new ArrayList<HighSymbol>();
                Iterator<HighSymbol> it = res.getHighFunction().getLocalSymbolMap().getSymbols();
                while (it.hasNext()) {
                    HighSymbol s = it.next();
                    if (s.isParameter()) {
                        params.add(s);
                    }
                    else {
                        locals.add(s);
                    }
                }

                w.write("# " + raw + "  " + func.getName() + "  locals=" + locals.size()
                    + " parameters=" + params.size() + "\n");
                for (HighSymbol s : params) {
                    w.write("# parameter, rename via prototype: " + s.getName() + "|"
                        + storageOf(s) + "\n");
                }
                for (HighSymbol s : locals) {
                    w.write(OP_RENAME_LOCAL + "\t" + raw + "\t" + s.getName() + "|"
                        + storageOf(s) + "|<newName>\n");
                    listed++;
                }
            }
        }
        finally {
            w.close();
        }
        println("LIST_LOCALS functions=" + functions + " locals=" + listed);
    }

    private void applyAll(String editsPath, String reportPath, String undoPath, boolean dryRun)
            throws Exception {
        List<Edit> edits = parseAndValidate(editsPath);
        resolveLocals(edits);

        if (!errors.isEmpty()) {
            writeReport(reportPath, "VALIDATION_FAILED", 0, edits.size(), 0);
            throw new IllegalStateException(
                "validation failed with " + errors.size() + " error(s); no transaction opened. See "
                    + reportPath);
        }

        // Write undo data before the transaction so a mid-apply failure has a
        // revert path.
        if (undoPath != null && !undoPath.isEmpty()) {
            writeUndo(undoPath, edits);
        }

        if (dryRun) {
            writeReport(reportPath, "DRY_RUN_OK", 0, edits.size(), 0);
            println("DRY_RUN_OK validated=" + edits.size());
            return;
        }

        int applied = 0;
        boolean commit = false;
        long t0 = System.nanoTime();
        int txId = currentProgram.startTransaction("ApplyProgramEdits");
        try {
            for (Edit e : edits) {
                apply(e);
                applied++;
            }
            commit = errors.isEmpty();
        }
        finally {
            currentProgram.endTransaction(txId, commit);
        }
        long txMs = (System.nanoTime() - t0) / 1000000L;

        if (!commit) {
            writeReport(reportPath, "APPLY_FAILED_ROLLED_BACK", applied, edits.size(), txMs);
            throw new IllegalStateException(
                "apply failed; transaction rolled back. See " + reportPath);
        }

        try {
            rewriteUndoForLocals(undoPath, edits);
        }
        catch (Exception ex) {
            errors.add("edits committed, but the undo file could not be refreshed: "
                + ex.getMessage());
            writeReport(reportPath, "APPLIED_UNDO_FAILED", applied, edits.size(), txMs);
            throw new IllegalStateException(
                "edits committed, but undo generation failed. See " + reportPath, ex);
        }

        writeReport(reportPath, "OK", applied, edits.size(), txMs);
        println("OK applied=" + applied + " tx_ms=" + txMs);
    }

    /** Re-resolves local storage after commit because synthetic storage can become a dynamic HASH slot during a rename. */
    private void rewriteUndoForLocals(String undoPath, List<Edit> edits) throws Exception {
        if (undoPath == null || undoPath.isEmpty()) {
            return;
        }
        Map<String, List<Edit>> byFunc = new LinkedHashMap<String, List<Edit>>();
        for (Edit e : edits) {
            if (OP_RENAME_LOCAL.equals(e.op) && e.highSym != null) {
                String key = e.rawAddr.toLowerCase();
                if (!byFunc.containsKey(key)) {
                    byFunc.put(key, new ArrayList<Edit>());
                }
                byFunc.get(key).add(e);
            }
        }
        if (byFunc.isEmpty()) {
            return;
        }

        // Reopen the decompiler so it reflects the committed database.
        if (decomp != null) {
            decomp.dispose();
        }
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        ConsoleTaskMonitor monitor = new ConsoleTaskMonitor();

        for (Map.Entry<String, List<Edit>> group : byFunc.entrySet()) {
            List<Edit> rows = group.getValue();
            DecompileResults res = decomp.decompileFunction(rows.get(0).func, 60, monitor);
            if (res == null || !res.decompileCompleted()) {
                throw new IllegalStateException(
                    "post-commit decompile failed for " + rows.get(0).rawAddr);
            }
            Map<String, String> storageByName = new HashMap<String, String>();
            Iterator<HighSymbol> it = res.getHighFunction().getLocalSymbolMap().getSymbols();
            while (it.hasNext()) {
                HighSymbol s = it.next();
                storageByName.put(s.getName(), storageOf(s));
            }
            for (Edit e : rows) {
                String post = storageByName.get(e.localNewName);
                if (post == null) {
                    throw new IllegalStateException(
                        "renamed local '" + e.localNewName + "' was not found after commit at "
                            + e.rawAddr);
                }
                e.priorValue = e.localNewName + "|" + post + "|" + e.localName;
            }
        }
        writeUndo(undoPath, edits);
    }

    private List<Edit> parseAndValidate(String path) throws Exception {
        List<Edit> edits = new ArrayList<Edit>();
        Set<String> seen = new HashSet<String>();
        BufferedReader r = new BufferedReader(
            new InputStreamReader(new FileInputStream(path), StandardCharsets.UTF_8));
        try {
            String line;
            int lineNo = 0;
            while ((line = r.readLine()) != null) {
                lineNo++;
                String trimmed = line.trim();
                if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                    continue;
                }
                String[] parts = line.split("\t", -1);
                if (parts.length != 3) {
                    err(lineNo, "expected 3 tab-separated fields, got " + parts.length);
                    continue;
                }
                Edit e = new Edit();
                e.lineNo = lineNo;
                e.op = parts[0].trim();
                e.rawAddr = parts[1].trim();
                e.value = unescape(parts[2]);

                if (!ADDR.matcher(e.rawAddr).matches()) {
                    // Reject multi-VA fields from symbols.json, such as
                    // "0x0075E1C0;0089E0D0".
                    err(lineNo, "not a single hex address: '" + e.rawAddr + "'");
                    continue;
                }
                String key = e.op + "@" + e.rawAddr.toLowerCase();
                if (OP_RENAME_LOCAL.equals(e.op)) {
                    String[] localParts = e.value.split("\\|", -1);
                    if (localParts.length >= 2) {
                        key += "|" + localParts[0].trim() + "|" + localParts[1].trim();
                    }
                }
                if (!seen.add(key)) {
                    err(lineNo, "duplicate " + e.op + " for " + e.rawAddr);
                    continue;
                }
                try {
                    e.addr = currentProgram.getAddressFactory().getDefaultAddressSpace()
                        .getAddress(Long.parseLong(stripHexPrefix(e.rawAddr), 16));
                }
                catch (Exception ex) {
                    err(lineNo, "unresolvable address " + e.rawAddr + ": " + ex.getMessage());
                    continue;
                }

                if (validateOp(e)) {
                    edits.add(e);
                }
            }
        }
        finally {
            r.close();
        }
        return edits;
    }

    private boolean validateOp(Edit e) {
        if (OP_RENAME.equals(e.op) || OP_COMMENT.equals(e.op) || OP_PROTOTYPE.equals(e.op)
                || OP_RENAME_LOCAL.equals(e.op)) {
            e.func = currentProgram.getFunctionManager().getFunctionAt(e.addr);
            if (e.func == null) {
                err(e.lineNo, "no function starts at " + e.rawAddr
                    + " (use the entry VA, not an interior address)");
                return false;
            }
        }

        if (OP_RENAME.equals(e.op)) {
            if (!NAME.matcher(e.value).matches()) {
                err(e.lineNo, "invalid symbol name '" + e.value + "'");
                return false;
            }
            e.priorValue = e.func.getName();
            return true;
        }
        if (OP_RENAME_DATA.equals(e.op)) {
            if (!NAME.matcher(e.value).matches()) {
                err(e.lineNo, "invalid symbol name '" + e.value + "'");
                return false;
            }
            SymbolTable st = currentProgram.getSymbolTable();
            e.symbol = st.getPrimarySymbol(e.addr);
            if (e.symbol == null) {
                err(e.lineNo, "no symbol at " + e.rawAddr + "; rename_data cannot create one");
                return false;
            }
            e.priorValue = e.symbol.getName();
            return true;
        }
        if (OP_COMMENT.equals(e.op)) {
            e.priorValue = nullToEmpty(e.func.getComment());
            return true;
        }
        if (OP_EOL.equals(e.op)) {
            if (currentProgram.getListing().getCodeUnitContaining(e.addr) == null) {
                err(e.lineNo, "no code unit at " + e.rawAddr);
                return false;
            }
            e.priorValue =
                nullToEmpty(currentProgram.getListing().getComment(CommentType.EOL, e.addr));
            return true;
        }
        if (OP_PROTOTYPE.equals(e.op)) {
            try {
                e.parsedSig = parser.parse(e.func.getSignature(), e.value);
            }
            catch (Exception ex) {
                err(e.lineNo, "unparsable signature '" + e.value + "': " + ex.getMessage());
                return false;
            }
            e.priorValue = e.func.getSignature().getPrototypeString();
            return true;
        }
        if (OP_RENAME_LOCAL.equals(e.op)) {
            String[] p = e.value.split("\\|", -1);
            if (p.length != 3) {
                err(e.lineNo, "rename_local value must be 'currentName|storage|newName', got '"
                    + e.value + "'");
                return false;
            }
            e.localName = p[0].trim();
            e.localStorage = p[1].trim();
            e.localNewName = p[2].trim();
            if (!NAME.matcher(e.localNewName).matches()) {
                err(e.lineNo, "invalid local name '" + e.localNewName + "'");
                return false;
            }
            if (e.localName.isEmpty() || e.localStorage.isEmpty()) {
                err(e.lineNo, "rename_local needs both a current name and a storage string");
                return false;
            }
            return true;
        }
        err(e.lineNo, "unknown op '" + e.op + "'");
        return false;
    }

    /** Resolves rename_local rows once per function before opening a transaction. */
    private void resolveLocals(List<Edit> edits) {
        Map<String, List<Edit>> byFunc = new LinkedHashMap<String, List<Edit>>();
        Set<String> prototypeTargets = new HashSet<String>();
        for (Edit e : edits) {
            if (OP_RENAME_LOCAL.equals(e.op)) {
                String key = e.rawAddr.toLowerCase();
                if (!byFunc.containsKey(key)) {
                    byFunc.put(key, new ArrayList<Edit>());
                }
                byFunc.get(key).add(e);
            }
            else if (OP_PROTOTYPE.equals(e.op)) {
                prototypeTargets.add(e.rawAddr.toLowerCase());
            }
        }
        if (byFunc.isEmpty()) {
            return;
        }

        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        ConsoleTaskMonitor monitor = new ConsoleTaskMonitor();

        for (Map.Entry<String, List<Edit>> group : byFunc.entrySet()) {
            List<Edit> rows = group.getValue();
            Edit first = rows.get(0);

            // Prototype changes rerun decompilation and invalidate resolved local symbols.
            if (prototypeTargets.contains(group.getKey())) {
                for (Edit e : rows) {
                    err(e.lineNo, "same file has a prototype edit for " + e.rawAddr
                        + "; split the local renames into a second run");
                }
                continue;
            }

            DecompileResults res = decomp.decompileFunction(first.func, 60, monitor);
            if (res == null || !res.decompileCompleted()) {
                for (Edit e : rows) {
                    err(e.lineNo, "decompile failed for " + e.rawAddr);
                }
                continue;
            }
            HighFunction hf = res.getHighFunction();

            List<HighSymbol> locals = new ArrayList<HighSymbol>();
            Iterator<HighSymbol> it = hf.getLocalSymbolMap().getSymbols();
            while (it.hasNext()) {
                locals.add(it.next());
            }

            for (Edit e : rows) {
                List<HighSymbol> hits = new ArrayList<HighSymbol>();
                for (HighSymbol s : locals) {
                    if (s.getName().equals(e.localName) && storageOf(s).equals(e.localStorage)) {
                        hits.add(s);
                    }
                }
                if (hits.isEmpty()) {
                    err(e.lineNo, "no local named '" + e.localName + "' with storage '"
                        + e.localStorage + "' in " + e.rawAddr + "; present: " + describe(locals));
                    continue;
                }
                if (hits.size() > 1) {
                    err(e.lineNo, "ambiguous: " + hits.size() + " locals match '" + e.localName
                        + "|" + e.localStorage + "' in " + e.rawAddr);
                    continue;
                }
                HighSymbol sym = hits.get(0);
                if (sym.isParameter()) {
                    err(e.lineNo, "'" + e.localName + "' is a parameter; rename it via prototype");
                    continue;
                }
                e.highSym = sym;
                e.priorValue =
                    e.localNewName + "|" + e.localStorage + "|" + e.localName;
            }
        }
    }

    private static String storageOf(HighSymbol s) {
        if (s.getStorage() == null) {
            return "";
        }
        return s.getStorage().toString();
    }

    /** Formats Name|storage pairs for rename_local diagnostics. */
    private static String describe(List<HighSymbol> locals) {
        StringBuilder b = new StringBuilder();
        int n = 0;
        for (HighSymbol s : locals) {
            if (s.isParameter()) {
                continue;
            }
            if (n >= MAX_CANDIDATES_REPORTED) {
                b.append("; ...");
                break;
            }
            // Use "; " because storage strings may contain commas.
            if (n > 0) {
                b.append("; ");
            }
            b.append(s.getName()).append("|").append(storageOf(s));
            n++;
        }
        if (n == 0) {
            return "(no non-parameter locals)";
        }
        return b.toString();
    }

    private void apply(Edit e) {
        try {
            if (OP_RENAME.equals(e.op)) {
                e.func.setName(e.value, SourceType.USER_DEFINED);
            }
            else if (OP_RENAME_DATA.equals(e.op)) {
                e.symbol.setName(e.value, SourceType.USER_DEFINED);
            }
            else if (OP_COMMENT.equals(e.op)) {
                e.func.setComment(emptyToNull(e.value));
            }
            else if (OP_EOL.equals(e.op)) {
                currentProgram.getListing()
                    .setComment(e.addr, CommentType.EOL, emptyToNull(e.value));
            }
            else if (OP_PROTOTYPE.equals(e.op)) {
                ApplyFunctionSignatureCmd cmd =
                    new ApplyFunctionSignatureCmd(e.addr, e.parsedSig, SourceType.USER_DEFINED);
                if (!cmd.applyTo(currentProgram)) {
                    err(e.lineNo, "signature apply rejected: " + cmd.getStatusMsg());
                }
            }
            else if (OP_RENAME_LOCAL.equals(e.op)) {
                HighFunctionDBUtil.updateDBVariable(
                    e.highSym, e.localNewName, null, SourceType.USER_DEFINED);
            }
        }
        catch (Exception ex) {
            err(e.lineNo, e.op + " failed at " + e.rawAddr + ": " + ex.getMessage());
        }
    }

    /** Emits inverse edits in reverse so rename chains unwind cleanly. */
    private void writeUndo(String path, List<Edit> edits) throws Exception {
        BufferedWriter w = new BufferedWriter(
            new OutputStreamWriter(new FileOutputStream(path), StandardCharsets.UTF_8));
        try {
            w.write("# inverse of " + System.getenv("BCS_EDITS") + "\n");
            for (int i = edits.size() - 1; i >= 0; i--) {
                Edit e = edits.get(i);
                w.write(e.op + "\t" + e.rawAddr + "\t" + escape(e.priorValue) + "\n");
            }
        }
        finally {
            w.close();
        }
    }

    private void writeReport(String path, String status, int applied, int rows, long txMs)
            throws Exception {
        BufferedWriter w = new BufferedWriter(
            new OutputStreamWriter(new FileOutputStream(path), StandardCharsets.UTF_8));
        try {
            w.write("status=" + status + "\n");
            w.write("rows=" + rows + "\n");
            w.write("applied=" + applied + "\n");
            w.write("errors=" + errors.size() + "\n");
            w.write("tx_ms=" + txMs + "\n");
            for (String e : errors) {
                w.write(e + "\n");
            }
        }
        finally {
            w.close();
        }
    }

    private void err(int lineNo, String msg) {
        errors.add("line " + lineNo + ": " + msg);
    }

    private String requireEnv(String name) {
        String v = System.getenv(name);
        if (v == null || v.isEmpty()) {
            throw new IllegalStateException("required env var " + name + " is unset");
        }
        return v;
    }

    private static String stripHexPrefix(String s) {
        if (s.startsWith("0x") || s.startsWith("0X")) {
            return s.substring(2);
        }
        return s;
    }

    private static String nullToEmpty(String s) {
        if (s == null) {
            return "";
        }
        return s;
    }

    private static String emptyToNull(String s) {
        if (s == null || s.isEmpty()) {
            return null;
        }
        return s;
    }

    private static String unescape(String s) {
        StringBuilder b = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\\' && i + 1 < s.length()) {
                char n = s.charAt(++i);
                if (n == 'n') {
                    b.append('\n');
                }
                else if (n == 't') {
                    b.append('\t');
                }
                else if (n == '\\') {
                    b.append('\\');
                }
                else {
                    b.append('\\').append(n);
                }
            }
            else {
                b.append(c);
            }
        }
        return b.toString();
    }

    private static String escape(String s) {
        return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n");
    }
}
