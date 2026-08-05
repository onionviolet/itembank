"""The one palette, shared by every surface that renders.

`study` used to declare its own blue accent and its own ok and bad, which made
two surfaces of one tool read as two products, and left the study page with no
dark-mode accent at all because its dark block never redefined one. Anything
that renders substitutes __THEME__ rather than restating colours, so a theme is
changed in one place.
"""


THEME_CSS = r""":root{
  --bg:#f3f5f4; --card:#fff; --ink:#171d1c; --mut:#5f6d6a; --line:#dfe5e3;
  --accent:#0e6e62; --accent-soft:#e3efec;
  --ok:#1b7a3d; --ok-bg:#e8f4ec; --bad:#b4272b; --bad-bg:#fbebeb; --warn:#b5760a;
  --chip:#eef2f1;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0e1413; --card:#161e1d; --ink:#e4ebe9; --mut:#8fa19d; --line:#26312f;
    --accent:#34b3a0; --accent-soft:#13302c;
    --ok:#4fbf74; --ok-bg:#11291b; --bad:#f0666a; --bad-bg:#2b1416; --warn:#e0a23a;
    --chip:#1d2726;
  }
}"""
"""The one palette, shared by every surface.

`study` used to declare its own blue accent and its own ok and bad, which made
two surfaces of one tool read as two products, and left the study page with no
dark-mode accent at all because its dark block never redefined one. Anything
that renders substitutes __THEME__ rather than restating colours, so a theme
is changed in one place.
"""
