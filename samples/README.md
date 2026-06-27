# Synthetic Local Test Material

This folder contains local test material for exercising the current parser and rule engine before the full `blue-linter review` pipeline is wired together.

Generate the synthetic DOCX:

```powershell
python .\samples\create_synthetic_docx.py
```

Run the parser and active rules against it:

```powershell
python .\samples\run_synthetic_review.py .\samples\synthetic-style-review.docx
```

The CLI command still returns a placeholder response until later milestones connect parsing, rule execution, reporting, and packaging.
