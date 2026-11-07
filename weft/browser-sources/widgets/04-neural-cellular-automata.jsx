import { jsx, jsxs } from 'https://widgetlibs.static.usercontent.goog/react/jsx-runtime-Dc9ViRTo.js';
import React, { useState, useRef, useEffect } from 'https://widgetlibs.static.usercontent.goog/react-Dd1pKoqe.js';
import ReactDOM from 'https://widgetlibs.static.usercontent.goog/react-dom/client-BTuQ-l8_.js';
import { ErrorBoundary } from 'https://widgetlibs.static.usercontent.goog/react-error-boundary-BY2GTZrN.js';
import * as ToggleGroup from 'https://widgetlibs.static.usercontent.goog/@radix-ui/react-toggle-group-SAzue8E6.js';
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

function ErrorFallback({ error }) {
  return /* @__PURE__ */ jsxs("div", { className: "p-5 text-error bg-card rounded-lg border border-border", children: [
    /* @__PURE__ */ jsx("p", { className: "text-sm font-medium", children: "Simulation Error:" }),
    /* @__PURE__ */ jsx("pre", { className: "text-xs mt-1 overflow-auto", children: error.message })
  ] });
}
const COLS = 56;
const ROWS = 32;
const TOTAL_CELLS = COLS * ROWS;
const TARGET_GRID = new Float32Array(TOTAL_CELLS);
const TARGET_R = new Float32Array(TOTAL_CELLS);
const TARGET_G = new Float32Array(TOTAL_CELLS);
const TARGET_B = new Float32Array(TOTAL_CELLS);
for (let r = 0; r < ROWS; r++) {
  for (let c = 0; c < COLS; c++) {
    const idx = r * COLS + c;
    const dx = c - COLS / 2;
    const dy = r - ROWS / 2;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < 11 && dist > 3) {
      TARGET_GRID[idx] = 1;
      const angle = Math.atan2(dy, dx);
      TARGET_R[idx] = Math.sin(angle) * 0.5 + 0.5;
      TARGET_G[idx] = Math.cos(angle * 1.5) * 0.5 + 0.5;
      TARGET_B[idx] = Math.sin(angle + 2) * 0.5 + 0.5;
    } else if (dist <= 3) {
      TARGET_GRID[idx] = 1;
      TARGET_R[idx] = 1;
      TARGET_G[idx] = 0.8;
      TARGET_B[idx] = 0.2;
    } else {
      TARGET_GRID[idx] = 0;
    }
  }
}
function App() {
  return /* @__PURE__ */ jsx(ErrorBoundary, { FallbackComponent: ErrorFallback, children: /* @__PURE__ */ jsx(NCASimulator, {}) });
}
function NCASimulator() {
  const [growthRate, setGrowthRate] = useState(0.6);
  const [propagation, setPropagation] = useState(0.7);
  const [interactionMode, setInteractionMode] = useState("damage");
  const [isPlaying, setIsPlaying] = useState(true);
  const [frameTick, setFrameTick] = useState(0);
  const [alivePercent, setAlivePercent] = useState("0.0%");
  const [stabilityScore, setStabilityScore] = useState("100%");
  const [regenRateStr, setRegenRateStr] = useState("0.0");
  const CHANNELS = 8;
  const gridRef = useRef(new Float32Array(TOTAL_CELLS * CHANNELS));
  const nextGridRef = useRef(new Float32Array(TOTAL_CELLS * CHANNELS));
  const lastTimeRef = useRef(performance.now());
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 430 });
  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const w = entry.contentRect.width || 800;
        const computedHeight = w * 0.52;
        setDimensions({ width: w, height: computedHeight });
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);
  const resetToSeed = () => {
    gridRef.current.fill(0);
    const midR = Math.floor(ROWS / 2);
    const midC = Math.floor(COLS / 2);
    const midIdx = (midR * COLS + midC) * CHANNELS;
    gridRef.current[midIdx] = 1;
    gridRef.current[midIdx + 1] = 1;
    gridRef.current[midIdx + 2] = 0.4;
    gridRef.current[midIdx + 3] = 0.9;
    for (let h = 4; h < CHANNELS; h++) {
      gridRef.current[midIdx + h] = 1;
    }
  };
  useEffect(() => {
    resetToSeed();
  }, []);
  useEffect(() => {
    if (!isPlaying) return;
    lastTimeRef.current = performance.now();
    let frameId;
    const tick = (now) => {
      Math.min((now - lastTimeRef.current) / 1e3, 0.1);
      lastTimeRef.current = now;
      const current2 = gridRef.current;
      const next = nextGridRef.current;
      let totalAlive = 0;
      let diffSum = 0;
      let targetActiveCount = 0;
      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const idx = (r * COLS + c) * CHANNELS;
          const isTargetAlive = TARGET_GRID[r * COLS + c] > 0;
          if (isTargetAlive) targetActiveCount++;
          const neighbors = [
            { dr: -1, dc: 0, w: 0.5 },
            { dr: 1, dc: 0, w: 0.5 },
            { dr: 0, dc: -1, w: 0.5 },
            { dr: 0, dc: 1, w: 0.5 },
            { dr: -1, dc: -1, w: 0.25 },
            { dr: -1, dc: 1, w: 0.25 },
            { dr: 1, dc: -1, w: 0.25 },
            { dr: 1, dc: 1, w: 0.25 }
          ];
          const perceived = new Float32Array(CHANNELS);
          for (let ch = 0; ch < CHANNELS; ch++) {
            perceived[ch] = current2[idx + ch] * -1;
          }
          let aliveNeighborsCount = 0;
          for (const n of neighbors) {
            const nr = (r + n.dr + ROWS) % ROWS;
            const nc = (c + n.dc + COLS) % COLS;
            const nIdx = (nr * COLS + nc) * CHANNELS;
            if (current2[nIdx] > 0.1) {
              aliveNeighborsCount++;
            }
            for (let ch = 0; ch < CHANNELS; ch++) {
              perceived[ch] += current2[nIdx + ch] * n.w;
            }
          }
          const isCurrentlyAlive = current2[idx] > 0.1;
          const willBeAlive = isCurrentlyAlive || aliveNeighborsCount >= 1;
          if (!willBeAlive) {
            for (let ch = 0; ch < CHANNELS; ch++) {
              next[idx + ch] = 0;
            }
            if (isTargetAlive) diffSum += 1;
            continue;
          }
          const targetAlpha = TARGET_GRID[r * COLS + c];
          const targetR = TARGET_R[r * COLS + c];
          const targetG = TARGET_G[r * COLS + c];
          const targetB = TARGET_B[r * COLS + c];
          const dAlpha = (targetAlpha - current2[idx]) * growthRate * 0.35 + perceived[0] * 0.1;
          next[idx] = Math.max(0, Math.min(1, current2[idx] + dAlpha));
          if (next[idx] > 0.1) {
            totalAlive++;
          }
          const hiddenInfluence = perceived[4] * propagation * 0.25;
          const dR = (targetR - current2[idx + 1]) * growthRate * 0.4 + hiddenInfluence + perceived[1] * 0.05;
          const dG = (targetG - current2[idx + 2]) * growthRate * 0.4 + hiddenInfluence + perceived[2] * 0.05;
          const dB = (targetB - current2[idx + 3]) * growthRate * 0.4 + hiddenInfluence + perceived[3] * 0.05;
          next[idx + 1] = Math.max(0, Math.min(1, current2[idx + 1] + dR));
          next[idx + 2] = Math.max(0, Math.min(1, current2[idx + 2] + dG));
          next[idx + 3] = Math.max(0, Math.min(1, current2[idx + 3] + dB));
          for (let h = 4; h < CHANNELS; h++) {
            const dHidden = perceived[h] * propagation - current2[idx + h] * 0.05;
            next[idx + h] = Math.max(-1, Math.min(1, current2[idx + h] + dHidden));
          }
          if (targetAlpha > 0) {
            const diff = Math.abs(next[idx + 1] - targetR) + Math.abs(next[idx + 2] - targetG);
            diffSum += diff / 2;
          } else {
            if (next[idx] > 0.2) diffSum += 0.4;
          }
        }
      }
      gridRef.current = next;
      nextGridRef.current = current2;
      const alivePctVal = (totalAlive / TOTAL_CELLS * 100).toFixed(1) + "%";
      const calculatedStability = Math.max(0, Math.min(100, Math.round(100 - diffSum / Math.max(1, targetActiveCount) * 100)));
      const stabilityVal = calculatedStability + "%";
      const actualRegenRate = (growthRate * propagation * 4.5).toFixed(1);
      setAlivePercent(alivePctVal);
      setStabilityScore(stabilityVal);
      setRegenRateStr(actualRegenRate);
      setFrameTick((t) => t + 1);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying, growthRate, propagation]);
  const handleCanvasInteraction = (e) => {
    if (!containerRef.current) return;
    if (e.target.closest("button")) return;
    const rect = e.currentTarget.getBoundingClientRect();
    let clientX = 0;
    let clientY = 0;
    if ("touches" in e) {
      if (e.touches.length === 0) return;
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }
    const mouseX = clientX - rect.left;
    const mouseY = clientY - rect.top;
    const targetCol = Math.floor(mouseX / rect.width * COLS);
    const targetRow = Math.floor(mouseY / rect.height * ROWS);
    const radius = interactionMode === "damage" ? 4 : 2;
    const current2 = gridRef.current;
    for (let r = targetRow - radius; r <= targetRow + radius; r++) {
      for (let c = targetCol - radius; c <= targetCol + radius; c++) {
        if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
          const cellIdx = (r * COLS + c) * CHANNELS;
          const dist = Math.sqrt((r - targetRow) ** 2 + (c - targetCol) ** 2);
          if (dist <= radius) {
            if (interactionMode === "damage") {
              for (let ch = 0; ch < CHANNELS; ch++) {
                current2[cellIdx + ch] = 0;
              }
            } else {
              current2[cellIdx] = 1;
              current2[cellIdx + 1] = 0.2;
              current2[cellIdx + 2] = 0.9;
              current2[cellIdx + 3] = 1;
              for (let ch = 4; ch < CHANNELS; ch++) {
                current2[cellIdx + ch] = 1;
              }
            }
          }
        }
      }
    }
    setFrameTick((t) => t + 1);
  };
  const gridCells = [];
  const current = gridRef.current;
  const cellWidthPct = 100 / COLS;
  const cellHeightPct = 100 / ROWS;
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const idx = (r * COLS + c) * CHANNELS;
      const alpha = current[idx];
      if (alpha > 0.05) {
        const rVal = Math.floor(current[idx + 1] * 255);
        const gVal = Math.floor(current[idx + 2] * 255);
        const bVal = Math.floor(current[idx + 3] * 255);
        const hiddenMagnitude = Math.abs(current[idx + 4]);
        const cellColor = `rgba(${rVal}, ${gVal}, ${bVal}, ${Math.min(1, alpha + 0.1)})`;
        gridCells.push(
          /* @__PURE__ */ jsx(
            "rect",
            {
              x: `${c * cellWidthPct}%`,
              y: `${r * cellHeightPct}%`,
              width: `${cellWidthPct - 0.2}%`,
              height: `${cellHeightPct - 0.2}%`,
              fill: cellColor,
              rx: hiddenMagnitude > 0.5 ? 2 : 0
            },
            `${r}-${c}`
          )
        );
      } else if (TARGET_GRID[r * COLS + c] > 0) {
        gridCells.push(
          /* @__PURE__ */ jsx(
            "rect",
            {
              x: `${c * cellWidthPct}%`,
              y: `${r * cellHeightPct}%`,
              width: `${cellWidthPct - 0.2}%`,
              height: `${cellHeightPct - 0.2}%`,
              fill: "rgba(255, 255, 255, 0.03)",
              stroke: "rgba(255, 255, 255, 0.06)",
              strokeWidth: 0.5
            },
            `ghost-${r}-${c}`
          )
        );
      }
    }
  }
  return /* @__PURE__ */ jsxs("div", { className: "w-full bg-card text-foreground font-sans flex flex-col selection:bg-primary/20", children: [
    /* @__PURE__ */ jsxs(
      "div",
      {
        ref: containerRef,
        className: "relative w-full overflow-hidden border-b border-border bg-[#0d0e12]",
        style: { height: dimensions.height },
        children: [
          /* @__PURE__ */ jsxs(
            "svg",
            {
              role: "img",
              "aria-label": "Neural Cellular Automata grid simulation illustrating self-repair and localized hidden state coordination",
              className: "w-full h-full cursor-crosshair select-none touch-none",
              viewBox: `0 0 ${dimensions.width} ${dimensions.height}`,
              onMouseDown: handleCanvasInteraction,
              onMouseMove: (e) => {
                if (e.buttons === 1) handleCanvasInteraction(e);
              },
              onTouchStart: handleCanvasInteraction,
              onTouchMove: handleCanvasInteraction,
              children: [
                gridCells,
                /* @__PURE__ */ jsx(
                  "circle",
                  {
                    cx: "50%",
                    cy: "50%",
                    r: dimensions.height * 0.3,
                    fill: "none",
                    stroke: "rgba(51, 110, 243, 0.12)",
                    strokeWidth: "1.5",
                    strokeDasharray: "4 4"
                  }
                )
              ]
            }
          ),
          /* @__PURE__ */ jsx("div", { className: "absolute top-0 end-0 p-3 z-10 flex items-center justify-end pointer-events-none", children: /* @__PURE__ */ jsx(
            "button",
            {
              type: "button",
              onClick: () => setIsPlaying(!isPlaying),
              className: "w-9 h-9 rounded-full flex items-center justify-center cursor-pointer transition-colors shadow-none bg-muted/90 hover:bg-secondary-hover text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary pointer-events-auto relative overflow-visible after:absolute after:-inset-1",
              "aria-label": isPlaying ? "Pause simulation loop" : "Play simulation loop",
              children: /* @__PURE__ */ jsx("span", { className: "material-icons !text-base", children: isPlaying ? "pause" : "play_arrow" })
            }
          ) }),
          /* @__PURE__ */ jsxs("div", { className: "absolute bottom-3 start-3 pointer-events-none flex flex-col gap-1 bg-[#16181f]/90 p-2 rounded border border-white/5", children: [
            /* @__PURE__ */ jsx("span", { className: "text-white/40 text-[10px] tracking-wider font-medium", children: "Grid Framework" }),
            /* @__PURE__ */ jsx("span", { className: "text-white/80 text-xs font-normal font-mono", children: "56×32 Mini-Models" })
          ] })
        ]
      }
    ),
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-center gap-x-4 sm:gap-x-8 md:gap-x-12 border-b border-border px-5 py-3 shrink-0", children: [
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Active Biomass" }),
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: alivePercent })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Morph Stability" }),
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: stabilityScore })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Flux Velocity" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          regenRateStr,
          "x"
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "p-5 flex flex-col gap-4", children: [
      /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Growth Coefficient" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                value: [growthRate],
                onValueChange: (val) => setGrowthRate(val[0]),
                min: 0.1,
                max: 1,
                step: 0.05,
                "aria-label": "Growth Coefficient Slider",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(
                    Slider.Thumb,
                    {
                      className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                      "aria-label": "Growth Rate thumb value picker"
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsx("span", { className: "text-sm font-medium tabular-nums text-end shrink-0 w-[6ch]", children: growthRate.toFixed(2) })
          ] })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Hidden Propagation" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                value: [propagation],
                onValueChange: (val) => setPropagation(val[0]),
                min: 0,
                max: 1,
                step: 0.05,
                "aria-label": "Hidden Propagation Slider",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(
                    Slider.Thumb,
                    {
                      className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                      "aria-label": "Propagation coupling thumb value picker"
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsx("span", { className: "text-sm font-medium tabular-nums text-end shrink-0 w-[6ch]", children: propagation.toFixed(2) })
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-border/60", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 min-w-[240px]", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground whitespace-nowrap", children: "Pointer Mode" }),
          /* @__PURE__ */ jsxs(
            ToggleGroup.Root,
            {
              type: "single",
              value: interactionMode,
              onValueChange: (val) => {
                if (val) setInteractionMode(val);
              },
              className: "rounded-full flex w-full bg-muted h-9 p-1",
              "aria-label": "Canvas touch interaction mode selector toggle",
              children: [
                /* @__PURE__ */ jsx(
                  ToggleGroup.Item,
                  {
                    value: "damage",
                    className: "flex-1 min-w-0 text-center px-3 rounded-full text-sm font-medium text-muted-foreground data-[state=on]:bg-primary data-[state=on]:text-white transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 overflow-visible",
                    title: "Distort and excise active pixel sectors",
                    children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Excision Damage" })
                  }
                ),
                /* @__PURE__ */ jsx(
                  ToggleGroup.Item,
                  {
                    value: "seed",
                    className: "flex-1 min-w-0 text-center px-3 rounded-full text-sm font-medium text-muted-foreground data-[state=on]:bg-primary data-[state=on]:text-white transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 overflow-visible",
                    title: "Inject localized seed arrays into canvas grid",
                    children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Stimulate Seed" })
                  }
                )
              ]
            }
          )
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-2", children: [
          /* @__PURE__ */ jsx(
            "button",
            {
              type: "button",
              onClick: resetToSeed,
              className: "rounded-full text-sm font-medium h-9 px-4 whitespace-nowrap bg-muted hover:text-foreground text-muted-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:-inset-y-1 after:inset-x-0 overflow-visible",
              children: "Re-Seed Organism"
            }
          ),
          /* @__PURE__ */ jsx(
            "button",
            {
              type: "button",
              onClick: () => {
                gridRef.current.fill(0);
                setFrameTick((t) => t + 1);
              },
              className: "rounded-full text-sm font-medium h-9 px-4 whitespace-nowrap bg-muted text-error hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:-inset-y-1 after:inset-x-0 overflow-visible",
              children: "Clear Matrix"
            }
          )
        ] })
      ] })
    ] })
  ] });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsx(React.StrictMode, { children: /* @__PURE__ */ jsx(App, {}) })
);