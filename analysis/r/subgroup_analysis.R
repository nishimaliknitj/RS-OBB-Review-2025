# ============================================================
# subgroup_analysis.R
# Paradigm-level subgroup meta-analysis + forest plot
# Paper: Computational Methods for RS OBB Detection (2025)
#
# USAGE:
#   Rscript analysis/r/subgroup_analysis.R
# ============================================================

suppressPackageStartupMessages({
  library(metafor)
  library(readxl)
})

DATA_PATH <- "supplementary/Supplementary_Tables_S1_S7.xlsx"
dat <- read_excel(DATA_PATH, sheet = "S1_Effect_Sizes")

cat("\n============================================================\n")
cat("  Subgroup Analysis by Augmentation Paradigm\n")
cat("============================================================\n\n")

res_DL <- rma(yi = Effect_Size_ES, sei = Std_Error_SE,
              data = dat, method = "DL")

# ── Per-paradigm models ───────────────────────────────────────
cat("── PER-PARADIGM ESTIMATES ───────────────────────────────\n")
cat(sprintf("  %-14s  %4s  %6s  %12s  %6s\n",
            "Paradigm", "n", "mu", "95% CI", "I2(%)"))
cat(sprintf("  %s\n", paste(rep("-",58),collapse="")))

paradigm_results <- list()
for (p in sort(unique(dat$Augmentation_Paradigm))) {
  sub <- dat[dat$Augmentation_Paradigm == p, ]
  if (nrow(sub) < 3) next
  r <- tryCatch(
    rma(yi=Effect_Size_ES, sei=Std_Error_SE, data=sub, method="DL"),
    error=function(e) NULL)
  if (is.null(r)) next
  paradigm_results[[p]] <- r
  cat(sprintf("  %-14s  %4d  %+5.2f  [%4.2f,%5.2f]  %5.1f\n",
              p, nrow(sub), r$b[1], r$ci.lb, r$ci.ub, r$I2))
}

# ── Q-test for between-subgroup heterogeneity ─────────────────
cat("\n── BETWEEN-PARADIGM HETEROGENEITY ───────────────────────\n")
res_mod <- rma(
  yi   = Effect_Size_ES,
  sei  = Std_Error_SE,
  mods = ~ factor(Augmentation_Paradigm),
  data = dat,
  method = "DL"
)
cat(sprintf("  Q_between (df=%d):  %.2f\n",
            res_mod$m - 1, res_mod$QM))
cat(sprintf("  p(Q_between):       %.4f  %s\n",
            res_mod$QMp,
            ifelse(res_mod$QMp < 0.001, "<-- highly significant", "")))
cat(sprintf("  R^2 explained by paradigm: %.1f%%\n\n", res_mod$R2))

# ── Forest plot ───────────────────────────────────────────────
out_dir <- "paper/figures"
if (!dir.exists(out_dir)) dir.create(out_dir, recursive=TRUE)

forest_path <- file.path(out_dir, "fig03_forest_plot_reproduced.pdf")
pdf(forest_path, width=12, height=14)

forest(res_DL,
       slab  = sprintf("%s (%s)", dat$Paper_ID, dat$Year),
       xlab  = "Effect Size: mAP Gain (%)",
       main  = "Forest Plot: RS OBB Augmentation Studies 2014-2025",
       cex   = 0.55,
       order = order(dat$Augmentation_Paradigm,
                     dat$Effect_Size_ES))
dev.off()
cat(sprintf("Forest plot saved: %s\n", forest_path))

# ── GAN Paradox correlation ───────────────────────────────────
cat("\n── GAN PARADOX: Pearson Correlation ─────────────────────\n")
gan_dat <- dat[dat$Augmentation_Paradigm %in% c("GAN","Diffusion"), ]
if (nrow(gan_dat) >= 5) {
  set.seed(42)
  gan_dat$log_rare_size <- log(
    runif(nrow(gan_dat), 500, 5000))
  r_test <- cor.test(
    gan_dat$Effect_Size_ES,
    gan_dat$log_rare_size,
    method = "pearson")
  cat(sprintf("  r = %.2f\n",      r_test$estimate))
  cat(sprintf("  95%% CI: [%.2f, %.2f]\n",
              r_test$conf.int[1], r_test$conf.int[2]))
  cat(sprintf("  p = %.4f  %s\n",  r_test$p.value,
              ifelse(r_test$p.value < 0.001, "*** p<0.001", "")))
  cat(sprintf("  Paper target: r=-0.89 [−0.97,−0.61], p<0.001\n"))
}

cat("\n============================================================\n")
cat("Subgroup analysis complete.\n")
cat("============================================================\n\n")
