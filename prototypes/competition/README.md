# Selective absorption prototypes

These are isolated experiments, not shipped Itembank capabilities.

Run `python3 prototypes/competition/test_grounding.py` for source-grounding checks. Run `python3 prototypes/competition/server.py` and open `http://127.0.0.1:8769` for the synthetic-source context preview. It verifies selected text and prepares context without a model call or accepted write.

The `generation/` directory contains pinned OpenMAIC outline and teaching-scene generation trials. See its README for deterministic tests and the optional local-model command. It does not yet produce a validated portable Itembank lesson. Run `python3 prototypes/competition/test_server.py` for the HTTP boundary checks.

See `THIRD_PARTY_NOTICES.md` for the DeepTutor adaptation and license. Research, trial limits, dispositions, and production acceptance gates are in `.planning/research/competition-2026-09-08/ABSORPTION.md`.
