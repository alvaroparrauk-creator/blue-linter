import json

import pytest
from pydantic import ValidationError

from blue_linter.findings import DocumentLocation, Finding, FindingIdGenerator


def test_finding_ids_increment_with_stable_format() -> None:
    generator = FindingIdGenerator()

    assert generator.next_id() == "F-000001"
    assert generator.next_id() == "F-000002"


def test_finding_serializes_to_json_compatible_dictionary() -> None:
    location = DocumentLocation(
        block_id="p-00012",
        paragraph_index=12,
        style_name="Normal",
        section_title=None,
    )
    finding = Finding(
        finding_id="F-000001",
        rule_id="STYLE-PERCENT-SPACING",
        rule_version="1.0.0",
        rule_name="Percentage spacing",
        severity="medium",
        location=location,
        original_text="Revenue increased by 25 %",
        suggested_correction="Revenue increased by 25%",
        applied_to_candidate=False,
        review_status="pending_review",
    )

    serialized = finding.to_json_dict()

    assert serialized["finding_id"] == "F-000001"
    assert serialized["location"]["paragraph_index"] == 12
    json.dumps(serialized)


def test_finding_requires_rule_metadata() -> None:
    location = DocumentLocation(block_id="p-00001", paragraph_index=1, style_name="Normal")

    with pytest.raises(ValidationError):
        Finding(
            finding_id="F-000001",
            rule_id="",
            rule_version="1.0.0",
            rule_name="Percentage spacing",
            severity="medium",
            location=location,
            original_text="Revenue increased by 25 %",
        )


def test_invalid_review_status_fails_validation() -> None:
    location = DocumentLocation(block_id="p-00001", paragraph_index=1, style_name="Normal")

    with pytest.raises(ValidationError):
        Finding(
            finding_id="F-000001",
            rule_id="STYLE-PERCENT-SPACING",
            rule_version="1.0.0",
            rule_name="Percentage spacing",
            severity="medium",
            location=location,
            original_text="Revenue increased by 25 %",
            review_status="needs_review",
        )

