const $=id=>document.getElementById(id);
const key='itembank-workspace-demo-v1';
let returnPoint=null, noticeTimer;
function announce(text){$('notice').textContent=text;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>$('notice').textContent='',3500)}
function appearance(dark){document.body.classList.toggle('dark',dark);$('theme').textContent=dark?'Light':'Dark';$('theme').setAttribute('aria-label',`Switch to ${dark?'light':'dark'} appearance`)}
appearance(new URLSearchParams(location.search).get('theme')==='dark');
$('theme').onclick=()=>appearance(!document.body.classList.contains('dark'));
function companion(kind){$('reference-panel').hidden=kind!=='reference';$('note-panel').hidden=kind!=='note';document.querySelectorAll('[data-companion]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.companion===kind));}
function view(kind,focus=true){document.body.dataset.view=kind;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.view===kind));if(kind!=='reading'){document.body.classList.remove('focus');$('focus').setAttribute('aria-pressed','false');$('focus').textContent='Focus reading';companion(kind)}if(focus){if(kind==='note')$('note').focus();else if(kind==='reference')$('tab-reference').focus();else $('reading').focus({preventScroll:true})}}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{if(b.dataset.view!=='reading')remember(b);view(b.dataset.view,false)});
document.querySelectorAll('[data-companion]').forEach(b=>b.onclick=()=>companion(b.dataset.companion));
function remember(el){returnPoint={y:window.scrollY,el}}
$('reference-open').onclick=()=>{remember($('reference-open'));view('reference',false);if(innerWidth<=760)window.scrollTo(0,0);$('reference-panel').querySelector('h2').tabIndex=-1;$('reference-panel').querySelector('h2').focus({preventScroll:true})};
$('note-open').onclick=()=>{remember($('note-open'));view('note');if(innerWidth<=760)window.scrollTo(0,0)};
document.querySelectorAll('.return-passage').forEach(b=>b.onclick=()=>{view('reading',false);if(returnPoint){window.scrollTo(0,returnPoint.y);returnPoint.el.focus({preventScroll:true})}else{$('passage').scrollIntoView();$('reference-open').focus({preventScroll:true})}});
$('highlight').onclick=()=>{const active=$('passage').classList.toggle('marked');$('highlight').setAttribute('aria-pressed',active);announce(active?'Passage highlighted for this visit.':'Highlight removed.')};
$('note').oninput=()=>{$('save-status').textContent='Unsaved demo draft'};
$('save').onclick=()=>{try{localStorage.setItem(key,JSON.stringify({text:$('note').value}));$('save-status').textContent='Saved in this browser';}catch(e){$('save-status').textContent='Save unavailable. Draft retained; retry or copy it.'}};
try{const saved=JSON.parse(localStorage.getItem(key)||'null');if(saved&&typeof saved.text==='string'){$('note').value=saved.text;$('save-status').textContent='Saved demo note restored'}}catch(e){$('save-status').textContent='Saved note unavailable. New draft is still editable.'}
function time(){const t=Number($('elapsed').value);$('seconds').textContent=`${t} seconds`;$('a-distance').textContent=`${3*t} m`;$('b-distance').textContent=`${5*t} m`;$('bar-a').style.width=`${3*t/60*100}%`;$('bar-b').style.width=`${5*t/60*100}%`;$('meaning').textContent=`At ${t} seconds, A travels ${3*t} metres and B travels ${5*t} metres. The gap is ${2*t} metres.`}
$('elapsed').oninput=time;time();
let practiceReturn;
function practice(){practiceReturn={y:window.scrollY,el:document.activeElement};$('lesson').hidden=true;$('practice').hidden=false;view('reading',false);window.scrollTo(0,0);$('answer').focus({preventScroll:true})}
$('practice-open').onclick=practice;$('practice-bottom').onclick=practice;
$('practice-return').onclick=()=>{$('practice').hidden=true;$('lesson').hidden=false;if(practiceReturn){window.scrollTo(0,practiceReturn.y);practiceReturn.el.focus({preventScroll:true})}};
$('reveal').onclick=()=>{$('worked').hidden=false};
$('focus').onclick=()=>{const active=document.body.classList.toggle('focus');$('focus').setAttribute('aria-pressed',active);$('focus').textContent=active?'Show companion':'Focus reading'};
let ratio=64;
function resize(value){ratio=Math.max(45,Math.min(72,value));$('workspace').style.setProperty('--reader',`${ratio}%`);$('divider').setAttribute('aria-valuenow',Math.round(ratio))}
$('divider').onkeydown=e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();resize(ratio+(e.key==='ArrowRight'?2:-2))}};
$('divider').onpointerdown=e=>{e.preventDefault();$('divider').setPointerCapture(e.pointerId);$('divider').onpointermove=ev=>{const box=$('workspace').getBoundingClientRect();resize((ev.clientX-box.left)/box.width*100)};$('divider').onpointerup=()=>{$('divider').onpointermove=null}};
view('reading',false);
