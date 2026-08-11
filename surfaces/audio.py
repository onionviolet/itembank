"""Audio drill pack export: one objective leaves the bank as an audio drill
pack -- stem, timed pause, key, why -- plus a plain-text transcript, behind one
TTSEngine interface with named registered implementations (D-01..D-16).

The shape copies the Phase 8 model-backend registry idiom rather than
inventing a second one: adding an engine is a new module plus a settings
entry, never a branch in a dispatcher. `transcript-only` is a real registered
engine (D-03), which is what makes "refuse cleanly, still emit the transcript"
fall out of the interface instead of being special-cased.

The one runtime call both surfaces reach is `export_audio()`: the CLI wraps it
in `cmd_export_audio`, and the daemon route (plan 09.1-03) will call the same
function -- neither surface is the real one (D-08).
"""
import hashlib
import os
import re
import sys

from model import load, parse_sources
from runtime import answer_text
from surfaces import settings as settings_surface


class EngineError(Exception):
    """A named refusal: the thing that failed (an engine name, an objective
    id) and the reason, in one message (D-04). `transcript_path` is set when
    the refusal happened after the transcript was already written (D-04's
    "still emit the transcript"), so the CLI can print where it landed."""

    def __init__(self, name, reason, transcript_path=None):
        super().__init__("%s: %s" % (name, reason))
        self.name = name
        self.reason = reason
        self.transcript_path = transcript_path


class TTSEngine:
    """One swappable TTS backend (D-01). Subclasses declare `name` and
    `container`, and implement `available()` and `speak(text) -> bytes`;
    `speak` raises EngineError(reason) when it cannot produce audio."""

    name = ""
    container = ""  # "mp3" | "wav" | "" for an engine that emits no audio

    def available(self):
        return True

    def speak(self, text):
        raise NotImplementedError


class TranscriptOnlyEngine(TTSEngine):
    """The always-available null engine (D-03): it emits the transcript and
    no audio. A real registered engine, not an error path."""

    name = "transcript-only"
    container = ""

    def available(self):
        return True

    def speak(self, text):
        return None


TTSEngines = {}  # engine name -> factory callable


def register(name, factory):
    TTSEngines[name] = factory


def _transcript_only_factory():
    return TranscriptOnlyEngine()


register("transcript-only", _transcript_only_factory)


def resolve_engine(name, settings=None):
    """Resolve an engine by exact registry name (D-01). An unknown name is a
    named refusal listing the engine name -- never a KeyError and never a
    silent default (D-04)."""
    if name is None:
        audio = (settings or {}).get("audio") or {}
        name = audio.get("engine") or "edge-tts"
    factory = TTSEngines.get(name)
    if factory is None:
        raise EngineError(name, "no engine registered under that name")
    return factory()


def resolve_objective_items(bank, objective_id):
    """The objective's items in bank order (CONTEXT integration points):
    objective ids come from Phase 3.2's [OBJ:] registry when the bank carries
    a resolvable ## SOURCES/[OBJ:] set, else from the item's [OBJECTIVE:] /
    Educational Objective line. An unknown objective id is a named refusal
    listing the id (D-04's spirit -- degrade, never block)."""
    qs = load(bank)
    ps = parse_sources(bank)
    known = (ps or {}).get("sources") or {}
    by_obj = {}
    for idx, q in enumerate(qs, 1):
        tag = "Q%d" % idx
        objectives = set()
        if q.get("objective"):
            objectives.add(q["objective"])
        if q.get("objective_line"):
            objectives.add(q["objective_line"])
        if ps:
            for d in ps.get("objs") or []:
                if d["item"] == tag and d["obj"] in known:
                    objectives.add(d["obj"])
        for o in sorted(objectives):
            by_obj.setdefault(o, []).append(q)
    if objective_id not in by_obj:
        raise EngineError(objective_id,
                          "no items found for objective %r in %s"
                          % (objective_id, bank))
    return by_obj[objective_id]


# Per-item-type pause starting values (D-07), recorded in the settings schema
# as the audio.pause map; tuned against real use, not invented precisely.
PAUSE_DEFAULTS = {"mc": 1.5, "multi": 2.0, "short": 2.0, "cloze": 2.5,
                  "build": 4.0, "table": 3.0, "dnd": 3.0, "check": 3.0}


def build_sequence(items, pause_map):
    """D-06/D-07: per item, stem -> timed pause -> key -> why. The pause
    duration is read from the per-item-type `pause_map` (settings), falling
    back to the recorded starting values. Returns a flat list of segment
    dicts: {"kind": "stem"|"pause"|"key"|"why", "text": str, "seconds": n}."""
    seq = []
    for q in items:
        pause = (pause_map or {}).get(q["type"],
                                      PAUSE_DEFAULTS.get(q["type"], 2.0))
        seq.append({"kind": "stem", "text": q["stem"], "seconds": None})
        seq.append({"kind": "pause", "text": "", "seconds": pause})
        seq.append({"kind": "key", "text": answer_text(q), "seconds": None})
        seq.append({"kind": "why",
                    "text": q.get("why") or q.get("disc") or "",
                    "seconds": None})
    return seq


def pack_transcript(sequence):
    """D-11: the plain-text transcript, exactly the sequence's spoken text in
    the same order the audio speaks -- one segment per block, pauses carry no
    text. This is the diffable check on what the engine was given."""
    spoken = [s["text"] for s in sequence if s["kind"] != "pause"]
    return "\n\n".join(spoken) + "\n"


def digest_name(objective_id, content):
    """D-12: the file base from the objective id (slugged) and a sha256
    short-form digest of the pack content, so re-exporting an unchanged
    objective is idempotent and a changed one never overwrites."""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9]+", "-", objective_id).strip("-").lower()
    return "%s-%s" % (slug or "objective", digest)


def write_pack(out_dir, objective_id, transcript, audio_bytes, container):
    """D-05/D-11/D-12: write the transcript always, then the audio
    temp-then-`os.replace` (the `runtime.write_session()` pattern). A failed
    write never leaves a partial audio file. Returns the written file paths."""
    os.makedirs(out_dir, exist_ok=True)
    base = digest_name(objective_id, transcript)
    transcript_path = os.path.join(out_dir, base + ".txt")
    with open(transcript_path, "w", encoding="utf-8") as fh:
        fh.write(transcript)
    audio_path = None
    if audio_bytes:
        audio_path = os.path.join(out_dir, base + "." + container)
        tmp = audio_path + ".tmp"
        try:
            with open(tmp, "wb") as fh:
                fh.write(audio_bytes)
            os.replace(tmp, audio_path)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    return {"transcript": transcript_path, "audio": audio_path, "base": base}


def export_audio(bank, objective_id, out_dir, engine=None, container=None,
                 settings=None):
    """The ONE runtime call both surfaces reach (D-08): resolve the objective,
    build the sequence, write the transcript always, then speak through the
    configured engine and write the audio temp-then-rename (D-05/D-11).

    Order is load-bearing (D-04/D-05): the transcript is written BEFORE the
    engine is called, so an engine that is missing, unreachable, or fails
    mid-run still leaves the transcript on disk and raises EngineError -- the
    caller turns that into a named refusal with a non-zero exit.

    Raises EngineError for an unknown objective, an unknown engine, an
    unavailable engine, or a mid-run engine failure. Writes nothing to the
    evidence store (D-13). Returns the written file paths plus the engine
    name.
    """
    if settings is None:
        settings = settings_surface.load_settings(".")
    audio = settings.get("audio") or {}
    container = container or audio.get("container") or "mp3"
    items = resolve_objective_items(bank, objective_id)
    seq = build_sequence(items, audio.get("pause"))
    transcript = pack_transcript(seq)
    # Transcript always writes -- before the engine attempt (D-04/D-11).
    written = write_pack(out_dir, objective_id, transcript, None, container)
    try:
        engine_obj = resolve_engine(engine, settings)
    except EngineError as exc:
        exc.transcript_path = written["transcript"]
        raise
    if not engine_obj.available():
        raise EngineError(engine_obj.name, "engine is not available",
                          transcript_path=written["transcript"])
    audio_bytes = None
    if engine_obj.container:
        # Speak every segment first, then write once: a mid-run engine failure
        # never creates a partial audio file (D-05).
        chunks = []
        try:
            for s in seq:
                if s["kind"] == "pause":
                    continue
                chunk = engine_obj.speak(s["text"])
                if chunk is not None:
                    chunks.append(chunk)
        except EngineError as exc:
            exc.transcript_path = written["transcript"]
            raise
        audio_bytes = b"".join(chunks)
    if audio_bytes:
        written = write_pack(out_dir, objective_id, transcript, audio_bytes,
                             container)
    written["engine"] = engine_obj.name
    return written


def cmd_export_audio(a):
    """The CLI surface (D-08): `itembank export audio <bank> --objective <id>`.
    Wraps `export_audio` -- the same runtime call the daemon route reaches --
    and turns every EngineError into a printed named refusal with a non-zero
    exit (D-04). Returns 0 on success, 1 on refusal.
    """
    bank = getattr(a, "out", None)
    objective_id = getattr(a, "objective", None)
    if not bank or not objective_id:
        sys.exit("usage: itembank export audio <bank> --objective <id> "
                 "[--out DIR] [--engine NAME] [--split per-pack|per-item] "
                 "[--container mp3|wav]")
    settings = settings_surface.load_settings(".")
    out_dir = getattr(a, "out_dir", None) or \
        os.path.dirname(os.path.abspath(bank))
    try:
        written = export_audio(bank, objective_id, out_dir,
                               engine=getattr(a, "engine", None),
                               container=getattr(a, "container", None),
                               settings=settings)
    except EngineError as exc:
        print("refusing to export audio: %s" % exc, file=sys.stderr)
        # The transcript was already written by export_audio (D-04); the
        # refusal names the engine and the reason and exits non-zero.
        if exc.transcript_path:
            print("transcript -> %s" % exc.transcript_path)
        return 1
    print("audio pack -> %s (engine %s)" % (written["base"],
                                            written["engine"]))
    print("transcript -> %s" % written["transcript"])
    if written["audio"]:
        print("audio -> %s" % written["audio"])
    return 0
