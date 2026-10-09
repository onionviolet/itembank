
var D=window.__day__;
var SNAP=D.snapshot||{};
var INVALID_COPY="Plan not saved. Fix the highlighted cells and try again.";
var CONFLICT_HEADING="Plan changed outside itembank — nothing was overwritten.";
var FORCE_COPY="I understand this replaces these edited cells using the latest plan version.";
var baseline={},draft={},forceToken="",forceDraftHash="",forceRevision="",dirty=false;
var editStatus=document.getElementById('edit-status');
var saveBtn=document.getElementById('save-edits');
var forcePanel=document.getElementById('force-panel');
function revShort(r){return r?r.slice(0,12):"";}
function inputs(){return [].slice.call(document.querySelectorAll('.editor input[type=text]'));}
function values(){
 var o={};
 inputs().forEach(function(i){o[i.name]=i.value;});
 return o;
}
function setDraft(o){draft={};Object.keys(o).forEach(function(k){draft[k]=o[k];});}
function setBaseline(o){baseline={};Object.keys(o).forEach(function(k){baseline[k]=o[k];});}
function isDirty(){
 var v=values(),k;
 for(k in baseline){if(v[k]!==baseline[k]){return true;}}
 return false;
}
function setDirty(){
 dirty=isDirty();
 saveBtn.disabled=!dirty;
 if(dirty){window.addEventListener('beforeunload',beforeunload);}
 else{window.removeEventListener('beforeunload',beforeunload);}
}
function beforeunload(e){
 e.preventDefault();
 e.returnValue="You have unsaved plan changes.";
}
function say(t,cls){editStatus.textContent=t;editStatus.className="status "+(cls||"");}
function draftHash(o){
 var keys=Object.keys(o).sort(),parts=[];
 keys.forEach(function(k){parts.push(JSON.stringify(k)+":"+JSON.stringify(o[k]));});
 return parts.join(",");
}
function highlightErrors(fields){
 inputs().forEach(function(i){
  i.closest('.field').classList.toggle('invalid',fields.indexOf(i.name)>=0);
 });
}
function post(path,payload,cb){
 var r=new XMLHttpRequest();
 r.open('POST',D.base+path);
 r.setRequestHeader('Content-Type','application/json');
 r.onload=function(){
  var response;
  try{response=JSON.parse(r.responseText);}
  catch(e){response={status:"unavailable",reason:"The local response could not be read. The request outcome is unknown; keep your draft and reload the current plan."};}
  cb(response);
 };
 r.onerror=function(){cb({status:"unavailable",reason:"The local request was interrupted. Its outcome is unknown; keep your draft and reload the current plan."});};
 r.send(JSON.stringify(payload));
}
function copyText(t,btn){
 if(navigator.clipboard&&navigator.clipboard.writeText){
  navigator.clipboard.writeText(t).then(function(){btn.textContent="Copied";});
 }else{
  var ta=document.createElement('textarea');
  ta.value=t;ta.style.position='fixed';ta.style.opacity='0';
  document.body.appendChild(ta);ta.select();
  try{document.execCommand('copy');btn.textContent="Copied";}catch(e){}
  document.body.removeChild(ta);
 }
}
function downloadText(name,t){
 var a=document.createElement('a');
 a.href=URL.createObjectURL(new Blob([t],{type:'text/plain'}));
 a.download=name;a.click();
 setTimeout(function(){URL.revokeObjectURL(a.href);},1000);
}
function fillPanels(draftCells,currentCells,currentDoc,draftRev,currentRev){
 var d=document.getElementById('draft-pane'),c=document.getElementById('current-pane');
 d.querySelector('[data-draft-cells]').textContent=
  draftCells?JSON.stringify(draftCells,null,1):"";
 d.querySelector('[data-draft-rev]').textContent="Your draft · revision "+revShort(draftRev);
 c.querySelector('[data-current-cells]').textContent=
  currentCells?JSON.stringify(currentCells,null,1):"";
 c.querySelector('[data-current-rev]').textContent="Current file · revision "+revShort(currentRev);
 document.getElementById('current-doc').textContent=currentDoc||"";
}
function showConflict(d){
 forceToken=d.force_token||"";
 forceDraftHash=d.force_draft_hash||"";
 forceRevision=d.current&&d.current.revision?d.current.revision:SNAP.revision;
 setDraft(values());
 fillPanels(draft,currentCells(d),(d.current&&d.current.document)||SNAP.document,
   SNAP.revision,d.current.revision);
 document.getElementById('conflict').classList.add('on');
 forcePanel.classList.add('on');
 document.getElementById('force-confirm').checked=false;
 document.getElementById('force-btn').disabled=true;
 var h=document.getElementById('conflict-heading');
 h.textContent=CONFLICT_HEADING;
 h.focus();
}
function currentCells(d){
 return d.current&&d.current.cells?d.current.cells:SNAP.cells;
}
function saveEdits(){
 var changed={},v=values(),k,forceRev=SNAP.revision;
 if(document.getElementById('conflict').classList.contains('on')){
  forceRev=forceRevision;
 }
 for(k in baseline){if(v[k]!==baseline[k]){changed[k]=v[k];}}
 if(!Object.keys(changed).length){return;}
 say("Saving…");
 saveBtn.disabled=true;
 post('/edit',{revision:forceRev,edits:changed},function(d){
  if(d.status==="saved"){
   SNAP.revision=d.revision;
   setBaseline(d.cells);
   setDraft({});
   setDirty();
   document.getElementById('conflict').classList.remove('on');
   forcePanel.classList.remove('on');
   forceToken="";forceDraftHash="";
   say("Saved. Plan version "+revShort(d.revision)+".","ok");
   location.reload();
   return;
  }
  if(d.status==="conflict"){showConflict(d);return;}
  highlightErrors(d.errors||[]);
  if(d.status==="invalid"){
   say(INVALID_COPY,"err");
  }else{
   say((d.reason||"Plan not available.")+" Retry, or copy/download the plan and reload.","warn");
   document.getElementById('current-doc').textContent=d.document||SNAP.document||"";
   document.getElementById('edit-recovery').classList.add('on');
  }
  saveBtn.disabled=!isDirty();
 });
}
function retryEdits(){
 document.getElementById('edit-recovery').classList.remove('on');
 saveEdits();
}
function reloadCurrent(){
 say("Reloading current plan…");
 getPage();
}
function reapplyDraft(){
 var k;
 for(k in draft){var i=document.querySelector('.editor input[name="'+k+'"]');if(i){i.value=draft[k];}}
 highlightErrors([]);
 document.getElementById('conflict').classList.remove('on');
 forcePanel.classList.remove('on');
 forceToken="";forceDraftHash="";
 setDirty();
 var first=inputs()[0];
 if(first){first.focus();}
}
function getPage(){
 var r=new XMLHttpRequest();
 r.open('GET',D.base);
 r.onload=function(){
  try{
   var m=r.responseText.match(/window\.__day__=(\{.*?\});\n/s);
   if(!m){return;}
   var b=JSON.parse(m[1]);
   SNAP=b.snapshot||SNAP;
   setBaseline(SNAP.cells||{});
   inputs().forEach(function(i){i.value=baseline[i.name]||"";});
   document.getElementById('revision-code').textContent=revShort(SNAP.revision);
   say("Current plan reloaded. Your recoverable draft is still available.","warn");
   setDirty();
  }catch(e){}
 };
 r.send();
}
function openFile(lane,i){
 var r=new XMLHttpRequest();
 r.open('POST',D.base+'/open');
 r.setRequestHeader('Content-Type','application/json');
 r.send(JSON.stringify({lane:lane,i:i}));
}
function editMode(){
 document.getElementById('editor').classList.add('on');
 document.getElementById('edit-btn').disabled=true;
 var first=inputs()[0];
 if(first){first.focus();}
}
function initEditor(){
 setBaseline(SNAP.cells||{});
 setDraft({});
 forceRevision=SNAP.revision;
 setDirty();
 document.getElementById('edit-btn').addEventListener('click',function(){editMode();});
 saveBtn.addEventListener('click',saveEdits);
 document.getElementById('copy-revision').addEventListener('click',function(){
  copyText(SNAP.revision||"",this);
 });
 document.getElementById('discard-edits').addEventListener('click',function(){
  inputs().forEach(function(i){i.value=baseline[i.name]||"";});
  highlightErrors([]);
  setDraft({});
  setDirty();
  say("Edits discarded.","");
 });
 inputs().forEach(function(i){
  i.addEventListener('input',setDirty);
 });
 document.getElementById('reload-current').addEventListener('click',reloadCurrent);
 document.getElementById('reapply-draft').addEventListener('click',reapplyDraft);
 document.getElementById('retry-edits').addEventListener('click',retryEdits);
 document.getElementById('copy-draft').addEventListener('click',function(){
  copyText(JSON.stringify(draft,null,1),this);
 });
 document.getElementById('download-draft').addEventListener('click',function(){
  downloadText("draft-plan.json",JSON.stringify(draft,null,1));
 });
 document.getElementById('copy-current').addEventListener('click',function(){
  copyText(document.getElementById('current-doc').textContent,this);
 });
 document.getElementById('download-current').addEventListener('click',function(){
  downloadText("current-plan.md",document.getElementById('current-doc').textContent);
 });
 document.getElementById('copy-unavailable').addEventListener('click',function(){
  copyText(document.getElementById('current-doc').textContent,this);
 });
 document.getElementById('download-unavailable').addEventListener('click',function(){
  downloadText("current-plan.md",document.getElementById('current-doc').textContent);
 });
 document.getElementById('force-confirm').addEventListener('change',function(){
  document.getElementById('force-btn').disabled=!this.checked;
 });
 document.getElementById('force-btn').addEventListener('click',function(){
  var v=values(),changed={},k;
  for(k in baseline){if(v[k]!==baseline[k]){changed[k]=v[k];}}
  if(!Object.keys(changed).length){return;}
  var hash=draftHash(changed);
  if(hash!==forceDraftHash){forceToken="";forceDraftHash="";return;}
  say("Confirming force overwrite…");
  this.disabled=true;
  post('/edit',{revision:forceRevision,edits:changed,force_token:forceToken,
                confirmation:FORCE_COPY,force:true},function(d){
   if(d.status==="saved"){
    SNAP.revision=d.revision;
    setBaseline(d.cells);
    setDirty();
    forceToken="";forceDraftHash="";
    document.getElementById('conflict').classList.remove('on');
    forcePanel.classList.remove('on');
    say("Force overwrite saved. Plan version "+revShort(d.revision)+".","ok");
    location.reload();
    return;
   }
   document.getElementById('force-confirm').checked=false;
   document.getElementById('force-btn').disabled=true;
   if(d.status==="conflict"){
    showConflict(d);
   }else{
    say((d.reason||"Force overwrite not completed.")+" Your draft is still here.","err");
   }
  });
 });
}
function paint(){
 var on=[].slice.call(document.querySelectorAll('.lane input[type=checkbox]'))
        .filter(function(i){return i.checked}).map(function(i){return i.name});
 var floor=D.floor.every(function(l){return on.indexOf(l)>=0});
 var full=D.lanes.every(function(l){return on.indexOf(l)>=0});
 var v=document.getElementById('verdict');
 v.className='verdict '+(full?'full':floor?'floor':'');
 v.textContent=full?'Full day. Done.':floor?'Floor met. This day counts.'
   :'Floor needs '+D.floor.filter(function(l){return on.indexOf(l)<0}).join(', ')+'.';
 return on;
}
function saveTicks(){
 var on=paint();
 var r=new XMLHttpRequest();
 r.open('POST',D.base+'/save');
 r.setRequestHeader('Content-Type','application/json');
 r.onload=function(){
  try{
   var d=JSON.parse(r.responseText);
   document.getElementById('streak').firstChild.nodeValue=d.streak;
   document.getElementById('streakword').textContent=d.streak===1?'day':'days';
   var h=document.getElementById('hist');h.innerHTML='';
   d.hist.forEach(function(x){var i=document.createElement('i');
     i.className=x.status==='miss'?'':x.status;i.title=x.date+': '+x.status;h.appendChild(i)});
  }catch(e){}
 };
 r.send(JSON.stringify({date:D.date,done:on}));
}
function saveOwnerTask(el){
 var wanted=el.checked;
 el.disabled=true;
 var status=document.getElementById('task-status');
 status.className='task-status';status.textContent=wanted?'Checking task...':'Reopening task...';
 var r=new XMLHttpRequest();
 r.open('POST',D.base+'/task');
 r.setRequestHeader('Content-Type','application/json');
 r.onload=function(){
  var d={};
  try{d=JSON.parse(r.responseText);}catch(e){}
  if(r.status>=200&&r.status<300&&d.status==='saved'){
   el.setAttribute('data-revision',d.revision);
   el.closest('.task-card').classList.toggle('done',wanted);
   status.textContent=wanted?'Task checked in its assignment ledger.':'Task reopened in its assignment ledger.';
  }else if(r.status>=200&&r.status<300&&d.status==='unchanged'){
   status.textContent='Task already matched its assignment ledger.';
  }else{
   el.checked=!wanted;
   status.className='task-status error';
   status.textContent=(d.reason||'Task owner unavailable. Nothing was overwritten.');
  }
  el.disabled=false;
 };
 r.onerror=function(){el.checked=!wanted;el.disabled=false;status.className='task-status error';
  status.textContent='Task owner unavailable. Nothing was overwritten.';};
 r.send(JSON.stringify({task_id:el.getAttribute('data-task-id'),
  revision:el.getAttribute('data-revision'),checked:wanted}));
}
document.addEventListener('change',function(ev){
 var el=ev.target;
 if(el.classList&&el.classList.contains('owner-task')){saveOwnerTask(el);return;}
 if(el.classList&&el.classList.contains('open')&&el.hasAttribute('data-lane')){
  if(el.value!==''){openFile(el.getAttribute('data-lane'),parseInt(el.value,10));el.value='';}
  return;
 }
 if(el.matches&&el.matches('.lane input[type=checkbox]')){saveTicks();}
});
document.addEventListener('click',function(ev){
 var b=ev.target.closest&&ev.target.closest('button.open[data-lane]');
 if(!b)return;
 ev.preventDefault();
 openFile(b.getAttribute('data-lane'),parseInt(b.getAttribute('data-i')||'0',10));
});
if(SNAP.status==="ready"){
 initEditor();
}
paint();

/* ---- 10-05 Today: focused start, one-sitting override, lesson complete ---- */
var TODAY=D.today||{};
var TODAY_STATUS=document.getElementById('today-status');
function todayAnnounce(text,alert){
 var el=TODAY_STATUS||document.createElement('p');
 el.id='today-status';
 if(!TODAY_STATUS){document.querySelector('.today').appendChild(el);TODAY_STATUS=el;}
 el.setAttribute('role',alert?'alert':'status');
 el.textContent=text;
}
function todayPost(url,body,okText,errText){
 var r=new XMLHttpRequest();
 r.open('POST',url);
 r.setRequestHeader('Content-Type','application/json');
 r.onload=function(){
  var ok=(r.status>=200&&r.status<300);
  var msg=ok?okText:errText;
  try{
   var d=JSON.parse(r.responseText);
   if(d&&d.error){msg=d.error;}
   if(d&&d.session_id&&ok){msg+=' -- session '+d.session_id;}
  }catch(e){}
  todayAnnounce(msg,false);
  if(ok&&location.search.indexOf('today=')<0){}
 };
 r.onerror=function(){todayAnnounce(errText,true);};
 r.send(JSON.stringify(body));
}
function focusedBank(){
 var banks=TODAY.banks||[];
 if(banks.length===1){return banks[0];}
 return '';
}
document.addEventListener('click',function(ev){
 var b=ev.target.closest&&ev.target.closest('button.start');
 if(!b)return;
 var bank=focusedBank();
 if(!bank){todayAnnounce('Choose a bank to start a focused session.',true);return;}
 var body={bank:bank,objective:b.getAttribute('data-objective'),count:10,
           snapshot:TODAY.claim||{}};
 todayPost('/api/start',body,'Focused session started.',
           'Start blocked. Refresh Today and try again.');
});
document.querySelectorAll('.override-dialog').forEach(function(dlg){
 var trigger=document.getElementById(dlg.id);
 if(!trigger){return;}
 trigger.addEventListener('click',function(){
  if(typeof dlg.showModal==='function'){dlg.showModal();}
  else{dlg.setAttribute('open','');}
 });
 dlg.addEventListener('close',function(){
  if(dlg.returnValue==='confirm'){
   var bank=focusedBank();
   if(!bank){todayAnnounce('Choose a bank to request an override.',true);return;}
   todayPost('/api/override',
     {bank:bank,objective:dlg.getAttribute('data-objective')||'',
      count:10,token:TODAY.confirm||'start one additional sitting'},
     'One additional sitting started.','Override refused. Refresh Today.');
  }
 });
});
document.querySelectorAll('form.lesson-complete').forEach(function(form){
 form.addEventListener('submit',function(ev){
  ev.preventDefault();
  var ref=form.querySelector('select[name=ref]').value;
  todayPost('/api/lesson-complete',{bank:form.getAttribute('data-bank'),ref:ref},
    'Lesson marked complete.','Lesson completion refused.');
 });
});
