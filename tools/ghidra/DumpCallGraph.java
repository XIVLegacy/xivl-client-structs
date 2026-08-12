// Ghidra post-script: dumps static direct-call edges as a TSV edge list.
// One row per function (forward address order):
//   <entryVA>\t<maxBodyVA>\t<name>\t<comma-separated callee entry VAs>
// Function.getCalledFunctions(monitor) supplies the callee set. Indirect and
// virtual dispatch are excluded. tools/build_callgraph.py inverts these edges.
// Env vars:
//   XIVL_CALLGRAPH_OUT  output path, default DumpCallGraph_output.tsv
// Run via:
//   analyzeHeadless <proj> <name> -process ffxivgame.exe -noanalysis -readOnly \
//     -scriptPath tools/ghidra -postScript DumpCallGraph.java
//@category XIVLegacy

import java.io.PrintWriter;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class DumpCallGraph extends GhidraScript {

    @Override
    public void run() throws Exception {
        String outPath = System.getenv("XIVL_CALLGRAPH_OUT");
        if (outPath == null || outPath.isEmpty()) {
            outPath = "DumpCallGraph_output.tsv";
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter pw = new PrintWriter(new FileWriter(outPath));

        int funcCount = 0;
        long edgeCount = 0;
        for (Function f : fm.getFunctions(true)) {
            if (monitor.isCancelled()) break;
            funcCount++;
            long entry = f.getEntryPoint().getOffset();
            long maxVa = f.getBody().getMaxAddress().getOffset();
            String name = f.getName();

            List<Long> calleeVas = new ArrayList<>();
            Set<Function> callees = f.getCalledFunctions(monitor);
            for (Function c : callees) {
                calleeVas.add(c.getEntryPoint().getOffset());
            }
            Collections.sort(calleeVas);

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < calleeVas.size(); i++) {
                if (i > 0) sb.append(",");
                sb.append(String.format("0x%08x", calleeVas.get(i)));
            }
            edgeCount += calleeVas.size();

            pw.println(String.format("0x%08x\t0x%08x\t%s\t%s",
                entry, maxVa, name, sb.toString()));
        }
        pw.flush();
        pw.close();
        println(String.format("DumpCallGraph: wrote %d functions, %d edges to %s",
            funcCount, edgeCount, outPath));
    }
}
