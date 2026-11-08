import { jsx, jsxs } from 'https://widgetlibs.static.usercontent.goog/react/jsx-runtime-Dc9ViRTo.js';
import React, { useState, useRef, useEffect } from 'https://widgetlibs.static.usercontent.goog/react-Dd1pKoqe.js';
import ReactDOM from 'https://widgetlibs.static.usercontent.goog/react-dom/client-BTuQ-l8_.js';
import * as Slider from 'https://widgetlibs.static.usercontent.goog/@radix-ui/react-slider-DXk-CvUR.js';
import { ErrorBoundary } from 'https://widgetlibs.static.usercontent.goog/react-error-boundary-BY2GTZrN.js';

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

function FallbackComponent() {
  return /* @__PURE__ */ jsx("div", { className: "p-5 text-error text-sm font-medium", children: "An error occurred inside the interaction net simulation." });
}
function InteractionNetWidget() {
  const [swarmActivity, setSwarmActivity] = useState([45]);
  const [reductionSpeed, setReductionSpeed] = useState([60]);
  const [attributionMode, setAttributionMode] = useState("strict");
  const [isPlaying, setIsPlaying] = useState(true);
  const [, setFrameTick] = useState(0);
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 450 });
  const nodesRef = useRef([]);
  const edgesRef = useRef([]);
  const lastTimeRef = useRef(performance.now());
  const [metrics, setMetrics] = useState({
    reductionsSec: 0,
    systemTension: 0,
    metabolicBudget: 100
  });
  useEffect(() => {
    if (!canvasRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width: width2 } = entry.contentRect;
        const boundedWidth = Math.max(width2, 360);
        setDimensions({
          width: boundedWidth,
          height: boundedWidth * 0.5625
          // 16:9 Landscape Forced
        });
      }
    });
    resizeObserver.observe(canvasRef.current);
    return () => resizeObserver.disconnect();
  }, []);
  useEffect(() => {
    const initialNodes = [
      { id: "a1", type: "agent", label: "M1_Max_Swarm_Alpha", x: 200, y: 150, vx: 0, vy: 0, metabolicCost: 12, tension: 0.1, provenanceHash: "0x8f2d" },
      { id: "a2", type: "agent", label: "M1_Max_Swarm_Beta", x: 600, y: 300, vx: 0, vy: 0, metabolicCost: 15, tension: 0.2, provenanceHash: "0x3a9e" },
      { id: "c1", type: "code_block", label: "Core_IP_Kernel", x: 400, y: 220, vx: 0, vy: 0, metabolicCost: 8, tension: 0.4, provenanceHash: "0x7bc1" },
      { id: "c2", type: "code_block", label: "Morphed_DSL_v2", x: 300, y: 320, vx: 0, vy: 0, metabolicCost: 22, tension: 0.7, provenanceHash: "0xef41" },
      { id: "c3", type: "net_construct", label: "Unified_Net_Combinator", x: 500, y: 120, vx: 0, vy: 0, metabolicCost: 34, tension: 0.5, provenanceHash: "0x91da" }
    ];
    const initialEdges = [
      { id: "e1", source: "a1", target: "c1", weight: 0.8, type: "contains" },
      { id: "e2", source: "a2", target: "c2", weight: 1.2, type: "morphs" },
      { id: "e3", source: "c2", target: "c1", weight: 1.5, type: "morphs" },
      { id: "e4", source: "a1", target: "c3", weight: 0.6, type: "executes" },
      { id: "e5", source: "c3", target: "a2", weight: 0.9, type: "contains" }
    ];
    nodesRef.current = initialNodes;
    edgesRef.current = initialEdges;
  }, []);
  useEffect(() => {
    if (!isPlaying) return;
    lastTimeRef.current = performance.now();
    let frameId;
    const tick = (now) => {
      const delta = Math.min((now - lastTimeRef.current) / 1e3, 0.1);
      lastTimeRef.current = now;
      const nodes = nodesRef.current;
      const edges = edgesRef.current;
      const { width: width2, height: height2 } = dimensions;
      if (nodes.length === 0) {
        frameId = requestAnimationFrame(tick);
        return;
      }
      const activityFactor = swarmActivity[0] / 50;
      const speedFactor = reductionSpeed[0] / 50;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 1200 / (dist * dist) * activityFactor;
          if (dist < 250) {
            const fx = dx / dist * force;
            const fy = dy / dist * force;
            nodes[i].vx -= fx;
            nodes[i].vy -= fy;
            nodes[j].vx += fx;
            nodes[j].vy += fy;
          }
        }
      }
      edges.forEach((edge) => {
        const sourceNode = nodes.find((n) => n.id === edge.source);
        const targetNode = nodes.find((n) => n.id === edge.target);
        if (sourceNode && targetNode) {
          const dx = targetNode.x - sourceNode.x;
          const dy = targetNode.y - sourceNode.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const targetDist = 140;
          const springForce = (dist - targetDist) * 0.4 * edge.weight * speedFactor;
          const fx = dx / dist * springForce;
          const fy = dy / dist * springForce;
          sourceNode.vx += fx;
          sourceNode.vy += fy;
          targetNode.vx -= fx;
          targetNode.vy -= fy;
        }
      });
      let totalTension = 0;
      let totalMetabolicLoad = 0;
      nodes.forEach((node) => {
        const cx = width2 / 2;
        const cy = height2 / 2;
        node.vx += (cx - node.x) * 0.05 * activityFactor;
        node.vy += (cy - node.y) * 0.05 * activityFactor;
        node.x += node.vx * delta * 15;
        node.y += node.vy * delta * 15;
        node.vx *= 0.82;
        node.vy *= 0.82;
        const pad = 40;
        if (node.x < pad) {
          node.x = pad;
          node.vx *= -0.5;
        }
        if (node.x > width2 - pad) {
          node.x = width2 - pad;
          node.vx *= -0.5;
        }
        if (node.y < pad) {
          node.y = pad;
          node.vy *= -0.5;
        }
        if (node.y > height2 - pad) {
          node.y = height2 - pad;
          node.vy *= -0.5;
        }
        const instantaneousTension = Math.sqrt(node.vx * node.vx + node.vy * node.vy);
        node.tension = Math.min(Math.max(instantaneousTension / 12, 0.1), 1);
        totalTension += node.tension;
        const baseMetabolic = node.type === "agent" ? 25 : node.type === "code_block" ? 12 : 18;
        node.metabolicCost = baseMetabolic * (1 + node.tension * 0.5) * activityFactor;
        totalMetabolicLoad += node.metabolicCost;
      });
      if (Math.random() < 0.03 * activityFactor) {
        const randNode = nodes[Math.floor(Math.random() * nodes.length)];
        if (randNode) {
          const hex = Math.floor(Math.random() * 65535).toString(16).padStart(4, "0");
          randNode.provenanceHash = `0x${hex}`;
        }
      }
      const computedReductions = speedFactor * 8.4 + totalTension / nodes.length * 4.2;
      const avgTension = totalTension / nodes.length;
      const attributionEfficiency = attributionMode === "strict" ? 0.95 : attributionMode === "fluid" ? 1.25 : 1;
      const budgetLeft = Math.max(140 - totalMetabolicLoad * 0.8 * attributionEfficiency, 10);
      setMetrics({
        reductionsSec: computedReductions,
        systemTension: avgTension,
        metabolicBudget: budgetLeft
      });
      setFrameTick((t) => t + 1);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying, swarmActivity, reductionSpeed, attributionMode, dimensions]);
  const { width, height } = dimensions;
  return /* @__PURE__ */ jsxs("div", { className: "w-full bg-card text-foreground font-sans select-none overflow-hidden", children: [
    /* @__PURE__ */ jsxs("div", { ref: canvasRef, className: "relative w-full overflow-hidden border-b border-border bg-[#0d0f14]", children: [
      /* @__PURE__ */ jsx("div", { className: "absolute top-0 end-0 p-3 z-10 flex items-center justify-end pointer-events-none", children: /* @__PURE__ */ jsx(
        "button",
        {
          onClick: () => setIsPlaying(!isPlaying),
          className: "w-9 h-9 rounded-full flex items-center justify-center cursor-pointer transition-colors shadow-none bg-zinc-800/90 hover:bg-zinc-700 text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-primary pointer-events-auto relative overflow-visible after:absolute after:-inset-1",
          "aria-label": isPlaying ? "Pause net reduction simulation" : "Play net reduction simulation",
          children: /* @__PURE__ */ jsx("span", { className: "material-icons !text-base", children: isPlaying ? "pause" : "play_arrow" })
        }
      ) }),
      /* @__PURE__ */ jsxs("div", { className: "absolute top-0 start-0 p-4 pointer-events-none flex flex-col gap-1 text-[11px] font-medium tracking-wide", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-1.5 text-blue-400", children: [
          /* @__PURE__ */ jsx("span", { className: "w-2 h-2 rounded-full bg-blue-400" }),
          " Swarm Agent Node"
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-1.5 text-emerald-400", children: [
          /* @__PURE__ */ jsx("span", { className: "w-2 h-2 rounded-full bg-emerald-400" }),
          " Immutable IP Block"
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-1.5 text-amber-400", children: [
          /* @__PURE__ */ jsx("span", { className: "w-2 h-2 rounded-full bg-amber-400" }),
          " Morph Net Construct"
        ] })
      ] }),
      /* @__PURE__ */ jsxs(
        "svg",
        {
          role: "img",
          "aria-label": "Interactive graph tracking interaction net reductions, cryptographic IP provenance mutation, and metabolic budget alignment",
          viewBox: `0 0 ${width} ${height}`,
          className: "w-full h-full block",
          children: [
            /* @__PURE__ */ jsx("defs", { children: /* @__PURE__ */ jsx("pattern", { id: "grid-pattern", width: "40", height: "40", patternUnits: "userSpaceOnUse", children: /* @__PURE__ */ jsx("path", { d: "M 40 0 L 0 0 0 40", fill: "none", stroke: "#ffffff", strokeOpacity: "0.03", strokeWidth: "1" }) }) }),
            /* @__PURE__ */ jsx("rect", { width: "100%", height: "100%", fill: "url(#grid-pattern)" }),
            edgesRef.current.map((edge) => {
              const src = nodesRef.current.find((n) => n.id === edge.source);
              const tgt = nodesRef.current.find((n) => n.id === edge.target);
              if (!src || !tgt) return null;
              let strokeColor = "#3b82f6";
              if (edge.type === "morphs") strokeColor = "#10b981";
              if (edge.type === "executes") strokeColor = "#f59e0b";
              const avgNodeTension = (src.tension + tgt.tension) / 2;
              return /* @__PURE__ */ jsxs("g", { children: [
                /* @__PURE__ */ jsx(
                  "line",
                  {
                    x1: src.x,
                    y1: src.y,
                    x2: tgt.x,
                    y2: tgt.y,
                    stroke: strokeColor,
                    strokeWidth: 1.5 + avgNodeTension * 3,
                    strokeOpacity: 0.4 + avgNodeTension * 0.5,
                    strokeDasharray: edge.type === "morphs" ? "4 4" : void 0
                  }
                ),
                isPlaying && /* @__PURE__ */ jsx(
                  "circle",
                  {
                    cx: src.x + (tgt.x - src.x) * (performance.now() * 15e-4 * edge.weight % 1),
                    cy: src.y + (tgt.y - src.y) * (performance.now() * 15e-4 * edge.weight % 1),
                    r: 2.5,
                    fill: "#ffffff",
                    opacity: 0.8
                  }
                )
              ] }, edge.id);
            }),
            nodesRef.current.map((node) => {
              let fillColor = "#1e40af";
              let borderColor = "#3b82f6";
              if (node.type === "code_block") {
                fillColor = "#065f46";
                borderColor = "#10b981";
              } else if (node.type === "net_construct") {
                fillColor = "#92400e";
                borderColor = "#f59e0b";
              }
              const radius = node.type === "agent" ? 16 : 13;
              const dynamicScale = 1 + node.tension * 0.25;
              return /* @__PURE__ */ jsxs("g", { className: "cursor-pointer", children: [
                /* @__PURE__ */ jsx(
                  "circle",
                  {
                    cx: node.x,
                    cy: node.y,
                    r: radius * dynamicScale + 5,
                    fill: "none",
                    stroke: borderColor,
                    strokeWidth: 1,
                    strokeOpacity: 0.3,
                    strokeDasharray: attributionMode === "strict" ? void 0 : "3 2"
                  }
                ),
                /* @__PURE__ */ jsx(
                  "circle",
                  {
                    cx: node.x,
                    cy: node.y,
                    r: radius * dynamicScale,
                    fill: fillColor,
                    stroke: borderColor,
                    strokeWidth: 2
                  }
                ),
                /* @__PURE__ */ jsx(
                  "text",
                  {
                    x: node.x,
                    y: node.y - radius * dynamicScale - 8,
                    textAnchor: "middle",
                    fill: "#94a3b8",
                    fontSize: 11,
                    fontFamily: "monospace",
                    className: "pointer-events-none select-none",
                    children: node.provenanceHash
                  }
                ),
                /* @__PURE__ */ jsx(
                  "text",
                  {
                    x: node.x,
                    y: node.y + radius * dynamicScale + 14,
                    textAnchor: "middle",
                    fill: "#f1f5f9",
                    fontSize: 11,
                    fontWeight: "normal",
                    className: "pointer-events-none select-none",
                    children: node.label
                  }
                )
              ] }, node.id);
            })
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-center gap-x-4 sm:gap-x-8 md:gap-x-12 border-b border-border px-5 py-3 shrink-0", children: [
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Net Reductions" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          metrics.reductionsSec.toFixed(1),
          "/s"
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "System Tension" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          (metrics.systemTension * 100).toFixed(1),
          "%"
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Metabolic Alloc" }),
        /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: [
          metrics.metabolicBudget.toFixed(1),
          " W"
        ] })
      ] })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "p-5 flex flex-col gap-4", children: [
      /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5 w-full", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Swarm Activity Level" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                value: swarmActivity,
                onValueChange: setSwarmActivity,
                max: 100,
                min: 10,
                step: 1,
                "aria-label": "Swarm Activity Level",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(
                    Slider.Thumb,
                    {
                      className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                      "aria-label": "Swarm activity thumb selector"
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums w-[6ch] text-end shrink-0 whitespace-nowrap", children: [
              swarmActivity[0],
              "%"
            ] })
          ] })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5 w-full", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Net Reduction Rate" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                value: reductionSpeed,
                onValueChange: setReductionSpeed,
                max: 100,
                min: 5,
                step: 1,
                "aria-label": "Net Reduction Rate",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(
                    Slider.Thumb,
                    {
                      className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                      "aria-label": "Net reduction speed thumb selector"
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium text-foreground tabular-nums w-[6ch] text-end shrink-0 whitespace-nowrap", children: [
              reductionSpeed[0],
              "%"
            ] })
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5 w-full sm:max-w-xs", children: [
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Provenance Attribution Constraint" }),
        /* @__PURE__ */ jsxs("div", { className: "relative h-9 rounded-lg bg-muted px-3 pointer-events-none flex items-center justify-between", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-foreground", children: attributionMode === "strict" ? "Strict Cryptographic Guard" : attributionMode === "fluid" ? "Fluid Morphic Exchange" : "Balanced Unified Protocol" }),
          /* @__PURE__ */ jsx("span", { className: "material-icons expand_more absolutely end-2.5 top-1/2 -translate-y-1/2 pointer-events-none !text-base", children: "expand_more" }),
          /* @__PURE__ */ jsxs(
            "select",
            {
              value: attributionMode,
              onChange: (e) => setAttributionMode(e.target.value),
              className: "absolute inset-x-0 top-1/2 -translate-y-1/2 h-11 w-full opacity-0 cursor-pointer pointer-events-auto",
              "aria-label": "Provenance Attribution Constraint Mode Selection",
              children: [
                /* @__PURE__ */ jsx("option", { value: "strict", children: "Strict Cryptographic Guard" }),
                /* @__PURE__ */ jsx("option", { value: "balanced", children: "Balanced Unified Protocol" }),
                /* @__PURE__ */ jsx("option", { value: "fluid", children: "Fluid Morphic Exchange" })
              ]
            }
          )
        ] })
      ] })
    ] })
  ] });
}
function App() {
  return /* @__PURE__ */ jsx(ErrorBoundary, { FallbackComponent, children: /* @__PURE__ */ jsx(InteractionNetWidget, {}) });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsx(React.StrictMode, { children: /* @__PURE__ */ jsx(App, {}) })
);