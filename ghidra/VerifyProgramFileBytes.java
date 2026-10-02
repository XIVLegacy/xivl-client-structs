// Authenticates retained source bytes and mapped loaded bytes.
//
// The script reads the analyzed program only. It writes a compact report to
// the explicit output path after all checks complete; no program transaction is
// opened and no raw bytes are written.
//
// Env vars:
//   XIVL_PROGRAM_FILE_BYTES_INPUT       required executable path
//   XIVL_PROGRAM_FILE_BYTES_SHA256      required input SHA-256
//   XIVL_PROGRAM_FILE_BYTES_SIZE        required input size in bytes
//   XIVL_PROGRAM_FILE_BYTES_IMAGE_BASE required image base, e.g. 0x00400000
//   XIVL_PROGRAM_FILE_BYTES_OUT         required new report path
//@category XIVLegacy

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Optional;

import ghidra.app.script.GhidraScript;
import ghidra.program.database.mem.FileBytes;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Program;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.mem.MemoryBlockSourceInfo;

public class VerifyProgramFileBytes extends GhidraScript {

    private static final String INPUT_ENV = "XIVL_PROGRAM_FILE_BYTES_INPUT";
    private static final String SHA256_ENV = "XIVL_PROGRAM_FILE_BYTES_SHA256";
    private static final String SIZE_ENV = "XIVL_PROGRAM_FILE_BYTES_SIZE";
    private static final String IMAGE_BASE_ENV = "XIVL_PROGRAM_FILE_BYTES_IMAGE_BASE";
    private static final String OUTPUT_ENV = "XIVL_PROGRAM_FILE_BYTES_OUT";
    private static final int CHUNK_SIZE = 1024 * 1024;

    private static final class Config {
        final Path inputPath;
        final String inputName;
        final String expectedSha256;
        final long expectedSize;
        final long expectedImageBase;
        final Path outputPath;

        Config(Path inputPath, String inputName, String expectedSha256,
               long expectedSize, long expectedImageBase, Path outputPath) {
            this.inputPath = inputPath;
            this.inputName = inputName;
            this.expectedSha256 = expectedSha256;
            this.expectedSize = expectedSize;
            this.expectedImageBase = expectedImageBase;
            this.outputPath = outputPath;
        }
    }

    private static final class SourceRange {
        final MemoryBlockSourceInfo sourceInfo;
        final FileBytes fileBytes;
        final long fileOffset;

        SourceRange(MemoryBlockSourceInfo sourceInfo, FileBytes fileBytes,
                    long fileOffset) {
            this.sourceInfo = sourceInfo;
            this.fileBytes = fileBytes;
            this.fileOffset = fileOffset;
        }
    }

    private static final class ExcludedRange {
        final Address minAddress;
        final Address maxAddress;
        final long length;
        final String reason;

        ExcludedRange(Address minAddress, Address maxAddress, long length,
                      String reason) {
            this.minAddress = minAddress;
            this.maxAddress = maxAddress;
            this.length = length;
            this.reason = reason;
        }
    }

    private static final class RangeDigest {
        final SourceRange sourceRange;
        final String inputSha256;
        final String originalSha256;
        final String modifiedSha256;
        final String mappedSha256;

        RangeDigest(SourceRange sourceRange, String inputSha256,
                    String originalSha256, String modifiedSha256,
                    String mappedSha256) {
            this.sourceRange = sourceRange;
            this.inputSha256 = inputSha256;
            this.originalSha256 = originalSha256;
            this.modifiedSha256 = modifiedSha256;
            this.mappedSha256 = mappedSha256;
        }
    }

    private static final class Verification {
        final Config config;
        final Program program;
        final FileBytes retained;
        final String inputSha256;
        final String originalSha256;
        final String modifiedSha256;
        final List<RangeDigest> ranges;
        final List<ExcludedRange> excludedRanges;
        final long verifiedBytes;
        final long excludedBytes;

        Verification(Config config, Program program, FileBytes retained,
                     String inputSha256,
                     String originalSha256, String modifiedSha256,
                     List<RangeDigest> ranges, List<ExcludedRange> excludedRanges,
                     long verifiedBytes, long excludedBytes) {
            this.config = config;
            this.program = program;
            this.retained = retained;
            this.inputSha256 = inputSha256;
            this.originalSha256 = originalSha256;
            this.modifiedSha256 = modifiedSha256;
            this.ranges = ranges;
            this.excludedRanges = excludedRanges;
            this.verifiedBytes = verifiedBytes;
            this.excludedBytes = excludedBytes;
        }
    }

    @Override
    public void run() throws Exception {
        Config config = readConfig();
        checkNotCancelled();
        require(!Files.exists(config.outputPath),
                "output path already exists; choose a new path");

        byte[] inputBytes = readInput(config);
        checkNotCancelled();
        Program program = requireProgram(config);
        Memory memory = program.getMemory();
        FileBytes retained = selectRetainedFileBytes(memory, config);
        String originalSha256 = digestFileBytes(retained, false, config.expectedSize);
        require(config.expectedSha256.equals(originalSha256),
                "original retained FileBytes hash mismatch");
        String modifiedSha256 = digestFileBytes(retained, true, config.expectedSize);
        require(config.expectedSha256.equals(modifiedSha256),
                "modified retained FileBytes hash mismatch");
        checkNotCancelled();

        List<ExcludedRange> excludedRanges = new ArrayList<>();
        List<SourceRange> sourceRanges = collectFileBackedRanges(
                memory, retained, config, excludedRanges);
        List<RangeDigest> rangeDigests = new ArrayList<>();
        long verifiedBytes = 0L;
        for (SourceRange sourceRange : sourceRanges) {
            checkNotCancelled();
            RangeDigest rangeDigest = verifyRange(sourceRange, inputBytes, memory);
            require(rangeDigest.originalSha256.equals(rangeDigest.inputSha256),
                    "original source range mismatch");
            require(rangeDigest.modifiedSha256.equals(rangeDigest.inputSha256),
                    "modified source range mismatch");
            require(rangeDigest.mappedSha256.equals(rangeDigest.inputSha256),
                    "mapped memory range mismatch");
            rangeDigests.add(rangeDigest);
            verifiedBytes = checkedAdd(verifiedBytes,
                    sourceRange.sourceInfo.getLength(), "verified coverage size overflow");
        }
        require(!rangeDigests.isEmpty(), "no loaded initialized file-backed ranges found");
        checkNotCancelled();

        long excludedBytes = 0L;
        for (ExcludedRange excludedRange : excludedRanges) {
            excludedBytes = checkedAdd(excludedBytes, excludedRange.length,
                    "excluded coverage size overflow");
        }

        Verification verification = new Verification(
                config, program, retained, config.expectedSha256,
                originalSha256, modifiedSha256, rangeDigests, excludedRanges,
                verifiedBytes, excludedBytes);
        writeReport(config.outputPath, buildReport(verification));
        println("COMPLETE: program-file-bytes-v1");
    }

    private Config readConfig() {
        String input = requireEnv(INPUT_ENV);
        Path inputPath = Paths.get(input).toAbsolutePath().normalize();
        String inputName = baseName(inputPath.toString());
        require(!inputName.isEmpty(), "input path has no file name");

        String expectedSha256 = requireEnv(SHA256_ENV).toLowerCase(Locale.ROOT);
        require(expectedSha256.matches("[0-9a-f]{64}"),
                SHA256_ENV + " must be 64 hexadecimal characters");
        long expectedSize = parseLong(SIZE_ENV, requireEnv(SIZE_ENV));
        require(expectedSize > 0 && expectedSize <= Integer.MAX_VALUE,
                SIZE_ENV + " must be in the supported positive range");
        long expectedImageBase = parseLong(IMAGE_BASE_ENV, requireEnv(IMAGE_BASE_ENV));
        require(expectedImageBase >= 0, IMAGE_BASE_ENV + " must be non-negative");

        Path outputPath = Paths.get(requireEnv(OUTPUT_ENV)).toAbsolutePath().normalize();
        Path outputParent = outputPath.getParent();
        require(outputParent != null && Files.isDirectory(outputParent),
                "output parent directory is unavailable");
        return new Config(inputPath, inputName, expectedSha256, expectedSize,
                expectedImageBase, outputPath);
    }

    private byte[] readInput(Config config) throws IOException {
        require(Files.isRegularFile(config.inputPath), "input executable is not a regular file");
        long actualSize = Files.size(config.inputPath);
        require(actualSize == config.expectedSize, "input executable size mismatch");
        byte[] inputBytes = Files.readAllBytes(config.inputPath);
        require(inputBytes.length == config.expectedSize, "input read size mismatch");
        String actualSha256 = digest(inputBytes);
        require(config.expectedSha256.equals(actualSha256), "input executable SHA-256 mismatch");
        return inputBytes;
    }

    private Program requireProgram(Config config) {
        require(currentProgram != null, "program unavailable");
        require(baseName(currentProgram.getName()).equalsIgnoreCase(config.inputName),
                "program name does not identify the input executable");
        Address imageBase = currentProgram.getImageBase();
        require(imageBase != null && imageBase.getOffset() == config.expectedImageBase,
                "program image base mismatch");
        require(currentProgram.getLanguageID() != null &&
                currentProgram.getLanguageID().getIdAsString() != null,
                "program language identity is missing");
        require(currentProgram.getCompilerSpec() != null &&
                currentProgram.getCompilerSpec().getCompilerSpecID() != null &&
                currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString() != null,
                "program compiler-spec identity is missing");
        return currentProgram;
    }

    private FileBytes selectRetainedFileBytes(Memory memory, Config config) {
        List<FileBytes> all = memory.getAllFileBytes();
        require(all != null && !all.isEmpty(), "retained FileBytes are missing");

        List<FileBytes> matches = new ArrayList<>();
        for (FileBytes fileBytes : all) {
            require(fileBytes != null && fileBytes.getFilename() != null,
                    "retained FileBytes identity is missing");
            String retainedName = baseName(fileBytes.getFilename());
            if (!retainedName.equalsIgnoreCase(config.inputName)) {
                continue;
            }
            require(fileBytes.getFileOffset() == 0,
                    "retained FileBytes source offset is unsupported");
            require(fileBytes.getSize() == config.expectedSize,
                    "retained FileBytes size does not identify the input");
            matches.add(fileBytes);
        }
        require(matches.size() == 1, "retained FileBytes source identity is missing or conflicting");
        return matches.get(0);
    }

    private List<SourceRange> collectFileBackedRanges(Memory memory,
                                                      FileBytes retained,
                                                      Config config,
                                                      List<ExcludedRange> excludedRanges) {
        List<SourceRange> ranges = new ArrayList<>();
        for (MemoryBlock block : memory.getBlocks()) {
            checkNotCancelled();
            if (!block.isLoaded() || !block.isInitialized()) {
                if (block.isExecute()) {
                    throw new IllegalStateException(
                            "executable block is not a loaded initialized block");
                }
                continue;
            }
            List<MemoryBlockSourceInfo> sourceInfos = block.getSourceInfos();
            if (sourceInfos == null || sourceInfos.isEmpty()) {
                if (block.isExecute()) {
                    throw new IllegalStateException("executable block has no source information");
                }
                excludedRanges.add(new ExcludedRange(block.getStart(), block.getEnd(),
                        block.getSize(), "source-info-missing"));
                continue;
            }
            for (MemoryBlockSourceInfo sourceInfo : sourceInfos) {
                require(sourceInfo != null, "loaded initialized source range is missing");
            }
            List<MemoryBlockSourceInfo> ordered = new ArrayList<>(sourceInfos);
            Collections.sort(ordered, Comparator.comparing(MemoryBlockSourceInfo::getMinAddress));

            Address expectedStart = block.getStart();
            for (MemoryBlockSourceInfo sourceInfo : ordered) {
                checkNotCancelled();
                require(sourceInfo != null && sourceInfo.getLength() > 0,
                        "executable source range is empty");
                require(expectedStart != null, "executable source coverage exceeds address space");
                require(sourceInfo.getMinAddress().equals(expectedStart),
                        "loaded initialized source coverage is incomplete or overlapping");
                require(sourceInfo.getMaxAddress().equals(
                        sourceInfo.getMinAddress().add(sourceInfo.getLength() - 1)),
                        "loaded initialized source range length is inconsistent");
                require(sourceInfo.getMaxAddress().compareTo(block.getEnd()) <= 0,
                        "source range exceeds its memory block");

                Optional<FileBytes> sourceFileBytes = sourceInfo.getFileBytes();
                if (!sourceFileBytes.isPresent()) {
                    if (block.isExecute()) {
                        throw new IllegalStateException(
                                "executable range is not backed by retained FileBytes");
                    }
                    excludedRanges.add(new ExcludedRange(sourceInfo.getMinAddress(),
                            sourceInfo.getMaxAddress(), sourceInfo.getLength(),
                            "unbacked-or-mapped-source"));
                }
                else {
                    require(sourceFileBytes.get().equals(retained),
                            "covered ranges have conflicting source identities");
                    long fileOffset = sourceInfo.getFileBytesOffset();
                    if (fileOffset < 0) {
                        if (block.isExecute()) {
                            throw new IllegalStateException("executable source offset is unsupported");
                        }
                        excludedRanges.add(new ExcludedRange(sourceInfo.getMinAddress(),
                                sourceInfo.getMaxAddress(), sourceInfo.getLength(),
                                "unsupported-source-offset"));
                    }
                    else {
                        long endOffset = checkedAdd(fileOffset, sourceInfo.getLength(),
                                "source offset overflow");
                        require(endOffset <= retained.getSize() && endOffset <= config.expectedSize,
                                "source range exceeds retained input");
                        ranges.add(new SourceRange(sourceInfo, retained, fileOffset));
                    }
                }
                expectedStart = sourceInfo.getMaxAddress().next();
                if (expectedStart == null) {
                    require(sourceInfo.getMaxAddress().equals(block.getEnd()),
                            "source coverage reaches address limit");
                }
            }
            Address blockSuccessor = block.getEnd().next();
            require(expectedStart == null ? blockSuccessor == null :
                    expectedStart.equals(blockSuccessor), "loaded initialized block coverage is incomplete");
        }
        Collections.sort(ranges, Comparator
                .comparing((SourceRange range) ->
                        range.sourceInfo.getMinAddress().getAddressSpace().getName())
                .thenComparingLong(range -> range.sourceInfo.getMinAddress().getOffset()));
        Collections.sort(excludedRanges, Comparator
                .comparing((ExcludedRange range) ->
                        range.minAddress.getAddressSpace().getName())
                .thenComparingLong(range -> range.minAddress.getOffset()));
        return ranges;
    }

    private RangeDigest verifyRange(SourceRange sourceRange, byte[] inputBytes,
                                    Memory memory) throws IOException, MemoryAccessException {
        long length = sourceRange.sourceInfo.getLength();
        MessageDigest inputDigest = newDigest();
        MessageDigest originalDigest = newDigest();
        MessageDigest modifiedDigest = newDigest();
        MessageDigest mappedDigest = newDigest();
        byte[] inputChunk = new byte[CHUNK_SIZE];
        byte[] originalChunk = new byte[CHUNK_SIZE];
        byte[] modifiedChunk = new byte[CHUNK_SIZE];
        byte[] mappedChunk = new byte[CHUNK_SIZE];

        long processed = 0;
        while (processed < length) {
            checkNotCancelled();
            int chunkLength = (int) Math.min(CHUNK_SIZE, length - processed);
            int inputOffset = checkedIndex(sourceRange.fileOffset + processed, inputBytes.length,
                    "input range offset overflow");
            System.arraycopy(inputBytes, inputOffset, inputChunk, 0, chunkLength);
            int sourceOffset = checkedIndex(processed + sourceRange.fileOffset,
                    sourceRange.fileBytes.getSize(), "retained source offset overflow");
            int originalCount = sourceRange.fileBytes.getOriginalBytes(
                    sourceOffset, originalChunk, 0, chunkLength);
            int modifiedCount = sourceRange.fileBytes.getModifiedBytes(
                    sourceOffset, modifiedChunk, 0, chunkLength);
            require(originalCount == chunkLength && modifiedCount == chunkLength,
                    "retained source range returned incomplete bytes");
            Address mappedAddress = sourceRange.sourceInfo.getMinAddress().add(processed);
            int mappedCount = memory.getBytes(mappedAddress, mappedChunk, 0, chunkLength);
            require(mappedCount == chunkLength, "mapped loaded range returned incomplete bytes");

            inputDigest.update(inputChunk, 0, chunkLength);
            originalDigest.update(originalChunk, 0, chunkLength);
            modifiedDigest.update(modifiedChunk, 0, chunkLength);
            mappedDigest.update(mappedChunk, 0, chunkLength);
            require(Arrays.equals(inputChunk, 0, chunkLength,
                    originalChunk, 0, chunkLength), "original source bytes differ from input");
            require(Arrays.equals(inputChunk, 0, chunkLength,
                    modifiedChunk, 0, chunkLength), "modified stored bytes differ from input");
            require(Arrays.equals(inputChunk, 0, chunkLength,
                    mappedChunk, 0, chunkLength), "mapped loaded bytes differ from input");
            processed += chunkLength;
        }
        return new RangeDigest(sourceRange, digest(inputDigest), digest(originalDigest),
                digest(modifiedDigest), digest(mappedDigest));
    }

    private String digestFileBytes(FileBytes fileBytes, boolean modified, long size)
            throws IOException {
        MessageDigest messageDigest = newDigest();
        byte[] chunk = new byte[CHUNK_SIZE];
        long offset = 0;
        while (offset < size) {
            checkNotCancelled();
            int length = (int) Math.min(CHUNK_SIZE, size - offset);
            int count = modified
                    ? fileBytes.getModifiedBytes(offset, chunk, 0, length)
                    : fileBytes.getOriginalBytes(offset, chunk, 0, length);
            require(count == length, "retained FileBytes returned incomplete bytes");
            messageDigest.update(chunk, 0, length);
            offset += length;
        }
        return digest(messageDigest);
    }

    private String buildReport(Verification verification) {
        StringBuilder report = new StringBuilder(512 + verification.ranges.size() * 180);
        report.append("schema=program-file-bytes-v1\n");
        report.append("program=").append(safeName(verification.program.getName())).append('\n');
        report.append("input_name=").append(safeName(verification.config.inputName)).append('\n');
        report.append("input_size=").append(verification.config.expectedSize).append('\n');
        report.append("input_sha256=").append(verification.inputSha256).append('\n');
        report.append("image_base=").append(hex(verification.config.expectedImageBase)).append('\n');
        report.append("language_id=")
                .append(verification.program.getLanguageID().getIdAsString()).append('\n');
        report.append("compiler_spec_id=")
                .append(verification.program.getCompilerSpec().getCompilerSpecID()
                        .getIdAsString()).append('\n');
        report.append("retained_file_bytes_count=")
                .append(verification.program.getMemory().getAllFileBytes().size()).append('\n');
        report.append("retained_source_name=")
                .append(safeName(baseName(verification.retained.getFilename()))).append('\n');
        report.append("retained_source_offset=").append(verification.retained.getFileOffset()).append('\n');
        report.append("retained_source_size=").append(verification.retained.getSize()).append('\n');
        report.append("retained_original_sha256=").append(verification.originalSha256).append('\n');
        report.append("retained_modified_sha256=").append(verification.modifiedSha256).append('\n');
        report.append("retained_original_matches_input=true\n");
        report.append("retained_modified_matches_input=")
                .append(verification.modifiedSha256.equals(verification.inputSha256)).append('\n');
        report.append("verified_range_count=").append(verification.ranges.size()).append('\n');
        report.append("verified_byte_count=").append(verification.verifiedBytes).append('\n');
        report.append("excluded_nonexec_initialized_range_count=")
                .append(verification.excludedRanges.size()).append('\n');
        report.append("excluded_nonexec_initialized_byte_count=")
                .append(verification.excludedBytes).append('\n');
        report.append("coverage=complete-for-loaded-initialized-file-backed-ranges\n");
        for (RangeDigest range : verification.ranges) {
            MemoryBlockSourceInfo sourceInfo = range.sourceRange.sourceInfo;
            report.append("range=")
                    .append(addressText(sourceInfo.getMinAddress())).append('-')
                    .append(addressText(sourceInfo.getMaxAddress()))
                    .append(",file_offset=").append(range.sourceRange.fileOffset)
                    .append(",size=").append(sourceInfo.getLength())
                    .append(",input_sha256=").append(range.inputSha256)
                    .append(",original_sha256=").append(range.originalSha256)
                    .append(",modified_sha256=").append(range.modifiedSha256)
                    .append(",mapped_sha256=").append(range.mappedSha256).append('\n');
        }
        for (ExcludedRange range : verification.excludedRanges) {
            report.append("excluded_nonexec_initialized_range=")
                    .append(addressText(range.minAddress)).append('-')
                    .append(addressText(range.maxAddress))
                    .append(",size=").append(range.length)
                    .append(",reason=").append(range.reason).append('\n');
        }
        report.append("COMPLETE: program-file-bytes-v1\n");
        return report.toString();
    }

    private void writeReport(Path outputPath, String report) throws IOException {
        Path parent = outputPath.getParent();
        require(parent != null && Files.isDirectory(parent), "output parent directory is unavailable");
        Path temporary = Files.createTempFile(parent, ".program-file-bytes-", ".tmp");
        boolean installed = false;
        try {
            try (BufferedWriter writer = Files.newBufferedWriter(
                    temporary, StandardCharsets.UTF_8, StandardOpenOption.WRITE,
                    StandardOpenOption.TRUNCATE_EXISTING)) {
                writer.write(report);
            }
            checkNotCancelled();
            Files.move(temporary, outputPath);
            installed = true;
        }
        finally {
            if (!installed) {
                Files.deleteIfExists(temporary);
            }
        }
    }

    private void checkNotCancelled() {
        if (monitor.isCancelled()) {
            throw new IllegalStateException("cancelled");
        }
    }

    private static String requireEnv(String name) {
        String value = System.getenv(name);
        require(value != null && !value.trim().isEmpty(), name + " is required");
        return value.trim();
    }

    private static long parseLong(String name, String value) {
        try {
            return Long.decode(value);
        }
        catch (NumberFormatException exception) {
            throw new IllegalArgumentException(name + " is not a valid integer", exception);
        }
    }

    private static String baseName(String value) {
        int slash = Math.max(value.lastIndexOf('/'), value.lastIndexOf('\\'));
        return slash < 0 ? value : value.substring(slash + 1);
    }

    private static String safeName(String value) {
        StringBuilder safe = new StringBuilder(value.length());
        for (int i = 0; i < value.length(); i++) {
            char character = value.charAt(i);
            if (Character.isLetterOrDigit(character) || character == '.' ||
                    character == '_' || character == '-') {
                safe.append(character);
            }
            else {
                safe.append('_');
            }
        }
        return safe.length() == 0 ? "unknown" : safe.toString();
    }

    private static int checkedIndex(long offset, long limit, String reason) {
        require(offset >= 0 && offset <= limit && offset <= Integer.MAX_VALUE, reason);
        return (int) offset;
    }

    private static long checkedAdd(long left, long right, String reason) {
        require(right >= 0 && left >= 0 && left <= Long.MAX_VALUE - right, reason);
        return left + right;
    }

    private static MessageDigest newDigest() {
        try {
            return MessageDigest.getInstance("SHA-256");
        }
        catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 unavailable", exception);
        }
    }

    private static String digest(byte[] bytes) {
        MessageDigest messageDigest = newDigest();
        messageDigest.update(bytes);
        return digest(messageDigest);
    }

    private static String digest(MessageDigest messageDigest) {
        byte[] bytes = messageDigest.digest();
        StringBuilder text = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            text.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return text.toString();
    }

    private static String hex(long value) {
        return String.format(Locale.ROOT, "0x%08X", value);
    }

    private static String addressText(Address address) {
        return safeName(address.getAddressSpace().getName()) + ":" + hex(address.getOffset());
    }

    private static void require(boolean condition, String reason) {
        if (!condition) {
            throw new IllegalStateException(reason);
        }
    }
}
