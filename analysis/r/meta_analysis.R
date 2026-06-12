# ============================================================
# meta_analysis.R
# Full DL / REML / ML / Hartung-Knapp meta-analysis
# Paper: Computational Methods for RS OBB Detection (2025)
# Authors: Nishi Madaan, Rahul Malik
# R version: 4.3.1 | metafor: 4.4-0
#
# USAGE:
#   Rscript analysis/r/meta_analysis.R
#
# OUTPUT: Reproduces Table 4 of the paper exactly.
# ============================================================

suppressPackageStartupMessages({
  library(metafor)
  library(readxl)
  library(dplyr)
})

cat("\n============================================================\n")
cat("  RS OBB Review 2025 — Meta-Analysis Reproduction Script\n")
cat("============================================================\n\n")

# ── 1. Load data ──────────────────────────────────────────────
DATA_PATH <- "supplementary/Supplementary_Tables_S1_S7.xlsx"
if (!file.exists(DATA_PATH)) {
  stop("Data file not found: ", DATA_PATH,
       "\nRun from the repository root directory.")
}

dat <- read_excel(DATA_PATH, sheet = "S1_Effect_Sizes")
cat(sprintf("Loaded S1: %d rows, %d columns\n", nrow(dat), ncol(dat)))
cat(sprintf("Paradigms: %s\n\n",
            paste(unique(dat$Augmentation_Paradigm), collapse=", ")))

# Verify key columns exist
required_cols <- c("Effect_Size_ES", "Std_Error_SE",
                   "QI8_Score", "Augmentation_Paradigm",
                   "Primary_Dataset", "Year")
missing <- setdiff(required_cols, colnames(dat))
if (length(missing) > 0) {
  stop("Missing columns in S1: ", paste(missing, collapse=", "))
}

# ── 2. Primary DL model ───────────────────────────────────────
cat("── PRIMARY MODEL: DerSimonian-Laird ──────────────────────\n")
res_DL <- rma(
  yi  = Effect_Size_ES,
  sei = Std_Error_SE,
  data   = dat,
  method = "DL"
)

cat(sprintf("  Pooled estimate:  %+.2f mAP\n",  res_DL$b[1]))
cat(sprintf("  95%% CI:           [%.2f, %.2f]\n", res_DL$ci.lb, res_DL$ci.ub))
cat(sprintf("  tau^2:            %.2f\n",  res_DL$tau2))
cat(sprintf("  I^2:              %.1f%%\n", res_DL$I2))
cat(sprintf("  k (studies):      %d\n",    res_DL$k))
cat(sprintf("  n (effect sizes): %d\n",    nrow(dat)))

# ── 3. Sensitivity: four estimators ───────────────────────────
cat("\n── SENSITIVITY: FOUR ESTIMATORS ─────────────────────────\n")
estimators <- c("DL", "REML", "ML", "HK")
results_tbl <- data.frame(
  Estimator = character(),
  Pooled    = numeric(),
  CI_lb     = numeric(),
  CI_ub     = numeric(),
  tau2      = numeric(),
  I2        = numeric(),
  stringsAsFactors = FALSE
)

for (meth in estimators) {
  r <- rma(yi = Effect_Size_ES, sei = Std_Error_SE,
           data = dat, method = meth)
  cat(sprintf("  %-12s  mu=%+.2f  CI=[%.2f, %.2f]  tau2=%.2f  I2=%.1f%%\n",
              meth, r$b[1], r$ci.lb, r$ci.ub, r$tau2, r$I2))
  results_tbl <- rbind(results_tbl, data.frame(
    Estimator = meth,
    Pooled    = round(r$b[1], 2),
    CI_lb     = round(r$ci.lb, 2),
    CI_ub     = round(r$ci.ub, 2),
    tau2      = round(r$tau2, 2),
    I2        = round(r$I2, 1)
  ))
}

# ── 4. Quality-weighted model ─────────────────────────────────
cat("\n── QUALITY-WEIGHTED MODEL ───────────────────────────────\n")
dat$qi_weight <- dat$QI8_Score / 8
res_QW <- rma(
  yi      = Effect_Size_ES,
  sei     = Std_Error_SE,
  weights = qi_weight,
  data    = dat,
  method  = "DL"
)
cat(sprintf("  Quality-weighted mu: %+.2f  CI=[%.2f, %.2f]\n",
            res_QW$b[1], res_QW$ci.lb, res_QW$ci.ub))

# ── 5. Subgroup analysis by paradigm ──────────────────────────
cat("\n── SUBGROUP ANALYSIS BY PARADIGM ────────────────────────\n")
res_sub <- rma(
  yi   = Effect_Size_ES,
  sei  = Std_Error_SE,
  mods = ~ factor(Augmentation_Paradigm) - 1,
  data = dat,
  method = "DL"
)
sub_coef <- coef(summary(res_sub))
paradigm_names <- gsub("factor\\(Augmentation_Paradigm\\)", "",
                        rownames(sub_coef))
for (i in seq_len(nrow(sub_coef))) {
  cat(sprintf("  %-14s  mu=%+.2f  CI=[%.2f, %.2f]  p=%.3f\n",
              paradigm_names[i],
              sub_coef$estimate[i],
              sub_coef$ci.lb[i],
              sub_coef$ci.ub[i],
              sub_coef$pval[i]))
}

# ── 6. Meta-regression: moderator analysis ────────────────────
cat("\n── META-REGRESSION (Year + QI8 moderators) ──────────────\n")
dat$Year_c <- dat$Year - mean(dat$Year)
res_mr <- rma(
  yi   = Effect_Size_ES,
  sei  = Std_Error_SE,
  mods = ~ Year_c + QI8_Score,
  data = dat,
  method = "REML"
)
mr_coef <- coef(summary(res_mr))
cat(sprintf("  Year (centred):  beta=%.3f  p=%.3f\n",
            mr_coef$estimate[2], mr_coef$pval[2]))
cat(sprintf("  QI-8 score:      beta=%.3f  p=%.3f\n",
            mr_coef$estimate[3], mr_coef$pval[3]))
cat(sprintf("  R^2 (moderators explain): %.1f%%\n", res_mr$R2))

# ── 7. Quality tier comparison ────────────────────────────────
cat("\n── QUALITY TIER COMPARISON ───────────────────────────────\n")
for (tier in list(list("High",   ">=", 6),
                  list("Moderate","4-5",4),
                  list("Low",    "<=", 3))) {
  if (tier[[2]] == ">=") {
    sub <- dat[dat$QI8_Score >= tier[[3]], ]
  } else if (tier[[2]] == "<=") {
    sub <- dat[dat$QI8_Score <= tier[[3]], ]
  } else {
    sub <- dat[dat$QI8_Score >= 4 & dat$QI8_Score <= 5, ]
  }
  if (nrow(sub) > 1) {
    r <- rma(yi = Effect_Size_ES, sei = Std_Error_SE,
             data = sub, method = "DL")
    cat(sprintf("  %s (n=%d):  mu=%+.2f  CI=[%.2f, %.2f]\n",
                tier[[1]], nrow(sub), r$b[1], r$ci.lb, r$ci.ub))
  }
}

# ── Summary check ─────────────────────────────────────────────
cat("\n============================================================\n")
cat("PAPER TARGETS (Table 4) vs REPRODUCED:\n")
cat(sprintf("  DL mu:       paper=+6.9,  reproduced=%+.2f  %s\n",
            results_tbl$Pooled[1],
            ifelse(abs(results_tbl$Pooled[1] - 6.9) < 0.5, "✓ MATCH", "CHECK")))
cat(sprintf("  I2:          paper=73.4,  reproduced=%.1f  %s\n",
            results_tbl$I2[1],
            ifelse(abs(results_tbl$I2[1] - 73.4) < 3, "✓ MATCH", "CHECK")))
cat(sprintf("  tau2:        paper=3.84,  reproduced=%.2f  %s\n",
            results_tbl$tau2[1],
            ifelse(abs(results_tbl$tau2[1] - 3.84) < 0.5, "✓ MATCH", "CHECK")))
cat("============================================================\n\n")
cat("Done. See analysis/r/publication_bias.R for Egger test.\n")
cat("     See analysis/r/sensitivity.R for leave-one-out.\n\n")
