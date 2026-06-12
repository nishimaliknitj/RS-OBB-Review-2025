"""
effect_size_stats.py
====================
Descriptive statistics and data integrity checks for S1 dataset.

Paper: Computational Methods for RS OBB Detection (2025)

USAGE:
    python analysis/python/effect_size_stats.py
"""

import pandas as pd
import numpy as np
import os
import sys


DATA_PATH = "supplementary/Supplementary_Tables_S1_S7.xlsx"


def load_s1():
    if not os.path.exists(DATA_PATH):
        sys.exit(f"ERROR: Data file not found: {DATA_PATH}\n"
                 "Run from repository root directory.")
    df = pd.read_excel(DATA_PATH, sheet_name="S1_Effect_Sizes")
    return df


def check_integrity(df):
    """Run data integrity checks — all should pass."""
    print("\n── Data Integrity Checks ────────────────────────────────")
    checks = []

    # Row count
    n = len(df)
    checks.append(("Row count == 387", n == 387, f"got {n}"))

    # No missing effect sizes
    n_miss = df["Effect_Size_ES"].isna().sum()
    checks.append(("No missing Effect_Size_ES", n_miss == 0, f"{n_miss} missing"))

    # No missing SE
    n_miss_se = df["Std_Error_SE"].isna().sum()
    checks.append(("No missing Std_Error_SE", n_miss_se == 0, f"{n_miss_se} missing"))

    # SE > 0
    n_neg_se = (df["Std_Error_SE"] <= 0).sum()
    checks.append(("All SE > 0", n_neg_se == 0, f"{n_neg_se} non-positive SE"))

    # All 9 paradigms present
    expected_paradigms = {
        "Geometric","Photometric","FDA","SSL",
        "GAN","Diffusion","Copy-Paste","Sim2Real","AutoAug"
    }
    found_paradigms = set(df["Augmentation_Paradigm"].unique())
    missing_par = expected_paradigms - found_paradigms
    checks.append(("All 9 paradigms present",
                   len(missing_par) == 0,
                   f"missing: {missing_par}"))

    # Year range 2018-2025
    yr_ok = df["Year"].between(2014, 2025).all()
    checks.append(("Years in 2014-2025", yr_ok,
                   f"range [{df['Year'].min()},{df['Year'].max()}]"))

    # QI-8 scores 1-8
    qi_ok = df["QI8_Score"].between(1, 8).all()
    checks.append(("QI-8 scores in [1,8]", qi_ok,
                   f"range [{df['QI8_Score'].min()},{df['QI8_Score'].max()}]"))

    all_pass = True
    for name, passed, detail in checks:
        icon = "✓" if passed else "✗"
        print(f"  {icon} {name:<40s} {detail}")
        if not passed:
            all_pass = False

    return all_pass


def descriptive_stats(df):
    """Print descriptive statistics matching paper claims."""
    print("\n── Descriptive Statistics ───────────────────────────────")
    print(f"  Total effect sizes:    {len(df)}")
    print(f"  Unique papers:         {df['Paper_ID'].nunique()}")
    print(f"  Mean effect size:      {df['Effect_Size_ES'].mean():.2f} mAP")
    print(f"  Median effect size:    {df['Effect_Size_ES'].median():.2f} mAP")
    print(f"  SD effect size:        {df['Effect_Size_ES'].std():.2f} mAP")
    print(f"  Range:                 [{df['Effect_Size_ES'].min():.2f}, "
          f"{df['Effect_Size_ES'].max():.2f}] mAP")
    print(f"  Mean SE:               {df['Std_Error_SE'].mean():.2f}")

    print(f"\n  QI-8 summary:")
    print(f"    Mean QI-8:           {df['QI8_Score'].mean():.2f}/8  "
          f"(paper: 3.2)")
    print(f"    High quality (>=6):  "
          f"{(df['QI8_Score']>=6).sum()} papers "
          f"({(df['QI8_Score']>=6).mean()*100:.1f}%)  (paper: 6.3%)")
    print(f"    Moderate (4-5):      "
          f"{df['QI8_Score'].between(4,5).sum()} papers "
          f"({df['QI8_Score'].between(4,5).mean()*100:.1f}%)  (paper: 25%)")
    print(f"    Low (<=3):           "
          f"{(df['QI8_Score']<=3).sum()} papers "
          f"({(df['QI8_Score']<=3).mean()*100:.1f}%)  (paper: 68.7%)")

    print(f"\n  By paradigm:")
    par_stats = df.groupby("Augmentation_Paradigm")["Effect_Size_ES"].agg(
        n="count", mean="mean", std="std").round(2)
    print(par_stats.to_string(index=True))

    print(f"\n  TTA disclosed: "
          f"{(df['TTA_Disclosed']=='Yes').sum()} "
          f"({(df['TTA_Disclosed']=='Yes').mean()*100:.1f}%)  "
          f"(paper: 62%)")
    print(f"  Compute stated: "
          f"{(df['Compute_Stated']=='Stated').sum()} "
          f"({(df['Compute_Stated']=='Stated').mean()*100:.1f}%)  "
          f"(paper: 8%)")


def publication_years(df):
    """Temporal distribution."""
    print("\n── Publication Year Distribution ────────────────────────")
    yr = df.groupby("Year").size()
    for year, count in yr.items():
        bar = "█" * (count // 3)
        print(f"  {year}: {count:3d}  {bar}")


def main():
    print("\n" + "="*60)
    print("  Effect Size Dataset (S1) — Statistics & Integrity")
    print("="*60)

    df = load_s1()
    print(f"\nLoaded: {len(df)} rows from S1_Effect_Sizes")

    all_pass = check_integrity(df)
    descriptive_stats(df)
    publication_years(df)

    print("\n" + "="*60)
    if all_pass:
        print("  ALL INTEGRITY CHECKS PASSED ✓")
    else:
        print("  SOME CHECKS FAILED — review output above")
    print("="*60 + "\n")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
