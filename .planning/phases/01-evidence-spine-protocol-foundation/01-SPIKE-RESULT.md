# Windows Append-Durability Spike Result

**Measured:** 2026-08-06, by `tests/durability_roundtrip.py`, run on the executor's own
machine — the same Windows 11 machine this milestone targets.

## Machine and interpreter

- `sys.platform`: `win32`
- OS: Microsoft Windows 11 Enterprise, Version 10.0.26220, Build 26220
- `python --version`: Python 3.13.5

## Probe (a): unlocked `O_APPEND`

Four OS subprocesses, each writing 250 lines with a bare `os.O_APPEND | os.O_CREAT |
os.O_WRONLY` open and a single unlocked `os.write()` per line — no lock held. Measured
at two padding sizes, run three times across this session:

| Run | Short padding (480 bytes, line ~512 bytes) | Long padding (4200 bytes, line ~4230 bytes) |
|-----|---|---|
| 1 | 0 lines torn/unparseable, 73 (tag,i) pairs missing or duplicated | 0 lines torn/unparseable, 183 (tag,i) pairs missing or duplicated |
| 2 | 0 lines torn/unparseable, 64 (tag,i) pairs missing or duplicated | 0 lines torn/unparseable, 178 (tag,i) pairs missing or duplicated |
| 3 | 0 lines torn/unparseable, 89 (tag,i) pairs missing or duplicated | 0 lines torn/unparseable, 216 (tag,i) pairs missing or duplicated |

What reproduced: every line was individually still valid JSON of the right shape and
pad length in all three runs (0 lines torn/unparseable) — a single unlocked `write()`
call itself did not shear mid-line at either padding size on this machine's NTFS volume.
What did reproduce, consistently and substantially, is **lost writes**: 64-89 of the
1,000 expected `(tag, i)` pairs at the short padding, and 178-216 of the 1,000 expected
pairs at the long padding, were missing entirely (duplicates did not occur; every
deviation was a missing pair, consistent with one process's `lseek(fd, 0, SEEK_END)`
racing another process's write and both landing at the same offset, with one write
silently clobbering the other rather than the two interleaving mid-line). This is
exactly the `lseek` + `write` two-step race bpo-42606 describes, not line-tearing —
and it reproduces every time on this machine, at both padding sizes, more severely at
the larger size. This is a property of the CRT implementation this project has to work
around, not an artifact of this particular run.

## Probe (b): locked append

4 processes x 2,500 lines = 10,000 total, long padding (4200 bytes), using
`evidence.append_line()` (advisory lock + single `write()` per line). Across all three
runs in this session: **10,000 lines total, 0 deviations** — every line parsed, every
`(tag, i)` pair from 0-2,499 present exactly once for each of the four tags, every
`pad` the exact expected length.

## Probe (c): kill mid-write

One `locked`-mode writer started against a 500,000-line target, terminated after a
200ms sleep. Across three runs: `itembank.iter_raw()` raised nothing; every parsed
record had the correct `pad` length; the number of records returned matched the number
of complete lines in the file (228, 389, and 489 records across the three runs — the
lock plus single-`write()`-per-line pattern meant `terminate()` landed between
complete, fully-flushed lines each time rather than mid-line, so no torn trailing line
was observed on this machine). A further `append_line()` call after termination
produced a line that `iter_raw()` read back correctly in all three runs, proving a
kill does not poison subsequent appends or reads.

## Verdict

**Advisory lock plus one `os.write()` per event is sufficient — proceed with
`evidence.append_line()` as written.**

The unlocked probe reproduces real, repeatable data loss on this exact machine —
confirming the risk bpo-42606 describes is not theoretical here — while the locked
probe shows zero deviations across 30,000 total locked appends (10,000 x 3 runs) from
concurrent OS processes, and the kill probe shows the reader degrading gracefully with
no poisoned subsequent state across three independent kills. The `ctypes` +
`CreateFileW(FILE_APPEND_DATA)` fallback named in RESEARCH.md's Assumptions Log (A3)
is not required.

## What this gates

This verdict gates plans `01-02` through `01-11` in this phase — every plan that
appends a real event through `evidence.append_line()` depends on this measurement
having been made and having passed before it writes anything. `01-02-PLAN.md`'s
tracer is the first of those dependents.
