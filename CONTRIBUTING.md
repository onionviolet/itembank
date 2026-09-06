<!-- generated-by: gsd-doc-writer -->
# Contributing to itembank

Itembank accepts focused contributions from humans and coding agents. The same correctness, privacy, evidence, and review standards apply to both.

## Before you start

1. Ask for or choose an issue with a bounded outcome.
2. Read `AGENTS.md` and the documents it identifies as binding for the affected area.
3. Search for existing implementations, artifacts, and active plans before creating replacements.
4. Create a topic branch from current `main`.
5. Run `python scripts/preflight.py --quick` to establish a clean baseline.

## Non-negotiable boundaries

- `model.py` is the one bank parser.
- `runtime.py` is the one settled scoring and assessment authority.
- Short prose answers remain pending until human review or another explicitly authorized settlement step.
- Real question banks, learner evidence, and operation journals never enter the repository.
- Accepted files are canonical. Generated indexes, previews, and caches are disposable views.

Read the full rules in `AGENTS.md`. If a proposed change conflicts with those rules, stop and raise the conflict in the issue or pull request.

## Human contribution standard

Keep each change small enough to review. State what was wrong before describing the fix. Add or update a test for behavior changes. Preserve compatibility unless the issue explicitly authorizes a breaking change.

Do not mix unrelated cleanup into a feature or fix. Do not rewrite documentation or learning artifacts for style alone. Preserve provenance, stable identity, citations, and assessment meaning.

## Agent contribution standard

An agent must identify itself in the pull request description and name the exact files and tests it inspected. It must also state which large files it sampled instead of reading completely.

Agents must preserve user changes, respect declared read and write roots, and avoid external writes that were not requested. A claim is not verified until the named command or check has actually run. Agent-generated content must remain reviewable and must not become accepted truth without the repository’s configured review step.

Do not add an AI co-author trailer to commits.

## Change workflow

1. Rebase or update from `main` before starting.
2. Implement one coherent change.
3. Run the narrowest relevant test during development.
4. Run `python scripts/preflight.py --quick` for small documentation-only work or `python scripts/preflight.py` for code and contract changes.
5. Commit only the files that belong to the change.
6. Open a pull request and complete the template.

GSD plan execution has an additional rule: exactly one atomic commit per plan after that plan’s verification passes.

## Review standard

A reviewer checks five things:

1. The change solves the stated problem without widening scope.
2. Parser, scorer, privacy, rights, and disclosure boundaries remain intact.
3. Tests exercise the changed behavior and were actually run.
4. Documentation and schemas match the implementation.
5. The change has a clear recovery or revert path.

Authors must resolve review findings or record why they do not apply. Merge only after required CI checks pass.

## Commit messages

Use an imperative summary that describes the outcome. GSD plan commits use `<type>(<plan>): <summary>`, such as `feat(10-01): add objective coverage report`. Do not add `Co-Authored-By` trailers.

## Security and private data

Do not include credentials, tokens, personal paths, learner data, copyrighted source material without rights, or real assessment banks. Report security-sensitive problems privately to the repository owner instead of opening a public issue.

## Licensing

By contributing, you agree that your contribution is provided under the repository’s existing license.
