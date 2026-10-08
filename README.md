# Systematic review and meta-analysis project template

A reusable GitHub + Codex project for planning a review, preserving reviewer decisions,
verifying extracted data, and rebuilding analyses and manuscript results.

**Start with [START_HERE.md](START_HERE.md).** Every real-review data file starts with
headers only. The analysis is disabled until a researcher configures and approves it.
Artificial data are used only by tests and the isolated demo.
See [TEMPLATE_CHECKS.md](TEMPLATE_CHECKS.md) for the scaffold's checks and remaining limitations.

## What is included

- Protocol and analysis-plan outlines, an amendment log, and a new-review checklist.
- Search history, original-export storage, record deduplication, and report-to-study links.
- Separate individual and resolved screening, extraction, and risk-of-bias forms.
- An AI-use log format and stage-specific prompt starters.
- Validation of identifiers, source references, decisions, approvals, and effect inputs.
- A working **independent pairwise inverse-variance** module using R/metafor.
- An R package lockfile, GitHub checks, and an editable Quarto manuscript outline.

## Folder guide

| Folder | Purpose |
|---|---|
| `protocol/` | Review methods, synthesis plan, and dated amendments |
| `search/` | Search strategies, original exports, records, and deduplication |
| `screening/` | Individual reviewer decisions and resolved decisions |
| `studies/` | Underlying studies and their associated reports |
| `extraction/` | Individual extractions, codebook, and verified values |
| `risk-of-bias/` | Individual and resolved domain-level judgments |
| `certainty/` | Outcome-level certainty assessments |
| `ai/` | Prompts and logs of AI inputs, outputs, and human checking |
| `analysis/` | Synthesis definitions, approved effect inputs, and R code |
| `reporting/` | Verified PRISMA counts and reporting checklist |
| `manuscript/` | Quarto manuscript and bibliography |
| `outputs/` | Generated results; excluded from Git by default |
| `fulltext/` | Local report files; excluded from Git by default |
| `work/` | Temporary local files and demo outputs |

## Reuse and scope

Make a new repository for each review. Keep the shared identifiers and provenance
rules; adapt eligibility, fields, tools, and models to the review question. This is
an original starter scaffold informed by the documented tools below. It does not
incorporate another repository's code or protocol wording.

The included analysis module assumes one independent effect per underlying study
within each synthesis. Network meta-analysis, diagnostic accuracy, clustered or
dependent effects, individual participant data, and other specialized designs need
their own documented and tested analysis modules. The core review folders remain useful.
Effect-size calculation from raw extracted statistics is intentionally specified
in each project's analysis plan; there is no automatic universal conversion.

## Reproduction

Requirements: Python 3.9 or later and R. The supplied lockfile records R 4.4.3;
use that version to match the tested environment. Quarto is optional for manuscript rendering.

From the repository root:

```sh
python3 scripts/validate_project.py
python3 -m unittest discover -s tests -v
Rscript analysis/setup.R
Rscript analysis/tests/test_pipeline.R
Rscript analysis/run.R
```

Setup restores the recorded R environment and requires internet access the first time.
The unconfigured template passes structural validation but cannot run a real analysis.
Use `python3 scripts/validate_project.py --analysis-ready` to check configured inputs.
Once analysis is enabled in review.json, the default validator also checks analysis readiness.
Quarto is optional for editing the manuscript and required to render it:

```sh
quarto render
```

The starter manuscript contains visible placeholders. Rendering it does not establish
that a review or PRISMA checklist is complete.

## Review and publication

Review changes to approved data and analysis plans through pull requests. Commit
permitted data, protocol versions, scripts, and `renv.lock`. Tag the exact version
used for submission. Store a permitted, frozen result bundle with a release or
archival repository. `scripts/archive_run.py` records SHA-256 hashes of input,
code, configuration, and environment files for each successful analysis run.

GitHub checks validate structure and test the analysis on artificial data. They
do not prove source accuracy, reviewer independence, methodological validity,
completeness of searches, or correctness of risk-of-bias and certainty judgments.

## Documentation and foundations

- [GitHub template repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Quarto projects](https://quarto.org/docs/projects/quarto-projects.html)
- [renv environment management](https://rstudio.github.io/renv/articles/renv.html)
- [metafor model documentation](https://wviechtb.github.io/metafor/reference/rma.uni.html)
- [PRISMA 2020](https://www.prisma-statement.org/prisma-2020-checklist)
- [Cochrane study selection](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)
- [Cochrane data collection](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-05)

Apply the conduct and reporting guidance appropriate to your review type. PRISMA
is reporting guidance. A repository scaffold does not replace protocol registration.
