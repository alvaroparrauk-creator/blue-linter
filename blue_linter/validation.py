"""Validation pass for generated candidate DOCX files."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from blue_linter.document import ParsedDocument
from blue_linter.engine import RuleEngine
from blue_linter.findings import Finding, ReviewStatus
from blue_linter.parser import parse_docx
from blue_linter.rules import Severity, StyleRule


class ValidationResult(BaseModel):
    """Result returned after checking a candidate document."""

    model_config = ConfigDict(extra="forbid")

    candidate_path: Path
    parsed_document: ParsedDocument
    findings: list[Finding]
    remaining_count: int = Field(ge=0)
    counts_by_severity: dict[Severity, int]
    counts_by_rule_id: dict[str, int]
    counts_by_review_status: dict[ReviewStatus, int]


def validate_candidate_document(
    candidate_path: Path,
    active_rules: Sequence[StyleRule],
) -> ValidationResult:
    """Re-run active rules against a candidate DOCX and report remaining findings."""
    parsed_document = parse_docx(candidate_path)
    findings = RuleEngine().run(parsed_document, active_rules)

    return ValidationResult(
        candidate_path=candidate_path,
        parsed_document=parsed_document,
        findings=findings,
        remaining_count=len(findings),
        counts_by_severity=dict(Counter(finding.severity for finding in findings)),
        counts_by_rule_id=dict(Counter(finding.rule_id for finding in findings)),
        counts_by_review_status=dict(Counter(finding.review_status for finding in findings)),
    )
