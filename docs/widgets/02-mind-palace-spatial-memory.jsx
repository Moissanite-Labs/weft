import { jsx, jsxs } from 'https://widgetlibs.static.usercontent.goog/react/jsx-runtime-Dc9ViRTo.js';
import React, { useState, useRef, useEffect, useMemo } from 'https://widgetlibs.static.usercontent.goog/react-Dd1pKoqe.js';
import ReactDOM from 'https://widgetlibs.static.usercontent.goog/react-dom/client-BTuQ-l8_.js';
import * as ToggleGroup from 'https://widgetlibs.static.usercontent.goog/@radix-ui/react-toggle-group-SAzue8E6.js';
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

const ErrorFallback = () => /* @__PURE__ */ jsx("div", { className: "p-5 text-error text-sm font-medium bg-card", children: "Something went wrong displaying the SDF Visualizer." });
function sdfCircle(x, y, cx, cy, r) {
  const dx = x - cx;
  const dy = y - cy;
  return Math.sqrt(dx * dx + dy * dy) - r;
}
function sdfBox(x, y, cx, cy, sx, sy) {
  const dx = Math.abs(x - cx) - sx;
  const dy = Math.abs(y - cy) - sy;
  const outsideDist = Math.sqrt(Math.max(dx, 0) ** 2 + Math.max(dy, 0) ** 2);
  const insideDist = Math.min(Math.max(dx, dy), 0);
  return outsideDist + insideDist;
}
function smin(a, b, k) {
  if (k <= 0) return Math.min(a, b);
  const h = Math.max(k - Math.abs(a - b), 0) / k;
  return Math.min(a, b) - h * h * h * k * (1 / 6);
}
function App() {
  return /* @__PURE__ */ jsx(ErrorBoundary, { FallbackComponent: ErrorFallback, children: /* @__PURE__ */ jsx(SdfVisualizer, {}) });
}
function SdfVisualizer() {
  const aspect = 16 / 9;
  const [width, setWidth] = useState(800);
  const containerRef = useRef(null);
  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width) {
          setWidth(Math.max(entry.contentRect.width, 360));
        }
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);
  const height = width / aspect;
  const [operation, setOperation] = useState("union");
  const [smoothK, setSmoothK] = useState(35);
  const [shapeSeparation, setShapeSeparation] = useState(120);
  const [probePos, setProbePos] = useState(null);
  const centerX = width / 2;
  const centerY = height / 2;
  const circleX = centerX - shapeSeparation / 2;
  const circleY = centerY;
  const circleRadius = Math.min(width * 0.12, 90);
  const boxX = centerX + shapeSeparation / 2;
  const boxY = centerY;
  const boxW = Math.min(width * 0.11, 80);
  const boxH = Math.min(width * 0.11, 80);
  const getSdfValue = (x, y) => {
    const dCircle = sdfCircle(x, y, circleX, circleY, circleRadius);
    const dBox = sdfBox(x, y, boxX, boxY, boxW, boxH);
    switch (operation) {
      case "union":
        return Math.min(dCircle, dBox);
      case "subtraction":
        return Math.max(-dCircle, dBox);
      case "intersection":
        return Math.max(dCircle, dBox);
      case "smooth_union":
        return smin(dCircle, dBox, smoothK);
      default:
        return Math.min(dCircle, dBox);
    }
  };
  const isolineLevels = useMemo(() => {
    const levels = [];
    for (let i = -60; i < 0; i += 15) levels.push(i);
    for (let i = 15; i <= 180; i += 20) levels.push(i);
    return levels;
  }, []);
  const probeSdf = probePos ? getSdfValue(probePos.x, probePos.y) : null;
  useEffect(() => {
    setProbePos({ x: centerX - 40, y: centerY - 40 });
  }, [centerX, centerY]);
  const handleCanvasPointer = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width * width;
    const y = (e.clientY - rect.top) / rect.height * height;
    setProbePos({ x, y });
  };
  const gridDots = useMemo(() => {
    const dots = [];
    const cols = 48;
    const rows = 27;
    for (let i = 0; i <= cols; i++) {
      for (let j = 0; j <= rows; j++) {
        const x = i / cols * 100;
        const y = j / rows * 100;
        dots.push({ x, y });
      }
    }
    return dots;
  }, []);
  return /* @__PURE__ */ jsxs("div", { ref: containerRef, className: "w-full bg-card text-foreground flex flex-col selection:bg-primary/20", children: [
    /* @__PURE__ */ jsxs("div", { className: "relative w-full overflow-hidden border-b border-border bg-[#0d1117]", children: [
      /* @__PURE__ */ jsx("div", { className: "absolute bottom-3 start-4 bg-[#161b22]/80 text-slate-300 rounded-full px-2.5 py-1 text-xs font-medium pointer-events-none backdrop-blur-xs", children: /* @__PURE__ */ jsx("span", { children: "Dark/Inside (−) • Bright/Outside (+)" }) }),
      /* @__PURE__ */ jsxs(
        "svg",
        {
          role: "img",
          "aria-label": "Interactive 2D Signed Distance Field simulation grid with circle and box geometries",
          viewBox: `0 0 ${width} ${height}`,
          className: "w-full h-auto block select-none touch-none cursor-crosshair",
          onPointerMove: handleCanvasPointer,
          onPointerDown: handleCanvasPointer,
          children: [
            gridDots.map((dot, index) => {
              const pixelX = dot.x / 100 * width;
              const pixelY = dot.y / 100 * height;
              const dist = getSdfValue(pixelX, pixelY);
              let color = "rgba(51, 110, 243, 0.15)";
              if (dist < 0) {
                color = "rgba(234, 67, 53, 0.4)";
              } else {
                const intensity = Math.max(0, 1 - dist / 220);
                color = `rgba(56, 139, 253, ${0.05 + intensity * 0.45})`;
              }
              const absDist = Math.abs(dist);
              const radius = absDist < 4 ? 3.5 : absDist < 12 ? 2.5 : 1.2;
              return /* @__PURE__ */ jsx(
                "circle",
                {
                  cx: `${dot.x}%`,
                  cy: `${dot.y}%`,
                  r: radius,
                  fill: color,
                  className: "transition-colors duration-150"
                },
                index
              );
            }),
            /* @__PURE__ */ jsx(
              "circle",
              {
                cx: circleX,
                cy: circleY,
                r: circleRadius,
                fill: "none",
                stroke: "rgba(255, 255, 255, 0.08)",
                strokeWidth: 1.5,
                strokeDasharray: "4 4"
              }
            ),
            /* @__PURE__ */ jsx(
              "rect",
              {
                x: boxX - boxW,
                y: boxY - boxH,
                width: boxW * 2,
                height: boxH * 2,
                fill: "none",
                stroke: "rgba(255, 255, 255, 0.08)",
                strokeWidth: 1.5,
                strokeDasharray: "4 4"
              }
            ),
            probeSdf !== null && /* @__PURE__ */ jsx("g", { children: isolineLevels.map((lvl, idx) => {
              return null;
            }) }),
            operation === "union" && /* @__PURE__ */ jsx("g", { fill: "none", stroke: "#34a853", strokeWidth: 2.5, opacity: 0.85, children: /* @__PURE__ */ jsx(
              "path",
              {
                d: `M ${circleX - circleRadius} ${circleY} A ${circleRadius} ${circleRadius} 0 1 1 ${circleX + circleRadius} ${circleY} A ${circleRadius} ${circleRadius} 0 1 1 ${circleX - circleRadius} ${circleY}`,
                strokeWidth: 1.5,
                stroke: "rgba(255,255,255,0.15)"
              }
            ) }),
            probePos && probeSdf !== null && /* @__PURE__ */ jsxs("g", { children: [
              /* @__PURE__ */ jsx(
                "circle",
                {
                  cx: probePos.x,
                  cy: probePos.y,
                  r: 6,
                  fill: "none",
                  stroke: probeSdf < 0 ? "#ea4335" : "#336ef3",
                  strokeWidth: 2
                }
              ),
              /* @__PURE__ */ jsx(
                "circle",
                {
                  cx: probePos.x,
                  cy: probePos.y,
                  r: 2,
                  fill: "#ffffff"
                }
              ),
              /* @__PURE__ */ jsxs(
                "text",
                {
                  x: probePos.x + 10,
                  y: probePos.y - 10,
                  fill: "#ffffff",
                  fontSize: 12,
                  fontFamily: "sans-serif",
                  className: "pointer-events-none select-none drop-shadow-sm font-medium",
                  children: [
                    "d = ",
                    probeSdf.toFixed(1),
                    "px"
                  ]
                }
              )
            ] })
          ]
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-center gap-x-4 sm:gap-x-8 md:gap-x-12 border-b border-border px-5 py-3 shrink-0", children: [
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Operation Mode" }),
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full capitalize", children: operation.replace("_", " ") })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Probe Distance" }),
        /* @__PURE__ */ jsx("span", { className: `text-sm font-medium tabular-nums truncate text-center w-full ${probeSdf !== null && probeSdf < 0 ? "text-error" : "text-primary"}`, children: probeSdf !== null ? `${probeSdf.toFixed(1)} px` : "—" })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col items-center gap-0.5 min-w-0 flex-1", children: [
        /* @__PURE__ */ jsx("span", { className: "text-xs text-muted-foreground font-medium truncate text-center w-full", children: "Shape Status" }),
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-foreground tabular-nums truncate text-center w-full", children: probeSdf !== null ? probeSdf < 0 ? "Inside Shape" : "Outside Shape" : "—" })
      ] })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "p-5 flex flex-col gap-4", children: [
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5", children: [
        /* @__PURE__ */ jsx("label", { className: "text-sm font-medium text-muted-foreground", children: "CSG Boolean Operation" }),
        /* @__PURE__ */ jsxs(
          ToggleGroup.Root,
          {
            type: "single",
            value: operation,
            onValueChange: (val) => {
              if (val) setOperation(val);
            },
            className: "rounded-full flex w-full bg-muted h-9 p-1",
            "aria-label": "SDF CSG Operation selection",
            children: [
              /* @__PURE__ */ jsx(
                ToggleGroup.Item,
                {
                  value: "union",
                  title: "Union",
                  className: "flex-1 min-w-0 text-center px-2 rounded-full text-sm font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 data-[state=on]:bg-primary data-[state=on]:text-white overflow-visible",
                  children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Union" })
                }
              ),
              /* @__PURE__ */ jsx(
                ToggleGroup.Item,
                {
                  value: "subtraction",
                  title: "Subtraction",
                  className: "flex-1 min-w-0 text-center px-2 rounded-full text-sm font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 data-[state=on]:bg-primary data-[state=on]:text-white overflow-visible",
                  children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Subtract" })
                }
              ),
              /* @__PURE__ */ jsx(
                ToggleGroup.Item,
                {
                  value: "intersection",
                  title: "Intersection",
                  className: "flex-1 min-w-0 text-center px-2 rounded-full text-sm font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 data-[state=on]:bg-primary data-[state=on]:text-white overflow-visible",
                  children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Intersect" })
                }
              ),
              /* @__PURE__ */ jsx(
                ToggleGroup.Item,
                {
                  value: "smooth_union",
                  title: "Smooth Union",
                  className: "flex-1 min-w-0 text-center px-2 rounded-full text-sm font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 data-[state=on]:bg-primary data-[state=on]:text-white overflow-visible",
                  children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Smooth" })
                }
              )
            ]
          }
        )
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3.5", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1", children: [
          /* @__PURE__ */ jsx("label", { id: "separation-label", className: "text-sm font-medium text-muted-foreground", children: "Shape Separation Distance" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                value: [shapeSeparation],
                onValueChange: (val) => setShapeSeparation(val[0]),
                min: 20,
                max: 240,
                step: 2,
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                "aria-labelledby": "separation-label",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(
                    Slider.Thumb,
                    {
                      className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                      "aria-label": "Separation value slider thumb"
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsxs("span", { className: "w-[7ch] text-sm font-medium tabular-nums text-end shrink-0 whitespace-nowrap", children: [
              shapeSeparation,
              " px"
            ] })
          ] })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1 opacity-100 data-[disabled=true]:opacity-40 transition-opacity", "data-disabled": operation !== "smooth_union", children: [
          /* @__PURE__ */ jsx("label", { id: "smooth-label", className: "text-sm font-medium text-muted-foreground", children: "Smoothing Factor (k)" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                value: [smoothK],
                onValueChange: (val) => setSmoothK(val[0]),
                min: 5,
                max: 90,
                step: 1,
                disabled: operation !== "smooth_union",
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3 disabled:cursor-not-allowed",
                "aria-labelledby": "smooth-label",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(
                    Slider.Thumb,
                    {
                      className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11",
                      "aria-label": "Smoothing value slider thumb"
                    }
                  )
                ]
              }
            ),
            /* @__PURE__ */ jsxs("span", { className: "w-[7ch] text-sm font-medium tabular-nums text-end shrink-0 whitespace-nowrap", children: [
              smoothK,
              " px"
            ] })
          ] })
        ] })
      ] })
    ] })
  ] });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsx(React.StrictMode, { children: /* @__PURE__ */ jsx(App, {}) })
);