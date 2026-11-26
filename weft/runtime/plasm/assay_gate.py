"""Anchored assay gate: separate capability gain from proxy-reward bleed.

Model. A batch where a fraction ``p`` of items starts as positives is scored
after one round. Selection amplifies positives by ``r``; true conversion of
negatives happens at rate ``c``; a proxy channel marks a fraction ``alpha`` of
everything positive regardless of content. The observed positive fraction is

    q(p; r, c) = (r * p + c * (1 - p)) / (r * p + (1 - p))
    y(p)       = (1 - alpha) * q(p; r, c) + alpha

Two mixtures alone cannot tell bleed from conversion: ``(r, c=0, alpha=a)``
and ``(r, c=a, alpha=0)`` give the same ``y`` at every ``p``. This gate takes
``alpha`` from a separate anchor batch, deflates each observation to
``q = (y - alpha) / (1 - alpha)``, and uses the survival ratio

    Phi(p) = (1 - p) / (1 - q) = (1 + (r - 1) * p) / (1 - c)

which is linear in ``p``. Its intercept gives ``c = 1 - 1 / Phi(0)`` and its
slope gives ``r = 1 + slope / Phi(0)``.

Limit. The result is only as good as ``alpha``. The anchor batch must contain
no item that can truly convert; if it can, its score mixes ``c`` into
``alpha`` and the split is wrong. Whether a given harness has such a batch is
outside this module.

All arithmetic is exact (``fractions.Fraction``); float inputs are rejected.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict

_ZERO = Fraction(0)
_ONE = Fraction(1)


def _require_fraction(name: str, value: object) -> Fraction:
    if type(value) is not Fraction:
        raise TypeError(f"{name} must be a fractions.Fraction, got {type(value).__name__}")
    return value


def observed_fraction(p: Fraction, r: Fraction, c: Fraction, alpha: Fraction) -> Fraction:
    """Forward model ``y(p)`` above, for tests and simulations."""
    for name, v in (("p", p), ("r", r), ("c", c), ("alpha", alpha)):
        _require_fraction(name, v)
    q = (r * p + c * (1 - p)) / (r * p + (1 - p))
    return (1 - alpha) * q + alpha


def anchored_assay_gate(
    alpha: Fraction,
    p1: Fraction,
    y1: Fraction,
    p2: Fraction,
    y2: Fraction,
) -> Dict[str, Fraction]:
    """Recover ``(r, c)`` from two mixtures ``(p1, y1)``, ``(p2, y2)`` and an
    anchor-measured bleed ``alpha``.

    Raises ``TypeError`` for non-Fraction inputs and ``ValueError`` when the
    inputs are outside the model: ``alpha`` outside ``[0, 1)``, mixtures not
    distinct or not in ``(0, 1)``, a deflated fraction at or above 1, or a
    survival-ratio intercept that is not positive (which would mean ``c >= 1``
    or data the model cannot produce).
    """
    for name, v in (("alpha", alpha), ("p1", p1), ("y1", y1), ("p2", p2), ("y2", y2)):
        _require_fraction(name, v)
    if not (_ZERO <= alpha < _ONE):
        raise ValueError("alpha must lie in [0, 1)")
    if p1 == p2 or not (_ZERO < p1 < _ONE) or not (_ZERO < p2 < _ONE):
        raise ValueError("need two distinct mixtures p1 != p2, each in (0, 1)")

    q1 = (y1 - alpha) / (1 - alpha)
    q2 = (y2 - alpha) / (1 - alpha)
    if q1 >= 1 or q2 >= 1:
        raise ValueError("deflated positive fraction is at or above 1")

    phi1 = (1 - p1) / (1 - q1)
    phi2 = (1 - p2) / (1 - q2)
    slope = (phi2 - phi1) / (p2 - p1)
    intercept = phi1 - slope * p1
    if intercept <= 0:
        raise ValueError("survival-ratio intercept is not positive; data outside the model")
    return {
        "alpha": alpha,
        "q1": q1,
        "q2": q2,
        "phi_intercept": intercept,
        "phi_slope": slope,
        "c": 1 - _ONE / intercept,
        "r": 1 + slope / intercept,
    }
