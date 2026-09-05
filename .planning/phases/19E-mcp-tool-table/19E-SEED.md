# 19E seed: the MCP tool table

Not a context. A starting note. This phase discharges backlog Phase 999.3.

**Goal.** The stdio MCP server of 999.3, generated from `API_ROUTES` as its own
success criterion 1 already specifies, now that the table contains course
operations.

**Depends on** 19A. This is the sequencing finding of the gap pass: 999.3 was
never blocked on MCP work, it was blocked on there being routes worth exposing.
Built before 19A it would expose fifteen assessment tools and no course tools.

**Gate.** 999.3's eight success criteria, unchanged, plus one addition: an
agent client builds a course through the tool table alone. That is the
acceptance test for 19A as much as for this phase. If the generated tools can
build a course, the routes are right.

**Design basis.** MCP specification revision 2026-07-28, current as of
2026-09-05. `scripts/ocr_mcp.py` is existing in-repo precedent for the
transport.

**Before planning:** write `19E-CONTEXT.md` and re-read 999.3's eight criteria
in `ROADMAP.md` rather than restating them from here.
