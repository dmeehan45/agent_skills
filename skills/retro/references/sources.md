# Where this comes from

A small team should not invent its own retrospective practice. Each piece
of this skill is lifted from something a larger team already wrote down,
and this file says which, so the next person can read the original and
judge whether it still fits.

| Idea in this skill | Source | What transfers, what does not |
|---|---|---|
| Write the lesson into a system, not a memory; blameless; the finding and the fix are separate from the person | Google SRE, "Postmortem Culture: Learning from Failure", *Site Reliability Engineering* (2016), sre.google/sre-book/postmortem-culture | Blamelessness transfers whole, and matters more with agents, because the temptation is to blame the tool. The incident trigger does not: this runs on a cadence, not after a failure |
| A fixed structure with a "did the last round's actions happen" step; gather data before generating insights; decide what to do, then close | Esther Derby and Diana Larsen, *Agile Retrospectives: Making Good Teams Great* (2006) | The five-stage shape (set the stage, gather data, generate insights, decide, close) is the run in SKILL.md. The facilitation games do not transfer to a session reading files |
| The same measures every round so a team can see direction; a health check is a conversation starter, not a KPI | Henrik Kniberg and Kristian Lindwall, "Squad Health Check model", Spotify Labs (2014), engineering.atspotify.com | The fixed-rows idea is the scorecard. Their rows are about team feeling; ours are about where the work left traces, because a session cannot be asked how it feels |
| Rework as a measure of delivery quality, alongside speed and stability | DORA, *Accelerate State of DevOps Report* (2023), which added rework rate to the four delivery metrics; dora.dev | Row 1 and row 14 are rework. DORA measures it as unplanned deployments; here it is files reopened and fix-on-fix chains, which is what a repo without deployment telemetry can see |
| Keep the instruction file short; put detail where it is loaded on demand; a rule the agent cannot test is a weak rule | Anthropic, "Claude Code: Best practices for agentic coding" (2025), anthropic.com/engineering/claude-code-best-practices | The fix ladder's preference for a check over a rule and a skill over a long section comes from here, together with the observation that instruction files grow until nobody reads them |
| A control earns trust by failing; a check that passes with the guarded thing deleted is not a check | The repo this skill was first built in, after watching a safety test pass eleven of eleven with its guarded database write removed | Transfers to any repo. "Proving a check fires" in fix-ladder.md is the procedure |
| Do not let the agent schedule its own follow-ups to wait on humans | The same repo: two sessions re-armed hourly check-ins about 120 times on a PR that had been green for a week | Transfers to any harness that offers scheduled wake-ups. The retro is started by a person |

## What this skill adds that none of the sources cover

The sources are written for teams of people. Two things change when some
of the workers are agents:

1. **The workers do not remember.** A retrospective that ends in "we
   agreed to" has changed nothing for the next session. So every fix lands
   as a check, a skill or a line in a file the agent will read, and the
   report says which.
2. **The operators' corrections are the richest evidence and the least
   recorded.** A person who tells a colleague the same thing three times
   notices. A person who tells three agent sessions the same thing often
   does not, because each session was new and each was polite. The ledger
   exists to make that countable.

If your team follows a different retro tradition, rewrite this file. Keep
the two additions.
