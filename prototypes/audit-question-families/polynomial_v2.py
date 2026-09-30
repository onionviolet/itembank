"""Synthetic checker contract experiment, never a learner grading endpoint.

No accepted artifacts, sessions or evidence are written. Exact coefficient
comparisons delegate to the existing runtime numeric-fill scorer. Syntax and
form analysis are advisory until integrated inside that scoring authority.
"""
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import runtime

VERSION = "a5-rational-polynomial-v2"
LIMITS = {"characters": 160, "tokens": 96, "nodes": 64, "depth": 16,
          "literal_digits": 12, "degree": 4, "coefficient": 10**6,
          "arithmetic_steps": 64}
TOKEN = re.compile(r"[0-9]+(?:\.[0-9]+)?|\.[0-9]+|x|[()+*/^\-]")


class DomainError(ValueError):
    def __init__(self, state, message):
        self.state = state
        super().__init__(message)


def refuse(state, message):
    raise DomainError(state, message)


class Parser:
    def __init__(self, raw):
        if not isinstance(raw, str) or not raw.strip():
            refuse("invalid", "Enter a polynomial expression.")
        if len(raw) > LIMITS["characters"]:
            refuse("unsupported", "Use at most 160 characters.")
        self.tokens = []
        pos = 0
        while pos < len(raw):
            if raw[pos] in " \t":
                pos += 1
                continue
            if raw[pos] in "\r\n" or ord(raw[pos]) < 32:
                refuse("invalid", "Use a single line without control characters.")
            match = TOKEN.match(raw, pos)
            if not match:
                if raw[pos] == ".":
                    refuse("invalid", "A decimal point needs following digits.")
                refuse("unsupported", "Use x, ASCII numbers and explicit + - * / ^ ( ).")
            self.tokens.append(match.group())
            pos = match.end()
        if len(self.tokens) > LIMITS["tokens"]:
            refuse("unsupported", "Use at most 96 tokens.")
        self.pos = self.nodes = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ""

    def take(self):
        value = self.peek()
        self.pos += 1
        return value

    def node(self, kind, *children):
        self.nodes += 1
        if self.nodes > LIMITS["nodes"]:
            refuse("unsupported", "Use at most 64 syntax nodes.")
        return (kind, *children)

    def expression(self, depth=0):
        left = self.term(depth)
        while self.peek() in ("+", "-"):
            op = self.take()
            left = self.node(op, left, self.term(depth))
        return left

    def term(self, depth):
        left = self.unary(depth)
        while self.peek() == "*":
            self.take()
            if self.peek() == "*":
                refuse("unsupported", "Use ^ for powers.")
            left = self.node("*", left, self.unary(depth))
        if self.peek() == "/":
            refuse("unsupported", "Only integer/integer rational literals allow division.")
        return left

    def unary(self, depth):
        if depth > LIMITS["depth"]:
            refuse("unsupported", "Use at most 16 nested parentheses or signs.")
        if self.peek() in ("+", "-"):
            return self.node("unary" + self.take(), self.unary(depth + 1))
        base = self.atom(depth)
        if self.peek() == "^":
            self.take()
            exponent = self.take()
            if not exponent:
                refuse("invalid", "A power needs an integer exponent.")
            if not exponent.isascii() or not exponent.isdigit():
                refuse("unsupported", "Use an unsigned integer exponent from 0 to 4.")
            if len(exponent) > 1 or int(exponent) > LIMITS["degree"]:
                refuse("unsupported", "Use an integer exponent from 0 to 4 without leading zeros.")
            base = self.node("^", base, int(exponent))
        return base

    def atom(self, depth):
        token = self.take()
        if token == "x":
            return self.node("x")
        if token == "(":
            child = self.expression(depth + 1)
            if self.take() != ")":
                refuse("invalid", "Close every parenthesis.")
            return child
        if token and (token[0].isdigit() or token[0] == "."):
            if sum(c.isdigit() for c in token) > LIMITS["literal_digits"]:
                refuse("unsupported", "Use at most 12 digits per numeric literal.")
            if self.peek() == "/":
                self.take()
                denominator = self.take()
                if not denominator:
                    refuse("invalid", "A fraction needs a denominator.")
                if not token.isdigit() or not denominator.isdigit():
                    refuse("unsupported", "Fractions require unsigned integer literals.")
                if len(denominator) > LIMITS["literal_digits"]:
                    refuse("unsupported", "Use at most 12 denominator digits.")
                if int(denominator) == 0:
                    refuse("invalid", "A fraction denominator cannot be zero.")
                return self.node("number", Fraction(int(token), int(denominator)))
            return self.node("number", Fraction(token))
        refuse("invalid", "Expected a number, x or a parenthesized expression.")

    def parse(self):
        tree = self.expression()
        if self.peek():
            if self.peek() == "^":
                refuse("unsupported", "Chained powers are outside this grammar.")
            refuse("invalid", "Unexpected token; write multiplication explicitly.")
        return tree


class Expansion:
    def __init__(self):
        self.steps = 0

    def step(self):
        self.steps += 1
        if self.steps > LIMITS["arithmetic_steps"]:
            refuse("unsupported", "Expansion exceeds 64 coefficient arithmetic steps.")

    def bound(self, values):
        while len(values) > 1 and values[-1] == 0:
            values.pop()
        if len(values) > LIMITS["degree"] + 1 or any(
                abs(v.numerator) > LIMITS["coefficient"] or
                v.denominator > LIMITS["coefficient"] for v in values):
            refuse("unsupported", "Intermediate degree or coefficient bound exceeded.")
        return values

    def product(self, left, right):
        if len(left) + len(right) - 2 > LIMITS["degree"]:
            refuse("unsupported", "Intermediate degree exceeds four.")
        out = [Fraction(0)] * (len(left) + len(right) - 1)
        for i, a in enumerate(left):
            for j, b in enumerate(right):
                self.step()
                out[i + j] += a * b
                self.bound(out[:])
        return self.bound(out)

    def visit(self, node):
        kind = node[0]
        if kind == "number":
            return self.bound([node[1]])
        if kind == "x":
            return [Fraction(0), Fraction(1)]
        left = self.visit(node[1])
        if kind.startswith("unary"):
            return [(-v if kind == "unary-" else v) for v in left]
        if kind == "^":
            out = [Fraction(1)]
            for _ in range(node[2]):
                out = self.product(out, left)
            return out
        right = self.visit(node[2])
        if kind == "*":
            return self.product(left, right)
        out = [Fraction(0)] * max(len(left), len(right))
        for i in range(len(out)):
            self.step()
            out[i] = (left[i] if i < len(left) else 0) + (
                1 if kind == "+" else -1) * (right[i] if i < len(right) else 0)
        return self.bound(out)


def monomial(node):
    """Return variable-factor count, or None if distribution/reduction is needed."""
    kind = node[0]
    if kind == "number":
        return 0
    if kind == "x" or (kind == "^" and node[1][0] == "x"):
        return 1
    if kind.startswith("unary"):
        return monomial(node[1])
    if kind == "*":
        left, right = monomial(node[1]), monomial(node[2])
        if left is not None and right is not None and left + right <= 1:
            return left + right
    return None


def expanded(node):
    return (expanded(node[1]) and expanded(node[2]) if node[0] in ("+", "-")
            else monomial(node) is not None)


def canonicalize(raw):
    tree = Parser(raw).parse()
    return Expansion().visit(tree), expanded(tree)


def runtime_equal(left, right):
    fields = [{"id": "c%d" % i, "label": "Coefficient %d" % i,
               "kind": "numeric", "answer": str(right[i] if i < len(right) else 0)}
              for i in range(LIMITS["degree"] + 1)]
    response = {"c%d" % i: str(left[i] if i < len(left) else 0)
                for i in range(LIMITS["degree"] + 1)}
    return runtime.score_response({"type": "fill", "fields": fields}, response)


DEFAULT_SPEC = {"domain": "rational-polynomial", "checker_version": VERSION,
                "variable": "x", "required_form": "expanded", "target": "2*x+2",
                "diagnostics": [
                    {"id": "distribution-omission", "answer": "2*x+1"},
                    {"id": "sign-error", "answer": "2*x-2"}]}


def validate_spec(spec):
    if not isinstance(spec, dict) or set(spec) != set(DEFAULT_SPEC):
        refuse("unavailable", "Checker specification has missing or unknown fields.")
    for key in ("domain", "checker_version", "variable", "required_form"):
        if spec[key] != DEFAULT_SPEC[key]:
            refuse("unavailable", "Checker specification uses an unsupported contract.")
    target, form = canonicalize(spec["target"])
    if not form:
        refuse("unavailable", "Teacher answer must satisfy expanded form.")
    rules = spec["diagnostics"]
    if not isinstance(rules, list) or len(rules) > 2:
        refuse("unavailable", "Author at most two named diagnostic rules.")
    diagnostics = []
    for rule in rules:
        if (not isinstance(rule, dict) or set(rule) != {"id", "answer"} or
                not isinstance(rule["id"], str) or
                not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", rule["id"])):
            refuse("unavailable", "Diagnostic rules require a stable ASCII identifier and answer.")
        vector, _ = canonicalize(rule["answer"])
        if runtime_equal(vector, target) or any(
                name == rule["id"] or runtime_equal(vector, previous)
                for name, previous in diagnostics):
            refuse("unavailable", "Diagnostic rules overlap each other or the teacher answer.")
        diagnostics.append((rule["id"], vector))
    return target, diagnostics


def analyze(raw, spec=None, mode="practice", session=None, fail=False):
    result = {"original": raw, "checker_version": VERSION,
              "authority": "synthetic-advisory-only", "settled_score": None,
              "runtime_comparison": None}
    if mode not in ("practice", "exam", "diagnostic"):
        return dict(result, state="unavailable", message="Use a recognized assessment mode.")
    try:
        target, diagnostics = validate_spec(DEFAULT_SPEC if spec is None else spec)
    except DomainError:
        return dict(result, state="unavailable", message="This checker needs author review.")
    except Exception:
        return dict(result, state="error", message="Checker failed; preserve input and retry.")
    try:
        if fail:
            raise ArithmeticError("Synthetic injected failure")
        vector, form = canonicalize(raw)
        equivalent = runtime_equal(vector, target)
        state = "correct" if equivalent and form else (
            "wrong_form" if equivalent else "mathematically_wrong")
        if not runtime.assessment_feedback_released(mode, session):
            return dict(result, state="withheld")
        result.update(state=state, runtime_comparison=equivalent)
        if state == "mathematically_wrong":
            for name, answer in diagnostics:
                if runtime_equal(vector, answer):
                    result["diagnostic_id"] = name
                    break
        return result
    except DomainError as exc:
        return dict(result, state=exc.state, message=str(exc))
    except Exception:
        return dict(result, state="error", message="Checker failed; preserve input and retry.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expression")
    parser.add_argument("--mode", choices=("practice", "exam", "diagnostic"), default="practice")
    args = parser.parse_args()
    print(json.dumps(analyze(args.expression, mode=args.mode), indent=2))
