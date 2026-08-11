#!/usr/bin/env python3
"""Out-of-process execution of a learner's source for a check item.

This module lives beside model.py and runtime.py rather than inside either:
canonical_response and canonical_key are pure string reductions with three
consumers, one of which is a static offline page with no process to ask, so
spawning a subprocess anywhere inside them would break the property that makes
that page trustworthy. The runner therefore executes at the surface layer --
surfaces/quiz.py:record_answer and surfaces/session.py:do_action call it once
per submission -- and returns a per-case result list that the scorer reduces
without ever running code. It imports no surface and nothing from runtime.py.

What the bounds here do, and what they leave untouched:

- A per-case wall-clock deadline kills a run that never terminates and yields
  no verdict: a timed-out run is not a wrong answer, and the caller records
  error_category "timeout" with a None score (criterion 12).
- An output cap truncates unbounded stdout and keeps draining to EOF so the
  child is never left blocked on a full pipe.
- The interpreter is started with -I so this process's own PYTHONPATH, user
  site-packages and PYTHON* environment variables stay out of the learner's
  run. That is exactly what it is: an accident guard against configuration
  bleed, nothing wider.

That is all. The learner's code runs with the full rights of the user running
itembank and may reach the filesystem and the network; this module stops
accidents, and model.HONEST_LIMITS_NOTE states exactly that.
"""
import ast, ctypes, json, os, re, signal, subprocess, sys, tempfile, threading, time
from ctypes import wintypes

import model

# The one honest-limits sentence, reused from the model rather than
# paraphrased: SPEC and the browser copy both read this single source (D-10).
HONEST_LIMITS_NOTE = model.HONEST_LIMITS_NOTE

# Language -> argv template (D-02's config-not-code shape). The two
# substitution tokens stand for the interpreter and the source path, so a
# second language later is a settings entry rather than a code change. -I
# keeps this process's own PYTHONPATH, user site-packages and PYTHON*
# environment variables out of the learner's run -- an accident guard against
# configuration bleed, nothing wider.
LANGUAGES = {"python": ["{interpreter}", "-I", "{source}"]}

DEFAULT_TIMEOUT_SECONDS = 5
DEFAULT_MAX_OUTPUT_BYTES = 65536
# Bound on joining a drain thread after a kill. The pipes close on
# the kill so the threads reach EOF and exit in milliseconds; the
# timeout is a guard so a pathological stall cannot hang a case that
# a next case in the same submission depends on.

_DRAIN_JOIN_TIMEOUT = 5


# --- Windows Job Object with kill-on-close (plan 05-02 Task 2) --------------
# The three ctypes structures the job API needs, plus the two constants. The
# field order and widths are what 05-RESEARCH.md records from Microsoft Learn:
# DWORD for 32-bit fields and c_size_t (pointer-width) for the pointer ones, or
# SetInformationJobObject rejects the struct as the wrong size on 64-bit. The
# symbols are defined at module scope so the size checks and the structures are
# introspectable on Linux CI, but nothing here calls ctypes.WinDLL -- that only
# happens inside new_job_object/assign_to_job/kill_tree, so the module imports
# cleanly on POSIX. JobObjectExtendedLimitInformation is Assumption A3: widely
# cited as 9 but not re-verified against a primary enum table this session; it
# fails loudly (SetInformationJobObject returns false) if wrong, and plan 05-04
# confirms it on the target machine.
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9     # JOBOBJECTINFOCLASS enum value


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount",  ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount",   ctypes.c_ulonglong),
        ("WriteTransferCount",  ctypes.c_ulonglong),
        ("OtherTransferCount",  ctypes.c_ulonglong),
    ]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),   # LARGE_INTEGER
        ("PerJobUserTimeLimit",     ctypes.c_int64),
        ("LimitFlags",              wintypes.DWORD),
        ("MinimumWorkingSetSize",   ctypes.c_size_t),
        ("MaximumWorkingSetSize",   ctypes.c_size_t),
        ("ActiveProcessLimit",      wintypes.DWORD),
        ("Affinity",                ctypes.c_size_t),  # ULONG_PTR
        ("PriorityClass",           wintypes.DWORD),
        ("SchedulingClass",         wintypes.DWORD),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo",                IO_COUNTERS),
        ("ProcessMemoryLimit",    ctypes.c_size_t),
        ("JobMemoryLimit",        ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed",     ctypes.c_size_t),
    ]


# The two bounds tests share one kill trigger. The private switch and the two
# trace slots let the kill test (and plan 05-04's spike record) tell which
# Windows path actually ran, and force the taskkill fallback without a real
# job-object failure.
_FORCE_TASKKILL_FALLBACK = False
_last_kill_path = None      # which kill path ran last (group/job/fallback)
_last_job_error = None      # repr of the WinError that fell to the fallback



class UnknownLanguage(Exception):
    """A [LANG:] tag with no entry in the languages map. Never a fallback: a
    missing entry is a lint error at authoring time (item.check_lang_unknown)
    and an exception here."""


# The harness driver script, run in place of the learner's source for a
# [HARNESS:] item. It imports the source as a module, calls the named
# function with the authored arguments, and prints one typed line so the
# runner can compare the return value without executing anything itself.
HARNESS_DRIVER = """import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("submission", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
func = getattr(mod, sys.argv[2])
args = json.loads(sys.argv[3])
value = func(*args)
if isinstance(value, bool):
    print("bool:" + repr(value))
elif isinstance(value, int):
    print("int:" + repr(value))
elif isinstance(value, float):
    print("float:" + repr(value))
elif isinstance(value, str):
    print("str:" + json.dumps(value))
else:
    print("other:" + type(value).__name__)
"""


def run_cases(q, source, timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
              max_output_bytes=DEFAULT_MAX_OUTPUT_BYTES, languages=None):
    """Run source once per authored case, in order, inside one temporary
    directory, returning one result dict per case: case_index, passed,
    actual, timed_out and truncated.

    languages defaults to LANGUAGES; plan 05-03 passes settings-derived
    values in. A case that timed out carries timed_out True and passed False;
    the run-level killed_at_timeout fact is derived by scanning for any
    timed_out case -- that is the shape score_response() receives directly,
    so the timeout signal survives into the scorer without the scorer ever
    executing code.
    """
    languages = LANGUAGES if languages is None else languages
    lang = q.get("lang") or "python"
    template = languages.get(lang)
    if template is None:
        raise UnknownLanguage(
            "language %r is not configured; known languages: %s"
            % (lang, ", ".join(sorted(languages))))
    harness = q.get("harness") or ""
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, "submission.py")
        with open(src_path, "w", encoding="utf-8") as fh:
            fh.write(source)
        argv = [a.replace("{interpreter}", sys.executable)
                  .replace("{source}", src_path) for a in template]
        driver_path = None
        if harness:
            driver_path = os.path.join(td, "harness_driver.py")
            with open(driver_path, "w", encoding="utf-8") as fh:
                fh.write(HARNESS_DRIVER)
        results = []
        for i, case in enumerate(q.get("cases") or []):
            if harness:
                r = run_harness_case(argv, case, harness, q.get("tolerance"),
                                     timeout_seconds, max_output_bytes,
                                     driver_path)
            else:
                r = run_one_case(argv, case, q.get("match", "trimmed"),
                                 timeout_seconds, max_output_bytes)
            r["case_index"] = i
            results.append(r)
    return results


def run_one_case(argv, case, match_mode, timeout_seconds, max_output_bytes):
    """Spawn one fresh interpreter for one stdin/stdout case. Each case gets
    its own subprocess so a hang consumes only that case's budget and a crash
    cannot contaminate the one after it."""
    actual, timed_out, truncated = _spawn_and_drain(
        argv, case.get("stdin", ""), timeout_seconds, max_output_bytes)
    passed = False
    if not timed_out and not truncated:
        passed = case_passed(match_mode, case.get("expected", ""), actual)
    return {"passed": passed, "actual": actual,
            "timed_out": timed_out, "truncated": truncated}


def run_harness_case(argv, case, func_name, tolerance, timeout_seconds,
                     max_output_bytes, driver_path):
    """One [HARNESS:] case: import the learner's module, call the named
    function with the authored arguments, and compare the return value --
    exact for integers and strings, abs(actual - expected) <= tolerance for
    floats when [TOLERANCE:] is authored (criterion 8). A configured strategy
    inside the runner, never a second scorer."""
    args = _parse_call(case.get("call") or case.get("stdin", ""))
    call_argv = argv[:2] + [driver_path, argv[2], func_name,
                            json.dumps(args)]
    actual, timed_out, truncated = _spawn_and_drain(
        call_argv, "", timeout_seconds, max_output_bytes)
    passed = False
    if not timed_out and not truncated:
        passed = _harness_passed(case.get("expected", ""),
                                 _parse_emitted(actual), tolerance)
    return {"passed": passed, "actual": actual,
            "timed_out": timed_out, "truncated": truncated}


def case_passed(match_mode, expected, actual):
    """Interpret a [MATCH:] mode against one case's expected and actual
    output. exact is byte equality; trimmed (the default) compares with
    trailing newlines stripped from both sides -- the common failure is a
    missing or extra trailing newline, and failing a correct answer on that
    teaches nothing; regex is a full match over the whole actual output with
    dot-matching-newline. An unrecognized mode returns False (lint catches it
    before this is ever reached)."""
    if match_mode == "exact":
        return actual == expected
    if match_mode == "trimmed":
        return actual.rstrip(chr(10)) == expected.rstrip(chr(10))
    if match_mode == "regex":
        return re.fullmatch(expected, actual, re.S) is not None
    return False


def drain_pipe(pipe, cap_bytes, buf, truncated, stop_event):
    """Incrementally read one pipe: accumulate into buf up to cap_bytes,
    then set the truncated flag and the stop event but keep reading and
    discarding until EOF -- stopping the read early would leave the child
    blocked on a full OS pipe buffer and convert an output overrun into a
    hang."""
    total = 0
    overflow = False
    while True:
        chunk = pipe.read(4096)
        if not chunk:
            break
        if not overflow:
            buf.append(chunk)
            total += len(chunk)
            if total >= cap_bytes:
                overflow = True
                truncated.set()
                stop_event.set()


def kill_tree(proc, job_handle=None, proc_handle=None):
    """The single kill path both the deadline branch and the output-cap branch
    call -- never a second kill mechanism for the second trigger. POSIX:
    SIGKILL the child's process group (spawned with its own session) so
    grandchildren that did not detach die with it. Windows: closing a
    kill-on-close job handle terminates the whole job (no separate
    TerminateProcess call), falling back to taskkill /T /F /PID when no job was
    built. The direct child is reaped with wait() so it cannot linger as a
    zombie until the parent exits. Which path ran is recorded on _last_kill_path
    so the kill test and plan 05-04's spike record can tell them apart."""
    global _last_kill_path
    if os.name == "posix":
        _last_kill_path = "killpg"
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                proc.kill()
            except OSError:
                pass
    elif job_handle:
        _last_kill_path = "job"
        kernel32 = ctypes.WinDLL("kernel32")
        CloseHandle = kernel32.CloseHandle
        CloseHandle.argtypes = [wintypes.HANDLE]
        CloseHandle(job_handle)      # the kill: closes the job, kills the tree
        if proc_handle:
            CloseHandle(proc_handle) # release the extra process reference
    else:
        _last_kill_path = "taskkill"
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait()
    except OSError:
        pass


def new_job_object():
    """Create a Windows job object configured with
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, so closing the last handle to the job
    terminates every process in it. Windows only; raises on POSIX. Never
    returns a falsy handle -- a job that was not configured must not be
    mistaken for one that was."""
    if sys.platform != "win32":
        raise OSError("job objects are a Windows mechanism")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    CreateJobObjectW = kernel32.CreateJobObjectW
    CreateJobObjectW.restype = wintypes.HANDLE
    CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    hjob = CreateJobObjectW(None, None)
    if not hjob:
        raise ctypes.WinError(ctypes.get_last_error())
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    SetInformationJobObject = kernel32.SetInformationJobObject
    SetInformationJobObject.restype = wintypes.BOOL
    SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                        ctypes.c_void_p, wintypes.DWORD]
    ok = SetInformationJobObject(hjob, JobObjectExtendedLimitInformation,
                                 ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return hjob


def assign_to_job(handle, pid):
    """Assign a freshly spawned process (by the pid Popen exposes) into a job
    object, so it inherits the job's kill-on-close membership. Windows only.
    Returns the process handle opened for the assignment; the caller (kill_tree)
    closes it. Raises ctypes.WinError on failure."""
    if sys.platform != "win32":
        raise OSError("job objects are a Windows mechanism")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    PROCESS_ALL_ACCESS = 0x1F0FFF
    OpenProcess = kernel32.OpenProcess
    OpenProcess.restype = wintypes.HANDLE
    OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    hproc = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not hproc:
        raise ctypes.WinError(ctypes.get_last_error())
    AssignProcessToJobObject = kernel32.AssignProcessToJobObject
    AssignProcessToJobObject.restype = wintypes.BOOL
    AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    ok = AssignProcessToJobObject(handle, hproc)
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return hproc


def _spawn_and_drain(argv, stdin_text, timeout_seconds, max_output_bytes):
    """One subprocess: stdin written then closed immediately -- so a program
    reading to EOF finishes its own read instead of sitting out the deadline
    -- stdout and stderr drained on two threads (never sequentially, which is
    the pipe-buffer deadlock), and killed by deadline or output cap through
    the one kill_tree path. Returns (stdout, timed_out, truncated)."""
    global _last_job_error
    kwargs = {}
    job_handle = None
    proc_handle = None
    if os.name == "posix":
        kwargs["start_new_session"] = True   # the child leads its own group
    elif sys.platform == "win32" and not _FORCE_TASKKILL_FALLBACK:
        # Create the kill-on-close job before spawning so there is no gap in
        # which the child could run outside any job.
        try:
            job_handle = new_job_object()
        except OSError as exc:
            _last_job_error = repr(exc)
            job_handle = None
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            **kwargs)
    if job_handle is not None:
        # Assign the child to the job as the very next statement after Popen
        # returns, with no I/O, no logging and no other call in between.
        # subprocess.Popen cannot spawn suspended and resume afterwards --
        # CPython's Windows child-creation closes the child's thread handle
        # before returning, tracked upstream as bpo-1677688 -- so the
        # textbook race-free create-then-assign-then-resume sequence is not
        # reachable through the public API. D-16 accepts the resulting window
        # rather than dropping to the private process-creation module: a
        # grandchild created inside it escapes the job. Plan 05-04 measures
        # that window over 50 iterations rather than claiming it is zero.
        try:
            proc_handle = assign_to_job(job_handle, proc.pid)
        except OSError as exc:
            _last_job_error = repr(exc)
            job_handle = None
            proc_handle = None
    stop = threading.Event()
    out_buf, out_trunc = [], threading.Event()
    err_buf, err_trunc = [], threading.Event()
    t_out = threading.Thread(target=drain_pipe,
                             args=(proc.stdout, max_output_bytes, out_buf,
                                   out_trunc, stop), daemon=True)
    t_err = threading.Thread(target=drain_pipe,
                             args=(proc.stderr, max_output_bytes, err_buf,
                                   err_trunc, stop), daemon=True)
    t_out.start(); t_err.start()
    if stdin_text:
        try:
            proc.stdin.write(stdin_text.encode("utf-8"))
        except (BrokenPipeError, OSError):
            pass
    try:
        proc.stdin.close()
    except OSError:
        pass
    timed_out = False
    deadline = time.monotonic() + timeout_seconds
    while True:
        if stop.is_set():
            kill_tree(proc, job_handle, proc_handle)
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            kill_tree(proc, job_handle, proc_handle)
            break
        try:
            proc.wait(timeout=min(0.05, remaining))
            break
        except subprocess.TimeoutExpired:
            continue
    t_out.join(timeout=_DRAIN_JOIN_TIMEOUT)
    t_err.join(timeout=_DRAIN_JOIN_TIMEOUT)
    actual = b"".join(out_buf).decode("utf-8", "replace")
    truncated = out_trunc.is_set() or err_trunc.is_set()
    return actual, timed_out, truncated


def _parse_call(text):
    """Parse a harness CASE) lhs such as add(1, 2) into a tuple of literal
    arguments. ast.literal_eval is used because the arguments are authored
    literal values; the function name itself comes from [HARNESS:], never from
    the call text."""
    m = re.match(r"^\s*\w+\s*\((.*)\)\s*$", text, re.S)
    if m is None:
        raise ValueError("cannot parse harness call %r" % text)
    inner = m.group(1).strip()
    if not inner:
        return ()
    return ast.literal_eval("(" + inner + ",)")


def _parse_emitted(stdout):
    """The driver's last non-empty stdout line (int:5, float:0.3, str:"hi",
    bool:True) parsed into a (kind, value) pair, or None when absent."""
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    if not lines:
        return None
    line = lines[-1]
    if line.startswith("int:"):
        return ("int", int(line[4:]))
    if line.startswith("float:"):
        return ("float", float(line[6:]))
    if line.startswith("bool:"):
        return ("bool", line[5:] == "True")
    if line.startswith("str:"):
        return ("str", json.loads(line[4:]))
    return None


def _harness_passed(expected, emitted, tolerance):
    if emitted is None:
        return False
    kind, value = emitted
    if kind == "int":
        try:
            return int(expected) == value
        except (TypeError, ValueError):
            return False
    if kind == "float":
        try:
            want = float(expected)
        except (TypeError, ValueError):
            return False
        if tolerance is None:
            return False
        return abs(value - want) <= tolerance
    return str(expected) == str(value)
