# 0001: Adopt a PR-first multi-agent workflow

- Status: Accepted

## Context

This project is a research repository owned by a single human maintainer who wants to increase throughput without losing traceability. The team needs a process that allows specialist agents to make isolated changes while preserving reviewability, clear ownership, and a clean history.

## Decision

The repository will adopt a PR-first, issue-driven multi-agent workflow:

- The human owner sets goals and approves plans.
- A PM agent manages issues, dependencies, and documentation updates.
- Specialists work on their own branches and pull requests.
- A reviewer agent validates each change against the acceptance criteria and the repo rules.
- All work must happen through GitHub issues and PRs; direct agent-to-agent coordination is not allowed.
- Reviewers operate with fresh context and do not reuse the implementer’s reasoning history.
- Changes follow the documented branch, commit, and PR conventions in `CONTRIBUTING.md` and `AGENTS.md`.

## Consequences

This process adds administrative overhead per change, but it gives the project stronger auditability, clearer ownership, and less risk of drift. It encourages predictable delivery and makes it easier for a human to resume or take over work at any point.
