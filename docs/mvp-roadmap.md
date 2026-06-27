# Blue Linter MVP Roadmap

## Summary

Blue Linter should be implemented as a small, local-first, deterministic document review pipeline. The MVP starts with `.docx` input only, repository-owned style rules, traceable findings, candidate document generation, validation, human-readable reports, machine-readable audit output, and ZIP packaging.

The implementation should prioritize clear contracts between components:

```text
DOCX input
  -> document parser
  -> rule loader / rule registry
  -> rule engine
  -> findings model
  -> candidate document generator
  -> validation pass
  -> report generator
  -> ZIP package generator
  -> CLI
```

The corrected document is always a candidate pending human review.

## Milestone 1: Project Foundation

Status: completed

Goal: establish the Python project structure, development workflow, and CLI entry point.

Components:

- CLI / application entry point
- package structure
- test structure
- project configuration
- basic documentation

Implementation tasks:

- Add `pyproject.toml`.
- Create the `blue_linter/` package.
- Add a `blue-linter review` CLI command.
- Add `tests/` with a smoke test.
- Add README setup, run, and test commands.
- Decide initial app versioning convention.

Recommended dependencies:

- `typer`
- `pytest`
- `ruff`

Acceptance criteria:

- The CLI can be invoked locally.
- A placeholder review command returns a clear message.
- Tests can be run with one command.
- Project commands are documented.

## Milestone 2: Rule Pack And Findings Core

Status: completed

Goal: define the version-controlled rule format and the central findings contract before touching `.docx` mutation.

Components:

- rule pack
- rule loader / registry
- findings model
- schema validation

Implementation tasks:

- Add `rules/active-style-rules.yaml`.
- Define rule fields:
  - stable ID
  - version
  - name
  - category
  - severity
  - enabled flag
  - detection type
  - auto-fix safety flag
  - suggested fix behavior
- Implement rule loading and validation.
- Implement the finding model.
- Implement stable finding ID generation for a single run.
- Add JSON serialization for findings.

Initial rule types:

- `regex_replace`
- `regex_flag`
- `heading_check`
- `bullet_check`
- `acronym_first_use`

Recommended dependencies:

- `PyYAML`
- `pydantic`

Acceptance criteria:

- Valid rule packs load successfully.
- Invalid rule packs fail with useful errors.
- Disabled rules are ignored.
- Findings serialize to stable JSON.

## Milestone 3: Rule Engine

Status: completed

Goal: apply enabled deterministic rules to a parsed document model and produce normalized findings.

Components:

- rule engine
- rule executors
- finding generation

Implementation tasks:

- Define the internal parsed document/block model.
- Implement a rule engine entry point:

```python
RuleEngine.run(parsed_document, active_rules) -> list[Finding]
```

- Implement regex replacement rules.
- Implement regex flag-only rules.
- Implement heading capitalisation checks.
- Implement bullet punctuation checks.
- Implement acronym first-use checks.
- Ensure the engine does not mutate documents directly.

Initial MVP rules:

- percentage spacing, for example `25 %` -> `25%`
- repeated whitespace
- preferred bullet point punctuation
- acronym first-use detection
- heading capitalisation checks

Acceptance criteria:

- One rule can produce multiple findings.
- Each finding includes rule ID and rule version.
- Auto-fixable findings are clearly marked.
- Manual-review findings remain non-mutating.
- Unit tests cover each initial rule.

## Milestone 4: DOCX Parser

Status: implemented, pending merge

Goal: read `.docx` files and produce a structured, traceable document model.

Components:

- document parser
- parsed document model
- block classification

Implementation tasks:

- Use `python-docx` to read `.docx` files.
- Extract paragraphs in document order.
- Capture paragraph index, text, and Word style name.
- Infer block type:
  - paragraph
  - heading
  - bullet
  - list item
  - unknown
- Capture simple heading/section context where practical.

Recommended dependency:

- `python-docx`

Acceptance criteria:

- Parser preserves paragraph order.
- Headings are identified from Word styles.
- Basic bullet/list-like paragraphs are identified.
- Parsed blocks include stable IDs and locations.

Milestone limitations:

- Parses main-body paragraphs only.
- Does not parse tables, headers, footers, comments, footnotes, or text boxes.
- Uses practical heuristics for bullet/list classification.

## Milestone 5: Candidate Document Generator

Status: next

Goal: create a corrected candidate `.docx` by applying only safe deterministic fixes.

Components:

- candidate generator
- fix application logic
- applied finding updates

Implementation tasks:

- Copy the original `.docx`.
- Apply only findings where:
  - the rule allows auto-fix
  - the suggested correction is deterministic
  - the document location is still valid
- Update findings with `applied_to_candidate`.
- Preserve basic document formatting where possible.
- Avoid applying ambiguous changes.

Acceptance criteria:

- Safe paragraph-level replacements are applied.
- Review-only findings do not modify the candidate document.
- Candidate document can be opened as a valid `.docx`.
- Candidate document is clearly labelled as pending human review in reports.

## Milestone 6: Validation Pass

Goal: re-run the rule engine against the candidate document and report remaining findings.

Components:

- validation runner
- candidate re-parser
- validation findings

Implementation tasks:

- Parse the candidate `.docx`.
- Run the same active rule set against it.
- Do not apply fixes during validation.
- Produce remaining findings and summary counts.

Acceptance criteria:

- Auto-fixed issues disappear when the fix succeeded.
- Manual-review findings remain visible.
- Validation succeeds even when no findings remain.

## Milestone 7: Reports And Audit Output

Goal: generate human-readable and machine-readable reports from the same finding data.

Components:

- HTML report generator
- JSON report generator
- audit generator

Implementation tasks:

- Generate `style-analysis-report.html`.
- Generate `style-analysis-report.json`.
- Generate `validation-report.html`.
- Generate `audit.json`.
- Include rule IDs, rule versions, severities, locations, original text, suggested correction, applied status, and review status.
- Add summary counts by severity, category, rule, and applied status.

Recommended dependency:

- `jinja2`

Acceptance criteria:

- HTML report is readable without JavaScript.
- JSON report contains all findings.
- Audit output records run metadata, ruleset version, counts, and generated files.
- Human and JSON reports are based on the same finding records.

## Milestone 8: ZIP Package Generator

Goal: package all review artifacts into the required output structure.

Components:

- package generator
- output staging
- ZIP writer

Implementation tasks:

- Stage output files in the expected folder structure.
- Copy the original document.
- Copy the candidate document.
- Copy `rules/active-style-rules.yaml`.
- Include reports and audit JSON.
- Produce `style-review-package.zip`.

Required ZIP structure:

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

Acceptance criteria:

- ZIP contains every required path.
- Included files are not empty.
- Rules file in the ZIP matches the active rule pack used for the run.

## Milestone 9: End-To-End MVP Verification

Goal: prove the complete local pipeline works with a generated sample `.docx`.

Components:

- end-to-end test
- generated sample document
- ZIP assertions

Implementation tasks:

- Generate a sample `.docx` during the test.
- Include examples that trigger the initial rules.
- Run the full review pipeline.
- Assert ZIP structure and key report contents.
- Assert validation findings reflect candidate changes.

Acceptance criteria:

- End-to-end test passes from a clean checkout.
- The test does not depend on a manually maintained binary fixture.
- The generated candidate document can be parsed again.

## Milestone 10: MVP Hardening

Goal: make the MVP reliable enough for real local trials.

Implementation tasks:

- Improve error messages for invalid input documents.
- Add clear handling for unsupported files.
- Refine list and heading detection.
- Improve report wording.
- Fill remaining `AGENTS.md` command placeholders.
- Document known MVP limitations.

Acceptance criteria:

- Common user mistakes produce useful errors.
- Known limitations are explicit.
- Development, test, and run commands are documented.

## Deferred Roadmap Items

These items should influence architecture, but they are not MVP blockers.

### Backend-Compatible Core

The MVP runs locally, but parser, rule engine, candidate generation, reporting, and packaging should be callable from a future backend service.

### Multiple Input Formats

The MVP only accepts `.docx`. Future work may add other parsers that feed the same internal document model.

### External Rules Repository

The MVP stores rules inside this repository. Future work may move rules to a separate version-controlled repository with pinned versions and audit metadata.

### Interactive Review Interface

The MVP uses static reports. Future work may add a web-based review interface for filtering findings, accepting/rejecting suggestions, and downloading final outputs.

## Recommended Build Order

1. Project foundation.
2. Rule pack and findings core.
3. Rule engine.
4. DOCX parser.
5. Candidate document generator.
6. Validation pass.
7. Reports and audit output.
8. ZIP package generator.
9. End-to-end verification.
10. Hardening.

This order keeps contracts stable before the implementation starts touching Word document mutation, which is the part most likely to become messy if introduced too early.
