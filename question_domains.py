"""Proposed exact domain normalizers, with no scoring or durable writes.

The runtime supplies its existing numeric parser and owns comparison, diagnostic
release and scoring. This module is not a registered authoring format until its
v1 declaration is reviewed and wired through the existing runtime.
"""
from dataclasses import dataclass
from fractions import Fraction
import re

VERSION = "exact-domains-v1"
LIMITS = {"characters": 4096, "scalar_characters": 128,
          "numerator": 10**6, "denominator": 10**6, "set_entries": 32,
          "interval_pieces": 8, "vector_entries": 8, "matrix_rows": 8,
          "matrix_columns": 8}
GRAMMARS = {
    "rational-set": "{a,b,...} or {}; exact rational numbers; order and duplicates ignored.",
    "rational-interval-set": "[a,b], (a,b], [a,b), (a,b), unions with U, or empty; infinite endpoints use -inf and inf with open brackets.",
    "rational-vector": "[a,b,...]; exact rational numbers in declared order and shape.",
    "rational-matrix": "[[a,b,...],[c,d,...],...]; rectangular exact rational rows in declared order and shape.",
}


class DomainRefusal(ValueError):
    """Unresolved input/configuration, never an incorrect or pending mark."""
    def __init__(self, state, message):
        self.state = state
        super().__init__(message)


def _refuse(state, message):
    raise DomainRefusal(state, message)


def _entry(raw):
    if not isinstance(raw, str) or not raw.strip():
        _refuse("invalid", "Enter a nonempty domain answer.")
    if len(raw) > LIMITS["characters"]:
        _refuse("unsupported", "Use at most 4096 characters.")
    if any(ord(c) < 32 or ord(c) == 127 for c in raw):
        _refuse("invalid", "Use one line without control characters.")
    if any(ord(c) > 126 for c in raw):
        _refuse("unsupported", "Use the declared ASCII domain notation.")
    return raw.strip()


def _scalar(raw, number_parser):
    raw = raw.strip()
    if not raw:
        _refuse("invalid", "Every component needs a number; blanks are not zero.")
    if len(raw) > LIMITS["scalar_characters"]:
        _refuse("unsupported", "Use at most 128 characters per number.")
    if re.search(r"[^0-9eE+./\-]", raw):
        _refuse("unsupported", "Use rational numeric literals without symbols or units.")
    try:
        value = number_parser(raw)
    except ValueError as exc:
        _refuse("invalid", str(exc))
    if not isinstance(value, Fraction):
        _refuse("error", "Numeric parser failed; preserve input and retry.")
    if abs(value.numerator) > LIMITS["numerator"] or value.denominator > LIMITS["denominator"]:
        _refuse("unsupported", "Reduced numerator and denominator must be at most 1000000.")
    return value


def _components(body, maximum, number_parser, empty=False):
    if not body.strip():
        if empty:
            return ()
        _refuse("invalid", "Enter at least one numeric component.")
    pieces = body.split(",")
    if len(pieces) > maximum:
        _refuse("unsupported", "Too many numeric components for this domain.")
    return tuple(_scalar(piece, number_parser) for piece in pieces)


def _bracketed(raw, number_parser):
    if not raw.startswith("[") or not raw.endswith("]"):
        _refuse("invalid", "Enclose the vector in square brackets.")
    return _components(raw[1:-1], LIMITS["vector_entries"], number_parser)


def _matrix(raw, number_parser):
    if not raw.startswith("[") or not raw.endswith("]"):
        _refuse("invalid", "Enclose the matrix rows in square brackets.")
    body = raw[1:-1].strip()
    rows = []
    while body:
        if not body.startswith("[") or "]" not in body:
            _refuse("invalid", "Each matrix row needs square brackets.")
        stop = body.index("]")
        rows.append(_bracketed(body[:stop + 1], number_parser))
        if len(rows) > LIMITS["matrix_rows"]:
            _refuse("unsupported", "Use at most eight matrix rows.")
        body = body[stop + 1:].strip()
        if body:
            if not body.startswith(",") or not body[1:].strip():
                _refuse("invalid", "Separate matrix rows with commas, without a trailing comma.")
            body = body[1:].strip()
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        _refuse("invalid", "Enter a nonempty rectangular matrix.")
    return tuple(rows)


# An endpoint is (rank, value): rank -1/+1 denotes negative/positive infinity;
# rank zero is finite. This avoids floats, sentinels and approximate sorting.
def _endpoint(raw, number_parser):
    raw = raw.strip()
    if raw in ("-inf", "inf"):
        return (-1 if raw == "-inf" else 1, Fraction(0))
    return (0, _scalar(raw, number_parser))


def _intervals(raw, number_parser):
    if raw == "empty":
        return ()
    pieces = raw.split("U")
    if len(pieces) > LIMITS["interval_pieces"]:
        _refuse("unsupported", "Use at most eight interval pieces.")
    intervals = []
    for piece in pieces:
        piece = piece.strip()
        if (len(piece) < 5 or piece[0] not in "([" or piece[-1] not in ")]"
                or piece[1:-1].count(",") != 1):
            _refuse("invalid", "Use two endpoints and explicit open or closed interval brackets.")
        a, b = piece[1:-1].split(",")
        low, high = _endpoint(a, number_parser), _endpoint(b, number_parser)
        lc, hc = piece[0] == "[", piece[-1] == "]"
        if low[0] == 1 or high[0] == -1 or low > high:
            _refuse("invalid", "Interval endpoints must be in increasing order.")
        if (low[0] == -1 and lc) or (high[0] == 1 and hc):
            _refuse("invalid", "Infinite endpoints must be open.")
        if low == high and not (lc and hc):
            continue
        intervals.append((low, high, lc, hc))
    intervals.sort(key=lambda p: (p[0], not p[2], p[1], not p[3]))
    merged = []
    for low, high, lc, hc in intervals:
        if not merged:
            merged.append((low, high, lc, hc))
            continue
        pl, ph, plc, phc = merged[-1]
        if low < ph or (low == ph and (phc or lc)):
            if high > ph:
                merged[-1] = (pl, high, plc, hc)
            elif high == ph:
                merged[-1] = (pl, ph, plc, phc or hc)
        else:
            merged.append((low, high, lc, hc))
    return tuple(merged)


def canonicalize(raw, domain, number_parser):
    """Return an immutable exact object or raise a typed unresolved refusal."""
    try:
        if not isinstance(domain, str) or domain not in GRAMMARS:
            _refuse("unavailable", "Unknown exact domain; request author review.")
        raw = _entry(raw)
        if domain == "rational-set":
            if not raw.startswith("{") or not raw.endswith("}"):
                _refuse("invalid", "Enclose the finite set in braces.")
            return tuple(sorted(set(_components(raw[1:-1], LIMITS["set_entries"], number_parser, empty=True))))
        if domain == "rational-vector":
            return _bracketed(raw, number_parser)
        if domain == "rational-matrix":
            return _matrix(raw, number_parser)
        return _intervals(raw, number_parser)
    except DomainRefusal:
        raise
    except Exception as exc:
        raise DomainRefusal("error", "Domain checker failed; preserve input and retry.") from exc


def _shape(value, domain):
    if domain == "rational-vector":
        return [len(value)]
    if domain == "rational-matrix":
        return [len(value), len(value[0])]
    return None


def _check_shape(value, spec, state):
    if _shape(value, spec["domain"]) != spec["shape"]:
        _refuse(state, "Use the declared vector or matrix shape: " + str(spec["shape"]) + ".")


def validate_spec(spec, number_parser):
    """Validate the private proposed v1 spec, including diagnostic disjointness."""
    try:
        keys = {"domain", "checker_version", "target", "diagnostics", "shape", "orientation"}
        if not isinstance(spec, dict) or set(spec) != keys:
            _refuse("unavailable", "Checker specification has missing or unknown fields.")
        domain = spec["domain"]
        if not isinstance(domain, str) or domain not in GRAMMARS or spec["checker_version"] != VERSION:
            _refuse("unavailable", "Checker specification uses an unsupported domain or version.")
        shape = spec["shape"]
        dimensions = 1 if domain == "rational-vector" else 2 if domain == "rational-matrix" else 0
        if dimensions:
            if (not isinstance(shape, list) or len(shape) != dimensions
                    or any(type(n) is not int or not 1 <= n <= 8 for n in shape)):
                _refuse("unavailable", "Declare one to eight entries per vector or matrix dimension.")
        elif shape is not None:
            _refuse("unavailable", "Sets and interval unions have no fixed shape.")
        if ((domain == "rational-vector" and spec["orientation"] not in ("row", "column"))
                or (domain != "rational-vector" and spec["orientation"] is not None)):
            _refuse("unavailable", "Only vectors declare row or column orientation.")
        target = canonicalize(spec["target"], domain, number_parser)
        _check_shape(target, spec, "unavailable")
        rules = spec["diagnostics"]
        if not isinstance(rules, list) or len(rules) > 2:
            _refuse("unavailable", "Author at most two named diagnostic rules.")
        diagnostics = []
        for rule in rules:
            if (not isinstance(rule, dict) or set(rule) != {"id", "answer"}
                    or not isinstance(rule["id"], str)
                    or not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", rule["id"])):
                _refuse("unavailable", "Each diagnostic needs a bounded ASCII ID and answer.")
            value = canonicalize(rule["answer"], domain, number_parser)
            _check_shape(value, spec, "unavailable")
            if value == target or any(name == rule["id"] or previous == value for name, previous in diagnostics):
                _refuse("unavailable", "Diagnostic rules overlap each other or the teacher answer.")
            diagnostics.append((rule["id"], value))
        return target, tuple(diagnostics)
    except DomainRefusal as exc:
        if exc.state == "error":
            raise
        raise DomainRefusal("unavailable", "Checker needs author review: " + str(exc)) from exc
    except Exception as exc:
        raise DomainRefusal("error", "Domain checker failed; preserve input and retry.") from exc


@dataclass(frozen=True)
class Comparison:
    """Private exact operands for the runtime, with no verdict or score."""
    original: str
    domain: str
    checker_version: str
    response: tuple
    target: tuple
    diagnostics: tuple


def prepare_comparison(raw, spec, number_parser):
    target, diagnostics = validate_spec(spec, number_parser)
    value = canonicalize(raw, spec["domain"], number_parser)
    _check_shape(value, spec, "invalid")
    return Comparison(raw, spec["domain"], VERSION, value, target, diagnostics)


def public_contract(spec, number_parser):
    """Validated proposed entry declaration; excludes targets and diagnostics."""
    validate_spec(spec, number_parser)
    return {"domain": spec["domain"], "checker_version": VERSION,
            "shape": list(spec["shape"]) if spec["shape"] is not None else None,
            "orientation": spec["orientation"], "grammar": GRAMMARS[spec["domain"]],
            "limits": dict(LIMITS)}


def private_test_errors(spec, rows, number_parser, runtime_analyze):
    """Replay private authored tests through a runtime-supplied analyzer only.

    The callback is trusted runtime code, never source or a callable from an
    authored file. The module cannot settle correctness without that authority.
    """
    try:
        _, diagnostics = validate_spec(spec, number_parser)
    except DomainRefusal as exc:
        return [("checker", str(exc))]
    if not isinstance(rows, list) or not 4 <= len(rows) <= 128:
        return [("checker_tests", "Author 4 to 128 private pinned checker tests.")]
    errors, states, tested_ids = [], set(), set()
    teacher_tested = False
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {"input", "state", "diagnostic_id", "checker_version"}
                or not isinstance(row["input"], str) or row["checker_version"] != VERSION
                or row["state"] not in ("correct", "mathematically_wrong", "invalid", "unsupported")
                or (row["diagnostic_id"] is not None and not isinstance(row["diagnostic_id"], str))):
            errors.append(("checker_tests", "Every row needs input, state, diagnostic_id and pinned checker_version."))
            continue
        try:
            actual = runtime_analyze(row["input"], spec)
        except DomainRefusal as exc:
            actual = {"state": exc.state}
        except Exception:
            errors.append(("checker_tests", "Runtime checker failed; preserve tests and retry."))
            continue
        if not isinstance(actual, dict) or actual.get("state") not in ("correct", "mathematically_wrong", "invalid", "unsupported"):
            errors.append(("checker_tests", "Runtime checker returned an unresolved or malformed outcome."))
            continue
        if actual["state"] != row["state"] or actual.get("diagnostic_id") != row["diagnostic_id"]:
            errors.append(("checker_tests", "Authored expectation differs from runtime outcome."))
        states.add(actual["state"])
        if actual.get("diagnostic_id"):
            tested_ids.add(actual["diagnostic_id"])
        teacher_tested |= row["input"] == spec["target"] and actual["state"] == "correct"
    if not teacher_tested or not {"correct", "mathematically_wrong", "invalid", "unsupported"} <= states:
        errors.append(("checker_tests", "Tests must cover teacher answer, wrong mathematics and both entry refusal states."))
    if tested_ids != {name for name, _ in diagnostics}:
        errors.append(("checker_tests", "Tests must reproduce every authored diagnostic."))
    return errors
