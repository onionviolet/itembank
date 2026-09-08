"""The seeding loop: the six-stage pipeline, the one accept endpoint, the
batch-framed browser surface, and the refuse-by-name degrade.

This module is plan 03.2-03's deliverable. It owns:

* `run_seeding_run(...)` -- the six-stage pipeline in the LOCKED order
  (D-08): (1) deterministic source selection from the bank's `## SOURCES`
  registry, (2) outline-only draft, (3) per-section drafting, (4) the
  deterministic checks via `model.lint()` (with parsed sources passed so
  `[SRC:]`/`[OBJ:]` provenance lint runs) BEFORE any model critique --
  retrying within a configured cap -- (5) independent CoVe-style
  verification, a second model pass over the deterministic-clean draft, and
  (6) human accept, one item at a time (D-06). A cancelled run writes
  nothing (D-09). The order is structural and asserted by the fixture: no
  plan may reorder these stages.
* `accept_candidate(...)` -- the ONE accept endpoint behind both surfaces
  (D-07): `itembank seed <bank>` in `surfaces/cli.py` and `POST /seed/accept`
  in `surfaces/daemon.py` call this same function, never two implementations
  of the accept decision. It refuses a candidate with lint errors, appends a
  clean one to the bank exactly once (content-fingerprint dedup), and leaves
  a skipped item in the draft set (deferral, reported at the end).
* The batch-framed browser surface per 03.2-UI-SPEC sections 2 and 4:
  `render_accept_surface`, `render_cancelled_surface`, `render_degraded_surface`
  reproduce the verbatim copy rows, staged progress (a count, never a fill
  bar), Accept/Skip/Cancel controls, Accept disabled WITH the stated reason
  on lint errors (never a silent dead button), no chat affordance, and the
  cancelled summary `Nothing was written.`
* The degrade contract (D-10): with no model backend reachable,
  `run_seeding_run` refuses by name (`The authoring backend is unreachable.
  Import, lint, and provenance still work.`) and starts no draft; import,
  lint, and coverage are untouched because this module is the only place
  seeding reaches for a backend.

Adapter seam. Phase 8 (`08-model-adapter-interface-tier-gate-enforcement`) is
NOT built in code yet. This module defines the seam as the injectable
`ModelAdapter` interface below -- the Phase 8 contract, hosted-first per
Directive 1 -- and satisfies every test with the deterministic
`FakeModelAdapter` shipped here (documented, headless, stdlib-only). Phase 8
will implement the real hosted adapter behind this same interface; no caller
in this module changes. The default adapter (`NoBackendAdapter`) reports
unavailable, so seeding refuses by name until a real backend exists.

Plan 03.2-04's additional deterministic checks (paraphrase lint,
`style.unsourced_specific`, `[CASE:]`, `[PREREQ:]`) are NOT implemented here.
The pipeline's stage-4 seam `extra_checks` is where that plan wires them in;
with the checks available today, stage 4 runs `model.lint()` (with sources
passed) plus the deterministic `[SRC:]`/`[OBJ:]` resolution over the draft's
own directives.
"""
import os
import re
import uuid

import model
import model_adapter
from model import LintError, lint, parse_question, parse_sources

from surfaces import presentation

# ---------------------------------------------------------------------------
# UI-SPEC section 4 copy contract -- every string verbatim, in its voice.
# ---------------------------------------------------------------------------

BATCH_FRAMING_LINE = "This is a batch authoring run. Each item is drafted, checked, and accepted one at a time."
PROGRESS_LINE = "Draft {n} of {m} · stage {stage}"
ACCEPT_COPY = "Accept item"
SKIP_COPY = "Skip item"
CANCEL_COPY = "Cancel run"
CANCELLED_SUMMARY = "Nothing was written."
BACKEND_UNREACHABLE = "The authoring backend is unreachable. Import, lint, and provenance still work."
NO_SOURCE_RECORDED = "No source recorded"
NO_DRAFTS_TO_ACCEPT = "No drafts to accept."

# ---------------------------------------------------------------------------
# The locked six-stage order (D-08). The pipeline walks STAGES in this exact
# order and the fixture asserts both the constant and an executed run against
# it, so a reorder fails the build.
# ---------------------------------------------------------------------------

STAGE_SOURCE_SELECTION = "source selection"
STAGE_OUTLINE = "outline"
STAGE_DRAFTING = "drafting"
STAGE_CHECKS = "checks"
STAGE_VERIFICATION = "verification"
STAGE_ACCEPT = "accept"

STAGES = (STAGE_SOURCE_SELECTION, STAGE_OUTLINE, STAGE_DRAFTING,
          STAGE_CHECKS, STAGE_VERIFICATION, STAGE_ACCEPT)

DEFAULT_RETRY_CAP = 3

# The draft's own [SRC:]/[OBJ:] directives, scanned deterministically in
# stage 4 and at accept time. Mirrors model.parse_sources()'s directive
# regexes; restated here because the draft block is not yet inside the bank
# file parse_sources() reads.
_SRC_RE = re.compile(r"\[SRC:\s*([^\]]+?)\]")
_OBJ_RE = re.compile(r"\[OBJ:\s*([^\]]+?)\]")


# ---------------------------------------------------------------------------
# The Phase 8 adapter seam (hosted-first, Directive 1). Phase 8 is not built
# in code yet: this interface is the contract, and tests use the deterministic
# fake below. No real backend ships in this plan.
# ---------------------------------------------------------------------------

class ModelAdapter:
    """The model-adapter interface the pipeline calls (Phase 8's contract).

    A backend is anything that implements these four methods. Phase 8 builds
    the hosted adapter behind this same boundary; this plan ships only the
    deterministic `FakeModelAdapter` and the refusing `NoBackendAdapter`.
    """

    name = "base"

    def available(self):
        """True when the backend is reachable and can take a call. A False
        return is the typed unavailable result: seeding refuses by name
        (D-10) and never starts a draft."""
        return False

    def draft_outline(self, objective, sources):
        """Stage 2: the outline-only draft. One call, never per-section."""
        raise NotImplementedError

    def draft_section(self, outline, section):
        """Stage 3: one section of the item, one call per section."""
        raise NotImplementedError

    def verify(self, draft_block, objective, sources):
        """Stage 5: the independent CoVe-style verification pass -- a second
        model call over the deterministic-clean draft. Returns a dict with
        `ok` and `notes`; advisory, never a gate on human accept."""
        raise NotImplementedError


class NoBackendAdapter(ModelAdapter):
    """The default: unavailable. `run_seeding_run(bank)` therefore refuses by
    name until Phase 8 lands a real adapter behind the same interface."""

    name = "none"

    def available(self):
        return False


class ConfiguredModelAdapter(ModelAdapter):
    """Adapt the shared settings-backed model boundary to the seeding stages."""

    name = "configured"

    def __init__(self, settings_data):
        self.settings = settings_data or {}

    def available(self):
        profile, reason = model_adapter.resolve_profile(self.settings)
        return profile is not None and reason is None

    def _call(self, stage, instruction, contract=None, **values):
        payload = {
            "schema_version": 1,
            "contract": contract or model.SPEC,
            "request": {"stage": stage, "instruction": instruction,
                        **values},
            "attempt": 1,
            "findings": [],
        }
        request = model_adapter.request_from_operation(
            "author", "seed-" + uuid.uuid4().hex[:16], "",
            author_request=payload)
        result = model_adapter.invoke(request, self.settings)
        if result.get("status") != "ok" or not isinstance(
                result.get("candidate"), dict):
            return {}
        return result["candidate"]

    def draft_outline(self, objective, sources):
        result = self._call(
            "outline", "Return the three required seeding sections.",
            contract="Outline sections: Stem, Options, Rationale.",
            objective=objective, sources=sources)
        sections = result.get("sections") or []
        return "\n".join(sections) if isinstance(sections, list) else ""

    def draft_section(self, outline, section):
        result = self._call(
            "drafting", "Draft only the requested question-bank section. "
            "The Stem starts with the question text, not Qn. or Q1.",
            outline=outline, section=section)
        return result.get("text") or ""

    def verify(self, draft_block, objective, sources):
        result = self._call(
            "verification", "Verify the draft independently. Return JSON "
            "fields ok and notes.", draft=draft_block,
            objective=objective, sources=sources)
        return {"ok": result.get("ok") is True,
                "notes": result.get("notes") or []}


class FakeModelAdapter(ModelAdapter):
    """The deterministic test adapter -- fully headless, stdlib-only.

    `draft_outline` returns `outline`; `draft_section` returns `stem`,
    `options`, and `rationale` for the sections of the same names (and the
    rationale for any other section). With `rationale_dirty_attempts > 0`
    the first N rationale calls return `dirty_rationale` instead, which is
    how the retry-before-critique and retry-cap fixtures make the assembled
    draft fail the deterministic checks. `verify` returns `verify_result`
    and counts calls, so the fixtures can assert no model critique ran over
    a draft that failed the deterministic gate.
    """

    name = "fake"

    def __init__(self, outline="", stem="", options="", rationale="",
                 rationale_dirty_attempts=0, dirty_rationale="",
                 verify_result=None):
        self.outline = outline
        self.stem = stem
        self.options = options
        self.rationale = rationale
        self.dirty_rationale = dirty_rationale
        self.remaining_dirty = max(0, int(rationale_dirty_attempts))
        self.verify_result = verify_result or {
            "ok": True, "notes": ["independent verification passed"]}
        self.outline_calls = 0
        self.section_calls = 0
        self.verify_calls = 0

    def available(self):
        return True

    def draft_outline(self, objective, sources):
        self.outline_calls += 1
        return self.outline

    def draft_section(self, outline, section):
        self.section_calls += 1
        if section == "Stem":
            return self.stem
        if section == "Options":
            return self.options
        if section == "Rationale" and self.remaining_dirty > 0:
            self.remaining_dirty -= 1
            return self.dirty_rationale
        return self.rationale

    def verify(self, draft_block, objective, sources):
        self.verify_calls += 1
        return dict(self.verify_result)


# ---------------------------------------------------------------------------
# The run: one in-memory draft set, written to the bank only through an
# explicit human accept.
# ---------------------------------------------------------------------------

class SeedingRun:
    """One seeding run's in-memory state and report. Nothing in here writes a
    bank except `accept_candidate` -- and only `accept` reaches it (D-06)."""

    def __init__(self, bank_path, adapter, objective, retry_cap, extra_checks):
        self.bank_path = bank_path
        self.adapter = adapter
        self.objective = objective or ""
        self.retry_cap = max(1, int(retry_cap))
        self.extra_checks = extra_checks or (lambda draft: [])
        self.refused = False
        self.refusal = ""
        self.stages = []
        self.registry = {}
        self.source_selection = []
        self.outline = ""
        self.sections = []
        self.drafts = []
        self.failed_drafts = []
        self.accepted = []
        self.skipped = []
        self.cancelled = False
        self._pending = None

    # -- the six stages, in the locked order ---------------------------------

    def _run(self):
        self.stages.append(STAGE_SOURCE_SELECTION)
        self._stage1_select_sources()
        self.stages.append(STAGE_OUTLINE)
        self._stage2_outline()
        self.stages.append(STAGE_DRAFTING)
        self._stage3_sections()
        self.stages.append(STAGE_CHECKS)
        self._stage4_checks()
        self.stages.append(STAGE_VERIFICATION)
        self._stage5_verify()
        self.stages.append(STAGE_ACCEPT)

    def _stage1_select_sources(self):
        """Stage 1: deterministic source selection from the `## SOURCES`
        registry -- sorted registry ids, no randomness, nothing stored."""
        ps = parse_sources(self.bank_path)
        self.registry = ps or {"sources": {}, "srcs": [], "objs": [],
                               "duplicates": [], "path": self.bank_path}
        self.source_selection = sorted(self.registry["sources"])
        if not self.objective:
            m = model.coverage_map(self.bank_path)
            self.objective = sorted(m)[0] if m else ""

    def _stage2_outline(self):
        """Stage 2: the outline-only draft -- one model call, no item text."""
        self.outline = self.adapter.draft_outline(
            self.objective, self.registry["sources"])

    def _stage3_sections(self):
        """Stage 3: the deterministic section plan derived from the outline
        (one section per non-empty outline line), drafted per section inside
        each stage-4 attempt."""
        self.sections = [s.strip() for s in self.outline.splitlines()
                         if s.strip()] or ["Item"]

    def _assemble_draft(self):
        """One per-section drafting pass: each section of the outline is
        drafted once, then the section texts are composed into one parseable
        item block -- the deterministic object every later stage runs over."""
        section_texts = {}
        for section in self.sections:
            section_texts[section] = self.adapter.draft_section(
                self.outline, section)
        block = _compose_item_block(section_texts, self.sections)
        return {"index": 0, "sections": self.sections,
                "section_texts": section_texts, "block": block,
                "candidate": parse_question(block), "attempts": 0,
                "lint_errors": [], "warnings": [], "verify": None,
                "failed": False}

    def _stage4_checks(self):
        """Stage 4: the deterministic checks BEFORE any model critique.
        `model.lint()` (with parsed sources, so provenance lint runs), the
        draft's own `[SRC:]`/`[OBJ:]` resolution against the bank registry,
        and the plan 03.2-04 seam (`extra_checks`). A failing draft is
        re-drafted within the configured cap; only a deterministic-clean
        draft ever reaches stage 5."""
        attempt = 0
        while attempt < self.retry_cap:
            attempt += 1
            draft = self._assemble_draft()
            draft["attempts"] = attempt
            errors, warnings = self._check_draft(draft)
            draft["lint_errors"] = ["%s (%s)" % (e.code, e) for e in errors]
            draft["warnings"] = [str(w) for w in warnings]
            if not errors:
                draft["index"] = len(self.drafts) + 1
                self._pending = draft
                return
        draft["failed"] = True
        draft["index"] = len(self.failed_drafts) + 1
        self.failed_drafts.append(draft)

    def _check_draft(self, draft):
        ps = parse_sources(self.bank_path)
        errors, warnings = [], []
        if draft["candidate"] is None:
            errors.append(LintError(
                "seed.draft_unparsable", "block", "DRAFT",
                "the assembled draft does not parse as an item"))
        else:
            e, w = lint([draft["candidate"]], sources=ps)
            errors.extend(e)
            warnings.extend(w)
        for code, msg in _directive_errors(draft["block"], ps):
            errors.append(LintError(code, "src", "DRAFT", msg))
        errors.extend(self.extra_checks(draft))
        return errors, warnings

    def _stage5_verify(self):
        """Stage 5: the independent CoVe-style verification -- a second model
        pass over the deterministic-clean draft only. A draft that failed
        stage 4 is never critiqued."""
        if self._pending is None:
            return
        self._pending["verify"] = self.adapter.verify(
            self._pending["block"], self.objective,
            self.registry["sources"])
        self.drafts.append(self._pending)
        self._pending = None

    # -- stage 6: the human gate -------------------------------------------------

    def accept(self, index):
        """Stage 6: an explicit human accept for draft `index` (0-based),
        through the one `accept_candidate` endpoint. The result of the accept
        is returned; a refused accept keeps the draft in the set."""
        if not 0 <= index < len(self.drafts):
            return {"accepted": False, "reason": "no such draft"}
        result = accept_candidate(self.bank_path, self.drafts[index]["candidate"])
        if result.get("accepted"):
            self.accepted.append(index)
        return result

    def skip(self, index):
        """Stage 6: skip is a deferral -- the item stays in the draft set and
        is reported at the end, never discarded silently (UI-SPEC 2.1)."""
        if not 0 <= index < len(self.drafts):
            return {"deferred": False, "reason": "no such draft"}
        self.skipped.append(index)
        return {"deferred": True, "index": index}

    def cancel(self):
        """Stage 6: cancel stops the batch. A cancelled run writes nothing
        (D-09); the summary states `Nothing was written.` verbatim."""
        self.cancelled = True

    def summary(self):
        """The end-of-run report. A cancelled run reports the verbatim
        summary line; otherwise accepted/skipped/failed are surfaced, with
        skipped items named -- a deferral report, never a silent discard."""
        if self.cancelled:
            return CANCELLED_SUMMARY
        lines = ["%d drafted, %d accepted, %d skipped, %d failed "
                 "deterministic checks"
                 % (len(self.drafts), len(self.accepted), len(self.skipped),
                    len(self.failed_drafts))]
        if self.skipped:
            lines.append("Skipped (deferred, reported here): %s" % ", ".join(
                "draft %d" % (i + 1) for i in self.skipped))
        if self.failed_drafts:
            lines.append("Failed deterministic checks (not accepted): %s"
                         % ", ".join("draft %d" % d["index"]
                                     for d in self.failed_drafts))
        return "\n".join(lines)


def run_seeding_run(bank_path, adapter=None, objective=None,
                    retry_cap=DEFAULT_RETRY_CAP, extra_checks=None,
                    settings_data=None):
    """Run the six-stage pipeline (D-08) over `bank_path`.

    With no reachable backend (adapter None, or `adapter.available()` False)
    the run refuses by name with the exact D-10 line and starts no draft.
    Otherwise stages 1-5 execute in the locked order and the run holds the
    in-memory draft set; stage 6 (human accept) is driven through
    `run.accept` / `run.skip` / `run.cancel` -- nothing writes to the bank
    without an accept (D-06), and a cancelled run writes nothing (D-09).
    """
    adapter = adapter or (ConfiguredModelAdapter(settings_data)
                          if settings_data is not None else NoBackendAdapter())
    run = SeedingRun(bank_path, adapter, objective, retry_cap, extra_checks)
    if not adapter.available():
        run.refused = True
        run.refusal = BACKEND_UNREACHABLE
        return run
    run._run()
    return run


# ---------------------------------------------------------------------------
# The one accept endpoint behind both surfaces (D-07).
# ---------------------------------------------------------------------------

def accept_candidate(bank_path, candidate, sources=None, block=None):
    """The ONE accept endpoint. `itembank seed <bank>` and the daemon's
    `POST /seed/accept` both call this function -- one implementation, two
    surfaces, never two decisions (D-07).

    Gates the candidate through `model.lint()` (with parsed sources, so
    `[SRC:]`/`[OBJ:]` provenance lint runs) plus deterministic resolution of
    the draft's own directives against the bank registry; refuses on any
    error. A clean candidate is appended to the bank exactly once -- the
    same content fingerprint is detected and refused as already accepted.
    Returns a machine-readable result dict:
        {action, bank, accepted, errors, warnings, reason?,
         number?/already_accepted?}
    """
    if block is None:
        block = render_candidate(candidate, 1)
    ps = parse_sources(bank_path) if sources is None else sources
    errors, warnings = lint([candidate], sources=ps)
    errors = list(errors)
    result = {
        "action": "accept",
        "bank": os.path.basename(bank_path),
        "accepted": False,
        "errors": [],
        "warnings": [str(w) for w in warnings],
    }
    reasons = []
    for e in errors:
        reasons.append("%s (%s)" % (e.code, e))
    for code, msg in _directive_errors(block, ps):
        full = "%s: %s" % (code, msg)
        reasons.append(full)
        result["errors"].append(full)
    result["errors"].extend("%s (%s)" % (e.code, e) for e in errors)
    if reasons:
        result["reason"] = "; ".join(reasons)
        return result

    # Exactly once: content-fingerprint dedup against the bank's own items.
    fp = model.content_fingerprint(candidate)
    text = open(bank_path, encoding="utf-8", newline="").read()
    for q in model.parse_bank(text):
        if q.get("content_hash") == fp or model.content_fingerprint(q) == fp:
            result["reason"] = "already in the bank (same content fingerprint)"
            result["already_accepted"] = True
            return result

    numbers = [q["number"] for q in model.parse_bank(text)]
    number = (max(numbers) if numbers else 0) + 1
    block_n = render_candidate(candidate, number)
    new_text = text.rstrip("\n") + "\n\n" + block_n.rstrip("\n") + "\n"
    tmp = bank_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    os.replace(tmp, bank_path)
    result.update({"accepted": True, "number": number})
    return result


# ---------------------------------------------------------------------------
# The deterministic render-then-write half: a parse_question()-shaped dict
# back into a bank `Qn.` block. The reverse of model.parse_question() for the
# fields a seeded item carries; optional fields are omitted, never fabricated.
# ---------------------------------------------------------------------------

def render_candidate(q, number):
    """Serialize one `parse_question()`-shaped candidate into a bank `Qn.`
    block, numbered `number`. Fields absent from the dict are omitted, never
    invented. The output re-parses through `model.parse_question()` and
    round-trips `model.content_fingerprint()` byte-faithfully."""
    difficulty = (q.get("difficulty") or "recall").strip()
    lines = ["Q%d. %s   (difficulty: %s)" % (number, (q.get("stem") or "").strip(),
                                             difficulty)]
    obj = (q.get("objective") or "").strip()
    if obj:
        lines.append("[OBJECTIVE: %s]" % obj)
    t = q.get("type") or "mc"
    if t != "mc":
        lines.append("[TYPE: %s]" % t)
    if t in ("mc", "multi"):
        for letter in sorted(q.get("opts") or {}):
            lines.append("%s) %s" % (letter, (q["opts"][letter] or "").strip()))
        lines.append("")
        lines.append("CORRECT: %s" % ", ".join(sorted(q.get("correct") or [])))
        lines.append("")
        for label, field in (("WHY BEST", "why"),
                             ("KEY DISCRIMINATOR", "disc"),
                             ("SECOND-BEST", "second"), ("TRAP", "trap")):
            value = (q.get(field) or "").strip()
            if value:
                lines.append("%s: %s" % (label, value))
        da = q.get("da") or {}
        da_lines = ["- %s) %s" % (letter, (da[letter] or "").strip())
                    for letter in sorted(da) if da[letter]]
        if da_lines:
            lines.append("")
            lines.append("DISTRACTOR ANALYSIS:")
            lines.extend(da_lines)
        conf = (q.get("conf") or "").strip()
        if conf:
            lines.append("")
            lines.append("CONFIDENCE: %s" % conf)
    elif t == "short":
        model_text = (q.get("model") or "").strip()
        if model_text:
            lines.append("")
            lines.append("MODEL: %s" % model_text)
        rubric = q.get("rubric") or []
        if rubric:
            lines.append("")
            lines.append("RUBRIC:")
            lines.extend("- %s" % p.strip() for p in rubric if p.strip())
    elif t in ("table", "dnd"):
        lines.append("[CATEGORIES: %s]" % "|".join(q.get("cats") or []))
        marker = "ROW" if t == "table" else "ITEM"
        for row in q.get("rows") or []:
            lines.append("%s) %s::%s" % (marker, row["text"], row["cat"]))
        for note in q.get("notes") or []:
            lines.append("DISTRACTOR ANALYSIS:")
            lines.append("- %s" % note)
    elif t == "build":
        for step in q.get("steps") or []:
            lines.append("STEP) %s" % step)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Deterministic [SRC:]/[OBJ:] resolution over one draft block (D-11). A draft
# is not inside the bank file yet, so parse_sources() cannot see its
# directives; the pipeline and accept_candidate resolve them against the
# bank's registry the same way lint() resolves the bank's own directives.
# ---------------------------------------------------------------------------

def _directive_errors(block, sources):
    """Every unresolvable [SRC:]/[OBJ:] id in `block`, as (code, message)
    pairs naming the id and the registry file -- never silently ignored."""
    out = []
    if not sources:
        return out
    known = sources.get("sources") or {}
    path = sources.get("path") or "the bank"
    for mm in _SRC_RE.finditer(block or ""):
        parts = mm.group(1).strip().split(None, 1)
        sid = parts[0] if parts else ""
        if sid and sid not in known:
            out.append(("prov.src_unknown",
                        "[SRC:] names source '%s', which is not in "
                        "## SOURCES of %s" % (sid, path)))
    for mm in _OBJ_RE.finditer(block or ""):
        oid = mm.group(1).strip()
        if oid and oid not in known:
            out.append(("prov.obj_unknown",
                        "[OBJ:] names objective '%s', which is not in "
                        "## SOURCES of %s" % (oid, path)))
    return out


def _compose_item_block(section_texts, sections):
    """Deterministic composition of the per-section drafts into one parseable
    item block: Stem first, then the option block, then the remaining
    sections as the rationale. The stage-3 output every later stage runs on."""
    stem = (section_texts.get("Stem") or "").strip()
    options = (section_texts.get("Options") or "").strip()
    rationale = "\n\n".join(section_texts[s].strip()
                            for s in sections
                            if s not in ("Stem", "Options")
                            and (section_texts.get(s) or "").strip())
    return "Q1. %s   (difficulty: recall)\n\n%s\n\n%s\n\n\n" % (
        stem, options, rationale)


# ---------------------------------------------------------------------------
# The batch-framed browser surface (03.2-UI-SPEC sections 2 and 4): staged
# progress as a count (never a fill bar), the verbatim framing line, the
# candidate at text-body, the provenance line, the lint block, Accept/Skip/
# Cancel controls, and Accept disabled WITH its reason on lint errors -- never
# a silent dead button. No chat affordance anywhere.
# ---------------------------------------------------------------------------

def _resolved_provenance(block, sources):
    """The resolved [SRC:]/[OBJ:] lines for the surface's provenance line,
    or '' when the draft carries none (caller falls back to
    `No source recorded`)."""
    if not sources:
        return ""
    known = sources.get("sources") or {}
    parts = []
    for mm in _SRC_RE.finditer(block or ""):
        rest = mm.group(1).strip()
        split = rest.split(None, 1)
        sid, loc = (split[0], split[1]) if split else ("", "")
        if sid and sid in known:
            parts.append("[SRC: %s %s] -> %s" % (sid, loc, known[sid]).strip())
    for mm in _OBJ_RE.finditer(block or ""):
        oid = mm.group(1).strip()
        if oid and oid in known:
            parts.append("[OBJ: %s] -> %s" % (oid, known[oid]))
    return " · ".join(parts)


def _accept_surface_body(bank_path, draft, n, m, stage, sources):
    """The accept-loop body markup. Kept separate from the shell so the
    fixtures can assert the copy contract on the surface's own markup."""
    ps = parse_sources(bank_path) if sources is None else sources
    errors = draft.get("lint_errors") or []
    warnings = draft.get("warnings") or []
    block = draft.get("block") or ""
    provenance = _resolved_provenance(block, ps) or NO_SOURCE_RECORDED
    parts = [
        '<p class="ledger" data-seed-batch-framing>%s</p>'
        % presentation.esc(BATCH_FRAMING_LINE),
        '<p class="ledger" data-seed-progress>%s</p>'
        % presentation.esc(PROGRESS_LINE.format(n=n, m=m, stage=stage)),
        '<div class="item text-body" data-seed-item>%s</div>'
        % presentation.esc(block),
        '<p class="ledger" data-seed-provenance>%s</p>'
        % presentation.esc(provenance),
    ]
    if errors:
        parts.append(
            '<div class="lint lint-error" data-seed-lint="error"><p>%d lint '
            'error%s:</p><ul>%s</ul></div>'
            % (len(errors), "s" if len(errors) != 1 else "",
               "".join("<li>%s</li>" % presentation.esc(e) for e in errors)))
    elif warnings:
        parts.append(
            '<div class="lint lint-warn" data-seed-lint="warn"><p>%d lint '
            'warning%s:</p><ul>%s</ul></div>'
            % (len(warnings), "s" if len(warnings) != 1 else "",
               "".join("<li>%s</li>" % presentation.esc(w) for w in warnings)))
    else:
        parts.append('<div class="lint lint-clean" data-seed-lint="clean">'
                     "<p>No lint errors.</p></div>")
    accept = ('<button type="button" class="go primary" '
              'data-seed-action="accept">%s</button>' % ACCEPT_COPY)
    if errors:
        accept = ('<button type="button" class="go primary" '
                  'data-seed-action="accept" disabled>%s</button>' % ACCEPT_COPY)
        parts.append(
            '<p class="reason" role="status" data-seed-accept-reason>'
            "Accept disabled: %s</p>"
            % "; ".join(presentation.esc(e) for e in errors))
    parts.append(
        '<div class="actions">%s'
        '<button type="button" class="go" data-seed-action="skip">%s</button>'
        '<button type="button" class="go" data-seed-action="cancel">%s</button>'
        "</div>" % (accept, SKIP_COPY, CANCEL_COPY))
    return "\n".join(parts)


def render_accept_surface(bank_path, draft, n, m, stage=STAGE_ACCEPT,
                          sources=None, theme_css=""):
    """The batch-framed accept-loop browser page (UI-SPEC 2.1/2.2): one
    candidate at a time, the exact framing line, staged progress as a count,
    the candidate at text-body, the provenance line, the lint block, and
    Accept/Skip/Cancel controls. Accept is disabled with the stated reason on
    lint errors. The markup carries no chat affordance and no fill bar."""
    body = _accept_surface_body(bank_path, draft, n, m, stage, sources)
    return presentation.surface_shell("Seed a bank", body, theme_css=theme_css)


def render_cancelled_surface(theme_css=""):
    """The cancelled-run page: the verbatim summary `Nothing was written.`."""
    body = '<p class="ledger" data-seed-summary>%s</p>' \
        % presentation.esc(CANCELLED_SUMMARY)
    return presentation.surface_shell("Seed run cancelled", body,
                                      theme_css=theme_css)


def render_degraded_surface(theme_css=""):
    """The no-backend page: the exact D-10 refusal line, and no draft."""
    body = '<p class="ledger" data-seed-degraded>%s</p>' \
        % presentation.esc(BACKEND_UNREACHABLE)
    return presentation.surface_shell("Seed unavailable", body,
                                      theme_css=theme_css)
