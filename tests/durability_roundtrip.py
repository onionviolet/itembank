#!/usr/bin/env python3
"""The Windows append-durability spike RESEARCH.md Open Question 1 calls for.

This executor's own machine is the target Windows 11 machine the spike measures
against; CI runs this same file on `ubuntu-latest`, covering the POSIX path where
`O_APPEND` is genuinely atomic. Runnable as `python tests/durability_roundtrip.py`.
"""
import contextlib, io, json, os, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

TAGS = ("0", "1", "2", "3")
PAD_SHORT = 480             # near 512 bytes once wrapped in the JSON envelope
PAD_LONG = 4200              # above the 4096-byte NTFS sector size


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def raw_append(path, line):
    """The bare, unlocked O_APPEND write this spike measures against."""
    payload = line.encode("utf-8") + b"\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)


def run_writer(mode, path, tag, count, padding):
    for i in range(count):
        line = json.dumps({"tag": tag, "i": i, "pad": "x" * padding}, ensure_ascii=False)
        if mode == "locked":
            itembank.append_line(path, line)
        elif mode == "raw":
            raw_append(path, line)
        else:
            sys.exit("unknown writer mode %r" % mode)
    return 0


def spawn_writers(mode, path, count, padding, tags=TAGS):
    procs = [subprocess.Popen([sys.executable, __file__, "--writer", mode, path,
                               tag, str(count), str(padding)]) for tag in tags]
    for p in procs:
        p.wait()
    return procs


def analyze_log(path, expected_count, expected_padding, tags):
    """Torn/unparseable line count and (tag, i) pairs missing or duplicated."""
    seen = {}
    torn = 0
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except ValueError:
                    torn += 1
                    continue
                if not isinstance(obj, dict) or "tag" not in obj or "i" not in obj \
                        or len(obj.get("pad", "")) != expected_padding:
                    torn += 1
                    continue
                key = (obj["tag"], obj["i"])
                seen[key] = seen.get(key, 0) + 1
    deviated = sum(1 for tag in tags for i in range(expected_count)
                   if seen.get((tag, i), 0) != 1)
    return torn, deviated


def probe_torn_multibyte():
    """(0) A torn multi-byte tail — DETERMINISTIC, ASSERTED, runs first. D-09
    promises a malformed line is skipped and reported, never fatal, but the
    other probes here pad with pure ASCII, and ASCII cannot be torn
    mid-character — exactly why a green suite gated a broken guarantee. This
    probe builds the tear by hand instead of waiting for `probe_kill` to get
    timing-lucky, so a regression surfaces immediately and every run,
    not only on the runs where a kill happened to land mid-character."""
    d = tempfile.mkdtemp()
    try:
        path = os.path.join(d, "torn.jsonl")
        first = json.dumps({"probe": "torn_multibyte", "marker": "kept"},
                            ensure_ascii=False).encode("utf-8") + b"\n"
        full = json.dumps({"tag": "cjk", "text": "けさ文"}, ensure_ascii=False).encode("utf-8")
        cut = full.index("文".encode("utf-8")) + 2
        tail = full[:cut]
        with open(path, "wb") as fh:
            fh.write(first)
            fh.write(tail)

        buf = io.StringIO()
        records = None
        exc_caught = None
        with contextlib.redirect_stdout(buf):
            try:
                records = list(itembank.iter_raw(path))
            except UnicodeDecodeError as exc:
                exc_caught = exc
        output = buf.getvalue()

        if exc_caught is not None:
            fail("probe_torn_multibyte: iter_raw raised UnicodeDecodeError on a torn "
                 "multi-byte tail (%s); D-09 requires a malformed line to be skipped "
                 "and reported, never fatal" % exc_caught)
        if len(records) != 1:
            fail("probe_torn_multibyte: expected exactly 1 record before the tear, got %d"
                 % len(records))
        if records[0][1].get("marker") != "kept":
            fail("probe_torn_multibyte: the surviving record was not the first line's "
                 "marker record (got %r)" % (records[0][1],))
        expect = "%s:2 malformed, skipped" % os.path.basename(path)
        if expect not in output:
            fail("probe_torn_multibyte: expected stdout to report %r, got %r"
                 % (expect, output))
        print("torn multi-byte probe: ok (1 record survived a mid-character tear, "
              "the torn line was reported)")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def probe_unlocked():
    """(a) Unlocked O_APPEND — MEASURED, NOT ASSERTED. A clean run is a valid
    measurement of this machine's timing, not a refutation of bpo-42606."""
    count = 250
    results = {}
    for label, padding in (("short", PAD_SHORT), ("long", PAD_LONG)):
        d = tempfile.mkdtemp()
        try:
            path = os.path.join(d, "raw.jsonl")
            spawn_writers("raw", path, count, padding)
            torn, deviated = analyze_log(path, count, padding, TAGS)
            results[label] = (torn, deviated)
            print("unlocked probe (%s padding, %d bytes): %d lines torn/unparseable, "
                  "%d (tag,i) pairs missing or duplicated" % (label, padding, torn, deviated))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return results


def probe_locked():
    """(b) Locked append — ASSERTED. 4 processes x 2,500 lines = 10,000 total."""
    count = 2500
    d = tempfile.mkdtemp()
    try:
        path = os.path.join(d, "locked.jsonl")
        spawn_writers("locked", path, count, PAD_LONG)
        torn, deviated = analyze_log(path, count, PAD_LONG, TAGS)
        if torn:
            fail("locked probe: %d lines failed to parse or had the wrong pad length" % torn)
        if deviated:
            fail("locked probe: %d (tag,i) pairs missing or duplicated" % deviated)
        total = count * len(TAGS)
        print("locked probe: %d lines, all parsed, all (tag,i) pairs present exactly once" % total)
        return total
    finally:
        shutil.rmtree(d, ignore_errors=True)


def probe_kill():
    """(c) Kill mid-write — ASSERTED. The reader must survive a torn tail, and a
    further append after the torn tail must still be readable."""
    d = tempfile.mkdtemp()
    try:
        path = os.path.join(d, "kill.jsonl")
        padding = 100
        proc = subprocess.Popen([sys.executable, __file__, "--writer", "locked", path,
                                 "0", "500000", str(padding)])
        time.sleep(0.2)
        proc.terminate()
        proc.wait()

        records = list(itembank.iter_raw(path))     # must not raise (D-09)
        for lineno, obj, raw in records:
            if len(obj.get("pad", "")) != padding:
                fail("kill probe: record at line %d has the wrong pad length" % lineno)
        with open(path, "rb") as fh:
            complete_lines = fh.read().count(b"\n")
        if len(records) < complete_lines - 1:
            fail("kill probe: reader returned %d records but the file had %d complete lines"
                 % (len(records), complete_lines))

        itembank.append_line(path, json.dumps({"tag": "post-kill", "i": 0, "pad": "y" * 16}))
        if not any(o.get("tag") == "post-kill" for _, o, _ in itembank.iter_raw(path)):
            fail("kill probe: an append after the torn tail was not readable")

        print("kill probe: reader survived, %d records read, %d complete lines in file, "
              "post-kill append readable" % (len(records), complete_lines))
        return len(records)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def check_gitignore_hygiene():
    """The automated half of the data-residency prohibition: learner evidence can
    never be committed."""
    path = os.path.join(ROOT, ".gitignore")
    lines = [l.strip() for l in open(path, encoding="utf-8")]
    if "_evidence/" not in lines:
        fail("`.gitignore` has no literal `_evidence/` entry")


def main():
    probe_torn_multibyte()
    check_gitignore_hygiene()
    probe_unlocked()
    total = probe_locked()
    probe_kill()
    print("append durability: ok (%s, %d locked lines, %d torn under lock)"
          % (sys.platform, total, 0))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--writer":
        _, mode, path, tag, count, padding = sys.argv[1:]
        sys.exit(run_writer(mode, path, tag, int(count), int(padding)))
    else:
        sys.exit(main())
