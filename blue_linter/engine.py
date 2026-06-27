"""Deterministic rule engine for parsed documents."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from blue_linter.document import DocumentBlock, ParsedDocument
from blue_linter.findings import DocumentLocation, Finding, FindingIdGenerator, ReviewStatus
from blue_linter.rules import StyleRule

ACRONYM_ALLOWLIST = {"UK", "US"}
ACRONYM_PATTERN = re.compile(r"\b[A-Z]{2,}\b")
ACRONYM_DEFINITION_PATTERN = re.compile(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+\(([A-Z]{2,})\)")
BULLET_TYPES = {"bullet", "list_item"}
TERMINAL_PUNCTUATION = {".", ";", ":"}


class RuleEngineError(ValueError):
    """Raised when a rule cannot be executed."""


class RuleEngine:
    """Apply enabled deterministic style rules to a parsed document."""

    def run(
        self,
        parsed_document: ParsedDocument,
        active_rules: Sequence[StyleRule],
    ) -> list[Finding]:
        """Run rules in rule-pack order and return normalized findings."""
        id_generator = FindingIdGenerator()
        findings: list[Finding] = []

        for rule in active_rules:
            if rule.type == "regex_replace":
                findings.extend(self._run_regex_replace(parsed_document, rule, id_generator))
            elif rule.type == "regex_flag":
                findings.extend(self._run_regex_flag(parsed_document, rule, id_generator))
            elif rule.type == "heading_check":
                findings.extend(self._run_heading_check(parsed_document, rule, id_generator))
            elif rule.type == "bullet_check":
                findings.extend(self._run_bullet_check(parsed_document, rule, id_generator))
            elif rule.type == "acronym_first_use":
                findings.extend(self._run_acronym_first_use(parsed_document, rule, id_generator))
            else:
                raise RuleEngineError(f"Unsupported rule type for {rule.id}: {rule.type}")

        return findings

    def _run_regex_replace(
        self,
        parsed_document: ParsedDocument,
        rule: StyleRule,
        id_generator: FindingIdGenerator,
    ) -> list[Finding]:
        pattern = self._compile_pattern(rule)
        if rule.replacement is None:
            raise RuleEngineError(f"Rule {rule.id} requires replacement for regex_replace.")

        findings: list[Finding] = []
        for block in parsed_document.blocks:
            corrected_text = pattern.sub(rule.replacement, block.text)
            if corrected_text != block.text:
                findings.append(
                    self._build_finding(
                        rule=rule,
                        block=block,
                        id_generator=id_generator,
                        suggested_correction=corrected_text,
                        review_status="pending_review",
                    )
                )
        return findings

    def _run_regex_flag(
        self,
        parsed_document: ParsedDocument,
        rule: StyleRule,
        id_generator: FindingIdGenerator,
    ) -> list[Finding]:
        pattern = self._compile_pattern(rule)

        return [
            self._build_finding(
                rule=rule,
                block=block,
                id_generator=id_generator,
                review_status="manual_review_required",
            )
            for block in parsed_document.blocks
            if pattern.search(block.text)
        ]

    def _run_heading_check(
        self,
        parsed_document: ParsedDocument,
        rule: StyleRule,
        id_generator: FindingIdGenerator,
    ) -> list[Finding]:
        return [
            self._build_finding(
                rule=rule,
                block=block,
                id_generator=id_generator,
                review_status="manual_review_required",
            )
            for block in parsed_document.blocks
            if block.block_type == "heading" and _heading_needs_review(block.text)
        ]

    def _run_bullet_check(
        self,
        parsed_document: ParsedDocument,
        rule: StyleRule,
        id_generator: FindingIdGenerator,
    ) -> list[Finding]:
        findings: list[Finding] = []
        for run in _iter_bullet_runs(parsed_document.blocks):
            if len(run) < 2:
                continue
            terminal_styles = {_terminal_style(block.text) for block in run}
            if len(terminal_styles) <= 1:
                continue
            findings.extend(
                self._build_finding(
                    rule=rule,
                    block=block,
                    id_generator=id_generator,
                    review_status="manual_review_required",
                )
                for block in run
            )
        return findings

    def _run_acronym_first_use(
        self,
        parsed_document: ParsedDocument,
        rule: StyleRule,
        id_generator: FindingIdGenerator,
    ) -> list[Finding]:
        findings: list[Finding] = []
        defined_acronyms: set[str] = set(ACRONYM_ALLOWLIST)

        for block in parsed_document.blocks:
            definitions = set(ACRONYM_DEFINITION_PATTERN.findall(block.text))
            defined_acronyms.update(definitions)

            for match in ACRONYM_PATTERN.finditer(block.text):
                acronym = match.group(0)
                if acronym in defined_acronyms:
                    continue
                findings.append(
                    self._build_finding(
                        rule=rule,
                        block=block,
                        id_generator=id_generator,
                        review_status="manual_review_required",
                    )
                )
                defined_acronyms.add(acronym)
                break

        return findings

    def _compile_pattern(self, rule: StyleRule) -> re.Pattern[str]:
        if rule.pattern is None:
            raise RuleEngineError(f"Rule {rule.id} requires pattern for {rule.type}.")
        try:
            return re.compile(rule.pattern)
        except re.error as exc:
            raise RuleEngineError(f"Rule {rule.id} has invalid regex pattern: {exc}") from exc

    def _build_finding(
        self,
        *,
        rule: StyleRule,
        block: DocumentBlock,
        id_generator: FindingIdGenerator,
        review_status: ReviewStatus,
        suggested_correction: str | None = None,
    ) -> Finding:
        return Finding(
            finding_id=id_generator.next_id(),
            rule_id=rule.id,
            rule_version=rule.version,
            rule_name=rule.name,
            severity=rule.severity,
            location=DocumentLocation(
                block_id=block.block_id,
                paragraph_index=block.paragraph_index,
                style_name=block.style_name,
                section_title=block.section_title,
            ),
            original_text=block.text,
            suggested_correction=suggested_correction,
            applied_to_candidate=False,
            review_status=review_status,
        )


def _iter_bullet_runs(blocks: Iterable[DocumentBlock]) -> Iterable[list[DocumentBlock]]:
    run: list[DocumentBlock] = []
    for block in blocks:
        if block.block_type in BULLET_TYPES:
            run.append(block)
        elif run:
            yield run
            run = []
    if run:
        yield run


def _terminal_style(text: str) -> str:
    stripped = text.rstrip()
    if not stripped:
        return "none"
    last_character = stripped[-1]
    if last_character in TERMINAL_PUNCTUATION:
        return last_character
    return "none"


def _heading_needs_review(text: str) -> bool:
    words = re.findall(r"[A-Za-z]+", text)
    if not words:
        return False

    long_uppercase_words = [
        word for word in words if len(word) > 3 and word.isupper() and word not in ACRONYM_ALLOWLIST
    ]
    if long_uppercase_words:
        return True

    title_case = all(_is_title_word(word) or _is_allowed_acronym(word) for word in words)
    sentence_case = _is_sentence_start(words[0]) and all(
        word.islower() or _is_allowed_acronym(word) for word in words[1:]
    )
    return not (title_case or sentence_case)


def _is_title_word(word: str) -> bool:
    return word[:1].isupper() and word[1:].islower()


def _is_sentence_start(word: str) -> bool:
    return _is_title_word(word) or word.islower() or _is_allowed_acronym(word)


def _is_allowed_acronym(word: str) -> bool:
    return word.isupper() and len(word) <= 3
