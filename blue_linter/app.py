"""Application boundary for the Blue Linter review workflow."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from blue_linter import __version__
from blue_linter.candidate import generate_candidate_document
from blue_linter.engine import RuleEngine
from blue_linter.package import package_review_artifacts
from blue_linter.parser import parse_docx
from blue_linter.reports import ReportRunMetadata, generate_report_artifacts
from blue_linter.rules import load_rule_set
from blue_linter.validation import validate_candidate_document

RULE_PACK_PATH = Path(__file__).parents[1] / "rules" / "active-style-rules.yaml"


class ReviewWorkflowError(ValueError):
    """Raised when the review workflow cannot complete."""


@dataclass(frozen=True)
class ReviewResult:
    """Result returned by the completed review workflow."""

    input_path: Path
    output_path: Path
    status: Literal["completed"]
    finding_count: int
    applied_fix_count: int
    skipped_fix_count: int
    validation_remaining_count: int
    packaged_paths: list[str]


def run_review(input_path: Path, output_path: Path) -> ReviewResult:
    """Run the local review pipeline and write the final ZIP package."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ReviewWorkflowError(f"Output preparation failed: {exc}") from exc

    try:
        with tempfile.TemporaryDirectory(
            prefix="blue-linter-review-",
            dir=output_path.parent,
        ) as staging_root_name:
            staging_root = Path(staging_root_name)
            candidate_path = staging_root / "document-style-corrected-candidate.docx"
            reports_dir = staging_root / "reports"

            rule_set = _run_stage("Rule loading", lambda: load_rule_set(RULE_PACK_PATH))
            active_rules = rule_set.active_rules
            parsed_document = _run_stage("Parsing", lambda: parse_docx(input_path))
            findings = _run_stage(
                "Rule execution",
                lambda: RuleEngine().run(parsed_document, active_rules),
            )
            candidate_result = _run_stage(
                "Candidate generation",
                lambda: generate_candidate_document(
                    input_path=input_path,
                    output_path=candidate_path,
                    parsed_document=parsed_document,
                    active_rules=active_rules,
                    findings=findings,
                ),
            )
            validation_result = _run_stage(
                "Validation",
                lambda: validate_candidate_document(
                    candidate_result.candidate_path,
                    active_rules,
                ),
            )
            report_result = _run_stage(
                "Reporting",
                lambda: generate_report_artifacts(
                    reports_dir,
                    analysis_findings=candidate_result.findings,
                    validation_findings=validation_result.findings,
                    rule_set=rule_set,
                    run_metadata=ReportRunMetadata(
                        source_document_path=input_path,
                        candidate_document_path=candidate_result.candidate_path,
                        generated_at_utc=datetime.now(UTC),
                        tool_version=__version__,
                    ),
                ),
            )
            package_result = _run_stage(
                "Packaging",
                lambda: package_review_artifacts(
                    output_path,
                    original_document_path=input_path,
                    candidate_document_path=candidate_result.candidate_path,
                    rule_pack_path=RULE_PACK_PATH,
                    report_result=report_result,
                ),
            )
    except Exception as exc:
        if isinstance(exc, ReviewWorkflowError):
            raise
        raise ReviewWorkflowError(f"Unable to complete review workflow: {exc}") from exc

    return ReviewResult(
        input_path=input_path,
        output_path=package_result.package_path,
        status="completed",
        finding_count=len(findings),
        applied_fix_count=candidate_result.applied_count,
        skipped_fix_count=candidate_result.skipped_count,
        validation_remaining_count=validation_result.remaining_count,
        packaged_paths=package_result.included_paths,
    )


def _run_stage[T](stage_name: str, operation: Callable[[], T]) -> T:
    try:
        return operation()
    except ReviewWorkflowError:
        raise
    except Exception as exc:
        raise ReviewWorkflowError(f"{stage_name} failed: {exc}") from exc

