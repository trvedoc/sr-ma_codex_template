# Analysis plan

Status: DRAFT. Specify the methods for this review before enabling the analysis.

## Synthesis definitions
List each outcome, comparison, population, timepoint, and eligible study design.
Define when studies are sufficiently comparable to pool and when to use narrative synthesis.
Assign each synthesis a stable synthesis_id in analysis/syntheses.csv.

## Effect inputs
Specify the effect measure, direction, units, analysis scale, and display scale.
Specify calculations from extracted values, sampling-variance calculations, and
any adjusted/unadjusted estimate selection. Define every variable in an equation.
Link effect inputs to adjudicated extraction entry IDs. Keep reported values intact.

## Unit of analysis and dependence
Specify handling of multiple reports, multiple arms, repeated measurements,
overlapping samples, cluster designs, and correlated effects. The included module
accepts one independent effect per study in a synthesis; repeated study IDs fail validation.

## Models and inference
Justify the model, between-study variance estimator where applicable, confidence
interval method, confidence level, and interpretation. The included module supports
EE, FE, REML, DL, or PM models, and z, t, or knha inference where appropriate.
These options are software capabilities, not recommendations for every review.

## Missing data and conversions
Define missing-data decisions, assumptions, imputation, standard deviation
recovery, unit conversion, zero events, small samples, and exclusions.
Implement effect calculations in analysis/R/prepare_effects.R and test them
against independent known examples before using them on the review.

## Additional analyses
Prespecify heterogeneity interpretation, prediction intervals if appropriate,
influence analysis, sensitivity analyses, subgroup analyses, meta-regression,
reporting bias assessment, and eligibility thresholds for those analyses.
These are not automatically run by the supplied basic module.

## Validation and approvals
Document independent checks of source values, derived effects, and selected model.
Approved by: [FILL]
Approval date: [FILL]
Record amendments, including their timing and reasons, in amendments.csv.
