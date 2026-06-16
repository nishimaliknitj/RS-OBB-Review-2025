# Computational Methods for Data Augmentation and Labeling in Oriented Object Detection from Remote Sensing Imagery

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRISMA 2020](https://img.shields.io/badge/PRISMA-2020%20Compliant-brightgreen)](supplementary/)
[![R Version](https://img.shields.io/badge/R-4.3.1-blue.svg)](analysis/r/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](analysis/python/)
[![DOI](https://img.shields.io/badge/DOI-10.xxxx%2Fxxxx-orange)](https://doi.org/10.xxxx/xxxx)

>

---

## Overview

This repository contains the complete reproducibility package for our systematic review of **112 peer-reviewed works (2014–2025)** on data augmentation and labeling methods for oriented object detection (OBB) in remote sensing imagery.

### Key Findings

| Finding | Result |
|---|---|
| **Meta-analytic pooled effect** | +6.9% mAP (95% CI: 5.8–8.0%), I²=73.4% |
| **OBB rotation bug rate** | 59% of 22 audited public repositories contain implementation errors |
| **GAN Paradox** | r=−0.89 (p<0.001): generative augmentation harms every rare RS category |
| **Benchmark Overfitting Index (BOI)** | 40% of DOTA-v1.0 gains do not transfer (BOI>2) |
| **Best strategy** | FDA achieves BOI=0.41 — best cross-dataset generalisation |
| **Publication bias** | Localised exclusively to GAN studies (Egger: α=1.42, p=0.024) |

---

## Repository Structure

```
RS-OBB-Review-2025/
│
├── README.md                    ← This file
├── REPRODUCE.md                 ← Step-by-step reproduction guide
├── CITATION.cff                 ← Machine-readable citation
├── LICENSE                      ← MIT License
├── requirements.txt             ← Python dependencies
├── renv.lock                    ← R package lockfile
│
├── paper/                       ← LaTeX source of main paper
│   ├── final_main.tex
│   ├── sn-jnl.cls
│   ├── sn-bibliography.bib
│   └── figures/                 ← All 10 PDF figures
│
├── supplementary/               ← Supplementary material (S1–S7)
│   └── Supplementary_Tables_S1_S7.xlsx
│
├── analysis/
│   ├── r/
│   │   ├── meta_analysis.R      ← Full DL/REML/ML/HK meta-analysis
│   │   ├── publication_bias.R   ← Egger test + trim-and-fill
│   │   ├── sensitivity.R        ← Leave-one-out + estimator comparison
│   │   └── subgroup_analysis.R  ← Paradigm-level subgroup models
│   └── python/
│       ├── boi_calculator.py    ← BOI computation for any method
│       ├── figures_gen.py       ← Reproduce all 10 paper figures
│       └── effect_size_stats.py ← Descriptive statistics for S1 data
│
├── rotation_bug/
│   ├── README.md                ← Explains the bug and its impact
│   ├── buggy_rotation.py        ← Incorrect implementation (59% repos)
│   ├── correct_rotation.py      ← Mathematically correct implementation
│   ├── compare_iou.py           ← Shows IoU drop: 0.85 → 0.52
│   └── test_rotation.py         ← Unit tests proving the difference
│
├── audit/
│   ├── protocol.md              ← 3-step audit classification protocol
│   ├── decision_tree.md         ← Auditor decision tree (reproducible)
│   └── test_cases.py            ← Verification test cases
│
├── boi_calculator/
│   ├── boi_tool.py              ← Standalone BOI calculator
│   └── README.md
│
├── notebooks/
│   ├── 01_meta_analysis.ipynb   ← Full meta-analysis walkthrough
│   ├── 02_forest_plot.ipynb     ← Forest plot reproduction
│   ├── 03_publication_bias.ipynb← Egger + funnel + trim-and-fill
│   ├── 04_boi_analysis.ipynb    ← BOI calculations + visualisation
│   └── 05_rotation_bug_demo.ipynb ← Interactive bug demonstration
│
├── tests/
│   ├── test_rotation_bug.py     ← Pytest: rotation correctness
│   ├── test_boi_calculator.py   ← Pytest: BOI formula
│   └── test_effect_sizes.py     ← Pytest: S1 data integrity checks
│
└── .github/
    └── workflows/
        ├── test.yml             ← Run pytest on push
        ├── latex_compile.yml    ← Compile PDF on push
        ├── figures.yml          ← Regenerate figures
        └── reproduce.yml        ← End-to-end numbers validation
```

---

## Quick Reproduction (5 minutes)

```bash
# 1. Clone
git clone https://github.com/nishimaliknitj/RS-OBB-Review-2025
cd RS-OBB-Review-2025

# 2. Python environment
pip install -r requirements.txt

# 3. R environment
Rscript -e "install.packages('renv'); renv::restore()"

# 4. Run full meta-analysis — should reproduce Table 4 of paper
Rscript analysis/r/meta_analysis.R

# 5. Run rotation bug demo
python rotation_bug/compare_iou.py

# 6. Run all tests
pytest tests/ -v
```

**Expected output from step 4:**
```
DL:  mu=+6.87, CI=[5.81, 7.93], tau2=3.84, I2=73.4%
REML: mu=+6.71, CI=[5.52, 7.90], tau2=4.11, I2=74.8%
ML:  mu=+6.78, CI=[5.61, 7.95], tau2=3.97, I2=74.1%
HK:  mu=+6.87, CI=[5.19, 8.55], tau2=3.84, I2=73.4%
Trim-and-fill: mu=+5.61, CI=[4.72, 6.50]
Quality-weighted: mu=+5.82, CI=[4.91, 6.73]
```

---

## Cite This Work

```bibtex
@article{madaan2025computational,
  title   = {Computational Methods for Data Augmentation and Labeling
             in Oriented Object Detection from Remote Sensing Imagery:
             A Critical Review of Algorithms, Documented Failures,
             and Engineering Guidelines},
  author  = {Madaan, Nishi and Malik, Rahul},
  journal = {ACME},
  year    = {2025},
  note    = {Under Review},
  url     = {https://github.com/nishimaliknitj/RS-OBB-Review-2025}
}
```

---

## License

This repository is licensed under the [MIT License](LICENSE).  
The paper itself is © 2025 Nishi Madaan, Rahul Malik. All rights reserved pending journal publication.
