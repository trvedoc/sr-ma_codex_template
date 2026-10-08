# Working rules for this review

## Read first
Read README.md, review.json, protocol/protocol.md, protocol/analysis-plan.md, and
extraction/codebook.md before substantive review work. Follow the human user's
instructions and approved project methods. Define every variable when giving an equation.

## Records and sources
- Preserve original database exports. Put cleaned records in separate files.
- Keep record_id, report_id, study_id, entry_id, and effect_id stable.
- Multiple reports can describe the same study. Do not treat reports as independent studies.
- Preserve individual reviewer entries. Put resolved decisions in the designated final tables.
- Attach a report identifier and exact page, table, figure, supplement, or section location
  to every extraction. Record ambiguous or missing information explicitly.
- Do not invent studies, citations, sample sizes, outcomes, dates, or numeric data.

## AI and human review
- Save AI candidates and run metadata under ai/runs/. Include model/version when available,
  prompt, source IDs, date, output, and the human verification result.
- AI output begins as a proposal. Only a human researcher may approve eligibility,
  verified extractions, risk-of-bias judgments, certainty judgments, or analysis plans.
  Do not fill human approval fields on the strength of AI agreement.
- AI agents do not count as human reviewers. Preserve the independence required by
  the project's protocol; keep one reviewer's decisions hidden from the other when needed.
- A private GitHub repository can still expose reviewers' decisions to teammates.
  Use access-controlled reviewer workspaces or a suitable screening tool when blinding is required.

## Analysis
- Read the approved plan. Propose unresolved choices for human decision; record deviations
  in protocol/amendments.csv. Do not pick a model merely because it gives a preferred result.
- Preserve reported values. Document conversions, assumptions, missing-data handling,
  and selection among outcomes, arms, timepoints, and multiple reports.
- Use verified source-linked inputs. Effect inputs must name their adjudicated input entry IDs.
- The supplied module permits only one independent effect per study within each synthesis.
  Use an appropriate new module for dependence, network meta-analysis, or specialized designs.
- Keep variances distinct from standard errors. Ratios use log analysis scale in this module.
- Never manually edit generated model results, plots, or tables.

## Checks and handoff
- Run python3 scripts/validate_project.py after changing data forms or review records.
- Run python3 -m unittest discover -s tests -v after changing the validator.
- Run Rscript analysis/tests/test_pipeline.R after changing the analysis module.
- For a configured analysis, run the --analysis-ready validation and analysis/run.R.
- Do not call passing checks proof of scientific correctness. Report remaining source,
  methodological, software, and rendering limitations clearly.
- Keep credentials and local PDFs out of Git. Review permitted data and AI logs before sharing.
- Document final changes in a pull request and preserve the exact submission version.
