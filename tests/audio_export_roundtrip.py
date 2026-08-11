#!/usr/bin/env python3
"""Audio drill pack export roundtrip: the TTSEngine interface + registry,
transcript-only engine, objective resolution, the stem->pause->key->why
sequence builder, the audio settings block, the export audio CLI, digest
naming, atomic writes, and the no-evidence boundary (phase 09.1 plans
09.1-01..04).

Standard library only, runnable as `python tests/audio_export_roundtrip.py`.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "itembank.py")
BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
SCHEMA = os.path.join(ROOT, "schemas", "settings.schema.json")

sys.path.insert(0, ROOT)
from surfaces import audio as audio_surface                     # noqa: E402
from surfaces.audio import TTSEngine                            # noqa: E402
import evidence                                                 # noqa: E402
from model import parse_sources                                 # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(*args, cwd=None, check=False):
    flat = []
    for a in args:
        if isinstance(a, (list, tuple)):
            flat.extend(a)
        else:
            flat.append(a)
    return subprocess.run([sys.executable, TOOL, *map(str, flat)],
                          cwd=cwd or ROOT, check=check,
                          capture_output=True, text=True)


# A small bank with two objectives and mixed item types so the pause map and
# bank-order resolution are exercised without touching the shared fixture.
AUDIO_BANK = """# Audio fixture bank (synthetic)

Fully invented content for the audio drill export fixtures. No real exam
content.

Q1. What does a rising chlorine residual indicate?   (difficulty: recall)
[OBJECTIVE: Water / chemistry]
A) The plant is underdosing
B) The plant is overdosing
C) Nothing, residuals drift
D) Demand fell sharply
CORRECT: B
WHY BEST: A rising residual means more disinfectant survives the trip.
KEY DISCRIMINATOR: The direction of the trend.
SECOND-BEST: D. A demand drop would also raise the residual.
DISTRACTOR ANALYSIS:
- A) Underdosing lowers the residual; correct if the residual fell.
- B) Correct: the keyed answer.
- C) Residuals are stable at steady state; correct if the instrument drifted.
- D) Demand falling raises residual; correct if the question asked why.
TRAP: Reading the trend backwards.
CONFIDENCE: high

Q2. Put the treatment train in order.   (difficulty: application)
[TYPE: build]
[OBJECTIVE: Water / chemistry]
STEP) Coagulation
STEP) Flocculation
STEP) Sedimentation
STEP) Filtration
STEP) Disinfection
WHY BEST: Coagulation first, disinfection last.
KEY DISCRIMINATOR: Sedimentation precedes filtration.
TRAP: Reversing filtration and disinfection.
CONFIDENCE: high

Q3. Explain residual maintenance.   (difficulty: analysis)
[TYPE: short]
[OBJECTIVE: Public / notification]
MODEL: Keep chlorine above the regulatory floor at the far end of the network.
RUBRIC:
- Names the regulatory floor
- Names the far end
TRAP: Talking only about the plant outlet.
CONFIDENCE: high
"""

# The [OBJ:] grammar variant: a ## SOURCES registry + [OBJ:] directives, so
# objective resolution through the Phase 3.2 registry is exercised too.
OBJ_BANK = """# Provenance audio fixture (synthetic)

## SOURCES

emt:airway | EMT airway chapter, sect. 5

Q1. Which finding suggests an at-risk airway?   (difficulty: application)
[SRC: emt:airway p. 214]
[OBJ: emt:airway]
[OBJECTIVE: emt:airway]
A) Snoring respirations with a weak effort
B) Thirst
C) Tachycardia
D) Warm dry skin
CORRECT: A
WHY BEST: Snoring with a weak effort is obstruction with failing compensation.
KEY DISCRIMINATOR: Air movement itself is threatened.
SECOND-BEST: B. Thirst is a perfusion finding.
DISTRACTOR ANALYSIS:
- A) Correct: the keyed answer.
- B) Perfusion, not airway.
- C) Compensation, not airway.
- D) Perfusion, not airway.
TRAP: Any abnormal vital sign.
CONFIDENCE: high

Q2. Which airway adjunct keeps the tongue off the posterior pharynx?   (difficulty: recall)
[OBJ: emt:airway]
[OBJECTIVE: emt:airway]
A) Oropharyngeal airway
B) Nasal cannula
C) Nebulizer
D) Tourniquet
CORRECT: A
WHY BEST: The OPA holds the tongue forward mechanically.
KEY DISCRIMINATOR: It is a mechanical, not a medication, device.
SECOND-BEST: B. A cannula delivers oxygen; correct if the question asked
about oxygen delivery.
DISTRACTOR ANALYSIS:
- A) Correct: the keyed answer.
- B) Oxygen delivery, not airway positioning.
- C) Medication delivery, not airway positioning.
- D) Hemorrhage control, not airway.
TRAP: Confusing adjuncts with oxygen devices.
CONFIDENCE: high
"""

# Pre-change golden output of `itembank export fixtures/sample_bank.md OUT
# --format basic`, captured before plan 09.1-01 touched the export parser.
# The legacy flat form must stay byte-identical (D-08, AUDIO-05).
LEGACY_GOLDEN = (
    "#separator:tab\n"
    "#html:true\n"
    "#notetype:Basic\n"
    "#tags column:3\n"
    "Front\tBack\tTags\n"
    "An operator notices the chlorine residual at the far end of the distribution "
    "network has fallen below the regulatory floor, while the reading at the plant "
    "outlet is normal. What is the most likely explanation? Options: A) The plant is "
    "underdosing chlorine | B) Chlorine demand in the network is consuming the residual "
    "before it reaches the far end | C) The far-end sampling tap is contaminated | D) "
    "The regulatory floor was recently raised\tB) Chlorine demand in the network is "
    "consuming the residual before it reaches the far end<br><br>A normal outlet "
    "reading rules out underdosing at the source, so the loss is happening in transit. "
    "Chlorine demand from biofilm, sediment, and long residence time consumes residual "
    "as water travels.\titembank\n"
    "Which conditions require an immediate boil-water notice? Options: A) Loss of "
    "positive pressure across the distribution system | B) A single customer complaint "
    "about taste | C) Confirmed detection of E. coli in a routine sample | D) A "
    "scheduled hydrant flushing program | E) A turbidity reading slightly below the "
    "action level\tA) Loss of positive pressure across the distribution system; C) "
    "Confirmed detection of E. coli in a routine sample<br><br>Both indicate a credible "
    "pathway for pathogens to reach customers. Loss of pressure allows intrusion; a "
    "confirmed indicator organism means contamination is already present.\titembank\n"
    "Classify each task as ROUTINE or EMERGENCY response.\tMonthly calibration of a "
    "turbidimeter -> Routine; Responding to a confirmed main break flooding a street -> "
    "Emergency; Quarterly lead and copper sampling -> Routine; Isolating a section after "
    "a chemical spill enters a storm drain -> Emergency<br><br>Scheduled, "
    "calendar-driven work is routine. Unplanned events that threaten water quality or "
    "public safety are emergencies.\titembank\n"
    "Put the conventional surface-water treatment train in order.\tCoagulation -> "
    "Flocculation -> Sedimentation -> Filtration -> Disinfection<br><br>Coagulant "
    "destabilises particles, gentle mixing grows them into settleable floc, gravity "
    "removes the bulk, filtration removes what remains, and disinfection treats the "
    "clarified water.\titembank\n"
    "Sort each parameter into PRIMARY or SECONDARY drinking-water standard.\tTotal "
    "coliform -> Primary; Lead -> Primary; Iron staining laundry -> Secondary; Odour -> "
    "Secondary<br><br>Primary standards are enforceable and protect health. Secondary "
    "standards are guidelines covering aesthetics: taste, odour, colour, staining."
    "\titembank\n"
    "A plant meets every primary standard but customers still complain the water is "
    "undrinkable. Explain how both facts can be true at once, and what the operator "
    "should investigate.\tPrimary standards are health-based and enforceable; they say "
    "nothing about taste, odour, colour or staining, which secondary standards cover as "
    "non-enforceable guidelines. Water can therefore be legally safe and aesthetically "
    "unacceptable at the same time. The operator should investigate the secondary "
    "parameters, iron and manganese for staining and taste, sulphide or algal by-products "
    "for odour, and turbidity or colour for appearance.\titembank\n"
)


def write_bank(tmp, text=AUDIO_BANK, name="audio_bank.md"):
    p = os.path.join(tmp, name)
    open(p, "w", encoding="utf-8").write(text)
    return p


def namespace(**kw):
    base = dict(bank="audio", out=None, objective=None, engine=None,
                split=None, container=None, out_dir=None)
    base.update(kw)
    return argparse.Namespace(**base)


# ---- Task 1: the interface, the registry, and transcript-only -------------

def test_registry_resolves_fake_engine_by_name():
    """A fake engine registered by name resolves through TTSEngines with no
    branch in any dispatcher; the interface exposes name, container,
    available() and speak(text) -> bytes (D-01, AUDIO-01)."""
    class Fake(TTSEngine):
        name = "fake-registered"
        container = "mp3"

        def available(self):
            return True

        def speak(self, text):
            return b"AUDIO:" + text.encode("utf-8")

    audio_surface.TTSEngines["fake-registered"] = lambda: Fake()
    try:
        eng = audio_surface.resolve_engine("fake-registered")
        if eng.name != "fake-registered" or eng.container != "mp3":
            fail("registry resolved engine lost its name/container")
        if not eng.available():
            fail("fake engine must report available")
        got = eng.speak("hello")
        if got != b"AUDIO:hello":
            fail("speak() did not return the engine's bytes")
    finally:
        audio_surface.TTSEngines.pop("fake-registered", None)


def test_transcript_only_is_a_real_registered_engine():
    """transcript-only is registered by name, always available, and speak()
    returns None -- a real engine, not an error path (D-02/D-03)."""
    if "transcript-only" not in audio_surface.TTSEngines:
        fail("transcript-only is not registered in TTSEngines")
    eng = audio_surface.resolve_engine("transcript-only")
    if not eng.available():
        fail("transcript-only must always be available")
    if eng.speak("anything") is not None:
        fail("transcript-only speak() must return None, not bytes")


def test_unknown_engine_refuses_by_name():
    """An unknown engine name resolves to a named refusal listing the engine
    name -- never a KeyError or a silent default (D-04)."""
    try:
        audio_surface.resolve_engine("no-such-engine")
        fail("unknown engine did not refuse")
    except audio_surface.EngineError as exc:
        if "no-such-engine" not in str(exc):
            fail("refusal does not name the engine: %r" % str(exc))
    except KeyError:
        fail("unknown engine leaked a KeyError instead of a named refusal")


# ---- Task 2: objective resolution, the sequence builder, settings ----------

def test_resolve_objective_items_bank_order_and_obj_grammar():
    """resolve_objective_items returns the objective's items in bank order via
    the [OBJ:] grammar when present, else via the item [OBJECTIVE:]/Educational
    Objective line; an unknown objective id is a named refusal (D-04)."""
    tmp = tempfile.mkdtemp()
    try:
        bank = write_bank(tmp)
        items = audio_surface.resolve_objective_items(bank, "Water / chemistry")
        stems = [q["stem"] for q in items]
        if len(stems) != 2 or "residual indicate" not in stems[0] \
                or "treatment train" not in stems[1]:
            fail("Water / chemistry did not resolve to its two items in bank "
                 "order: %r" % stems)
        pub = audio_surface.resolve_objective_items(bank, "Public / notification")
        if len(pub) != 1 or "residual maintenance" not in pub[0]["stem"]:
            fail("Public / notification did not resolve to its one item")

        # [OBJ:] grammar: both items carry [OBJ: emt:airway] and the registry
        # row registers emt:airway, so both resolve under the obj id.
        obj_bank = write_bank(tmp, OBJ_BANK, name="obj_bank.md")
        ps = parse_sources(obj_bank)
        if "emt:airway" not in (ps or {}).get("sources", {}):
            fail("## SOURCES did not register emt:airway")
        air = audio_surface.resolve_objective_items(obj_bank, "emt:airway")
        if len(air) != 2:
            fail("[OBJ:] resolution returned %d items, expected 2" % len(air))

        try:
            audio_surface.resolve_objective_items(bank, "No / such objective")
            fail("unknown objective id did not refuse")
        except audio_surface.EngineError as exc:
            if "No / such objective" not in str(exc):
                fail("objective refusal does not name the id: %r" % str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_build_sequence_and_transcript_contract():
    """build_sequence yields stem -> timed pause -> key -> why per item with
    the pause duration read from the per-item-type map (D-06/D-07), and the
    transcript text equals the sequence's spoken text in the same order
    (D-11's diffable contract)."""
    tmp = tempfile.mkdtemp()
    try:
        bank = write_bank(tmp)
        items = audio_surface.resolve_objective_items(bank, "Water / chemistry")
        pause_map = {"mc": 1.5, "multi": 2.0, "short": 2.0, "cloze": 2.5,
                     "build": 4.0, "table": 3.0, "dnd": 3.0, "check": 3.0}
        seq = audio_surface.build_sequence(items, pause_map)
        kinds = [s["kind"] for s in seq]
        if kinds != ["stem", "pause", "key", "why",
                     "stem", "pause", "key", "why"]:
            fail("sequence kinds are not stem->pause->key->why per item: %r"
                 % kinds)
        if seq[1]["seconds"] != 1.5:
            fail("mc pause is not 1.5s: %r" % seq[1]["seconds"])
        if seq[5]["seconds"] != 4.0:
            fail("build pause is not 4.0s: %r" % seq[5]["seconds"])
        spoken = [s["text"] for s in seq if s["kind"] != "pause"]
        transcript = audio_surface.pack_transcript(seq)
        if transcript != "\n\n".join(spoken) + "\n":
            fail("transcript does not equal the spoken text in order:\n%r\n%r"
                 % (transcript, spoken))
        if seq[2]["kind"] != "key" or not seq[2]["text"]:
            fail("key segment missing its answer text")
        if seq[3]["kind"] != "why" or not seq[3]["text"]:
            fail("why segment missing its why/disc text")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_settings_schema_audio_block():
    """The settings schema validates the audio block: engine enum defaults to
    edge-tts, container to mp3, split to per-pack; a hand-edited invalid value
    is rejected by the one validator, and `itembank config` prints the keys
    (D-07/D-09/D-10)."""
    import schema_validate
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    audio = schema.get("properties", {}).get("audio")
    if not audio:
        fail("settings schema has no audio block")
    if audio["properties"]["engine"]["default"] != "edge-tts" or \
            audio["properties"]["engine"]["enum"] != \
            ["edge-tts", "piper", "transcript-only"]:
        fail("audio.engine must enum edge-tts|piper|transcript-only default "
             "edge-tts")
    if audio["properties"]["container"]["default"] != "mp3":
        fail("audio.container must default to mp3")
    if audio["properties"]["split"]["default"] != "per-pack":
        fail("audio.split must default to per-pack")
    for key in ("mc", "multi", "short", "cloze", "build", "table", "dnd",
                "check"):
        if key not in audio["properties"]["pause"]["properties"]:
            fail("audio.pause is missing the %r item type" % key)
    # A hand-edited invalid value is rejected by the one validator.
    errs = schema_validate.validate({"engine": "kokoro", "container": "mp3",
                                     "split": "per-pack", "pause": {},
                                     "edge_tts": {"voice": "x"},
                                     "piper": {"voice": "x", "model": "x"}},
                                    audio)
    if not errs:
        fail("schema_validate accepted audio.engine = kokoro")
    # The one settings surface prints the new keys.
    r = run(["config"])
    if r.returncode != 0:
        fail("itembank config exited %d: %s" % (r.returncode, r.stderr))
    for token in ("audio", "audio.engine", "audio.pause", "audio.edge_tts"):
        if token not in r.stdout:
            fail("itembank config table is missing %r" % token)


# ---- Task 3: the CLI, transcript, digest naming, atomic write, no evidence -

def test_cli_transcript_only_and_legacy_byte_compat():
    """`itembank export audio <bank> --objective <id> --engine transcript-only`
    writes the transcript file and exits 0 with no audio file; the legacy flat
    `itembank export <bank> <out> --format basic` stays byte-identical
    (D-08/D-11, AUDIO-05)."""
    tmp = tempfile.mkdtemp()
    try:
        bank = write_bank(tmp)
        out_dir = os.path.join(tmp, "pack")
        r = run(["export", "audio", bank, "--objective", "Water / chemistry",
                 "--engine", "transcript-only", "--out", out_dir])
        if r.returncode != 0:
            fail("export audio exited %d: %s" % (r.returncode, r.stdout + r.stderr))
        files = os.listdir(out_dir)
        txt = [f for f in files if f.endswith(".txt")]
        aud = [f for f in files if f.endswith((".mp3", ".wav"))]
        if len(txt) != 1:
            fail("expected exactly one transcript, got %r" % files)
        if aud:
            fail("transcript-only must write no audio file, got %r" % aud)
        transcript = open(os.path.join(out_dir, txt[0]), encoding="utf-8").read()
        if "residual indicate" not in transcript or \
                "treatment train" not in transcript:
            fail("transcript is missing the objective's spoken text")

        # The legacy flat form stays byte-identical to the pre-change golden.
        out_tsv = os.path.join(tmp, "legacy.tsv")
        r2 = run(["export", BANK, out_tsv, "--format", "basic"])
        if r2.returncode != 0:
            fail("legacy flat export exited %d: %s"
                 % (r2.returncode, r2.stdout + r2.stderr))
        got = open(out_tsv, encoding="utf-8").read()
        if got != LEGACY_GOLDEN:
            fail("legacy flat export is not byte-identical to the pre-change "
                 "golden")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_failing_engine_leaves_no_partial_audio():
    """A fake engine that raises EngineError mid-run leaves no partial audio
    file anywhere, the transcript still writes, and the exit code is non-zero
    with the engine name and reason in the message (D-04/D-05, AUDIO-04)."""
    class FailingEngine(TTSEngine):
        name = "fake-failing"
        container = "mp3"

        def available(self):
            return True

        def speak(self, text):
            if "treatment train" in text or "Coagulation" in text:
                raise audio_surface.EngineError(
                    self.name, "synthetic mid-run failure")
            return b"OK:" + text.encode("utf-8")

    audio_surface.TTSEngines["fake-failing"] = lambda: FailingEngine()
    try:
        tmp = tempfile.mkdtemp()
        try:
            bank = write_bank(tmp)
            out_dir = os.path.join(tmp, "pack")
            rc = audio_surface.cmd_export_audio(namespace(
                bank="audio", out=bank, objective="Water / chemistry",
                engine="fake-failing", out_dir=out_dir))
            if rc == 0:
                fail("failing engine run exited 0, expected non-zero")
            leftovers = [f for f in os.listdir(out_dir)
                         if f.endswith((".mp3", ".wav", ".tmp"))]
            if leftovers:
                fail("failing engine left partial audio: %r" % leftovers)
            txt = [f for f in os.listdir(out_dir) if f.endswith(".txt")]
            if len(txt) != 1:
                fail("failing engine run did not leave the transcript: %r"
                     % os.listdir(out_dir))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        audio_surface.TTSEngines.pop("fake-failing", None)


def test_digest_naming_and_atomic_audio_write():
    """The transcript file is named from the objective id and a content digest
    (sha256 short form); re-exporting an unchanged objective produces the same
    name, and the audio bytes land via temp-then-os.replace (D-12, AUDIO-06)."""
    class EchoEngine(TTSEngine):
        name = "fake-echo"
        container = "mp3"

        def available(self):
            return True

        def speak(self, text):
            return text.encode("utf-8")

    audio_surface.TTSEngines["fake-echo"] = lambda: EchoEngine()
    try:
        tmp = tempfile.mkdtemp()
        try:
            bank = write_bank(tmp)
            out1 = os.path.join(tmp, "pack1")
            out2 = os.path.join(tmp, "pack2")
            rc = audio_surface.cmd_export_audio(namespace(
                bank="audio", out=bank, objective="Public / notification",
                engine="fake-echo", out_dir=out1))
            if rc != 0:
                fail("echo engine export failed: %d" % rc)
            names1 = sorted(os.listdir(out1))
            rc2 = audio_surface.cmd_export_audio(namespace(
                bank="audio", out=bank, objective="Public / notification",
                engine="fake-echo", out_dir=out2))
            if rc2 != 0:
                fail("second echo engine export failed: %d" % rc2)
            names2 = sorted(os.listdir(out2))
            if names1 != names2:
                fail("unchanged objective re-export changed file names: %r vs %r"
                     % (names1, names2))
            if len(names1) != 2:
                fail("expected transcript + mp3, got %r" % names1)
            base = os.path.splitext(names1[0])[0]
            digest = hashlib.sha256(
                open(os.path.join(out1, base + ".txt"), encoding="utf-8")
                .read().encode("utf-8")).hexdigest()[:12]
            if base != "public-notification-%s" % digest:
                fail("file base is not <objective-slug>-<sha256-short>: %r"
                     % base)
            # The audio file content came through the engine and no .tmp is
            # left behind.
            audio_path = os.path.join(out1, base + ".mp3")
            if not os.path.exists(audio_path):
                fail("audio file was not written")
            if any(f.endswith(".tmp") for f in os.listdir(out1)):
                fail("a .tmp file was left behind after success")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        audio_surface.TTSEngines.pop("fake-echo", None)


def test_no_evidence_write():
    """After a successful export (and a failing-engine run), the evidence store
    is byte-identical -- listening records nothing (D-13, AUDIO-07)."""
    tmp = tempfile.mkdtemp()
    try:
        bank = write_bank(tmp)
        log = evidence.log_path(tmp)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        sentinel = b'{"event_type": "response"}\n'
        open(log, "wb").write(sentinel)
        out_dir = os.path.join(tmp, "pack")
        rc = audio_surface.cmd_export_audio(namespace(
            bank="audio", out=bank, objective="Water / chemistry",
            engine="transcript-only", out_dir=out_dir))
        if rc != 0:
            fail("transcript-only export failed: %d" % rc)
        after = open(log, "rb").read()
        if after != sentinel:
            fail("export mutated the evidence store")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_no_evidence_import_in_shipped_module():
    """The shipped audio modules never import or write evidence.py (D-13)."""
    for name in ("audio.py", "audio_edge_tts.py", "audio_piper.py"):
        path = os.path.join(ROOT, "surfaces", name)
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        if re.search(r"(?m)^\s*(import|from)\s+evidence\b", src):
            fail("surfaces/%s imports evidence.py" % name)


# ---- Plan 09.1-02: the two real engines ------------------------------------

# The fake edge_tts module: exposes the Communicate.stream() shape the pinned
# library uses (type/data chunks), so the edge-tts engine path is tested
# offline. Tests insert it into sys.modules under "edge_tts".
class _FakeCommunicate:
    def __init__(self, text, voice):
        self.text = text
        self.voice = voice

    async def stream(self):
        yield {"type": "audio", "data": b"ID3" + self.text.encode("utf-8")}


_FAKE_EDGE_MODULE = type("edge_tts", (), {"Communicate": _FakeCommunicate})()


def _install_fake_edge():
    import sys as _sys
    _sys.modules["edge_tts"] = _FAKE_EDGE_MODULE


def _remove_fake_edge():
    import sys as _sys
    _sys.modules.pop("edge_tts", None)


def test_edge_tts_registers_and_speaks_mp3_offline():
    """edge_tts() registers by name, declares container 'mp3', and speak(text)
    returns MP3 bytes from the pinned library (endpoint faked offline); the
    engine never transcribes, only speaks (D-02/D-09, AUDIO-02)."""
    from surfaces import audio_edge_tts
    _install_fake_edge()
    try:
        eng = audio_surface.resolve_engine("edge-tts")
        if eng.name != "edge-tts" or eng.container != "mp3":
            fail("edge-tts engine lost its name/container")
        eng.probe = lambda: True
        if not eng.available():
            fail("edge-tts with a fake lib + reachable probe must be available")
        out = eng.speak("hello")
        if not out.startswith(b"ID3"):
            fail("edge-tts speak() did not return MP3 bytes: %r" % out[:12])
        if b"hello" not in out:
            fail("edge-tts speak() did not stream the given text")
    finally:
        _remove_fake_edge()


def test_edge_tts_refuses_missing_or_unreachable_by_name():
    """When the pinned library is missing or the endpoint is unreachable,
    available() is False and speak() raises EngineError naming the engine and
    the reason -- the command refuses by name, never silently substituting
    (D-04, AUDIO-04)."""
    from surfaces import audio_edge_tts
    # Missing library: no fake installed.
    eng = audio_surface.resolve_engine("edge-tts")
    eng.probe = lambda: True
    if eng.available():
        fail("edge-tts without the pinned library reported available")
    try:
        eng.speak("anything")
        fail("edge-tts without the library did not refuse")
    except audio_surface.EngineError as exc:
        if "edge-tts" not in str(exc):
            fail("edge-tts refusal does not name the engine: %r" % str(exc))
    # Unreachable endpoint: library present, probe fails.
    _install_fake_edge()
    try:
        eng2 = audio_surface.resolve_engine("edge-tts")
        eng2.probe = lambda: False
        if eng2.available():
            fail("edge-tts with an unreachable endpoint reported available")
        try:
            eng2.speak("anything")
            fail("edge-tts with an unreachable endpoint did not refuse")
        except audio_surface.EngineError as exc:
            if "edge-tts" not in str(exc) or "unreachable" not in str(exc).lower():
                fail("edge-tts refusal does not name engine+reason: %r" % str(exc))
    finally:
        _remove_fake_edge()


def test_edge_tts_disclosure_in_cli_help():
    """The CLI help for --engine edge-tts contains the disclosure that item
    text is sent to Microsoft's endpoint (D-16); the disclosure is a tested
    string, not prose that can rot (AUDIO-07)."""
    r = run(["export", "--help"])
    if r.returncode != 0:
        fail("itembank export --help exited %d: %s"
             % (r.returncode, r.stderr))
    # argparse wraps help text across lines, so compare whitespace-collapsed.
    collapsed = re.sub(r"\s+", " ", r.stdout)
    disclosure = "edge-tts sends item text to Microsoft's endpoint"
    if disclosure not in collapsed:
        fail("export --help is missing the edge-tts network disclosure")


def test_edge_tts_and_lameenc_pinned_with_license_review():
    """requirements.txt pins edge-tts and lameenc with a recorded checksum and
    a named license review; the Piper artifact decision (bundled binary/model
    per research A3, never the GPL PyPI package) is recorded (Directive 4a,
    D-15, AUDIO-07)."""
    req = open(os.path.join(ROOT, "requirements.txt"), encoding="utf-8").read()
    if "edge-tts==7.2.8" not in req:
        fail("requirements.txt does not pin edge-tts==7.2.8")
    if "sha256:" not in req.split("edge-tts==7.2.8")[1][:400]:
        fail("requirements.txt edge-tts pin has no recorded checksum")
    if "LGPL" not in req:
        fail("requirements.txt has no named license review for edge-tts")
    if "lameenc==1.8.4" not in req:
        fail("requirements.txt does not pin lameenc==1.8.4")
    if "sha256:" not in req.split("lameenc==1.8.4")[1][:400]:
        fail("requirements.txt lameenc pin has no recorded checksum")
    if "Piper" not in req or "bundled" not in req.lower():
        fail("requirements.txt does not record the Piper bundled-artifact "
             "decision")


def test_piper_registers_and_speaks_wav_offline():
    """piper() registers by name, declares container 'wav', and speak(text)
    returns WAV bytes through a stubbed Piper invocation; a missing model or
    binary makes available() False and speak() raise EngineError naming the
    engine and the missing piece (D-02/D-04, AUDIO-02/AUDIO-04)."""
    from surfaces import audio_piper
    eng = audio_surface.resolve_engine("piper")
    if eng.name != "piper" or eng.container != "wav":
        fail("piper engine lost its name/container")

    def fake_run(argv, text):
        with open(argv[argv.index("--output_file") + 1], "wb") as fh:
            fh.write(b"RIFF" + text.encode("utf-8"))

    eng.runner = fake_run
    eng.model = "/nonexistent/voice.onnx"
    if eng.available():
        fail("piper with a missing model reported available")
    try:
        eng.speak("anything")
        fail("piper with a missing model did not refuse")
    except audio_surface.EngineError as exc:
        if "piper" not in str(exc) or "model" not in str(exc).lower():
            fail("piper refusal does not name engine+missing piece: %r" % str(exc))

    # With a model present, speak returns the WAV bytes the binary wrote.
    tmp = tempfile.mkdtemp()
    try:
        model = os.path.join(tmp, "voice.onnx")
        open(model, "wb").write(b"fake-model")
        eng.model = model
        if not eng.available():
            fail("piper with model present reported unavailable")
        eng.target_container = "wav"
        out = eng.speak("hello")
        if not out.startswith(b"RIFF") or b"hello" not in out:
            fail("piper speak() did not return the stubbed WAV bytes")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_piper_mp3_path_engine_scoped():
    """When the container setting is mp3, the piper engine's MP3 path converts
    the WAV through one pinned encoder (lameenc) and returns MP3 bytes; when
    the setting is wav, it passes WAV through untouched -- the encoder is
    engine-scoped (D-09, AUDIO-06)."""
    from surfaces import audio_piper

    class _FakeEncoder:
        def __init__(self):
            self.called = False

        def __call__(self, wav_bytes):
            self.called = True
            return b"MP3" + wav_bytes

    fake = _FakeEncoder()
    audio_piper._to_mp3 = fake
    tmp = tempfile.mkdtemp()
    try:
        model = os.path.join(tmp, "voice.onnx")
        open(model, "wb").write(b"fake-model")
        eng = audio_surface.resolve_engine("piper")
        eng.runner = lambda argv, text: open(
            argv[argv.index("--output_file") + 1], "wb").write(b"RIFFwav")
        eng.model = model
        eng.target_container = "mp3"
        mp3 = eng.speak("hello")
        if not mp3.startswith(b"MP3") or not fake.called:
            fail("piper mp3 path did not run the encoder: %r" % mp3[:8])
        eng.target_container = "wav"
        wav = eng.speak("hello")
        if not wav.startswith(b"RIFF") or fake.called is not True:
            fail("piper wav path must pass WAV through untouched")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_roster_exactly_three_engines_kokoro_documented():
    """The registry contains exactly edge-tts, piper, and transcript-only;
    Kokoro appears only in the documented registration-target note and
    resolves to a named refusal if selected (D-02, AUDIO-02)."""
    names = set(audio_surface.TTSEngines)
    if names != {"edge-tts", "piper", "transcript-only"}:
        fail("registry is not exactly {edge-tts, piper, transcript-only}: %r"
             % names)
    src = open(os.path.join(ROOT, "surfaces", "audio.py"), encoding="utf-8").read()
    if "Kokoro" not in src:
        fail("audio.py does not document Kokoro as a registration target")
    try:
        audio_surface.resolve_engine("kokoro")
        fail("kokoro resolved -- it must be a documented target, not built")
    except audio_surface.EngineError as exc:
        if "kokoro" not in str(exc):
            fail("kokoro refusal does not name the engine: %r" % str(exc))


def test_unavailable_configured_engine_no_silent_fallback():
    """With the configured engine unavailable, the command emits the
    transcript, names the engine and reason, and exits non-zero -- and never
    substitutes another engine's voice (D-04, AUDIO-04)."""
    class Unavailable(TTSEngine):
        name = "fake-unavailable"
        container = "mp3"

        def available(self):
            return False

        def speak(self, text):
            return b"SHOULD-NOT-RUN:" + text.encode("utf-8")

    audio_surface.TTSEngines["fake-unavailable"] = lambda: Unavailable()
    try:
        tmp = tempfile.mkdtemp()
        try:
            bank = write_bank(tmp)
            out_dir = os.path.join(tmp, "pack")
            settings = {"audio": {"engine": "fake-unavailable", "pause": {}}}
            # export_audio must refuse by name (D-04), never silently write
            # with an unavailable engine -- and the transcript must already be
            # on disk when it does.
            try:
                audio_surface.export_audio(bank, "Water / chemistry", out_dir,
                                           settings=settings)
                fail("unavailable engine did not refuse")
            except audio_surface.EngineError as exc:
                if "fake-unavailable" not in str(exc):
                    fail("unavailable-engine refusal does not name the engine: "
                         "%r" % str(exc))
            txt = [f for f in os.listdir(out_dir) if f.endswith(".txt")]
            if len(txt) != 1:
                fail("unavailable-engine refusal left no transcript")
            rc = audio_surface.cmd_export_audio(namespace(
                bank="audio", out=bank, objective="Water / chemistry",
                out_dir=out_dir))
            if rc == 0:
                fail("unavailable configured engine exited 0")
            txt2 = [f for f in os.listdir(out_dir) if f.endswith(".txt")]
            if len(txt2) != 1:
                fail("unavailable-engine run left no transcript")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        audio_surface.TTSEngines.pop("fake-unavailable", None)


def test_engine_switch_is_settings_change_only():
    """Switching engines is a settings change only: the same command text
    produces the same pack shape through a different registered engine, and
    the --engine flag overrides the settings entry without touching the schema
    (D-01, AUDIO-01)."""
    class EchoA(TTSEngine):
        name = "fake-settings-a"
        container = "mp3"

        def available(self):
            return True

        def speak(self, text):
            return b"A:" + text.encode("utf-8")

    class EchoB(TTSEngine):
        name = "fake-settings-b"
        container = "mp3"

        def available(self):
            return True

        def speak(self, text):
            return b"B:" + text.encode("utf-8")

    audio_surface.TTSEngines["fake-settings-a"] = lambda: EchoA()
    audio_surface.TTSEngines["fake-settings-b"] = lambda: EchoB()
    try:
        tmp = tempfile.mkdtemp()
        try:
            bank = write_bank(tmp)
            out_a = os.path.join(tmp, "pack_a")
            out_b = os.path.join(tmp, "pack_b")
            settings_a = {"audio": {"engine": "fake-settings-a", "pause": {}}}
            settings_b = {"audio": {"engine": "fake-settings-b", "pause": {}}}
            wa = audio_surface.export_audio(bank, "Water / chemistry", out_a,
                                            settings=settings_a)
            wb = audio_surface.export_audio(bank, "Water / chemistry", out_b,
                                            settings=settings_b)
            if not wa.get("audio") or not wb.get("audio"):
                fail("both settings engines must produce audio")
            if wa["audio"] == wb["audio"]:
                fail("two engines produced identical audio -- no real switch")
            ba = os.path.splitext(os.path.basename(wa["audio"]))[0]
            bb = os.path.splitext(os.path.basename(wb["audio"]))[0]
            if ba != bb:
                fail("same objective through different engines changed the "
                     "pack name: %r vs %r" % (ba, bb))
            # --engine flag overrides the settings entry without touching the
            # schema: same settings, explicit flag, different engine.
            wc = audio_surface.export_audio(bank, "Water / chemistry",
                                            os.path.join(tmp, "pack_c"),
                                            engine="fake-settings-b",
                                            settings=settings_a)
            if not wc.get("audio") or wc["audio"] == wa["audio"]:
                fail("--engine flag did not override the settings entry")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        audio_surface.TTSEngines.pop("fake-settings-a", None)
        audio_surface.TTSEngines.pop("fake-settings-b", None)


def main():
    test_registry_resolves_fake_engine_by_name()
    test_transcript_only_is_a_real_registered_engine()
    test_unknown_engine_refuses_by_name()
    test_resolve_objective_items_bank_order_and_obj_grammar()
    test_build_sequence_and_transcript_contract()
    test_settings_schema_audio_block()
    test_cli_transcript_only_and_legacy_byte_compat()
    test_failing_engine_leaves_no_partial_audio()
    test_digest_naming_and_atomic_audio_write()
    test_no_evidence_write()
    test_no_evidence_import_in_shipped_module()
    test_edge_tts_registers_and_speaks_mp3_offline()
    test_edge_tts_refuses_missing_or_unreachable_by_name()
    test_edge_tts_disclosure_in_cli_help()
    test_edge_tts_and_lameenc_pinned_with_license_review()
    test_piper_registers_and_speaks_wav_offline()
    test_piper_mp3_path_engine_scoped()
    test_roster_exactly_three_engines_kokoro_documented()
    test_unavailable_configured_engine_no_silent_fallback()
    test_engine_switch_is_settings_change_only()
    print("ok: audio export roundtrip -- registry, transcript-only, objective "
          "resolution, sequence/transcript contract, settings block, CLI + "
          "legacy byte-compat, atomic write, digest naming, no-evidence, "
          "edge-tts + piper engines, roster contract all held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
