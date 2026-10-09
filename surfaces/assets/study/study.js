
const CARDS=__DATA__;
const esc=s=>(s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const REDUCED=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
const deck=document.getElementById("deck"),status=document.getElementById("status"),prog=document.getElementById("prog");
let mode="flash",order=[],i=0,queue=[],setAside=0;
const selected={};
function shuffle(a){for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]]}return a}
function cardEl(n){return deck.querySelector('[data-card="'+n+'"]')}
function say(t){status.textContent=t}
function setMode(m){mode=m;document.getElementById("tFlash").classList.toggle("on",m==="flash");document.getElementById("tLearn").classList.toggle("on",m==="learn");start()}
document.getElementById("tFlash").onclick=()=>setMode("flash");
document.getElementById("tLearn").onclick=()=>setMode("learn");
function show(n){deck.querySelectorAll("[data-card]").forEach((c,k)=>{c.hidden=k!==n})}
function syncState(c){
  const revealed=!c.querySelector("[data-explain]").hidden;
  const r=c.querySelector("[data-reveal]");
  if(!revealed){
    r.textContent="Reveal explanation";
    r.setAttribute("data-action-primary","");
    r.removeAttribute("aria-disabled");
  }
  c.querySelector("[data-acts=front]").hidden=revealed;
  c.querySelector("[data-acts=revealed]").hidden=!(revealed&&mode==="flash");
  c.querySelector("[data-acts=rating]").hidden=!(revealed&&mode==="learn");
}
function reveal(c){
  const sec=c.querySelector("[data-explain]");
  if(sec.hidden){say("Revealing explanation\u2026");sec.hidden=false;}
  const sel=selected[c.dataset.card]||[];
  sel.forEach(k=>{
    const d=c.querySelector('[data-opt="'+k+'"]');
    if(!d)return;
    d.open = true;
    const p=d.querySelector("p");
    if(p&&!p.querySelector(".badge.selected")){
      const b=document.createElement("span");
      b.className="badge selected";
      b.textContent="Selected";
      p.insertBefore(b,p.firstChild);
    }
  });
  const r=c.querySelector("[data-reveal]");
  r.textContent="Explanation revealed";
  r.setAttribute("aria-disabled","true");
  r.removeAttribute("data-action-primary");
  syncState(c);
  say("Explanation revealed. Review the answer and rationale.");
  r.focus({preventScroll:true});
}
function wireRecall(c){
  c.querySelectorAll("[data-recall]").forEach(b=>{
    b.addEventListener("click",()=>{
      const k=b.getAttribute("data-recall");
      const wasOn=b.getAttribute("aria-pressed")==="true";
      b.setAttribute("aria-pressed",wasOn?"false":"true");
      let s=selected[c.dataset.card]||(selected[c.dataset.card]=[]);
      const at=s.indexOf(k);
      if(wasOn){if(at>=0)s.splice(at,1)}else if(at<0)s.push(k);
      say(wasOn?"Your recall choice cleared. Not graded.":"Your recall choice recorded. Not graded.");
    });
  });
}
function wireNav(c){
  c.querySelectorAll("[data-prev]").forEach(prev=>prev.addEventListener("click",()=>{
    if(mode==="flash"){if(i>0){i--;render()}}
    else if(queue.length>1){queue.unshift(queue.pop());render()}
  }));
  c.querySelectorAll("[data-next]").forEach(next=>next.addEventListener("click",()=>{
    if(mode==="flash"){if(i<CARDS.length-1){i++;render()}else finish("Flashcards done.")}
    else{queue.push(queue.shift());render()}
  }));
  c.querySelector("[data-got]").addEventListener("click",()=>{if(mode==="learn"){setAside++;queue.shift();render()}});
  c.querySelector("[data-miss]").addEventListener("click",()=>{if(mode==="learn"){queue.push(queue.shift());render()}});
  c.querySelector("[data-reveal]").addEventListener("click",()=>reveal(c));
}
function render(){mode==="flash"?renderFlash():renderLearn()}
function renderFlash(){
  if(i>=CARDS.length)return finish("Flashcards done.");
  show(i);const c=cardEl(i);
  prog.style.width=((i+1)/CARDS.length*100)+"%";
  syncState(c);
  say("Flashcards · card "+(i+1)+" of "+CARDS.length);
  const r=c.querySelector("[data-reveal]");
  if(r&&!REDUCED)r.focus({preventScroll:true});
}
function renderLearn(){
  if(!queue.length)return finish("Review pile complete. This recall rating was not graded or saved.");
  show(queue[0]);const c=cardEl(queue[0]);
  prog.style.width=(setAside/CARDS.length*100)+"%";
  syncState(c);
  say("Learn · "+setAside+" set aside / "+CARDS.length+" · "+queue.length+" in pile. Recall ratings are not graded or saved.");
  const r=c.querySelector("[data-reveal]");
  if(r&&!REDUCED)r.focus({preventScroll:true});
}
function finish(msg){
  prog.style.width="100%";say("");
  deck.innerHTML='<div class="done"><div class="big">Done</div><p>'+esc(msg)+'</p><button type="button" class="b nav" data-again>Shuffle and restart</button></div>';
  document.querySelector("[data-again]").onclick=start;
}
function start(){
  order=shuffle([...Array(CARDS.length).keys()]);
  if(mode==="flash"){i=0;renderFlash()}else{queue=[...order];setAside=0;renderLearn()}
}
deck.querySelectorAll("[data-card]").forEach(c=>{wireRecall(c);wireNav(c)});
start();
