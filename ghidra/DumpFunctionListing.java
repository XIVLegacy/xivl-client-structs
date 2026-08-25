// Ghidra post-script. Dumps instruction listings for explicit function VAs.
// Inputs: XIVL_TARGET_VAS (comma-separated VAs), XIVL_DUMP_PATH (output).
// Run with tools/ghidra/run-headless.ps1 -ReadOnly.
//@category XIVLegacy

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

public class DumpFunctionListing extends GhidraScript {
    @Override
    public void run() throws Exception {
        String targets = System.getenv("XIVL_TARGET_VAS");
        if (targets == null || targets.trim().isEmpty()) {
            throw new IllegalArgumentException("XIVL_TARGET_VAS is required");
        }
        String output = System.getenv("XIVL_DUMP_PATH");
        if (output == null || output.trim().isEmpty()) {
            output = new File(System.getProperty("user.dir"), "listing.txt").getAbsolutePath();
        }

        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        FunctionManager functions = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        int requested = 0;
        int completed = 0;

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(output))) {
            line(writer, "XIVLegacy function listing");
            line(writer, "Targets: " + targets);
            for (String token : targets.split(",")) {
                String value = token.trim();
                if (value.isEmpty()) continue;
                requested++;
                long va = Long.decode(value);
                Address address = space.getAddress(va);
                Function function = functions.getFunctionAt(address);
                line(writer, "");
                line(writer, String.format("VA 0x%08X", va));
                if (function == null) {
                    line(writer, "ERROR: no function starts at target");
                    continue;
                }
                line(writer, "Name: " + function.getName());
                InstructionIterator instructions = listing.getInstructions(function.getBody(), true);
                while (instructions.hasNext()) {
                    Instruction instruction = instructions.next();
                    line(writer, String.format("0x%08X  %s", instruction.getAddress().getOffset(), instruction));
                }
                completed++;
            }
            if (completed != requested) {
                line(writer, String.format("INCOMPLETE: requested=%d completed=%d", requested, completed));
                throw new IllegalStateException("one or more target functions were unavailable");
            }
            line(writer, String.format("COMPLETE: requested=%d completed=%d", requested, completed));
        }
        println("WROTE: " + output);
    }

    private void line(BufferedWriter writer, String value) throws IOException {
        writer.write(value);
        writer.newLine();
    }
}
