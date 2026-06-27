from pathlib import Path

import pytest

from blue_linter.rules import RulePackLoadError, RuleSet, load_active_rules, load_rule_set


def write_rule_pack(tmp_path: Path, content: str) -> Path:
    rule_path = tmp_path / "rules.yaml"
    rule_path.write_text(content, encoding="utf-8")
    return rule_path


def test_load_rule_set_from_repository_rule_pack() -> None:
    rule_set = load_rule_set(Path("rules/active-style-rules.yaml"))

    assert isinstance(rule_set, RuleSet)
    assert rule_set.id == "corporate-style"
    assert rule_set.version == "0.1.0"
    assert {rule.id for rule in rule_set.rules} >= {
        "STYLE-PERCENT-SPACING",
        "STYLE-REPEATED-WHITESPACE",
        "STYLE-BULLET-PUNCTUATION",
        "STYLE-ACRONYM-FIRST-USE",
        "STYLE-HEADING-CAPITALISATION",
    }


def test_load_active_rules_excludes_disabled_rules() -> None:
    active_rules = load_active_rules(Path("rules/active-style-rules.yaml"))

    assert "STYLE-DISABLED-EXAMPLE" not in {rule.id for rule in active_rules}
    assert all(rule.enabled for rule in active_rules)


def test_invalid_severity_fails_validation(tmp_path: Path) -> None:
    rule_path = write_rule_pack(
        tmp_path,
        """
id: corporate-style
version: 0.1.0
rules:
  - id: STYLE-BAD-SEVERITY
    version: 1.0.0
    name: Bad severity
    category: example
    severity: urgent
    enabled: true
    type: regex_flag
    auto_fix: false
""",
    )

    with pytest.raises(RulePackLoadError, match="Invalid rule pack"):
        load_rule_set(rule_path)


def test_invalid_rule_type_fails_validation(tmp_path: Path) -> None:
    rule_path = write_rule_pack(
        tmp_path,
        """
id: corporate-style
version: 0.1.0
rules:
  - id: STYLE-BAD-TYPE
    version: 1.0.0
    name: Bad type
    category: example
    severity: low
    enabled: true
    type: unknown_rule_type
    auto_fix: false
""",
    )

    with pytest.raises(RulePackLoadError, match="Invalid rule pack"):
        load_rule_set(rule_path)


def test_missing_required_field_fails_validation(tmp_path: Path) -> None:
    rule_path = write_rule_pack(
        tmp_path,
        """
id: corporate-style
version: 0.1.0
rules:
  - id: STYLE-MISSING-NAME
    version: 1.0.0
    category: example
    severity: low
    enabled: true
    type: regex_flag
    auto_fix: false
""",
    )

    with pytest.raises(RulePackLoadError, match="Invalid rule pack"):
        load_rule_set(rule_path)


def test_empty_rule_pack_fails_validation(tmp_path: Path) -> None:
    rule_path = write_rule_pack(tmp_path, "")

    with pytest.raises(RulePackLoadError, match="is empty"):
        load_rule_set(rule_path)

