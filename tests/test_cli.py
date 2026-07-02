from pathlib import Path
from zipfile import ZipFile

from docx import Document
from typer.testing import CliRunner

from blue_linter import __version__
from blue_linter.cli import app

runner = CliRunner()


def test_version_is_exposed() -> None:
    assert __version__ == "0.1.0"


def test_cli_version_option() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def save_synthetic_document(path: Path) -> Path:
    document = Document()
    document.add_paragraph("Revenue increased by 25 %.")
    document.save(path)
    return path


def test_review_command_creates_review_package(tmp_path: Path) -> None:
    input_path = save_synthetic_document(tmp_path / "sample.docx")
    output_path = tmp_path / "style-review-package.zip"

    result = runner.invoke(
        app,
        ["review", str(input_path), "--output", str(output_path)],
    )

    assert result.exit_code == 0
    assert "Blue Linter review completed." in result.output
    assert "status: completed" in result.output
    assert output_path.exists()
    with ZipFile(output_path) as package:
        assert "candidate/document-style-corrected-candidate.docx" in package.namelist()


def test_review_reports_missing_docx_with_parsing_stage(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "review",
            str(tmp_path / "missing.docx"),
            "--output",
            str(tmp_path / "style-review-package.zip"),
        ],
    )

    assert result.exit_code != 0
    assert "Parsing failed" in result.output
    assert "does not exist" in result.output


def test_review_reports_invalid_docx_with_parsing_stage(tmp_path: Path) -> None:
    input_path = tmp_path / "broken.docx"
    input_path.write_text("not a real docx", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "review",
            str(input_path),
            "--output",
            str(tmp_path / "style-review-package.zip"),
        ],
    )

    assert result.exit_code != 0
    assert "Parsing failed" in result.output
    assert "Unable to parse DOCX" in result.output


def test_review_reports_invalid_output_destination_with_packaging_stage(
    tmp_path: Path,
) -> None:
    input_path = save_synthetic_document(tmp_path / "sample.docx")

    result = runner.invoke(
        app,
        ["review", str(input_path), "--output", str(tmp_path)],
    )

    assert result.exit_code != 0
    assert "Packaging failed" in result.output


def test_review_rejects_non_docx_input() -> None:
    result = runner.invoke(
        app,
        ["review", "sample.pdf", "--output", "style-review-package.zip"],
    )

    assert result.exit_code != 0
    assert "Input document must use the .docx extension." in result.output
