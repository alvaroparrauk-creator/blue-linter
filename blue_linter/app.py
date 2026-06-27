"""Application boundary for the Blue Linter review workflow."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class ReviewResult:
    """Result returned by the placeholder review workflow."""

    input_path: Path
    output_path: Path
    status: Literal["not_implemented"]


def run_review(input_path: Path, output_path: Path) -> ReviewResult:
    """Return a placeholder result until the review pipeline is implemented."""
    return ReviewResult(
        input_path=input_path,
        output_path=output_path,
        status="not_implemented",
    )

