// w3ft.org page script: theme toggle, hero loom, and the three live demos.
// Every demo imports a tested module from this repository; nothing is mocked.
import { frobeniusNorm, verifyWeightUpdateSafety } from "./invariant-gate.js";
import { parseSym2pLine, verifySym2pLine } from "./sym2p-parse.js";
import { mountSimplexPad } from "./simplex-pad.js";
import { mixAestheticPresets } from "./aesthetic-mixer.js";
import { attention } from "./attention.js"; // starts the reading weave on this page too

const $ = (sel, root = document) => root.querySelector(sel);
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const cssVar = (name, el = document.documentElement) => getComputedStyle(el).getPropertyValue(name).trim();
const themeListeners = [];

/* ---------- Theme ---------- */
function setupTheme() {
  const btn = $(".theme-toggle");
  if (!btn) return;
  // Navy (dark) is the brand default; the reader can switch to the light theme.
  const effective = () => (document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark");
  const sync = () => btn.setAttribute("aria-pressed", String(effective() === "dark"));
  btn.addEventListener("click", () => {
    const next = effective() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("weft-theme", next); } catch { /* not persisted */ }
    sync();
    themeListeners.forEach((fn) => fn());
  });
  sync();
}

/* ---------- Mobile menu: close after choosing a link ---------- */
function setupMenu() {
  const menu = $(".menu");
  if (!menu) return;
  menu.addEventListener("click", (ev) => {
    if (ev.target.closest("a")) menu.open = false;
  });
  document.addEventListener("click", (ev) => {
    if (menu.open && !menu.contains(ev.target)) menu.open = false;
  });
}

/* ---------- Hero loom ----------
   Warp threads run vertically; weft threads pass over and under them in a
   plain weave. The pointer acts as a shuttle, pushing nearby weft aside. */
function setupLoom() {
  const canvas = $("#loom");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  let w = 0, h = 0, dpr = 1, spacing = 28, running = false, visible = true, raf = 0;
  let colors = {};
  const pointer = { x: -1e4, y: -1e4, tx: -1e4, ty: -1e4 };

  // The hero is always navy (.navy-scope), so read tokens from the canvas, not the root.
  const readColors = () => {
    colors = {
      bg: cssVar("--bg", canvas),
      warp: cssVar("--thread-warp", canvas),
      weft: cssVar("--thread-weft", canvas),
      gold: cssVar("--thread-gold", canvas),
    };
    metallic();
  };
  // Liquid-metal strokes: the colour varies along each thread, never on text.
  const metallic = () => {
    if (!w) return;
    const sheen = (stops) => {
      const g = ctx.createLinearGradient(0, 0, w, h * 0.35);
      stops.forEach(([o, c]) => g.addColorStop(o, c));
      return g;
    };
    colors.a = sheen([[0, "#487775"], [0.18, "#b0d5d2"], [0.36, "#5a9892"], [0.55, "#d7ebea"], [0.74, "#306d68"], [1, "#8abeb8"]]);
    colors.s = sheen([[0, "#7d8a90"], [0.2, "#e8eef0"], [0.4, "#a9b6bb"], [0.6, "#f5f8f9"], [0.8, "#97a4a9"], [1, "#d3dcdf"]]);
    colors.b = sheen([[0, "#bfa97c"], [0.25, "#efe3c8"], [0.45, "#d9c7a0"], [0.62, "#f7efdc"], [0.82, "#bfa97c"], [1, "#e6d6b0"]]);
  };

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = rect.width;
    h = rect.height;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    spacing = Math.max(20, Math.min(34, w / 34));
    metallic();
    draw(performance.now());
  };

  const weftY = (j, x, t) => {
    const base = j * spacing + spacing / 2;
    let y = base + Math.sin(x * 0.011 + t * 0.00055 + j * 0.7) * spacing * 0.16;
    const dx = x - pointer.x, dy = base - pointer.y;
    const d2 = dx * dx + dy * dy;
    if (d2 < 40000) y += Math.sign(dy || 1) * 26 * Math.exp(-d2 / (2 * 70 * 70));
    return y + ripple(x, base);
  };

  function draw(t) {
    if (!w || !h) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const lw = spacing * 0.3;
    const halo = lw + 3;
    const cols = Math.ceil(w / spacing) + 1;
    const rows = Math.ceil(h / spacing) + 1;
    const step = spacing / 4;
    ctx.lineCap = "butt";

    // Warp: straight vertical threads.
    ctx.strokeStyle = colors.warp;
    ctx.lineWidth = lw;
    ctx.beginPath();
    for (let i = 0; i < cols; i++) {
      const x = i * spacing + spacing / 2;
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
    }
    ctx.stroke();

    // Weft: wavy horizontal threads with a background halo so crossings read as depth.
    for (let j = 0; j < rows; j++) {
      const color = j % 7 === 3 ? colors.b : (j % 7 === 1 || j % 7 === 5) ? colors.s : colors.a; // champagne + silver, sparingly
      for (const pass of [0, 1]) {
        ctx.beginPath();
        for (let x = 0; x <= w + step; x += step) {
          const y = weftY(j, x, t);
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = pass === 0 ? colors.bg : color;
        ctx.lineWidth = pass === 0 ? halo : lw;
        ctx.globalAlpha = pass === 0 ? 1 : 0.9;
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;

    // Where the warp passes over, redraw a short warp piece on top.
    for (let j = 0; j < rows; j++) {
      for (let i = 0; i < cols; i++) {
        if ((i + j) % 2 === 0) continue;
        const x = i * spacing + spacing / 2;
        const y = weftY(j, x, t);
        const half = lw * 0.9;
        ctx.strokeStyle = colors.bg;
        ctx.lineWidth = halo;
        ctx.beginPath();
        ctx.moveTo(x, y - half);
        ctx.lineTo(x, y + half);
        ctx.stroke();
        ctx.strokeStyle = colors.warp;
        ctx.lineWidth = lw;
        ctx.beginPath();
        ctx.moveTo(x, y - half - 1.5);
        ctx.lineTo(x, y + half + 1.5);
        ctx.stroke();
      }
    }

    drawWaves(t, lw, halo);
  }

  /* ---------- Living weave ----------
     The cloth is a medium. Waves pass through it: rings of oscillation spread
     from sources and fade as they spread. Where a crest passes, the threads
     catch the light and the weft ripples a few pixels. The warp never moves:
     it is the fixed set of checks, and the weft is what changes, within a
     small, fixed amplitude. A slow breath swells through the cloth.

     The weave takes its mood from the visitor. Calm, smooth movement makes
     long, slow, cool swells, and the cursor leaves a wake along its heading.
     Fast, jerky movement makes short, quick, choppy, warmer waves scattered
     in every direction. A click drops a stone in the pond. The mood rises
     quickly and settles slowly, like breath after exertion. */
  const waves = [];
  let lastT = 0, seedDebt = 0, wakeDebt = 0, breathPhase = 0, swellPhase = 0;
  const CALM = [214, 236, 234]; // marble teal sheen
  const HOT = [255, 212, 156]; // champagne heat when agitated
  const mix = (a, b, k) => `${Math.round(a[0] + (b[0] - a[0]) * k)}, ${Math.round(a[1] + (b[1] - a[1]) * k)}, ${Math.round(a[2] + (b[2] - a[2]) * k)}`;
  const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

  /* Visitor mood, from how the cursor moves:
       speed  how fast the pointer travels
       turn   how fast it changes heading (angular velocity)
       jolt   how fast that turning changes (angular acceleration): frantic zig-zags score high,
              a smooth sweep or a steady curve scores low
     Plus: scrolling stirs the cloth a little, a click drops a stone, and stillness deepens the rest. */
  const gesture = { x: 0, y: 0, t: 0, heading: 0, omega: 0, has: false };
  const raw = { speed: 0, turn: 0, jolt: 0 }; // latest readings; they fade while the pointer rests
  const mood = { speed: 0, turn: 0, jolt: 0, idle: 0, heading: 0 };
  const readGesture = (x, y, ts) => {
    if (!gesture.has || ts - gesture.t > 250) {
      Object.assign(gesture, { x, y, t: ts, omega: 0, has: true });
      return;
    }
    const dx = x - gesture.x, dy = y - gesture.y, dist = Math.hypot(dx, dy);
    if (dist < 10) return; // heading is noise over tiny steps
    const dt = Math.max(0.008, (ts - gesture.t) / 1000);
    const v = dist / dt;
    const heading = Math.atan2(dy, dx);
    const dTheta = Math.atan2(Math.sin(heading - gesture.heading), Math.cos(heading - gesture.heading));
    const omega = gesture.omega * 0.5 + (dTheta / dt) * 0.5; // rad/s, lightly smoothed
    const alpha = Math.abs(omega - gesture.omega) / dt; // rad/s²
    Object.assign(gesture, { x, y, t: ts, heading, omega });
    const moving = clamp01(v / 350); // turning only counts while the cursor really moves
    raw.speed = Math.max(raw.speed, clamp01(v / 1800));
    raw.turn = Math.max(raw.turn, clamp01(Math.abs(omega) / 14) * moving);
    raw.jolt = Math.max(raw.jolt, clamp01(alpha / 1400) * moving);
    mood.heading = heading;
    mood.idle = 0;
  };
  const settleMood = (dt) => {
    const fade = Math.exp(-dt / 0.12);
    for (const k of ["speed", "turn", "jolt"]) {
      raw[k] *= fade;
      const rate = raw[k] > mood[k] ? 1 - Math.exp(-dt / 0.18) : 1 - Math.exp(-dt / 2.4);
      mood[k] += (raw[k] - mood[k]) * rate;
    }
    mood.idle += dt;
  };
  // Derived feelings, 0..1.
  // A restless reader (see attention.js) agitates the loom too.
  const arousal = () => Math.max(mood.speed, mood.turn * 0.8, mood.jolt, attention.restless);
  const agitation = () => Math.max(clamp01(mood.jolt * 1.1 + mood.turn * 0.35), attention.restless * 0.9);
  const rest = () => clamp01((mood.idle - 4) / 8);

  const center = (k) => k * spacing + spacing / 2;
  const budget = () => Math.round(7 + 9 * arousal());
  // On wide screens the CSS mask hides the left ~40% of the loom; start waves where they can be seen.
  const visibleX = () => (w > 700 ? w * 0.42 : 0);

  // A wave packet: a ring (or, with `heading`, a forward lobe) whose crest band travels outwards.
  const launch = (x, y, { amp = 0.6, heading = null, force = false } = {}) => {
    if (!force && waves.length >= budget()) return;
    const g = agitation(), a = arousal();
    const lambda = 110 - 62 * g + Math.random() * 20; // calm: long swells; agitated: short chop
    waves.push({
      x, y, heading, amp,
      r: 0,
      c: 55 + 90 * a + 110 * g + Math.random() * 15, // px per second
      lambda,
      len: lambda * (1.6 + Math.random() * 0.8), // how many crests the packet carries
      phase: Math.random() * Math.PI * 2,
      fade: 0,
      age: 0,
      life: 4 + Math.random() * 3 - 2 * g,
    });
  };
  // Displacement field of all waves at (x, y): roughly -1..1.
  const field = (x, y) => {
    let f = 0;
    for (let n = 0; n < waves.length; n++) {
      const v = waves[n];
      const dx = x - v.x, dy = y - v.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      const u = v.r - d; // distance behind the wavefront
      if (u < 0 || u > v.len) continue;
      let k = v.amp * Math.sin((Math.PI * u) / v.len) * v.fade; // smooth envelope over the packet
      if (v.heading !== null && d > 1) {
        const c = (dx * Math.cos(v.heading) + dy * Math.sin(v.heading)) / d;
        k *= ((1 + c) / 2) ** 3; // a wake: mostly ahead of the cursor
      }
      f += k * Math.cos((2 * Math.PI * u) / v.lambda + v.phase);
    }
    return f;
  };
  // The breath: a very slow, faint swell drifting diagonally through the cloth.
  const swell = (x, y) => Math.max(0, Math.sin(x * 0.0082 + y * 0.011 - swellPhase)) ** 6;

  // A click drops a stone: a strong ring from that point.
  const drop = (x, y) => {
    if (!w) return;
    launch(x, y, { amp: 1, force: true });
    raw.speed = Math.max(raw.speed, 0.3);
  };

  const stepWaves = (dt) => {
    if (!w || !h || !dt) return;
    settleMood(dt);
    const a = arousal(), g = agitation(), r = rest();

    // Breath: a ~12 s cycle at rest that quickens with arousal and slows when the visitor is still.
    breathPhase += dt * 0.52 * (1 + 1.3 * a) * (1 - 0.4 * r);
    swellPhase += dt * 0.5 * (1 + 1.5 * a) * (1 - 0.4 * r);
    const breath = 0.5 + 0.5 * Math.sin(breathPhase);
    seedDebt += dt * (0.12 + 0.4 * breath) * (1 + 2.5 * a) * (1 - 0.5 * r);
    while (seedDebt >= 1) {
      seedDebt -= 1;
      const x0 = visibleX();
      launch(x0 + Math.random() * (w - x0), Math.random() * h, { amp: 0.35 + 0.35 * Math.random() + 0.3 * g });
    }

    // The cursor's wake: smooth movement sends a lobe ahead along its heading; frantic movement scatters rings.
    if (pointer.x > -1000) {
      wakeDebt += dt * 5 * mood.speed;
      while (wakeDebt >= 1) {
        wakeDebt -= 1;
        const jitter = 12 * g;
        launch(pointer.x + (Math.random() - 0.5) * jitter, pointer.y + (Math.random() - 0.5) * jitter, {
          amp: 0.45 + 0.4 * mood.speed,
          heading: g < 0.4 ? mood.heading : null,
        });
      }
    }

    const reach = Math.hypot(w, h);
    for (let n = waves.length - 1; n >= 0; n--) {
      const v = waves[n];
      v.age += dt;
      v.r += v.c * dt * (1 - 0.3 * r);
      // Fade with age and as the ring spreads its energy over a longer circumference.
      v.fade = Math.min(1, v.age * 3) * Math.max(0, 1 - v.age / v.life) / Math.sqrt(1 + v.r / 160);
      if (v.age > v.life || v.r - v.len > reach) waves.splice(n, 1);
    }
  };
  // How far the weft is pushed by the waves at (x, y): a few px at most.
  const ripple = (x, y) => (waves.length ? field(x, y) * spacing * 0.11 : 0);

  // Light on the threads where crests pass. Drawn last, trimmed so it never lies on a thread
  // that is under the other one at a crossing.
  function drawWaves(t, lw, halo) {
    const a = arousal(), g = agitation();
    const cols = Math.ceil(w / spacing) + 1, rows = Math.ceil(h / spacing) + 1;
    const trim = halo * 0.55;
    const gain = 0.5 * (0.8 + 0.8 * a);
    const rgb = mix(CALM, HOT, g * 0.85);
    const x0 = visibleX() - spacing * 2;
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    ctx.lineCap = "round";
    ctx.lineWidth = lw * 0.5;
    const light = (x, y) => clamp01(Math.max(0, field(x, y)) * gain + swell(x, y) * 0.07);
    // Weft segments between crossings.
    for (let j = 0; j < rows; j++) {
      for (let i = 0; i < cols - 1; i++) {
        const xa = center(i), xb = center(i + 1);
        if (xb < x0) continue;
        const xm = (xa + xb) / 2;
        const b = light(xm, j * spacing + spacing / 2);
        if (b < 0.015) continue;
        const s = xa + ((i + j) % 2 === 1 ? trim : 0); // warp lies on top at an odd crossing
        const e = xb - ((i + 1 + j) % 2 === 1 ? trim : 0);
        ctx.strokeStyle = `rgba(${rgb}, ${b})`;
        ctx.beginPath();
        ctx.moveTo(s, weftY(j, s, t));
        ctx.lineTo(xm, weftY(j, xm, t));
        ctx.lineTo(e, weftY(j, e, t));
        ctx.stroke();
      }
    }
    // Warp segments between rows (the warp lights up but never moves).
    for (let i = 0; i < cols; i++) {
      const x = center(i);
      if (x < x0) continue;
      for (let j = 0; j < rows - 1; j++) {
        const ya = weftY(j, x, t), yb = weftY(j + 1, x, t);
        const b = light(x, (ya + yb) / 2) * 0.8;
        if (b < 0.015) continue;
        const s = ya + ((i + j) % 2 === 0 ? trim : 0); // weft lies on top at an even crossing
        const e = yb - ((i + j + 1) % 2 === 0 ? trim : 0);
        ctx.strokeStyle = `rgba(${rgb}, ${b})`;
        ctx.beginPath();
        ctx.moveTo(x, s);
        ctx.lineTo(x, e);
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  const frame = (t) => {
    pointer.x += (pointer.tx - pointer.x) * 0.12;
    pointer.y += (pointer.ty - pointer.y) * 0.12;
    stepWaves(lastT ? Math.min(0.05, (t - lastT) / 1000) : 0);
    lastT = t;
    draw(t);
    raf = running ? requestAnimationFrame(frame) : 0;
  };
  const start = () => {
    if (running || reducedMotion.matches || !visible || document.hidden) return;
    running = true;
    raf = requestAnimationFrame(frame);
  };
  const stop = () => {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    lastT = 0;
    if (reducedMotion.matches) waves.length = 0;
  };

  readColors();
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    visible ? start() : stop();
  }).observe(canvas);
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
  reducedMotion.addEventListener("change", () => (reducedMotion.matches ? (stop(), draw(0)) : start()));
  const hero = canvas.parentElement;
  hero.addEventListener("pointermove", (ev) => {
    const r = canvas.getBoundingClientRect();
    pointer.tx = ev.clientX - r.left;
    pointer.ty = ev.clientY - r.top;
    if (pointer.x < -1000) { pointer.x = pointer.tx; pointer.y = pointer.ty; }
    const samples = ev.getCoalescedEvents ? ev.getCoalescedEvents() : [];
    for (const e of samples.length ? samples : [ev]) readGesture(e.clientX - r.left, e.clientY - r.top, e.timeStamp);
  });
  hero.addEventListener("pointerleave", () => { pointer.tx = pointer.ty = -1e4; gesture.has = false; });
  hero.addEventListener("pointerdown", (ev) => {
    const r = canvas.getBoundingClientRect();
    drop(ev.clientX - r.left, ev.clientY - r.top);
  });
  // Scrolling stirs the cloth a little.
  let lastScroll = { y: window.scrollY, t: performance.now() };
  window.addEventListener("scroll", () => {
    const now = performance.now(), dt = Math.max(16, now - lastScroll.t) / 1000;
    raw.speed = Math.max(raw.speed, Math.min(0.5, Math.abs(window.scrollY - lastScroll.y) / dt / 4000));
    mood.idle = 0;
    lastScroll = { y: window.scrollY, t: now };
  }, { passive: true });
  themeListeners.push(() => { readColors(); draw(performance.now()); });
  start();
  // Deterministic redraw at a fixed time (used by loom visual-regression checks only).
  window.__loomSnapshot = (t) => {
    waves.length = 0;
    for (const k of ["speed", "turn", "jolt"]) {
      raw[k] = 0;
      mood[k] = 0;
    }
    mood.idle = 0;
    Object.assign(pointer, { x: -1e4, y: -1e4, tx: -1e4, ty: -1e4 });
    gesture.has = false;
    attention.restless = 0;
    readColors();
    draw(t);
  };
}

/* ---------- Demo 1: the safety gate ---------- */
function setupGate() {
  const root = $("#gate");
  if (!root) return;
  const N = 12, SIZE = N * N, BUDGET = 10, COST = 1, METER_MAX = 8;

  // Deterministic baseline so every visitor sees the same starting matrix.
  let seed = 0x5eed;
  const rand = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const gauss = () => Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand());
  const baseline = Float64Array.from({ length: SIZE }, () => gauss() * 0.5);
  let weights = Float64Array.from(baseline);
  let budget = BUDGET;

  const canvas = $("#gateMatrix");
  const ctx = canvas.getContext("2d");
  const radiusInput = $("#gateRadius");
  const radiusOut = $("#gateRadiusOut");
  const distEl = $("#gateDist");
  const distFill = $("#gateDistFill");
  const radiusMark = $("#gateRadiusMark");
  const budgetEl = $("#gateBudget");
  const budgetFill = $("#gateBudgetFill");
  const weakEl = $("#verdictWeak");
  const gateEl = $("#verdictGate");
  const log = $("#gateLog");
  const radius = () => Number(radiusInput.value);

  const hexToRgb = (hex) => {
    const m = hex.replace("#", "");
    const v = m.length === 3 ? m.split("").map((c) => c + c).join("") : m;
    return [parseInt(v.slice(0, 2), 16), parseInt(v.slice(2, 4), 16), parseInt(v.slice(4, 6), 16)];
  };
  const paintMatrix = () => {
    const pos = hexToRgb(cssVar("--gold-flat"));
    const neg = hexToRgb(cssVar("--accent"));
    const mid = hexToRgb(cssVar("--surface"));
    const img = ctx.createImageData(N, N);
    for (let k = 0; k < SIZE; k++) {
      const d = Math.max(-1, Math.min(1, (weights[k] - baseline[k]) / 1.2));
      const tgt = d >= 0 ? pos : neg;
      const a = Math.abs(d);
      for (let c = 0; c < 3; c++) img.data[k * 4 + c] = Math.round(mid[c] + (tgt[c] - mid[c]) * a);
      img.data[k * 4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  };

  const setVerdict = (el, ok, text) => {
    el.classList.toggle("pass", ok);
    el.classList.toggle("fail", !ok);
    $(".result", el).textContent = text;
  };

  const showDistance = (d) => {
    const shown = Number.isFinite(d) ? d : 0;
    distEl.textContent = shown.toFixed(2);
    distFill.style.width = `${Math.min(shown / METER_MAX, 1) * 100}%`;
    distFill.classList.toggle("over", shown > radius());
  };
  const showRadius = () => {
    radiusOut.textContent = radius().toFixed(1);
    radiusMark.style.left = `calc(${(radius() / METER_MAX) * 100}% - 1px)`;
  };
  const showBudget = () => {
    budgetEl.textContent = `${budget} / ${BUDGET}`;
    budgetFill.style.width = `${(budget / BUDGET) * 100}%`;
  };

  const propose = (kind) => {
    let candidate;
    if (kind === "small") candidate = weights.map((v) => v + gauss() * 0.06);
    else if (kind === "large") candidate = weights.map((v) => v + gauss() * 0.35);
    else candidate = weights.map((v) => -v);

    const weakDelta = Math.abs(frobeniusNorm(candidate) - frobeniusNorm(baseline));
    const weakOk = weakDelta <= radius();
    setVerdict(weakEl, weakOk, `${weakOk ? "Accept" : "Reject"} · size change ${weakDelta.toFixed(2)}`);

    const res = verifyWeightUpdateSafety(baseline, candidate, radius(), budget, COST);
    const distText = Number.isFinite(res.distance) ? res.distance.toFixed(2) : "n/a";
    setVerdict(gateEl, res.accepted, `${res.accepted ? "Accept" : "Reject"} · ${res.reason.replaceAll("_", " ")}`);
    if (Number.isFinite(res.distance)) showDistance(res.distance);

    if (res.accepted) {
      weights = Float64Array.from(candidate);
      budget = res.remainingBudget;
      log.textContent = `Committed. Distance ${distText} ≤ R ${radius().toFixed(1)}; spent ${COST} budget.`;
    } else if (res.reason === "baseline_distance_exceeded") {
      log.textContent = weakOk
        ? `Rejected at distance ${distText}, although the size barely changed. This is the case the weak check misses.`
        : `Rejected: distance ${distText} is past R ${radius().toFixed(1)}. Nothing was committed and no budget was spent.`;
    } else {
      log.textContent = `Rejected: ${res.reason.replaceAll("_", " ")}. Press Reset to start over.`;
    }
    paintMatrix();
    showBudget();
  };

  const reset = () => {
    weights = Float64Array.from(baseline);
    budget = BUDGET;
    showDistance(0);
    showBudget();
    for (const el of [weakEl, gateEl]) {
      el.classList.remove("pass", "fail");
      $(".result", el).textContent = "Waiting for a proposal";
    }
    log.textContent = "Propose an update. Only proposals the gate accepts are committed.";
    paintMatrix();
  };

  root.addEventListener("click", (ev) => {
    const btn = ev.target.closest("[data-gate]");
    if (!btn) return;
    if (btn.dataset.gate === "reset") reset();
    else propose(btn.dataset.gate);
  });
  radiusInput.addEventListener("input", () => {
    showRadius();
    distFill.classList.toggle("over", Number(distEl.textContent) > radius());
  });
  themeListeners.push(paintMatrix);
  showRadius();
  reset();
}

/* ---------- Demo 2: SYM-2P packets ---------- */
function setupPackets() {
  const input = $("#packetInput");
  if (!input) return;
  const original = input.value;
  const badge = $("#packetBadge");
  const msg = $("#packetMsg");
  const fields = $("#packetFields");
  let ticket = 0;

  const row = (k, v) => {
    const dt = document.createElement("dt");
    dt.textContent = k;
    const dd = document.createElement("dd");
    dd.textContent = v;
    fields.append(dt, dd);
  };

  const check = async () => {
    const mine = ++ticket;
    const line = input.value;
    let ok = false;
    try { ok = await verifySym2pLine(line); } catch { ok = false; }
    if (mine !== ticket) return;
    fields.replaceChildren();
    badge.className = `badge ${ok ? "ok" : "bad"}`;
    badge.textContent = ok ? "verified" : "rejected";
    msg.textContent = ok ? "SHA-256 of the payload matches." : "Hash does not match the payload, or the line is malformed.";
    try {
      const p = parseSym2pLine(line);
      const hex = (n) => (Number.isFinite(n) ? `0x${n.toString(16).padStart(2, "0")}` : "?");
      row("role", hex(p.role));
      row("action/state", hex(p.actionState));
      row("sequence", Number.isFinite(p.sequence) ? String(p.sequence) : "?");
      for (const [k, v] of Object.entries(p.metrics)) row(k, String(v));
    } catch (err) {
      row("parse", err.message);
    }
    row("bytes", String(new TextEncoder().encode(line.trim()).length));
  };

  input.addEventListener("input", check);
  $("#packetTamper").addEventListener("click", () => {
    input.value = input.value.replace(/\(active_nodes (\d+)\)/, (_, n) => `(active_nodes ${Number(n) + 1})`);
    check();
  });
  $("#packetReset").addEventListener("click", () => {
    input.value = original;
    check();
  });
  check();
}

/* ---------- Demo 3: aesthetic simplex ---------- */
function setupMixer() {
  const mount = $("#simplexMount");
  if (!mount) return;
  // Presets as shipped in AestheticMixer (aesthetic-mixer.js).
  const presets = {
    native: { rounding: 0.85, density: 0.3, hue: 0.12, contrast: 0.05 },
    terminal: { rounding: 0.0, density: 0.1, hue: 0.45, contrast: 0.01 },
    pastel: { rounding: 1.0, density: 0.85, hue: 0.85, contrast: 0.2 },
  };
  const names = Object.keys(presets);
  const preview = $("#preview");
  const readout = $("#mixReadout");

  const apply = (w) => {
    const weights = Object.fromEntries(names.map((n, i) => [n, w[i]]));
    const v = mixAestheticPresets(presets, weights);
    preview.style.setProperty("--p-hue", (v.hue * 360).toFixed(1));
    preview.style.setProperty("--p-round", `${(v.rounding * 22).toFixed(1)}px`);
    preview.style.setProperty("--p-pad", `${(10 + v.density * 22).toFixed(1)}px`);
    preview.style.setProperty("--p-contrast", (v.contrast * 0.6).toFixed(3));
    readout.textContent =
      `weights ${w.map((x) => x.toFixed(2)).join(" / ")} → ` +
      `hue ${v.hue.toFixed(3)} · rounding ${v.rounding.toFixed(2)} · density ${v.density.toFixed(2)} · contrast ${v.contrast.toFixed(2)}`;
  };

  const start = [0.5, 0.15, 0.35];
  mountSimplexPad(mount, {
    labels: names,
    weights: start,
    hues: names.map((n) => presets[n].hue),
    onChange: apply,
  });
  apply(start);
}

/* ---------- Copy buttons ---------- */
function setupCopy() {
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const target = $(btn.dataset.copy);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent);
        btn.textContent = "Copied";
      } catch {
        btn.textContent = "Select and copy";
      }
      setTimeout(() => (btn.textContent = "Copy"), 1800);
    });
  });
}

setupTheme();
setupMenu();
setupLoom();
setupGate();
setupPackets();
setupMixer();
setupCopy();
