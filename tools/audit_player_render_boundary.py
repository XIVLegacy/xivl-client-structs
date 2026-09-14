"""Verify pinned PE anchors for the player render-transform boundary."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from audit_shader_constant_task import PeImage, require_equal


EXPECTED_SHA256 = "9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9"

ENTRY_BYTES = {
    0x0058DF90: bytes.fromhex("83ec14568bf18a866d020000a8405774"),
    0x006679C0: bytes.fromhex("558bec83e4f06aff68cb7fe80064a100"),
    0x00A60B80: bytes.fromhex("6aff68ecc2ed0064a100000000506489"),
    0x00A5F8A0: bytes.fromhex("558bec83e4f08b490c8b018b5044ffd20f28008b45080f2900"),
    0x00A5FF60: bytes.fromhex("558bec83e4f081ec4401000053568bf18b464885c057"),
    0x008DEC70: bytes.fromhex("558bec83e4f081ec0c040000a1b0a82e0133c489842408040000"),
    0x00A61620: bytes.fromhex("558bec83e4f081eca8000000568bf183bed80000000057"),
    0x008DE790: bytes.fromhex("558bec83e4f083ec6ca1b0a82e0133c489442468568bf1"),
    0x00BB7550: bytes.fromhex("558bec83e4f08b45080f28000f2941300f2840100f294140"),
    0x006A3560: bytes.fromhex("6aff6846f1e80064a1000000005081ec8c000000"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    args = parser.parse_args()

    digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    require_equal(digest, EXPECTED_SHA256, "binary SHA-256")
    image = PeImage(args.binary)
    require_equal(image.image_base, 0x00400000, "image base")

    for va, expected in ENTRY_BYTES.items():
        require_equal(image.read_va(va, len(expected)), expected, f"entry 0x{va:08X}")

    require_equal(image.read_u32(0x00FC0D34 + 34 * 4), 0x00A5F8A0, "CharaActor slot 34")
    require_equal(image.read_u32(0x0109CE2C + 7 * 4), 0x00A61620, "ModelObject slot 7")
    require_equal(
        image.read_u32(0x0109CE2C + 17 * 4), 0x008DDAF0, "ModelObject slot 17"
    )
    require_equal(
        image.read_u32(0x0109CE2C + 25 * 4), 0x008DE790, "ModelObject slot 25"
    )
    require_equal(
        image.read_u32(0x0109CE2C + 26 * 4), 0x008DEC70, "ModelObject slot 26"
    )
    require_equal(image.read_u32(0x00FCF98C + 13 * 4), 0x006A3560, "NamePlate slot 13")
    require_equal(image.read_u32(0x00FC0D34 + 86 * 4), 0x00A5FF60, "CharaActor slot 86")
    require_equal(
        image.read_va(0x00A61180, 8),
        bytes.fromhex("8b01ffa058010000"),
        "UPDATE_MODEL_TRANSFORM thunk",
    )
    require_equal(
        image.read_va(0x008DDAF0, 4), bytes.fromhex("8d4130c3"), "position getter"
    )
    require_equal(
        image.read_va(0x00A600E5, 12),
        bytes.fromhex("8b118b52688d44242050ffd2"),
        "publish callsite",
    )
    require_equal(
        image.read_va(0x00A60179, 12),
        bytes.fromhex("8b018b40688d54242052ffd0"),
        "alternate publish callsite",
    )
    transform_stores = bytes.fromhex("0f28000f2946500f2840100f2946600f2840200f294670")
    require_equal(
        image.read_va(0x008DEC9F, len(transform_stores)),
        transform_stores,
        "transform stores",
    )

    print(f"binary_sha256={digest}")
    print("actor_slot34=0x00A5F8A0 model_position_record=ModelObject+0x30")
    print("model_update=0x00A5FF60 publish_call=0x00A600EF")
    print("model_slot26=0x008DEC70 cache=ModelObject+0x50..+0x8C")
    print("model_slot7=0x00A61620 drawable_publish=0x00BB7550")
    print("nameplate_slot13=0x006A3560")


if __name__ == "__main__":
    main()
