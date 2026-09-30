"""The supported study desk, consuming reading and notes authority."""
from surfaces import presentation
from surfaces.theme import THEME_CSS

SOURCE_STATUS = {
    'available': 'Source available.',
    'course.reading_source_stale': 'The source changed. Refresh the course source binding before reading or saving a note. Previous wording remains available for recovery.',
}


def source_status(availability):
    return (availability.get('message') or SOURCE_STATUS.get(availability['state'])
            or 'This source range is unavailable. Refresh the course or inspect source recovery.')


CSS = '''
.overhaul-reading{max-width:1200px;margin-inline:auto}
.reading-layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,310px);gap:var(--space-6,32px);align-items:start}
.reading-path{grid-column:1/-1;border-block:1px solid var(--line);padding-block:var(--space-2,8px)}
.reading-path summary{min-height:44px;display:flex;align-items:center;cursor:pointer;font-family:var(--font-chrome)}
.reading-path a{display:block;padding:12px 0;border-top:1px solid var(--line);text-decoration:none}
.reading-path a[aria-current]{font-weight:600;color:var(--accent)}
.reading-column{min-width:0}.reading-column h2{font-family:var(--font-paper);font-size:var(--text-heading);line-height:1.3;text-wrap:balance}
.reading-source{font:var(--text-lesson,18px)/1.85 var(--font-paper,Georgia,serif);white-space:pre-wrap;overflow-wrap:anywhere;border-block:1px solid var(--line);padding-block:var(--space-5,24px);margin:var(--space-4,20px) 0;max-width:var(--measure-prose,70ch)}
.reading-notes{border-inline-start:3px solid var(--note-mark,var(--line));padding-inline-start:var(--space-4,20px);min-width:0}
.reading-notes h2{font-family:var(--font-chrome);font-size:var(--text-body)}
.reading-notes textarea{box-sizing:border-box;width:100%;min-height:180px;padding:12px;font:inherit;line-height:1.6;background:var(--note-bg,var(--card));color:inherit;border:1px solid var(--line);border-radius:var(--r-1,4px)}
.reading-notes label{display:block;margin-block:var(--space-3,12px) var(--space-2,8px)}
.reading-layout button,.reading-layout a{min-height:44px}.reading-layout button{padding:10px 16px;cursor:pointer}.reading-layout :focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.reading-note{border-top:1px solid var(--line);margin-top:20px;padding-top:16px}.reading-note p{white-space:pre-wrap;overflow-wrap:anywhere}.reading-meta{font-family:var(--font-chrome);font-size:var(--text-xs,13px);color:var(--mut)}.reading-layout code{overflow-wrap:anywhere}
.overhaul-reading-recovery{margin-block:var(--space-3,12px)}
.overhaul-reading-actions{padding-block:var(--space-3,12px)}
@media(max-width:767px){.reading-layout{display:block}.reading-path{margin-bottom:var(--space-4,20px)}.reading-notes{border-inline-start:0;border-top:3px solid var(--note-mark,var(--line));padding:var(--space-4,20px) 0;margin-top:var(--space-5,24px)}.reading-source{font-size:18px}}
'''

SCRIPT = r'''
const ctx=__CONTEXT__;let intent=null,noteId=null,dirty=false,view=null,savingNote=false,noteVersion=0;
const $=s=>document.querySelector(s);
const continuityKey='itembank-reading:'+JSON.stringify([ctx.course_id,ctx.occurrence_id,ctx.revision_id]);
let restored=false,continuityBlocked=false;
function sourceFingerprint(){return view?.occurrence?.source_ref?.source_fingerprint||null}
function rememberReading(){if(continuityBlocked){if(dirty)$('#save-state').textContent='Unsaved draft. Previous-source wording is kept for recovery. Copy this new wording before leaving.';return}if(!view||view.content===null||!sourceFingerprint())return;try{sessionStorage.setItem(continuityKey,JSON.stringify({source:sourceFingerprint(),y:window.scrollY,focus:document.activeElement?.id||'',draft:$('#note').value,noteId}));}catch(e){if(dirty)$('#save-state').textContent='Unsaved draft. Browser recovery is unavailable. Keep this tab open or copy your wording.'}}
function showPreviousDraft(saved){const root=$('#previous-drafts');if(!root||typeof saved.draft!=='string'||!saved.draft)return;const details=document.createElement('details'),summary=document.createElement('summary'),label=document.createElement('label'),field=document.createElement('textarea');summary.textContent='Copy a local draft from a changed or unavailable source';label.textContent='Previous unsaved wording. Review against its original source before reusing it.';field.value=saved.draft;field.readOnly=true;field.id='previous-draft-'+root.children.length;label.htmlFor=field.id;details.append(summary,label,field);root.append(details)}
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
restoreReading();
}
$('#mark-read').addEventListener('click',async()=>{const b=$('#mark-read');b.disabled=true;try{if(!intent){const c=await api('confirm_reading',{confirmation:'read'});intent=c.intent_id}await api('declare_reading',{intent_id:intent});await refresh();intent=null;b.textContent='I have read this range'}catch(e){$('#reading-state').textContent=e.message;b.textContent=intent?'Retry the same declaration':'I have read this range'}finally{b.disabled=view?.content===null}});
$('#note').addEventListener('input',()=>{noteVersion++;dirty=true;noteId=null;$('#save-state').textContent='Unsaved draft';rememberReading();});
$('#save-note').addEventListener('click',async()=>{if(savingNote||!view||view.content===null||view.note_error)return;const field=$('#note'),wording=field.value;if(!wording.trim())return;const version=noteVersion,id=noteId??crypto.randomUUID().replaceAll('-',''),fingerprint=view.notes_fingerprint;noteId=id;savingNote=true;updateSaveButton();try{await api('save_reading_note',{note_id:id,wording,notes_fingerprint:fingerprint});if(noteVersion===version&&field.value===wording){dirty=false;noteId=null;field.value='';$('#save-state').textContent='Saved to your notes.'}else{$('#save-state').textContent='Earlier wording saved. Current draft is unsaved.'}try{await refresh()}catch(e){$('#note-state').textContent='Saved. The note list could not refresh. Reopen the course to view it.'}}catch(e){if(noteVersion===version&&field.value===wording)noteId=id;$('#save-state').textContent=e.message+(noteVersion===version&&field.value===wording?'':' Current draft is unsaved.')}finally{savingNote=false;updateSaveButton()}});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
$('#save-note').addEventListener('click',()=>{rememberReading();});
refresh().catch(e=>{$('#reading-state').textContent=e.message});
'''
SCRIPT = SCRIPT.replace('__SOURCE_STATUS__', presentation.script_safe_json(SOURCE_STATUS))


def href(course_id, row):
    return '/course/%s/reading/%s/%s' % (course_id, row['occurrence_id'], row['revision_id'])


def render(course_id, read, occurrence_id, revision_id, view, origin='learn', theme_css=None):
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
    origin_suffix = '?from=overview' if origin == 'overview' else ''
    path = ''.join('<a href="%s"%s>%s</a>' % (esc(href(course_id,row) + origin_suffix),
                    ' aria-current="page"' if row['occurrence_id']==occurrence_id else '',
                    esc(view['placements'][row['occurrence_id']]['title'])) for row in view['occurrences'])
    body = '''<div class="overhaul-reading"><p class="reading-meta overhaul-reading-recovery">This tab keeps your reading position and local unsaved draft for this source revision. Saved notes remain separate.</p><button id="resume-reading" type="button" hidden>Resume previous reading position</button>
<div class="reading-layout"><nav class="reading-path" aria-label="Reading assignments"><details><summary>Reading assignments</summary>%s</details></nav>
<article class="reading-column overhaul-source" aria-label="Assigned reading"><p class="reading-meta">Assigned source range · %s</p><h2>%s</h2><p>%s</p>
<p id="source-state">%s</p><div id="source-content" class="reading-source">%s</div>
<div class="overhaul-reading-actions"><button id="mark-read" class="go primary" type="button" disabled>I have read this range</button><p id="reading-state" role="status" aria-live="polite">%s</p>
<p class="reading-meta">Your declaration describes reading. It is not a score, grade, or mastery claim.</p></div>
<details><summary>Source and revision</summary><p><code>%s</code></p><p>Occurrence <code>%s</code></p><p>Revision <code>%s</code></p></details></article>
<aside class="reading-notes overhaul-notes" aria-label="Private source notes"><h2>My source notes</h2><p id="note-state">%s</p><div id="previous-drafts"></div><label for="note">A note to yourself</label><textarea id="note"></textarea><button id="save-note" class="go primary" type="button" disabled>Save to my notes</button><p id="save-state" role="status" aria-live="polite">No unsaved draft</p><h3>Saved notes</h3><div id="saved-notes">%s</div></aside></div></div>''' % (
        path,esc(selected.get('preparation_mode','')),esc(title),esc(selected.get('purpose','')),esc(source_status(view['availability'])),
        esc(view['content'] or 'Source unavailable.'),esc(reading_status),esc((selected.get('source_ref') or {}).get('locator','Unavailable')),
        esc(occurrence_id),esc(revision_id),esc(view['note_error'] or 'Private source notes. Shared across assignments using this source.'),saved_notes)
    ctx=dict(course_id=course_id, expected_fingerprint=read['fingerprint'], occurrence_id=occurrence_id, revision_id=revision_id)
    return presentation.surface_shell('Reading desk',body,theme_css=THEME_CSS if theme_css is None else theme_css,wide=True,extra_css=CSS,
        back={'href':'/course/'+course_id+('' if origin == 'overview' else '/learn'),
              'label':'Back to overview' if origin == 'overview' else 'Back to Learn'},
        noscript='The source range is readable here. Enable JavaScript to report read or save a note.',
        tail='<script>'+SCRIPT.replace('__CONTEXT__',presentation.script_safe_json(ctx))+'</script>')
