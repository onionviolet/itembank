<script>
(function () {
  document.querySelectorAll('#lesson-content .code-tools').forEach(function (tools) {
    var source = tools.parentElement.querySelector('.code-source code');
    if (!source) return;
    tools.hidden = false;
    var status = tools.querySelector('.code-status');
    var copy = tools.querySelector('.code-copy');
    var pending = false;
    tools.querySelector('.code-select').addEventListener('click', function () {
      if (!source.textContent.length) { status.textContent = 'No code to select.'; return; }
      var selection = window.getSelection();
      if (!selection) { status.textContent = 'Selection unavailable. Select the source manually.'; return; }
      var range = document.createRange();
      range.selectNodeContents(source);
      source.closest('.code-source').focus({preventScroll:true});
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = 'Code selected.';
    });
    copy.addEventListener('click', async function () {
      if (pending) return;
      var text = source.textContent;
      if (!text.length) { status.textContent = 'No code to copy.'; return; }
      if (!navigator.clipboard || !navigator.clipboard.writeText) {
        status.textContent = 'Copy unavailable. Use Select code and copy manually.'; return;
      }
      pending = true;
      copy.setAttribute('aria-disabled', 'true');
      status.textContent = 'Copying code...';
      try {
        await navigator.clipboard.writeText(text);
        status.textContent = 'Code copied.';
      } catch (_) {
        status.textContent = 'Copy denied. Use Select code and copy manually.';
      } finally {
        pending = false;
        copy.removeAttribute('aria-disabled');
      }
    });
  });
})();
</script>