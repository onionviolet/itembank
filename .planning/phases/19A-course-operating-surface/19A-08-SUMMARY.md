# 19A-08 Summary: package recovery closure

## Why this summary exists

A measured fact contradicted the plan's inherited package surface. The 17B
course could not export because manifest validation rejected its registered
scope object as a second course-kind entry. This summary records that repair
and the completed recovery gate.

## Result

The 19A package family now has acceptance evidence through its existing route
and CLI twins. The exercised 17B package restored every registered object and
every evidence event. Every F-LOSS-1 through F-LOSS-5 exclusion appeared in
the package response and plain loss report.

The surface implementation itself was already present in the 19A spine before
this packet. This packet did not duplicate it. It added the realistic recovery
gate and repaired one validator regression exposed by that gate.

## Repair

`validate_manifest` incorrectly required exactly one entry whose kind was
`course`. The frozen 17B course legitimately carries two such entries. One is
the course sidecar and one is `scope.md`. That check made the existing CLI
export fail before a package could be produced.

The validator now requires exactly one `course` entry whose object id matches
`course_object_id`. Other registered course-kind objects remain valid. Export
capture also locates the sidecar by that identity instead of assuming the first
course-kind entry is the sidecar.

## Recovery result

- The manifest verified 7 of 7 payload entries.
- The fresh destination restored 7 of 7 registered objects.
- It restored 47 of 47 evidence events through the existing evidence writer.
- It recorded no restore-time loss.
- The destination journal contains restore entries only.
- The restored bank reports `media.declared_present_missing` for the disclosed
  unregistered diagram.

F-LOSS-1 through F-LOSS-5 remain preserved as findings. Their absence from the
payload is not presented as lossless recovery. Each exclusion is classified in
the plan and printed by both the structured and plain loss surfaces.

## Changed files

- `course_package.py`
- `tests/course_ops_roundtrip.py`
- `19A-08-PLAN.md`
- `19A-08-SUMMARY.md`
- `19A-08-VERIFICATION.md`
- `evidence/19A-08-manifest.json`
- `evidence/19A-08-loss-report.md`

No 19A-09 work was started. Large implementation files were inspected
symbol-first.
