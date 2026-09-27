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
            0x0093F9CC,
            "56e85efdffff8baea00000008bf88b86a40000008b98a0000000e83548030085c0740c8b1057538bc88b420c55ffd0",
            "Visual child, parent and preceding peer publication",
        ),
        (
            0x0054BBB0,
            "83ec0c8b5424108b442414895424046a0c8d542404894424048b44241c526a2189442414e8f7f4ffff83c40cc20c00",
            "visual context parent operation publication",
        ),
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
        (0x00FA2D8C, 3, 0x0054BBB0),
        (0x00FA28E4, 13, 0x0055A000),
        (0x00FA28E4, 41, 0x0055A650),
        (0x00FA28E4, 47, 0x0055A5A0),
        (0x00FA28E4, 49, 0x0055A620),
        (0x00FF1CC4, 42, 0x007F8C60),
        (0x00FF1CC4, 94, 0x007CD090),
        (0x00FF1CC4, 95, 0x007CD1A0),
        (0x00FF1CC4, 135, 0x007F9D00),
        (0x00FF1CC4, 141, 0x007F8C10),
        (0x00FF1CC4, 157, 0x007FA2B0),
    ):
        require_equal(
            image.read_u32(vtable + slot * 4),
            target,
            f"vtable 0x{vtable:08X} slot {slot}",
        )
    anchor_producer_anchors = (
        (
            0x007F95A0,
            "558bec83e4f06aff6883ceea0064a1000000005083ec2853",
            "WindowActor constructor entry",
        ),
        (
            0x007F8D20,
            "558bec83e4f083ec34a1b0a82e0133c48944243053568bf1",
            "WindowActor anchor producer entry",
        ),
        (
            0x007F9D00,
            "83ec085356578b3d5ce5f3008bf1ffd72b86300100006a00",
            "WindowActor anchor tick entry and timer read",
        ),
        (
            0x007F8C10,
            "51568bf18b8ea401000085c9743c8a86c0010000d0e88d542407240152884424",
            "WindowActor deferred-operation producer entry",
        ),
        (
            0x007F8C36,
            "f686c001000002741b807c24070074146a006a006a2a8bcee85d5bfdff80a6c0010000fd",
            "WindowActor operation 0x2A submission and state clear",
        ),
        (
            0x007CCAF0,
            "8bc18b4c24088b11568b742408508b826c01000056ffd0",
            "scene-actor attachment slot-91 dispatch",
        ),
        (
            0x007CCBC0,
            "558bec83e4f083ec5ca1b0a82e0133c4894424588b4d0c8b45108b118b927801",
            "scene-actor secondary slot-94 dispatch entry",
        ),
        (
            0x007CD090,
            "8b018b5064568b7424086a0056ffd28bc65ec20c00",
            "generic scene-actor slot-94 index-0 path",
        ),
        (
            0x007CD1A0,
            "568b7424086a0056e8432d29008bc65ec20800",
            "generic scene-actor slot-95 index-0 path",
        ),
        (
            0x00855150,
            "8bc18b4c24048988e4000000c20400",
            "Chara attachment-helper owner store",
        ),
        (
            0x0055A5A0,
            "535657e838f8ffff8b5c24108bcb8bf0",
            "DrawingToolContext selector writer entry",
        ),
        (
            0x0055A5B5,
            "8dbe88030000660fefc0660fd6078bcb660fd64708e841aceeff6a0f506a1057e8a7054800804e5a08",
            "DrawingToolContext selector copy and dirty-bit writer",
        ),
        (
            0x0055A650,
            "e88bf7ffff80485b02c6405c01c3",
            "DrawingToolContext deferred-state dirty writer",
        ),
        (
            0x0054EFB9,
            "f6465a08742a85c90f842b0100006a108d9688030000526a1ee8f9c0ffff3c010f851301000080665af78b0da86b3301",
            "cached selector operation 0x1E submission",
        ),
        (
            0x0054F06C,
            "f6465b02742185c90f84780000006a006a006a29e84bc0ffff3c01756980665bfd8b0da8",
            "cached deferred operation 0x29 submission",
        ),
        (
            0x0055EE60,
            "83ec108b442414f30f7e00660fd60424f30f7e40086a108d442404506a1b660fd6442414e8f78af7ff83c410c20400",
            "generic operation 0x1B emitter complete body",
        ),
        (
            0x0055C970,
            "6a006a006a1ce805b0f7ffc3",
            "generic operation 0x1C emitter complete body",
        ),
        (
            0x0055C980,
            "6a006a006a1de8f5aff7ffc3",
            "generic operation 0x1D emitter complete body",
        ),
        (
            0x00664A4C,
            "8d8e3c140000e809071f00",
            "Chara attachment-table refresh call",
        ),
        (
            0x00664B44,
            "8d9e601900000f284424206a016a008d4c241851578bcb0f29442420e80b1d1e006a01578bcbe8711b1e0083c70183ff077cd3",
            "Chara owner attachment-record refresh loop",
        ),
        (
            0x007F9175,
            "0f284424240f58c1f30f100d704ff5000f28d00fc6c9000f15c10fc6d0c40f29542424f30f10442424f30f11442414f30f10442428f30f11442418f30f1044242c8d442414f30f1144241cf30f1044243050f30f11442424e83eac4a00",
            "anchor offset addition, W force and publication call",
        ),
    )
    for va, expected_hex, label in anchor_producer_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    attachment_name_tables = {
        0x012D1380: (
            0x01043310,
            0x01043304,
            0x010432F8,
            0x010432EC,
            0x010432E0,
            0x010432D4,
            0x010432C8,
            0x010432BC,
            0x010432B0,
            0x010432A4,
            0x01043298,
            0x0104328C,
            0x01043280,
            0x01043274,
            0x01043268,
            0x0104325C,
        ),
        0x012D13C0: (
            0x01043250,
            0x01043244,
            0x01043238,
            0x0104322C,
            0x01043220,
            0x01043214,
            0x01043208,
            0x010431FC,
            0x010431F0,
            0x010431E8,
            0x010431E0,
            0x010431D8,
            0x010431D0,
            0x010431C8,
            0x010431C0,
            0x010431B8,
            0x010431B0,
            0x010431A8,
            0x010431A0,
            0x01043198,
            0x01043190,
            0x01043188,
            0x01043180,
            0x01043178,
            0x01043170,
            0x01043168,
            0x01043160,
            0x01043158,
            0x01043150,
            0x01043148,
            0x01043140,
            0x01043138,
            0x01043130,
            0x01043128,
            0x01043120,
            0x01043118,
            0x01043110,
            0x01043108,
            0x01043100,
            0x010430F0,
            0x010430E0,
        ),
    }
    for table_va, expected_pointers in attachment_name_tables.items():
        actual_pointers = tuple(
            image.read_u32(table_va + index * 4)
            for index in range(len(expected_pointers))
        )
        require_equal(
            actual_pointers,
            expected_pointers,
            f"attachment-name table 0x{table_va:08X}",
        )
    attachment_names = {
        0x012D1380: (
            "EID_DAM_N",
            "EID_DAM_NNE",
            "EID_DAM_NE",
            "EID_DAM_NEE",
            "EID_DAM_E",
            "EID_DAM_SEE",
            "EID_DAM_SE",
            "EID_DAM_SSE",
            "EID_DAM_S",
            "EID_DAM_SSW",
            "EID_DAM_SW",
            "EID_DAM_SWW",
            "EID_DAM_W",
            "EID_DAM_NWW",
            "EID_DAM_NW",
            "EID_DAM_NNW",
        ),
        0x012D13C0: (
            "EID_NONE",
            "EID_L_FOOT",
            "EID_R_FOOT",
            "EID_L2_FOOT",
            "EID_R2_FOOT",
            "EID_L3_FOOT",
            "EID_R3_FOOT",
            "EID_L4_FOOT",
            "EID_R4_FOOT",
            *(f"EID_V{index:02d}" for index in range(1, 31)),
            "EID_SE_FOOT_R",
            "EID_SE_FOOT_L",
        ),
    }
    for table_va, expected_names in attachment_names.items():
        for index, expected_name in enumerate(expected_names):
            name_va = image.read_u32(table_va + index * 4)
            expected = expected_name.encode("ascii") + b"\0"
            require_equal(
                image.read_va(name_va, len(expected)),
                expected,
                f"attachment name {expected_name}",
            )
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
    consumer_anchors = (
        (0x007FA2B0, "558bec83e4f86aff6860cfea00", "WindowActor dispatcher entry"),
        (0x007FA916, "c20c00", "WindowActor dispatcher RET 12"),
        (0x007FA703, "8b5d0c8d530452b9a4e03401e8eca5e9ff8938", "association map value"),
        (0x007FA759, "89b8a4010000894774", "actor and context reciprocal stores"),
        (
            0x007FA59A,
            "8b400456508986a0010000e866fcffff83c408",
            "selected context store",
        ),
        (
            0x007FA504,
            "85ff741185f6740d8b54241052568bcfe8273f0d00",
            "resolved parent and child context attachment",
        ),
        (
            0x007FA8EA,
            "8bb6a00100003bf374108b55108b450c52508bce57e85c430d00",
            "selected context forwarding",
        ),
        (
            0x008CEC60,
            "558bec83e4f88b450881ec74020000538bd9808b2801000002",
            "context dispatcher entry and flag",
        ),
        (
            0x008CF0A9,
            "8b450cf30f7e008b4008660fd644242cf30f1044242cf30f114328f30f1044243089442434f30f11432cf30f10442434f30f114330c6832d01000001c6832c010000015f5e5b8be55dc20c00",
            "operation 0E triplet copy and RET 12",
        ),
        (0x008CD700, "558bec83e4f06aff68a532ec00", "derived processor entry"),
        (
            0x008CE440,
            "83ec08538b5c241055568bf18b4b7085c957740653",
            "WindowContext child attachment entry",
        ),
        (
            0x008CE4F1,
            "895c2430e8861700008b4b7485c9b00189737088832c01000088832d010000",
            "WindowContext child parent store and dirty flags",
        ),
        (
            0x008CD765,
            "8a9e2d0100008a8e2c0100000a5d100a45140a4d1884db88442434885c2438c6862d01000000884c2430c6862c01000000",
            "selector combination and state clear",
        ),
        (
            0x008CDA9E,
            "8b467085c07514d94628d95e34d9462cd95e38d94630d95e3ceb9c",
            "parent guard and derived triplet copy",
        ),
        (0x008CDDE5, "c21400", "derived processor RET 20"),
        (0x008CE7D0, "81ec88000000568bf18b4e74", "context draw entry"),
        (
            0x008CE9C4,
            "837e20007506837e240074068b4e2451eb0d8d542458528bcee87e0e0000508d4c241ce874b1b4ff",
            "draw record selection and helper call",
        ),
        (0x008CEBB4, "c20400", "context draw RET 4"),
        (0x008CEBCF, "c20400", "context draw alternate RET 4"),
    )
    for va, expected_hex, label in consumer_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    require_equal(
        image.read_u32(0x00FF1CC4 + 0x274), 0x007FA2B0, "WindowActor slot 157"
    )
    require_equal(
        image.read_u32(0x008CF3B8 + 4 * 0x0E), 0x008CF0A9, "context operation 0E"
    )
    report_anchors = (
        (
            0x0054F019,
            "f6465a20741d85c974196a006a006a20e8a2c0ffff3c01750480665adf",
            "slot-49 flag publication",
        ),
        (0x008CF3A8, "c6833001000001", "operation 20 report enable"),
        (0x008CEB37, "80be300100000074078bcee8e9d8ffff", "draw-time report dispatch"),
        (0x008CEBB7, "80be300100000074078bcee849d2ffff", "non-drawing report dispatch"),
        (0x008CC430, "558bec83e4f081ec78020000", "context actor-report entry"),
        (
            0x008CC450,
            "8bc685c0740c8b487485c98b407074f2eb0885c90f8467050000",
            "parent walk to associated actor",
        ),
        (
            0x007F8CC0,
            "8b81ac0100008b89180100005083c154e87b74faffc3",
            "associated actor resolution",
        ),
        (
            0x008CC9C2,
            "8d842490010000508bcfe82f15d9ff",
            "stack payload and CharaActor ECX report",
        ),
        (0x008CC9E4, "c3", "context actor-report plain RET"),
        (
            0x0065DF00,
            "8b4424046a20506a4fe8a2081700c20400",
            "operation 4F producer complete body",
        ),
        (
            0x0058E504,
            "f30f7e07660fd68644020000f30f7e4708660fd6864c020000f30f7e4710660fd68654020000f30f7e4718660fd6865c020000",
            "operation 4F receiver 32-byte copy",
        ),
    )
    for va, expected_hex, label in report_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    require_equal(
        image.read_u32(0x008CF3B8 + 4 * 0x20), 0x008CF3A8, "context operation 20"
    )
    require_equal(
        image.read_u32(0x0058E6B0 + 4 * (0x4F - 0x4A)),
        0x0058E504,
        "element operation 4F",
    )
    command_draw_anchors = (
        (0x008CE530, "558bec83e4f06aff68ad33ec00", "command-stream draw entry"),
        (
            0x008CE6C1,
            "8d8c249c000000518d4c243ce8ce92dcff",
            "stack-local record container binding",
        ),
        (
            0x008CE730,
            "8b542420f30f7e86000100008d0c3a660fd684247c010000f30f7e86080100008d54243852660fd684248801000089bc24740100008b018b40048d9424f000000052ffd003f8",
            "command ECX, explicit records and byte-cursor advancement",
        ),
        (0x008CE7C1, "c20400", "command-stream draw RET 4"),
    )
    for va, expected_hex, label in command_draw_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    primary_label_draw_anchors = (
        (0x006A4270, "8b44240483ec085356578d7104508d4c", "named TextBlock lookup"),
        (0x00955990, "6aff68a6deec0064a1000000005081ec", "TextBlock draw entry"),
        (
            0x00955D65,
            "8b3a50518d4c244c518d442460508d8c245c040000518bca8b5704c684246805000009ffd2",
            "TextBlock drawing-context slot 1 dispatch",
        ),
        (
            0x00559F00,
            "e8dbfeffff8bc8e9a438ffff",
            "DrawingToolContext slot 1 cached-record tail dispatch",
        ),
        (0x0054D7B0, "6aff682fb9e60064a1000000005081ec", "DrawText producer entry"),
        (
            0x0054DB71,
            "8b4c24548d879b00000083e0fc5068980000008d8424a800000050e82ff1ffff",
            "DrawText cached-record binding and fixed-record append",
        ),
        (0x00553F70, "6aff6828c9e60064a100000000505156", "DrawText constructor entry"),
        (
            0x00553F98,
            "c7008c28fa0033d2895424148b4c2430c700d029fa00",
            "DrawingBase then DrawText vtable stores",
        ),
        (0x0054CCC0, "568bf1f6465a405774138d4e60e81e06", "command-byte append entry"),
        (0x00697580, "81ecd0000000578bf980bf920000007f", "DrawText command consumer"),
        (0x00697170, "6aff6892d5e80064a1000000005083ec", "DrawText render preparation"),
        (
            0x00697338,
            "8b45008b5018578d4c2440518bcdffd2e9fe",
            "text-render object slot 6 dispatch",
        ),
        (
            0x0069753A,
            "8b4c24188b018b4018578d54244052ffd0c7",
            "alternate text-render object slot 6 dispatch",
        ),
    )
    for va, expected_hex, label in primary_label_draw_anchors:
        expected = bytes.fromhex(expected_hex)
        require_equal(image.read_va(va, len(expected)), expected, label)
    require_equal(
        image.read_u32(0x0106E840), 0x0117BD08, "TextBlock complete-object COL"
    )
    require_equal(image.read_u32(0x0117BD14), 0x012BD188, "TextBlock TypeDescriptor")
    require_equal(image.read_u32(0x0106E844 + 34 * 4), 0x00955990, "TextBlock slot 34")
    require_equal(
        image.read_u32(0x00FA28E4 + 1 * 4),
        0x00559F00,
        "DrawingToolContext slot 1",
    )
    require_equal(image.read_u32(0x00FA29D0 + 1 * 4), 0x00697580, "DrawText slot 1")
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
    print("anchor_producer=0x007F8D20 publication_call=0x007F91CD")
    print("anchor_target_helpers=0x007CCAF0,0x007CCBC0")
    print("anchor_state_ops=0x1B,0x1C,0x1D,0x1E,0x29")


if __name__ == "__main__":
    main()
