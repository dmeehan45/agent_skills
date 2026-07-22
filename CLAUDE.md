# CLAUDE.md

Guidance for AI agents working in this repository.

## What this repo is

A library of **Agent Skills**. Every skill lives in its own folder under
[`skills/`](skills/) and contains a `SKILL.md` (with a `name` and `description`)
plus optional `references/` and `scripts/` subfolders. Keep this structure
consistent — all skills live under `skills/`, one folder each.

## Keep the README in sync

`README.md` is the public entry point: it orients new readers and lists every
skill with a plain-language summary of what it does.

**Whenever you change the skills, update `README.md` in the same change.** That
includes:

- adding a new skill,
- removing a skill,
- renaming a skill, or
- changing what a skill does (its purpose or `description`).

Treat the README update as part of the skill change, not a follow-up. After any
such change, confirm the README's skill list still matches the folders under
`skills/` and that each summary is accurate and written in simple language for a
public reader.
