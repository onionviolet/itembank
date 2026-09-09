"""A bounded, source-grounded payload builder for the competition prototype.

Adapted from DeepTutor's ``deeptutor.reading._grounding`` at revision
7a96bba1ae03401644c17763a2411c28aff3dcc9. This prototype adds duplicate
selection rejection, rights gates, and source-revision verification.

It never reads files, calls a model, writes evidence, or assigns a score.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
from typing import Any
from urllib.parse import urlsplit

MAX_UNIT_CHARS = 60_000
MAX_SELECTION_CHARS = 6_000
MAX_WINDOW_CHARS = 6_000


class GroundingCode:
    OK = "ok"
    READ_NOT_ALLOWED = "read_not_allowed"
    REMOTE_PROCESS_NOT_ALLOWED = "remote_process_not_allowed"
    REMOTE_TARGET_NOT_ALLOWED = "remote_target_not_allowed"
    INVALID_REMOTE_TARGET = "invalid_remote_target"
    INVALID_INPUT = "invalid_input"
    INVALID_SOURCE = "invalid_source"
    STALE_REVISION = "stale_revision"
    UNIT_TOO_LARGE = "unit_too_large"
    SELECTION_TOO_LARGE = "selection_too_large"
    EMPTY_SELECTION = "empty_selection"
    UNMATCHED_SELECTION = "unmatched_selection"
    AMBIGUOUS_SELECTION = "ambiguous_selection"
    INVALID_SELECTION_RANGE = "invalid_selection_range"


@dataclass(frozen=True)
class GroundingResult:
    """An explicit result. A failed result never contains a payload."""

    code: str
    payload: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return self.code == GroundingCode.OK


def normalized_with_map(value: str) -> tuple[str, list[int]]:
    """Collapse whitespace while retaining each normalized character's source index."""
    normalized: list[str] = []
    source_positions: list[int] = []
    for index, character in enumerate(value):
        if character.isspace():
            if normalized and normalized[-1] != " ":
                normalized.append(" ")
                source_positions.append(index)
            continue
        normalized.append(character)
        source_positions.append(index)
    if normalized and normalized[-1] == " ":
        normalized.pop()
        source_positions.pop()
    return "".join(normalized), source_positions


def source_fingerprint(text: str) -> str:
    """Return the SHA-256 fingerprint for the trusted UTF-8 source unit."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _all_indexes(haystack: str, needle: str) -> list[int]:
    indexes: list[int] = []
    start = 0
    while True:
        found = haystack.find(needle, start)
        if found < 0:
            return indexes
        indexes.append(found)
        start = found + 1


def selection_ranges(text: str, selection: str) -> list[tuple[int, int]]:
    """Return every canonical span matching selection, including normalized matches."""
    if not selection:
        return []
    normalized_text, positions = normalized_with_map(text)
    normalized_selection, _ = normalized_with_map(selection)
    if not normalized_selection:
        return []
    ranges = []
    for start in _all_indexes(normalized_text, normalized_selection):
        end_index = start + len(normalized_selection) - 1
        if end_index < len(positions):
            ranges.append((positions[start], positions[end_index] + 1))
    return ranges


def _window(text: str, start: int, end: int) -> tuple[int, int]:
    """Return source-relative code-point offsets for a bounded selected window."""
    if len(text) <= MAX_WINDOW_CHARS:
        return 0, len(text)
    midpoint = (start + end) // 2
    window_start = max(0, midpoint - MAX_WINDOW_CHARS // 2)
    window_end = min(len(text), window_start + MAX_WINDOW_CHARS)
    window_start = max(0, window_end - MAX_WINDOW_CHARS)
    return window_start, window_end


def _is_absolute_http_url(value: str) -> bool:
    """Accept an exact absolute HTTP(S) URL without normalizing it."""
    if not value or any(character.isspace() for character in value):
        return False
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
        and not parsed.fragment
    )


def build_grounded_payload(
    *,
    trusted_text: str,
    source_id: str,
    locator: str,
    revision: str,
    expected_fingerprint: str,
    selection: str,
    allow_read: bool = False,
    allow_remote_process: bool = False,
    remote_target: str | None = None,
    approved_remote_targets: tuple[str, ...] | list[str] = (),
    selection_start: int | None = None,
    selection_end: int | None = None,
) -> GroundingResult:
    """Build a bounded payload only from caller-supplied, already trusted text.

    ``expected_fingerprint`` must be the SHA-256 of ``trusted_text`` encoded as
    UTF-8. A remote target must be an exact member of an operation-scoped,
    approved target collection. No target means no remote egress, even if an
    operation has remote-process authority.
    """
    text_fields = (trusted_text, source_id, locator, revision, expected_fingerprint, selection)
    if not all(isinstance(value, str) for value in text_fields):
        return GroundingResult(GroundingCode.INVALID_INPUT)
    if remote_target is not None and not isinstance(remote_target, str):
        return GroundingResult(GroundingCode.INVALID_INPUT)
    if not isinstance(approved_remote_targets, (tuple, list)) or not all(
        isinstance(target, str) and _is_absolute_http_url(target)
        for target in approved_remote_targets
    ):
        return GroundingResult(GroundingCode.INVALID_INPUT)
    if not all(
        isinstance(value, bool)
        for value in (allow_read, allow_remote_process)
    ):
        return GroundingResult(GroundingCode.INVALID_INPUT)
    if (selection_start is not None and (isinstance(selection_start, bool) or not isinstance(selection_start, int))) or (
        selection_end is not None and (isinstance(selection_end, bool) or not isinstance(selection_end, int))
    ):
        return GroundingResult(GroundingCode.INVALID_SELECTION_RANGE)
    if len(expected_fingerprint) != 64 or any(char not in "0123456789abcdef" for char in expected_fingerprint.lower()):
        return GroundingResult(GroundingCode.INVALID_INPUT)
    if not allow_read:
        return GroundingResult(GroundingCode.READ_NOT_ALLOWED)
    if remote_target is not None:
        if not _is_absolute_http_url(remote_target):
            return GroundingResult(GroundingCode.INVALID_REMOTE_TARGET)
        if not allow_remote_process:
            return GroundingResult(GroundingCode.REMOTE_PROCESS_NOT_ALLOWED)
        if remote_target not in approved_remote_targets:
            return GroundingResult(GroundingCode.REMOTE_TARGET_NOT_ALLOWED)
    if not all(value for value in (source_id, locator, revision)):
        return GroundingResult(GroundingCode.INVALID_SOURCE)
    if not hmac.compare_digest(source_fingerprint(trusted_text), expected_fingerprint):
        return GroundingResult(GroundingCode.STALE_REVISION)
    if len(trusted_text) > MAX_UNIT_CHARS:
        return GroundingResult(GroundingCode.UNIT_TOO_LARGE)
    if len(selection) > MAX_SELECTION_CHARS:
        return GroundingResult(GroundingCode.SELECTION_TOO_LARGE)
    if not selection.strip():
        return GroundingResult(GroundingCode.EMPTY_SELECTION)

    ranges = selection_ranges(trusted_text, selection)
    if not ranges:
        return GroundingResult(GroundingCode.UNMATCHED_SELECTION)
    positions_given = selection_start is not None or selection_end is not None
    if positions_given:
        if selection_start is None or selection_end is None:
            return GroundingResult(GroundingCode.INVALID_SELECTION_RANGE)
        if (selection_start, selection_end) not in ranges:
            return GroundingResult(GroundingCode.INVALID_SELECTION_RANGE)
        start, end = selection_start, selection_end
    elif len(ranges) != 1:
        return GroundingResult(GroundingCode.AMBIGUOUS_SELECTION)
    else:
        start, end = ranges[0]
    if end - start > MAX_SELECTION_CHARS:
        return GroundingResult(GroundingCode.SELECTION_TOO_LARGE)

    window_start, window_end = _window(trusted_text, start, end)
    payload: dict[str, Any] = {
        "source_id": source_id,
        "locator": locator,
        "revision": revision,
        "source_fingerprint": expected_fingerprint,
        "selection": trusted_text[start:end],
        "selection_start": start,
        "selection_end": end,
        "window_start": window_start,
        "window_end": window_end,
        "surrounding_context": trusted_text[window_start:window_end],
    }
    if remote_target is not None:
        payload["remote_target"] = remote_target
    return GroundingResult(GroundingCode.OK, payload)
