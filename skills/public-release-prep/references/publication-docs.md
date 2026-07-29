# Public-facing documentation and files

Contents:
1. The README's job
2. README structure
3. Writing the backstory
4. Maintenance status — say it plainly
5. `.env.example`
6. Licensing: MIT vs Apache-2.0, and how to present the choice
7. Which other files earn their place
8. What to remove from an old README

---

## 1. The README's job

For a repo published as a reference or template, the README does three things
in its first screen: tells a reader what this is, tells them whether it is for
them, and gets them to a working state. Everything else is secondary.

The failure mode specific to old project work is a README written for the
author's past self — it assumes context nobody else has, describes intentions
rather than the code that exists, and promises a roadmap abandoned three years
ago. Rewriting it is usually not editing. It is starting over from what the
code actually does now, keeping whatever was accurate.

## 2. README structure

Adapt to the project; keep the order, because it matches the order a reader
needs it in.

```markdown
# Project name

One sentence: what it does and for whom.

[Status line: what this repo is and how maintained it is — see §4]

## Background
Two to four sentences, in the owner's voice: why it was built, what it was
for, what turned out to be interesting.

## What this demonstrates
The specific techniques or patterns worth borrowing.

## Who this is for
The reader who benefits, and what they can reuse.

## Requirements
Runtime versions, package manager, external services, accounts and expected
costs. Be specific: "Node 20.x" not "Node".

## Quick start
Numbered commands, tested from a clean checkout, in order, no gaps.

## Configuration
Every environment variable: name, purpose, required or optional, and where to
get it. Points at .env.example.

## Usage
The central flow, with a real example and its real output.

## How it works
Short architecture and repository-structure explanation.

## Adapting this
The seams a forker changes first, and what to expect when they do.

## Known limitations
What does not work, what is unfinished, what is intentionally unsupported.

## Security and privacy notes
Appropriate to what the project touches.

## Attribution
People, projects, and assets that require credit.

## License
Name it and link the LICENSE file.
```

**The quick start is the most important section, and the most commonly wrong.**
Write it, then follow it literally from a fresh clone — copy-pasting each
command — before publishing. Every missing step is one an author performs from
memory without noticing.

Screenshots and examples only when sanitized and genuinely helpful. A
screenshot from an old project is a scan finding first: check it for customer
names, internal URLs, real email addresses, browser bookmarks, and
notifications before it goes anywhere near a public README.

## 3. Writing the backstory

This comes from the owner's answers and stays in their voice. It is the section
that makes the difference between a repo people read and one they scroll past —
and the one most easily ruined by inflation.

Good, because it is specific and honest about scale:

> I built this over a few weekends in 2021 because our deploy checklist was a
> Google Doc that everyone forgot to update. It reads the deploy config and
> generates the checklist instead. The interesting part turned out to be the
> dependency ordering — it is a topological sort with a cycle-breaking rule I
> am still fond of.

Bad, because none of it is true and all of it is generic:

> A robust, production-grade deployment orchestration platform leveraging
> advanced graph algorithms to deliver enterprise-scale reliability.

Rules: use the owner's words where they gave them; keep it to a few sentences;
name the specific interesting thing rather than claiming general excellence;
never inflate scale, user counts, or impact; and if the honest story is "I
built this to learn X and then stopped", write that. Readers respect it, and it
sets expectations correctly for everything that follows.

## 4. Maintenance status — say it plainly

Publishing creates an implicit promise. State the real one near the top, so
nobody files an issue expecting a response that will not come:

- **Maintained** — actively developed, issues and PRs welcome. Only if true.
- **Occasionally maintained template** — intended to be forked and adapted;
  the original may see occasional fixes; no support commitment.
- **Archived / reference example** — a snapshot of past work, published because
  it is useful or interesting to read. Not maintained. Fork it rather than
  expecting changes.

Most old project work is the third. Examples that read well:

> **Status:** archived reference project. Built in 2021, published in 2026 as a
> worked example. Not maintained — fork it freely; issues will not be answered.

> **Status:** template, occasionally maintained. Verified to install and run on
> Node 20 as of 2026-07. Adapt it to your needs; I do not take feature requests.

If the repo really is finished, GitHub's archive setting makes that unambiguous
and turns off issues — worth mentioning to the owner as a platform action they
may want to take after publishing.

## 5. `.env.example`

Every environment variable the project reads, with names and safe placeholders
only — never a real value, never a real-shaped one that could be mistaken for
live.

```bash
# Required. Postgres connection string.
# Local dev: docker compose up db, then use the value below.
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/appdev

# Required. Stripe secret key — https://dashboard.stripe.com/apikeys
# Use a test-mode key (sk_test_...) for local development.
STRIPE_SECRET_KEY=

# Optional. Enables the email digest. Unset disables the feature.
SENDGRID_API_KEY=
```

What makes this file good: it says which variables are required versus
optional, what happens when an optional one is missing, and where to obtain
each value. Local-development defaults that are genuinely safe (a local
Postgres password) can be filled in; anything that authenticates to a real
service is left empty with a comment pointing at where to get it.

Confirm `.env` is in `.gitignore`, and verify `.env.example` holds nothing
usable before publishing.

## 6. Licensing

**Making a repository public grants no reuse rights.** Without a license, the
default is exclusive copyright: readers may look, but may not legally copy,
modify, or reuse. A repo published as a template with no license is a
contradiction, and it is a very common one.

Add a license only after ownership is confirmed and the owner has chosen. If
ownership is unresolved, licensing is blocked — that is a gate, not a
preference.

The comparison to present, briefly:

| | MIT | Apache-2.0 |
| --- | --- | --- |
| Length | ~170 words | ~10,000 words |
| Permissions | Use, modify, distribute, commercially | Same |
| Requires | Keep copyright + license notice | Same, plus note significant changes |
| Patent grant | None explicit | Explicit grant from contributors |
| Patent retaliation | None | Grant terminates if you sue over patents |
| Common in | Small libraries, examples, templates | Larger projects, corporate contexts |

A reasonable default: **MIT** for a small template or reference project where
brevity is a feature and patents are not a live concern; **Apache-2.0** when
the project touches anything patent-adjacent or when contributions from others
are anticipated and explicit patent terms are worth having. Both are permissive
and widely understood; either is a defensible choice.

Other cases worth naming when they apply: **GPL-3.0** if the owner wants
derivatives to stay open (and note it constrains commercial adoption);
**CC0 / Unlicense** for public-domain dedication where even attribution is
unwanted; **CC-BY-4.0** for documentation, writing, or datasets, which the
software licenses fit poorly.

Also check the license is *available* to grant: a copyleft dependency, a
vendored component, or licensed assets can constrain what the owner may offer
for the combined work. Flag the conflict rather than resolving it silently.

Fill the copyright line with the owner's chosen name and the year. Ask which
name they want on it; a legal name, a handle, and an organization are all valid
answers and it is not the agent's call.

## 7. Which other files earn their place

Add only what serves a reader. Every file implying a commitment the owner will
not keep makes the repo *less* trustworthy, not more.

| File | Add when | Skip when |
| --- | --- | --- |
| `LICENSE` | Ownership confirmed and license chosen | Ownership unresolved — blocker |
| `.env.example` | The project reads env vars | It reads none |
| Runtime version file (`.nvmrc`, `.python-version`, `.tool-versions`) | A specific version is needed | Already declared elsewhere |
| `CONTRIBUTING.md` | Contributions genuinely welcome | Archived project — say so in the README instead |
| `SECURITY.md` | The project handles credentials, auth, or user data, *and* the owner will act on reports | Nobody is monitoring an inbox |
| `CODE_OF_CONDUCT.md` | Outside contribution is genuinely expected | An archived example with no community |
| `CHANGELOG.md` | Versioned releases are planned | A one-shot publication |
| CI workflow | It runs and passes | It would sit red — a red badge on a first release reads as broken |

For an archived reference project the honest set is usually small: `README.md`,
`LICENSE`, `.env.example`, and a runtime version file. A repo carrying a code
of conduct, a security policy, and a contributing guide for a project nobody
maintains is performing openness rather than practicing it.

## 8. What to remove from an old README

- Badges that are stale, broken, or point at a decommissioned CI.
- Screenshots that no longer match the UI, or that leak private information.
- Performance claims with no reproducible benchmark behind them.
- Roadmaps and "coming soon" for work that never happened.
- References to internal infrastructure: private URLs, internal wikis, ticket
  systems, Slack channels, deploy dashboards, staging hostnames.
- Team and contact details that are no longer accurate, and personal contact
  information the owner does not want public.
- Instructions requiring access nobody outside the original org has.
- "Production-ready", "battle-tested", "enterprise-grade", and similar claims
  the evidence does not support.
