# Blue Linter

Blue Linter is a local-first Word document style compliance tool. The MVP will analyse `.docx` documents against a version-controlled corporate style rule set and produce traceable review outputs for human approval.

The current foundation includes the CLI skeleton, repository-owned YAML rule pack, typed rule models, active-rule loading, finding models, internal parsed-document models, and a deterministic rule engine. DOCX parsing, candidate documents, reports, validation, and ZIP packaging are planned for later milestones.

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

Run the placeholder review command:

```powershell
blue-linter review .\sample.docx --output .\style-review-package.zip
```

The review command currently returns a clear placeholder response. It does not generate a ZIP package until later MVP milestones.

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

The CLI does not yet run the engine against real `.docx` files because DOCX parsing begins in the next milestone.

## Documentation Workflow

Code changes should include a documentation review before commit. Update the README, roadmap, process docs, or feature docs when behavior, public interfaces, verification steps, project status, or workflow expectations change.

## Verify

```powershell
python -m pytest
python -m ruff check .
```

