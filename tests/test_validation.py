from pathlib import Path

from docx import Document

from blue_linter.candidate import generate_candidate_document
from blue_linter.engine import RuleEngine
from blue_linter.parser import parse_docx
from blue_linter.rules import StyleRule
from blue_linter.validation import validate_candidate_document


def save_document(path: Path, paragraphs: list[str]) -> Path:
    document = Document()
    for text in paragraphs:
        document.add_paragraph(text)
    document.save(path)
    return path


def percent_rule() -> StyleRule:
    return StyleRule(
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
    )


def whitespace_rule() -> StyleRule:
    return StyleRule(
        id="STYLE-REPEATED-WHITESPACE",
        version="1.0.0",
        name="Repeated whitespace",
        category="spacing",
        severity="low",
        enabled=True,
        type="regex_replace",
        auto_fix=True,
        pattern=r" {2,}",
        replacement=" ",
    )


def manual_rule() -> StyleRule:
    return StyleRule(
        id="STYLE-ACRONYM-FIRST-USE",
        version="1.0.0",
        name="Acronym first use",
        category="terminology",
        severity="high",
        enabled=True,
        type="acronym_first_use",
        auto_fix=False,
    )


def validate_generated_candidate(
    input_path: Path,
    output_path: Path,
    rules: list[StyleRule],
):
    parsed_document = parse_docx(input_path)
    findings = RuleEngine().run(parsed_document, rules)
    candidate_result = generate_candidate_document(
        input_path=input_path,
        output_path=output_path,
        parsed_document=parsed_document,
        active_rules=rules,
        findings=findings,
    )
    validation_result = validate_candidate_document(candidate_result.candidate_path, rules)
    return candidate_result, validation_result


def test_auto_fixed_issues_disappear_from_validation(tmp_path: Path) -> None:
    input_path = save_document(tmp_path / "original.docx", ["Revenue increased by 25 %."])
    output_path = tmp_path / "candidate.docx"

    candidate_result, validation_result = validate_generated_candidate(
        input_path,
        output_path,
        [percent_rule()],
    )

    assert candidate_result.applied_count == 1
    assert validation_result.candidate_path == output_path
    assert validation_result.remaining_count == 0
    assert validation_result.findings == []
    assert validation_result.counts_by_severity == {}
    assert validation_result.counts_by_rule_id == {}
    assert validation_result.counts_by_review_status == {}


def test_manual_review_findings_remain_visible_in_validation(tmp_path: Path) -> None:
    input_path = save_document(tmp_path / "original.docx", ["The API remains undocumented."])
    output_path = tmp_path / "candidate.docx"

    candidate_result, validation_result = validate_generated_candidate(
        input_path,
        output_path,
        [manual_rule()],
    )

    assert candidate_result.applied_count == 0
    assert validation_result.remaining_count == 1
    assert validation_result.findings[0].rule_id == "STYLE-ACRONYM-FIRST-USE"
    assert validation_result.findings[0].review_status == "manual_review_required"


def test_validation_summary_counts_remaining_findings(tmp_path: Path) -> None:
    input_path = save_document(
        tmp_path / "original.docx",
        [
            "The API remains undocumented.",
            "The SDK  has extra spacing.",
        ],
    )
    output_path = tmp_path / "candidate.docx"

    _, validation_result = validate_generated_candidate(
        input_path,
        output_path,
        [manual_rule(), whitespace_rule()],
    )

    assert validation_result.remaining_count == 2
    assert validation_result.counts_by_severity == {"high": 2}
    assert validation_result.counts_by_rule_id == {"STYLE-ACRONYM-FIRST-USE": 2}
    assert validation_result.counts_by_review_status == {"manual_review_required": 2}


def test_validation_uses_fresh_findings_without_mutating_candidate_result(
    tmp_path: Path,
) -> None:
    input_path = save_document(
        tmp_path / "original.docx",
        ["Revenue increased by 25 %. The API remains undocumented."],
    )
    output_path = tmp_path / "candidate.docx"
    rules = [percent_rule(), manual_rule()]

    candidate_result, validation_result = validate_generated_candidate(
        input_path,
        output_path,
        rules,
    )

    assert [finding.review_status for finding in candidate_result.findings] == [
        "auto_applied",
        "manual_review_required",
    ]
    assert validation_result.remaining_count == 1
    assert validation_result.findings[0].finding_id == "F-000001"
    assert validation_result.findings[0].rule_id == "STYLE-ACRONYM-FIRST-USE"
    assert [finding.review_status for finding in candidate_result.findings] == [
        "auto_applied",
        "manual_review_required",
    ]
