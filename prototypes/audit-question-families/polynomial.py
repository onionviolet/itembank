"""Disposable bounded-domain analysis, never a learner scoring authority.

Coefficient comparison calls runtime.score_response on an existing numeric
fill item. Required form and named diagnostics are advisory experiment output.
No session, accepted bank or evidence event is produced by this module.
"""
import ast
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import runtime

VERSION = "a2-rational-polynomial-v1"
MAX_LENGTH = 160
MAX_NODES = 64
MAX_DEGREE = 4
MAX_COEFFICIENT = 10**6


class DomainError(ValueError):
    def __init__(self, state, message):
        self.state = state
        super().__init__(message)


def _bound(values):
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    if len(values) > MAX_DEGREE + 1 or any(
            abs(v.numerator) > MAX_COEFFICIENT or v.denominator > MAX_COEFFICIENT
            for v in values):
        raise DomainError("unsupported", "Degree or rational coefficient limit exceeded.")
    return values


def _product(left, right):
    if len(left) + len(right) - 2 > MAX_DEGREE:
        raise DomainError("unsupported", "Intermediate degree exceeds four.")
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return _bound(out)


def canonicalize(raw):
    """Return exact coefficients and expanded-form flag, with bounded work."""
    if not isinstance(raw, str) or not raw.strip():
        raise DomainError("invalid", "Enter an expression.")
    if len(raw) > MAX_LENGTH:
        raise DomainError("unsupported", "Input exceeds 160 characters.")
    if re.search(r"[^0-9x\s.+*/()^\-]", raw) or "**" in raw:
        raise DomainError("unsupported", "Only x, rational literals, + - * / and ^ are supported.")
    source = raw.strip().replace("^", "**")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError, RecursionError):
        raise DomainError("invalid", "Malformed expression; use explicit multiplication.") from None
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise DomainError("unsupported", "Expression exceeds 64 syntax nodes.")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            # Fraction reads the original decimal token, never a rounded float.
            return _bound([Fraction(ast.get_source_segment(source, node))]), True
        if isinstance(node, ast.Name) and node.id == "x":
            return [Fraction(0), Fraction(1)], True
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            vector, form = visit(node.operand)
            return _bound([(-v if isinstance(node.op, ast.USub) else v) for v in vector]), form
        if not isinstance(node, ast.BinOp):
            raise DomainError("unsupported", "Syntax is outside this domain.")
        left, lf = visit(node.left)
        right, rf = visit(node.right)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            sign = -1 if isinstance(node.op, ast.Sub) else 1
            out = [Fraction(0)] * max(len(left), len(right))
            for i, v in enumerate(left):
                out[i] += v
            for i, v in enumerate(right):
                out[i] += sign * v
            return _bound(out), lf and rf
        if isinstance(node.op, ast.Mult):
            # Expanded means multiplication contains no additive syntax.
            sums = any(isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub))
                       for n in ast.walk(node))
            return _product(left, right), lf and rf and not sums
        if isinstance(node.op, ast.Div):
            # Only a numeric rational literal, not division of expressions.
            if not isinstance(node.left, ast.Constant) or not isinstance(node.right, ast.Constant):
                raise DomainError("unsupported", "Division is restricted to numeric rational literals.")
            if right[0] == 0:
                raise DomainError("invalid", "A rational denominator cannot be zero.")
            return _bound([left[0] / right[0]]), True
        if isinstance(node.op, ast.Pow):
            if not isinstance(node.right, ast.Constant) or type(node.right.value) is not int:
                raise DomainError("unsupported", "Exponent must be a nonnegative integer literal.")
            exponent = node.right.value
            if not 0 <= exponent <= MAX_DEGREE:
                raise DomainError("unsupported", "Exponent must be between zero and four.")
            out = [Fraction(1)]
            for _ in range(exponent):
                out = _product(out, left)
            sums = any(isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub))
                       for n in ast.walk(node.left))
            return out, lf and not sums
        raise DomainError("unsupported", "Operation is outside this domain.")

    return visit(tree.body)


def _equal(left, right):
    """The existing runtime owns the only boolean comparison verdict."""
    fields = [{"id": "c%d" % i, "label": "Coefficient %d" % i,
               "kind": "numeric", "answer": str(right[i] if i < len(right) else 0)}
              for i in range(MAX_DEGREE + 1)]
    q = {"type": "fill", "fields": fields}
    answer = {"c%d" % i: str(left[i] if i < len(left) else 0)
              for i in range(MAX_DEGREE + 1)}
    return runtime.score_response(q, answer)


def analyze(raw, target="2*x+2", mode="practice", session=None, fail=False):
    """Report advisory outcomes; unresolved inputs have no comparison verdict."""
    result = {"original": raw, "checker_version": VERSION, "authority": "advisory-only",
              "runtime_comparison": None}
    try:
        teacher, teacher_form = canonicalize(target)
        if not teacher_form:
            raise DomainError("unavailable", "Teacher answer is not in expanded form.")
    except DomainError as exc:
        return dict(result, state="unavailable", message="Invalid teacher answer: " + str(exc))
    try:
        if fail:
            raise ArithmeticError("Injected failure")
        vector, expanded = canonicalize(raw)
        equivalent = _equal(vector, teacher)
        result["runtime_comparison"] = equivalent
        state = "correct" if equivalent and expanded else (
            "wrong_form" if equivalent else "mathematically_wrong")
        private = {"state": state}
        # Diagnostics are defined only for this one synthetic teacher target.
        if _equal(teacher, [Fraction(2), Fraction(2)]):
            for name, misconception in (("distribution-omission", [Fraction(1), Fraction(2)]),
                                        ("sign-error", [Fraction(-2), Fraction(2)])):
                if _equal(vector, misconception):
                    private["diagnostic_id"] = name
        if runtime.assessment_feedback_released(mode, session):
            result.update(private)
        else:
            result.update(state="withheld", runtime_comparison=None)
    except DomainError as exc:
        result.update(state=exc.state, message=str(exc))
    except (ArithmeticError, ValueError):
        result.update(state="error", message="Analysis failed; preserve input and retry.",
                      runtime_comparison=None)
    return result


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Synthetic advisory polynomial analysis; no learner marks.")
    parser.add_argument("expression")
    parser.add_argument("--mode", choices=("practice", "exam", "diagnostic"), default="practice")
    args = parser.parse_args()
    print(json.dumps(analyze(args.expression, mode=args.mode), indent=2))
