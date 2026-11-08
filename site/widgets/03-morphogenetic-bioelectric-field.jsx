import { jsx, jsxs } from 'https://widgetlibs.static.usercontent.goog/react/jsx-runtime-Dc9ViRTo.js';
import React, { useState, useRef, useEffect } from 'https://widgetlibs.static.usercontent.goog/react-Dd1pKoqe.js';
import ReactDOM from 'https://widgetlibs.static.usercontent.goog/react-dom/client-BTuQ-l8_.js';
import { ErrorBoundary } from 'https://widgetlibs.static.usercontent.goog/react-error-boundary-BY2GTZrN.js';
import * as Slider from 'https://widgetlibs.static.usercontent.goog/@radix-ui/react-slider-DXk-CvUR.js';

true              &&(function polyfill() {
	const relList = document.createElement("link").relList;
	if (relList && relList.supports && relList.supports("modulepreload")) return;
	for (const link of document.querySelectorAll("link[rel=\"modulepreload\"]")) processPreload(link);
	new MutationObserver((mutations) => {
		for (const mutation of mutations) {
			if (mutation.type !== "childList") continue;
			for (const node of mutation.addedNodes) if (node.tagName === "LINK" && node.rel === "modulepreload") processPreload(node);
		}
	}).observe(document, {
		childList: true,
		subtree: true
	});
	function getFetchOpts(link) {
		const fetchOpts = {};
		if (link.integrity) fetchOpts.integrity = link.integrity;
		if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
		if (link.crossOrigin === "use-credentials") fetchOpts.credentials = "include";
		else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
		else fetchOpts.credentials = "same-origin";
		return fetchOpts;
	}
	function processPreload(link) {
		if (link.ep) return;
		link.ep = true;
		const fetchOpts = getFetchOpts(link);
		fetch(link.href, fetchOpts);
	}
}());

const ErrorFallback = ({ error }) => /* @__PURE__ */ jsxs("div", { className: "p-5 text-error bg-card rounded-lg border border-border", children: [
  /* @__PURE__ */ jsx("p", { className: "text-sm font-medium", children: "Something went wrong in the simulation:" }),
  /* @__PURE__ */ jsx("pre", { className: "text-xs mt-2 overflow-auto max-w-full", children: error.message })
] });
const SYSTEM_NODES = [
  { id: "telemetry", name: "Telemetry", x: 0.15, y: 0.5, color: "#34a853", baseRadius: 18 },
  { id: "sys1", name: "System 1 (Reflex)", x: 0.4, y: 0.25, color: "#ea4335", baseRadius: 24 },
  { id: "sys2", name: "System 2 (Cognitive)", x: 0.4, y: 0.75, color: "#336ef3", baseRadius: 26 },
  { id: "uniforms", name: "Uniforms (State)", x: 0.65, y: 0.5, color: "#fbbc04", baseRadius: 16 },
  { id: "gpu", name: "GPU Shaders", x: 0.85, y: 0.5, color: "#9c27b0", baseRadius: 22 }
];
function App() {
  return /* @__PURE__ */ jsx(ErrorBoundary, { FallbackComponent: ErrorFallback, children: /* @__PURE__ */ jsx(MindPalaceSimulation, {}) });
}
function MindPalaceSimulation() {
  const [system1Reflex, setSystem1Reflex] = useState(60);
  const [system2Load, setSystem2Load] = useState(40);
  const [isPlaying, setIsPlaying] = useState(true);
  const [frameTick, setFrameTick] = useState(0);
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const lastTimeRef = useRef(performance.now());
  const [dimensions, setDimensions] = useState({ width: 600, height: 337 });
  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const w = Math.max(entry.contentRect.width, 360);
        const h = w * 0.5625;
        setDimensions({ width: w, height: h });
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);
  useEffect(() => {
    if (!isPlaying) return;
    lastTimeRef.current = performance.now();
    let frameId;
    const tick = (now) => {
      Math.min((now - lastTimeRef.current) / 1e3, 0.1);
      lastTimeRef.current = now;
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          const { width, height } = dimensions;
          ctx.fillStyle = "#0c0e14";
          ctx.fillRect(0, 0, width, height);
          const s1Speed = 2 + system1Reflex / 20;
          const s2Intensity = system2Load / 100;
          const timeSec = now / 1e3;
          ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
          ctx.lineWidth = 1;
          const gridSize = 30;
          for (let x = 0; x < width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
          }
          for (let y = 0; y < height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
          }
          const evaluatedNodes = SYSTEM_NODES.map((node) => {
            let dx = 0;
            let dy = 0;
            if (node.id === "sys1") {
              dx = Math.sin(timeSec * s1Speed) * 8;
              dy = Math.cos(timeSec * s1Speed * 1.3) * 8;
            } else if (node.id === "sys2") {
              dx = Math.cos(timeSec * 1.2) * (5 + s2Intensity * 15);
              dy = Math.sin(timeSec * 0.9) * (5 + s2Intensity * 15);
            } else {
              dx = Math.sin(timeSec * 1.5 + node.x * 10) * 3;
              dy = Math.cos(timeSec * 1.1 + node.y * 10) * 3;
            }
            return {
              ...node,
              pixelX: node.x * width + dx,
              pixelY: node.y * height + dy,
              currentRadius: node.baseRadius * (1 + Math.sin(timeSec * 3 + node.x * 5) * 0.08)
            };
          });
          evaluatedNodes.forEach((nodeA, i) => {
            evaluatedNodes.forEach((nodeB, j) => {
              if (i >= j) return;
              let isConnected = false;
              let signalPulse = false;
              let flowSpeed = 1;
              if (nodeA.id === "telemetry" && (nodeB.id === "sys1" || nodeB.id === "sys2")) isConnected = true;
              if (nodeA.id === "sys1" && nodeB.id === "uniforms") {
                isConnected = true;
                signalPulse = true;
                flowSpeed = s1Speed * 0.5;
              }
              if (nodeA.id === "sys2" && nodeB.id === "uniforms") {
                isConnected = true;
                signalPulse = true;
                flowSpeed = 1 + s2Intensity * 2;
              }
              if (nodeB.id === "gpu" && nodeA.id === "uniforms") isConnected = true;
              if (isConnected) {
                const grad = ctx.createLinearGradient(nodeA.pixelX, nodeA.pixelY, nodeB.pixelX, nodeB.pixelY);
                grad.addColorStop(0, nodeA.color);
                grad.addColorStop(1, nodeB.color);
                ctx.beginPath();
                ctx.moveTo(nodeA.pixelX, nodeA.pixelY);
                ctx.lineTo(nodeB.pixelX, nodeB.pixelY);
                ctx.strokeStyle = grad;
                ctx.lineWidth = 2 + (signalPulse ? s2Intensity * 3 : 0);
                ctx.globalAlpha = 0.4 + Math.sin(timeSec * 4) * 0.1;
                ctx.stroke();
                ctx.globalAlpha = 1;
                const totalParticles = signalPulse ? 3 : 1;
                for (let p = 0; p < totalParticles; p++) {
                  const offset = (timeSec * flowSpeed * 0.3 + p / totalParticles) % 1;
                  const px = nodeA.pixelX + (nodeB.pixelX - nodeA.pixelX) * offset;
                  const py = nodeA.pixelY + (nodeB.pixelY - nodeA.pixelY) * offset;
                  ctx.beginPath();
                  ctx.arc(px, py, 4 + (signalPulse ? s2Intensity * 2 : 0), 0, Math.PI * 2);
                  ctx.fillStyle = nodeB.color;
                  ctx.shadowColor = nodeB.color;
                  ctx.shadowBlur = 10;
                  ctx.fill();
                  ctx.shadowBlur = 0;
                }
              }
            });
          });
          evaluatedNodes.forEach((node) => {
            const pulseGlow = node.currentRadius * (1.3 + Math.sin(timeSec * 5) * 0.15);
            const auraGrad = ctx.createRadialGradient(
              node.pixelX,
              node.pixelY,
              node.currentRadius * 0.5,
              node.pixelX,
              node.pixelY,
              pulseGlow
            );
            auraGrad.addColorStop(0, node.color);
            auraGrad.addColorStop(0.3, node.color + "44");
            auraGrad.addColorStop(1, "transparent");
            ctx.fillStyle = auraGrad;
            ctx.beginPath();
            ctx.arc(node.pixelX, node.pixelY, pulseGlow, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(node.pixelX, node.pixelY, node.currentRadius, 0, Math.PI * 2);
            ctx.fillStyle = "#121620";
            ctx.strokeStyle = node.color;
            ctx.lineWidth = 3;
            ctx.fill();
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(node.pixelX, node.pixelY, 4, 0, Math.PI * 2);
            ctx.fillStyle = node.color;
            ctx.fill();
            ctx.fillStyle = "#ffffff";
            ctx.font = "medium 12px sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "top";
            ctx.fillText(node.name, node.pixelX, node.pixelY + node.currentRadius + 6);
          });
        }
      }
      setFrameTick((t) => t + 1);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying, dimensions, system1Reflex, system2Load]);
  const synergyScore = Math.min(100, Math.max(10, (system1Reflex + (100 - system2Load)) / 2)).toFixed(1);
  const latencyMs = Math.max(2, 120 - system1Reflex * 0.9 + system2Load * 0.5).toFixed(0);
  const gpuLoadPercent = Math.min(100, Math.max(5, system1Reflex * 0.4 + system2Load * 0.6)).toFixed(0);
  return /* @__PURE__ */ jsxs("div", { className: "w-full bg-card text-foreground flex flex-col font-sans", children: [
    /* @__PURE__ */ jsxs("div", { className: "relative w-full overflow-hidden border-b border-border bg-[#0c0e14]", children: [
      /* @__PURE__ */ jsx("div", { className: "absolute top-0 end-0 p-3 z-10 flex items-center justify-end pointer-events-none", children: /* @__PURE__ */ jsx(
        "button",
        {
          onClick: () => setIsPlaying(!isPlaying),
          "aria-label": isPlaying ? "Pause animation" : "Play animation",
          className: "w-9 h-9 rounded-full flex items-center justify-center cursor-pointer transition-colors shadow-none bg-muted/90 hover:bg-secondary-hover text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary pointer-events-auto relative overflow-visible after:absolute after:-inset-1",
          children: /* @__PURE__ */ jsx("span", { className: "material-icons !text-base", children: isPlaying ? "pause" : "play_arrow" })
        }
      ) }),
      /* @__PURE__ */ jsx("div", { ref: containerRef, className: "w-full h-full flex items-center justify-center", children: /* @__PURE__ */ jsx(
        "canvas",
        {
          ref: canvasRef,
          width: dimensions.width,
          height: dimensions.height,
          className: "block w-full h-auto aspect-video",
          role: "img",
          "aria-label": "Interactive procedural shader simulation representing System 1, System 2, Telemetry, and GPU Shaders working together as a biological system."
        }
      ) })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-center gap-x-4 sm:gap-x-8 md:gap-x-12 border-b border-border px-5 py-3 shrink-0", children: [
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "System Synergy" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          synergyScore,
          "%"
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Reflex Latency" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          latencyMs,
          "ms"
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "GPU Shaders" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          gpuLoadPercent,
          "% Load"
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsx("div", { className: "p-5 flex flex-col gap-3.5", children: /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3.5", children: [
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5 w-full", children: [
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "System 1 Reflexes" }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
          /* @__PURE__ */ jsxs(
            Slider.Root,
            {
              className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
              value: [system1Reflex],
              onValueChange: (val) => setSystem1Reflex(val[0]),
              max: 100,
              step: 1,
              "aria-label": "System 1 Reflexes",
              children: [
                /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                /* @__PURE__ */ jsx(
                  Slider.Thumb,
                  {
                    className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                    "aria-label": "System 1 Reflex value thumb"
                  }
                )
              ]
            }
          ),
          /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium tabular-nums text-end shrink-0 whitespace-nowrap w-[6ch]", children: [
            system1Reflex,
            "%"
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5 w-full", children: [
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "System 2 Cognitive Load" }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
          /* @__PURE__ */ jsxs(
            Slider.Root,
            {
              className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
              value: [system2Load],
              onValueChange: (val) => setSystem2Load(val[0]),
              max: 100,
              step: 1,
              "aria-label": "System 2 Cognitive Load",
              children: [
                /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                /* @__PURE__ */ jsx(
                  Slider.Thumb,
                  {
                    className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                    "aria-label": "System 2 Cognitive Load value thumb"
                  }
                )
              ]
            }
          ),
          /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium tabular-nums text-end shrink-0 whitespace-nowrap w-[6ch]", children: [
            system2Load,
            "%"
          ] })
        ] })
      ] })
    ] }) })
  ] });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsx(React.StrictMode, { children: /* @__PURE__ */ jsx(App, {}) })
);