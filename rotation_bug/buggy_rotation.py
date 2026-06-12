"""
buggy_rotation.py
=================
The INCORRECT OBB rotation implementation.

This is the pattern found in 59% (13/22) of audited public repositories.
Provided ONLY to document the bug described in Theorem 3.2 of the paper.
DO NOT use this in production code.

Root cause: numpy.fmod() returns values with the sign of the dividend
(C-style), so fmod(-15, 180) = -15.0 instead of 165.0.
This causes angles near 0° to become large negative values after rotation.
"""

import numpy as np


def rotate_obb_buggy_v2(cx, cy, w, h, theta_deg, rotation_deg):
    """
    BUGGY implementation using numpy.fmod — the most common pattern
    found in audited repositories using PyTorch/NumPy OBB pipelines.

    numpy.fmod(-15, 180) = -15.0  (WRONG — should be 165.0)
    Python  (-15) % 180 = 165.0   (correct)

    Fails for: theta + rotation < 0 (near-zero boundary cases)
    """
    rot_rad = np.deg2rad(rotation_deg)
    cx_new = cx * np.cos(rot_rad) - cy * np.sin(rot_rad)
    cy_new = cx * np.sin(rot_rad) + cy * np.cos(rot_rad)

    # BUG: fmod returns negative values when (theta + rotation) < 0
    theta_new_deg = np.fmod(theta_deg + rotation_deg, 180.0)

    return cx_new, cy_new, w, h, theta_new_deg


def rotate_obb_buggy(cx, cy, w, h, theta_deg, rotation_deg):
    """
    Second variant — single Python % (works in pure Python but
    fails when ported to C extensions or PyTorch).
    Included for completeness.
    """
    rot_rad = np.deg2rad(rotation_deg)
    cx_new = cx * np.cos(rot_rad) - cy * np.sin(rot_rad)
    cy_new = cx * np.sin(rot_rad) + cy * np.cos(rot_rad)
    theta_new_deg = (theta_deg + rotation_deg) % 180
    return cx_new, cy_new, w, h, theta_new_deg


if __name__ == "__main__":
    print("Demonstrating the bug:\n")
    print(f"  numpy.fmod(-15.0, 180) = {np.fmod(-15.0, 180.0):<8.2f}  "
          f"← WRONG (should be 165.0)")
    print(f"  Python (-15) % 180     = {(-15) % 180:<8.2f}  "
          f"← correct in Python, but repos use C/numpy")
    print()

    cases = [(5.0,-20.0,"near 0°"),(2.0,-8.0,"very near 0°"),(178.0,8.0,"near 180°")]
    from correct_rotation import rotate_obb_correct

    print(f"  {'Case':<15} {'theta':>6} {'rot':>6} {'correct':>9} {'buggy':>9} {'BUG?'}")
    print("  " + "-"*55)
    for theta, rot, desc in cases:
        _, _, _, _, tc = rotate_obb_correct(0, 0, 1, 1, theta, rot)
        _, _, _, _, tb = rotate_obb_buggy_v2(0, 0, 1, 1, theta, rot)
        err = abs(tc - tb)
        if err > 90: err = 180 - err
        flag = "BUG!" if err > 0.1 else "ok"
        print(f"  {desc:<15} {theta:>6.1f} {rot:>6.1f} "
              f"{tc:>9.2f} {tb:>9.2f} {flag}")
