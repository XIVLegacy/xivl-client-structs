// Exports every Ghidra-recorded reference to explicit addresses or defined
// strings. Use tools/ghidra/export-references.ps1 so the run is read-only and
// the completed report is independently verified.
//
// Env vars:
//   XIVL_REFERENCE_MODE            ADDRESS or STRING, required
//   XIVL_REFERENCE_ADDRESSES       comma-separated VAs, ADDRESS mode only
//   XIVL_REFERENCE_STRINGS         newline-separated literals, STRING mode only
//   XIVL_STRING_MATCH              EXACT or SUBSTRING, default EXACT
//   XIVL_REFERENCE_MAX_MATCHES     1..4096 aggregate, default 4096
//   XIVL_REFERENCE_MAX_REFERENCES  1..100000 aggregate, default 100000
//   XIVL_DUMP_PATH                 new explicit output path, required
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
import ghidra.util.exception.CancelledException;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;

public class FindReferences extends GhidraScript {
    private static final int MAX_TARGETS = 256;
    private static final int MAX_QUERIES = 256;
    private static final int HARD_MAX_MATCHES = 4096;
    private static final int HARD_MAX_REFERENCES = 100000;

    private enum Mode { ADDRESS, STRING }
    private enum StringMatch { EXACT, SUBSTRING }
    private enum Status { COMPLETE, CANCELLED, PARTIAL, FAILED }

    private static final class PartialExportException extends Exception {
        PartialExportException(String message) { super(message); }
    }

    private static final class ReferenceHit {
        Address from;
        int operandIndex;
        String owner;
        String type;
        String source;
        boolean primary;
    }

    private static final class AddressResult {
        Address target;
        String mappedSection;
        List<ReferenceHit> references = new ArrayList<>();
    }

    private static final class StringResult {
        String query;
        List<StringAddressResult> matches = new ArrayList<>();
    }

    private static final class StringAddressResult {
        AddressResult addressResult;
        String value;
        String dataType;
    }

    private Mode mode;
    private StringMatch stringMatch;
    private String rawAddresses;
    private Listing listing;
    private FunctionManager functions;
    private ReferenceManager references;
    private final List<AddressResult> addressResults = new ArrayList<>();
    private final List<StringResult> stringResults = new ArrayList<>();
    private long definedStringsScanned;
    private int totalMatches;
    private int totalReferences;
    private int maxMatches;
    private int maxReferences;

    @Override
    public void run() throws Exception {
        Path output = requireNewOutputPath();
        Status status = Status.FAILED;
        String detail = "initialization did not complete";

        try {
            mode = parseMode(requireEnv("XIVL_REFERENCE_MODE"));
            maxMatches = parseLimit("XIVL_REFERENCE_MAX_MATCHES",
                HARD_MAX_MATCHES, HARD_MAX_MATCHES);
            maxReferences = parseLimit("XIVL_REFERENCE_MAX_REFERENCES",
                HARD_MAX_REFERENCES, HARD_MAX_REFERENCES);
            listing = currentProgram.getListing();
            functions = currentProgram.getFunctionManager();
            references = currentProgram.getReferenceManager();

            if (mode == Mode.ADDRESS) runAddressMode();
            else runStringMode();

            monitor.checkCancelled();
            status = Status.COMPLETE;
            detail = completionSummary();
        }
        catch (CancelledException e) {
            status = Status.CANCELLED;
            detail = "monitor cancelled before the exhaustive walk completed";
            throw e;
        }
        catch (PartialExportException e) {
            status = Status.PARTIAL;
            detail = e.getMessage();
            throw e;
        }
        catch (Exception e) {
            status = Status.FAILED;
            detail = describeFailure(e);
            throw e;
        }
        finally {
            writeReportAtomically(output, status, detail);
        }

        println("COMPLETE: FindReferences " + output);
    }

    private void runAddressMode() throws Exception {
        rawAddresses = requireEnv("XIVL_REFERENCE_ADDRESSES");
        for (Address target : parseAddresses(rawAddresses)) {
            monitor.checkCancelled();
            addressResults.add(inspectAddress(target));
        }
    }

    private void runStringMode() throws Exception {
        String rawStrings = requireRawEnv("XIVL_REFERENCE_STRINGS");
        stringMatch = parseStringMatch(System.getenv("XIVL_STRING_MATCH"));
        for (String query : parseStrings(rawStrings)) {
            StringResult result = new StringResult();
            result.query = query;
            stringResults.add(result);
        }

        DataIterator iterator = listing.getDefinedData(true);
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Data data = iterator.next();
            if (!data.hasStringValue()) continue;
            Object valueObject = data.getValue();
            if (!(valueObject instanceof String)) continue;
            definedStringsScanned++;
            String value = (String) valueObject;

            for (StringResult result : stringResults) {
                if (!matches(value, result.query)) continue;
                if (totalMatches == maxMatches) {
                    throw new PartialExportException(String.format(
                        "export exceeded the %d-match aggregate limit; no negative is valid",
                        maxMatches));
                }
                StringAddressResult match = new StringAddressResult();
                match.addressResult = inspectAddress(data.getAddress());
                match.value = value;
                match.dataType = data.getDataType().getDisplayName();
                result.matches.add(match);
                totalMatches++;
            }
        }
        for (StringResult result : stringResults) {
            result.matches.sort(Comparator.comparingLong(
                match -> match.addressResult.target.getOffset()));
        }
    }

    private AddressResult inspectAddress(Address target) throws Exception {
        if (!currentProgram.getMemory().contains(target)) {
            throw new IllegalArgumentException(String.format(
                "target 0x%08x is outside program memory", target.getOffset()));
        }

        AddressResult result = new AddressResult();
        result.target = target;
        MemoryBlock targetBlock = currentProgram.getMemory().getBlock(target);
        result.mappedSection = targetBlock.getName();

        ReferenceIterator iterator = references.getReferencesTo(target);
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            if (totalReferences == maxReferences) {
                throw new PartialExportException(String.format(
                    "export exceeded the %d-reference aggregate limit; no negative is valid",
                    maxReferences));
            }
            Reference reference = iterator.next();
            ReferenceHit hit = new ReferenceHit();
            hit.from = reference.getFromAddress();
            hit.operandIndex = reference.getOperandIndex();
            hit.owner = ownerOf(hit.from);
            hit.type = reference.getReferenceType().toString();
            hit.source = reference.getSource().toString();
            hit.primary = reference.isPrimary();
            result.references.add(hit);
            totalReferences++;
        }
        result.references.sort(Comparator
            .comparingLong((ReferenceHit hit) -> hit.from.getOffset())
            .thenComparingInt(hit -> hit.operandIndex)
            .thenComparing(hit -> hit.type)
            .thenComparing(hit -> hit.source)
            .thenComparing(hit -> hit.primary));
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
        Set<Long> offsets = new TreeSet<>();
        int entries = 0;
        for (String token : text.split(",", -1)) {
            if (++entries > MAX_TARGETS) {
                throw new IllegalArgumentException("address target limit is " + MAX_TARGETS);
            }
            String value = token.trim();
            if (!value.matches("(?i)0x[0-9a-f]{1,16}")) {
                throw new IllegalArgumentException("invalid XIVL_REFERENCE_ADDRESSES entry");
            }
            offsets.add(Long.parseUnsignedLong(value.substring(2), 16));
        }
        List<Address> result = new ArrayList<>();
        for (long offset : offsets) {
            result.add(currentProgram.getAddressFactory().getDefaultAddressSpace()
                .getAddress(offset));
        }
        return result;
    }

    private List<String> parseStrings(String text) {
        Set<String> result = new TreeSet<>();
        int entries = 0;
        for (String line : text.split("\\r\\n|[\\r\\n]", -1)) {
            if (line.isEmpty()) continue;
            if (++entries > MAX_QUERIES) {
                throw new IllegalArgumentException("string query limit is " + MAX_QUERIES);
            }
            result.add(line);
        }
        if (result.isEmpty()) {
            throw new IllegalArgumentException("XIVL_REFERENCE_STRINGS contained no strings");
        }
        return new ArrayList<>(result);
    }

    private int parseLimit(String name, int defaultValue, int hardMaximum) {
        String source = System.getenv(name);
        if (source == null || source.trim().isEmpty()) return defaultValue;
        int value;
        try {
            value = Integer.parseInt(source.trim());
        }
        catch (NumberFormatException e) {
            throw new IllegalArgumentException(name + " must be a decimal integer");
        }
        if (value < 1 || value > hardMaximum) {
            throw new IllegalArgumentException(String.format(
                "%s must be between 1 and %d", name, hardMaximum));
        }
        return value;
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

    private Path requireNewOutputPath() throws IOException {
        String source = requireEnv("XIVL_DUMP_PATH");
        Path output = Paths.get(source).toAbsolutePath().normalize();
        Path parent = output.getParent();
        if (parent == null || !Files.isDirectory(parent)) {
            throw new IOException("output parent directory does not exist");
        }
        if (Files.exists(output)) {
            throw new IOException("output already exists");
        }
        return output;
    }

    private String describeFailure(Exception e) {
        String message = e.getMessage();
        if (message == null || message.isEmpty()) return e.getClass().getSimpleName();
        return e.getClass().getSimpleName() + ": " + message;
    }

    private void writeReportAtomically(Path output, Status status, String detail)
            throws IOException {
        Path parent = output.getParent();
        Path temporary = Files.createTempFile(parent,
            output.getFileName().toString() + ".", ".tmp");
        try {
            try (BufferedWriter writer = Files.newBufferedWriter(temporary,
                    StandardCharsets.UTF_8, StandardOpenOption.TRUNCATE_EXISTING)) {
                writeReport(writer, status, detail);
            }
            Files.move(temporary, output, StandardCopyOption.ATOMIC_MOVE);
        }
        finally {
            Files.deleteIfExists(temporary);
        }
    }

    private void writeReport(BufferedWriter writer, Status status, String detail)
            throws IOException {
        line(writer, "XIVL_REFERENCE_EXPORT_V1");
        line(writer, "Program: " + (currentProgram == null ? "<unavailable>" : currentProgram.getName()));
        line(writer, "Mode: " + (mode == null ? "<unresolved>" : mode));
        line(writer, "Coverage: every Ghidra-recorded reference to each resolved target");
        line(writer, "Limit: computed, indirect, dynamic, and unanalyzed references may be absent");

        if (mode == Mode.ADDRESS) writeAddressReport(writer);
        else if (mode == Mode.STRING) writeStringReport(writer);

        if (status == Status.COMPLETE) line(writer, "COMPLETE: FindReferences " + detail);
        else line(writer, "INCOMPLETE: " + status + " " + detail);
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
            line(writer, "STRING QUERY: " + quote(result.query));
            line(writer, "Defined-data matches: " + result.matches.size());
            for (StringAddressResult match : result.matches) {
                line(writer, String.format("MATCH: 0x%08x section=%s type=%s value=%s",
                    match.addressResult.target.getOffset(), match.addressResult.mappedSection,
                    match.dataType, quote(match.value)));
                writeReferences(writer, match.addressResult.references);
            }
        }
    }

    private void writeAddressResult(BufferedWriter writer, AddressResult result, String label)
            throws IOException {
        line(writer, String.format("%s ADDRESS: 0x%08x", label, result.target.getOffset()));
        line(writer, "Target section: " + result.mappedSection);
        writeReferences(writer, result.references);
    }

    private void writeReferences(BufferedWriter writer, List<ReferenceHit> hits) throws IOException {
        line(writer, "References to target: " + hits.size());
        for (ReferenceHit hit : hits) {
            line(writer, String.format(
                "REF from=0x%08x operand=%d type=%s source=%s primary=%s owner=%s",
                hit.from.getOffset(), hit.operandIndex, hit.type, hit.source,
                hit.primary, hit.owner));
        }
    }

    private String completionSummary() {
        if (mode == Mode.ADDRESS) {
            long count = 0;
            for (AddressResult result : addressResults) count += result.references.size();
            return String.format("targets=%d references=%d", addressResults.size(), count);
        }
        long matches = 0;
        long refs = 0;
        for (StringResult result : stringResults) {
            matches += result.matches.size();
            for (StringAddressResult match : result.matches) {
                refs += match.addressResult.references.size();
            }
        }
        return String.format("defined_strings=%d queries=%d matches=%d references=%d",
            definedStringsScanned, stringResults.size(), matches, refs);
    }

    private String quote(String value) {
        StringBuilder result = new StringBuilder("\"");
        for (int index = 0; index < value.length(); index++) {
            char character = value.charAt(index);
            switch (character) {
                case '\"': result.append("\\\""); break;
                case '\\': result.append("\\\\"); break;
                case '\b': result.append("\\b"); break;
                case '\f': result.append("\\f"); break;
                case '\n': result.append("\\n"); break;
                case '\r': result.append("\\r"); break;
                case '\t': result.append("\\t"); break;
                default:
                    if (character < 0x20 || character == 0x85 ||
                            character == 0x2028 || character == 0x2029) {
                        result.append(String.format("\\u%04x", (int) character));
                    }
                    else result.append(character);
            }
        }
        return result.append('\"').toString();
    }

    private void line(BufferedWriter writer, String text) throws IOException {
        writer.write(text);
        writer.newLine();
    }
}
