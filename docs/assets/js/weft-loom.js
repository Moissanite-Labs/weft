import { AestheticMixer } from "./aesthetic-mixer.js";
import { parseSym2pLine, verifySym2pLine } from "./sym2p-parse.js";

const WGSL_FALLBACK = `struct OrgTelemetry {
    active_nodes: f32, org_tension: f32, system_time: f32, gini_index: f32,
    user_rounding: f32, user_density: f32, user_hue: f32, user_contrast: f32,
    node_vel_0: vec4<f32>, node_vel_1: vec4<f32>,
};
@group(0) @binding(0) var<uniform> telemetry : OrgTelemetry;
struct VertexOutput { @builtin(position) position: vec4<f32>, @location(0) uv: vec2<f32> };
@vertex fn vs_main(@builtin(vertex_index) vi: u32) -> VertexOutput {
    var pos = array<vec2<f32>, 6>(vec2(-1.,-1.), vec2(1.,-1.), vec2(-1.,1.), vec2(-1.,1.), vec2(1.,-1.), vec2(1.,1.));
    var out: VertexOutput; out.position = vec4(pos[vi], 0., 1.); out.uv = pos[vi]; return out;
}
@fragment fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    var p = in.uv; p.x *= 1.6;
    let d = length(p) - 0.35 - telemetry.org_tension * 0.08;
    let glow = exp(-abs(d) * 14.0);
    let col = mix(vec3(0.02, 0.03, 0.05), vec3(0.1, 0.5, 0.85), glow);
    return vec4(col, 1.0);
}`;

export class WeftLoomEngine {
  constructor({ canvas, shaderUrl, dataUrl, hudEl, mixer }) {
    this.canvas = canvas;
    this.shaderUrl = shaderUrl;
    this.dataUrl = dataUrl;
    this.hudEl = hudEl;
    this.mixer = mixer || new AestheticMixer();
    this.state = {
      active_nodes: 4,
      org_tension: 0.1,
      gini_index: 0.2,
      scroll_jitter: 0,
      lineage_alpha_confidence: 0.52,
      lineage_beta_confidence: 0.48,
    };
    this.labelMatrix = [];
    this.device = null;
    this.context = null;
    this.pipeline = null;
    this.uniformBuffer = null;
    this.bindGroup = null;
    this.worker = null;
    this.telemetrySab = null;
  }

  async loadSeedJson() {
    try {
      const res = await fetch("data/moissanite_telemetry.json");
      if (!res.ok) return;
      const data = await res.json();
      this.state.active_nodes = data.active_nodes;
      this.state.org_tension = data.org_tension;
      this.state.gini_index = data.gini_index;
      this.labelMatrix = data.repoLabelsTextMatrix || [];
    } catch (_) {
      /* offline file:// or missing seed */
    }
  }

  async fetchSym2p() {
    try {
      const res = await fetch(`${this.dataUrl}?t=${Date.now()}`);
      const text = await res.text();
      const line = text.split("\n").find((l) => l.trim().startsWith(":"));
      if (!line) return;
      const parsed = parseSym2pLine(line);
      const hashOk = await verifySym2pLine(line);
      if (parsed.metrics.active_nodes != null) this.state.active_nodes = parsed.metrics.active_nodes;
      if (parsed.metrics.tension != null) this.state.org_tension = parsed.metrics.tension;
      if (parsed.metrics.gini != null) this.state.gini_index = parsed.metrics.gini;
      this.hudEl.textContent = `SYM-2P hash ${hashOk ? "valid" : "unverified"} | nodes ${this.state.active_nodes} | tension ${this.state.org_tension.toFixed(4)}`;
    } catch (err) {
      this.hudEl.textContent = `Telemetry deferred: ${err.message}`;
    }
  }

  startTelemetryWorker() {
    try {
      this.telemetrySab = new SharedArrayBuffer(64);
    } catch (_) {
      this.telemetrySab = null;
    }
    this.worker = new Worker("./assets/workers/telemetry-worker.js");
    this.worker.onmessage = (event) => {
      if (event.data?.type === "telemetry") {
        const m = event.data.metrics;
        if (m.tension != null) this.state.org_tension = m.tension;
        if (m.active_nodes != null) this.state.active_nodes = m.active_nodes;
        if (m.gini != null) this.state.gini_index = m.gini;
      }
    };
    this.worker.postMessage({
      type: "init",
      dataUrl: this.dataUrl,
      sab: this.telemetrySab,
      pollMs: 60000,
    });
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
    let code = WGSL_FALLBACK;
    try {
      const res = await fetch(this.shaderUrl);
      if (res.ok) code = await res.text();
    } catch (_) {
      /* use fallback */
    }
    const module = this.device.createShaderModule({ code });
    this.uniformBuffer = this.device.createBuffer({
      size: 64,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
    this.pipeline = this.device.createRenderPipeline({
      layout: "auto",
      vertex: { module, entryPoint: "vs_main" },
      fragment: { module, entryPoint: "fs_main", targets: [{ format }] },
      primitive: { topology: "triangle-list" },
    });
    this.bindGroup = this.device.createBindGroup({
      layout: this.pipeline.getBindGroupLayout(0),
      entries: [{ binding: 0, resource: { buffer: this.uniformBuffer } }],
    });
  }

  packUniforms() {
    const aesthetic = this.mixer.calculateUnifiedAestheticVector();
    const t0 = performance.now() / 1000;
    const blendTension =
      this.state.org_tension * this.state.lineage_alpha_confidence +
      this.state.gini_index * this.state.lineage_beta_confidence;
    return new Float32Array([
      this.state.active_nodes,
      blendTension,
      t0,
      this.state.gini_index,
      aesthetic.rounding,
      aesthetic.density,
      aesthetic.hue,
      aesthetic.contrast,
      0, 0, 0, 0,
      0, 0, 0, 0,
    ]);
  }

  renderFrame() {
    if (!this.device) return;
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
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
      ctx.fillStyle = "#05070b";
      ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      const cols = 4;
      const nodes = Math.min(this.labelMatrix.length, Math.floor(this.state.active_nodes));
      for (let i = 0; i < nodes; i++) {
        const c = i % cols;
        const r = Math.floor(i / cols);
        const x = 60 + c * 240;
        const y = 80 + r * 110;
        ctx.strokeStyle = i % 2 ? "#38bdf8" : "#f59e0b";
        ctx.strokeRect(x, y, 210, 80);
        const label = (this.labelMatrix[i] || []).map((ch) => String.fromCharCode(ch)).join("").trim();
        ctx.fillStyle = "#e2e8f0";
        ctx.font = "12px monospace";
        ctx.fillText(label || `NODE ${i + 1}`, x + 10, y + 28);
      }
      ctx.fillStyle = "#94a3b8";
      ctx.fillText(
        `membrane fallback | α=${this.state.lineage_alpha_confidence.toFixed(2)} β=${this.state.lineage_beta_confidence.toFixed(2)}`,
        24,
        this.canvas.height - 24,
      );
      requestAnimationFrame(draw);
    };
    requestAnimationFrame(draw);
  }

  async boot() {
    await this.loadSeedJson();
    await this.fetchSym2p();
    this.startTelemetryWorker();
    this.trackPointerMembrane();
    setInterval(() => this.fetchSym2p(), 45000);
    try {
      await this.initializeWebGPU();
      const loop = () => {
        this.renderFrame();
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    } catch (err) {
      this.hudEl.textContent = `WebGPU membrane pending: ${err.message}`;
      this.fallback2d();
    }
  }
}
