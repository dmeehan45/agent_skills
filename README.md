# Agent Skills

A collection of reusable **Agent Skills** — self-contained packages that teach an
AI coding agent (like [Claude Code](https://claude.com/claude-code)) how to do a
specific job well. Instead of re-explaining the same workflow every time, you
hand the agent a skill and it follows the playbook.

## What is a skill?

A skill is just a folder under [`skills/`](skills/). Each one contains:

- **`SKILL.md`** — the instructions, with a short `name` and `description` at the
  top. The agent reads that description to decide when the skill applies.
- **`references/`** *(optional)* — extra documents the agent opens only when it
  needs them, so the main instructions stay short.
- **`scripts/`** *(optional)* — helper programs the skill can run.

```
skills/
  frontend-polish/
    SKILL.md
  handoff-audit/
    SKILL.md
    references/
      report-template.md
      scan-playbook.md
  public-site-design-system-modernizer/
    SKILL.md
    references/
    scripts/
    agents/
```

## How to use them

1. **Make the skill available to your agent.** Copy the skill's folder into the
   place your agent looks for skills (for Claude Code, that's a `skills/`
   directory in your project or personal config), or point your agent at this
   repository.
2. **Just describe your task in plain language.** The agent matches what you
   asked for against each skill's `description` and pulls in the right one
   automatically. You can also ask for a skill by name.
3. **That's it.** No configuration files to edit — the SKILL.md tells the agent
   everything it needs.

These skills follow the open Agent Skills format, so they work with Claude Code
and other agents that support it.

## The skills

### Design & UX
| Skill | What it does |
| --- | --- |
| [`frontend-polish`](skills/frontend-polish/) | Design guardrails that keep new UI on-brand and free of the tell-tale "AI-generated" look. |
| [`ux-quality-review`](skills/ux-quality-review/) | A structured UX and visual-quality review — accessibility, flow, clarity, mobile — with prioritized fixes. |
| [`public-site-design-system-modernizer`](skills/public-site-design-system-modernizer/) | Study a public website and produce a brand-faithful (not cloned) modern design system: tokens, components, and handoff docs. |

### Writing & content
| Skill | What it does |
| --- | --- |
| [`content-rigor`](skills/content-rigor/) | Fact-check and source-check user-facing writing so its claims are true, traceable, and earned — not just nicely worded. |
| [`i18n-propagate`](skills/i18n-propagate/) | When you change a piece of copy, push the update into every language catalog and check nothing was left behind in English. |

### Review, QA & hardening
| Skill | What it does |
| --- | --- |
| [`adversarial-review`](skills/adversarial-review/) | Pressure-test a product or marketing surface by role-playing your toughest critics, then fix the worst gaps. |
| [`qa-sweep`](skills/qa-sweep/) | Run a scoped QA pass over the product and file prioritized findings (P0–P3) with evidence. It reports; it doesn't fix. |
| [`handoff-audit`](skills/handoff-audit/) | A full codebase health check that flags dead code, tech debt, and what breaks at scale — as a report, before anything gets deleted. |

### Engineering & operations
| Skill | What it does |
| --- | --- |
| [`analytics-instrument`](skills/analytics-instrument/) | Make sure a change is tracked correctly against your analytics event catalog — no missing or orphaned events, no PII leaks. |
| [`conversational-ai-efficiency-audit`](skills/conversational-ai-efficiency-audit/) | Audit a chatbot / LLM system for ways to cut cost, latency, and token usage without hurting quality or safety. |
| [`readiness-loop`](skills/readiness-loop/) | A recurring maintenance cycle that keeps a codebase handoff-ready and works down the tech-debt list one safe change at a time. |

### Customer feedback
| Skill | What it does |
| --- | --- |
| [`process-feedback`](skills/process-feedback/) | Turn a piece of customer feedback into a root-caused, prioritized action plan routed to the right owner. |

## Adding your own skill

1. Create a new folder under `skills/` named after your skill.
2. Add a `SKILL.md` with a `name` and a clear `description` — the description is
   what the agent uses to know when to reach for it, so make it specific.
3. Put any supporting docs in `references/` and any helper programs in
   `scripts/`.
4. Add a row for it to the table above so people can find it.
