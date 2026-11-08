import { jsx, jsxs } from 'https://widgetlibs.static.usercontent.goog/react/jsx-runtime-Dc9ViRTo.js';
import React, { useState, useRef, useEffect } from 'https://widgetlibs.static.usercontent.goog/react-Dd1pKoqe.js';
import ReactDOM from 'https://widgetlibs.static.usercontent.goog/react-dom/client-BTuQ-l8_.js';
import { ErrorBoundary } from 'https://widgetlibs.static.usercontent.goog/react-error-boundary-BY2GTZrN.js';
import * as Slider from 'https://widgetlibs.static.usercontent.goog/@radix-ui/react-slider-DXk-CvUR.js';
import * as ToggleGroup from 'https://widgetlibs.static.usercontent.goog/@radix-ui/react-toggle-group-SAzue8E6.js';

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
    /* @__PURE__ */ jsx("p", { className: "text-sm font-medium", children: "Something went wrong:" }),
    /* @__PURE__ */ jsx("pre", { className: "text-xs mt-1 whitespace-pre-wrap", children: error.message })
  ] });
}
function App() {
  return /* @__PURE__ */ jsx(ErrorBoundary, { FallbackComponent: ErrorFallback, children: /* @__PURE__ */ jsx(ShaderSandbox, {}) });
}
function ShaderSandbox() {
  const [isPlaying, setIsPlaying] = useState(true);
  const [frameTick, setFrameTick] = useState(0);
  const [speed, setSpeed] = useState(1.5);
  const [frequency, setFrequency] = useState(4);
  const [patternMode, setPatternMode] = useState("sine");
  const canvasRef = useRef(null);
  const lastTimeRef = useRef(performance.now());
  const timeAccumulatorRef = useRef(0);
  useEffect(() => {
    if (!isPlaying) return;
    lastTimeRef.current = performance.now();
    let frameId;
    const tick = (now) => {
      const delta = Math.min((now - lastTimeRef.current) / 1e3, 0.1);
      lastTimeRef.current = now;
      timeAccumulatorRef.current += delta * speed;
      setFrameTick((t) => t + 1);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [isPlaying, speed]);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const width = canvas.width;
    const height = canvas.height;
    const t = timeAccumulatorRef.current;
    ctx.fillStyle = "#0c0f16";
    ctx.fillRect(0, 0, width, height);
    const cols = 48;
    const rows = 27;
    const cellWidth = width / cols;
    const cellHeight = height / rows;
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const nx = x / cols * 2 - 1;
        const ny = y / rows * 2 - 1;
        const dist = Math.sqrt(nx * nx + ny * ny);
        let intensity = 0;
        if (patternMode === "sine") {
          intensity = Math.sin(dist * frequency - t) * 0.5 + 0.5;
        } else {
          intensity = Math.sin(nx * frequency + t) * Math.cos(ny * frequency + t) * 0.5 + 0.5;
        }
        const r = Math.floor(intensity * 50 + 20);
        const g = Math.floor(intensity * 180 + 40);
        const b = Math.floor(intensity * 255 + 100);
        ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
        ctx.fillRect(
          x * cellWidth + 0.5,
          y * cellHeight + 0.5,
          cellWidth - 1,
          cellHeight - 1
        );
      }
    }
  }, [frameTick, frequency, patternMode]);
  return /* @__PURE__ */ jsxs("div", { className: "w-full bg-card text-foreground select-none", children: [
    /* @__PURE__ */ jsxs("div", { className: "relative w-full overflow-hidden border-b border-border aspect-video", children: [
      /* @__PURE__ */ jsx(
        "canvas",
        {
          ref: canvasRef,
          width: 640,
          height: 360,
          className: "w-full h-full block",
          style: { imageRendering: "pixelated" }
        }
      ),
      /* @__PURE__ */ jsx("div", { className: "absolute top-0 end-0 p-3 z-10 flex items-center justify-end pointer-events-none", children: /* @__PURE__ */ jsx(
        "button",
        {
          type: "button",
          onClick: () => setIsPlaying(!isPlaying),
          className: "w-9 h-9 rounded-full flex items-center justify-center cursor-pointer transition-colors shadow-none bg-muted/90 hover:bg-secondary-hover text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-primary pointer-events-auto relative overflow-visible after:absolute after:-inset-1",
          "aria-label": isPlaying ? "Pause animation" : "Play animation",
          children: /* @__PURE__ */ jsx("span", { className: "material-icons !text-base", children: isPlaying ? "pause" : "play_arrow" })
        }
      ) })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "p-5 flex flex-col gap-4", children: [
      /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4", children: [
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Animation speed" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                value: [speed],
                onValueChange: (val) => setSpeed(val[0]),
                max: 4,
                min: 0,
                step: 0.1,
                "aria-label": "Animation speed",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(Slider.Thumb, { className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11" })
                ]
              }
            ),
            /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium tabular-nums w-[8ch] text-end shrink-0 whitespace-nowrap", children: [
              speed.toFixed(1),
              "x"
            ] })
          ] })
        ] }),
        /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5", children: [
          /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Spatial frequency" }),
          /* @__PURE__ */ jsxs("div", { className: "flex items-center gap-3 w-full", children: [
            /* @__PURE__ */ jsxs(
              Slider.Root,
              {
                className: "relative flex items-center grow touch-none select-none h-11 cursor-pointer py-3 -my-3",
                value: [frequency],
                onValueChange: (val) => setFrequency(val[0]),
                max: 12,
                min: 1,
                step: 0.2,
                "aria-label": "Spatial frequency",
                children: [
                  /* @__PURE__ */ jsx(Slider.Track, { className: "relative grow rounded-full h-1 !bg-muted", children: /* @__PURE__ */ jsx(Slider.Range, { className: "absolute h-full bg-primary rounded-full" }) }),
                  /* @__PURE__ */ jsx(Slider.Thumb, { className: "block w-[18px] h-[18px] rounded-full bg-primary border-none shadow-none focus:outline-none focus-visible:ring-2 focus-visible:ring-primary relative after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-11 after:h-11" })
                ]
              }
            ),
            /* @__PURE__ */ jsxs("span", { className: "text-sm font-medium tabular-nums w-[8ch] text-end shrink-0 whitespace-nowrap", children: [
              frequency.toFixed(1),
              " Hz"
            ] })
          ] })
        ] })
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex flex-col gap-1.5 max-w-xs", children: [
        /* @__PURE__ */ jsx("span", { className: "text-sm font-medium text-muted-foreground", children: "Procedural generator" }),
        /* @__PURE__ */ jsxs(
          ToggleGroup.Root,
          {
            type: "single",
            value: patternMode,
            onValueChange: (val) => {
              if (val) setPatternMode(val);
            },
            className: "rounded-full flex w-full bg-muted h-9 p-1",
            "aria-label": "Procedural generator mode",
            children: [
              /* @__PURE__ */ jsx(
                ToggleGroup.Item,
                {
                  value: "sine",
                  className: "flex-1 min-w-0 text-center px-3 rounded-full text-sm font-medium text-muted-foreground data-[state=on]:bg-primary data-[state=on]:text-white hover:text-foreground transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 overflow-visible",
                  title: "Sine radial wave",
                  children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Radial wave" })
                }
              ),
              /* @__PURE__ */ jsx(
                ToggleGroup.Item,
                {
                  value: "matrix",
                  className: "flex-1 min-w-0 text-center px-3 rounded-full text-sm font-medium text-muted-foreground data-[state=on]:bg-primary data-[state=on]:text-white hover:text-foreground transition-colors cursor-pointer relative after:absolute after:-inset-y-2 after:inset-x-0 overflow-visible",
                  title: "Matrix grid wave",
                  children: /* @__PURE__ */ jsx("span", { className: "truncate block w-full", children: "Matrix grid" })
                }
              )
            ]
          }
        )
      ] })
    ] })
  ] });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  /* @__PURE__ */ jsx(React.StrictMode, { children: /* @__PURE__ */ jsx(App, {}) })
);