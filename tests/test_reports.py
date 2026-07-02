import json
from datetime import UTC, datetime
from pathlib import Path

from blue_linter.findings import DocumentLocation, Finding
from blue_linter.reports import ReportRunMetadata, generate_report_artifacts
from blue_linter.rules import RuleSet, StyleRule


def rule_set() -> RuleSet:
    return RuleSet(
        id="blue-linter-style-rules",
        version="2026.06",
        rules=[
            StyleRule(
                id="STYLE-PERCENT-SPACING",
                version="1.0.0",
                name="Percentage spacing",
                category="number-format",
                severity="medium",
                enabled=True,
                type="regex_replace",
                auto_fix=True,
                pattern=r"\b(\d+)\s+%",
                replacement=r"\1%",
            ),
            StyleRule(
                id="STYLE-ACRONYM-FIRST-USE",
                version="1.0.0",
                name="Acronym first use",
                category="terminology",
                severity="high",
                enabled=True,
                type="acronym_first_use",
                auto_fix=False,
            ),
        ],
    )


def finding(
    finding_id: str,
    *,
    rule_id: str = "STYLE-PERCENT-SPACING",
    rule_version: str = "1.0.0",
    rule_name: str = "Percentage spacing",
    severity: str = "medium",
    paragraph_index: int = 0,
    original_text: str = "Revenue increased by 25 %",
    suggested_correction: str | None = "Revenue increased by 25%",
    applied_to_candidate: bool = False,
    review_status: str = "pending_review",
) -> Finding:
    return Finding(
        finding_id=finding_id,
        rule_id=rule_id,
        rule_version=rule_version,
        rule_name=rule_name,
        severity=severity,
        location=DocumentLocation(
            block_id=f"p-{paragraph_index:05d}",
            paragraph_index=paragraph_index,
            style_name="Normal",
            section_title=None,
        ),
        original_text=original_text,
        suggested_correction=suggested_correction,
        applied_to_candidate=applied_to_candidate,
        review_status=review_status,
    )


def metadata(tmp_path: Path) -> ReportRunMetadata:
    return ReportRunMetadata(
        source_document_path=tmp_path / "original.docx",
        candidate_document_path=tmp_path / "candidate.docx",
        generated_at_utc=datetime(2026, 6, 27, 12, 30, tzinfo=UTC),
        tool_version="0.1.0",
    )


def test_report_generation_writes_expected_artifacts(tmp_path: Path) -> None:
    result = generate_report_artifacts(
        tmp_path,
        analysis_findings=[finding("F-000001")],
        validation_findings=[],
        rule_set=rule_set(),
        run_metadata=metadata(tmp_path),
    )

    assert result.analysis_html_path == tmp_path / "style-analysis-report.html"
    assert result.analysis_json_path == tmp_path / "style-analysis-report.json"
    assert result.validation_html_path == tmp_path / "validation-report.html"
    assert result.audit_json_path == tmp_path / "audit.json"
    assert result.analysis_html_path.exists()
    assert result.analysis_json_path.exists()
    assert result.validation_html_path.exists()
    assert result.audit_json_path.exists()


def test_analysis_json_contains_all_findings_with_enriched_categories(tmp_path: Path) -> None:
    generate_report_artifacts(
        tmp_path,
        analysis_findings=[
            finding("F-000001", applied_to_candidate=True, review_status="auto_applied"),
            finding(
                "F-000002",
                rule_id="STYLE-ACRONYM-FIRST-USE",
                rule_name="Acronym first use",
                severity="high",
                paragraph_index=3,
                original_text="The API remains undocumented.",
                suggested_correction=None,
                review_status="manual_review_required",
            ),
        ],
        validation_findings=[],
        rule_set=rule_set(),
        run_metadata=metadata(tmp_path),
    )

    payload = json.loads((tmp_path / "style-analysis-report.json").read_text(encoding="utf-8"))

    assert payload["summary"]["total_findings"] == 2
    assert payload["summary"]["counts_by_category"] == {
        "number-format": 1,
        "terminology": 1,
    }
    assert {record["finding_id"] for record in payload["findings"]} == {
        "F-000001",
        "F-000002",
    }
    assert {record["category"] for record in payload["findings"]} == {
        "number-format",
        "terminology",
    }
    assert payload["findings"][0]["severity"] == "high"


def test_html_report_has_summary_and_finding_details_without_javascript(tmp_path: Path) -> None:
    generate_report_artifacts(
        tmp_path,
        analysis_findings=[
            finding("F-000001", applied_to_candidate=True, review_status="auto_applied")
        ],
        validation_findings=[],
        rule_set=rule_set(),
        run_metadata=metadata(tmp_path),
    )

    html = (tmp_path / "style-analysis-report.html").read_text(encoding="utf-8")

    assert "<script" not in html.lower()
    assert "Style Analysis Report" in html
    assert "Total findings" in html
    assert "number-format" in html
    assert "STYLE-PERCENT-SPACING" in html
    assert "Revenue increased by 25 %" in html
    assert "Candidate documents are review artifacts for human approval." in html
    assert "Applied" in html
    assert "Not applied" not in html
    assert "auto_applied" in html


def test_validation_html_handles_zero_findings(tmp_path: Path) -> None:
    generate_report_artifacts(
        tmp_path,
        analysis_findings=[finding("F-000001")],
        validation_findings=[],
        rule_set=rule_set(),
        run_metadata=metadata(tmp_path),
    )

    html = (tmp_path / "validation-report.html").read_text(encoding="utf-8")

    assert "Validation Report" in html
    assert "Total findings" in html
    assert "No findings were reported." in html


def test_audit_json_records_metadata_counts_and_generated_files(tmp_path: Path) -> None:
    generate_report_artifacts(
        tmp_path,
        analysis_findings=[
            finding("F-000001", applied_to_candidate=True, review_status="auto_applied")
        ],
        validation_findings=[],
        rule_set=rule_set(),
        run_metadata=metadata(tmp_path),
    )

    payload = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))

    assert payload["run_metadata"]["tool_version"] == "0.1.0"
    assert payload["rule_set"] == {
        "id": "blue-linter-style-rules",
        "version": "2026.06",
    }
    assert payload["counts"]["analysis"]["counts_by_applied_status"] == {"applied": 1}
    assert payload["counts"]["validation"]["total_findings"] == 0
    assert payload["generated_files"]["style_analysis_html"].endswith(
        "style-analysis-report.html"
    )
    assert payload["generated_files"]["audit_json"].endswith("audit.json")


def test_missing_rule_metadata_uses_unknown_category(tmp_path: Path) -> None:
    generate_report_artifacts(
        tmp_path,
        analysis_findings=[
            finding(
                "F-000001",
                rule_id="STYLE-STALE-RULE",
                rule_name="Stale rule",
                severity="low",
            )
        ],
        validation_findings=[],
        rule_set=rule_set(),
        run_metadata=metadata(tmp_path),
    )

    payload = json.loads((tmp_path / "style-analysis-report.json").read_text(encoding="utf-8"))

    assert payload["findings"][0]["category"] == "unknown"
    assert payload["summary"]["counts_by_category"] == {"unknown": 1}
