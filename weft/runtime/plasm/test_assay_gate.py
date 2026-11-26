"""Tests for weft/runtime/plasm/assay_gate.py."""

from __future__ import annotations

import unittest
from fractions import Fraction as F

from weft.runtime.plasm.assay_gate import anchored_assay_gate, observed_fraction


class TestAnchoredAssayGate(unittest.TestCase):
    P1, P2 = F(1, 20), F(3, 8)

    def test_two_mixtures_alone_cannot_separate_bleed_from_conversion(self) -> None:
        for p in (self.P1, self.P2, F(1, 2), F(9, 10)):
            bleed = observed_fraction(p, F(6), F(0), F(1, 2))
            conversion = observed_fraction(p, F(6), F(1, 2), F(0))
            self.assertEqual(bleed, conversion)

    def test_anchor_alpha_separates_the_two_worlds(self) -> None:
        y = [observed_fraction(p, F(6), F(0), F(1, 2)) for p in (self.P1, self.P2)]
        bleed = anchored_assay_gate(F(1, 2), self.P1, y[0], self.P2, y[1])
        conversion = anchored_assay_gate(F(0), self.P1, y[0], self.P2, y[1])
        self.assertEqual((bleed["r"], bleed["c"]), (F(6), F(0)))
        self.assertEqual((conversion["r"], conversion["c"]), (F(6), F(1, 2)))

    def test_recovers_parameters_exactly_over_a_grid(self) -> None:
        for r in (F(1), F(3, 2), F(11)):
            for c in (F(0), F(1, 4), F(9, 10)):
                for alpha in (F(0), F(3, 20), F(2, 5)):
                    y1 = observed_fraction(self.P1, r, c, alpha)
                    y2 = observed_fraction(self.P2, r, c, alpha)
                    out = anchored_assay_gate(alpha, self.P1, y1, self.P2, y2)
                    self.assertEqual((out["r"], out["c"]), (r, c))

    def test_wrong_alpha_gives_a_wrong_split(self) -> None:
        # The limit stated in the module docstring: the split depends on alpha.
        y1 = observed_fraction(self.P1, F(6), F(1, 4), F(1, 10))
        y2 = observed_fraction(self.P2, F(6), F(1, 4), F(1, 10))
        out = anchored_assay_gate(F(0), self.P1, y1, self.P2, y2)
        self.assertNotEqual(out["c"], F(1, 4))

    def test_rejects_floats_and_out_of_model_inputs(self) -> None:
        y = observed_fraction(self.P1, F(2), F(0), F(0))
        with self.assertRaises(TypeError):
            anchored_assay_gate(0.0, self.P1, y, self.P2, y)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            anchored_assay_gate(F(1), self.P1, y, self.P2, y)
        with self.assertRaises(ValueError):
            anchored_assay_gate(F(0), self.P1, y, self.P1, y)
        with self.assertRaises(ValueError):
            anchored_assay_gate(F(0), F(0), y, self.P2, y)
        with self.assertRaises(ValueError):
            anchored_assay_gate(F(0), self.P1, F(1), self.P2, y)


if __name__ == "__main__":
    unittest.main()
