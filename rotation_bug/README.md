# The OBB Rotation Bug

## What is it?

When rotating an Oriented Bounding Box (OBB) during data augmentation,
the rotated angle must be wrapped into the correct range using modular
arithmetic. **59% of 22 audited public repositories (2018–2025) get this wrong.**

## The Bug in One Line

```python
# BUGGY — wrong for angles near boundary
new_angle = (original_angle + rotation_degrees) % 180

# CORRECT — proper modular arithmetic with sign handling
new_angle = ((original_angle + rotation_degrees) % 180 + 180) % 180
```

The difference is subtle but catastrophic:

| Metric | Correct | Buggy |
|--------|---------|-------|
| Mean angular error | 0.0° | 22.5° |
| Mean IoU | 0.85 | 0.52 |
| mAP degradation | — | −1.8 to −4.3 mAP |

## Why Does It Happen?

Python's `%` operator returns negative values when the dividend is negative:

```python
(-10) % 180   # Python: 170  ✓ (correct for negative angles)
(-10 + 180)   # = 170
```

But many implementations use NumPy or C-style modulo, which behaves differently
for negative values. Near the boundary (θ ≈ 0° or θ ≈ 180°), rotation can
produce negative intermediate values — and the bug silently produces wrong angles.

## The Formal Proof (Theorem 3.2 of the paper)

For OBB parameterisation θ ∈ [0°, 180°), the correct rotation by φ degrees is:

```
θ' = ((θ + φ) mod 180 + 180) mod 180
```

The buggy version omits the outer `+ 180) mod 180` guard, which is a
no-op for positive intermediate values but wrong for negative ones.

The IoU degradation follows from:
- Angular error e = |θ_correct - θ_buggy| ≈ 22.5° (mean)
- IoU_rotated_box ≈ cos(2e) × IoU_correct
- At e = 22.5°: IoU ≈ cos(45°) × 0.85 ≈ 0.60 × 0.85 ≈ 0.52

## Files in this folder

| File | Description |
|------|-------------|
| `buggy_rotation.py` | The incorrect implementation (as found in 13/22 repos) |
| `correct_rotation.py` | Mathematically correct implementation |
| `compare_iou.py` | Demonstrates IoU degradation: 0.85 → 0.52 |
| `test_rotation.py` | Pytest unit tests proving the difference |

## Run the Demo

```bash
python rotation_bug/compare_iou.py
```

## Citation

If this bug fix helped your work, please cite our paper:

```bibtex
@article{madaan2025computational,
  title={Computational Methods for Data Augmentation and Labeling
         in Oriented Object Detection from Remote Sensing Imagery},
  author={Madaan, Nishi and Malik, Rahul},
  year={2025}
}
```
