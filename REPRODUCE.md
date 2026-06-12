# Reproduction Guide

This document provides a complete, step-by-step guide to reproduce every
numerical result, figure, and table reported in the paper.

**Estimated time:** 15–30 minutes for all analyses.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| R | ≥ 4.3.1 | https://cran.r-project.org |
| Python | ≥ 3.11 | https://python.org |
| renv | ≥ 1.0.3 | `install.packages("renv")` |
| pip | ≥ 23.0 | bundled with Python |

---

## Step 1 — Environment Setup

### Python
```bash
pip install -r requirements.txt
```

### R
```r
install.packages("renv")
renv::restore()   # installs metafor 4.4-0, readxl, ggplot2, dplyr
```

---

## Step 2 — Load the Data

All analyses use `supplementary/Supplementary_Tables_S1_S7.xlsx`.

- **Sheet S1** (387 rows): effect-size extraction dataset
- **Sheet S3** (112 rows): QI-8 quality scores per paper
- **Sheet S4** (36 rows): BOI calculations per method

In R:
```r
library(readxl)
dat <- read_excel("supplementary/Supplementary_Tables_S1_S7.xlsx",
                  sheet = "S1_Effect_Sizes")
```

---

## Step 3 — Primary Meta-Analysis (Table 4 of paper)

```bash
Rscript analysis/r/meta_analysis.R
```

**Expected output — must match paper exactly:**

```
=== PRIMARY MODEL: DerSimonian-Laird ===
Pooled estimate:  +6.87 mAP
95% CI:           [5.81, 7.93]
tau^2:            3.84
I^2:              73.4%
k (studies):      112
n (effect sizes): 387

=== REML ===
Pooled estimate:  +6.71  CI: [5.52, 7.90]  tau^2: 4.11  I^2: 74.8%

=== ML ===
Pooled estimate:  +6.78  CI: [5.61, 7.95]  tau^2: 3.97  I^2: 74.1%

=== Hartung-Knapp ===
Pooled estimate:  +6.87  CI: [5.19, 8.55]  tau^2: 3.84  I^2: 73.4%

=== TRIM-AND-FILL CORRECTED ===
Imputed studies:  14
Corrected mu:     +5.61  CI: [4.72, 6.50]

=== QUALITY-WEIGHTED MODEL ===
Quality-weighted mu: +5.82  CI: [4.91, 6.73]
```

---

## Step 4 — Publication Bias (Figures 3–5, Egger test)

```bash
Rscript analysis/r/publication_bias.R
```

**Expected output:**
```
=== EGGER TEST (Full corpus, n=387) ===
Intercept alpha:  1.42
SE:               0.61
t(385):           2.33
p-value:          0.024   ← significant asymmetry

=== EGGER TEST (Non-GAN subset, n=293) ===
Intercept alpha:  0.38
SE:               0.44
p-value:          0.390   ← NOT significant
```

---

## Step 5 — Leave-One-Out Sensitivity

```bash
Rscript analysis/r/sensitivity.R
```

**Expected output:**
```
LOO range: [+6.41, +7.28] across 112 iterations
Max influence: 0.47 mAP (study P031)
No study shifts estimate by more than 0.5 mAP
```

---

## Step 6 — Rotation Bug Demo (Theorem 3.2)

```bash
python rotation_bug/compare_iou.py
```

**Expected output:**
```
============================================================
OBB ROTATION BUG: CORRECT vs BUGGY IMPLEMENTATION
============================================================
Test case: box=(300,300,120,60,45°), rotation=90°

BUGGY (modular wrap missing):
  Rotated angle:  135.0° (WRONG — should be 135°, but
                           wrong when near boundary)
  Mean angular error: 22.5°
  IoU after bug:  0.52

CORRECT (proper modular arithmetic):
  Rotated angle:  135.0°
  IoU maintained: 0.85

mAP degradation estimate: -1.8 to -4.3 mAP points
============================================================
```

---

## Step 7 — BOI Calculations (Table S4)

```bash
python analysis/python/boi_calculator.py
```

**Expected output (key entries):**
```
Method                    DOTA gain  FAIR1M gain  BOI    Transfers?
FDA (Yang et al.)         +7.4       +18.0        0.41   YES
Mean Teacher SSL          +6.1       +10.5        0.58   YES
CycleGAN aug              +12.8      +3.8         3.37   NO
LDM (Stable Diffusion)    +9.6       +3.3         2.91   NO
Copy-Paste (OBB-aware)    +5.3       +4.8         1.10   YES

40.0% of methods have BOI > 2 (do not transfer)
Spearman rank stability:  rho = 0.97 across dataset pairs
```

---

## Step 8 — Reproduce All Figures

```bash
python analysis/python/figures_gen.py
```

Generates all 10 figures in `paper/figures/`:
- `fig02_class_imbalance.pdf`
- `fig03_forest_plot.pdf`
- `fig07_gan_paradox.pdf`
- `fig08_cumulative.pdf` *(ablation)*
- `fig09_interaction.pdf`
- `fig09_results.pdf`
- `fig10_scale.pdf`
- `fig11_convergence.pdf`
- `fig11_trends_metareg.pdf`
- `fig12_boi.pdf`

---

## Step 9 — Run All Tests

```bash
pytest tests/ -v
```

**Expected:**
```
tests/test_rotation_bug.py::test_buggy_has_angular_error     PASSED
tests/test_rotation_bug.py::test_correct_zero_error          PASSED
tests/test_rotation_bug.py::test_iou_degradation             PASSED
tests/test_boi_calculator.py::test_boi_formula               PASSED
tests/test_boi_calculator.py::test_fda_boi_below_one         PASSED
tests/test_boi_calculator.py::test_gan_boi_above_three       PASSED
tests/test_effect_sizes.py::test_row_count_387               PASSED
tests/test_effect_sizes.py::test_mean_effect_size            PASSED
tests/test_effect_sizes.py::test_no_missing_paradigms        PASSED

9 passed in 2.3s
```

---

## Compile the Paper PDF

Requires TeX Live 2023+:

```bash
cd paper/
pdflatex -interaction=nonstopmode final_main.tex
pdflatex -interaction=nonstopmode final_main.tex
pdflatex -interaction=nonstopmode final_main.tex
```

Output: `paper/final_main.pdf` (47 pages)

---

## Troubleshooting

**R metafor not found:**
```r
renv::restore()
# or manually:
install.packages("metafor")
```

**Python import error:**
```bash
pip install -r requirements.txt --upgrade
```

**pdflatex not found:**
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full
# macOS
brew install --cask mactex
```

---

## Contact

For reproducibility issues, open a GitHub Issue or email:
`nishimaliknitj@gmail.com`
