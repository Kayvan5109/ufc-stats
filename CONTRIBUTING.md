# Contributing

This project uses a disciplined, PR-first workflow so work is traceable and reviewable.

## Branching model

- Always work from a branch, never directly on `main`.
- Use the naming convention: `agent/<role>/<issue#>-<short-slug>`.
- Example: `agent/impl/42-player-respawn`
- The owner is responsible for protecting `main` in GitHub settings.

## Commit conventions

Use Conventional Commits and include the agent role in the trailer when relevant.

Examples:
- `docs: add agent workflow and repo conventions`
- `feat: add data collection skeleton`
- `test: add collector smoke validation`
- `refactor: simplify config structure`
- `chore: update repo housekeeping`

Commit trailer:
- `Agent: implementer`
- `Agent: reviewer`
- `Agent: docs`
- `Agent: pm`

## Pull requests

- One issue per PR.
- Target `main` only after approval and green CI.
- Use squash merge only.
- Keep PRs scoped and under roughly 400 changed lines.
- Include a summary, acceptance criteria, testing commands, and reviewer notes.

## Required review policy

`main` is protected by the `protect-main` repository ruleset, which enforces:
- pull request required (no direct pushes to `main`)
- 0 required approving reviews (see below)
- required status check `validate (3.12)` from the CI workflow
- branches up to date before merge
- squash merge only
- no force pushes or branch deletion
- repository admins may bypass, for emergencies only

Why 0 approvals: this repo has a single human owner, and agents act through the owner's GitHub identity. GitHub does not allow approving your own PR, so a required approval would block every merge. Instead, approval means the reviewer agent posts `VERDICT: APPROVE` as a PR comment (see [AGENTS.md](AGENTS.md#8-reviewer-checklist)) and the owner merges.

## Local workflow

```powershell
# create branch
git checkout -b agent/docs/workflow-setup

# verify the project still works
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m compileall src
.\.venv\Scripts\python.exe -m pytest
```

## Agent workflow

- PM creates issues and tracks dependencies.
- Specialists work in their own git worktree and branch.
- Reviewers validate the code and issue acceptance criteria without reusing the implementor context.
- No direct agent-to-agent handoff: coordinate through issues and PR comments only.

## Human owner responsibilities

- approve scope and priorities,
- resolve escalations,
- merge after reviewer approval and CI pass,
- own the `main` branch and release decisions.

## Security and scope rules

Do not change secrets, CI tokens, release scripts, or dependency versions unless an issue explicitly calls for it.

## Useful references

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/adr/](docs/adr/)
