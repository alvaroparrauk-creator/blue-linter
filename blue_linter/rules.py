"""Rule pack models and loading helpers."""

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

Severity = Literal["low", "medium", "high", "critical"]
RuleType = Literal[
    "regex_replace",
    "regex_flag",
    "heading_check",
    "bullet_check",
    "acronym_first_use",
]


class RulePackLoadError(ValueError):
    """Raised when a rule pack cannot be loaded or validated."""


class StyleRule(BaseModel):
    """Repository-owned style rule configuration."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    severity: Severity
    enabled: bool = True
    type: RuleType
    auto_fix: bool = False
    pattern: str | None = None
    replacement: str | None = None
    message: str | None = None


class RuleSet(BaseModel):
    """Versioned collection of style rules."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    rules: list[StyleRule]

    @property
    def active_rules(self) -> list[StyleRule]:
        """Return enabled rules only."""
        return [rule for rule in self.rules if rule.enabled]


def load_rule_set(path: Path) -> RuleSet:
    """Load and validate a YAML rule set."""
    try:
        with path.open("r", encoding="utf-8") as rule_file:
            raw_data: Any = yaml.safe_load(rule_file)
    except OSError as exc:
        raise RulePackLoadError(f"Unable to read rule pack at {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise RulePackLoadError(f"Invalid YAML in rule pack at {path}: {exc}") from exc

    if raw_data is None:
        raise RulePackLoadError(f"Rule pack at {path} is empty.")

    try:
        return RuleSet.model_validate(raw_data)
    except ValidationError as exc:
        raise RulePackLoadError(f"Invalid rule pack at {path}: {exc}") from exc


def load_active_rules(path: Path) -> list[StyleRule]:
    """Load enabled style rules from a YAML rule pack."""
    return load_rule_set(path).active_rules

