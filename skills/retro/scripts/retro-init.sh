#!/usr/bin/env bash
# First-run setup for the retro skill in a repo. Creates .agents/retro.env
# (guessed, every guess commented), .agents/ledger/README.md and
# .agents/retro/. Prints the two snippets the owner applies: the
# instruction-file line and the session-end hook. Never overwrites a file
# that exists; touches nothing else.
#
#   bash scripts/retro-init.sh [--mode solo|team] [--owner <handle>]
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$repo_root"

MODE="solo"; OWNER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --mode) MODE="$2"; shift 2;; --owner) OWNER="$2"; shift 2;;
    -h|--help) sed -n '2,9p' "$0"; exit 0;; *) echo "unknown flag $1" >&2; exit 2;;
  esac
done
[ -z "$OWNER" ] && OWNER="$(git config user.name 2>/dev/null || echo owner)"

first_existing() { for p in "$@"; do [ -e "$p" ] && { printf '%s' "$p"; return; }; done; printf ''; }
all_existing() { local out=""; for p in "$@"; do [ -e "$p" ] && out="$out $p"; done; printf '%s' "${out# }"; }

TESTS=$(all_existing tests test __tests__ spec e2e)
MIGS=$(first_existing supabase/migrations migrations db/migrations prisma/migrations alembic/versions)
I18N=$(first_existing src/lib/i18n src/i18n locales public/locales i18n)
SRC=$(all_existing src app lib pages components)
RULES=$(all_existing CLAUDE.md AGENTS.md .cursorrules .github/copilot-instructions.md .claude/CLAUDE.md)
[ -d .claude/skills ] && RULES="$RULES .claude/skills/*/SKILL.md"
[ -d .cursor/rules ] && RULES="$RULES .cursor/rules/*"
LOG=$(first_existing CHANGELOG.md CHANGES.md docs/CHANGELOG.md HISTORY.md)
PRT=$(first_existing .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE.md PULL_REQUEST_TEMPLATE.md docs/PULL_REQUEST_TEMPLATE.md)
BASE=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' || true); BASE="${BASE:-main}"
PRFLOW="pr"; [ -z "$PRT" ] && [ -z "$(git ls-remote --heads origin 2>/dev/null | grep -v "refs/heads/$BASE$" | head -1)" ] && PRFLOW="none"
skill_rel="${here#"$repo_root"/}"
# Inside the repo: paths relative to the root, and the hook uses $CLAUDE_PROJECT_DIR.
# Outside it (a shared skills checkout): absolute paths, no variable.
if [ "$skill_rel" = "$here" ]; then hook_cmd="node $here/ledger-from-transcript.mjs"; else hook_cmd="node \\\"\$CLAUDE_PROJECT_DIR\\\"/$skill_rel/ledger-from-transcript.mjs"; fi

made=()
mkdir -p .agents
if [ ! -f .agents/retro.env ]; then
cat > .agents/retro.env <<ENV
# Retro skill config. Read by scripts/git-signals.sh, pr-signals.sh,
# ledger-*.mjs. Every value below was guessed by retro-init.sh on $(date -u +%F);
# check each one. Paths are space-separated and may use globs.

# solo: one person steers the agents; their own corrections are evidence.
# team: several operators; the retro aggregates by handle and reports patterns, not people.
RETRO_MODE=$MODE
# Who decides by default when a finding needs a call. In team mode a finding on
# someone else's turf names them instead.
RETRO_DECISION_OWNER="$OWNER"

# Where reports go, and where the ledger lives.
RETRO_REPORT_DIR=.agents/retro
RETRO_LEDGER_DIR=.agents/ledger

# The branch production (or the trunk) is on.
RETRO_BASE_BRANCH=$BASE
# pr: work reaches the base through pull requests. none: commits land directly.
RETRO_PR_FLOW=$PRFLOW
# Path to the PR template, if any; pass B measures the definition-of-done gap against it.
RETRO_PR_TEMPLATE="$PRT"
# One line, plain English: what a finished change must have (a PR, green CI, a preview link, a changelog entry...).
RETRO_DEFINITION_OF_DONE=""

# Paths for git-signals.sh.
RETRO_SRC_PATHS="${SRC:-src}"
RETRO_TEST_PATHS="${TESTS:-tests}"
RETRO_MIGRATION_PATHS="$MIGS"
RETRO_I18N_PATHS="$I18N"
# Files every agent session reads. The scorecard tracks their size.
RETRO_RULE_FILES="${RULES:-CLAUDE.md}"

# Logins of automated reviewers whose findings pass B checks were answered
# (for example: chatgpt-codex-connector, coderabbitai, copilot-pull-request-reviewer). Comma-separated.
RETRO_REVIEWER_LOGINS=""
# Where the team writes what it learned: a CHANGELOG, release notes, a journal table, an incident log, or "none".
RETRO_LOG_SOURCE="${LOG:-none}"
# Recurring routines pass D checks actually ran, with where their output lands. Semicolon-separated, "name=output path".
RETRO_ROUTINES=""
# Where operators' messages can be read for pass C: local (~/.claude/projects), api (a sessions API), interview, none.
RETRO_TRANSCRIPTS=local
ENV
made+=(".agents/retro.env")
fi

mkdir -p .agents/ledger .agents/retro
if [ ! -f .agents/ledger/README.md ]; then
cat > .agents/ledger/README.md <<MD
# Agent action ledger

One small JSON file per agent session that touched this repo: who ran it,
with what, on which branch, how it ended, what the operator had to repeat,
what waited on a person, which checks failed. The retro skill reads it every
two weeks; anyone with repo access can read it any time.

**It holds metadata and the operator's own instructions, paraphrased as the
rule they imply. Never product or customer content, never pasted material,
never a quote longer than a few words.** If you would not want a line read by
someone who was not in the session, do not write it.

How entries get written:
1. The agent, at wrap-up: \`bash $skill_rel/ledger-append.sh --task ... --outcome ...\`
2. A session-end hook that fills in counts (turns, tool calls, duration).
3. A person, for a tool that has neither.

Mode: $MODE. Decision owner: $OWNER.
Retention: indefinite until the team sets one. Who may delete an entry: its operator, or $OWNER.
Schema: see $skill_rel/../references/ledger.md.
MD
made+=(".agents/ledger/README.md")
fi
[ -f .agents/retro/.gitkeep ] || { touch .agents/retro/.gitkeep; made+=(".agents/retro/.gitkeep"); }

echo "retro-init: repo $repo_root"
if [ ${#made[@]} -gt 0 ]; then printf '  created %s\n' "${made[@]}"; else echo "  nothing to create; all files exist"; fi
echo
echo "Check the guesses in .agents/retro.env, then apply these two snippets. The script does not apply them."
echo
echo "1) Add to the instruction file every session reads (CLAUDE.md / AGENTS.md / .cursorrules), next to the definition of done:"
cat <<SNIP

    ## Always: write the ledger entry before you finish
    End every session by recording it in the agent action ledger (metadata and my
    own instructions only; never product or customer content):
      bash $skill_rel/ledger-append.sh --task "<one line>" --outcome <merged|pr-open|pushed-no-pr|local-only|abandoned|question-only> \\
        --correction "<each thing I had to say twice>" --blocked "<each question that waited on me>" \\
        --check-failed <step> --rule-broken "<rule>"
SNIP
echo
echo "2) Claude Code session-end hook, in .claude/settings.json (the owner applies this; a session must not edit its own hooks):"
cat <<SNIP

    {
      "hooks": {
        "SessionEnd": [
          { "hooks": [ { "type": "command",
              "command": "$hook_cmd" } ] }
        ]
      }
    }
SNIP
echo
echo "Then run the retro. The first report is the baseline."
