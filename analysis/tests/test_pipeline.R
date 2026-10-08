# Numerical checks use artificial inputs, never real review data.
file_argument <- grep("^--file=", commandArgs(), value = TRUE)[1L]
script_path <- sub("^--file=", "", file_argument)
root <- normalizePath(file.path(dirname(script_path), "..", ".."), mustWork = TRUE)
source(file.path(root, "analysis", "R", "pipeline.R"))
if (!requireNamespace("metafor", quietly = TRUE)) stop("Run analysis/setup.R first.")
whitespace_fixture <- tempfile(fileext = ".csv")
writeLines(c("study_id,include", '" ARTIFICIAL1 "," true "'), whitespace_fixture)
normalized <- read_text_csv(whitespace_fixture)
stopifnot(normalized$study_id == "ARTIFICIAL1", normalized$include == "true")
unlink(whitespace_fixture)

group <- data.frame(study_id = c("ARTIFICIAL1", "ARTIFICIAL2"),
                    effect_value = c(0.2, 0.6), sampling_variance = c(0.04, 0.09),
                    effect_measure = "MD", analysis_scale = "identity")
specification <- data.frame(synthesis_id = "ARTIFICIAL", outcome = "Artificial outcome",
                            comparison = "A vs B", timepoint = "Artificial endpoint",
                            effect_measure = "MD", analysis_scale = "identity",
                            direction = "Higher artificial outcome", method = "FE",
                            inference = "z", confidence_level = "95")
fit <- fit_synthesis(group, specification)
# Independent reference calculation: weights are inverse sampling variances;
# reference_estimate is the weighted mean, and reference_se is its standard error.
weights <- 1 / group$sampling_variance
reference_estimate <- sum(weights * group$effect_value) / sum(weights)
reference_se <- sqrt(1 / sum(weights))
reference_limits <- reference_estimate + c(-1, 1) * qnorm(0.975) * reference_se
stopifnot(abs(as.numeric(fit$b) - reference_estimate) < 1e-10,
          abs(fit$se - reference_se) < 1e-10,
          max(abs(c(fit$ci.lb, fit$ci.ub) - reference_limits)) < 1e-10)

ratio_group <- group
ratio_group$effect_value <- log(c(2, 4))
ratio_group$effect_measure <- "RR"
ratio_group$analysis_scale <- "log"
ratio_spec <- specification
ratio_spec$effect_measure <- "RR"
ratio_spec$analysis_scale <- "log"
ratio_fit <- fit_synthesis(ratio_group, ratio_spec)
ratio_summary <- summarize_fit(ratio_fit, ratio_spec)
reference_ratio <- exp(sum(weights * log(c(2, 4))) / sum(weights))
stopifnot(abs(ratio_summary$estimate_display_scale - reference_ratio) < 1e-10,
          identical(display_transform(0, "log"), 1),
          abs(display_transform(atanh(0.5), "fisher_z") - 0.5) < 1e-10)

expect_failure <- function(expression) {
  failure <- inherits(try(force(expression), silent = TRUE), "try-error")
  if (!failure) stop("Expected invalid input to be rejected.")
}
duplicate <- group
duplicate$study_id[2L] <- duplicate$study_id[1L]
expect_failure(fit_synthesis(duplicate, specification))
invalid <- group
invalid$sampling_variance[1L] <- 0
expect_failure(fit_synthesis(invalid, specification))
invalid$sampling_variance[1L] <- Inf
expect_failure(fit_synthesis(invalid, specification))
expect_failure(fit_synthesis(group[1L, , drop = FALSE], specification))
mixed <- group
mixed$analysis_scale[2L] <- "log"
expect_failure(fit_synthesis(mixed, specification))

cat("Numerical reference checks and invalid-input checks passed on artificial data.\n")
