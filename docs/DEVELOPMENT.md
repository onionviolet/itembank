<!-- generated-by: gsd-doc-writer -->
# Development

## Local setup

1. Clone the repository and create a topic branch from current `main`.
2. Read `AGENTS.md` and the planning contracts it names for your area.
3. Run `python scripts/preflight.py --quick` before editing.
4. Make the smallest change that satisfies the issue or plan.
5. Run targeted tests, then the appropriate preflight gate before opening a pull request.

The core runtime needs no package installation. Install pinned optional dependencies only when the changed feature requires them.

## Build and development commands

| Command | Description |
|---|---|
| `python itembank.py spec` | Print the bank format contract |
| `python itembank.py lint fixtures/sample_bank.md` | Exercise bank validation |
| `python itembank.py build fixtures/sample_bank.md /tmp/out.html` | Build an offline sample quiz |
| `python scripts/preflight.py --quick` | Run fast local gates |
| `python scripts/preflight.py` | Run all portable CI gates |
| `npm ci --prefix tests/js` | Reproduce the pinned JS test dependencies |

## Code style

Follow nearby code and keep the project standard-library-first. Search by symbol and read narrow implementation windows. Do not duplicate parsing or scoring logic. Repository-authored prose, comments, fixtures, lessons, and questions must not use em dash characters.

Use `apply_patch` or an equivalent reviewable editing mechanism. Preserve unrelated working-tree changes. Never commit real question banks, learner evidence, secrets, or machine-specific paths.

## Branch conventions

Use a short topic branch. Agent-created branches use the `codex/` prefix by default. Humans may use `feat/`, `fix/`, `docs/`, or another clear issue-oriented prefix. Do not develop directly on `main`.

## Pull request process

- Keep one coherent change per pull request.
- Explain the actual problem, the chosen solution, and the evidence that verifies it.
- Link the issue, plan, or requirement when one exists.
- Complete every applicable item in the pull request template.
- Wait for CI and review before merge.

## Commit discipline

Commit only files owned by the change. Never use a broad stage command in a shared or dirty worktree. GSD phase work uses exactly one atomic commit per plan with the repository’s documented commit-message shape.
