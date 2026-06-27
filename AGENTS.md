# Codex Agent Instructions

## Operating Rules

- The user may speak Spanish, but respond in English unless the user specifically asks otherwise.
- The user may refer to Codex chats as "agents."
- Use Docker Desktop by default when developing or verifying apps unless the project says otherwise.
- If Docker commands fail because Docker is not available on PATH, report that Docker access is unavailable in this shell. Do not silently switch to non-Docker verification.
- Keep `main` as the integration branch unless the user says otherwise.
- Use one branch per agent, normally with the `codex/` prefix.
- Inspect relevant code and project context before planning or editing.
- For non-trivial work, produce a plan and wait for explicit approval before implementing.
- Update docs when product behavior, configuration, deployment, workflows, or project status changes.
- Commit, push, and create a pull request after verified implementation unless the user says otherwise.

## Standard Commands

Refresh the local app:

```powershell
python -m pip install -e ".[dev]"
```

Build or refresh the deployed app when explicitly requested:

```powershell
TBD: add release or deploy command after packaging is introduced
```

## Operating Model

Follow `docs/codex-standard-procedures.md` for agent coordination, feature workflow, pull requests, verification, documentation expectations, and agent lifecycle.

Role-specific guidance lives in `docs/agent-roles/`.

Workflow guides live in `docs/workflows/`.

## Project-Specific Values To Fill In

- Project name: `Blue linter`
- Integration branch: `main`
- Branch prefix: `codex/`
- High-churn files or risk areas: `blue_linter/`, `tests/`, `rules/active-style-rules.yaml`, `docs/mvp-roadmap.md`
- Default verification commands: `python -m pytest`; `python -m ruff check .`
