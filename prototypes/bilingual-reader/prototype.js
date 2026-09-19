// Disposable fixture and browser state only. No production imports or migration.
export const glossary = Object.freeze({
  "学习": Object.freeze({lemma:"学习", pinyin:"xuéxí", meaning:"to study", source:"synthetic-glossary-v2:1"}),
  "中文": Object.freeze({lemma:"中文", pinyin:"Zhōngwén", meaning:"Chinese language", source:"synthetic-glossary-v2:2"}),
  "读": Object.freeze({lemma:"读", pinyin:"dú", meaning:"to read", source:"synthetic-glossary-v2:3"})
});
export const passage = "我学习中文。今天我读一本书，也学习中文。\nStudy note: 中文 + English, 2026! 未匹配的字、🙂。";
export const occurrenceId = "synthetic-reading-2";
export const provenance = Object.freeze({source:"agent-authored synthetic fixture v2", rights:"created for this disposable prototype", tokenizer:"literal-longest-match-v2", offsets:"UTF-16 code units", lemmas:"explicit glossary mapping, no inference"});
export function tokenize(text, entries = glossary) {
  const keys = Object.keys(entries).filter(Boolean).sort((a,b) => b.length - a.length || a.localeCompare(b));
  const result = [];
  let offset = 0;
  while (offset < text.length) {
    const match = keys.find(key => text.startsWith(key, offset));
    const value = match || String.fromCodePoint(text.codePointAt(offset));
    const previous = result.at(-1);
    if (!match && previous && !previous.lemma) { previous.text += value; previous.end += value.length; }
    else result.push({text:value, lemma:match ? entries[match].lemma : null, start:offset, end:offset + value.length, source:match ? entries[match].source : "unmatched source text", lemmaSource:match ? "explicit glossary mapping" : null});
    offset += value.length;
  }
  return result;
}
export const storageKey = "itembank-prototype:bilingual-reader:v2:synthetic-reading-2";
export const statuses = ["new", "learning", "known"];
export const fixture = JSON.stringify({occurrenceId, passage, glossary, provenance});
const lemmas = [...new Set(Object.values(glossary).map(entry => entry.lemma))];
export function emptyState() { return Object.fromEntries(lemmas.map(lemma => [lemma, "new"])); }
export function pack(states, revision) { return {format:"itembank-disposable-bilingual-reader", version:2, fixture, occurrenceId, revision, states}; }
export function validate(value) {
  const fields = ["format", "version", "fixture", "occurrenceId", "revision", "states"];
  if (!value || typeof value !== "object" || Object.keys(value).sort().join() !== fields.sort().join() || value.format !== "itembank-disposable-bilingual-reader" || value.version !== 2 || value.fixture !== fixture || value.occurrenceId !== occurrenceId || typeof value.revision !== "string" || !value.revision || value.revision.length > 100) throw Error("Unsupported or changed prototype fixture. Nothing restored.");
  if (!value.states || typeof value.states !== "object" || Object.keys(value.states).sort().join() !== [...lemmas].sort().join() || lemmas.some(lemma => !statuses.includes(value.states[lemma]))) throw Error("Invalid word states. Nothing restored.");
  return value;
}
export function decode(raw) {
  if (typeof raw !== "string" || raw.length > 20000) throw Error("Expected prototype JSON under 20,000 characters.");
  return validate(JSON.parse(raw));
}
// Compare before writing detects stale tabs but localStorage has no atomic CAS.
// The UI serializes cooperating tabs with Web Locks when available.
export function createStore(storage, revision = () => globalThis.crypto.randomUUID()) {
  let base;
  let states = emptyState();
  return {
    get states() { return {...states}; },
    load() {
      base = undefined;
      const raw = storage.getItem(storageKey);
      const next = raw === null ? emptyState() : decode(raw).states;
      base = raw; states = {...next}; return this.states;
    },
    save(next) {
      const value = validate(pack(next, revision()));
      if (base === undefined) throw Error("Storage unavailable or invalid. Reload saved state first.");
      if (storage.getItem(storageKey) !== base) throw Error("Conflict: another tab changed state. Reload saved state before editing.");
      const raw = JSON.stringify(value);
      storage.setItem(storageKey, raw);
      base = raw; states = {...value.states}; return this.states;
    },
    export() { return JSON.stringify(pack(states, "portable-copy"), null, 2); }
  };
}

if (typeof document !== "undefined") {
  const byId = id => document.getElementById(id);
  const notice = byId("notice");
  const passageNode = byId("passage");
  const popover = byId("word-popover");
  const controls = byId("lookup-controls");
  let anchor = null;
  let closeTimer;
  let returningFocus = false;
  function positionLookup() {
    if (!anchor || popover.hidden) return;
    const rect = anchor.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top > innerHeight) { closeLookup(); return; }
    const width = popover.offsetWidth;
    const height = popover.offsetHeight;
    const above = rect.top - height - 9;
    const top = above >= 8 ? above : rect.bottom + 9;
    const left = Math.max(8, Math.min(innerWidth - width - 8, rect.left + rect.width / 2 - width / 2));
    popover.dataset.side = above >= 8 ? "above" : "below";
    popover.style.setProperty("--tip", `${Math.max(10, Math.min(width - 10, rect.left + rect.width / 2 - left))}px`);
    popover.style.left = `${left}px`;
    popover.style.top = `${Math.max(8, Math.min(innerHeight - height - 8, top))}px`;
  }
  function closeLookup(restoreFocus = false) {
    clearTimeout(closeTimer);
    if (restoreFocus && anchor) {
      returningFocus = true;
      anchor.focus();
      returningFocus = false;
    }
    anchor?.setAttribute("aria-expanded", "false");
    anchor?.removeAttribute("aria-describedby");
    popover.hidden = true;
    controls.hidden = true;
    anchor = null;
  }
  function scheduleClose() {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      if (controls.hidden && !popover.matches(":hover") && !anchor?.matches(":hover") && document.activeElement !== anchor) closeLookup();
    }, 180);
  }
  popover.addEventListener("pointerenter", () => clearTimeout(closeTimer));
  popover.addEventListener("pointerleave", scheduleClose);
  popover.addEventListener("focusout", scheduleClose);
  byId("close-lookup").addEventListener("click", () => closeLookup(true));
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !popover.hidden) { event.preventDefault(); closeLookup(controls.contains(document.activeElement)); }
  });
  document.addEventListener("pointerdown", event => {
    if (!popover.contains(event.target) && !controls.contains(event.target) && !event.target.closest(".word")) closeLookup();
  });
  document.addEventListener("focusin", event => {
    if (!returningFocus && anchor && event.target !== anchor && !controls.contains(event.target) && !event.target.closest(".word")) closeLookup();
  });
  window.addEventListener("resize", positionLookup);
  window.addEventListener("scroll", positionLookup, true);
  new ResizeObserver(positionLookup).observe(popover);
  let selected = null;
  let blocked = false;
  let saving = false;
  const storage = {getItem:key => localStorage.getItem(key), setItem:(key,value) => localStorage.setItem(key,value)};
  const store = createStore(storage);
  const say = text => { notice.textContent = text; };
  function refresh() {
    for (const button of passageNode.querySelectorAll("button")) {
      const status = store.states[button.dataset.lemma];
      button.dataset.status = status;
      button.setAttribute("aria-label", `${button.textContent}, ${status}`);
    }
    byId("statuses").disabled = blocked || saving || !selected;
    for (const input of document.querySelectorAll("input[name=status]")) input.checked = !!selected && store.states[selected] === input.value;
    byId("restore").disabled = blocked || saving;
    byId("reset").disabled = blocked || saving;
    byId("export").disabled = blocked || saving;
    byId("reload").disabled = saving;
  }
  function reload() {
    try { store.load(); blocked = false; say("Saved prototype state loaded."); }
    catch (error) { blocked = true; say(`${error.message} Stored bytes were preserved. Reading and glossary still work.`); }
    refresh();
  }
  async function save(states, message) {
    if (saving) return;
    const focused = document.activeElement;
    saving = true;
    refresh();
    try {
      if (blocked) throw Error("Reload saved state before editing.");
      const write = () => store.save(states);
      if (navigator.locks) await navigator.locks.request(storageKey, write);
      else write();
      say(message);
    } catch (error) { blocked = true; say(error.message); }
    saving = false;
    refresh();
    if (!blocked && document.activeElement === document.body && focused?.isConnected && !focused.disabled) focused.focus();
  }
  for (const token of tokenize(passage)) {
    if (!token.lemma) { passageNode.append(document.createTextNode(token.text)); continue; }
    const button = document.createElement("button");
    button.type = "button"; button.className = "word";
    button.textContent = token.text; button.dataset.lemma = token.lemma;
    button.setAttribute("aria-controls", "word-popover");
    button.setAttribute("aria-expanded", "false");
    const choose = (expanded = false) => {
      if (returningFocus) return;
      clearTimeout(closeTimer);
      anchor?.setAttribute("aria-expanded", "false");
      anchor?.removeAttribute("aria-describedby");
      anchor = button;
      button.setAttribute("aria-expanded", "true");
      button.setAttribute("aria-describedby", "lookup");
      selected = token.lemma;
      const entry = glossary[token.text];
      byId("lookup").textContent = `${entry.pinyin} · ${entry.meaning}`;
      byId("lookup-title").textContent = `${token.text} · ${entry.meaning}`;
      controls.hidden = !expanded;
      byId("token-source").textContent = `Token range [${token.start}, ${token.end}) in UTF-16 code units. Gloss: ${entry.source}. Lemma: ${token.lemmaSource}. Match: ${provenance.tokenizer}.`;
      refresh();
      popover.hidden = false;
      positionLookup();
    };
    button.addEventListener("focus", () => choose()); button.addEventListener("click", () => choose(true));
    button.addEventListener("pointerenter", event => { if (event.pointerType === "mouse" && controls.hidden) choose(); });
    button.addEventListener("pointerleave", scheduleClose);
    button.addEventListener("blur", scheduleClose);
    button.addEventListener("keydown", event => {
      if (event.key === "ArrowDown") { event.preventDefault(); choose(true); byId("close-lookup").focus(); }
    });
    passageNode.append(button);
  }
  document.querySelectorAll("input[name=status]").forEach(input => input.addEventListener("change", () => {
    if (selected) void save({...store.states, [selected]:input.value}, "Saved for every matching lemma in this reading only.");
  }));
  byId("reload").addEventListener("click", reload);
  byId("export").addEventListener("click", () => {
    byId("transfer").value = store.export();
    say("Copy this JSON to a local file. It restores only this exact prototype fixture.");
  });
  byId("restore").addEventListener("click", () => {
    if (!byId("replace").checked) { say("Check the replacement box before restoring."); return; }
    try {
      const value = decode(byId("transfer").value);
      byId("replace").checked = false;
      void save(value.states, "Restored prototype word states. No production data was imported.");
    } catch (error) { say(error.message); }
  });
  byId("reset").addEventListener("click", () => {
    if (!byId("replace").checked) { say("Check the replacement box before resetting."); return; }
    byId("replace").checked = false;
    void save(emptyState(), "Reset all words in this prototype reading to New.");
  });
  window.addEventListener("storage", event => {
    if (event.key === storageKey || event.key === null) {
      blocked = true;
      say("Conflict: browser storage changed. Reload saved state before editing. Your transfer text is retained.");
      refresh();
    }
  });
  byId("interactive").hidden = false;
  byId("lock-mode").textContent = navigator.locks ? "Cooperating tabs use a browser lock and stale-state checks." : "No browser locks available. Use one tab only. Simultaneous saves can overwrite each other.";
  reload();
}
