// Reading attention: the page rewards reading and resists skimming.
//
// A restlessness score (0..1) rises when the visitor skims: scrolling past
// paragraphs they saw but did not give time to, sustained fast scrolling,
// frantic changes of scroll direction, long jumps, and jerky cursor movement.
// It falls mostly by reading. The score drives waves that pass through the
// page as a medium: words bob as crests pass, fade in the troughs and blur,
// and at the top end links and buttons drift and slide away from a hurried
// cursor. Paragraphs that were actually read get a thread woven beside them.
//
// Guardrails: the focused element never moves, text stays text for assistive
// technology, displacement is capped, a cursor held still on a link settles
// it, and nothing moves under prefers-reduced-motion.
//
// A small panel shows the reading, explains it, and lets the visitor switch it off.
// It runs on every page with a few passages to read; the module starts itself,
// unless a page calls holdAttention() first and later starts it with its own
// options. The paper pages do that: they keep the reading score but swap the
// motion and this panel for condensing prose (condense.js).
// For review and tuning: ?attn adds raw numbers to the panel, ?restless=0.7 pins the score.

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const smooth = (a, b, v) => {
  const t = clamp01((v - a) / (b - a));
  return t * t * (3 - 2 * t);
};

// Shared with the hero loom, so the whole page feels the same mood.
export const attention = { restless: 0, reading: false };

const READ_WPS = 10; // lenient: ~600 words a minute counts as having read a block
const BLOCKS = "main :is(p, li)";
// Never read or rippled: the navy heroes, code, math, figures, tables, forms, demos and navigation.
const NOT_TEXT = ".hero, .paper-hero, pre, code, button, label, form, .demo, figure, table, nav, aside, .crumbs";
const NAV = ".site-header .nav a, .site-header .icon-btn, .btn, .card h3 a, .paper-toc a, .site-footer a";
let started = false, held = false;

// Stop the module from starting itself, so a page can start it with options.
export function holdAttention() {
  held = true;
}

// Options: motion (default true) moves words, links and waves; panel (default true)
// shows the reading weave panel. Returns a small handle for pages that build on the score.
export function setupAttention({ motion = true, panel = true } = {}) {
  if (started) return null;
  started = true;
  const params = new URLSearchParams(location.search);
  const pinned = params.has("restless") ? clamp01(parseFloat(params.get("restless")) || 0) : null;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ---------- Reading blocks ---------- */
  const blocks = [...document.querySelectorAll(BLOCKS)]
    .filter((el) => !el.closest(NOT_TEXT) && !el.querySelector("p, li"))
    .map((el, order) => {
      const words = (el.textContent.match(/\S+/g) || []).length;
      return { el, order, words, need: Math.max(1.2, words / READ_WPS), dwell: 0, seen: false, read: false, skipped: false, visible: false, spans: null };
    })
    .filter((b) => b.words >= 4);
  if (blocks.length < 3) return null; // nothing much to read here
  blocks.forEach((b) => b.el.classList.add("attn-block"));
  const byEl = new Map(blocks.map((b) => [b.el, b]));
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      const b = byEl.get(e.target);
      b.visible = e.isIntersecting;
      // Coming back to a skipped passage gives it a fresh chance, and skipping it again counts again.
      if (b.visible && b.skipped && !b.read) { b.skipped = false; b.seen = false; b.dwell = 0; b.again = true; }
      // Seen: most of it was on screen (or, for a tall block, it filled a good part of the screen).
      if (e.intersectionRatio > 0.6 || e.intersectionRect.height > innerHeight * 0.4) b.seen = true;
    }
  }, { threshold: [0, 0.3, 0.6, 1] });
  blocks.forEach((b) => io.observe(b.el));

  /* ---------- Signals ---------- */
  let restless = pinned ?? 0;
  const stats = { skippedWords: 0, readWords: 0, jumps: 0, flips: 0 };
  const scroll = { y: scrollY, t: performance.now(), v: 0, dir: 0, flips: [] };
  addEventListener("scroll", () => {
    const now = performance.now();
    const dt = Math.max(8, now - scroll.t) / 1000;
    const dy = scrollY - scroll.y;
    const v = Math.abs(dy) / dt;
    scroll.v = Math.max(scroll.v * 0.6, v);
    if (Math.abs(dy) > innerHeight * 1.5 && dt < 0.25) {
      bump(0.05); // a long jump past content
      stats.jumps++;
    }
    const dir = Math.sign(dy);
    if (dir && scroll.dir && dir !== scroll.dir && v > 300) {
      scroll.flips.push(now);
      stats.flips++;
    }
    if (dir) scroll.dir = dir;
    scroll.y = scrollY;
    scroll.t = now;
  }, { passive: true });

  // Cursor: speed and how abruptly its turning changes (the same reading as the hero).
  const cur = { x: -1e4, y: -1e4, t: 0, heading: 0, omega: 0, speed: 0, jolt: 0, still: 0, has: false };
  addEventListener("pointermove", (ev) => {
    const samples = ev.getCoalescedEvents ? ev.getCoalescedEvents() : [];
    for (const e of samples.length ? samples : [ev]) readCursor(e.clientX, e.clientY, e.timeStamp);
  }, { passive: true });
  function readCursor(x, y, ts) {
    if (!cur.has || ts - cur.t > 250) {
      Object.assign(cur, { x, y, t: ts, omega: 0, has: true });
      return;
    }
    const dx = x - cur.x, dy = y - cur.y, dist = Math.hypot(dx, dy);
    if (dist < 10) return;
    const dt = Math.max(0.008, (ts - cur.t) / 1000);
    const v = dist / dt;
    const heading = Math.atan2(dy, dx);
    const dTheta = Math.atan2(Math.sin(heading - cur.heading), Math.cos(heading - cur.heading));
    const omega = cur.omega * 0.5 + (dTheta / dt) * 0.5;
    const alpha = Math.abs(omega - cur.omega) / dt;
    const moving = clamp01(v / 350);
    cur.speed = Math.max(cur.speed, clamp01(v / 1800));
    cur.jolt = Math.max(cur.jolt, clamp01(alpha / 1400) * moving);
    Object.assign(cur, { x, y, t: ts, heading, omega, still: 0 });
  }

  function bump(v) {
    if (pinned === null) restless = clamp01(restless + v);
  }

  /* ---------- Waves through the page (document coordinates, so they travel with the content) ---------- */
  const waves = [];
  let seedDebt = 0;
  const launch = (x, y, amp, r) => {
    if (waves.length >= 4 + Math.round(10 * r)) return;
    const lambda = 220 - 150 * r + Math.random() * 40;
    waves.push({ x, y, amp, r0: 0, c: 70 + 260 * r, lambda, len: lambda * (1.5 + Math.random()), phase: Math.random() * 6.28, age: 0, life: 5 + Math.random() * 3, fade: 0 });
  };
  // Turbulence: interfering plane waves that churn the whole page once restlessness is high.
  let clock = 0, churn = 0;
  const field = (x, y) => {
    let f = churn
      ? churn * (0.6 * Math.sin(x * 0.013 + clock * 1.9) * Math.cos(y * 0.009 - clock * 1.4) + 0.4 * Math.sin((x - y) * 0.021 + clock * 3.1))
      : 0;
    for (const v of waves) {
      const dx = x - v.x, dy = y - v.y;
      const u = v.r0 - Math.sqrt(dx * dx + dy * dy);
      if (u < 0 || u > v.len) continue;
      f += v.amp * v.fade * Math.sin((Math.PI * u) / v.len) * Math.cos((6.2832 * u) / v.lambda + v.phase);
    }
    return f;
  };

  /* ---------- Text: split words lazily, the first time the page gets restless ---------- */
  let split = false;
  const words = []; // { el, block, x, y } in document coordinates
  function splitWords() {
    split = true;
    for (const b of blocks) {
      const walker = document.createTreeWalker(b.el, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      b.spans = [];
      for (const node of nodes) {
        if (!node.textContent.trim() || node.parentElement.closest("code, kbd, button, math, svg, sup, sub")) continue;
        const frag = document.createDocumentFragment();
        for (const part of node.textContent.split(/(\s+)/)) {
          if (!part) continue;
          if (/^\s+$/.test(part)) {
            frag.append(part);
          } else {
            const s = document.createElement("span");
            s.className = "attn-w";
            s.textContent = part;
            frag.append(s);
            b.spans.push(s);
          }
        }
        node.replaceWith(frag);
      }
    }
    measure();
  }
  function measure() {
    words.length = 0;
    for (const b of blocks) {
      if (!b.spans) continue;
      for (const el of b.spans) {
        const r = el.getBoundingClientRect();
        words.push({ el, block: b, x: r.left + r.width / 2 + scrollX, y: r.top + r.height / 2 + scrollY, moved: false });
      }
    }
    navs.forEach((n) => {
      const r = n.el.getBoundingClientRect();
      n.x = r.left + r.width / 2;
      n.y = r.top + r.height / 2;
      n.fixed = !!n.el.closest(".site-header");
      if (!n.fixed) { n.x += scrollX; n.y += scrollY; }
    });
  }
  let measureTimer = 0;
  addEventListener("resize", () => {
    clearTimeout(measureTimer);
    measureTimer = setTimeout(() => {
      // Clear transforms first so measurements are of the resting layout.
      words.forEach((w) => (w.el.style.transform = ""));
      navs.forEach((n) => (n.el.style.transform = ""));
      if (split) measure();
    }, 150);
  });

  /* ---------- Links and buttons ---------- */
  const navs = (motion ? [...document.querySelectorAll(NAV)] : []).map((el) => ({ el, x: 0, y: 0, ox: 0, oy: 0, hover: 0, fixed: false }));
  navs.forEach((n) => {
    n.el.classList.add("attn-nav");
    n.el.addEventListener("pointerenter", () => (n.hover = 0.0001));
    n.el.addEventListener("pointerleave", () => (n.hover = 0));
  });

  /* ---------- Overlay: the waves themselves, faintly visible at higher levels ---------- */
  const overlay = document.createElement("canvas");
  overlay.className = "attn-overlay";
  overlay.setAttribute("aria-hidden", "true");
  if (motion) document.body.append(overlay);
  const octx = overlay.getContext("2d");
  let ow = 0, oh = 0, odpr = 1, overlayOn = false;
  const sizeOverlay = () => {
    odpr = Math.min(devicePixelRatio || 1, 2);
    ow = innerWidth;
    oh = innerHeight;
    overlay.width = Math.round(ow * odpr);
    overlay.height = Math.round(oh * odpr);
  };
  sizeOverlay();
  addEventListener("resize", sizeOverlay);

  /* ---------- The reading panel ----------
     Shows how the page reads you, and lets you minimise it (−), learn how it
     works (?) or switch the effects off altogether (×). A second ? appears by
     itself once the effects start to get in the way, to explain why. The
     visitor's choice to minimise or switch off is remembered. */
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch { /* not kept */ } },
  };
  let off = panel && store.get("weft-attn-off") === "1";
  const debug = params.has("attn");
  const ui = !panel ? { update() {} } : (() => {
    const icon = {
      help: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .8-1 1.5v.6"/><circle cx="12" cy="16.9" r=".6" fill="currentColor"/></svg>',
      min: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 12h12"/></svg>',
      close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17"/></svg>',
    };
    const root = document.createElement("div");
    root.className = "attn-ui";
    root.innerHTML = `
      <div class="attn-pop" role="dialog" aria-modal="false" aria-labelledby="attn-pop-title" hidden>
        <button class="attn-icon attn-pop-close" type="button" aria-label="Close">${icon.close}</button>
        <div class="attn-pop-body"></div>
      </div>
      <button class="attn-warn" type="button" aria-label="Why is the page getting hard to read?" hidden>?</button>
      <section class="attn-panel" aria-label="Reading weave">
        <div class="attn-head">
          <span class="attn-title">Reading weave</span>
          <button class="attn-icon attn-help" type="button" aria-label="What is this?">${icon.help}</button>
          <button class="attn-icon attn-min" type="button" aria-label="Minimise">${icon.min}</button>
          <span class="attn-x-wrap">
            <button class="attn-icon attn-x" type="button" aria-labelledby="attn-x-tip">${icon.close}</button>
            <span class="attn-tip" id="attn-x-tip" role="tooltip">Stops the dynamic effects</span>
          </span>
        </div>
        <p class="attn-status" aria-live="polite"></p>
        <div class="attn-meter" aria-hidden="true"><span></span></div>
        <dl class="attn-stats">
          <div><dt>Read</dt><dd class="attn-read-n"></dd></div>
          <div><dt>Skipped</dt><dd class="attn-skip-n"></dd></div>
        </dl>
        <button class="attn-on" type="button" hidden>Turn the effects back on</button>
        <pre class="attn-debug" ${debug ? "" : "hidden"}></pre>
      </section>
      <button class="attn-dock" type="button" aria-label="Show the reading weave panel" hidden>
        <svg viewBox="0 0 32 32" aria-hidden="true"><use href="#weave-mark"/></svg>
      </button>`;
    document.body.append(root);
    const $ = (s) => root.querySelector(s);
    const panel = $(".attn-panel"), dock = $(".attn-dock"), warn = $(".attn-warn"), pop = $(".attn-pop"), popBody = $(".attn-pop-body");
    const xBtn = $(".attn-x");
    let minimised = store.get("weft-attn-min") === "1";
    let popKind = null, warnShown = false;

    const HELP = `
      <h2 id="attn-pop-title">The reading weave</h2>
      <p>This page notices how you read it. In Weft the warp is a set of checks that never loosens and the threads are what moves; here, you are the weaver.</p>
      <h3>How it works</h3>
      <p>Each passage needs a little time on screen, about as long as a quick reader would take. The page watches how you scroll and move the cursor. It is all measured in your browser, nothing is sent anywhere, and it is forgotten when you leave.</p>
      <h3>Rewarded</h3>
      <p>Reading at a steady pace. Each passage you read gets a thread woven beside it, and the page settles.</p>
      <h3>Punished</h3>
      <p>Skimming: scrolling past passages without reading them, scrolling fast, jumping around, and frantic cursor movement. The page grows restless: the text ripples, fades and blurs, and the links start to drift away from a hurried cursor.</p>
      <p class="attn-pop-foot">To calm it, slow down and read. To switch it off, press <span class="attn-kbd" aria-label="the close button">×</span> on this panel.</p>`;
    const WARN = `
      <h2 id="attn-pop-title">Why is the page getting hard to read?</h2>
      <p>It looks like you are skimming: passages are going past faster than they can be read. This page is built to resist that, so the more you rush, the more the text ripples, fades and blurs, and the more the links drift.</p>
      <p>Slow down and read a passage or two, and it will settle.</p>
      <p class="attn-pop-foot">Or stop the effects altogether with the <span class="attn-kbd" aria-label="close button">×</span> on the reading panel.</p>`;

    const openPop = (kind) => {
      if (popKind === kind) return closePop();
      popKind = kind;
      popBody.innerHTML = kind === "help" ? HELP : WARN;
      pop.hidden = false;
      root.classList.toggle("attn-point-x", kind === "warn");
      if (kind === "warn" && minimised) setMin(false);
      $(".attn-pop-close").focus({ preventScroll: true });
    };
    const closePop = () => {
      popKind = null;
      pop.hidden = true;
      root.classList.remove("attn-point-x");
    };
    const setMin = (m) => {
      minimised = m;
      store.set("weft-attn-min", m ? "1" : null);
      panel.hidden = m;
      dock.hidden = !m;
      if (m && popKind === "help") closePop();
    };
    const setOff = (o) => {
      off = o;
      store.set("weft-attn-off", o ? "1" : null);
      document.documentElement.classList.toggle("attn-off", o);
      $(".attn-on").hidden = !o;
      xBtn.hidden = o;
      if (o) {
        restless = 0;
        attention.restless = 0;
        waves.length = 0;
        still();
        closePop();
      }
      update();
    };

    $(".attn-help").addEventListener("click", () => openPop("help"));
    $(".attn-min").addEventListener("click", () => setMin(true));
    dock.addEventListener("click", () => { setMin(false); $(".attn-min").focus({ preventScroll: true }); });
    xBtn.addEventListener("click", () => { setOff(true); setMin(true); dock.focus({ preventScroll: true }); });
    $(".attn-on").addEventListener("click", () => setOff(false));
    warn.addEventListener("click", () => openPop("warn"));
    $(".attn-pop-close").addEventListener("click", closePop);
    addEventListener("keydown", (ev) => { if (ev.key === "Escape" && popKind) closePop(); });

    const status = $(".attn-status"), fill = $(".attn-meter span"), readN = $(".attn-read-n"), skipN = $(".attn-skip-n"), dbg = $(".attn-debug");
    let lastStatus = "";
    function update() {
      const read = blocks.filter((b) => b.read).length;
      let s;
      if (off) s = "Effects are off. The page stays still.";
      else if (restless > 0.6) s = "Rushing. The page is pushing back.";
      else if (restless > 0.3) s = "Skimming detected.";
      else if (attention.reading) s = "Reading steadily.";
      else s = "Calm.";
      if (s !== lastStatus) { status.textContent = s; lastStatus = s; }
      fill.style.transform = `scaleX(${off ? 0 : restless.toFixed(3)})`;
      root.style.setProperty("--attn-level", off ? 0 : restless.toFixed(3));
      readN.textContent = `${read} of ${blocks.length} passages`;
      skipN.textContent = `${stats.skippedWords} words`;
      // The warning appears once the effects start to get in the way, with some hysteresis.
      const want = !off && (warnShown ? restless > 0.25 : restless > 0.4);
      if (want !== warnShown) {
        warnShown = want;
        warn.hidden = !want;
        if (!want && popKind === "warn") closePop();
      }
      if (debug) {
        dbg.textContent = [
          `restless ${restless.toFixed(2)}${pinned !== null ? " (pinned)" : ""}`,
          `scroll   ${Math.round(scroll.v)} px/s`,
          `cursor   speed ${cur.speed.toFixed(2)} jolt ${cur.jolt.toFixed(2)}`,
          `words    read ${stats.readWords}, skipped ${stats.skippedWords}`,
          `jumps ${stats.jumps}, flips ${stats.flips}, waves ${waves.length}`,
        ].join("\n");
      }
    }
    setMin(minimised);
    setOff(off);
    return { update };
  })();

  /* ---------- The loop ---------- */
  let last = 0;
  function frame(t) {
    const dt = last ? Math.min(0.05, (t - last) / 1000) : 0;
    last = t;
    if (dt) step(dt, t);
    requestAnimationFrame(frame);
  }

  function step(dt) {
    if (off) return;
    const now = performance.now();
    scroll.v *= Math.exp(-dt / 0.15);
    if (now - scroll.t > 120) scroll.v *= Math.exp(-dt / 0.05);
    cur.speed *= Math.exp(-dt / 0.3);
    cur.jolt *= Math.exp(-dt / 0.3);
    cur.still += dt;
    scroll.flips = scroll.flips.filter((f) => now - f < 2000);

    // Reading: credit time to the first unread block on screen, top-down, while the page is steady.
    const steady = scroll.v < 350 && cur.jolt < 0.3;
    let current = null;
    for (const b of blocks) {
      if (b.visible && !b.read) { current = b; break; }
    }
    attention.reading = !!current && steady;
    if (attention.reading) {
      current.dwell += dt;
      if (current.dwell >= current.need) {
        current.read = true;
        current.el.classList.add("attn-read");
        stats.readWords += current.words;
        if (pinned === null) restless = clamp01(restless - 0.06 - current.words / 1500);
      }
    }
    // Skipping: a block that was seen and has now left the top of the screen without being read.
    for (const b of blocks) {
      if (b.read || b.skipped || !b.seen || b.visible) continue;
      if (b.el.getBoundingClientRect().bottom < 0 && b.dwell < b.need * 0.35) {
        b.skipped = true;
        stats.skippedWords += b.words;
        bump(Math.min(0.2, 0.03 + b.words / 500) * (b.again ? 0.6 : 1));
      }
    }
    // Fast scrolling, frantic direction changes and a jerky cursor.
    bump(dt * 0.14 * smooth(500, 2600, scroll.v));
    if (scroll.flips.length >= 3 && now - scroll.t < 300) bump(dt * 0.2); // only while it is happening
    bump(dt * 0.06 * cur.jolt);
    // Recovery: mostly by reading.
    if (pinned === null) restless = clamp01(restless - dt * (attention.reading ? 0.05 : 0.006));
    attention.restless = restless;
    ui.update();

    if (!motion || reducedMotion.matches) return;
    const r = restless;
    clock += dt * (0.6 + 0.8 * r);
    churn = 0.9 * smooth(0.22, 1, r);

    // Waves: sources across the visible page, plus wakes from a hurried cursor.
    seedDebt += dt * (0.1 + 1.6 * r) * (r > 0.08 ? 1 : 0);
    while (seedDebt >= 1) {
      seedDebt -= 1;
      launch(scrollX + Math.random() * innerWidth, scrollY + Math.random() * innerHeight, 0.5 + 0.5 * r, r);
    }
    if (r > 0.25 && cur.x > -1000 && Math.random() < dt * 6 * cur.speed) launch(cur.x + scrollX, cur.y + scrollY, 0.7, r);
    for (let n = waves.length - 1; n >= 0; n--) {
      const v = waves[n];
      v.age += dt;
      v.r0 += v.c * dt;
      v.fade = Math.min(1, v.age * 2) * Math.max(0, 1 - v.age / v.life) / Math.sqrt(1 + v.r0 / 300);
      if (v.age > v.life) waves.splice(n, 1);
    }

    if (r > 0.12 && !split) splitWords();
    if (split) moveWords(r);
    moveNavs(r, dt);
    drawOverlay(r);
  }

  function moveWords(r) {
    const amp = 7 * smooth(0.12, 1, r);
    const tilt = 5 * smooth(0.45, 1, r);
    const dim = 0.6 * smooth(0.4, 1, r);
    const blur = 1.4 * smooth(0.65, 1, r);
    document.documentElement.style.setProperty("--attn-blur", `${blur.toFixed(2)}px`);
    document.documentElement.classList.toggle("attn-blurry", blur > 0.02);
    const top = scrollY - 80, bottom = scrollY + innerHeight + 80;
    const active = amp > 0.05;
    for (const w of words) {
      if (w.y < top || w.y > bottom || !w.block.visible) continue;
      if (!active) {
        if (w.moved) { w.el.style.transform = ""; w.el.style.opacity = ""; w.moved = false; }
        continue;
      }
      const f = field(w.x, w.y);
      w.el.style.transform = `translate3d(0, ${(f * amp).toFixed(2)}px, 0) rotate(${(f * tilt).toFixed(2)}deg)`;
      w.el.style.opacity = (1 - dim * Math.max(0, -f)).toFixed(3);
      w.moved = true;
    }
  }

  function moveNavs(r, dt) {
    const drift = 14 * smooth(0.5, 1, r);
    const evade = 26 * smooth(0.75, 1, r);
    for (const n of navs) {
      if (n.el === document.activeElement && n.el.matches(":focus-visible")) {
        n.el.style.transform = "";
        continue; // keyboard users are never chased
      }
      let tx = 0, ty = 0;
      if (drift > 0.1) {
        const x = n.fixed ? n.x + scrollX : n.x, y = n.fixed ? n.y + scrollY : n.y;
        tx = field(x, y - 20) * drift;
        ty = field(x + 20, y) * drift;
        // A hurried cursor pushes links away; one held still lets them settle.
        const sx = n.fixed ? n.x : n.x - scrollX, sy = n.fixed ? n.y : n.y - scrollY;
        const dx = sx - cur.x, dy = sy - cur.y, d = Math.hypot(dx, dy);
        const patience = smooth(0.25, 0.9, cur.still);
        if (evade > 0.1 && d < 110 && d > 0.1) {
          const push = evade * (1 - d / 110) * (1 - patience) * (0.4 + cur.speed);
          tx += (dx / d) * push;
          ty += (dy / d) * push;
        }
        tx *= 1 - patience * 0.85;
        ty *= 1 - patience * 0.85;
      }
      const k = 1 - Math.exp(-dt / 0.12);
      n.ox += (tx - n.ox) * k;
      n.oy += (ty - n.oy) * k;
      n.el.style.transform = Math.abs(n.ox) + Math.abs(n.oy) > 0.05 ? `translate(${n.ox.toFixed(1)}px, ${n.oy.toFixed(1)}px)` : "";
    }
  }

  function drawOverlay(r) {
    const vis = smooth(0.35, 1, r);
    if (vis <= 0.01) {
      if (overlayOn) { octx.clearRect(0, 0, overlay.width, overlay.height); overlayOn = false; }
      return;
    }
    overlayOn = true;
    octx.setTransform(odpr, 0, 0, odpr, 0, 0);
    octx.clearRect(0, 0, ow, oh);
    const rgb = getComputedStyle(document.documentElement).getPropertyValue("--attn-wave").trim() || "217, 199, 160";
    for (const v of waves) {
      const cx = v.x - scrollX, cy = v.y - scrollY;
      // Draw each crest as a ring; the packet's envelope sets its strength.
      for (let u = v.lambda * 0.25; u < v.len; u += v.lambda) {
        const rad = v.r0 - u;
        if (rad <= 0) continue;
        const a = v.amp * v.fade * Math.sin((Math.PI * u) / v.len) * vis * 0.09;
        if (a < 0.004) continue;
        octx.strokeStyle = `rgba(${rgb}, ${a})`;
        octx.lineWidth = v.lambda * 0.22;
        octx.beginPath();
        octx.arc(cx, cy, rad, 0, Math.PI * 2);
        octx.stroke();
      }
    }
  }

  // Put everything back at rest: used when the effects are switched off, and under reduced motion.
  function still() {
    words.forEach((w) => { w.el.style.transform = ""; w.el.style.opacity = ""; w.moved = false; });
    navs.forEach((n) => { n.el.style.transform = ""; n.ox = n.oy = 0; });
    octx.clearRect(0, 0, overlay.width, overlay.height);
    overlayOn = false;
    document.documentElement.classList.remove("attn-blurry");
  }
  // Keep the woven threads, but skip all motion under reduced motion.
  reducedMotion.addEventListener("change", () => { if (reducedMotion.matches) still(); });
  requestAnimationFrame(frame);

  return {
    blocks: blocks.map((b) => b.el),
    stats,
    // Settle the score (never raise it), e.g. when the visitor undoes what the score has done.
    calm(to = 0) {
      if (pinned === null) restless = attention.restless = Math.min(restless, clamp01(to));
    },
    // A block's text changed: re-count its words so the time it needs stays fair.
    recount(el) {
      const b = byEl.get(el);
      if (!b) return;
      b.words = (el.textContent.match(/\S+/g) || []).length;
      b.need = Math.max(1.2, b.words / READ_WPS);
    },
  };
}

// Module scripts run in one go, so a page that imports this can hold it before it starts.
queueMicrotask(() => { if (!held) setupAttention(); });
