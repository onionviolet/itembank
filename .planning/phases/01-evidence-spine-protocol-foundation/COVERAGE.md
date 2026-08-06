# API Coverage — Phase 1

No external API integration: this phase touches only local files (`_evidence/evidence.jsonl`,
`schemas/*.json`, bank markdown, `_attempts/*`, `daily_log.md`) through the Python standard
library, under PROJECT.md's "no cloud sync, no hosted gradebook, no telemetry" constraint.

**Detector result (deterministic, run at plan time):**

```
gsd-tools query check api-coverage-verify-pre .planning/phases/01-evidence-spine-protocol-foundation
{ "block": false, "passed": true, "coverage_present": false, "detected": false,
  "message": "api-coverage: no external-API integration detected; coverage matrix not required" }
```

The only network-adjacent code in the repository is the optional AnkiConnect *read* integration
(`ANKI_CONNECT_URL`, `surfaces/day.py`), which this phase does not touch, and the loopback HTTP
server (`server.py`), which is a local transport rather than an external API.

No capability matrix is produced because there is no external capability surface to subtract from.
