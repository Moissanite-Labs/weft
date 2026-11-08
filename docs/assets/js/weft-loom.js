import { AestheticMixer } from "./aesthetic-mixer.js";
import { hitTest, layerThreads, layoutCells } from "./cell-layout.js";
import { GLYPH_ADVANCE, encodeFontTable, glyphBit, packLabel } from "./glyph-font.js";
import { parseSym2pLine, verifySym2pLine } from "./sym2p-parse.js";

const MAX_CELLS = 32;
const MAX_THREADS = 32;
const CELL_FLOATS = 16; // 64 bytes per cell record (see `struct Cell` in the shader)
const THREAD_FLOATS = 8; // 32 bytes per thread record

/** Layers in fixture order; a layer's hue is the simplex hue rotated by k/5 of the circle. */
export const LAYERS = ["governance", "interface", "substrate", "cognition", "ledger"];

/**
 * Which layers each locus brings forward (editorial mapping, shown in the legend).
 * 0 spine, 1 Aywa, 2 Horizon I, 3 Horizon II, 4 Horizon III, 5 whitepaper.
 */
export const LOCUS_LAYERS = [
  LAYERS,
  ["interface"],
  ["substrate", "cognition"],
  ["substrate"],
  ["ledger", "governance"],
  LAYERS,
];

export function layerHue(baseHue, layerIndex) {
  return (((baseHue + layerIndex / LAYERS.length) % 1) + 1) % 1;
}

/** Layout options by region width: smaller label glyphs on phones (1 css px per glyph pixel). */
export function labelMetrics(regionWidth) {
  const glyphPx = regionWidth < 600 ? 1 : 1.4;
  const phone = regionWidth < 600;
  return {
    glyphPx,
    options: {
      charWidth: GLYPH_ADVANCE * glyphPx,
      labelHeight: 7 * glyphPx,
      labelGap: phone ? 4 : 6,
      gap: phone ? 8 : 12,
      padding: phone ? 10 : 16,
    },
  };
}

/**
 * Pack cells into the 64-byte-per-record storage layout of `struct Cell`.
 * Returns an ArrayBuffer of MAX_CELLS records.
 */
export function packCellRecords(layout, repos, dynamic) {
  const buf = new ArrayBuffer(MAX_CELLS * CELL_FLOATS * 4);
  const f = new Float32Array(buf);
  const u = new Uint32Array(buf);
  layout.cells.slice(0, MAX_CELLS).forEach((c, i) => {
    const r = repos[c.index];
    const o = i * CELL_FLOATS;
    const label = packLabel(r.name);
    f[o + 0] = c.x;
    f[o + 1] = c.y;
    f[o + 2] = c.half;
    f[o + 3] = c.labelW;
    f[o + 4] = dynamic.hue[c.index];
    f[o + 5] = Number(r.tension) || 0;
    f[o + 6] = (Number(r.prs) || 0) / Math.max(1, Number(r.commits) || 1);
    f[o + 7] = dynamic.emphasis[c.index];
    f[o + 8] = label.length;
    f[o + 9] = Number(r.commits) || 0;
    f[o + 10] = dynamic.hover[c.index];
    f[o + 11] = Math.max(0, LAYERS.indexOf(r.layer));
    u.set(label.words, o + 12);
  });
  return buf;
}

export class WeftLoomEngine {
  constructor({ canvas, shaderUrl, dataUrl, hudEl, mixer, onUniformUpdate, regionEl, onHover }) {
    this.canvas = canvas;
    this.shaderUrl = shaderUrl;
    this.dataUrl = dataUrl;
    this.hudEl = hudEl;
    this.regionEl = regionEl || null;
    this.onHover = onHover || null;
    this.mixer = mixer || new AestheticMixer();
    this.onUniformUpdate = onUniformUpdate || null;
    this.locusMode = 0;
    this.state = {
      source: "fixture",
      active_nodes: 19,
      org_tension: 0.2053,
      gini_index: 0.2167,
      scroll_jitter: 0,
      lineage_alpha_confidence: 0.52,
      lineage_beta_confidence: 0.48,
      rejected_packets: 0,
      velocities: [0.28, 0.84, 0.62, 0.54, 0.38, 0.32, 0.44, 0.30],
    };
    this.repositories = [];
    this.layout = null;
    this.threads = [];
    this.glyphPx = 1.4;
    this.labelGap = 6;
    this.region = { left: 0, top: 0, width: 1, height: 1 };
    this.pointer = { x: -1, y: -1 };
    this.hoverIndex = -1;
    this.dyn = { hue: [], emphasis: [], hover: [], emphasisTarget: [] };
    this.calm = 1;
    this.scrollSpeed = 0;
    this.reducedMotion = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
    this.device = null;
    this.context = null;
    this.pipeline = null;
    this.buffers = {};
    this.bindGroup = null;
    this.worker = null;
    this.telemetrySab = null;
    this.ctx2d = null;
    this.t0 = performance.now();
  }

  setLocusMode(modeIndex) {
    this.locusMode = Math.max(0, Math.min(5, Number(modeIndex) || 0));
    this.updateEmphasisTargets();
  }

  updateEmphasisTargets() {
    const wanted = new Set(LOCUS_LAYERS[this.locusMode]);
    this.dyn.emphasisTarget = this.repositories.map((r) => (wanted.has(r.layer) ? 1 : 0.28));
    if (!this.dyn.emphasis.length) this.dyn.emphasis = this.dyn.emphasisTarget.slice();
  }

  // ---------------------------------------------------------------- sizing
  resizeCanvasToDisplaySize() {
    if (!this.canvas) return false;
    const dpr = Math.min(window.devicePixelRatio || 1, 3);
    const w = Math.max(1, Math.round((this.canvas.clientWidth || window.innerWidth) * dpr));
    const h = Math.max(1, Math.round((this.canvas.clientHeight || window.innerHeight) * dpr));
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
      return true;
    }
    return false;
  }

  /** Re-run the layout when the field region changes size. Region position is tracked per frame. */
  relayout() {
    if (!this.regionEl || !this.repositories.length) return;
    const r = this.regionEl.getBoundingClientRect();
    const width = Math.round(r.width);
    const height = Math.round(r.height);
    if (this.layout && this.layout.region.width === width && this.layout.region.height === height) return;
    const { glyphPx, options } = labelMetrics(width);
    this.glyphPx = glyphPx;
    this.labelGap = options.labelGap;
    const items = this.repositories.map((repo) => ({
      weight: Math.max(1, Number(repo.commits) || 1),
      labelLength: Math.min(16, String(repo.name).length),
    }));
    this.layout = layoutCells(items, { width, height }, options);
    this.threads = layerThreads(this.layout.cells, this.repositories.map((repo) => repo.layer));
    this.dirty = true;
  }

  observeResize() {
    this.resizeCanvasToDisplaySize();
    this.relayout();
    const onResize = () => {
      this.resizeCanvasToDisplaySize();
      this.relayout();
      this.dirty = true;
    };
    window.addEventListener("resize", onResize, { passive: true });
    if (typeof ResizeObserver !== "undefined") {
      const ro = new ResizeObserver(onResize);
      if (this.canvas) ro.observe(this.canvas);
      if (this.regionEl) ro.observe(this.regionEl);
    }
  }

  // ---------------------------------------------------------------- data
  async loadSeedJson() {
    try {
      const res = await fetch("./data/moissanite_telemetry.json");
      if (!res.ok) return;
      const data = await res.json();
      if (data.source) this.state.source = data.source;
      if (data.active_nodes != null) this.state.active_nodes = data.active_nodes;
      if (data.org_tension != null) this.state.org_tension = data.org_tension;
      if (data.gini_index != null) this.state.gini_index = data.gini_index;
      if (Array.isArray(data.repositories)) {
        this.repositories = data.repositories.slice(0, MAX_CELLS);
        this.state.velocities = data.repositories.slice(0, 8).map((r) => Number(r.commits || 10) / 50.0);
        const n = this.repositories.length;
        this.dyn.hover = new Array(n).fill(0);
        this.dyn.hue = new Array(n).fill(0);
        this.updateEmphasisTargets();
      }
    } catch (_) {
      /* offline or missing seed */
    }
  }

  applyVerifiedSym2pPacket(parsed) {
    if (parsed.metrics.active_nodes != null) this.state.active_nodes = parsed.metrics.active_nodes;
    if (parsed.metrics.tension != null) this.state.org_tension = parsed.metrics.tension;
    if (parsed.metrics.gini != null) this.state.gini_index = parsed.metrics.gini;
    if (this.hudEl) {
      this.hudEl.textContent = `SYM-2P verified (#${String(parsed.sequence).padStart(4, "0")}) | source=${this.state.source} | nodes=${this.state.active_nodes} | tension=${this.state.org_tension.toFixed(4)} | gini=${this.state.gini_index.toFixed(4)}`;
    }
  }

  async fetchSym2pOnce() {
    try {
      const res = await fetch(`${this.dataUrl}?t=${Date.now()}`);
      if (!res.ok) return;
      const text = await res.text();
      const line = text.split("\n").find((l) => l.trim().startsWith(":"));
      if (!line) return;
      const parsed = parseSym2pLine(line);
      const verified = await verifySym2pLine(line);
      if (!verified) {
        this.state.rejected_packets += 1;
        if (this.hudEl) {
          this.hudEl.textContent = `SYM-2P packet rejected (invalid/missing SHA-256) | rejected=${this.state.rejected_packets}`;
        }
        return;
      }
      this.applyVerifiedSym2pPacket(parsed);
    } catch (_) {
      if (this.hudEl) {
        this.hudEl.textContent = `Telemetry snapshot (${this.state.source}) | nodes=${this.state.active_nodes} | tension=${this.state.org_tension.toFixed(4)}`;
      }
    }
  }

  startTelemetryWorker() {
    try {
      if (typeof SharedArrayBuffer !== "undefined" && window.crossOriginIsolated) {
        this.telemetrySab = new SharedArrayBuffer(64);
      }
    } catch (_) {
      this.telemetrySab = null;
    }
    try {
      this.worker = new Worker("./assets/workers/telemetry-worker.js", { type: "module" });
      this.worker.onmessage = (event) => {
        const data = event.data || {};
        if (data.type === "telemetry" && data.hashValid) {
          this.applyVerifiedSym2pPacket({ sequence: data.sequence ?? 1, metrics: data.metrics || {} });
        } else if (data.type === "telemetry_rejected") {
          this.state.rejected_packets += 1;
        }
      };
      this.worker.postMessage({ type: "init", dataUrl: this.dataUrl, sab: this.telemetrySab, pollMs: 60000 });
    } catch (_) {
      setInterval(() => this.fetchSym2pOnce(), 60000);
    }
  }

  // ---------------------------------------------------------------- input
  /**
   * Reading cadence (weft/design/alive.md). A scroll-speed heuristic, not a
   * model: calm -> 1 while the reader dwells or scrolls slowly, -> 0 while
   * skimming. It drives glow and grain and the panels' --laya-calm, and never
   * changes layout (line-height or letter-spacing changes would move the
   * text under the reader).
   */
  trackReadingCadence() {
    let lastY = window.scrollY;
    let lastT = performance.now();
    window.addEventListener(
      "scroll",
      () => {
        const now = performance.now();
        const dt = Math.max(8, now - lastT);
        const v = (Math.abs(window.scrollY - lastY) / dt) * 1000;
        lastY = window.scrollY;
        lastT = now;
        this.scrollSpeed = this.scrollSpeed * 0.7 + v * 0.3;
        this.dirty = true;
      },
      { passive: true },
    );
  }

  trackPointer() {
    const update = (x, y) => {
      this.pointer = { x, y };
      let idx = -1;
      if (this.layout && x >= 0) idx = hitTest(this.layout, x - this.region.left, y - this.region.top);
      if (idx !== this.hoverIndex) {
        this.hoverIndex = idx;
        if (this.onHover) this.onHover(idx, idx >= 0 ? this.repositories[idx] : null, x, y);
      } else if (idx >= 0 && this.onHover) {
        this.onHover(idx, this.repositories[idx], x, y);
      }
      this.dirty = true;
    };
    window.addEventListener("pointermove", (e) => update(e.clientX, e.clientY), { passive: true });
    window.addEventListener("pointerdown", (e) => update(e.clientX, e.clientY), { passive: true });
    document.addEventListener("pointerleave", () => update(-1, -1));
    window.addEventListener("blur", () => update(-1, -1));
  }

  // ---------------------------------------------------------------- per-frame state
  stepDynamics() {
    const n = this.repositories.length;
    let moving = false;
    const ease = this.reducedMotion ? 1 : 0.14;
    for (let i = 0; i < n; i++) {
      const ht = i === this.hoverIndex ? 1 : 0;
      const et = this.dyn.emphasisTarget[i] ?? 1;
      const h = this.dyn.hover[i] + (ht - this.dyn.hover[i]) * ease;
      const e = this.dyn.emphasis[i] + (et - this.dyn.emphasis[i]) * ease;
      if (Math.abs(h - this.dyn.hover[i]) > 1e-4 || Math.abs(e - this.dyn.emphasis[i]) > 1e-4) moving = true;
      this.dyn.hover[i] = h;
      this.dyn.emphasis[i] = e;
    }
    this.scrollSpeed *= 0.92;
    const calmTarget = Math.exp(-this.scrollSpeed / 900);
    const calm = this.calm + (calmTarget - this.calm) * 0.06;
    if (Math.abs(calm - this.calm) > 1e-3) moving = true;
    this.calm = calm;
    const jitter = 1 - calm;
    this.state.scroll_jitter = jitter;
    this.state.lineage_alpha_confidence = 0.52 + jitter * 0.2;
    this.state.lineage_beta_confidence = 1 - this.state.lineage_alpha_confidence;
    document.documentElement.style.setProperty("--laya-calm", calm.toFixed(3));

    if (this.regionEl) {
      const r = this.regionEl.getBoundingClientRect();
      if (r.left !== this.region.left || r.top !== this.region.top) moving = true;
      this.region = { left: r.left, top: r.top, width: r.width, height: r.height };
    }
    return moving;
  }

  /** The I1 64-byte frame; also publishes the aesthetic vector as CSS custom properties. */
  packUniforms() {
    const aesthetic = this.mixer.calculateUnifiedAestheticVector();
    const hueDeg = Math.round(aesthetic.hue * 360);
    const rootStyle = document.documentElement.style;
    rootStyle.setProperty("--weft-rounding", `${Math.round(aesthetic.rounding * 14)}px`);
    rootStyle.setProperty("--weft-density", aesthetic.density.toFixed(3));
    rootStyle.setProperty("--weft-hue-deg", `${hueDeg}deg`);
    rootStyle.setProperty("--weft-accent", `hsl(${hueDeg}, 84%, 62%)`);
    rootStyle.setProperty("--weft-accent-2", `hsl(${(hueDeg + 48) % 360}, 82%, 58%)`);
    rootStyle.setProperty("--weft-accent-dim", `hsla(${hueDeg}, 84%, 62%, 0.22)`);
    rootStyle.setProperty("--weft-contrast", aesthetic.contrast.toFixed(3));
    for (let i = 0; i < LAYERS.length; i++) {
      rootStyle.setProperty(`--layer-${i}`, `hsl(${Math.round(layerHue(aesthetic.hue, i) * 360)}, 72%, 60%)`);
    }
    this.repositories.forEach((r, i) => {
      this.dyn.hue[i] = layerHue(aesthetic.hue, Math.max(0, LAYERS.indexOf(r.layer)));
    });

    const t = this.reducedMotion ? 12.0 : (performance.now() - this.t0) / 1000;
    const blendTension =
      this.state.org_tension * this.state.lineage_alpha_confidence +
      this.state.gini_index * this.state.lineage_beta_confidence;
    const v = this.state.velocities;
    const arr = new Float32Array([
      this.state.active_nodes,
      blendTension,
      t,
      this.state.gini_index,
      aesthetic.rounding,
      aesthetic.density,
      aesthetic.hue,
      aesthetic.contrast,
      v[0] || 0.2, v[1] || 0.2, v[2] || 0.2, v[3] || 0.2,
      v[4] || 0.2, v[5] || 0.2, v[6] || 0.2, v[7] || 0.2,
    ]);
    if (this.onUniformUpdate) this.onUniformUpdate(arr, aesthetic);
    return arr;
  }

  packView() {
    const cssW = Math.max(1, this.canvas.clientWidth || window.innerWidth);
    const cssH = Math.max(1, this.canvas.clientHeight || window.innerHeight);
    return new Float32Array([
      cssW,
      cssH,
      this.canvas.width / cssW, // actual device pixels per CSS px
      this.glyphPx,
      this.region.left,
      this.region.top,
      this.hoverIndex,
      this.calm,
      this.layout ? Math.min(this.layout.cells.length, MAX_CELLS) : 0,
      Math.min(this.threads.length, MAX_THREADS),
      this.reducedMotion ? 0 : 1,
      this.labelGap,
      this.pointer.x,
      this.pointer.y,
      window.scrollY,
      0,
      ...(this.layout && this.layout.bounds
        ? [this.layout.bounds.x0, this.layout.bounds.y0, this.layout.bounds.x1, this.layout.bounds.y1]
        : [0, 0, 0, 0]),
    ]);
  }

  packThreads() {
    const f = new Float32Array(MAX_THREADS * THREAD_FLOATS);
    if (!this.layout) return f;
    this.threads.slice(0, MAX_THREADS).forEach((e, i) => {
      const a = this.layout.cells[e.a];
      const b = this.layout.cells[e.b];
      const o = i * THREAD_FLOATS;
      f[o] = a.x;
      f[o + 1] = a.y;
      f[o + 2] = b.x;
      f[o + 3] = b.y;
      f[o + 4] = this.dyn.hue[e.a];
      f[o + 5] = Math.min(this.dyn.emphasis[e.a], this.dyn.emphasis[e.b]);
      f[o + 6] = (i * 0.381966) % 1;
    });
    return f;
  }

  // ---------------------------------------------------------------- WebGPU
  async initializeWebGPU() {
    if (!navigator.gpu) throw new Error("WebGPU unavailable");
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) throw new Error("No GPU adapter");
    this.device = await adapter.requestDevice();
    const res = await fetch(this.shaderUrl);
    if (!res.ok) throw new Error(`Shader fetch failed: ${res.status}`);
    const module = this.device.createShaderModule({ code: await res.text() });
    const info = await module.getCompilationInfo?.();
    if (info && info.messages.some((m) => m.type === "error")) {
      throw new Error(info.messages.map((m) => `${m.lineNum}:${m.linePos} ${m.message}`).join("\n"));
    }
    this.context = this.canvas.getContext("webgpu");
    const format = navigator.gpu.getPreferredCanvasFormat();
    this.context.configure({ device: this.device, format, alphaMode: "opaque" });

    const U = GPUBufferUsage;
    const mk = (size, usage) => this.device.createBuffer({ size, usage });
    this.buffers.telemetry = mk(64, U.UNIFORM | U.COPY_DST);
    this.buffers.view = mk(80, U.UNIFORM | U.COPY_DST);
    this.buffers.cells = mk(MAX_CELLS * CELL_FLOATS * 4, U.STORAGE | U.COPY_DST);
    this.buffers.threads = mk(MAX_THREADS * THREAD_FLOATS * 4, U.STORAGE | U.COPY_DST);
    const fontTable = encodeFontTable();
    this.buffers.font = mk(fontTable.byteLength, U.STORAGE | U.COPY_DST);
    this.device.queue.writeBuffer(this.buffers.font, 0, fontTable);

    this.pipeline = await this.device.createRenderPipelineAsync({
      layout: "auto",
      vertex: { module, entryPoint: "vs_main" },
      fragment: { module, entryPoint: "fs_main", targets: [{ format }] },
      primitive: { topology: "triangle-list" },
    });
    this.bindGroup = this.device.createBindGroup({
      layout: this.pipeline.getBindGroupLayout(0),
      entries: ["telemetry", "view", "cells", "threads", "font"].map((k, binding) => ({
        binding,
        resource: { buffer: this.buffers[k] },
      })),
    });
    this.device.lost?.then((e) => {
      if (e.reason !== "destroyed") console.warn("WebGPU device lost:", e.message);
    });
  }

  renderFrame() {
    if (!this.device) return;
    this.resizeCanvasToDisplaySize();
    this.stepDynamics();
    const q = this.device.queue;
    q.writeBuffer(this.buffers.telemetry, 0, this.packUniforms());
    q.writeBuffer(this.buffers.view, 0, this.packView());
    if (this.layout) q.writeBuffer(this.buffers.cells, 0, packCellRecords(this.layout, this.repositories, this.dyn));
    q.writeBuffer(this.buffers.threads, 0, this.packThreads());
    const encoder = this.device.createCommandEncoder();
    const pass = encoder.beginRenderPass({
      colorAttachments: [
        {
          view: this.context.getCurrentTexture().createView(),
          clearValue: { r: 0.01, g: 0.014, b: 0.024, a: 1 },
          loadOp: "clear",
          storeOp: "store",
        },
      ],
    });
    pass.setPipeline(this.pipeline);
    pass.setBindGroup(0, this.bindGroup);
    pass.draw(3);
    pass.end();
    q.submit([encoder.finish()]);
  }

  // ---------------------------------------------------------------- Canvas2D fallback
  /**
   * Same layout, threads, encodings and 5x7 font, drawn with Canvas2D. Static
   * (no per-pixel weave, grain or pulse), and redrawn only when something
   * changes.
   */
  fallback2d() {
    this.ctx2d = this.canvas.getContext("2d");
    const font = encodeFontTable();
    const drawText = (ctx, text, x, y, gp) => {
      const s = String(text).toUpperCase();
      for (let k = 0; k < s.length; k++) {
        const code = s.charCodeAt(k) & 127;
        const words = [font[code * 2], font[code * 2 + 1]];
        for (let row = 0; row < 7; row++) {
          for (let col = 0; col < 5; col++) {
            if (glyphBit(words, col, row)) ctx.fillRect(x + (k * GLYPH_ADVANCE + col) * gp, y + row * gp, gp, gp);
          }
        }
      }
    };
    const draw = () => {
      const resized = this.resizeCanvasToDisplaySize();
      const moving = this.stepDynamics();
      const uniforms = this.packUniforms();
      if (this.dirty || moving || resized) {
        this.dirty = false;
        const ctx = this.ctx2d;
        const dpr = this.canvas.width / Math.max(1, this.canvas.clientWidth);
        const hue = uniforms[6];
        const rounding = uniforms[4];
        const contrast = uniforms[7];
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        const g = Math.round(3 + Math.min(1, contrast * 3) * 4);
        ctx.fillStyle = `hsl(225, 40%, ${g}%)`;
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const step = 34 - 16 * uniforms[5];
        ctx.strokeStyle = `hsla(${Math.round(hue * 360)}, 45%, 50%, 0.07)`;
        ctx.lineWidth = step * 0.34;
        ctx.beginPath();
        const W = this.canvas.clientWidth;
        const H = this.canvas.clientHeight;
        const off = (window.scrollY * 0.35) % step;
        for (let x = step / 2; x < W; x += step) {
          ctx.moveTo(x, 0);
          ctx.lineTo(x, H);
        }
        for (let y = step / 2 - off; y < H; y += step) {
          ctx.moveTo(0, y);
          ctx.lineTo(W, y);
        }
        ctx.stroke();
        if (this.layout) {
          ctx.save();
          ctx.translate(this.region.left, this.region.top);
          for (const e of this.threads) {
            const a = this.layout.cells[e.a];
            const b = this.layout.cells[e.b];
            const em = Math.min(this.dyn.emphasis[e.a], this.dyn.emphasis[e.b]);
            ctx.strokeStyle = `hsla(${Math.round(this.dyn.hue[e.a] * 360)}, 70%, 60%, ${0.3 * em})`;
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
          const gini = uniforms[3];
          for (const c of this.layout.cells) {
            const i = c.index;
            const r = this.repositories[i];
            const em = this.dyn.emphasis[i];
            const hov = this.dyn.hover[i];
            const half = c.half * (1 + 0.05 * hov);
            const hd = Math.round(this.dyn.hue[i] * 360);
            const sw = 1 + 3 * gini;
            ctx.beginPath();
            ctx.roundRect(c.x - half + sw / 2, c.y - half + sw / 2, 2 * half - sw, 2 * half - sw, Math.max(0, half * rounding - sw / 2));
            ctx.fillStyle = `hsla(${hd}, 60%, ${12 + 8 * hov}%, ${0.55 + 0.45 * em})`;
            ctx.fill();
            ctx.lineWidth = sw;
            ctx.strokeStyle = `hsla(${hd}, 72%, 60%, ${0.35 + 0.65 * em})`;
            ctx.stroke();
            const digits = String(r.commits);
            const gpD = Math.max(1, Math.round((half * 0.62 / 7) * dpr)) / dpr;
            ctx.fillStyle = `hsla(${hd}, 80%, 82%, ${0.5 + 0.5 * em})`;
            drawText(ctx, digits, c.x - ((digits.length * 6 - 1) * gpD) / 2, c.y - 3.5 * gpD, gpD);
            const gpL = Math.max(1, Math.round(this.glyphPx * dpr)) / dpr;
            const name = String(r.name).slice(0, 16);
            ctx.fillStyle = `rgba(${hov > 0.5 ? "255,255,255" : "148,163,184"}, ${0.35 + 0.65 * em})`;
            drawText(ctx, name, c.x - ((name.length * 6 - 1) * gpL) / 2, c.y + half + this.labelGap, gpL);
          }
          ctx.restore();
        }
      }
      requestAnimationFrame(draw);
    };
    this.dirty = true;
    requestAnimationFrame(draw);
  }

  async boot() {
    await this.loadSeedJson();
    this.observeResize();
    await this.fetchSym2pOnce();
    this.startTelemetryWorker();
    this.trackReadingCadence();
    this.trackPointer();
    try {
      await this.initializeWebGPU();
      document.documentElement.dataset.renderer = "webgpu";
      const loop = () => {
        this.renderFrame();
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    } catch (err) {
      if (navigator.gpu) console.warn("WebGPU path failed, using Canvas2D:", err.message);
      document.documentElement.dataset.renderer = "canvas2d";
      this.fallback2d();
    }
  }
}
