# Phase 05 — Windows Process-Tree Kill Spike Result

**Attempted:** 2026-08-11, on the target machine — the Windows 11 host this milestone
targets (`sys.platform` target: `win32`).

## Verdict: PENDING — the six-step measurement could not be executed from this shell

This record is deliberately **not** a measurement. The shell available to the executor
is WSL2 (`Linux ... microsoft-standard-WSL2`, `python` = `/usr/bin/python`, Python
3.13.3, `sys.platform == "linux"`), and it **cannot spawn any Windows process**: every
PE binary attempted — `tasklist.exe`, `where.exe`, and the target interpreter
`C:\Users\wayba\AppData\Local\Programs\Python\Python313\python.exe` — fails at the
exec level with

```
run-detectors: unable to find an interpreter for /mnt/c/.../<binary>.exe
```

both when invoked directly from the shell and when spawned via `subprocess.run()` from
a Linux interpreter. The command classifier in this environment refuses the PE exec
before WSL interop (`/init`) can run; `binfmt_misc`'s `WSLInterop` registration exists
but is never reached. Plan 05-04's own precondition stops here: "The machine running
this task reports `win32` ... this verification is meaningless anywhere else" — and "If
it does not say `win32`, stop."

No escape rate is claimed, confirmed, or corrected. **0 of 50 runs were executed on
Windows**; the escape rate for the accepted spawn window is unmeasured and recorded as
PENDING rather than guessed at. The plan's own language is explicit that a zero
observation over a sample bounds the rate rather than proving it — and that applies
only when the observation exists. Here it does not.

## Environment

- Machine: Windows 11 host (this machine), Windows 11 Enterprise, per the host's
  release string 10.0.26220 recorded in 05-RESEARCH.md's dependency audit.
- Executor shell: WSL2 (`Linux ... microsoft-standard-WSL2`, kernel
  6.18.35.2-microsoft-standard-WSL2), `bash`.
- Executor python: `/usr/bin/python`, Python 3.13.3, `sys.platform = "linux"`.
- Target Windows interpreter present but unreachable from this shell:
  `C:\Users\wayba\AppData\Local\Programs\Python\Python313\python.exe` (Python 3.13).
- Date: 2026-08-11.

## The six steps, as executed

| Step | What was attempted | What happened |
|---|---|---|
| 1. platform + version | platform probe via the shell's interpreter | Reported `linux` / Python 3.13.3, not `win32` — plan says stop here; the Windows interpreter could not be invoked to re-probe |
| 2. `runner.new_job_object()` | `python -c "import runner; runner.new_job_object()"` on the Windows interpreter | Could not run — the Windows interpreter cannot be executed from this shell (`run-detectors: unable to find an interpreter`, exit status 2) |
| 3. `python tests/check_kill_roundtrip.py` | run once on this machine | Ran on the **Linux** interpreter: `check kill roundtrip: ok`, exit 0. The Windows-only assertions are platform-guarded and skipped on `linux` (by design, 05-VALIDATION.md); this proves the POSIX kill path, not the Windows one |
| 4. `tasklist /FI "IMAGENAME eq python.exe"` | post-run orphan check | Could not run — `tasklist.exe` itself fails at exec with the same `run-detectors` error; no Windows process table is reachable from this shell |
| 5. 50-iteration escape measurement | `for /L %i in (1,1,50) do @python tests/check_kill_roundtrip.py` | Could not run — requires the Windows interpreter. **0 of 50 runs executed; escape rate unmeasured (PENDING)** |
| 6. forced fallback (`runner._FORCE_TASKKILL_FALLBACK`) | set the switch, rerun the kill test | Could not run on Windows for the same reason. The switch exists in `runner.py` (`_FORCE_TASKKILL_FALLBACK = False`, line 112) and the fallback path is source-covered by the Windows-guarded test, but its behaviour on this machine is unmeasured |

## Which path ran by default, and what the other did

**Neither Windows path was exercised.** On this machine, the only kill path that ran
was the POSIX one: `check kill roundtrip: ok` above ran `kill_tree()`'s `killpg`
branch under the Linux interpreter. The Job Object close (the default Windows path in
`runner.py`'s `elif sys.platform == "win32" and not _FORCE_TASKKILL_FALLBACK` branch)
and the forced `taskkill /T /F` fallback both remain unmeasured here. This half of the
record is PENDING until the six steps run on a shell that can spawn Windows processes.

## The one tertiary-confidence constant

`runner.JobObjectExtendedLimitInformation` (Assumption A3, value 9) is **not
confirmed or corrected** by this record — step 2, which settles it against the real
API, could not run. It remains exactly where 05-RESEARCH.md left it: a commonly-cited
value with a loud failure mode if wrong (`SetInformationJobObject` returns false and
the guard raises `ctypes.WinError`). The Linux-side unit assertion
(`check_windows_constants_and_layouts`) pins the module constant to 9, but that is a
source assertion, not a WinAPI contact. **PENDING: run step 2 on a Windows-capable
shell.**

## The residual gap (standing property, from source)

The accepted spawn window stands as designed and is written into `runner.py` next to
the assignment call: a process created between the moment the child starts executing
and the moment `AssignProcessToJobObject` returns is outside the job and survives the
kill. It cannot be closed here: the public process-spawning API does not hand back the
child's thread handle — CPython's Windows `_execute_child` closes it before returning,
tracked upstream as bpo-1677688 — so the create-suspended-then-assign-then-resume
sequence is unreachable through `subprocess.Popen`. Dropping to the private
process-creation module (`_winapi.CreateProcess`) was considered and declined per
D-16/Assumption A4. This is a standing property of the design, recorded so it is not
rediscovered as a surprise; it is not an open defect. Its measured escape rate is the
PENDING number this record declines to invent.

## What would invalidate this record

This record is a blocker report, not a measurement, so the normal invalidation list
applies to the measurement it defers: the six steps must be run on a shell whose
interpreter reports `win32` (a Windows terminal, or a WSL session with working interop)
before the escape rate, the two paths' outcomes, and the enum constant can be recorded.
A Python version bump, a Windows build that changes nested-job defaults, or any change
to `runner.py`'s spawn site would each invalidate that future measurement the same way
they would have invalidated the one planned here.

## Supersession note for 05-RESEARCH.md

05-RESEARCH.md's Metadata section says its Windows section "should be superseded by the
spike-result artifact" once the spike "either confirms or corrects Assumption A3 and
A4". This record does **not** supersede it: no measurement exists to supersede it
with, and marking research superseded by a blocker report would be the same overclaim
the phase forbids. Supersession is deferred until the six steps actually run; the
research document remains the current authority for the Windows kill path until then.
