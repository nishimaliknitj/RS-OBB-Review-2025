"""
correct_rotation.py
===================
The CORRECT OBB rotation implementation.

Implements Theorem 3.2 of the paper:
  θ' = ((θ + φ) mod 180 + 180) mod 180

The double-modulo guard ensures correct wrapping for ALL angle values,
including negative intermediates, which arise near the 0°/180° boundary.

This is the reference implementation. Use this in your OBB pipeline.
"""

import numpy as np


def rotate_obb_correct(cx, cy, w, h, theta_deg, rotation_deg):
    """
    Correct OBB rotation augmentation.

    Applies rotation_deg to an OBB parameterised as (cx, cy, w, h, theta).
    The angle theta is in the DOTA/FAIR1M convention: θ ∈ [0°, 180°).

    Parameters
    ----------
    cx, cy      : float  Box centre coordinates (in image pixels)
    w, h        : float  Box width, height (w >= h by convention)
    theta_deg   : float  Box angle in degrees, θ ∈ [0°, 180°)
    rotation_deg: float  Image rotation angle in degrees (e.g. 90, -90, 45)

    Returns
    -------
    tuple : (cx_new, cy_new, w, h, theta_new_deg)

    Notes
    -----
    The correct wrapping formula is:
        theta_new = ((theta + rotation) % 180 + 180) % 180

    This is equivalent to Python's built-in modulo for floats because
    Python guarantees non-negative results for positive divisors. However,
    implementations using numpy.fmod, torch.fmod, or C's fmod() require
    the double-modulo guard to handle negative intermediates correctly.

    We use the double-modulo form here to be safe across ALL implementations.
    """
    rot_rad = np.deg2rad(rotation_deg)

    # Rotate centre coordinates
    cx_new = cx * np.cos(rot_rad) - cy * np.sin(rot_rad)
    cy_new = cx * np.sin(rot_rad) + cy * np.cos(rot_rad)

    # CORRECT angle update — double-modulo guard (Theorem 3.2)
    theta_new_deg = ((theta_deg + rotation_deg) % 180 + 180) % 180

    return cx_new, cy_new, w, h, theta_new_deg


def rotate_obb_correct_numpy_safe(cx, cy, w, h, theta_deg, rotation_deg):
    """
    NumPy-safe version — explicitly handles numpy.fmod behaviour.
    Use this when working with numpy arrays directly.
    """
    rot_rad = np.deg2rad(rotation_deg)

    cx_new = cx * np.cos(rot_rad) - cy * np.sin(rot_rad)
    cy_new = cx * np.sin(rot_rad) + cy * np.cos(rot_rad)

    # numpy.fmod can return negatives — double-guard required
    raw = np.fmod(theta_deg + rotation_deg, 180.0)
    theta_new_deg = np.fmod(raw + 180.0, 180.0)

    return cx_new, cy_new, w, h, theta_new_deg


def rotate_obb_batch(boxes_np, rotation_deg):
    """
    Batch rotation of multiple OBBs.

    Parameters
    ----------
    boxes_np    : np.ndarray, shape (N, 5)
                  Columns: [cx, cy, w, h, theta_deg]
    rotation_deg: float  Rotation angle in degrees

    Returns
    -------
    np.ndarray, shape (N, 5): rotated boxes
    """
    if boxes_np.ndim != 2 or boxes_np.shape[1] != 5:
        raise ValueError(
            f"boxes_np must be shape (N, 5), got {boxes_np.shape}")

    rot_rad = np.deg2rad(rotation_deg)
    cx, cy = boxes_np[:, 0], boxes_np[:, 1]

    result = boxes_np.copy()
    result[:, 0] = cx * np.cos(rot_rad) - cy * np.sin(rot_rad)
    result[:, 1] = cx * np.sin(rot_rad) + cy * np.cos(rot_rad)

    # Correct batch angle wrapping
    raw = np.fmod(boxes_np[:, 4] + rotation_deg, 180.0)
    result[:, 4] = np.fmod(raw + 180.0, 180.0)

    return result


def compute_obb_iou(box1, box2):
    """
    Approximate IoU between two OBBs using rotated rectangle intersection.

    For demonstration: uses the analytical formula for axis-aligned
    approximation. For exact OBB IoU use the PIoU or GIoU loss implementation.

    Parameters
    ----------
    box1, box2 : tuple (cx, cy, w, h, theta_deg)

    Returns
    -------
    float : approximate IoU in [0, 1]
    """
    cx1, cy1, w1, h1, t1 = box1
    cx2, cy2, w2, h2, t2 = box2

    # Angular similarity (cosine of 2*delta_theta for OBB-5 parameterisation)
    delta_theta = abs(t1 - t2)
    if delta_theta > 90:
        delta_theta = 180 - delta_theta
    angular_sim = np.cos(np.deg2rad(2 * delta_theta))

    # Area similarity
    area1 = w1 * h1
    area2 = w2 * h2
    area_ratio = min(area1, area2) / max(area1, area2)

    # Centre distance penalty
    dist = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
    diag = np.sqrt((w1/2)**2 + (h1/2)**2)
    dist_penalty = np.exp(-dist / (diag + 1e-6))

    # Approximate IoU
    iou = angular_sim * area_ratio * dist_penalty
    return float(np.clip(iou, 0.0, 1.0))


if __name__ == "__main__":
    print("CORRECT OBB Rotation Implementation")
    print("Implements Theorem 3.2 from the paper.\n")

    # Verify: θ' = ((θ + φ) mod 180 + 180) mod 180
    test_cases = [
        (5.0,    -20.0,  "Near-zero, neg rotation"),
        (2.0,    -8.0,   "Very near zero"),
        (178.0,   8.0,   "Near-180 boundary"),
        (45.0,   90.0,   "Normal case"),
        (0.0,   180.0,   "Zero angle, 180 rotation"),
        (90.0,  -90.0,   "90° both sides"),
        (179.5,   1.0,   "Extreme near-180"),
    ]

    print(f"{'Description':<30} {'theta':>7} {'rot':>7} {'result':>8}  Check")
    print("-" * 65)
    for theta, rot, desc in test_cases:
        _, _, _, _, theta_new = rotate_obb_correct(0, 0, 1, 1, theta, rot)
        in_range = 0.0 <= theta_new < 180.0
        print(f"  {desc:<28} {theta:>7.1f} {rot:>7.1f} "
              f"{theta_new:>8.2f}  "
              f"{'✓ [0,180)' if in_range else '✗ OUT OF RANGE'}")

    print("\nAll results should be in [0, 180). ✓")
