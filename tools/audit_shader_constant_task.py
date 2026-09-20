"""Verify the pinned shader-constant task bytes and camera vtable slots."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path


EXPECTED_SHA256 = "9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9"
EXPECTED_PROCESS = bytes.fromhex(
    "8b4424048b108b9278010000568b7108568b710c8b4904565150ffd25ec20400"
)


class PeImage:
    def __init__(self, path: Path) -> None:
        self.data = path.read_bytes()
        pe_offset = struct.unpack_from("<I", self.data, 0x3C)[0]
        if self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise ValueError("not a PE image")
        coff = pe_offset + 4
        section_count = struct.unpack_from("<H", self.data, coff + 2)[0]
        optional_size = struct.unpack_from("<H", self.data, coff + 16)[0]
        optional = coff + 20
        if struct.unpack_from("<H", self.data, optional)[0] != 0x10B:
            raise ValueError("expected a PE32 image")
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]
        section_table = optional + optional_size
        self.sections: list[tuple[int, int, int, int, int]] = []
        for index in range(section_count):
            row = section_table + index * 40
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, row + 8
            )
            characteristics = struct.unpack_from("<I", self.data, row + 36)[0]
            self.sections.append(
                (virtual_address, virtual_size, raw_offset, raw_size, characteristics)
            )

    def read_va(self, va: int, size: int) -> bytes:
        rva = va - self.image_base
        for section_rva, virtual_size, raw_offset, raw_size, _ in self.sections:
            extent = max(virtual_size, raw_size)
            if section_rva <= rva and rva + size <= section_rva + extent:
                offset = raw_offset + rva - section_rva
                return self.data[offset : offset + size]
        raise ValueError(f"VA 0x{va:08X} is outside mapped sections")

    def read_u32(self, va: int) -> int:
        return struct.unpack("<I", self.read_va(va, 4))[0]

    def is_executable_va(self, va: int) -> bool:
        rva = va - self.image_base
        return any(
            section_rva <= rva < section_rva + max(virtual_size, raw_size)
            and characteristics & 0x20000000
            for section_rva, virtual_size, _, raw_size, characteristics in self.sections
        )


def require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    args = parser.parse_args()

    digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    require_equal(digest, EXPECTED_SHA256, "binary SHA-256")
    image = PeImage(args.binary)
    require_equal(image.image_base, 0x00400000, "image base")

    require_equal(image.read_va(0x00435200, 0x20), EXPECTED_PROCESS, "process bytes")
    require_equal(image.read_u32(0x00F64904), 0x00435200, "task vtable slot 1")
    require_equal(
        image.read_u32(0x00FB906C + 34 * 4), 0x0060E7B0, "CameraActor slot 34"
    )
    require_equal(
        image.read_u32(0x00FB906C + 157 * 4), 0x0061A6C0, "CameraActor slot 157"
    )
    require_equal(image.read_u32(0x00FF101C + 4), 0x007F31A0, "FPS slot 1")
    require_equal(image.read_u32(0x00FF10BC + 4), 0x007F3BA0, "TPS slot 1")

    camera_slots = 0
    while image.is_executable_va(image.read_u32(0x00FB906C + camera_slots * 4)):
        camera_slots += 1
    require_equal(camera_slots, 164, "CameraActor executable slot count")

    print(f"binary_sha256={digest}")
    print("task_vftable=0x00F64900 process=0x00435200..0x0043521F")
    print("device_dispatch_offset=0x178 task_fields=+0x04,+0x08,+0x0C")
    print("camera_vftable=0x00FB906C slots=164 slot34=0x0060E7B0")
    print("fps_slot1=0x007F31A0 tps_slot1=0x007F3BA0")


if __name__ == "__main__":
    main()
