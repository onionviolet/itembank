# Exact domain completion packet, 2026-09-30

Status: proposed v1 mechanisms and declaration, not an accepted bank grammar
or registered production checker. C owns shared production wiring. D owns only
`question_domains.py`, `tests/question_domains_roundtrip.py` and this report.
These paths were absent before creation. No existing writer's paths were edited.

## Direct-user decision specimen

Q1: Approve the following additive `kind: domain` FIELDS declaration, exact
normalization rules and refusal policy for the four bounded domains? This
accepts the v1 format only; production, source journeys, human accessibility,
package and installed acceptance still need their respective evidence.

The existing fill answer transport remains a dictionary from field IDs to raw
single-line strings. Native labelled text inputs and useful plain Markdown
examples remain the initial surface. No matrix widget or new item type is
needed. Proposed public metadata contains only domain, version, grammar, fixed
limits, shape and vector orientation. Target, diagnostic answers and test rows
remain private. Existing formal withholding and practice hint tiers apply.

```json
{
  "id": "solution",
  "label": "Solution set",
  "kind": "domain",
  "checker": {
    "domain": "rational-set",
    "checker_version": "exact-domains-v1",
    "target": "{1,2}",
    "diagnostics": [{"id": "missing-member", "answer": "{1}"}],
    "shape": null,
    "orientation": null
  },
  "checker_tests": [
    {"input": "{1,2}", "state": "correct", "diagnostic_id": null, "checker_version": "exact-domains-v1"},
    {"input": "{2,1,1.0}", "state": "correct", "diagnostic_id": null, "checker_version": "exact-domains-v1"},
    {"input": "{3}", "state": "mathematically_wrong", "diagnostic_id": null, "checker_version": "exact-domains-v1"},
    {"input": "{1}", "state": "mathematically_wrong", "diagnostic_id": "missing-member", "checker_version": "exact-domains-v1"},
    {"input": "{1,}", "state": "invalid", "diagnostic_id": null, "checker_version": "exact-domains-v1"},
    {"input": "{x}", "state": "unsupported", "diagnostic_id": null, "checker_version": "exact-domains-v1"}
  ]
}
```

Other exact declarations replace the checker above with these specimens and
carry the same private test-row grammar:

```json
[
  {"domain": "rational-interval-set", "checker_version": "exact-domains-v1", "target": "[0,2)", "diagnostics": [{"id": "endpoint-inclusion", "answer": "[0,2]"}], "shape": null, "orientation": null},
  {"domain": "rational-vector", "checker_version": "exact-domains-v1", "target": "[1,2]", "diagnostics": [{"id": "reversed-components", "answer": "[2,1]"}], "shape": [2], "orientation": "column"},
  {"domain": "rational-matrix", "checker_version": "exact-domains-v1", "target": "[[1,2],[3,4]]", "diagnostics": [{"id": "transpose", "answer": "[[1,3],[2,4]]"}], "shape": [2,2], "orientation": null}
]
```

Recommended rules requiring the same direct decision:

- D1: All scalars reuse `runtime.fill_number` exactly, including signed
  fractions, decimals and scientific literals. Reduced numerator magnitude and
  denominator are each at most 1000000; scalar text is at most 128 characters.
  No tolerance, significant-figure checking, units, irrational, symbolic or
  complex semantics are inferred. This does not narrow existing numeric fields.
- D2: Finite rational sets use braces, including `{}`; at most 32 entered
  members before normalization. Order and duplicate multiplicity are ignored.
  Intervals denote subsets of the real line with rational finite endpoints:
  `[a,b]`, `(a,b]`, `[a,b)`, `(a,b)` and at most eight pieces joined with `U`.
  `empty` is the empty interval union. `-inf` and `inf` occur only as open
  outer endpoints. Canonicalization merges overlap and connected endpoints
  exactly, preserves excluded gaps, makes `[a,a]` a singleton, and other
  equal-endpoint intervals empty. Reversed endpoints refuse as invalid.
- D3: Vectors use `[a,b,...]`, with one to eight entries and explicit authored
  row or column orientation. Entry order is meaningful. Matrices use bracketed
  rows, one to eight rows by one to eight columns. Shape and every entry are
  exact. Transposition, row-equivalence and basis-equivalence are not equality.
- D4: A well-formed answer in the declared shape/domain with a different exact
  value is mathematically wrong and may receive a runtime-settled `False`.
  Wrong shape is proposed as an unresolved `invalid` entry refusal, not scored
  wrong, because shape is the declared response contract. This is an explicit
  pedagogical choice to approve; a future wrong-dimension diagnostic would need
  a different contract. Blank components never mean zero. Malformed syntax,
  unsupported constructs or bounds, unavailable configuration, and checker
  failure refuse before mutation with an input-preserving retry action. None
  creates a false mark or pending-prose evidence.
- D5: Entire input is one ASCII line of at most 4096 characters. At most two
  unique diagnostic IDs compare exact canonical answers, disjoint from the
  teacher and each other. Four to 128 pinned private test rows cover the exact
  teacher string, wrong mathematics, invalid, unsupported and every diagnostic.
  Tests replay through the runtime analyzer; test-table validation cannot
  independently settle scores. Config failure precedes learner-entry analysis.

Q1 may approve these rules together or request changes to particular D codes.
Until it is answered, the new module remains unregistered proposal code.

Private test specimens for the other declarations use the same pinned row
objects shown above. Each cell below is the `input` value; the column names
give the expected state and diagnostic ID. These must travel with the private
declaration and never become public sample answers:

| Domain | Correct teacher | Correct equivalent | Wrong mathematics, no diagnostic | Wrong mathematics, named diagnostic | Invalid | Unsupported |
| --- | --- | --- | --- | --- | --- | --- |
| rational-interval-set | `[0,2)` | `[0,1] U (1,2)` | `(0,2)` | `[0,2]`, endpoint-inclusion | `[1,0]` | `[0,x]` |
| rational-vector | `[1,2]` | `[1.0,4/2]` | `[3,4]` | `[2,1]`, reversed-components | `[1]` | `[x,2]` |
| rational-matrix | `[[1,2],[3,4]]` | `[[1.0,4/2],[3e0,4]]` | `[[3,4],[5,6]]` | `[[1,3],[2,4]]`, transpose | `[[1,2]]` | `[[x,2],[3,4]]` |

## Mechanism, authority and source basis

`canonicalize` returns immutable exact rational tuples. `validate_spec` checks
the proposed strict declaration and overlapping diagnostics. `prepare_comparison`
returns only original input, pinned version/domain and private exact operands.
It has no score, verdict, correctness state or file operations. A future
runtime adapter compares these operands inside `score_response`; surfaces never
receive the private Comparison object. `public_contract` returns copied public
entry metadata. `private_test_errors` replays pinned rows through a trusted
runtime-supplied analyzer, never authored executable code.

The existing numeric parser, multiplicative unit scales and polynomial checker
were sampled in `runtime.py`; completed polynomial work was not recreated.
F2/F8/F9 remain the family owners. Sets/intervals/linear algebra are distinct
answer constructs; this slice does not promise equations, CAS, Big-O,
significant figures, affine units, variants, dependent inputs or partial credit.

Official references refreshed September 30 provide patterns, not donor code:
[STACK set tests](https://docs.stack-assessment.org/en/Authoring/Answer_Tests/Results/Sets/)
separate set failures and checker execution failures;
[STACK linear algebra](https://docs.stack-assessment.org/en/Topics/Linear_algebra/)
and [vector representations](https://docs.stack-assessment.org/en/Topics/Linear_algebra/Vectors/)
distinguish vector/matrix constructs;
[PrairieLearn matrix components](https://docs.prairielearn.com/elements/pl-matrix-component-input/)
declare shape, fractions, blank handling, comparison policy and optional partial
credit independently. Exact rational equality and ASCII interval grammar here
are original bounded proposals. No source content or software was downloaded
or reused; no third-party runtime dependency was introduced.

## Production integration packet for C

After explicit Q1 acceptance, C extends the existing fill kind dispatch, private
field lint, canonical response identity, scorer, outcome evidence and public
entry contract through the same polynomial lifecycle. Reuse its refusal before
session mutation and existing formal/hint-tier filters. Resolve checker errors
before scoring; never translate DomainRefusal to `False` or `None`. Pin domain,
version, original input and normalization in private evidence; review any new
response/schema fields before writing. No checker output may grant disclosure.

Replay private authored tests on lint/accept, include checker/test declaration in
the existing fingerprint, and use existing agent proposal, journal-backed CAS
acceptance, stale conflict, cancellation and byte-exact undo. Session reload
must preserve original input, authored revision and pinned version. Old
text/numeric/polynomial declarations and historic evidence retain their meaning.
An unsupported future version refuses with an author review recovery action.

Exact next gate: a synthetic author-to-lint-to-preview-to-sitting-to-feedback-
to-report run for each domain, with raw-response reload, formal withholding,
injected checker failure and byte-identical session/evidence refusal checks.
Separate source/browser/native and package/installed/human gates explicitly.
C owns that shared production work; D can receive an exact released lease if
needed. No broad suite should run concurrently with C's combined freeze gate.

## Verification, recovery and limits

`python3 tests/question_domains_roundtrip.py` passed eight tests on the final
mechanism bytes. Independent interval membership checks covered all 576
two-piece combinations from 24 endpoint/closure pieces at seven rational
points, including singletons, empty pieces and gaps. Exact set, vector and
matrix values also have direct Fraction expectations. Boundaries cover 32/33
set members, 8/9 interval pieces, 8/9 vector entries, matrix 8-by-8 acceptance
and exceeded rows/columns, exact coefficient bounds and unknown versions.

Tests prove two diagnostic branches are order-independent and exact equivalent
overlaps refuse. Private table mismatches, omitted diagnostics, unknown fields,
wrong versions, checker failure and malformed runtime output reject acceptance.
Public projection excludes private targets/diagnostics and copies its limits.
Module refusal and preparation read/write no files under patched file APIs,
preserve original strings/configuration and leave a synthetic session file
byte-identical. Comparison operands contain no score or state. The synthetic
comparison harness calls only the existing runtime text-fill scorer; it is not
a production domain session or new grading authority.

The first scoped run passed six of seven tests; the harness used `answer`
instead of the existing text-fill `accepted` key and was corrected. This was
a synthetic harness error, not a production change. The corrected seven-test
run passed, then the added adversarial eighth test also passed.
`git diff --check` passed for tracked changes; new files are untracked so that
command does not certify their contents. No em dash was introduced in this
lane's authored files.

Tested SHA-256 fingerprints:

| Path | SHA-256 |
| --- | --- |
| `question_domains.py` | `eb79187ac4313d13d9d20b1a186d14c36fd325caf91c0a2fc058a27ca314cb69` |
| `tests/question_domains_roundtrip.py` | `15bd2aeb3dab9d25df3d3400fa73110a085539a09334d07ae07b7705cc962055` |

Commands actually run included the scoped suite (initial failure and two
passing revisions), `git diff --check`, `shasum -a 256` for mechanism/test,
read-only `rg`/`sed`/`cat` inventory and symbol windows, and absent-path `test`
checks before creation. Broad preflight is reserved for C after integration.

Read scope was this checkout and a narrow memory keyword search with no relevant
hits. Symbol windows sampled runtime numeric/polynomial and fill score/validation
functions. Binding workflow, execution context, exact product-contract clauses,
existing checker packet/evidence, backlog and reference-pattern sections were
read. Large runtime/model/evidence modules were not audited in full.

All test data are synthetic. Rights basis is user-authorized source development;
read-only public-source research sent only public query terms. No learner data,
private source, telemetry, remote source processing or execution service was
used. No commit, push, broad preflight, build, install or app mutation occurred.

These three paths had an absent expected base; patch creation records their
creation, and later patches preserve this lane's bytes. Undo removes only these
three new files while they remain unregistered and unconsumed. Once C wires
production, coordinate dependent removal first. This code cannot mutate a
session, bank, accepted revision or evidence file. Source proposal evidence
does not certify production, an installed package, accessibility or learning.
