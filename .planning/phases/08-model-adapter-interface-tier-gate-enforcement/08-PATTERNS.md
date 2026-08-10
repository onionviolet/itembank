# Phase 8: Model Adapter Interface & Tier-Gate Enforcement - Pattern Map

**Mapped:** 2026-08-10
**Files analyzed:** 13 (5 new, 8 modified, derived from CONTEXT.md D-01..D-27 + RESEARCH.md file list)
**Analogs found:** 13 / 13 (1 partial)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `model_adapter.py` (new) | service / adapter | request-response (subprocess + HTTP transport) | `surfaces/launcher.py` + `surfaces/update.py:282-339` | role-match |
| `tier_gate.py` (new) | service / gate | transform + validation | `runtime.py:230` `glossable()` + `schema_validate.py:117` `validate()` | partial (no existing gate module; `glossable()` is the only runtime-gate precedent) |
| `schemas/model_adapter.schema.json` (new) | config / contract | validation | `schemas/settings.schema.json:91-131` (typed record) + `schemas/response.schema.json` `$defs` | exact |
| `tests/model_adapter_roundtrip.py` (new) | test | request-response | `tests/agent_roundtrip.py` | exact |
| `tests/model_gate_roundtrip.py` (new) | test | transform / validation | `tests/evidence_roundtrip.py:38-57` fail() harness + adversarial assertion style | exact |
| `evidence.py` (modified) | model / event schema | event-driven | itself: `KNOWN_EVENT_TYPES:43`, `term_lookup_event:1393`, `key_review_event:1435`, `mark_event:1036` | exact |
| `schemas/response.schema.json` (modified) | published contract | validation | itself: `$defs` `mark_event:132`, `term_lookup:220`, `event_type` enum `:24-28` | exact |
| `schemas/settings.schema.json` (modified) | config / contract | validation | itself: `model_backend:91-131` (inert object to be replaced by a profile array) | exact |
| `surfaces/settings.py` (modified) | config reader | request-response | itself: `get_at:120`, `schema_for_key:141`, `load_settings:78` | exact |
| `surfaces/session.py` (modified) | controller / CLI | request-response | itself: `do_start:54` / `cmd_start:87` split; evidence append in `do_submit` | exact |
| `surfaces/daemon.py` (modified) | route / controller | request-response | itself: `API_ROUTES:69-75`, `handle_api_submit:1273`, `api_read_json:1117`, `API_FORBIDDEN_FIELDS:1070` | exact |
| `surfaces/cli.py` (modified) | route / config | request-response | itself: import block `:7-21`, `main():111` sub_parser registration | exact |
| `surfaces/evidence_cli.py` (modified) | controller / CLI | request-response | itself: `cmd_mark:253-302` batch-resolve-then-append | exact |
| `runtime.py` (modified) | runtime seam | request-response | itself: `public_item:27`, `explain_payload:301`, `glossable:230` | exact |

## Pattern Assignments

### `model_adapter.py` (service/adapter, request-response)

**Analog 1:** `surfaces/launcher.py` - the house subprocess-with-timeout pattern.

Error classes are captured at import time so tests that patch `launcher.subprocess` cannot read failure modes off a fake module (launcher.py:24-27):

```python
_SUBPROCESS_ERRORS = (OSError, subprocess.SubprocessError)
```

Transport call shape (launcher.py:75-90):

```python
result = subprocess.run(
    argv, capture_output=True, text=True, timeout=...)
...
except (OSError, subprocess.TimeoutExpired):
    ...
```

**Analog 2:** `surfaces/update.py:282-339` `check_latest()` - the house urllib pattern: "Returns the parsed JSON document, or `None` on anything short of a clean 200 ... Nothing here raises." Concrete shape:

```python
req = urllib.request.Request(url, headers=headers)
try:
    with _open_request(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as exc:
    return None            # HTTPError must precede URLError (subclass)
except (urllib.error.URLError, TimeoutError, OSError):
    return None
```

**Core pattern for Phase 8:** one typed `invoke(request, profile)` boundary (D-01/D-02); the caller receives a normalized result dict, never a provider type. Every failure family (disabled profile, executable-not-found, nonzero exit, timeout, HTTP/URL error, malformed JSON, oversized stdout/body, refusal) converts to one typed `unavailable` result before any surface or evidence call - RESEARCH.md Pattern 2. Hosted CLI is the default and first backend (D-18); local HTTP is a second registration behind the same function (D-27: third backend = new module + config entry only).

**Secrets:** mirror `surfaces/update.py`'s token rule - credentials come from an environment variable reference in the profile, never from the settings file value, and never enter a log or manifest (D-03/D-15).

### `tier_gate.py` (service/gate, transform + validation)

**Analog:** `runtime.py:230` `glossable()` - the one existing "runtime decides what reaches the learner" gate. It is deliberately conservative ("on any ambiguity it returns False"), pure, deterministic, and its docstring states it is NOT a secrecy mechanism (runtime.py:230-265). Phase 8's gate is the same class of decision, one layer stricter:

```python
def glossable(qs, term):
    """The one gate between a term's definition and the learner: False when
    the definition text could disclose keyed answer material ... It is
    deliberately conservative -- on any ambiguity it returns False. It is a
    pure function: no I/O, no side effects, deterministic across calls."""
```

**Analog 2:** `schema_validate.py:117` `validate()` - returns a list of error strings; strict `additionalProperties: false` + `required` + enum enforcement; a schema using an unsupported keyword is refused before any instance is examined (`check_schema:47`, `SUPPORTED:24-33`). The gate's layer 1 (schema validation) should call exactly this function against the new `schemas/model_adapter.schema.json`; "any validation error is `drop` with a reason code" (RESEARCH.md Pattern 1 step 2).

**Analog 3:** `model.py:630` `content_fingerprint()` - the house pattern for deterministic include/exclude sets over tested content (explicitly excludes `why`, `disc`, `second`, `trap`, `conf`, `da`, `notes`; includes `correct`, `model`, `rubric`). The tier manifest's allowed-fact/protected-fact split (D-06) must be built from the same `q["correct"]`, `q["model"]`, `q["rubric"]`, `q["da"]` fields with an explicit include list, exactly this way.

**Core pattern (RESEARCH.md Pattern 1, must be independently planned and tested):** build a manifest from the private item + most recent genuine wrong response + Phase 6 permitted tier; assign stable internal fact IDs; validate provider JSON strictly; resolve every learner-response span and fact ID against the manifest (never trust a provider-supplied source label - Pitfall 1); reject unknown/protected/higher-tier/duplicate/raw-text references; render the learner text only from fixed runtime templates (D-05/D-06/D-07). Gate outcomes are `pass` / `drop` / `unavailable` with machine-readable reasons (D-08).

### `schemas/model_adapter.schema.json` (config/contract, validation)

**Analog 1:** `schemas/settings.schema.json:91-131` - the existing `model_backend` typed-object contract (strict `additionalProperties: false`, `required`, `enum`, `default`, `x-itembank-phase`). The new schema reuses this exact shape for profiles, but as an **array of records** with fixed properties and runtime validation of unique names / active-profile resolution (RESEARCH.md Pitfall 3 - the local validator has no `patternProperties` or value-valued `additionalProperties`).

**Analog 2:** `schemas/response.schema.json` `$defs` (lines 132-294) - each published payload gets its own `$id`, `x-itembank-version`, strict `additionalProperties: false`, and descriptive `$defs` for compound shapes.

**Constraint:** only keywords in `schema_validate.py:24-33` (`SUPPORTED`) are usable: `type, properties, required, additionalProperties, enum, const, items, minItems, minLength, pattern, minimum, maximum, $defs, $ref (local), oneOf`. Anything else fails `check_schema` by design.

### `tests/model_adapter_roundtrip.py` (test, request-response)

**Analog:** `tests/agent_roundtrip.py` (63 lines, exact). Structure: module-level `ROOT`/`BANK`/`TOOL` paths; `run(*args)` helper that invokes `itembank.py` via `subprocess.run` and returns parsed stdout JSON; `check_*()` functions; `main()` that runs each check and prints a one-line PASS; `if __name__ == "__main__": main()`. For Phase 8 add: a fake hosted CLI executable (a temp script fed through the configured profile) and a fake loopback HTTP server, both returning the identical normalized result (MODEL-01/MODEL-02), plus unavailable cases (MODEL-03) and the no-score invariant for proposals (TEACH-09/MODEL-05).

### `tests/model_gate_roundtrip.py` (test, transform/validation)

**Analog:** `tests/evidence_roundtrip.py:38-57` - the fail() harness and constant assertion sets:

```python
def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```

Adversarial corpus style (research Wave 0): key, correct option, higher-tier fact, fake source label, raw free-text field, and malformed response all must `drop` (TEACH-05/TEACH-06); a pass fixture must contain exactly one exact learner-response span and one allowed fact ID (TEACH-04). Assertions should use the same "forbidden phrase absent from output" discipline `evidence_roundtrip.py`'s `flatten()` uses (lines 44-57).

### `evidence.py` (model/event schema, event-driven)

**Analog 1 - the one-line type registration (evidence.py:43-44):**

```python
KNOWN_EVENT_TYPES = ("response", "retraction", "mark", "day_tick",
                     "term_lookup", "key_review")
```

Phase 8 adds `"mark_proposal"` (D-23) and a model-interaction event type here. `events()` (429+) skips-and-warns on unknown types, so this tuple is the entire reader mechanism.

**Analog 2 - the event-builder shape (`term_lookup_event:1393`, `key_review_event:1435`):** own envelope (`schema_version`, `event_id`, `event_type`, `ts`, ...), `ValueError` on malformed args (provenance validated because the log is append-only), `dedupe_key = sha256 over (session fields)`, and **structurally no `score` key at all** - the concrete form of "proposal never accepted evidence" (D-20/D-25, mirroring how `term_lookup`/`key_review` carry no score).

**Analog 3 - the human-only guard (evidence.py:1058-1063):**

```python
if marker != "human":
    raise ValueError(
        "mark_event: marker must be 'human' in this phase (got %r); a "
        "model verdict is not accepted evidence until Phase 8 (TEACH-09)"
        % (marker,))
```

This guard is **unchanged** (D-23). `mark_proposal_event` is a separate event type; `marks_by_event:1117` and the `review_state` read-time derivation (render_attempt_md / render_session_json) keep operating on `MARK_EVENT_TYPE` only, so a proposal never settles a mark.

**Analog 4 - append-only writer:** `append_event:399` is the ONE writer; new events go through it with a `dedupe_key` (at-most-one generation per interaction id, D-12).

### `schemas/response.schema.json` (published contract, validation)

**Analog:** itself - the `$defs` block pattern (mark_event at 132, term_lookup at 220, key_review at 246): each event body is a descriptive object under `$defs` with `event_type: {"const": ...}` plus its own fields, "not yet wired into a top-level oneOf". Phase 8 adds `mark_proposal` and model-interaction `$defs` the same way and extends the `event_type` enum at lines 26-27. Update the required/properties note in the description when the phase wires a top-level `oneOf`.

### `schemas/settings.schema.json` (config/contract, validation)

**Analog:** itself - the `model_backend` block at 91-131 is the exact contract to replace: currently a single object `{kind, endpoint, model}` with `"none"` default. Per D-02/D-18/D-27 and RESEARCH.md Pitfall 3, the new shape is an **array of named profile records** (each carrying transport type, endpoint/command, model, context/latency limits, secret env reference) plus an active-profile selector; the default remains disabled (`kind: none` behavior) per RESEARCH.md Environment Availability. Keep `x-itembank-phase: 8` on every new key so `itembank config` reports them as read by this phase.

### `surfaces/settings.py` (config reader, request-response)

**Analog:** itself - `get_at:120` / `schema_for_key:141` walk nested dotted paths; `load_settings:78` validates per-key through `schema_validate.validate()`; `classify_error:154` maps validator strings to `SETTINGS_CODES`; `decode_value` handles CLI value typing. The active-profile resolver for `model_backend` should live here (or be imported from here) so both `itembank config` and the adapter read the same validated settings (RESEARCH.md Architectural Responsibility Map row 1).

### `surfaces/session.py` (controller/CLI, request-response)

**Analog:** itself - the `do_*`/`cmd_*` split (do_start:54 / cmd_start:87; do_submit ~97-135 / cmd_submit ~137). New hint/rubric operations follow the same split: `do_*` computes and returns a dict, `cmd_*` unpacks argparse, prints `json.dumps(result, ensure_ascii=False, indent=2)`, returns 0. `do_submit` is the model for the evidence append flow (build event -> `evidence.append_event(log, event)` -> record `status` -> write session). A failed/gated hint augments the authored tier and must never `sys.exit` out of the session path (D-04/D-08/MODEL-03).

### `surfaces/daemon.py` (route/controller, request-response)

**Analog:** itself - add routes to `API_ROUTES:69-75` and a `ROUTE_CLI` entry (99-125, the key set is asserted equal to ROUTES so a route without a CLI twin fails the build). Every new handler follows `handle_api_start:1154` / `handle_api_submit:1273`:

- `api_read_json(handler)` first (malformed/non-object/forbidden-field -> 400, no 500);
- identifier resolution through an allowlist (`session_index` / `handler.banks`), never a path join;
- the two-clause containment that must not be collapsed:

```python
try:
    result = session.do_submit(path, answer, confidence)
except SystemExit as exc:
    handler.send_error(400, str(exc.code))
    return
except Exception as exc:
    handler.send_server_error(exc)
    return
```

- **browser never receives key/tier/private item:** extend `API_FORBIDDEN_FIELDS` (1070-1076) so a client cannot smuggle `key`, `tier`, `item_id`-style authority fields into a hint/review request (D-09);
- learner-facing refusal is runtime state rendered as a structural lock, never model voice (D-26).

### `surfaces/cli.py` (route/config, request-response)

**Analog:** itself - add the new `cmd_hint`/proposal commands to the import block (7-21) and register in `main()` (111+) with the exact `sub.add_parser` + `s.set_defaults(fn=...)` shape used by `mark`/`render`/`start`. Keep wiring declarative and thin; all logic lives in `session.py`/`evidence_cli.py`.

### `surfaces/evidence_cli.py` (controller/CLI, request-response)

**Analog:** itself - `cmd_mark:253-302` is the batch human-accept path. The pattern to copy: resolve **every** entry against the log before appending any (a batch naming one unknown target exits non-zero with nothing appended), then append through `evidence.append_event`, reporting `recorded` vs `already_recorded` and printing the JSON payload plus a one-line human summary. Phase 8's batch accept of pending proposals is this exact command shape with `mark_proposal` resolution replacing `_resolve_marks_event`.

### `runtime.py` (runtime seam, request-response)

**Analog:** itself - `public_item:27` / `explain_payload:301` are the existing private/public boundaries; `glossable:230` is the conservative-gate precedent. Phase 8 Plan 1 must declare the minimal `permitted_hint_context` input contract here (private item + Phase 6 permitted tier + most recent wrong response) so tier-gate and adapter never see or infer tier progression (D-09); the browser gets neither (RESEARCH.md Open Question 1).

## Shared Patterns

### Append-only event addition
**Sources:** `evidence.py:43`, `:1393`, `:1435`, `:1036`; `schemas/response.schema.json` `$defs`
**Apply to:** `evidence.py`, `schemas/response.schema.json`
Add the event type to `KNOWN_EVENT_TYPES` in the same commit as the builder; builder has no `score` key; `dedupe_key` hashed over identifying fields; `mark_event`'s `marker != "human"` guard untouched.

### Strict schema validation
**Source:** `schema_validate.py:24-33` (`SUPPORTED`) + `:117` `validate()`
**Apply to:** `schemas/model_adapter.schema.json`, `tier_gate.py` layer 1
New schemas use only the supported keyword subset; validation failures are a list of `path: message` strings; any validation error is `drop`.

### Typed unavailable, never exception leakage
**Sources:** `surfaces/launcher.py:24-27,75-90`; `surfaces/update.py:282-339`
**Apply to:** `model_adapter.py`
Convert disabled/unreachable/malformed/timed-out/refused to one typed unavailable result before any surface or evidence call; authored hints, scoring, lessons, reports, and marking continue (D-04, MODEL-03).

### Daemon route containment + identifier allowlist
**Source:** `surfaces/daemon.py:1060-1141`, `:1154`, `:1273`
**Apply to:** new hint/review routes in `surfaces/daemon.py`
`api_read_json` first; resolve ids through allowlists only; separate `SystemExit` (400) from `Exception` (500); forbid `key`/`tier`/path fields on the wire.

### do_* / cmd_* split + ROUTE_CLI parity
**Sources:** `surfaces/session.py:54,87`; `surfaces/evidence_cli.py:253`; `surfaces/cli.py:111`; `surfaces/daemon.py:99-125`
**Apply to:** every new CLI command and daemon route. One runtime call behind both surfaces; `tests/agent_roundtrip.py`'s `check_cli_reaches_shared_do_functions` proves it by source inspection.

### Runtime owns the learner boundary
**Source:** `runtime.py:27,230,301`
**Apply to:** `tier_gate.py`, `model_adapter.py`, `runtime.py`
Only `pass` content enters a learner-facing payload; the gate receives the full private item, the browser receives neither item nor tier; refusals render as runtime structural locks (D-08, D-09, D-26).

### Test harness
**Sources:** `tests/evidence_roundtrip.py:38-57`; `tests/agent_roundtrip.py`
**Apply to:** `tests/model_gate_roundtrip.py`, `tests/model_adapter_roundtrip.py`
No framework; `fail()` + plain asserts; subprocess-driven CLI paths; adversarial fixtures assert forbidden content never appears in any normal output.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tier_gate.py` | service / gate | transform + validation | No existing gate component; `runtime.glossable()` is a role-match precedent, but the bounded hint-plan + manifest + fixed-renderer design is original. Planner should use RESEARCH.md Pattern 1 (gate algorithm steps 1-5) with the `glossable()` / `validate()` / `content_fingerprint()` excerpts above. |

## Metadata

**Analog search scope:** repository root modules (`runtime.py`, `evidence.py`, `schema_validate.py`, `model.py`, `resources.py`), `surfaces/` (daemon, session, settings, cli, evidence_cli, launcher, update, lesson), `schemas/`, `tests/`
**Files scanned:** 24 source/schema/test files (plus prior-phase PATTERNS.md for house style)
**Pattern extraction date:** 2026-08-10
