from pathlib import Path

import pytest

from blue_linter.document import DocumentBlock, ParsedDocument
from blue_linter.engine import RuleEngine, RuleEngineError
from blue_linter.rules import StyleRule, load_active_rules


def block(
    block_id: str,
    paragraph_index: int,
    text: str,
    *,
    block_type: str = "paragraph",
    style_name: str = "Normal",
) -> DocumentBlock:
    return DocumentBlock(
        block_id=block_id,
        paragraph_index=paragraph_index,
        text=text,
        style_name=style_name,
        block_type=block_type,
    )


def document(*blocks: DocumentBlock) -> ParsedDocument:
    return ParsedDocument(source_name="sample.docx", blocks=list(blocks))


def rule(rule_type: str, **overrides: object) -> StyleRule:
    values = {
        "id": "STYLE-TEST",
        "version": "1.0.0",
        "name": "Test rule",
        "category": "test",
        "severity": "medium",
        "enabled": True,
        "type": rule_type,
        "auto_fix": False,
    }
    values.update(overrides)
    return StyleRule.model_validate(values)


def test_regex_replacement_creates_finding_with_full_corrected_text() -> None:
    parsed_document = document(block("p-00001", 0, "Revenue increased by 25 %  today."))
    style_rule = rule(
        "regex_replace",
        id="STYLE-PERCENT-SPACING",
        name="Percentage spacing",
        auto_fix=True,
        pattern=r"\b(\d+)\s+%",
        replacement=r"\1%",
    )

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert len(findings) == 1
    assert findings[0].finding_id == "F-000001"
    assert findings[0].rule_id == "STYLE-PERCENT-SPACING"
    assert findings[0].suggested_correction == "Revenue increased by 25%  today."
    assert findings[0].review_status == "pending_review"
    assert findings[0].applied_to_candidate is False


def test_regex_flag_creates_manual_review_finding_without_suggestion() -> None:
    parsed_document = document(block("p-00001", 0, "This contains example text."))
    style_rule = rule("regex_flag", pattern=r"\bexample\b")

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert len(findings) == 1
    assert findings[0].suggested_correction is None
    assert findings[0].review_status == "manual_review_required"


def test_disabled_rules_are_absent_when_loading_active_rules() -> None:
    active_rules = load_active_rules(Path("rules/active-style-rules.yaml"))
    parsed_document = document(
        block("p-00001", 0, "This example should not trigger disabled rule.")
    )

    findings = RuleEngine().run(parsed_document, active_rules)

    assert "STYLE-DISABLED-EXAMPLE" not in {finding.rule_id for finding in findings}


def test_one_rule_can_produce_multiple_findings_with_stable_ids() -> None:
    parsed_document = document(
        block("p-00001", 0, "Revenue increased by 25 %."),
        block("p-00002", 1, "Margin improved by 3 %."),
    )
    style_rule = rule(
        "regex_replace",
        pattern=r"\b(\d+)\s+%",
        replacement=r"\1%",
        auto_fix=True,
    )

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert [finding.finding_id for finding in findings] == ["F-000001", "F-000002"]
    assert [finding.location.block_id for finding in findings] == ["p-00001", "p-00002"]


def test_engine_does_not_mutate_parsed_document() -> None:
    parsed_document = document(block("p-00001", 0, "Revenue increased by 25 %."))
    original_dump = parsed_document.model_dump()
    style_rule = rule(
        "regex_replace",
        pattern=r"\b(\d+)\s+%",
        replacement=r"\1%",
        auto_fix=True,
    )

    RuleEngine().run(parsed_document, [style_rule])

    assert parsed_document.model_dump() == original_dump
    assert parsed_document.blocks[0].text == "Revenue increased by 25 %."


def test_heading_check_flags_inconsistent_capitalisation() -> None:
    parsed_document = document(
        block(
            "p-00001",
            0,
            "Quarterly business REVIEW",
            block_type="heading",
            style_name="Heading 1",
        ),
        block(
            "p-00002",
            1,
            "Quarterly Business Review",
            block_type="heading",
            style_name="Heading 1",
        ),
    )
    style_rule = rule("heading_check")

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert [finding.location.block_id for finding in findings] == ["p-00001"]
    assert findings[0].suggested_correction is None
    assert findings[0].review_status == "manual_review_required"


def test_bullet_check_flags_inconsistent_terminal_punctuation_in_run() -> None:
    parsed_document = document(
        block("p-00001", 0, "Reduce operating costs", block_type="bullet"),
        block("p-00002", 1, "Improve customer retention.", block_type="bullet"),
        block("p-00003", 2, "Next section", block_type="paragraph"),
        block("p-00004", 3, "Single bullet.", block_type="bullet"),
    )
    style_rule = rule("bullet_check")

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert [finding.location.block_id for finding in findings] == ["p-00001", "p-00002"]
    assert all(finding.review_status == "manual_review_required" for finding in findings)


def test_acronym_first_use_flags_undefined_acronym_once() -> None:
    parsed_document = document(
        block("p-00001", 0, "The API should remain stable."),
        block("p-00002", 1, "The API response is documented."),
    )
    style_rule = rule("acronym_first_use")

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert [finding.location.block_id for finding in findings] == ["p-00001"]
    assert findings[0].original_text == "The API should remain stable."


def test_acronym_first_use_ignores_prior_local_definition() -> None:
    parsed_document = document(
        block("p-00001", 0, "Application Programming Interface (API) guidance."),
        block("p-00002", 1, "The API response is documented."),
    )
    style_rule = rule("acronym_first_use")

    findings = RuleEngine().run(parsed_document, [style_rule])

    assert findings == []


def test_malformed_regex_rule_raises_engine_error() -> None:
    parsed_document = document(block("p-00001", 0, "Any text."))
    style_rule = rule("regex_replace", pattern="[", replacement="")

    with pytest.raises(RuleEngineError, match="invalid regex pattern"):
        RuleEngine().run(parsed_document, [style_rule])


def test_regex_replace_requires_replacement() -> None:
    parsed_document = document(block("p-00001", 0, "Any text."))
    style_rule = rule("regex_replace", pattern=r"text")

    with pytest.raises(RuleEngineError, match="requires replacement"):
        RuleEngine().run(parsed_document, [style_rule])
