// Scans every instruction for memory operands whose displacement matches one of
// IMPLEMENTATION_OFFSET_QUERY, and reports the containing function, the instruction,
// and whether the field was the destination operand (write) or a source (read).
//
// Exists because the scripts-dir FindOffsetWriters.java only inspects operands
// typed ADDRESS or SCALAR. A register-relative field access like
// `MOV byte ptr [EAX + 0x92],0x1` is typed DYNAMIC, so its displacement is
// never examined and only unrelated immediates of the same value come back.
//
// Env vars:
//   IMPLEMENTATION_OFFSET_QUERY (comma-separated hex offsets, required, e.g. 0x92,0x17838)
//   XIVL_DUMP_PATH    (default FindFieldRefs_output.txt)
//   XIVL_BASE_REGS    (optional comma-separated register filter, e.g. EAX,ESI;
//                         default excludes ESP and EBP so stack locals drop out)
//@category XIVLegacy

import ghidra.app.script.GhidraScript;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class FindFieldRefs extends GhidraScript {

    @Override
    public void run() throws Exception {
        String offArg = System.getenv("IMPLEMENTATION_OFFSET_QUERY");
        if (offArg == null || offArg.isEmpty()) {
            println("Set IMPLEMENTATION_OFFSET_QUERY to comma-separated hex offsets (e.g. 0x92)");
            return;
        }
        Set<Long> targets = new HashSet<>();
        for (String s : offArg.split(",")) {
            s = s.trim();
            if (s.isEmpty()) continue;
            targets.add(Long.parseLong(s.startsWith("0x") || s.startsWith("0X") ? s.substring(2) : s, 16));
        }

        Set<String> allowRegs = new HashSet<>();
        String regArg = System.getenv("XIVL_BASE_REGS");
        if (regArg != null && !regArg.isEmpty()) {
            for (String s : regArg.split(",")) allowRegs.add(s.trim().toUpperCase());
        }

        String outPath = System.getenv("XIVL_DUMP_PATH");
        if (outPath == null || outPath.isEmpty()) outPath = "FindFieldRefs_output.txt";

        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();

        TreeMap<Long, List<String>> byFunc = new TreeMap<>();
        Map<Long, String> funcNames = new HashMap<>();
        long scanned = 0;
        long hits = 0;

        InstructionIterator it = listing.getInstructions(true);
        while (it.hasNext()) {
            if (monitor.isCancelled()) break;
            Instruction insn = it.next();
            scanned++;
            for (int op = 0; op < insn.getNumOperands(); op++) {
                Object[] objs = insn.getOpObjects(op);
                long disp = -1;
                String base = null;
                for (Object o : objs) {
                    if (o instanceof Scalar) disp = ((Scalar) o).getUnsignedValue();
                    else if (o instanceof Register && base == null) base = ((Register) o).getName().toUpperCase();
                }
                // A field access needs both a base register and a displacement.
                // a bare immediate has no register and is not what we are after.
                if (base == null || disp < 0 || !targets.contains(disp)) continue;
                if (allowRegs.isEmpty()) {
                    if (base.equals("ESP") || base.equals("EBP")) continue;
                } else if (!allowRegs.contains(base)) {
                    continue;
                }
                hits++;
                Function f = fm.getFunctionContaining(insn.getAddress());
                long fva = (f == null) ? 0 : f.getEntryPoint().getOffset();
                funcNames.putIfAbsent(fva, (f == null) ? "<no_function>" : f.getName());
                byFunc.computeIfAbsent(fva, k -> new ArrayList<>())
                      .add(String.format("    0x%08x  off=0x%x  %-5s  %s",
                          insn.getAddress().getOffset(), disp,
                          (op == 0 ? "WRITE" : "READ"), insn.toString()));
                break;
            }
        }

        PrintWriter pw = new PrintWriter(new FileWriter(outPath));
        pw.println("======================================================================");
        pw.println(String.format("Field references for offsets %s", offArg));
        pw.println(String.format("Scanned %d instructions, found %d hits in %d functions", scanned, hits, byFunc.size()));
        pw.println("WRITE/READ is operand position only: operand 0 of a two-operand x86");
        pw.println("instruction is the destination, but for CMP/TEST it is still a read.");
        pw.println("======================================================================");
        for (Map.Entry<Long, List<String>> e : byFunc.entrySet()) {
            pw.println();
            pw.println(String.format("Function 0x%08x %s  (%d hits)", e.getKey(), funcNames.get(e.getKey()), e.getValue().size()));
            for (String line : e.getValue()) pw.println(line);
        }
        pw.flush();
        pw.close();
        println("WROTE: " + outPath);
    }
}
