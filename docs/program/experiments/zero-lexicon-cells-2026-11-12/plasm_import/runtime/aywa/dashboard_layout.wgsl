// Sovereign Weft // Zero-Allocation WebGPU Spatial Dashboard & Procedural ASCII SDF Shader
// Consumes all 16 float32 fields of the 64-byte uniform buffer (Interface I1) plus
// the packed repository label storage buffer (`labelData`).
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

struct TextLinePack {
    chars : array<u32, 16>,
};

@group(0) @binding(0) var<uniform> telemetry : OrgTelemetry;
@group(0) @binding(1) var<storage, read> labelData : array<TextLinePack>;

struct VertexOutput {
    @builtin(position) position : vec4<f32>,
    @location(0) uv : vec2<f32>,
};

@vertex
fn vs_main(@builtin(vertex_index) vertexIndex : u32) -> VertexOutput {
    var pos = array<vec2<f32>, 6>(
        vec2<f32>(-1.0, -1.0), vec2<f32>( 1.0, -1.0), vec2<f32>(-1.0,  1.0),
        vec2<f32>(-1.0,  1.0), vec2<f32>( 1.0, -1.0), vec2<f32>( 1.0,  1.0)
    );
    var out : VertexOutput;
    out.position = vec4<f32>(pos[vertexIndex], 0.0, 1.0);
    out.uv = pos[vertexIndex];
    return out;
}

fn sdBox(p : vec2<f32>, b : vec2<f32>, r : f32) -> f32 {
    let q = abs(p) - b + vec2<f32>(r);
    return min(max(q.x, q.y), 0.0) + length(max(q, vec2<f32>(0.0))) - r;
}

fn huePalette(h : f32) -> vec3<f32> {
    return 0.5 + 0.5 * cos(6.2831853 * (h + vec3<f32>(0.0, 0.33, 0.67)));
}

fn nodeVelocity(nodeIdx : u32) -> f32 {
    let slot = nodeIdx % 8u;
    if (slot < 4u) {
        return telemetry.node_vel_0[slot];
    }
    return telemetry.node_vel_1[slot - 4u];
}

fn glyphPixel(ch : u32, gx : i32, gy : i32) -> f32 {
    if (ch <= 32u || gx < 0 || gx >= 5 || gy < 0 || gy >= 7) {
        return 0.0;
    }
    let bitIdx = u32(gy * 5 + gx);
    let seed = (ch * 2654435761u) ^ (bitIdx * 2246822519u);
    let border = (gy == 0 || gy == 6 || gx == 0 || gx == 4);
    let fill = ((seed >> (bitIdx % 16u)) & 1u) == 1u;
    return select(0.0, 1.0, border || fill);
}

@fragment
fn fs_main(in : VertexOutput) -> @location(0) vec4<f32> {
    var p = in.uv;
    p.x *= 1.6;
    let densityScale = mix(0.82, 1.28, clamp(telemetry.user_density, 0.0, 1.0));
    let wave = sin(p.x * 48.0 * densityScale + telemetry.system_time)
             * cos(p.y * 48.0 * densityScale - telemetry.system_time * 0.5);
    let grid = smoothstep(0.012, 0.0, abs(wave) - 0.002);
    let accent = huePalette(telemetry.user_hue);
    let bg = vec3<f32>(mix(0.01, 0.05, telemetry.user_contrast)) + accent * (grid * 0.03);

    let spacing = vec2<f32>(0.52, 0.42) / densityScale;
    let cell_id = floor((p + spacing * 0.5) / spacing);
    let local_p = (p + spacing * 0.5) - cell_id * spacing - spacing * 0.5;
    let idx_f = (cell_id.x + 2.0) + (cell_id.y + 2.0) * 5.0;

    if (idx_f < 0.0 || idx_f >= telemetry.active_nodes) {
        return vec4<f32>(bg, 1.0);
    }

    let nodeIdx = u32(idx_f);
    let vel = nodeVelocity(nodeIdx);
    let boxHalf = vec2<f32>(0.21, 0.16) / densityScale;
    let radius = mix(0.01, 0.08, clamp(telemetry.user_rounding, 0.0, 1.0));
    let d = sdBox(local_p, boxHalf, radius);
    let giniMod = 0.75 + 0.5 * clamp(telemetry.gini_index, 0.0, 1.0);
    let glow = exp(-max(d, 0.0) * 18.0) * (0.35 + 0.65 * telemetry.org_tension) * giniMod;
    var col = bg + accent * glow;

    if (d < 0.0) {
        let pulse = 0.5 + 0.5 * sin(telemetry.system_time * (1.5 + vel * 2.0) + idx_f);
        let fillBase = mix(vec3<f32>(0.04, 0.09, 0.16), accent * 0.55, 0.25 + 0.25 * pulse);
        col = mix(fillBase, vec3<f32>(0.85, 0.25, 0.15), telemetry.org_tension * 0.35);

        // Render procedural 16-char ASCII label inside upper band of each cell
        let rel = (local_p + boxHalf) / (boxHalf * 2.0);
        if (rel.y > 0.55 && rel.y < 0.85 && rel.x > 0.08 && rel.x < 0.92) {
            let charPos = (rel.x - 0.08) / 0.84 * 16.0;
            let charIdx = u32(clamp(charPos, 0.0, 15.0));
            let fracX = fract(charPos);
            let fracY = (rel.y - 0.55) / 0.30;
            let gx = i32(fracX * 6.0);
            let gy = i32((1.0 - fracY) * 7.0);
            let ch = labelData[min(nodeIdx, 31u)].chars[charIdx];
            let ink = glyphPixel(ch, gx, gy);
            col = mix(col, vec3<f32>(0.92, 0.96, 1.0), ink * 0.85);
        }
    }
    return vec4<f32>(col, 1.0);
}
