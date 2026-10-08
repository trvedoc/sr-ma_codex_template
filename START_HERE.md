# Start a new review

## Make your reusable GitHub template

1. Upload the contents of this folder to a new repository named, for example, `sr-ma-template`.
   Include the hidden `.github/` folder and `.gitignore`; a Git push preserves them.
2. In the repository's **Settings**, select **Template repository**.
3. For each new review, select **Use this template → Create a new repository**.
   Changes to the template do not automatically update existing review repositories.
4. Open the new review repository in Codex. Its `AGENTS.md` provides working rules.

## Customize the new copy

- [ ] Fill `review.json`: review ID, title, question, type, registration, protocol version,
  and team. Each team member is an object with `id`, `name`, and `role`.
  Use stable IDs such as `reviewer-a`; declare only actual human team members.
- [ ] Complete `protocol/protocol.md` and `protocol/analysis-plan.md`.
- [ ] Choose the conduct/reporting guidance, extraction fields, risk-of-bias tool,
  and certainty framework appropriate to the question.
- [ ] Pilot screening and extraction forms on a small sample. Add project-specific
  fields consistently and update `data/schema.json` and `extraction/codebook.md`.
- [ ] Agree on the independent-review and disagreement-resolution process.
- [ ] Preserve original search exports and log exact searches and dates.
- [ ] Record reviewer decisions and resolve disagreements in the final tables.
- [ ] Link every report to its underlying study. Preserve all search records and
  map duplicate hits to one retained record.
- [ ] Record verified extractions, keeping individual entries intact.
- [ ] Define each intended synthesis in `analysis/syntheses.csv` and record approval.
- [ ] Create the effect inputs in `analysis/effects.csv` using documented,
  project-specific calculations and source entry IDs.
- [ ] For the included module, set `analysis.module` to `pairwise_independent` and
  `analysis.enabled` to `true`; record the plan approver and date in `review.json`.
- [ ] Run the validation, analysis, and relevant numerical checks.
- [ ] Complete the manuscript, PRISMA checklist, and verified flow counts.
- [ ] Tag the submitted version and retain its results and input manifest.

## Starter prompt for Codex

> Read AGENTS.md and START_HERE.md. Help me configure this review from its research
> question and protocol. List unresolved methodological choices before changing
> the analysis. Preserve original records and reviewer decisions, keep proposed AI
> extractions separate, and attach source locations to every extracted value.

## What can be reused

Folder structure, forms, identifier rules, AI logging, checks, and manuscript
organization are reusable. Search strategies, eligibility, extraction variables,
outcome/timepoint selection, bias tools, and statistical models belong to the new review.

## Try the isolated demo

After R setup, run `python3 scripts/run_demo.py`. This creates a copy under
`work/demo-project`, fills it with explicitly artificial records, and runs the
included model. It never edits the actual review tables. Results are labeled demo.
