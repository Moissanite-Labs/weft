// ML Weft // w3ft.org field shader (Codebase C7, issue #37)
//
// One full-screen triangle (weft/design/eh.md) evaluates the whole field per
// pixel from signed distance functions (weft/design/art.md):
//
//   ground  : a plain-weave loom. Warp and weft threads cross; at crossing
//             (i, j) the weft lies on top when i + j is even.
//   threads : layer minimum-spanning-tree segments with a travelling bead.
//   cells   : rounded-box SDFs. Exact rectangles come from the CPU layout
//             (cell-layout.js): area proportional to commits, packed on the
//             golden angle, fitted to the real viewport. No clip-space aspect
//             constant, no modulo grid.
//   text    : a 5x7 bitmask font, two u32 per glyph (glyph-font.js), drawn at
//             whole device pixels so it stays crisp at any DPR.
//   grain   : hash noise scaled by organisation tension (weft/design/feeed.md).
//
// Units: everything is in CSS pixels. One device pixel is 1/dpr CSS px, which
// is also the anti-aliasing width, so edges are one device pixel wide at
// every resolution.

// Interface I1: the 64-byte telemetry frame (16 x f32). Unchanged.
struct OrgTelemetry {
    active_nodes  : f32,
    org_tension   : f32,
    system_time   : f32,
    gini_index    : f32,
    user_rounding : f32,
    user_density  : f32,
    user_hue      : f32,
    user_contrast : f32,
    node_vel_0    : vec4<f32>,
    node_vel_1    : vec4<f32>,
};

// Viewport and interaction state (C7-internal, not part of I1).
struct View {
    frame   : vec4<f32>, // css width, css height, dpr, label glyph px (css)
    stage   : vec4<f32>, // field region origin x, y (viewport css), hover index, reading calm
    counts  : vec4<f32>, // cell count, thread count, motion (0 = reduced), label gap (css)
    pointer : vec4<f32>, // pointer x, y (viewport css; negative = none), scroll y, unused
    bounds  : vec4<f32>, // cluster bounds x0, y0, x1, y1 (region css), labels included
};

struct Cell {
    rect  : vec4<f32>, // centre x, y (region css), half side, label width
    style : vec4<f32>, // hue, tension, resonance, emphasis
    info  : vec4<f32>, // label length, commits, hover (0..1), layer index
    chars : vec4<u32>, // 16 ASCII codes, 4 per word, little-endian
};

struct Thread {
    ends  : vec4<f32>, // a.x, a.y, b.x, b.y (region css)
    style : vec4<f32>, // hue, emphasis, phase, unused
};

@group(0) @binding(0) var<uniform> telemetry : OrgTelemetry;
@group(0) @binding(1) var<uniform> view : View;
@group(0) @binding(2) var<storage, read> cells : array<Cell>;
@group(0) @binding(3) var<storage, read> threads : array<Thread>;
@group(0) @binding(4) var<storage, read> font : array<vec2<u32>>;

@vertex
fn vs_main(@builtin(vertex_index) vid : u32) -> @builtin(position) vec4<f32> {
    // Full-screen triangle: (-1,-1), (3,-1), (-1,3).
    let x = f32(i32(vid << 1u) & 2) * 2.0 - 1.0;
    let y = f32(i32(vid & 2u)) * 2.0 - 1.0;
    return vec4<f32>(x, y, 0.0, 1.0);
}

fn hsl(h : f32, s : f32, l : f32) -> vec3<f32> {
    let k = (vec3<f32>(0.0, 8.0, 4.0) + fract(h) * 12.0) % vec3<f32>(12.0);
    let a = s * min(l, 1.0 - l);
    return l - a * clamp(min(k - 3.0, 9.0 - k), vec3<f32>(-1.0), vec3<f32>(1.0));
}

fn sdRoundBox(p : vec2<f32>, b : vec2<f32>, r : f32) -> f32 {
    let q = abs(p) - b + vec2<f32>(r);
    return min(max(q.x, q.y), 0.0) + length(max(q, vec2<f32>(0.0))) - r;
}

fn sdSegment(p : vec2<f32>, a : vec2<f32>, b : vec2<f32>) -> vec2<f32> {
    let pa = p - a;
    let ba = b - a;
    let h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
    return vec2<f32>(length(pa - ba * h), h);
}

// Polynomial smooth minimum: the "liquid" union of two fields (art.md).
fn smin(a : f32, b : f32, k : f32) -> f32 {
    let h = max(k - abs(a - b), 0.0) / k;
    return min(a, b) - h * h * h * k * (1.0 / 6.0);
}

fn hash21(p : vec2<f32>) -> f32 {
    var q = fract(p * vec2<f32>(123.34, 456.21));
    q += dot(q, q + 45.32);
    return fract(q.x * q.y);
}

fn glyphBit(ch : u32, col : i32, row : i32) -> f32 {
    if (col < 0 || col >= 5 || row < 0 || row >= 7) {
        return 0.0;
    }
    let b = u32(row * 5 + col);
    let g = font[ch & 127u];
    let w = select(g.y, g.x, b < 20u);
    return f32((w >> (b % 20u)) & 1u);
}

// Ink of a string at whole-device-pixel glyph size `gp` (css px per glyph pixel).
fn textInk(q : vec2<f32>, origin : vec2<f32>, gp : f32, chars : vec4<u32>, len : u32) -> f32 {
    let l = (q - origin) / gp;
    if (l.x < 0.0 || l.y < 0.0 || l.y >= 7.0 || l.x >= f32(len) * 6.0) {
        return 0.0;
    }
    let k = u32(l.x / 6.0);
    let col = i32(floor(l.x - f32(k) * 6.0));
    let row = i32(floor(l.y));
    let ch = (chars[k >> 2u] >> (8u * (k & 3u))) & 255u;
    return glyphBit(ch, col, row);
}

fn snapPx(v : vec2<f32>, dpr : f32) -> vec2<f32> {
    return floor(v * dpr + 0.5) / dpr;
}

fn snapGlyph(want : f32, dpr : f32) -> f32 {
    return max(1.0, floor(want * dpr + 0.5)) / dpr;
}

// Decimal digits of n (0..9999) as packed ASCII.
fn digitsOf(n : u32) -> vec4<u32> {
    var out = vec4<u32>(0u);
    var len = 1u;
    if (n >= 10u) { len = 2u; }
    if (n >= 100u) { len = 3u; }
    if (n >= 1000u) { len = 4u; }
    var v = n;
    for (var i = 0u; i < len; i++) {
        let k = len - 1u - i;
        out[0] |= (48u + v % 10u) << (8u * k);
        v = v / 10u;
    }
    out[1] = len;
    return out;
}

fn weave(p : vec2<f32>, spacing : f32, aa : f32, tension : f32, t : f32) -> vec4<f32> {
    let g = p / spacing;
    let cellIdx = floor(g);
    let f = fract(g) - 0.5;
    // Loom tension above the homeostatic band makes the weft shiver.
    let shiver = max(tension - 0.35, 0.0) * 0.12 * sin(g.x * 3.1 + t * 9.0);
    let w = 0.17 * spacing;
    let warpD = abs(f.x) * spacing;
    let weftD = abs(f.y + shiver) * spacing;
    let warpInk = 1.0 - smoothstep(w - aa, w + aa, warpD);
    let weftInk = 1.0 - smoothstep(w - aa, w + aa, weftD);
    // Thread heights: weft row j is over warp i when i + j is even.
    let hWeft = cos(3.14159265 * (g.x - 0.5 - cellIdx.y));
    let hWarp = -cos(3.14159265 * (g.y - 0.5 - cellIdx.x));
    let weftTop = hWeft >= hWarp;
    var ink = 0.0;
    var shade = 0.0;
    var isWeft = 0.0;
    if (warpInk > 0.0 && (!weftTop || weftInk <= 0.0)) {
        ink = warpInk;
        shade = 0.55 + 0.45 * hWarp;
    }
    if (weftInk > 0.0 && (weftTop || warpInk <= 0.0)) {
        ink = weftInk;
        shade = 0.55 + 0.45 * hWeft;
        isWeft = 1.0;
    }
    return vec4<f32>(ink, shade, isWeft, 0.0);
}

@fragment
fn fs_main(@builtin(position) frag : vec4<f32>) -> @location(0) vec4<f32> {
    let dpr = max(view.frame.z, 0.5);
    let px = 1.0 / dpr;
    let css = frag.xy / dpr;
    let q = css - view.stage.xy;
    let motion = view.counts.z;
    let t = telemetry.system_time;
    let hue = telemetry.user_hue;
    let calm = clamp(view.stage.w, 0.0, 1.0);
    let tension = clamp(telemetry.org_tension, 0.0, 1.0);
    let rounding = clamp(telemetry.user_rounding, 0.0, 1.0);
    let density = clamp(telemetry.user_density, 0.0, 1.0);
    let contrast = clamp(telemetry.user_contrast, 0.0, 1.0);

    // Ground.
    var col = mix(vec3<f32>(0.010, 0.014, 0.024), vec3<f32>(0.045, 0.050, 0.075), clamp(contrast * 3.0, 0.0, 1.0));

    // Loom weave, drifting at 0.35x scroll for depth.
    let spacing = mix(34.0, 18.0, density);
    let wv = weave(css + vec2<f32>(0.0, view.pointer.z * 0.35), spacing, px, tension, t * motion);
    let warpCol = hsl(hue, 0.45, 0.42);
    let weftCol = hsl(hue + 0.08, 0.55, 0.50);
    col = mix(col, mix(warpCol, weftCol, wv.z) * wv.y, wv.x * 0.075);

    // Pixels far from the cluster skip the cell, thread and label loops.
    let reach = 64.0;
    let nearCluster = q.x > view.bounds.x - reach && q.y > view.bounds.y - reach &&
                      q.x < view.bounds.z + reach && q.y < view.bounds.w + reach;
    let nThreads = select(0u, u32(view.counts.y), nearCluster);

    // Threads between cells of a layer.
    for (var s = 0u; s < nThreads; s++) {
        let th = threads[s];
        let sd = sdSegment(q, th.ends.xy, th.ends.zw);
        let em = th.style.y;
        let tc = hsl(th.style.x, 0.70, 0.60);
        let core = 1.0 - smoothstep(0.6 - px, 0.6 + px, sd.x);
        let bead = exp(-pow((fract(sd.y - t * 0.22 * motion + th.style.z) - 0.5) * 9.0, 2.0));
        col = mix(col, tc, core * (0.30 + 0.6 * bead) * em);
        col += tc * exp(-sd.x / 7.0) * 0.05 * em;
    }

    // Cells: nearest SDF wins the fill; every cell contributes glow.
    let nCells = select(0u, u32(view.counts.x), nearCluster);
    var bestD = 1e9;
    var bestI = 0u;
    var glow = vec3<f32>(0.0);
    for (var i = 0u; i < nCells; i++) {
        let c = cells[i];
        let hov = c.info.z;
        let half = c.rect.z * (1.0 + 0.05 * hov);
        var p = q - c.rect.xy;
        let over = max(c.style.y - 0.35, 0.0) / 0.5;
        p.x += sin(p.y * 0.35 + t * 11.0 + f32(i)) * over * 2.0 * motion;
        let d = sdRoundBox(p, vec2<f32>(half), half * rounding);
        if (d < bestD) {
            bestD = d;
            bestI = i;
        }
        let pulse = 0.85 + 0.15 * sin(t * (1.2 + 6.0 * c.style.z) * motion + f32(i) * 1.7);
        let spread = 5.0 + 16.0 * c.style.y + 6.0 * calm;
        glow += hsl(c.style.x, 0.75, 0.55) * exp(-max(d, 0.0) / spread) * (0.10 + 0.35 * hov) * c.style.w * pulse;
    }
    col += glow * (0.8 + 0.4 * calm);

    if (nCells > 0u) {
        let c = cells[bestI];
        let hov = c.info.z;
        let em = c.style.w;
        let half = c.rect.z * (1.0 + 0.05 * hov);
        let lc = hsl(c.style.x, 0.72, 0.60);
        let fill = 1.0 - smoothstep(-px, px, bestD);
        let over = max(c.style.y - 0.35, 0.0) / 0.5;
        var inner = mix(col, lc * 0.42, 0.20 + 0.10 * hov) * (0.55 + 0.45 * em);
        inner = mix(inner, vec3<f32>(0.85, 0.32, 0.18) * 0.5, over * 0.5);
        col = mix(col, inner, fill);

        // Stroke weight follows the Gini concentration (build.md, feeed.md).
        let sw = mix(1.0, 4.0, clamp(telemetry.gini_index, 0.0, 1.0));
        let stroke = 1.0 - smoothstep(sw * 0.5 - px, sw * 0.5 + px, abs(bestD + sw * 0.5));
        col = mix(col, lc * (0.45 + 0.55 * em), stroke * (0.55 + 0.45 * em));

        // Commit count, drawn by the GPU, as large as the cell allows.
        let dg = digitsOf(u32(c.info.y));
        let gpD = snapGlyph(half * 0.62 / 7.0, dpr);
        let wD = (f32(dg.y) * 6.0 - 1.0) * gpD;
        let oD = snapPx(c.rect.xy - vec2<f32>(wD * 0.5, 3.5 * gpD), dpr);
        let inkD = textInk(q, oD, gpD, vec4<u32>(dg.x, 0u, 0u, 0u), dg.y) * fill;
        col = mix(col, mix(lc, vec3<f32>(1.0), 0.55) * (0.5 + 0.5 * em), inkD * 0.92);

        // Liquid union with the pointer (smooth minimum).
        if (view.pointer.x >= 0.0) {
            let dp = length(q - (view.pointer.xy - view.stage.xy)) - 5.0;
            let dm = smin(bestD, dp, 28.0);
            let rim = 1.0 - smoothstep(0.0, 1.5 * px + 0.6, abs(dm));
            col = mix(col, lc, rim * (1.0 - fill) * 0.55);
        }
    }

    // Labels: each cell's name below it, at whole device pixels.
    let gpL = snapGlyph(view.frame.w, dpr);
    for (var i = 0u; i < nCells; i++) {
        let c = cells[i];
        let len = u32(c.info.x);
        let wL = (f32(len) * 6.0 - 1.0) * gpL;
        let half = c.rect.z * (1.0 + 0.05 * c.info.z);
        let oL = snapPx(vec2<f32>(c.rect.x - wL * 0.5, c.rect.y + half + view.counts.w), dpr);
        if (q.x < oL.x || q.x > oL.x + wL || q.y < oL.y || q.y > oL.y + 7.0 * gpL) {
            continue;
        }
        let ink = textInk(q, oL, gpL, c.chars, len);
        let tc = mix(vec3<f32>(0.58, 0.64, 0.72), vec3<f32>(1.0), c.info.z);
        col = mix(col, tc * (0.35 + 0.65 * c.style.w), ink);
    }

    // Grain: visible static in proportion to tension; calm reading softens it.
    let n = hash21(floor(frag.xy) + floor(t * 24.0 * motion)) - 0.5;
    col += vec3<f32>(n * tension * 0.06 * (1.0 - 0.5 * calm));

    // Vignette.
    let uv = css / max(view.frame.xy, vec2<f32>(1.0)) - 0.5;
    col *= 1.0 - 0.35 * dot(uv, uv);
    return vec4<f32>(max(col, vec3<f32>(0.0)), 1.0);
}
