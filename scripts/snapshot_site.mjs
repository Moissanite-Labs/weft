#!/usr/bin/env node
/**
 * Headless snapshot of the w3ft.org surface, including the WebGPU field.
 *
 * Headless Chromium renders WebGPU (SwiftShader) but does not composite a
 * WebGPU canvas into page screenshots, so a plain screenshot shows an empty
 * canvas. This script installs an init hook that hands the page a persistent
 * COPY_SRC texture from `getCurrentTexture()`, reads it back after a few
 * frames, and paints the pixels into a 2D canvas overlay before the
 * screenshot. Page code is not modified.
 *
 * Usage (needs Playwright + Chromium; not run in CI):
 *   python3 -m http.server 8765 --directory docs &
 *   node scripts/snapshot_site.mjs http://localhost:8765/ out-dir [--no-webgpu] [--full] [--field-only] [--only=desktop|phone|wide]
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const url = process.argv[2] || "http://localhost:8765/";
const outDir = process.argv[3] || "snapshots";
const noWebGPU = process.argv.includes("--no-webgpu");
const full = process.argv.includes("--full");
const fieldOnly = process.argv.includes("--field-only");
const VIEWPORTS = [
  ["desktop", 1440, 900, 1],
  ["phone", 390, 844, 3],
  ["wide", 2560, 1300, 1],
];

const HOOK = `(() => {
  if (!window.GPUCanvasContext) return;
  const configure = GPUCanvasContext.prototype.configure;
  const getCurrentTexture = GPUCanvasContext.prototype.getCurrentTexture;
  window.__snapTargets = [];
  GPUCanvasContext.prototype.configure = function (cfg) {
    this.__cfg = cfg;
    return configure.call(this, { ...cfg, usage: (cfg.usage || GPUTextureUsage.RENDER_ATTACHMENT) | GPUTextureUsage.COPY_SRC });
  };
  GPUCanvasContext.prototype.getCurrentTexture = function () {
    const c = this.canvas, cfg = this.__cfg;
    if (!this.__tex || this.__tex.width !== c.width || this.__tex.height !== c.height) {
      this.__tex = cfg.device.createTexture({ size: [c.width, c.height], format: cfg.format,
        usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.COPY_SRC });
      if (!window.__snapTargets.includes(this)) window.__snapTargets.push(this);
    }
    return this.__tex;
  };
  window.__snap = async () => {
    for (const ctx of window.__snapTargets) {
      const tex = ctx.__tex, dev = ctx.__cfg.device, w = tex.width, h = tex.height;
      const bpr = Math.ceil((w * 4) / 256) * 256;
      const buf = dev.createBuffer({ size: bpr * h, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ });
      const enc = dev.createCommandEncoder();
      enc.copyTextureToBuffer({ texture: tex }, { buffer: buf, bytesPerRow: bpr }, [w, h]);
      dev.queue.submit([enc.finish()]);
      await buf.mapAsync(GPUMapMode.READ);
      const src = new Uint8Array(buf.getMappedRange());
      const img = new ImageData(w, h);
      const bgra = String(ctx.__cfg.format).startsWith("bgra");
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const s = y * bpr + x * 4, d = (y * w + x) * 4;
        img.data[d] = src[s + (bgra ? 2 : 0)]; img.data[d + 1] = src[s + 1];
        img.data[d + 2] = src[s + (bgra ? 0 : 2)]; img.data[d + 3] = 255;
      }
      const o = document.createElement("canvas");
      o.width = w; o.height = h;
      o.getContext("2d").putImageData(img, 0, 0);
      const r = ctx.canvas.getBoundingClientRect();
      Object.assign(o.style, { position: "fixed", left: r.left + "px", top: r.top + "px",
        width: r.width + "px", height: r.height + "px", zIndex: getComputedStyle(ctx.canvas).zIndex, pointerEvents: "none" });
      ctx.canvas.after(o);
    }
    return window.__snapTargets.length;
  };
})();`;

fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ args: noWebGPU ? [] : ["--enable-unsafe-webgpu"] });
const only = (process.argv.find((a) => a.startsWith("--only=")) || "").slice(7);
for (const [name, width, height, dpr] of VIEWPORTS.filter((v) => !only || v[0] === only)) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: dpr });
  const logs = [];
  page.on("console", (m) => logs.push(`${m.type()}: ${m.text()}`));
  page.on("pageerror", (e) => logs.push(`pageerror: ${e.message}`));
  if (noWebGPU) await page.addInitScript(() => { try { delete Navigator.prototype.gpu; } catch (_) {} });
  else await page.addInitScript(HOOK);
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => document.documentElement.dataset.renderer, null, { timeout: 60000 });
  await page.waitForTimeout(1500);
  if (fieldOnly) await page.addStyleTag({ content: "body > *:not(canvas){visibility:hidden!important}" });
  const snapped = noWebGPU ? 0 : await page.evaluate(() => (window.__snap ? window.__snap() : 0));
  const metrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    renderer: document.documentElement.dataset.renderer || "unknown",
  }));
  const file = path.join(outDir, `${name}${noWebGPU ? "-2d" : ""}${fieldOnly ? "-field" : ""}.png`);
  await page.screenshot({ path: file, fullPage: full });
  console.log(JSON.stringify({ name, file, snapped, ...metrics, logs: logs.slice(0, 8) }));
  await page.close();
}
await browser.close();
