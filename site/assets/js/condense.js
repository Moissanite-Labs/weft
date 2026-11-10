// Condensing prose: on the papers, skimming squeezes the writing.
//
// The reading score from attention.js decides; this module only acts on it.
// Read at a steady pace and the paper stays as written. Skim and the prose
// condenses, one level at a time: concise prose, terse notes, caveman, and
// finally one line per section (TL;DR). Only passages you have not read
// condense, so the page ends up a map of how you read it. Headings condense
// with the page. Keep skimming at TL;DR and a button offering a simple
// explanation (ELI5) comes looking for you.
//
// It never loosens by itself; the visitor brings the words back from the panel.
// Condensed passages are marked (≈), and pressing and holding one shows it in
// full. Every level is written ahead of time (condensed.json beside the page),
// so the condensing is editing, not generation, and the full text stays the one
// that counts: printing always prints it.
//
// For review: ?condense=4 opens the page at a level, ?attn adds raw numbers.

import { attention } from "./attention.js";

const LEVELS = ["Full prose", "Concise", "Terse", "Caveman", "TL;DR", "ELI5"];
const SHORT = ["Full", "Concise", "Terse", "Caveman", "TL;DR", "ELI5"];
const TLDR = 4, ELI5 = 5;
// Restlessness at which the next squeeze happens. Each squeeze spends the
// pressure that caused it (down to SPENT), so every level is earned by more skimming.
const STEP_AT = [0.3, 0.5, 0.5, 0.55];
const SPENT = 0.2;
const WANDER_AT = 0.4; // still skimming at TL;DR: the ELI5 button comes looking
const STEP_GAP = 1500; // ms: one squeeze at a time, so each one can be seen
const PEEK_HOLD = 350; // ms
const WPM = 230;
const ELI5_TIP = "I still don’t get it, please explain wewwy simple";

// Exported for the Node test (weft/runtime/aywa/test_condense.mjs): the
// level clamp is the guard the PR 93 review caught missing on the
// ?condense= path. NaN clamps to the floor, so a bad value can never slip
// a level outside its range. fnv is the passage-key hash; the Python key
// check in scripts/check_condensed.py uses the same function.
export const clamp = (v, a, b) => (Number.isNaN(v) ? a : v < a ? a : v > b ? b : v);
export const fnv = (s) => {
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
  /* ---------- What can change ---------- */
  // Passages: four versions each (full, concise, terse, caveman), and their own level.
  const passages = reading.blocks
    .map((el) => {
      const hash = fnv(textOf(el));
      const v = data.blocks[hash];
      if (!Array.isArray(v) || v.length !== 3) return null;
      const html = [el.innerHTML, ...v];
      return { el, hash, html, words: html.map(countWords), shown: 0, lv: 0, timers: [], passage: true };
    })
    .filter(Boolean);
  if (!passages.length) return false;
  const byEl = new Map(passages.map((p) => [p.el, p]));

  // Sections: a heading that condenses with the page, and a summary line (TL;DR, then ELI5).
  const sections = [...document.querySelectorAll("article.paper section")]
    .map((el) => {
      const id = el.id || (el.classList.contains("abstract") ? "abstract" : "");
      const h = el.querySelector(":scope > h2");
      const heads = data.headings?.[id], tldr = data.tldr?.[id], eli5 = data.eli5?.[id];
      if (!h || !Array.isArray(heads) || heads.length !== 5 || !tldr || !eli5) return null;
      const sum = document.createElement("p");
      sum.className = "cx-sum";
      sum.innerHTML = tldr;
      h.after(sum);
      return {
        el, id,
        head: { el: h, html: [h.innerHTML, ...heads], shown: 0, timers: [] },
        sum: { el: sum, html: [tldr, eli5], words: [countWords(tldr), countWords(eli5)], shown: 0, timers: [] },
      };
    })
    .filter(Boolean);
  const canFold = sections.length > 0;
  const top = canFold ? 5 : 3;

  // The ELI5 button at the end of the TL;DR version.
  let eliSlot = null;
  if (canFold) {
    eliSlot = document.createElement("div");
    eliSlot.className = "cx-eli5-slot";
    eliSlot.innerHTML = eli5Button("cx-eli5");
    sections[sections.length - 1].el.after(eliSlot);
  }
  function eli5Button(cls) {
    return `<span class="cx-eli5-wrap"><button type="button" class="${cls}" aria-describedby="${cls}-tip">ELI5</button><span class="cx-eli5-tip" id="${cls}-tip" role="tooltip">${ELI5_TIP}</span></span>`;
  }

  /* ---------- State ---------- */
  const params = new URLSearchParams(location.search);
  const debug = params.has("attn");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const key = `weft-condense:${location.pathname}`;
  let level = 0;
  try {
    const saved = JSON.parse(store.get(key) ?? "null");
    if (typeof saved === "number") level = saved;
    else if (saved) {
      level = saved.level | 0;
      passages.forEach((p) => (p.lv = clamp(saved.lv?.[p.hash] | 0, 0, 3)));
    }
  } catch { /* start fresh */ }
  if (params.has("condense")) {
    level = parseInt(params.get("condense"), 10) || 0;
    passages.forEach((p) => (p.lv = clamp(level, 0, 3)));
  }
  level = clamp(level, 0, top);
  let off = store.get("weft-condense-off") === "1";
  let printing = false, lastStep = 0;

  const save = () => {
    const lv = {};
    passages.forEach((p) => { if (p.lv) lv[p.hash] = p.lv; });
    store.set(key, level || Object.keys(lv).length ? JSON.stringify({ level, lv }) : null);
  };
  // What the page shows right now: the full text when off or printing.
  const view = () => (off || printing ? 0 : level);
  const passageView = (p) => (off || printing ? 0 : p.lv);

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

  function settle(it, to) {
    it.timers.forEach(clearTimeout);
    it.timers = [];
    it.el.innerHTML = it.html[to];
    it.el.classList.remove("cx-editing");
    it.shown = to;
    if (it.passage) {
      it.el.classList.toggle("cx-condensed", to > 0);
      it.el.dataset.cx = LEVELS[to];
      reading.recount(it.el);
    }
  }

  // Like an editor's pen: words that go are struck through and close up, then new words are written in.
  function morph(it, to, delay) {
    settle(it, it.shown);
    const tmp = document.createElement(it.el.tagName);
    tmp.innerHTML = it.html[to];
    const oldW = wrapWords(it.el), newW = wrapWords(tmp);
    const [keepOld, keepNew] = keepers(oldW.map(wordKey), newW.map(wordKey));
    const going = oldW.filter((_, i) => !keepOld.has(i));
    const coming = newW.filter((_, i) => !keepNew.has(i));
    it.el.classList.add("cx-editing");
    const at = (ms, fn) => it.timers.push(setTimeout(fn, delay + ms));
    at(0, () => going.forEach((s) => s.classList.add("cx-strike")));
    at(380, () => {
      going.forEach((s) => { s.style.maxWidth = `${s.offsetWidth}px`; s.classList.add("cx-box"); });
      void it.el.offsetWidth;
      going.forEach((s) => s.classList.add("cx-gone"));
    });
    at(900, () => {
      it.el.replaceChildren(...tmp.childNodes);
      coming.forEach((s) => s.classList.add("cx-box"));
      const widths = coming.map((s) => s.offsetWidth);
      coming.forEach((s) => s.classList.add("cx-gone", "cx-new"));
      void it.el.offsetWidth;
      coming.forEach((s, i) => { s.style.maxWidth = `${widths[i]}px`; s.classList.remove("cx-gone"); });
    });
    at(1500, () => coming.forEach((s) => s.classList.add("cx-inked")));
    at(2600, () => settle(it, to));
  }

  const headerBottom = () => document.querySelector(".site-header")?.getBoundingClientRect().bottom ?? 0;
  const onScreen = (el) => {
    const r = el.getBoundingClientRect();
    return r.bottom > headerBottom() - 40 && r.top < innerHeight + 40;
  };

  // Bring every passage, heading and summary to what the page should show.
  function render(animate) {
    animate = animate && !reducedMotion.matches && !printing;
    const v = view();
    const fold = v >= TLDR;
    const root = document.documentElement;
    const wasFolded = root.classList.contains("cx-folded");
    // Keep what is at the top of the screen where it is while everything above changes length.
    const hb = headerBottom();
    const anchorList = fold !== wasFolded ? sections.map((s) => s.head.el) : passages.map((p) => p.el);
    const anchor = anchorList.find((el) => el.getBoundingClientRect().bottom > hb);
    const before = anchor?.getBoundingClientRect().top ?? 0;
    root.style.overflowAnchor = "none";

    const jobs = [];
    for (const p of passages) {
      const to = passageView(p);
      if (p.shown !== to || p.timers.length) jobs.push([p, to]);
    }
    for (const s of sections) {
      if (s.head.shown !== v || s.head.timers.length) jobs.push([s.head, v]);
      const to = v === ELI5 ? 1 : 0;
      if (s.sum.shown !== to || s.sum.timers.length) jobs.push([s.sum, to]);
    }
    // Folding to one line per section, or back: a quick fade, then the new layout settles in.
    if (fold !== wasFolded) {
      root.classList.toggle("cx-folded", fold);
      if (animate) {
        root.classList.remove("cx-unfolding");
        void root.offsetWidth;
        root.classList.add("cx-unfolding");
        setTimeout(() => root.classList.remove("cx-unfolding"), 700);
      }
    }
    let n = 0;
    for (const [it, to] of jobs) {
      // Inside folded sections, passages are hidden: no need to animate them.
      const hidden = fold && it.passage;
      if (animate && !hidden && onScreen(it.el)) morph(it, to, 90 * n++);
      else settle(it, to);
    }
    if (anchor) {
      const after = anchor.getBoundingClientRect().top;
      // If the anchor would end up above the screen, bring its heading into view instead.
      const target = before < hb && fold !== wasFolded ? hb + 16 : before;
      scrollBy({ top: after - target, behavior: "instant" });
    }
    requestAnimationFrame(() => (root.style.overflowAnchor = ""));
    root.dataset.condense = String(v);
  }

  // Squeeze, choose or restore. auto: only passages not yet read condense.
  function setLevel(to, why) {
    to = clamp(to, 0, top);
    if (to === level) return;
    level = to;
    if (why === "auto") {
      if (to <= 3) passages.forEach((p) => { if (!p.el.classList.contains("attn-read")) p.lv = Math.max(p.lv, to); });
    } else {
      passages.forEach((p) => (p.lv = Math.min(to, 3)));
    }
    save();
    render(true);
    if (to !== TLDR) wander.stop();
    ui.announce(why);
  }

  // Printing and saving always use the full text.
  addEventListener("beforeprint", () => { printing = true; render(false); });
  addEventListener("afterprint", () => { printing = false; render(false); });

  /* ---------- Peek: press and hold a condensed passage to read it in full ---------- */
  const peek = (() => {
    const card = document.createElement("div");
    card.className = "cx-peek";
    card.setAttribute("role", "note");
    card.hidden = true;
    document.body.append(card);
    let hold = null, open = null;
    const close = () => {
      clearTimeout(hold?.timer);
      hold = null;
      if (!open) return;
      open.el.classList.remove("cx-peeking");
      open = null;
      card.hidden = true;
    };
    const show = (p) => {
      open = p;
      p.el.classList.add("cx-peeking");
      getSelection()?.removeAllRanges();
      card.innerHTML = `<span class="cx-peek-label">As written</span>${p.html[0]}`;
      card.hidden = false;
      const r = p.el.getBoundingClientRect();
      const w = Math.min(r.width + 24, innerWidth - 24);
      card.style.width = `${w}px`;
      card.style.left = `${clamp(r.left - 12, 12, innerWidth - w - 12)}px`;
      const h = card.offsetHeight;
      // Above the passage if there is room, otherwise below it.
      const y = r.top - h - 10 > headerBottom() ? r.top - h - 10 : Math.min(r.bottom + 10, innerHeight - h - 12);
      card.style.top = `${Math.max(headerBottom() + 8, y)}px`;
    };
    addEventListener("pointerdown", (ev) => {
      if (ev.button !== 0) return;
      const el = ev.target.closest?.(".cx-condensed");
      const p = el && byEl.get(el);
      if (!p || ev.target.closest("a, button") || p.shown === 0) return;
      hold = { p, x: ev.clientX, y: ev.clientY, timer: setTimeout(() => show(p), PEEK_HOLD) };
    });
    addEventListener("pointermove", (ev) => {
      if (hold && !open && Math.hypot(ev.clientX - hold.x, ev.clientY - hold.y) > 8) close();
    }, { passive: true });
    addEventListener("pointerup", close);
    addEventListener("pointercancel", close);
    addEventListener("scroll", close, { passive: true });
    addEventListener("contextmenu", (ev) => { if (open || hold) ev.preventDefault(); });
    return { close };
  })();

  /* ---------- The wandering ELI5 button ----------
     At TL;DR, still skimming: a floating copy of the button follows the cursor,
     lazily, and stops when the cursor stops or comes close, so it can be clicked. */
  const wander = (() => {
    const wrap = document.createElement("div");
    wrap.className = "cx-eli5-float";
    wrap.innerHTML = eli5Button("cx-eli5-f");
    wrap.hidden = true;
    document.body.append(wrap);
    const fine = window.matchMedia("(pointer: fine)");
    let on = false, x = 0, y = 0, cx = -1, cy = -1, moved = 0, raf = 0, last = 0;
    addEventListener("pointermove", (ev) => {
      if (ev.pointerType !== "mouse") return;
      cx = ev.clientX; cy = ev.clientY; moved = performance.now();
    }, { passive: true });
    function frame(t) {
      raf = 0;
      if (!on) return;
      const dt = last ? Math.min(0.05, (t - last) / 1000) : 0.016;
      last = t;
      const w = wrap.offsetWidth, h = wrap.offsetHeight;
      if (fine.matches && cx >= 0) {
        const near = Math.hypot(cx - (x + w / 2), cy - (y + h / 2)) < 70;
        const busy = performance.now() - moved < 250;
        if (busy && !near) {
          // Trail the cursor, a little behind and to the side, with a lazy wobble.
          const tx = cx + 26 + Math.sin(t / 340) * 10, ty = cy + 20 + Math.cos(t / 410) * 8;
          const k = 1 - Math.exp(-dt * 3.2);
          x += (tx - x) * k;
          y += (ty - y) * k;
        }
      }
      x = clamp(x, 8, innerWidth - w - 8);
      y = clamp(y, headerBottom() + 8, innerHeight - h - 8);
      wrap.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
      raf = requestAnimationFrame(frame);
    }
    return {
      get on() { return on; },
      start() {
        if (on || reducedMotion.matches) return;
        on = true;
        wrap.hidden = false;
        document.documentElement.classList.add("cx-wandering");
        // Start near the cursor, or above the panel on touch screens.
        x = cx >= 0 && fine.matches ? cx + 40 : innerWidth / 2 - 40;
        y = cy >= 0 && fine.matches ? cy + 30 : innerHeight - 260;
        last = 0;
        if (!raf) raf = requestAnimationFrame(frame);
      },
      stop() {
        on = false;
        wrap.hidden = true;
        document.documentElement.classList.remove("cx-wandering");
      },
    };
  })();
  addEventListener("click", (ev) => {
    if (ev.target.closest(".cx-eli5, .cx-eli5-f")) {
      reading.calm(0);
      setLevel(ELI5, "eli5");
    }
  });

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
          <p>Skim, scrolling past passages faster than they can be read, and the writing condenses to match: concise prose, then terse notes, then caveman, then one line per section. Only passages you have not read condense; the ones you read stay as they were. Keep skimming even then, and an offer of a simpler explanation comes looking for you.</p>
          <p>It only ever condenses. Calm reading does not bring the words back; you do, by picking a level on the panel or pressing <em>Back to full prose</em>. Your level is remembered for this paper on this device.</p>
          <h3>Reading a condensed passage</h3>
          <p>Condensed passages end with <span class="attn-kbd">≈</span>. Press and hold one to see it as written.</p>
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
          ${SHORT.slice(0, top + 1).map((s, i) => `<button type="button" class="cx-rung${i === ELI5 ? " cx-rung-eli5" : ""}" data-level="${i}" title="${i === ELI5 ? ELI5_TIP : LEVELS[i]}">${s}</button>`).join("")}
        </div>
        <p class="attn-status cx-status" aria-live="polite"></p>
        <div class="attn-meter cx-meter" aria-hidden="true"><span></span></div>
        <dl class="attn-stats">
          <div><dt>Words</dt><dd class="cx-words"></dd></div>
          <div><dt>Reading</dt><dd class="cx-time"></dd></div>
        </dl>
        <p class="cx-map" hidden></p>
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
    const restore = $(".cx-restore"), onBtn = $(".cx-on"), xBtn = $(".attn-x"), dbg = $(".attn-debug"), map = $(".cx-map");
    let minimised = store.get("weft-condense-min") === "1";

    // Each level describes itself in its own voice.
    const VOICE = [
      "As written. Skim, and it condenses.",
      "Concise. You were skimming, so the page trimmed itself.",
      "Terse. Skim more → fewer words. Grammar optional.",
      "Caveman. You skim. Page shrink. Press button, get big words back.",
      "TL;DR. One line per section. Still lost? There’s help at the end.",
      "Explained simply. The full paper is one tap away whenever you want it.",
    ];
    const SQUEEZED = [
      "Back to the full text.",
      "Skimming detected: unread passages condensed to concise prose.",
      "Still skimming: unread passages condensed to terse notes.",
      "Still skim. Now caveman.",
      "Skimmed the caveman. One line per section now.",
      "Explained simply.",
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
      if (o) { pop.hidden = true; wander.stop(); peek.close(); }
      if (show) render(true);
      update();
    };

    rungs.forEach((b) => b.addEventListener("click", () => {
      const to = +b.dataset.level;
      if (off) setOff(false, false);
      reading.calm(to ? SPENT : 0);
      setLevel(to, "chosen");
      if (to === level) render(true); // e.g. turned back on at the same level
    }));
    restore.addEventListener("click", () => { reading.calm(0); setLevel(0, "chosen"); rungs[0].focus({ preventScroll: true }); });
    $(".attn-help").addEventListener("click", () => {
      pop.hidden = !pop.hidden;
      if (!pop.hidden) $(".attn-pop-close").focus({ preventScroll: true });
    });
    $(".attn-pop-close").addEventListener("click", () => (pop.hidden = true));
    addEventListener("keydown", (ev) => { if (ev.key === "Escape") { pop.hidden = true; peek.close(); } });
    $(".attn-min").addEventListener("click", () => setMin(true));
    dock.addEventListener("click", () => { setMin(false); $(".attn-min").focus({ preventScroll: true }); });
    xBtn.addEventListener("click", () => { setOff(true); onBtn.focus({ preventScroll: true }); });
    onBtn.addEventListener("click", () => setOff(false));

    const fmt = (n) => n.toLocaleString("en-GB");
    const full = passages.reduce((s, p) => s + p.words[0], 0);
    const shownWords = () => {
      const v = view();
      if (v >= TLDR) return sections.reduce((s, x) => s + x.sum.words[v === ELI5 ? 1 : 0], 0);
      return passages.reduce((s, p) => s + p.words[passageView(p)], 0);
    };
    let lastStatus = "", flash = -Infinity;
    function announce(why) {
      if (why === "auto" || why === "eli5") {
        status.textContent = lastStatus = SQUEEZED[level];
        flash = performance.now();
        root.classList.remove("cx-squeezed");
        void root.offsetWidth;
        root.classList.add("cx-squeezed");
      }
      update();
    }
    function update() {
      const v = view();
      rungs.forEach((b, i) => {
        b.setAttribute("aria-pressed", String(i === v));
        b.classList.toggle("cx-past", i < v);
      });
      const s = off ? "Condensing is off. The paper stays as written." : performance.now() - flash < 4000 ? lastStatus : VOICE[level];
      if (s !== lastStatus) { status.textContent = s; lastStatus = s; }
      // The meter fills toward the next squeeze (or, at TL;DR, toward the ELI5 button coming to find you).
      const r = attention.restless;
      let toward = 0;
      if (!off && level < TLDR && canFold || !off && level < 3) toward = clamp((r - (level ? SPENT : 0)) / (STEP_AT[level] - (level ? SPENT : 0)), 0, 1);
      else if (!off && level === TLDR) toward = wander.on ? 1 : clamp((r - SPENT) / (WANDER_AT - SPENT), 0, 1);
      else if (!off) toward = 1;
      fill.style.transform = `scaleX(${toward.toFixed(3)})`;
      const now = shownWords();
      wordsOut.textContent = v ? `${fmt(now)} of ${fmt(full)}` : fmt(full);
      timeOut.textContent = `${Math.max(1, Math.round(now / WPM))} min`;
      // The map of how you read: passages kept as written because you read them.
      const kept = passages.filter((p) => p.lv < level && level <= 3).length;
      map.hidden = !kept || off;
      if (kept) map.textContent = `${kept} passage${kept === 1 ? "" : "s"} you read ${kept === 1 ? "stays" : "stay"} as ${kept === 1 ? "it was" : "they were"}.`;
      restore.hidden = off || !level;
      badge.hidden = !v;
      badge.textContent = v ? ["", "1", "2", "3", "1L", "5"][v] : "";
      if (debug) {
        dbg.textContent = [
          `restless ${r.toFixed(2)}  level ${level}${off ? " (off)" : ""}`,
          `next at  ${level < TLDR ? STEP_AT[level] : level === TLDR ? `wander ${WANDER_AT}` : "-"}`,
          `passages ${passages.length}, sections ${sections.length}, wander ${wander.on}`,
        ].join("\n");
      }
    }
    setMin(minimised);
    return { announce, update, setOff };
  })();

  /* ---------- The ratchet ---------- */
  ui.setOff(off, false);
  render(false);
  ui.update();
  setInterval(() => {
    if (!off) {
      const r = attention.restless;
      const maxAuto = canFold ? TLDR : 3;
      if (level < maxAuto && r >= STEP_AT[level] && performance.now() - lastStep > STEP_GAP) {
        lastStep = performance.now();
        reading.calm(SPENT); // the squeeze spends the pressure that caused it
        setLevel(level + 1, "auto");
      } else if (level === TLDR && r >= WANDER_AT && !wander.on) {
        wander.start();
      }
    }
    ui.update();
  }, 200);
  return true;
}
