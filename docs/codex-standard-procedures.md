# Codex Standard Procedures

## Operating Defaults

- Use Docker Desktop by default when developing or verifying apps unless the project says otherwise.
- Treat `main` as the integration branch unless the user names another branch.
- Use one branch per agent, normally with the `codex/` prefix.
- Keep implementation agents scoped to one feature, bug fix, or documentation task.
- Do not reuse completed implementation agents for unrelated new work.
- Keep project-specific high-churn files and risk areas visible in `AGENTS.md`.

## Planning and Execution

For feature work, non-trivial UI changes, deployment changes, guardrail changes, benchmark changes, or shared infrastructure changes:

1. Inspect relevant code, docs, and project context first.
2. Produce an implementation plan before editing files.
3. Wait for explicit user approval before implementing when the project process requires approval.
4. Implement the approved scope end-to-end.
5. Verify with the relevant Docker, frontend, backend, deployment, or documentation checks.
6. Review documentation impact for every code change, including README, roadmap, process docs, feature docs, and backlog/status docs.
7. Update relevant documentation when behavior, public interfaces, configuration, deployment, workflows, verification steps, or project status changes.
8. Commit and push after the feature is complete and verified.
9. Create a pull request for review.
10. Provide a short validation note covering what changed, how to test it, useful non-GUI checks, which verification commands ran, and what docs were updated or reviewed.

Tiny, clearly scoped fixes may be implemented directly unless the user or project instructions require a plan first.

## Documentation Expectations

Before deciding whether docs need updates, check the project README, roadmap, feature docs, infrastructure docs, evaluation docs, process docs, and backlog. Prefer targeted updates over broad rewrites.

For code changes, document the decision explicitly in the PR or final validation note: either list the docs updated or state that the docs were reviewed and no changes were needed.

When defining a recurring specialist agent role, create or update a reusable role guide under `docs/agent-roles/`.

## Template Hygiene

For projects created from this template:

- Keep `AGENTS.md` short, project-specific, and easy for every agent to read first.
- Treat this file and `docs/template-adoption.md` as the source of truth for reusable process guidance.
- Avoid source-project names, internal paths, credentials, vendors, customer details, or implementation assumptions that do not belong in the target repo.
- Prefer generic reusable language in role and workflow docs.
- Replace template placeholders during adoption. Raw placeholder markers should remain only in the canonical template source.
- Run docs-only validation after adoption or template changes, including placeholder scans and source-leak scans.

## Parallel Agent Coordination

When multiple Codex agents are active:

- Use one feature branch per agent.
- Keep each agent scoped to a clear task.
- Avoid overlapping high-churn files, shared abstractions, data models, guardrails, benchmark assertions, and deployment workflows.
- Prefer one Coordinator agent to track branches, PRs, blockers, merge order, and active file overlap.
- Confirm each implementation agent has produced a plan before editing.
- Merge one PR at a time unless the project explicitly allows batch merges.
- After one branch lands, tell other active agents to refresh or rebase from the integration branch.

## Agent Lifecycle

Implementation agents are ephemeral. After an implementation agent's feature is merged, accepted, or abandoned, and the user confirms the agent is done, the Coordinator should record the outcome and archive the thread.

Do not archive an agent while its PR is under review, checks are failing, follow-up fixes are pending, or the branch still contains unmerged work.

## Pull Request Validation Note

After opening a pull request, report:

- what changed
- how to test the change in the GUI when applicable
- useful non-GUI validation steps
- verification commands run
- Docker verification status when relevant
- docs or backlog updates made
- PR link
