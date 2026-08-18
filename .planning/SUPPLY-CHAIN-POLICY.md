# Supply-chain policy

- **Created:** 2026-08-17 (this session settles IL-20260815-09)
- **Status:** binding on every plan that introduces, updates, or removes a
  third-party artifact, and on every threat table that names supply-chain risk
- **Origin:** constraint audit `research/2026-08-10-constraint-audit.md` F5
  found the zero-dependency preference "standing in as a security control"
  after the 2026-08-09 relaxation left no control in its place. The
  `PLANNING-DIRECTIVES.md` section 4a supply-chain paragraph is the seed rule;
  this file is the full policy it promised.
- **Authority:** tier 3 record (binding format and rights surface,
  `AGENT-WORKFLOW.md` section 5). Changes to this policy are themselves
  tier 3.

## 1. Scope: what counts as a third-party artifact

Every artifact not authored in this repository that ships with, builds, or
runs the product: libraries (Python or JS), fonts, JS bundles, CSS
frameworks, icons, build toolchains, packagers, installers, signing tools,
CI actions, and any future plugin from outside the repository. Test-only and
build-only tools are in scope: they run with write access to the tree.

Out of scope: the learner's own content, model backends reached over an
adapter (governed by the rights and egress grants, not this file), and the
Python interpreter itself.

## 2. Acquisition rules

1. **Vendored by default.** A runtime dependency is copied into the
   repository at a pinned version, following the KaTeX precedent
   (`09-03-PLAN.md`). No CDN loads, no install-time network fetch on the
   learner's machine. This keeps the shipped product's "degrade, never
   block" promise independent of any registry being reachable.
2. **Pinned exactly.** Version pinned to an exact release, never a range.
   The pin, the upstream project URL, and the release URL are recorded in
   `VENDORED.md` at the repository root (created by the first plan that
   adds a vendored artifact after this policy; KaTeX and CodeMirror rows
   are backfilled by that same plan).
3. **Checksum recorded.** A SHA-256 of each vendored artifact (per file or
   per archive, whichever the artifact ships as) is recorded beside the pin
   in `VENDORED.md`. CI recomputes and compares these checksums; a mismatch
   fails the build. This turns silent tampering or accidental local edits of
   vendored code into a visible failure.
4. **License review named.** Each row names its license, the reviewer, and
   the review date. Acceptable by default: MIT, BSD, Apache-2.0, ISC, OFL
   (fonts). Copyleft (GPL/AGPL) and no-license artifacts require an explicit
   Weibao decision before adoption.
5. **Build-time and CI tools** (packagers, signers, GitHub Actions) may be
   fetched at build time rather than vendored, but must be pinned to an
   exact version or commit SHA (never a floating tag such as `@v5` alone
   where a SHA pin is supported), and the pin recorded in the same table.

## 3. Adoption gate: what a plan owes before adding a dependency

A plan that introduces a dependency states, in the plan itself:

1. The product capability that earns it, and the stdlib or vendored-code
   alternative considered with its real cost. "It needs a dependency" is
   never a rejection; "it does not earn its cost" must be argued.
2. The artifact's size, transitive dependency count (target: zero or near
   zero transitive runtime dependencies; each transitive dependency is
   itself a row in `VENDORED.md`), maintenance signal (release cadence,
   bus factor), and extraction fidelity or correctness evidence where the
   dependency parses learner content.
3. The exact `VENDORED.md` row it will add: pin, URLs, SHA-256, license,
   reviewer.
4. The removal path: what breaks if the dependency is deleted, and the
   degraded behavior. A dependency whose removal would strand learner data
   in an unreadable form is refused; formats stay readable without it.

## 4. Update cadence and review

- Vendored artifacts are reviewed opportunistically at each phase that
  touches their surface, and at minimum once per milestone: check upstream
  for security advisories, decide update or hold, record the decision as a
  dated note in `VENDORED.md`.
- An update is a normal compare-and-swap mutation: new pin, new checksum,
  diff reviewed, one commit, revert path stated.
- A security advisory against a vendored artifact is a stop-the-line item:
  it outranks feature work in the next session that sees it.

## 5. Threat-table language

A threat table may no longer accept supply-chain risk on the grounds that
"no dependency is installed" or "stdlib-only means nothing to audit". The
accepted mitigation is this policy: vendored, pinned, checksummed in CI,
license-reviewed, with a recorded update cadence. The two stale rows the
constraint audit left outstanding (`10-03-PLAN.md:128`, `10-06-PLAN.md:130`)
are historical execution artifacts of a shipped phase; they are superseded
by this file and are not rewritten in place.

## 6. Interaction with plugins (IL-20260816-01)

Plugin machinery at named seams does not change this policy: a first-party
plugin in this repository is ordinary code; any third-party plugin would be
a third-party artifact under section 1 and is not currently proposed. No
plugin loader may fetch code at runtime.

## 7. What this policy does not decide

It does not decide any specific dependency (PDF extraction, test runner,
Anki import are their own ledger entries). It sets the bar those decisions
must clear and the record they must leave.
