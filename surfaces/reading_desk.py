"""The supported study desk, consuming reading and notes authority."""
from surfaces import presentation

CSS = '''
main{max-width:1320px!important}.reading-layout{display:grid;grid-template-columns:200px minmax(0,1fr) 290px;gap:32px}
.reading-path{border-right:1px solid var(--line,#d7dbd2);padding-right:20px}.reading-path a{display:block;padding:12px 0;border-bottom:1px solid var(--line,#d7dbd2);text-decoration:none}
.reading-column{min-width:0}.reading-source{font:20px/1.85 Georgia,serif;white-space:pre-wrap;overflow-wrap:anywhere;border-top:1px solid var(--line,#d7dbd2);padding-top:28px;margin:24px 0 40px}
.reading-notes{border-left:1px solid var(--line,#d7dbd2);padding-left:24px;min-width:0}.reading-notes textarea{width:100%;min-height:160px;padding:12px;font:inherit;background:var(--product-paper,#fffdf8);color:inherit;border:1px solid var(--line,#d7dbd2);border-radius:4px}
.reading-layout button,.reading-layout a{min-height:44px}.reading-layout button{padding:10px 16px;cursor:pointer}.reading-layout :focus-visible{outline:3px solid #a46b2c;outline-offset:3px}
.reading-note{border-top:1px solid var(--line,#d7dbd2);margin-top:20px;padding-top:16px}.reading-note p{white-space:pre-wrap;overflow-wrap:anywhere}.reading-meta{font-size:13px;opacity:.8}.reading-layout code{overflow-wrap:anywhere}
@media(max-width:1000px){.reading-layout{grid-template-columns:minmax(0,1fr) 270px}.reading-path{grid-column:1/-1;border:0;display:flex;gap:20px;flex-wrap:wrap}}
@media(max-width:680px){.reading-layout{display:block}.reading-notes{border:0;border-top:1px solid var(--line,#d7dbd2);padding:24px 0}.reading-source{font-size:18px}.reading-path{display:block}}
'''

SCRIPT = r'''
const ctx=__CONTEXT__;let intent=null,noteId=null,dirty=false,view=null;
const $=s=>document.querySelector(s);
async function api(op,extra={}){const r=await fetch('/api/course/'+op.replaceAll('_','-'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...ctx,...extra})});if(!r.ok)throw Error('Request refused. Keep your draft. Refresh the course or inspect recovery before trying again.');return r.json()}
function status(s){return {'reported-read':'Reported read for this assignment','not-reported':'Not reported read','unavailable':'Reading history unavailable','unsupported':'Reading history unsupported. Restore or inspect it.'}[s]||s}
async function refresh(){view=await api('reading_view');$('#reading-state').textContent=status(view.reading_state.state);$('#source-state').textContent=view.availability.message||view.availability.state;$('#source-content').textContent=view.content===null?'This source range is unavailable. Your notes and historical declaration remain separate.':view.content;
$('#mark-read').disabled=view.content===null;$('#save-note').disabled=view.content===null||!!view.note_error;
$('#note-state').textContent=view.note_error||'Private source notes. Shared across assignments using this source.';
$('#saved-notes').replaceChildren();for(const n of view.notes){const article=document.createElement('article');article.className='reading-note';const p=document.createElement('p');p.textContent=n.learner_wording;const meta=document.createElement('small');meta.textContent=n.anchor_state+' · Private · '+n.owner;article.append(p,meta);$('#saved-notes').append(article)}
}
$('#mark-read').addEventListener('click',async()=>{const b=$('#mark-read');b.disabled=true;try{if(!intent){const c=await api('confirm_reading',{confirmation:'read'});intent=c.intent_id}await api('declare_reading',{intent_id:intent});await refresh();intent=null;b.textContent='I have read this range'}catch(e){$('#reading-state').textContent=e.message;b.textContent=intent?'Retry the same declaration':'I have read this range'}finally{b.disabled=view?.content===null}});
$('#note').addEventListener('input',()=>{dirty=true;noteId=null;$('#save-state').textContent='Unsaved draft';});
$('#save-note').addEventListener('click',async()=>{const b=$('#save-note');if(!$('#note').value.trim())return;b.disabled=true;noteId??=crypto.randomUUID().replaceAll('-','');try{await api('save_reading_note',{note_id:noteId,wording:$('#note').value,notes_fingerprint:view.notes_fingerprint});dirty=false;noteId=null;$('#note').value='';$('#save-state').textContent='Saved to your notes.';try{await refresh()}catch(e){$('#note-state').textContent='Saved. The note list could not refresh. Reopen the course to view it.'}}catch(e){$('#save-state').textContent=e.message}finally{b.disabled=view?.content===null||!!view?.note_error}});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
refresh().catch(e=>{$('#reading-state').textContent=e.message});
'''


def href(course_id, row):
    return '/course/%s/reading/%s/%s' % (course_id, row['occurrence_id'], row['revision_id'])


def render(course_id, read, occurrence_id, revision_id, view):
    esc = presentation.esc
    selected = view['occurrence'] or {}
    title = (view['placements'].get(occurrence_id) or {}).get('title') or 'Reading desk'
    path = ''.join('<a href="%s"%s>%s</a>' % (esc(href(course_id,row)),
                    ' aria-current="page"' if row['occurrence_id']==occurrence_id else '',
                    esc(view['placements'][row['occurrence_id']]['title'])) for row in view['occurrences'])
    body = '''<p class="reading-meta">Return opens the beginning of this range. Exact reading position is not saved.</p>
<div class="reading-layout"><nav class="reading-path" aria-label="Reading assignments"><h2>Your path</h2>%s</nav>
<article class="reading-column"><p class="reading-meta">Assigned source range · %s</p><h2>%s</h2><p>%s</p>
<p id="source-state">%s</p><div id="source-content" class="reading-source">%s</div>
<button id="mark-read" class="go primary" type="button" disabled>I have read this range</button><p id="reading-state" role="status" aria-live="polite">Loading reading history</p>
<p class="reading-meta">Your declaration describes reading. It is not a score, grade, or mastery claim.</p>
<details><summary>Source and revision</summary><p><code>%s</code></p><p>Occurrence <code>%s</code></p><p>Revision <code>%s</code></p></details></article>
<aside class="reading-notes" aria-label="Private source notes"><h2>At the source</h2><p id="note-state">Shared source notes</p><label for="note">A note to yourself</label><textarea id="note"></textarea><button id="save-note" class="go primary" type="button" disabled>Save to my notes</button><p id="save-state" role="status" aria-live="polite">No unsaved draft</p><h3>My course notes</h3><div id="saved-notes"></div></aside></div>''' % (
        path,esc(selected.get('preparation_mode','')),esc(title),esc(selected.get('purpose','')),esc(view['availability'].get('message',view['availability']['state'])),
        esc(view['content'] or 'Source unavailable.'),esc((selected.get('source_ref') or {}).get('locator','Unavailable')),
        esc(occurrence_id),esc(revision_id))
    ctx=dict(course_id=course_id, expected_fingerprint=read['fingerprint'], occurrence_id=occurrence_id, revision_id=revision_id)
    return presentation.surface_shell('Reading desk',body,wide=True,extra_css=CSS,
        back={'href':'/course/'+course_id+'/learn','label':'Back to course'},
        noscript='The source range is readable here. Enable JavaScript to report read or save a note.',
        tail='<script>'+SCRIPT.replace('__CONTEXT__',presentation.script_safe_json(ctx))+'</script>')
