// Finds switch dispatch fed by a register-relative +0x90 load and unusually
// large computed jumps that could cover scene record id 0x93.
//
// Env vars:
//   XIVL_DUMP_PATH (required output path)
//@category XIVLegacy

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.JumpTable;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class FindSceneRecordConsumers extends GhidraScript {
    private static final long FIELD_OFFSET = 0x90;
    private static final int MIN_CASES = 0x93;

    private static class FieldHit {
        Function function;
        Instruction instruction;
        String baseRegister;
    }

    private static class FlowHit {
        FieldHit field;
        PcodeOpAST branch;
        List<String> path;
    }

    private static class LargeJump {
        Function function;
        Instruction instruction;
        List<Long> destinations;
        List<Integer> recoveredCases = new ArrayList<>();
        List<Long> recoveredDestinations = new ArrayList<>();
        int recoveredCaseCount;
        boolean recoveredCase93;
        boolean recoveredIndex93;
        Integer recoveredIndexMin;
        Integer recoveredIndexMax;
    }

    private static class DecompStats {
        int attempts;
        int completed;
        int failures;
        int cancellations;
        int timeouts;
        List<String> failureDetails = new ArrayList<>();
        List<String> cancellationDetails = new ArrayList<>();
        List<String> timeoutDetails = new ArrayList<>();
    }

    @Override
    public void run() throws Exception {
        String outPath = System.getenv("XIVL_DUMP_PATH");
        if (outPath == null || outPath.isEmpty()) {
            throw new IllegalArgumentException("XIVL_DUMP_PATH is required");
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        ReferenceManager refs = currentProgram.getReferenceManager();
        Map<Long, List<FieldHit>> fieldsByFunction = new HashMap<>();
        List<LargeJump> largeJumps = new ArrayList<>();
        long instructionCount = 0;
        boolean cancelled = false;
        boolean sweepCancellation = false;
        DecompStats decompStats = new DecompStats();

        InstructionIterator instructions = listing.getInstructions(true);
        while (instructions.hasNext()) {
            if (monitor.isCancelled()) {
                cancelled = true;
                sweepCancellation = true;
                break;
            }
            Instruction instruction = instructions.next();
            instructionCount++;
            Function function = fm.getFunctionContaining(instruction.getAddress());
            if (function == null) continue;

            FieldHit field = findFieldRead(function, instruction);
            if (field != null) {
                fieldsByFunction.computeIfAbsent(
                    function.getEntryPoint().getOffset(), k -> new ArrayList<>()).add(field);
            }

            if (instruction.getFlowType().isComputed()) {
                List<Long> destinations = new ArrayList<>();
                for (Reference reference : refs.getReferencesFrom(instruction.getAddress())) {
                    RefType type = reference.getReferenceType();
                    if (type.isFlow() && type.isComputed()) {
                        // Preserve one entry per recovered table reference. Multiple
                        // entries may intentionally share a destination.
                        destinations.add(reference.getToAddress().getOffset());
                    }
                }
                if (!destinations.isEmpty()) {
                    LargeJump hit = new LargeJump();
                    hit.function = function;
                    hit.instruction = instruction;
                    hit.destinations = destinations;
                    largeJumps.add(hit);
                }
            }
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        int computedJumpCount = largeJumps.size();
        largeJumps = inspectLargeJumps(largeJumps, decompiler, decompStats);
        List<FlowHit> flowHits = traceFieldLoads(fieldsByFunction, fm, decompiler, decompStats);
        if (monitor.isCancelled()) {
            cancelled = true;
            if (decompStats.cancellations == 0) sweepCancellation = true;
        }
        decompiler.dispose();
        flowHits.sort(Comparator
            .comparingLong((FlowHit h) -> h.field.function.getEntryPoint().getOffset())
            .thenComparingLong(h -> h.field.instruction.getAddress().getOffset())
            .thenComparingLong(h -> h.branch.getSeqnum().getTarget().getOffset()));
        largeJumps.sort(Comparator
            .comparingLong((LargeJump h) -> h.function.getEntryPoint().getOffset())
            .thenComparingLong(h -> h.instruction.getAddress().getOffset()));
        int recoveredCoverageCount = 0;
        int largeTableOnlyCount = 0;
        for (LargeJump hit : largeJumps) {
            if (hit.recoveredCase93 || hit.recoveredIndex93) recoveredCoverageCount++;
            else largeTableOnlyCount++;
        }

        try (PrintWriter out = new PrintWriter(new FileWriter(outPath))) {
            out.println("Scene record 0x93 consumer sweep");
            out.println("Program: " + currentProgram.getName());
            out.println("Executable: " + currentProgram.getExecutablePath());
            out.println("Image base: " + currentProgram.getImageBase());
            out.println("Field criterion: register-relative read at +0x90 reaches BRANCHIND in high p-code");
            out.println("Large-table fallback criterion: recovered case count is at least 0x93; duplicate destinations retained");
            out.println("Recovered coverage criterion: decompiler switch labels or recovered table-index coverage include 0x93");
            out.printf("Scanned instructions: %d%n", instructionCount);
            out.printf("Functions with register-relative +0x90 reads: %d%n", fieldsByFunction.size());
            out.printf("Field-to-switch hits: %d%n", flowHits.size());
            out.printf("Computed flow instructions with references: %d%n", computedJumpCount);
            out.printf("Qualified computed switch hits: %d%n", largeJumps.size());
            out.printf("Recovered 0x93 case/index coverage hits: %d%n", recoveredCoverageCount);
            out.printf("Large-table-only fallback hits: %d%n", largeTableOnlyCount);
            out.printf("Sweep status: %s%n", cancelled ? "CANCELLED" : "COMPLETED");
            out.printf("Cancellation count: %d%n", decompStats.cancellations + (sweepCancellation ? 1 : 0));
            out.printf("Timeout count: %d%n", decompStats.timeouts);
            out.printf("Decompilation attempts: %d%n", decompStats.attempts);
            out.printf("Decompilations completed: %d%n", decompStats.completed);
            out.printf("Decompilation failure count: %d%n", decompStats.failures);

            out.println();
            out.println("[RUN_EVENTS]");
            if (!cancelled && decompStats.cancellations == 0 && decompStats.timeouts == 0 && decompStats.failures == 0) {
                out.println("COMPLETE_WITH_ZERO_CANCELLATION_TIMEOUT_FAILURE");
            }
            for (String detail : decompStats.cancellationDetails) out.println("CANCELLATION " + detail);
            if (sweepCancellation) out.println("CANCELLATION sweep monitor was cancelled");
            for (String detail : decompStats.timeoutDetails) out.println("TIMEOUT " + detail);
            for (String detail : decompStats.failureDetails) out.println("DECOMP_FAILURE " + detail);

            out.println();
            out.println("[FIELD_TO_SWITCH]");
            if (flowHits.isEmpty()) out.println("NONE");
            for (FlowHit hit : flowHits) {
                out.printf("Function 0x%08x %s%n",
                    hit.field.function.getEntryPoint().getOffset(), hit.field.function.getName());
                out.printf("  field 0x%08x base=%s insn=%s%n",
                    hit.field.instruction.getAddress().getOffset(), hit.field.baseRegister,
                    hit.field.instruction.toString());
                out.printf("  branchind 0x%08x%n", hit.branch.getSeqnum().getTarget().getOffset());
                out.println("  path " + String.join(" -> ", hit.path));
            }

            out.println();
            out.println("[LARGE_JUMP_TABLE]");
            if (largeJumps.isEmpty()) out.println("NONE");
            for (LargeJump hit : largeJumps) {
                out.printf("Function 0x%08x %s%n",
                    hit.function.getEntryPoint().getOffset(), hit.function.getName());
                out.printf("  jump 0x%08x entries=%d raw_references=%d insn=%s%n",
                    hit.instruction.getAddress().getOffset(), hit.recoveredCaseCount,
                    hit.destinations.size(),
                    hit.instruction.toString());
                out.printf("  raw distinct destinations=%d recovered targets=%d%n",
                    new HashSet<Long>(hit.destinations).size(), hit.recoveredDestinations.size());
                out.printf("  recovered cases=%d case_0x93=%s%n", hit.recoveredCaseCount,
                    hit.recoveredCase93 ? "YES" : "NO");
                if (hit.recoveredIndexMin != null) {
                    out.printf("  recovered index coverage=0x%08x..0x%08x index_0x93=%s%n",
                        hit.recoveredIndexMin, hit.recoveredIndexMax,
                        hit.recoveredIndex93 ? "YES" : "NO");
                } else {
                    out.println("  recovered index coverage=NONE index_0x93=NO");
                }
                out.print("  recovered case values");
                for (int value : hit.recoveredCases) out.printf(" 0x%08x", value);
                out.println();
                out.print("  recovered targets");
                for (long destination : hit.recoveredDestinations) out.printf(" 0x%08x", destination);
                out.println();
            }
        }
        println("WROTE: " + outPath);
    }

    private FieldHit findFieldRead(Function function, Instruction instruction) {
        boolean hasLoad = false;
        for (PcodeOp op : instruction.getPcode()) {
            if (op.getOpcode() == PcodeOp.LOAD) {
                hasLoad = true;
                break;
            }
        }
        if (!hasLoad) return null;

        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            String base = null;
            boolean hasOffset = false;
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof ghidra.program.model.lang.Register && base == null) {
                    base = ((ghidra.program.model.lang.Register) object).getName().toUpperCase();
                } else if (object instanceof ghidra.program.model.scalar.Scalar) {
                    long value = ((ghidra.program.model.scalar.Scalar) object).getUnsignedValue();
                    if (value == FIELD_OFFSET) hasOffset = true;
                }
            }
            if (base == null || !hasOffset || base.equals("ESP") || base.equals("EBP")) continue;
            FieldHit hit = new FieldHit();
            hit.function = function;
            hit.instruction = instruction;
            hit.baseRegister = base;
            return hit;
        }
        return null;
    }

    private List<FlowHit> traceFieldLoads(Map<Long, List<FieldHit>> fieldsByFunction,
                                          FunctionManager fm,
                                          DecompInterface decompiler,
                                          DecompStats stats) {
        List<FlowHit> hits = new ArrayList<>();
        for (Map.Entry<Long, List<FieldHit>> entry : fieldsByFunction.entrySet()) {
            if (monitor.isCancelled()) break;
            Function function = fm.getFunctionAt(
                currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(entry.getKey()));
            if (function == null) continue;
            stats.attempts++;
            DecompileResults result = decompiler.decompileFunction(function, 180, monitor);
            if (!result.decompileCompleted() || result.getHighFunction() == null) {
                recordDecompFailure(entry.getKey(), result, stats);
                continue;
            }
            stats.completed++;
            HighFunction high = result.getHighFunction();
            Map<Long, List<PcodeOpAST>> opsByAddress = new HashMap<>();
            Iterator<PcodeOpAST> operations = high.getPcodeOps();
            while (operations.hasNext()) {
                PcodeOpAST op = operations.next();
                long address = op.getSeqnum().getTarget().getOffset();
                opsByAddress.computeIfAbsent(address, k -> new ArrayList<>()).add(op);
            }
            for (FieldHit field : entry.getValue()) {
                List<PcodeOpAST> addressOps = opsByAddress.get(
                    field.instruction.getAddress().getOffset());
                if (addressOps == null) continue;
                for (PcodeOpAST op : addressOps) {
                    if (op.getOpcode() != PcodeOp.LOAD || op.getOutput() == null) continue;
                    traceToBranch(field, op, hits);
                }
            }
        }
        return hits;
    }

    private List<LargeJump> inspectLargeJumps(List<LargeJump> largeJumps,
                                   DecompInterface decompiler, DecompStats stats) {
        List<LargeJump> qualified = new ArrayList<>();
        Set<Long> seenFunctions = new HashSet<>();
        for (LargeJump hit : largeJumps) {
            long entry = hit.function.getEntryPoint().getOffset();
            if (!seenFunctions.add(entry)) continue;
            if (monitor.isCancelled()) return qualified;
            stats.attempts++;
            DecompileResults result = decompiler.decompileFunction(hit.function, 180, monitor);
            if (!result.decompileCompleted() || result.getHighFunction() == null) {
                recordDecompFailure(entry, result, stats);
                continue;
            }
            stats.completed++;
            HighFunction high = result.getHighFunction();
            for (LargeJump candidate : largeJumps) {
                if (candidate.function.getEntryPoint().getOffset() != entry) continue;
                for (JumpTable table : high.getJumpTables()) {
                    if (table.getSwitchAddress() == null ||
                        table.getSwitchAddress().getOffset() != candidate.instruction.getAddress().getOffset()) {
                        continue;
                    }
                    Integer[] labels = table.getLabelValues();
                    if (labels == null) continue;
                    Address[] cases = table.getCases();
                    if (cases != null) {
                        for (Address destination : cases) {
                            if (destination != null) {
                                candidate.recoveredDestinations.add(destination.getOffset());
                            }
                        }
                    }
                    for (Integer label : labels) {
                        if (label == null) continue;
                        candidate.recoveredCases.add(label);
                        candidate.recoveredCaseCount++;
                        if (label == MIN_CASES) candidate.recoveredCase93 = true;
                        if (candidate.recoveredIndexMin == null || label < candidate.recoveredIndexMin) {
                            candidate.recoveredIndexMin = label;
                        }
                        if (candidate.recoveredIndexMax == null || label > candidate.recoveredIndexMax) {
                            candidate.recoveredIndexMax = label;
                        }
                    }
                    candidate.recoveredIndex93 = candidate.recoveredIndexMin != null &&
                        candidate.recoveredIndexMin <= MIN_CASES && candidate.recoveredIndexMax >= MIN_CASES;
                    if (candidate.recoveredCaseCount >= MIN_CASES || candidate.recoveredCase93 ||
                        candidate.recoveredIndex93) {
                        qualified.add(candidate);
                    }
                }
            }
        }
        return qualified;
    }

    private void recordDecompFailure(long entry, DecompileResults result, DecompStats stats) {
        String error = result.getErrorMessage();
        if (error == null || error.isEmpty()) error = "no error message";
        String detail = String.format("0x%08x: %s", entry, error);
        String lower = error.toLowerCase();
        if (monitor.isCancelled() || lower.contains("cancel")) {
            stats.cancellations++;
            stats.cancellationDetails.add(detail);
        } else if (lower.contains("timeout") || lower.contains("timed out")) {
            stats.timeouts++;
            stats.timeoutDetails.add(detail);
        } else {
            stats.failures++;
            stats.failureDetails.add(detail);
        }
        printerr("DECOMP FAILED " + detail);
    }

    private void traceToBranch(FieldHit field, PcodeOpAST load, List<FlowHit> hits) {
        ArrayDeque<Varnode> queue = new ArrayDeque<>();
        Map<Varnode, List<String>> paths = new HashMap<>();
        Set<Varnode> seen = new HashSet<>();
        queue.add(load.getOutput());
        paths.put(load.getOutput(), new ArrayList<>(Collections.singletonList("LOAD")));
        while (!queue.isEmpty()) {
            Varnode value = queue.removeFirst();
            if (!seen.add(value)) continue;
            Iterator<PcodeOp> descendants = value.getDescendants();
            while (descendants.hasNext()) {
                PcodeOp descendant = descendants.next();
                List<String> path = new ArrayList<>(paths.get(value));
                path.add(descendant.getMnemonic());
                if (descendant.getOpcode() == PcodeOp.BRANCHIND) {
                    FlowHit hit = new FlowHit();
                    hit.field = field;
                    hit.branch = (PcodeOpAST) descendant;
                    hit.path = path;
                    hits.add(hit);
                    continue;
                }
                Varnode output = descendant.getOutput();
                if (output != null && path.size() <= 32 && !seen.contains(output)) {
                    queue.addLast(output);
                    paths.putIfAbsent(output, path);
                }
            }
        }
    }
}
