# 17B-04 evidence: egress and rights-unknown checks (G11)

Wave 4, Task 2 of `17B-04-PLAN.md`, run 2026-09-05. Gate G11 asks three
things: egress capture equals disclosed manifests, rights-unknown refuses
unsafe operations, and diagnostics are redacted. This file records all
three.

Working directory for every command below is the repository root
`/Users/weiwei/Documents/Dev/itembank`. `$SP` is this session's scratchpad,
`/private/tmp/claude-501/-Users-weiwei-Documents-Dev-itembank/102385dc-d487-4f91-b332-915ed41a8e35/scratchpad`.

## 1. Egress determination (17B-CONTEXT D-09)

G11 egress: not applicable, the tracer run made no hosted-model call (17B-CONTEXT D-09).

### How that was verified rather than assumed

The wave 2 and wave 3 evidence files each carry their own egress record,
but a claim in an evidence file is not itself proof. Four independent
checks were run against the evidence and the code:

1. **No captured payload or disclosed manifest exists.** The whole point
   of the byte comparison is a pair of captures taken at call time
   (17B-02 Task 1 step 4, 17B-03 Task 1). Directory listing of
   `.planning/phases/17B-production-vertical-tracer/evidence/`:

   ```
   17B-02-binding.md      17B-03-learner-pass.md    17B-03-rollup-dim.html
   17B-02-coverage.md     17B-03-legacy-audit.md    17B-03-rollup-map.html
   17B-02-faults.md       17B-03-rollup-choice.md   17B-03-rollup-tuples.json
   ```

   There is no captured outbound payload and no disclosed manifest to
   compare. Both prior waves state the reason: no call was made.

2. **No non-loopback address appears anywhere in the recorded evidence.**

   ```
   grep -rn "https://\|http://" .planning/phases/17B-production-vertical-tracer/evidence/*.md \
     | grep -v "127.0.0.1\|localhost"
   ```

   returns nothing. Every URL in the wave 2 and wave 3 transcripts, the
   driven browser's network log included, is loopback.

3. **The `Get optional guidance` control was left unactivated, checked in
   the transcript rather than taken on trust.** The accessibility tree at
   `evidence/17B-03-learner-pass.md:301` shows the control present:

   ```
   region "Optional generated guidance"
     button "Get optional guidance"
   ```

   The stage 5 sequence that follows it drives the wrong answer, the
   `Open the next hint` button, the tier ladder, and submit, and never
   dispatches this button. The file's own egress record at line 723
   states the same. The control is present and unpressed, which is the
   condition D-09 describes.

4. **The default forbids the call in the first place.**

   ```
   python3 -c "from surfaces import settings; print(settings.NETWORK_EGRESS_SETTINGS_DEFAULTS)"
   {'hosted_operations': 'off', 'last_disclosure': ''}
   ```

   `schemas/settings.schema.json` carries the same default
   (`"hosted_operations": "off"`). A hosted call during the tracer would
   have required changing that setting, and no wave records changing it.

So the not-applicable path is the honest finding, not a convenience. The
byte comparison D-09 asks for stays owed to the first tracer run that
actually makes a hosted call, and the rights-unknown refusal check below
runs anyway, exactly as D-09 requires.

## 2. Rights-unknown refusal check

### Fixture

The check needs a source whose rights state is unknown. The repository
fixture `course_fixture_17b/` already carries two sources with
`remote_process`, `package`, `export`, and `share` all `unknown`, but with
`transform` granted, so it cannot exercise the transform gate. A third
source with all seven rights unknown was therefore added inside the
fixture.

The fixture was copied to `$SP/g11/fixture` first and the new source was
created in the copy, so the repository fixture keeps the exact bytes and
the exact journal that gates G1, G2, G3, and the wave 4 restore drill read
from. `git status --porcelain course_fixture_17b/` is empty after this
task.

```
cp -R course_fixture_17b "$SP/g11/fixture"
cat > "$SP/g11/fixture/sources/unrightsed_bog_transect.md" <<'EOF'
# Bog transect notes, rights unknown

SECRET_BODY_MARKER_A1B2C3: station four recorded a water table depth of
eighteen centimetres under the banking peat, with a lantern moss cover of
sixty percent.
EOF
```

The body carries a unique marker string on purpose: section 3's redaction
check needs a token that can only have come from the source body.

### Check 2a: the frozen 14A transform gate refuses the pull

`identity.RIGHTS_OPERATIONS` and `identity.RIGHTS_STATES` are frozen by
14A-FREEZE. The shipped operation that consumes a source's bytes into a new
owned artifact is `source import`, whose CLI is the same
`source_adapters.import_source` the daemon route reaches. Omitting
`--grant` links the file with `identity.rights_default()`, which is all
seven rights unknown.

Command:

```
python3 itembank.py source import --base "$SP/g11/fixture" \
  --file sources/unrightsed_bog_transect.md --adapter markdown
```

Output, verbatim, and the exit status:

```
journal.rights_unknown: the transform right for source fcbcadcb4ec740b9 is unknown, so import is refused by name. Next safe action: record a rights grant for this source, or link the file where it lives instead of importing it.
=== EXIT 1 ===
```

The refusal `code` is `journal.rights_unknown`, which 14A-FREEZE names as
the stable machine-readable part (the message string is copy, not
contract). The command refused; it did not proceed.

The refusal is journaled and it left no mutation behind. Last three
journal entries, key fields only:

```
{"entry_id": "78dc120c4dcb4485befa7286a8a9fd66", "operation": "link",   "state": "prepared", "resolves_entry": null, "object_id": "fcbcadcb4ec740b9", "kind": "source", "path": "sources/unrightsed_bog_transect.md", "code": null, "message": null, "before_image": null}
{"entry_id": "48f3dddba52d4b1a8c872cf78bc30a59", "operation": "link",   "state": "applied",  "resolves_entry": "78dc120c4dcb4485befa7286a8a9fd66", "object_id": "fcbcadcb4ec740b9", "kind": "source", "path": "sources/unrightsed_bog_transect.md", "code": null, "message": null, "before_image": null}
{"entry_id": "15ee5c156a3c4c79a67d4659174b23d4", "operation": "import", "state": "refused",  "resolves_entry": null, "object_id": "f14738ccac7d442f", "kind": "source", "path": "sources/unrightsed_bog_transect.md.md", "code": "journal.rights_unknown", "message": "the transform right for source fcbcadcb4ec740b9 is unknown, so import is refused by name. Next safe action: record a rights grant for this source, or link the file where it lives instead of importing it.", "before_image": null}
```

Post-conditions checked:

```
ls "$SP/g11/fixture/sources/unrightsed_bog_transect.md.md"
  -> No such file or directory        (the derived artifact was never written)
f14738ccac7d442f in registry: False   (the refused import minted no accepted row)
fcbcadcb4ec740b9 in registry: True    (the link stands, as linking is not gated)
rights on the linked raw source:
  {"export": "unknown", "package": "unknown", "quote": "unknown", "read": "unknown",
   "remote_process": "unknown", "share": "unknown", "transform": "unknown"}
```

Rerunning the same command a second time refuses identically with exit 1,
so the refusal is stable and does not decay into a grant.

Observation, recorded rather than filed as a defect: the refused `import`
entry carries `resolves_entry: null` because the rights gate fires before
the `prepared` entry is appended (`journal.py:468` runs ahead of
`journal.py:533`). The 14A-FREEZE two-line protocol governs durable writes
that were prepared; this refusal prevents the write from ever being
prepared, and the refusal is still journaled by name. Nothing in the frozen
contract is broken, but the asymmetry is worth naming so a later reader does
not mistake it for a missing pair.

### Check 2b: the export and package gate refuses to carry the bytes

`export` and `package` are separate grants from `transform` (14A-FREEZE:
the seven rights operation names, and "one never implies another"). The
shipped operation that hands bytes to another machine is
`course_package.export_package`, gated on `PACKAGE_RIGHT = "package"` via
`identity.rights_granted(rights, "package")` being exactly True, so unknown
and denied both stay restrictive.

Command (module call over the same fixture copy, package written to the
scratchpad):

```
python3 -c "import course_package; course_package.export_package(base, base, dest)"
```

Manifest entries actually carried:

```
  course ba070378d35d44e7 course-graph.md
```

Loss report, verbatim from `$SP/g11/package/LOSS-REPORT.md`:

```
# Package loss report

| category | target | reason |
|---|---|---|
| machine-local | settings | not included by design; model backend configuration, update policy, and local paths belong to the machine, not to the course |
| rights-restricted | 1672ba231fd446ee | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
| rights-restricted | 36157b3e10cb46e5 | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
| rights-restricted | 5c5bc6b17baa44c6 | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
| rights-restricted | 8bd25c20ceaa4e20 | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
| rights-restricted | 95abc1ccd3e241f9 | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
| rights-restricted | d035bddef2d84eff | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
| rights-restricted | fcbcadcb4ec740b9 | the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged |
```

Payload tree:

```
  payload/ba070378d35d44e7.md
```

The unknown-rights source `fcbcadcb4ec740b9` is named and its bytes are
not carried. Neither are the fixture's other six objects, all of which
record `package` as unknown. Only the course sidecar leaves, which
`build_manifest` documents as deliberately not rights-gated (a package
without it would carry no course at all). The refusal here is a named loss
rather than a raise, and the effect G11 asks about is the same: unknown
rights kept the bytes at home, and the omission is reported rather than
silent.

This result is load-bearing for the wave 4 restore drill (G10): with the
fixture's recorded rights as they stand, an export carries one file, so
the drill's loss report will be long. That is a fixture rights-recording
question for Task 1, not a G11 failure.

### On `remote_process`

`remote_process` is one of the seven frozen rights names and is recorded
on every source, but no shipped operation consumes it today:

```
grep -rn "remote_process" --include="*.py" . | grep -v tests/ | grep -v fixtures/
identity.py:49:RIGHTS_OPERATIONS = ("read", "quote", "transform", "remote_process",
```

There is no hosted-processing operation to gate, which is the same fact
section 1 records from the other side (`hosted_operations` defaults to
`off` and the tracer made no hosted call). Recorded as an observation and
a watch item for whichever phase first ships a hosted operation: that
phase owes the gate, not 17B. Not a D-06 defect, because no shipped
operation currently bypasses the grant.

## 3. Redaction check on the refusal diagnostic

The refusal diagnostic, exact bytes as printed:

```
'journal.rights_unknown: the transform right for source fcbcadcb4ec740b9 is unknown, so import is refused by name. Next safe action: record a rights grant for this source, or link the file where it lives instead of importing it.\n'
```

Every distinctive string from the source body was tested against it:

```
  SECRET_BODY_MARKER_A1B2C3    in source body: True   in refusal diagnostic: False
  station four                 in source body: True   in refusal diagnostic: False
  eighteen centimetres         in source body: True   in refusal diagnostic: False
  banking peat                 in source body: True   in refusal diagnostic: False
  lantern moss cover           in source body: True   in refusal diagnostic: False
  sixty percent                in source body: True   in refusal diagnostic: False
  Bog transect notes           in source body: True   in refusal diagnostic: False
```

The same seven strings against the five journaled `refused` entries in the
fixture copy:

```
  SECRET_BODY_MARKER_A1B2C3    in journaled refusal: False
  station four                 in journaled refusal: False
  eighteen centimetres         in journaled refusal: False
  banking peat                 in journaled refusal: False
  lantern moss cover           in journaled refusal: False
  sixty percent                in journaled refusal: False
  Bog transect notes           in journaled refusal: False
```

A stricter check than a needle list: every word of six or more characters
in the source body, intersected with every such word in the diagnostic.

```
body words of 6+ characters also present in the diagnostic:
  ['rights', 'unknown']
```

`rights` and `unknown` are the rights vocabulary, not source content. No
word of the source body reaches the diagnostic. The diagnostic identifies
the object by its 16-hex id, names the right and its state, and gives the
next safe action, which is what a redacted refusal should say.

The same check over the export path:

```
  SECRET_BODY_MARKER_A1B2C3    in loss report: False   in manifest: False
  station four                 in loss report: False   in manifest: False
  eighteen centimetres         in loss report: False   in manifest: False
  banking peat                 in loss report: False   in manifest: False
  Bog transect                 in loss report: False   in manifest: False
  package payload files: ['ba070378d35d44e7.md']
  source bytes anywhere under package/: False
```

The loss report names targets by object id only.

## 4. G11 determination

| G11 clause | result |
|---|---|
| egress capture equals disclosed manifests | not applicable, no hosted-model call was made, verified four ways in section 1 (17B-CONTEXT D-09) |
| rights-unknown refuses unsafe operations | pass: `journal.rights_unknown`, exit 1, no derived artifact and no registry row (2a); export carries no unknown-rights bytes and names every omission (2b) |
| diagnostics are redacted | pass: no source-body word reaches the diagnostic, the journaled refusal, the loss report, or the manifest (section 3) |

State recorded on the G11 row: `pass`. No D-06 defect is filed by this
task. Two observations are recorded above (the unpaired refused entry, and
`remote_process` having no consuming operation), neither of which
contradicts a frozen contract.
