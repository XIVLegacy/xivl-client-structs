// Exports every reference Ghidra analysis recorded to target addresses or
// matching defined strings. Computed, indirect, dynamically dispatched, and
// unanalyzed-region references may be absent from the reference database.
//
// Env vars:
//   XIVL_REFERENCE_MODE       (ADDRESS or STRING, required)
//   XIVL_REFERENCE_ADDRESSES  (comma-separated VAs, required in ADDRESS mode)
//   XIVL_REFERENCE_STRINGS    (newline-separated literals, required in STRING mode)
//   XIVL_STRING_MATCH         (EXACT or SUBSTRING, default EXACT in STRING mode)
//   XIVL_DUMP_PATH            (explicit output path, required)
//@category XIVLegacy

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class FindReferences extends GhidraScript {
    private enum Mode { ADDRESS, STRING }
    private enum StringMatch { EXACT, SUBSTRING }

    private static class ReferenceHit {
        Address from;
        String owner;
        String type;
    }

    private static class AddressResult {
        Address target;
        String mappedSection;
        List<ReferenceHit> references = new ArrayList<>();
    }

    private static class StringResult {
        String query;
        List<StringAddressResult> matches = new ArrayList<>();
    }

    private static class StringAddressResult {
        AddressResult addressResult;
        String value;
        String dataType;
    }

    private Mode mode;
    private StringMatch stringMatch;
    private String rawAddresses;
    private String rawStrings;
    private Listing listing;
    private FunctionManager functions;
    private ReferenceManager references;
    private final List<AddressResult> addressResults = new ArrayList<>();
    private final List<StringResult> stringResults = new ArrayList<>();
    private long definedStringsScanned;

    @Override
    public void run() throws Exception {
        String outPath = requireEnv("XIVL_DUMP_PATH");
        boolean complete = false;
        String incompleteReason = "unknown failure";

        try {
            mode = parseMode(requireEnv("XIVL_REFERENCE_MODE"));
            listing = currentProgram.getListing();
            functions = currentProgram.getFunctionManager();
            references = currentProgram.getReferenceManager();

            if (mode == Mode.ADDRESS) runAddressMode();
            else runStringMode();

            if (monitor.isCancelled()) incompleteReason = "cancelled during reference export";
            else complete = true;
        }
        catch (Exception e) {
            incompleteReason = describeFailure(e);
            throw e;
        }
        finally {
            writeReport(outPath, complete, incompleteReason);
        }

        if (complete) println("COMPLETE: FindReferences " + outPath);
        else println("INCOMPLETE: FindReferences " + incompleteReason);
    }

    private void runAddressMode() {
        rawAddresses = requireEnv("XIVL_REFERENCE_ADDRESSES");
        for (Address target : parseAddresses(rawAddresses)) {
            if (monitor.isCancelled()) return;
            addressResults.add(inspectAddress(target));
        }
    }

    private void runStringMode() {
        rawStrings = requireRawEnv("XIVL_REFERENCE_STRINGS");
        stringMatch = parseStringMatch(System.getenv("XIVL_STRING_MATCH"));
        List<String> queries = parseStrings(rawStrings);
        for (String query : queries) {
            StringResult result = new StringResult();
            result.query = query;
            stringResults.add(result);
        }

        DataIterator iterator = listing.getDefinedData(true);
        while (iterator.hasNext()) {
            if (monitor.isCancelled()) return;
            Data data = iterator.next();
            if (!data.hasStringValue()) continue;
            Object valueObject = data.getValue();
            if (!(valueObject instanceof String)) continue;
            definedStringsScanned++;
            String value = (String) valueObject;

            for (StringResult result : stringResults) {
                if (!matches(value, result.query)) continue;
                StringAddressResult match = new StringAddressResult();
                match.addressResult = inspectAddress(data.getAddress());
                match.value = value;
                match.dataType = data.getDataType().getDisplayName();
                result.matches.add(match);
            }
        }
        for (StringResult result : stringResults) {
            result.matches.sort(Comparator.comparingLong(
                match -> match.addressResult.target.getOffset()));
        }
    }

    private AddressResult inspectAddress(Address target) {
        AddressResult result = new AddressResult();
        result.target = target;
        MemoryBlock targetBlock = currentProgram.getMemory().getBlock(target);
        result.mappedSection = targetBlock == null ? "<not mapped>" : targetBlock.getName();

        ReferenceIterator iterator = references.getReferencesTo(target);
        while (iterator.hasNext()) {
            if (monitor.isCancelled()) return result;
            Reference reference = iterator.next();
            ReferenceHit hit = new ReferenceHit();
            hit.from = reference.getFromAddress();
            hit.owner = ownerOf(hit.from);
            hit.type = reference.getReferenceType().toString();
            result.references.add(hit);
        }
        result.references.sort(Comparator
            .comparingLong((ReferenceHit hit) -> hit.from.getOffset())
            .thenComparing(hit -> hit.type));
        return result;
    }

    private String ownerOf(Address from) {
        Function function = functions.getFunctionContaining(from);
        if (function != null) {
            return String.format("function %s @ 0x%08x", function.getName(),
                function.getEntryPoint().getOffset());
        }
        MemoryBlock block = currentProgram.getMemory().getBlock(from);
        return block == null ? "section <not mapped>" : "section " + block.getName();
    }

    private boolean matches(String value, String query) {
        if (stringMatch == StringMatch.SUBSTRING) return value.contains(query);
        return value.equals(query);
    }

    private Mode parseMode(String value) {
        try {
            return Mode.valueOf(value.toUpperCase(Locale.ROOT));
        }
        catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("XIVL_REFERENCE_MODE must be ADDRESS or STRING");
        }
    }

    private StringMatch parseStringMatch(String value) {
        if (value == null || value.trim().isEmpty()) return StringMatch.EXACT;
        try {
            return StringMatch.valueOf(value.trim().toUpperCase(Locale.ROOT));
        }
        catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("XIVL_STRING_MATCH must be EXACT or SUBSTRING");
        }
    }

    private List<Address> parseAddresses(String text) {
        Set<Address> result = new LinkedHashSet<>();
        for (String token : text.split(",")) {
            String value = token.trim();
            if (value.isEmpty()) continue;
            if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
            long offset = Long.parseUnsignedLong(value, 16);
            result.add(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset));
        }
        if (result.isEmpty()) {
            throw new IllegalArgumentException("XIVL_REFERENCE_ADDRESSES contained no addresses");
        }
        return new ArrayList<>(result);
    }

    private List<String> parseStrings(String text) {
        Set<String> result = new LinkedHashSet<>();
        for (String line : text.split("\\R", -1)) {
            if (!line.isEmpty()) result.add(line);
        }
        if (result.isEmpty()) {
            throw new IllegalArgumentException("XIVL_REFERENCE_STRINGS contained no strings");
        }
        return new ArrayList<>(result);
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException("Set " + name + " to an explicit value");
        }
        return value.trim();
    }

    private String requireRawEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isEmpty()) {
            throw new IllegalArgumentException("Set " + name + " to an explicit value");
        }
        return value;
    }

    private String describeFailure(Exception e) {
        String message = e.getMessage();
        if (message == null || message.isEmpty()) return e.getClass().getSimpleName();
        return e.getClass().getSimpleName() + ": " + message;
    }

    private void writeReport(String outPath, boolean complete, String incompleteReason)
            throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outPath))) {
            line(writer, "======================================================================");
            line(writer, "Reference database export");
            line(writer, "Program: " + currentProgram.getName());
            line(writer, "Mode: " + (mode == null ? "<unresolved>" : mode));
            line(writer, "Coverage: every reference recorded by Ghidra analysis to each resolved target.");
            line(writer, "Limit: directly encoded references are complete only when analysis covered the");
            line(writer, "relevant bytes. Computed, indirect, dynamically dispatched, or unanalyzed-region");
            line(writer, "references can be absent. Zero proves no directly encoded reference recorded by");
            line(writer, "this analyzed database, not an absolute absence of runtime references.");
            line(writer, "======================================================================");

            if (mode == Mode.ADDRESS) writeAddressReport(writer);
            else if (mode == Mode.STRING) writeStringReport(writer);

            line(writer, "");
            if (complete) line(writer, completionSummary());
            else line(writer, "INCOMPLETE: " + incompleteReason);
        }
    }

    private void writeAddressReport(BufferedWriter writer) throws IOException {
        line(writer, "Address inputs: " + rawAddresses);
        line(writer, "Targets processed: " + addressResults.size());
        for (AddressResult result : addressResults) writeAddressResult(writer, result, "TARGET");
    }

    private void writeStringReport(BufferedWriter writer) throws IOException {
        line(writer, "String match: " + stringMatch);
        line(writer, "String queries: " + stringResults.size());
        line(writer, "Defined strings scanned: " + definedStringsScanned);
        for (StringResult result : stringResults) {
            line(writer, "");
            line(writer, "----------------------------------------------------------------------");
            line(writer, "STRING QUERY: " + quote(result.query));
            line(writer, "Defined-data matches: " + result.matches.size());
            if (result.matches.isEmpty()) {
                line(writer, "OUTCOME: no defined-string data matched");
                continue;
            }
            int index = 0;
            for (StringAddressResult match : result.matches) {
                index++;
                line(writer, String.format("MATCH %d: 0x%08x section=%s type=%s value=%s", index,
                    match.addressResult.target.getOffset(), match.addressResult.mappedSection,
                    match.dataType, quote(match.value)));
                writeReferences(writer, match.addressResult.references);
            }
        }
    }

    private void writeAddressResult(BufferedWriter writer, AddressResult result, String label)
            throws IOException {
        line(writer, "");
        line(writer, "----------------------------------------------------------------------");
        line(writer, String.format("%s ADDRESS: 0x%08x", label, result.target.getOffset()));
        line(writer, "Target section: " + result.mappedSection);
        writeReferences(writer, result.references);
    }

    private void writeReferences(BufferedWriter writer, List<ReferenceHit> hits) throws IOException {
        line(writer, "References to target: " + hits.size());
        if (hits.isEmpty()) line(writer, "OUTCOME: target resolved with zero recorded references");
        for (ReferenceHit hit : hits) {
            line(writer, String.format("REF from=0x%08x owner=%s type=%s",
                hit.from.getOffset(), hit.owner, hit.type));
        }
    }

    private String completionSummary() {
        if (mode == Mode.ADDRESS) {
            long count = 0;
            for (AddressResult result : addressResults) count += result.references.size();
            return String.format("COMPLETE: processed %d address targets and %d references",
                addressResults.size(), count);
        }
        long matches = 0;
        long refs = 0;
        for (StringResult result : stringResults) {
            matches += result.matches.size();
            for (StringAddressResult match : result.matches) {
                refs += match.addressResult.references.size();
            }
        }
        return String.format(
            "COMPLETE: scanned %d defined strings for %d queries; %d matches and %d references",
            definedStringsScanned, stringResults.size(), matches, refs);
    }

    private String quote(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\r", "\\r").replace("\n", "\\n") + "\"";
    }

    private void line(BufferedWriter writer, String text) throws IOException {
        writer.write(text);
        writer.newLine();
    }
}
