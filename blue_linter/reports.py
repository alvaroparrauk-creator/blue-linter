"""Report and audit artifact generation."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment
from pydantic import BaseModel, ConfigDict

from blue_linter.findings import Finding
from blue_linter.rules import RuleSet, StyleRule

ANALYSIS_HTML_FILENAME = "style-analysis-report.html"
ANALYSIS_JSON_FILENAME = "style-analysis-report.json"
VALIDATION_HTML_FILENAME = "validation-report.html"
AUDIT_JSON_FILENAME = "audit.json"

SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


class ReportRunMetadata(BaseModel):
    """Metadata shared by generated report artifacts."""

    model_config = ConfigDict(extra="forbid")

    source_document_path: Path
    candidate_document_path: Path
    generated_at_utc: datetime
    tool_version: str


class ReportGenerationResult(BaseModel):
    """Paths written by report generation."""

    model_config = ConfigDict(extra="forbid")

    analysis_html_path: Path
    analysis_json_path: Path
    validation_html_path: Path
    audit_json_path: Path


def generate_report_artifacts(
    output_dir: Path,
    *,
    analysis_findings: Sequence[Finding],
    validation_findings: Sequence[Finding],
    rule_set: RuleSet,
    run_metadata: ReportRunMetadata,
) -> ReportGenerationResult:
    """Write Milestone 7 human-readable, machine-readable, and audit artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_records = _enrich_and_sort_findings(analysis_findings, rule_set.rules)
    validation_records = _enrich_and_sort_findings(validation_findings, rule_set.rules)
    analysis_summary = _summarize_findings(analysis_records)
    validation_summary = _summarize_findings(validation_records)

    analysis_html_path = output_dir / ANALYSIS_HTML_FILENAME
    analysis_json_path = output_dir / ANALYSIS_JSON_FILENAME
    validation_html_path = output_dir / VALIDATION_HTML_FILENAME
    audit_json_path = output_dir / AUDIT_JSON_FILENAME

    common_context = _common_context(run_metadata, rule_set)
    analysis_payload = {
        **common_context,
        "report_type": "style-analysis",
        "summary": analysis_summary,
        "findings": analysis_records,
    }
    audit_payload = {
        **common_context,
        "counts": {
            "analysis": analysis_summary,
            "validation": validation_summary,
        },
        "generated_files": {
            "style_analysis_html": str(analysis_html_path),
            "style_analysis_json": str(analysis_json_path),
            "validation_html": str(validation_html_path),
            "audit_json": str(audit_json_path),
        },
    }

    _write_text(
        analysis_html_path,
        _render_html_report(
            title="Style Analysis Report",
            report_type="style-analysis",
            run_metadata=run_metadata,
            rule_set=rule_set,
            summary=analysis_summary,
            findings=analysis_records,
        ),
    )
    _write_json(analysis_json_path, analysis_payload)
    _write_text(
        validation_html_path,
        _render_html_report(
            title="Validation Report",
            report_type="validation",
            run_metadata=run_metadata,
            rule_set=rule_set,
            summary=validation_summary,
            findings=validation_records,
        ),
    )
    _write_json(audit_json_path, audit_payload)

    return ReportGenerationResult(
        analysis_html_path=analysis_html_path,
        analysis_json_path=analysis_json_path,
        validation_html_path=validation_html_path,
        audit_json_path=audit_json_path,
    )


def _enrich_and_sort_findings(
    findings: Sequence[Finding],
    rules: Sequence[StyleRule],
) -> list[dict[str, Any]]:
    rule_categories = {
        (rule.id, rule.version): rule.category
        for rule in rules
    }
    records: list[dict[str, Any]] = []
    for finding in findings:
        record = finding.to_json_dict()
        record["category"] = rule_categories.get(
            (finding.rule_id, finding.rule_version),
            "unknown",
        )
        records.append(record)

    return sorted(
        records,
        key=lambda record: (
            SEVERITY_ORDER.get(str(record["severity"]), len(SEVERITY_ORDER)),
            record["location"]["paragraph_index"],
            record["finding_id"],
        ),
    )


def _summarize_findings(findings: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total_findings": len(findings),
        "counts_by_severity": _count(finding["severity"] for finding in findings),
        "counts_by_category": _count(finding["category"] for finding in findings),
        "counts_by_rule_id": _count(finding["rule_id"] for finding in findings),
        "counts_by_applied_status": _count(
            "applied" if finding["applied_to_candidate"] else "not_applied"
            for finding in findings
        ),
        "counts_by_review_status": _count(finding["review_status"] for finding in findings),
    }


def _count(values: Sequence[object] | Any) -> dict[str, int]:
    return dict(Counter(str(value) for value in values))


def _common_context(run_metadata: ReportRunMetadata, rule_set: RuleSet) -> dict[str, Any]:
    return {
        "run_metadata": run_metadata.model_dump(mode="json"),
        "rule_set": {
            "id": rule_set.id,
            "version": rule_set.version,
        },
    }


def _render_html_report(
    *,
    title: str,
    report_type: str,
    run_metadata: ReportRunMetadata,
    rule_set: RuleSet,
    summary: dict[str, Any],
    findings: Sequence[dict[str, Any]],
) -> str:
    generated_at = run_metadata.generated_at_utc
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=UTC)

    environment = Environment(autoescape=True)
    template = environment.from_string(_HTML_TEMPLATE)
    return template.render(
        title=title,
        report_type=report_type,
        generated_at_utc=generated_at.isoformat(),
        source_document_path=run_metadata.source_document_path,
        candidate_document_path=run_metadata.candidate_document_path,
        tool_version=run_metadata.tool_version,
        rule_set=rule_set,
        summary=summary,
        findings=findings,
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <style>
    body {
      color: #202124;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
      margin: 2rem;
    }
    h1, h2 {
      color: #12395d;
    }
    table {
      border-collapse: collapse;
      margin: 1rem 0 2rem;
      width: 100%;
    }
    th, td {
      border: 1px solid #d7dde3;
      padding: 0.55rem;
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #edf2f7;
    }
    .metadata {
      background: #f8fafc;
      border: 1px solid #d7dde3;
      padding: 1rem;
    }
    .empty {
      border: 1px solid #d7dde3;
      padding: 1rem;
    }
  </style>
</head>
<body>
  <h1>{{ title }}</h1>
  <p>
    Candidate documents are review artifacts for human approval. They are not final
    approved documents.
  </p>
  <section class="metadata">
    <p><strong>Report type:</strong> {{ report_type }}</p>
    <p><strong>Generated:</strong> {{ generated_at_utc }}</p>
    <p><strong>Tool version:</strong> {{ tool_version }}</p>
    <p><strong>Rule set:</strong> {{ rule_set.id }} {{ rule_set.version }}</p>
    <p><strong>Source document:</strong> {{ source_document_path }}</p>
    <p><strong>Candidate document:</strong> {{ candidate_document_path }}</p>
  </section>

  <h2>Summary</h2>
  <table>
    <tbody>
      <tr><th>Total findings</th><td>{{ summary.total_findings }}</td></tr>
      <tr><th>By severity</th><td>{{ summary.counts_by_severity }}</td></tr>
      <tr><th>By category</th><td>{{ summary.counts_by_category }}</td></tr>
      <tr><th>By rule</th><td>{{ summary.counts_by_rule_id }}</td></tr>
      <tr><th>By applied status</th><td>{{ summary.counts_by_applied_status }}</td></tr>
      <tr><th>By review status</th><td>{{ summary.counts_by_review_status }}</td></tr>
    </tbody>
  </table>

  <h2>Findings</h2>
  {% if findings %}
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Severity</th>
        <th>Category</th>
        <th>Rule</th>
        <th>Location</th>
        <th>Original text</th>
        <th>Suggested correction</th>
        <th>Applied</th>
        <th>Review status</th>
      </tr>
    </thead>
    <tbody>
      {% for finding in findings %}
      <tr>
        <td>{{ finding.finding_id }}</td>
        <td>{{ finding.severity }}</td>
        <td>{{ finding.category }}</td>
        <td>{{ finding.rule_id }} {{ finding.rule_version }}<br>{{ finding.rule_name }}</td>
        <td>
          paragraph {{ finding.location.paragraph_index }};
          block {{ finding.location.block_id }};
          style {{ finding.location.style_name }}
          {% if finding.location.section_title %}
          ; section {{ finding.location.section_title }}
          {% endif %}
        </td>
        <td>{{ finding.original_text }}</td>
        <td>{{ finding.suggested_correction or "" }}</td>
        <td>{{ "Applied" if finding.applied_to_candidate else "Not applied" }}</td>
        <td>{{ finding.review_status }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p class="empty">No findings were reported.</p>
  {% endif %}
</body>
</html>
"""
