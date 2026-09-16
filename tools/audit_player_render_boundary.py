"""Verify pinned PE anchors for the player render-transform boundary."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from audit_shader_constant_task import PeImage, require_equal


EXPECTED_SHA256 = "9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9"

ENTRY_BYTES = {
    0x0092FD20: bytes.fromhex("6aff684baeec0064a1000000005083ec5453"),
    0x009302F0: bytes.fromhex("6aff6876aeec0064a1000000005083ec1453"),
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

    require_equal(image.read_u32(0x0106A0B8), 0x01179064, "Window COL pointer")
    require_equal(image.read_u32(0x01179068), 0, "Window complete-object offset")
    require_equal(image.read_u32(0x0117906C), 0, "Window construction displacement")
    require_equal(image.read_u32(0x01179070), 0x01269E20, "Window TypeDescriptor")
    require_equal(
        image.read_va(0x01269E28, 18),
        b".?AVWindow@Sqwt@@\0",
        "Window decorated RTTI name",
    )
    window_anchors = {
        0x00924724: "c706bca00601",
        0x00F21D80: "68fca80601b9f0873501e851eb9eff",
        0x00F21DB0: "680ca90601b910893501e821eb9eff",
        0x009300E8: "8dbeac01000033dbf6470410bdb0da9200",
        0x00930113: "8a4f04d9442420f6c1037431d907d9c1dae9dfe0f6c4447b24",
        0x0093012C: "6a01ddd968f0873501d91f535580c90456884f04578bcfe8583a0200",
        0x0093037A: "8db7ac01000033dbf6460410bdb0da9200",
        0x009303A3: "8a4e04f6c1037425d816dfe0f6c4447b1c6a01d91e",
        0x00930404: "8b4424385152508d4c2420518bcfe809f9ffff",
        0x009302BF: "c21000",
        0x0093043A: "c20400",
    }
    for va, hex_bytes in window_anchors.items():
        expected = bytes.fromhex(hex_bytes)
        require_equal(
            image.read_va(va, len(expected)), expected, f"Window anchor 0x{va:08X}"
        )
    require_equal(image.read_va(0x0106A8FC, 13), b"ActualHeight\0", "height name")
    require_equal(image.read_va(0x0106A90C, 12), b"ActualWidth\0", "width name")

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
    require_equal(
        image.read_va(0x00C579A0, 18),
        bytes.fromhex("558bec83e4f083ec108bc183a0a0000000bf"),
        "Drawable derived-flag update entry",
    )
    require_equal(image.read_u32(0x00FCF98C + 20 * 4), 0x006A2A80, "NamePlate slot 20")
    require_equal(image.read_u32(0x00FCF98C + 23 * 4), 0x006A2E60, "NamePlate slot 23")
    require_equal(
        image.read_va(0x006A2A80, 16),
        bytes.fromhex("0fb68190010000c1e802f7d083e001c3"),
        "NamePlate slot-20 state predicate",
    )
    require_equal(
        image.read_va(0x006A2E60, 34),
        bytes.fromhex(
            "568bf18b068b5050ffd284c074108b8694010000f30f2c80ac0100005ec333c05ec3"
        ),
        "NamePlate slot-23 opaque scalar getter",
    )
    require_equal(
        image.read_va(0x006A3E1A, 21),
        bytes.fromhex("8b86200100006860f5fc008d4c2438898694010000"),
        "NamePlate UI pointer alias publication",
    )
    require_equal(
        image.read_va(0x006A41D9, 3),
        bytes.fromhex("c20800"),
        "NamePlate constructor RET 8",
    )
    visual_offset_anchors = (
        (
            0x00939720,
            "8b542404d98178010000d9420c83ec08",
            "rectangle pair forwarding entry",
        ),
        (0x00939782, "e88969000083c408c20400", "rectangle pair call and RET 4"),
        (
            0x00940110,
            "8b44240c8b542408508b4424085268fc9735016800fe9300515083c124e8ae100000c20c00",
            "VisualOffset wrapper",
        ),
        (
            0x009411E0,
            "538b5c240c568bf1f6460810578b7c241c",
            "float-pair property setter entry",
        ),
        (
            0x00941210,
            "84d2740d84c0751180fa01750c84ca75125f5e32c05bc21800",
            "property rejection gates and RET 24",
        ),
        (
            0x00941253,
            "804e0804807c2424018b0189068b4904894e0475118b5424186a01575253568bcee857fbffff5f5eb0015bc21800",
            "pair stores, conditional notification and RET 24",
        ),
        (
            0x00F23210,
            "6898c40601b9fc973501e8c1d69effc7051098350100000000c3",
            "VisualOffset metadata initializer and ID zero",
        ),
        (0x0106C498, "56697375616c4f666673657400", "VisualOffset property name"),
        (0x00940DD0, "6aff68fbe8ec0064a10000000050", "pair notification entry"),
        (
            0x00940E55,
            "8d442414508bcfc78424a000000000000000ffd3",
            "owner-bound event callback call",
        ),
        (0x00940EA1, "c21400", "pair notification RET 20"),
        (
            0x0093FE00,
            "56578b7c240c8bf18b068b501857ffd2e82b44030084c00f85cd00000083bea0000000000f95c084c00f84bb0000008b47708b401483f80a0f87ac000000ff248540ff93008b8ea00000008b118b52348d462450ffd2",
            "callback guards, property dispatch and +0xA0 slot-13 call",
        ),
    )
    for va, expected_hex, label in visual_offset_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    require_equal(
        image.read_u32(0x0093FF40), 0x0093FE45, "VisualOffset ID-zero dispatch"
    )
    context_anchors = (
        (
            0x009741F0,
            "8bc1c70074350701a3acc23501c3",
            "base interface global publication",
        ),
        (0x00974220, "a1acc23501c3", "interface global getter"),
        (0x0054E1D8, "c7068c2dfa00c746046c2dfa00", "concrete interface vtables"),
        (
            0x0093EF90,
            "568bf1e88852030085c074128b8ea80000008b108b5204518bc8ffd25ec333c05ec3",
            "Visual context factory dispatch",
        ),
        (0x0093F880, "83ec08568bf1e8b5490300", "Visual context acquisition entry"),
        (
            0x0093F8B1,
            "8b068b50548bceffd285c08986a00000000f841a0200008b16508b42588bceffd0",
            "UI slot-21 result publication and slot-22 follow-up",
        ),
        (
            0x0093F8E9,
            "f6462c0474118b8ea00000008b018b40348d562452ffd0",
            "pending VisualOffset publication",
        ),
        (
            0x005522D0,
            "6aff68c9c3e60064a1000000005083ec08",
            "drawing context factory entry",
        ),
        (0x00552416, "c20400", "drawing context factory RET 4"),
        (0x004D7C10, "568bf1b9786b3301", "element creation entry"),
        (0x004D6750, "8b8188000000c3", "backing context getter"),
        (
            0x00553D90,
            "6aff68f8c8e60064a1000000005051",
            "DrawingToolContext constructor entry",
        ),
        (
            0x00553DC3,
            "8b54241880480c018948088b4c241cc700e428fa00895004890da86b3301",
            "context record initialization and concrete vtable",
        ),
        (0x00553DF8, "c20800", "DrawingToolContext constructor RET 8"),
        (
            0x00559DE0,
            "6aff68eb70e70064a100000000505156",
            "context record acquisition entry",
        ),
        (0x00559E50, "c3", "context record acquisition RET"),
        (
            0x0055A000,
            "e8dbfdffff8b4c2404f30f2c11f30f2ac2f30f1180a0000000f30f2c4904f30f2ac1f30f1180a40000000f57c080485a80f30f1180a8000000c6405c01c20400",
            "context slot-13 truncating pair setter",
        ),
        (
            0x006A34B0,
            "6aff68fbf0e80064a1000000005083ec58",
            "NamePlate primary-label initialization entry",
        ),
        (
            0x006A4090,
            "8bcee819f4ffff",
            "NamePlate constructor primary-label helper call",
        ),
        (
            0x006A351A,
            "8b4c24086a0068c8df260168e8dc26016a00e84fc3290050e8957133008b108bc88b82c400000083c414ffd0",
            "primary-label context acquisition, RTTI cast and slot-49 call",
        ),
        (0x0055A620, "e8bbf7ffff80485a20c6405c01c3", "context slot-49 record flags"),
    )
    for va, expected_hex, label in context_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    for vtable, slot, target in (
        (0x0106A0BC, 21, 0x0093EF90),
        (0x00FA2D8C, 1, 0x005522D0),
        (0x00FA28E4, 13, 0x0055A000),
        (0x00FA28E4, 49, 0x0055A620),
    ):
        require_equal(image.read_u32(vtable + slot * 4), target, f"context slot {slot}")
    publication_anchors = (
        (
            0x0054E890,
            "558bec83e4f081ecb4000000",
            "cached drawing record publisher entry",
        ),
        (
            0x0054E8AF,
            "8bf18b8ecc0300003b8ed0030000577404c6465c01807e5c00750c838604040000ffe91c080000c78604040000020000008b0da86b3301",
            "dirty state and reclamation-value prefix",
        ),
        (
            0x0054E8E0,
            "8b0da86b330185c98944242c0f84000800006a048d542430526a22e8d0c7ffff84c00f84ea070000",
            "context-item selection submission and prefix failure exit",
        ),
        (
            0x0054F03C,
            "f6465a80742a85c90f84a80000006a0c8d96a0000000526a0ee876c0ffff3c010f859000000080665a7f8b0da86b3301",
            "three-float publication and success-gated dirty-bit clear",
        ),
        (
            0x0054F0EE,
            "c6465c008b8604040000",
            "normal dirty-byte clear and full EAX result",
        ),
        (0x0054F10C, "c20400", "cached record publisher RET 4"),
        (0x005527A0, "5355568bf18b86300300008b5008", "context publication loop entry"),
        (
            0x00552836,
            "8b75008b4e0885c9742856e84ac0ffff85c07f1e8b7e0885ff74178bcfe8d89cffff57e8b9f2470083c404c7460800000000",
            "record ECX, explicit item, signed result and cache reclamation",
        ),
        (
            0x00552877,
            "5f5e5db0015bc3",
            "context publication loop AL-only result and RET",
        ),
        (0x0054B0D0, "558bec83e4f06aff", "internal scene submission helper entry"),
        (
            0x0054B115,
            "8bf18b4d0852508b463883c11551508d4c2424e8530ffaff",
            "scene type code plus 0x15 and builder call",
        ),
        (
            0x004DAB2D,
            "8b8f547d0100e8687c07008d4f105f5e5d83c408e93afbffff",
            "MainModule UI publication before container-update tail jump",
        ),
    )
    for va, expected_hex, label in publication_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
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
