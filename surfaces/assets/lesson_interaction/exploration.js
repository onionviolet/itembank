
if (!window.itembankLessonExploration) {
  window.itembankLessonExploration = function(root, kind, valid) {
    const owner = root.closest('[data-exploration-lesson]');
    const note = kind === 'reading' ? null : root.querySelector('.exploration-continuity');
    let available = false, storage, recovery = '';
    const key = 'itembank:lesson-exploration:v1';
    const ids = owner ? ['lesson','occurrence','revision'].map(name =>
      owner.getAttribute('data-exploration-' + name)) : [];
    const admitted = ids.length === 3 && ids.every(id => typeof id === 'string' &&
      id.trim() && id.length <= 256 && !/[\x00-\x1f]/.test(id));
    const section = root.closest('section[id]') || owner;
    const peers = kind === 'reading' && root === owner ? [root] :
      section ? Array.from(section.querySelectorAll('.lesson-' + kind)) : [];
    const shape = kind === 'reading' ? Array.from(root.querySelectorAll('.stage')).map(stage =>
      [stage.closest('section[id]') && stage.closest('section[id]').id || '', stage.dataset.stage]) :
      section && section.id || '';
    const slot = JSON.stringify([kind, shape, peers.indexOf(root)]);
    function notice() {
      if (note) note.textContent = available ?
        recovery + 'Exploration stays in this tab for this reading revision. Reset clears it.' :
        'Exploration is available on this page. Tab storage is unavailable; changes may not survive reopening.';
    }
    function ledger() {
      const raw = storage.getItem(key);
      if (!raw) return {version:1, entries:[]};
      if (raw.length > 32768) throw new Error('Exploration storage is too large');
      const data = JSON.parse(raw);
      if (!data || data.version !== 1 || !Array.isArray(data.entries) || data.entries.length > 16 ||
          data.entries.some(entry => !entry || !Array.isArray(entry.identity) ||
            entry.identity.length !== 2 || entry.identity.some(id => typeof id !== 'string') ||
            typeof entry.revision !== 'string' || !Array.isArray(entry.states) || entry.states.length > 32 ||
            entry.states.some(pair => !Array.isArray(pair) || pair.length !== 2 || typeof pair[0] !== 'string')))
        throw new Error('Exploration storage is invalid');
      return data;
    }
    function matching(entry) {return entry.identity[0] === ids[0] && entry.identity[1] === ids[1];}
    function put(data) {
      const raw = JSON.stringify(data);
      if (raw.length > 32768) throw new Error('Exploration storage is full');
      if (!data.entries.length) storage.removeItem(key);
      else storage.setItem(key, raw);
    }
    if (admitted && peers.indexOf(root) >= 0) {
      try {
        storage = window.sessionStorage;
        // A newly opened same-origin tab may inherit its opener's storage.
        // Give that tab an independent ledger; reloads retain its new token.
        const tabKey = key + ':tab';
        let token = storage.getItem(tabKey);
        if (window.opener && token && window.opener.itembankExplorationTab === token) {
          storage.removeItem(key); token = null;
        }
        token = token || window.crypto.randomUUID();
        storage.setItem(tabKey, token);
        window.itembankExplorationTab = token;
        let data;
        try {data = ledger();} catch (_) {
          storage.removeItem(key); data = {version:1,entries:[]};
          recovery = 'Previous exploration was unreadable and has been cleared. ';
        }
        const fresh = data.entries.filter(entry => !matching(entry) || entry.revision === ids[2]);
        if (fresh.length !== data.entries.length) {
          data.entries = fresh; put(data); recovery = 'Reading changed; previous exploration was cleared. ';
        }
        available = true;
      } catch (_) {available = false;}
    }
    notice();
    function use(action) {
      if (!available) return null;
      try {return action(ledger());}
      catch (_) {
        available = false;
        try {storage.removeItem(key);} catch (_) {}
        notice(); return null;
      }
    }
    return {
      read: () => use(data => {
        const entry = data.entries.find(item => matching(item) && item.revision === ids[2]);
        const pair = entry && entry.states.find(item => item[0] === slot);
        return pair && valid(pair[1]) ? pair[1] : null;
      }),
      write: value => {
        if (!valid(value)) return;
        use(data => {
          let entry = data.entries.find(item => matching(item) && item.revision === ids[2]);
          data.entries = data.entries.filter(item => !matching(item));
          entry = entry || {identity:ids.slice(0,2),revision:ids[2],states:[]};
          entry.states = entry.states.filter(pair => pair[0] !== slot);
          entry.states.push([slot,value]); entry.states = entry.states.slice(-32);
          data.entries.push(entry); data.entries = data.entries.slice(-16); put(data);
        });
      },
      clear: () => use(data => {
        data.entries.forEach(entry => {if (matching(entry)) entry.states = entry.states.filter(pair => pair[0] !== slot);});
        data.entries = data.entries.filter(entry => entry.states.length); put(data);
      })
    };
  };
}
