from pathlib import Path
from zipfile import ZipFile

import pytest

from blue_linter.package import PackageGenerationError, package_review_artifacts
from blue_linter.reports import ReportGenerationResult

EXPECTED_ARCHIVE_PATHS = [
    "original/document-original.docx",
    "candidate/document-style-corrected-candidate.docx",
    "reports/style-analysis-report.html",
    "reports/style-analysis-report.json",
    "reports/validation-report.html",
    "rules/active-style-rules.yaml",
    "audit/audit.json",
]


def write_artifact(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def report_result(tmp_path: Path) -> ReportGenerationResult:
    return ReportGenerationResult(
        analysis_html_path=write_artifact(tmp_path / "generated" / "analysis.html", b"<html>ok"),
        analysis_json_path=write_artifact(tmp_path / "generated" / "analysis.json", b'{"ok":true}'),
        validation_html_path=write_artifact(
            tmp_path / "generated" / "validation.html",
            b"<html>valid",
        ),
        audit_json_path=write_artifact(
            tmp_path / "generated" / "audit-output.json",
            b'{"audit":true}',
        ),
    )


def source_artifacts(tmp_path: Path) -> tuple[Path, Path, Path, ReportGenerationResult]:
    original_path = write_artifact(tmp_path / "inputs" / "quarterly-report.docx", b"original-docx")
    candidate_path = write_artifact(tmp_path / "outputs" / "candidate-v2.docx", b"candidate-docx")
    rule_pack_path = write_artifact(tmp_path / "rules-used.yaml", b"rules: active\n")
    return original_path, candidate_path, rule_pack_path, report_result(tmp_path)


def test_package_review_artifacts_creates_zip_with_required_paths(tmp_path: Path) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    output_zip_path = tmp_path / "style-review-package.zip"

    result = package_review_artifacts(
        output_zip_path,
        original_document_path=original_path,
        candidate_document_path=candidate_path,
        rule_pack_path=rule_pack_path,
        report_result=reports,
    )

    assert result.package_path == output_zip_path
    assert result.included_paths == EXPECTED_ARCHIVE_PATHS
    assert output_zip_path.exists()
    with ZipFile(output_zip_path) as package:
        assert package.namelist() == EXPECTED_ARCHIVE_PATHS


def test_packaged_entries_are_non_empty(tmp_path: Path) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    output_zip_path = tmp_path / "style-review-package.zip"

    package_review_artifacts(
        output_zip_path,
        original_document_path=original_path,
        candidate_document_path=candidate_path,
        rule_pack_path=rule_pack_path,
        report_result=reports,
    )

    with ZipFile(output_zip_path) as package:
        for archive_path in EXPECTED_ARCHIVE_PATHS:
            assert package.getinfo(archive_path).file_size > 0


def test_packaged_rule_pack_matches_supplied_rule_pack_bytes(tmp_path: Path) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    output_zip_path = tmp_path / "style-review-package.zip"

    package_review_artifacts(
        output_zip_path,
        original_document_path=original_path,
        candidate_document_path=candidate_path,
        rule_pack_path=rule_pack_path,
        report_result=reports,
    )

    with ZipFile(output_zip_path) as package:
        assert package.read("rules/active-style-rules.yaml") == rule_pack_path.read_bytes()


def test_source_file_names_are_normalized_inside_zip(tmp_path: Path) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    output_zip_path = tmp_path / "custom-output-name.zip"

    package_review_artifacts(
        output_zip_path,
        original_document_path=original_path,
        candidate_document_path=candidate_path,
        rule_pack_path=rule_pack_path,
        report_result=reports,
    )

    with ZipFile(output_zip_path) as package:
        names = package.namelist()

    assert "inputs/quarterly-report.docx" not in names
    assert "outputs/candidate-v2.docx" not in names
    assert names == EXPECTED_ARCHIVE_PATHS


@pytest.mark.parametrize(
    "missing_field",
    [
        "original",
        "candidate",
        "rule_pack",
        "analysis_html",
        "analysis_json",
        "validation_html",
        "audit_json",
    ],
)
def test_missing_artifacts_raise_package_generation_error(
    tmp_path: Path,
    missing_field: str,
) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    missing_path = tmp_path / "missing-artifact"

    if missing_field == "original":
        original_path = missing_path
    elif missing_field == "candidate":
        candidate_path = missing_path
    elif missing_field == "rule_pack":
        rule_pack_path = missing_path
    else:
        reports = reports.model_copy(
            update={
                {
                    "analysis_html": "analysis_html_path",
                    "analysis_json": "analysis_json_path",
                    "validation_html": "validation_html_path",
                    "audit_json": "audit_json_path",
                }[missing_field]: missing_path
            }
        )

    with pytest.raises(PackageGenerationError):
        package_review_artifacts(
            tmp_path / "style-review-package.zip",
            original_document_path=original_path,
            candidate_document_path=candidate_path,
            rule_pack_path=rule_pack_path,
            report_result=reports,
        )


def test_empty_artifact_raises_package_generation_error(tmp_path: Path) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    candidate_path.write_bytes(b"")

    with pytest.raises(PackageGenerationError):
        package_review_artifacts(
            tmp_path / "style-review-package.zip",
            original_document_path=original_path,
            candidate_document_path=candidate_path,
            rule_pack_path=rule_pack_path,
            report_result=reports,
        )


def test_existing_output_zip_is_replaced_after_successful_write(tmp_path: Path) -> None:
    original_path, candidate_path, rule_pack_path, reports = source_artifacts(tmp_path)
    output_zip_path = write_artifact(tmp_path / "style-review-package.zip", b"old zip bytes")

    package_review_artifacts(
        output_zip_path,
        original_document_path=original_path,
        candidate_document_path=candidate_path,
        rule_pack_path=rule_pack_path,
        report_result=reports,
    )

    with ZipFile(output_zip_path) as package:
        assert package.namelist() == EXPECTED_ARCHIVE_PATHS
