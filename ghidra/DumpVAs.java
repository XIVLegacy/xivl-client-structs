// Ghidra post-script (Java). Generic VA dumper.
// Reads a comma-separated list of hex VAs from XIVL_TARGET_VAS, dumps
// each function's decompilation + caller/callee lists, writes a combined
// report to XIVL_DUMP_PATH (or CWD/dump.txt if unset).
//
// Run via:
//   set XIVL_TARGET_VAS=0x00891F00,0x00DA76B0
//   set XIVL_DUMP_PATH=%TEMP%\xivl-dump.txt
//   analyzeHeadless ... -postScript DumpVAs.java
//
//@category XIVLegacy

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.util.task.ConsoleTaskMonitor;

public class DumpVAs extends GhidraScript {

    @Override
    public void run() throws Exception {
        String vasEnv = System.getenv("XIVL_TARGET_VAS");
        if (vasEnv == null || vasEnv.isEmpty()) {
            println("ERROR: XIVL_TARGET_VAS not set");
            return;
        }
        String outPath = System.getenv("XIVL_DUMP_PATH");
        if (outPath == null || outPath.isEmpty()) {
            outPath = new File(System.getProperty("user.dir"), "dump.txt").getAbsolutePath();
        }

        BufferedWriter w = new BufferedWriter(new FileWriter(outPath));
        try {
            AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
            FunctionManager fm = currentProgram.getFunctionManager();
            DecompInterface decompiler = new DecompInterface();
            decompiler.openProgram(currentProgram);
            ConsoleTaskMonitor monitor = new ConsoleTaskMonitor();

            writeln(w, repeat("=", 70));
            writeln(w, "XIVLegacy VA dump");
            writeln(w, "Source: " + currentProgram.getExecutablePath());
            writeln(w, "VAs: " + vasEnv);
            writeln(w, repeat("=", 70));

            for (String token : vasEnv.split(",")) {
                String va = token.trim();
                if (va.isEmpty()) continue;
                long vaLong = Long.decode(va);
                Address target = space.getAddress(vaLong);
                Function func = fm.getFunctionAt(target);
                if (func == null) {
                    func = fm.getFunctionContaining(target);
                }
                writeln(w, "");
                writeln(w, repeat("-", 70));
                writeln(w, String.format("VA 0x%08X", vaLong));
                writeln(w, repeat("-", 70));
                if (func == null) {
                    writeln(w, "ERROR: no function at or containing VA");
                    continue;
                }
                writeln(w, "Name:       " + func.getName());
                writeln(w, "Entry:      " + func.getEntryPoint());
                writeln(w, "Body bytes: " + func.getBody().getNumAddresses());
                writeln(w, "Signature:  " + func.getSignature());
                writeln(w, "Convention: " + func.getCallingConventionName());
                writeln(w, "");
                writeln(w, "Callers:");
                for (Function c : func.getCallingFunctions(monitor)) {
                    writeln(w, "  " + c.getName() + " @ " + c.getEntryPoint());
                }
                writeln(w, "");
                writeln(w, "Callees:");
                for (Function c : func.getCalledFunctions(monitor)) {
                    writeln(w, "  " + c.getName() + " @ " + c.getEntryPoint());
                }
                writeln(w, "");
                writeln(w, "--- DECOMPILATION ---");
                DecompileResults res = decompiler.decompileFunction(func, 180, monitor);
                if (res.decompileCompleted()) {
                    writeln(w, res.getDecompiledFunction().getC());
                } else {
                    writeln(w, "DECOMP FAILED: " + res.getErrorMessage());
                }
                writeln(w, "");
            }
        } finally {
            w.close();
        }
        println("WROTE: " + outPath);
    }

    private void writeln(BufferedWriter w, String line) throws IOException {
        w.write(line);
        w.newLine();
        println(line);
    }

    private String repeat(String s, int n) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) sb.append(s);
        return sb.toString();
    }
}
