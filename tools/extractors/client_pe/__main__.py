"""CLI dispatcher for the client PE extraction toolkit.

Usage:
  python -m tools.extractors.client_pe --rtti                    Dump full RTTI database
  python -m tools.extractors.client_pe --imports                 Dump import table
  python -m tools.extractors.client_pe --vtable <class>          Dump vtable for class
  python -m tools.extractors.client_pe --vtfuncs <class>         Analyze vtable functions
  python -m tools.extractors.client_pe --analyze <class>         Full struct analysis
  python -m tools.extractors.client_pe --hierarchy <class>       Inheritance hierarchy
  python -m tools.extractors.client_pe --search <pattern>        Search classes
  python -m tools.extractors.client_pe --strings <class>         Extract string refs
  python -m tools.extractors.client_pe --findstr <literal>       xref a string literal
  python -m tools.extractors.client_pe --all                     RTTI + imports

Options:
  --exe <path>        required path to ffxivgame.exe
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import IMAGE_BASE, TEXT_VA_END, TEXT_VA_START
from . import import_table_dumper, rtti_dumper, string_extractor, struct_analyzer, vtable_analyzer

def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("--help", "-h"):
        print_usage()
        return 0

    args = list(argv)

    exe_path = None
    if "--exe" in args:
        idx = args.index("--exe")
        if idx + 1 < len(args):
            exe_path = args[idx + 1]
            del args[idx:idx + 2]

    if exe_path is None:
        print("ERROR: --exe <path> is required")
        return 2
    if not Path(exe_path).exists():
        print(f"ERROR: Executable not found: {exe_path}")
        print("Use --exe <path> to specify the location of ffxivgame.exe")
        return 1

    out_dir = Path.cwd()
    cmd = args[0].lower()

    print("=== FFXIV 1.0 (1.23b) Client PE Toolkit ===\n")

    if cmd in ("--rtti", "--all"):
        out = out_dir / "ffxiv_1.0_rtti.txt"
        print("Extracting RTTI database...", end="", flush=True)
        count = rtti_dumper.dump_to_file(exe_path, out)
        entries = rtti_dumper.extract_all(exe_path)
        with_vt = sum(1 for e in entries if e.vtable_va is not None)
        with_bases = sum(1 for e in entries if e.base_classes)
        print(f" done! {count} classes ({with_vt} with vtables, {with_bases} with inheritance info)")
        print(f"  -> {out}")

    if cmd in ("--imports", "--all"):
        out = out_dir / "ffxiv_1.0_imports.txt"
        print("Extracting import table...", end="", flush=True)
        import_table_dumper.dump_to_file(exe_path, out)
        print(" done!")
        print(f"  -> {out}")

    if cmd == "--vtable" and len(args) > 1:
        class_name = args[1]
        out = out_dir / f"vtable_{class_name.replace('::', '_')}.txt"
        print(f"Extracting vtable for '{class_name}'...", end="", flush=True)
        try:
            rtti_dumper.dump_vtable(exe_path, class_name, out)
            print(" done!")
            print(f"  -> {out}")
        except ValueError as e:
            print(f"\n  ERROR: {e}")
            return 1

    if cmd == "--vtfuncs" and len(args) > 1:
        class_name = args[1]
        print(f"Analyzing vtable functions for '{class_name}'...")
        entries = rtti_dumper.extract_all(exe_path)
        target = next((e for e in entries if class_name.lower() in e.demangled_name.lower()), None)
        if target is None or target.vtable_va is None:
            print(f"  ERROR: Class '{class_name}' not found or has no vtable")
            return 1
        exe = Path(exe_path).read_bytes()
        out = out_dir / f"vtfuncs_{class_name.replace('::', '_')}.txt"
        with out.open("w", encoding="utf-8") as f:
            vtable_analyzer.dump_vtable_analysis(exe, target, f)
        vtable_analyzer.dump_vtable_analysis(exe, target, sys.stdout)
        print(f"\n  -> {out}")

    if cmd == "--analyze" and len(args) > 1:
        class_name = args[1]
        print(f"Analyzing struct '{class_name}'...")
        try:
            exe = Path(exe_path).read_bytes()
            layout = struct_analyzer.analyze(exe, class_name, exe_path)
            out = out_dir / f"struct_{class_name.replace('::', '_')}.txt"
            with out.open("w", encoding="utf-8") as f:
                struct_analyzer.dump_analysis(layout, f)
            struct_analyzer.dump_analysis(layout, sys.stdout)
            print(f"\n  -> {out}")
        except ValueError as e:
            print(f"  ERROR: {e}")
            print("  (Class may be abstract, template-only, or use a non-standard init pattern)")
            return 1

    if cmd == "--hierarchy" and len(args) > 1:
        class_name = args[1]
        print(f"Building hierarchy for '{class_name}'...")
        try:
            out = out_dir / f"hierarchy_{class_name.replace('::', '_')}.txt"
            with out.open("w", encoding="utf-8") as f:
                rtti_dumper.dump_hierarchy(exe_path, class_name, f)
            rtti_dumper.dump_hierarchy(exe_path, class_name, sys.stdout)
            print(f"\n  -> {out}")
        except ValueError as e:
            print(f"  ERROR: {e}")
            return 1

    if cmd == "--search" and len(args) > 1:
        pattern = args[1]
        print(f"Searching for classes matching '{pattern}'...")
        matches = rtti_dumper.search_classes(exe_path, pattern)
        print(f"Found {len(matches)} matches:\n")
        for m in matches:
            vt = f"vt=0x{m.vtable_va:08X}" if m.vtable_va else "no vtable"
            count = f"{m.vtable_entry_count} vfuncs" if m.vtable_entry_count else ""
            bases = f" : {', '.join(m.base_classes[:3])}" if m.base_classes else ""
            print(f"  {m.demangled_name:<80} {vt} {count}{bases}")

    if cmd == "--strings" and len(args) > 1:
        class_name = args[1]
        print(f"Extracting string references for '{class_name}'...")
        try:
            entries = rtti_dumper.extract_all(exe_path)
            target = next((e for e in entries if class_name.lower() in e.demangled_name.lower()), None)
            if target is None:
                raise ValueError(f"Class '{class_name}' not found in RTTI")
            exe = Path(exe_path).read_bytes()
            ctor_va = struct_analyzer.find_constructor(exe, target.vtable_va)
            if ctor_va == 0:
                raise ValueError(f"Constructor not found for '{class_name}'")
            strings = string_extractor.extract_from_function(exe, ctor_va)
            if target.vtable_va is not None and target.vtable_entry_count:
                import struct as _struct
                vt_off = target.vtable_va - IMAGE_BASE
                for i in range(min(target.vtable_entry_count, 50)):
                    func_va = _struct.unpack_from("<I", exe, vt_off + i * 4)[0]
                    if TEXT_VA_START <= func_va < TEXT_VA_END:
                        strings.extend(string_extractor.extract_from_function(exe, func_va, 2048))

            seen: dict[str, string_extractor.StringRef] = {}
            for s in strings:
                if s.value not in seen:
                    seen[s.value] = s
            unique = sorted(seen.values(), key=lambda x: x.value)

            out = out_dir / f"strings_{class_name.replace('::', '_')}.txt"
            with out.open("w", encoding="utf-8") as f:
                f.write(f"// String references in/around {target.demangled_name}\n")
                f.write(f"// Constructor: 0x{ctor_va:08X}\n")
                f.write(f"// {len(unique)} unique strings found\n\n")
                for s in unique:
                    f.write(f"0x{s.instruction_va:08X}  -> 0x{s.string_va:08X}  \"{s.value}\"\n")

            print(f"Found {len(unique)} unique strings")
            for s in unique[:30]:
                print(f"  0x{s.instruction_va:08X}  \"{s.value}\"")
            if len(unique) > 30:
                print(f"  ... and {len(unique) - 30} more")
            print(f"\n  -> {out}")
        except ValueError as e:
            print(f"  ERROR: {e}")
            return 1

    if cmd == "--findstr" and len(args) > 1:
        search_str = args[1]
        print(f"Finding cross-references to string '{search_str}'...")
        exe = Path(exe_path).read_bytes()
        xrefs = string_extractor.find_string_xrefs(exe, search_str)
        print(f"Found {len(xrefs)} xrefs:")
        for x in xrefs:
            func_start = struct_analyzer.find_func_start(exe, x.instruction_va)
            func_info = f" (in func 0x{func_start:08X})" if func_start else ""
            print(f"  0x{x.instruction_va:08X}{func_info}  \"{x.value}\"")

    print("\nAnalysis complete.")
    return 0


def print_usage() -> None:
    print(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
