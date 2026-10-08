# Data dictionary and extraction rules

## Identifiers
- record_id: one search hit, even if it duplicates another hit.
- search_id: one logged search/export event.
- report_id: one publication, registry report, or other source document.
- study_id: one underlying study, potentially described in several reports.
- entry_id: one extracted item within its owning extraction table.
- synthesis_id: one defined outcome/comparison/timepoint synthesis.
- effect_id: one derived or reported effect estimate proposed for analysis.
- reviewer_id: a human team ID declared in review.json.

Treat identifiers as text. Do not recycle an ID after a row is removed. Extra reports
found by citation searching should receive search records and reports of their own.

## General conventions
CSV files are UTF-8. Quote cells containing commas or newlines. Dates use YYYY-MM-DD.
Keep original numbers and units. A blank numeric value means unavailable, not zero.
Use value_status: reported, not_reported, unclear, or not_applicable.
Keep reported missing-data indicators in source_quote if relevant.
Verification status is pending or verified. verified_by identifies a human who checked
the original source, and verified_date records the check date.
The validator checks structure and declared approver IDs; it cannot authenticate a signature.

## Search and deduplication
Each record points to a logged search. Preserve exports unchanged.
In deduplication-map.csv, use one row per search record. A retained record maps to
itself with decision=retained. A duplicate maps to its canonical retained record
with decision=duplicate. Do not use chains of duplicate mappings.
search-log records_exported counts the records actually represented by that search ID.

## Screening
Individual decisions: include, exclude, or unclear. Final decisions: include or exclude.
Individual tables have one row per item/reviewer; final tables have one row per item.
Document reasons for full-text exclusions. final-title-abstract includes only retained
records; final-full-text uses report IDs. Missing final decisions remain unresolved.
Track reports not retrieved separately from reports excluded after assessment;
use availability_status=unavailable in reports.csv and account for them in flow counts.

## Extraction and bias assessment
source_location identifies an exact page/table/figure/section/supplement.
source_quote is a short supporting excerpt; it is optional, and should remain concise.
Customize field, arm, outcome, timepoint, and unit definitions below before extraction.
Define bias tool/version, domains, permissible judgments, and assessment unit in the protocol.
Add reviewers as needed; keep independent entries separate from adjudicated values.

Project-specific fields and coding rules: [FILL]

## Synthesis definitions
Each row in analysis/syntheses.csv defines one synthesis with an approved plan.
effect_measure: MD, SMD, RR, OR, HR, RD, ZCOR, or GEN.
analysis_scale: identity for MD/SMD/RD; log for RR/OR/HR; fisher_z for ZCOR.
GEN requires an explicitly justified identity, log, or fisher_z scale.
direction describes how positive/larger estimates should be interpreted.
method: EE, FE, REML, DL, or PM; inference: z, t, or knha.
confidence_level is a percentage strictly between zero and 100.
plan_location points to the relevant section of the project analysis plan.

## Effect inputs
effect_value: the effect estimate already expressed on the declared analysis scale.
sampling_variance: its sampling variance on that same scale; it is not a standard error.
input_entry_ids: semicolon-separated adjudicated extraction entry IDs supporting the effect.
derivation: a traceable calculation or script/function reference with assumptions.
include: true or false. Excluded effects need exclusion_reason; they remain in the file.
Included effects must be verified, supported by verified entries from the same study,
and linked to an included source report. The basic module accepts at least two studies
per synthesis and rejects repeated study IDs within a synthesis.
The module back-transforms log estimates with the exponential function and Fisher-z
estimates with the hyperbolic tangent; it keeps both scales in generated tables.

## Schema changes
data/schema.json records required column names. Extra columns are permitted.
Extend the codebook, schema, and validator together when changing required fields.
Header-only files represent an unused or not-yet-started stage, not a completed stage.
