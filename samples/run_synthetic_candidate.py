"""Generate a candidate DOCX from the synthetic sample document."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from blue_linter.candidate import generate_candidate_document
from blue_linter.engine import RuleEngine
from blue_linter.parser import parse_docx
from blue_linter.rules import load_active_rules

DEFAULT_DOCX_PATH = Path(__file__).with_name("synthetic-style-review.docx")
DEFAULT_CANDIDATE_PATH = Path(__file__).with_name("synthetic-style-review-candidate.docx")
RULE_PATH = Path(__file__).parents[1] / "rules" / "active-style-rules.yaml"


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOCX_PATH
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CANDIDATE_PATH

    active_rules = load_active_rules(RULE_PATH)
    parsed_document = parse_docx(input_path)
    findings = RuleEngine().run(parsed_document, active_rules)
    result = generate_candidate_document(
        input_path=input_path,
        output_path=output_path,
        parsed_document=parsed_document,
        active_rules=active_rules,
        findings=findings,
    )

    print(f"Original: {input_path}")
    print(f"Candidate: {result.candidate_path}")
    print(f"Parsed blocks: {len(parsed_document.blocks)}")
    print(f"Findings: {len(findings)}")
    print(f"Applied fixes: {result.applied_count}")
    print(f"Skipped fixes: {result.skipped_count}")
    if result.skipped_reasons:
        print("Skipped reasons:")
        for finding_id, reason in sorted(result.skipped_reasons.items()):
            print(f"- {finding_id}: {reason}")

    print()
    print(json.dumps([finding.to_json_dict() for finding in result.findings], indent=2))


if __name__ == "__main__":
    main()
