"""Expected-base, atomic presentation adoption with a recoverable source patch."""
import hashlib
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TARGET = ROOT / 'surfaces/reading_desk.py'
EXPECTED = '085244b14d3becb683fa86d5d1ba9eb51a2a6962f30fd5317dc64f1ec1ae1974'

CSS = '''
.product-workspace:has(.overhaul-reading)>.product-topbar{display:none}
.product-workspace:has(.overhaul-reading)>.surface{padding-top:24px}
.product-workspace:has(.overhaul-reading)>.surface>h1{font-family:var(--font-paper);font-size:clamp(28px,3vw,40px);margin-block:16px 24px;font-weight:400}
.overhaul-reading{max-width:1200px;margin-inline:auto}
.reading-layout{display:grid;grid-template-columns:minmax(0,1fr) var(--companion-width,320px);gap:40px;align-items:start}
.reading-path{margin-bottom:16px;border-block:1px solid var(--line)}
.reading-path summary{min-height:44px;display:flex;align-items:center;cursor:pointer;font-family:var(--font-chrome)}
.reading-path a{display:block;padding:12px 0;border-top:1px solid var(--line);text-decoration:none}
.reading-path a[aria-current]{font-weight:600;color:var(--accent)}
.reading-column{min-width:0}.reading-column h2{font-family:var(--font-chrome);font-size:var(--text-xs);font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.product-workspace .reading-column.overhaul-source{background:transparent;border:0;padding:0}
.reading-source{font:var(--text-lesson,18px)/1.9 var(--font-paper,Georgia,serif);white-space:pre-wrap;overflow-wrap:anywhere;padding-block:24px;margin:16px 0;max-width:var(--measure-prose,70ch);border-block:1px solid var(--line)}
.reading-source:focus{outline:2px solid var(--accent);outline-offset:6px}
.product-workspace .reading-notes.overhaul-notes{border:1px solid var(--line);border-block-start:3px solid var(--note-mark);background:var(--card);padding:24px;position:sticky;top:88px;min-width:0;max-height:calc(100dvh - 112px);overflow-y:auto;overscroll-behavior:contain}
.reading-notes h2{font-family:var(--font-chrome);font-size:var(--text-body)}
.reading-notes textarea{box-sizing:border-box;width:100%;min-height:200px;padding:12px;font:inherit;line-height:1.6;background:var(--note-bg,var(--card));color:inherit;border:1px solid var(--line);border-radius:var(--r-1,4px);resize:vertical}
.reading-notes label{display:block;margin-block:12px 8px}
.overhaul-reading button,.overhaul-reading a{min-height:44px}.overhaul-reading button{padding:10px 16px;cursor:pointer}
.overhaul-reading :focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.reading-note{border-top:1px solid var(--line);margin-top:20px;padding-top:16px}.reading-note p{white-space:pre-wrap;overflow-wrap:anywhere}
.reading-meta{font-family:var(--font-chrome);font-size:var(--text-xs,13px);line-height:1.6;color:var(--mut)}.reading-layout code{overflow-wrap:anywhere}
.reading-toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:24px}
.reading-toolbar button{background:transparent;color:var(--ink);border:1px solid var(--line);border-radius:var(--r-1)}
.reading-toolbar button:hover{background:var(--card)}
.reading-toolbar details{position:relative}.reading-toolbar summary{padding:10px;cursor:pointer;min-height:44px;box-sizing:border-box}
.reading-width-control{position:absolute;z-index:2;background:var(--card);border:1px solid var(--line);padding:16px;width:240px;box-shadow:0 8px 24px #0002;right:0}
.reading-width-control input{width:100%;min-height:44px}.reading-toolbar details{margin-left:auto}
.reading-layout.reading-focused{grid-template-columns:minmax(0,1fr)}.reading-focused .reading-column{max-width:var(--measure-prose,70ch);margin-inline:auto}
.reading-reference{border-top:1px solid var(--line);padding-block:12px;margin-top:24px}.reading-reference summary{min-height:44px;cursor:pointer;display:flex;align-items:center;font-weight:600}
.reading-reference p{overflow-wrap:anywhere}.reading-reference .reading-return{display:block;margin-top:12px}
.overhaul-reading-recovery{margin-top:24px}.overhaul-reading-actions{padding-block:12px}
[hidden]{display:none!important}
@media(max-width:1023px){.reading-layout{grid-template-columns:minmax(0,1fr) minmax(260px,300px);gap:24px}.reading-toolbar details{display:none}}
@media(max-width:767px){.reading-layout{display:block}.product-workspace .reading-notes.overhaul-notes{position:static;margin-top:32px;padding:20px;max-height:none;overflow:visible}.reading-source{font-size:18px}.reading-toolbar #reading-focus{display:none}.reading-toolbar{gap:8px}.reading-layout.reading-focused .reading-column{max-width:none}.reading-path{margin-bottom:16px}}
'''

VIEW_SCRIPT = r'''
// View controls never save a note, declare reading, or create evidence.
const readingLayout=$('.reading-layout'),readingSource=$('#source-content'),readingCompanion=$('.reading-notes');
let passageReturn=null;
function rememberPassage(){passageReturn={y:window.scrollY};}
function showCompanion(){readingCompanion.hidden=false;readingLayout.classList.remove('reading-focused');$('#reading-focus').setAttribute('aria-pressed','false');$('#reading-focus').textContent='Focus reading';}
function returnToPassage(){readingSource.focus({preventScroll:true});if(passageReturn)window.scrollTo({top:passageReturn.y,behavior:'instant'});}
$('#reading-focus').onclick=()=>{const focus=!readingCompanion.hidden;readingCompanion.hidden=focus;readingLayout.classList.toggle('reading-focused',focus);$('#reading-focus').setAttribute('aria-pressed',String(focus));$('#reading-focus').textContent=focus?'Show companion':'Focus reading';};
$('#companion-width').oninput=e=>{const width=Number(e.target.value);if(Number.isFinite(width)&&width>=260&&width<=440){readingLayout.style.setProperty('--companion-width',width+'px');$('#companion-width-value').textContent=width+' px';}};
$('#reading-reference-open').onclick=()=>{rememberPassage();showCompanion();$('#reading-reference').open=true;$('#reading-reference summary').focus();};
$('#reading-note-open').onclick=()=>{rememberPassage();showCompanion();$('#note').focus();};
$('#reading-quote').onclick=()=>{const selection=window.getSelection(),text=selection?.toString().trim();if(!view||view.content===null||view.note_error){$('#reading-tools-state').textContent='Source or notes unavailable. Keep any existing draft.';return}if(!text||!readingSource.contains(selection.anchorNode)||!readingSource.contains(selection.focusNode)){ $('#reading-tools-state').textContent='Select words inside the source passage, then choose Add selection to draft.';return}rememberPassage();showCompanion();const field=$('#note');field.value+=(field.value?'\n\n':'')+'Source passage: '+text+'\nMy thought: ';field.dispatchEvent(new Event('input',{bubbles:true}));field.focus();$('#reading-tools-state').textContent='Selection added to your unsaved draft. Review it before saving.';};
document.querySelectorAll('.reading-return').forEach(button=>button.onclick=returnToPassage);
window.matchMedia('(max-width:767px)').addEventListener('change',event=>{if(event.matches)showCompanion()});
'''


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise SystemExit('Presentation seam changed: '+old[:60])
    return source.replace(old, new, 1)


def candidate(source):
    begin = source.index("CSS = '''")
    end = source.index("\nSCRIPT =", begin)
    source = source[:begin]+"CSS = '''\n"+CSS+"'''\n"+source[end:]
    source = replace_once(source, '\n\ndef href(', "\n\nVIEW_SCRIPT = r'''\n"+VIEW_SCRIPT+"'''\n\ndef href(")
    source = replace_once(source,
        '<div class="overhaul-reading"><p class="reading-meta overhaul-reading-recovery">This tab keeps your reading position and local unsaved draft for this source revision. Saved notes remain separate.</p><button id="resume-reading" type="button" hidden>Resume previous reading position</button>\n<div class="reading-layout"><nav class="reading-path" aria-label="Reading assignments"><details><summary>Reading assignments</summary>%s</details></nav>',
        '<div class="overhaul-reading"><nav class="reading-path" aria-label="Reading assignments"><details><summary>Reading assignments</summary>%s</details></nav>\n<div class="reading-toolbar" hidden><button id="reading-focus" type="button" aria-pressed="false">Focus reading</button><button id="reading-reference-open" type="button">Source context</button><button id="reading-note-open" type="button">Write a note</button><button id="reading-quote" type="button">Add selection to draft</button><details><summary>Reading tools</summary><div class="reading-width-control"><label for="companion-width">Companion width</label><input id="companion-width" type="range" min="260" max="440" step="20" value="320"><output id="companion-width-value" for="companion-width">320 px</output></div></details></div><p id="reading-tools-state" class="reading-meta" role="status"></p>\n<div class="reading-layout">')
    source = replace_once(source, '<h2>%s</h2><p>%s</p>', '<h2>Assigned passage</h2><p>%s</p>')
    source = replace_once(source, 'id="source-content" class="reading-source"', 'id="source-content" tabindex="-1" class="reading-source"')
    source = replace_once(source, 'aria-label="Private source notes"', 'aria-label="Private source notes" tabindex="0"')
    source = replace_once(source,
        '<details><summary>Source and revision</summary><p><code>%s</code></p><p>Occurrence <code>%s</code></p><p>Revision <code>%s</code></p></details></article>',
        '</article>')
    source = replace_once(source, '<div id="saved-notes">%s</div></aside></div></div>',
        '<div id="saved-notes">%s</div><button class="reading-return" type="button" hidden>Return to passage</button><details id="reading-reference" class="reading-reference"><summary>Source and revision</summary><p><code>%s</code></p><p>Occurrence <code>%s</code></p><p>Revision <code>%s</code></p><button class="reading-return" type="button" hidden>Return to passage</button></details></aside></div><p class="reading-meta overhaul-reading-recovery">This tab keeps your reading position and local unsaved draft for this source revision. Saved notes remain separate.</p><button id="resume-reading" type="button" hidden>Resume previous reading position</button></div>')
    source = replace_once(source, "path,esc(selected.get('preparation_mode','')),esc(title),esc(selected.get('purpose',''))", "path,esc(selected.get('preparation_mode','')),esc(selected.get('purpose',''))")
    source = replace_once(source,
        "esc(view['content'] or 'Source unavailable.'),esc(reading_status),esc((selected.get('source_ref') or {}).get('locator','Unavailable')),\n        esc(occurrence_id),esc(revision_id),esc(view['note_error'] or 'Private source notes. Shared across assignments using this source.'),saved_notes)",
        "esc(view['content'] or 'Source unavailable.'),esc(reading_status),\n        esc(view['note_error'] or 'Private source notes. Shared across assignments using this source.'),saved_notes,\n        esc((selected.get('source_ref') or {}).get('locator','Unavailable')),esc(occurrence_id),esc(revision_id))")
    source = replace_once(source, "presentation.surface_shell('Reading desk',body", "presentation.surface_shell(title,body")
    source = replace_once(source, "tail='<script>'+SCRIPT.replace('__CONTEXT__',presentation.script_safe_json(ctx))+'</script>')",
        "tail='<script>'+SCRIPT.replace('__CONTEXT__',presentation.script_safe_json(ctx))+VIEW_SCRIPT+\"\\ndocument.querySelector('.reading-toolbar').hidden=false;document.querySelectorAll('.reading-return').forEach(b=>b.hidden=false);\"+'</script>')")
    return source


if __name__ == '__main__':
    before = TARGET.read_bytes()
    expected = EXPECTED
    if '--revise' in sys.argv:
        expected = __import__('json').loads((HERE / 'recovery/operation.json').read_text())['after']
    if hashlib.sha256(before).hexdigest() != expected:
        raise SystemExit('Refusing changed base; inspect the concurrent writer first.')
    baseline = (HERE / 'recovery/reading_desk.py.txt').read_bytes() if '--revise' in sys.argv else before
    after = candidate(baseline.decode()).encode()
    compile(after, str(TARGET), 'exec')
    (HERE / 'reading_desk.candidate.py.txt').write_bytes(after)
    if '--apply' in sys.argv:
        if TARGET.read_bytes() != before:
            raise SystemExit('Concurrent base change; refusing overwrite.')
        temporary = TARGET.with_suffix('.py.ui-experience.tmp')
        temporary.write_bytes(after)
        os.replace(temporary, TARGET)
        (HERE / 'recovery/operation.json').write_text(__import__('json').dumps(dict(
            path='surfaces/reading_desk.py', before=EXPECTED,
            after=hashlib.sha256(after).hexdigest(), operation='presentation-adoption'), indent=2))
    print(hashlib.sha256(after).hexdigest())
