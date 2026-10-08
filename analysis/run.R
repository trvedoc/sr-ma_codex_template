# Run from any directory; --root can select an explicit review copy.
arguments <- commandArgs(trailingOnly = TRUE)
file_argument <- grep("^--file=", commandArgs(), value = TRUE)[1L]
script_path <- sub("^--file=", "", file_argument)
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
if (length(arguments)) {
  if (length(arguments) != 2L || arguments[1L] != "--root") {
    stop("Usage: Rscript analysis/run.R [--root /path/to/review]")
  }
  root <- normalizePath(arguments[2L], mustWork = TRUE)
}
source(file.path(root, "analysis", "R", "pipeline.R"))
run_pipeline(root)
