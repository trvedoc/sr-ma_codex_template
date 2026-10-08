# Checks of this starter template

Checked on October 8, 2026. These checks concern the reusable scaffold and artificial
test data. They are not checks of a real review's studies, methods, or conclusions.

- Structural validation passed for the empty starter; real analysis remains disabled.
- Sixteen Python tests passed, including identifiers, declared approvers, source-entry
  verification, scale consistency, invalid variances, exclusion decisions, deduplication,
  search-record counts, malformed CSV/JSON, and automatic readiness checks when enabled.
- R numerical checks matched independent inverse-variance reference calculations for
  the pooled estimate, standard error, and confidence interval on artificial data.
- Log-ratio display conversion and Fisher-z display conversion were checked.
- The R module rejected dependent effects, invalid variances, mixed scales, and a
  single-study input.
- The artificial demo completed end to end, saving frozen inputs, SHA-256 hashes,
  session information, model objects, tables, and a forest plot. The plot was inspected.

The local analysis checks used R 4.4.3, metafor 4.8-0, and jsonlite 2.0.0. Package
versions and their dependencies are recorded in renv.lock.

GitHub-hosted checks have not been run remotely. A fresh renv download/restore has
not been tested on a second machine. Quarto is not installed in the authoring
environment, so the manuscript outline has not been rendered.

After adapting the template, add checks appropriate to your effect calculations,
study designs, model choices, and manuscript. A different analytical module requires
its own numerical and methodological validation.
