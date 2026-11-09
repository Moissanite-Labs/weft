// Condensing prose: on the papers, skimming squeezes the writing.
//
// The reading score from attention.js decides; this module only acts on it.
// Read at a steady pace and the paper stays as written. Skim and the prose
// condenses, one level at a time: concise prose, then terse notes, then
// caveman. It never loosens by itself; the visitor brings the words back from
// the panel. Each level is written ahead of time (condensed.json beside the
// page), so the condensing is editing, not generation, and the full text stays
// the one that counts: printing always prints it.
//
// For review: ?condense=2 opens the page at a level, ?attn adds raw numbers.

import { attention } from "./attention.js";

const LEVELS = ["Full prose", "Concise", "Terse", "Caveman"];
const SHORT = ["Full", "Concise", "Terse", "Caveman"];
// Restlessness at which each squeeze happens. Each squeeze spends the pressure
// that caused it, so every level has to be earned by more skimming.
const RISE = [0.3, 0.5, 0.7];
const STEP_GAP = 1500; // ms: one squeeze at a time, so each one can be seen
const WPM = 230;

const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const fnv = (s) => {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, "0");
};
const textOf = (el) => el.textContent.replace(/\s+/g, " ").trim();
const countWords = (html) => {
  const t = document.createElement("template");
  t.innerHTML = html;
  return (t.content.textContent.match(/\S+/g) || []).length;
};
const store = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch { /* not kept */ } },
};

export async function loadCondensed(url = new URL("condensed.json", location.href)) {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    const data = await r.json();
    return data && data.blocks ? data : null;
  } catch {
    return null;
  }
}

// reading: the handle returned by setupAttention({ motion: false, panel: false }).
export function setupCondense(data, reading) {
  const entries = reading.blocks
    .map((el) => {
      const v = data.blocks[fnv(textOf(el))];
      if (!Array.isArray(v) || v.length !== 3) return null;
      const html = [el.innerHTML, ...v];
      return { el, html, words: html.map(countWords), shown: 0, timers: [] };
    })
    .filter(Boolean);
  if (!entries.length) return false;

  const params = new URLSearchParams(location.search);
  const debug = params.has("attn");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const key = `weft-condense:${location.pathname}`;
  let level = clamp(parseInt(params.get("condense") ?? store.get(key) ?? "0", 10) || 0, 0, 3);
  let off = store.get("weft-condense-off") === "1";
  let lastStep = 0;

  /* ---------- Swapping the text ---------- */
  // Words are wrapped with their trailing space, so a word that shrinks away takes its space with it.
  function wrapWords(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    const spans = [];
    for (const node of nodes) {
      if (!node.textContent.trim() || node.parentElement.closest("math, svg")) continue;
      const frag = document.createDocumentFragment();
      const lead = node.textContent.match(/^\s*/)[0];
      if (lead) frag.append(lead);
      for (const tok of node.textContent.slice(lead.length).match(/\S+\s*/g) || []) {
        const s = document.createElement("span");
        s.className = "cx-w";
        s.textContent = tok;
        frag.append(s);
        spans.push(s);
      }
      node.replaceWith(frag);
    }
    return spans;
  }
  const wordKey = (s) => {
    const t = s.textContent.trim().toLowerCase();
    return t.replace(/[^\p{L}\p{N}]/gu, "") || t;
  };
  // Longest common subsequence of words: these stay put while the rest is struck out or written in.
  function keepers(a, b) {
    const n = a.length, m = b.length, w = m + 1;
    const dp = new Uint16Array((n + 1) * w);
    for (let i = n - 1; i >= 0; i--)
      for (let j = m - 1; j >= 0; j--)
        dp[i * w + j] = a[i] === b[j] ? dp[(i + 1) * w + j + 1] + 1 : Math.max(dp[(i + 1) * w + j], dp[i * w + j + 1]);
    const ka = new Set(), kb = new Set();
    for (let i = 0, j = 0; i < n && j < m; ) {
      if (a[i] === b[j]) { ka.add(i++); kb.add(j++); }
      else if (dp[(i + 1) * w + j] >= dp[i * w + j + 1]) i++;
      else j++;
    }
    return [ka, kb];
  }

  function settle(e, to) {
    e.timers.forEach(clearTimeout);
    e.timers = [];
    e.el.innerHTML = e.html[to];
    e.el.classList.remove("cx-editing");
    e.shown = to;
    reading.recount(e.el);
  }

  // Like an editor's pen: words that go are struck through and close up, then new words are written in.
  function morph(e, to, delay) {
    settle(e, e.shown);
    const tmp = document.createElement(e.el.tagName);
    tmp.innerHTML = e.html[to];
    const oldW = wrapWords(e.el), newW = wrapWords(tmp);
    const [keepOld, keepNew] = keepers(oldW.map(wordKey), newW.map(wordKey));
    const going = oldW.filter((_, i) => !keepOld.has(i));
    const coming = newW.filter((_, i) => !keepNew.has(i));
    e.el.classList.add("cx-editing");
    const at = (ms, fn) => e.timers.push(setTimeout(fn, delay + ms));
    at(0, () => going.forEach((s) => s.classList.add("cx-strike")));
    at(380, () => {
      going.forEach((s) => { s.style.maxWidth = `${s.offsetWidth}px`; s.classList.add("cx-box"); });
      void e.el.offsetWidth;
      going.forEach((s) => s.classList.add("cx-gone"));
    });
    at(900, () => {
      e.el.replaceChildren(...tmp.childNodes);
      coming.forEach((s) => s.classList.add("cx-box"));
      const widths = coming.map((s) => s.offsetWidth);
      coming.forEach((s) => s.classList.add("cx-gone", "cx-new"));
      void e.el.offsetWidth;
      coming.forEach((s, i) => { s.style.maxWidth = `${widths[i]}px`; s.classList.remove("cx-gone"); });
    });
    at(1500, () => coming.forEach((s) => s.classList.add("cx-inked")));
    at(2600, () => settle(e, to));
  }

  function render(to, animate) {
    // Keep the passage at the top of the screen where it is while everything above changes length.
    const top = document.querySelector(".site-header")?.getBoundingClientRect().bottom ?? 0;
    const anchor = entries.find((e) => e.el.getBoundingClientRect().bottom > top)?.el;
    const before = anchor?.getBoundingClientRect().top ?? 0;
    const root = document.documentElement;
    root.style.overflowAnchor = "none";
    let n = 0;
    for (const e of entries) {
      if (e.shown === to && !e.timers.length) continue;
      const r = e.el.getBoundingClientRect();
      const onScreen = r.bottom > top - 40 && r.top < innerHeight + 40;
      if (animate && onScreen && !reducedMotion.matches) morph(e, to, 90 * n++);
      else settle(e, to);
    }
    if (anchor) scrollBy({ top: anchor.getBoundingClientRect().top - before, behavior: "instant" });
    requestAnimationFrame(() => (root.style.overflowAnchor = ""));
  }

  function setLevel(to, why) {
    to = clamp(to, 0, 3);
    if (to === level) return;
    level = to;
    store.set(key, to ? String(to) : null);
    render(to, true);
    ui.announce(why);
  }

  // Printing and saving always use the full text.
  addEventListener("beforeprint", () => entries.forEach((e) => settle(e, 0)));
  addEventListener("afterprint", () => entries.forEach((e) => settle(e, off ? 0 : level)));

  /* ---------- The panel ---------- */
  const ui = (() => {
    const icon = {
      help: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.5v.6"/><circle cx="12" cy="16.9" r=".6" fill="currentColor"/></svg>',
      min: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 12h12"/></svg>',
      close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17"/></svg>',
    };
    const root = document.createElement("div");
    root.className = "attn-ui cx-ui";
    root.innerHTML = `
      <div class="attn-pop" role="dialog" aria-modal="false" aria-labelledby="cx-pop-title" hidden>
        <button class="attn-icon attn-pop-close" type="button" aria-label="Close">${icon.close}</button>
        <div class="attn-pop-body">
          <h2 id="cx-pop-title">Condensing prose</h2>
          <p>This paper notices how you read it. Read at a steady pace and it stays as written.</p>
          <p>Skim, scrolling past passages faster than they can be read, and the writing condenses to match: first to concise prose, then to terse notes, and finally to caveman.</p>
          <p>It only ever condenses. Calm reading does not bring the words back; you do, by picking a level on the panel or pressing <em>Back to full prose</em>. Your level is remembered for this paper on this device.</p>
          <p>Every level is written ahead of time and checked against the paper. The full text is the one to cite, and it is the one that prints. Reading is measured in your browser and nothing is sent anywhere.</p>
          <p class="attn-pop-foot">To stop it, press <span class="attn-kbd" aria-label="the close button">×</span> on the panel.</p>
        </div>
      </div>
      <section class="attn-panel" aria-label="Condensing prose">
        <div class="attn-head">
          <span class="attn-title">Condensing prose</span>
          <button class="attn-icon attn-help" type="button" aria-label="What is this?">${icon.help}</button>
          <button class="attn-icon attn-min" type="button" aria-label="Minimise">${icon.min}</button>
          <span class="attn-x-wrap">
            <button class="attn-icon attn-x" type="button" aria-describedby="cx-x-tip">${icon.close}</button>
            <span class="attn-tip" id="cx-x-tip" role="tooltip">Stops condensing</span>
          </span>
        </div>
        <div class="cx-ladder" role="group" aria-label="Prose level">
          ${SHORT.map((s, i) => `<button type="button" class="cx-rung" data-level="${i}" title="${LEVELS[i]}">${s}</button>`).join("")}
        </div>
        <p class="attn-status cx-status" aria-live="polite"></p>
        <div class="attn-meter cx-meter" aria-hidden="true"><span></span></div>
        <dl class="attn-stats">
          <div><dt>Words</dt><dd class="cx-words"></dd></div>
          <div><dt>Reading</dt><dd class="cx-time"></dd></div>
        </dl>
        <button class="attn-on cx-restore" type="button" hidden>Back to full prose</button>
        <button class="attn-on cx-on" type="button" hidden>Turn condensing back on</button>
        <pre class="attn-debug" ${debug ? "" : "hidden"}></pre>
      </section>
      <button class="attn-dock" type="button" aria-label="Show the condensing prose panel" hidden>
        <svg viewBox="0 0 32 32" aria-hidden="true"><use href="#weave-mark"/></svg>
        <span class="cx-badge" aria-hidden="true" hidden></span>
      </button>`;
    document.body.append(root);
    const $ = (s) => root.querySelector(s);
    const panel = $(".attn-panel"), dock = $(".attn-dock"), pop = $(".attn-pop"), badge = $(".cx-badge");
    const rungs = [...root.querySelectorAll(".cx-rung")];
    const status = $(".cx-status"), fill = $(".cx-meter span"), wordsOut = $(".cx-words"), timeOut = $(".cx-time");
    const restore = $(".cx-restore"), onBtn = $(".cx-on"), xBtn = $(".attn-x"), dbg = $(".attn-debug");
    let minimised = store.get("weft-condense-min") === "1";

    // Each level describes itself in its own voice.
    const VOICE = [
      "As written. Skim, and it condenses.",
      "Concise. You were skimming, so the page trimmed itself.",
      "Terse. Skim more → fewer words. Grammar optional.",
      "Caveman. You skim. Page shrink. Press button, get big words back.",
    ];
    const SQUEEZED = [
      "Back to the full text.",
      "Skimming detected: condensed to concise prose.",
      "Still skimming: condensed to terse notes.",
      "Still skim. Now caveman.",
    ];

    const setMin = (m) => {
      minimised = m;
      store.set("weft-condense-min", m ? "1" : null);
      panel.hidden = m;
      dock.hidden = !m;
      if (m) pop.hidden = true;
    };
    const setOff = (o, show = true) => {
      off = o;
      store.set("weft-condense-off", o ? "1" : null);
      document.documentElement.classList.toggle("cx-off", o);
      xBtn.hidden = o;
      onBtn.hidden = !o;
      if (o) pop.hidden = true;
      if (show) render(o ? 0 : level, true);
      update();
    };

    rungs.forEach((b) => b.addEventListener("click", () => {
      const to = +b.dataset.level;
      if (off) setOff(false, false);
      reading.calm(to ? RISE[to - 1] : 0);
      setLevel(to, "chosen");
    }));
    restore.addEventListener("click", () => { reading.calm(0); setLevel(0, "chosen"); rungs[0].focus({ preventScroll: true }); });
    $(".attn-help").addEventListener("click", () => {
      pop.hidden = !pop.hidden;
      if (!pop.hidden) $(".attn-pop-close").focus({ preventScroll: true });
    });
    $(".attn-pop-close").addEventListener("click", () => (pop.hidden = true));
    addEventListener("keydown", (ev) => { if (ev.key === "Escape") pop.hidden = true; });
    $(".attn-min").addEventListener("click", () => setMin(true));
    dock.addEventListener("click", () => { setMin(false); $(".attn-min").focus({ preventScroll: true }); });
    xBtn.addEventListener("click", () => { setOff(true); onBtn.focus({ preventScroll: true }); });
    onBtn.addEventListener("click", () => setOff(false));

    const fmt = (n) => n.toLocaleString("en-GB");
    const total = (l) => entries.reduce((s, e) => s + e.words[l], 0);
    const full = total(0);
    let lastStatus = "", flash = -Infinity;
    function announce(why) {
      if (why === "auto") {
        status.textContent = lastStatus = SQUEEZED[level];
        flash = performance.now();
        root.classList.remove("cx-squeezed");
        void root.offsetWidth;
        root.classList.add("cx-squeezed");
      }
      update();
    }
    function update() {
      const shown = off ? 0 : level;
      rungs.forEach((b, i) => {
        b.setAttribute("aria-pressed", String(i === shown));
        b.classList.toggle("cx-past", i < shown);
      });
      document.documentElement.dataset.condense = String(shown);
      const s = off ? "Condensing is off. The paper stays as written." : performance.now() - flash < 4000 ? lastStatus : VOICE[level];
      if (s !== lastStatus) { status.textContent = s; lastStatus = s; }
      // The meter fills toward the next squeeze.
      const lo = level ? RISE[level - 1] : 0, hi = RISE[level];
      const toward = off || level === 3 ? (level === 3 && !off ? 1 : 0) : clamp((attention.restless - lo) / (hi - lo), 0, 1);
      fill.style.transform = `scaleX(${toward.toFixed(3)})`;
      const now = total(shown);
      wordsOut.textContent = shown ? `${fmt(now)} of ${fmt(full)}` : fmt(full);
      timeOut.textContent = `${Math.max(1, Math.round(now / WPM))} min`;
      restore.hidden = off || !level;
      badge.hidden = !shown;
      badge.textContent = shown ? SHORT[shown][0] : "";
      if (debug) {
        dbg.textContent = [
          `restless ${attention.restless.toFixed(2)}  level ${level}${off ? " (off)" : ""}`,
          `next at  ${level < 3 ? RISE[level] : "-"}`,
          `passages ${entries.length} condensable`,
        ].join("\n");
      }
    }
    setMin(minimised);
    return { announce, update, setOff };
  })();

  /* ---------- The ratchet ---------- */
  if (level && !off) render(level, false);
  ui.setOff(off, false);
  setInterval(() => {
    if (!off && level < 3 && attention.restless >= RISE[level] && performance.now() - lastStep > STEP_GAP) {
      lastStep = performance.now();
      reading.calm(RISE[level]); // the squeeze spends the pressure that caused it
      setLevel(level + 1, "auto");
    }
    ui.update();
  }, 200);
  return true;
}
