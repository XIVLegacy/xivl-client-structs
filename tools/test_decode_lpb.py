#!/usr/bin/env python3
"""Tests for tools/decode_lpb.py.

Covers:
    1. rlu\\x0b uncompressed wrapper: 8-byte header strip.
    2. rle\\x0c XOR-0x73 wrapper: bytes 13-15 deobfuscated as the \\x1bLu
       Lua-signature prefix, bytes 16.. deobfuscated as the rest of the
       Lua bytecode.
    3. Filename cipher involution + two known fixtures from the upstream
       decode_lpb.py docstring:
            ZoneMoveProgTest <-> kvw5xvo5usv3q5rq (16/16)
            Man0g0           <-> x9wj3j           (6/6)

Run:
    python tools\\test_decode_lpb.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from decode_lpb import decode_lpb, encode_filename, decode_filename  # noqa: E402


class DecodeLpbWrapperTests(unittest.TestCase):
    def test_rlu_passthrough_strips_8_byte_header(self):
        # rlu\x0b + 4 reserved bytes (total 8) followed by arbitrary bytecode.
        header = b"rlu\x0b" + b"\x00\x00\x00\x00"
        body = b"\x1bLuaQ\x00\x01\x04\x04\x04\x08\x00"
        out = decode_lpb(header + body)
        self.assertEqual(out, body)

    def test_rle_xor_recovers_lua_prefix_and_body(self):
        # 13 leading bytes of header are not used by the decoder.
        # Bytes 13-15 hold the XOR-encoded `\x1bLu` prefix.
        # Bytes 16.. hold the XOR-encoded rest of the bytecode.
        clear_prefix = b"\x1bLu"
        clear_body = b"aQ\x00\x01\x04\x04\x04\x08\x00"
        encoded_prefix = bytes(b ^ 0x73 for b in clear_prefix)
        encoded_body = bytes(b ^ 0x73 for b in clear_body)
        header_leader = b"rle\x0c" + b"\x00" * 9  # 13 bytes total
        out = decode_lpb(header_leader + encoded_prefix + encoded_body)
        self.assertEqual(out, clear_prefix + clear_body)

    def test_unknown_magic_returns_none(self):
        self.assertIsNone(decode_lpb(b"junkjunkjunkjunk"))

    def test_rle_xor_matches_known_decoded_prefix_literal(self):
        # The docstring states: encoded `ff 68 3f 06` at bytes 13..16 decodes
        # to `8c 1b 4c 75`; bytes 14..16 of that = `\x1bLu` (Lua signature).
        encoded_quad = bytes.fromhex("ff 68 3f 06".replace(" ", ""))
        decoded_quad = bytes(b ^ 0x73 for b in encoded_quad)
        self.assertEqual(decoded_quad, bytes.fromhex("8c 1b 4c 75".replace(" ", "")))
        self.assertEqual(decoded_quad[1:4], b"\x1bLu")


class FilenameCipherTests(unittest.TestCase):
    def test_known_fixture_zone_move_prog_test(self):
        self.assertEqual(encode_filename("ZoneMoveProgTest"), "kvw5xvo5usv3q5rq")

    def test_known_fixture_man0g0(self):
        self.assertEqual(encode_filename("Man0g0"), "x9wj3j")

    def test_involution_alphabet(self):
        for c in "abcdefghijklmnopqrstuvwxyz0123456789":
            self.assertEqual(encode_filename(encode_filename(c)), c)

    def test_involution_compound(self):
        for sample in ["ZoneMoveProgTest", "Man0g0", "OpeningDirector", "abc123"]:
            self.assertEqual(encode_filename(encode_filename(sample)), sample.lower())

    def test_decode_filename_is_alias(self):
        self.assertEqual(decode_filename("kvw5xvo5usv3q5rq"), "zonemoveprogtest")

    def test_non_alphanum_passthrough(self):
        self.assertEqual(encode_filename("a-b_c.d"), encode_filename("a") + "-" + encode_filename("b") + "_" + encode_filename("c") + "." + encode_filename("d"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
