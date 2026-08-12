// Ghidra post-script: extracts MSVC RTTI_Complete_Object_Locator (COL) symbols
// as tab-separated records.
// Output format:
//   <vftable_VA>\t<col_VA>\t<mangled_name>\t<demangled_name>
// Required environment:
//   XIVL_RTTI_OUT  output file path for the full index
// Optional targeted detail mode:
//   XIVL_RTTI_DETAILS_OUT      output file path
//   XIVL_RTTI_DETAILS_TARGETS  comma-separated exact mangled RTTI names
// Run via:
//   analyzeHeadless ... -postScript ExtractRtti.java
// @category XIVLegacy
// Headless Ghidra 12.1 uses this Java exporter because Python post-scripts
// require unavailable PyGhidra/CPython support in this environment.

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.app.util.demangler.DemangledObject;
import ghidra.app.util.demangler.DemanglerOptions;
import ghidra.app.util.demangler.MangledContext;
import ghidra.app.util.demangler.microsoft.MicrosoftDemangler;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolTable;

public class ExtractRtti extends GhidraScript {

    private Memory mem;
    private AddressSpace space;
    private MicrosoftDemangler demangler;
    private DemanglerOptions demanglerOpts;

    @Override
    public void run() throws Exception {
        mem = currentProgram.getMemory();
        space = currentProgram.getAddressFactory().getDefaultAddressSpace();

        String detailsOutPath = System.getenv("XIVL_RTTI_DETAILS_OUT");
        if (detailsOutPath != null && !detailsOutPath.isEmpty()) {
            writeDetails(detailsOutPath, requireEnv("XIVL_RTTI_DETAILS_TARGETS"));
            return;
        }

        String outPath = System.getenv("XIVL_RTTI_OUT");
        if (outPath == null || outPath.isEmpty()) {
            throw new IllegalStateException("Set XIVL_RTTI_OUT to the output file path");
        }

        SymbolTable symTab = currentProgram.getSymbolTable();
        ReferenceManager refMgr = currentProgram.getReferenceManager();

        long imageBase = currentProgram.getImageBase().getOffset();

        demangler = new MicrosoftDemangler();
        demanglerOpts = new DemanglerOptions();

        println("[extract_rtti] image_base = 0x" + String.format("%08X", imageBase));
        println("[extract_rtti] scanning symbol table for RTTI_Complete_Object_Locator...");

        List<long[]> stringless = new ArrayList<long[]>();
        List<Object[]> records = new ArrayList<Object[]>();
        Set<String> seenVftables = new HashSet<String>();

        SymbolIterator colSyms = symTab.getSymbolIterator("RTTI_Complete_Object_Locator*", true);
        int colCount = 0;
        int noRefCount = 0;
        int noTypeCount = 0;

        while (colSyms.hasNext()) {
            Symbol sym = colSyms.next();
            colCount++;
            Address colAddr = sym.getAddress();
            long colVa = colAddr.getOffset() & 0xFFFFFFFFL;

            // MSVC x86 COL stores pTypeDescriptor at +0x0C as an absolute VA.
            Long typeDescVa = readU32(colAddr.add(0x0C));
            if (typeDescVa == null || typeDescVa.longValue() == 0L) {
                noTypeCount++;
                continue;
            }

            String mangled = null;
            try {
                Address tdAddr = space.getAddress(typeDescVa.longValue() & 0xFFFFFFFFL);
                mangled = readCstrAscii(tdAddr.add(0x08), 512);
            } catch (Exception e) {
                mangled = null;
            }
            if (mangled == null || mangled.isEmpty()) {
                noTypeCount++;
                continue;
            }

            // The COL pointer is stored at vftable - 4. Derive vftable VA as
            // ref.fromAddress + 4.
            List<Long> foundVftables = new ArrayList<Long>();
            for (Reference r : refMgr.getReferencesTo(colAddr)) {
                long vftableVa = (r.getFromAddress().getOffset() + 4) & 0xFFFFFFFFL;
                foundVftables.add(Long.valueOf(vftableVa));
            }

            String demangled = demangle(mangled);
            if (foundVftables.isEmpty()) {
                noRefCount++;
                records.add(new Object[] { Long.valueOf(0L), Long.valueOf(colVa), mangled, demangled });
                continue;
            }
            for (Long v : foundVftables) {
                String key = v + ":" + colVa;
                if (seenVftables.contains(key)) {
                    continue;
                }
                seenVftables.add(key);
                records.add(new Object[] { v, Long.valueOf(colVa), mangled, demangled });
            }
        }

        println("[extract_rtti] COL symbols seen: " + colCount);
        println("[extract_rtti] COLs with no inbound ref: " + noRefCount);
        println("[extract_rtti] COLs with bad/missing TypeDescriptor: " + noTypeCount);
        println("[extract_rtti] total emitted records: " + records.size());

        // Stable output order: vftable VA, then COL VA.
        Collections.sort(records, new Comparator<Object[]>() {
            @Override
            public int compare(Object[] a, Object[] b) {
                long av = ((Long) a[0]).longValue();
                long bv = ((Long) b[0]).longValue();
                if (av != bv) return Long.compare(av, bv);
                long ac = ((Long) a[1]).longValue();
                long bc = ((Long) b[1]).longValue();
                return Long.compare(ac, bc);
            }
        });

        BufferedWriter w = new BufferedWriter(new FileWriter(outPath));
        try {
            w.write("# FFXIV 1.0 (1.23b) RTTI extraction (self-sourced)\n");
            w.write("# Source binary: " + currentProgram.getExecutablePath() + "\n");
            w.write("# Image base: 0x" + String.format("%08X", imageBase) + "\n");
            w.write("# Total records: " + records.size() + "\n");
            w.write("# Format: <vftable_VA>\\t<col_VA>\\t<mangled_name>\\t<demangled_name>\n");
            for (Object[] rec : records) {
                long vftableVa = ((Long) rec[0]).longValue();
                long colVa = ((Long) rec[1]).longValue();
                String mangled = (String) rec[2];
                String demangled = (String) rec[3];
                w.write(String.format("0x%08X\t0x%08X\t%s\t%s\n",
                        vftableVa, colVa, mangled, demangled));
            }
        } finally {
            w.close();
        }

        println("WROTE: " + outPath);
    }

    private void writeDetails(String outPath, String targetText) throws Exception {
        Set<String> targets = new HashSet<String>();
        for (String value : targetText.split(",")) {
            String trimmed = value.trim();
            if (!trimmed.isEmpty()) targets.add(trimmed);
        }
        if (targets.isEmpty()) {
            throw new IllegalStateException("XIVL_RTTI_DETAILS_TARGETS contains no names");
        }

        SymbolTable symTab = currentProgram.getSymbolTable();
        ReferenceManager refMgr = currentProgram.getReferenceManager();
        List<String> records = new ArrayList<String>();
        Set<String> foundTargets = new HashSet<String>();

        SymbolIterator colSyms = symTab.getSymbolIterator("RTTI_Complete_Object_Locator*", true);
        while (colSyms.hasNext()) {
            Symbol sym = colSyms.next();
            Address colAddr = sym.getAddress();
            Long typeDescVa = readU32(colAddr.add(0x0c));
            Long classHierarchyVa = readU32(colAddr.add(0x10));
            if (typeDescVa == null || classHierarchyVa == null) continue;

            String mangled = readTypeName(typeDescVa.longValue());
            if (mangled == null || !targets.contains(mangled)) continue;
            foundTargets.add(mangled);

            List<String> bases = readBaseClasses(classHierarchyVa.longValue());
            for (Reference ref : refMgr.getReferencesTo(colAddr)) {
                long vftableVa = (ref.getFromAddress().getOffset() + 4) & 0xffffffffL;
                records.add(String.format(
                    "%s\t0x%08X\t0x%08X\t0x%08X\t0x%08X\t%d\t%s\t%s",
                    mangled,
                    vftableVa,
                    colAddr.getOffset() & 0xffffffffL,
                    typeDescVa.longValue(),
                    classHierarchyVa.longValue(),
                    countExecutableSlots(vftableVa),
                    join(bases),
                    join(readCodeReferences(vftableVa, refMgr))));
            }
        }

        Set<String> missing = new HashSet<String>(targets);
        missing.removeAll(foundTargets);
        if (!missing.isEmpty()) {
            throw new IllegalStateException("RTTI targets not found: " + join(new ArrayList<String>(missing)));
        }

        Collections.sort(records);
        BufferedWriter writer = new BufferedWriter(new FileWriter(outPath));
        try {
            writer.write("# FFXIV 1.0 (1.23b) targeted RTTI details\n");
            writer.write("# Source binary: " + currentProgram.getExecutablePath() + "\n");
            writer.write("# Format: mangled\\tvftable_VA\\tCOL_VA\\tTypeDescriptor_VA\\tCHD_VA\\tslot_count\\tbases\\tcode_refs\n");
            for (String record : records) {
                writer.write(record);
                writer.write("\n");
            }
        } finally {
            writer.close();
        }
        println("WROTE: " + outPath);
        println("TARGETS: " + targets.size() + ", RECORDS: " + records.size());
    }

    private String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalStateException("Set " + name);
        }
        return value;
    }

    private List<String> readBaseClasses(long classHierarchyVa) {
        List<String> result = new ArrayList<String>();
        Address chdAddr = space.getAddress(classHierarchyVa & 0xffffffffL);
        Long countValue = readU32(chdAddr.add(0x08));
        Long arrayVa = readU32(chdAddr.add(0x0c));
        if (countValue == null || arrayVa == null) return result;
        int count = (int) Math.min(countValue.longValue(), 256L);
        Address arrayAddr = space.getAddress(arrayVa.longValue() & 0xffffffffL);
        for (int i = 0; i < count; i++) {
            Long descriptorVa = readU32(arrayAddr.add(i * 4L));
            if (descriptorVa == null) continue;
            Long baseTypeDescVa = readU32(space.getAddress(descriptorVa.longValue()).add(0x00));
            if (baseTypeDescVa == null) continue;
            String baseName = readTypeName(baseTypeDescVa.longValue());
            if (baseName != null) result.add(baseName);
        }
        return result;
    }

    private int countExecutableSlots(long vftableVa) {
        Address slot = space.getAddress(vftableVa & 0xffffffffL);
        int count = 0;
        for (; count < 1024; count++) {
            Long functionVa = readU32(slot.add(count * 4L));
            if (functionVa == null) break;
            Address functionAddr = space.getAddress(functionVa.longValue() & 0xffffffffL);
            MemoryBlock block = mem.getBlock(functionAddr);
            if (block == null || !block.isExecute()) break;
        }
        return count;
    }

    private List<String> readCodeReferences(long vftableVa, ReferenceManager refMgr) {
        List<String> result = new ArrayList<String>();
        Address vftableAddr = space.getAddress(vftableVa & 0xffffffffL);
        for (Reference ref : refMgr.getReferencesTo(vftableAddr)) {
            Address from = ref.getFromAddress();
            MemoryBlock block = mem.getBlock(from);
            if (block == null || !block.isExecute()) continue;
            Function function = getFunctionContaining(from);
            Instruction instruction = getInstructionAt(from);
            String functionVa = function == null
                ? "none"
                : String.format("0x%08X", function.getEntryPoint().getOffset() & 0xffffffffL);
            String instructionText = instruction == null ? "no-instruction" : instruction.toString();
            instructionText = instructionText.replace('\t', ' ').replace(';', ',');
            result.add(String.format("0x%08X@%s:%s",
                from.getOffset() & 0xffffffffL, functionVa, instructionText));
        }
        Collections.sort(result);
        return result;
    }

    private String readTypeName(long typeDescVa) {
        try {
            return readCstrAscii(space.getAddress(typeDescVa & 0xffffffffL).add(0x08), 512);
        } catch (Exception e) {
            return null;
        }
    }

    private String join(List<String> values) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) result.append(';');
            result.append(values.get(i));
        }
        return result.toString();
    }

    private Long readU32(Address addr) {
        try {
            byte[] b = new byte[4];
            mem.getBytes(addr, b);
            long v = ((long) (b[0] & 0xFF))
                   | (((long) (b[1] & 0xFF)) << 8)
                   | (((long) (b[2] & 0xFF)) << 16)
                   | (((long) (b[3] & 0xFF)) << 24);
            return Long.valueOf(v & 0xFFFFFFFFL);
        } catch (Exception e) {
            return null;
        }
    }

    private String readCstrAscii(Address addr, int maxLen) {
        StringBuilder sb = new StringBuilder();
        Address cur = addr;
        for (int i = 0; i < maxLen; i++) {
            int byteVal;
            try {
                byteVal = mem.getByte(cur) & 0xFF;
            } catch (Exception e) {
                return null;
            }
            if (byteVal == 0) {
                return sb.toString();
            }
            if (byteVal < 0x20 || byteVal > 0x7E) {
                return null;
            }
            sb.append((char) byteVal);
            cur = cur.add(1);
        }
        return null;
    }

    private String demangle(String mangled) {
        if (mangled == null || mangled.isEmpty()) return "";

        String custom = tryDecodeRttiName(mangled);
        if (custom != null && !custom.isEmpty()) {
            return custom;
        }

        String candidate = mangled;
        if (candidate.startsWith(".")) {
            candidate = candidate.substring(1);
        }
        try {
            MangledContext ctx = demangler.createMangledContext(candidate, demanglerOpts, currentProgram, null);
            DemangledObject obj = demangler.demangle(ctx);
            if (obj == null) return "";
            String sig = obj.getSignature(false);
            return sig != null ? sig : "";
        } catch (Throwable t) {
            return "";
        }
    }

    // Hand-decode plain class/struct and nested-namespace names. Return null for
    // forms handled by Ghidra.
    private String tryDecodeRttiName(String name) {
        if (!name.startsWith(".?A") || name.length() < 5) return null;
        int pos = 4;
        // Components are between '@' separators and end with "@@".
        int end = name.length();
        if (end < pos + 2 || !name.endsWith("@@")) return null;
        end -= 2;

        java.util.List<String> components = new java.util.ArrayList<String>();
        int compStart = pos;
        while (compStart < end) {
            int at = name.indexOf('@', compStart);
            if (at < 0 || at > end) at = end;
            String comp = name.substring(compStart, at);
            String decoded = decodeRttiComponent(comp, name, compStart, at);
            if (decoded == null) return null;
            components.add(decoded);
            compStart = at + 1;
        }
        if (components.isEmpty()) return null;

        // Components are innermost-first. Reverse for outer::...::inner order.
        java.util.Collections.reverse(components);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < components.size(); i++) {
            if (i > 0) sb.append("::");
            sb.append(components.get(i));
        }
        return sb.toString();
    }

    private String decodeRttiComponent(String comp, String fullName, int absStart, int absEnd) {
        if (comp.isEmpty()) return null;

        // Anonymous-namespace marker: "?A0x<hex>".
        if (comp.startsWith("?A0x")) {
            return "?A0x" + comp.substring(4);
        }

        // Template arguments are encoded inline. Hand-rendering is unsafe, so
        // return null for Ghidra's demangler.
        if (comp.startsWith("?$")) {
            return null;
        }

        // Plain components use letters, digits, and underscore. Other forms fall back.
        for (int i = 0; i < comp.length(); i++) {
            char c = comp.charAt(i);
            if (!Character.isLetterOrDigit(c) && c != '_') {
                return null;
            }
        }
        return comp;
    }
}
