// Verifies the fixed actor-rebuild receiver-field pilot.
//
// This script intentionally inspects only the listed functions, instructions,
// and call targets. It never invokes the decompiler and emits no disassembly,
// bytes, paths, or symbol names.
//
// Env vars:
//   XIVL_RETAIL_OBSERVATIONS_OUT  required JSON output path
//@category XIVLegacy

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.Locale;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.CompilerSpec;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.util.GhidraProgramUtilities;

public class VerifyActorRebuild extends GhidraScript {

    private static final String CHECK_ID = "actor-rebuild-receiver-field-v1";
    private static final String PROGRAM_NAME = "ffxivgame.exe";
    private static final long IMAGE_BASE = 0x00400000L;
    private static final String LANGUAGE_ID = "x86:LE:32:default";
    private static final String COMPILER_SPEC_ID = "windows";
    private static final long FIELD_DISPLACEMENT = 0x92L;

    private enum Kind {
        WRITE,
        COMPARE,
        CALL
    }

    private static final class ObservationSpec {
        final Kind kind;
        final long instruction;
        final long owner;
        final int immediate;
        final long target;

        private ObservationSpec(Kind kind, long instruction, long owner,
                                int immediate, long target) {
            this.kind = kind;
            this.instruction = instruction;
            this.owner = owner;
            this.immediate = immediate;
            this.target = target;
        }

        static ObservationSpec write(long instruction, long owner, int immediate) {
            return new ObservationSpec(Kind.WRITE, instruction, owner, immediate, 0L);
        }

        static ObservationSpec compare(long instruction, long owner, int immediate) {
            return new ObservationSpec(Kind.COMPARE, instruction, owner, immediate, 0L);
        }

        static ObservationSpec call(long instruction, long owner, long target) {
            return new ObservationSpec(Kind.CALL, instruction, owner, 0, target);
        }
    }

    private static final ObservationSpec[] EXPECTED = {
        ObservationSpec.write(0x004DCCDDL, 0x004DC690L, 1),
        ObservationSpec.compare(0x004D8863L, 0x004D8860L, 0),
        ObservationSpec.call(0x004D88ABL, 0x004D8860L, 0x00575860L),
        ObservationSpec.write(0x004D88B0L, 0x004D8860L, 0),
        ObservationSpec.write(0x004D88EAL, 0x004D8860L, 0),
        ObservationSpec.call(0x004D8902L, 0x004D8860L, 0x00574780L),
        ObservationSpec.call(0x005747FBL, 0x00574780L, 0x00774AD0L),
        ObservationSpec.call(0x005758C4L, 0x00575860L, 0x00764630L)
    };

    @Override
    public void run() throws Exception {
        String outPath = requireOutputPath();
        checkNotCancelled();
        validateProgram();
        checkNotCancelled();

        for (ObservationSpec expected : EXPECTED) {
            checkNotCancelled();
            validateObservation(expected);
        }

        checkNotCancelled();
        String json = buildJson();
        checkNotCancelled();
        writeAtomically(outPath, json);
        println("COMPLETE: " + CHECK_ID);
    }

    private String requireOutputPath() {
        String outPath = System.getenv("XIVL_RETAIL_OBSERVATIONS_OUT");
        if (outPath == null || outPath.trim().isEmpty()) {
            throw new IllegalArgumentException("XIVL_RETAIL_OBSERVATIONS_OUT is required");
        }
        return outPath;
    }

    private void validateProgram() {
        require(currentProgram != null, "program unavailable");
        require(PROGRAM_NAME.equals(currentProgram.getName()), "program identity mismatch");
        require(currentProgram.getImageBase() != null &&
                currentProgram.getImageBase().getOffset() == IMAGE_BASE,
                "image base mismatch");
        require(currentProgram.getLanguageID() != null &&
                LANGUAGE_ID.equals(currentProgram.getLanguageID().getIdAsString()),
                "language mismatch");

        CompilerSpec compilerSpec = currentProgram.getCompilerSpec();
        require(compilerSpec != null && compilerSpec.getCompilerSpecID() != null &&
                COMPILER_SPEC_ID.equals(compilerSpec.getCompilerSpecID().getIdAsString()),
                "compiler spec mismatch");
        require(GhidraProgramUtilities.isAnalyzed(currentProgram),
                "analysis incomplete");
    }

    private void validateObservation(ObservationSpec expected) {
        Instruction instruction = validateOwnership(expected.instruction, expected.owner);
        if (expected.kind == Kind.CALL) {
            validateDirectCall(instruction, expected.target);
        }
        else if (expected.kind == Kind.WRITE) {
            validateFieldWrite(instruction, expected.immediate);
        }
        else {
            validateFieldCompare(instruction, expected.immediate);
        }
    }

    private Instruction validateOwnership(long instructionVa, long ownerVa) {
        Address instructionAddress = address(instructionVa);
        Address ownerAddress = address(ownerVa);
        Listing listing = currentProgram.getListing();
        FunctionManager functions = currentProgram.getFunctionManager();
        Instruction instruction = listing.getInstructionAt(instructionAddress);
        require(instruction != null, "fixed instruction missing");

        Function containing = functions.getFunctionContaining(instructionAddress);
        require(containing != null && containing.getEntryPoint().equals(ownerAddress),
                "fixed instruction ownership mismatch");
        Function entry = functions.getFunctionAt(ownerAddress);
        require(entry != null && entry.getEntryPoint().equals(ownerAddress),
                "fixed owner missing");
        return instruction;
    }

    private void validateFieldWrite(Instruction instruction, int immediate) {
        require("MOV".equalsIgnoreCase(instruction.getMnemonicString()),
                "fixed write mnemonic mismatch");
        require(instruction.getNumOperands() == 2, "fixed write operand count mismatch");
        validateFieldOperand(instruction, 0, true);
        validateImmediate(instruction, 1, immediate);
    }

    private void validateFieldCompare(Instruction instruction, int immediate) {
        require("CMP".equalsIgnoreCase(instruction.getMnemonicString()),
                "fixed compare mnemonic mismatch");
        require(instruction.getNumOperands() == 2, "fixed compare operand count mismatch");
        validateFieldOperand(instruction, 0, false);
        validateImmediate(instruction, 1, immediate);
    }

    private void validateFieldOperand(Instruction instruction, int operandIndex,
                                      boolean write) {
        validatePcodeMemoryWidth(instruction, write);

        int registers = 0;
        int displacements = 0;
        for (Object object : instruction.getOpObjects(operandIndex)) {
            if (object instanceof ghidra.program.model.lang.Register) {
                registers++;
            }
            else if (object instanceof Scalar) {
                Scalar scalar = (Scalar) object;
                if (scalar.getUnsignedValue() == FIELD_DISPLACEMENT) {
                    displacements++;
                }
                else {
                    throw new IllegalStateException("field displacement mismatch");
                }
            }
            else {
                throw new IllegalStateException("field operand object mismatch");
            }
        }
        require(registers == 1 && displacements == 1,
                "field operand shape mismatch");
    }

    private void validatePcodeMemoryWidth(Instruction instruction, boolean write) {
        int memoryOperations = 0;
        for (PcodeOp operation : instruction.getPcode()) {
            if (write && operation.getOpcode() == PcodeOp.STORE) {
                require(operation.getNumInputs() == 3 && operation.getInput(2) != null &&
                        operation.getInput(2).getSize() == 1,
                        "field write width mismatch");
                memoryOperations++;
            }
            else if (!write && operation.getOpcode() == PcodeOp.LOAD) {
                require(operation.getOutput() != null && operation.getOutput().getSize() == 1,
                        "field compare width mismatch");
                memoryOperations++;
            }
        }
        require(memoryOperations == 1, "field memory operation count mismatch");
    }

    private void validateImmediate(Instruction instruction, int operandIndex, int expected) {
        int scalars = 0;
        for (Object object : instruction.getOpObjects(operandIndex)) {
            require(object instanceof Scalar, "immediate operand object mismatch");
            Scalar scalar = (Scalar) object;
            require(scalar.getUnsignedValue() == expected, "immediate value mismatch");
            scalars++;
        }
        require(scalars == 1, "immediate operand shape mismatch");
    }

    private void validateDirectCall(Instruction instruction, long targetVa) {
        require("CALL".equalsIgnoreCase(instruction.getMnemonicString()),
                "fixed call mnemonic mismatch");
        require(instruction.getNumOperands() == 1, "fixed call operand count mismatch");
        require(instruction.getFlowType() != null && instruction.getFlowType().isCall(),
                "fixed call flow mismatch");

        RefType operandRefType = instruction.getOperandRefType(0);
        require(operandRefType != null && operandRefType.isCall() &&
                !operandRefType.isIndirect(), "fixed call is not direct");

        Address target = address(targetVa);
        ReferenceManager references = currentProgram.getReferenceManager();
        int directCallReferences = 0;
        for (Reference reference : references.getReferencesFrom(instruction.getAddress())) {
            RefType referenceType = reference.getReferenceType();
            if (!referenceType.isCall()) {
                continue;
            }
            require(!referenceType.isIndirect() && reference.getOperandIndex() == 0,
                    "fixed call reference is not direct");
            directCallReferences++;
            require(reference.getToAddress().equals(target), "fixed call target mismatch");
        }
        require(directCallReferences == 1, "fixed call reference count mismatch");
    }

    private Address address(long va) {
        AddressSpace defaultSpace = currentProgram.getAddressFactory().getDefaultAddressSpace();
        return defaultSpace.getAddress(va);
    }

    private void checkNotCancelled() {
        if (monitor.isCancelled()) {
            throw new IllegalStateException("cancelled");
        }
    }

    private static void require(boolean condition, String reason) {
        if (!condition) {
            throw new IllegalStateException(reason);
        }
    }

    private String buildJson() {
        StringBuilder json = new StringBuilder(2048);
        json.append("{\n");
        json.append("  \"check\": \"").append(CHECK_ID).append("\",\n");
        json.append("  \"program\": \"").append(PROGRAM_NAME).append("\",\n");
        json.append("  \"image_base\": \"").append(hex(IMAGE_BASE)).append("\",\n");
        json.append("  \"language\": \"").append(LANGUAGE_ID).append("\",\n");
        json.append("  \"compiler_spec\": \"").append(COMPILER_SPEC_ID).append("\",\n");
        json.append("  \"analysis_complete\": true,\n");
        json.append("  \"observations\": [\n");
        for (int i = 0; i < EXPECTED.length; i++) {
            if (i != 0) {
                json.append(",\n");
            }
            appendObservation(json, EXPECTED[i]);
        }
        json.append("\n  ],\n");
        json.append("  \"complete\": true,\n");
        json.append("  \"completion_marker\": \"complete\"\n");
        json.append("}\n");
        return json.toString();
    }

    private static void appendObservation(StringBuilder json, ObservationSpec observation) {
        json.append("    {\n");
        json.append("      \"kind\": \"").append(observation.kind.name().toLowerCase(Locale.ROOT))
            .append("\",\n");
        json.append("      \"instruction_va\": \"").append(hex(observation.instruction))
            .append("\",\n");
        json.append("      \"owner_va\": \"").append(hex(observation.owner)).append("\"");
        if (observation.kind == Kind.CALL) {
            json.append(",\n      \"target_va\": \"").append(hex(observation.target)).append("\"\n");
        }
        else {
            json.append(",\n      \"width\": \"byte\",\n");
            json.append("      \"displacement\": \"").append(hex(FIELD_DISPLACEMENT)).append("\",\n");
            json.append("      \"immediate\": ").append(observation.immediate).append("\n");
        }
        json.append("    }");
    }

    private static String hex(long value) {
        return String.format(Locale.ROOT, "0x%08X", value);
    }

    private void writeAtomically(String outPath, String json) throws IOException {
        Path output = Paths.get(outPath).toAbsolutePath();
        Path parent = output.getParent();
        if (parent == null) {
            throw new IOException("output parent unavailable");
        }

        Path temporary = Files.createTempFile(parent, ".actor-rebuild-", ".tmp");
        boolean installed = false;
        try {
            try (BufferedWriter writer = Files.newBufferedWriter(
                    temporary, StandardCharsets.UTF_8,
                    StandardOpenOption.WRITE, StandardOpenOption.TRUNCATE_EXISTING)) {
                writer.write(json);
            }
            checkNotCancelled();
            try {
                Files.move(temporary, output, StandardCopyOption.ATOMIC_MOVE,
                           StandardCopyOption.REPLACE_EXISTING);
            }
            catch (AtomicMoveNotSupportedException exception) {
                throw new IOException("atomic output unavailable");
            }
            installed = true;
        }
        finally {
            if (!installed) {
                Files.deleteIfExists(temporary);
            }
        }
    }
}
