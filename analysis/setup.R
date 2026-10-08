# Run from the repository root. Restores the recorded project environment.
if (!file.exists("review.json")) stop("Run setup.R from the repository root.")
if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv", repos = "https://cloud.r-project.org")
}
renv::restore(project = getwd(), prompt = FALSE)
renv::activate(project = getwd())
cat("R environment restored. Run analysis/tests/test_pipeline.R next.\n")
