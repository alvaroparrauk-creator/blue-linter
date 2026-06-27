"""Finding models used by reports, audit output, and candidate generation."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from blue_linter.rules import Severity

ReviewStatus = Literal["pending_review", "auto_applied", "manual_review_required"]


class DocumentLocation(BaseModel):
    """Traceable location for a finding in a parsed document."""

    model_config = ConfigDict(extra="forbid")

    block_id: str = Field(min_length=1)
    paragraph_index: int = Field(ge=0)
    style_name: str = Field(min_length=1)
    section_title: str | None = None


class Finding(BaseModel):
    """Normalized style compliance finding."""

    model_config = ConfigDict(extra="forbid")

    finding_id: str = Field(min_length=1)
    rule_id: str = Field(min_length=1)
    rule_version: str = Field(min_length=1)
    rule_name: str = Field(min_length=1)
    severity: Severity
    location: DocumentLocation
    original_text: str
    suggested_correction: str | None = None
    applied_to_candidate: bool = False
    review_status: ReviewStatus = "pending_review"

    def to_json_dict(self) -> dict[str, object]:
        """Return a JSON-compatible dictionary."""
        return self.model_dump(mode="json")


class FindingIdGenerator:
    """Generate stable sequential finding IDs for one review run."""

    def __init__(self, prefix: str = "F") -> None:
        self._prefix = prefix
        self._next_value = 1

    def next_id(self) -> str:
        """Return the next finding ID."""
        finding_id = f"{self._prefix}-{self._next_value:06d}"
        self._next_value += 1
        return finding_id

