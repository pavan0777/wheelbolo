/* ==========================================================================
   Wheel Bolo — shared wheel engine (vanilla ES6+, no dependencies)
   Responsibilities: canvas wheel render + spin physics, fair winner pick,
   elimination mode, in-memory history, share-as-image, URL state, confetti,
   theme + language wiring. One file, included by every page.
   ========================================================================== */
(function () {
  'use strict';

  /* ----------------------------------------------------------------------
     Small helpers
     ---------------------------------------------------------------------- */
  const TAU = Math.PI * 2;
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Festive segment palette (cycled). Chosen for contrast against each other.
  const SEGMENT_COLORS = [
    '#FF8A1E', // marigold
    '#E5247B', // magenta
    '#0FA3A3', // teal
    '#FFC53D', // saffron
    '#7C4DFF', // indigo-violet
    '#2BB673', // leaf green
    '#FF5A5F', // coral
    '#3D8BFD'  // blue
  ];
  const CONFETTI_COLORS = ['#FF8A1E', '#E5247B', '#0FA3A3', '#FFC53D', '#7C4DFF', '#2BB673'];

  function cryptoRandom() {
    if (window.crypto && window.crypto.getRandomValues) {
      const u = new Uint32Array(1);
      window.crypto.getRandomValues(u);
      return u[0] / 4294967296;
    }
    return Math.random();
  }
  function randInt(n) { return Math.floor(cryptoRandom() * n); }

  function parseEntries(raw) {
    if (!raw) return [];
    return raw
      .split(/\r?\n|,/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  }

  function relLuminance(hex) {
    const m = hex.replace('#', '');
    const r = parseInt(m.substring(0, 2), 16) / 255;
    const g = parseInt(m.substring(2, 4), 16) / 255;
    const b = parseInt(m.substring(4, 6), 16) / 255;
    const lin = (c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  }
  function labelColor(bgHex) { return relLuminance(bgHex) > 0.45 ? '#2B0A3D' : '#FFF7EC'; }
  function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }

  function getCssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function toast(msg) {
    let el = document.querySelector('.toast');
    if (!el) {
      el = document.createElement('div');
      el.className = 'toast';
      el.setAttribute('role', 'status');
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('show'), 2600);
  }

  const t = (key, vars) => (window.I18n ? window.I18n.t(key, vars) : key);

  /* ----------------------------------------------------------------------
     Theme + language (run on every page, even without a wheel)
     ---------------------------------------------------------------------- */
  function currentTheme() {
    const explicit = document.documentElement.getAttribute('data-theme');
    if (explicit) return explicit;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setupTheme(onChange) {
    const params = new URLSearchParams(location.search);
    const urlTheme = params.get('theme');
    if (urlTheme === 'dark' || urlTheme === 'light') {
      document.documentElement.setAttribute('data-theme', urlTheme);
    }
    const btn = document.querySelector('[data-theme-toggle]');

    function syncBtn() {
      if (!btn) return;
      const dark = currentTheme() === 'dark';
      // emoji is decorative; the aria-label carries the accessible name (no
      // visible text → no label/name mismatch).
      btn.innerHTML = '<span aria-hidden="true">' + (dark ? '☀️' : '🌙') + '</span>';
      btn.setAttribute('aria-label', t(dark ? 'theme.toLight' : 'theme.toDark'));
      btn.setAttribute('aria-pressed', String(dark));
    }
    syncBtn();

    if (btn) {
      btn.addEventListener('click', () => {
        const next = currentTheme() === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        const p = new URLSearchParams(location.search);
        p.set('theme', next);
        history.replaceState(null, '', location.pathname + '?' + p.toString() + location.hash);
        syncBtn();
        if (onChange) onChange();
      });
    }
    document.addEventListener('i18n:change', syncBtn);
    return { syncBtn };
  }

  /* ---- generic accessible modal open/close (shared by lang picker + winner) */
  let _openModal = null;
  let _lastFocus = null;
  function openModalEl(el, focusSel) {
    _lastFocus = document.activeElement;
    el.classList.add('open');
    el.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    _openModal = el;
    const f = focusSel && el.querySelector(focusSel);
    (f || el.querySelector('button, input, [tabindex]') || el).focus();
  }
  function closeModalEl(el) {
    el.classList.remove('open');
    el.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (_openModal === el) _openModal = null;
    if (_lastFocus && _lastFocus.focus) _lastFocus.focus();
  }
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && _openModal) closeModalEl(_openModal); });

  function setLanguage(code) {
    window.I18n.set(code);
    const p = new URLSearchParams(location.search);
    if (code === 'en') p.delete('lang'); else p.set('lang', code);
    history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p.toString() : '') + location.hash);
  }

  function buildLangModal() {
    const I = window.I18n;
    const overlay = document.createElement('div');
    overlay.className = 'wb-modal lang-modal';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-hidden', 'true');

    const dialog = document.createElement('div');
    dialog.className = 'wb-dialog lang-dialog';
    overlay.appendChild(dialog);

    const head = document.createElement('div');
    head.className = 'wb-modal-head';
    const title = document.createElement('h2');
    title.className = 'wb-modal-title';
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'wb-close';
    closeBtn.innerHTML = '<span aria-hidden="true">✕</span>';
    closeBtn.addEventListener('click', () => closeModalEl(overlay));
    head.appendChild(title);
    head.appendChild(closeBtn);
    dialog.appendChild(head);

    const sugTitle = document.createElement('h3');
    sugTitle.className = 'wb-section-title';
    const sugGrid = document.createElement('div');
    sugGrid.className = 'lang-grid';
    const allTitle = document.createElement('h3');
    allTitle.className = 'wb-section-title';
    const search = document.createElement('input');
    search.type = 'search';
    search.className = 'lang-search';
    const allGrid = document.createElement('div');
    allGrid.className = 'lang-grid all-list';
    dialog.appendChild(sugTitle);
    dialog.appendChild(sugGrid);
    dialog.appendChild(allTitle);
    dialog.appendChild(search);
    dialog.appendChild(allGrid);

    function option(L) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'lang-option';
      b.dataset.code = L.code;
      b.dataset.search = (L.native + ' ' + L.en).toLowerCase();
      b.setAttribute('lang', L.code);
      b.innerHTML = '<span class="lo-native">' + L.native + '</span><span class="lo-en">' + L.en + '</span>';
      b.addEventListener('click', () => {
        setLanguage(L.code);
        markActive();
        closeModalEl(overlay);
      });
      return b;
    }
    I.LANGS.filter((l) => l.s).forEach((l) => sugGrid.appendChild(option(l)));
    I.LANGS.slice().sort((a, b) => a.en.localeCompare(b.en)).forEach((l) => allGrid.appendChild(option(l)));

    function markActive() {
      overlay.querySelectorAll('.lang-option').forEach((o) => {
        const on = o.dataset.code === I.lang;
        o.classList.toggle('active', on);
        if (on) o.setAttribute('aria-current', 'true'); else o.removeAttribute('aria-current');
      });
    }
    search.addEventListener('input', () => {
      const q = search.value.trim().toLowerCase();
      allGrid.querySelectorAll('.lang-option').forEach((o) => {
        o.hidden = q && o.dataset.search.indexOf(q) === -1;
      });
    });

    function applyText() {
      overlay.setAttribute('aria-label', I.t('lang.modalTitle'));
      title.textContent = I.t('lang.modalTitle');
      closeBtn.setAttribute('aria-label', I.t('lang.close'));
      sugTitle.textContent = I.t('lang.suggested');
      allTitle.textContent = I.t('lang.all');
      search.setAttribute('placeholder', I.t('lang.search'));
      search.setAttribute('aria-label', I.t('lang.search'));
    }
    applyText();
    document.addEventListener('i18n:change', () => { applyText(); markActive(); });
    overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModalEl(overlay); });
    document.body.appendChild(overlay);
    overlay._markActive = markActive;
    return overlay;
  }

  function setupLanguage() {
    if (!window.I18n) return;
    const params = new URLSearchParams(location.search);
    const urlLang = params.get('lang');
    window.I18n.set(window.I18n.has(urlLang) ? urlLang : 'en');

    const btn = document.querySelector('[data-lang-toggle]');
    if (!btn) return;
    const modal = buildLangModal();

    function syncBtn() {
      const L = window.I18n.getLang(window.I18n.lang);
      btn.innerHTML = '<span aria-hidden="true">🌐</span> <span class="lang-name">' + (L ? L.native : 'Language') + '</span>';
      btn.setAttribute('aria-label', window.I18n.t('lang.label'));
      btn.setAttribute('aria-haspopup', 'dialog');
    }
    syncBtn();
    document.addEventListener('i18n:change', syncBtn);
    btn.addEventListener('click', () => { modal._markActive(); openModalEl(modal, '.lang-search'); });
  }

  /* ----------------------------------------------------------------------
     The wheel app
     ---------------------------------------------------------------------- */
  function initWheel() {
    const canvas = document.getElementById('wheel-canvas');
    if (!canvas) return null;

    const cfg = window.SPIN_CONFIG || {};
    const ctx = canvas.getContext('2d');
    const stage = canvas.closest('.wheel-stage');
    const confettiCanvas = document.getElementById('confetti-canvas');

    const els = {
      input: document.getElementById('entries-input'),
      meta: document.getElementById('entries-meta'),
      spinBtns: Array.from(document.querySelectorAll('[data-spin]')),
      hubBtn: document.querySelector('.wheel-hub-btn'),
      modeRadios: Array.from(document.querySelectorAll('input[name="mode"]')),
      modeHint: document.getElementById('mode-hint'),
      banner: document.getElementById('winner-banner'),
      history: document.getElementById('history-list'),
      historyEmpty: document.getElementById('history-empty'),
      clearHistory: document.querySelector('[data-clear-history]'),
      shuffleBtn: document.querySelector('[data-shuffle]'),
      resetBtn: document.querySelector('[data-reset]'),
      shareBtn: document.querySelector('[data-share]'),
      copyBtn: document.querySelector('[data-copy-link]')
    };

    const params = new URLSearchParams(location.search);

    const state = {
      entries: [],
      original: [],
      mode: 'random',
      rotation: cryptoRandom() * TAU,
      spinning: false,
      history: [],
      lastWinner: null,
      size: 460,
      dpr: Math.max(1, Math.min(window.devicePixelRatio || 1, 2))
    };

    // ---- initial entries: URL wins, else config, else placeholder names ----
    const urlNames = params.get('names');
    if (urlNames) {
      state.entries = parseEntries(decodeURIComponent(urlNames));
    } else if (Array.isArray(cfg.entries) && cfg.entries.length) {
      state.entries = cfg.entries.slice();
    } else {
      state.entries = ['Aarav', 'Diya', 'Kabir', 'Myra', 'Vihaan', 'Anaya'];
    }
    state.original = state.entries.slice();

    // ---- initial mode ----
    const urlMode = params.get('mode');
    state.mode = (urlMode === 'elim' || cfg.mode === 'elim') ? 'elim' : 'random';

    /* ---------- rendering ---------- */
    function resize() {
      const rect = stage.getBoundingClientRect();
      const size = Math.max(200, Math.round(rect.width));
      state.size = size;
      state.dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 2));
      canvas.width = Math.round(size * state.dpr);
      canvas.height = Math.round(size * state.dpr);
      canvas.style.width = size + 'px';
      canvas.style.height = size + 'px';
      draw();
    }

    function draw(highlightIndex) {
      const size = state.size;
      const dpr = state.dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, size, size);

      const cx = size / 2;
      const cy = size / 2;
      const radius = size / 2 - 4;
      const n = state.entries.length;

      // rim
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius + 3, 0, TAU);
      ctx.fillStyle = currentTheme() === 'dark' ? '#3A2350' : '#FFFFFF';
      ctx.fill();
      ctx.restore();

      if (n === 0) {
        ctx.fillStyle = getCssVar('--surface-2') || '#eee';
        ctx.beginPath(); ctx.arc(cx, cy, radius, 0, TAU); ctx.fill();
        ctx.fillStyle = getCssVar('--text-soft') || '#888';
        ctx.font = '600 ' + Math.round(size * 0.045) + "px 'Mukta', sans-serif";
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(t('winner.none'), cx, cy);
        return;
      }

      const seg = TAU / n;
      for (let i = 0; i < n; i++) {
        const start = i * seg + state.rotation;
        const end = start + seg;
        let color = SEGMENT_COLORS[i % SEGMENT_COLORS.length];
        // avoid identical color where the cycle wraps onto itself
        if (n > 1 && i === n - 1 && color === SEGMENT_COLORS[0]) {
          color = SEGMENT_COLORS[(i + 2) % SEGMENT_COLORS.length];
        }
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, radius, start, end);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();

        if (highlightIndex === i) {
          ctx.save();
          ctx.fillStyle = 'rgba(255, 197, 61, 0.55)';
          ctx.fill();
          ctx.lineWidth = 4;
          ctx.strokeStyle = '#FFC53D';
          ctx.stroke();
          ctx.restore();
        } else {
          ctx.lineWidth = 1;
          ctx.strokeStyle = 'rgba(0,0,0,0.08)';
          ctx.stroke();
        }

        // label
        const label = state.entries[i];
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(start + seg / 2);
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = labelColor(color);
        const fontSize = Math.max(11, Math.min(size * 0.045, size / n * 0.7, 24));
        ctx.font = '600 ' + fontSize + "px 'Mukta', 'Segoe UI', sans-serif";
        let text = label;
        const maxLabel = radius - size * 0.13;
        while (ctx.measureText(text).width > maxLabel && text.length > 1) {
          text = text.slice(0, -1);
        }
        if (text !== label && text.length > 1) text = text.slice(0, -1) + '…';
        ctx.fillText(text, radius - size * 0.05, 0);
        ctx.restore();
      }

      // subtle center ring under the hub
      ctx.beginPath();
      ctx.arc(cx, cy, size * 0.11, 0, TAU);
      ctx.fillStyle = currentTheme() === 'dark' ? '#241334' : '#FFFFFF';
      ctx.fill();
    }

    /* ---------- winner detection from rotation ---------- */
    function winnerFromRotation() {
      const n = state.entries.length;
      if (n === 0) return -1;
      const seg = TAU / n;
      // pointer sits at angle 0 (3 o'clock). Segment i covers [i*seg+rot, ...].
      let a = ((-state.rotation) % TAU + TAU) % TAU;
      return Math.floor(a / seg) % n;
    }

    /* ---------- spin ---------- */
    function spin() {
      if (state.spinning) return;
      const n = state.entries.length;
      if (n < 2) { announce(t('winner.needMore')); toast(t('winner.needMore')); return; }

      state.spinning = true;
      setSpinUI(true);
      els.banner.classList.remove('has-winner');

      const seg = TAU / n;
      const winnerIndex = randInt(n);
      // land the winner's centre under the pointer, with small in-segment jitter
      const jitter = (cryptoRandom() - 0.5) * seg * 0.7;
      const targetAligned = -((winnerIndex + 0.5) * seg) + jitter; // rotation s.t. winner at pointer
      const turns = 5 + randInt(3); // 5–7 full rotations
      const startRot = state.rotation;
      // normalise so we always travel forward by `turns` plus the delta to target
      let delta = (targetAligned - startRot) % TAU;
      if (delta < 0) delta += TAU;
      const totalDelta = turns * TAU + delta;

      const duration = prefersReduced ? 600 : 4200 + randInt(700);
      const startTime = performance.now();

      function frame(now) {
        const elapsed = now - startTime;
        const p = Math.min(1, elapsed / duration);
        const eased = easeOutQuart(p);
        state.rotation = startRot + totalDelta * eased;
        draw();
        if (p < 1) {
          requestAnimationFrame(frame);
        } else {
          state.rotation = (startRot + totalDelta) % TAU;
          finishSpin();
        }
      }
      requestAnimationFrame(frame);
    }

    function finishSpin() {
      const idx = winnerFromRotation();
      const name = state.entries[idx];
      draw(idx);

      if (state.mode === 'elim') {
        // Elimination: the landed entry is OUT (no popup) — show a banner,
        // log it as "eliminated", remove it, and crown the last one standing.
        showResultBanner(name, 'eliminated');
        addHistory(name, 'eliminated');
        setTimeout(() => {
          state.entries.splice(idx, 1);
          syncInputFromEntries();
          updateUrl();
          updateMeta();
          draw();
          if (state.entries.length === 1) {
            const last = state.entries[0];
            state.lastWinner = last;
            showResultBanner(last, 'winner', 'elim.last');
            addHistory(last, 'winner');
            burstConfetti();
          }
          state.spinning = false;
          setSpinUI(false);
        }, 900);
      } else {
        // Random pick: winner stays — celebrate with confetti + a popup.
        state.lastWinner = name;
        showResultBanner(name, 'winner');
        addHistory(name, 'winner');
        burstConfetti();
        showWinnerPopup(name);
        state.spinning = false;
        setSpinUI(false);
      }
    }

    function setSpinUI(spinning) {
      const n = state.entries.length;
      const disabled = spinning || n < 2;
      els.spinBtns.forEach((b) => {
        b.disabled = disabled;
        // Only relabel buttons that opt in via [data-spin-label]; the compact
        // hub button keeps its own short "SPIN" text.
        const labelSpan = b.querySelector('[data-spin-label]');
        if (labelSpan) labelSpan.textContent = spinning ? t('app.spinning') : t('app.spin');
      });
    }

    // kind = 'winner' | 'eliminated'. msgKey overrides the default phrasing.
    function showResultBanner(name, kind, msgKey) {
      const key = msgKey || (kind === 'eliminated' ? 'elim.eliminated' : 'winner.wins');
      const icon = kind === 'eliminated' ? '❌' : '🏆';
      els.banner.innerHTML =
        '<span aria-hidden="true">' + icon + '</span> ' +
        t(key, { name: '|N|' }).split('|N|').map(escapeHtml).join('<span class="winner-name">' + escapeHtml(name) + '</span>');
      els.banner.classList.remove('is-winner', 'is-elim');
      els.banner.classList.add('has-winner', kind === 'eliminated' ? 'is-elim' : 'is-winner');
    }

    /* ---------- history ---------- */
    function addHistory(name, kind) {
      state.history.unshift({ name: name, kind: kind || 'winner' });
      renderHistory();
    }
    function renderHistory() {
      if (!els.history) return;
      els.history.innerHTML = '';
      if (state.history.length === 0) {
        if (els.historyEmpty) els.historyEmpty.hidden = false;
        return;
      }
      if (els.historyEmpty) els.historyEmpty.hidden = true;
      const total = state.history.length;
      state.history.forEach((item, i) => {
        const li = document.createElement('li');
        li.className = item.kind === 'eliminated' ? 'h-elim' : 'h-win';
        const idx = document.createElement('span');
        idx.className = 'h-index';
        idx.textContent = '#' + (total - i);
        const nm = document.createElement('span');
        nm.className = 'h-name';
        nm.textContent = item.name;
        const tag = document.createElement('span');
        tag.className = 'h-tag';
        tag.textContent = t(item.kind === 'eliminated' ? 'history.elimTag' : 'history.winnerTag');
        li.appendChild(idx);
        li.appendChild(nm);
        li.appendChild(tag);
        els.history.appendChild(li);
      });
    }

    /* ---------- entries <-> input sync ---------- */
    function syncInputFromEntries() {
      if (els.input) els.input.value = state.entries.join('\n');
    }
    function updateMeta() {
      if (els.meta) els.meta.textContent = t('app.entriesHint', { count: state.entries.length });
    }
    function onInputChange() {
      state.entries = parseEntries(els.input.value);
      state.original = state.entries.slice();
      updateUrl();
      updateMeta();
      setSpinUI(false);
      draw();
    }

    /* ---------- URL state ---------- */
    function updateUrl() {
      const p = new URLSearchParams(location.search);
      if (state.entries.length) {
        p.set('names', state.entries.join(','));
      } else {
        p.delete('names');
      }
      if (state.mode === 'elim') p.set('mode', 'elim'); else p.delete('mode');
      const qs = p.toString();
      history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
    }

    /* ---------- confetti ---------- */
    let confettiParticles = [];
    let confettiRAF = null;
    function setupConfettiCanvas() {
      if (!confettiCanvas) return;
      const dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 2));
      confettiCanvas.width = Math.round(window.innerWidth * dpr);
      confettiCanvas.height = Math.round(window.innerHeight * dpr);
      const cctx = confettiCanvas.getContext('2d');
      cctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function burstConfetti() {
      if (!confettiCanvas || prefersReduced) return;
      setupConfettiCanvas();
      // origin = pointer position (right edge of wheel, vertical centre)
      const rect = stage.getBoundingClientRect();
      const ox = rect.right - 10;
      const oy = rect.top + rect.height / 2;
      const count = 120;
      for (let i = 0; i < count; i++) {
        const angle = Math.PI + (cryptoRandom() - 0.5) * Math.PI * 1.1; // fan leftwards/up
        const speed = 6 + cryptoRandom() * 9;
        confettiParticles.push({
          x: ox, y: oy,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 3,
          size: 5 + cryptoRandom() * 7,
          color: CONFETTI_COLORS[randInt(CONFETTI_COLORS.length)],
          rot: cryptoRandom() * TAU,
          vr: (cryptoRandom() - 0.5) * 0.3,
          life: 1
        });
      }
      if (!confettiRAF) confettiRAF = requestAnimationFrame(confettiFrame);
    }
    function confettiFrame() {
      const cctx = confettiCanvas.getContext('2d');
      cctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      const gravity = 0.22;
      confettiParticles.forEach((pt) => {
        pt.vy += gravity;
        pt.x += pt.vx;
        pt.y += pt.vy;
        pt.vx *= 0.99;
        pt.rot += pt.vr;
        pt.life -= 0.008;
        cctx.save();
        cctx.globalAlpha = Math.max(0, pt.life);
        cctx.translate(pt.x, pt.y);
        cctx.rotate(pt.rot);
        cctx.fillStyle = pt.color;
        cctx.fillRect(-pt.size / 2, -pt.size / 2, pt.size, pt.size * 0.6);
        cctx.restore();
      });
      confettiParticles = confettiParticles.filter((p) => p.life > 0 && p.y < window.innerHeight + 40);
      if (confettiParticles.length) {
        confettiRAF = requestAnimationFrame(confettiFrame);
      } else {
        cctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        confettiRAF = null;
      }
    }

    /* ---------- share as image ---------- */
    function buildShareCard(winnerName) {
      const S = 1080;
      const c = document.createElement('canvas');
      c.width = S; c.height = S;
      const g = c.getContext('2d');
      const dark = currentTheme() === 'dark';

      // background
      const grad = g.createLinearGradient(0, 0, S, S);
      if (dark) { grad.addColorStop(0, '#1D0F29'); grad.addColorStop(1, '#160A1F'); }
      else { grad.addColorStop(0, '#FFF7EC'); grad.addColorStop(1, '#FFE7C2'); }
      g.fillStyle = grad; g.fillRect(0, 0, S, S);

      // glow
      const glow = g.createRadialGradient(S / 2, S * 0.46, 40, S / 2, S * 0.46, S * 0.5);
      glow.addColorStop(0, 'rgba(255,138,30,0.35)');
      glow.addColorStop(1, 'rgba(255,138,30,0)');
      g.fillStyle = glow; g.fillRect(0, 0, S, S);

      // wheel with the real entries, rotated so the winner sits at the top
      const cx = S / 2, cy = S * 0.4, r = S * 0.215;
      const entries = (state.original && state.original.length ? state.original : [winnerName]).slice();
      const n = entries.length;
      const seg = TAU / n;
      let winIdx = entries.indexOf(winnerName);
      if (winIdx < 0) winIdx = 0;
      // rotate so the winning segment's centre points straight up (-90°)
      const rot = -Math.PI / 2 - (winIdx + 0.5) * seg;

      for (let i = 0; i < n; i++) {
        const a0 = rot + i * seg, a1 = a0 + seg;
        let color = SEGMENT_COLORS[i % SEGMENT_COLORS.length];
        if (n > 1 && i === n - 1 && color === SEGMENT_COLORS[0]) color = SEGMENT_COLORS[(i + 2) % SEGMENT_COLORS.length];
        g.beginPath(); g.moveTo(cx, cy); g.arc(cx, cy, r, a0, a1); g.closePath();
        g.fillStyle = color; g.fill();
        if (i === winIdx) {                       // highlight the winning slice
          g.save();
          g.fillStyle = 'rgba(255,197,61,0.5)'; g.fill();
          g.lineWidth = 6; g.strokeStyle = '#FFC53D'; g.stroke();
          g.restore();
        } else {
          g.lineWidth = 2; g.strokeStyle = 'rgba(255,255,255,0.85)'; g.stroke();
        }
        // label
        const label = entries[i];
        g.save();
        g.translate(cx, cy); g.rotate(a0 + seg / 2);
        g.textAlign = 'right'; g.textBaseline = 'middle';
        g.fillStyle = labelColor(color);
        let fs = Math.max(14, Math.min(r * 0.18, (r * seg) * 0.9, 30));
        g.font = '700 ' + fs + "px 'Mukta', sans-serif";
        let text = label;
        const maxW = r - S * 0.05;
        while (g.measureText(text).width > maxW && text.length > 1) text = text.slice(0, -1);
        if (text !== label && text.length > 1) text = text.slice(0, -1) + '…';
        g.fillText(text, r - S * 0.022, 0);
        g.restore();
      }
      // hub
      g.beginPath(); g.arc(cx, cy, r * 0.2, 0, TAU);
      g.fillStyle = dark ? '#241334' : '#fff';
      g.fill(); g.lineWidth = 4; g.strokeStyle = '#FFC53D'; g.stroke();

      // pointer above the wheel, tip pointing down at the winner
      g.save();
      g.shadowColor = 'rgba(0,0,0,0.45)'; g.shadowBlur = 12; g.shadowOffsetY = 4;
      g.beginPath();
      g.moveTo(cx, cy - r + 14);                 // tip (just inside the rim)
      g.lineTo(cx - 26, cy - r - 30);
      g.lineTo(cx + 26, cy - r - 30);
      g.closePath();
      g.fillStyle = '#E5247B'; g.fill();
      g.lineWidth = 5; g.strokeStyle = '#FFFFFF'; g.stroke();
      g.restore();

      // brand
      g.fillStyle = dark ? '#F3E9DE' : '#2B0A3D';
      g.font = "800 56px 'Baloo 2', sans-serif";
      g.textAlign = 'center';
      g.fillText('🎡 Wheel Bolo', S / 2, S * 0.74);

      // "Winner!"
      g.fillStyle = '#E5247B';
      g.font = "700 46px 'Baloo 2', sans-serif";
      g.fillText('🎉 ' + (window.I18n && window.I18n.lang === 'hi' ? 'विजेता' : 'Winner') + ' 🎉', S / 2, S * 0.82);

      // name (auto-fit)
      g.fillStyle = dark ? '#FFC53D' : '#F2740A';
      let fs = 92;
      g.font = '800 ' + fs + "px 'Baloo 2', sans-serif";
      while (g.measureText(winnerName).width > S * 0.86 && fs > 30) {
        fs -= 4; g.font = '800 ' + fs + "px 'Baloo 2', sans-serif";
      }
      g.fillText(winnerName, S / 2, S * 0.9);

      // footer url
      g.fillStyle = dark ? '#B9A6C9' : '#6E5A78';
      g.font = "600 30px 'Mukta', sans-serif";
      g.fillText('wheelbolo.com', S / 2, S * 0.96);

      return c;
    }

    async function shareResult() {
      const winner = state.lastWinner || (state.history[0] && state.history[0].name);
      if (!winner) { toast(t('winner.none')); return; }
      const card = buildShareCard(winner);
      card.toBlob(async (blob) => {
        if (!blob) return;
        const file = new File([blob], 'wheelbolo-winner.png', { type: 'image/png' });
        const shareData = {
          files: [file],
          title: 'Wheel Bolo',
          text: (window.I18n && window.I18n.lang === 'hi' ? 'विजेता: ' : 'Winner: ') + winner + ' 🎉 wheelbolo.com'
        };
        if (navigator.canShare && navigator.canShare(shareData)) {
          try { await navigator.share(shareData); return; }
          catch (e) { /* user cancelled or failed → fall through to download */ }
        }
        // fallback: download
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'wheelbolo-winner.png';
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        toast(t('toast.imgSaved'));
      }, 'image/png');
    }

    async function copyLink() {
      updateUrl();
      const url = location.href;
      try {
        await navigator.clipboard.writeText(url);
        toast(t('toast.linkCopied'));
      } catch (e) {
        // fallback
        const ta = document.createElement('textarea');
        ta.value = url; document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); toast(t('toast.linkCopied')); } catch (_) {}
        ta.remove();
      }
    }

    /* ---------- mode ---------- */
    function applyMode() {
      els.modeRadios.forEach((r) => { r.checked = (r.value === state.mode); });
      if (els.modeHint) {
        els.modeHint.textContent = t(state.mode === 'elim' ? 'app.modeElimHint' : 'app.modeRandomHint');
      }
    }
    function onModeChange(value) {
      state.mode = value === 'elim' ? 'elim' : 'random';
      // entering a fresh mode resets eliminated entries back to the full list
      if (state.entries.length !== state.original.length) {
        state.entries = state.original.slice();
        syncInputFromEntries();
        draw();
      }
      applyMode();
      updateUrl();
      setSpinUI(false);
    }

    /* ---------- misc actions ---------- */
    function shuffle() {
      if (state.spinning) return;
      const a = state.entries;
      for (let i = a.length - 1; i > 0; i--) {
        const j = randInt(i + 1);
        [a[i], a[j]] = [a[j], a[i]];
      }
      syncInputFromEntries();
      updateUrl();
      draw();
    }
    function reset() {
      if (state.spinning) return;
      state.entries = state.original.slice();
      state.history = [];
      state.lastWinner = null;
      els.banner.innerHTML = '';
      els.banner.classList.remove('has-winner', 'is-winner', 'is-elim');
      syncInputFromEntries();
      renderHistory();
      updateUrl();
      updateMeta();
      setSpinUI(false);
      draw();
    }

    /* ---------- winner popup (random mode only) ---------- */
    const winnerPopup = (function () {
      const overlay = document.createElement('div');
      overlay.className = 'wb-modal winner-modal';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');
      overlay.setAttribute('aria-hidden', 'true');
      overlay.innerHTML =
        '<div class="wb-dialog winner-dialog">' +
          '<div class="winner-pop-head"><span class="wp-emoji" aria-hidden="true">🎉</span> <span class="wp-title"></span></div>' +
          '<div class="winner-pop-body"><span class="wp-name"></span></div>' +
          '<div class="winner-pop-actions">' +
            '<button type="button" class="btn btn-secondary wp-close"></button>' +
            '<button type="button" class="btn btn-primary wp-again"></button>' +
          '</div>' +
        '</div>';
      document.body.appendChild(overlay);
      const closeBtn = overlay.querySelector('.wp-close');
      const againBtn = overlay.querySelector('.wp-again');
      closeBtn.addEventListener('click', () => closeModalEl(overlay));
      againBtn.addEventListener('click', () => { closeModalEl(overlay); spin(); });
      overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModalEl(overlay); });
      return overlay;
    })();

    function showWinnerPopup(name) {
      winnerPopup.querySelector('.wp-title').textContent = t('winner.popupTitle');
      winnerPopup.querySelector('.wp-name').textContent = name;
      winnerPopup.querySelector('.wp-close').textContent = t('lang.close');
      winnerPopup.querySelector('.wp-again').textContent = t('winner.spinAgain');
      winnerPopup.setAttribute('aria-label', t('winner.popupTitle'));
      openModalEl(winnerPopup, '.wp-close');
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, (c) => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
      ));
    }

    /* ---------- wire up ---------- */
    syncInputFromEntries();
    updateMeta();
    applyMode();
    setSpinUI(false);

    // hub button also carries [data-spin], so it is already in spinBtns
    els.spinBtns.forEach((b) => b.addEventListener('click', spin));
    if (els.input) {
      els.input.addEventListener('input', onInputChange);
      els.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); spin(); }
      });
    }
    els.modeRadios.forEach((r) => r.addEventListener('change', () => onModeChange(r.value)));
    if (els.shuffleBtn) els.shuffleBtn.addEventListener('click', shuffle);
    if (els.resetBtn) els.resetBtn.addEventListener('click', reset);
    if (els.shareBtn) els.shareBtn.addEventListener('click', shareResult);
    if (els.copyBtn) els.copyBtn.addEventListener('click', copyLink);
    if (els.clearHistory) els.clearHistory.addEventListener('click', () => {
      state.history = []; renderHistory();
    });

    // re-render on theme/language change so canvas + labels + dynamic text match
    document.addEventListener('i18n:change', () => { updateMeta(); applyMode(); setSpinUI(false); draw(); });

    // responsive canvas
    if ('ResizeObserver' in window) {
      new ResizeObserver(() => resize()).observe(stage);
    } else {
      window.addEventListener('resize', resize);
    }
    window.addEventListener('resize', () => { if (confettiCanvas) setupConfettiCanvas(); });

    renderHistory();
    resize();
    updateUrl();

    return { redraw: draw };
  }

  /* ----------------------------------------------------------------------
     Footer year + boot
     ---------------------------------------------------------------------- */
  function boot() {
    const yearEl = document.querySelector('[data-year]');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    setupLanguage();
    const app = { redraw: null };
    const theme = setupTheme(() => { if (app.redraw) app.redraw(); });
    const wheel = initWheel();
    if (wheel) app.redraw = wheel.redraw;
    void theme;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
