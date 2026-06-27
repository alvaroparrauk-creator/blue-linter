# Synthetic Local Test Material

This folder contains local test material for exercising the current parser, rule engine, and candidate document generator before the full `blue-linter review` pipeline is wired together.

Generate the synthetic DOCX:

```powershell
python .\samples\create_synthetic_docx.py
```

Run the parser and active rules against it:

```powershell
python .\samples\run_synthetic_review.py .\samples\synthetic-style-review.docx
```

Generate a candidate DOCX from the same synthetic input:

```powershell
python .\samples\run_synthetic_candidate.py .\samples\synthetic-style-review.docx .\samples\synthetic-style-review-candidate.docx
```

Open these files in Word to inspect the current end-to-end behavior:

```text
samples\synthetic-style-review.docx
samples\synthetic-style-review-candidate.docx
```

The CLI command still returns a placeholder response until later milestones connect parsing, rule execution, reporting, and packaging.
