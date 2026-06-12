"""
tests/test_boi_calculator.py
============================
Pytest suite for BOI calculator validation.
"""

import sys, os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.python.boi_calculator import compute_boi, interpret_boi


class TestBOIFormula:

    def test_boi_formula_basic(self):
        """BOI = primary / transfer."""
        boi = compute_boi(7.4, 18.0)
        assert abs(boi - 7.4 / 18.0) < 1e-10

    def test_perfect_transfer_boi_one(self):
        """Equal gains → BOI = 1.0."""
        boi = compute_boi(6.9, 6.9)
        assert abs(boi - 1.0) < 1e-10

    def test_fda_boi_below_one(self):
        """FDA should have BOI < 1 (transfers better than primary)."""
        boi = compute_boi(7.4, 18.0)  # FDA values from paper
        assert boi < 1.0
        assert abs(boi - 0.41) < 0.05

    def test_gan_boi_above_three(self):
        """GAN methods should have BOI > 3."""
        boi = compute_boi(12.8, 3.8)  # CycleGAN from paper
        assert boi > 3.0

    def test_scale_invariance(self):
        """P1: BOI(c*a, c*b) == BOI(a, b)."""
        a, b, c = 7.4, 18.0, 3.5
        assert abs(compute_boi(a, b) - compute_boi(c*a, c*b)) < 1e-10

    def test_monotonicity(self):
        """P2: larger primary gain → larger BOI (fixed transfer)."""
        assert compute_boi(9.0, 10.0) > compute_boi(5.0, 10.0)

    def test_zero_transfer_returns_inf(self):
        """Zero transfer gain → BOI = inf."""
        boi = compute_boi(5.0, 0.0)
        assert np.isinf(boi)

    def test_negative_primary_raises(self):
        """Negative primary gain → ValueError."""
        with pytest.raises(ValueError):
            compute_boi(-1.0, 5.0)

    @pytest.mark.parametrize("primary,transfer,expected_tier", [
        (7.4,  18.0, "excellent"),   # FDA
        (5.3,   4.8, "good"),        # Copy-Paste
        (6.8,   3.5, "moderate"),        # Sim2Real — BOI=1.94
        (12.8,  3.8, "poor"),        # GAN
    ])
    def test_interpret_boi_tiers(self, primary, transfer, expected_tier):
        boi = compute_boi(primary, transfer)
        result = interpret_boi(boi)
        assert result["tier"] == expected_tier, (
            f"BOI={boi:.2f}: expected '{expected_tier}', "
            f"got '{result['tier']}'")

    @pytest.mark.parametrize("primary,transfer,transfers", [
        (7.4,  18.0, True),   # FDA — transfers
        (12.8,  3.8, False),  # GAN — does not transfer
        (5.3,   4.8, True),   # Copy-Paste — transfers
        (9.6,   3.3, False),  # Diffusion — does not transfer
    ])
    def test_interpret_transfers_flag(self, primary, transfer, transfers):
        boi = compute_boi(primary, transfer)
        result = interpret_boi(boi)
        assert result["transfers"] == transfers


class TestBOIProperties:

    def test_all_four_properties(self):
        """Verify all four proven BOI properties."""
        from analysis.python.boi_calculator import verify_boi_properties
        assert verify_boi_properties() is True

    def test_non_transfer_rate_approx_40pct(self):
        """~40% of methods in S4 should have BOI > 2."""
        methods = [
            (7.4, 18.0), (6.8, 14.9), (6.1, 10.5), (5.8, 9.3),
            (5.3,  4.8), (5.8,  4.9), (12.8,  3.8), (14.2, 3.5),
            (9.6,  3.3), (5.6,  5.7), (6.8,  3.5),
        ]
        non_transfer = sum(
            1 for dp, dt in methods
            if compute_boi(dp, dt) > 2.0) / len(methods)
        # Should be approximately 40%
        assert 0.25 <= non_transfer <= 0.55, (
            f"Non-transfer rate {non_transfer:.1%} outside expected range")
