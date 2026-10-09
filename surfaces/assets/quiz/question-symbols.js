<script id="question-symbols">
(function () {
  function esc(s) { var d=document.createElement("div"); d.textContent=String(s||""); return d.innerHTML; }
  window.renderQuestionSymbols = function (q, card) {
    var rows = (window.ItembankQuestionSymbols || {})[q && q.id] || [];
    if (!rows.length || !card) { return; }
    var section = document.createElement("section");
    section.className = "question-symbols";
    section.setAttribute("aria-label", "Symbols in this question");
    var items = rows.map(function (row) {
      if (row.definition !== undefined) {
        return '<li><span class="question-symbol-static"><span class="symbol">' +
          esc(row.symbol) + '</span><span class="question-symbol-def">' +
          esc(row.definition) + '</span></span></li>';
      }
      var panel = "question-gloss-" + String(q.id || "item") + "-" + row.slug;
      return '<li><a class="term" href="' + esc(row.href) +
        '" data-gloss-fetch="' + esc(row.fetch) + '" aria-details="' + panel +
        '"><span class="symbol">' + esc(row.symbol) +
        '</span><span class="meaning">' + esc(row.label || "meaning") + '</span></a>' +
        '<div id="' + panel + '" class="gloss" popover>' +
        '<p class="gloss-term">' + esc(row.symbol) + '</p>' +
        '<p class="gloss-def" data-gloss-state="pending">Open to load the definition.</p>' +
        '<p class="gloss-more"><a href="' + esc(row.href) +
        '">Open the definition page</a></p></div></li>';
    }).join("");
    section.innerHTML = '<h2>Symbols in this question</h2>' +
      '<p class="question-symbol-note">Shown in reading order. Open one for its course meaning, not the answer.</p>' +
      '<ul class="question-symbol-list">' + items + '</ul>';
    var stem = card.querySelector(".stem");
    if (stem) { stem.insertAdjacentElement("afterend", section); }
  };
})();
</script>