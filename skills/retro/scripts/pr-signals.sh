#!/usr/bin/env bash
# Pass B numbers from the pull-request record via the GitHub CLI, as markdown.
#
#   bash scripts/pr-signals.sh [--since 14d|YYYY-MM-DD] [--until YYYY-MM-DD] [--limit 60]
#
# Read-only: list and read only, never comment, label or resolve. If `gh` is
# missing or not signed in, it says so and exits 0; pass B then uses a GitHub
# tool directly. Reviewer logins come from RETRO_REVIEWER_LOGINS in retro.env.
set -uo pipefail
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$repo_root"
if [ -f .agents/retro.env ]; then set -a; . .agents/retro.env; set +a; fi

SINCE_ARG="14d"; UNTIL_ARG=""; LIMIT=60
while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE_ARG="$2"; shift 2;; --until) UNTIL_ARG="$2"; shift 2;; --limit) LIMIT="$2"; shift 2;;
    -h|--help) sed -n '2,9p' "$0"; exit 0;; *) echo "unknown flag $1" >&2; exit 2;;
  esac
done
utc_date() { if date -u -d "$1" +%F >/dev/null 2>&1; then date -u -d "$1" +%F; else date -u -v"$2" +%F; fi; }
UNTIL="${UNTIL_ARG:-$(date -u +%F)}"
case "$SINCE_ARG" in *d) d="${SINCE_ARG%d}"; SINCE="$(utc_date "$UNTIL -$d days" "-${d}d")";; *) SINCE="$SINCE_ARG";; esac

echo "# PR signals: $SINCE to $UNTIL"
echo
if ! command -v gh >/dev/null 2>&1; then echo "> gh not installed. Pass B reads PRs with a GitHub tool instead."; exit 0; fi
if ! gh auth status >/dev/null 2>&1; then echo "> gh not signed in. Pass B reads PRs with a GitHub tool instead."; exit 0; fi
if ! command -v jq >/dev/null 2>&1; then echo "> jq not installed; needed to tally. Pass B reads PRs with a GitHub tool instead."; exit 0; fi

repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fields=number,title,state,isDraft,createdAt,mergedAt,closedAt,updatedAt,author,headRefName,headRefOid,reviewDecision,url
prs=$(gh pr list --repo "$repo" --state all --limit 500 --search "updated:>=$SINCE" --json "$fields")

echo "## Volume"
echo "- Opened in window: $(jq --arg s "$SINCE" '[.[] | select(.createdAt >= $s)] | length' <<<"$prs")"
echo "- Merged in window: $(jq --arg s "$SINCE" '[.[] | select(.mergedAt != null and .mergedAt >= $s)] | length' <<<"$prs")"
echo "- Closed without merge in window: $(jq --arg s "$SINCE" '[.[] | select(.state=="CLOSED" and .closedAt >= $s)] | length' <<<"$prs")"
echo "- Open now: $(jq '[.[] | select(.state=="OPEN")] | length' <<<"$prs") (drafts: $(jq '[.[] | select(.state=="OPEN" and .isDraft)] | length' <<<"$prs"))"
echo "- Authors (opened in window):"
jq -r --arg s "$SINCE" '[.[] | select(.createdAt >= $s) | .author.login] | group_by(.) | map({a: .[0], n: length}) | sort_by(-.n) | .[] | "  - \(.a): \(.n)"' <<<"$prs"
echo

echo "## Open PRs older than 14 days"
jq -r --arg cutoff "$(utc_date "$UNTIL -14 days" "-14d")" '.[] | select(.state=="OPEN" and .createdAt < $cutoff) | "  - #\(.number) \(.title) (opened \(.createdAt[:10]), \(.headRefName))"' <<<"$prs"
echo "- Count: $(jq --arg cutoff "$(utc_date "$UNTIL -14 days" "-14d")" '[.[] | select(.state=="OPEN" and .createdAt < $cutoff)] | length' <<<"$prs")"
echo

echo "## Time to merge (merged in window)"
jq -r --arg s "$SINCE" '
  [.[] | select(.mergedAt != null and .mergedAt >= $s) | ((.mergedAt | fromdateiso8601) - (.createdAt | fromdateiso8601)) / 3600] | sort |
  if length == 0 then "- none" else
    "- Median hours: \(.[length/2|floor] | floor), fastest \(.[0] | floor), slowest \(.[-1] | floor), n=\(length)" end' <<<"$prs"
echo

echo "## Per PR: review comments, replies, failing checks (newest $LIMIT in window)"
echo "- Reviewer logins of interest: ${RETRO_REVIEWER_LOGINS:-<none set in retro.env>}"
echo
echo "| PR | state | review comments | by reviewers of interest | replies | checks failed (latest head) |"
echo "|---|---|---|---|---|---|"
reviewers=$(printf '%s' "${RETRO_REVIEWER_LOGINS:-}" | tr ', ' '\n\n' | grep . | jq -R . | jq -s .)
jq -r --arg s "$SINCE" '.[] | select(.updatedAt >= $s) | "\(.number) \(.state) \(.headRefOid)"' <<<"$prs" | head -n "$LIMIT" | while read -r num state sha; do
  comments=$(gh api "repos/$repo/pulls/$num/comments?per_page=100" 2>/dev/null || echo '[]')
  total=$(jq length <<<"$comments")
  byrev=$(jq --argjson r "$reviewers" '[.[] | select(.user.login as $l | $r | index($l))] | length' <<<"$comments")
  replies=$(jq '[.[] | select(.in_reply_to_id != null)] | length' <<<"$comments")
  failed=$(gh api "repos/$repo/commits/$sha/check-runs?per_page=100" --jq '[.check_runs[] | select(.conclusion=="failure") | .name] | unique | join(", ")' 2>/dev/null || echo "?")
  echo "| #$num | $state | $total | $byrev | $replies | ${failed:-none} |"
done
echo
echo "- 'Replies' is a floor for 'answered': a fix commit or a resolve with a reason also counts. Pass B reads the threads."
