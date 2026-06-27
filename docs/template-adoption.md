# Template Adoption Guide

Use this guide when importing the Codex multi-agent operating model into another code project. The goal is to make each adopted copy project-specific enough to be useful without leaking assumptions from any source project.

## Adoption Flow

1. Identify the target repo and confirm it is the project root.
2. Choose the placeholder values in the registry below.
3. Copy `AGENTS.md`, `docs/`, and `templates/` into the target repo manually or with `scripts/install-template.py`.
4. Review the imported docs and remove guidance that does not apply to the target project.
5. Run the validation checks below.
6. Commit the adopted operating model in the target repo.

Prefer the installer for repeatable imports. Use manual copying only while testing new template changes or when the target repo needs unusual file placement.

For a fictional filled project profile and task brief, see `examples/`. Use them to understand the shape of completed artifacts, not as copy-paste source for real projects.

## Target Repo Choices

Before installing, decide which adoption path applies.

Existing Git repo:

1. Confirm the target path is the repo root and contains `.git`.
2. Run the installer with `--dry-run`.
3. Review existing `AGENTS.md`, `docs/`, or `templates/` before using `--force`.
4. Run validation, then commit the adopted operating docs in a normal feature branch or setup commit.

New local repo:

1. Create the project directory.
2. Ask the user before running `git init -b <default-branch>`.
3. Run the installer with `--dry-run`, then real mode after review.
4. Run validation, commit the adopted files, and add a remote later if needed.

New GitHub repo:

1. Confirm owner/name, visibility, default branch, and local target path.
2. Ask the user before running `gh repo create`.
3. Ask before adding remotes, committing, or pushing.
4. Run the installer and validation before the first template adoption commit.

Docs-only or smoke-test target:

1. Run dry-run first and keep the target outside real project source.
2. Do not treat temporary installed files as source-controlled project state.
3. Delete or ignore the temporary target after the test.

The installer does not initialize Git, create GitHub repositories, add remotes, commit, or push. Those steps are adoption orchestration and require explicit user approval in the active Codex thread.

If `git init -b <default-branch>` is unavailable in the local Git version, initialize Git only after approval, then ask before running `git branch -M <default-branch>`.

## Placeholder Registry

| Placeholder | Meaning | Default | Example |
| --- | --- | --- | --- |
| `Blue linter` | Human-readable project name for agent naming and status notes. | Required | `Customer Portal` |
| `main` | Integration branch agents should refresh from and merge into. | `main` | `main` |
| `codex/` | Prefix for Codex implementation branches. | `codex/` | `codex/` |
| `TBD: add local development refresh command` | Command to start or refresh the local development app. | Project-specific TBD | `docker compose up --build` |
| `TBD: add release or deploy command` | Command to build, deploy, or refresh the released app when explicitly requested. | Project-specific TBD | `docker compose build` |
| `TBD: list high-churn files or risk areas` | Files, directories, or concepts that commonly conflict across agents. | Project-specific TBD | `src/app/routes.ts`, `docs/backlog.md` |
| `TBD: add verification commands` | Default verification commands or categories. | Project-specific TBD | `docker compose run --rm test` |

If a project has no release command yet, replace the release-command placeholder with a clear value such as `TBD: add release command`. Do not leave raw template placeholders in an adopted project unless the file is intentionally documenting the template itself.

## Project Profile Choices

Before importing, choose:

- Project type: frontend app, backend service, full-stack app, library, CLI, or docs-only repo.
- Verification stance: Docker Compose, Dockerfile, package scripts, language-native tests, docs-only checks, or not established yet.
- Branch model: normally `main` plus `codex/` feature branches.
- PR model: always PR by default unless the target project has a different review process.
- Active roles: keep all four role guides unless the project is intentionally single-agent or docs-only.
- Risk areas: list high-churn files, shared abstractions, data models, deployment config, benchmark assertions, or design-system files.

## Installer Usage

Run from this template repo.

PowerShell:

```powershell
python scripts/install-template.py --target C:\path\to\target-repo --project-name "Target Project"
```

Bash:

```bash
python3 scripts/install-template.py --target /path/to/target-repo --project-name "Target Project"
```

Preview first.

PowerShell:

```powershell
python scripts/install-template.py --target C:\path\to\target-repo --project-name "Target Project" --dry-run
```

Bash:

```bash
python3 scripts/install-template.py --target /path/to/target-repo --project-name "Target Project" --dry-run
```

Common options.

PowerShell:

```powershell
python scripts/install-template.py `
  --target C:\path\to\target-repo `
  --project-name "Target Project" `
  --default-branch main `
  --branch-prefix codex/ `
  --dev-refresh-command "docker compose up --build" `
  --release-command "docker compose build" `
  --verification-commands "docker compose run --rm test" `
  --high-churn-files "src/app/routes.ts, docs/backlog.md"
```

Bash:

```bash
python3 scripts/install-template.py \
  --target /path/to/target-repo \
  --project-name "Target Project" \
  --default-branch main \
  --branch-prefix codex/ \
  --dev-refresh-command "docker compose up --build" \
  --release-command "docker compose build" \
  --verification-commands "docker compose run --rm test" \
  --high-churn-files "src/app/routes.ts, docs/backlog.md"
```

The installer refuses to overwrite existing files unless `--force` is passed. Use `--force` only after reviewing the target repo's current operating docs.

## Version Control Expectations

In normal project adoption, commit the copied and customized `AGENTS.md`, `docs/`, and `templates/` files to the target repo. These files are the shared operating model that future Codex agents need after clone, across branches, and during pull request review.

Do not commit local installed skill snapshots, temporary smoke-test targets, validation output, machine-specific notes, or personal Codex configuration. Installed skills under locations such as `~/.codex/skills` are local tool state, not target-project source.

Before committing, confirm:

- Intentional `TBD` values are acceptable or replaced.
- `docs/backlog.md` describes the target project's real work.
- `AGENTS.md` names the target project and branch model.
- Source-leak scans pass for any terms from projects used while creating the target.

## Manual Adoption

If copying manually:

1. Copy `AGENTS.md`, `docs/`, and `templates/` into the target repo.
2. Replace every placeholder in the registry.
3. Keep `AGENTS.md` short and project-specific.
4. Put detailed process changes in `docs/codex-standard-procedures.md` or focused docs under `docs/`.
5. Add project-specific role or workflow docs only when they are reusable for future agents.

## Validation

Run these checks in the adopted project.

PowerShell:

```powershell
$placeholderMarker = '{' + '{'
rg -n -F $placeholderMarker AGENTS.md docs templates
rg -n -F "TBD" AGENTS.md docs templates
```

Bash:

```bash
placeholder_marker="$(printf '{%.0s' 1 2)"
rg -n -F "$placeholder_marker" AGENTS.md docs templates
rg -n -F 'TBD' AGENTS.md docs templates
```

If `rg` is not available in the Linux environment, use `grep`:

```bash
placeholder_marker="$(printf '{%.0s' 1 2)"
grep -R -n -F "$placeholder_marker" AGENTS.md docs templates
grep -R -n -F 'TBD' AGENTS.md docs templates
```

Run source-leak scans for names, paths, products, vendors, or internal terms from any source project used while creating the target repo. For this template repo, also scan for accidental copied project names before release.

## Automated Validation

The template repo also provides a dependency-free validation script.

Validate the canonical template source:

PowerShell:

```powershell
python scripts/validate-template.py --mode template-source --leak-term <source-project-name> --leak-term <source-product-name>
```

Bash:

```bash
python3 scripts/validate-template.py --mode template-source --leak-term <source-project-name> --leak-term <source-product-name>
```

Validate an adopted target from this repo:

PowerShell:

```powershell
python scripts/validate-template.py --root C:\path\to\target-repo --mode adopted --leak-term <source-project-name>
```

Bash:

```bash
python3 scripts/validate-template.py --root /path/to/target-repo --mode adopted --leak-term <source-project-name>
```

By default, `TBD` markers are warnings because adopted copies may intentionally leave some project values unfinished during the first pass. Add `--fail-on-tbd` when the adopted project should be fully customized.

The validation script fails when the root path does not exist or when the requested paths match no files. This prevents a mis-typed target path from looking like a clean validation pass.

Confirm manually:

- `AGENTS.md` names the right project values.
- The default branch and branch prefix match the target repo.
- Verification commands are real or explicitly marked as not established yet.
- High-churn files reflect the target repo, not this template.
- Backlog entries describe the target project's actual near-term work.
- The target Git/GitHub state matches the intended adoption path.

## Updating An Adopted Project

When updating a repo that already adopted the template:

1. Run the installer with `--dry-run`.
2. Compare existing files before using `--force`.
3. Preserve target-project customizations unless the user explicitly wants a reset.
4. Re-run validation checks after updates.

## Adoption Validation Notes

The template was validated against a disposable target repo with an existing `README.md`, `src/` directory, Git repository, and `main` branch.

Observed behavior:

- Dry-run reported the expected files and placeholder replacement counts.
- Real install copied `AGENTS.md`, `docs/`, and `templates/` without changing existing project files outside those paths.
- Raw placeholder marker scans found no unresolved template placeholders in the adopted target.
- A second install without `--force` refused to overwrite the adopted operating docs.

Manual review is still required after adoption:

- Replace any intentional `TBD` values left by omitted optional installer arguments.
- Update the copied backlog so it describes the target project's actual work.
- Review high-churn files, verification commands, and role/workflow fit for the target project.
