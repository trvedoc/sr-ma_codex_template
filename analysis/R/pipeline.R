# Basic independent pairwise module. Method choices belong to the approved plan.

read_text_csv <- function(path) {
  result <- read.csv(path, colClasses = "character", check.names = FALSE,
                     na.strings = character(), stringsAsFactors = FALSE)
  # Use the same surrounding-whitespace normalization as the input validator.
  result[] <- lapply(result, trimws)
  result
}

display_transform <- function(values, scale) {
  switch(scale, identity = values, log = exp(values), fisher_z = tanh(values),
         stop("Unsupported display scale."))
}

fit_synthesis <- function(group, specification) {
  if (nrow(group) < 2L) stop("This module requires at least two independent studies.")
  if (anyDuplicated(group$study_id)) stop("Repeated study IDs: dependent effects need another module.")
  estimates <- suppressWarnings(as.numeric(group$effect_value))
  variances <- suppressWarnings(as.numeric(group$sampling_variance))
  if (any(!is.finite(estimates)) || any(!is.finite(variances)) || any(variances <= 0)) {
    stop("Effect inputs must be finite and variances must be positive.")
  }
  if (any(group$effect_measure != specification$effect_measure) ||
      any(group$analysis_scale != specification$analysis_scale)) {
    stop("Mixed effect measures or analysis scales in a synthesis.")
  }
  metafor::rma.uni(
    yi = estimates, vi = variances, measure = specification$effect_measure,
    method = specification$method, test = specification$inference,
    level = as.numeric(specification$confidence_level),
    slab = if ("study_label" %in% names(group)) group$study_label else group$study_id
  )
}

summarize_fit <- function(fit, specification) {
  estimate <- as.numeric(fit$b)[1L]
  analysis_limits <- c(estimate, fit$ci.lb, fit$ci.ub)
  displayed <- display_transform(analysis_limits, specification$analysis_scale)
  data.frame(
    synthesis_id = specification$synthesis_id,
    outcome = specification$outcome, comparison = specification$comparison,
    timepoint = specification$timepoint, effect_measure = specification$effect_measure,
    analysis_scale = specification$analysis_scale, direction = specification$direction,
    method = specification$method, inference = specification$inference,
    confidence_level = as.numeric(specification$confidence_level), studies = fit$k,
    estimate_analysis_scale = estimate, ci_lower_analysis_scale = fit$ci.lb,
    ci_upper_analysis_scale = fit$ci.ub, estimate_display_scale = displayed[1L],
    ci_lower_display_scale = displayed[2L], ci_upper_display_scale = displayed[3L],
    p_value = fit$pval, between_study_variance = fit$tau2,
    heterogeneity_I2_percent = fit$I2, heterogeneity_Q = fit$QE,
    heterogeneity_Q_p_value = fit$QEp, stringsAsFactors = FALSE
  )
}

find_python <- function() {
  explicit <- Sys.getenv("SRMA_PYTHON", unset = "")
  if (nzchar(explicit)) return(explicit)
  candidate <- Sys.which("python3")
  if (!nzchar(candidate)) candidate <- Sys.which("python")
  if (!nzchar(candidate)) stop("Python 3.9 or later is required for project validation.")
  unname(candidate)
}

run_validator <- function(root, ready = TRUE) {
  arguments <- c(shQuote(file.path(root, "scripts", "validate_project.py")),
                 "--root", shQuote(root))
  if (ready) arguments <- c(arguments, "--analysis-ready")
  status <- system2(find_python(), arguments)
  if (status != 0L) stop("Project validation failed. Resolve the listed issues before analysis.")
}

run_pipeline <- function(root) {
  for (package in c("jsonlite", "metafor")) {
    if (!requireNamespace(package, quietly = TRUE)) {
      stop(paste("Missing R package:", package, "- run analysis/setup.R."))
    }
  }
  root <- normalizePath(root, mustWork = TRUE)
  run_validator(root)
  run_id <- paste0(format(Sys.time(), "%Y%m%dT%H%M%OS6Z", tz = "UTC"), "_", Sys.getpid())
  run_id <- gsub("\\.", "", run_id)
  runs <- file.path(root, "outputs", "runs")
  pending <- file.path(runs, paste0(".pending-", run_id))
  destination <- file.path(runs, run_id)
  if (dir.exists(pending) || dir.exists(destination)) stop("Run folder already exists.")
  dir.create(pending, recursive = TRUE)
  on.exit(if (dir.exists(pending)) unlink(pending, recursive = TRUE), add = TRUE)
  status <- system2(find_python(), c(
    shQuote(file.path(root, "scripts", "archive_run.py")), "--root", shQuote(root),
    "--destination", shQuote(pending)))
  if (status != 0L) stop("Could not freeze the run inputs.")

  # Fit the frozen input copy so the manifest describes the values actually analyzed.
  inputs <- file.path(pending, "inputs")
  run_validator(inputs)
  config <- jsonlite::fromJSON(file.path(inputs, "review.json"), simplifyVector = FALSE)
  effects <- read_text_csv(file.path(inputs, "analysis", "effects.csv"))
  definitions <- read_text_csv(file.path(inputs, "analysis", "syntheses.csv"))
  studies <- read_text_csv(file.path(inputs, "studies", "studies.csv"))
  selected <- effects[effects$include == "true", , drop = FALSE]
  selected$study_label <- studies$study_label[match(selected$study_id, studies$study_id)]
  selected$study_label[!nzchar(selected$study_label)] <- selected$study_id[!nzchar(selected$study_label)]
  dir.create(file.path(pending, "tables"))
  dir.create(file.path(pending, "figures"))
  dir.create(file.path(pending, "models"))
  is_demo <- identical(config$review$type, "artificial_demo")
  summaries <- list()

  for (index in seq_len(nrow(definitions))) {
    specification <- definitions[index, , drop = FALSE]
    group <- selected[selected$synthesis_id == specification$synthesis_id, , drop = FALSE]
    fit <- fit_synthesis(group, specification)
    summaries[[index]] <- summarize_fit(fit, specification)
    # Keep synthesis IDs out of output paths; index provides a stable safe filename.
    stem <- sprintf("synthesis-%03d", index)
    saveRDS(fit, file.path(pending, "models", paste0(stem, ".rds")))
    transform_function <- switch(specification$analysis_scale,
                                 identity = identity, log = exp, fisher_z = tanh)
    png(file.path(pending, "figures", paste0(stem, "-forest.png")),
        width = 1800, height = max(1200, 600 + nrow(group) * 70), res = 180)
    tryCatch({
      metafor::forest(fit, atransf = transform_function,
                      xlab = paste(specification$effect_measure, "(display scale)"),
                      main = paste(if (is_demo) "DEMO ONLY -" else "", specification$synthesis_id))
    }, finally = dev.off())
  }
  summary_table <- do.call(rbind, summaries)
  summary_table$is_artificial_demo <- is_demo
  write.csv(summary_table, file.path(pending, "tables", "synthesis-summary.csv"), row.names = FALSE)
  write.csv(selected, file.path(pending, "analysis-data.csv"), row.names = FALSE)
  capture.output(sessionInfo(), file = file.path(pending, "session-info.txt"))
  jsonlite::write_json(list(
    run_id = run_id, created_at_utc = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    review_id = config$review$id, module = config$analysis$module,
    is_artificial_demo = is_demo,
    note = "Structural checks do not establish source accuracy or scientific validity."
  ), file.path(pending, "run-metadata.json"), auto_unbox = TRUE, pretty = TRUE)
  if (is_demo) writeLines("ARTIFICIAL DEMO ONLY. No real studies or evidence.", file.path(pending, "DEMO_ONLY.txt"))
  if (!file.rename(pending, destination)) stop("Could not finalize the output folder.")
  cat(if (is_demo) "Artificial demo completed: " else "Analysis completed: ", destination, "\n", sep = "")
  invisible(destination)
}
