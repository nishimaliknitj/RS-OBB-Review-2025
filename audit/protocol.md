# OBB Rotation Bug Audit Protocol

## Overview

This document describes the exact 3-step protocol used to classify
22 public OBB detection repositories as **Correct** or **Buggy** with
respect to rotation augmentation angle wrapping.

**Audit period:** January 2018 – December 2025  
**Auditors:** Nishi Madaan, Rahul Malik  
**Reproducibility:** All test cases in `test_cases.py` are self-verifying.

---

## The Three-Step Protocol

### Step 1 — Convention Identification

**Goal:** Determine which OBB angle convention the repository uses.

| Convention | Angle Range | Common in |
|-----------|-------------|-----------|
| DOTA LE   | [0°, 180°)  | Most RS papers |
| OpenCV    | (-90°, 0°]  | OpenCV-based |
| Custom    | Varies      | Rare |

**Method:**
1. Search `README` and paper for "convention", "angle", "theta"
2. Check `dataset.py` or `utils/bbox.py` for angle definition
3. Run test case: input a 45° box, confirm output range

**Classification criteria:**
- DOTA LE: `assert 0 <= theta < 180`
- OpenCV: `assert -90 < theta <= 0`
- Mixed/custom: note in audit record

---

### Step 2 — Modular Arithmetic Check

**Goal:** Check if rotation augmentation uses correct wrapping.

**Search for these patterns in `augmentation.py`, `transforms.py`,
`data_augment.py`, or equivalent:**

```python
# PATTERN A — Potentially buggy (single modulo)
new_angle = (angle + rotation) % 180

# PATTERN B — Definitely buggy (fmod without guard)
new_angle = np.fmod(angle + rotation, 180)
new_angle = torch.fmod(angle + rotation, 180)

# PATTERN C — Correct (double-modulo guard)
new_angle = ((angle + rotation) % 180 + 180) % 180

# PATTERN D — Correct (numpy-safe)
raw = np.fmod(angle + rotation, 180)
new_angle = np.fmod(raw + 180, 180)

# PATTERN E — Correct (explicit clip)
new_angle = (angle + rotation) % 180
if new_angle < 0: new_angle += 180
```

**Pattern A is ambiguous** — Python's native `%` handles negatives correctly,
but if the codebase uses it with PyTorch tensors or numpy arrays,
the underlying C fmod is used, which does NOT.

**Classification:**
- Patterns B alone → **BUGGY**
- Pattern C or D → **CORRECT**
- Pattern A → run Step 3 to determine

---

### Step 3 — Empirical Test Case

**Goal:** Run a specific test to confirm correct/buggy classification.

**Test inputs (chosen to trigger the bug):**
```python
theta     = 5.0    # degrees — near-zero boundary
rotation  = -20.0  # degrees — negative rotation

expected  = 165.0  # correct result: (5 - 20 + 180) % 180 = 165
```

**Procedure:**
1. Import the repository's augmentation function
2. Apply rotation of −20° to a box with θ=5°
3. Check if result == 165° ± 0.01°

**Verdict:**
- Result ≈ 165.0 → **CORRECT**
- Result ≈ −15.0 or np.nan → **BUGGY** (fmod returned negative)
- Result ≈ 145.0 (off by 20) → different convention, check Step 1

---

## Bug Classification Taxonomy

| Bug Type | Description | Prevalence |
|----------|-------------|-----------|
| Modular wrap missing | Single `fmod` without guard | 8/13 buggy |
| 180° alias error | Off by 180° for some inputs | 3/13 buggy |
| Sign flip on reflection | Angle negated during horizontal flip | 1/13 buggy |
| Incorrect quadrant mapping | Wrong formula for DOTA→OpenCV conversion | 1/13 buggy |

---

## Audit Record Format

Each audited repository is recorded as:

```yaml
repo_id: R01
name: mmrotate/mmrotate
year: 2022
convention: OpenCV (LE)
step1_result: DOTA LE convention confirmed
step2_result: Pattern C found — correct double-modulo
step3_result: theta=5, rot=-20 → 165.0 ✓
verdict: CORRECT
angular_error_deg: 0.0
iou_maintained: 0.85
mAP_cost: 0.0
```

---

## Reproducing the Audit

```bash
# Run all test cases from the paper
python audit/test_cases.py

# Expected output:
# 9 repos: CORRECT (0° angular error)
# 13 repos: BUGGY  (mean 22.5° angular error)
# Bug rate: 59.1%
```

---

## Threats to Validity

1. **Code evolution:** Repositories may have fixed bugs after audit date
2. **Platform dependence:** `fmod` behaviour is platform-specific;
   bugs may not manifest on all systems
3. **Anonymisation:** Buggy repo names are anonymised to avoid
   adversarial forking or defacement
4. **Sampling:** 22 repos cover popular GitHub stars (>175 stars);
   may not represent low-visibility implementations
