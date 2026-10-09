"""The supported study desk, consuming reading and notes authority."""
from surfaces import presentation, context_help
from surfaces.theme import THEME_CSS
from urllib.parse import urlencode

SOURCE_STATUS = {
    'available': 'Source available.',
    'course.reading_source_stale': 'The source changed. Refresh the course source binding before reading or saving a note. Previous wording remains available for recovery.',
}


def source_status(availability):
    return (availability.get('message') or SOURCE_STATUS.get(availability['state'])
            or 'This source range is unavailable. Refresh the course or inspect source recovery.')


CSS = '''

.product-workspace:has(.overhaul-reading)>.surface{padding-top:24px}
.product-workspace:has(.overhaul-reading)>.surface>h1{font-family:var(--font-paper);font-size:var(--text-title);margin-block:16px 24px;font-weight:600}
.overhaul-reading{max-width:1200px;margin-inline:auto}
.reading-layout{display:grid;grid-template-columns:minmax(0,1fr) var(--companion-width,320px);gap:40px;align-items:start}
.reading-path{margin-bottom:16px;border-block:1px solid var(--line)}
.reading-path summary{min-height:44px;display:flex;align-items:center;cursor:pointer;font-family:var(--font-chrome)}
.reading-path a{display:block;padding:12px 0;border-top:1px solid var(--line);text-decoration:none}
.reading-path a[aria-current]{font-weight:600;color:var(--accent)}
.reading-column{min-width:0}.reading-column h2{font-family:var(--font-paper);font-size:24px;font-weight:600;line-height:1.35}
.product-workspace .reading-column.overhaul-source{background:color-mix(in srgb,var(--source-bg) 45%,var(--paper));border:0;border-inline-start:3px solid var(--source-mark);padding:24px}
.reading-source{font:var(--text-lesson,18px)/1.9 var(--font-paper,Georgia,serif);white-space:pre-wrap;overflow-wrap:anywhere;padding-block:24px;margin:16px 0;max-width:var(--measure-prose,70ch);border-block:1px solid var(--line)}
.reading-source:focus{outline:2px solid var(--accent);outline-offset:6px}
.product-workspace .reading-notes.overhaul-notes{border:0;border-inline-start:3px solid var(--note-mark);background:var(--note-bg);padding:24px;position:sticky;top:88px;min-width:0;max-height:calc(100dvh - 112px);overflow-y:auto;overscroll-behavior:contain}
.reading-notes h2{font-family:var(--font-paper);font-size:25px;font-weight:400;font-style:italic;line-height:1.3}
.reading-notes textarea{box-sizing:border-box;width:100%;min-height:200px;padding:12px;font:inherit;line-height:1.6;background:var(--note-bg,var(--card));color:inherit;border:1px solid var(--line);border-radius:var(--r-1,4px);resize:vertical}
.reading-notes label{display:block;margin-block:12px 8px}
.overhaul-reading button,.overhaul-reading a{min-height:44px}.overhaul-reading button{padding:10px 16px;cursor:pointer}
.overhaul-reading :focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.reading-note{border-top:1px solid var(--line);margin-top:20px;padding-top:16px}.reading-note p{white-space:pre-wrap;overflow-wrap:anywhere}
.reading-meta{font-family:var(--font-chrome);font-size:var(--text-xs,13px);line-height:1.6;color:var(--mut)}.reading-layout code{overflow-wrap:anywhere}
.reading-toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.reading-toolbar button{background:transparent;color:var(--ink);border:0;border-bottom:1px solid transparent;border-radius:0}
.reading-toolbar #reading-note-open{background:var(--note-bg);border-inline-start:2px solid var(--note-mark)}
.reading-toolbar #reading-reference-open{background:var(--source-bg);border-inline-start:2px solid var(--source-mark)}
.reading-toolbar button:hover{background:var(--card);border-bottom-color:var(--line)}
.reading-toolbar details{position:relative}.reading-toolbar summary{padding:10px;cursor:pointer;min-height:44px;box-sizing:border-box}
.reading-modes{display:flex;flex-wrap:wrap;gap:4px;padding:4px;background:var(--card);border:1px solid var(--line);border-radius:var(--r-1,4px)}
.reading-modes button{border-radius:var(--r-1,4px);padding:8px 14px;font-weight:600}
.reading-modes button[aria-pressed=true]{background:var(--ink);color:var(--paper);border-bottom-color:transparent}
.reading-tools-panel{display:flex;flex-direction:column;gap:12px;max-height:65dvh;overflow-y:auto;overscroll-behavior:contain}
.reading-tools-panel h3{font-family:var(--font-chrome);font-size:var(--text-xs,13px);margin:4px 0 0;color:var(--mut)}
.reading-tools-panel button{text-align:start;border:1px solid var(--line);border-radius:var(--r-1,4px)}
.reading-tools-panel #reading-reference-open{border-inline-start:2px solid var(--source-mark)}
.reading-tools-panel #reading-help-selection{background:var(--card)}
.reading-tools-panel hr{width:100%;border:0;border-top:1px solid var(--line);margin:0}
#reading-tools-state:empty{display:none}
@media(max-width:767px){.reading-tools-panel{max-height:none;overflow:visible}}
.reading-column .reading-purpose{margin-block:8px 12px;line-height:1.6}
.reading-column #source-state{font-size:var(--text-xs,13px);line-height:1.6;margin-block:8px;color:var(--mut)}
.reading-column h2{margin-block:8px 12px}
.reading-tools-panel label{font-size:var(--text-xs,13px);font-weight:600}
.reading-tools-panel select{width:100%;min-height:44px;background:var(--paper);color:var(--ink);border:1px solid var(--line);padding:8px}
.reading-mode-description{margin-top:-8px;margin-bottom:20px}
.reading-layout[data-reading-mode=read]{grid-template-columns:minmax(0,1fr)}
.reading-layout[data-reading-mode=read] .reading-column{width:100%;max-width:calc(var(--measure-prose,70ch) + 48px);box-sizing:border-box;margin-inline:auto}
.reading-layout[data-reading-mode=notebook]{grid-template-columns:minmax(0,2fr) minmax(0,3fr)}
.product-workspace .reading-layout[data-reading-mode=notebook] .reading-column{position:sticky;top:24px}
.reading-layout[data-reading-mode=notebook] .reading-source{max-height:42dvh;overflow-y:auto;overscroll-behavior:contain}
.product-workspace .reading-layout[data-reading-mode=notebook] .reading-notes{position:static;max-height:none;overflow:visible}
.reading-layout[data-reading-mode=notebook] textarea#note{min-height:340px}
.reading-layout{--reading-font-size:18px}.reading-source{font-size:var(--reading-font-size)}
.reading-width-control{position:absolute;z-index:2;background:var(--card);border:1px solid var(--line);padding:16px;width:240px;box-shadow:0 8px 24px #0002;right:0}
.reading-width-control input{width:100%;min-height:44px}.reading-toolbar details{margin-left:auto}
.reading-layout.reading-focused{grid-template-columns:minmax(0,1fr)}.reading-focused .reading-column{max-width:var(--measure-prose,70ch);margin-inline:auto}
.reading-reference{border-top:1px solid var(--line);padding-block:12px;margin-top:24px}.reading-reference summary{min-height:44px;cursor:pointer;display:flex;align-items:center;font-weight:600}
.reading-reference p{overflow-wrap:anywhere}.reading-reference .reading-return{display:block;margin-top:12px}
.overhaul-reading-recovery{margin-top:24px}.overhaul-reading-actions{padding-block:12px}
[hidden]{display:none!important}
@media(max-width:1023px){.reading-layout{grid-template-columns:minmax(0,1fr) minmax(260px,300px);gap:24px}}
@media(max-width:767px){.reading-layout,.reading-layout[data-reading-mode=notebook]{display:block}.product-workspace .reading-notes.overhaul-notes{position:static;margin-top:32px;padding:20px;max-height:none;overflow:visible}.reading-toolbar #reading-focus{display:none}.reading-toolbar{gap:8px}.reading-layout.reading-focused .reading-column{max-width:none}.reading-path{margin-bottom:16px}.reading-width-control{position:static;width:min(280px,calc(100vw - 56px))}.reading-toolbar details{margin-left:0}.reading-modes{width:100%;box-sizing:border-box}.reading-modes button{flex:1}.product-workspace .reading-layout[data-reading-mode=notebook] .reading-column{position:static}.reading-layout[data-reading-mode=notebook] .reading-source{max-height:28dvh}.reading-layout[data-reading-mode=notebook] textarea#note{min-height:260px}}
@media(forced-colors:active){.reading-modes button[aria-pressed=true]{outline:2px solid Highlight;outline-offset:-4px}}
'''

SCRIPT = r'''
const ctx=__CONTEXT__;let intent=null,noteId=null,dirty=false,view=null,savingNote=false,noteVersion=0;
const $=s=>document.querySelector(s);
const continuityKey='itembank-reading:'+JSON.stringify([ctx.course_id,ctx.occurrence_id,ctx.revision_id]);
let restored=false,continuityBlocked=false;
function sourceFingerprint(){return view?.occurrence?.source_ref?.source_fingerprint||null}
function rememberReading(){if(continuityBlocked){if(dirty)$('#save-state').textContent='Unsaved draft. Previous-source wording is kept for recovery. Copy this new wording before leaving.';return}if(!view||view.content===null||!sourceFingerprint())return;try{sessionStorage.setItem(continuityKey,JSON.stringify({source:sourceFingerprint(),y:window.scrollY,focus:document.activeElement?.id||'',draft:$('#note').value,noteId}));}catch(e){if(dirty)$('#save-state').textContent='Unsaved draft. Browser recovery is unavailable. Keep this tab open or copy your wording.'}}
function showPreviousDraft(saved){const root=$('#previous-drafts');if(!root||typeof saved.draft!=='string'||!saved.draft)return;const details=document.createElement('details'),summary=document.createElement('summary'),label=document.createElement('label'),field=document.createElement('textarea');summary.textContent='Copy a local draft from a changed or unavailable source';label.textContent='Previous unsaved wording. Review against its original source before reusing it.';field.value=saved.draft;field.readOnly=true;field.id='previous-draft-'+root.children.length;label.htmlFor=field.id;details.append(summary,label,field);root.append(details);const recovery=$('#recover-reading-draft');if(recovery){recovery.hidden=false;recovery.onclick=()=>{dismissReadingTools();showCompanion('notebook');details.open=true;field.focus();};}}
function restoreReading(){if(restored||!view)return;restored=true;let saved;try{saved=JSON.parse(sessionStorage.getItem(continuityKey)||'null')}catch(e){return}if(!saved)return;
if(view.content===null||!sourceFingerprint()||saved.source!==sourceFingerprint()){continuityBlocked=true;showPreviousDraft(saved);const resume=$('#resume-reading');if(resume){resume.hidden=false;resume.disabled=true;resume.textContent='The source changed or is unavailable. Previous position and draft were not restored.'}return}
if(typeof saved.draft==='string'&&saved.draft&&!dirty){$('#note').value=saved.draft;noteId=typeof saved.noteId==='string'?saved.noteId:null;dirty=true;$('#save-state').textContent='Recovered local unsaved draft. Save to my notes when ready.'}
const resume=$('#resume-reading');if(resume&&Number.isFinite(saved.y)&&saved.y>=0){resume.hidden=false;resume.onclick=()=>{const target=document.getElementById(saved.focus);if(target)target.focus({preventScroll:true});window.scrollTo({top:saved.y,behavior:'instant'});resume.hidden=true;};}}
window.addEventListener('pagehide',rememberReading);
document.addEventListener('click',e=>{if(e.target.closest('a[href]'))rememberReading()});
function updateSaveButton(){ $('#save-note').disabled=savingNote||!view||view.content===null||!!view.note_error;if(restored)rememberReading(); }
async function api(op,extra={}){const r=await fetch('/api/course/'+op.replaceAll('_','-'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...ctx,...extra})});if(!r.ok)throw Error('Request refused. Keep your draft. Refresh the course or inspect recovery before trying again.');return r.json()}
function status(s){return {'reported-read':'Reported read for this assignment','not-reported':'Not reported read','unavailable':'Reading history unavailable','unsupported':'Reading history unsupported. Restore or inspect it.'}[s]||s}
async function refresh(){view=await api('reading_view');$('#reading-state').textContent=status(view.reading_state.state);$('#source-state').textContent=view.availability.message||__SOURCE_STATUS__[view.availability.state]||'This source range is unavailable. Refresh the course or inspect source recovery.';$('#source-content').textContent=view.content===null?'This source range is unavailable. Your notes and historical declaration remain separate.':view.content;
$('#mark-read').disabled=view.content===null;updateSaveButton();
$('#note-state').textContent=view.note_error||'Private source notes. Shared across assignments using this source.';
$('#saved-notes').replaceChildren();for(const n of view.notes){const article=document.createElement('article');article.className='reading-note';const p=document.createElement('p');p.textContent=n.learner_wording;const meta=document.createElement('small');meta.textContent=n.anchor_state+' · Private · '+n.owner;article.append(p,meta);$('#saved-notes').append(article)}
restoreReading();helpReady();
}
$('#mark-read').addEventListener('click',async()=>{const b=$('#mark-read');b.disabled=true;try{if(!intent){const c=await api('confirm_reading',{confirmation:'read'});intent=c.intent_id}await api('declare_reading',{intent_id:intent});await refresh();intent=null;b.textContent='I have read this range'}catch(e){$('#reading-state').textContent=e.message;b.textContent=intent?'Retry the same declaration':'I have read this range'}finally{b.disabled=view?.content===null}});
$('#note').addEventListener('input',()=>{noteVersion++;dirty=true;noteId=null;$('#save-state').textContent='Unsaved draft';rememberReading();});
$('#save-note').addEventListener('click',async()=>{if(savingNote||!view||view.content===null||view.note_error)return;const field=$('#note'),wording=field.value;if(!wording.trim())return;const version=noteVersion,id=noteId??crypto.randomUUID().replaceAll('-',''),fingerprint=view.notes_fingerprint;noteId=id;savingNote=true;updateSaveButton();try{await api('save_reading_note',{note_id:id,wording,notes_fingerprint:fingerprint});if(noteVersion===version&&field.value===wording){dirty=false;noteId=null;field.value='';$('#save-state').textContent='Saved to your notes.'}else{$('#save-state').textContent='Earlier wording saved. Current draft is unsaved.'}try{await refresh()}catch(e){$('#note-state').textContent='Saved. The note list could not refresh. Reopen the course to view it.'}}catch(e){if(noteVersion===version&&field.value===wording)noteId=id;$('#save-state').textContent=e.message+(noteVersion===version&&field.value===wording?'':' Current draft is unsaved.')}finally{savingNote=false;updateSaveButton()}});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
$('#save-note').addEventListener('click',()=>{rememberReading();});
refresh().catch(e=>{$('#reading-state').textContent=e.message});
'''
SCRIPT = SCRIPT.replace('__SOURCE_STATUS__', presentation.script_safe_json(SOURCE_STATUS))


VIEW_SCRIPT = r'''

// View controls never save a note, declare reading, or create evidence.
const readingLayout=$('.reading-layout'),readingSource=$('#source-content'),readingCompanion=$('.reading-notes');
const workspaceKey=continuityKey+':workspace';
const readingModeDescriptions={read:'A centered passage, with your notes one click away.',study:'Keep the source close while you take notes.',notebook:'More space to write, with the source nearby.'};
let passageReturn=null,selectedPassageReturn=null;
function workspacePreferences(){return {mode:readingLayout.dataset.readingMode,size:$('#reading-size').value,measure:$('#reading-measure').value,width:$('#companion-width').value};}
function rememberWorkspace(){try{sessionStorage.setItem(workspaceKey,JSON.stringify(workspacePreferences()));}catch(e){}}
function updateWidthControl(){$('#companion-width').disabled=readingLayout.dataset.readingMode!=='study'||window.matchMedia('(max-width:1023px)').matches;}
function setReadingMode(mode,remember=true){if(!Object.hasOwn(readingModeDescriptions,mode))return;readingLayout.dataset.readingMode=mode;readingCompanion.hidden=mode==='read';readingLayout.classList.toggle('reading-focused',mode==='read');readingSource.tabIndex=mode==='notebook'?0:-1;document.querySelectorAll('[data-reading-mode-button]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.readingModeButton===mode)));$('#reading-focus').setAttribute('aria-pressed',String(mode==='read'));$('#reading-focus').textContent=mode==='read'?'Show companion':'Focus reading';$('#reading-mode-description').textContent=readingModeDescriptions[mode];updateWidthControl();if(remember)rememberWorkspace();}
function setReadingType(){readingLayout.style.setProperty('--reading-font-size',$('#reading-size').value+'px');readingLayout.style.setProperty('--measure-prose',$('#reading-measure').value+'ch');rememberWorkspace();}
function restoreWorkspace(){let saved;try{saved=JSON.parse(sessionStorage.getItem(workspaceKey)||'null')}catch(e){return}if(!saved||typeof saved!=='object')return;for(const [id,key] of [['reading-size','size'],['reading-measure','measure']]){const field=$('#'+id);if(Array.from(field.options).some(option=>option.value===saved[key]))field.value=saved[key];}readingLayout.style.setProperty('--reading-font-size',$('#reading-size').value+'px');readingLayout.style.setProperty('--measure-prose',$('#reading-measure').value+'ch');const width=Number(saved.width);if(typeof saved.width==='string'&&width>=260&&width<=440&&width%20===0){$('#companion-width').value=saved.width;readingLayout.style.setProperty('--companion-width',width+'px');$('#companion-width-value').textContent=width+' px';}if(Object.hasOwn(readingModeDescriptions,saved.mode))setReadingMode(saved.mode,false);}
function liveSourceSelection(){const selected=window.getSelection();if(!view||view.content===null||!selected||selected.rangeCount!==1||selected.isCollapsed||!readingSource.contains(selected.anchorNode)||!readingSource.contains(selected.focusNode)||!selected.toString().trim())return null;return selected.getRangeAt(0);}
function passagePosition(){return {y:window.scrollY,sourceY:readingSource.scrollTop,mode:readingLayout.dataset.readingMode,source:sourceFingerprint()};}
function trackSelectedPassage(){const range=liveSourceSelection();if(!range){selectedPassageReturn=null;return;}if(typeof range.getBoundingClientRect!=='function')return;const box=range.getBoundingClientRect(),bounds=readingSource.getBoundingClientRect();if(box.bottom<Math.max(0,bounds.top)||box.top>Math.min(innerHeight,bounds.bottom))return;selectedPassageReturn={position:passagePosition(),rendered:readingSource.firstChild,start:range.startContainer,startOffset:range.startOffset,end:range.endContainer,endOffset:range.endOffset};}
document.addEventListener('selectionchange',trackSelectedPassage);
readingSource.addEventListener('scroll',trackSelectedPassage,{passive:true});
function passageSnapshot(){const range=liveSourceSelection(),saved=selectedPassageReturn;if(range&&saved&&saved.rendered===readingSource.firstChild&&saved.position.source===sourceFingerprint()&&saved.start===range.startContainer&&saved.startOffset===range.startOffset&&saved.end===range.endContainer&&saved.endOffset===range.endOffset)return {...saved.position};return passagePosition();}
function rememberPassage(){passageReturn=passageSnapshot();}
function restorePassagePosition(position){if(!view||view.content===null||(position&&Object.hasOwn(position,'source')&&position.source!==sourceFingerprint()))return false;dismissReadingTools();if(position&&Object.hasOwn(readingModeDescriptions,position.mode))setReadingMode(position.mode);readingSource.focus({preventScroll:true});if(position){if(Number.isFinite(position.sourceY)&&position.sourceY>=0)readingSource.scrollTop=position.sourceY;if(Number.isFinite(position.y)&&position.y>=0)window.scrollTo({top:position.y,behavior:'instant'});}return true;}
function dismissReadingTools(returnFocus=false){const tools=$('#reading-tools');tools.open=false;if(returnFocus)tools.querySelector('summary').focus();}
$('#reading-tools').addEventListener('pointerdown',event=>{const selected=window.getSelection();if(event.target.closest('summary,#reading-quote,#reading-help-selection')&&selected?.rangeCount===1&&!selected.isCollapsed&&readingSource.contains(selected.anchorNode)&&readingSource.contains(selected.focusNode)&&selected.toString().trim())event.preventDefault();});
$('#reading-tools').addEventListener('keydown',event=>{if(event.key==='Escape'&&$('#reading-tools').open){event.preventDefault();dismissReadingTools(true);}});
function showCompanion(mode='study'){setReadingMode(mode);}
function returnToPassage(){restorePassagePosition(passageReturn);}
document.querySelectorAll('[data-reading-mode-button]').forEach(button=>button.onclick=()=>{setReadingMode(button.dataset.readingModeButton);if(button.dataset.readingModeButton==='notebook')$('#note').focus();});
$('#reading-size').onchange=setReadingType;$('#reading-measure').onchange=setReadingType;
$('#reading-focus').onclick=()=>setReadingMode(readingCompanion.hidden?'study':'read');
$('#companion-width').oninput=e=>{const width=Number(e.target.value);if(Number.isFinite(width)&&width>=260&&width<=440){readingLayout.style.setProperty('--companion-width',width+'px');$('#companion-width-value').textContent=width+' px';rememberWorkspace();}};
$('#reading-reference-open').onclick=()=>{rememberPassage();dismissReadingTools();showCompanion();$('#reading-reference').open=true;$('#reading-reference summary').focus();};
$('#reading-note-open').onclick=()=>{rememberPassage();dismissReadingTools();showCompanion('notebook');$('#note').focus();};
$('#reading-quote').onclick=()=>{const selection=window.getSelection(),text=selection?.toString().trim();if(!view||view.content===null||view.note_error){$('#reading-tools-state').textContent='Source or notes unavailable. Keep any existing draft.';return}if(!text||!readingSource.contains(selection.anchorNode)||!readingSource.contains(selection.focusNode)){ $('#reading-tools-state').textContent='Select words inside the source passage, then choose Add selection to draft.';return}rememberPassage();dismissReadingTools();showCompanion('notebook');const field=$('#note');field.value+=(field.value?'\n\n':'')+'Source passage: '+text+'\nMy thought: ';field.dispatchEvent(new Event('input',{bubbles:true}));field.focus();$('#reading-tools-state').textContent='Selection added to your unsaved draft. Review it before saving.';};
document.querySelectorAll('.reading-return').forEach(button=>button.onclick=returnToPassage);
setReadingMode('study',false);restoreWorkspace();
window.matchMedia('(max-width:1023px)').addEventListener('change',updateWidthControl);
'''

def href(course_id, row):
    return '/course/%s/reading/%s/%s' % (course_id, row['occurrence_id'], row['revision_id'])


def render(course_id, read, occurrence_id, revision_id, view, origin='learn', theme_css=None,
           source_return=None):
    """Render an admitted reading; source_return is a daemon-resolved back action."""
    esc = presentation.esc
    selected = view['occurrence'] or {}
    title = (view['placements'].get(occurrence_id) or {}).get('title') or 'Reading desk'
    reading_status = {
        'reported-read': 'Reported read for this assignment',
        'not-reported': 'Not reported read',
        'unavailable': 'Reading history unavailable',
        'unsupported': 'Reading history unsupported. Restore or inspect it.',
    }.get(view['reading_state']['state'], view['reading_state']['state'])
    saved_notes = ''.join(
        '<article class="reading-note"><p>%s</p><small class="reading-meta">%s · Private · %s</small></article>'
        % (esc(note['learner_wording']), esc(note['anchor_state']), esc(note['owner']))
        for note in view['notes'])
    origin_suffix = ('?' + urlencode({'return_source': source_return['source_id']})
                     if source_return else '?from=overview' if origin == 'overview' else '')
    path = ''.join('<a href="%s"%s>%s</a>' % (esc(href(course_id,row) + origin_suffix),
                    ' aria-current="page"' if row['occurrence_id']==occurrence_id else '',
                    esc(view['placements'][row['occurrence_id']]['title'])) for row in view['occurrences'])
    body = '''<div class="overhaul-reading"><nav class="reading-path" aria-label="Reading assignments"><details><summary>Reading assignments</summary>%s</details></nav>
<div class="reading-toolbar" hidden><div class="reading-modes" role="group" aria-label="Reading workspace"><button type="button" data-reading-mode-button="read" aria-pressed="false">Read</button><button type="button" data-reading-mode-button="study" aria-pressed="true">Study</button><button type="button" data-reading-mode-button="notebook" aria-pressed="false">Notebook</button></div><button id="reading-note-open" type="button">Write a note</button><details id="reading-tools"><summary>Reading tools</summary><div class="reading-width-control reading-tools-panel"><h3>Source support</h3><button id="reading-reference-open" type="button">Source context</button><button id="reading-help-selection" type="button">Ask about selection</button><button id="reading-quote" type="button">Add selection to draft</button><hr><h3>Reading display</h3><button id="reading-focus" type="button" aria-pressed="false">Focus reading</button><label for="reading-size">Text size<select id="reading-size"><option value="18">Standard</option><option value="20">Large</option><option value="22">Larger</option></select></label><label for="reading-measure">Line width<select id="reading-measure"><option value="58">Narrow</option><option value="70" selected>Comfortable</option><option value="82">Wide</option></select></label><label for="companion-width">Notes width (desktop Study mode)</label><input id="companion-width" type="range" min="260" max="440" step="20" value="320"><output id="companion-width-value" for="companion-width">320 px</output></div></details></div><p id="reading-mode-description" class="reading-meta reading-mode-description" hidden></p><p id="reading-tools-state" class="reading-meta" role="status"></p>
<div class="reading-layout" data-reading-mode="study">
<article class="reading-column overhaul-source" aria-label="Assigned reading"><p class="reading-meta">Assigned source range · %s</p><h2>Source reading</h2><p class="reading-purpose">%s</p>
<p id="source-state">%s</p><button id="recover-reading-draft" type="button" hidden>Review previous unsaved draft</button><div id="source-content" tabindex="-1" class="reading-source" role="region" aria-label="Source passage">%s</div>
%s
<div class="overhaul-reading-actions"><button id="mark-read" class="go primary" type="button" disabled>I have read this range</button><p id="reading-state" role="status" aria-live="polite">%s</p>
<p class="reading-meta">Your declaration describes reading. It is not a score, grade, or mastery claim.</p></div>
</article>
<aside class="reading-notes overhaul-notes" aria-label="Private source notes" tabindex="0"><h2>My source notes</h2><p id="note-state">%s</p><div id="previous-drafts"></div><label for="note">A note to yourself</label><textarea id="note"></textarea><button id="save-note" class="go primary" type="button" disabled>Save to my notes</button><p id="save-state" role="status" aria-live="polite">No unsaved draft</p><h3>Saved notes</h3><div id="saved-notes">%s</div><button class="reading-return" type="button" hidden>Return to passage</button><details id="reading-reference" class="reading-reference"><summary>Source and revision</summary><p><code>%s</code></p><p>Occurrence <code>%s</code></p><p>Revision <code>%s</code></p><button class="reading-return" type="button" hidden>Return to passage</button></details></aside></div><p class="reading-meta overhaul-reading-recovery">This tab keeps your reading position and local unsaved draft for this source revision. Saved notes remain separate.</p><button id="resume-reading" type="button" hidden>Resume previous reading position</button></div>''' % (
        path,esc(selected.get('preparation_mode','')),esc(selected.get('purpose','')),esc(source_status(view['availability'])),
        esc(view['content'] or 'Source unavailable.'),context_help.reader_panel(view),esc(reading_status),
        esc(view['note_error'] or 'Private source notes. Shared across assignments using this source.'),saved_notes,
        esc((selected.get('source_ref') or {}).get('locator','Unavailable')),esc(occurrence_id),esc(revision_id))
    ctx=dict(course_id=course_id, expected_fingerprint=read['fingerprint'], occurrence_id=occurrence_id, revision_id=revision_id)
    return presentation.surface_shell(title,body,theme_css=THEME_CSS if theme_css is None else theme_css,wide=True,extra_css=CSS+context_help.CSS,
        back=source_return or {'href':'/course/'+course_id+('' if origin == 'overview' else '/learn'),
              'label':'Back to overview' if origin == 'overview' else 'Back to Learn'},
        noscript='The source range is readable here. Enable JavaScript to report read or save a note.',
        tail='<script>'+SCRIPT.replace('__CONTEXT__',presentation.script_safe_json(ctx))+VIEW_SCRIPT+context_help.READER_SCRIPT+"\ndocument.querySelector('.reading-toolbar').hidden=false;document.querySelector('#reading-mode-description').hidden=false;document.querySelectorAll('.reading-return').forEach(b=>b.hidden=false);"+'</script>')
