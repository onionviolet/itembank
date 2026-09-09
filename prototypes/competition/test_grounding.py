"""Stdlib tests for the isolated source-grounding prototype."""

from __future__ import annotations

import unittest

from grounding import (
    GroundingCode,
    MAX_SELECTION_CHARS,
    MAX_UNIT_CHARS,
    MAX_WINDOW_CHARS,
    build_grounded_payload,
    source_fingerprint,
)


class GroundingTests(unittest.TestCase):
    def build(self, text: str, selection: str, **changes):
        args = {
            "trusted_text": text,
            "source_id": "source-1",
            "locator": "chapter-1#p2",
            "revision": "revision-1",
            "expected_fingerprint": source_fingerprint(text),
            "selection": selection,
            "allow_read": True,
        }
        args.update(changes)
        return build_grounded_payload(**args)

    def test_builds_payload_from_a_single_verified_selection(self):
        result = self.build("Before verified phrase after.", "verified phrase")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["selection"], "verified phrase")
        self.assertEqual(result.payload["locator"], "chapter-1#p2")

    def test_stale_fingerprint_returns_no_payload(self):
        result = self.build("Trusted source.", "Trusted", expected_fingerprint="0" * 64)
        self.assertEqual(result.code, GroundingCode.STALE_REVISION)
        self.assertIsNone(result.payload)

    def test_read_right_is_required(self):
        result = self.build("Trusted source.", "Trusted", allow_read=False)
        self.assertEqual(result.code, GroundingCode.READ_NOT_ALLOWED)
        self.assertIsNone(result.payload)

    def test_remote_process_right_is_required_for_a_remote_target(self):
        target = "https://provider.example/process"
        result = self.build(
            "Trusted source.", "Trusted", remote_target=target, approved_remote_targets=(target,)
        )
        self.assertEqual(result.code, GroundingCode.REMOTE_PROCESS_NOT_ALLOWED)

    def test_remote_target_must_be_an_exact_approved_member(self):
        allowed = "https://provider.example/process"
        result = self.build(
            "Trusted source.", "Trusted", remote_target="https://other.example/process",
            allow_remote_process=True, approved_remote_targets=(allowed,),
        )
        self.assertEqual(result.code, GroundingCode.REMOTE_TARGET_NOT_ALLOWED)

    def test_remote_target_is_recorded_only_when_approved(self):
        target = "https://provider.example/process"
        result = self.build(
            "Trusted source.", "Trusted", remote_target=target, allow_remote_process=True,
            approved_remote_targets=[target],
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["remote_target"], target)

    def test_malformed_remote_target_is_rejected_without_normalization(self):
        result = self.build(
            "Trusted source.", "Trusted", remote_target="provider.example/process",
            allow_remote_process=True, approved_remote_targets=("https://provider.example/process",),
        )
        self.assertEqual(result.code, GroundingCode.INVALID_REMOTE_TARGET)

    def test_whitespace_normalized_selection_maps_to_exact_canonical_span(self):
        text = "before\n\tverified   phrase after"
        result = self.build(text, "verified phrase")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["selection"], "verified   phrase")

    def test_duplicate_selection_requires_explicit_valid_span(self):
        text = "first repeated phrase, then repeated phrase"
        result = self.build(text, "repeated phrase")
        self.assertEqual(result.code, GroundingCode.AMBIGUOUS_SELECTION)
        second = text.rfind("repeated phrase")
        selected = self.build(
            text, "repeated phrase", selection_start=second,
            selection_end=second + len("repeated phrase"),
        )
        self.assertTrue(selected.ok)
        self.assertEqual(selected.payload["selection_start"], second)

    def test_whitespace_variant_duplicates_also_require_disambiguation(self):
        text = "one repeated phrase, then repeated   phrase"
        result = self.build(text, "repeated phrase")
        self.assertEqual(result.code, GroundingCode.AMBIGUOUS_SELECTION)

    def test_explicit_span_must_match_a_canonical_occurrence(self):
        result = self.build(
            "one selected phrase", "selected phrase", selection_start=0, selection_end=15
        )
        self.assertEqual(result.code, GroundingCode.INVALID_SELECTION_RANGE)
        self.assertIsNone(result.payload)

    def test_boolean_offsets_are_not_valid_integer_ranges(self):
        result = self.build(
            "one selected phrase", "selected phrase", selection_start=False, selection_end=19
        )
        self.assertEqual(result.code, GroundingCode.INVALID_SELECTION_RANGE)

    def test_invalid_input_types_fail_before_hash_or_length_operations(self):
        result = build_grounded_payload(
            trusted_text=object(), source_id="source", locator="locator", revision="revision",
            expected_fingerprint="f" * 64, selection="phrase", allow_read=True,
        )
        self.assertEqual(result.code, GroundingCode.INVALID_INPUT)
        bad_fingerprint = self.build("Stored phrase.", "phrase", expected_fingerprint="é" * 64)
        self.assertEqual(bad_fingerprint.code, GroundingCode.INVALID_INPUT)

    def test_unmatched_and_whitespace_only_selections_fail(self):
        self.assertEqual(self.build("Stored text.", "forged").code, GroundingCode.UNMATCHED_SELECTION)
        self.assertEqual(self.build("Stored text.", " \n\t").code, GroundingCode.EMPTY_SELECTION)

    def test_late_selection_stays_inside_the_bounded_window(self):
        text = "prefix " * 4_000 + "verified phrase" + " suffix" * 4_000
        result = self.build(text, "verified phrase")
        self.assertTrue(result.ok)
        self.assertEqual(len(result.payload["surrounding_context"]), MAX_WINDOW_CHARS)
        self.assertIn("verified phrase", result.payload["surrounding_context"])

    def test_window_offsets_match_the_canonical_source_slice(self):
        text = "before " * 2_000 + "verified phrase" + " after" * 2_000
        result = self.build(text, "verified phrase")
        self.assertTrue(result.ok)
        payload = result.payload
        self.assertEqual(
            payload["surrounding_context"], text[payload["window_start"] : payload["window_end"]]
        )
        self.assertLessEqual(payload["window_start"], payload["selection_start"])
        self.assertGreaterEqual(payload["window_end"], payload["selection_end"])

    def test_window_offsets_cover_near_start_and_near_end_selections(self):
        text = "start phrase " + ("middle " * 7_000) + "end phrase"
        for selection in ("start phrase", "end phrase"):
            result = self.build(text, selection)
            self.assertTrue(result.ok)
            payload = result.payload
            self.assertEqual(
                payload["surrounding_context"], text[payload["window_start"] : payload["window_end"]]
            )
            self.assertLessEqual(payload["window_start"], payload["selection_start"])
            self.assertGreaterEqual(payload["window_end"], payload["selection_end"])

    def test_huge_unit_and_huge_selection_fail(self):
        huge_unit = "x" * (MAX_UNIT_CHARS + 1)
        self.assertEqual(self.build(huge_unit, "x").code, GroundingCode.UNIT_TOO_LARGE)
        text = "a" * (MAX_SELECTION_CHARS + 1)
        self.assertEqual(self.build(text, text).code, GroundingCode.SELECTION_TOO_LARGE)

    def test_short_normalized_selection_cannot_expand_past_window_cap(self):
        text = "a" + (" " * (MAX_SELECTION_CHARS + 1)) + "b"
        result = self.build(text, "a b")
        self.assertEqual(result.code, GroundingCode.SELECTION_TOO_LARGE)

    def test_payload_never_contains_scoring_fields(self):
        result = self.build("Before verified phrase after.", "verified phrase")
        self.assertTrue(result.ok)
        forbidden = {"score", "correct", "answer_key", "evidence", "grade"}
        self.assertTrue(forbidden.isdisjoint(result.payload))


if __name__ == "__main__":
    unittest.main()
