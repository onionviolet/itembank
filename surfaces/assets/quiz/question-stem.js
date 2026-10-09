
function questionStemHTML(stem){
  const raw = String(stem || "");
  const match = raw.match(new RegExp(__STEM_PATTERN__));
  if(!match || !match[1].trim() || match[1].includes("```") || match[3].includes("```"))
    return `<h1 class="stem" tabindex="-1">${esc(raw)}</h1>`;
  return `<h1 class="stem" tabindex="-1">${esc(match[1].trim())}</h1>`
    + `<figure class="question-code"><figcaption>${esc(match[2] || "text")} · Read-only code</figcaption>`
    + `<pre tabindex="0" role="region" aria-label="Read-only code"><code>${esc(match[3])}</code></pre></figure>`;
}
