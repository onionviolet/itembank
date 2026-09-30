# Visual comparison

Both directions use identical fictional course-journey content and controls.
Quiet reading uses a single measured column, open section rhythm and minimal
panel grounds. Expressive workshop uses a wider activity canvas, an accent
entry panel and separate source/private-note columns. Workshop is the reversible
working direction because it makes concurrent reading and note-taking visible;
this is a design rationale, not evidence of user preference.

Generate with `python3 tests/ui_overhaul_visual_roundtrip.py --previews`.
Serve this directory locally and inspect `quiet-light.html` and
`workshop-light.html`; dark and custom-accent variants exercise the same content.
These are presentation comparisons, not scored sittings or durable course files.
The browser checker is `verify.mjs`, with optional `ITEMBANK_PLAYWRIGHT_MODULE`
and `ITEMBANK_CHROMIUM` environment paths. It owns and stops its static server.
