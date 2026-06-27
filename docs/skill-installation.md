# Skill Installation

This repo contains the canonical source for the `codex-project-template` skill at `skill/codex-project-template`. An installed skill is a copied snapshot in a Codex skills directory, not a live auto-updating checkout.
Installed skill files are local Codex tool state. They are not target-project adoption files and should not be committed to projects that use the template.

## Source And Installed Copies

- Repo-owned source: `skill/codex-project-template`
- Default installed location: `$CODEX_HOME/skills/codex-project-template`
- Fallback installed location: `~/.codex/skills/codex-project-template`

Update the repo source through pull requests. Update an installed copy by reinstalling from the repo source, a GitHub ref, or a release tag. Restart Codex after installing or updating skills so the new metadata is discovered.

## Install From This Local Repo

Preview first.

PowerShell:

```powershell
python scripts/install-local-skill.py --dry-run
```

Bash:

```bash
python3 scripts/install-local-skill.py --dry-run
```

Install into the default Codex skills directory.

PowerShell:

```powershell
python scripts/install-local-skill.py
```

Bash:

```bash
python3 scripts/install-local-skill.py
```

Install into a temporary or custom skills directory.

PowerShell:

```powershell
python scripts/install-local-skill.py --dest C:\path\to\skills
```

Bash:

```bash
python3 scripts/install-local-skill.py --dest /path/to/skills
```

The helper refuses to overwrite an existing installed skill unless `--force` is passed.

## Install From GitHub

Use Codex's skill installer workflow when installing from GitHub. The underlying installer supports repo, path, and ref values:

```text
repo: owner/project-template-repo
path: skill/codex-project-template
ref: main
```

Use a tag instead of `main` when you want a stable pinned version:

```text
ref: v0.1
```

## Update An Installed Skill

1. Merge skill changes to `main` or create a release tag.
2. Reinstall from the chosen ref, or run `scripts/install-local-skill.py --force` from a trusted local checkout.
3. Restart Codex.
4. Start a fresh thread and confirm the skill appears in the available skills list.

Do not assume installed skills update automatically when this repo changes.
