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


def test_review_command_returns_placeholder_response() -> None:
    result = runner.invoke(
        app,
        ["review", "sample.docx", "--output", "style-review-package.zip"],
    )

    assert result.exit_code == 0
    assert "review pipeline is not implemented yet" in result.output
    assert "status: not_implemented" in result.output


def test_review_rejects_non_docx_input() -> None:
    result = runner.invoke(
        app,
        ["review", "sample.pdf", "--output", "style-review-package.zip"],
    )

    assert result.exit_code != 0
    assert "Input document must use the .docx extension." in result.output
