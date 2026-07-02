# Synthetic Local Test Material

This folder contains local test material for exercising the parser, rule engine, candidate document generator, and validation pass alongside the full `blue-linter review` workflow.

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

Validate the generated candidate DOCX:

```powershell
python .\samples\run_synthetic_validation.py .\samples\synthetic-style-review.docx .\samples\synthetic-style-review-candidate.docx
```

Expected validation summary:

```text
Original findings: 9
Applied fixes: 2
Remaining validation findings: 7
```

Open these files in Word to inspect the current end-to-end behavior:

```text
samples\synthetic-style-review.docx
samples\synthetic-style-review-candidate.docx
```

To produce the full review ZIP package from a synthetic document, run:

```powershell
blue-linter review .\samples\synthetic-style-review.docx --output .\samples\style-review-package.zip
```
