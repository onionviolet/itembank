const $ = (id) => document.getElementById(id);
const labels = [
  {id:'evaporation',text:'Evaporation',x:19,y:48,context:'Arrow rising from the lake'},
  {id:'condensation',text:'Condensation',x:66,y:25,context:'Cloud formation area'},
  {id:'precipitation',text:'Precipitation',x:61,y:55,context:'Arrow falling from cloud to land'},
  {id:'runoff',text:'Runoff',x:77,y:82,context:'Arrow moving across land toward water'},
];
const rows = [['Monday',12,18],['Tuesday',5,5],['Wednesday',0,7],['Thursday',9,4]];
const background = `<svg viewBox="0 0 760 420" role="img" aria-label="A lake below a hill, cloud, and sun. Arrows rise from the lake, fall from cloud to land, and travel downhill to water."><rect width="760" height="420" fill="#eaf1e5"/><circle cx="112" cy="82" r="39" fill="#e1b34e"/><path d="M0 292 C100 230 180 260 273 285 C363 310 447 212 560 242 C640 262 699 228 760 237V420H0Z" fill="#93b880"/><path d="M0 341C122 320 222 365 347 340C466 317 580 353 760 333V420H0Z" fill="#6f9e90"/><path d="M0 350C120 330 227 374 350 349C482 322 602 360 760 340" fill="none" stroke="#d6e9dc" stroke-width="7"/><path d="M338 104C360 64 413 64 433 107C467 77 520 102 520 145H299C299 116 316 101 338 104Z" fill="#fffdf8" stroke="#b6c7bd" stroke-width="3"/><g stroke="#315c49" stroke-width="5" fill="none" stroke-linecap="round"><path d="M154 290C151 237 191 198 244 177M225 170l20 4-10 18M416 158C405 200 407 238 416 275M409 266l8 20 14-15M566 298C514 305 474 316 424 336M434 324l-21 12 19 10"/></g></svg>`;
function initialState() {
  return {
    figure:{selection:new Set(['evaporation','precipitation']),instruction:'Name the water processes at the marked locations.',purpose:'Match a process label to its location and direction in the watershed.',format:'placement',showBank:true,answers:{blank:{},placement:{}}},
    tableComparison:{selection:new Set(['0-1','0-2']),instruction:globalThis.ItembankTableExport.instruction,purpose:globalThis.ItembankTableExport.purpose,format:'comparison',showBank:false,answers:{comparison:{}}},
    table:{selection:new Set(['0-2']),instruction:'Complete the selected rainfall measurements in millimeters.',purpose:'Retrieve selected source values with day, gauge, and interval preserved.',format:'blank',showBank:true,answers:{blank:{},placement:{}}},
  };
}
let state=initialState(),source='figure',view='edit',picked='';
let exportedBank=null;
const active=()=>source==='table'&&state.table.format==='comparison'?state.tableComparison:state[source];
const comparison=()=>source==='table'&&active().format==='comparison';
function clearExport() {
  exportedBank=null;
  $('export-bank-panel').hidden=true;$('export-bank-text').textContent='';
  $('export-bank-download').disabled=true;$('export-bank-status').textContent='';
  $('export-bank-error').hidden=true;$('export-bank-error').textContent='';
}
const responses=()=>active().answers[active().format];
const bankVisible=()=>active().format==='placement'||active().showBank;
const bankLabels=()=>[...labels].sort((a,b)=>a.text.localeCompare(b.text));
const locator=()=>source==='figure'?'figures.md#source-figure-2':'figures.md#source-table-1';
function node(tag,text,className) {const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function say(text) {$('activity-status').textContent=text;}
function toggle(id) {
  const s=active();s.selection.has(id)?s.selection.delete(id):s.selection.add(id);
  delete s.answers.blank[id];delete s.answers.placement[id];render();
  document.querySelector(`[data-select="${id}"]`)?.focus({preventScroll:true});
  say(`${s.selection.size} ${source==='figure'?'labels':'cells'} selected for the activity.`);
}
function setAnswer(id,value) {
  if(active().format==='placement'&&value){
    for(const [other,placed] of Object.entries(responses())){
      if(other!==id&&placed===value)delete responses()[other];
    }
  }
  responses()[id]=value;
  if(active().format==='placement'){
    labels.forEach((item,index)=>{
      const placed=responses()[item.id]||'';
      const target=document.querySelector(`[data-target="${item.id}"]`);
      if(target){
        target.textContent=placed||String(index+1);
        target.setAttribute('aria-label',`Location ${index+1}: ${item.context}${placed?', placed '+placed:''}`);
      }
      const select=document.querySelector(`select[data-answer="${item.id}"]`);
      if(select)select.value=placed;
    });
  }
  say('Preview response changed. Nothing is evaluated or saved.');
}
function figure(original=false) {
  const canvas=node('div',undefined,'canvas');canvas.innerHTML=background;
  labels.forEach((item,index)=>{
    const selected=active().selection.has(item.id),masked=!original&&view==='preview'&&selected;
    let element;
    if(original || (!masked&&view==='preview')) {
      element=node('span',item.text,'visual-label original-label');
    } else if(view==='edit') {
      element=node('button',item.text,'visual-label'+(selected?' selected':''));
      element.dataset.select=item.id;element.setAttribute('aria-pressed',String(selected));
      element.setAttribute('aria-label',`Select ${item.text} to hide in preview`);
      element.addEventListener('click',()=>toggle(item.id));
    } else {
      const value=active().format==='placement'?responses()[item.id]:'';
      element=node('button',value||String(index+1),'visual-label marker');
      element.dataset.target=item.id;
      element.setAttribute('aria-label',`Location ${index+1}: ${item.context}${value?', placed '+value:''}`);
      element.addEventListener('click',()=>{
        if(active().format==='placement'&&picked){setAnswer(item.id,picked);render();document.querySelector(`[data-target="${item.id}"]`)?.focus({preventScroll:true});say('Label placed in the preview. No placement is evaluated.');}
        else document.querySelector(`[data-answer="${item.id}"]`)?.focus();
      });
      element.addEventListener('dragover',e=>{if(active().format==='placement')e.preventDefault();});
      element.addEventListener('drop',e=>{
        e.preventDefault();const text=e.dataTransfer.getData('text/plain');
        if(active().format==='placement'&&labels.some(l=>l.text===text)){setAnswer(item.id,text);render();say('Label placed in the preview. No placement is evaluated.');}
      });
    }
    element.style.left=item.x+'%';element.style.top=item.y+'%';canvas.append(element);
  });return canvas;
}
function table(original=false) {
  const wrap=node('div',undefined,'tablewrap'),table=node('table',undefined,'rain');
  table.append(node('caption','Table 1 · Rainfall over equal 24-hour intervals'));
  const head=node('thead'),tr=node('tr');
  ['Day','Gauge A','Gauge B','Interval'].forEach(t=>{const th=node('th',t);th.scope='col';tr.append(th);});head.append(tr);table.append(head);
  const body=node('tbody');
  rows.forEach((row,i)=>{
    if(!original&&comparison()&&i!==0)return;
    const tr=node('tr'),th=node('th',row[0]);th.scope='row';tr.append(th);
    [1,2].forEach(j=>{
      const td=node('td'),id=`${i}-${j}`,selected=active().selection.has(id),context=`${row[0]}, Gauge ${j===1?'A':'B'}`;
      if(original||comparison())td.textContent=row[j]+' mm';
      else if(view==='edit'){
        const b=node('button',row[j]+' mm','cell');b.dataset.select=id;b.setAttribute('aria-pressed',String(selected));b.setAttribute('aria-label',`Select ${context}, ${row[j]} mm`);b.addEventListener('click',()=>toggle(id));td.append(b);
      }else if(selected){
        const input=node('input');input.dataset.answer=id;input.setAttribute('aria-label',context+' in millimeters');input.value=responses()[id]||'';input.autocomplete='off';input.addEventListener('input',()=>setAnswer(id,input.value));td.append(input);
      }else td.textContent=row[j]+' mm';tr.append(td);
    });tr.append(node('td','24 hours'));body.append(tr);
  });table.append(body);wrap.append(table);return wrap;
}
function responseControls() {
  const area=$('response-area');area.replaceChildren();
  if(view!=='preview')return;
  if(comparison()){
    const label=node('label', 'Your explanation (ungraded trial)', 'field');
    const input=node('textarea');input.id='comparison-answer';input.rows=4;input.value=responses().prose||'';
    input.addEventListener('input',()=>setAnswer('prose',input.value));label.append(input);area.append(label);
    area.append(node('p','Both source values stay visible. Explain the comparison in prose. Any future runtime response remains pending human review.','drop-help'));
    return;
  }
  if(bankVisible()){
    const heading=node('p',source==='figure'?'Word bank':'Value bank','drop-help');heading.id='answer-bank-title';area.append(heading);
    if(active().format!=='placement'){
      const bank=node('ul',undefined,'answer-bank');bank.id='answer-bank';bank.setAttribute('aria-labelledby','answer-bank-title');
      const words=source==='figure'?bankLabels().map(item=>item.text):[...new Set(rows.flatMap(row=>row.slice(1)))].sort((a,b)=>a-b).map(value=>value+' mm');
      words.forEach(word=>bank.append(node('li',word)));area.append(bank);
    }
  }
  if(source!=='figure')return;
  if(active().format==='placement') {
    area.append(node('p','Drag a label onto a marked location, or select a label and then a location. Use each label at most once. Moving it clears its previous location. The dropdowns provide the same choices.','drop-help'));
    const palette=node('div',undefined,'palette');palette.id='answer-bank';palette.setAttribute('aria-labelledby','answer-bank-title');
    bankLabels().forEach(item=>{
      const b=node('button',item.text);b.dataset.label=item.id;b.draggable=true;b.setAttribute('aria-pressed',String(picked===item.text));
      b.addEventListener('click',()=>{picked=item.text;responseControls();document.querySelector(`[data-label="${item.id}"]`)?.focus({preventScroll:true});say(`${picked} selected. Choose a numbered location.`);});
      b.addEventListener('dragstart',e=>e.dataTransfer.setData('text/plain',item.text));palette.append(b);
    });area.append(palette);
  }
  const fields=node('div',undefined,'responses');
  labels.forEach((item,i)=>{
    if(!active().selection.has(item.id))return;
    const label=node('label',undefined,'response-field');label.append(node('span',`${i+1}. ${item.context}`));
    const control=node(active().format==='placement'?'select':'input');control.dataset.answer=item.id;
    if(active().format==='placement'){
      const empty=node('option','Choose a label');empty.value='';control.append(empty);bankLabels().forEach(l=>{const option=node('option',l.text);option.value=l.text;control.append(option);});
    }else control.autocomplete='off';
    control.value=responses()[item.id]||'';
    control.addEventListener(active().format==='placement'?'change':'input',()=>{
      setAnswer(item.id,control.value);
      if(active().format==='placement')document.querySelector(`[data-target="${item.id}"]`).textContent=control.value||String(i+1);
    });label.append(control);fields.append(label);
  });area.append(fields);
}
function render() {
  clearExport();
  const s=active(),preview=view==='preview';
  document.querySelectorAll('[data-source]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.source===source)));
  $('instruction').value=s.instruction;$('purpose').value=s.purpose;
  $('format-options').hidden=source==='table';
  $('table-treatment').hidden=source!=='table';
  $('bank-options').hidden=comparison();
  document.querySelectorAll('[name="table-format"]').forEach(r=>r.checked=r.value===s.format);
  document.querySelectorAll('[name="format"]').forEach(r=>r.checked=r.value===s.format);
  $('show-bank').checked=bankVisible();$('show-bank').disabled=s.format==='placement';
  $('bank-help').textContent=s.format==='placement'?'Placement uses supplied labels. Choose typed answers to practice without a bank.':source==='table'?'Turn the bank off for recall practice. With a bank, visible cells may let you solve this by elimination.':'Turn the bank off for recall practice. Your typed responses stay in place.';
  $('source-locator').textContent=source==='figure'?'Figure 2 / Original synthetic source':'Table 1 / Original synthetic source';
  $('activity-title').textContent=source==='figure'?'Water moving through a landscape':'Reading rainfall observations';
  $('edit-view').setAttribute('aria-pressed',String(!preview));$('preview-view').setAttribute('aria-pressed',String(preview));
  $('preview-view').disabled=s.selection.size===0;$('review-open').disabled=s.selection.size===0;
  $('selection-count').textContent=`${s.selection.size} ${source==='figure'?'labels':'cells'} selected`;
  $('view-help').textContent=preview?'Try the activity. Responses are ungraded and temporary.':source==='figure'?'Select labels to replace with numbered locations.':'Select cells to turn into blanks. Keep headers and units visible.';
  $('preview-instruction').hidden=!preview;$('preview-instruction').textContent=s.instruction;
  if(comparison()){
    $('selection-count').textContent='Monday / both gauges';
    $('view-help').textContent='Compare both Monday readings over the same 24 hours. Values stay visible.';
  }
  $('visual').replaceChildren(source==='figure'?figure():table());responseControls();
  $('footer-help').textContent=preview?'Inspect the original at any time, then return to these responses.':'Your instruction, purpose, and selection determine the reviewable draft.';
}
function review() {
  const s=active();
  exportedBank=null;
  $('export-bank-panel').hidden=true;$('export-bank-text').textContent='';
  $('export-bank-download').disabled=true;$('export-bank-status').textContent='';
  $('export-bank-error').hidden=true;$('export-bank-error').textContent='';
  $('export-bank-show').disabled=!(comparison()||(source==='figure'&&s.format==='placement'&&s.selection.size>0));
  $('export-bank-help').textContent=source==='figure'&&s.format==='placement'?'Keeps the selected locations and all four supplied labels. Extra labels get a Not used destination.':'Bank export supports diagram placement and Monday comparison. Typed labels and value retrieval remain preview-only.';
  if(comparison())$('export-bank-help').textContent='Exports both Monday readings and one prose explanation using short. The proposed rubric remains pending human review.';
  const selected=source==='figure'?labels.filter(l=>s.selection.has(l.id)).map(l=>`${labels.indexOf(l)+1}. ${l.context} [${l.id}]`):[...s.selection].map(id=>{const [i,j]=id.split('-').map(Number);return `${rows[i][0]}, Gauge ${j===1?'A':'B'} [${id}]`;});
  $('review-summary').textContent=`${selected.length} ${source==='figure'?'locations':'cells'} will accept ${s.format==='placement'?'a chosen process label':'text'}. The source is unchanged.`;
  $('draft-text').textContent=`# Treatment draft\n\nStatus: unaccepted prototype\nSource: ${locator()}\nResponse shape: ${s.format==='placement'?'one label per selected location, each label used at most once':'one text field per selected location'}\nAnswer bank: ${bankVisible()?'shown':'hidden for recall practice'}\nSource presentation: current adapted preview with original-source dialog. Reproduction and future presentation remain user choices.\n\n## Instruction\n${s.instruction}\n\n## Selected locations\n${selected.map(x=>'- '+x).join('\n')}\n\n## Author purpose\n${s.purpose}\n\n## Static representation\nUse the source diagram with the selected labels replaced by the numbered locations above. For a table, preserve row and column headings and units while leaving selected values blank.\n\nAssessment key: not defined\nRuntime validation: not performed\nReviewer: pending`;
  if(comparison()){
    $('review-summary').textContent='One prose explanation compares Monday readings. Both values stay visible. Human review is pending.';
    $('draft-text').textContent=`# Treatment draft\n\nStatus: unaccepted prototype\nSource: figures.md#source-table-1, Table 1, Monday row\nGauge A: 12 mm\nGauge B: 18 mm\nCollection interval: 24 hours for both\nResponse shape: one prose explanation, pending human review\n\n## Instruction\n${s.instruction}\n\n## Author purpose\n${s.purpose}\n\nStatic representation: both readings and interval remain visible beside the prompt. No value bank or hidden cells.\nRuntime validation: not performed\nReviewer: pending`;
  }
  $('review-dialog').showModal();
}
function createBankDraft() {
  try{
    const exporter=comparison()?globalThis.ItembankTableExport:globalThis.ItembankPlacementExport;
    if(!exporter)throw new Error('The bank exporter did not load. Reload the page to try again.');
    const s=active();
    const draft=exporter.create({source,format:s.format,selectedIds:[...s.selection],instruction:s.instruction,purpose:s.purpose,wordBank:bankVisible()});
    exportedBank=draft;
    $('export-bank-text').textContent=draft.text;
    $('export-bank-summary').textContent=`${draft.selectedCount} selected locations, four supplied labels${draft.unusedCount?`, ${draft.unusedCount} labels assigned to Not used`:''}. The downloaded file includes its synthetic source and static description.${draft.instructionNormalized?' Instruction line breaks become spaces in the question. The original wording is retained in the author metadata.':''}`;
    if(comparison())$('export-bank-summary').textContent='One short item with Monday source values, exact locator, author wording, and a proposed human-review rubric. No trial answer is included.';
    $('export-bank-error').hidden=true;$('export-bank-panel').hidden=false;
    $('export-bank-download').disabled=false;
    $('export-bank-text').focus({preventScroll:true});
  }catch(error){
    exportedBank=null;$('export-bank-panel').hidden=true;$('export-bank-download').disabled=true;
    $('export-bank-error').textContent=error.message;$('export-bank-error').hidden=false;
  }
}
function downloadBankDraft() {
  if(!exportedBank)return;
  const url=URL.createObjectURL(new Blob([exportedBank.text],{type:'text/markdown;charset=utf-8'}));
  const link=node('a');link.href=url;link.download=exportedBank.filename;
  document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  $('export-bank-status').textContent='Download requested. The file is an unaccepted draft with a proposed source key or human-review rubric.';
}
document.querySelectorAll('[data-source]').forEach(b=>b.addEventListener('click',()=>{source=b.dataset.source;view='edit';picked='';render();say('Source changed. Each source keeps its own draft in this page.');}));
document.querySelectorAll('[name="format"]').forEach(r=>r.addEventListener('change',()=>{active().format=r.value;render();}));
document.querySelectorAll('[name="table-format"]').forEach(r=>r.addEventListener('change',()=>{state.table.format=r.value;view='edit';render();say('Table treatment changed. Each treatment keeps its own wording and trial responses.');}));
$('show-bank').addEventListener('change',e=>{active().showBank=e.target.checked;render();say(bankVisible()?'Answer bank shown. Responses retained.':'Answer bank hidden for recall practice. Responses retained.');});
$('instruction').addEventListener('input',e=>{active().instruction=e.target.value;clearExport();$('preview-instruction').textContent=e.target.value;});
$('purpose').addEventListener('input',e=>{active().purpose=e.target.value;clearExport();});
$('edit-view').addEventListener('click',()=>{view='edit';render();say('Editing the selection. Preview responses are retained for unchanged locations.');});
$('preview-view').addEventListener('click',()=>{view='preview';render();say('Preview ready. No answers are evaluated.');});
$('source-open').addEventListener('click',()=>{
  $('source-dialog-title').textContent=source==='figure'?'Figure 2 · Water moving through a landscape':'Table 1 · Rainfall observations';
  $('dialog-locator').textContent=locator();$('raw-source').href=locator();
  $('source-content').replaceChildren(source==='figure'?figure(true):table(true));
  if(source==='figure')$('source-content').append(node('p','The figure names four movements of water in the illustrated watershed: evaporation rises from the lake, condensation names cloud formation, precipitation falls from the cloud, and runoff moves across land toward the stream and lake.'));
  $('source-dialog').showModal();
});
$('review-open').addEventListener('click',review);
$('export-bank-show').addEventListener('click',createBankDraft);
$('export-bank-download').addEventListener('click',downloadBankDraft);
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>$(b.dataset.close).close()));
$('reset').addEventListener('click',()=>{state=initialState();source='figure';view='edit';picked='';render();say('Studio reset. No changes were saved.');});
render();
