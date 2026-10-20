#!/usr/bin/env bash
# Pass A numbers from the commit history, over a window, as markdown.
#
#   bash scripts/git-signals.sh [--since 14d|YYYY-MM-DD] [--until YYYY-MM-DD] [--base main]
#
# Reads path filters from .agents/retro.env (RETRO_SRC_PATHS, RETRO_TEST_PATHS,
# RETRO_MIGRATION_PATHS, RETRO_I18N_PATHS, RETRO_RULE_FILES, RETRO_BASE_BRANCH).
# Read-only. Needs enough history to cover the window: on a shallow clone,
# `git fetch --deepen=<n>` or `--shallow-since=<date>` first, and the script
# says so when it notices.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
if [ -f .agents/retro.env ]; then
  # shellcheck disable=SC1091
  set -a; . .agents/retro.env; set +a
fi

SINCE_ARG="14d"; UNTIL_ARG=""; BASE="${RETRO_BASE_BRANCH:-main}"
while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE_ARG="$2"; shift 2;;
    --until) UNTIL_ARG="$2"; shift 2;;
    --base) BASE="$2"; shift 2;;
    -h|--help) sed -n '2,12p' "$0"; exit 0;;
    *) echo "unknown flag $1" >&2; exit 2;;
  esac
done

utc_date() { # utc_date <GNU -d expr | BSD -v expr> -> YYYY-MM-DD
  if date -u -d "$1" +%F >/dev/null 2>&1; then date -u -d "$1" +%F; else date -u -v"$2" +%F; fi
}
if [ -n "$UNTIL_ARG" ]; then UNTIL="$UNTIL_ARG"; else UNTIL="$(date -u +%F)"; fi
case "$SINCE_ARG" in
  *d) days="${SINCE_ARG%d}"; SINCE="$(utc_date "$UNTIL -$days days" "-${days}d")";;
  *) SINCE="$SINCE_ARG";;
esac
UNTIL_END="${UNTIL}T23:59:59"
RANGE=(--since="$SINCE" --until="$UNTIL_END")

SRC_PATHS="${RETRO_SRC_PATHS:-src}"
TEST_PATHS="${RETRO_TEST_PATHS:-tests test}"
MIG_PATHS="${RETRO_MIGRATION_PATHS:-}"
I18N_PATHS="${RETRO_I18N_PATHS:-}"
RULE_FILES="${RETRO_RULE_FILES:-CLAUDE.md AGENTS.md}"

existing() { for p in $1; do [ -e "$p" ] && printf '%s\n' "$p"; done; }
count_commits_touching() { # paths...
  local paths; paths=$(existing "$1"); [ -z "$paths" ] && { echo 0; return; }
  # shellcheck disable=SC2086
  git log --no-merges "${RANGE[@]}" --format=%H -- $paths | wc -l | tr -d ' '
}

echo "# Git signals: $SINCE to $UNTIL (base: $BASE)"
echo
if [ -f "$(git rev-parse --git-dir)/shallow" ]; then
  oldest="$(git log --reverse --format=%cs | head -1)"
  if [[ "$oldest" > "$SINCE" ]]; then
    echo "> Shallow clone: history starts $oldest, after the window start $SINCE. Numbers below are incomplete. Deepen first: git fetch --shallow-since=$SINCE origin"
  else
    echo "> Shallow clone, but history starts $oldest, before the window."
  fi
  echo
fi

total=$(git log --no-merges "${RANGE[@]}" --format=%H | wc -l | tr -d ' ')
merges=$(git log --merges "${RANGE[@]}" --format=%H | wc -l | tr -d ' ')
echo "## Volume"
echo "- Non-merge commits: $total"
echo "- Merge commits: $merges"
echo "- Authors (non-merge commits):"
git log --no-merges "${RANGE[@]}" --format=%an | sort | uniq -c | sort -rn | awk '{c=$1; $1=""; sub(/^ /,""); printf "  - %s: %d\n", $0, c}' | head -15
echo

echo "## Catch-up merges (base merged into a feature branch)"
catchups=$(git log --merges "${RANGE[@]}" --format='%h %cs %s' | grep -Ei "merge (remote-tracking )?branch '(origin/)?(${BASE}|main|master)'( into| of)?" || true)
echo "- Count: $(printf '%s' "$catchups" | grep -c . || true)"
printf '%s\n' "$catchups" | grep . | head -25 | sed 's/^/  - /'
[ -z "$catchups" ] && echo "  - none"
echo

echo "## Surfaces reopened 3+ times (files under: $SRC_PATHS)"
src_existing=$(existing "$SRC_PATHS")
if [ -n "$src_existing" ]; then
  # shellcheck disable=SC2086
  git log --no-merges "${RANGE[@]}" --name-only --format='' -- $src_existing \
    | grep . | sort | uniq -c | sort -rn | awk '$1>=3 {printf "  - %s: %d commits\n", $2, $1}' | head -20 > /tmp/retro-reopened.$$
  if [ -s /tmp/retro-reopened.$$ ]; then cat /tmp/retro-reopened.$$; echo "- (Read the commits for each before calling it rework; see pass A.)"; else echo "  - none"; fi
  rm -f /tmp/retro-reopened.$$
else
  echo "- none of $SRC_PATHS exists; set RETRO_SRC_PATHS"
fi
echo

echo "## Fix-on-fix chains"
fixshas=$(git log --no-merges "${RANGE[@]}" --format='%H' -i -E --grep='^(fix|hotfix|revert|bugfix)\b' || true)
fixcount=$(printf '%s' "$fixshas" | grep -c . || true)
echo "- Commits whose subject starts with fix/hotfix/revert: $fixcount"
if [ "$fixcount" -gt 1 ]; then
  printf '%s\n' "$fixshas" | while read -r sha; do [ -n "$sha" ] && git show --name-only --format='' "$sha"; done \
    | grep . | sort | uniq -c | sort -rn | awk '$1>=2 {printf "  - %s: touched by %d fix commits\n", $2, $1}' | head -15 > /tmp/retro-fixchain.$$
  if [ -s /tmp/retro-fixchain.$$ ]; then cat /tmp/retro-fixchain.$$; else echo "  - no file touched by two fix commits"; fi
  rm -f /tmp/retro-fixchain.$$
fi
echo

echo "## Commits by area"
echo "- Touching tests ($TEST_PATHS): $(count_commits_touching "$TEST_PATHS")"
[ -n "$MIG_PATHS" ] && echo "- Touching migrations ($MIG_PATHS): $(count_commits_touching "$MIG_PATHS")"
[ -n "$I18N_PATHS" ] && echo "- Touching translations ($I18N_PATHS): $(count_commits_touching "$I18N_PATHS")"
echo "- Touching rule files: $(count_commits_touching "$RULE_FILES")"
echo

echo "## Rule files: size at window start vs now (lines)"
start_rev=$(git rev-list -1 --before="$SINCE" HEAD 2>/dev/null || true)
total_then=0; total_now=0
for f in $RULE_FILES; do
  for path in $(compgen -G "$f" 2>/dev/null || echo "$f"); do
    [ -e "$path" ] || continue
    now=$(wc -l < "$path" | tr -d ' ')
    if [ -n "$start_rev" ]; then then_=$(git show "$start_rev:$path" 2>/dev/null | wc -l | tr -d ' '); else then_="?"; fi
    echo "- $path: $then_ -> $now"
    total_now=$((total_now + now))
    case "$then_" in ''|*[!0-9]*) ;; *) total_then=$((total_then + then_));; esac
  done
done
echo "- Total: $total_then -> $total_now"
[ -z "$start_rev" ] && echo "- (no commit before $SINCE in this clone; 'then' unknown)"
echo

echo "## Commit body quality (non-merge)"
thin=0
while read -r sha; do
  [ -z "$sha" ] && continue
  lines=$(git show -s --format=%b "$sha" | grep -vE '^(Co-Authored-By|Co-authored-by|Claude-Session|Signed-off-by|Change-Id|Reviewed-by):?' | grep -c . || true)
  [ "$lines" -lt 2 ] && thin=$((thin + 1))
done < <(git log --no-merges "${RANGE[@]}" --format=%H)
echo "- Commits with a body under two lines: $thin of $total"
echo

echo "## Repeated subjects (same normalised subject, 2+ commits)"
git log --no-merges "${RANGE[@]}" --format=%s | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9 ]+/ /g; s/ +/ /g; s/^ | $//g' \
  | sort | uniq -c | sort -rn | awk '$1>=2 {c=$1; $1=""; printf "  - %d x%s\n", c, $0}' | head -15 > /tmp/retro-subjects.$$
if [ -s /tmp/retro-subjects.$$ ]; then cat /tmp/retro-subjects.$$; else echo "  - none"; fi
rm -f /tmp/retro-subjects.$$
echo

echo "## Remote branches with commits in the window"
if git remote get-url origin >/dev/null 2>&1; then
  since_epoch=$(date -u -d "$SINCE" +%s 2>/dev/null || date -u -j -f %F "$SINCE" +%s)
  git for-each-ref --sort=-committerdate 'refs/remotes/origin' --format='%(committerdate:unix) %(committerdate:short) %(refname:short)' \
    | awk -v s="$since_epoch" '$1>=s {print "  - " $2 " " $3}' > /tmp/retro-branches.$$ || true
  echo "- Count: $(grep -c . /tmp/retro-branches.$$ || true) (compare to the PR list: a branch with no PR ran no checks)"
  head -40 /tmp/retro-branches.$$
  rm -f /tmp/retro-branches.$$
  echo "- (Only branches this clone has fetched are visible. \`git fetch --all\` first for the full set.)"
else
  echo "- no origin remote"
fi
