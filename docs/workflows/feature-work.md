# Feature Work Workflow

Use this workflow for non-trivial implementation work.

## Steps

1. Read `AGENTS.md`, `docs/codex-standard-procedures.md`, and relevant feature docs.
2. Create or switch to a dedicated branch using `codex/<short-task-name>`.
3. Inspect the implementation surface before planning.
4. Produce an implementation plan and wait for approval when required.
5. Implement only the approved scope.
6. Verify with relevant checks, including Docker when the project requires it.
7. Update docs and backlog when needed.
8. Commit and push.
9. Open a pull request.
10. Provide a validation note.

## Branch Naming

Use short, descriptive branch names:

```text
codex/<short-task-name>
```

## Documentation Rule

If behavior, configuration, deployment, workflows, or project status changes, update the matching docs. If no docs update is needed, say so in the validation note.
