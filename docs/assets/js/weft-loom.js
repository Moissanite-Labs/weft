import { AestheticMixer } from "./aesthetic-mixer.js";
import { parseSym2pLine, verifySym2pLine } from "./sym2p-parse.js";

const MAX_LABEL_NODES = 32;
const CHARS_PER_LABEL = 16;

export class WeftLoomEngine {
  constructor({ canvas, shaderUrl, dataUrl, hudEl, mixer }) {
    this.canvas = canvas;
    this.shaderUrl = shaderUrl;
    this.dataUrl = dataUrl;
    this.hudEl = hudEl;
    this.mixer = mixer || new AestheticMixer();
    this.state = {
      source: "fixture",
      active_nodes: 19,
      org_tension: 0.2105,
      gini_index: 0.2072,
      scroll_jitter: 0,
      lineage_alpha_confidence: 0.52,
      lineage_beta_confidence: 0.48,
      rejected_packets: 0,
      velocities: [0.28, 0.84, 0.62, 0.54, 0.38, 0.32, 0.44, 0.30],
    };
    this.repositories = [];
    this.labelMatrix = [];
    this.device = null;
    this.context = null;
    this.pipeline = null;
    this.uniformBuffer = null;
    this.labelBuffer = null;
    this.bindGroup = null;
    this.worker = null;
    this.telemetrySab = null;
    this.resizeObserver = null;
  }

  resizeCanvasToDisplaySize() {
    if (!this.canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const rect = this.canvas.getBoundingClientRect();
    const width = Math.max(1, Math.floor((rect.width || window.innerWidth || 960) * dpr));
    const height = Math.max(1, Math.floor((rect.height || window.innerHeight || 540) * dpr));
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  observeCanvasResize() {
    this.resizeCanvasToDisplaySize();
    window.addEventListener("resize", () => this.resizeCanvasToDisplaySize(), { passive: true });
    if (typeof ResizeObserver !== "undefined" && this.canvas) {
      this.resizeObserver = new ResizeObserver(() => this.resizeCanvasToDisplaySize());
      this.resizeObserver.observe(this.canvas);
    }
  }

  encodeLabelStorageArray() {
    const out = new Uint32Array(MAX_LABEL_NODES * CHARS_PER_LABEL);
    for (let i = 0; i < MAX_LABEL_NODES; i++) {
      const row = this.labelMatrix[i] || [];
      for (let c = 0; c < CHARS_PER_LABEL; c++) {
        out[i * CHARS_PER_LABEL + c] = row[c] || 32;
      }
    }
    return out;
  }

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
        this.repositories = data.repositories;
        this.state.velocities = data.repositories.slice(0, 8).map((r) => Number(r.commits || 10) / 50.0);
        if (!Array.isArray(data.repoLabelsTextMatrix)) {
          this.labelMatrix = data.repositories.map((r) => {
            const padded = String(r.name || "").toUpperCase().slice(0, CHARS_PER_LABEL).padEnd(CHARS_PER_LABEL, " ");
            return Array.from(padded).map((ch) => ch.charCodeAt(0));
          });
        }
      }
      if (Array.isArray(data.repoLabelsTextMatrix)) {
        this.labelMatrix = data.repoLabelsTextMatrix;
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
    } catch (err) {
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
          this.applyVerifiedSym2pPacket({
            sequence: data.sequence ?? 1,
            metrics: data.metrics || {},
          });
        } else if (data.type === "telemetry_rejected") {
          this.state.rejected_packets += 1;
        }
      };
      this.worker.postMessage({
        type: "init",
        dataUrl: this.dataUrl,
        sab: this.telemetrySab,
        pollMs: 60000,
      });
    } catch (_) {
      /* Fallback single poller on main thread if module worker cannot start */
      setInterval(() => this.fetchSym2pOnce(), 60000);
    }
  }

  trackPointerMembrane() {
    let lastY = window.scrollY;
    window.addEventListener(
      "scroll",
      () => {
        const delta = Math.abs(window.scrollY - lastY);
        lastY = window.scrollY;
        this.state.scroll_jitter = Math.min(1, this.state.scroll_jitter * 0.9 + delta * 0.02);
        const alpha = 0.52 + this.state.scroll_jitter * 0.2;
        this.state.lineage_alpha_confidence = alpha;
        this.state.lineage_beta_confidence = 1 - alpha;
      },
      { passive: true },
    );
  }

  async initializeWebGPU() {
    if (!navigator.gpu) throw new Error("WebGPU unavailable");
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) throw new Error("No GPU adapter");
    this.device = await adapter.requestDevice();
    this.context = this.canvas.getContext("webgpu");
    const format = navigator.gpu.getPreferredCanvasFormat();
    this.context.configure({ device: this.device, format, alphaMode: "opaque" });

    const res = await fetch(this.shaderUrl);
    if (!res.ok) throw new Error(`Shader fetch failed: ${res.status}`);
    const code = await res.text();
    const module = this.device.createShaderModule({ code });

    this.uniformBuffer = this.device.createBuffer({
      size: 64,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
    const labelBytes = this.encodeLabelStorageArray();
    this.labelBuffer = this.device.createBuffer({
      size: labelBytes.byteLength,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    });
    this.device.queue.writeBuffer(this.labelBuffer, 0, labelBytes);

    this.pipeline = this.device.createRenderPipeline({
      layout: "auto",
      vertex: { module, entryPoint: "vs_main" },
      fragment: { module, entryPoint: "fs_main", targets: [{ format }] },
      primitive: { topology: "triangle-list" },
    });
    this.bindGroup = this.device.createBindGroup({
      layout: this.pipeline.getBindGroupLayout(0),
      entries: [
        { binding: 0, resource: { buffer: this.uniformBuffer } },
        { binding: 1, resource: { buffer: this.labelBuffer } },
      ],
    });
  }

  packUniforms() {
    const aesthetic = this.mixer.calculateUnifiedAestheticVector();
    document.documentElement.style.setProperty("--weft-rounding", `${Math.round(aesthetic.rounding * 16)}px`);
    document.documentElement.style.setProperty("--weft-density", aesthetic.density.toFixed(3));
    document.documentElement.style.setProperty("--weft-hue-deg", `${Math.round(aesthetic.hue * 360)}deg`);
    document.documentElement.style.setProperty("--weft-contrast", aesthetic.contrast.toFixed(3));

    const t0 = performance.now() / 1000;
    const blendTension =
      this.state.org_tension * this.state.lineage_alpha_confidence +
      this.state.gini_index * this.state.lineage_beta_confidence;
    const v = this.state.velocities;
    return new Float32Array([
      this.state.active_nodes,
      blendTension,
      t0,
      this.state.gini_index,
      aesthetic.rounding,
      aesthetic.density,
      aesthetic.hue,
      aesthetic.contrast,
      v[0] || 0.2, v[1] || 0.2, v[2] || 0.2, v[3] || 0.2,
      v[4] || 0.2, v[5] || 0.2, v[6] || 0.2, v[7] || 0.2,
    ]);
  }

  renderFrame() {
    if (!this.device) return;
    this.resizeCanvasToDisplaySize();
    const uniforms = this.packUniforms();
    this.device.queue.writeBuffer(this.uniformBuffer, 0, uniforms);
    const encoder = this.device.createCommandEncoder();
    const view = this.context.getCurrentTexture().createView();
    const pass = encoder.beginRenderPass({
      colorAttachments: [
        {
          view,
          clearValue: { r: 0.01, g: 0.015, b: 0.02, a: 1 },
          loadOp: "clear",
          storeOp: "store",
        },
      ],
    });
    pass.setPipeline(this.pipeline);
    pass.setBindGroup(0, this.bindGroup);
    pass.draw(6);
    pass.end();
    this.device.queue.submit([encoder.finish()]);
  }

  fallback2d() {
    const ctx = this.canvas.getContext("2d");
    const draw = () => {
      this.resizeCanvasToDisplaySize();
      const uniforms = this.packUniforms();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = this.canvas.width;
      const h = this.canvas.height;
      const hueDeg = Math.round(uniforms[6] * 360);
      const roundingPx = Math.round(uniforms[4] * 18 * dpr);
      const density = uniforms[5];

      ctx.fillStyle = "#05070b";
      ctx.fillRect(0, 0, w, h);

      const cols = 5;
      const nodes = Math.min(this.labelMatrix.length || 19, Math.floor(this.state.active_nodes));
      const padX = Math.round(48 * dpr);
      const padY = Math.round(130 * dpr);
      const cellW = Math.max(120 * dpr, Math.floor((w - padX * 2) / cols) - Math.round(14 * (1.2 - density) * dpr));
      const cellH = Math.max(64 * dpr, Math.round(82 * dpr));

      for (let i = 0; i < nodes; i++) {
        const c = i % cols;
        const r = Math.floor(i / cols);
        const x = padX + c * (cellW + Math.round(12 * dpr));
        const y = padY + r * (cellH + Math.round(12 * dpr));
        ctx.strokeStyle = i % 2 ? `hsl(${hueDeg}, 82%, 60%)` : `hsl(${(hueDeg + 45) % 360}, 85%, 58%)`;
        ctx.lineWidth = Math.max(1, 1.5 * dpr);
        ctx.beginPath();
        if (typeof ctx.roundRect === "function") {
          ctx.roundRect(x, y, cellW, cellH, roundingPx);
        } else {
          ctx.rect(x, y, cellW, cellH);
        }
        ctx.stroke();

        const label = (this.labelMatrix[i] || []).map((ch) => String.fromCharCode(ch)).join("").trim();
        ctx.fillStyle = "#e2e8f0";
        ctx.font = `${Math.round(12 * dpr)}px "SF Mono", Menlo, monospace`;
        ctx.fillText(label || `NODE ${i + 1}`, x + Math.round(10 * dpr), y + Math.round(26 * dpr));

        const repo = this.repositories[i];
        if (repo) {
          ctx.fillStyle = "#94a3b8";
          ctx.font = `${Math.round(10 * dpr)}px "SF Mono", Menlo, monospace`;
          ctx.fillText(
            `${repo.layer} | T=${Number(repo.tension).toFixed(2)}`,
            x + Math.round(10 * dpr),
            y + Math.round(48 * dpr),
          );
        }
      }
      requestAnimationFrame(draw);
    };
    requestAnimationFrame(draw);
  }

  async boot() {
    this.observeCanvasResize();
    await this.loadSeedJson();
    await this.fetchSym2pOnce();
    this.startTelemetryWorker();
    this.trackPointerMembrane();
    try {
      await this.initializeWebGPU();
      const loop = () => {
        this.renderFrame();
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    } catch (err) {
      if (this.hudEl && !this.hudEl.textContent.includes("SYM-2P")) {
        this.hudEl.textContent = `Canvas2D fallback (${err.message}) | nodes=${this.state.active_nodes}`;
      }
      this.fallback2d();
    }
  }
}
