const $ = s => document.querySelector(s);
const params = new URLSearchParams(location.search);
const validComposition = ['atlas','studio','baseline'].includes(params.get('composition')) ? params.get('composition') : 'atlas';
$('#composition').value = validComposition;
$('#appearance').value = params.get('theme') === 'dark' ? 'dark' : 'light';
let previousComposition;
function appearance(){
  document.body.className = $('#composition').value;
  if(previousComposition !== $('#composition').value){
    for(const details of document.querySelectorAll('.reading-more,.source-more,.note-more')) details.open = $('#composition').value !== 'studio';
    previousComposition = $('#composition').value;
  }
  document.documentElement.dataset.theme = $('#appearance').value;
  $('#baseline-css').disabled = $('#composition').value !== 'baseline';
  const url = new URL(location.href);
  url.searchParams.set('composition', $('#composition').value);
  url.searchParams.set('theme', $('#appearance').value);
  history.replaceState(null,'',url);
}
const baseline = document.createElement('link');
baseline.id='baseline-css'; baseline.rel='stylesheet'; baseline.href='baseline.css'; document.head.append(baseline);
$('#composition').addEventListener('change',appearance);$('#appearance').addEventListener('change',appearance);appearance();
function time(){const t=Number($('#elapsed').value);$('#clock').value=t;$('#a-value').value=`${3*t} m`;$('#b-value').value=`${5*t} m`;for(const [id,speed,y] of [['a',3,92],['b',5,188]]){const x=64+speed*t*8.8;$(`#walker-${id}`).setAttribute('transform',`translate(${x} ${y})`);$(`#distance-${id}`).setAttribute('d',`M64 ${y}H${x}`);}const text=`At ${t} seconds: A travels ${3*t} m; B travels ${5*t} m. B travels ${2*t} m farther.`;$('#description').textContent=text;$('#diagram-desc').textContent=text+' The scale runs from 0 to 60 metres.';}
$('#elapsed').addEventListener('input',time);
for(const button of document.querySelectorAll('[data-time]'))button.addEventListener('click',()=>{$('#elapsed').value=button.dataset.time;time();});
$('#private-note').addEventListener('input',()=>{$('.note-count').textContent=$('#private-note').value.trim()?'Draft':'Empty';});
for(const anchor of document.querySelectorAll('a[href="#note"],a[href="#source"],a[href="#reading"]'))anchor.addEventListener('click',()=>{const panel=$(anchor.getAttribute('href'));const details=panel.querySelector('details');if(details)details.open=true;});
$('#reveal').addEventListener('click',()=>{const answer=$('input[name=prediction]:checked');$('#feedback').hidden=false;if(answer){$('#elapsed').value='12';time();}$('#feedback').textContent=answer?'Demo explanation, unscored: doubling time doubles both distances. At 12 s, A travels 36 m and B 60 m. Their distance ratio stays 3:5.':'Choose a prediction first. This demo does not record a score.';});
for(const trigger of document.querySelectorAll('[data-practice]'))trigger.addEventListener('click',e=>{e.preventDefault();$('#practice').showModal();});
