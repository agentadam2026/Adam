# AGENTS.md

Instructions for coding agents working in this repository.

## Scope

- This file applies to the repository root.
- Adam's own identity/instructions live in `packages/adam-agent/AGENTS.md`.
- Treat `packages/adam-agent/AGENTS.md` as Adam's internal prompt/config, not this repo's coding-agent policy.

## Repo Overview

- Monorepo root
- `packages/adam-agent`: Adam/OpenClaw agent files, SQLite schema/data dirs, Python tools
- `apps/web`: Next.js website that will render Adam's outputs
- `.agents/rules`: reusable operational rules for coding agents
- `.agents/skills`: local skills to extend agent workflows

## Working Norms

- Prefer small, reviewable changes.
- Preserve git history when moving files (`git mv` when possible).
- Do not modify Adam's voice/identity files unless explicitly requested.
- Keep docs and paths aligned when restructuring.
- When adding operational guidance, put reusable policies in `.agents/rules`.

## Rules

- Apply rules in `.agents/rules` when relevant.
- Current rules:
  - `.agents/rules/commit-messages.md`

## Skills

- Add repository-specific skills in `.agents/skills`.
- Keep each skill in its own folder with a `SKILL.md`.
