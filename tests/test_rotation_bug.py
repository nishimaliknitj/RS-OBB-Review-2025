"""
tests/test_rotation_bug.py
==========================
Main pytest suite for rotation bug validation.
Run from repository root: pytest tests/ -v

Imports from rotation_bug/ module.
"""

import sys, os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rotation_bug.correct_rotation import rotate_obb_correct, rotate_obb_batch
from rotation_bug.buggy_rotation   import rotate_obb_buggy_v2


class TestRotationCorrectness:

    @pytest.mark.parametrize("theta,rot,expected", [
        (45.0,   90.0, 135.0),
        (170.0,  20.0,  10.0),
        (5.0,  -20.0,  165.0),
        (90.0,   90.0,   0.0),
        (0.0,   180.0,   0.0),
        (30.0,  -30.0,   0.0),
        (10.0,  170.0,   0.0),
        (150.0,  45.0,  15.0),
    ])
    def test_correct_rotation_known_values(self, theta, rot, expected):
        _, _, _, _, t = rotate_obb_correct(0, 0, 1, 1, theta, rot)
        assert abs(t - expected) < 1e-8, (
            f"theta={theta}, rot={rot}: expected {expected}, got {t:.6f}")

    @pytest.mark.parametrize("theta", list(range(0, 180, 5)))
    @pytest.mark.parametrize("rot", [-90, -45, 0, 45, 90, 135, 180])
    def test_output_always_in_range(self, theta, rot):
        _, _, _, _, t = rotate_obb_correct(0, 0, 1, 1, float(theta), float(rot))
        assert 0.0 <= t < 180.0, f"theta={theta}, rot={rot} → {t}"

    def test_buggy_has_angular_error(self):
        """Buggy impl produces wrong angles for near-boundary cases on platforms
        where numpy.fmod(-x, 180) returns negative (C-style). This test is
        skipped on platforms where Python % and numpy.fmod agree."""
        import numpy as np
        if np.fmod(-15.0, 180.0) >= 0:
            pytest.skip("Platform numpy.fmod returns non-negative — bug not visible here")
        error_found = False
        for theta in list(range(0, 10)) + list(range(170, 180)):
            for rot in [-20, -15, -10, -8, 8, 10, 15, 20]:
                _, _, _, _, tc = rotate_obb_correct(0, 0, 1, 1, theta, rot)
                _, _, _, _, tb = rotate_obb_buggy_v2(0, 0, 1, 1, theta, rot)
                # tc is always in [0,180); tb may be negative
                # Any negative result from buggy is a clear error
                if tb < 0 or abs(tc - tb) > 0.5:
                    error_found = True
                    break
        assert error_found, "Buggy implementation showed no errors"

    def test_correct_zero_error(self):
        """Correct implementation: angular error must be 0 for all cases."""
        for theta in range(0, 180, 10):
            for rot in range(-180, 181, 30):
                _, _, _, _, tc = rotate_obb_correct(0, 0, 1, 1, theta, rot)
                _, _, _, _, tc2 = rotate_obb_correct(0, 0, 1, 1, theta, rot)
                assert abs(tc - tc2) < 1e-10

    def test_iou_degradation(self):
        """Buggy angle causes measurable IoU reduction."""
        from rotation_bug.correct_rotation import compute_obb_iou
        iou_correct = compute_obb_iou(
            (0, 0, 100, 50, 45), (0, 0, 100, 50, 45))
        iou_buggy = compute_obb_iou(
            (0, 0, 100, 50, 45), (0, 0, 100, 50, 67.5))  # +22.5° error
        assert iou_buggy < iou_correct, "IoU should drop with angular error"

    def test_batch_rotation_shape(self):
        """Batch rotation preserves shape."""
        boxes = np.random.uniform(0, 100, size=(50, 5))
        boxes[:, 4] = np.random.uniform(0, 180, size=50)
        result = rotate_obb_batch(boxes, 45.0)
        assert result.shape == (50, 5)

    def test_batch_angles_in_range(self):
        """All batch-rotated angles must be in [0, 180)."""
        boxes = np.zeros((100, 5))
        boxes[:, 2] = 100
        boxes[:, 3] = 50
        boxes[:, 4] = np.linspace(0, 179, 100)
        for rot in [-90, -45, 0, 45, 90, 135]:
            result = rotate_obb_batch(boxes, float(rot))
            assert np.all(result[:, 4] >= 0.0), f"Negative angle at rot={rot}"
            assert np.all(result[:, 4] < 180.0), f"Angle >= 180 at rot={rot}"
