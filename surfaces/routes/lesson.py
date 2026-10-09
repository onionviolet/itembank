"""Lesson routes; daemon-owned helpers are imported at request time."""
from model import lesson_slug
from model import load
from model import parse_activities
from model import parse_lesson
from model import parse_media
from runtime import lesson_run_record
from runtime import ordering_response_error
from runtime import read_lesson_run
from surfaces import lesson
from surfaces import quiz
import evidence
import os
import urllib.parse
import urllib.request


def handle_media_asset(handler, stem, name):
    """`GET /media/<stem>/<name>` -- one media file from the directory the
    bank at `stem` lives in, so a lesson can show the picture its own
    `## MEDIA` registry declares.

    Contained by resolution rather than by allowlist, because the files are
    the learner's and cannot be enumerated in advance: the stem must be one
    the startup scan already admitted, `..` is refused rather than clamped,
    the resolved real path must sit inside the bank's own directory after
    link resolution, and the extension must be a known static image type.
    Every refusal is the same plain 404, so a probe learns nothing about the
    filesystem it did not already know.
    """
    from surfaces.daemon import (
        MEDIA_ASSET_TYPES,
    )

    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    if os.path.pardir in name.replace("\\", "/").split("/"):
        handler.send_not_found(name)
        return
    mime = MEDIA_ASSET_TYPES.get(os.path.splitext(name)[1].lower())
    if mime is None:
        handler.send_not_found(name)
        return
    root = os.path.realpath(os.path.dirname(os.path.abspath(path)))
    target = os.path.realpath(os.path.join(root, name))
    try:
        contained = os.path.commonpath([root, target]) == root
    except ValueError:
        contained = False
    if not contained or target == root or not os.path.isfile(target):
        handler.send_not_found(name)
        return
    try:
        with open(target, "rb") as fh:
            body = fh.read()
    except OSError:
        handler.send_not_found(name)
        return
    handler.send_bytes(body, mime)


def _gate_answer_from_form(q, fields):
    """Serialise a gate band form submission into the answer shape the one
    scorer (`runtime.score_response`) and the one writer
    (`evidence.response_event`) expect -- the same shape `submit --answer`
    takes, so a lesson-gate attempt and a quiz attempt are the same object
    to every consumer (D-08). `fields` is `parse_qs`-shaped ({name:
    [values]}) because multi-select checkboxes repeat their name."""
    def one(name):
        vals = fields.get(name) or []
        return vals[-1] if vals else ""
    t = q["type"]
    if t in ("mc", "multi"):
        values = [v for v in (fields.get("option") or []) if v]
        if t == "mc":
            return values[0] if values else ""
        return sorted(set(values))
    if t in ("table", "dnd"):
        out = {}
        for i in range(len(q.get("rows") or [])):
            v = one("row_%d" % i)
            if v:
                out[str(q["rows"][i].get("id", i))] = v
        return out
    if t == "build":
        out = []
        blocks = q.get("blocks") if "ordering" in q else q.get("steps")
        for i in range(len(blocks or [])):
            v = one("step_%d" % i)
            if v:
                out.append(v)
        return out
    return one("answer")


def _section_after_check(lesson, check_id):
    """The slug of the section that follows the one carrying the check, or
    None when the check sits in the last section -- the gate-reveal focus
    target (06.2-UI-SPEC section 7.1)."""
    for idx, h in enumerate((lesson or {}).get("headings") or []):
        if "[!CHECK: %s]" % check_id in (h.get("body") or ""):
            rest = (lesson.get("headings") or [])[idx + 1:]
            return rest[0]["slug"] if rest else None
    return None


def handle_lesson_check(handler, stem):
    """`POST /lesson/<stem>/check` -- the gate band's check submission:
    scores through `runtime.score_response()` via the one shared
    `quiz.record_gate_check` path, records ordinary response evidence with
    context="lesson_gate" (D-08), and issues a 303 to the re-rendered
    lesson so a reload never re-submits the check (section 7.1). Under
    required with a cleared check the next section renders and focus
    targets its h2; the composed announcement appends `The next section is
    below.` (7.2).
    """
    from surfaces.daemon import (
        _lesson_gate_ctx,
        _lesson_run_path,
        _reject_cross_origin_write,
        _resolve_check,
    )

    if _reject_cross_origin_write(handler):
        return
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        qs = load(path)
        les = parse_lesson(path)
        fields = handler.read_form()
        check_id = (fields.get("check") or [""])[-1]
        q = _resolve_check(qs, check_id)
        if q is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        answer = _gate_answer_from_form(q, fields)
        if "ordering" in q:
            problem = ordering_response_error(q, answer)
            if problem:
                handler.send_error(400, problem)
                return
        sess = handler.sessions[stem]
        bank_dir = os.path.dirname(os.path.abspath(path)) or "."
        log = evidence.log_path(bank_dir)
        session_id = sess.get("session_id", "reader")
        # Phase 16D: a check submitted from the paced view is a lesson-run
        # checkpoint: same scorer, same store, context "lesson_run" and
        # mode "paced" on the event (D-PACED-2), the attempt summarised
        # into the run for gating and tier counts, and the redirect coming
        # back to the same paced step.
        paced_step = None
        if (fields.get("view") or [""])[-1] == "paced":
            paced_step = (fields.get("step") or [""])[-1] or None
        score = quiz.record_gate_check(
            path, check_id, answer,
            mode=("paced" if paced_step else sess.get("mode", "practice")),
            session_id=session_id,
            context=("lesson_run" if paced_step else "lesson_gate"))
        if score is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        if paced_step:
            run_path = _lesson_run_path(handler, stem, path)
            run = read_lesson_run(run_path)
            prior = ([a for a in run.get("attempts", ())
                      if a.get("item_id") == check_id]
                     if not run.get("error") else [])
            wrong_before = sum(1 for a in prior if a.get("state") == "held")
            state = "correct" if score is True else "held"
            tier = 0 if score is True else (1 if wrong_before == 0 else 3)
            stored = (answer if isinstance(answer, str)
                      else [str(x) for x in answer]
                      if isinstance(answer, list) else str(answer))
            lesson_run_record(run_path, check_id,
                             {"state": state, "attempt": len(prior) + 1,
                              "tier": tier, "answer": stored})
            if score is True:
                target = ("/lesson/%s?view=paced&step=%s&reveal=check"
                          % (stem, paced_step))
            else:
                target = ("/lesson/%s?view=paced&step=%s&checked=%s"
                          % (stem, paced_step, check_id))
            handler.send_redirect(target)
            return
        gate = _lesson_gate_ctx(handler, stem, path, qs, les)
        next_slug = None
        if gate is not None and gate["policy"] == "required" \
                and not gate.get("degraded") \
                and evidence.gate_state(log, session_id, check_id) == "cleared":
            next_slug = _section_after_check(les, check_id)
        if next_slug:
            target = ("/lesson/%s?focus=%s&reveal=check#%s"
                      % (stem, next_slug, next_slug))
        else:
            target = "/lesson/%s" % stem
        handler.send_redirect(target)
    except Exception as exc:
        handler.send_server_error(exc)


def handle_lesson_skip(handler, stem):
    """`POST /lesson/<stem>/skip` -- the recorded-skip action (D-11, C17):
    appends exactly one `gate_skip` event (never a response, never a hint
    tier), re-renders with the next section appended, and leaves the band
    live and answerable. A skip that was not recorded never advances the
    reading position (section 6.3): the event is written through the one
    shared `quiz.record_gate_skip` path before the redirect, and an
    unwritable log renders the section-12.1 copy instead of revealing.
    """
    from surfaces.daemon import (
        _lesson_gate_ctx,
        _lesson_run_path,
        _reject_cross_origin_write,
        media_base,
    )

    if _reject_cross_origin_write(handler):
        return
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    try:
        qs = load(path)
        les = parse_lesson(path)
        fields = handler.read_form()
        check_id = (fields.get("check") or [""])[-1]
        gate = _lesson_gate_ctx(handler, stem, path, qs, les)
        if gate is None or gate.get("degraded") or gate.get("unreachable"):
            # A degraded sitting records no gate_skip (there is nothing to
            # skip); an unreachable runtime must not reveal without its
            # event. Re-render with the honest copy (section 12.1).
            page = lesson.lesson_page(
                path, qs, les, runtime=True, gate=gate,
                media=parse_media(path), media_base=media_base(stem),
                activities=parse_activities(path))
            handler.send_html(page.encode("utf-8"))
            return
        sess = handler.sessions[stem]
        status = quiz.record_gate_skip(
            path, check_id, mode=sess.get("mode", "practice"),
            session_id=sess.get("session_id", "reader"))
        if status is None:
            handler.send_error(404, "no item %r in this bank" % check_id)
            return
        if status == "off":
            handler.send_error(400, "an off lesson offers no skip")
            return
        # Phase 16D: a paced skip opens the gate (gate on attempted; a skip
        # is the ordinary control 6.2 already made it) and returns to the
        # same step. The gate_skip event above is unchanged.
        if (fields.get("view") or [""])[-1] == "paced":
            paced_step = (fields.get("step") or [""])[-1] or None
            if paced_step:
                run_path = _lesson_run_path(handler, stem, path)
                run = read_lesson_run(run_path)
                prior = ([a for a in run.get("attempts", ())
                          if a.get("item_id") == check_id]
                         if not run.get("error") else [])
                lesson_run_record(run_path, check_id,
                                 {"state": "skipped",
                                  "attempt": len(prior) + 1, "tier": 0})
                handler.send_redirect(
                    "/lesson/%s?view=paced&step=%s&reveal=skip"
                    % (stem, paced_step))
                return
        next_slug = _section_after_check(les, check_id)
        if next_slug:
            target = ("/lesson/%s?focus=%s&reveal=skip#%s"
                      % (stem, next_slug, next_slug))
        else:
            target = "/lesson/%s?reveal=skip" % stem
        handler.send_redirect(target)
    except Exception as exc:
        handler.send_server_error(exc)


def handle_gloss_get(handler, stem, slug):
    """`GET /gloss/<stem>/<slug>` -- one term's definition from the bank's
    `## TERMS` block, gated server-side by `glossable()` before any
    definition leaves the process (D-20), with a `term_lookup` event
    recorded through the one evidence writer (D-19, UI-SPEC §8.3/§8.5).

    A suppressed term returns the same bare 404 an unknown slug gets, with
    no event: per-term disclosure is exactly what §8.4 forbids, and an
    indistinguishable 404 is how the route keeps that promise structurally.
    The session_id and mode come from the daemon's own per-bank session
    bookkeeping when present, falling back to a stable reader identity and
    the practice default -- the route records provenance, never a guess.
    """
    path = handler.banks.get(stem)
    if path is None:
        handler.send_not_found(stem)
        return
    status, record = lesson.gloss_lookup(path, slug)
    if status != "ok":
        handler.send_not_found(slug)
        return
    sess = handler.sessions.get(stem) or {}
    bank_dir = os.path.dirname(os.path.abspath(path)) or "."
    event = evidence.term_lookup_event(
        session_id=sess.get("session_id", "reader"),
        bank=os.path.basename(path),
        term_slug=lesson_slug(slug),
        mode=sess.get("mode", "practice"),
        source="session")
    evidence.append_event(evidence.log_path(bank_dir), event)
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(handler.path).query)
    if query.get("format", [""])[-1] == "json":
        handler.send_json({"term": record.get("canonical", ""),
                           "def": record.get("def", "")})
        return
    return_href = query.get("return", [""])[-1]
    if not (return_href.startswith("/quiz/") and
            not return_href.startswith("//")):
        return_href = None
    handler.send_html(lesson.gloss_page(
        stem, record, lesson_slug(slug), return_href=return_href).encode("utf-8"))

