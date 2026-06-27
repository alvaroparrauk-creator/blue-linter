# Blue Linter

Blue Linter is a local-first Word document style compliance tool. The MVP will analyse `.docx` documents against a version-controlled corporate style rule set and produce traceable review outputs for human approval.

The current foundation includes the CLI skeleton, repository-owned YAML rule pack, typed rule models, active-rule loading, and finding models. DOCX parsing, rule execution, candidate documents, reports, validation, and ZIP packaging are planned for later milestones.

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

## Verify

```powershell
python -m pytest
python -m ruff check .
```

