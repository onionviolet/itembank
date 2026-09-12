#!/usr/bin/env python3
"""Build the reversible course-preparation occurrence prototype."""
import hashlib
import html
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import course
import journal
from surfaces import course_ops

SOURCE_NAME = "source.md"
LOCATOR = "source.md#reading-range"
SOURCE_TEMPLATE = os.path.join(ROOT, "prototypes", "course-preparation", SOURCE_NAME)


def fingerprint(path):
    with open(path, "rb") as stream:
        return hashlib.sha256(stream.read()).hexdigest()


def build_fixture(root):
    course_ops.run(root, "create", {"course_id": "tides", "title": "Tide Reading Lab"})
    base = os.path.join(root, "tides")
    sources = os.path.join(base, "sources")
    os.makedirs(sources, exist_ok=True)
    source_path = os.path.join(sources, SOURCE_NAME)
    shutil.copyfile(SOURCE_TEMPLATE, source_path)
    linked = journal.op_link(base, "source", "sources/" + SOURCE_NAME,
                             "human", "prototype-builder")
    source_id = linked["object_id"]
    course_ops.run(root, "add_source",
                   {"course_id": "tides", "source_object_id": source_id,
                    "title": "Tide table field note"}, actor_name="prototype-builder")
    course_ops.run(root, "rights",
                   {"course_id": "tides", "source": source_id,
                    "grants": {"read": "granted"}}, actor_name="prototype-builder")
    container = course_ops.run(root, "add_container",
                               {"course_id": "tides", "label": "unit",
                                "title": "Reading local tables"},
                               actor_name="prototype-builder")
    objective = course_ops.run(root, "add_objective",
                               {"course_id": "tides",
                                "container": container["container_id"],
                                "statement": "Distinguish observation and prediction times."},
                               actor_name="prototype-builder")
    course_ops.run(root, "bind",
                   {"course_id": "tides", "objective": objective["objective_id"],
                    "source": source_id, "locator": LOCATOR,
                    "state": "covered", "confidence": "high",
                    "binding_kind": "treatment", "treatment": "direct-reading"},
                   actor_name="prototype-builder")
    doc = course.read_course(base)
    binding = doc["doc"]["bindings"][-1]
    return {"base": base, "course_path": os.path.join(base, course.COURSE_SIDECAR_FILENAME),
            "source_path": source_path, "source_id": source_id,
            "objective_id": objective["objective_id"], "binding": binding,
            "course_fingerprint": doc["fingerprint"],
            "source_fingerprint": fingerprint(source_path)}


def occurrences(fixture):
    common = {"course_id": "tides", "objective_id": fixture["objective_id"],
              "source_id": fixture["source_id"], "source_fingerprint": fixture["source_fingerprint"],
              "locator": LOCATOR, "binding": dict(fixture["binding"])}
    return [
        dict(common, occurrence_id="occ-preread-tides", title="Read the assigned tide note",
             preparation_mode="preread", path_role="required-instructor-work",
             learning_phase="Ahead", activation="Now", sequence_evidence="Bounded",
             purpose="Separate observation time from prediction time."),
        dict(common, occurrence_id="occ-prelearn-tides", title="Deepen the same source",
             preparation_mode="prelearn", path_role="recommended-preparation",
             learning_phase="Deepen", activation="Now", sequence_evidence="Bounded",
             purpose="Explain why missing timezone metadata blocks comparison."),
        dict(common, occurrence_id="occ-library-tides", title="Optional reference copy",
             preparation_mode="none", path_role="optional-enrichment",
             learning_phase="not-applicable", activation="Library",
             sequence_evidence="Published", purpose="Keep the source available for later."),
    ]


def resolve(occurrence, fixture, rights="granted", online=True,
            locator=LOCATOR, source_fingerprint=None):
    if rights != "granted":
        return "rights-refused", "Reading is not authorized. Review source rights."
    if not online and occurrence.get("remote_only"):
        return "offline-remote", "This source is remote-only. Reconnect or use an accepted local copy."
    if source_fingerprint not in (None, fixture["source_fingerprint"]):
        return "revision-conflict", "The accepted source revision changed. Review the new revision."
    if locator != LOCATOR:
        return "locator-missing", "The assigned range is unavailable. Return to the activity and repair its locator."
    return "available", "Open the accepted bounded range."


def render_page(fixture):
    rows = occurrences(fixture)
    now = [row for row in rows if row["activation"] == "Now"]
    activity_buttons = "".join("""<button class=\"path-item%s\" data-occurrence=\"%s\">
<span class=\"path-index\">%02d</span><span><strong>%s</strong><small>%s · %s</small></span>
<span class=\"path-state\" data-status=\"%s\">%s</span></button>""" % (
        " active" if index == 0 else "", html.escape(row["occurrence_id"]), index + 1,
        html.escape(row["title"]), html.escape(row["learning_phase"]),
        html.escape(row["preparation_mode"]), html.escape(row["occurrence_id"]),
        "In progress" if index == 0 else "Ready") for index, row in enumerate(now))
    resources = "".join("""<article class=\"resource-row\"><span class=\"book\">T</span><div>
<p class=\"kicker\">%s · %s</p><h3>%s</h3><p>Accepted local Markdown · exact revision · <code>%s</code></p>
<button class=\"text-action\" data-view=\"learn\" data-occurrence=\"%s\">Open in reading desk →</button>
</div></article>""" % (html.escape(row["activation"]), html.escape(row["path_role"]),
        html.escape(row["title"]), html.escape(row["source_id"]),
        html.escape(row["occurrence_id"])) for row in rows)
    payload = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    return """<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Itembank · Tide Reading Lab</title>
<style>
:root{--paper:#f5f3ed;--surface:#fffdf8;--ink:#20363f;--muted:#697674;--line:#d7dbd2;--forest:#315b4a;--moss:#dce7bc;--indigo:#53508c;--amber:#a46b2c;--serif:Georgia,'Times New Roman',serif;--sans:Inter,ui-sans-serif,system-ui,sans-serif;--mono:'SFMono-Regular',Consolas,monospace;color-scheme:light}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 var(--sans)}button,textarea{font:inherit;color:inherit}button{cursor:pointer}button,a,textarea{min-height:44px}button:focus-visible,a:focus-visible,textarea:focus-visible{outline:3px solid var(--amber);outline-offset:3px}.skip{position:fixed;top:-5rem;z-index:20;background:var(--surface);padding:.75rem}.skip:focus{top:.5rem}.shell{min-height:100vh;display:grid;grid-template-columns:224px minmax(0,1fr)}
.side{position:sticky;top:0;height:100vh;border-right:1px solid var(--line);padding:32px 22px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:10px;font-size:22px;font-weight:750;letter-spacing:-.06em}.brandmark{width:25px;height:28px;border-radius:3px 9px 3px 3px;background:var(--ink);position:relative}.brandmark:after{content:'';position:absolute;left:6px;right:6px;top:8px;height:2px;background:var(--paper);box-shadow:0 5px var(--paper),0 10px var(--paper)}.tagline,.kicker{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}.tagline{margin:12px 0 38px}.nav{display:grid;gap:6px}.nav button{border:0;background:transparent;text-align:left;border-radius:6px;padding:10px 12px;display:flex;gap:12px;align-items:center}.nav button.active{background:#e5e9de;font-weight:650}.nav button span:first-child{width:20px;text-align:center}.side-course{margin-top:32px;padding:15px 12px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.side-course strong,.side-course small{display:block}.side-course small{color:var(--muted);font-size:11px;margin-top:4px}.local{margin-top:auto;color:var(--muted);font-size:11px}.local:before{content:'';display:inline-block;width:7px;height:7px;border-radius:50%%;background:#66846c;margin-right:8px}
.workspace{min-width:0}.topbar{height:72px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 42px;font-size:12px}.topbar div{display:flex;align-items:center;gap:12px}.badge{border:1px solid var(--line);border-radius:999px;padding:4px 10px;color:var(--muted)}.main{max-width:1440px;margin:auto;padding:34px 42px 64px}.course-head{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:25px}.course-head h1{font:46px/1.05 var(--serif);letter-spacing:-.035em;margin:5px 0}.course-head p{margin:0;color:var(--muted)}.course-number{font:74px/1 var(--serif);color:#b7c1ac}.course-tabs{display:flex;gap:26px;border-bottom:1px solid var(--line);margin-bottom:26px;overflow:auto}.course-tabs button{border:0;background:transparent;border-bottom:3px solid transparent;padding:10px 0;white-space:nowrap;color:var(--muted)}.course-tabs button.active{border-color:var(--forest);color:var(--ink);font-weight:650}
.view{display:none}.view.active{display:block}.learn-grid{display:grid;grid-template-columns:minmax(190px,260px) minmax(0,1fr) 245px;gap:28px}.panel-title{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:11px;margin-bottom:8px}.panel-title h2{font-size:13px;margin:0}.path-item{width:100%%;border:0;border-bottom:1px solid var(--line);background:transparent;text-align:left;padding:15px 3px;display:grid;grid-template-columns:32px 1fr;gap:10px;align-items:start}.path-item.active{border-left:3px solid var(--indigo);padding-left:10px;background:#ecebe3}.path-index{font:11px var(--mono);color:var(--muted)}.path-item strong,.path-item small{display:block}.path-item strong{font-size:13px}.path-item small{font-size:10px;color:var(--muted);margin-top:4px}.path-state{grid-column:2;font-size:10px;color:var(--forest)}
.reader{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:34px clamp(24px,5vw,60px);box-shadow:0 12px 35px #26372d0a}.reader h2{font:40px/1.08 var(--serif);letter-spacing:-.025em;margin:12px 0}.reader .purpose{font-size:16px;line-height:1.75;color:#52645e;border-bottom:1px solid var(--line);padding-bottom:22px}.source-chip{display:inline-flex;align-items:center;gap:8px;background:#edf0e3;border:1px solid #d7dec8;border-radius:999px;padding:4px 10px;font-size:10px}.source-text{font:18px/1.85 var(--serif);color:#344b43}.source-text h3{font:28px/1.2 var(--serif);color:var(--ink);margin:30px 0 12px}.callout{background:#edf0e3;border-left:4px solid var(--forest);padding:16px 18px;margin:26px 0}.callout strong{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase}.reader-actions{display:flex;align-items:center;justify-content:space-between;gap:12px;border-top:1px solid var(--line);padding-top:22px;margin-top:28px}.primary{border:0;border-radius:5px;background:var(--ink);color:white;padding:11px 18px}.primary:hover{background:var(--forest)}.quiet,.text-action{border:1px solid var(--line);border-radius:5px;background:transparent;padding:9px 13px}.text-action{border:0;text-decoration:underline;text-underline-offset:4px;padding-left:0}.context{border-left:1px solid var(--line);padding-left:22px}.source-cover{height:155px;background:var(--forest);color:#eef0d8;border-radius:2px 7px 7px 2px;padding:20px;box-shadow:inset 6px 0 #ffffff15;font:24px/1.15 var(--serif);margin:12px 0}.source-cover small{display:block;font:9px var(--sans);letter-spacing:.13em;margin-bottom:25px}.context p,.context details{font-size:11px;color:var(--muted)}.context textarea{width:100%%;min-height:115px;resize:vertical;border:1px solid var(--line);border-radius:5px;background:var(--surface);padding:10px}.saved{font-size:10px;color:var(--forest);margin-top:5px}.recovery{background:#f2ead9;border:1px solid #dfcba5;border-radius:5px;padding:12px;margin-top:18px}.recovery strong{color:var(--ink)}
.overview-grid{display:grid;grid-template-columns:1.5fr 1fr;gap:35px}.journey{position:relative}.journey:before{content:'';position:absolute;left:17px;top:34px;bottom:34px;width:1px;background:var(--line)}.journey-row{position:relative;display:grid;grid-template-columns:36px 1fr auto;gap:14px;align-items:center;padding:18px 0;border-bottom:1px solid var(--line)}.journey-num{z-index:1;width:35px;height:35px;border-radius:50%%;background:var(--paper);border:1px solid var(--line);display:grid;place-items:center;font:11px var(--mono)}.journey-row.current .journey-num{background:var(--forest);color:white}.journey-row h3,.resource-row h3{margin:0;font-size:14px}.journey-row p,.resource-row p{margin:3px 0;color:var(--muted);font-size:11px}.next-card{background:#e8ecdc;border:1px solid #d7dec8;border-radius:9px;padding:25px;height:max-content}.next-card h2{font:29px/1.12 var(--serif)}.resource-row{display:flex;gap:20px;padding:22px 0;border-bottom:1px solid var(--line)}.book{width:64px;height:88px;background:var(--forest);color:#e8ebcf;display:grid;place-items:center;border-radius:2px 6px 6px 2px;box-shadow:inset 6px 0 #ffffff18;font:34px var(--serif);flex:none}.resource-row code{font:10px var(--mono)}.evidence-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.evidence-card{border-top:3px solid var(--line);padding:18px 0}.evidence-card strong{font:42px var(--serif)}.evidence-card p{font-size:12px;color:var(--muted)}.boundary{border:1px solid var(--line);padding:20px;margin-top:25px;background:var(--surface)}
.mobile-nav{display:none}@media(max-width:1000px){.learn-grid{grid-template-columns:190px minmax(0,1fr)}.context{grid-column:2;border-left:0;border-top:1px solid var(--line);padding:22px 0;display:grid;grid-template-columns:180px 1fr;gap:20px}.source-cover{margin:0}.overview-grid{grid-template-columns:1fr}}
@media(max-width:720px){.shell{display:block}.side{display:none}.workspace{padding-bottom:70px}.topbar{height:61px;padding:0 20px}.main{padding:24px 18px 45px}.course-head{align-items:start}.course-head h1{font-size:36px}.course-number{display:none}.course-tabs{gap:21px}.learn-grid{display:block}.path{margin-bottom:20px}.path-item:not(.active){display:none}.reader{padding:25px 20px;border-radius:8px}.reader h2{font-size:34px}.source-text{font-size:17px}.context{display:block;border-top:1px solid var(--line);margin-top:22px;padding-top:22px}.source-cover{height:120px}.reader-actions{align-items:stretch;flex-direction:column}.reader-actions button{width:100%%}.evidence-grid{grid-template-columns:1fr}.mobile-nav{display:flex;position:fixed;z-index:10;left:0;right:0;bottom:0;height:66px;background:var(--paper);border-top:1px solid var(--line);justify-content:space-around}.mobile-nav button{border:0;background:transparent;font-size:10px;min-width:60px}.mobile-nav button span{display:block;font-size:18px}.topbar .crumb{display:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style></head><body><a class=\"skip\" href=\"#main\">Skip to learning activity</a>
<div class=\"shell\"><aside class=\"side\"><div class=\"brand\"><span class=\"brandmark\"></span>itembank</div><p class=\"tagline\">A place for understanding</p><nav class=\"nav\" aria-label=\"Workspace\"><button data-view=\"path\"><span>⌂</span>Your desk</button><button class=\"active\" data-view=\"learn\"><span>◫</span>Learn</button><button data-view=\"resources\"><span>▤</span>Resources</button><button data-view=\"evidence\"><span>◎</span>Evidence</button></nav><div class=\"side-course\"><span class=\"kicker\">Current course</span><strong>Tide Reading Lab</strong><small>2 active readings · local</small></div><p class=\"local\">Local workspace · no egress</p></aside>
<div class=\"workspace\"><header class=\"topbar\"><span class=\"crumb\">Your desk / Tide Reading Lab / Learn</span><div><span class=\"badge\">Prototype-only state</span><button class=\"quiet\" id=\"commands\">⌘ K</button></div></header><main class=\"main\" id=\"main\" tabindex=\"-1\"><header class=\"course-head\"><div><p class=\"kicker\">Course from one accepted local source</p><h1>Tide Reading Lab</h1><p>Read precisely. Keep the source close. Separate your claim from measured evidence.</p></div><span class=\"course-number\">01</span></header>
<nav class=\"course-tabs\" aria-label=\"Course areas\"><button data-view=\"path\">Path</button><button class=\"active\" data-view=\"learn\">Learn</button><button data-view=\"resources\">Resources</button><button data-view=\"evidence\">Evidence</button></nav>
<section class=\"view active\" id=\"view-learn\"><div class=\"learn-grid\"><aside class=\"path\"><div class=\"panel-title\"><h2>Now</h2><span class=\"kicker\">2 activities</span></div>%s</aside>
<article class=\"reader\"><span class=\"source-chip\">● Accepted source · exact range</span><p class=\"kicker\" id=\"reader-meta\">Ahead · preread · required instructor work</p><h2 id=\"reader-title\">Read the assigned tide note</h2><p class=\"purpose\" id=\"reader-purpose\">Separate observation time from prediction time.</p><div class=\"source-text\"><h3 id=\"reading-range\">Reading range</h3><p>An observation time and a prediction time answer different questions. Record which one a value represents before comparing two entries.</p><div class=\"callout\"><strong>Field caution</strong>When a table omits the timezone, stop and verify the source metadata. Do not silently infer local time.</div><p>This is the bounded accepted range. The rest of the source remains available in Resources without becoming assigned work.</p></div><div class=\"reader-actions\"><button class=\"quiet\" id=\"back-occurrence\">← Back to this activity</button><button class=\"primary\" id=\"mark-read\">Mark read (simulated)</button></div><p class=\"kicker\">Your declaration is descriptive. It is not a score, grade, or mastery claim.</p></article>
<aside class=\"context\"><div><p class=\"kicker\">At the source</p><div class=\"source-cover\"><small>LOCAL FIELD NOTES</small>Tide table<br>field note</div></div><div><p><strong>Synthetic local source</strong><br>Reading range · accepted revision<br><code>%s</code></p><details><summary>Inspect source and provenance</summary><p>Created for this prototype and linked through Itembank's real journal, rights, objective, and direct-reading operations.</p><a href=\"source.md#reading-range\">Open plain Markdown fallback</a></details><label class=\"kicker\" for=\"note\">A note to yourself</label><textarea id=\"note\" placeholder=\"What must you verify before comparing entries?\"></textarea><p class=\"saved\" id=\"note-state\">In-memory draft · resets on reload</p><div class=\"recovery\"><strong>Revision protected</strong><p>This activity stays on its accepted source fingerprint. A changed revision requires review instead of silently opening newer bytes.</p></div></div></aside></div></section>
<section class=\"view\" id=\"view-path\"><div class=\"overview-grid\"><div class=\"journey\"><p class=\"kicker\">From reading to evidence</p><div class=\"journey-row current\"><span class=\"journey-num\">01</span><div><h3>Read the assigned range</h3><p>Ahead · direct source reading · exact locator</p></div><button class=\"text-action\" data-view=\"learn\">Continue</button></div><div class=\"journey-row\"><span class=\"journey-num\">02</span><div><h3>Deepen the same source</h3><p>Independent occurrence · same bytes · separate status</p></div><button class=\"text-action\" data-view=\"learn\" data-occurrence=\"occ-prelearn-tides\">Open</button></div><div class=\"journey-row\"><span class=\"journey-num\">03</span><div><h3>Check the distinction</h3><p>Practice is a separate runtime activity, not simulated here</p></div><span class=\"badge\">Not started</span></div><div class=\"journey-row\"><span class=\"journey-num\">04</span><div><h3>Review evidence</h3><p>Reading claim, responses, and retention stay separate</p></div><button class=\"text-action\" data-view=\"evidence\">Inspect</button></div></div><aside class=\"next-card\"><p class=\"kicker\">Your next 8 minutes</p><h2>Read one range with the source beside you.</h2><p>The path is a suggestion. It does not invent completion or lock you out of Resources.</p><button class=\"primary\" data-view=\"learn\">Open the reading →</button></aside></div></section>
<section class=\"view\" id=\"view-resources\"><p class=\"kicker\">Your material, in context</p><h2>One source. Three deliberate uses.</h2><p>All activities resolve the same accepted identity and bytes. Library stays available here without appearing in Now.</p>%s<div class=\"recovery\"><strong>Recovery states are not one generic error.</strong><p>Denied rights asks for a rights review. A missing locator asks for range repair. A divergent revision asks for comparison. Remote-only content while offline asks for reconnection or an accepted local copy.</p></div></section>
<section class=\"view\" id=\"view-evidence\"><p class=\"kicker\">What this course knows, and what it does not</p><h2>Evidence without inflated certainty.</h2><div class=\"evidence-grid\"><article class=\"evidence-card\"><strong id=\"read-count\">0 / 2</strong><p>reading occurrences marked by you in this temporary view</p></article><article class=\"evidence-card\"><strong>0</strong><p>assessment responses. No scorer is connected to this prototype.</p></article><article class=\"evidence-card\"><strong>?</strong><p>retention and mastery. Neither can be inferred from opening or marking a reading.</p></article></div><div class=\"boundary\"><h3>Zero-mutation boundary</h3><p>The generated prototype records no course, source, evidence, score, or schema changes. Notes and marked-read state live only in this page's JavaScript memory and reset on reload.</p></div></section></main></div></div>
<nav class=\"mobile-nav\" aria-label=\"Mobile workspace\"><button data-view=\"path\"><span>⌂</span>Path</button><button data-view=\"learn\"><span>◫</span>Learn</button><button data-view=\"resources\"><span>▤</span>Resources</button><button data-view=\"evidence\"><span>◎</span>Evidence</button></nav>
<script>const OCCURRENCES=%s;const state=new Map(OCCURRENCES.map(o=>[o.occurrence_id,'not-reported']));let current=OCCURRENCES[0];
function show(name){document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id==='view-'+name));document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));document.querySelector('#main').focus({preventScroll:true});}
function select(id){const row=OCCURRENCES.find(o=>o.occurrence_id===id);if(!row||row.activation==='Library')return;current=row;document.querySelectorAll('.path-item').forEach(b=>b.classList.toggle('active',b.dataset.occurrence===id));document.querySelector('#reader-title').textContent=row.title;document.querySelector('#reader-purpose').textContent=row.purpose;document.querySelector('#reader-meta').textContent=row.learning_phase+' · '+row.preparation_mode+' · '+row.path_role;document.querySelector('#mark-read').textContent=state.get(id)==='marked-read'?'Marked read, simulated':'Mark read (simulated)';show('learn');}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.occurrence)select(b.dataset.occurrence);else show(b.dataset.view)}));document.querySelectorAll('[data-occurrence]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.occurrence)));
document.querySelector('#mark-read').addEventListener('click',()=>{state.set(current.occurrence_id,'marked-read');document.querySelectorAll('[data-status="'+current.occurrence_id+'"]').forEach(s=>s.textContent='Marked read');document.querySelector('#mark-read').textContent='Marked read, simulated';document.querySelector('#read-count').textContent=[...state.values()].filter(v=>v==='marked-read').length+' / 2';});document.querySelector('#back-occurrence').addEventListener('click',()=>document.querySelector('[data-occurrence="'+current.occurrence_id+'"]').focus());document.querySelector('#note').addEventListener('input',e=>document.querySelector('#note-state').textContent=e.target.value?'Draft held in page memory · resets on reload':'In-memory draft · resets on reload');document.querySelector('#commands').addEventListener('click',()=>alert('Prototype command layer: Path, Learn, Resources, Evidence. No external action is available.'));</script></body></html>""" % (activity_buttons, html.escape(fixture["source_id"]), resources, payload)


def snapshot(fixture):
    evidence_dir = os.path.join(fixture["base"], "_evidence")
    evidence_files = []
    if os.path.isdir(evidence_dir):
        evidence_files = sorted(os.listdir(evidence_dir))
    return {"course": fingerprint(fixture["course_path"]),
            "source": fingerprint(fixture["source_path"]),
            "evidence": evidence_files}


def build(output):
    os.makedirs(output, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="course_preparation_fixture_") as root:
        fixture = build_fixture(root)
        shutil.copyfile(fixture["source_path"], os.path.join(output, SOURCE_NAME))
        with open(os.path.join(output, "index.html"), "w", encoding="utf-8", newline="\n") as stream:
            stream.write(render_page(fixture))
        with open(os.path.join(output, "prototype-data.json"), "w", encoding="utf-8", newline="\n") as stream:
            json.dump({"occurrences": occurrences(fixture), "zero_mutation_baseline": snapshot(fixture)},
                      stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    return output


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "itembank-course-preparation")
    print(build(os.path.abspath(target)))
