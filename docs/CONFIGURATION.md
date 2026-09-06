<!-- generated-by: gsd-doc-writer -->
# Configuration

## Runtime configuration

The core CLI has no required account, environment file, or server configuration. Commands take bank, course, session, and output paths explicitly. Generated sessions and evidence remain on the local machine.

## Optional dependencies

The core assessment loop uses the Python standard library. `requirements.txt` contains pinned dependencies for optional import and audio features. `requirements-build.txt` contains build-only tooling. Install only the dependency group needed for the work you are doing.

The JavaScript editor tests use the lockfile in `tests/js/`:

```bash
npm ci --prefix tests/js
```

## Machine-local files

Copy `reasonix.toml.example` to `reasonix.toml` only when local Reasonix integration is needed. `reasonix.toml` and `.reasonix/` are intentionally ignored and must not be committed.

Learner data and operation journals are also local. The ignored paths include `_attempts/`, `_evidence/`, `_journal/`, and session JSON files.

## Agent configuration

All agents must read `AGENTS.md` before consequential work. Product-direction work must also read `.planning/USER-VISION.md`, `.planning/SOURCE-TO-COURSE.md`, and `.planning/AGENT-WORKFLOW.md`.

Project skills are mirrored under `.agents/skills/` and `.claude/skills/`. Keep the two trees byte-identical when editing a skill.

## Security and privacy defaults

- Never place real question banks or learner evidence in the repository.
- Treat unknown rights as restrictive.
- Declare remote egress before sending source content to a hosted model.
- Keep secrets and machine-specific paths out of committed configuration and documentation.
