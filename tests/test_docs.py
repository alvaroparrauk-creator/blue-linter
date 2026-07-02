from pathlib import Path


def test_docs_do_not_describe_cli_as_placeholder() -> None:
    checked_paths = [
        Path("README.md"),
        Path("samples/README.md"),
        Path("AGENTS.md"),
    ]

    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)

    assert "CLI command still returns a placeholder" not in combined_text
    assert "review command currently returns a clear placeholder" not in combined_text
