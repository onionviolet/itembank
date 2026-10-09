
(() => {
  function initialize() {
    document.querySelectorAll('.lesson-comparison').forEach(root => {
      if (root.dataset.initialized === '1') return;
      const input = root.querySelector('input[type=range]');
      const number = root.querySelector('.comparison-number');
      const decrease = root.querySelector('.comparison-decrease');
      const increase = root.querySelector('.comparison-increase');
      const reset = root.querySelector('.comparison-reset');
      const cancel = root.querySelector('.comparison-cancel');
      const controls = root.querySelector('.comparison-controls');
      const direct = root.querySelector('.comparison-direct');
      const handle = root.querySelector('.comparison-handle');
      if (!input || !number || !decrease || !increase || !reset || !controls || !direct || !handle) return;
      const a = Number(input.dataset.a), initial = Number(input.defaultValue);
      const maximum = Number(input.max), unit = input.dataset.unit;
      if (![a, initial, maximum].every(Number.isSafeInteger) || maximum < 1 ||
          maximum > 10000 || a < 0 || a > maximum || initial < 0 || initial > maximum) return;
      let gesture = null;
      const state = window.itembankLessonExploration(root, 'comparison', value =>
        Number.isSafeInteger(value) && value >= 0 && value <= maximum);
      const restored = state.read();
      function update(remember = true) {
        let b = Number(input.value);
        if (!Number.isSafeInteger(b) || b < 0 || b > maximum) b = initial;
        input.value = String(b);
        number.value = String(b);
        number.setCustomValidity('');
        decrease.disabled = b === 0;
        increase.disabled = b === maximum;
        const delta = b - a;
        root.querySelector('.comparison-b').textContent = String(b);
        root.querySelector('.comparison-meter-b').value = b;
        direct.style.setProperty('--comparison-b', (b / maximum * 100) + '%');
        handle.dataset.pending = gesture && gesture.moved ? '1' : '0';
        if (cancel) cancel.disabled = !gesture && number.value === input.value;
        root.querySelector('.comparison-result').textContent =
          'B − A = ' + delta + ' ' + unit + '. ' +
          (delta === 0 ? 'Equal quantities.' : 'B is ' + Math.abs(delta) + ' ' + unit +
          (delta > 0 ? ' higher.' : ' lower.')) +
          (b === initial ? ' Authored starting value.' : ' Hypothetical value.') +
          (gesture && gesture.moved ? ' Preview. Release to keep; Escape to cancel.' : '');
        if (remember && !gesture) state.write(b);
      }
      function finish(cancelled) {
        if (!gesture) return;
        const previous = gesture;
        gesture = null;
        if (cancelled) input.value = String(previous.start);
        if (handle.hasPointerCapture && handle.hasPointerCapture(previous.id)) {
          handle.releasePointerCapture(previous.id);
        }
        update(!cancelled);
      }
      handle.onpointerdown = event => {
        if (gesture || !event.isPrimary || event.button !== 0) return;
        const bounds = direct.getBoundingClientRect();
        if (!bounds.width) return;
        event.preventDefault();
        input.focus({preventScroll:true});
        const start = Number(input.value);
        gesture = {id:event.pointerId, start, x:event.clientX, y:event.clientY,
          left:bounds.left, width:bounds.width, height:bounds.height,
          offset:event.clientX - (bounds.left + start / maximum * bounds.width), moved:false};
        if (cancel) cancel.disabled = false;
        try { handle.setPointerCapture(event.pointerId); }
        catch (_) { finish(true); }
      };
      function previewPointer(event) {
        if (!gesture || gesture.id !== event.pointerId) return;
        const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;
        if (!gesture.moved && dx * dx + dy * dy < 16) return;
        gesture.moved = true;
        input.value = String(Math.max(0, Math.min(maximum, Math.round(
          (event.clientX - gesture.left - gesture.offset) / gesture.width * maximum))));
        update();
      }
      handle.onpointermove = previewPointer;
      handle.onpointerup = event => {
        if (gesture && gesture.id === event.pointerId) { previewPointer(event); finish(false); }
      };
      handle.onpointercancel = event => { if (gesture && gesture.id === event.pointerId) finish(true); };
      handle.onlostpointercapture = event => { if (gesture && gesture.id === event.pointerId) finish(true); };
      root.addEventListener('keydown', event => {
        if (event.key === 'Escape') { event.preventDefault(); cancelChange(); }
      });
      ['blur', 'resize', 'pagehide'].forEach(name => window.addEventListener(name, () => finish(true)));
      if (typeof ResizeObserver === 'function') {
        new ResizeObserver(() => {
          if (!gesture) return;
          const bounds = direct.getBoundingClientRect();
          if (bounds.width !== gesture.width || bounds.height !== gesture.height) finish(true);
        }).observe(direct);
      }
      input.addEventListener('blur', () => finish(true));
      function cancelChange() {
        finish(true); number.value = input.value; number.setCustomValidity('');
        if (cancel) cancel.disabled = true;
      }
      if (cancel) {
        cancel.onclick = cancelChange;
        cancel.onpointerdown = event => event.preventDefault();
      }
      input.value = String(restored === null ? initial : restored);
      input.oninput = () => { const value = input.value; finish(true); input.value = value; update(); };
      number.oninput = () => {number.setCustomValidity(''); if (cancel) cancel.disabled = number.value === input.value;};
      number.onchange = () => {
        finish(true);
        const b = Number(number.value);
        if (!number.value || !Number.isSafeInteger(b) || b < 0 || b > maximum) {
          number.setCustomValidity('Enter a whole number from 0 to ' + maximum + '.');
          number.reportValidity();
          return;
        }
        input.value = String(b);
        update();
      };
      decrease.onclick = () => { finish(true); input.value = String(Math.max(0, Number(input.value) - 1)); update(); };
      increase.onclick = () => { finish(true); input.value = String(Math.min(maximum, Number(input.value) + 1)); update(); };
      reset.onclick = () => { finish(true); state.clear(); input.value = String(initial); update(false); };
      update(false);
      root.dataset.initialized = '1';
      controls.hidden = false;
    });
  }
  initialize();
  window.addEventListener('pageshow', initialize);
})();
</script>