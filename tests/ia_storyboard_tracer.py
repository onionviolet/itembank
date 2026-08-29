#!/usr/bin/env python3
"""Interrupt each of the seven end-to-end loops mid-step, then walk a reading,
lesson, practice, and feedback path with the model backend genuinely disabled.

Two requirements are executable here rather than asserted. FLOW-01 says every
loop resumes at an exact position with a next justified action, so each loop is
interrupted at a fixed mid-loop step, every in-memory reference is dropped, and
the resume state is recomputed from a file read back off disk. FLOW-02 says the
core loop degrades and never blocks, so the walk runs the real CLI against the
real runtime with no model backend configured and asserts that scoring, the
authored hint ladder, evidence, and reports all still run.

The failure both guard against is a loop that only looks resumable because the
test kept the answer in memory, and a core loop that quietly depends on a model
being reachable.

Standard library only, no test framework, runnable as
`python tests/ia_storyboard_tracer.py`.
"""
import inspect, io, json, os, random, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                             # noqa: E402
import evidence                                             # noqa: E402
import model                                                # noqa: E402
import runtime                                              # noqa: E402
from surfaces import ia                                     # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "fixtures"))
import course_storyboard_corpus as corpus                   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from daemon_roundtrip import start_daemon, get              # noqa: E402

ITEMBANK = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
LESSON_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")

UI_SPEC = os.path.join(
    ROOT, ".planning", "phases", "16B-ia-modes-recovery-contract",
    "16B-UI-SPEC.md")

# Stages of the FLOW-02 walk that could not be exercised in this environment.
# Reported in the summary line rather than counted as passes.
SKIPPED = []


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def skip(stage, why):
    SKIPPED.append("%s: %s" % (stage, why))


def run(args, cwd=None, env=None):
    return subprocess.run([sys.executable, ITEMBANK] + list(args),
                          capture_output=True, text=True, cwd=cwd, env=env)


def _assert_boundaries(loop):
    """Every step boundary of one loop resumes at the following step."""
    spec = ia.LOOP_STEPS[loop]
    steps = spec["steps"]
    if len(set(steps)) != len(steps):
        fail("loop %s has a duplicate step" % loop)
    for step in steps:
        if not step.strip():
            fail("loop %s has an empty step" % loop)

    for i in range(len(steps) + 1):
        state = ia.loop_resume_state(loop, i)
        if state["completed_step"] != i:
            fail("loop %s at boundary %d reported completed_step %d"
                 % (loop, i, state["completed_step"]))
        if i < len(steps):
            if state["next_step"] != steps[i]:
                fail("loop %s at boundary %d resumed at %r, expected %r"
                     % (loop, i, state["next_step"], steps[i]))
            if state["at_end"]:
                fail("loop %s reported at_end before its final boundary" % loop)
        else:
            if state["next_step"] is not None:
                fail("loop %s past its last step still named a next step"
                     % loop)
            if not state["at_end"]:
                fail("loop %s did not report at_end at its final boundary"
                     % loop)
        if state["resume_unit"] != spec["resume_unit"]:
            fail("loop %s reported the resume unit %r"
                 % (loop, state["resume_unit"]))
        if not state["next_action"]:
            fail("loop %s at boundary %d owed no next action" % (loop, i))
        if "%" in state["next_action"]:
            fail("loop %s's next action carried a percent character" % loop)


def _assert_durable_interruption(loop):
    """The resume state survives losing every in-memory reference."""
    workdir = tempfile.mkdtemp(prefix="storyboard_%s_" % loop.lower())
    try:
        written = corpus.build_loop_storyboard(workdir)
        path = written[loop]

        record = json.load(io.open(path, encoding="utf-8"))
        before = ia.loop_resume_state(loop, record["completed_step"])
        expected = ia.LOOP_STEPS[loop]["steps"][record["completed_step"]]
        if before["next_step"] != expected:
            fail("loop %s resumed at %r, expected %r"
                 % (loop, before["next_step"], expected))

        # Drop every in-memory reference and recompute from disk alone. This
        # is the "never from client-side memory alone" rule executed rather
        # than described.
        del record
        reread = json.load(io.open(path, encoding="utf-8"))
        after = ia.loop_resume_state(loop, reread["completed_step"])
        if after != before:
            fail("loop %s did not recompute an identical resume state from "
                 "disk: %r vs %r" % (loop, after, before))

        raw = io.open(path, encoding="utf-8").read()
        if "%" in raw:
            fail("loop %s's record carried a percent character" % loop)
        if os.path.abspath(workdir) in raw or "/Users/" in raw:
            fail("loop %s's record carried an absolute path" % loop)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _loop_scenario(loop):
    _assert_boundaries(loop)
    _assert_durable_interruption(loop)


def scenario_loop_a():
    _loop_scenario("A")


def scenario_loop_b():
    _loop_scenario("B")


def scenario_loop_c():
    _loop_scenario("C")


def scenario_loop_d():
    _loop_scenario("D")


def scenario_loop_e():
    _loop_scenario("E")


def scenario_loop_f():
    _loop_scenario("F")


def scenario_loop_g():
    _loop_scenario("G")


def scenario_empty_loops():
    """An empty run of every loop states an outcome, not an absence."""
    outcomes = set()
    for loop in ia.LOOP_ORDER:
        state = ia.loop_resume_state(loop, 0, item_count=0)
        if state["empty"] is not True:
            fail("loop %s with zero items did not report empty" % loop)
        if state["outcome"] != ia.LOOP_EMPTY_OUTCOME[loop]:
            fail("loop %s's empty outcome was %r" % (loop, state["outcome"]))
        if not state["outcome"].strip() or not state["outcome"].endswith("."):
            fail("loop %s's empty outcome is not a sentence: %r"
                 % (loop, state["outcome"]))
        if not state["next_action"]:
            fail("loop %s owed no next action when empty" % loop)
        lowered = state["outcome"].lower()
        for banned in ("nothing to show", "no data", "empty"):
            if banned in lowered:
                fail("loop %s's empty outcome reports an absence (%r) rather "
                     "than an outcome" % (loop, banned))
        outcomes.add(state["outcome"])
    if len(outcomes) != len(ia.LOOP_ORDER):
        fail("two loops share an empty outcome sentence")

    try:
        ia.loop_resume_state("Z", 0)
    except ValueError as exc:
        if "Z" not in str(exc):
            fail("the unknown-loop error did not name the loop: %s" % exc)
    else:
        fail("an unknown loop returned a plausible-looking result")

    source = inspect.getsource(ia.loop_resume_state)
    for banned in ("open(", "import "):
        if banned in source:
            fail("loop_resume_state reads more than its arguments: %r" % banned)


def scenario_loop_ordering():
    """One total order across ten seeded shuffles, with course id last."""
    entries = [
        {"loop": "C", "course_id": "crs-b", "last_activity": "2026-03-01T00:00:00Z"},
        {"loop": "C", "course_id": "crs-a", "last_activity": "2026-03-01T00:00:00Z"},
        {"loop": "D", "course_id": "crs-a", "last_activity": "2026-03-01T00:00:00Z"},
        {"loop": "D", "course_id": "crs-a", "last_activity": "2026-03-05T00:00:00Z"},
        {"loop": "A", "course_id": "crs-a", "last_activity": "2026-03-01T00:00:00Z"},
        {"loop": "B", "course_id": "crs-a", "last_activity": "2026-03-01T00:00:00Z"},
    ]
    sequences = set()
    for _ in range(10):
        shuffled = list(entries)
        random.Random(20260815).shuffle(shuffled)
        ordered = ia.resumable_loops(shuffled)
        sequences.add(tuple((e["loop"], e["course_id"],
                             e["last_activity"]) for e in ordered))
    if len(sequences) != 1:
        fail("ten shuffles produced %d different orders" % len(sequences))

    ordered = ia.resumable_loops(entries)
    letters = [e["loop"] for e in ordered]
    if letters != sorted(letters, key=ia.LOOP_ORDER.index):
        fail("loops were not ordered by LOOP_ORDER: %r" % letters)

    same_loop = [e for e in ordered if e["loop"] == "C"]
    if [e["course_id"] for e in same_loop] != ["crs-a", "crs-b"]:
        fail("the course-id final tiebreak did not fire: %r"
             % [e["course_id"] for e in same_loop])

    d_entries = [e for e in ordered if e["loop"] == "D"]
    if [e["last_activity"] for e in d_entries] != ["2026-03-05T00:00:00Z",
                                                   "2026-03-01T00:00:00Z"]:
        fail("same-loop entries were not ordered newest first: %r" % d_entries)


def scenario_steps_are_verbatim():
    """Every step string appears verbatim in the approved contract."""
    spec = io.open(UI_SPEC, encoding="utf-8").read()
    for loop in ia.LOOP_ORDER:
        for step in ia.LOOP_STEPS[loop]["steps"]:
            if step not in spec:
                fail("loop %s's step %r is not in the UI-SPEC verbatim"
                     % (loop, step))
        if ia.LOOP_STEPS[loop]["resume_unit"] not in spec:
            fail("loop %s's resume unit is not in the UI-SPEC verbatim" % loop)
    counts = [len(ia.LOOP_STEPS[k]["steps"]) for k in ia.LOOP_ORDER]
    if counts != [9, 9, 9, 8, 6, 9, 9] or sum(counts) != 59:
        fail("the transcribed step counts are %r, totalling %d"
             % (counts, sum(counts)))


def _disabled_backend_dir():
    """A temp root with the two synthetic banks and the shipped no-backend
    configuration.

    Branch one of plan 16B-10 Task 3 step 1: `tests/model_adapter_roundtrip.py`
    already disables the backend with `model_backend.active == ""`, which
    `model_adapter.resolve_profile` answers with `adapter.profile_disabled`.
    That mechanism is reused verbatim rather than a second one invented.
    """
    workdir = tempfile.mkdtemp(prefix="flow02_walk_")
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    shutil.copy(LESSON_BANK, os.path.join(workdir, "lesson_bank.md"))
    with io.open(os.path.join(workdir, "itembank.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps({"model_backend": {"active": "", "profiles": []}}))
    return workdir


def scenario_model_disabled_walk():
    """Reading, practice, scoring, hints, evidence, and reports all run with
    no model backend configured."""
    workdir = _disabled_backend_dir()
    env = dict(os.environ)
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                 "http_proxy", "https_proxy", "all_proxy"):
        env.pop(name, None)
    bank = os.path.join(workdir, "sample_bank.md")
    lesson_bank = os.path.join(workdir, "lesson_bank.md")
    session = os.path.join(workdir, "session.json")
    proc = None
    try:
        # Reading, and it is continuous.
        result = run(["lesson", lesson_bank], cwd=workdir, env=env)
        if result.returncode != 0:
            fail("reading failed with the backend disabled: %s"
                 % (result.stdout + result.stderr))
        for banned in ("Next page", "Previous page", "page="):
            if banned in result.stdout:
                fail("reading paginated: %r" % banned)

        # Practice reached from the same bank, without the test supplying
        # context by hand.
        # `--type mc` so the walk lands on a multiple-choice item and the
        # scoring stage exercises a real letter answer. Without it the
        # selector can serve a drag-and-drop item, whose response is not a
        # letter, and the scoring stage would skip rather than run.
        result = run(["start", bank, "--out", session, "--count", "2",
                      "--type", "mc"], cwd=workdir, env=env)
        if result.returncode != 0:
            fail("starting practice failed: %s"
                 % (result.stdout + result.stderr))
        stored = json.load(io.open(session, encoding="utf-8"))
        if os.path.basename(stored["bank"]) != "sample_bank.md":
            fail("the session names %r, not the bank the walk read from"
                 % stored["bank"])

        # The public item carries no key.
        result = run(["next", session], cwd=workdir, env=env)
        if result.returncode != 0:
            fail("next failed with the backend disabled: %s"
                 % (result.stdout + result.stderr))
        served = json.loads(result.stdout)
        item = served.get("item") or served
        for banned in ("correct", "da", "why"):
            if banned in item:
                fail("the served public item carried %r" % banned)

        # Scoring, and the served verdict equals the one scorer's.
        questions = model.load(bank)
        target = [q for q in questions if q["id"] == item.get("id")]
        if not target:
            target = [questions[stored["items"][stored["cursor"]]]]
        question = target[0]
        options = item.get("options") or []
        wrong = None
        for letter in "ABCDEFGH"[:len(options)]:
            if runtime.score_response(question, [letter]) is False:
                wrong = letter
                break
        if wrong is None:
            skip("scoring", "no wrong option was available on the served item")
        else:
            result = run(["submit", session, "--answer", wrong],
                         cwd=workdir, env=env)
            if result.returncode != 0:
                fail("submit failed with the backend disabled: %s"
                     % (result.stdout + result.stderr))
            stored = json.load(io.open(session, encoding="utf-8"))
            recorded = stored["responses"][-1]
            in_process = runtime.score_response(question, [wrong])
            if recorded.get("score") != in_process:
                fail("the recorded verdict %r disagrees with the one scorer's "
                     "%r" % (recorded.get("score"), in_process))

        # The authored hint ladder still runs with no model reachable.
        result = run(["teach", session], cwd=workdir, env=env)
        if result.returncode != 0:
            fail("the authored hint ladder failed with the backend disabled: "
                 "%s" % (result.stdout + result.stderr))
        combined = result.stdout + result.stderr
        for banned in ("generated for you", "I think", "as an AI"):
            if banned in combined:
                fail("the authored ladder emitted generated-sounding copy: %r"
                     % banned)

        # Evidence.
        result = run(["evidence", "--session", session, "--base", workdir],
                     cwd=workdir, env=env)
        if result.returncode != 0:
            fail("evidence failed with the backend disabled: %s"
                 % (result.stdout + result.stderr))

        # Report, and it separates settled from pending rather than reporting
        # one number.
        result = run(["report", session], cwd=workdir, env=env)
        if result.returncode != 0:
            fail("report failed with the backend disabled: %s"
                 % (result.stdout + result.stderr))
        report = result.stdout
        if "%" in report:
            fail("the report carried a percent character")
        lowered = report.lower()
        if "settled" not in lowered and "pending" not in lowered:
            fail("the report did not separate settled from pending")

        # The loop closes: the home names the bank the walk was in.
        proc, url, lines = start_daemon(workdir)
        status, body = get(url)
        if status != 200:
            fail("the home returned %d after the walk" % status)
        if "sample_bank" not in body:
            fail("the home did not name the bank the walk was in")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def scenario_no_second_authority():
    """One scorer, one parser, one evidence store, and no second one here."""
    own = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    for match in re.findall(r"\b(\w*[Ss]core\w*)\s*\(", own):
        if match != "score_response":
            fail("this tracer reaches a verdict through %r rather than "
                 "runtime.score_response" % match)

    source = io.open(os.path.join(ROOT, "surfaces", "ia.py"),
                     encoding="utf-8").read()
    body = re.sub(r"^\s*#.*$", "", source, flags=re.M)
    body = re.sub(r'"""[\s\S]*?"""', "", body)
    # Strip string literals too. Loop D's verbatim UI-SPEC step text contains
    # the phrase "runtime records/scores or marks pending", which is the
    # contract being transcribed rather than a call being made, and a raw
    # substring scan cannot tell the two apart.
    code = re.sub(r"'[^'\n]*'", "''", re.sub(r'"[^"\n]*"', '""', body))
    for banned in ("import runtime", "score", "parse_bank", "mark_event"):
        if banned in code:
            fail("surfaces/ia.py reaches for assessment authority: %r"
                 % banned)

    workdir = tempfile.mkdtemp(prefix="authority_")
    try:
        try:
            evidence.mark_event(workdir, "any-id", "correct", marker="model")
        except (ValueError, TypeError):
            pass
        except Exception as exc:
            fail("mark_event refused a model marker with %s, expected a "
                 "ValueError" % type(exc).__name__)
        else:
            fail("evidence.mark_event accepted a non-human marker")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    questions = model.load(BANK)
    public = runtime.public_item(questions[0])
    if "correct" in public:
        fail("public_item leaked the answer key")


SCENARIOS = (scenario_loop_a, scenario_loop_b, scenario_loop_c,
             scenario_loop_d, scenario_loop_e, scenario_loop_f,
             scenario_loop_g, scenario_empty_loops, scenario_loop_ordering,
             scenario_steps_are_verbatim, scenario_model_disabled_walk,
             scenario_no_second_authority)


def main():
    for scenario in SCENARIOS:
        scenario()
    for note in SKIPPED:
        print("  SKIPPED " + note)
    print("STORYBOARD: %d passed, %d skipped, 0 failed"
          % (len(SCENARIOS), len(SKIPPED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
