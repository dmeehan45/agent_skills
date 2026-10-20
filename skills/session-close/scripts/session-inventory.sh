#!/usr/bin/env bash
# Session inventory: everything a close-out needs to look at, printed in one
# pass so nothing is forgotten. Read-only. Prints to stdout; exits 0.
#
#   bash skills/session-close/scripts/session-inventory.sh [base-ref]
#
# base-ref defaults to origin/main. Run from anywhere inside the repo.
# The area globs near the bottom are a starting point; edit them to match
# the repo (where its migrations, translations, analytics and docs live).
set -uo pipefail

base="${1:-origin/main}"
root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not a git repo" >&2; exit 2; }
cd "$root"

branch="$(git branch --show-current)"
merge_base="$(git merge-base "$base" HEAD 2>/dev/null || echo '')"

hr() { printf '\n== %s ==\n' "$1"; }

hr "Branch"
echo "branch:      $branch"
echo "base:        $base"
echo "merge-base:  ${merge_base:-<none: fetch $base first>}"
echo "head:        $(git rev-parse --short HEAD)"

hr "Working tree (must be clean before you stop)"
if [ -z "$(git status --porcelain)" ]; then echo "clean"; else git status --short; fi

hr "Commits on this branch not on $base"
if [ -n "$merge_base" ]; then
  git log --oneline "$base..HEAD"
  echo "count: $(git rev-list --count "$base..HEAD")"
else
  echo "(cannot compute; fetch $base)"
fi

hr "Other local branches ahead of $base (work from this session on another branch?)"
for b in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  [ "$b" = "$branch" ] && continue
  n="$(git rev-list --count "$base..$b" 2>/dev/null || echo 0)"
  [ "$n" != "0" ] && echo "$b: $n commit(s) ahead"
done
echo "(end)"

if [ -n "$merge_base" ]; then
  hr "Files changed vs $base"
  git diff --stat "$merge_base" HEAD | tail -n 1
  git diff --name-status "$merge_base" HEAD

  hr "Deferral markers ADDED in this branch (each is a follow-up or a lie)"
  # Lines this branch added, in code and config, that promise later work or
  # describe something as unshipped. Translations, content, docs and data are
  # excluded (they say "follow-up" about the product, not about the work).
  # TODO is matched case-sensitively because "todo" is a Spanish word.
  git diff "$merge_base" HEAD -- . \
      ':(exclude)**/i18n/**' ':(exclude)**/locales/**' ':(exclude)**/content/**' \
      ':(exclude)docs' ':(exclude)*.json' ':(exclude)*.md' \
    | grep -E '^\+' | grep -vE '^\+\+\+' \
    | grep -nE 'TODO|FIXME|XXX|HACK|[Nn]ot (yet )?(shipped|built|wired|implemented)|[Ll]ater phase|[Hh]as not shipped|[Ff]ollow-?up (session|PR)|[Dd]eferred|[Tt]emporar(y|ily)' \
    | sed 's/^+//' | cut -c1-160 | head -n 60
  echo "(end)"

  hr "Test files added or changed"
  git diff --name-only "$merge_base" HEAD | grep -iE '(^|/)(test|tests|__tests__|spec)(/|\.)|\.(test|spec)\.' || true
  echo "(end)"

  hr "Schema / migration files touched"
  git diff --name-only "$merge_base" HEAD | grep -iE 'migrat|schema|prisma|\.sql$' || true
  echo "(end)"

  hr "Translation / copy files touched"
  git diff --name-only "$merge_base" HEAD | grep -iE 'i18n|locale|translation|/content/' || true
  echo "(end)"

  hr "Analytics / telemetry / API files touched"
  git diff --name-only "$merge_base" HEAD | grep -iE 'analytic|telemetry|posthog|segment|sentry|(^|/)api/' || true
  echo "(end)"

  hr "Docs, rules and skills touched (do they still describe what shipped?)"
  git diff --name-only "$merge_base" HEAD | grep -iE '\.md$|(^|/)\.claude/|(^|/)\.cursor/|AGENTS|CLAUDE|README' || true
  echo "(end)"
fi

hr "Scratch files that may have been left behind"
git ls-files --others --exclude-standard | head -n 40
echo "(end)"

hr "Next"
cat <<'TXT'
1. Every PR this session opened: open, targets the default branch, green, preview link in the body.
2. Every deferral marker above: do it now, file it in the handoff, or remove it with a reason.
3. Run the repo's own gate command (the one CI runs), locally.
4. Fill references/wrap-up-template.md.
TXT
