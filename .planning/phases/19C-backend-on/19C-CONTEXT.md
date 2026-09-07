# Phase 19C context: backend on

**Status:** execution context for the bounded 19C diagnostic. This context
implements the phase seed and VPA-03. It adds no backend capability and accepts
no generated course content.

## Observable result

The shipped `local-qwen` profile is active with a model that exists on this
machine. The product's director, recommendation pass, and six-stage seeding
entry point are each run against a disposable copy of the existing real EMT
course material. Their complete terminal records are retained outside the
repository and judged in `19C-VERIFICATION.md`.

## Operation declaration

| Field | Declaration |
|---|---|
| Profile and revision | `local-qwen`, profile revision 2 for 19C. Revision 2 changes the registered model from unavailable `qwen3.8-27b:latest` to installed `qwen3.5:4b`; transport and limits are unchanged. |
| Endpoint | `http://127.0.0.1:11434/v1/chat/completions`, Ollama 0.31.1 on this Mac. |
| Egress | Local process to loopback only. No content leaves this machine. |
| Read scope | `/Users/weiwei/Documents/itembank-courses/emt-unit-1`, the existing user-owned real EMT course, read through a disposable diagnostic copy. |
| Rights basis | The learner owns the local course artifacts and authorized this bounded diagnostic. Existing accepted lesson and bank files may be read and locally transformed for inspection. No remote processing, publication, packaging, export, or sharing is granted. |
| Authority | `recommend-only`. Model output is advisory diagnostic material. It cannot bind a treatment, modify the canonical EMT course, settle a mark, reveal a key, or become accepted learner content. |
| Write scope | A new diagnostic directory below `/Users/weiwei/Documents/itembank-courses/_diagnostics/19c-backend-on`; `itembank.json`; and Phase 19C planning, verification, and summary records. |
| Durable record | Verbatim command transcripts and disposable course copies stay below the diagnostic directory. The repository records paths, hashes, results, and judgment without copying real bank or source text. |
| Validation | Confirm endpoint version and installed models, run one director recommendation, one recommendation pass, and one seeding attempt, inspect every transcript, run targeted adapter/director/seeding suites, run guard, then run preflight. |
| Recovery | Revert the Phase 19C commit to restore the disabled shipped profile. Move the diagnostic directory to trash after review if desired. The original EMT course is never written. |
| Manual fallback | Keep direct reading, hand-authored treatment selection, lint, provenance, and assessment runtime available. A failed local model call never blocks them. |

## Settled decisions

- **D19C-01:** Use the existing EMT unit because it is the only retained real
  course material named by project state. The 17B fixture is excluded.
- **D19C-02:** Use the installed 4.7B Qwen model rather than downloading the
  historical 27B planning candidate. This phase measures the machine as found
  and does not expand into model procurement or benchmarking.
- **D19C-03:** Preserve failures as findings. A transport, response-contract,
  or seeding integration defect is routed to its existing owner and is not
  repaired inside 19C.
- **D19C-04:** A diagnostic run cannot accept or apply model output. The
  canonical EMT course and its evidence remain byte-untouched.

## Bounded execution packet

Execute `19C-01-PLAN.md` as one atomic plan. Stop after recording and routing
the three required path results. Do not change Phase 19A, 19B, 19D, or 19E.
