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
    0x00A61130: bytes.fromhex("558bec83e4f08b492c83ec1085c98d0424"),
    0x008DE970: bytes.fromhex("558bec83e4f081ec0c040000a1b0a82e0133c4"),
    0x008DEC70: bytes.fromhex("558bec83e4f081ec0c040000a1b0a82e0133c489842408040000"),
    0x00A61620: bytes.fromhex("558bec83e4f081eca8000000568bf183bed80000000057"),
    0x008DE790: bytes.fromhex("558bec83e4f083ec6ca1b0a82e0133c489442468568bf1"),
    0x00BB7550: bytes.fromhex("558bec83e4f08b45080f28000f2941300f2840100f294140"),
    0x006A3560: bytes.fromhex("6aff6846f1e80064a1000000005081ec8c000000"),
    0x006A3AD0: bytes.fromhex("8b442404f30f1044240883ec108bd056"),
    0x006A2A60: bytes.fromhex("807c2404000f94c002c002c032819001"),
    0x007CD360: bytes.fromhex("6aff685cb0ea0064a1000000005083ec"),
    0x007D4560: bytes.fromhex("558bec83e4f06aff6805b8ea0064a100"),
    0x007D49F0: bytes.fromhex("558bec83e4f06aff6807b9ea0064a100"),
    0x00A68CB0: bytes.fromhex("6aff6843caed0064a100000000506489"),
    0x00A68000: bytes.fromhex("568bf18b460c83e801743c83e801741e"),
    0x00A68060: bytes.fromhex("8b49048b018b4004ffe0"),
    0x00A68070: bytes.fromhex("558bec83e4f083ec2c568bf18b46048b"),
    0x00A680D0: bytes.fromhex("8b49048b018b4008ffe0"),
    0x008D5570: bytes.fromhex("8b4104c3"),
    0x00AFA220: bytes.fromhex("558bec83e4f08b41148b49106bc97003"),
    0x00AFA070: bytes.fromhex("558bec83e4f08b450883ec085333db56"),
    0x00AFA160: bytes.fromhex("558bec83e4f08b45080f28008b41108b"),
    0x00A67F80: bytes.fromhex("558bec83e4f08b450cc7410c01000000"),
    0x00A67FB0: bytes.fromhex("558bec83e4f08b4508c7410c02000000"),
    0x00A67FD0: bytes.fromhex("558bec83e4f08b4508c7410c03000000"),
    0x007D8080: bytes.fromhex("558bec83e4f083ec48a1b0a82e0133c4"),
    0x007D77E0: bytes.fromhex("558bec83e4f083ec54a1b0a82e0133c4"),
    0x007D70D0: bytes.fromhex("558bec83e4f06aff68e0b9ea0064a100"),
    0x007D8E90: bytes.fromhex("8b492c85c97405e9c4123200c20400"),
    0x00A5F810: bytes.fromhex("558bec83e4f083ec2c8b45080f280056"),
    0x008DDAB0: bytes.fromhex("558bec83e4f08b45080f28000f294130"),
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
        image.read_u32(0x0109CE2C + 13 * 4), 0x008DE970, "ModelObject slot 13"
    )
    require_equal(
        image.read_u32(0x0109CE2C + 17 * 4), 0x008DDAF0, "ModelObject slot 17"
    )
    require_equal(
        image.read_u32(0x0109CE2C + 25 * 4), 0x008DE790, "ModelObject slot 25"
    )
    require_equal(
        image.read_u32(0x0109CE2C + 26 * 4), 0x008DEC70, "ModelObject slot 26"
    )
    require_equal(
        image.read_u32(0x00FEA500 + 1 * 4),
        0x008C7F70,
        "RaptureModelObjectFactory slot 1",
    )
    require_equal(
        image.read_u32(0x010653A4 + 7 * 4),
        0x00A61620,
        "RaptureModelObject slot 7",
    )
    require_equal(
        image.read_u32(0x010653A4 + 13 * 4),
        0x008DE970,
        "RaptureModelObject slot 13",
    )
    require_equal(
        image.read_u32(0x010653A4 + 25 * 4),
        0x008DE790,
        "RaptureModelObject slot 25",
    )
    require_equal(
        image.read_u32(0x010653A4 + 26 * 4),
        0x008DEC70,
        "RaptureModelObject slot 26",
    )
    require_equal(image.read_u32(0x00FCF98C + 13 * 4), 0x006A3560, "NamePlate slot 13")
    require_equal(image.read_u32(0x00FCF98C + 2 * 4), 0x006A3AD0, "NamePlate slot 2")
    require_equal(image.read_u32(0x00FCF98C + 19 * 4), 0x006A2A60, "NamePlate slot 19")
    require_equal(image.read_u32(0x00FC0D34 + 86 * 4), 0x00A5FF60, "CharaActor slot 86")
    require_equal(image.read_u32(0x00FC0D34 + 68 * 4), 0x007CD360, "CharaActor slot 68")
    require_equal(image.read_u32(0x00FC0D34 + 32 * 4), 0x00A5F810, "CharaActor slot 32")
    require_equal(
        image.read_u32(0x00FEE17C + 7 * 4),
        0x00A67F80,
        "RaptureCharacterController slot 7",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 8 * 4),
        0x00A67FB0,
        "RaptureCharacterController slot 8",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 9 * 4),
        0x00A67FD0,
        "RaptureCharacterController slot 9",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 10 * 4),
        0x00A68000,
        "RaptureCharacterController slot 10",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 29 * 4),
        0x008D5570,
        "RaptureCharacterController slot 29",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 32 * 4),
        0x00A68060,
        "RaptureCharacterController slot 32",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 33 * 4),
        0x00A68070,
        "RaptureCharacterController slot 33",
    )
    require_equal(
        image.read_u32(0x00FEE17C + 34 * 4),
        0x00A680D0,
        "RaptureCharacterController slot 34",
    )
    require_equal(
        image.read_u32(0x00FEE210 + 1 * 4),
        0x007D8080,
        "RaptureCharacterProxy slot 1",
    )
    require_equal(
        image.read_u32(0x00FEE210 + 2 * 4),
        0x007D8E90,
        "RaptureCharacterProxy slot 2",
    )
    require_equal(
        image.read_u32(0x010653A4 + 16 * 4),
        0x008DDAB0,
        "RaptureModelObject slot 16",
    )
    require_equal(
        image.read_va(0x00F54F70, 4),
        bytes.fromhex("0000803f"),
        "RigidBody position W constant",
    )
    require_equal(
        image.read_va(0x00A61180, 8),
        bytes.fromhex("8b01ffa058010000"),
        "UPDATE_MODEL_TRANSFORM thunk",
    )
    require_equal(
        image.read_va(0x00A601DF, 7),
        bytes.fromhex("5f5e5b8be55dc20400")[:7],
        "UPDATE_MODEL_TRANSFORM epilogue prefix",
    )
    require_equal(
        image.read_va(0x00A601E5, 3),
        bytes.fromhex("c20400"),
        "UPDATE_MODEL_TRANSFORM RET 4",
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
    require_equal(
        image.read_va(0x00A60195, 59),
        bytes.fromhex(
            "837e180074348b4e188b018b5028ffd2837e0c0074348b460c8b4e188b388b01"
            "8d542470528b5074ffd28bc8e86a0f00008b4e0c508b4734ffd083"
        ),
        "fallback source and slot-13 call prefix",
    )
    require_equal(
        image.read_va(0x00A6114C, 12),
        bytes.fromhex("8b45080f29008be55dc20400"),
        "transform-source reader non-default return",
    )
    require_equal(
        image.read_va(0x00A61166, 12),
        bytes.fromhex("8b45080f29008be55dc20400"),
        "transform-source reader default return",
    )
    require_equal(
        image.read_va(0x007D8102, 27),
        bytes.fromhex("8d4c2417518d542420528d442420508d4c243c518bcee8c3f6ffff"),
        "proxy slot-1 segmented-displacement call",
    )
    require_equal(
        image.read_va(0x007D75B7, 33),
        bytes.fromhex(
            "f30f104c24640f57f60f2ff17618f30f10c90fc6c9000f59cb0f5cd10f29542454"
        ),
        "negative vector-projection removal through output store",
    )
    require_equal(
        image.read_va(0x007D7612, 57),
        bytes.fromhex(
            "f30f5cee0f296c2444f30f104424440fc6c0000f59c3f30f5adcf20f5cd9"
            "f20f5acbc6442414010fc6c9000f59c10f58c20f28d00f29542454"
        ),
        "thresholded record-vector correction through output store",
    )
    require_equal(
        image.read_va(0x007D776C, 20),
        bytes.fromhex("8b44241c50518d4c245c518bcbe852f9ffff84c0"),
        "recursive adjusted-displacement call",
    )
    require_equal(
        image.read_va(0x007D7799, 32),
        bytes.fromhex(
            "8b4c24200f28010f28088d5424440f58c1528bcf0f29442448e8a929320032c0"
        ),
        "current-plus-displacement RigidBody write",
    )
    transform_stores = bytes.fromhex("0f28000f2946500f2840100f2946600f2840200f294670")
    require_equal(
        image.read_va(0x008DEC9F, len(transform_stores)),
        transform_stores,
        "transform stores",
    )

    print(f"binary_sha256={digest}")
    print("actor_slot34=0x00A5F8A0 model_position_record=ModelObject+0x30")
    print("model_update=0x00A5FF60 ret=4 fallback=0x00A60195")
    print("model_slot13=0x008DE970 model_slot26=0x008DEC70")
    print("model_slot7=0x00A61620 drawable_publish=0x00BB7550")
    print("actor_slot68=0x007CD360 rapture_controller_vtable=0x00FEE17C")
    print("controller_slot10=0x00A68000 controller_slot29=0x008D5570")
    print("rapture_proxy_slot1=0x007D8080 rigidbody_writer=0x00AFA160")
    print("proxy_segment_dispatch=0x007D77E0 vector_resolver=0x007D70D0")
    print("retained_y_writer_call=0x007D77B2 return=0x007D77B7")
    print("nameplate_slot13=0x006A3560")


if __name__ == "__main__":
    main()
