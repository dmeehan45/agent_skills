#!/usr/bin/env bash
# scan-release-surface.sh — mechanical pre-publication sweep for a repo moving
# from private to public.
#
# Read-only. Never modifies the repository under audit. Never prints a matched
# secret value: every content finding is reported as rule + location + a short
# fingerprint, so duplicates can be correlated across history without the value
# ever entering a transcript, a log, or a report.
#
# Usage:
#   scan-release-surface.sh [--repo DIR] [--out DIR] [--skip-history]
#                           [--max-blobs N] [--max-blob-bytes N] [--quiet]
#
#   --repo            repo to scan (default: current directory)
#   --out             where findings are written (default: a fresh mktemp dir)
#   --skip-history    scan the working tree only, not reachable history
#   --max-blobs       cap on distinct historical blobs scanned (default 20000)
#   --max-blob-bytes  skip blobs larger than this in the fallback scanner
#                     (default 2000000)
#
# Exit codes: 0 scan completed (findings may exist), 1 usage/environment error.
#
# The scan is a lead generator, not a verdict. Every finding needs human review:
# these patterns produce false positives (test fixtures, documentation examples,
# public sample keys) and false negatives (custom credential formats, encoded or
# split values, secrets in binary assets).

set -uo pipefail

REPO="$PWD"
OUT=""
SKIP_HISTORY=0
MAX_BLOBS=20000
MAX_BLOB_BYTES=2000000
QUIET=0

die() { printf 'error: %s\n' "$1" >&2; exit 1; }
say() { [ "$QUIET" -eq 1 ] || printf '%s\n' "$1" >&2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    --skip-history) SKIP_HISTORY=1; shift ;;
    --max-blobs) MAX_BLOBS="${2:-}"; shift 2 ;;
    --max-blob-bytes) MAX_BLOB_BYTES="${2:-}"; shift 2 ;;
    --quiet) QUIET=1; shift ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

command -v git >/dev/null 2>&1 || die "git not found on PATH"
[ -d "$REPO" ] || die "not a directory: $REPO"
REPO="$(cd "$REPO" && pwd)"
git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || die "not a git repository: $REPO"

if [ -z "$OUT" ]; then
  OUT="$(mktemp -d 2>/dev/null)" || die "could not create temp output directory"
else
  mkdir -p "$OUT" || die "could not create output directory: $OUT"
  OUT="$(cd "$OUT" && pwd)"
fi
case "$OUT" in
  "$REPO"|"$REPO"/*)
    say "WARNING: output directory is inside the repo under audit."
    say "         Add it to .gitignore or it will be committed into the public snapshot." ;;
esac
mkdir -p "$OUT/inventory"

# Prefer ripgrep: faster, and it understands the inline (?i) flag used below.
if command -v rg >/dev/null 2>&1; then GREP=rg; else GREP=grep; fi

# POSIX ERE has no inline (?i) flag, so the grep paths strip it and pass -i
# instead. Done inline at each call site rather than in a function, because a
# function returning via $(...) runs in a subshell and cannot set the flag.
#   case "$pattern" in "(?i)"*) ere="${pattern#(?i)}"; iflag=-i ;; ... esac

nlines() { [ -f "$1" ] && awk 'END {print NR+0}' "$1" || echo 0; }

# Fingerprint a matched value without disclosing it. Correlates repeat hits of
# the same credential across branches and history.
if command -v sha256sum >/dev/null 2>&1; then
  fingerprint() { printf '%s' "$1" | sha256sum | cut -c1-8; }
elif command -v shasum >/dev/null 2>&1; then
  fingerprint() { printf '%s' "$1" | shasum -a 256 | cut -c1-8; }
else
  fingerprint() { printf 'nohash'; }
fi

# ---------------------------------------------------------------------------
# Detection rules. Format: NAME<TAB>TIER<TAB>ERE
# Tiers: CREDENTIAL (treat as compromised if real), IDENTITY (personal or
# internal identifiers), CONTEXT (confidentiality signals needing judgment).
# ---------------------------------------------------------------------------
read -r -d '' RULES <<'RULES_EOF'
aws-access-key-id	CREDENTIAL	(A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}
aws-secret-hint	CREDENTIAL	(?i)aws.{0,20}(secret|private).{0,20}['"][0-9a-zA-Z/+]{40}['"]
github-token	CREDENTIAL	(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})
gitlab-token	CREDENTIAL	glpat-[A-Za-z0-9_\-]{20,}
slack-token	CREDENTIAL	xox[abprs]-[A-Za-z0-9-]{10,}
slack-webhook	CREDENTIAL	https://hooks\.slack\.com/services/[A-Za-z0-9/]{20,}
discord-webhook	CREDENTIAL	https://discord(app)?\.com/api/webhooks/[0-9]{10,}/[A-Za-z0-9_\-]{20,}
google-api-key	CREDENTIAL	AIza[0-9A-Za-z_\-]{35}
gcp-service-account	CREDENTIAL	"type":[[:space:]]*"service_account"
stripe-live-key	CREDENTIAL	(sk|rk)_live_[0-9a-zA-Z]{20,}
openai-key	CREDENTIAL	sk-(proj-)?[A-Za-z0-9_\-]{32,}
anthropic-key	CREDENTIAL	sk-ant-[A-Za-z0-9_\-]{20,}
sendgrid-key	CREDENTIAL	SG\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}
twilio-sid	CREDENTIAL	AC[0-9a-fA-F]{32}
mailgun-key	CREDENTIAL	key-[0-9a-zA-Z]{32}
npm-token	CREDENTIAL	npm_[A-Za-z0-9]{36}
pypi-token	CREDENTIAL	pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_\-]{20,}
private-key-block	CREDENTIAL	-----BEGIN ([A-Z ]+ )?PRIVATE KEY( BLOCK)?-----
ssh-private-hint	CREDENTIAL	-----BEGIN OPENSSH PRIVATE KEY-----
pgp-private-block	CREDENTIAL	-----BEGIN PGP PRIVATE KEY BLOCK-----
jwt-token	CREDENTIAL	eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}
db-url-with-password	CREDENTIAL	(postgres|postgresql|mysql|mongodb\+srv|mongodb|redis|rediss|amqp|amqps|clickhouse)://[^:@/[:space:]'"]+:[^@/[:space:]'"]+@
basic-auth-in-url	CREDENTIAL	https?://[A-Za-z0-9._%+-]+:[^@/[:space:]'"]{4,}@
generic-secret-assignment	CREDENTIAL	(?i)(api[_-]?key|apikey|secret|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd|private[_-]?key|session[_-]?key|encryption[_-]?key)['"]?[[:space:]]*[:=][[:space:]]*['"][^'"${}[:space:]]{8,}['"]
authorization-header	CREDENTIAL	(?i)authorization['"]?[[:space:]]*[:=][[:space:]]*['"]?(bearer|basic)[[:space:]]+[A-Za-z0-9_\-\.=+/]{16,}
email-address	IDENTITY	[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
phone-number-na	IDENTITY	(\+1[ .-]?)?\(?[2-9][0-9]{2}\)?[ .-][0-9]{3}[ .-][0-9]{4}
us-ssn-shaped	IDENTITY	[0-9]{3}-[0-9]{2}-[0-9]{4}
credit-card-shaped	IDENTITY	[0-9]{4}[ -][0-9]{4}[ -][0-9]{4}[ -][0-9]{4}
aws-account-arn	IDENTITY	arn:aws[a-z-]*:[a-z0-9-]+:[a-z0-9-]*:[0-9]{12}:
internal-hostname	IDENTITY	(?i)https?://[A-Za-z0-9.-]*\.(internal|intranet|corp|local|lan|test|vpn)\b
private-workspace-url	IDENTITY	(?i)https?://[A-Za-z0-9.-]+\.(slack\.com/archives|atlassian\.net|notion\.so|linear\.app|sharepoint\.com|zendesk\.com)/
ip-address-private	IDENTITY	\b(10\.[0-9]{1,3}|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.[0-9]{1,3}\.[0-9]{1,3}\b
confidentiality-marker	CONTEXT	(?i)\b(confidential|proprietary and confidential|do not distribute|internal use only|nda|non-disclosure|trade secret)\b
commercial-context	CONTEXT	(?i)\b(pricing tier|contract value|invoice|salary|compensation band|arr|mrr|churn rate|roadmap q[1-4])\b
customer-context	CONTEXT	(?i)\b(customer list|client list|support transcript|prod(uction)? dump|real user data|pii)\b
suspicious-todo	CONTEXT	(?i)(TODO|FIXME|HACK|XXX).{0,80}(secur|password|secret|token|auth|hack|temporar|remove before|don'?t ship)
RULES_EOF

# High-signal paths. Their presence is the finding; contents are not printed.
read -r -d '' PATH_RULES <<'PATH_EOF'
env-file	(^|/)\.env($|\.[^/]*$)
env-file-nested	(^|/)\.env\.(local|development|production|staging|prod|dev|test)$
private-key-file	\.(pem|key|p12|pfx|jks|keystore|ppk|asc|gpg)$
ssh-material	(^|/)(id_rsa|id_dsa|id_ecdsa|id_ed25519|authorized_keys|known_hosts)($|\.)
cloud-credentials	(^|/)\.(aws|azure|gcloud|kube|docker)/|(^|/)kubeconfig$|(^|/)credentials$|(^|/)service-account.*\.json$
package-registry-auth	(^|/)\.(npmrc|pypirc|netrc|gem/credentials|cargo/credentials)
shell-history	(^|/)\.(bash_history|zsh_history|psql_history|python_history|mysql_history)$
infra-state	(^|/)\.terraform/|\.tfstate(\.backup)?$|(^|/)\.pulumi/|(^|/)\.serverless/
database-artifact	\.(sqlite3?|db|mdb|dump|bak)$|\.sql(\.gz)?$
data-export	\.(csv|tsv|xlsx|xls|parquet|jsonl|ndjson)$
log-file	\.log$|(^|/)logs?/
capture-file	\.(har|pcap|pcapng|mitm)$
media-and-docs	\.(png|jpe?g|gif|webp|bmp|tiff|pdf|docx?|pptx?|mp4|mov|webm|wav|mp3)$
notebook	\.ipynb$
build-output	(^|/)(dist|build|out|target|coverage|\.next|\.nuxt|\.output|\.parcel-cache|\.turbo|\.cache)/
dependency-dir	(^|/)(node_modules|vendor|\.venv|venv|__pycache__|\.tox|Pods|bower_components)/
editor-residue	(^|/)\.(idea|vscode|fleet)/|(^|/)\.DS_Store$|(^|/)Thumbs\.db$|~$|\.swp$|\.orig$|\.rej$
backup-copy	(^|/)[^/]*\.(bak|backup|old|copy|save|tmp)$|(^|/)[^/]*[ ._-](copy|old|backup|final|FINAL|v[0-9])\.[a-z0-9]+$
agent-residue	(^|/)\.(claude|cursor|aider|continue|codeium|windsurf)/|(^|/)(AGENTS|CLAUDE|CURSOR)\.md$|(^|/)\.aider\.
internal-planning	(?i)(^|/)(notes?|scratch|internal|private|wip|drafts?|meeting[_-]?notes|standup|retro|planning|roadmap|handoff|transcripts?)/
PATH_EOF

# ---------------------------------------------------------------------------
# Section 1 — repository inventory
# ---------------------------------------------------------------------------
say "[1/5] inventorying repository surfaces"
INV="$OUT/inventory"

git -C "$REPO" ls-files                                   > "$INV/tracked-files.txt" 2>/dev/null
git -C "$REPO" ls-files -o --exclude-standard             > "$INV/untracked-files.txt" 2>/dev/null
git -C "$REPO" ls-files -o -i --exclude-standard          > "$INV/ignored-files.txt" 2>/dev/null
git -C "$REPO" branch -a --format='%(refname) %(committerdate:short) %(authorname)' > "$INV/branches.txt" 2>/dev/null
git -C "$REPO" tag -l                                     > "$INV/tags.txt" 2>/dev/null
git -C "$REPO" remote -v                                  > "$INV/remotes.txt" 2>/dev/null
git -C "$REPO" log --all --format='%an <%ae>' 2>/dev/null | sort -u > "$INV/commit-authors.txt"
git -C "$REPO" log --all --format='%s' 2>/dev/null         > "$INV/commit-subjects.txt"
git -C "$REPO" count-objects -vH                          > "$INV/object-stats.txt" 2>/dev/null
[ -f "$REPO/.gitmodules" ] && cp "$REPO/.gitmodules" "$INV/gitmodules.txt"
git -C "$REPO" lfs ls-files                               > "$INV/lfs-files.txt" 2>/dev/null || : > "$INV/lfs-files.txt"

# Largest tracked blobs — oversized files are both a fork-friction problem and a
# common carrier of exported data.
git -C "$REPO" ls-tree -r -l --full-name HEAD 2>/dev/null \
  | awk '$4 ~ /^[0-9]+$/ {print $4"\t"$5}' | sort -rn | head -40 > "$INV/largest-tracked-files.txt"

# ---------------------------------------------------------------------------
# Section 2 — path-based findings
# ---------------------------------------------------------------------------
say "[2/5] matching high-signal paths"
: > "$OUT/path-findings.tsv"
printf 'rule\tscope\tpath\n' >> "$OUT/path-findings.tsv"

scan_paths() {
  local listfile="$1" scope="$2" rule pattern
  [ -s "$listfile" ] || return 0
  while IFS=$'\t' read -r rule pattern; do
    [ -z "${rule:-}" ] && continue
    while IFS= read -r p; do
      [ -z "$p" ] && continue
      printf '%s\t%s\t%s\n' "$rule" "$scope" "$p" >> "$OUT/path-findings.tsv"
    done < <(grep -aiE "$pattern" "$listfile" 2>/dev/null)
  done <<< "$PATH_RULES"
}

scan_paths "$INV/tracked-files.txt" tracked
scan_paths "$INV/untracked-files.txt" untracked
scan_paths "$INV/ignored-files.txt" ignored

# Historical paths — files deleted from HEAD but still reachable in history.
if [ "$SKIP_HISTORY" -eq 0 ]; then
  git -C "$REPO" log --all --pretty=format: --name-only --diff-filter=A 2>/dev/null \
    | sort -u | sed '/^$/d' > "$INV/historical-paths.txt"
  # Paths that existed once but are gone from HEAD deserve the closest look.
  comm -23 "$INV/historical-paths.txt" <(sort -u "$INV/tracked-files.txt") \
    > "$INV/paths-deleted-from-head.txt" 2>/dev/null || : > "$INV/paths-deleted-from-head.txt"
  scan_paths "$INV/paths-deleted-from-head.txt" history-deleted
fi

# ---------------------------------------------------------------------------
# Section 3 — content findings in the working tree
# ---------------------------------------------------------------------------
say "[3/5] scanning working tree contents"
: > "$OUT/content-findings.tsv"
printf 'rule\ttier\tscope\tlocation\tline\tfingerprint\n' >> "$OUT/content-findings.tsv"

emit_matches() {
  # stdin: "path:line:match" triples. Emits redacted rows.
  local rule="$1" tier="$2" scope="$3" loc line match fp
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    loc="${hit%%:*}"; hit="${hit#*:}"
    line="${hit%%:*}"; match="${hit#*:}"
    fp="$(fingerprint "$match")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$rule" "$tier" "$scope" "$loc" "$line" "$fp" \
      >> "$OUT/content-findings.tsv"
  done
}

scan_tree_contents() {
  local rule tier pattern
  while IFS=$'\t' read -r rule tier pattern; do
    [ -z "${rule:-}" ] && continue
    if [ "$GREP" = rg ]; then
      rg --no-heading --line-number --no-messages --text --only-matching \
         --max-columns 400 --hidden --no-ignore \
         --glob '!.git/' --glob '!node_modules/' --glob '!vendor/' \
         -e "$pattern" "$REPO" 2>/dev/null \
        | sed "s|^$REPO/||" | emit_matches "$rule" "$tier" working-tree
    else
      case "$pattern" in
        "(?i)"*) ere="${pattern#(?i)}"; iflag=-i ;;
        *) ere="$pattern"; iflag= ;;
      esac
      grep -rnoaE $iflag --binary-files=without-match \
        --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor \
        -e "$ere" "$REPO" 2>/dev/null \
        | sed "s|^$REPO/||" | emit_matches "$rule" "$tier" working-tree
    fi
  done <<< "$RULES"
}
scan_tree_contents

# ---------------------------------------------------------------------------
# Section 4 — content findings in reachable history
# ---------------------------------------------------------------------------
if [ "$SKIP_HISTORY" -eq 1 ]; then
  say "[4/5] history scan skipped (--skip-history)"
  echo "skipped" > "$OUT/inventory/history-scan-status.txt"
elif command -v gitleaks >/dev/null 2>&1; then
  # gitleaks walks history natively and redacts by default. Preferred when present.
  say "[4/5] scanning history with gitleaks"
  gitleaks detect --source "$REPO" --no-banner --redact \
    --report-format json --report-path "$OUT/gitleaks-report.json" \
    --exit-code 0 >"$OUT/inventory/gitleaks-stdout.txt" 2>&1
  echo "gitleaks" > "$OUT/inventory/history-scan-status.txt"
  if command -v jq >/dev/null 2>&1 && [ -s "$OUT/gitleaks-report.json" ]; then
    jq -r '.[] | [.RuleID, "CREDENTIAL", "history-gitleaks",
                  (.File // "?"), ((.StartLine // 0)|tostring),
                  ((.Fingerprint // "-")|tostring)] | @tsv' \
      "$OUT/gitleaks-report.json" >> "$OUT/content-findings.tsv" 2>/dev/null
  fi
else
  say "[4/5] scanning history (fallback blob walk; install gitleaks for better coverage)"
  echo "fallback-blob-walk" > "$OUT/inventory/history-scan-status.txt"
  # Distinct blobs reachable from any ref, newest refs first. Deduplicated by
  # SHA so a file unchanged across 500 commits is scanned once.
  # rev-list --objects emits "<sha> <path>", and paths contain spaces. Take
  # everything after the first field as the path, not just field 2.
  git -C "$REPO" rev-list --objects --all 2>/dev/null \
    | awk 'NF>1 {sha=$1; $1=""; sub(/^[ \t]+/, ""); print sha"\t"$0}' \
    | sort -u -k1,1 > "$INV/history-blobs.txt"
  blob_count=0
  while IFS=$'\t' read -r sha path; do
    [ -z "${sha:-}" ] && continue
    blob_count=$((blob_count + 1))
    [ "$blob_count" -gt "$MAX_BLOBS" ] && { say "  blob cap reached ($MAX_BLOBS); coverage incomplete"; break; }
    meta="$(git -C "$REPO" cat-file -s "$sha" 2>/dev/null)" || continue
    [ -z "$meta" ] && continue
    [ "$meta" -gt "$MAX_BLOB_BYTES" ] 2>/dev/null && continue
    while IFS=$'\t' read -r rule tier pattern; do
      [ -z "${rule:-}" ] && continue
      # Only CREDENTIAL rules run over full history: IDENTITY and CONTEXT rules
      # are far too noisy across every historical revision to be actionable.
      [ "$tier" = CREDENTIAL ] || continue
      case "$pattern" in
        "(?i)"*) ere="${pattern#(?i)}"; iflag=-i ;;
        *) ere="$pattern"; iflag= ;;
      esac
      hits="$(git -C "$REPO" cat-file blob "$sha" 2>/dev/null \
              | grep -aonE $iflag "$ere" 2>/dev/null | head -5)" || true
      [ -z "$hits" ] && continue
      while IFS= read -r h; do
        [ -z "$h" ] && continue
        ln="${h%%:*}"; mt="${h#*:}"
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
          "$rule" "$tier" "history-blob" "${path:-<unnamed>}@${sha:0:10}" "$ln" "$(fingerprint "$mt")" \
          >> "$OUT/content-findings.tsv"
      done <<< "$hits"
    done <<< "$RULES"
  done < "$INV/history-blobs.txt"
  echo "$blob_count" > "$INV/history-blobs-scanned.txt"
fi

# ---------------------------------------------------------------------------
# Section 5 — summary
# ---------------------------------------------------------------------------
say "[5/5] writing summary"

count_rows() { [ -f "$1" ] || { echo 0; return; }; awk 'END {print (NR>0 ? NR-1 : 0)}' "$1"; }
n_path=$(count_rows "$OUT/path-findings.tsv")
n_content=$(count_rows "$OUT/content-findings.tsv")
n_cred=$(awk -F'\t' 'NR>1 && $2=="CREDENTIAL" {c++} END {print c+0}' "$OUT/content-findings.tsv" 2>/dev/null)

{
  echo "# Release-surface scan"
  echo
  echo "Repository: \`$REPO\`"
  echo "History scan: $(cat "$INV/history-scan-status.txt" 2>/dev/null || echo unknown)"
  echo
  echo "Values are never printed. Each content row carries a fingerprint (first 8"
  echo "hex of the match's SHA-256) so the same value can be tracked across files,"
  echo "branches, and history without disclosure."
  echo
  echo "## Counts"
  echo
  echo "| Signal | Count |"
  echo "| --- | --- |"
  echo "| Path-based findings | $n_path |"
  echo "| Content findings (all tiers) | $n_content |"
  echo "| Content findings, CREDENTIAL tier | $n_cred |"
  echo "| Tracked files | $(nlines "$INV/tracked-files.txt") |"
  echo "| Untracked files | $(nlines "$INV/untracked-files.txt") |"
  echo "| Ignored files present on disk | $(nlines "$INV/ignored-files.txt") |"
  echo "| Paths in history but absent from HEAD | $(nlines "$INV/paths-deleted-from-head.txt") |"
  echo "| Branches | $(nlines "$INV/branches.txt") |"
  echo "| Tags | $(nlines "$INV/tags.txt") |"
  echo "| Distinct commit authors | $(nlines "$INV/commit-authors.txt") |"
  echo "| Git LFS objects | $(nlines "$INV/lfs-files.txt") |"
  echo
  echo "## Top rules fired (content)"
  echo
  awk -F'\t' 'NR>1 {print $2"\t"$1}' "$OUT/content-findings.tsv" 2>/dev/null \
    | sort | uniq -c | sort -rn | head -25 \
    | awk '{printf "- %s (%s) — %s hits\n", $3, $2, $1}'
  echo
  echo "## Top rules fired (paths)"
  echo
  awk -F'\t' 'NR>1 {print $2"\t"$1}' "$OUT/path-findings.tsv" 2>/dev/null \
    | sort | uniq -c | sort -rn | head -25 \
    | awk '{printf "- %s (%s) — %s paths\n", $3, $2, $1}'
  echo
  echo "## Files written"
  echo
  echo "- \`path-findings.tsv\` — rule, scope, path"
  echo "- \`content-findings.tsv\` — rule, tier, scope, location, line, fingerprint"
  echo "- \`inventory/\` — tracked/untracked/ignored files, branches, tags, authors,"
  echo "  commit subjects, LFS objects, submodules, largest blobs, deleted paths"
  [ -f "$OUT/gitleaks-report.json" ] && echo "- \`gitleaks-report.json\` — redacted gitleaks output"
  echo
  echo "## What this scan cannot see"
  echo
  echo "- Hosted surfaces: issues, pull requests, wikis, releases, Actions logs and"
  echo "  artifacts, project boards, discussions, forks, and repository settings."
  echo "- Content inside binary assets, images, PDFs, and embedded file metadata."
  echo "- Secrets that are encoded, split across lines, or in a bespoke format."
  echo "- Whether an included asset or dependency may be redistributed."
  echo "- Whether the work is the author's to publish at all."
} > "$OUT/summary.md"

say ""
say "Scan complete. Output: $OUT"
printf '%s\n' "$OUT"
