# Execution and specialty-answer audit

Status: source audit with focused synthetic verification, 2026-09-25. This packet changes only this report. It does not change the runner, question format, installed app, or accepted course artifacts.

## Result

Itembank already grades submitted programs through production `check` items. Python is the default executable language. CodeMirror is an input surface, and the CS Dojo JavaScript/Pyodide workers are a separate prototype. LaTeX input is present but still receives pending short-answer treatment. Native math equivalence and a general numeric-answer field are absent from the current response/scoring contract.

Two verified defects should precede expansion: an unfinished exam leaks check verdicts and hidden cases inside a nested response, and a program can print the expected result, crash, and still pass.

## Current capability map

| Capability | Verified state | Boundary and evidence |
|---|---|---|
| Run learner programs against cases | Present in production source | `[TYPE: check]`, `[LANG:]`, `CASE) stdin :: expected`, optional starter and match mode are parsed in `model.py:152-179`. `surfaces/session.py:610-634` runs cases and calls the shared scorer. |
| Output comparison | Present | Exact text, trailing-newline trimming, and full regular-expression match exist in `runner.py:280-294`. `trimmed` removes trailing newlines only, not arbitrary spaces. |
| Function-return checking | Present but narrow | `[HARNESS: function]` imports a Python module and supplies authored literal arguments. Integers and strings compare directly. Floats require absolute `[TOLERANCE:]`. The driver and comparison are at `runner.py:124-145`, `260-277`, `510-559`. Arbitrary object/list/dict equality is not implemented by this driver. |
| Default and additional languages | Python present, additional interpreters configurable | `runner.py:38-47` defaults to Python with `-I`. `schemas/settings.schema.json:1080-1140` declares the language argv allowlist, limits, and default LAN refusal. A configurable language is not a shipped language-specific harness. The function harness constructs a Python driver and assumes the Python argv shape at `runner.py:268-269`. |
| Runtime-owned verdict and evidence | Present, with disclosure defect below | `runtime.py:202-326` reduces a pass vector to an all-cases-pass verdict. Any timed-out case makes the answer pending. Source is retained verbatim as `check_source`, while the vector remains the scored answer at `surfaces/session.py:1047-1109` and `schemas/response.schema.json:390-402`. |
| Editor and offline fallback | Present | CodeMirror submits source text at `surfaces/quiz_page.py:2336-2419`. The no-script form uses a textarea at `1068-1079`. A directly opened offline quiz declines execution at `2341-2364`. An editor alone does not provide grading. |
| Runnable lesson examples | Present, ungraded | `/api/lesson/run` validates the session and authored fence, then calls `runner.run_source`, returning stdout, stderr, exit code and limit observations. It does not settle an item or create a score. See `surfaces/daemon.py:5935-5950`, `5990-6020` and `runner.py:148-180`. |
| CS Dojo JavaScript and Python execution | Prototype | JavaScript and local Pyodide use replaceable browser workers with time/output bounds. Local drafts and export exist. Reports are untrusted observations with no accepted assessment evidence. See `prototypes/cs-dojo/README.md:25-67`, `dojo.js:278-336`, `runner.js`, and `python-runner.js`. |
| Multi-file code workspace | Prototype only in inspected route | Dojo has a declared CommonJS-style two-file example. It does not implement Node.js, package installation, a filesystem or native ES modules. See `prototypes/cs-dojo/README.md:47-50`. Production `check` writes one submission source file per run at `runner.py:171-178`. |
| LaTeX entry and preview | Present | `[INPUT: latex]` is limited to `short`. The UI retains text and uses local KaTeX with a source fallback. The preview does not grade. See `model.py:3696-3701`, `surfaces/quiz_page.py:452-487`, and `tests/latex_input_roundtrip.py:35-45`. |
| Exact numeric spatial answers | Present within `visual` | Plot/number-line/interval/timeline/trace answers use a bounded rational scalar contract and declared tolerances. Decimal `2.50` normalizes exactly to `5/2`. Units, exponents, mixed numbers and symbolic expressions are invalid. See `runtime.py:409-439`, `973-1042`. This is not a general numeric-entry item. |
| General numeric entry, unit-aware quantities, symbolic equality, proofs | Gap in current contract | The closed forms are `mc`, `multi`, `table`, `dnd`, `build`, `short`, `check`, `visual` at `model.py:2678-2679`. There is no numeric/unit/symbolic normalizer in `runtime.py:227-260`. Short mathematical answers remain pending at `306-326`. A programmer can author code that computes a value, but that does not create a native numeric or algebraic response contract. |

Draft scope is uneven. The served baseline autosaves text fields in browser storage, but restores only into an empty field at `surfaces/quiz_page.py:4100-4136`. A check item with a nonempty authored starter begins with that starter at `1072-1079`, so this restore condition can skip its saved edit. This is a source-level finding, not a new rendered-browser result. Dojo separately restores bounded code, prediction and reflection at `prototypes/cs-dojo/dojo.js:5-24` and `110-123`.

## Verified defects and authority boundaries

### E1. Exam check responses disclose hidden cases before completion

Priority: P1. A synthetic six-item exam remained active after its first submission. The HTTP result correctly said `action: defer_feedback` and omitted top-level `score`, yet included `interaction_result.verdict`, every case's expected output and input, and pass flags. This defeats the silent assessment contract even if the visible page hides those fields.

`surfaces/session.py:1111-1116` constructs the check result without a feedback-mode gate, and `1151-1163` returns it plus raw run results. `runtime.py:132-156` includes authored `expected` and `input` values in each observation. The API removes only top-level score, explanation and selection feedback for exam/diagnostic at `surfaces/daemon.py:5875-5883`. The nested payload survives.

Reproduction used a temporary copy of `fixtures/check_bank.md`, the repository's temporary-server helper, `POST /api/start` with `mode: exam`, `count: 6`, `focus: q1`, then `POST /api/submit` with the fixture's correct sum program. No real bank or evidence was used. The server was stopped and the temporary directory removed.

Exact Python probe, run from the repository root:

```python
import importlib.util, json, os, shutil, tempfile
spec = importlib.util.spec_from_file_location("audit_helper", "tests/check_roundtrip.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
with tempfile.TemporaryDirectory(prefix="itembank-audit-check-") as work:
    bank = os.path.join(work, "check_bank.md")
    shutil.copyfile(helper.CHECK_BANK, bank)
    process, base = helper._serve_base(bank, os.path.join(work, "attempt.md"), [])
    try:
        assert base, "temporary test server failed to start"
        started = helper.post(base + "api/start", {
            "bank": "check_bank", "count": 6, "mode": "exam", "focus": "q1"})
        result = helper.post(base + "api/submit", {
            "session_id": started["session_id"], "answer": helper.SUM_SOURCE})
        print(json.dumps(result, sort_keys=True))
    finally:
        process.terminate()
        process.wait(timeout=10)
```

Observed response excerpt:

```json
{
  "action": "defer_feedback",
  "status": "active",
  "next_status": "active",
  "top_level_score_present": false,
  "interaction_verdict": true,
  "first_observation": {
    "input": "5 7",
    "expected": "12",
    "actual": "12\n",
    "passed": true,
    "reason": "passed"
  }
}
```

Required correction is a recursive, mode-aware disclosure contract shared by API, CLI and other adapters. The test must inspect the complete serialized response while the exam is still active, not just top-level fields or rendered text. This report does not implement that correction.

### E2. Matching output can pass after a runtime error

Priority: P2. `run_source` correctly captures the nonzero exit and stderr, but `run_cases` checks only timeout/truncation before matching stdout at `runner.py:232-243`. `run_harness_case` also discards exit status at `270-275`.

This harmless synthetic probe ran through the repository runner with a one-second deadline and 1 KB output cap:

```python
import runner
import runtime

q = {"type": "check", "lang": "python", "match": "trimmed",
     "cases": [{"stdin": "", "expected": "42"}]}
source = 'print(42)\nraise RuntimeError("synthetic audit probe")\n'
observation = runner.run_source("python", source,
                                timeout_seconds=1, max_output_bytes=1024)
results = runner.run_cases(q, source,
                          timeout_seconds=1, max_output_bytes=1024)
print(observation)
print(results, runtime.score_response(q, results))
```

Observed: `stdout` was `42\n`, `exit_code` was `1`, stderr contained the RuntimeError, timeout and truncation were false, the case had `passed: true`, and `score_response` returned `True`. A pure mock-observation probe confirmed the same comparison behavior without spawning candidate code.

The execution result contract needs to retain runtime errors and exit status through the case result. A regression test should assert that matching stdout followed by failure cannot silently settle as correct. Timeout should retain the current null/pending policy unless that policy is deliberately revised. This report proposes no timeout-policy change.

### E3. Clients do not directly supply trusted pass vectors

The public response contract accepts source text, not a caller-provided verdict. `surfaces/session.py:1029-1039` requires a string, executes it server-side, and replaces the action answer with the generated case results. `surfaces/quiz.py:439-460` uses the same execution gate. `/api/submit` rejects authority-shaped fields and delegates to `do_action` at `surfaces/daemon.py:5799-5851`.

`score_response` accepts vectors internally by design. Calling that pure function with a handcrafted vector is not evidence of a public submit bypass. This audit found the nested disclosure defect above, not a client-pass-vector acceptance route.

### E4. Native execution has accident limits, not an isolation boundary

This limitation is explicit and verified in source. Native submitted programs run with the user's filesystem and network permissions at `runner.py:13-27`. Python `-I` prevents Python environment configuration bleed. It does not isolate files, secrets, network access, or memory.

Defaults are five seconds per case and 65,536 bytes per stdout/stderr drain at `runner.py:44-47` and `423-502`. POSIX execution creates a process group and the kill path uses group termination at `318-335`. The spawn has no `cwd` or scrubbed `env` argument at `443-445`. Source lives in a temporary directory, but the process working directory is inherited. These observations do not assert a sandbox escape or test malicious code.

The HTTP boundary separately refuses LAN-triggered execution unless enabled and refuses unconfigured languages at `surfaces/daemon.py:3420-3433`. The browser Dojo has a different prototype boundary using worker CSP, documented at `prototypes/cs-dojo/server.py:30-42`. Neither existing route establishes a production hostile-code sandbox or hard memory quota.

## Next execution contract, scoped to the existing authority

1. X1. Extend the existing `check` result and disclosure path before adding another interpreter. Preserve source, item/case revisions, language/runtime version, exit status and error category. Settle the verdict only through the existing runtime, and keep timeout, unavailable and incorrect distinct.
2. X2. Make execution capabilities explicit per adapter: language/version, dependencies, file inputs, network policy, time/memory/process/output limits, cancellation and cleanup. A code interpreter should be an execution adapter beneath the runtime, not a source of self-reported correctness.
3. X3. Keep public examples and private assessment cases distinct. The accepted item owns its tests and comparison policy. Candidate stdout, assertions and browser worker messages remain untrusted observations. Verify full silent-mode payloads before connecting Dojo to assessments.
4. X4. Add domain checkers according to the answer's meaning. Numeric answers need absolute/relative tolerance and rounding rules. Quantities also need units and dimensions. Symbolic answers need a bounded grammar, variable/domain assumptions and a specified equivalence relation. SQL/data tasks need controlled datasets and result comparators. Proofs and explanation quality remain reviewed or explicitly advisory.
5. X5. Preserve recoverable drafts and versioned submitted artifacts before expanding to packages or multi-file projects. Require replayable synthetic tests, offline/unavailable behavior, and meaningful accessible input for each new adapter. A Python result, a diagram result and a math expression should share authority without being forced into the same editor.

These are audit recommendations. They do not accept a new schema or implementation plan. Existing user direction supports code reading, tracing, debugging, typed code and broader CS coursework. The prior depth audit remains the selection guide for choosing the smallest useful interaction.

## Verification and scope limits

`python3 tests/check_roundtrip.py` passed with `check roundtrip: ok`. It covers parser defaults, ordinary and harness execution, timeout/output limits, public contracts, evidence, browser/agent paths, and network/language refusal. `python3 tests/latex_input_roundtrip.py` passed with `latex input: contract, pending authority, fallback, and local preview passed`. The two targeted defect probes above also ran successfully and demonstrated the failures. Passing existing tests does not close either defect.

The audit read the earlier code-depth report, its September 19 implementation update, the bounded current vision/workflow sections, and relevant symbols in model, runtime, runner, session, daemon, quiz and prototype files. Large production modules were sampled by symbol and line window, not read in full. No full suite, packaged/installed-app test, new Dojo browser validation, malicious execution test, or human accessibility acceptance was performed. Prior Dojo Chromium results are historical evidence only.

Read scope was this checkout and relevant memory pointers. Write scope was this new report with an absent expected base. Patch creation is the operation record. Removing this report reverses this packet. No real learner material was read or submitted, and no source or learner data was sent to an external service.
