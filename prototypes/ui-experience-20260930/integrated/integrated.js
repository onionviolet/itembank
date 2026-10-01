/* Disposable view arrangement. Demo-only browser note handling remains explicit. */
(() => {
  const $ = id => document.getElementById(id);
  let origin = null;
  function showCompanion() {
    $('workspace').classList.remove('focus-reading');
    $('focus-reading').setAttribute('aria-pressed', 'false');
    $('focus-reading').textContent = 'Focus reading';
  }
  function note(trigger) {
    origin = {control: trigger, y: window.scrollY};
    showCompanion();
    $('note').focus();
  }
  $('open-note').onclick = event => note(event.currentTarget);
  $('append-passage').onclick = event => {
    $('note').value += ($('note').value ? '\n\n' : '') + 'Source passage: ' + $('source-passage').textContent + '\nMy thought: ';
    $('note').dispatchEvent(new Event('input', {bubbles:true}));
    note(event.currentTarget);
  };
  $('return-passage').onclick = () => {
    if (origin) {origin.control.focus({preventScroll:true}); window.scrollTo({top:origin.y, behavior:'instant'});}
    else {$('open-note').focus();}
  };
  $('focus-reading').onclick = () => {
    const active = $('workspace').classList.toggle('focus-reading');
    $('focus-reading').setAttribute('aria-pressed', String(active));
    $('focus-reading').textContent = active ? 'Show companion' : 'Focus reading';
  };
  $('companion-width').oninput = event => $('workspace').style.setProperty('--companion-width', event.target.value+'px');
  matchMedia('(max-width:767px)').addEventListener('change', event => {if(event.matches)showCompanion()});
  document.querySelector('.integrated-tools').hidden = false;
  $('append-passage').hidden = false;
  $('return-passage').hidden = false;
})();
