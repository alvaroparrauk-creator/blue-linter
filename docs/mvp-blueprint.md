# Blue Linter MVP Blueprint

## Objective

Blue Linter is a local-first Word document style compliance tool. The MVP analyses uploaded `.docx` files against a built-in, version-controlled corporate style rule set and produces a traceable review package for human approval.

The candidate corrected document is never treated as final. It is an automatically prepared review artifact that must remain traceable to the source document, the active rule set, and each individual finding.

## MVP Principles

- Deterministic checks before broad coverage.
- Version-controlled rules inside the application repository.
- Every finding must be traceable to a stable rule ID, rule version, document location, original text or structure, and suggested correction.
- Safe automatic fixes may be applied to a candidate document; uncertain fixes remain review-only.
- Human-readable and machine-readable reports must contain the same finding data.
- The validation pass must re-check the candidate document and report remaining findings.

## In Scope

- Accept one Word `.docx` document as input.
- Parse paragraphs, headings, bullet/list-like paragraphs, styles, and document order.
- Load the active rule pack from repository-owned configuration.
- Run deterministic style rules over the parsed document.
- Generate normalized findings.
- Apply safe fixes to a candidate `.docx`.
- Generate HTML and JSON analysis reports.
- Run validation against the candidate document.
- Package all outputs into a single ZIP file.

## Out Of Scope For MVP

- Runtime rule uploads by users.
- AI-based rewriting or subjective style scoring.
- Multi-user backend service.
- Web-based interactive review.
- Multi-format input beyond `.docx`.
- External rules repository.
- Full Word change tracking.

## Target Architecture

```text
DOCX input
  -> document parser
  -> rule engine
  -> findings model
  -> candidate document generator
  -> validation pass
  -> report generator
  -> ZIP package generator
```

## Suggested Components

### Document Parser

Responsible for reading `.docx` files and producing a structured document model.

Minimum captured fields:

- document ID or source file name
- paragraph index
- paragraph text
- Word style name
- inferred block type, such as paragraph, heading, bullet, list item, or unknown
- section context where available

### Rule Pack

Rules live in `rules/active-style-rules.yaml`.

Each rule should include:

- stable ID
- version
- name
- category
- severity
- enabled flag
- detection type or logic reference
- auto-fix safety flag
- suggested fix behavior where applicable

Initial rule examples:

- percentage spacing: `25 %` -> `25%`
- repeated whitespace
- preferred bullet punctuation
- acronym first-use detection
- heading capitalisation checks

### Rule Engine

Responsible for applying enabled rules to the parsed document model and producing findings. The rule engine should not directly mutate the source document.

### Findings Model

Each finding must include:

- finding ID
- rule ID
- rule version
- rule name
- severity
- document location
- original text or structure
- suggested correction
- whether the change was applied to the candidate document
- review status

Suggested review statuses:

- `pending_review`
- `auto_applied`
- `manual_review_required`
- `accepted`
- `rejected`

### Candidate Document Generator

Creates `document-style-corrected-candidate.docx` from the original document and applies only safe deterministic fixes.

### Report Generator

Produces:

- `style-analysis-report.html`
- `style-analysis-report.json`
- `validation-report.html`

The HTML report should be easy for a human reviewer to scan by severity, category, rule, and document location.

### Package Generator

Creates the final package:

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

## Recommended Technical Stack

- Python 3.12
- `python-docx` for `.docx` parsing and candidate generation
- `PyYAML` for rule configuration
- `pydantic` for validating rules, findings, and audit structures
- `typer` for the local CLI
- `jinja2` for HTML reports
- `pytest` for unit and end-to-end tests
- `ruff` for formatting and linting

## MVP CLI Shape

```powershell
blue-linter review .\input.docx --output .\style-review-package.zip
```

The CLI should return a non-zero exit code only for processing failures. Style findings are expected product output, not command failures.

## Validation Strategy

Minimum tests:

- Rule engine unit tests for each initial rule.
- Rule pack schema validation test.
- Finding model serialization test.
- End-to-end test that creates a sample `.docx`, runs the pipeline, and asserts the ZIP contents, reports, audit file, candidate document, and validation output exist.

## Future Direction

The MVP should remain local-first, but the architecture should not prevent a future backend. The parser, rule engine, report generation, and package generation should be usable from a CLI now and from an API later.

Future extensions:

- backend service that many frontend types can call
- web-based interactive review interface
- support for additional document formats
- rules maintained in a separate version-controlled repository
- richer review workflows and approval states
