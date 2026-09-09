"""Progressive enhancement of runtime-approved guided lesson content."""

CSS = """
.lesson-reading-controls {display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;margin-block:1rem}
.lesson-reading-controls button {min-height:44px;white-space:normal}
.lesson-reading-outline summary,.lesson-reading-detail summary {min-height:44px;cursor:pointer;font-weight:700}
.lesson-reading-outline a {display:inline-block;padding-block:.5rem}
.lesson-source-preview {margin-block:.75rem}
.lesson-source-preview summary {min-height:44px;cursor:pointer;font-weight:700}
.lesson-source-preview blockquote {white-space:pre-line;border-inline-start:3px solid currentColor;padding-inline-start:1rem}
#lesson-content .stage[aria-current="step"] {border-inline-start:3px solid currentColor;padding-inline-start:1rem}
#lesson-content.reading-emphasis .stage strong {color:#18251b;background:#fff08a;text-decoration:underline;text-decoration-thickness:.08em}
@media print {
 .lesson-reading-controls {display:none!important}
 #lesson-content .stage[hidden] {display:block!important}
}
@media (forced-colors:active) {
 #lesson-content.reading-emphasis .stage strong {color:CanvasText;background:Canvas;text-decoration:underline}
}
"""

JS = """<script>
(function () {
  function start() {
    const root = document.getElementById('lesson-content');
    if (!root) return;
    const stages = Array.from(root.querySelectorAll('.stage'));
    if (!stages.length) return;
    const bar = document.createElement('div');
    bar.className = 'lesson-reading-controls';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', 'Reading controls');
    function button(label, handler) {
      const control = document.createElement('button');
      control.type = 'button';
      control.className = 'go';
      control.textContent = label;
      control.addEventListener('click', handler);
      bar.append(control);
      return control;
    }
    let count = 1;
    const next = button('Next explanation', () => {count = Math.min(count + 1, stages.length); paint();});
    next.classList.add('primary');
    const all = button('Show all explanations', () => {count = stages.length; paint();});
    button('Start again', () => {count = 1; paint();});
    const emphasis = button('Highlight key wording', () => {
      const active = root.classList.toggle('reading-emphasis');
      emphasis.setAttribute('aria-pressed', String(active));
    });
    emphasis.setAttribute('aria-pressed', 'false');
    const status = document.createElement('span');
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    bar.append(status);
    root.prepend(bar);
    // An outline uses only headings already present after runtime truncation.
    const outline = document.createElement('details');
    outline.className = 'lesson-reading-outline';
    const title = document.createElement('summary');
    title.textContent = 'In this lesson';
    outline.append(title);
    const list = document.createElement('ul');
    root.querySelectorAll('h2').forEach(heading => {
      const target = heading.id ? heading : heading.closest('[id]');
      if (!target) return;
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + encodeURIComponent(target.id);
      link.textContent = heading.textContent;
      link.addEventListener('click', () => {
        const index = stages.findIndex(stage => stage.contains(heading));
        if (index >= count) {count = index + 1; paint();}
      });
      item.append(link);
      list.append(item);
    });
    outline.append(list);
    root.insertBefore(outline, bar);
    // Preview a single already-rendered source excerpt beside its citation.
    // External sources and ambiguous targets keep their ordinary link.
    root.querySelectorAll('a[href^="#"]').forEach(link => {
      if (link.closest('.lesson-reading-outline')) return;
      let id;
      try {id = decodeURIComponent(link.getAttribute('href').slice(1));} catch (_) {return;}
      const target = document.getElementById(id);
      if (!target || !root.contains(target)) return;
      const excerpts = target.querySelectorAll('.callout-excerpt .callout-body');
      if (excerpts.length !== 1 || target.contains(link)) return;
      const preview = document.createElement('details');
      preview.className = 'lesson-source-preview';
      const summary = document.createElement('summary');
      summary.textContent = 'Preview source excerpt';
      const quote = document.createElement('blockquote');
      quote.textContent = excerpts[0].textContent;
      preview.append(summary, quote);
      // Place a block beside the citation paragraph, never inside its prose.
      const paragraph = link.closest('p');
      (paragraph || link).after(preview);
    });
    // Optional tips can be folded independently, like an accordion.
    // Required semantics, checks and source excerpts remain outside this rule.
    root.querySelectorAll('.callout-tip:not([data-required])').forEach(callout => {
      const label = callout.querySelector('.callout-label');
      const body = callout.querySelector('.callout-body');
      if (!label || !body) return;
      const detail = document.createElement('details');
      detail.className = 'lesson-reading-detail';
      detail.open = true;
      const summary = document.createElement('summary');
      summary.textContent = label.textContent.trim();
      detail.append(summary, body);
      label.replaceWith(detail);
    });
    function paint() {
      stages.forEach((stage, index) => {
        stage.hidden = index >= count;
        if (index === count - 1) stage.setAttribute('aria-current', 'step');
        else stage.removeAttribute('aria-current');
      });
      next.disabled = count === stages.length;
      all.disabled = count === stages.length;
      status.textContent = count + ' of ' + stages.length + ' available explanations shown';
    }
    function revealFragment(fragment) {
      let id;
      try {id = decodeURIComponent(fragment.slice(1));} catch (_) {return;}
      const target = document.getElementById(id);
      const index = stages.findIndex(stage => target &&
        (stage.contains(target) || target.contains(stage)));
      if (index >= count) {count = index + 1; paint();}
      if (index >= 0) target.scrollIntoView();
    }
    function revealTarget() {revealFragment(location.hash);}
    paint();
    revealTarget();
    root.addEventListener('click', event => {
      const link = event.target.closest('a[href^="#"]');
      if (link) revealFragment(link.getAttribute('href'));
    });
    window.addEventListener('hashchange', revealTarget);
    let foldedForPrint = [];
    window.addEventListener('beforeprint', () => {
      stages.forEach(stage => {stage.hidden = false;});
      foldedForPrint = Array.from(root.querySelectorAll('.lesson-reading-detail:not([open])'));
      foldedForPrint.forEach(detail => {detail.open = true;});
    });
    window.addEventListener('afterprint', () => {
      foldedForPrint.forEach(detail => {detail.open = false;});
      paint();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
</script>"""
