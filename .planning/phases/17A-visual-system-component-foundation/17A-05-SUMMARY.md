# 17A-05 summary

Executed 2026-08-24. `PLANNING-DIRECTIVES.md` B1 makes a summary exceptional
and this plan did not ask for one, so this file exists for exactly one reason:
a measured fact contradicted the plan.

## The contradiction

The plan treats `tests/config_roundtrip.py`'s enum pin as a red gate: change
the schema, watch `test_theme_schema_additive_accent` fail, then make it pass.
**That function was defined and never called from `main()`.** It guarded
nothing, and had the plan been executed as written the gate would have gone
green without ever having been red.

It is wired into `main()` now, second in line. Only after that did it fail on
the missing `oled` value, which is what the plan expected to see.

This is worth recording beyond this plan: a pin that is never called is
indistinguishable from a pin that passes, and the same failure mode is what
let 17A-05 look built when it was not (see `STATE.md`, 2026-08-23). Both are
the same mistake, which is trusting a name rather than an artifact.

## What shipped

`oled` is one additive theme enum value. `system`, `light` and `dark` are
byte-identical to before, verified by comparing `theme_css` output against
HEAD rather than by inspection.

The token set is derived, not picked. `BASE_TOKENS["oled"]` takes dark's
per-surface offsets above its background and translates them down so the
ground is `#000000`: card `#080a0a`, chip `#0f1313`, line `#181d1c`. `ink` and
`mut` are dark's verbatim, because a darker ground only raises their measured
ratios. `SEMANTIC_TOKENS["oled"]` is dark's set verbatim for the same reason.

That reasoning is an argument, and an argument is not evidence, so the
argument is not what the suite trusts: `stylesheet_roundtrip` invariant 4 now
iterates `("light", "dark", "oled")` and re-measures every pairing through
`theme.contrast_ratio` on every run. The plan named that hardcoded tuple as
the one key link and it was right. Without that edit the new tokens would have
shipped unmeasured.

`derive_theme` runs oled through the same accent correction and soft blend the
other modes use, so a custom accent is corrected against true black rather
than inheriting dark's correction. `theme_css` returns the oled root block
with no dark media override, because a forced mode is forced.

## Measured, at the default accent

| Pairing | Ratio | Floor |
|---|---|---|
| accent `#118879` vs `#000000` | 4.82 | 4.5 |
| ink vs bg | 17.36 | 4.5 |
| mut vs bg | 7.75 | 4.5 |
| edge vs card / bg / chip | 4.49 / 4.24 / 4.00 | 3.0 |

## Verification

`stylesheet_roundtrip`, `config_roundtrip`, `presentation_roundtrip` and
`daemon_roundtrip` all exit 0. `python3 itembank.py guard .` reports zero
offending files. `itembank config set theme oled` was exercised live and
accepted, and the emitted document carries `--bg:#000000` with no media
override.

## Provenance

The implementation was executed by Ox Alpha (`stealth/ox-alpha` via dsh) in
the `wt/17A-05` worktree. Its sandbox could not write to git, because the
worktree's `.git` file points into the main checkout outside its writable
root, so it finished the work and stopped rather than stacking plan 03 on an
uncommitted tree. That was the right call. The orchestrating session reviewed
the diff, re-ran every suite independently, exercised the CLI path, and
committed it as `cc0347d`.

**Operational note for the next unattended run:** `scripts/ox_overnight.sh`
with `IB_DIR` pointed at a worktree cannot commit. Either run Ox Alpha in the
main checkout (queued, never concurrent), or create the worktree with its git
directory inside the sandbox's writable root.
