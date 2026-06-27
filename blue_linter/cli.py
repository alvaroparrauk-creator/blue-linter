"""Command line interface for Blue Linter."""

from pathlib import Path
from typing import Annotated

import typer

from blue_linter import __version__
from blue_linter.app import run_review

app = typer.Typer(
    help="Blue Linter reviews Word documents against deterministic style rules.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the Blue Linter version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Blue Linter command line interface."""


@app.command()
def review(
    input_path: Annotated[Path, typer.Argument(help="Path to the input .docx document.")],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path where the style review ZIP package will be written.",
        ),
    ],
) -> None:
    """Prepare to review a Word document."""
    if input_path.suffix.lower() != ".docx":
        raise typer.BadParameter("Input document must use the .docx extension.")

    result = run_review(input_path=input_path, output_path=output)
    typer.echo(
        "Blue Linter review pipeline is not implemented yet. "
        "Milestone 1 only validates the CLI foundation. "
        f"Input: {result.input_path}; output package: {result.output_path}; "
        f"status: {result.status}."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
