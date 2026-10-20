# The agent action ledger

A record of every agent session that touched the repo: who ran it, with what,
on which branch, how it ended, what the operator had to repeat, what blocked
on a person, which checks failed. It is the half of the evidence that git
and PRs cannot hold, and it evaporates when the session closes unless
something writes it down.

## Why a ledger, in plain terms

A commit says what changed. A PR says who reviewed it and whether CI
passed. Neither says that the owner typed "no em dashes" into eleven
sessions in a fortnight, that four sessions ended waiting on a question
nobody saw, that a session woke itself up 40 times overnight, or that the
agent read a rule file and did the opposite. Those are the costs of working
with agents, and today they live only in transcripts that scroll off, or in
the owner's memory.

The ledger makes them countable. Once they are countable, the retro can say
"fewer corrections than last time" instead of "it feels better", and a team
lead can answer "what are the agents actually doing in our repos" from a
folder instead of a survey.

## Design decisions, and why

- **One file per session, never a shared append-only file.** Two sessions
  on two branches write two files and never conflict. A shared log line is
  how every agent branch ends up conflicting with every other one.
- **JSON, written by a script, never by hand.** Counting needs structure;
  people hate typing JSON. `scripts/ledger-append.sh` takes flags and
  writes the file. The summary script renders markdown.
- **Metadata and the operator's own instructions only.** No product
  content, no customer text, no pasted material, no prompt someone typed
  into the product. The ledger is read by people who did not run the
  session, and it may outlive the session's privacy expectations.
- **Lives in the repo**, under `.agents/ledger/`, committed on the
  session's branch. It rides the PR, so a session that pushed and never
  opened a PR is visible as a ledger entry with no PR number, which is
  itself a finding. For an organisation that wants a cross-repo view, a
  nightly job can copy the folders into one place; the per-repo files stay
  the source of truth.
- **Three writers, and the mechanism beats the rule.** The hook writes the
  counts nobody remembers. The agent writes the judgement fields at
  wrap-up because its instruction file asks. A person writes entries for
  agents that have neither. A repo should have at least the first two; a
  ledger that depends only on the agent remembering is a rule, not a
  mechanism, and the retro's "did it hold" step will say so.

## Layout

```
.agents/
  retro.env                 # config for the scripts (paths, mode, names)
  ledger/
    README.md               # what this folder is, written by retro-init
    2026/
      2026-10-20T0215Z-claude-code-7f3a.json
      2026-10-20T0940Z-codex-b21c.json
  retro/
    2026-10-20.md           # the reports
```

File name: `<UTC start, minute precision>-<agent>-<4 hex>.json`. The hex
comes from the session id when there is one, so the hook and the agent's
wrap-up entry land in the same file and merge.

## Schema (version 1)

```json
{
  "schema": 1,
  "id": "2026-10-20T0215Z-claude-code-7f3a",
  "session_id": "full id from the harness, if known",
  "agent": "claude-code",
  "model": "optional, as the harness reports it",
  "surface": "cli | web | ide | ci | other",
  "operator": "handle or git user.name; 'unattended' for a scheduled run",
  "repo": "owner/name",
  "branch": "claude/kind-curie-o2hc3e",
  "started_at": "2026-10-20T02:15:00Z",
  "ended_at": "2026-10-20T02:51:00Z",
  "task": "one line in the operator's words, no customer data",
  "outcome": "merged | pr-open | pushed-no-pr | local-only | abandoned | question-only | unknown",
  "pr": 1234,
  "commits": 3,
  "turns": { "operator": 12, "agent": 40, "automated": 0 },
  "tool_calls": 180,
  "corrections": [
    "re-stated: no em dashes in copy",
    "re-stated: open a PR, do not just push"
  ],
  "blocked_on_person": [
    "which of two designs to build; asked at 02:40, unanswered at close"
  ],
  "checks_failed": ["lint", "typecheck"],
  "rules_read": ["CLAUDE.md", ".claude/skills/retro/SKILL.md"],
  "rules_broken": ["pushed without opening a PR"],
  "learned": "optional one line, generalisable, no names",
  "cost_note": "optional: tokens or spend if the harness reports it",
  "source": ["hook", "agent"]
}
```

Field notes:

- **`corrections`** is the most valuable field and the one only a person or
  the agent can fill. A correction is something the operator had to say
  that a rule file, a skill, or a check should already have covered. Write
  it as the rule it implies ("no em dashes"), not as a quote.
- **`blocked_on_person`** is any point where the session stopped for an
  answer. Include whether it was answered before the session closed.
- **`rules_broken`** is self-reported by the agent at wrap-up and is
  therefore incomplete. Pass D cross-checks it against git and PRs.
- **`turns.automated`** counts turns that came from a scheduled wake-up or
  an external event, not from a person. A high number is the cost signal
  that found the biggest waste in the first repo this ran on.
- **`outcome: pushed-no-pr`** and **`question-only`** are both legitimate.
  The first is a finding if the team's definition of done says PR; the
  second is a reminder that reading is work too.

## The three writers

### 1. The agent, at wrap-up

One line in the instruction file every session reads (CLAUDE.md,
AGENTS.md, `.cursorrules`, a system prompt):

```
End every session by writing its ledger entry:
  bash scripts/ledger-append.sh --task "<one line>" --outcome <outcome> \
    --correction "<each thing the operator had to say twice>" \
    --blocked "<each question that waited on a person>" \
    --check-failed <step> --rule-broken "<rule>"
Metadata and the operator's own instructions only; never product or customer content.
```

Keep the line in the section about finishing work, next to the PR rule, so
it is read at the right moment.

### 2. The hook, at session end

For Claude Code, a `SessionEnd` hook that runs
`scripts/ledger-from-transcript.mjs`. It reads the transcript path the
harness passes on stdin, counts operator turns, agent turns, automated
turns, tool calls, and duration, reads the branch, and merges those counts
into the session's entry (creating it if the agent did not). It stores no
message text.

The owner applies it, never the session (the harness blocks a session from
editing its own hooks, correctly). `scripts/retro-init.sh` prints the
exact snippet for `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR\"/.claude/skills/retro/scripts/ledger-from-transcript.mjs"
          }
        ]
      }
    ]
  }
}
```

Other agents: Cursor and Copilot expose no session-end hook today. Use the
agent's wrap-up line, and for anything with a history export, a small
script in the same shape as the transcript reader.

### 3. A person

`scripts/ledger-append.sh` with flags, from the terminal, for a session in
a tool with neither hook nor instruction file. Thirty seconds, once per
session. If the team finds this is the only writer in use, the retro's
first decision should be which agent to standardise on so the other two
writers can exist.

## Solo and team variants

| | Solo | Team |
|---|---|---|
| `operator` | Defaults to `git config user.name` | A stable handle; the retro aggregates by it but reports in aggregate |
| `corrections` | The owner's own words, paraphrased as rules | Written at wrap-up by the agent; never copied from one operator's transcript into a shared report |
| Who reads the ledger | The owner, and the retro | Anyone with repo access; say so in the folder README so nobody writes something they would not want read |
| Retention | Indefinite is fine | Set it. The folder README states the retention and who can delete |
| Cross-repo | Not needed | A nightly copy into one place, read-only, per `setup-guide.md` |

## Privacy rules, restated because they matter most here

1. No product or customer content. Not even "the user wrote something
   like".
2. No pasted material. If the operator pasted an email or a log, the
   ledger records that a correction happened, not what was in it.
3. Operators' corrections are rules, not quotes.
4. In a team, a person's entries are theirs. Aggregate in reports; take
   detail to the person.
5. The hook stores counts, never text. Read its source before installing
   it and keep it that way.
