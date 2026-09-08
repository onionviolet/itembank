"""The quiz page itself: markup, style and behaviour, as one asset.

Kept apart from the code that fills it in because it is a different kind of
thing to read. `quiz.py` decides what an item may contain; this decides how it
looks and what clicking it does.

The page ships two mutually exclusive clients. `OFFLINE_JS` is the static
`build` compatibility client: it receives the full Python-produced item array
with canonical keys and compares against them, because a file:// page has no
process behind it. `SERVED_JS` is the daemon-served client (SURF-02): it
receives only bootstrap metadata, starts the sitting through POST /api/start,
submits through POST /api/submit, and renders only the server-issued verdict
and explanation. The served page never contains the offline canonicalization
implementation, and the static page never references the API.

Both clients share the Phase 4 question hierarchy (D-01 through D-03): one
sticky context line (bank/lesson context, objective, item N of M, session
mode), one native details disclosure for secondary metadata, a single
dominant stem h1, native response controls, a reserved feedback region, and
one primary next action per state.

THE STYLE BLOCK'S ORDER IS LOAD-BEARING AND IS LOCKED (14-UI-SPEC §3, D-B):
`__THEME__` (the generated palette) then `__SHARED__`
(`presentation.SHARED_CSS`, the token layer that carries the four vendored
`@font-face` rules and the spacing/radius/voice/measure `:root` block) then
this page's own rules, which therefore still win on equal specificity.

Until this file gained `__SHARED__` it substituted `__THEME__` and nothing
else, which is the whole of DEFECT D-B: the four `@font-face` rules live in
the shared token layer, so the sat quiz had never once rendered in either
vendored face and could not. The 2026-08-12 font-404 fix repaired the reader
and never reached here, because the quiz was not joined to the layer it
fixed. The families themselves are deliberately not named anywhere in this
docstring: `presentation.py` is the only file in `surfaces/` permitted to
spell a vendored family, and that rule is asserted over source text, prose
included (`tests/presentation_roundtrip.py` Test 2).
"""

import html


RESPONSE_FORMAT_LABELS = {
    "mc": "Single choice", "multi": "Multiple choice",
    "table": "Table response", "build": "Build response",
    "dnd": "Ordering or matching", "short": "Short response",
    "visual": "Visual interaction", "check": "Code check",
}
RESPONSE_FORMAT_INSTRUCTIONS = {
    "mc": "Choose one option.",
    "multi": "Choose the requested number of options.",
    "table": "Choose one category for every row.",
    "build": "Select every step in the order it should happen.",
    "dnd": "Match every row to a category. Dragging is not required.",
    "short": "Write your response. It stays pending until a marker reviews it.",
    "visual": "Use the visual or its adjacent keyboard controls, then submit.",
    "check": "Edit the source, then run the check. The runtime records the verdict.",
}


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
__THEME__
__SHARED__
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.5 var(--font-chrome)}
.wrap{max-width:800px;margin:0 auto;padding:22px 18px 96px}
/* The one sticky orientation line (D-01): bank/lesson context, objective,
   item N of M, session mode -- and nothing else persistent. */
.context-line{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;
  gap:4px 18px;align-items:center;background:var(--bg);padding:8px 0 10px;
  border-bottom:1px solid var(--line);margin-bottom:14px;font-size:12px;
  color:var(--mut)}
.context-line .objective{flex:1 1 220px;min-width:0;overflow-wrap:anywhere}
.context-line .lesson{margin-left:auto}
/* The way back, when the serving surface has one. Underlined rather than
   coloured, so it reads as a link at any contrast setting and does not
   depend on the accent to be recognisable. */
.context-line .cx-home{color:inherit;text-decoration:underline;
  text-underline-offset:2px}
.context-line .cx-home:hover{color:var(--accent)}
.context-line a.lesson{color:var(--accent);text-decoration:none;font-weight:600}
.context-line a.lesson:hover,.context-line a.lesson:focus-visible{
  text-decoration:underline;outline:2px solid var(--accent);outline-offset:2px}
/* One native disclosure owns all secondary metadata (D-01). */
.session-details{margin:0 0 14px;font-size:12px;color:var(--mut)}
.session-details summary{cursor:pointer;padding:4px 0;font-size:16px;
  color:var(--mut);font-family:var(--font-chrome)}
.session-details a{font-size:16px;font-family:var(--font-chrome)}
.detail-body{margin-top:8px;display:flex;flex-wrap:wrap;gap:7px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:18px 18px 16px;margin-bottom:14px;
  scroll-margin-top:calc(var(--sticky-h,0px) + var(--space-2))}
.chip{font-size:12px;letter-spacing:.08em;text-transform:uppercase;
  background:var(--chip);color:var(--mut);padding:3px 8px;border-radius:5px;
  font-family:var(--font-ledger)}
.chip.type{background:var(--accent-soft);color:var(--accent)}
.chip.aon{background:var(--bad-bg);color:var(--bad)}
.chip.lesson{background:var(--accent-soft);color:var(--accent);
  text-decoration:none;display:inline-block}
/* The active stem is the page's single dominant h1 (D-02). */
h1.stem{font-size:32px;font-weight:600;line-height:1.2;margin:0 0 14px;
  font-family:var(--font-paper);
  text-wrap:pretty}
/* Response controls: native inputs with a 44px target (D-03). */
.choices{display:flex;flex-direction:column;gap:7px;border:0;padding:0;
  margin:0 0 6px}
.choices legend{font-size:12px;color:var(--mut);margin-bottom:6px;
  font-family:var(--font-chrome)}
.choice{display:flex;gap:10px;align-items:center;min-height:44px;width:100%;
  text-align:left;background:var(--card);border:1px solid var(--edge);
  border-radius:9px;padding:10px 12px;font:inherit;color:inherit;cursor:pointer;
  transition:.12s}
.choice:hover:not(:disabled){border-color:var(--accent)}
.choice:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}
.choice input{width:20px;height:20px;flex:0 0 auto;accent-color:var(--accent)}
.choice input:disabled{cursor:default}
.choice .k{flex:0 0 auto;font-family:var(--font-ledger);
  font-size:16px;color:var(--mut);min-width:1.2em}
.choice .ot{flex:1 1 auto;min-width:0;font-family:var(--font-paper)}
.choice .rat{display:block;margin-top:6px;font-size:16px;line-height:1.5;
  font-family:var(--font-paper);
  color:var(--mut)}
.choice.right{background:var(--ok-bg);border-color:var(--ok)}
.choice.right .rat{color:var(--ok)}
.choice.wrong{background:var(--bad-bg);border-color:var(--bad)}
.choice.wrong .rat{color:var(--bad)}
.choice:has(input:checked){border-color:var(--accent);background:var(--accent-soft)}
.choice:has(input:checked).right{border-color:var(--ok);background:var(--ok-bg)}
.choice:has(input:checked).wrong{border-color:var(--bad);background:var(--bad-bg)}
.opts{display:flex;flex-direction:column;gap:7px}
.opt{display:flex;gap:10px;align-items:center;min-height:44px;width:100%;
  text-align:left;background:var(--card);border:1px solid var(--edge);
  border-radius:9px;padding:10px 12px;font:inherit;color:inherit;cursor:pointer;
  transition:.12s}
.opt:hover:not(:disabled){border-color:var(--accent)}
.opt[aria-pressed="true"]{border-color:var(--accent);background:var(--accent-soft)}
.opt .k{flex:0 0 auto;font-family:var(--font-ledger);
  font-size:16px;color:var(--mut);min-width:1.2em}
.opt .ot{flex:1 1 auto;min-width:0;font-family:var(--font-paper)}
.opt .rat{display:block;margin-top:6px;font-size:16px;line-height:1.5;
  color:var(--mut);font-family:var(--font-paper)}
.opt.right .rat{color:var(--ok)}
.opt.wrong .rat{color:var(--bad)}
.opt.right{border-color:var(--ok);background:var(--ok-bg)}
.opt.wrong{border-color:var(--bad);background:var(--bad-bg)}
.opt:disabled{cursor:default}
.rowline{display:flex;gap:10px;align-items:center;flex-wrap:wrap;
  padding:9px 0;border-bottom:1px solid var(--line)}
.rowline:last-of-type{border-bottom:0}
.rowtext{flex:1 1 240px;min-width:0;font-family:var(--font-paper)}
.rowline select{flex:1 1 12rem;min-width:0;max-width:100%;min-height:44px;
  font:inherit;font-size:16px;padding:8px 12px;border:1px solid var(--edge);
  border-radius:8px;background:var(--card);color:inherit}
.response-body{min-width:0;max-width:100%;overflow-wrap:anywhere}
.response-table,.response-dnd,.response-visual,.response-check{
  max-width:100%;overflow-x:auto;overscroll-behavior-inline:contain}
.seg{display:flex;gap:5px;flex-wrap:wrap}
.seg button{font:inherit;font-size:16px;padding:8px 12px;min-height:44px;
  font-family:var(--font-chrome);border-radius:7px;border:1px solid var(--edge);background:var(--card);
  color:inherit;cursor:pointer}
.seg button[aria-pressed="true"]{border-color:var(--accent);
  background:var(--accent-soft);color:var(--accent)}
.seg button.right{border-color:var(--ok);background:var(--ok-bg);color:var(--ok)}
.seg button.wrong{border-color:var(--bad);background:var(--bad-bg);color:var(--bad)}
.ord{flex:0 0 auto;width:26px;height:26px;border-radius:50%;display:grid;
  place-items:center;font-family:var(--font-ledger);font-size:12px;
  border:1px solid var(--line);color:var(--mut)}
.ord.set{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
/* Reserved feedback region: directly below the response control, before the
   next action, with stable minimum height so the layout never shifts once a
   verdict is showing (D-02).

   Amended 2026-09-05: the reservation now applies only once the region has
   something in it. Empty, it reserved 96px (120px under 768) between the
   choices and Submit on every unanswered item, which read as a hole in the
   card rather than as a space waiting for something, and it could not have
   been protecting the stem in the first place: the stem is ABOVE this
   region, and content below never pushes content above. What the
   reservation genuinely protects is the action row's position between one
   verdict and the next, and that still holds, because the region only
   collapses while it is empty. The order D-02 fixes (response control,
   feedback, then the next action, so a screen reader meets the verdict
   before the control that leaves it) is untouched. */
.feedback{min-height:96px;margin-top:14px;padding-top:12px;
  border-top:1px solid var(--line);font-size:16px}
.feedback:empty{min-height:0;margin-top:0;padding-top:0;border-top:0}
.feedback .status{color:var(--mut);margin-bottom:8px}
/* Own-selection feedback on a held multiple-response attempt: which of the
   learner's OWN picks were right and which were wrong. Never colour alone --
   every row carries the word as text, because a verdict a learner cannot
   read is not feedback (UI-SPEC section 8). */
.picks{margin-top:var(--space-2)}
.picks p{margin:0 0 var(--space-2)}
.picks ul{list-style:none;margin:0;padding:0;display:flex;
  flex-direction:column;gap:var(--space-1)}
.picks li{display:flex;gap:var(--space-2);align-items:baseline;
  font:16px/1.5 var(--font-paper)}
.picks .mark{font:12px/1.5 var(--font-ledger);letter-spacing:.08em;
  text-transform:uppercase;flex:0 0 auto}
.picks li.y .mark{color:var(--ok)}
.picks li.n .mark{color:var(--bad)}
.support-region{border-top:1px solid var(--line);margin-top:var(--space-4);
  padding-top:var(--space-4)}
.hint-heading{font:12px/1.5 var(--font-ledger);letter-spacing:.08em;
  text-transform:uppercase;color:var(--mut);margin:0 0 var(--space-2)}
.hint-ladder{list-style:none;margin:0;padding:0;display:flex;
  flex-direction:column;gap:var(--space-2)}
.hint-card{padding:var(--space-3);border:1px solid var(--line);
  border-radius:var(--r-2);background:var(--card)}
.hint-card h4{font:12px/1.5 var(--font-ledger);letter-spacing:.08em;
  text-transform:uppercase;color:var(--mut);margin:0 0 var(--space-1)}
.hint-card p{font:16px/1.5 var(--font-paper);margin:0}
.hint-card.locked{background:var(--chip);border-style:dashed}
.hint-card.locked p{font:12px/1.5 var(--font-ledger)}
.hint-card.unavailable{color:var(--unknown);background:var(--unknown-bg)}
.hint-actions{display:flex;gap:var(--space-2);flex-wrap:wrap;margin-top:var(--space-2)}
.act{margin-top:13px;display:flex;gap:9px;align-items:center;flex-wrap:wrap}
button.go{font:inherit;font-family:var(--font-chrome);font-weight:600;font-size:16px;padding:11px 17px;
  min-height:44px;min-width:44px;border:1px solid var(--accent);border-radius:9px;
  background:var(--accent-soft);color:var(--accent);cursor:pointer}
button.go:disabled{opacity:.4;cursor:default}
button.go:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
button.ghost{background:var(--card);color:var(--ink);border:1px solid var(--edge)}
.hint{font-size:16px;color:var(--mut);font-family:var(--font-chrome)}
.exp h4{margin:0 0 5px;font-size:12px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--mut);font-family:var(--font-ledger)}
.exp .blk{margin-bottom:11px;font-family:var(--font-paper)}
.blk.note{color:var(--mut);font-size:16px}
.exp ul{margin:5px 0 0;padding-left:18px}
.exp li{margin-bottom:4px}
.verdict{font-family:var(--font-ledger);font-weight:600;margin-bottom:10px}
.verdict.y{color:var(--ok)} .verdict.n{color:var(--bad)}
.pend{font-family:var(--font-ledger);color:var(--warn);font-weight:600;margin-bottom:10px}
.trap{background:var(--accent-soft);border-left:3px solid var(--accent);
  padding:9px 12px;border-radius:0 7px 7px 0}
textarea.ans{width:100%;min-height:150px;padding:11px 12px;border-radius:9px;
  border:1px solid var(--edge);background:var(--card);color:inherit;
  font:inherit;font-family:var(--font-paper);font-size:16px;line-height:1.5;resize:vertical}
textarea.ans:focus{outline:2px solid var(--accent);outline-offset:1px;
  border-color:var(--accent)}
textarea.ans:disabled{opacity:.75}
/* check item code editor (plan 05-05): the wrapper declares the shared
   monospace stack once -- font family, size and line height -- and
   CodeMirror's own layers inherit it, so gutter row N is editor line N at
   any content width (CODE-03). No new colour token; every value below is an
   existing theme custom property. */
.codewrap{display:flex;flex-direction:column;border:1px solid var(--edge);
  border-radius:9px;background:var(--card);overflow:hidden;
  font-family:var(--font-code);font-size:16px;line-height:1.5}
.codewrap .cm-editor,.codewrap .cm-content,.codewrap .cm-gutters{
  font-family:var(--font-code);font-size:16px;line-height:inherit;
  background:transparent}
.codewrap .cm-editor{outline:none}
.codewrap .cm-content{padding:11px 12px}
.codewrap .cm-gutters{background:var(--chip);color:var(--mut);
  border-right:1px solid var(--line)}
.codewrap .cm-gutters .cm-gutterElement{padding:0 6px}
.codewrap:focus-within{outline:2px solid var(--accent);outline-offset:1px;
  border-color:var(--accent)}
.codewrap[data-readonly="true"]{opacity:.8}
/* check per-case readout rows (plan 05-06): mirror the option styles
   exactly -- same border, background, shape -- so a case row reads as the
   same kind of thing as every other answer widget. Bound stops (timeout,
   truncation) keep the failure row but their status text takes the warning
   role, so "stopped by a bound" is visible at a glance (D-08). */
.case{border:1px solid var(--line);border-radius:9px;padding:11px 12px;
  background:var(--card);margin-bottom:8px}
.case:last-child{margin-bottom:0}
.case .case-head{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;
  margin-bottom:7px}
.case .case-n{font-size:12px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--mut);font-family:var(--font-ledger)}
.case .st{font-size:12px;font-family:var(--font-ledger);font-weight:600}
.case.right{border-color:var(--ok);background:var(--ok-bg)}
.case.right .st{color:var(--ok)}
.case.wrong{border-color:var(--bad);background:var(--bad-bg)}
.case.wrong .st{color:var(--bad)}
.case.wrong .st.warn{color:var(--warn)}
.case .cf{margin-bottom:7px}
.case .cf:last-child{margin-bottom:0}
.case .cf h5{margin:0 0 3px;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--mut);
  font-family:var(--font-ledger)}
.case pre{white-space:pre-wrap;overflow-wrap:anywhere;font-family:var(--font-code);
  font-size:16px;line-height:1.5;
  margin:0;background:var(--card);border:1px solid var(--line);
  border-radius:6px;padding:7px 9px;max-height:180px;overflow:auto}
/* server-side refusal states (plan 05-06): the network refusal reuses the
   pending treatment; the language refusal reads as an error because it is a
   misconfiguration, not a boundary. */
.refused{font-family:var(--font-ledger);font-size:16px;margin-bottom:10px}
.refused.pend{color:var(--warn);font-weight:600}
.refused.err{color:var(--bad);font-weight:600}

.done{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:20px}
.lti-framing{background:var(--card);border:1px solid var(--line);
  border-radius:12px;padding:12px 16px;margin-bottom:14px;color:var(--mut);
  font-size:16px;line-height:1.5}
.score{font-size:32px;font-weight:600;letter-spacing:-.02em}
.score-sub{font-size:20px;color:var(--mut)}
.empty{text-align:center;padding:28px 10px}
@media (max-width:767px){
  .wrap{max-width:100%;padding:18px 16px 80px}
  .context-line{gap:2px 12px}
  h1.stem{font-size:20px}
  .feedback{min-height:120px}
  .feedback:empty{min-height:0}
  .context-line .objective,.context-line .mode,.context-line .lesson{display:none}
}
/* AgentAssist (plan 08-05): optional, subordinate, collapsed, opt-in
   generated support. Phase 4 tokens only; no fixed or minimum widths, so
   320px/200% zoom never scrolls horizontally. */
.agent-assist{margin:14px 0 0;font-size:16px;max-width:72ch;
  font-family:var(--font-chrome)}
.assist summary{cursor:pointer;padding:4px 0;font-size:16px;
  color:var(--mut);font-family:var(--font-chrome)}
.assist-body{display:flex;flex-direction:column;gap:8px;margin-top:8px}
.assist-status{color:var(--mut);font-size:16px;margin:0;font-family:var(--font-ledger)}
.assist-actions{display:flex;flex-wrap:wrap;gap:8px}
.assist-copy{color:var(--mut);margin:0}
.generated{background:var(--card);border:1px solid var(--line);
  border-left:3px solid var(--accent);border-radius:0 9px 9px 0;
  padding:12px 14px}
.generated h4,.authored-hint h4,.rubric h4{margin:0 0 5px;font-size:12px;
  letter-spacing:.09em;text-transform:uppercase;color:var(--mut);
  font-family:var(--font-ledger)}
.generated-disclosure{color:var(--mut);font-size:12px;margin:0 0 8px;
  font-family:var(--font-ledger)}
.generated-text{margin:0;overflow-wrap:anywhere}
.authored-hint{margin-top:10px;background:var(--card);border:1px solid var(--line);
  border-radius:9px;padding:12px 14px}
.authored-hint p{margin:0;overflow-wrap:anywhere}
.rubric-rows{list-style:none;margin:0;padding:0;display:flex;
  flex-direction:column;gap:8px}
.rubric-row{display:flex;gap:10px;align-items:flex-start;background:var(--card);
  border:1px solid var(--line);border-radius:9px;padding:10px 12px}
.rubric-token{flex:0 0 auto;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;font-family:var(--font-ledger);
  color:var(--warn);background:var(--chip);border:1px solid var(--line);
  border-radius:5px;padding:2px 7px}
.rubric-rationale{margin:0;overflow-wrap:anywhere}
.provenance{margin-top:10px;font-size:12px;color:var(--mut);
  font-family:var(--font-ledger)}
.provenance summary{cursor:pointer}
.assist-id{overflow-wrap:anywhere;word-break:break-all}
.activity-frame{margin:0 0 var(--space-4)}
.activity-facts{display:flex;flex-wrap:wrap;gap:var(--space-2) var(--space-4);margin:0}
.activity-facts div{min-width:10rem}.activity-facts dt{font-size:12px;color:var(--mut)}
.activity-facts dd{margin:2px 0 0;font-size:16px}
</style></head><body><div class="wrap" data-presentation-profile="__PRESENTATION_PROFILE__">
<nav class="context-line" data-surface-context aria-label="Session context">
  <span class="cx" id="cx-bank">__CTX_BANK__</span>
  <span class="cx objective" id="cx-objective"></span>
  <span class="cx mono">Item <b id="pos">1</b> of <b id="tot">__CTX_TOTAL__</b></span>
  <span class="cx mode" id="cx-mode">__CTX_MODE__</span>
  <span class="cx lesson" id="cx-lesson"></span>
</nav>
<section class="activity-frame" aria-label="Learner activity">
  <dl class="activity-facts"><div><dt>Purpose</dt><dd id="activity-purpose">__CTX_MODE__</dd></div>
  <div><dt>Response format</dt><dd id="activity-response">Response</dd></div>
  <div><dt>Disclosure</dt><dd id="activity-disclosure">Feedback follows session policy</dd></div></dl>
  <p class="hint" id="activity-instructions">Follow the response instructions below.</p>
</section>
<details class="session-details">
  <summary>Session details</summary>
  <div id="detail-body" class="detail-body"></div>
</details>
__LTI_FRAMING__
<div id="host"></div>
<div id="assist-slot">__ASSIST__</div>
</div>
__CM6_TAG__
__CM6_BOOT__
<script id="offline">
__OFFLINE_JS__
</script>
<script id="served">
__SERVED_JS__
</script>
<script id="assist">
__ASSIST_JS__
</script>
</body></html>"""


# The locked 08-UI-SPEC Copywriting Contract strings for the assist region
# (phase 8 UI-SPEC copy tables are binding; tests assert each verbatim).
ASSIST_COPY = {
    "summary": "Help and evidence",
    "request": "Get optional guidance",
    "preparing": "Preparing optional guidance\u2026",
    "generated_heading": "Generated support",
    "generated_disclosure": ("This guidance is generated from the current "
                             "attempt and the help available at this step."),
    "unavailable": ("Generated help is unavailable. You can keep learning "
                    "with the lesson and authored hints."),
    "policy_drop": ("Generated help is unavailable for this step. Continue "
                    "with the available hint or try another attempt."),
    "cancelled": ("Optional guidance was cancelled. Your current work is "
                  "unchanged."),
    "already_requested": ("Optional guidance was already requested for this "
                          "attempt. Continue with the available hint or make "
                          "another attempt."),
    "retry": "Try generated guidance again",
    "pending_heading": ("Pending rubric suggestion \u2014 human review "
                        "required"),
    "rubric_empty": ("No complete rubric suggestion is available. This "
                     "response is still waiting for a human mark."),
    "provenance_summary": "Generated support details",
}


# The assist chrome, substituted into TEMPLATE's __ASSIST__ slot only for the
# daemon-served page (build/offline mode ships no assist). Native
# details/summary, one opt-in button, one bounded status line, a generated
# support container, a provenance disclosure, and the structural lock /
# pending rubric containers the client fills -- no accept or mark control.
AGENT_ASSIST_HTML = (r"""<section class="agent-assist" data-agent-assist
  aria-label="Optional generated guidance">
  <details class="assist" id="assist">
    <summary>__ASSIST_SUMMARY__</summary>
    <div class="assist-body">
      <div class="assist-actions">
        <button type="button" class="go ghost" id="assist-request">__ASSIST_REQUEST__</button>
      </div>
      <p class="assist-status" id="assist-status"></p>
      <div class="assist-outcome" id="assist-outcome" hidden></div>
    </div>
  </details>
</section>"""
    .replace("__ASSIST_SUMMARY__", ASSIST_COPY["summary"])
    .replace("__ASSIST_REQUEST__", ASSIST_COPY["request"]))


# The AgentAssist client (plan 08-05). Wires the served client to POST
# /api/hint and POST /api/rubric-review, renders only the typed payload
# fields, announces each lifecycle state once through the single polite
# status region, and never reads or renders a reason code, a tier, a
# profile, a backend class, a fact manifest, a candidate body, or provider
# detail. It never creates an accept or mark control: the browser may render
# a pending suggestion, never settle one (D-14/D-25).
ASSIST_JS = (r"""/* AgentAssist client: renders only typed /api payloads in
   fixed chrome. No authority vocabulary is read or rendered here. */
const Assist = (function(){
  const statusEl = document.getElementById("assist-status");
  const outcomeEl = document.getElementById("assist-outcome");
  const requestBtn = document.getElementById("assist-request");
  let sessionId = null;
  let itemType = null;
  let requested = false;      /* at most one automatic generation per item */

  const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,
    c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

  function setStatus(text, live){
    if(!statusEl) return;
    if(live) statusEl.setAttribute("aria-live", "polite");
    else statusEl.removeAttribute("aria-live");
    statusEl.textContent = text || "";
  }
  function setBusy(busy){
    if(requestBtn) requestBtn.disabled = !!busy;
  }
  function render(html){
    if(!outcomeEl) return;
    outcomeEl.hidden = !html;
    outcomeEl.innerHTML = html || "";
  }
  function setSession(id){ sessionId = id; }
  function onItem(q){
    itemType = (q && q.type) || null;
    requested = false;
    setStatus("");
    setBusy(false);
    render("");
  }
  async function api(path, payload){
    const res = await fetch(path, {method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(payload)});
    if(!res.ok) throw new Error("HTTP " + res.status);
    return res.json();
  }
  /* The runtime shapes the words; this only renders them. `display` is the
     learner-facing text the runtime already resolved -- never an id, and
     never re-derived here. An absent payload renders nothing, as before; a
     payload that is present but has no text renders the locked empty
     state, because a silent nothing is indistinguishable from a broken
     panel. */
  function unavailableHtml(copy){
    return `<p class="assist-copy">${esc(copy)}</p>
      <button type="button" class="go ghost" id="assist-retry">__ASSIST_RETRY__</button>`;
  }
  function provenanceHtml(id){
    if(!id) return "";
    return `<details class="provenance"><summary>__ASSIST_PROVENANCE_SUMMARY__</summary>
      <p><span class="provenance-label">__ASSIST_GENERATED_HEADING__</span>
      &middot; interaction <span class="mono assist-id">${esc(id)}</span></p>
      </details>`;
  }
  function renderHint(v){
    if(v && v.status === "pass" && v.generated && v.generated.text){
      render(`<div class="generated">
          <h4>__ASSIST_GENERATED_HEADING__</h4>
          <p class="generated-disclosure">__ASSIST_GENERATED_DISCLOSURE__</p>
          <p class="generated-text">${esc(v.generated.text)}</p>
        </div>` + provenanceHtml(v.interaction_id));
      return;
    }
    if(v && (v.status === "unavailable" || v.status === "drop")){
      const copy = v.status === "drop"
        ? "__ASSIST_POLICY_DROP__" : "__ASSIST_UNAVAILABLE__";
      render(unavailableHtml(copy));
      const retry = document.getElementById("assist-retry");
      if(retry) retry.onclick = () => { request(true); };
      return;
    }
    if(v && v.status === "cancelled"){
      render(`<p class="assist-copy">__ASSIST_CANCELLED__</p>`);
      return;
    }
    render(unavailableHtml("__ASSIST_UNAVAILABLE__"));
  }
  function renderRubric(v){
    const points = (v && v.points) || [];
    if(v && v.status === "pending" && points.length){
      const rows = points.map(p => {
        const rationale = (p && p.rationale)
          ? `<div class="rubric-rationale">${esc(p.rationale)}</div>` : "";
        return `<li class="rubric-row">
          <span class="rubric-token">pending</span>
          <div>${rationale}</div></li>`;
      }).join("");
      render(`<div class="rubric">
        <h4>__ASSIST_PENDING_HEADING__</h4>
        <ul class="rubric-rows">${rows}</ul></div>`);
      return;
    }
    render(`<p class="assist-copy">__ASSIST_RUBRIC_EMPTY__</p>`);
  }
  function request(retry){
    if(!sessionId) return;
    if(requested && !retry){
      render(`<p class="assist-copy">__ASSIST_ALREADY_REQUESTED__</p>`);
      return;
    }
    requested = true;
    setBusy(true);
    setStatus("__ASSIST_PREPARING__", true);
    const path = itemType === "short" ? "/api/rubric-review" : "/api/hint";
    const payload = {session_id: sessionId};
    if(retry) payload.retry = true;
    api(path, payload).then(v => {
      if(itemType === "short") renderRubric(v); else renderHint(v);
      setStatus("", false);
    }).catch(() => {
      render(unavailableHtml("__ASSIST_UNAVAILABLE__"));
      const retryBtn = document.getElementById("assist-retry");
      if(retryBtn) retryBtn.onclick = () => { request(true); };
      setStatus("", false);
    }).then(() => { setBusy(false); });
  }
  if(requestBtn) requestBtn.onclick = () => { request(false); };
  return {setSession, onItem};
})();
window.Assist = Assist;
""")


def _prefilled(prefill, name):
    """The last value the learner submitted under this control name, or "".

    `prefill` is the raw submitted form mapping, presentation state only: it
    is echoed back into the controls so a failed POST does not throw away what
    was typed. It never reaches the scorer, the session, or evidence.
    """
    values = (prefill or {}).get(name) or []
    return values[-1] if values else ""


def _form_controls(item, prefill=None):
    """Render only the response vocabulary declared by a public item, with any
    previously submitted values echoed back in (see `_prefilled`)."""
    t = item.get("type")
    schema = item.get("response_schema") or {}
    if t in ("mc", "multi"):
        kind = "checkbox" if t == "multi" else "radio"
        chosen = set((prefill or {}).get("option") or [])
        rows = []
        for option in item.get("options") or []:
            key = str(option.get("key", ""))
            rows.append('<label class="choice"><input type="%s" name="option" '
                        'value="%s"%s><span class="k">%s</span><span class="ot">%s</span></label>'
                        % (kind, html.escape(key, quote=True),
                           " checked" if key in chosen else "",
                           html.escape(str(option.get("label", option.get("key", "")))),
                           html.escape(str(option.get("text", "")))))
        legend = "Select %s" % schema.get("select", "all that apply") if t == "multi" else "Choose one"
        return '<fieldset class="choices"><legend>%s</legend>%s</fieldset>' % (legend, "".join(rows))
    if t in ("table", "dnd"):
        cats = item.get("categories") or []
        rows = []
        for n, row in enumerate(item.get("rows") or []):
            was = _prefilled(prefill, "row_%d" % n)
            opts = ''.join('<option value="%s"%s>%s</option>' %
                           (html.escape(str(c), quote=True),
                            " selected" if str(c) == was else "",
                            html.escape(str(c))) for c in cats)
            rows.append('<label class="rowline"><span class="rowtext">%s</span><select name="row_%d">'
                        '<option value=""></option>%s</select></label>' %
                        (html.escape(str(row.get("text", ""))), n, opts))
        return "".join(rows)
    if t == "build":
        return "".join('<label class="rowline"><span class="rowtext">Step %d</span>'
                       '<select name="step_%d"><option value=""></option>%s</select></label>' %
                       (n + 1, n, ''.join('<option value="%s"%s>%s</option>' %
                                         (html.escape(str(s), quote=True),
                                          " selected" if str(s) == _prefilled(prefill, "step_%d" % n) else "",
                                          html.escape(str(s)))
                                         for s in item.get("steps") or []))
                       for n in range(len(item.get("steps") or [])))
    if t == "visual":
        return ('<div class="pend" role="note">This visual response needs the '
                'interactive page. Enable JavaScript, then reload this item. '
                'No response has been recorded.</div>')
    label = "Code response" if t == "check" else "Your response"
    value = _prefilled(prefill, "answer")
    if t == "check" and not value:
        value = item.get("starter", "")
    return '<label>%s<textarea class="ans" name="answer">%s</textarea></label>' % (
        label, html.escape(value))


def _selection_card(picks):
    """Render the runtime's own-selection disclosure, or nothing.

    The sentence is the runtime's (`runtime.selection_feedback` shapes it);
    this only lays out what it released, and shows nothing about options the
    learner did not pick because the payload does not name them. It is not a
    verdict and not partial credit: the item is still marked as a whole.
    """
    if not isinstance(picks, dict) or not picks.get("display"):
        return ""
    rows = []
    for cls, word, group in (("y", "right", picks.get("right") or []),
                             ("n", "not right", picks.get("wrong") or [])):
        for option in group:
            rows.append('<li class="pick %s"><span class="mark">%s</span>'
                        '<span>%s) %s</span></li>'
                        % (cls, word, html.escape(str(option.get("key", ""))),
                           html.escape(str(option.get("text", "")))))
    return '<div class="picks" data-selection-feedback><p>%s</p><ul>%s</ul></div>' % (
        html.escape(str(picks["display"])), "".join(rows))


def _hint_card(row, locked=False):
    body = " ".join(row.get("unlock_copy") or []) if locked else row.get("display", "")
    return '<li class="hint-card %s"><h4>%s</h4><p>%s</p></li>' % (
        "locked" if locked else "shown", html.escape(str(row.get("header", ""))),
        html.escape(str(body)))


def baseline_for(view, teaching_result, post_path, tokens, flash=None, prefill=None,
                 continue_href=None, continue_label=None):
    """Pure, key-free HTML adapter over public runtime projections.

    `prefill` is the raw form mapping of a submission that did not go through
    (an expired token, a refused body), echoed back into the controls so the
    learner does not lose what they wrote. Presentation state, never truth.
    """
    item = (view or {}).get("item")
    if not item:
        return '<div class="done empty" data-server-baseline>Session complete.</div>'
    teaching = (teaching_result or {}).get("teaching") or {}
    response_type = item.get("type", "")
    format_label = RESPONSE_FORMAT_LABELS.get(response_type, "Response")
    instructions = RESPONSE_FORMAT_INSTRUCTIONS.get(
        response_type, "Follow the response instructions below.")
    feedback = ""
    if isinstance(flash, dict):
        if flash.get("refused"):
            feedback = '<div class="refused pend">%s</div>' % html.escape(str(flash["refused"]))
        elif flash.get("action") == "hold":
            feedback = '<div class="verdict n">Not correct. Try a different answer, or open the next hint.</div>'
            feedback += _selection_card(flash.get("selection_feedback"))
        elif flash.get("action") == "defer_feedback":
            # The scoped serve path renders server-side, so this branch is what
            # a learner actually sees after a constructed response. It did not
            # exist until 2026-08-24: the flash fell through every case and
            # `feedback` stayed empty, so answering a short item produced a
            # blank panel and no control. A designed pause was indistinguishable
            # from a hung page, which is how the 13.9 sitting read it.
            #
            # No verdict, no model answer, no explanation: deferring feedback is
            # the point of the branch. It says only where the sitting is and how
            # to move it, and the reload works because this route's GET runs
            # `session.do_next`, which collects a settled mark.
            feedback = (
                '<div class="pend"><b>Recorded, and waiting on a mark.</b>'
                '<div>A constructed response is not scored by the machine. This'
                ' sitting stays on this item until a human marker records a'
                ' verdict, so nothing you wrote has been graded and no model'
                ' answer is shown to you now.</div>'
                '<div>Record the verdict with <span class="mono">itembank mark'
                ' --session &lt;id&gt; --item %s --verdict pass|fail</span>,'
                ' then reload this page to continue.</div></div>'
                % html.escape(str(item.get("id", ""))))
        elif flash.get("action") in ("advance", "complete"):
            score = flash.get("score")
            feedback = '<div class="%s">%s</div>' % (
                "pend" if score is None else "verdict " + ("y" if score else "n"),
                "Recorded. Not marked here." if score is None else
                ("Correct. Your answer was recorded." if score else
                 "Not correct. Your answer was recorded."))
    # The served form uses PRG. The runtime may already hold the next cursor
    # after accepting this answer, but the learner must first see the verdict
    # for the item they just answered. This pause is presentation only: the
    # explicit link resumes the runtime's current item without a second submit.
    if continue_href:
        action = ('<div class="act"><a class="go" data-feedback-continue '
                  'href="%s">%s</a></div>' %
                  (html.escape(continue_href, quote=True),
                   html.escape(continue_label or "Continue")))
        return ('<div class="card" data-server-baseline data-feedback-pause '
                'data-session-id="%s" data-item-id="%s">'
                '<h1 class="stem">%s</h1><p class="hint"><b>%s.</b> %s</p>'
                '<div class="feedback" role="status" aria-live="polite">%s</div>%s</div>' %
                (html.escape(str(view.get("session_id", "")), quote=True),
                 html.escape(str(item.get("id", "")), quote=True),
                 html.escape(str(item.get("stem", ""))), html.escape(format_label),
                 html.escape(instructions), feedback, action))
    ladder = ""
    if teaching.get("available"):
        cards = ''.join(_hint_card(x) for x in teaching.get("shown") or [])
        if teaching.get("next_locked"):
            cards += _hint_card(teaching["next_locked"], True)
        action = ""
        if not teaching.get("exhausted"):
            kind = "hint" if teaching.get("entitled") else "stumped"
            label = "Open the next hint" if kind == "hint" else "I'm stumped, show the next hint"
            action = ('<form method="post" action="%s" class="hint-actions">'
                      '<input type="hidden" name="form_token" value="%s">'
                      '<input type="hidden" name="action" value="%s">'
                      '<button class="go ghost" data-teach="%s" type="submit">%s</button></form>' %
                      (html.escape(post_path, quote=True), html.escape(tokens[kind], quote=True),
                       kind, kind, html.escape(label)))
        # The runtime owns hint entitlement. The page offers one next help
        # action instead of promoting locked future tiers as competing tasks.
        ladder = '<section class="support-region"><h3 class="hint-heading">Help</h3>' \
                 '<ol class="hint-ladder">%s</ol>%s</section>' % (cards, action)
    elif teaching.get("unavailable_reason"):
        ladder = '<section class="support-region"><p class="assist-copy">%s</p></section>' % \
                 html.escape(str(teaching["unavailable_reason"]))
    submit = ('' if response_type == "visual" else
              '<div class="act"><button class="go" type="submit">Submit answer</button></div>')
    return ('<div class="card" data-server-baseline data-session-id="%s" data-item-id="%s">'
            '<h1 class="stem">%s</h1><p class="hint"><b>%s.</b> %s</p>'
            '<form method="post" action="%s" data-answer-form>%s'
            '<input type="hidden" name="form_token" value="%s"><input type="hidden" name="action" value="submit">'
            '<div class="feedback" role="status" aria-live="polite">%s</div>'
            '%s</form>%s</div>' %
            (html.escape(str(view.get("session_id", "")), quote=True),
             html.escape(str(item.get("id", "")), quote=True), html.escape(str(item.get("stem", ""))),
             html.escape(format_label), html.escape(instructions),
             html.escape(post_path, quote=True), _form_controls(item, prefill),
             html.escape(tokens["submit"], quote=True), feedback, submit, ladder))
ASSIST_JS = (ASSIST_JS
    .replace("__ASSIST_PREPARING__", ASSIST_COPY["preparing"])
    .replace("__ASSIST_GENERATED_HEADING__", ASSIST_COPY["generated_heading"])
    .replace("__ASSIST_GENERATED_DISCLOSURE__", ASSIST_COPY["generated_disclosure"])
    .replace("__ASSIST_UNAVAILABLE__", ASSIST_COPY["unavailable"])
    .replace("__ASSIST_POLICY_DROP__", ASSIST_COPY["policy_drop"])
    .replace("__ASSIST_CANCELLED__", ASSIST_COPY["cancelled"])
    .replace("__ASSIST_ALREADY_REQUESTED__", ASSIST_COPY["already_requested"])
    .replace("__ASSIST_RETRY__", ASSIST_COPY["retry"])
    .replace("__ASSIST_PENDING_HEADING__", ASSIST_COPY["pending_heading"])
    .replace("__ASSIST_RUBRIC_EMPTY__", ASSIST_COPY["rubric_empty"])
    .replace("__ASSIST_PROVENANCE_SUMMARY__", ASSIST_COPY["provenance_summary"]))


# The static `build` compatibility client. This is the only place the
# canonical-key comparison lives; under `serve` this whole block is
# substituted away so the daemon-served page contains none of the offline-only
# implementation (plan 04-01 Test 5).
OFFLINE_JS = r"""const Q = __DATA__;
const SERVE = false;
const LESSON_BASE = "__LESSON_BASE__";   /* empty when no reader sits behind this page */
const LESSON_LABEL = "__LESSON_LABEL__";
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer", check:"code check",
               visual:"visual assessment"};
const FORMAT_LABEL = {mc:"Single choice", multi:"Multiple choice",
  table:"Table response", build:"Build response", dnd:"Ordering or matching",
  short:"Short response", visual:"Visual interaction", check:"Code check"};
const FORMAT_INSTRUCTION = {mc:"Choose one option.",
  multi:"Choose the requested number of options.",
  table:"Choose one category for every row.",
  build:"Select every step in the order it should happen.",
  dnd:"Match every row to a category. Dragging is not required.",
  short:"Write your response. It stays pending until a marker reviews it.",
  visual:"Use the visual or its adjacent keyboard controls, then submit.",
  check:"Edit the source, then run the check. The runtime records the verdict."};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
let i = 0, score = 0, autoTotal = 0;
let shownAt = performance.now();
const miss = [];
const host = document.getElementById("host");
const cxObjective = document.getElementById("cx-objective");
const cxLesson = document.getElementById("cx-lesson");
const detailBody = document.getElementById("detail-body");
const activityResponse = document.getElementById("activity-response");
const activityDisclosure = document.getElementById("activity-disclosure");
const activityPurpose = document.getElementById("activity-purpose");
const activityInstructions = document.getElementById("activity-instructions");
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

function installStickyMeasure(){
  const band = document.querySelector("[data-surface-context]");
  if(!band || !("ResizeObserver" in window)) return;
  let last = -1;
  new ResizeObserver(entries=>{
    const h = Math.round(entries[0].contentRect.height);
    if(h!==last){ last=h; document.documentElement.style.setProperty("--sticky-h",h+"px"); }
  }).observe(band);
}
function scrollCardIfNeeded(card){
  const r=card.getBoundingClientRect();
  const sticky=parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--sticky-h"))||0;
  if(r.top<sticky || r.bottom>innerHeight)
    card.scrollIntoView({block:"start",behavior:REDUCED?"auto":"smooth"});
}
installStickyMeasure();

function canon(q, r){
  if(q.type==="mc")    return String(r).toUpperCase();
  if(q.type==="multi") return r.map(x=>String(x).toUpperCase()).sort().join(",");
  if(q.type==="table" || q.type==="dnd")
    return q.rows.map(row => row.id + PS + (r[String(row.id)]||"")).join(FS);
  if(q.type==="build") return r.join(FS);
  return "";
}

async function verify(q, response){
  return {score: (q.key===null || q.key===undefined) ? null : canon(q, response)===q.key,
          explain: q.explain || {}};
}

function lessonChip(q){
  /* D-12: no chip when no reader sits behind the page, or when the slug does
     not resolve (--force). */
  if(!(q.lesson_slug && LESSON_BASE)) return "";
  return `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}"
          target="_blank" rel="noopener">${LESSON_LABEL}</a>`;
}

function metaChips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  h += `<span class="chip aon">dichotomous scoring</span>`;
  return h;
}

function setContext(q){
  if(cxObjective) cxObjective.textContent = q.objective || "";
  if(activityPurpose) activityPurpose.textContent = document.getElementById("cx-mode").textContent === "exam"
    ? "Formal assessment" : "Practice";
  if(activityResponse) activityResponse.textContent = FORMAT_LABEL[q.type] || q.type || "Response";
  if(activityInstructions) activityInstructions.textContent = FORMAT_INSTRUCTION[q.type] || "Follow the response instructions below.";
  if(activityDisclosure) activityDisclosure.textContent = q.type === "short"
    ? "Pending human review" : (document.getElementById("cx-mode").textContent === "exam"
      ? "Feedback after completion" : "Feedback available now");
  if(cxLesson) cxLesson.innerHTML = lessonChip(q);
  if(detailBody) detailBody.innerHTML = `<span class="chip">${esc(q.objective||"")}</span>`
    + `<span class="chip">${esc(document.getElementById("cx-mode").textContent)}</span>`
    + lessonChip(q) + metaChips(q);
}

function feedbackFor(card){
  let fb = card.querySelector(".feedback");
  if(!fb){
    fb = document.createElement("div");
    fb.className = "feedback";
    fb.setAttribute("role", "status");
    fb.setAttribute("aria-live", "polite");
    card.appendChild(fb);
  }
  return fb;
}

async function settle(q, response, card, act, paint){
  const fb = feedbackFor(card);
  fb.innerHTML = `<div class="status">Checking answer&hellip;</div>`;
  let v;
  try {
    v = await verify(q, response);
  } catch(err){
    fb.innerHTML = `<div class="status">Could not reach the process that scores and records
      this sitting (${esc(err.message)}). This answer was not saved and was not marked.
      Restart itembank and sit it again.</div>`;
    return;
  }
  if(paint) paint(v);
  close(q, card, act, v);
}

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function render(){
  document.getElementById("pos").textContent = Math.min(i+1, Q.length);
  document.getElementById("tot").textContent = Q.length;
  if(i>=Q.length) return finish();
  shownAt = performance.now();
  const q = Q[i];
  setContext(q);
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<h1 class="stem">${esc(q.stem)}</h1>`;
  const body = document.createElement("div");
  body.className = `response-body response-${q.type}`;
  card.appendChild(body);
  const fb = document.createElement("div");
  fb.className = "feedback";
  fb.setAttribute("role", "status");
  fb.setAttribute("aria-live", "polite");
  card.appendChild(fb);
  const act = document.createElement("div");
  act.className = "act";
  card.appendChild(act);
  host.innerHTML = "";
  host.appendChild(card);
  ({mc:asChoice, multi:asChoice, table:asAssign, dnd:asAssign, build:asBuild,
    short:asShort, check:asCheck, visual:asVisualOffline}[q.type])(q, body, act, card);
  scrollCardIfNeeded(card);
}

/* ---- visual assessment, offline (plan 06.1-03, D-03/A-05) ------------------
   The static build has no process behind it, so it cannot score a visual item
   or protect its answer. It renders the honest served-runtime-required state:
   no scorer, no key, no private scene fields, and no dead control. The copy
   is the 06.1-UI-SPEC Copywriting Contract's exact offline refusal text. */
function asVisualOffline(q, body, act, card){
  const note = document.createElement("div");
  note.className = "status";
  note.setAttribute("role", "note");
  note.textContent = "This visual item needs a served itembank session because "
    + "scoring and answer protection happen there. Open it with itembank serve "
    + "or the daemon.";
  body.appendChild(note);
}

/* ---- multiple choice (native radio) + multiple response (native checkboxes) */
const PINNED = /^\s*(all|none)\s+of\s+the\s+above|^\s*both\s+[A-H]\s+and\s+[A-H]/i;

function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const want = q.response_schema.select;
  const free = q.options.filter(o=>!PINNED.test(o.text));
  const pins = q.options.filter(o=> PINNED.test(o.text));
  const shown = shuffled(free).concat(pins);
  shown.forEach((o,n)=> o.label = LETTERS[n]);

  const fieldset = document.createElement("fieldset");
  fieldset.className = "choices";
  const legend = document.createElement("legend");
  legend.textContent = multi ? `Select ${want}` : "Choose one";
  fieldset.appendChild(legend);
  const picked = [];       // holds ORIGINAL keys
  const boxes = {};
  let submit = null;
  shown.forEach(o=>{
    const label = document.createElement("label");
    label.className = "choice";
    const input = document.createElement("input");
    input.type = multi ? "checkbox" : "radio";
    input.name = "answer";
    input.value = o.key;
    const k = document.createElement("span");
    k.className = "k"; k.textContent = o.label;
    const ot = document.createElement("span");
    ot.className = "ot"; ot.innerHTML = esc(o.text);
    label.append(input, k, ot);
    input.onchange = ()=>{
      if(!multi){
        picked.length = 0; picked.push(o.key);
        if(submit) submit.disabled = false;
        return;
      }
      if(input.checked){
        if(picked.length >= want){ input.checked = false; return; }
        picked.push(o.key);
      } else {
        const at = picked.indexOf(o.key);
        if(at >= 0) picked.splice(at, 1);
      }
      if(submit) submit.disabled = picked.length !== want;
    };
    boxes[o.key] = {label, input};
    fieldset.appendChild(label);
  });
  body.appendChild(fieldset);
  submit = mkSubmit(act, multi ? `select ${want}` : "choose one");
  submit.disabled = multi;
  submit.onclick = go;
  function revert(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = false; });
    if(!multi) submit.disabled = false;
  }
  function go(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint);
  }
  function paint(v){
    const ex = v.explain || {};
    const correct = ex.correct || [];
    const sole = correct.length === 1 ? correct[0] : null;
    shown.forEach(o=>{
      const {label, input} = boxes[o.key];
      if(correct.includes(o.key)) label.classList.add("right");
      else if(picked.includes(o.key)) label.classList.add("wrong");
      const line = (o.key === sole && ex.why) ? ex.why : ((ex.da||{})[o.key] || "");
      if(line){
        const r = document.createElement("span");
        r.className = "rat";
        r.textContent = line;      // textContent, so a bank cannot inject markup
        label.querySelector(".ot").appendChild(r);
      }
    });
    v.skipWhy = !!(sole && ex.why);
  }
}

/* ---- options table + drag-and-drop ---------------------------------------- */
function asAssign(q, body, act, card){
  const rows = shuffled(q.rows);
  const chosen = {};                 // row id -> category
  const segs = {};
  rows.forEach(r=>{
    const id = String(r.id);
    const line = document.createElement("div");
    line.className = "rowline";
    const t = document.createElement("div");
    t.className = "rowtext"; t.textContent = r.text;
    const seg = document.createElement("div");
    seg.className = "seg";
    const bs = q.categories.map(c=>{
      const b = document.createElement("button");
      b.type="button"; b.textContent=c; b.setAttribute("aria-pressed","false");
      b.onclick = ()=>{
        chosen[id]=c;
        bs.forEach(x=>x.setAttribute("aria-pressed", x.textContent===c?"true":"false"));
        submit.disabled = Object.keys(chosen).length !== q.rows.length;
      };
      seg.appendChild(b); return b;
    });
    segs[id] = bs;
    line.appendChild(t); line.appendChild(seg); body.appendChild(line);
  });
  const submit = mkSubmit(act, "assign every row");
  submit.onclick = ()=>{
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = true; }));
    submit.remove();
    settle(q, Object.assign({}, chosen), card, act, v=>{
      const cats = (v.explain||{}).row_cats || {};
      rows.forEach(r=>{
        const id = String(r.id);
        segs[id].forEach(b=>{
          if(b.textContent===cats[id]) b.classList.add("right");
          else if(b.textContent===chosen[id]) b.classList.add("wrong");
        });
      });
    });
  };
}

/* ---- build list (click into order) ---------------------------------------- */
function asBuild(q, body, act, card){
  const shown = shuffled(q.steps);
  const order = [];
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = shown.map(s=>{
    const b = document.createElement("button");
    b.className="opt"; b.type="button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="ord">-</span><span>${esc(s)}</span>`;
    b.onclick = ()=>{
      const at = order.indexOf(s);
      if(at>=0) order.splice(at,1); else order.push(s);
      redraw(); submit.disabled = order.length !== q.steps.length;
    };
    wrap.appendChild(b); return b;
  });
  function redraw(){
    shown.forEach((s,n)=>{
      const at = order.indexOf(s);
      const o = btns[n].querySelector(".ord");
      o.textContent = at>=0 ? (at+1) : "-";
      o.classList.toggle("set", at>=0);
      btns[n].setAttribute("aria-pressed", at>=0?"true":"false");
    });
  }
  body.appendChild(wrap);
  const submit = mkSubmit(act, "tap the steps in order");
  submit.onclick = ()=>{
    shown.forEach((s,n)=>{ btns[n].disabled = true; });
    submit.remove();
    settle(q, order.slice(), card, act, v=>{
      const right = (v.explain||{}).steps || [];
      shown.forEach((s,n)=>{
        const at = right.indexOf(s);
        btns[n].classList.add(order.indexOf(s)===at ? "right" : "wrong");
        btns[n].querySelector(".ord").textContent = at>=0 ? at+1 : "-";
      });
    });
  };
}

/* ---- short answer --------------------------------------------------------- */
function asShort(q, body, act, card){
  const ta = document.createElement("textarea");
  ta.className = "ans";
  ta.placeholder = "Type your answer. Complete sentences; this is marked on what you actually wrote.";
  body.appendChild(ta);
  const submit = mkSubmit(act, "your own words, no notes");
  ta.oninput = ()=>{ submit.disabled = ta.value.trim().length < 2; };
  ta.focus();
  submit.onclick = ()=>{
    ta.disabled = true;
    submit.remove();
    settle(q, ta.value.trim(), card, act, null);
  };
}

/* ---- check: vendored CodeMirror 6 code field ---------------------------- */
function asCheck(q, body, act, card){
  const cfg = (q.interaction_contract && q.interaction_contract.renderer_config) || {};
  const n = cfg.hidden_case_count || 0;
  const starter = q.starter || "";
  /* D-06 (plan 05-06): execution is server-side only, so a file:// page has
     no process to ask. Render the locked file-refusal sentence instead of
     the editor -- never a dead field the learner can type into and never
     submit -- and one skip control that advances without verifying, settling
     or closing: nothing is scored, nothing is recorded, and the item never
     reaches the auto-marked total (it is excluded exactly as if it were
     never reached). The honest-limits line below still renders from the
     item card. */
  if(!SERVE){
    const ref = document.createElement("div");
    ref.className = "pend";
    ref.textContent = "This item runs code on the machine serving itembank and can't be answered from a file opened directly in a browser. Open this bank with itembank serve (or the daemon) and try again.";
    body.appendChild(ref);
    const skip = document.createElement("button");
    skip.className = "go ghost"; skip.type = "button";
    skip.textContent = "Skip — not answerable offline";
    act.appendChild(skip);
    skip.onclick = ()=>{ i++; render(); };
    skip.focus();
    const lim2 = document.createElement("div");
    lim2.className = "hint";
    lim2.textContent = "__HONEST_LIMITS__";
    card.appendChild(lim2);
    return;
  }
  const wrap = document.createElement("div");
  wrap.className = "codewrap";
  const mount = document.createElement("div");
  wrap.appendChild(mount);
  body.appendChild(wrap);
  const submit = mkSubmit(act, caseHint(n));
  /* Locked hint copy (05-UI-SPEC Check button hint row): runs against %d
     hidden test case%s -- e.g. "runs against 1 hidden test case" /
     "runs against 3 hidden test cases". Hidden is locked: CASE) pairs are
     key material under D-12 and never reach public_item. */
  function caseHint(n){
    return n === 1 ? "runs against 1 hidden test case"
                   : "runs against " + n + " hidden test cases";
  }
  /* The editor's whole configuration -- line numbers, Tab/Shift-Tab keymap,
     placeholder, read-only lock, no wrap -- lives in the one boot script
     embedded above as a separate script, so the page and the JS test runner boot
     identical editors. The mount gets a semantic program label and concise
     keyboard instructions (05-UI-SPEC); Enter/Space activate the focused
     Check control natively (it is a real button). */
  mount.setAttribute("role", "textbox");
  mount.setAttribute("aria-label", "Source code");
  mount.setAttribute("aria-multiline", "true");
  const editor = CheckEditorBoot.create(mount, {starter: starter});
  const hintLine = document.createElement("div");
  hintLine.className = "hint";
  hintLine.textContent = "Tab inserts a tab, Shift-Tab dedents; the focused Check control activates with Enter or Space.";
  body.appendChild(hintLine);
  const sync = ()=>{ submit.disabled = editor.isEmpty(); };
  const origDispatch = editor.getView().dispatch;
  editor.getView().dispatch = function(tr){
    origDispatch.call(this, tr); sync();
  };
  sync();
  submit.onclick = ()=>{
    const src = editor.getSource();
    submit.disabled = true;
    submit.textContent = "Running…";
    editor.setReadOnly(true);
    settle(q, src, card, act, null, ()=>{ submit.textContent = "Submit answer"; submit.disabled = false; editor.setReadOnly(false); });
  };
  /* The honest-limits line renders from the item card, not from the editor
     branch, so plan 05-06's refusal states replace the editor without
     removing the statement. __HONEST_LIMITS__ is substituted by
     quiz.page_for from model.HONEST_LIMITS_NOTE (D-10). */
  const lim = document.createElement("div");
  lim.className = "hint";
  lim.textContent = "__HONEST_LIMITS__";
  card.appendChild(lim);
}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Submit answer"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

/* ---- check per-case readout (plan 05-06) ---------------------------------
   The learner's submitted source is their executable prediction; the ordered
   rows below are the bounded observations from that exact run, consumed from
   the shared normalized contract -- never scraped from prose, never a second
   verdict, never a re-run of the source. The overall verdict header stays
   the dichotomous runtime return; a null verdict (killed at timeout) renders
   the pending treatment, because a timeout is not a verdict (criterion 12). */
const CASE_STATUS = {
  passed:     ["Passed", ""],
  wrong_output:["Failed", ""],
  timeout:    ["Failed — timed out after %ss", "warn"],
  output_cap: ["Failed — output was cut off at %d KB", "warn"]
};
function caseStatus(reason, timeoutSecs, capKB){
  const [tmpl, role] = CASE_STATUS[reason] || ["Failed", ""];
  const text = reason === "timeout"
    ? tmpl.replace("%s", String(timeoutSecs))
    : reason === "output_cap" ? tmpl.replace("%d", String(capKB)) : tmpl;
  return {text, role};
}
function checkMatrix(rows, timeoutSecs, capKB){
  let h = `<div class="check-matrix" role="list">`;
  rows.forEach(r=>{
    const st = caseStatus(r.reason, timeoutSecs, capKB);
    const cls = r.passed ? "right" : "wrong";
    const warn = st.role === "warn" ? " warn" : "";
    h += `<div class="case ${cls}" role="listitem">
      <div class="case-head"><span class="case-n">Case ${r.case_index}</span>
        <span class="st${warn}">${esc(st.text)}</span></div>`;
    if(r.input) h += `<div class="cf"><h5>Input</h5><pre>${esc(r.input)}</pre></div>`;
    h += `<div class="cf"><h5>${r.expected_kind === "pattern" ? "Expected (pattern)" : "Expected"}</h5>
      <pre>${esc(r.expected)}</pre></div>`;
    h += `<div class="cf"><h5>Your output</h5><pre>${esc(r.actual || "")}</pre></div>`;
    h += `</div>`;
  });
  return h + `</div>`;
}

/* Offline-only row derivation: the static page holds the authored case
   halves in its explain payload and derives each observation's reason from
   the case flags plus the dichotomous score. Never a second verdict -- the
   header already came from canon()===key, and a null score (unanswered
   check) renders the pending header above. */
function checkRows(ex, v){
  return (ex.cases || []).map(c=>{
    const timed = !!c.timed_out, trunc = !!c.truncated;
    const failed = v.score === false;
    let reason = "passed";
    if(timed) reason = "timeout";
    else if(trunc) reason = "output_cap";
    else if(failed) reason = "wrong_output";
    return {case_index: c.case_index || 0, passed: !timed && !trunc && !failed,
            reason: reason, input: c.input || "", expected: c.expected || "",
            expected_kind: c.expected_kind || "output",
            actual: c.actual !== undefined ? c.actual : ""};
  });
}

function close(q, card, act, v){
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  if(!pending){ autoTotal++; if(right) score++; else miss.push({q, ex}); }
  act.innerHTML = "";
  const fb = feedbackFor(card);
  const exp = document.createElement("div");
  exp.className = "exp";
  const blk = (t,val)=> val ? `<div class="blk"><h4>${t}</h4><div>${esc(val)}</div></div>` : "";
  let h = pending
    ? `<div class="pend">Recorded. Not marked here.</div>`
    : `<div class="verdict ${right?"y":"n"}">${right?"Correct":"Not correct"}</div>`;
  if(q.type === "short"){
    if(ex.model){
      h += blk("Model answer", ex.model);
      if(ex.rubric && ex.rubric.length)
        h += `<div class="blk"><h4>What a marker checks</h4><ul><li>`
           + ex.rubric.map(esc).join("</li><li>") + `</li></ul></div>`;
    } else {
      h += `<div class="blk note">The model answer is
        held back so it cannot contaminate the items after this one. It is in the bank file.`;
    }
  } else if(q.type === "check"){
    /* The per-case readout (plan 05-06). The offline page compares against
       the canonical key it shipped, so the rows derive from the explain
       payload's authored halves plus the score; the served page feeds the
       normalized observations instead. The verdict header above stays the
       dichotomous runtime return; a null verdict (killed at timeout)
       renders the pending treatment, never pass or fail (criterion 12). */
    h += checkMatrix(checkRows(ex, v), 5, 64);
  } else {
    if(!v.skipWhy) h += blk("Why this is best", ex.why);
    h += blk("Key discriminator", ex.disc);
    h += blk("Second best", ex.second);
    if(ex.notes && ex.notes.length) h += `<div class="blk"><h4>Notes</h4><ul><li>`
      + ex.notes.map(esc).join("</li><li>") + `</li></ul></div>`;
  }
  if(ex.trap) h += `<div class="blk trap"><h4>Trap</h4><div>${esc(ex.trap)}</div></div>`;
  exp.innerHTML = h;
  fb.innerHTML = "";
  fb.appendChild(exp);
  const next = document.createElement("button");
  next.className="go"; next.type="button";
  next.textContent = (i===Q.length-1) ? "See results" : "Next";
  next.onclick = ()=>{ i++; render(); };
  act.appendChild(next);
  next.focus();
}

function finish(){
  document.getElementById("rail") && (document.getElementById("rail").style.width = "100%");
  const pct = autoTotal ? Math.round(score/autoTotal*100) : 0;
  const pend = Q.filter(q=>q.type==="short").length;
  let h = `<div class="done"><div class="score mono">${score}/${autoTotal}
    <span class="score-sub"> &middot; ${pct}% auto-marked</span></div>`;
  if(pend) h += `<p style="margin:12px 0 0;color:var(--warn)"><b>${pend} short
    answer${pend>1?"s":""} not marked here.</b> Nothing recorded them, because this page
    was opened as a file. Use <code>itembank serve</code> for a sitting that is meant
    to be graded.</p>`;
  if(miss.length){
    h += `<p style="margin:14px 0 6px"><b>${miss.length} to harvest.</b>
      Per Anki_Testing_Strategy &sect;2, the discriminator becomes the card, not the question.</p><ul>`;
    miss.forEach(m=>{
      h += `<li style="margin-bottom:9px"><b>${esc(m.q.stem.slice(0,110))}</b>`
        + (m.q.objective ? ` <span class="chip">${esc(m.q.objective)}</span>` : "")
        + (m.ex.trap ? `<br><span style="color:var(--mut)">Trap: ${esc(m.ex.trap)}</span>` : "")
        + `</li>`;
    });
    h += `</ul>`;
  } else {
    h += `<p style="margin-top:14px">Clean sweep. Nothing to harvest.</p>`;
  }
  h += `</div>`;
  host.innerHTML = h;
  window.scrollTo({top:0, behavior: REDUCED ? "auto" : "smooth"});
}

const frag = location.hash.replace(/^#/, "");
if(frag){ const at = Q.findIndex(x => String(x.id) === frag); if(at >= 0) Q.unshift(Q.splice(at, 1)[0]); }
Q.sort(()=>Math.random()-0.5);
render();
"""


# The daemon-served client (SURF-02): starts and submits through the canonical
# /api/* JSON session API. This script contains no scoring, no canonicalization,
# no key material, and no full item array -- it renders only what the server
# returns. Presentation state (selection, current item, position) is managed
# here; every verdict and every explanation comes from /api/submit.
SERVED_JS = r"""const BOOT = __BOOT__;
const SERVE = true;
const LESSON_BASE = "__LESSON_BASE__";   /* empty when no reader sits behind this page */
const LESSON_LABEL = "__LESSON_LABEL__";
const LETTERS = "ABCDEFGH";
const LABEL = {mc:"multiple choice", multi:"multiple response",
               table:"options table", build:"build list", dnd:"drag-and-drop",
               short:"short answer", check:"code check",
               visual:"visual assessment"};
const FORMAT_LABEL = {mc:"Single choice", multi:"Multiple choice",
  table:"Table response", build:"Build response", dnd:"Ordering or matching",
  short:"Short response", visual:"Visual interaction", check:"Code check"};
const FORMAT_INSTRUCTION = {mc:"Choose one option.",
  multi:"Choose the requested number of options.",
  table:"Choose one category for every row.",
  build:"Select every step in the order it should happen.",
  dnd:"Match every row to a category. Dragging is not required.",
  short:"Write your response. It stays pending until a marker reviews it.",
  visual:"Use the visual or its adjacent keyboard controls, then submit.",
  check:"Edit the source, then run the check. The runtime records the verdict."};
const FS = "\u001f", PS = "\u001e";   /* must match FIELD_SEP and PAIR_SEP */
const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
let sessionId = null, i = 0, total = 0, score = 0, autoTotal = 0;
let shownAt = performance.now();
/* Phase 999.4 (LTI): the server includes the assignment-completion line in
   the final submit response; finish() renders it when present. Never a
   number or score claim -- the two UI-SPEC section-4 lines only. */
let LTI_COMPLETION = null;
const miss = [];
const host = document.getElementById("host");
const cxObjective = document.getElementById("cx-objective");
const cxLesson = document.getElementById("cx-lesson");
const detailBody = document.getElementById("detail-body");
const activityResponse = document.getElementById("activity-response");
const activityDisclosure = document.getElementById("activity-disclosure");
const activityPurpose = document.getElementById("activity-purpose");
const activityInstructions = document.getElementById("activity-instructions");
const esc = s => (s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

function installStickyMeasure(){
  const band = document.querySelector("[data-surface-context]");
  if(!band || !("ResizeObserver" in window)) return;
  let last = -1;
  new ResizeObserver(entries=>{
    const h = Math.round(entries[0].contentRect.height);
    if(h!==last){ last=h; document.documentElement.style.setProperty("--sticky-h",h+"px"); }
  }).observe(band);
}
function scrollCardIfNeeded(card){
  const r=card.getBoundingClientRect();
  const sticky=parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--sticky-h"))||0;
  if(r.top<sticky || r.bottom>innerHeight)
    card.scrollIntoView({block:"start",behavior:REDUCED?"auto":"smooth"});
}
installStickyMeasure();

async function api(url, payload){
  const res = await fetch(url, {method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify(payload)});
  if(!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}

/* ---- the verdict -----------------------------------------------------------
   This page never decides whether an answer is right. Every response goes to
   /api/submit; the server scores it through runtime.score_response and returns
   the verdict, the explanation and the next item. No key, canonicalization or
   scoring code exists anywhere in this script. */
async function verify(q, response){
  const v = await api("/api/submit", {session_id: sessionId, answer: response});
  if(v.lti_completion) LTI_COMPLETION = v.lti_completion;
  return {action: v.action, score: v.score, explain: v.explain || {},
          next: v.next};
}

function lessonChip(q){
  /* D-12: no chip when no reader sits behind the page, and no chip when the
     slug does not resolve to a served heading (--force). */
  if(!(q.lesson_slug && LESSON_BASE
       && (!BOOT.lesson_slugs || BOOT.lesson_slugs.indexOf(q.lesson_slug) >= 0)))
    return "";
  return `<a class="chip lesson" href="${LESSON_BASE}#${q.lesson_slug}"
          target="_blank" rel="noopener">${LESSON_LABEL}</a>`;
}

function metaChips(q){
  let h = `<span class="chip type">${LABEL[q.type]||q.type}</span>`;
  if(q.type==="short") h += `<span class="chip aon">graded by a marker, not by this page</span>`;
  else if(q.type!=="mc") h += `<span class="chip aon">no partial credit</span>`;
  if(q.difficulty) h += `<span class="chip">${esc(q.difficulty)}</span>`;
  h += `<span class="chip aon">dichotomous scoring</span>`;
  return h;
}

function setContext(q){
  if(cxObjective) cxObjective.textContent = q.objective || "";
  if(activityPurpose) activityPurpose.textContent = document.getElementById("cx-mode").textContent === "exam"
    ? "Formal assessment" : "Practice";
  if(activityResponse) activityResponse.textContent = FORMAT_LABEL[q.type] || q.type || "Response";
  if(activityInstructions) activityInstructions.textContent = FORMAT_INSTRUCTION[q.type] || "Follow the response instructions below.";
  if(activityDisclosure) activityDisclosure.textContent = q.type === "short"
    ? "Pending human review" : (document.getElementById("cx-mode").textContent === "exam"
      ? "Feedback after completion" : "Feedback available now");
  if(cxLesson) cxLesson.innerHTML = lessonChip(q);
  if(detailBody) detailBody.innerHTML = `<span class="chip">${esc(q.objective||"")}</span>`
    + `<span class="chip">${esc(document.getElementById("cx-mode").textContent)}</span>`
    + lessonChip(q) + metaChips(q);
}

function feedbackFor(card){
  let fb = card.querySelector(".feedback");
  if(!fb){
    fb = document.createElement("div");
    fb.className = "feedback";
    fb.setAttribute("role", "status");
    fb.setAttribute("aria-live", "polite");
    card.appendChild(fb);
  }
  return fb;
}

async function settle(q, response, card, act, paint, revert){
  const fb = feedbackFor(card);
  fb.innerHTML = `<div class="status">Checking answer&hellip;</div>`;
  try {
    const v = await verify(q, response);
    if(paint) paint(v);
    close(q, card, act, v, revert);
  } catch(err){
    /* API failure: keep the current item and the entered response visible,
       offer a retry, and never manufacture a verdict the server did not issue. */
    fb.innerHTML = `<div class="status">Couldn't check that answer. Your selection
      is still here.</div>`;
    if(revert) revert();
    const b = document.createElement("button");
    b.className = "go"; b.type = "button"; b.textContent = "Try again";
    b.onclick = ()=>{ act.innerHTML = ""; settle(q, response, card, act, paint, revert); };
    act.appendChild(b);
    b.focus();
  }
}

function shuffled(a){const b=a.slice();for(let j=b.length-1;j>0;j--){
  const k=Math.floor(Math.random()*(j+1));[b[j],b[k]]=[b[k],b[j]];}return b;}

function renderItem(view){
  if(!view || !view.item){
    if(view && view.summary){ finish(view.summary); return; }
    emptyState();
    return;
  }
  i = view.position || 0;
  total = view.total || 0;
  document.getElementById("pos").textContent = i + 1;
  document.getElementById("tot").textContent = total;
  shownAt = performance.now();
  const q = view.item;
  setContext(q);
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<h1 class="stem">${esc(q.stem)}</h1>`;
  const body = document.createElement("div");
  body.className = `response-body response-${q.type}`;
  card.appendChild(body);
  const fb = document.createElement("div");
  fb.className = "feedback";
  fb.setAttribute("role", "status");
  fb.setAttribute("aria-live", "polite");
  card.appendChild(fb);
  const act = document.createElement("div");
  act.className = "act";
  card.appendChild(act);
  host.innerHTML = "";
  host.appendChild(card);
  ({mc:asChoice, multi:asChoice, table:asAssign, dnd:asAssign, build:asBuild,
    short:asShort, check:asCheck, visual:asVisual}[q.type])(q, body, act, card);
  /* AgentAssist (plan 08-05): the assist client resets per item so the
     Get optional guidance control targets the current item's operation. */
  if(window.Assist) window.Assist.onItem(q);
  /* Restore focus to the first meaningful control of the new item. */
  const first = card.querySelector("input, button, textarea");
  if(first && !REDUCED) first.focus({preventScroll:true});
  scrollCardIfNeeded(card);
}

/* ---- multiple choice (native radio) + multiple response (native checkboxes) */
const PINNED = /^\s*(all|none)\s+of\s+the\s+above|^\s*both\s+[A-H]\s+and\s+[A-H]/i;

function asChoice(q, body, act, card){
  const multi = q.type === "multi";
  const want = q.response_schema.select;
  const free = q.options.filter(o=>!PINNED.test(o.text));
  const pins = q.options.filter(o=> PINNED.test(o.text));
  const shown = shuffled(free).concat(pins);
  shown.forEach((o,n)=> o.label = LETTERS[n]);

  const fieldset = document.createElement("fieldset");
  fieldset.className = "choices";
  const legend = document.createElement("legend");
  legend.textContent = multi ? `Select ${want}` : "Choose one";
  fieldset.appendChild(legend);
  const picked = [];       // holds ORIGINAL keys
  const boxes = {};
  let submit = null;
  shown.forEach(o=>{
    const label = document.createElement("label");
    label.className = "choice";
    const input = document.createElement("input");
    input.type = multi ? "checkbox" : "radio";
    input.name = "answer";
    input.value = o.key;
    const k = document.createElement("span");
    k.className = "k"; k.textContent = o.label;
    const ot = document.createElement("span");
    ot.className = "ot"; ot.innerHTML = esc(o.text);
    label.append(input, k, ot);
    input.onchange = ()=>{
      if(!multi){
        picked.length = 0; picked.push(o.key);
        if(submit) submit.disabled = false;
        return;
      }
      if(input.checked){
        if(picked.length >= want){ input.checked = false; return; }
        picked.push(o.key);
      } else {
        const at = picked.indexOf(o.key);
        if(at >= 0) picked.splice(at, 1);
      }
      if(submit) submit.disabled = picked.length !== want;
    };
    boxes[o.key] = {label, input};
    fieldset.appendChild(label);
  });
  body.appendChild(fieldset);
  submit = mkSubmit(act, multi ? `select ${want}` : "choose one");
  submit.disabled = multi;
  submit.onclick = go;
  function revert(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = false; });
    if(!multi) submit.disabled = false;
  }
  function go(){
    shown.forEach(o=>{ boxes[o.key].input.disabled = true; });
    if(submit) submit.remove();
    settle(q, multi ? picked.slice() : picked[0], card, act, paint, revert);
  }
  function paint(v){
    const ex = v.explain || {};
    const correct = ex.correct || [];
    const sole = correct.length === 1 ? correct[0] : null;
    shown.forEach(o=>{
      const {label, input} = boxes[o.key];
      if(correct.includes(o.key)) label.classList.add("right");
      else if(picked.includes(o.key)) label.classList.add("wrong");
      const line = (o.key === sole && ex.why) ? ex.why : ((ex.da||{})[o.key] || "");
      if(line){
        const r = document.createElement("span");
        r.className = "rat";
        r.textContent = line;      // textContent, so a bank cannot inject markup
        label.querySelector(".ot").appendChild(r);
      }
    });
    v.skipWhy = !!(sole && ex.why);
  }
}

function asAssign(q, body, act, card){
  const rows = shuffled(q.rows);
  const chosen = {};                 // row id -> category
  const segs = {};
  rows.forEach(r=>{
    const id = String(r.id);
    const line = document.createElement("div");
    line.className = "rowline";
    const t = document.createElement("div");
    t.className = "rowtext"; t.textContent = r.text;
    const seg = document.createElement("div");
    seg.className = "seg";
    const bs = q.categories.map(c=>{
      const b = document.createElement("button");
      b.type="button"; b.textContent=c; b.setAttribute("aria-pressed","false");
      b.onclick = ()=>{
        chosen[id]=c;
        bs.forEach(x=>x.setAttribute("aria-pressed", x.textContent===c?"true":"false"));
        submit.disabled = Object.keys(chosen).length !== q.rows.length;
      };
      seg.appendChild(b); return b;
    });
    segs[id] = bs;
    line.appendChild(t); line.appendChild(seg); body.appendChild(line);
  });
  const submit = mkSubmit(act, "assign every row");
  function revert(){
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = false; }));
  }
  submit.onclick = ()=>{
    rows.forEach(r=>segs[String(r.id)].forEach(b=>{ b.disabled = true; }));
    submit.remove();
    settle(q, Object.assign({}, chosen), card, act, v=>{
      const cats = (v.explain||{}).row_cats || {};
      rows.forEach(r=>{
        const id = String(r.id);
        segs[id].forEach(b=>{
          if(b.textContent===cats[id]) b.classList.add("right");
          else if(b.textContent===chosen[id]) b.classList.add("wrong");
        });
      });
    }, revert);
  };
}

function asBuild(q, body, act, card){
  const shown = shuffled(q.steps);
  const order = [];
  const wrap = document.createElement("div");
  wrap.className = "opts";
  const btns = shown.map(s=>{
    const b = document.createElement("button");
    b.className="opt"; b.type="button"; b.setAttribute("aria-pressed","false");
    b.innerHTML = `<span class="ord">-</span><span>${esc(s)}</span>`;
    b.onclick = ()=>{
      const at = order.indexOf(s);
      if(at>=0) order.splice(at,1); else order.push(s);
      redraw(); submit.disabled = order.length !== q.steps.length;
    };
    wrap.appendChild(b); return b;
  });
  function redraw(){
    shown.forEach((s,n)=>{
      const at = order.indexOf(s);
      const o = btns[n].querySelector(".ord");
      o.textContent = at>=0 ? (at+1) : "-";
      o.classList.toggle("set", at>=0);
      btns[n].setAttribute("aria-pressed", at>=0?"true":"false");
    });
  }
  body.appendChild(wrap);
  const submit = mkSubmit(act, "tap the steps in order");
  function revert(){ shown.forEach((s,n)=>{ btns[n].disabled = false; }); }
  submit.onclick = ()=>{
    shown.forEach((s,n)=>{ btns[n].disabled = true; });
    submit.remove();
    settle(q, order.slice(), card, act, v=>{
      const right = (v.explain||{}).steps || [];
      shown.forEach((s,n)=>{
        const at = right.indexOf(s);
        btns[n].classList.add(order.indexOf(s)===at ? "right" : "wrong");
        btns[n].querySelector(".ord").textContent = at>=0 ? at+1 : "-";
      });
    }, revert);
  };
}

function asShort(q, body, act, card){
  const ta = document.createElement("textarea");
  ta.className = "ans";
  ta.placeholder = "Type your answer. Complete sentences; this is marked on what you actually wrote.";
  body.appendChild(ta);
  const submit = mkSubmit(act, "your own words, no notes");
  ta.oninput = ()=>{ submit.disabled = ta.value.trim().length < 2; };
  ta.focus();
  function revert(){ ta.disabled = false; }
  submit.onclick = ()=>{
    ta.disabled = true;
    submit.remove();
    settle(q, ta.value.trim(), card, act, null, revert);
  };
}


/* ---- check: vendored CodeMirror 6 code field ---------------------------- */
function asCheck(q, body, act, card){
  const cfg = (q.interaction_contract && q.interaction_contract.renderer_config) || {};
  const n = cfg.hidden_case_count || 0;
  const starter = q.starter || "";
  /* D-06 (plan 05-06): execution is server-side only, so a file:// page has
     no process to ask. Render the locked file-refusal sentence instead of
     the editor -- never a dead field the learner can type into and never
     submit -- and one skip control that advances without verifying, settling
     or closing: nothing is scored, nothing is recorded, and the item never
     reaches the auto-marked total (it is excluded exactly as if it were
     never reached). The honest-limits line below still renders from the
     item card. */
  if(!SERVE){
    const ref = document.createElement("div");
    ref.className = "pend";
    ref.textContent = "This item runs code on the machine serving itembank and can't be answered from a file opened directly in a browser. Open this bank with itembank serve (or the daemon) and try again.";
    body.appendChild(ref);
    const skip = document.createElement("button");
    skip.className = "go ghost"; skip.type = "button";
    skip.textContent = "Skip — not answerable offline";
    act.appendChild(skip);
    skip.onclick = ()=>{ i++; render(); };
    skip.focus();
    const lim2 = document.createElement("div");
    lim2.className = "hint";
    lim2.textContent = "__HONEST_LIMITS__";
    card.appendChild(lim2);
    return;
  }
  const wrap = document.createElement("div");
  wrap.className = "codewrap";
  const mount = document.createElement("div");
  wrap.appendChild(mount);
  body.appendChild(wrap);
  const submit = mkSubmit(act, caseHint(n));
  /* Locked hint copy (05-UI-SPEC Check button hint row): runs against %d
     hidden test case%s -- e.g. "runs against 1 hidden test case" /
     "runs against 3 hidden test cases". Hidden is locked: CASE) pairs are
     key material under D-12 and never reach public_item. */
  function caseHint(n){
    return n === 1 ? "runs against 1 hidden test case"
                   : "runs against " + n + " hidden test cases";
  }
  /* The editor's whole configuration -- line numbers, Tab/Shift-Tab keymap,
     placeholder, read-only lock, no wrap -- lives in the one boot script
     embedded above as a separate script, so the page and the JS test runner boot
     identical editors. The mount gets a semantic program label and concise
     keyboard instructions (05-UI-SPEC); Enter/Space activate the focused
     Check control natively (it is a real button). */
  mount.setAttribute("role", "textbox");
  mount.setAttribute("aria-label", "Source code");
  mount.setAttribute("aria-multiline", "true");
  const editor = CheckEditorBoot.create(mount, {starter: starter});
  const hintLine = document.createElement("div");
  hintLine.className = "hint";
  hintLine.textContent = "Tab inserts a tab, Shift-Tab dedents; the focused Check control activates with Enter or Space.";
  body.appendChild(hintLine);
  const sync = ()=>{ submit.disabled = editor.isEmpty(); };
  const origDispatch = editor.getView().dispatch;
  editor.getView().dispatch = function(tr){
    origDispatch.call(this, tr); sync();
  };
  sync();
  submit.onclick = ()=>{
    const src = editor.getSource();
    submit.disabled = true;
    submit.textContent = "Running…";
    editor.setReadOnly(true);
    settle(q, src, card, act, null, ()=>{ submit.textContent = "Submit answer"; submit.disabled = false; editor.setReadOnly(false); });
  };
  /* The honest-limits line renders from the item card, not from the editor
     branch, so plan 05-06's refusal states replace the editor without
     removing the statement. __HONEST_LIMITS__ is substituted by
     quiz.page_for from model.HONEST_LIMITS_NOTE (D-10). */
  const lim = document.createElement("div");
  lim.className = "hint";
  lim.textContent = "__HONEST_LIMITS__";
  card.appendChild(lim);
}

/* ---- check per-case readout (plan 05-06) ---------------------------------
   The served client consumes the shared normalized observations
   (v.interaction_result.observations) -- the exact ordered rows the runtime
   built from the one run -- and never re-derives the verdict. The status
   line comes from the stable machine-readable `reason`; a bounded stop keeps
   the failure row but reads in the warning role. */
const CASE_STATUS = {
  passed:     ["Passed", ""],
  wrong_output:["Failed", ""],
  timeout:    ["Failed — timed out after %ss", "warn"],
  output_cap: ["Failed — output was cut off at %d KB", "warn"]
};
function caseStatus(reason, timeoutSecs, capKB){
  const [tmpl, role] = CASE_STATUS[reason] || ["Failed", ""];
  const text = reason === "timeout"
    ? tmpl.replace("%s", String(timeoutSecs))
    : reason === "output_cap" ? tmpl.replace("%d", String(capKB)) : tmpl;
  return {text, role};
}
function checkMatrix(rows, timeoutSecs, capKB){
  let h = `<div class="check-matrix" role="list">`;
  rows.forEach(r=>{
    const st = caseStatus(r.reason, timeoutSecs, capKB);
    const cls = r.passed ? "right" : "wrong";
    const warn = st.role === "warn" ? " warn" : "";
    h += `<div class="case ${cls}" role="listitem">
      <div class="case-head"><span class="case-n">Case ${r.case_index}</span>
        <span class="st${warn}">${esc(st.text)}</span></div>`;
    if(r.input) h += `<div class="cf"><h5>Input</h5><pre>${esc(r.input)}</pre></div>`;
    h += `<div class="cf"><h5>${r.expected_kind === "pattern" ? "Expected (pattern)" : "Expected"}</h5>
      <pre>${esc(r.expected)}</pre></div>`;
    h += `<div class="cf"><h5>Your output</h5><pre>${esc(r.actual || "")}</pre></div>`;
    h += `</div>`;
  });
  return h + `</div>`;

}


/* ---- visual assessment (plan 06.1-01) --------------------------------------
   asVisual is the one renderer-registry adapter for declarative plot and
   number-line contracts. It reads ONLY q.interaction_contract
   (renderer_config scene + response_schema), never a key, tolerance or
   scoring field. All input paths -- SVG pointer, tap, and the adjacent
   native semantic controls -- reduce through ONE state object and ONE
   serializer, so equivalent states produce byte-identical canonical SCALAR
   strings. The serialized semantic response is submitted through the normal
   served /api/submit path; this page never computes a verdict. */
/* ---- exact-fraction drawing helpers (phase 999.1, advanced families) --------
   DRAWING ONLY: these parse canonical SCALAR strings into [n,d] pairs for SVG
   layout. The submitted state is always the canonical SCALAR string or a
   stable id -- never this float, never a pixel. */
function vfGCD(a, b){ a = Math.abs(a); b = Math.abs(b);
  while(b){ const t = a % b; a = b; b = t; } return a || 1; }
function vfParse(s){
  if(typeof s !== "string") return null;
  s = s.trim();
  let m = s.match(/^([+-]?\d+)\/(\d+)$/);
  if(m){ let n = +m[1], d = +m[2]; if(!d) return null;
    const g = vfGCD(n, d); n /= g; d /= g;
    if(d < 0){ n = -n; d = -d; } return [n, d]; }
  m = s.match(/^([+-]?\d+)(?:\.(\d{1,6}))?$/);
  if(!m) return null;
  const sign = m[1][0] === "-" ? -1 : 1;
  const whole = Math.abs(+m[1]);
  let d = 1, frac = 0;
  if(m[2]){ d = Math.pow(10, m[2].length); frac = +m[2]; }
  let n = sign * (whole * d + frac);
  const g = vfGCD(n, d); n /= g; d /= g;
  if(d < 0){ n = -n; d = -d; } return [n, d];
}
function vfStr(f){ return f[1] === 1 ? String(f[0]) : f[0] + "/" + f[1]; }
function vfNum(s){ const f = vfParse(s); return f ? f[0] / f[1] : NaN; }
function vfAdd(a, b){ const n = a[0]*b[1] + b[0]*a[1], d = a[1]*b[1];
  const g = vfGCD(n, d); return [n/g, d/g]; }
function vfMul(a, k){ const n = a[0]*k, d = a[1]; const g = vfGCD(n, d);
  return [n/g, d/g]; }
function vfCmp(a, b){ return a[0]*b[1] - b[0]*a[1]; }
function vfPos(f, mn, mx){
  const num = (f[0]*mn[1] - mn[0]*f[1]) * mx[1];
  const den = (mx[0]*mn[1] - mn[0]*mx[1]) * f[1];
  if(!den) return 0;
  return Math.max(0, Math.min(1, num / den));
}
function vfTicks(axis){
  const lo = vfParse(axis.min), hi = vfParse(axis.max), st = vfParse(axis.step);
  if(!lo || !hi || !st || st[0] <= 0) return [];
  const out = [];
  for(let k = 0; ; k++){
    const f = vfAdd(lo, vfMul(st, k));
    if(vfCmp(f, hi) > 0) break;
    out.push({v: vfStr(f), f});
  }
  return out;
}

/* ActionStatus remains persistently polite for ordinary visual updates, as
   required by 06.1. Blocking failures promote it to an assertive alert before
   changing the text, so assistive technology cannot observe alert + live-off
   or miss the failure because content changed first. */
function setVisualStatus(status, text, isError){
  if(isError){
    status.setAttribute("role", "alert");
    status.setAttribute("aria-live", "assertive");
  } else {
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
  }
  status.textContent = text;
}

/* ---- timeline renderer (phase 999.1-02) ------------------------------------
   Time-series placement: the learner picks one authored event and places it
   at a canonical SCALAR time value on an axis. Scene comes from the
   interaction_contract renderer_config only (axis, events, initial, actions,
   accessibility) -- never the answer value or any scoring field. Pointer,
   keyboard and the event/value select controls reduce through ONE state
   object and ONE serializer; a changed explicit commit posts
   place_timeline_event / move_timeline_event through /api/interact. */
function renderTimeline(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const axis = rc.axis || {min:"0", max:"10", step:"1"};
  const events = Array.isArray(rc.events) ? rc.events : [];
  const initial = rc.initial || {};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 130, L = 34, R = 14, T = 24, B = 40;
  const mid = T + (H - T - B) / 2;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  const tks = vfTicks(axis);
  const mn = vfParse(axis.min), mx = vfParse(axis.max);
  const step = vfParse(axis.step);
  function X(v){ return L + vfPos(vfParse(v), mn, mx) * (W - L - R); }

  const committed = {kind:"timeline_event", event: null, value: null};
  const tentative = {kind:"timeline_event", event: null, value: null};
  const pl = (initial.placements && initial.placements.length)
    ? initial.placements[0] : null;
  if(pl){ committed.event = pl.event; committed.value = pl.value; }
  Object.assign(tentative, committed);
  let selected = committed.event;    /* which event chip the learner moves */

  function snapshot(s){ return {kind:"timeline_event", event: s.event, value: s.value}; }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return !!(s.event && s.value); }
  function eventLabel(id){ const ev = events.find(e => e.id === id); return ev ? ev.label : id; }
  function adopt(s){ committed.event = s.event; committed.value = s.value; }
  function revertTentative(){
    tentative.event = committed.event; tentative.value = committed.value;
    draw(tentative); syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function draw(s){
    let h = `<line x1="${L}" y1="${mid}" x2="${W-R}" y2="${mid}" stroke="currentColor"/>`;
    tks.forEach(tk=>{
      const x = X(tk.v);
      h += `<line x1="${x}" y1="${mid-5}" x2="${x}" y2="${mid+5}" stroke="currentColor"/>`;
      h += `<text x="${x}" y="${mid+20}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
    });
    if(s.event && s.value){
      const x = X(s.value);
      const isCommitted = sameState(s, committed);
      h += `<line x1="${x}" y1="${mid-8}" x2="${x}" y2="${mid+8}" stroke="var(--accent)" stroke-width="2"/>`;
      h += `<text x="${x}" y="${mid-12}" font-size="11" text-anchor="middle" fill="var(--accent)">${esc(eventLabel(s.event))}</text>`;
      if(!isCommitted){
        h += `<text x="${x}" y="${mid+38}" font-size="10" text-anchor="middle" fill="var(--accent)">${esc(s.value)}</text>`;
      }
    }
    svg.innerHTML = h;
  }

  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid,
        action_type: filled(committed) ? "move_timeline_event" : "place_timeline_event",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  function snapTick(clientX){
    const r = svg.getBoundingClientRect();
    const px = (clientX - r.left) / r.width * W;
    let best = tks[0], bestD = Infinity;
    tks.forEach(tk=>{
      const d = Math.abs(X(tk.v) - px);
      if(d < bestD){ bestD = d; best = tk; }
    });
    return best;
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    const hit = snapTick(e.clientX);
    if(!hit || !selected) return;
    const before = JSON.stringify(snapshot(tentative));
    tentative.event = selected;
    tentative.value = hit.v;
    draw(tentative); syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if((e.key === "ArrowLeft" || e.key === "ArrowRight") && step){
      e.preventDefault();
      if(!selected) selected = events[0] ? events[0].id : null;
      const at = tks.findIndex(t => t.v === tentative.value);
      const delta = e.key === "ArrowLeft" ? -1 : 1;
      const nxt = tks[Math.max(0, Math.min(tks.length-1, (at < 0 ? 0 : at) + delta))];
      tentative.event = selected;
      tentative.value = nxt.v;
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  const controls = document.createElement("div");
  controls.className = "visual-controls";
  const evSel = document.createElement("select");
  events.forEach(ev=>{
    const o = document.createElement("option");
    o.value = ev.id; o.textContent = ev.label; evSel.appendChild(o);
  });
  evSel.onchange = ()=>{
    selected = evSel.value;
    tentative.event = evSel.value;
    draw(tentative);
  };
  const valSel = document.createElement("select");
  tks.forEach(tk=>{
    const o = document.createElement("option");
    o.value = tk.v; o.textContent = tk.v; valSel.appendChild(o);
  });
  valSel.onchange = ()=>{
    tentative.value = valSel.value;
    draw(tentative);
  };
  controls.appendChild(labelCtl("event", evSel));
  controls.appendChild(labelCtl("value", valSel));
  host.appendChild(controls);
  function labelCtl(label, sel){
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode(label + " "));
    row.appendChild(sel);
    return row;
  }
  function syncControls(){
    if(evSel.value !== tentative.event) evSel.value = tentative.event || "";
    if(tentative.value && valSel.value !== tentative.value) valSel.value = tentative.value;
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

/* ---- diagram renderer (phase 999.1-03) -------------------------------------
   Node-connection: the learner connects one authored node to another. Scene
   comes from the interaction_contract renderer_config only (plane, nodes,
   initial, actions, accessibility) -- never the answer connection or any
   scoring field. Pointer (click source then target), keyboard and the
   from/to select controls reduce through ONE state object and ONE
   serializer; a changed explicit commit posts connect_diagram. */
function renderDiagram(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const plane = rc.plane || {width:"8", height:"6"};
  const nodes = Array.isArray(rc.nodes) ? rc.nodes : [];
  const initial = rc.initial || {};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 240, R = 16;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  const Wf = vfNum(plane.width) || 8, Hf = vfNum(plane.height) || 6;
  function X(n){ return vfNum(n.x) / Wf * (W - 2) + 1; }
  function Y(n){ return vfNum(n.y) / Hf * (H - 2) + 1; }
  function nodeAt(clientX, clientY){
    const r = svg.getBoundingClientRect();
    const x = (clientX - r.left) / r.width * W;
    const y = (clientY - r.top) / r.height * H;
    let best = null, bestD = Infinity;
    nodes.forEach(n=>{
      const dx = x - X(n), dy = y - Y(n);
      const d = Math.sqrt(dx*dx + dy*dy);
      if(d < bestD){ bestD = d; best = n; }
    });
    return (best && bestD <= R) ? best : null;
  }

  const committed = {kind:"diagram_connection", from: null, to: null};
  const tentative = {kind:"diagram_connection", from: null, to: null};
  const conn = (initial.connections && initial.connections.length)
    ? initial.connections[0] : null;
  if(conn){ committed.from = conn.from; committed.to = conn.to; }
  Object.assign(tentative, committed);

  function snapshot(s){ return {kind:"diagram_connection", from: s.from, to: s.to}; }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return !!(s.from && s.to); }
  function label(id){ const n = nodes.find(n => n.id === id); return n ? n.label : id; }
  function adopt(s){ committed.from = s.from; committed.to = s.to; }
  function revertTentative(){
    tentative.from = committed.from; tentative.to = committed.to;
    draw(tentative); syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function draw(s){
    let h = `<rect x="1" y="1" width="${W-2}" height="${H-2}" fill="var(--card)" stroke="currentColor"/>`;
    if(s.from && s.to){
      const a = nodes.find(n => n.id === s.from), b = nodes.find(n => n.id === s.to);
      if(a && b){
        const x1 = X(a), y1 = Y(a), x2 = X(b), y2 = Y(b);
        const ang = Math.atan2(y2 - y1, x2 - x1);
        const tipX = x2 - Math.cos(ang) * (R + 4), tipY = y2 - Math.sin(ang) * (R + 4);
        h += `<line x1="${x1}" y1="${y1}" x2="${tipX}" y2="${tipY}" stroke="var(--accent)" stroke-width="2"/>`;
        h += `<polygon points="${tipX},${tipY} ${tipX - 9*Math.cos(ang - 0.45)},${tipY - 9*Math.sin(ang - 0.45)} ${tipX - 9*Math.cos(ang + 0.45)},${tipY - 9*Math.sin(ang + 0.45)}" fill="var(--accent)"/>`;
      }
    }
    nodes.forEach(n=>{
      const x = X(n), y = Y(n);
      const isFrom = s.from === n.id, isTo = s.to === n.id;
      h += `<circle cx="${x}" cy="${y}" r="${R}" fill="${isFrom || isTo ? "var(--accent)" : "var(--chip)"}" stroke="currentColor"/>`;
      h += `<text x="${x}" y="${y}" font-size="11" text-anchor="middle" dominant-baseline="middle" fill="var(--ink)">${esc(label(n.id))}</text>`;
    });
    svg.innerHTML = h;
  }

  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid, action_type: "connect_diagram",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    const hit = nodeAt(e.clientX, e.clientY);
    if(!hit) return;
    const before = JSON.stringify(snapshot(tentative));
    if(!tentative.from){
      tentative.from = hit.id;
    } else if(!tentative.to){
      if(hit.id === tentative.from){
        tentative.from = null;
      } else {
        tentative.to = hit.id;
      }
    } else {
      tentative.from = hit.id; tentative.to = null;
    }
    draw(tentative); syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      if(!nodes.length) return;
      const cur = tentative.to || tentative.from || nodes[0].id;
      const at = nodes.findIndex(n => n.id === cur);
      const delta = (e.key === "ArrowLeft" || e.key === "ArrowUp") ? -1 : 1;
      const nxt = nodes[Math.max(0, Math.min(nodes.length - 1, (at < 0 ? 0 : at) + delta))];
      if(tentative.to){ tentative.to = nxt.id; } else { tentative.from = nxt.id; }
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  const controls = document.createElement("div");
  controls.className = "visual-controls";
  function nodeSelect(onPick){
    const sel = document.createElement("select");
    nodes.forEach(n=>{
      const o = document.createElement("option");
      o.value = n.id; o.textContent = n.label; sel.appendChild(o);
    });
    sel.onchange = ()=>{ onPick(sel.value); };
    return sel;
  }
  const fromSel = nodeSelect(v => { tentative.from = v; draw(tentative); });
  const toSel = nodeSelect(v => { tentative.to = v; draw(tentative); });
  controls.appendChild(labelCtl("from", fromSel));
  controls.appendChild(labelCtl("to", toSel));
  host.appendChild(controls);
  function labelCtl(label, sel){
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode(label + " "));
    row.appendChild(sel);
    return row;
  }
  function syncControls(){
    if(tentative.from && fromSel.value !== tentative.from) fromSel.value = tentative.from;
    if(tentative.to && toSel.value !== tentative.to) toSel.value = tentative.to;
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

/* ---- trace renderer (phase 999.1-03) ---------------------------------------
   Re-trace a reference polyline: the learner places an ordered list of
   point_count points. Scene comes from the interaction_contract
   renderer_config only (axes, point_count, initial reference path, actions,
   accessibility) -- the answer path stays in the private SCORING envelope
   and is never rendered. Pointer (click places the next point in order),
   keyboard, and per-point x/y selects reduce through ONE state object and
   ONE serializer; a changed explicit commit posts place_trace_point /
   move_trace_point with the full canonical path. */
function renderTrace(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const axes = rc.axes || {};
  const ax = {x: axes.x || {min:"0", max:"4", step:"1"},
              y: axes.y || {min:"0", max:"4", step:"1"}};
  const pointCount = (typeof rc.point_count === "number" && rc.point_count >= 1)
    ? rc.point_count : 1;
  const initial = rc.initial || {};
  const ref = Array.isArray(initial.points) ? initial.points : [];
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 240, L = 34, R = 10, T = 14, B = 26;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  const xTicks = vfTicks(ax.x), yTicks = vfTicks(ax.y);
  const mnX = vfParse(ax.x.min), mxX = vfParse(ax.x.max);
  const mnY = vfParse(ax.y.min), mxY = vfParse(ax.y.max);
  function X(v){ return L + vfPos(vfParse(v), mnX, mxX) * (W - L - R); }
  function Y(v){ return H - B - vfPos(vfParse(v), mnY, mxY) * (H - T - B); }
  function snap(tks, f){
    let best = tks[0], bestD = Infinity;
    tks.forEach(tk=>{
      const d = Math.abs(vfCmp(f, tk.f));
      if(d < bestD){ bestD = d; best = tk; }
    });
    return best;
  }
  function domain(clientX, clientY, tks, mn, mx, isY){
    const r = svg.getBoundingClientRect();
    const t = Math.max(0, Math.min(1, isY
      ? (1 - (clientY - r.top) / r.height)
      : (clientX - r.left) / r.width));
    const f = [mn[0]*mx[1] + Math.round(t * (mx[0]*mn[1] - mn[0]*mx[1])), mn[1]*mx[1]];
    const g = vfGCD(f[0], f[1]); return snap(tks, [f[0]/g, f[1]/g]);
  }

  const committed = {kind:"trace_path", points: []};
  const tentative = {kind:"trace_path", points: []};
  /* The reference polyline (`ref`, from initial.points) is scene data drawn
     for orientation only -- the learner's placed points start empty and the
     submitted path is exactly what they place. The answer path never
     leaves the server. */
  tentative.points = committed.points.map(p => ({x: p.x, y: p.y}));

  function snapshot(s){
    return {kind:"trace_path",
            points: s.points.map(p => ({x: p.x, y: p.y}))};
  }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return s.points.length === pointCount; }
  function adopt(s){ committed.points = s.points.map(p => ({x: p.x, y: p.y})); }
  function revertTentative(){
    tentative.points = committed.points.map(p => ({x: p.x, y: p.y}));
    draw(tentative); syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function draw(s){
    let h = `<line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="currentColor"/>`;
    h += `<line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="currentColor"/>`;
    xTicks.forEach(tk=>{
      const x = X(tk.v);
      h += `<line x1="${x}" y1="${H-B}" x2="${x}" y2="${H-B+5}" stroke="currentColor"/>`;
      h += `<text x="${x}" y="${H-B+18}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
    });
    yTicks.forEach(tk=>{
      const y = Y(tk.v);
      h += `<line x1="${L-5}" y1="${y}" x2="${L}" y2="${y}" stroke="currentColor"/>`;
      h += `<text x="${L-8}" y="${y+3}" font-size="10" text-anchor="end">${esc(tk.v)}</text>`;
    });
    if(ref.length >= 2){
      const pts = ref.map(p => X(p.x) + "," + Y(p.y)).join(" ");
      h += `<polyline points="${pts}" fill="none" stroke="var(--line)" stroke-width="2" stroke-dasharray="4 3"/>`;
    }
    if(s.points.length >= 2){
      const pts = s.points.map(p => X(p.x) + "," + Y(p.y)).join(" ");
      h += `<polyline points="${pts}" fill="none" stroke="var(--accent)" stroke-width="2"/>`;
    }
    s.points.forEach((p, i)=>{
      const x = X(p.x), y = Y(p.y);
      h += `<circle cx="${x}" cy="${y}" r="6" fill="var(--accent)" stroke="var(--ink)"/>`;
      h += `<text x="${x+9}" y="${y-6}" font-size="10" fill="var(--accent)">${i+1}</text>`;
    });
    svg.innerHTML = h;
  }

  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid,
        action_type: filled(committed) ? "move_trace_point" : "place_trace_point",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    if(tentative.points.length >= pointCount) return;
    const tkX = domain(e.clientX, e.clientY, xTicks, mnX, mxX, false);
    const tkY = domain(e.clientY, e.clientX, yTicks, mnY, mxY, true);
    tentative.points.push({x: tkX.v, y: tkY.v});
    draw(tentative); syncControls();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      if(!tentative.points.length) return;
      const last = tentative.points[tentative.points.length - 1];
      const moveX = e.key === "ArrowLeft" || e.key === "ArrowRight";
      const tks = moveX ? xTicks : yTicks;
      const at = tks.findIndex(t => t.v === (moveX ? last.x : last.y));
      const delta = (e.key === "ArrowLeft" || e.key === "ArrowDown") ? -1 : 1;
      const nxt = tks[Math.max(0, Math.min(tks.length-1, (at < 0 ? 0 : at) + delta))];
      if(moveX) last.x = nxt.v; else last.y = nxt.v;
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  const controls = document.createElement("div");
  controls.className = "visual-controls";
  function valueSelect(tks, onPick){
    const sel = document.createElement("select");
    tks.forEach(tk=>{
      const o = document.createElement("option");
      o.value = tk.v; o.textContent = tk.v; sel.appendChild(o);
    });
    sel.onchange = ()=>{ onPick(sel.value); };
    return sel;
  }
  const selPairs = [];
  for(let i = 0; i < pointCount; i++){
    const sx = valueSelect(xTicks, v => {
      if(!tentative.points[i]) tentative.points[i] = {x: v, y: null};
      tentative.points[i].x = v; draw(tentative);
    });
    const sy = valueSelect(yTicks, v => {
      if(!tentative.points[i]) tentative.points[i] = {x: null, y: v};
      tentative.points[i].y = v; draw(tentative);
    });
    selPairs.push([sx, sy]);
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode("p" + (i+1) + " "));
    row.appendChild(sx);
    row.appendChild(sy);
    controls.appendChild(row);
  }
  const clearBtn = document.createElement("button");
  clearBtn.type = "button"; clearBtn.className = "go ghost";
  clearBtn.textContent = "Clear last point";
  clearBtn.onclick = ()=>{
    if(tentative.points.length) tentative.points.pop();
    draw(tentative); syncControls();
  };
  controls.appendChild(clearBtn);
  host.appendChild(controls);
  function syncControls(){
    for(let i = 0; i < pointCount; i++){
      const p = tentative.points[i];
      if(p){
        if(selPairs[i][0].value !== p.x) selPairs[i][0].value = p.x || "";
        if(selPairs[i][1].value !== p.y) selPairs[i][1].value = p.y || "";
      }
    }
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

/* ---- hotspot renderer (phase 999.1-01) -------------------------------------
   Click-on-region mapping: the learner selects one named region of a plane.
   Scene comes from q.interaction_contract.renderer_config only (plane,
   regions, initial, actions, accessibility) -- never the answer region or
   any scoring field. Pointer, keyboard and the radio-list semantic control
   reduce through ONE state object and ONE serializer; a changed explicit
   commit posts a single select_hotspot action through /api/interact and the
   final submit stays the ordinary response event. */
function renderHotspot(q, c, body, act, card){
  const rc = c.renderer_config || {};
  const plane = rc.plane || {width:"10", height:"6"};
  const regions = Array.isArray(rc.regions) ? rc.regions : [];
  const initial = rc.initial || {};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const W = 400, H = 240;
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  /* plane units -> svg pixels (DRAWING ONLY; the submitted state is a region
     id, never a coordinate). */
  function num(s){
    if(typeof s !== "string") return NaN;
    const m = s.trim().match(/^([+-]?\d+)\/(\d+)$/);
    if(m) return (+m[1]) / (+m[2]);
    return parseFloat(s);
  }
  const Wf = num(plane.width) || 10, Hf = num(plane.height) || 6;
  function SX(x){ return num(x) / Wf * W; }
  function SY(y){ return num(y) / Hf * H; }

  function contains(reg, x, y){
    const co = reg.coords || [];
    if(reg.shape === "rect" && co.length === 4){
      return x >= SX(co[0]) && x <= SX(co[0]) + SX(co[2])
          && y >= SY(co[1]) && y <= SY(co[1]) + SY(co[3]);
    }
    if(reg.shape === "circle" && co.length === 3){
      const dx = x - SX(co[0]), dy = y - SY(co[1]);
      return dx * dx + dy * dy <= SX(co[2]) * SX(co[2]);
    }
    if(reg.shape === "polygon" && co.length >= 3){
      let inside = false;
      for(let i = 0, j = co.length - 1; i < co.length; j = i++){
        const xi = SX(co[i][0]), yi = SY(co[i][1]);
        const xj = SX(co[j][0]), yj = SY(co[j][1]);
        if(((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi))
          inside = !inside;
      }
      return inside;
    }
    return false;
  }

  function shapePath(reg){
    const co = reg.coords || [];
    if(reg.shape === "rect" && co.length === 4)
      return `<rect x="${SX(co[0])}" y="${SY(co[1])}" width="${SX(co[2])}" height="${SY(co[3])}"/>`;
    if(reg.shape === "circle" && co.length === 3)
      return `<circle cx="${SX(co[0])}" cy="${SY(co[1])}" r="${SX(co[2])}"/>`;
    if(reg.shape === "polygon" && co.length >= 3)
      return `<polygon points="${co.map(v => SX(v[0]) + "," + SY(v[1])).join(" ")}"/>`;
    return "";
  }

  function draw(s){
    let h = `<rect x="1" y="1" width="${W-2}" height="${H-2}" fill="var(--card)" stroke="currentColor"/>`;
    regions.forEach(reg=>{
      const sel = s.region === reg.id;
      h += shapePath(reg).replace(/>$/, ` fill="${sel ? "var(--accent)" : "var(--card)"}" stroke="currentColor" stroke-width="1.5"/>`);
      const co = reg.coords || [];
      let lx = 0, ly = 0;
      if(reg.shape === "rect" && co.length >= 2){ lx = SX(co[0]) + SX(co[2])/2; ly = SY(co[1]) + SY(co[3])/2; }
      else if(reg.shape === "circle" && co.length >= 2){ lx = SX(co[0]); ly = SY(co[1]); }
      else if(reg.shape === "polygon" && co.length >= 1){
        co.forEach(v => { lx += SX(v[0]); ly += SY(v[1]); });
        lx /= co.length; ly /= co.length;
      }
      h += `<text x="${lx}" y="${ly}" font-size="11" text-anchor="middle" dominant-baseline="middle" fill="var(--ink)">${esc(reg.label)}</text>`;
    });
    svg.innerHTML = h;
  }

  /* ---- state: committed vs tentative (D-04/D-05) --------------------------- */
  const committed = {kind:"hotspot", region: (initial.region) || null};
  const tentative = {kind:"hotspot", region: (initial.region) || null};
  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, ch=>{
        const r = Math.random()*16|0, v = ch==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));
  function snapshot(s){ return {kind:"hotspot", region: s.region}; }
  function sameState(a, b){ return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b)); }
  function filled(s){ return !!s.region; }
  function adopt(s){ committed.region = s.region; }
  function revertTentative(){
    tentative.region = committed.region;
    draw(tentative);
    syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  async function commitMove(){
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId, interaction_version: c.version,
        action_id: aid, action_type: "select_hotspot",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => e.preventDefault());
  svg.addEventListener("pointerup", e => {
    const r = svg.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width * W;
    const y = (e.clientY - r.top) / r.height * H;
    const hit = regions.find(reg => contains(reg, x, y));
    if(!hit) return;
    const before = JSON.stringify(snapshot(tentative));
    tentative.region = hit.id;
    draw(tentative);
    syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      const at = regions.findIndex(r => r.id === tentative.region);
      const delta = (e.key === "ArrowLeft" || e.key === "ArrowUp") ? -1 : 1;
      if(regions.length){
        const nxt = regions[Math.max(0, Math.min(regions.length - 1, (at < 0 ? 0 : at) + delta))];
        tentative.region = nxt.id;
        draw(tentative); syncControls();
      }
      return;
    }
    if(e.key === "Enter" || e.key === " "){ e.preventDefault(); commitMove(); return; }
    if(e.key === "Escape"){ e.preventDefault(); revertTentative(); }
  });

  /* ---- adjacent semantic HTML control: radio list of region labels ------- */
  const controls = document.createElement("div");
  controls.className = "visual-controls";
  const radios = [];
  regions.forEach(reg=>{
    const row = document.createElement("label");
    row.className = "visual-ctl";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "hotspot-region";
    radio.value = reg.id;
    radio.onchange = ()=>{
      tentative.region = reg.id;
      draw(tentative);
      commitMove();
    };
    radios.push(radio);
    row.appendChild(radio);
    row.appendChild(document.createTextNode(" " + reg.label));
    controls.appendChild(row);
  });
  host.appendChild(controls);
  function syncControls(){
    radios.forEach(r => { r.checked = r.value === tentative.region; });
  }

  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);

  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);
  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true; commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };
}

function asVisual(q, body, act, card){
  const c = q.interaction_contract || {};
  const interaction = (c.interaction || "").trim();
  if(interaction === "hotspot") return renderHotspot(q, c, body, act, card);
  if(interaction === "timeline") return renderTimeline(q, c, body, act, card);
  if(interaction === "diagram") return renderDiagram(q, c, body, act, card);
  if(interaction === "trace") return renderTrace(q, c, body, act, card);
  const rc = c.renderer_config || {};
  const kind = (c.response_schema || {}).kind || "point";
  const axes = rc.axes || {};
  const axis = rc.axis || {min:"0", max:"1", step:"1"};
  const acc = rc.accessibility || {};
  const desc = acc.description || q.stem;
  const initial = rc.initial || {};
  const host = document.createElement("div");
  host.className = "visual-host";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", desc);
  svg.setAttribute("viewBox", "0 0 400 240");
  svg.setAttribute("class", "visual-svg");
  host.appendChild(svg);
  body.appendChild(host);
  const status = document.createElement("div");
  status.className = "visual-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  body.appendChild(status);
  const submit = mkSubmit(act, "commit your placement");

  /* ---- exact SCALAR arithmetic: parse "2" | "1/2" | "2.5" to [n,d] -------- */
  function fracGCD(a, b){ a = Math.abs(a); b = Math.abs(b);
    while(b){ const t = a % b; a = b; b = t; } return a || 1; }
  function fracParse(s){
    if(typeof s !== "string") return null;
    s = s.trim();
    let m = s.match(/^([+-]?\d+)\/(\d+)$/);
    if(m){ let n = +m[1], d = +m[2]; if(!d) return null;
      const g = fracGCD(n, d); n /= g; d /= g;
      if(d < 0){ n = -n; d = -d; } return [n, d]; }
    m = s.match(/^([+-]?\d+)(?:\.(\d{1,6}))?$/);
    if(!m) return null;
    const sign = m[1][0] === "-" ? -1 : 1;
    const whole = Math.abs(+m[1]);
    let d = 1, frac = 0;
    if(m[2]){ d = Math.pow(10, m[2].length); frac = +m[2]; }
    let n = sign * (whole * d + frac);
    const g = fracGCD(n, d); n /= g; d /= g;
    if(d < 0){ n = -n; d = -d; } return [n, d];
  }
  function fracStr(f){ return f[1] === 1 ? String(f[0]) : f[0] + "/" + f[1]; }
  function fracAdd(a, b){ const n = a[0]*b[1] + b[0]*a[1], d = a[1]*b[1];
    const g = fracGCD(n, d); return [n/g, d/g]; }
  function fracMulInt(a, k){ const n = a[0]*k, d = a[1];
    const g = fracGCD(n, d); return [n/g, d/g]; }
  function fracSub(a, b){ return fracAdd(a, [-b[0], b[1]]); }
  function fracCmp(a, b){ return a[0]*b[1] - b[0]*a[1]; }   /* sign of a-b */

  /* ticks(min,max,step) -> [{v: canonical scalar string, f: [n,d]}] */
  function ticks(ax){
    const lo = fracParse(ax.min), hi = fracParse(ax.max), st = fracParse(ax.step);
    if(!lo || !hi || !st || st[0] <= 0) return [];
    const out = [];
    for(let k = 0; ; k++){
      const f = fracAdd(lo, fracMulInt(st, k));
      if(fracCmp(f, hi) > 0) break;
      out.push({v: fracStr(f), f});
    }
    return out;
  }
  /* normalized position of fraction f between mn and mx, as a float in [0,1]
     -- used for DRAWING ONLY; the submitted value is always a canonical
     SCALAR string, never this float. */
  function toFrac(f, mn, mx){
    const num = (f[0]*mn[1] - mn[0]*f[1]) * mx[1];
    const den = (mx[0]*mn[1] - mn[0]*mx[1]) * f[1];
    if(!den) return 0;
    return num / den;
  }
  function clamp01(t){ return Math.max(0, Math.min(1, t)); }
  function snap(tks, f){
    let best = 0, bestDist = Infinity;
    for(let k = 0; k < tks.length; k++){
      const d = Math.abs(fracCmp(f, tks[k].f));
      if(d < bestDist){ bestDist = d; best = k; }
    }
    return tks[best];
  }

  const px = ticks(axes.x || axis), py = ticks(axes.y || axis);
  const valueTicks = ticks(axis);
  const xTicks = px.length ? px : valueTicks;
  const yTicks = py.length ? py : valueTicks;
  const isPlot = !!(axes.x && axes.y);
  const mnX = fracParse(axes.x ? axes.x.min : axis.min);
  const mxX = fracParse(axes.x ? axes.x.max : axis.max);
  const mnY = fracParse(axes.y ? axes.y.min : axis.min);
  const mxY = fracParse(axes.y ? axes.y.max : axis.max);

  function domainX(clientX){
    const r = svg.getBoundingClientRect();
    const t = clamp01((clientX - r.left) / r.width);
    return fracAdd(mnX, fracMulInt(fracSub(mxX, mnX), t));
  }
  function domainY(clientY){
    const r = svg.getBoundingClientRect();
    const t = clamp01((clientY - r.top) / r.height);
    return fracAdd(mnY, fracMulInt(fracSub(mxY, mnY), t));
  }

  const W = 400, H = 240, L = 34, R = 10, T = 14, B = 26;

  function draw(s){
    s = s || tentative;
    let h = "";
    if(isPlot){
      h += `<line x1="${L}" y1="${H-B}" x2="${W-R}" y2="${H-B}" stroke="currentColor"/>`;
      h += `<line x1="${L}" y1="${T}" x2="${L}" y2="${H-B}" stroke="currentColor"/>`;
      px.forEach(tk=>{
        const x = L + clamp01(toFrac(tk.f, mnX, mxX)) * (W - L - R);
        h += `<line x1="${x}" y1="${H-B}" x2="${x}" y2="${H-B+5}" stroke="currentColor"/>`;
        h += `<text x="${x}" y="${H-B+18}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
      });
      py.forEach(tk=>{
        const y = H - B - clamp01(toFrac(tk.f, mnY, mxY)) * (H - T - B);
        h += `<line x1="${L-5}" y1="${y}" x2="${L}" y2="${y}" stroke="currentColor"/>`;
        h += `<text x="${L-8}" y="${y+3}" font-size="10" text-anchor="end">${esc(tk.v)}</text>`;
      });
      if(s.kind === "point" && s.x && s.y){
        const x = L + clamp01(toFrac(fracParse(s.x), mnX, mxX)) * (W - L - R);
        const y = H - B - clamp01(toFrac(fracParse(s.y), mnY, mxY)) * (H - T - B);
        h += `<circle cx="${x}" cy="${y}" r="6" fill="var(--accent)"/>`;
      }
    } else {
      const mid = H / 2;
      h += `<line x1="${L}" y1="${mid}" x2="${W-R}" y2="${mid}" stroke="currentColor"/>`;
      valueTicks.forEach(tk=>{
        const x = L + clamp01(toFrac(tk.f, mnX, mxX)) * (W - L - R);
        h += `<line x1="${x}" y1="${mid-5}" x2="${x}" y2="${mid+5}" stroke="currentColor"/>`;
        h += `<text x="${x}" y="${mid+20}" font-size="10" text-anchor="middle">${esc(tk.v)}</text>`;
      });
      if(s.kind === "numberline_point" && s.value){
        const x = L + clamp01(toFrac(fracParse(s.value), mnX, mxX)) * (W - L - R);
        h += `<circle cx="${x}" cy="${mid}" r="6" fill="var(--accent)"/>`;
      }
      if(s.kind === "interval" && s.start && s.end){
        const x1 = L + clamp01(toFrac(fracParse(s.start), mnX, mxX)) * (W - L - R);
        const x2 = L + clamp01(toFrac(fracParse(s.end), mnX, mxX)) * (W - L - R);
        h += `<line x1="${x1}" y1="${mid}" x2="${x2}" y2="${mid}" stroke="var(--accent)" stroke-width="5"/>`;
        h += `<circle cx="${x1}" cy="${mid}" r="5" fill="${s.start_closed ? "var(--accent)" : "var(--card)"}" stroke="var(--accent)"/>`;
        h += `<circle cx="${x2}" cy="${mid}" r="5" fill="${s.end_closed ? "var(--accent)" : "var(--card)"}" stroke="var(--accent)"/>`;
      }
    }
    svg.innerHTML = h;
  }

  /* ---- state: committed vs tentative (D-04/D-05) ---------------------------
     `state` is the last committed semantic state; `tentative` is in-progress
     editing that produces NO evidence until an explicit commit. Pointer
     down/move, focus, hover, pan/zoom, Escape-cancelled moves, and unchanged
     values never append anything. A commit is exactly: native
     control/Enter/Space, a tap, or pointer-up after a changed drag -- each
     posts ONE semantic action through /api/interact and renders only the
     runtime's observation. */
  const committed = {kind};
  const tentative = {kind};
  const actionId = () => (crypto.randomUUID ? crypto.randomUUID()
    : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c=>{
        const r = Math.random()*16|0, v = c==="x"?r:(r&0x3|0x8);
        return v.toString(16); }));

  function snapshot(s){ // canonical semantic state dict (wire shape)
    if(kind === "point") return {kind:"point", x:s.x, y:s.y};
    if(kind === "numberline_point") return {kind:"numberline_point", value:s.value};
    return {kind:"interval", start:s.start, end:s.end,
            start_closed:!!s.start_closed, end_closed:!!s.end_closed};
  }
  function sameState(a, b){
    return JSON.stringify(snapshot(a)) === JSON.stringify(snapshot(b));
  }
  function filled(s){
    return kind === "point" ? (s.x && s.y)
      : kind === "numberline_point" ? s.value
      : (s.start && s.end);
  }
  function adopt(s){ // tentative becomes committed
    Object.keys(committed).forEach(k=>{ if(k!=="kind") delete committed[k]; });
    Object.assign(committed, s);
    commitBtn.disabled = !filled(committed);
    checkBtn.disabled = !filled(committed);
  }
  function revertTentative(){
    Object.keys(tentative).forEach(k=>{ if(k!=="kind") delete tentative[k]; });
    Object.assign(tentative, committed);
    draw(tentative);
    syncControls();
    setVisualStatus(status, "Move cancelled. Your last committed state is still here.", false);
  }

  function syncControls(){
    const sels = controls.querySelectorAll("select");
    const wants = kind === "point" ? [tentative.x, tentative.y]
      : kind === "numberline_point" ? [tentative.value] : [tentative.start, tentative.end];
    sels.forEach((sel, i)=>{ if(wants[i]) sel.value = wants[i]; });
    if(kind === "interval"){
      const chks = controls.querySelectorAll("input[type=checkbox]");
      chks[0].checked = !!tentative.start_closed;
      chks[1].checked = !!tentative.end_closed;
    }
  }

  /* ---- the ONE serializer: canonical SCALAR strings, exact wire shapes ---- */
  function serialize(){
    return JSON.stringify(snapshot(tentative));
  }

  async function commitMove(){
    /* The explicit commit boundary: pointer-up after a changed drag, tap, or
       native Enter/Space. An unchanged value commits nothing (D-04). */
    if(!filled(tentative)) return;
    if(sameState(tentative, committed)){
      setVisualStatus(status, "No change to commit.", false);
      return;
    }
    const aid = actionId();
    try {
      const v = await api("/api/interact", {
        session_id: sessionId,
        interaction_version: c.version,
        action_id: aid,
        action_type: kind === "point"
            ? (filled(committed) ? "move_point" : "place_point")
          : kind === "numberline_point" ? "select_numberline_point" : "set_interval",
        state: snapshot(tentative),
      });
      adopt(tentative);
      if(v.status === "recorded" || v.status === "already_recorded"){
        setVisualStatus(status, "Move committed. You can adjust it or check your response.", false);
      } else {
        setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
        revertTentative();
      }
    } catch(err){
      setVisualStatus(status, "That move could not be recorded. Your last committed state is still here. Adjust it and try again.", true);
    }
  }

  svg.addEventListener("pointerdown", e => { e.preventDefault(); });
  svg.addEventListener("pointerup", e => {
    const before = JSON.stringify(snapshot(tentative));
    if(kind === "point"){
      const x = snap(xTicks, domainX(e.clientX));
      const y = snap(yTicks, domainY(e.clientY));
      Object.assign(tentative, {x: x.v, y: y.v});
    } else if(kind === "numberline_point"){
      Object.assign(tentative, {value: snap(valueTicks, domainX(e.clientX)).v});
    } else {
      const hit = snap(valueTicks, domainX(e.clientX)).v;
      if(!tentative.start || (tentative.start && tentative.end))
        Object.assign(tentative, {start: hit, end: undefined});
      else Object.assign(tentative, {end: hit});
    }
    draw(tentative);
    syncControls();
    if(JSON.stringify(snapshot(tentative)) !== before) commitMove();   // changed drag/tap
  });
  svg.addEventListener("pointercancel", revertTentative);
  svg.addEventListener("pointerleave", e => { if(e.buttons === 0) return; });
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    /* Arrows step by declared units on the focused scene; Enter/Space commit
       the tentative move; Escape cancels (D-07). */
    const step = fracParse(axis.step);
    if(!step) return;
    if(e.key === "ArrowLeft" || e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "ArrowDown"){
      e.preventDefault();
      const delta = e.key === "ArrowLeft" || e.key === "ArrowDown" ? -1 : 1;
      if(kind === "point"){
        const moveX = e.key === "ArrowLeft" || e.key === "ArrowRight";
        const cur = moveX ? (tentative.x || axis.min) : (tentative.y || axis.min);
        const idx = valueTicks.findIndex(t => t.v === cur);
        const tks = moveX ? xTicks : yTicks;
        const at = tks.findIndex(t => t.v === cur);
        const nxt = tks[Math.max(0, Math.min(tks.length-1, (at < 0 ? 0 : at) + delta))];
        if(nxt) Object.assign(tentative, moveX ? {x: nxt.v} : {y: nxt.v});
      } else if(kind === "numberline_point"){
        const at = valueTicks.findIndex(t => t.v === (tentative.value || axis.min));
        const nxt = valueTicks[Math.max(0, Math.min(valueTicks.length-1, (at < 0 ? 0 : at) + delta))];
        if(nxt) Object.assign(tentative, {value: nxt.v});
      } else {
        const focus = e.shiftKey ? "start" : "end";
        const at = valueTicks.findIndex(t => t.v === (tentative[focus] || axis.min));
        const nxt = valueTicks[Math.max(0, Math.min(valueTicks.length-1, (at < 0 ? 0 : at) + delta))];
        if(nxt) Object.assign(tentative, {[focus]: nxt.v});
      }
      draw(tentative); syncControls();
      return;
    }
    if(e.key === "Enter" || e.key === " "){
      e.preventDefault();
      commitMove();
      return;
    }
    if(e.key === "Escape"){
      e.preventDefault();
      revertTentative();
    }
  });

  /* ---- adjacent semantic HTML controls: same state, same serializer ------- */
  function valueSelect(tks, onPick){
    const sel = document.createElement("select");
    tks.forEach(tk=>{ const o = document.createElement("option");
      o.value = tk.v; o.textContent = tk.v; sel.appendChild(o); });
    sel.onchange = ()=>{ onPick(sel.value); };
    return sel;
  }
  const controls = document.createElement("div");
  controls.className = "visual-controls";
  if(kind === "point"){
    const sx = valueSelect(xTicks, v=>{ Object.assign(tentative, {x: v}); draw(tentative); });
    const sy = valueSelect(yTicks, v=>{ Object.assign(tentative, {y: v}); draw(tentative); });
    controls.appendChild(labelCtl("x", sx));
    controls.appendChild(labelCtl("y", sy));
  } else if(kind === "numberline_point"){
    controls.appendChild(labelCtl("point", valueSelect(valueTicks,
      v=>{ Object.assign(tentative, {value: v}); draw(tentative); })));
  } else {
    const s1 = valueSelect(valueTicks, v=>{ Object.assign(tentative, {start: v}); draw(tentative); });
    const s2 = valueSelect(valueTicks, v=>{ Object.assign(tentative, {end: v}); draw(tentative); });
    const c1 = document.createElement("input"); c1.type = "checkbox";
    c1.onchange = ()=>Object.assign(tentative, {start_closed: c1.checked});
    const c2 = document.createElement("input"); c2.type = "checkbox";
    c2.onchange = ()=>Object.assign(tentative, {end_closed: c2.checked});
    const r1 = labelCtl("start", s1, c1);
    const r2 = labelCtl("end", s2, c2);
    r1.appendChild(document.createTextNode(" closed"));
    r2.appendChild(document.createTextNode(" closed"));
    controls.appendChild(r1);
    controls.appendChild(r2);
  }
  host.appendChild(controls);
  function labelCtl(label, sel, extra){
    const row = document.createElement("label");
    row.className = "visual-ctl";
    row.appendChild(document.createTextNode(label + " "));
    row.appendChild(sel);
    if(extra) row.appendChild(extra);
    return row;
  }

  /* ---- actions: Commit move, then Check response (UI-SPEC copy) ----------- */
  const commitBtn = document.createElement("button");
  commitBtn.className = "go ghost"; commitBtn.type = "button";
  commitBtn.textContent = "Commit move"; commitBtn.disabled = true;
  commitBtn.onclick = commitMove;
  act.appendChild(commitBtn);
  const checkBtn = mkSubmit(act, "make a prediction, then commit your move before checking it");
  checkBtn.textContent = "Check response";

  if(kind === "point" && initial.points && initial.points.length){
    Object.assign(committed, {x: initial.points[0].x, y: initial.points[0].y});
  }
  Object.assign(tentative, committed);
  draw(tentative);
  syncControls();
  commitBtn.disabled = !filled(committed);
  checkBtn.disabled = !filled(committed);

  checkBtn.onclick = ()=>{
    if(!filled(committed)){
      setVisualStatus(status, "Commit your move before checking it.", true);
      return;
    }
    checkBtn.disabled = true;
    commitBtn.disabled = true;
    settle(q, JSON.stringify(snapshot(committed)), card, act, null);
  };

}

function mkSubmit(act, hint){
  const b = document.createElement("button");
  b.className="go"; b.type="button"; b.textContent="Submit answer"; b.disabled=true;
  const h = document.createElement("span"); h.className="hint"; h.textContent=hint;
  act.appendChild(b); act.appendChild(h);
  return b;
}

function hintCard(row, locked){
  const lines = locked ? (row.unlock_copy||[]).map(esc).join(" ") : esc(row.display||"");
  const unavailable = !locked && row.available === false ? " unavailable" : "";
  return `<li class="hint-card ${locked?"locked":"shown"}${unavailable}">
    <h4>${esc(row.header)}</h4><p>${lines}</p></li>`;
}
function renderTeaching(card, result){
  const teaching = (result && result.teaching) || {};
  let region = card.querySelector(".support-region");
  if(!region){ region=document.createElement("section"); region.className="support-region";
    card.querySelector(".act").before(region); }
  if(!teaching.available){
    region.innerHTML = teaching.unavailable_reason
      ? `<p class="assist-copy">${esc(teaching.unavailable_reason)}</p>` : "";
    return;
  }
  const shown=(teaching.shown||[]).map(x=>hintCard(x,false)).join("");
  const next=teaching.next_locked ? hintCard(teaching.next_locked,true) : "";
  const label=teaching.entitled ? "Open the next hint" : "I'm stumped &mdash; show the next hint";
  const action=teaching.exhausted ? "" : `<div class="hint-actions"><button type="button"
    class="go ghost" data-teach="${teaching.entitled?"hint":"stumped"}">${label}</button></div>`;
  region.innerHTML=`<h3 class="hint-heading">Hints</h3><ol class="hint-ladder">${shown}${next}</ol>${action}`;
  const button=region.querySelector("[data-teach]");
  if(button) button.onclick=()=>api("/api/teach",{session_id:sessionId,
    action:{kind:button.dataset.teach}}).then(fresh=>renderTeaching(card,fresh));
}
function loadTeaching(card){
  return api("/api/teach",{session_id:sessionId}).then(result=>renderTeaching(card,result));
}

function close(q, card, act, v, revert){
  /* Server-side refusal (plan 05-06): the daemon returned a normal
     `{"refused": ..., "refused_reason": ...}` body instead of a verdict --
     the served page's settle() surfaced it here, not in the catch block.
     The page renders its own locked copy of the matching sentence (the
     Copywriting Contract rows live in this client script; the daemon's
     `refused_reason` field picks which one), styled by cause: network =
     boundary/pending, language = misconfiguration/error. Check is not
     re-enabled -- retrying cannot change the outcome. */
  if(v && v.refused){
    act.innerHTML = "";
    const fb = feedbackFor(card);
    const langName = ((q.interaction_contract || {}).renderer_config || {}).language || "python";
    const lang = (v.refused_reason === "language")
      ? "This item requests the '" + langName + "' language, which isn't "
        + "enabled in this itembank's settings (check.languages). Add it in "
        + "settings, or ask whoever set up this bank to fix its [LANG:] value."
      : "Code execution is turned off while itembank is serving on your "
        + "network (--lan). Ask whoever runs itembank to turn on "
        + "check.allow_lan in settings if this device should be trusted, or "
        + "answer this item from the machine itembank is running on.";
    const div = document.createElement("div");
    div.className = "refused " + (v.refused_reason === "language" ? "err" : "pend");
    div.textContent = lang;
    act.appendChild(div);
    fb.innerHTML = "";
    return;
  }
  const ex = v.explain || {};
  const right = v.score;
  const pending = (right === null || right === undefined);
  act.innerHTML = "";
  const fb = feedbackFor(card);
  if(v.action === "hold"){
    if(revert) revert();
    fb.innerHTML = `<div class="verdict n">Not correct. Try a different answer, or open the next hint.</div>`;
    loadTeaching(card);
    return;
  }
  if(v.action === "defer_feedback"){
    /* The sitting is parked at the marker's desk and the runtime will not
       move it until a mark is recorded, which is deliberate. What was NOT
       deliberate is that this branch used to print "Recorded." and return,
       leaving no control and no explanation, so a designed pause was
       indistinguishable from a hung page. Found by the 13.9 sitting on
       2026-08-24, whose shuffle put the short item first.

       It still releases no verdict, no model answer and no explanation:
       deferring feedback is the point. It only says where the sitting is. */
    const waiting = (q.type === "short")
      ? `<div class="pend"><b>Recorded, and waiting on a mark.</b>
         <div>A constructed response is not scored here. This sitting stays on
         this item until a human marker records a verdict, so nothing you wrote
         is graded by the machine and no model answer is shown to you now.</div>
         <div>You are the marker. Record the verdict below, or from a
         terminal with <span class="mono">itembank mark --session
         ${esc(sessionId || "")} --item ${esc(q.id || "")} --verdict pass|fail</span>.
         Either way it is the same recorded mark.</div></div>`
      : `<div class="pend"><b>Recorded.</b>
         <div>This mode holds every verdict until the sitting is closed.</div></div>`;
    fb.innerHTML = waiting;
    /* The way out of the desk, on the surface the learner is already on.
       A constructed response is settled by a person, and the person is
       here; before this the only exit was a terminal, so a sitting whose
       short item came up first dead-ended in the app. The verdict is the
       learner's own: the page sends it to `/api/mark`, which appends the
       same mark event `itembank mark` appends, and the runtime decides
       what that mark means for the cursor. No model has a vote here. */
    if(q.type === "short"){
      const settle = async (verdict)=>{
        try {
          const res = await api("/api/mark", {
            session_id: sessionId, item_ref: q.id, verdict: verdict});
          const view = (res && res.view) || null;
          if(view && view.status === "complete"){ finish(view.summary || {}); return; }
          if(view && view.item && view.item.id !== q.id){ renderItem(view); return; }
          fb.innerHTML = waiting
            + `<div class="pend">Mark recorded. The sitting did not move; check again.</div>`;
        } catch(err){
          fb.innerHTML = waiting
            + `<div class="pend">Could not record the mark. Nothing was changed.</div>`;
        }
      };
      const markRow = document.createElement("div");
      markRow.className = "act mark-row";
      for(const [label, verdict] of [["I got this right", true],
                                     ["I did not", false]]){
        const b = document.createElement("button");
        b.className = "go" + (verdict ? "" : " ghost");
        b.type = "button"; b.textContent = label;
        b.onclick = ()=> settle(verdict);
        markRow.appendChild(b);
      }
      act.appendChild(markRow);
    }
    const dnext = document.createElement("button");
    dnext.className = "go ghost"; dnext.type = "button";
    dnext.textContent = "Check again";
    dnext.onclick = async ()=>{
      /* Ask the server whether the desk has been collected. If the mark
         landed, the runtime has advanced and hands back the next item; if it
         has not, the same item comes back and the page says so again. The
         client never decides that a mark exists. */
      try {
        const view = await api("/api/next", {session_id: sessionId});
        if(view && view.item && view.item.id !== q.id){ renderItem(view); return; }
        if(view && view.status === "complete"){ finish(view.summary || {}); return; }
        fb.innerHTML = waiting
          + `<div class="pend">Still waiting on a mark for this item.</div>`;
      } catch(err){
        fb.innerHTML = waiting
          + `<div class="pend">Could not reach itembank to check.</div>`;
      }
    };
    act.appendChild(dnext);
    dnext.focus();
    return;
  }
  /* advance / complete: the runtime released the verdict and explanation. */
  if(!pending){ autoTotal++; if(right){ score++; } else { miss.push({q, ex}); } }
  const exp = document.createElement("div");
  exp.className = "exp";
  const blk = (t,val)=> val ? `<div class="blk"><h4>${t}</h4><div>${esc(val)}</div></div>` : "";
  let h = pending
    ? `<div class="pend">Recorded. Not marked here.</div>`
    : `<div class="verdict ${right?"y":"n"}">${right?"Correct":"Not correct"}</div>`;
  if(q.type === "short"){
    if(ex.model){
      h += blk("Model answer", ex.model);
      if(ex.rubric && ex.rubric.length)
        h += `<div class="blk"><h4>What a marker checks</h4><ul><li>`
           + ex.rubric.map(esc).join("</li><li>") + `</li></ul></div>`;
    } else {
      h += `<div class="blk note">The model answer is
        held back so it cannot contaminate the items after this one. It is in the bank file
        and in the attempt file next to what you wrote.</div>`;
    }
  } else if(q.type === "check"){
    /* The matrix consumes the normalized ordered observations from the one
       run -- stable case_index/reason pairs, never scraped from prose and
       never a second verdict. The deadline and cap are interpolated from
       the config the daemon runs with (booleans stay bound flags). */
    const rows = (v.interaction_result && v.interaction_result.observations) || [];
    h += checkMatrix(rows, 5, 64);
  } else {
    if(!v.skipWhy) h += blk("Why this is best", ex.why);
    h += blk("Key discriminator", ex.disc);
    h += blk("Second best", ex.second);
    if(ex.notes && ex.notes.length) h += `<div class="blk"><h4>Notes</h4><ul><li>`
      + ex.notes.map(esc).join("</li><li>") + `</li></ul></div>`;
  }
  if(ex.trap) h += `<div class="blk trap"><h4>Trap</h4><div>${esc(ex.trap)}</div></div>`;
  exp.innerHTML = h;
  fb.innerHTML = "";
  fb.appendChild(exp);
  const next = document.createElement("button");
  next.className = "go"; next.type = "button";
  const nxt = v.next || {};
  if(nxt.item){
    next.textContent = "Next";
    next.onclick = ()=>{ renderItem(nxt); };
  } else {
    next.textContent = "View summary";
    next.onclick = ()=>{ finish(nxt.summary || {}); };
  }
  act.appendChild(next);
  next.focus();
}

/* ---- results: the summary is the server's session summary ----------------- */
function finish(summary){
  const s = summary || {};
  const report = "/report?session=" + encodeURIComponent(sessionId || "");
  const auto = s.auto_attempts || 0;
  const correct = s.auto_correct || 0;
  const pend = s.pending_manual || 0;
  const pct = auto ? Math.round(correct/auto*100) : 0;
  let h = `<div class="done"><div class="score mono">${correct}/${auto}
    <span class="score-sub"> &middot; ${pct}% auto-marked</span></div>`;
  if(pend) h += `<p style="margin:12px 0 0;color:var(--warn)"><b>${pend} short
    answer${pend>1?"s":""} not marked here.</b> They are in the attempt file,
    waiting for a marker.</p>`;
  if(miss.length){
    h += `<p style="margin:14px 0 6px"><b>${miss.length} to harvest.</b>
      Per Anki_Testing_Strategy &sect;2, the discriminator becomes the card, not the question.</p><ul>`;
    miss.forEach(m=>{
      h += `<li style="margin-bottom:9px"><b>${esc(m.q.stem.slice(0,110))}</b>`
        + (m.q.objective ? ` <span class="chip">${esc(m.q.objective)}</span>` : "")
        + (m.ex.trap ? `<br><span style="color:var(--mut)">Trap: ${esc(m.ex.trap)}</span>` : "")
        + `</li>`;
    });
    h += `</ul>`;
  } else {
    h += `<p style="margin-top:14px">Clean sweep. Nothing to harvest.</p>`;
  }
  if(LTI_COMPLETION && LTI_COMPLETION.line){
    h += `<p class="status" data-field="lti-completion">${esc(LTI_COMPLETION.line)}</p>`;
  }
  h += `<div class="act"><a class="go ghost" style="text-decoration:none"
        href="${report}">View report</a></div></div>`;
  host.innerHTML = h;
  window.scrollTo({top:0, behavior: REDUCED ? "auto" : "smooth"});
}

/* ---- empty session: no item to show --------------------------------------- */
function emptyState(){
  const report = "/report?session=" + encodeURIComponent(sessionId || "");
  host.innerHTML = `<div class="done empty">
    <p><b>This session has no question ready.</b></p>
    <p style="color:var(--mut)">No items match this sitting&rsquo;s filters or
      the bank has nothing to serve.</p>
    <div class="act"><a class="go ghost" style="text-decoration:none"
          href="${report}">View report</a>
      <a class="go ghost" style="text-decoration:none"
          href="/settings">Filters / settings</a></div>
  </div>`;
}

function draftKey(bank, itemId){
  return "itembank.draft." + bank + "." + itemId;
}
function installDraft(baseline){
  // Draft autosave is presentation state only (080bffc): it refills the
  // visible controls and is never read back as an answer, never sent
  // anywhere, and never recorded until the form POST itself succeeds.
  // Storage unavailable or scripting off degrades to exactly the
  // script-free baseline, so every branch here is allowed to give up.
  //
  // Keyed by bank and item, not session: cmd_serve mints a fresh session id
  // on every launch (surfaces/quiz.py, surfaces/daemon.py _ensure_quiz_session),
  // so a session-keyed draft is orphaned by exactly the restart it exists to
  // survive. The bank stem is stable across a restart, which is the whole
  // point. One learner per installation, so a draft surviving to whichever
  // session next opens the same item is the desired behaviour, not a leak.
  try{
    var store = window.localStorage;
    if(!store) return;
    var bank = (BOOT && BOOT.bank) || "", iid = baseline.dataset.itemId;
    if(!bank || !iid) return;
    var form = baseline.querySelector("[data-answer-form]");
    if(!form) return;
    var prefix = "itembank.draft." + bank + ".";
    var key = draftKey(bank, iid);
    for(var i = store.length - 1; i >= 0; i--){
      var k = store.key(i);
      if(k && k.indexOf(prefix) === 0 && k !== key) store.removeItem(k);
    }
    var fields = form.querySelectorAll("textarea, input[type=text]");
    var saved = null;
    try{ saved = JSON.parse(store.getItem(key) || "null"); }catch(e){ saved = null; }
    fields.forEach(function(el, idx){
      if(saved && !el.value && typeof saved[idx] === "string") el.value = saved[idx];
    });
    form.addEventListener("input", function(){
      var vals = [];
      fields.forEach(function(el){ vals.push(el.value); });
      try{ store.setItem(key, JSON.stringify(vals)); }catch(e){}
    });
  }catch(e){}
}

/* ---- start: one /api/start call bootstraps the whole sitting -------------- */
async function start(){
  const baseline = host.querySelector("[data-server-baseline]");
  if(baseline){
    sessionId = baseline.dataset.sessionId || null;
    if(window.Assist) window.Assist.setSession(sessionId);
    installDraft(baseline);
    return;
  }
  host.innerHTML = `<div class="card"><div class="feedback" role="status"
      aria-live="polite"><div class="status">Loading&hellip;</div></div></div>`;
  try {
    /* D-09: a #<item-id> fragment (lesson backlink) asks the server to start
       with that item first; unknown ids degrade to normal order server-side.
       Phase 999.4 (LTI): the server may embed an objective and a one-time
       launch-context token in BOOT -- the LTI /api/* family reads them. */
    const payload = {bank: BOOT.bank, count: BOOT.count, mode: BOOT.mode};
    if(BOOT.objective) payload.objective = BOOT.objective;
    if(BOOT.lti_ctx) payload.lti_ctx = BOOT.lti_ctx;
    const frag = location.hash.replace(/^#/, "");
    if(frag) payload.focus = frag;
    const view = await api("/api/start", payload);
    sessionId = view.session_id;
    if(window.Assist) window.Assist.setSession(sessionId);
    renderItem(view);
  } catch(err){
    host.innerHTML = `<div class="done empty">
      <p><b>This session has no question ready.</b></p>
      <p style="color:var(--mut)">Couldn't load this session (${esc(err.message)}).
        Your bank is still here; try again.</p>
      <div class="act"><button class="go" type="button" id="retry">Try again</button></div>
    </div>`;
    const b = document.getElementById("retry");
    b.onclick = ()=>{ start(); };
    b.focus();
  }
}

if(BOOT && BOOT.bank){ start(); }
"""
