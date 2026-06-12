"""
tests/test_effect_sizes.py
==========================
Data integrity tests for Supplementary Table S1 (387 effect sizes).
"""

import sys, os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH = "supplementary/Supplementary_Tables_S1_S7.xlsx"

@pytest.fixture(scope="module")
def s1_data():
    """Load S1 once for all tests — filter to actual data rows only."""
    try:
        import pandas as pd
        if not os.path.exists(DATA_PATH):
            pytest.skip(f"S1 data not found at {DATA_PATH}")
        df = pd.read_excel(DATA_PATH, sheet_name="S1_Effect_Sizes")
        # Filter out summary/blank rows at bottom (keep only rows with valid Obs_ID)
        df = df[df["Obs_ID"].notna() & df["Obs_ID"].astype(str).str.startswith("OBS-")]
        return df
    except ImportError:
        pytest.skip("pandas/openpyxl not installed")


class TestS1DataIntegrity:

    def test_row_count_387(self, s1_data):
        assert len(s1_data) == 387, f"Expected 387 rows, got {len(s1_data)}"

    def test_mean_effect_size(self, s1_data):
        mean_es = s1_data["Effect_Size_ES"].mean()
        assert 5.0 < mean_es < 10.0, (
            f"Mean ES={mean_es:.2f} outside plausible range [5, 10]")

    def test_no_missing_effect_sizes(self, s1_data):
        n_miss = s1_data["Effect_Size_ES"].isna().sum()
        assert n_miss == 0, f"{n_miss} missing Effect_Size_ES values"

    def test_no_missing_se(self, s1_data):
        n_miss = s1_data["Std_Error_SE"].isna().sum()
        assert n_miss == 0, f"{n_miss} missing SE values"

    def test_all_se_positive(self, s1_data):
        n_neg = (s1_data["Std_Error_SE"] <= 0).sum()
        assert n_neg == 0, f"{n_neg} non-positive SE values"

    def test_no_missing_paradigms(self, s1_data):
        expected = {
            "Geometric","Photometric","FDA","SSL",
            "GAN","Diffusion","Copy-Paste","Sim2Real","AutoAug"
        }
        found = set(s1_data["Augmentation_Paradigm"].unique())
        missing = expected - found
        assert len(missing) == 0, f"Missing paradigms: {missing}"

    def test_year_range(self, s1_data):
        assert s1_data["Year"].between(2014, 2025).all(), (
            f"Years outside [2014,2025]: "
            f"{s1_data['Year'][~s1_data['Year'].between(2014,2025)].unique()}")

    def test_qi8_score_range(self, s1_data):
        assert s1_data["QI8_Score"].between(1, 8).all(), (
            f"QI-8 scores outside [1,8]")

    def test_unique_obs_ids(self, s1_data):
        n_unique = s1_data["Obs_ID"].nunique()
        assert n_unique == len(s1_data), (
            f"Duplicate Obs_IDs: {len(s1_data) - n_unique} duplicates")

    def test_tta_values_valid(self, s1_data):
        valid = {"Yes", "No"}
        found = set(s1_data["TTA_Disclosed"].unique())
        assert found.issubset(valid), f"Invalid TTA values: {found - valid}"


class TestS2DataIntegrity:

    @pytest.fixture(scope="class")
    def s2_data(self):
        try:
            import pandas as pd
            if not os.path.exists(DATA_PATH):
                pytest.skip("S2 data not found")
            return pd.read_excel(DATA_PATH, sheet_name="S2_Repo_Audit")
        except ImportError:
            pytest.skip("pandas/openpyxl not installed")

    def test_row_count_22(self, s2_data):
        assert len(s2_data) == 22, f"Expected 22 repos, got {len(s2_data)}"

    def test_bug_rate_59pct(self, s2_data):
        buggy = (s2_data["Correct_Implementation"] == "No").sum()
        rate = buggy / len(s2_data)
        assert 0.55 <= rate <= 0.65, (
            f"Bug rate {rate:.1%} outside expected [55%, 65%]")

    def test_bug_count_13(self, s2_data):
        buggy = (s2_data["Correct_Implementation"] == "No").sum()
        assert buggy == 13, f"Expected 13 buggy repos, got {buggy}"


class TestS4DataIntegrity:

    @pytest.fixture(scope="class")
    def s4_data(self):
        try:
            import pandas as pd
            if not os.path.exists(DATA_PATH):
                pytest.skip("S4 data not found")
            return pd.read_excel(DATA_PATH, sheet_name="S4_BOI_Calculations")
        except ImportError:
            pytest.skip("pandas/openpyxl not installed")

    def test_fda_boi_below_one(self, s4_data):
        fda = s4_data[s4_data["Paradigm"] == "FDA"]
        assert (fda["BOI_Primary"] < 1.0).all(), (
            f"FDA BOI values not all < 1: {fda['BOI_Primary'].values}")

    def test_gan_boi_above_two(self, s4_data):
        gan = s4_data[s4_data["Paradigm"] == "GAN"]
        assert (gan["BOI_Primary"] > 2.0).all(), (
            f"GAN BOI values not all > 2: {gan['BOI_Primary'].values}")

    def test_boi_positive(self, s4_data):
        assert (s4_data["BOI_Primary"] > 0).all(), "All BOI must be positive"
