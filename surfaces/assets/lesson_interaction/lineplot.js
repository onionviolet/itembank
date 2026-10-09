
(() => {
  function coordinate(x, y) { return (160 + x * 55) + ',' + (120 - y * 17); }
  function initializeLineplot() {
    document.querySelectorAll('.lesson-lineplot').forEach(root => {
      if (root.dataset.initialized === '1') return;
      const m = Number(root.dataset.m), b = Number(root.dataset.b);
      const changed = Number(root.dataset.changedB);
      if (![m,b,changed].every(Number.isSafeInteger) ||
          [m,b,changed].some(n => n < -2 || n > 2) || changed === b) return;
      const controls = root.querySelector('.lineplot-controls');
      const staticView = root.querySelector('.lineplot-static');
      const selection = root.querySelector('.lineplot-prediction');
      const commit = root.querySelector('.lineplot-commit');
      const cancel = root.querySelector('.lineplot-cancel');
      const choice = root.querySelector('.lineplot-choice');
      const manipulate = root.querySelector('.lineplot-manipulate');
      const value = root.querySelector('.lineplot-value');
      const reset = root.querySelector('.lineplot-reset');
      const live = root.querySelector('.lineplot-live');
      const equation = root.querySelector('.lineplot-equation');
      const points = root.querySelectorAll('.lineplot-y');
      const line = root.querySelector('.lineplot-line');
      if (!controls || !staticView || !selection || !commit || !choice ||
          !manipulate || !value || !reset || !live || !equation ||
          points.length !== 3 || !line) return;
      let prediction = '';
      const state = window.itembankLessonExploration(root, 'lineplot', value =>
        value && ['all','origin','none'].includes(value.prediction) &&
        Number.isSafeInteger(value.intercept) && value.intercept >= -2 && value.intercept <= 2);
      const restored = state.read();
      function update(remember = true) {
        const current = Number(value.value);
        if (!Number.isSafeInteger(current) || current < -2 || current > 2) return;
        const shift = current - b;
        equation.textContent = 'y = ' + m + 'x ' + (current < 0 ? '- ' + Math.abs(current) : '+ ' + current);
        [-2,0,2].forEach((x, i) => { points[i].textContent = String(m*x + current); });
        line.setAttribute('points', [-2,0,2].map(x => coordinate(x,m*x+current)).join(' '));
        live.textContent = 'Intercept ' + current + '. At x = -2, 0, 2, y = ' +
          [-2,0,2].map(x => m*x+current).join(', ') + '. Compared with the starting rule, each y value ' +
          (shift > 0 ? 'increases by ' + shift : shift < 0 ?
            'decreases by ' + Math.abs(shift) : 'is unchanged') + '. Slope remains ' + m + '.';
        if (remember && prediction) state.write({prediction,intercept:current});
      }
      function cancelDraft() {
        selection.value = prediction;
        if (cancel) cancel.disabled = true;
      }
      selection.onchange = () => {if (cancel) cancel.disabled = selection.value === prediction;};
      selection.addEventListener('blur', event => {
        if (event.relatedTarget !== commit && event.relatedTarget !== cancel) cancelDraft();
      });
      root.addEventListener('keydown', event => {
        if (event.key === 'Escape') {event.preventDefault(); cancelDraft();}
      });
      window.addEventListener('blur', cancelDraft);
      window.addEventListener('pagehide', cancelDraft);
      if (cancel) cancel.onclick = cancelDraft;
      value.value = String(restored ? restored.intercept : changed);
      function reveal(remember = true) {
        prediction = selection.value;
        if (cancel) cancel.disabled = true;
        choice.textContent = 'Your prediction: ' + selection.options[selection.selectedIndex].text + '.';
        manipulate.hidden = false;
        staticView.hidden = false;
        update(remember);
      }
      commit.onclick = () => {
        if (!selection.value) {
          choice.textContent = 'Choose a prediction before revealing the change.';
          selection.focus();
          return;
        }
        reveal();
        value.focus();
      };
      value.onchange = () => update();
      reset.onclick = () => {
        state.clear(); prediction = ''; cancelDraft(); value.value = String(changed);
        manipulate.hidden = true; staticView.hidden = true;
        choice.textContent = 'Exploration reset. Choose a prediction to start again.';
        selection.focus();
      };
      root.dataset.initialized = '1';
      root.classList.add('lineplot-enhanced');
      staticView.hidden = true;
      controls.hidden = false;
      if (restored) {selection.value = restored.prediction; reveal(false);}
    });
  }
  initializeLineplot();
  window.addEventListener('pageshow', initializeLineplot);
})();
</script>