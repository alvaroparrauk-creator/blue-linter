# Project Backlog

Use this file as the shared planning surface for near-term work, deferred ideas, completed work, and coordination notes.

## Recommended Next

- Implement Milestone 3: rule engine execution over a parsed document model.
- Replace remaining project `TBD` values once the development, test, and packaging commands are established.

## Near-Term Candidates

### Build Local DOCX Style Review MVP

Status: in progress

Why now:
- Blue Linter needs a small, reliable foundation before adding UI, backend, or multi-format support.
- The first version should prove deterministic rule execution, traceable findings, candidate document generation, reports, validation, and ZIP packaging.

Scope:
- Create a Python package with parser, rule engine, findings model, candidate generator, report generator, validation pass, and ZIP package generator.
- Add `rules/active-style-rules.yaml` with versioned example rules for percentage spacing, repeated whitespace, bullet punctuation, acronym first-use, and heading capitalisation.
- Add a CLI that accepts a `.docx` and produces `style-review-package.zip`.
- Add unit tests for rules and an end-to-end test with a generated sample `.docx`.
- Document setup, test, and run commands.

Out of scope:
- Backend service.
- Web UI.
- Multiple input formats.
- Runtime rule uploads.
- External rule repository.
- AI-based rewriting.

Expected validation:
- Unit tests pass.
- End-to-end test confirms ZIP structure, candidate document, HTML report, JSON report, validation report, copied rules, and audit file.
- Candidate document is explicitly labelled as pending human review.

Suggested branch:
- `codex/local-docx-style-review-mvp`

### Prepare Backend-Compatible Core Boundaries

Status: deferred

Why later:
- The MVP runs locally, but the core should eventually be callable by a backend used by multiple frontend types.

Scope:
- Keep parsing, rule execution, reporting, and packaging separate from CLI concerns.
- Define service-layer interfaces that could later sit behind an HTTP API.
- Avoid filesystem assumptions inside core logic where practical.

Out of scope:
- Building the backend during the MVP.
- Authentication, tenancy, queues, or persistent storage.

Expected validation:
- CLI remains thin and delegates to reusable application services.

Suggested branch:
- `codex/backend-compatible-core`

### Explore Multi-Format Document Input

Status: deferred

Why later:
- The MVP only accepts Word `.docx`, but future users may need PDF, Markdown, HTML, or other formats.

Scope:
- Identify a normalized document model that can represent paragraphs, headings, lists, sections, and locations across formats.
- Document format-specific parser requirements.

Out of scope:
- Implementing non-DOCX parsers in the MVP.

Expected validation:
- Architecture notes show how future parsers can feed the same rule engine.

Suggested branch:
- `codex/multi-format-input-design`

### External Version-Controlled Rules Repository

Status: deferred

Why later:
- Rules live inside the app for the MVP, but a separate repository may be better for governance, review, and release control later.

Scope:
- Design how rule packs could be imported, pinned, validated, and audited from an external version-controlled source.
- Define rule pack versioning and compatibility expectations.

Out of scope:
- Runtime user-uploaded rules.
- Moving rules out of the app during the MVP.

Expected validation:
- Proposed design preserves deterministic behavior and auditability.

Suggested branch:
- `codex/external-rules-repo-design`

### Web-Based Interactive Review Interface

Status: deferred

Why later:
- Human review is central to the product, but a static report is enough for the first MVP.

Scope:
- Design a web interface for filtering findings, reviewing suggested changes, accepting or rejecting changes, and downloading outputs.
- Consider how the UI would consume the JSON report and candidate document.

Out of scope:
- Building the web UI during the MVP.

Expected validation:
- Design identifies the minimum API/data contract needed for interactive review.

Suggested branch:
- `codex/interactive-review-ui-design`

### Default-Branch Skill Prompt Guidance

Status: completed

Why now:
- New-project smoke testing showed plain `git init` can create `master` even when the chosen default branch is `main`.

Scope:
- Guide new local repo setup to initialize Git with the selected default branch.
- Add source-only skill usage prompts for adoption and role-thread startup.

Out of scope:
- Adding Git side effects to `scripts/install-template.py`.

Expected validation:
- Skill guidance and adoption docs mention `git init -b <default-branch>` with fallback branch rename.
- Usage prompts live outside copied template docs.

Suggested branch:
- `codex/default-branch-skill-prompts`

### Guided Git/GitHub Adoption Readiness

Status: completed

Why now:
- Outside-project smoke testing showed the skill could install files into a non-Git target without first explaining Git or GitHub setup choices.

Scope:
- Add required preflight guidance for existing repos, new local repos, new GitHub repos, and docs-only smoke targets.
- Clarify that Git init, GitHub repo creation, commits, remotes, and pushes are agent-guided actions that require explicit user approval.
- Document which adopted files should normally be version-controlled.

Out of scope:
- Adding Git or GitHub side effects to `scripts/install-template.py`.

Expected validation:
- Skill guidance keeps dry-run-first behavior and states that the installer only copies files.
- Adoption docs explain Git/GitHub paths and version-control expectations.

Suggested branch:
- `codex/guided-repo-adoption`

### Validate Template Adoption On A Real Repo

Status: completed

Why now:
- The template now has a documented adoption path and installer; it needs a realistic dry run before being treated as stable.

Scope:
- Run the installer against a target repo or disposable clone.
- Record unclear prompts, missing placeholders, or project-specific customization gaps.
- Update docs or installer behavior based on findings.

Out of scope:
- Building a packaged marketplace plugin or globally installing the skill.

Expected validation:
- Dry-run and real installer pass against a temporary target.
- Placeholder and source-leak scans in the target.

Suggested branch:
- `codex/validate-template-adoption`

### Validate Linux Skill Readiness

Status: completed

Why now:
- The template has a repo-owned skill source, but it needs Linux-friendly docs and install/update guidance before regular use.

Scope:
- Add paired PowerShell and Bash examples for adoption and validation.
- Document local and GitHub-based skill installation.
- Add a local skill install helper.
- Validate installer behavior through WSL or another Linux environment.

Out of scope:
- Marketplace packaging or automatic skill updates.

Expected validation:
- Local and WSL installer dry-run, real install, placeholder scan, and overwrite refusal.
- Local skill installer dry-run, real install, and overwrite refusal against a temp skills directory.

Suggested branch:
- `codex/linux-skill-readiness`

### Harden Docs-Only Validation

Status: completed

Why now:
- Adopted projects need a simple way to confirm that template placeholders and source-project details did not leak.

Scope:
- Define repeatable docs-only validation commands.
- Consider adding a small validation script if manual `rg` checks become too error-prone.
- Document expected output and common fixes.

Out of scope:
- Full Markdown linting infrastructure unless a target project already uses it.

Expected validation:
- Validation commands catch raw placeholders and known leak terms.

Suggested branch:
- `codex/docs-validation`

### Strengthen Template Examples

Status: completed

Why now:
- Users can understand the operating model faster with one generic filled example.

Scope:
- Add a small example project profile or filled task brief using imaginary generic values.
- Keep examples clearly fictional and reusable.

Out of scope:
- Source-project-specific examples.

Expected validation:
- Example contains no real project names, paths, or secrets.

Suggested branch:
- `codex/template-examples`

## In Progress

| Feature | Agent | Branch | Status | PR | Notes |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | No active implementation agents. |

## Deferred

- Package or globally install the `codex-project-template` Codex skill after docs and installer behavior are stable.
- Add richer project profiles for frontend apps, backend services, full-stack apps, libraries, CLIs, and docs-only repos.
- Add an update mode that can safely merge new template versions into already-adopted repos.

## Completed

- Initial docs-only template with `AGENTS.md`, standard procedures, role guides, workflow guides, and reusable templates.
- Template adoption workflow with adoption guide, placeholder registry, installer, and repo-owned skill source.
- Linux skill readiness with Bash examples, skill installation guidance, local skill installer, and WSL validation.
- Template adoption validation against a disposable realistic target repo with README, `src/`, Git, and `main` branch.
- Docs-only validation script for placeholders, `TBD` markers, and configurable source-leak terms.
- Generic fictional examples for a project profile and filled implementation task brief.
- Guided Git/GitHub adoption readiness with preflight guidance and version-control expectations.
- Default-branch Git initialization guidance and source-only skill usage prompts.

## Coordination Notes

High-churn files or risk areas:

- `AGENTS.md`
- `docs/codex-standard-procedures.md`
- `docs/template-adoption.md`
- `scripts/install-template.py`
- `skill/codex-project-template/SKILL.md`
