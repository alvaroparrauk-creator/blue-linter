from pathlib import Path

import pytest
from docx import Document

from blue_linter.engine import RuleEngine
from blue_linter.parser import DocumentParseError, parse_docx
from blue_linter.rules import StyleRule


def save_document(path: Path, paragraphs: list[tuple[str, str | None]]) -> Path:
    document = Document()
    for text, style in paragraphs:
        paragraph = document.add_paragraph(text)
        if style is not None:
            paragraph.style = style
    document.save(path)
    return path


def test_parse_docx_preserves_source_name_order_and_stable_block_ids(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "sample.docx",
        [
            ("First paragraph", None),
            ("Second paragraph", None),
        ],
    )

    parsed_document = parse_docx(docx_path)

    assert parsed_document.source_name == "sample.docx"
    assert [block.block_id for block in parsed_document.blocks] == ["p-000001", "p-000002"]
    assert [block.paragraph_index for block in parsed_document.blocks] == [0, 1]
    assert [block.text for block in parsed_document.blocks] == [
        "First paragraph",
        "Second paragraph",
    ]


def test_parse_docx_detects_headings_and_section_context(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "headings.docx",
        [
            ("Executive Summary", "Heading 1"),
            ("Revenue increased by 25 %.", None),
            ("Operating Model", "Heading 2"),
            ("Delivery remains on track.", None),
        ],
    )

    parsed_document = parse_docx(docx_path)

    assert [block.block_type for block in parsed_document.blocks] == [
        "heading",
        "paragraph",
        "heading",
        "paragraph",
    ]
    assert [block.section_title for block in parsed_document.blocks] == [
        "Executive Summary",
        "Executive Summary",
        "Operating Model",
        "Operating Model",
    ]


def test_parse_docx_classifies_bullets_lists_and_blank_paragraphs(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "lists.docx",
        [
            ("Styled bullet", "List Bullet"),
            ("\u2022 Manual bullet", None),
            ("1. Manual numbered item", None),
            ("A) Manual lettered item", None),
            ("", None),
            ("Normal paragraph", None),
        ],
    )

    parsed_document = parse_docx(docx_path)

    assert [block.block_type for block in parsed_document.blocks] == [
        "bullet",
        "bullet",
        "list_item",
        "list_item",
        "unknown",
        "paragraph",
    ]


def test_parse_docx_classifies_word_list_styles_as_list_items(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "word-list.docx",
        [
            ("Styled number", "List Number"),
        ],
    )

    parsed_document = parse_docx(docx_path)

    assert parsed_document.blocks[0].block_type == "list_item"


def test_parse_docx_classifies_manual_bullets_without_spaces(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "manual-bullets.docx",
        [
            ("\u2022Manual bullet", None),
            ("-Manual bullet", None),
            ("*Manual bullet", None),
            ("\u2013Manual bullet", None),
        ],
    )

    parsed_document = parse_docx(docx_path)

    assert [block.block_type for block in parsed_document.blocks] == [
        "bullet",
        "bullet",
        "bullet",
        "bullet",
    ]


def test_parse_docx_classifies_common_manual_list_markers(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "manual-lists.docx",
        [
            ("1) Numbered item", None),
            ("1. Numbered item", None),
            ("A) Lettered item", None),
            ("A. Lettered item", None),
            ("a) Lowercase item", None),
            ("a. Lowercase item", None),
        ],
    )

    parsed_document = parse_docx(docx_path)

    assert [block.block_type for block in parsed_document.blocks] == [
        "list_item",
        "list_item",
        "list_item",
        "list_item",
        "list_item",
        "list_item",
    ]


def test_parse_docx_rejects_non_docx_extension(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("not a docx", encoding="utf-8")

    with pytest.raises(DocumentParseError, match=".docx extension"):
        parse_docx(path)


def test_parse_docx_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(DocumentParseError, match="does not exist"):
        parse_docx(tmp_path / "missing.docx")


def test_parse_docx_rejects_invalid_docx_file(tmp_path: Path) -> None:
    path = tmp_path / "broken.docx"
    path.write_text("not a zip package", encoding="utf-8")

    with pytest.raises(DocumentParseError, match="Unable to parse DOCX"):
        parse_docx(path)


def test_parsed_docx_output_can_be_used_by_rule_engine(tmp_path: Path) -> None:
    docx_path = save_document(
        tmp_path / "engine-input.docx",
        [
            ("Revenue increased by 25 %.", None),
        ],
    )
    style_rule = StyleRule(
        id="STYLE-PERCENT-SPACING",
        version="1.0.0",
        name="Percentage spacing",
        category="number-format",
        severity="medium",
        enabled=True,
        type="regex_replace",
        auto_fix=True,
        pattern=r"\b(\d+)\s+%",
        replacement=r"\1%",
    )

    findings = RuleEngine().run(parse_docx(docx_path), [style_rule])

    assert len(findings) == 1
    assert findings[0].location.block_id == "p-000001"
    assert findings[0].suggested_correction == "Revenue increased by 25%."
