/** Barycentric aesthetic mixer from weft/design/baryonic.md */

export class AestheticMixer {
  constructor() {
    this.activeSlices = [
      { id: "native_base", weight: 1.0, rounding: 0.85, density: 0.30, hue_shift: 0.12, contrast: 0.05 },
      { id: "neon_terminal", weight: 0.0, rounding: 0.0, density: 0.1, hue_shift: 0.45, contrast: 0.01 },
      { id: "airy_pastel", weight: 0.0, rounding: 1.0, density: 0.85, hue_shift: 0.85, contrast: 0.2 },
    ];
  }

  setSliceWeight(id, weight) {
    const slice = this.activeSlices.find((s) => s.id === id);
    if (slice) slice.weight = Math.max(0, weight);
  }

  calculateUnifiedAestheticVector() {
    let totalRawWeight = this.activeSlices.reduce((sum, slice) => sum + slice.weight, 0);
    if (totalRawWeight === 0) {
      this.activeSlices[0].weight = 1.0;
      totalRawWeight = 1.0;
    }
    let fusedRounding = 0;
    let fusedDensity = 0;
    let fusedHue = 0;
    let fusedContrast = 0;
    for (const slice of this.activeSlices) {
      const w = slice.weight / totalRawWeight;
      fusedRounding += slice.rounding * w;
      fusedDensity += slice.density * w;
      fusedContrast += slice.contrast * w;
      fusedHue += slice.hue_shift * Math.PI * 2 * w;
    }
    return {
      rounding: fusedRounding,
      density: fusedDensity,
      contrast: fusedContrast,
      hue: (fusedHue / (Math.PI * 2)) % 1.0,
    };
  }
}
