# Parallel Agents Workflow

Use this workflow when multiple Codex agents are active at once.

## Coordinator Flow

1. List active agents, branches, tasks, PRs, status, and likely conflict files.
2. Confirm each agent has a separate branch.
3. Confirm each implementation agent has produced a plan before editing.
4. Compare planned files and shared concepts before approving implementation.
5. Decide merge order when tasks may overlap.
6. Review PRs one at a time.
7. After a PR lands, instruct other active agents to refresh or rebase from `main`.
8. Archive completed implementation agents only after the user confirms they are done.

## Avoid Pairing Work That Touches

- the same large UI files
- shared styles or design systems
- guardrails and benchmark assertions at the same time
- shared infrastructure modules
- deployment or model-provider configuration
- the same product workflow or data model

## Good Parallel Pairings

- isolated backend scaffolding plus isolated frontend polish
- docs work plus implementation work
- infrastructure/config work plus fixture or documentation work
- low-risk UI polish plus backend-only tests or metadata work
