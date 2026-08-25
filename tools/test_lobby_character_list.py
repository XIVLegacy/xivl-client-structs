from __future__ import annotations

import copy
import json
import unittest

from verify_lobby_character_list import FIXTURE, validate_fixture


class LobbyCharacterListFixtureTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assert_rejected(self, mutation, message="shape changed"):
        changed = copy.deepcopy(self.fixture)
        mutation(changed)
        with self.assertRaisesRegex(ValueError, message):
            validate_fixture(changed)

    def test_committed_fixture_is_valid(self):
        validate_fixture(self.fixture)

    def test_rejects_shifted_wire_length(self):
        self.assert_rejected(lambda value: value["characterList"].update(bodyLength=943))

    def test_rejects_shifted_record_stride(self):
        self.assert_rejected(lambda value: value["characterList"].update(entryStride=465))

    def test_rejects_changed_session_occurrence(self):
        self.assert_rejected(lambda value: value["sessions"][0].update(characterListOccurrenceCount=1))

    def test_rejects_changed_record_count(self):
        self.assert_rejected(lambda value: value["characterList"].update(recordCountReadByClient=2))

    def test_rejects_unterminated_append_string_observation(self):
        self.assert_rejected(
            lambda value: value["characterList"]["record"].update(
                appendCStringTerminatesWithinCopySource=False
            )
        )

    def test_rejects_sensitive_address(self):
        self.assert_rejected(
            lambda value: value["redactedClasses"].append("192.0.2.1"),
            "IPv4 address",
        )

    def test_rejects_raw_payload_key(self):
        self.assert_rejected(
            lambda value: value.update(payload="00"),
            "forbidden sensitive key",
        )


if __name__ == "__main__":
    unittest.main()
