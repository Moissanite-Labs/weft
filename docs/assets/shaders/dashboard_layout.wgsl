// Sovereign Weft // Zero-Allocation WebGPU Spatial Dashboard & Procedural ASCII SDF Shader
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

@fragment
fn fs_main(in : VertexOutput) -> @location(0) vec4<f32> {
    var p = in.uv;
    p.x *= 1.6;
    let wave = sin(p.x * 48.0 + telemetry.system_time) * cos(p.y * 48.0 - telemetry.system_time * 0.5);
    let grid = smoothstep(0.012, 0.0, abs(wave) - 0.002);
    let bg = vec3<f32>(mix(0.01, 0.04, telemetry.user_contrast)) + vec3<f32>(grid * 0.02);

    let spacing = vec2<f32>(0.52, 0.42);
    let cell_id = floor((p + spacing * 0.5) / spacing);
    let local_p = (p + spacing * 0.5) - cell_id * spacing - spacing * 0.5;
    let idx = (cell_id.x + 2.0) + (cell_id.y + 2.0) * 5.0;

    if (idx < 0.0 || idx >= telemetry.active_nodes) {
        return vec4<f32>(bg, 1.0);
    }
    let d = sdBox(local_p, vec2<f32>(0.21, 0.16), mix(0.01, 0.08, telemetry.user_rounding));
    let glow = exp(-max(d, 0.0) * 18.0) * (0.4 + 0.6 * telemetry.org_tension);
    var col = bg + vec3<f32>(0.05, 0.45, 0.85) * glow;
    if (d < 0.0) {
        col = mix(vec3<f32>(0.04, 0.09, 0.16), vec3<f32>(0.85, 0.25, 0.15), telemetry.org_tension * 0.35);
    }
    return vec4<f32>(col, 1.0);
}
