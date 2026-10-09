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
import hashlib
import re
import json

import resources


RESPONSE_FORMAT_LABELS = {
    "mc": "Single choice", "multi": "Multiple choice",
    "table": "Table response", "build": "Build response",
    "dnd": "Ordering or matching", "short": "Short response",
    "fill": "Typed fields", "visual": "Visual interaction", "check": "Code check",
}
RESPONSE_FORMAT_INSTRUCTIONS = {
    "mc": "Choose one option.",
    "multi": "Choose the requested number of options.",
    "table": "Choose one category for every row.",
    "build": "Select every step in the order it should happen.",
    "dnd": "Match every row to a category. Dragging is not required.",
    "short": "Write your response. It stays pending until a marker reviews it.",
    "fill": "Enter a response in every field. Include a unit when the label asks for one.",
    "visual": "Use the visual or its adjacent keyboard controls, then submit.",
    "check": "Edit the source, then run the check. The runtime records the verdict.",
}


QUESTION_STEM_PATTERN = r"^([\s\S]*?)\n\n```([A-Za-z0-9_+-]*)\n([\s\S]*?)\n```\s*$"


def question_stem_html(stem):
    """Present one fenced public stimulus; leave the canonical stem untouched."""
    raw = str(stem or '')
    match = re.fullmatch(QUESTION_STEM_PATTERN, raw)
    if not match or not match[1].strip() or '```' in match[1] or '```' in match[3]:
        return '<h1 class="stem" tabindex="-1">%s</h1>' % html.escape(raw)
    title, language, code = match.groups()
    return ('<h1 class="stem" tabindex="-1">%s</h1>'
            '<figure class="question-code"><figcaption>%s · Read-only code</figcaption>'
            '<pre tabindex="0" role="region" aria-label="Read-only code"><code>%s</code></pre></figure>'
            % (html.escape(title.strip()), html.escape(language or 'text'), html.escape(code)))


QUESTION_STEM_JS = resources.read_text("surfaces/assets/quiz/question-stem.js").replace('__STEM_PATTERN__', json.dumps(QUESTION_STEM_PATTERN))


LATEX_INPUT_STYLES = resources.read_text("surfaces/assets/quiz/latex-input.css")


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
  text-wrap:pretty;white-space:pre-line}
.ot,.rowtext{white-space:pre-line}
.quiz-argument{display:grid;gap:var(--space-1);margin:var(--space-1) 0;
  font-size:var(--text-body);font-weight:400;line-height:1.5}
.quiz-argument-line{display:grid;grid-template-columns:minmax(7rem,auto) 1fr;
  gap:var(--space-3);align-items:baseline;padding:4px var(--space-3);
  border-left:3px solid var(--accent);border-radius:0 var(--r-1) var(--r-1) 0;
  background:var(--chip)}
.quiz-argument-label{font:var(--text-xs)/1.5 var(--font-ledger);
  letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}
.quiz-argument-text{font-family:var(--font-paper);min-width:0}
.question-code{margin:0 0 var(--space-4);min-width:0;max-width:100%;border:1px solid var(--edge);background:var(--chip)}
.question-code figcaption{padding:var(--space-2) var(--space-3);color:var(--mut);font:var(--text-xs)/1.5 var(--font-ledger)}
.question-code pre{margin:0;padding:var(--space-3);max-width:100%;overflow:auto;white-space:pre;font:16px/1.5 var(--font-code)}
.question-code pre:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
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
.fill-fields{display:grid;gap:12px;margin:4px 0}
.fill-field{display:grid;gap:5px;font-family:var(--font-paper)}
.fill-fields.fill-inline{display:block;line-height:2}
.fill-inline .fill-field{display:inline-grid;vertical-align:middle;max-width:100%;margin:.3em .5em}
.fill-help{color:var(--mut);font:16px/1.4 var(--font-chrome)}
.fill-field input{width:100%;min-width:0;min-height:44px;box-sizing:border-box;
  font:inherit;font-size:16px;padding:8px 12px;border:1px solid var(--edge);
  border-radius:8px;background:var(--card);color:inherit}
.fill-field input:focus{outline:2px solid var(--accent);outline-offset:1px;
  border-color:var(--accent)}
.fill-field input:disabled{opacity:.75}
.response-table,.response-dnd,.response-visual,.response-check{
  max-width:100%;overflow-x:auto;overscroll-behavior-inline:contain}
.inline-completion{display:block;font-family:var(--font-paper);line-height:2.5;margin:8px 0}
.inline-completion select{font:inherit;min-height:44px;max-width:100%;margin:0 6px;
  border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.inline-completion select:focus{outline:2px solid var(--accent);outline-offset:2px}
.inline-completion select.right{border-color:var(--ok);background:var(--ok-bg);color:var(--ok)}
.inline-completion select.wrong{border-color:var(--bad);background:var(--bad-bg);color:var(--bad)}
.inline-word-bank{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.inline-word-bank span{padding:8px 12px;border:1px solid var(--line);border-radius:6px;cursor:grab;overflow-wrap:anywhere}
.ordering-source{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.ordering-source .ordering-block{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:6px;padding:8px}
.ordering-source [data-ordering-block-id]{padding:8px;cursor:grab;overflow-wrap:anywhere;user-select:none}
.ordering-source [aria-disabled=true]{cursor:default;opacity:.6}
.rowline.ordering-drop-active{outline:2px dashed var(--accent);outline-offset:3px}
.assignment-buckets{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(180px,100%),1fr));gap:12px;margin:16px 0}
.assignment-bucket{border:1px dashed var(--line);border-radius:6px;padding:12px;min-height:88px;overflow-wrap:anywhere}
.assignment-bucket.is-over{border-color:var(--accent);background:var(--card)}
.assignment-bucket h2{font-size:16px;margin:0 0 8px}
.assignment-bucket ul{margin:0;padding-left:20px}
.drag-card{cursor:grab;border:1px solid var(--line);border-radius:6px;padding:8px}
.drag-card:active{cursor:grabbing}
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
.question-assist{margin:0 0 var(--space-4);padding:var(--space-2) var(--space-3);
  border:1px solid var(--accent);border-radius:var(--r-2);background:var(--accent-soft)}
.question-assist summary{cursor:pointer;min-height:44px;display:flex;align-items:center;
  gap:var(--space-2);font:600 var(--text-body)/1.4 var(--font-chrome);color:var(--ink)}
.question-assist-count{font:var(--text-xs)/1.4 var(--font-ledger);color:var(--accent);
  text-transform:uppercase;letter-spacing:.06em}
.question-assist-note{margin:0 0 var(--space-2);font:var(--text-xs)/1.5 var(--font-ledger);
  color:var(--mut)}
.question-assist .hint-ladder{margin-bottom:var(--space-1)}
.question-assist .hint-card{background:var(--card);border-left:4px solid var(--accent)}
.question-assist .hint-card[data-hint-kind="trap"]{border-left-style:double}
.question-assist .hint-card[data-hint-kind="rationale"]{border-left-style:dashed}
.question-assist .hint-card[data-hint-kind="reveal"]{border-left-width:7px}
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
/*__LATEX_INPUT_CSS__*/
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
.quiz-math-source{font-family:var(--font-code);font-size:var(--text-body);
  background:var(--chip);border:1px solid var(--line);border-radius:var(--r-1);
  padding:2px 6px;white-space:nowrap}
.quiz-math-display{max-width:100%;overflow-x:auto;overflow-y:hidden;
  padding:var(--space-1) 0}
.quiz-math-note{font:var(--text-xs)/1.5 var(--font-ledger);color:var(--mut);
  margin:var(--space-2) 0 0}
.question-symbols{margin:0 0 var(--space-3);padding:var(--space-2) var(--space-3);
  border:1px solid var(--line);border-radius:var(--r-1);background:var(--chip)}
.question-symbols h2{margin:0 0 var(--space-2);font:var(--text-xs)/1.5 var(--font-ledger);
  letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.question-symbol-note{margin:calc(-1 * var(--space-1)) 0 var(--space-2);
  font:var(--text-xs)/1.5 var(--font-ledger);color:var(--mut)}
.question-symbol-list{display:flex;gap:var(--space-2);flex-wrap:wrap;margin:0;padding:0;
  list-style:none}
.question-symbol-list a,.question-symbol-static{display:inline-flex;align-items:baseline;
  gap:var(--space-1);min-height:44px;padding:8px 12px;border:1px solid var(--line);
  border-radius:999px;background:var(--card);color:var(--ink);text-decoration:none}
.question-symbol-list .symbol{font:600 20px/1 var(--font-code);color:var(--accent)}
.question-symbol-list .meaning{font:var(--text-xs)/1.4 var(--font-ledger);color:var(--mut)}
.question-symbol-def{font-family:var(--font-paper);font-size:var(--text-body)}
__GLOSS_CSS__
@media (max-width:767px){
  .wrap{max-width:100%;padding:18px 16px 80px}
  .context-line{gap:2px 12px}
  h1.stem{font-size:20px}
  .feedback{min-height:120px}
  .feedback:empty{min-height:0}
  .context-line .objective,.context-line .mode,.context-line .lesson{display:none}
}
@media (max-width:520px){
  .quiz-argument-line{grid-template-columns:1fr;gap:var(--space-1)}
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
.activity-facts{display:flex;flex-wrap:wrap;gap:var(--space-2) var(--space-4);
  margin:var(--space-2) 0 0}
.activity-facts div{min-width:10rem}.activity-facts dt{font-size:12px;color:var(--mut)}
.activity-facts dd{margin:2px 0 0;font-size:16px}
__PRODUCT_CSS__
</style>
__MATH_ASSETS__
</head><body><div class="wrap overhaul-quiz" data-presentation-profile="__PRESENTATION_PROFILE__">__PRODUCT_NAV__
<nav class="context-line" data-surface-context aria-label="Session context">
  <span class="cx" id="cx-bank">__CTX_BANK__</span>
  <span class="cx objective" id="cx-objective"></span>
  <span class="cx mono">Item <b id="pos">1</b> of <b id="tot">__CTX_TOTAL__</b></span>
  <span class="cx mode" id="cx-mode">__CTX_MODE__</span>
  <span class="cx lesson" id="cx-lesson"></span>
</nav>
<details class="session-details">
  <summary>Session details</summary>
  <div id="detail-body" class="detail-body"></div>
  <dl class="activity-facts"><div><dt>Purpose</dt><dd id="activity-purpose">__CTX_MODE__</dd></div>
  <div><dt>Response format</dt><dd id="activity-response">Response</dd></div>
  <div><dt>Disclosure</dt><dd id="activity-disclosure">Feedback follows session policy</dd></div></dl>
  <p class="hint" id="activity-instructions">Follow the response instructions below.</p>
</details>
__LTI_FRAMING__
<main class="overhaul-question-workspace" aria-label="Active question"><div id="host"></div></main>
<div id="assist-slot">__ASSIST__</div>
</div>
__CM6_TAG__
__CM6_BOOT__
<script>window.ItembankQuestionSymbols=__QUESTION_SYMBOLS__;</script>
__QUESTION_SYMBOLS_SCRIPT__
__LATEX_INPUT_SCRIPT__
<script id="offline">
__OFFLINE_JS__
</script>
<script id="served">
__SERVED_JS__
</script>
<script id="assist">
__ASSIST_JS__
</script>
__STRUCTURE_SCRIPT__
__MATH_SCRIPT__
__GLOSS_SCRIPT__
</body></html>"""


LATEX_INPUT_JS = resources.read_text("surfaces/assets/quiz/latex-input.js")


QUESTION_SYMBOLS_JS = resources.read_text("surfaces/assets/quiz/question-symbols.js")


# Structured question presentation is progressive enhancement over the exact
# authored text. Deliberate newlines remain visible through CSS. This adapter
# handles the common logic form whose stem explicitly names an argument and
# quotes premises followed by Therefore, Thus, or Hence. It never classifies
# unlabeled prose or changes the stored stem, scoring, or evidence.
STRUCTURE_ADAPTER_JS = resources.read_text("surfaces/assets/quiz/structure-adapter.js")


# Quiz math is a presentation-only extension of the lesson reader's vendored
# KaTeX path. The observer covers both the server-rendered baseline and later
# client-rendered items. Backticks already denote expressions in authored math
# banks, so the adapter upgrades them without changing stored question text.
# Every failure leaves the raw expression visible.
MATH_ADAPTER_JS = resources.read_text("surfaces/assets/quiz/math-adapter.js")


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
ASSIST_JS = (resources.read_text("surfaces/assets/quiz/assist.js"))


def _prefilled(prefill, name):
    """The last value the learner submitted under this control name, or "".

    `prefill` is the raw submitted form mapping, presentation state only: it
    is echoed back into the controls so a failed POST does not throw away what
    was typed. It never reaches the scorer, the session, or evidence.
    """
    values = (prefill or {}).get(name) or []
    return values[-1] if values else ""


def _form_controls(item, prefill=None, entry_error=False):
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
        matching = item.get("matching")
        labels = {c["id"]: c["text"] + " (" + c["id"] + ")" for c in (matching or {}).get("choices", [])}
        rows = []
        for n, row in enumerate(item.get("rows") or []):
            was = _prefilled(prefill, "row_%d" % n)
            opts = ''.join('<option value="%s"%s>%s</option>' %
                           (html.escape(str(c), quote=True),
                            " selected" if str(c) == was else "",
                            html.escape(labels.get(c, str(c)))) for c in cats)
            text = str(row.get("text", ""))
            if matching:
                rows.append('<label class="inline-completion"><span>%s (%s)</span><select name="row_%d" data-row-id="%s"><option value=""></option>%s</select></label>' %
                            (html.escape(text), html.escape(str(row["id"])), n, html.escape(str(row["id"]), quote=True), opts))
                continue
            if t == "dnd" and text.count("___") == 1:
                before, after = text.split("___")
                rows.append('<label class="inline-completion">%s<select name="row_%d" '
                            'data-row-id="%s" aria-label="Blank %d: %s"><option value=""></option>%s</select>%s</label>' %
                            (html.escape(before), n, html.escape(str(row.get("id", n)), quote=True), n + 1, html.escape(text, quote=True),
                             opts, html.escape(after)))
                continue
            rows.append('<label class="rowline"><span class="rowtext">%s</span><select name="row_%d" data-row-id="%s">'
                        '<option value=""></option>%s</select></label>' %
                        (html.escape(str(row.get("text", ""))), n, html.escape(str(row.get("id", n)), quote=True), opts))
        if matching:
            return '<fieldset data-matching-reuse="%s" data-matching-signature="%s"><legend>Match every row. %s Unused choices are allowed.</legend>%s</fieldset>' % (
                matching["reuse"], html.escape(json.dumps([matching, item["rows"]], ensure_ascii=False, separators=(",", ":")), quote=True), "Use each choice once." if matching["reuse"] == "once" else "Choices can be reused.", "".join(rows))
        return "".join(rows)
    if t == "build":
        if item.get("ordering"):
            blocks = item.get("blocks") or []
            signature = json.dumps([item["ordering"], sorted(blocks, key=lambda block: block["id"])], ensure_ascii=False, separators=(",", ":"))
            rows = []
            for n in range(len(blocks)):
                options = ''.join('<option value="%s"%s>%s (%s)</option>' % (
                    html.escape(block["id"], quote=True),
                    " selected" if block["id"] == _prefilled(prefill, "step_%d" % n) else "",
                    html.escape(block["text"]), html.escape(block["id"])) for block in blocks)
                rows.append('<label class="rowline"><span class="rowtext">Position %d</span>'
                            '<select name="step_%d" aria-label="Position %d"><option value=""></option>%s</select></label>'
                            % (n + 1, n, n + 1, options))
            return '<fieldset data-ordering-signature="%s"><legend>Arrange the selected blocks. Leave unused blocks in the source area.</legend>%s</fieldset>' % (html.escape(signature, quote=True), "".join(rows))
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
    if t == "fill":
        rows = []
        inline = {}
        for field in item.get("fields") or []:
            field_id = str(field.get("id", ""))
            label = str(field.get("label", field_id))
            name = "fill_" + field_id
            value = _prefilled(prefill, name)
            if field.get("kind") == "polynomial":
                checker = field.get("checker") or {}
                help_text = str(checker.get("grammar", "Use x, numbers, explicit * and powers 0 to 4."))
                help_text += " Expand products. Example: 3*x^2 + 4*x + 1. Maximum 160 characters."
            elif field.get("kind") == "text":
                case = ("Case matters." if field.get("case_sensitive", True)
                        else "Uppercase and lowercase are treated the same.")
                whitespace = {
                    "exact": "Spaces count exactly as typed.",
                    "collapse": "Repeated spaces are treated as one.",
                    "trim": "Leading and trailing spaces are ignored.",
                }.get(field.get("whitespace", "trim"), "")
                help_text = "%s %s" % (case, whitespace)
            else:
                help_text = "Enter a decimal, fraction, or scientific number."
                units = field.get("units") or []
                if units:
                    help_text += " Add a space, then one of: %s." % ", ".join(
                        str(unit) for unit in units)
            rows.append(
                '<label class="fill-field"><span>%s</span>'
                '<span class="fill-help" id="fill-help-%s">%s</span>'
                '<input type="text" name="%s" value="%s" autocomplete="off" '
                'inputmode="text" maxlength="4096" aria-describedby="fill-help-%s%s"%s></label>' %
                (html.escape(label), html.escape(field_id, quote=True), html.escape(help_text), html.escape(name, quote=True),
                 html.escape(value, quote=True), html.escape(field_id, quote=True),
                 " fill-entry-error" if entry_error else "", ' aria-invalid="true"' if entry_error else ""))
            inline[field_id] = rows[-1]
        if item.get("fill_layout") == "inline":
            sentence = re.sub(r"\{\{([a-z][a-z0-9_]{0,31})\}\}",
                              lambda match: inline[match.group(1)],
                              html.escape(item["stem"]))
            return '<div class="fill-fields fill-inline">%s</div>' % sentence
        return '<div class="fill-fields">%s</div>' % "".join(rows)
    label = "Code response" if t == "check" else "Your response"
    value = _prefilled(prefill, "answer")
    if t == "check" and not value:
        value = item.get("starter", "")
    input_format = item.get("input_format") or schema.get("format") or "plain"
    return ('<label>%s<textarea class="ans" name="answer" data-input-format="%s">'
            '%s</textarea></label>' %
            (label, html.escape(str(input_format), quote=True), html.escape(value)))


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


def _ordering_card(diagnostic):
    """Present only a runtime-released construction category."""
    if not isinstance(diagnostic, dict) or diagnostic.get("version") != 1:
        return ""
    message = {
        "missing_required": "A required block is missing. Review the selected blocks.",
        "selected_distractor": "An unneeded block is selected. Review which blocks belong in the answer.",
        "dependency_violation": "A block appears before a prerequisite. Review the order.",
    }.get(diagnostic.get("category"))
    return '<p data-ordering-diagnostic>%s</p>' % html.escape(message) if message else ""


def _hint_card(row, locked=False):
    body = " ".join(row.get("unlock_copy") or []) if locked else row.get("display", "")
    return '<li class="hint-card %s" data-hint-kind="%s"><h4>%s</h4><p>%s</p></li>' % (
        "locked" if locked else "shown",
        html.escape(str(row.get("name", "")), quote=True),
        html.escape(str(row.get("header", ""))), html.escape(str(body)))


def _question_assist_html(teaching):
    """Place only runtime-disclosed help beside the stable question.

    The original stem remains above this native disclosure. Collapsing it is
    the script-free original-only view. Locked tiers stay in the Help region,
    so proximity never widens disclosure or lets presentation imply a tier.
    """
    shown = list((teaching or {}).get("shown") or [])
    if not shown:
        return ""
    count = len(shown)
    return ('<details class="question-assist" data-question-assist open>'
            '<summary>Assisted question <span class="question-assist-count">'
            '%d %s</span></summary>'
            '<p class="question-assist-note">These runtime-issued cues add to the question. '
            'Collapse this layer to reread the untouched wording.</p>'
            '<ol class="hint-ladder">%s</ol></details>' %
            (count, "cue" if count == 1 else "cues",
             "".join(_hint_card(row) for row in shown)))


def _question_symbols_html(item, rows):
    """Script-free served baseline for authored question symbol links."""
    if not rows:
        return ""
    entries = []
    for row in rows:
        panel = "question-gloss-%s-%s" % (item.get("id", "item"), row["slug"])
        if "definition" in row:
            control = ('<span class="question-symbol-static"><span class="symbol">%s</span>'
                       '<span class="question-symbol-def">%s</span></span>' %
                       (html.escape(str(row.get("symbol", ""))),
                        html.escape(str(row.get("definition", "")))))
        else:
            control = ('<a class="term" href="%s" data-gloss-fetch="%s" '
                       'aria-details="%s"><span class="symbol">%s</span>'
                       '<span class="meaning">%s</span></a>'
                       '<div id="%s" class="gloss" popover>'
                       '<p class="gloss-term">%s</p>'
                       '<p class="gloss-def" data-gloss-state="pending">'
                       'Open to load the definition.</p>'
                       '<p class="gloss-more"><a href="%s">Open the definition page</a></p>'
                       '</div>' %
                       (html.escape(str(row.get("href", "")), quote=True),
                        html.escape(str(row.get("fetch", "")), quote=True),
                        html.escape(panel, quote=True),
                        html.escape(str(row.get("symbol", ""))),
                        html.escape(str(row.get("label", "meaning"))),
                        html.escape(panel, quote=True),
                        html.escape(str(row.get("symbol", ""))),
                        html.escape(str(row.get("href", "")), quote=True)))
        entries.append("<li>%s</li>" % control)
    return ('<section class="question-symbols" aria-label="Symbols in this question">'
            '<h2>Symbols in this question</h2>'
            '<p class="question-symbol-note">Shown in reading order. Open one for its course meaning, not the answer.</p>'
            '<ul class="question-symbol-list">%s</ul>'
            '</section>' % "".join(entries))


def _activity_card(activity, completed=False):
    """Render only the runtime's public case context and own commitment."""
    if not activity:
        return ""
    stage = activity.get("stage")
    own = ('<p data-committed-answer>Your committed answer: <b>%s</b>.</p>' %
           html.escape(str(activity["committed_answer"]))) if "committed_answer" in activity else ""
    instruction = "Both responses committed. Review each response below." if completed else "Commit each response once. Feedback follows both commitments."
    return ('<section class="staged-context" data-activity-stage="%s" '
            'aria-label="Answer and reason"><p>%s</p><p><b>%s</b> %s</p>%s</section>' %
            (html.escape(str(stage), quote=True), html.escape(str(activity.get("stimulus", ""))),
             "Answer and reason complete." if completed else "Step 1 of 2: answer." if stage == "answer" else "Step 2 of 2: reason.", instruction, own))


def _activity_feedback(rows):
    """Each released child keeps its own verdict, never a combined score."""
    if not isinstance(rows, list):
        return ""
    out = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        ex = row.get("explain") or {}
        verdict = "Correct." if row.get("score") is True else "Not correct." if row.get("score") is False else "Recorded."
        out.append('<section data-child-feedback><h2>%s feedback</h2><p>%s</p><p>%s</p><p>%s</p></section>' %
                   ("Answer" if index == 0 else "Reason", verdict,
                    html.escape(str(ex.get("answer_text", ""))), html.escape(str(ex.get("why", "")))))
    return "".join(out)


def _check_feedback_html(result):
    """Display only runtime-released observations, without running or scoring."""
    rows = (result.get('interaction_result') or {}).get('observations') or []
    if not isinstance(rows, list) or not rows:
        return ''
    saved = ''
    if result.get('saved_check_feedback'):
        source = (result.get('interaction_result') or {}).get('response', '')
        saved = ('<p>Saved run. Current edits have not been checked.</p>'
                 '<details><summary>Code from this run</summary><pre>%s</pre></details>'
                 % html.escape(str(source)))
    labels = {'passed': 'Passed', 'wrong_output': 'Output differs',
              'runtime_error': 'Program stopped', 'timeout': 'Time limit reached',
              'output_cap': 'Output limit reached'}
    out = [saved, '<div class="check-matrix" role="list" aria-label="Execution observations">']
    for row in rows:
        if not isinstance(row, dict):
            continue
        status = labels.get(row.get('reason'), 'Observation')
        cls = 'right' if row.get('passed') else 'wrong'
        out.append('<div class="case %s" role="listitem"><div class="case-head">'
                   '<span class="case-n">Case %s</span><span class="st">%s</span></div>'
                   % (cls, html.escape(str(row.get('case_index', ''))), html.escape(status)))
        for key, label in (('input', 'Input'), ('expected', 'Expected'), ('actual', 'Actual'), ('stderr', 'Program error')):
            if key in row:
                if key == 'expected' and row.get('expected_kind') == 'pattern':
                    label = 'Expected (pattern)'
                out.append('<div class="cf"><h5>%s</h5><pre>%s</pre></div>'
                           % (label, html.escape(str(row[key]))))
        out.append('</div>')
    out.append('</div>')
    return ''.join(out)


def baseline_for(view, teaching_result, post_path, tokens, flash=None, prefill=None,
                 continue_href=None, continue_label=None, symbol_help=None):
    """Pure, key-free HTML adapter over public runtime projections.

    `prefill` is the raw form mapping of a submission that did not go through
    (an expired token, a refused body), echoed back into the controls so the
    learner does not lose what they wrote. Presentation state, never truth.
    """
    item = (view or {}).get("item")
    if not item:
        return '<div class="done empty" data-server-baseline>Session complete.</div>'
    teaching = (teaching_result or {}).get("teaching") or {}
    symbols = _question_symbols_html(
        item, (symbol_help or {}).get(item.get("id"), []))
    assisted = _question_assist_html(teaching)
    response_type = item.get("type", "")
    format_label = RESPONSE_FORMAT_LABELS.get(response_type, "Response")
    instructions = RESPONSE_FORMAT_INSTRUCTIONS.get(
        response_type, "Follow the response instructions below.")
    if item.get("ordering"):
        format_label = "Ordering response"
        instructions = "Arrange the selected blocks in order. Leave unused blocks in the source area."
    feedback = _activity_feedback((view or {}).get("activity_feedback"))
    activity = (view or {}).get("activity")
    activity_html = _activity_card(activity, bool((flash or {}).get("activity_feedback")))
    activity_fields = ""
    if activity:
        activity_fields = "".join('<input type="hidden" name="%s" value="%s">' %
                                  (name, html.escape(str(activity.get(name, "")), quote=True))
                                  for name in ("activity_id", "child_id", "submission_token"))
    if isinstance(flash, dict):
        if flash.get("refused"):
            feedback = '<div id="fill-entry-error" class="refused pend" role="alert">%s</div>' % html.escape(str(flash["refused"]))
        elif flash.get("action") == "hold":
            feedback = '<div class="verdict n">Not correct. Re-read the question, then try another answer or open the next hint.</div>'
            feedback += _selection_card(flash.get("selection_feedback"))
            feedback += _ordering_card(flash.get("ordering_diagnostic"))
        elif flash.get("action") == "defer_feedback":
            if activity:
                feedback = '<div class="pend">Answer committed. Commit your reason to release feedback.</div>'
            elif response_type == 'check' and (flash.get('interaction_result') or {}).get('observations'):
                feedback = '<div class="pend">The run stopped. Review the observations and repair your code. No correctness verdict was settled.</div>'
            elif response_type == "short" and continue_href:
                feedback = (
                    '<div class="pend"><b>Response recorded, pending human review.</b>'
                    ' You can finish this sitting. The response is not scored yet.</div>')
            elif response_type == "short":
                feedback = (
                    '<div class="pend"><b>Recorded, and waiting on a mark.</b>'
                    '<div>A constructed response is not scored by the machine.'
                    ' It remains pending until a human marker records a verdict.'
                    ' No model answer is shown now.</div></div>')
            else:
                feedback = ('<div class="pend"><b>Response recorded.</b> '
                            'Feedback is available after the sitting closes.</div>')
        elif flash.get("action") in ("advance", "complete"):
            score = flash.get("score")
            feedback = '<div class="%s">%s</div>' % (
                "pend" if score is None else "verdict " + ("y" if score else "n"),
                "Recorded. Not marked here." if score is None else
                ("Correct. Your answer was recorded." if score else
                 "Not correct. Your answer was recorded."))
        if flash.get("activity_feedback"):
            feedback = _activity_feedback(flash["activity_feedback"])
        if response_type == 'check':
            feedback += _check_feedback_html(flash)
    # The served form uses PRG. The runtime may already hold the next cursor
    # after accepting this answer, but the learner must first see the verdict
    # for the item they just answered. This pause is presentation only: the
    # explicit link resumes the runtime's current item without a second submit.
    if continue_href:
        action = ('<div class="act"><a class="go" data-feedback-continue '
                  'href="%s">%s</a></div>' %
                  (html.escape(continue_href, quote=True),
                   html.escape(continue_label or "Continue")))
        return ('<div class="card overhaul-question" data-server-baseline data-feedback-pause '
                'data-session-id="%s" data-item-id="%s" data-response-type="%s" '
                'data-objective="%s" data-lesson-slug="%s">'
                '%s%s<p class="hint"><b>%s.</b> %s</p>'
                '<div class="feedback" role="status" aria-live="polite">%s</div>%s</div>' %
                (html.escape(str(view.get("session_id", "")), quote=True),
                 html.escape(str(item.get("id", "")), quote=True),
                 html.escape(str(response_type), quote=True),
                 html.escape(str(item.get("objective", "")), quote=True),
                 html.escape(str(item.get("lesson_slug", "")), quote=True),
                 question_stem_html(re.sub(r"\{\{[a-z][a-z0-9_]{0,31}\}\}", "____", str(item.get("stem", ""))) if item.get("fill_layout") == "inline" else str(item.get("stem", ""))), symbols,
                 html.escape(format_label),
                html.escape(instructions), activity_html + feedback, action))
    ladder = ""
    if teaching.get("available"):
        cards = ""
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
        if cards or action:
            ladder = '<section class="support-region"><h3 class="hint-heading">Help</h3>' \
                     '<ol class="hint-ladder">%s</ol>%s</section>' % (cards, action)
    elif teaching.get("unavailable_reason"):
        ladder = '<section class="support-region"><p class="assist-copy">%s</p></section>' % \
                 html.escape(str(teaching["unavailable_reason"]))
    submit = ('' if response_type == "visual" else
              '<div class="act"><button class="go" type="submit">Submit answer</button></div>')
    return ('<div class="card overhaul-question" data-server-baseline data-session-id="%s" data-item-id="%s" '
            'data-response-type="%s" data-objective="%s" data-lesson-slug="%s" data-presentation-signature="%s">'
            '%s%s%s<p class="hint"><b>%s.</b> %s</p>'
            '<form method="post" action="%s" class="overhaul-response" data-answer-form>%s'
            '<input type="hidden" name="form_token" value="%s"><input type="hidden" name="action" value="submit">'
            '<div class="feedback" role="status" aria-live="polite">%s</div>'
            '%s</form>%s</div>' %
            (html.escape(str(view.get("session_id", "")), quote=True),
             html.escape(str(item.get("id", "")), quote=True),
             html.escape(str(response_type), quote=True),
             html.escape(str(item.get("objective", "")), quote=True),
             html.escape(str(item.get("lesson_slug", "")), quote=True),
             hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode("utf-8")).hexdigest(),
             question_stem_html(re.sub(r"\{\{[a-z][a-z0-9_]{0,31}\}\}", "____", str(item.get("stem", ""))) if item.get("fill_layout") == "inline" else str(item.get("stem", ""))), symbols, assisted,
             html.escape(format_label), html.escape(instructions),
             html.escape(post_path, quote=True), activity_html + activity_fields + _form_controls(item, prefill, bool((flash or {}).get("refused"))),
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
OFFLINE_JS = QUESTION_STEM_JS + resources.read_text("surfaces/assets/quiz/offline.js")


# The daemon-served client (SURF-02): starts and submits through the canonical
# /api/* JSON session API. This script contains no scoring, no canonicalization,
# no key material, and no full item array -- it renders only what the server
# returns. Presentation state (selection, current item, position) is managed
# here; every verdict and every explanation comes from /api/submit.
SERVED_JS = QUESTION_STEM_JS + resources.read_text("surfaces/assets/quiz/served.js")
