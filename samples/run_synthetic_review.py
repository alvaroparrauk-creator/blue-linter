"""Run the current parser and rule engine against a DOCX file."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from blue_linter.engine import RuleEngine
from blue_linter.parser import parse_docx
from blue_linter.rules import load_active_rules

DEFAULT_DOCX_PATH = Path(__file__).with_name("synthetic-style-review.docx")
RULE_PATH = Path(__file__).parents[1] / "rules" / "active-style-rules.yaml"


def main() -> None:
    docx_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOCX_PATH
    parsed_document = parse_docx(docx_path)
    findings = RuleEngine().run(parsed_document, load_active_rules(RULE_PATH))
    rule_counts = Counter(finding.rule_id for finding in findings)

    print(f"Document: {parsed_document.source_name}")
    print(f"Parsed blocks: {len(parsed_document.blocks)}")
    print(f"Findings: {len(findings)}")
    for rule_id, count in sorted(rule_counts.items()):
        print(f"- {rule_id}: {count}")

    print()
    print(json.dumps([finding.to_json_dict() for finding in findings], indent=2))


if __name__ == "__main__":
    main()
