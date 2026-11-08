// w3ft.org page script: theme toggle, hero loom, and the three live demos.
// Every demo imports a tested module from this repository; nothing is mocked.
import { frobeniusNorm, verifyWeightUpdateSafety } from "./invariant-gate.js";
import { parseSym2pLine, verifySym2pLine } from "./sym2p-parse.js";
import { mountSimplexPad } from "./simplex-pad.js";
import { mixAestheticPresets } from "./aesthetic-mixer.js";

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
  // Brushed-metal strokes: the colour varies along each thread, never on text.
  const metallic = () => {
    if (!w) return;
    const sheen = (stops) => {
      const g = ctx.createLinearGradient(0, 0, w, h * 0.35);
      stops.forEach(([o, c]) => g.addColorStop(o, c));
      return g;
    };
    colors.a = sheen([[0, "#7f8ba0"], [0.18, "#dfe5ee"], [0.36, "#9aa6b9"], [0.55, "#f4f7fb"], [0.74, "#8d99ad"], [1, "#d3dae5"]]);
    colors.b = sheen([[0, "#b8862b"], [0.25, "#f6dc85"], [0.45, "#d4af37"], [0.62, "#fff1b8"], [0.82, "#b8862b"], [1, "#e8c45a"]]);
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
    return y;
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
      const color = j % 7 === 3 ? colors.b : colors.a; // gold, sparingly
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
  }

  const frame = (t) => {
    pointer.x += (pointer.tx - pointer.x) * 0.12;
    pointer.y += (pointer.ty - pointer.y) * 0.12;
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
  });
  hero.addEventListener("pointerleave", () => { pointer.tx = pointer.ty = -1e4; });
  themeListeners.push(() => { readColors(); draw(performance.now()); });
  start();
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
