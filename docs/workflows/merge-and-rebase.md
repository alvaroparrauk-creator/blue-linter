# Merge And Rebase Workflow

## Integration Branch

Use `main` as the integration branch unless the project says otherwise.

## Merge Order

The Coordinator should merge one PR at a time. Prefer the order that reduces conflicts and lands foundational changes before dependent work.

## After A Merge

After one PR lands:

- notify active agents
- ask them to refresh or rebase from `main`
- re-check planned file overlap
- update the active-agent status summary

## When To Pause

Pause and ask the user when:

- two active branches edit the same high-churn files
- one branch invalidates another branch's plan
- checks fail in a way that changes merge confidence
- a PR contains unexpected scope expansion
