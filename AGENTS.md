# Agent Operating Protocol

This repository is intended to support reproducible, low-friction research work for UFC fight and fighter analysis.

This file is the canonical agent ruleset for this repo. For decisions about project structure and review flow, also see [CONTRIBUTING.md](CONTRIBUTING.md), [docs/architecture.md](docs/architecture.md), and the ADRs in [docs/adr/](docs/adr/).

## 1. Core principles

- GitHub is the shared memory. Agents start without repo context; all required context should live in the issue, repo docs, or code.
- Agents communicate only through issues and PRs. No direct agent-to-agent handoffs, so there is always an audit trail and a human can take over at any point.
- The reviewer is independent. It validates the final result against the issue and the PR, not the implementer’s reasoning.
- Every change goes through a PR; no direct pushes to `main`.

## 2. Roles

- Human (owner): sets goals, approves plans, handles escalations, owns `main`.
- PM agent: breaks goals into issues, assigns work, tracks dependencies, updates docs and changelog.
- Specialist agents: complete exactly one issue each on their own branch.
- Reviewer agent: reviews the PR against acceptance criteria; read-only, no code fixes.

Separation rule:
- PM does not implement.
- Specialists do not review.
- Reviewer does not fix.

## 3. Verified repo commands

Use the actual commands below from the repo root.

```powershell
# install the local package
.\.venv\Scripts\python.exe -m pip install -e .

# syntax validation
.\.venv\Scripts\python.exe -m compileall src

# test execution
.\.venv\Scripts\python.exe -m pytest
```

Current repo status:
- There is no dedicated linting tool configured yet.
- `compileall` is the repo’s current syntax validation step until a linter is intentionally added.
- This repo does not currently have application code outside the package scaffold and docs; do not change runtime behavior without a clearly scoped issue.

## 4. Directory map and guardrails

- `src/ufc_stats/`: reusable Python package code
- `scripts/`: collection and ETL scripts
- `data/raw/`: raw downloaded data snapshots
- `data/processed/`: cleaned or derived datasets
- `notebooks/`: exploratory analysis work
- `docs/`: architecture docs and ADRs
- `.github/`: issue templates, PR template, CODEOWNERS, labels, and CI workflows

Never touch without an explicit issue:
- secrets and credentials
- CI config or release automation
- dependency version declarations
- release scripts
- lock files

## 5. Git and GitHub conventions

Branch naming:
- `agent/<role>/<issue#>-<short-slug>`
- Example: `agent/impl/42-player-respawn`

Commits:
- Use Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`
- Add a trailer identifying the agent role, e.g. `Agent: implementer`

PRs:
- one issue per PR
- include `Closes #<n>`
- keep change size small and reviewable
- squash merge only

> TODO(human): apply branch protection settings for `main` in GitHub.

## 6. Lifecycle

1. Human gives the PM a goal.
2. PM breaks the goal into issues and updates docs/changelog.
3. Owner approves the plan.
4. Specialists work in isolated branches and worktrees.
5. Draft PRs are opened after tests pass locally.
6. Reviewer validates the issue against the acceptance criteria.
7. PM closes the issue after merge and updates release notes.

## 7. Issue scope and review rules

- If an issue looks larger than ~half a day of human work, split it.
- Pass only the issue plus relevant file pointers; do not send full chat history.
- No agent-to-agent chat. Use issue/PR comments only.
- Rebase before review.
- Record non-obvious decisions in an ADR.

Hard-stop escalation rules:
- 3 failed review rounds
- touching CI config, secrets, dependency versions, or release scripts
- ambiguous requirements that contradict an ADR
- editing files outside the issue scope

Escalate using `needs-human`.

## 8. Reviewer checklist

The reviewer must verify that:
- each acceptance criterion is met and has a test demonstrating it
- tests pass locally
- scope stays within the issue
- AGENTS.md and ADR conventions are followed
- no secrets or risky changes are introduced
- docs were updated when behavior or structure changed

Verdict format:

```text
VERDICT: APPROVE | REQUEST_CHANGES | ESCALATE

Findings:
- [blocking] path/to/file.ext:LINE — issue and expected fix
- [nit] path/to/file.ext:LINE — optional suggestion
```

Nits never block a merge. Use `ESCALATE` when an owner decision is required.

## 9. Working conventions

- Prefer small, reproducible scripts over notebook-only edits.
- Validate all logic against a small sample before scaling.
- Store raw data in `data/raw/` and processed data in `data/processed/`.
- Document assumptions, limitations, and source provenance.
- Never silently discard data quality issues.
- Prefer simple baselines before more complex modeling.

## 10. Before finalizing work

- verify the relevant commands run successfully,
- summarize findings clearly,
- list limitations and next recommended actions,
- preserve a clean, maintainable project state for the next agent.

## 11. Related docs

- [README.md](README.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/adr/](docs/adr/)
