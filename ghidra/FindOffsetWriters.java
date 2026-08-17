// Finds stores whose effective address reaches an offset after address arithmetic,
// including register propagation, indexed addressing, and exact stack-local spills.
//
// Undefined executable bytes are decoded with PseudoDisassembler so unclaimed tails
// are swept without changing the program. Pseudo-decoded hits are labeled separately.
//
// Env vars:
//   XIVL_OFFSET_QUERY (comma-separated hex offsets, required, e.g. 0x4d8,0x4e8)
//   XIVL_DUMP_PATH    (explicit output path, required)
//@category XIVLegacy

import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.lang.InsufficientBytesException;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.UnknownContextException;
import ghidra.program.model.lang.UnknownInstructionException;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.FlowType;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class FindOffsetWriters extends GhidraScript {
    private static final long MASK32 = 0xffffffffL;
    private static final int MAX_TRACE = 12;

    private static class Expr {
        final TreeMap<String, Long> terms = new TreeMap<>();
        final LinkedHashSet<String> flags = new LinkedHashSet<>();
        final ArrayList<String> trace = new ArrayList<>();
        long constant;
        boolean known = true;

        static Expr unknown() {
            Expr e = new Expr();
            e.known = false;
            return e;
        }

        static Expr constant(long value) {
            Expr e = new Expr();
            e.constant = value;
            return e;
        }

        static Expr root(String name) {
            Expr e = new Expr();
            e.terms.put(name, 1L);
            return e;
        }

        Expr copy() {
            Expr e = new Expr();
            e.known = known;
            e.constant = constant;
            e.terms.putAll(terms);
            e.flags.addAll(flags);
            e.trace.addAll(trace);
            return e;
        }

        Expr add(Expr other, long factor) {
            if (!known || !other.known) return unknown();
            Expr e = copy();
            e.constant += other.constant * factor;
            for (Map.Entry<String, Long> term : other.terms.entrySet()) {
                long value = e.terms.getOrDefault(term.getKey(), 0L) + term.getValue() * factor;
                if (value == 0) e.terms.remove(term.getKey());
                else e.terms.put(term.getKey(), value);
            }
            e.flags.addAll(other.flags);
            appendTrace(e.trace, other.trace);
            return e;
        }

        Expr scale(long factor) {
            if (!known) return unknown();
            Expr e = copy();
            e.constant *= factor;
            for (Map.Entry<String, Long> term : new ArrayList<>(e.terms.entrySet())) {
                long value = term.getValue() * factor;
                if (value == 0) e.terms.remove(term.getKey());
                else e.terms.put(term.getKey(), value);
            }
            if (factor != 1) e.flags.add("INDEXED");
            return e;
        }

        void note(String line) {
            if (trace.size() == MAX_TRACE) trace.remove(0);
            trace.add(line);
        }

        long offset32() {
            return constant & MASK32;
        }

        String format() {
            if (!known) return "<unknown>";
            ArrayList<String> parts = new ArrayList<>();
            for (Map.Entry<String, Long> term : terms.entrySet()) {
                if (term.getValue() == 1) parts.add(term.getKey());
                else parts.add(term.getKey() + "*" + term.getValue());
            }
            long value = offset32();
            if (value != 0 || parts.isEmpty()) parts.add(String.format("0x%x", value));
            return String.join(" + ", parts);
        }
    }

    private static class State {
        final Map<Varnode, Expr> values = new HashMap<>();
        final Map<String, Expr> stack = new HashMap<>();
        final ArrayList<String> history = new ArrayList<>();
        Address blockStart;

        void reset(Address address) {
            values.clear();
            stack.clear();
            history.clear();
            blockStart = address;
        }
    }

    private static class Hit {
        Address address;
        Address blockStart;
        long target;
        boolean pseudo;
        String function;
        String instruction;
        String expression;
        String registerProvenance;
        String nearestDefinedInstruction;
        List<String> blockPrefix;
        List<String> forms;
        List<String> trace;
    }

    private static class Counters {
        long definedInstructions;
        long pseudoInstructions;
        long pseudoFailures;
        long definedDataBytes;
        long undefinedBytesSkipped;
        long blocks;
        long stores;
    }

    private Set<Long> targets;
    private Listing listing;
    private FunctionManager functions;
    private final ArrayList<Hit> hits = new ArrayList<>();
    private final Counters counts = new Counters();

    @Override
    public void run() throws Exception {
        String offsetArg = requireEnv("XIVL_OFFSET_QUERY");
        String outPath = requireEnv("XIVL_DUMP_PATH");
        targets = parseOffsets(offsetArg);
        listing = currentProgram.getListing();
        functions = currentProgram.getFunctionManager();

        boolean complete = false;
        String incompleteReason = "unknown failure";
        try {
            AddressSet blockStarts = collectDefinedBlockStarts();
            if (monitor.isCancelled()) {
                incompleteReason = "cancelled while collecting block starts";
            }
            else {
                sweepExecutable(blockStarts);
                if (monitor.isCancelled()) incompleteReason = "cancelled during executable sweep";
                else complete = true;
            }
        }
        catch (Exception e) {
            incompleteReason = e.getClass().getSimpleName() + ": " + e.getMessage();
            throw e;
        }
        finally {
            writeReport(outPath, offsetArg, complete, incompleteReason);
        }

        if (complete) println("COMPLETE: FindOffsetWriters " + outPath);
        else println("INCOMPLETE: FindOffsetWriters " + incompleteReason);
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException("Set " + name + " to an explicit value");
        }
        return value.trim();
    }

    private Set<Long> parseOffsets(String text) {
        Set<Long> result = new HashSet<>();
        for (String token : text.split(",")) {
            String value = token.trim();
            if (value.isEmpty()) continue;
            if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
            result.add(Long.parseUnsignedLong(value, 16) & MASK32);
        }
        if (result.isEmpty()) throw new IllegalArgumentException("XIVL_OFFSET_QUERY contained no offsets");
        return result;
    }

    private AddressSet collectDefinedBlockStarts() {
        AddressSet starts = new AddressSet();
        for (Function function : functions.getFunctions(true)) starts.add(function.getEntryPoint());

        InstructionIterator iterator = listing.getInstructions(true);
        while (iterator.hasNext()) {
            if (monitor.isCancelled()) break;
            Instruction instruction = iterator.next();
            for (Address flow : instruction.getFlows()) {
                if (currentProgram.getMemory().contains(flow)) starts.add(flow);
            }
            FlowType type = instruction.getFlowType();
            if (type.isJump() || type.isCall() || type.isTerminal()) {
                Address fallthrough = instruction.getFallThrough();
                if (fallthrough != null) starts.add(fallthrough);
            }
        }
        return starts;
    }

    private void sweepExecutable(AddressSet blockStarts) throws Exception {
        AddressSetView executable = currentProgram.getMemory().getExecuteSet();
        if (executable.isEmpty()) executable = currentProgram.getMemory().getLoadedAndInitializedAddressSet();
        PseudoDisassembler pseudo = new PseudoDisassembler(currentProgram);
        pseudo.setRespectExecuteFlag(true);
        State state = new State();
        AddressRangeIterator ranges = executable.getAddressRanges(true);

        while (ranges.hasNext() && !monitor.isCancelled()) {
            AddressRange range = ranges.next();
            Address cursor = range.getMinAddress();
            state.reset(cursor);
            counts.blocks++;
            while (cursor != null && cursor.compareTo(range.getMaxAddress()) <= 0) {
                if (monitor.isCancelled()) return;
                if (blockStarts.contains(cursor) && !cursor.equals(state.blockStart)) {
                    state.reset(cursor);
                    counts.blocks++;
                }

                Instruction defined = listing.getInstructionAt(cursor);
                if (defined != null) {
                    counts.definedInstructions++;
                    processInstruction(defined, false, state);
                    cursor = nextAddress(defined.getMaxAddress(), range.getMaxAddress());
                    if (endsBlock(defined)) resetAtNext(state, cursor);
                    continue;
                }

                if (listing.getUndefinedDataAt(cursor) != null) {
                    PseudoInstruction decoded = decodeUndefined(pseudo, cursor);
                    if (decoded == null || overlapsDefinedCode(decoded)) {
                        counts.pseudoFailures++;
                        counts.undefinedBytesSkipped++;
                        cursor = nextAddress(cursor, range.getMaxAddress());
                        resetAtNext(state, cursor);
                        continue;
                    }

                    counts.pseudoInstructions++;
                    processInstruction(decoded, true, state);
                    cursor = nextAddress(decoded.getMaxAddress(), range.getMaxAddress());
                    if (endsBlock(decoded)) resetAtNext(state, cursor);
                    continue;
                }

                CodeUnit codeUnit = listing.getCodeUnitContaining(cursor);
                if (codeUnit != null) {
                    counts.definedDataBytes += codeUnit.getLength();
                    cursor = nextAddress(codeUnit.getMaxAddress(), range.getMaxAddress());
                    resetAtNext(state, cursor);
                    continue;
                }

                counts.undefinedBytesSkipped++;
                cursor = nextAddress(cursor, range.getMaxAddress());
                resetAtNext(state, cursor);
            }
        }
    }

    private PseudoInstruction decodeUndefined(PseudoDisassembler pseudo, Address address) {
        try {
            return pseudo.disassemble(address);
        }
        catch (InsufficientBytesException | UnknownInstructionException | UnknownContextException e) {
            return null;
        }
    }

    private boolean overlapsDefinedCode(Instruction instruction) {
        Instruction nextInstruction = listing.getInstructionAfter(instruction.getAddress());
        if (nextInstruction != null &&
                nextInstruction.getMinAddress().compareTo(instruction.getMaxAddress()) <= 0) return true;
        Data nextData = listing.getDefinedDataAfter(instruction.getAddress());
        return nextData != null && nextData.getMinAddress().compareTo(instruction.getMaxAddress()) <= 0;
    }

    private Address nextAddress(Address address, Address rangeMax) {
        if (address.compareTo(rangeMax) >= 0) return null;
        try {
            return address.addNoWrap(1);
        }
        catch (Exception e) {
            return null;
        }
    }

    private void resetAtNext(State state, Address next) {
        if (next != null) {
            state.reset(next);
            counts.blocks++;
        }
    }

    private boolean endsBlock(Instruction instruction) {
        FlowType type = instruction.getFlowType();
        return type.isJump() || type.isCall() || type.isTerminal();
    }

    private void processInstruction(Instruction instruction, boolean pseudo, State state) {
        Map<Varnode, Expr> before = new HashMap<>();
        for (Map.Entry<Varnode, Expr> entry : state.values.entrySet()) {
            before.put(entry.getKey(), entry.getValue().copy());
        }

        for (PcodeOp op : instruction.getPcode()) {
            int opcode = op.getOpcode();
            if (opcode == PcodeOp.STORE) {
                processStore(instruction, pseudo, state, before, op);
                continue;
            }
            if (opcode == PcodeOp.LOAD) {
                processLoad(instruction, state, op);
                continue;
            }
            Varnode output = op.getOutput();
            if (output == null) continue;

            Expr result = evaluateAssignment(instruction, state, op);
            if (result.known) state.values.put(output, result);
            else state.values.remove(output);
        }
        if (state.history.size() == MAX_TRACE) state.history.remove(0);
        state.history.add(String.format("0x%08x %s", instruction.getAddress().getOffset(),
            instruction.toString()));
    }

    private Expr evaluateAssignment(Instruction instruction, State state, PcodeOp op) {
        int opcode = op.getOpcode();
        Expr a = op.getNumInputs() > 0 ? valueOf(state, op.getInput(0), instruction.getAddress()) : Expr.unknown();
        Expr b = op.getNumInputs() > 1 ? valueOf(state, op.getInput(1), instruction.getAddress()) : Expr.unknown();
        Expr result;

        switch (opcode) {
            case PcodeOp.COPY:
            case PcodeOp.CAST:
            case PcodeOp.INT_ZEXT:
            case PcodeOp.INT_SEXT:
            case PcodeOp.SUBPIECE:
                result = a.copy();
                break;
            case PcodeOp.INT_ADD:
                result = a.add(b, 1);
                break;
            case PcodeOp.INT_SUB:
                result = a.add(b, -1);
                break;
            case PcodeOp.INT_2COMP:
                result = a.scale(-1);
                break;
            case PcodeOp.INT_MULT:
                result = multiply(a, b);
                break;
            case PcodeOp.INT_LEFT:
                result = shiftLeft(a, b);
                break;
            case PcodeOp.PTRADD:
                Expr scale = valueOf(state, op.getInput(2), instruction.getAddress());
                result = scale.known && scale.terms.isEmpty() ? a.add(b.scale(scale.constant), 1) : Expr.unknown();
                if (result.known) result.flags.add("INDEXED");
                break;
            case PcodeOp.PTRSUB:
                result = a.add(b, 1);
                break;
            default:
                return Expr.unknown();
        }

        if (result.known && arithmeticOpcode(opcode)) {
            result.note(String.format("0x%08x %s -> %s", instruction.getAddress().getOffset(),
                instruction.toString(), result.format()));
        }
        return result;
    }

    private boolean arithmeticOpcode(int opcode) {
        return opcode == PcodeOp.INT_ADD || opcode == PcodeOp.INT_SUB ||
            opcode == PcodeOp.INT_2COMP || opcode == PcodeOp.INT_MULT ||
            opcode == PcodeOp.INT_LEFT || opcode == PcodeOp.PTRADD || opcode == PcodeOp.PTRSUB;
    }

    private Expr multiply(Expr a, Expr b) {
        if (!a.known || !b.known) return Expr.unknown();
        if (a.terms.isEmpty()) return b.scale(a.constant);
        if (b.terms.isEmpty()) return a.scale(b.constant);
        return Expr.unknown();
    }

    private Expr shiftLeft(Expr value, Expr shift) {
        if (!value.known || !shift.known || !shift.terms.isEmpty()) return Expr.unknown();
        if (shift.constant < 0 || shift.constant > 31) return Expr.unknown();
        return value.scale(1L << shift.constant);
    }

    private void processLoad(Instruction instruction, State state, PcodeOp op) {
        Varnode output = op.getOutput();
        if (output == null) return;
        Expr address = valueOf(state, op.getInput(1), instruction.getAddress());
        String stackKey = stackKey(address);
        if (stackKey != null && state.stack.containsKey(stackKey)) {
            Expr restored = state.stack.get(stackKey).copy();
            restored.flags.add("LOCAL_RELOAD");
            restored.note(String.format("0x%08x %s -> reload %s", instruction.getAddress().getOffset(),
                instruction.toString(), restored.format()));
            state.values.put(output, restored);
            return;
        }

        Expr loaded = Expr.root(String.format("load@0x%08x[%s]", instruction.getAddress().getOffset(),
            address.format()));
        loaded.note(String.format("0x%08x %s -> %s", instruction.getAddress().getOffset(),
            instruction.toString(), loaded.format()));
        state.values.put(output, loaded);
    }

    private void processStore(Instruction instruction, boolean pseudo, State state,
            Map<Varnode, Expr> before, PcodeOp op) {
        counts.stores++;
        Expr address = valueOf(state, op.getInput(1), instruction.getAddress());
        Expr stored = valueOf(state, op.getInput(2), instruction.getAddress());
        String stackKey = stackKey(address);
        if (stackKey != null) {
            if (stored.known) state.stack.put(stackKey, stored.copy());
            else state.stack.remove(stackKey);
        }

        if (!address.known || isStackOnly(address) || !targets.contains(address.offset32())) return;
        Hit hit = new Hit();
        hit.address = instruction.getAddress();
        hit.blockStart = state.blockStart;
        hit.target = address.offset32();
        hit.pseudo = pseudo;
        Function function = functions.getFunctionContaining(instruction.getAddress());
        hit.function = function == null ? "<no_function>" :
            String.format("%s @ 0x%08x", function.getName(), function.getEntryPoint().getOffset());
        hit.instruction = instruction.toString();
        hit.expression = address.format();
        hit.registerProvenance = formatRegisterProvenance(instruction, before, state.blockStart);
        hit.nearestDefinedInstruction = formatNearestDefinedInstruction(instruction.getAddress());
        hit.blockPrefix = new ArrayList<>(state.history);
        hit.blockPrefix.add(String.format("0x%08x %s", instruction.getAddress().getOffset(),
            instruction.toString()));
        hit.forms = classify(instruction, address);
        hit.trace = new ArrayList<>(address.trace);
        hits.add(hit);
    }

    private List<String> classify(Instruction instruction, Expr address) {
        ArrayList<String> forms = new ArrayList<>();
        if (hasLiteralTarget(instruction)) forms.add("DIRECT_LITERAL");
        if (address.flags.contains("INDEXED") || address.terms.size() > 1) forms.add("INDEXED");
        if (address.flags.contains("LOCAL_RELOAD")) forms.add("LOCAL_RELOAD");
        boolean earlier = false;
        String current = String.format("0x%08x", instruction.getAddress().getOffset());
        for (String trace : address.trace) {
            if (!trace.startsWith(current)) {
                earlier = true;
                break;
            }
        }
        if (earlier) forms.add("PROPAGATED");
        if (forms.isEmpty()) forms.add("PCODE_EFFECTIVE_ADDRESS");
        return forms;
    }

    private boolean hasLiteralTarget(Instruction instruction) {
        for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Scalar) {
                    long value = ((Scalar) object).getUnsignedValue() & MASK32;
                    if (targets.contains(value)) return true;
                }
            }
        }
        return false;
    }

    private String formatRegisterProvenance(Instruction instruction, Map<Varnode, Expr> before,
            Address blockStart) {
        LinkedHashSet<String> names = new LinkedHashSet<>();
        int operandCount = instruction.getNumOperands();
        for (int operand = 0; operand < operandCount; operand++) {
            for (Object object : instruction.getOpObjects(operand)) {
                if (object instanceof Register) {
                    Register register = ((Register) object).getBaseRegister();
                    if (isAddressRegister(register)) names.add(register.getName().toUpperCase(Locale.ROOT));
                }
            }
        }

        ArrayList<String> values = new ArrayList<>();
        for (String name : names) {
            Expr value = findRegisterValue(before, name);
            if (value == null) value = Expr.root(name + "@0x" + blockStart);
            values.add(name + "=" + value.format());
        }
        return values.isEmpty() ? "<no explicit address register>" : String.join("; ", values);
    }

    private Expr findRegisterValue(Map<Varnode, Expr> values, String name) {
        for (Map.Entry<Varnode, Expr> entry : values.entrySet()) {
            Varnode node = entry.getKey();
            if (!node.isRegister()) continue;
            Register register = currentProgram.getRegister(node);
            if (register != null && register.getBaseRegister().getName().equalsIgnoreCase(name)) {
                return entry.getValue();
            }
        }
        return null;
    }

    private boolean isAddressRegister(Register register) {
        if (register == null || register.isProcessorContext() || register.isProgramCounter()) return false;
        String name = register.getName().toUpperCase(Locale.ROOT);
        return !name.equals("EFLAGS") && !name.startsWith("XMM") && !name.startsWith("YMM") &&
            !name.startsWith("ZMM") && !name.startsWith("ST");
    }

    private String formatNearestDefinedInstruction(Address address) {
        Instruction previous = listing.getInstructionBefore(address);
        if (previous == null) return "<none>";
        Function function = functions.getFunctionContaining(previous.getAddress());
        String owner = function == null ? "<no_function>" :
            String.format("%s @ 0x%08x", function.getName(), function.getEntryPoint().getOffset());
        return String.format("0x%08x %s; distance=%d; function=%s",
            previous.getAddress().getOffset(), previous.toString(),
            address.subtract(previous.getMaxAddress()) - 1, owner);
    }

    private Expr valueOf(State state, Varnode node, Address instructionAddress) {
        if (node == null) return Expr.unknown();
        if (node.isConstant()) return Expr.constant(signedConstant(node));
        Expr known = state.values.get(node);
        if (known != null) return known.copy();
        if (node.isRegister()) {
            Register register = currentProgram.getRegister(node);
            if (register == null) return Expr.unknown();
            Register base = register.getBaseRegister();
            if (!isAddressRegister(base)) return Expr.unknown();
            return Expr.root(base.getName().toUpperCase(Locale.ROOT) + "@0x" + state.blockStart);
        }
        if (node.isAddress()) return Expr.constant(node.getOffset());
        return Expr.unknown();
    }

    private long signedConstant(Varnode node) {
        long value = node.getOffset();
        int bits = node.getSize() * 8;
        if (bits >= 64) return value;
        long mask = (1L << bits) - 1;
        value &= mask;
        long sign = 1L << (bits - 1);
        return (value & sign) == 0 ? value : value | ~mask;
    }

    private String stackKey(Expr address) {
        if (!address.known || address.terms.size() != 1) return null;
        Map.Entry<String, Long> term = address.terms.firstEntry();
        if (term.getValue() != 1) return null;
        String root = term.getKey().toUpperCase(Locale.ROOT);
        if (!root.startsWith("ESP@") && !root.startsWith("EBP@")) return null;
        return root + String.format("%+d", address.constant);
    }

    private boolean isStackOnly(Expr address) {
        if (!address.known || address.terms.isEmpty()) return false;
        for (String root : address.terms.keySet()) {
            String upper = root.toUpperCase(Locale.ROOT);
            if (!upper.startsWith("ESP@") && !upper.startsWith("EBP@")) return false;
        }
        return true;
    }

    private void writeReport(String outPath, String offsetArg, boolean complete,
            String incompleteReason) throws IOException {
        Collections.sort(hits, Comparator.comparingLong(hit -> hit.address.getOffset()));
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outPath))) {
            line(writer, "======================================================================");
            line(writer, "Compound offset writer scan");
            line(writer, "Program: " + currentProgram.getName());
            line(writer, "Offsets: " + offsetArg);
            line(writer, "Coverage: defined instructions plus read-only pseudo-disassembly of");
            line(writer, "undefined bytes in executable ranges; state resets at basic-block,");
            line(writer, "call, branch, terminal-flow, data, and decode-failure boundaries.");
            line(writer, "Provenance: affine register arithmetic and exact stack-local spills");
            line(writer, "and reloads within one block. Pseudo hits are explicitly labeled.");
            line(writer, "======================================================================");
            line(writer, String.format("Defined instructions swept: %d", counts.definedInstructions));
            line(writer, String.format("Pseudo instructions swept: %d", counts.pseudoInstructions));
            line(writer, String.format("Total instructions swept: %d",
                counts.definedInstructions + counts.pseudoInstructions));
            line(writer, String.format("Stores evaluated: %d", counts.stores));
            line(writer, String.format("Basic-block states: %d", counts.blocks));
            line(writer, String.format("Defined data bytes skipped: %d", counts.definedDataBytes));
            line(writer, String.format("Undefined bytes skipped after decode failure: %d",
                counts.undefinedBytesSkipped));
            line(writer, String.format("Pseudo decode failures: %d", counts.pseudoFailures));
            line(writer, String.format("Hits: %d", hits.size()));
            line(writer, "Hit forms: " + formatFormCounts());

            for (Hit hit : hits) {
                line(writer, "");
                line(writer, "----------------------------------------------------------------------");
                line(writer, String.format("Hit 0x%08x target=0x%x origin=%s forms=%s",
                    hit.address.getOffset(), hit.target, hit.pseudo ? "UNDEFINED_PSEUDO" : "DEFINED",
                    String.join(",", hit.forms)));
                line(writer, "Function: " + hit.function);
                line(writer, String.format("Block start: 0x%08x", hit.blockStart.getOffset()));
                line(writer, "Instruction: " + hit.instruction);
                line(writer, "Effective address: " + hit.expression);
                line(writer, "Register provenance: " + hit.registerProvenance);
                if (hit.pseudo) {
                    line(writer, "Nearest prior defined instruction: " + hit.nearestDefinedInstruction);
                    line(writer, "Pseudo block prefix:");
                    for (String prefix : hit.blockPrefix) line(writer, "  " + prefix);
                }
                line(writer, "Trace:");
                if (hit.trace.isEmpty()) line(writer, "  <direct p-code expression>");
                else for (String trace : hit.trace) line(writer, "  " + trace);
            }

            line(writer, "");
            if (complete) {
                line(writer, String.format("COMPLETE: swept %d instructions and evaluated %d stores",
                    counts.definedInstructions + counts.pseudoInstructions, counts.stores));
            }
            else {
                line(writer, "INCOMPLETE: " + incompleteReason);
            }
        }
    }

    private String formatFormCounts() {
        TreeMap<String, Integer> formCounts = new TreeMap<>();
        for (Hit hit : hits) {
            for (String form : hit.forms) {
                formCounts.put(form, formCounts.getOrDefault(form, 0) + 1);
            }
        }
        if (formCounts.isEmpty()) return "none";
        ArrayList<String> values = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : formCounts.entrySet()) {
            values.add(entry.getKey() + "=" + entry.getValue());
        }
        return String.join(", ", values);
    }

    private void line(BufferedWriter writer, String text) throws IOException {
        writer.write(text);
        writer.newLine();
    }

    private static void appendTrace(List<String> destination, List<String> source) {
        for (String line : source) {
            if (destination.size() == MAX_TRACE) destination.remove(0);
            destination.add(line);
        }
    }
}
