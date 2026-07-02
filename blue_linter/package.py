"""ZIP package generation for review artifacts."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pydantic import BaseModel, ConfigDict

from blue_linter.reports import ReportGenerationResult


class PackageGenerationError(ValueError):
    """Raised when a review package cannot be generated."""


class PackageGenerationResult(BaseModel):
    """Result returned after writing the review ZIP package."""

    model_config = ConfigDict(extra="forbid")

    package_path: Path
    included_paths: list[str]


PACKAGE_PATHS = {
    "original_document": "original/document-original.docx",
    "candidate_document": "candidate/document-style-corrected-candidate.docx",
    "analysis_html": "reports/style-analysis-report.html",
    "analysis_json": "reports/style-analysis-report.json",
    "validation_html": "reports/validation-report.html",
    "rule_pack": "rules/active-style-rules.yaml",
    "audit_json": "audit/audit.json",
}

PACKAGE_ORDER = [
    "original_document",
    "candidate_document",
    "analysis_html",
    "analysis_json",
    "validation_html",
    "rule_pack",
    "audit_json",
]


def package_review_artifacts(
    output_zip_path: Path,
    *,
    original_document_path: Path,
    candidate_document_path: Path,
    rule_pack_path: Path,
    report_result: ReportGenerationResult,
) -> PackageGenerationResult:
    """Create a ZIP package with the required review artifact layout."""
    sources = {
        "original_document": original_document_path,
        "candidate_document": candidate_document_path,
        "analysis_html": report_result.analysis_html_path,
        "analysis_json": report_result.analysis_json_path,
        "validation_html": report_result.validation_html_path,
        "rule_pack": rule_pack_path,
        "audit_json": report_result.audit_json_path,
    }
    for label, path in sources.items():
        _validate_source(path, label)

    try:
        output_zip_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PackageGenerationError(
            f"Unable to create package output directory: {exc}"
        ) from exc

    try:
        with tempfile.TemporaryDirectory(
            prefix="blue-linter-package-",
            dir=output_zip_path.parent,
        ) as staging_root_name:
            staging_root = Path(staging_root_name)
            for label in PACKAGE_ORDER:
                archive_path = PACKAGE_PATHS[label]
                staged_path = staging_root / archive_path
                staged_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(sources[label], staged_path)

            temporary_zip_path = staging_root / output_zip_path.name
            with ZipFile(temporary_zip_path, "w", compression=ZIP_DEFLATED) as package:
                for label in PACKAGE_ORDER:
                    archive_path = PACKAGE_PATHS[label]
                    package.write(staging_root / archive_path, arcname=archive_path)

            temporary_zip_path.replace(output_zip_path)
    except OSError as exc:
        raise PackageGenerationError(f"Unable to write review package: {exc}") from exc

    return PackageGenerationResult(
        package_path=output_zip_path,
        included_paths=[PACKAGE_PATHS[label] for label in PACKAGE_ORDER],
    )


def _validate_source(path: Path, label: str) -> None:
    try:
        stat_result = path.stat()
    except OSError as exc:
        raise PackageGenerationError(
            f"Required artifact is not available for {label}: {path}"
        ) from exc

    if not path.is_file():
        raise PackageGenerationError(f"Required artifact is not a file for {label}: {path}")
    if stat_result.st_size == 0:
        raise PackageGenerationError(f"Required artifact is empty for {label}: {path}")
