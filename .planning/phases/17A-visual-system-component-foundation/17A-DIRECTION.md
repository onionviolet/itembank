# 17A direction decision

- **Decided:** 2026-08-20 by Weibao
- **Closes:** the `checkpoint:decision` in 17A-02
- **Reviewed:** thirty-six combinations (3 looks by 3 navigation shapes by 4
  accents) in one self-contained prototype,
  `prototypes/17a/itembank-prototype.html`

## The decision

| Axis | Chosen | Alternatives kept |
|---|---|---|
| Look | `structured-studio` | `quiet-workbench`, `guided-canvas` |
| Navigation | `sidebar` | `tabs`, `bottom` |
| Accent | `indigo` (`#4a4ad4`) | `teal`, `plum`, `clay`, plus any hex |

**A default is a starting point, not a deletion.** Weibao: "we can keep all of
the options as something for the user to choose from." That is the standing
rule in `PLANNING-DIRECTIVES.md` section 1, so no direction stylesheet and no
navigation stylesheet is removed by this decision. Each remains one deletable
file, and `check_directions_are_deletable` still guards that.

## Contrast, measured not assumed

`theme.derive_theme("#4a4ad4")` was run before the choice was recorded:

| Mode | Accent | vs background | vs card |
|---|---|---|---|
| light | `#4a4ad4` | 5.95 | 6.52 |
| dark | `#7979df` | 4.98 | 4.54 |

The requirement is 4.5 for text pairings and 3.0 for focus pairings. Indigo
clears both in both modes and needed **no** contrast adjustment in light mode;
the dark accent is raised to `#7979df` by the shipped derivation, exactly as
designed.

## What this changes now, and what it does not

Changed in `surfaces/visual_fixture.py`: `DEFAULT_DIRECTION`, `DEFAULT_NAV`,
and `DEFAULT_ACCENT_ID`. These govern the prototype only.

**Not changed:** `theme.DEFAULT_ACCENT`, which is still the shipped teal
`#0e6e62` used by every real surface. Moving the shipped default to indigo is a
token-freeze action and belongs to 17A-04, not here, because it changes what
every existing surface renders and needs the accessibility QA pass that 17A-04
owns. Recorded so it is not lost.

## Open, deliberately

The `bottom` navigation shape hides the course selector because a thumb strip
has no room for it. If `bottom` is ever promoted from an option to the default
on small screens, the course switch needs another home. Not a blocker for the
chosen default.
