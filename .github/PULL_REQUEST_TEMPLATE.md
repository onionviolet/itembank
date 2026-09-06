## Problem

What was wrong or missing?

## Change

What does this pull request change, and what is intentionally out of scope?

## Authority and data impact

- [ ] Parsing still goes through `model.py`.
- [ ] Settled scoring and keyed disclosure still go through `runtime.py`.
- [ ] No real banks, learner evidence, secrets, or machine-specific paths are included.
- [ ] Rights, provenance, and remote egress are unchanged or explained below.

## Verification

List every command actually run and its result.

```text
command: result
```

- [ ] New or changed behavior has a focused test.
- [ ] The appropriate preflight command passed.
- [ ] The working tree stayed clean after tests.

## Review notes

Link the issue, requirement, or plan. Name any large file that was sampled rather than read completely. If an agent authored the change, identify the agent and the files it inspected.

## Recovery

How can this change be reverted or recovered if it fails?
