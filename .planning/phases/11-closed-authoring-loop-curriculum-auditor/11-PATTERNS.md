# Phase 11: Closed Authoring Loop & Curriculum Auditor - Pattern Map

**Mapped:** 2026-08-08  
**Files analyzed:** 12 planned source/test groups  
**Analogs found:** 11 / 12

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `auditor.py` | service | transform / file-I/O | `evidence.py` | role-match |
| `authoring.py` | service | request-response / transform | `model.py` | role-match |
| `surfaces/audit_cli.py` | controller | request-response | `surfaces/evidence_cli.py` | role-match |
| `surfaces/cli.py` | route/config | request-response | itself (`id-assign` registration) | exact |
| `schemas/authoring_request.schema.json` | config/contract | transform | `schemas/lint_error.schema.json` | role-match |
| `schemas/normalized_document.schema.json` | config/contract | file-I/O | `schemas/report.schema.json` | role-match |
| `schemas/audit_report.schema.json` | config/contract | transform | `schemas/report.schema.json` | exact |
| `schemas/quality_finding.schema.json` | config/contract | transform | `schemas/lint_error.schema.json` | exact |
| `schemas/write_manifest.schema.json` | config/contract | file-I/O | `schemas/update_manifest.schema.json` | role-match |
| `tests/audit_roundtrip.py` | test | request-response / file-I/O | `tests/protocol_roundtrip.py` | role-match |
| `fixtures/audit/` | test fixture | file-I/O | `fixtures/` and temporary copies in `tests/evidence_roundtrip.py` | role-match |
| `surfaces/daemon.py` (only after UI contract) | controller/route | request-response | existing daemon route table | partial |

## Pattern Assignments

### `auditor.py` (service, transform/file-I/O)

**Analog:** `evidence.py`

Keep this as a root-level domain primitive, not a surface extension. `evidence.py` explicitly separates its durable domain concern from the format model and surface tiers (lines 1-18), and centralizes path helpers (lines 56-66). Use the same shape for source normalization, reports, manifests, fingerprints, and coverage records.

```python
# evidence.py:56-66
def evidence_dir(base):
    return os.path.join(os.path.abspath(base), EVIDENCE_DIRNAME)

def log_path(base):
    return os.path.join(evidence_dir(base), LOG_FILENAME)
```

For derived JSON artifacts, retain the repository's UTF-8, pretty JSON, trailing newline, tmp-then-replace convention from `runtime.py:178-185`:

```python
tmp = target + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
os.replace(tmp, target)
```

### `authoring.py` (service, request-response/transform)

**Analog:** `model.py`

Authoring must compose the public model contract rather than duplicate parsing, IDs, hashes, or lint. Import from the model layer only; it intentionally has no surface/session dependency (`model.py:1-5`). Preflight the entire candidate set before any writer invocation, following the pure-transform boundary:

```python
# model.py:196-209
def assign_ids(text, taken=None):
    """Pure text transform ... touches no file."""
```

Use the published structured finding form for retry payloads, preserving errors/warnings as records:

```python
# model.py:403-410; surfaces/cli.py:29-41
errors, warnings = lint(qs)
payload = {
    "schema_version": 1,
    "errors": [e._asdict() for e in errors],
    "warnings": [w._asdict() for w in warnings],
}
```

Second-gate findings must remain separate from `LintError`; mirror lint's explicit, named evidence rather than a composite score. Reuse its observable checks as inputs: non-correct distractors without a condition are emitted at `model.py:475-485`, duplicate stems at `542-546`, and MC skew at `548-558`.

### `surfaces/audit_cli.py` (controller, request-response)

**Analog:** `surfaces/evidence_cli.py`

The surface receives parsed argparse arguments, calls domain functions, emits machine-readable UTF-8 JSON plus a concise human summary, and returns an exit code. It must not reimplement source parsing, coverage logic, validation, retries, or writing.

```python
# surfaces/evidence_cli.py:298-302
payload = {"schema_version": evidence.EVENT_SCHEMA_VERSION, ...}
print(json.dumps(payload, ensure_ascii=False, indent=2))
print("%d recorded, %d already recorded" % (recorded, already_recorded))
return 0
```

### `surfaces/cli.py` (route/config, request-response)

**Analog:** existing command import and `id-assign` registration.

Add `cmd_audit` from the dedicated surface module to the import block (`surfaces/cli.py:7-21`), then register a single command in `main()`. Keep CLI wiring declarative and thin:

```python
# surfaces/cli.py:249-255
s = sub.add_parser("id-assign", help="...")
s.add_argument("banks", nargs="+")
s.add_argument("--dry-run", action="store_true", dest="dry_run")
s.set_defaults(fn=cmd_id_assign)
```

Use sub-actions/arguments to expose `audit`, bounded authoring, explicit acceptance, and `audit undo <write-id>` without a second parser in `audit_cli.py`.

### `schemas/{authoring_request,normalized_document,audit_report,quality_finding,write_manifest}.schema.json` (config contracts)

**Analogs:** `schemas/lint_error.schema.json`, `schemas/report.schema.json`

Every new public payload gets its own versioned, strict JSON Schema. Follow `lint_error.schema.json:1-55`: `$id`, `x-itembank-version`, `type: object`, `additionalProperties: false`, explicit `required`, and descriptions. Use only keywords supported by the local validator (`schema_validate.py:23-33`); unsupported JSON Schema features fail intentionally.

```json
{
  "$id": "https://itembank.local/schemas/quality_finding.schema.json",
  "x-itembank-version": 1,
  "type": "object",
  "additionalProperties": false,
  "required": ["code", "field", "item", "message"],
  "properties": {"code": {"type": "string"}}
}
```

Use new schemas for the actual Phase 11 fields, not this lint field set: source span locators and fingerprints; exact `item_id` citations; coverage state; request bounds; detector version/evidence; proposal counts/diff; backend and before/after fingerprints. Ensure `schema_version` is required in every runtime payload.

### `tests/audit_roundtrip.py` (test, request-response/file-I/O)

**Analog:** `tests/protocol_roundtrip.py`

Use a standalone stdlib executable with repository-root import setup, `fail()`, subprocess-driven CLI checks, and temp directories:

```python
# tests/protocol_roundtrip.py:7-33
import json, os, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)
```

Test protocol data structurally (not only prose): `tests/protocol_roundtrip.py:62-109` asserts finding classes, dotted codes, declared code namespaces, and exact JSON keys. Copy the temporary-fixture isolation precedent from `tests/evidence_roundtrip.py:210-222`; never mutate a committed bank fixture.

### `fixtures/audit/` (test fixture, file-I/O)

**Analog:** `fixtures/` plus temp copies in `tests/evidence_roundtrip.py:210-222`.

Keep only synthetic Markdown/text sources, malformed/clean generated drafts, and expected normalized/report data. Tests copy them to a temporary directory before exercising either Git or shadow writer. Do not put a real bank outside `fixtures/`: `surfaces/cli.py:75-98` guard rejects it.

### `surfaces/daemon.py` (controller, request-response) — deferred pending UI contract

**No phase-ready analog assignment:** research marks the route/UI contract blocked. Once UI-SPEC supplies route names and approval interaction, call the same `auditor.py`/`authoring.py` domain functions as `audit_cli.py`; do not introduce browser-only validation or a separate writer.

## Shared Patterns

### Public contract, validation, and machine-readable errors

**Sources:** `model.py:280-362`, `model.py:373-400`, `schema_validate.py:115-149`, `surfaces/cli.py:29-47`

- Give a model `SPEC`, published JSON schemas, the bounded request, and structured failures only.
- Keep finding codes stable and additive; `LintError` uses a dotted public API namespace (`model.py:373-400`).
- Validate any newly published schema through `schema_validate.validate()`; this validator deliberately rejects unsupported schema keywords.

### All-or-nothing preflight and one writer

**Sources:** `surfaces/evidence_cli.py:305-342`, `model.py:196-277`

Read every relevant bank first, detect cross-bank identity conflicts, construct all outputs in memory, and only then mutate. The current writer's core form is:

```python
# surfaces/evidence_cli.py:305-342
texts[path] = text
new_text, changes = model.assign_ids(texts[path], taken)
if not a.dry_run and new_text != texts[path]:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    os.replace(tmp, path)
```

Phase 11 should establish its transactional authoring writer as the sole bank mutation seam, preserve a complete failed batch, and choose Git/shadow undo only after all lint and quality checks pass.

### Derived artifacts and integrity

**Sources:** `model.py:142-177`, `runtime.py:178-185`, `evidence.py:16-18`

Use SHA-256 fingerprints as change detection—not authorization—and include source, bank, request, adapter/profile, and tool-version provenance in reports/manifests. Produce reproducible diff/report artifacts with stable UTF-8 serialization.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `surfaces/daemon.py` audit/approval route | controller | request-response | UI/route contract is explicitly pending UI-SPEC; no current approval workflow analog exists. |

## Metadata

**Analog search scope:** root domain modules, `surfaces/`, `schemas/`, `tests/`, and `fixtures/`  
**Files scanned:** 10 primary analogs  
**Pattern extraction date:** 2026-08-08
