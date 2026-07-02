# Blue Linter

Blue Linter is a local-first Word document style compliance tool. The MVP will analyse `.docx` documents against a version-controlled corporate style rule set and produce traceable review outputs for human approval.

The current foundation includes the CLI, repository-owned YAML rule pack, typed rule models, active-rule loading, finding models, internal parsed-document models, a deterministic rule engine, main-body DOCX paragraph parsing, conservative candidate document generation, candidate validation, report/audit artifact generation, ZIP package generation, and end-to-end MVP workflow verification.

## Requirements

- Python 3.12 or later

## Setup

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run

Show the installed CLI version:

```powershell
blue-linter --version
```

Run a local review and write the MVP package:

```powershell
blue-linter review .\sample.docx --output .\style-review-package.zip
```

The review command parses the `.docx`, runs the active rules, creates a candidate document, validates it, generates reports and audit output, and writes the final ZIP package.

## Rule Pack

The active style rules live in:

```text
rules/active-style-rules.yaml
```

Rules are version-controlled with the application and are not uploaded by users at runtime.

## Rule Engine

The rule engine accepts an internal parsed-document model and enabled style rules, then returns normalized findings without mutating document content. It currently supports:

- regex replacement rules
- regex flag-only rules
- heading capitalisation checks
- bullet punctuation consistency checks
- acronym first-use checks

The CLI runs the full local MVP workflow against real `.docx` files and writes the review package.

## DOCX Parser

The parser reads main-body `.docx` paragraphs with `python-docx` and produces the internal parsed-document model consumed by the rule engine. It preserves paragraph order, stable block IDs, Word style names, block types, and simple heading section context.

Current parser limitations:

- only main-body paragraphs are parsed
- tables, headers, footers, comments, footnotes, and text boxes are not parsed
- bullet and list detection uses practical heuristics and may be refined later

The CLI still returns the placeholder review response until those later pipeline milestones are implemented.

## Candidate Documents

The candidate generator copies the original `.docx` and applies only safe deterministic auto-fixes to main-body paragraphs. It currently preserves formatting conservatively by editing single-run paragraphs only; multi-run paragraphs are skipped so inline formatting is not flattened accidentally.

Candidate generation returns a structured result containing the candidate path, copied finding records, applied count, skipped count, and skipped reasons. The original finding objects are not mutated. Applied findings in the returned result are marked with `applied_to_candidate=True` and `review_status="auto_applied"`.

When multiple auto-fix rules affect the same paragraph, fixes are applied in active-rule order so the candidate text is deterministic. Formatting preservation takes priority over applying every possible deterministic fix.

Candidate documents are review artifacts, not final approved documents. The CLI includes them in the generated review package for human approval.

## Candidate Validation

The validation pass re-parses a generated candidate `.docx`, runs the same active rule set against it, and returns remaining findings with summary counts by severity, rule ID, and review status.

Validation does not apply fixes. It reports whether safe auto-fixes disappeared from the candidate and which manual-review findings still remain visible.

## Reports And Audit Output

The report generator writes static review artifacts from existing finding data:

- `style-analysis-report.html`
- `style-analysis-report.json`
- `validation-report.html`
- `audit.json`

HTML reports are readable without JavaScript. JSON output contains enriched finding records with rule categories, summary counts, run metadata, rule set version, and generated file paths.

## ZIP Package Generation

The package generator writes the required review ZIP layout from already-created artifacts:

```text
style-review-package.zip
+-- original/
|   +-- document-original.docx
+-- candidate/
|   +-- document-style-corrected-candidate.docx
+-- reports/
|   +-- style-analysis-report.html
|   +-- style-analysis-report.json
|   +-- validation-report.html
+-- rules/
|   +-- active-style-rules.yaml
+-- audit/
    +-- audit.json
```

Packaging validates that every required artifact exists, is a file, and is non-empty before replacing the output ZIP. It preserves exact file bytes while normalizing artifact names inside the package.

## End-To-End Review Workflow

The CLI workflow produces the MVP package in one command:

```powershell
blue-linter review .\sample.docx --output .\style-review-package.zip
```

Style findings are expected product output and do not make the command fail. Processing failures, such as invalid input documents or unwritable output locations, return a non-zero exit code.

## Known MVP Limitations

- Only `.docx` input is supported.
- Parsing covers main-body paragraphs only; tables, headers, footers, comments, footnotes, and text boxes are not parsed yet.
- Candidate generation skips multi-run paragraphs to avoid flattening inline formatting.
- Reports are static HTML and JSON artifacts, not an interactive review interface.
- Rules are loaded from the repository-owned `rules/active-style-rules.yaml` file and are not uploaded at runtime.

## Local Synthetic Testing

Use the sample runners to inspect individual parser, rule engine, candidate, and validation steps. The full CLI workflow, report generation, and ZIP package generation are covered by automated tests.

Using the current Python environment:

```powershell
python -m pip install -e ".[dev]"
python .\samples\create_synthetic_docx.py
python .\samples\run_synthetic_review.py .\samples\synthetic-style-review.docx
python .\samples\run_synthetic_candidate.py .\samples\synthetic-style-review.docx .\samples\synthetic-style-review-candidate.docx
python .\samples\run_synthetic_validation.py .\samples\synthetic-style-review.docx .\samples\synthetic-style-review-candidate.docx
```

Using a PowerShell virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python .\samples\create_synthetic_docx.py
python .\samples\run_synthetic_review.py .\samples\synthetic-style-review.docx
python .\samples\run_synthetic_candidate.py .\samples\synthetic-style-review.docx .\samples\synthetic-style-review-candidate.docx
python .\samples\run_synthetic_validation.py .\samples\synthetic-style-review.docx .\samples\synthetic-style-review-candidate.docx
```

If PowerShell blocks virtual environment activation, run this in the same terminal session before activating:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Expected summary output:

```text
Document: synthetic-style-review.docx
Parsed blocks: 12
Findings: 9
- STYLE-ACRONYM-FIRST-USE: 2
- STYLE-BULLET-PUNCTUATION: 4
- STYLE-HEADING-CAPITALISATION: 1
- STYLE-PERCENT-SPACING: 1
- STYLE-REPEATED-WHITESPACE: 1
```

Expected candidate generation summary:

```text
Original: samples\synthetic-style-review.docx
Candidate: samples\synthetic-style-review-candidate.docx
Parsed blocks: 12
Findings: 9
Applied fixes: 2
Skipped fixes: 0
```

The candidate file is written to `samples\synthetic-style-review-candidate.docx` for manual inspection.

Expected validation summary:

```text
Original: samples\synthetic-style-review.docx
Candidate: samples\synthetic-style-review-candidate.docx
Original findings: 9
Applied fixes: 2
Remaining validation findings: 7
```

## Candidate And Validation Testing

Candidate generation and validation are currently library-level capabilities. To test them locally, run the automated generated-DOCX coverage:

```powershell
python -m pytest tests\test_candidate.py
python -m pytest tests\test_validation.py
```

If Windows blocks access to the default pytest temp folder, route pytest temp and cache output into the repository's ignored `.tmp` folder:

```powershell
New-Item -ItemType Directory -Path .tmp\pytest-temp -Force | Out-Null
New-Item -ItemType Directory -Path .tmp\pytest-cache -Force | Out-Null
$env:TMP = (Resolve-Path .tmp).Path
$env:TEMP = (Resolve-Path .tmp).Path
python -m pytest tests\test_candidate.py tests\test_validation.py --basetemp .tmp\pytest-temp -o cache_dir=.tmp\pytest-cache
```

To run it with the rest of the suite:

```powershell
python -m pytest
python -m ruff check .
```

With the same temp-folder workaround:

```powershell
$env:TMP = (Resolve-Path .tmp).Path
$env:TEMP = (Resolve-Path .tmp).Path
python -m pytest --basetemp .tmp\pytest-temp -o cache_dir=.tmp\pytest-cache
python -m ruff check .
```

The tests generate temporary `.docx` files, create candidate documents, verify that originals remain unchanged, confirm safe fixes are applied, confirm multi-run paragraphs are skipped to preserve formatting, and confirm validation reports remaining candidate findings without applying more fixes.

## Documentation Workflow

Code changes should include a documentation review before commit. Update the README, roadmap, process docs, or feature docs when behavior, public interfaces, verification steps, project status, or workflow expectations change.

## Verify

```powershell
python -m pytest
python -m ruff check .
```

