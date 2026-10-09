# F2 changed-source impact review

STATUS: source released for integration

Released paths: `surfaces/course_workbench.py`, `surfaces/course_context_view.py`,
`tests/product_gm_parity_source_impact_roundtrip.py`, and this report. No shared
route seam is required. Other source and tests were preserved.

The Sources route previously named only affected objectives. It now joins exact
accepted source IDs, binding revisions, and the validated reading manifest to
show current reading occurrence revisions and bound treatment task links. Each
reading names its occurrence, revision, binding revision, source fingerprint,
and locator. Treatments show their binding identity, revision and exact admitted
artifact locator. Missing artifacts, unsupported treatment routes, missing
objective IDs, unvalidated reading manifests and unavailable source registrations
are explicit. No title matching supplies identity.

Superseded reading and binding revisions remain recorded history and are counted
separately. A reading still pinned to a superseded binding is excluded from
current impact and reported explicitly. Legacy treatments keep honest missing-ID
language. Readings and linked lesson/practice/test actions use existing routes;
the existing source and runtime checks still own content disclosure. Changed
source bytes stay withheld, and source fingerprints are unavailable without the
read grant. No source adoption, regeneration, score, mastery claim, evidence
reassignment or durable write occurs during inspection.

## Source evidence and checks

Base HEAD: `28bf561865cf0696a8beb42dd6f356b8bf6ec648`. Before-images saved before
editing in ignored `.reasonix/product-gm-20261004/parity-impact/`:

| Before-image | SHA-256 |
| --- | --- |
| `course_workbench.py.txt` | `6f76c18459f16759ac9ef0ad64c5921dc6cca2a653dfa92815c5d5c9e51eb6f7` |
| `course_context_view.py.txt` | `1bdeb2d74cc644ce59d6612e73ac20dac96497c1b3111a2518797f6edc3720c3` |

Released source SHA-256 pins:

| Path | SHA-256 |
| --- | --- |
| `surfaces/course_workbench.py` | `e1de7a5949f19c90689556347c7c8a4f856ec78ca8d8dede5bf5dd3acebe4b5f` |
| `surfaces/course_context_view.py` | `e4528cf7e8b78a4dfeb512d183172b728a7b0a33bb577c8e3c2cb76edf0549d1` |
| `tests/product_gm_parity_source_impact_roundtrip.py` | `db3548b1e1ad29a387e75aa9529f07ad087badf605fd74bb0f84d245b0e93ea4` |

All checks exited 0:

| Command | Actual output or gate |
| --- | --- |
| `python3 tests/product_gm_parity_source_impact_roundtrip.py` | Native exact current reading/map/lesson links, restart, rights, missing IDs and read-only history pass |
| `python3 tests/course_context_journey_roundtrip.py` | Exact prerequisite/source return, restart, changed-source refusal and read-only GETs pass |
| `python3 tests/course_workbench_roundtrip.py` | Loopback navigation, proposal review, accept, undo, conflict, report-only pass |
| `python3 tests/course_guidance_journey_roundtrip.py` | Truthful history, pending/blind boundaries, read-only native entry, exact detour/reload/restart and retraction pass; expected damaged-evidence warnings |
| `git diff --check` scoped to released Python paths | No whitespace errors |

The new native gate makes a synthetic accepted reading successor and binding
successor, changes source bytes, GETs Sources, follows exact reading/map/lesson
links, repeats after daemon restart, and compares hashes of every durable file.
It separately verifies old reading evidence stays reported on its old revision
while the successor stays not reported. Native denied/unknown read rights and
missing source files expose inspectable assignment context without source bytes.
Projection tests cover unknown exact source ID, malformed manifest, missing
artifact, and a current reading pinned to a superseded binding.

These are source-level synthetic route gates, not human accessibility or
teaching-quality acceptance. No browser layout review, broad suite, package,
installation, commit, or push was performed. Large modules were sampled at
relevant symbols rather than read whole.

## Recovery

Undo only this delta by comparing each released module against its named
before-image and reverting the source-impact projection, exact-binding link
filter, superseded-reading filter and rendering changes. Remove the new test
and this report only if they have no later edits. Do not restore whole modules
from before-images: those images include inherited dirty work and later writers
may have changed the released files. All changes are local and reviewable.
