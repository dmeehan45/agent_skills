# Sensitive-material scan playbook

Contents:
1. Coverage model — what "the repo" actually means
2. Running the bundled scanner
3. Established scanners (gitleaks, TruffleHog)
4. Manual sweeps the scanner cannot do
5. Hosted surfaces (not in the clone)
6. Triage — separating real findings from noise
7. Credential remediation and rotation reporting
8. Third-party assets and redistribution rights

---

## 1. Coverage model

"Scan the repo" is ambiguous and the ambiguity is where leaks live. Six
distinct surfaces, each needing explicit coverage:

| Surface | Why it matters | How it is reached |
| --- | --- | --- |
| Tracked files at HEAD | The obvious one | `git ls-files` |
| Untracked files on disk | Often the real `.env`, dumps, notes | `git ls-files -o --exclude-standard` |
| Ignored files on disk | `.gitignore` hides them from tools, not from a copied directory | `git ls-files -o -i --exclude-standard` |
| Reachable history | Deleting a file from HEAD does not remove it from history | `git rev-list --objects --all` |
| Other refs | Old branches and tags carry material HEAD never had | `git branch -a`, `git tag -l` |
| LFS, submodules | Stored outside normal blobs | `git lfs ls-files`, `.gitmodules` |

A working-tree-only scan is the most common false clean bill of health.

Note the interaction between ignored files and release method: if the release
is a fresh-history export built by copying the directory, ignored files can be
copied along with it. If it is built with `git archive` or a clean clone, they
cannot. Know which method is planned before deciding how much the ignored-file
findings matter.

## 2. Running the bundled scanner

```bash
bash scripts/scan-release-surface.sh --repo /path/to/repo --out /tmp/release-audit
```

Options: `--skip-history` (working tree only — faster, much weaker),
`--max-blobs N` (cap on distinct historical blobs, default 20000),
`--max-blob-bytes N` (fallback scanner skips blobs above this, default 2MB),
`--quiet`.

Output:

- `summary.md` — counts, top rules fired, and an explicit list of what the scan
  could not see.
- `content-findings.tsv` — `rule, tier, scope, location, line, fingerprint`.
- `path-findings.tsv` — `rule, scope, path`.
- `inventory/` — tracked, untracked, ignored file lists; branches; tags;
  remotes; commit authors; commit subjects; LFS objects; submodules; largest
  tracked blobs; and `paths-deleted-from-head.txt`.

**Values are never printed.** Each content row carries the first 8 hex of the
match's SHA-256 instead. That fingerprint is genuinely useful: identical
fingerprints across files, branches, and history mean one credential with many
homes, which is one rotation, not five.

Three tiers:

- **CREDENTIAL** — if real, assume compromised. Scanned across full history.
- **IDENTITY** — personal or internal identifiers (emails, phone numbers,
  private hostnames, internal IPs, account ARNs, private workspace URLs).
- **CONTEXT** — confidentiality signals needing human judgment (NDA language,
  commercial terms, customer references, secret-adjacent TODOs).

IDENTITY and CONTEXT rules run over the working tree only. Across full history
they produce thousands of hits per repo — every revision of every file with a
contributor email in it — which drowns the findings that matter.

`inventory/paths-deleted-from-head.txt` deserves a direct read regardless of
what fired. Files someone deliberately removed are a curated list of what they
already considered too sensitive to keep.

## 3. Established scanners

Prefer a purpose-built scanner for history when one is available. The bundled
script uses `gitleaks` automatically if it is on PATH.

```bash
gitleaks detect --source . --no-banner --redact --report-format json \
  --report-path /tmp/gitleaks.json
```

`--redact` matters: it keeps values out of the report file, which is the same
discipline this skill requires everywhere.

TruffleHog adds live-credential verification, which answers the question that
actually drives urgency — is this key still valid?

```bash
trufflehog git file://. --results=verified,unknown --json > /tmp/trufflehog.json
```

A *verified* finding is an emergency: the credential works right now, and
rotation is needed whether or not the repo is ever published.

Neither tool's output is a verdict. Both miss custom formats and both flag
documentation examples. Review findings; do not paste them wholesale into a
report, because their raw output can contain values.

## 4. Manual sweeps

Targeted greps for things the pattern rules miss. Adapt the vocabulary to the
project — the useful search terms are the ones specific to this repo's world.

```bash
# Employer, client, and project code names — build this list from the repo's
# own vocabulary, commit authors, and the owner's answers.
git grep -In -iE 'acmecorp|initiative-atlas|projectname' -- . | head -50

# Same, across all history.
git log --all -p -S'acmecorp' --oneline | head -50

# Author identities: work email domains across history are an ownership signal
# as much as a privacy one.
git log --all --format='%an <%ae>' | sort | uniq -c | sort -rn

# Commit messages become public too, and get read more than people expect.
git log --all --format='%s%n%b' | grep -iE 'hack|temp|password|secret|client|internal|fix for <name>' | head -40

# Large blobs anywhere in history — data exports and media hide here, and they
# also make the repo unpleasant to clone.
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3>1000000 {print $3, $4}' | sort -rn | head -30
```

**Binary and document metadata.** Images carry EXIF (GPS, device, sometimes
author), PDFs and Office documents carry author names, organizations, revision
history, and comments. Screenshots are the worst offender in old project repos:
a UI screenshot routinely captures a real customer name, an internal URL, a
browser bookmark bar, or a Slack notification.

```bash
exiftool -r -q -q -common path/to/assets    # if available
pdfinfo file.pdf
```

Open every screenshot and look at it. There is no substitute.

**Notebooks** (`.ipynb`) store outputs alongside code — query results, dataframe
previews, printed credentials. Check the `outputs` arrays, not just the source
cells.

## 5. Hosted surfaces

None of these live in the clone, and all of them become public when the repo
does. The agent may inspect them with available GitHub tooling; whatever cannot
be checked goes into the final report as a manual owner task:

- **Issues and pull requests** — comments, logs, stack traces with real data,
  screenshots. The highest-risk surface after history.
- **Wiki** — a separate git repo, never covered by a scan of the main one.
- **Releases and release assets** — attached binaries, built artifacts.
- **Actions runs, logs, and artifacts** — logs may print environment values.
- **Project boards, discussions, forks** — forks retain what the original
  deleted, and cannot be un-forked.
- **Repository settings** — configured secrets, deploy keys, webhooks,
  integrations, collaborators, branch protections.
- **Existing forks and clones** — if a credential was ever committed, someone
  else may already hold a copy. Another reason rotation, not deletion, is the
  remedy.

## 6. Triage

Every automated hit gets one of four dispositions. Record which, and why:

| Disposition | Meaning | Action |
| --- | --- | --- |
| **Confirmed sensitive** | A real credential, real personal data, or real confidential material | Blocker; remediation + rotation |
| **Sensitive but synthetic** | Fixture, documented sample, or public test key | Verify it is genuinely fake, then note and move on |
| **False positive** | Rule matched a non-secret (a hash, a UUID, a base64 asset) | Dismiss with a one-line reason |
| **Needs owner judgment** | Only the owner knows whether it is publishable | Question in the Phase 1 list |

Common false positives worth recognizing on sight: base64-encoded images
matching entropy rules; UUIDs and content hashes matching key patterns;
Stripe's and other vendors' published test keys; `example.com` /
`user@example.com` / RFC-5737 documentation IPs; lockfile integrity hashes;
minified bundles.

Common *false negatives* — things a scanner will not catch, which is why the
manual pass exists: an internal token with a bespoke format; a credential split
across concatenated strings or built at runtime; anything base64-encoded; a
password inside a screenshot; a customer name that is just an ordinary English
word; a `.docx` attachment; a plausible-looking name in seed data that belongs
to a real person.

## 7. Credential remediation

If a real credential ever reached a commit, the sequence is fixed:

1. **Assume compromised.** Private repos are visible to collaborators, forks,
   CI systems, and anyone who ever cloned. "It was never public" is not
   containment.
2. **Rotate first, at the provider.** This is the only step that actually
   revokes access, and it is the owner's to perform. Report the credential type
   and location; never the value.
3. **Then remediate history**, per the chosen release method:
   - *Fresh-history export*: the credential is simply not present in the new
     repo. Nothing to rewrite. This is a strong argument for method 2.
   - *Preserve history*: rewriting is required (`git filter-repo` is the
     current tool; BFG is the older one), which changes every downstream SHA
     and requires coordination with anyone holding a clone. Hand back the
     commands; do not run them.
4. **Check what else the credential unlocked** — an old key may still be
   attached to a live billing account or database.
5. **Record it in the final report** as an owner action item, distinct from the
   things the agent already handled.

Reporting shape, for each finding — nothing more:

> `CREDENTIAL / stripe-live-key` — `.env`, present in history from commit
> `8aaf3dc` (2021-03) through `a91f22c` (2021-08); removed from HEAD.
> Fingerprint `28be19ba`, same value also at `deploy/notes.md:12`.
> **Action: rotate at the Stripe dashboard.** Deleting from HEAD is not
> sufficient; the value remains in history.

## 8. Third-party assets and redistribution rights

Being in the repo does not make it redistributable. Check each category and
report what could not be established, because "unknown provenance" is itself a
publication risk:

- **Fonts** — very commonly licensed for a specific site or app, not for
  redistribution in a public repo. A `.ttf`/`.otf`/`.woff2` in an old project
  needs its license confirmed.
- **Icons and illustrations** — many popular sets are free for use but not for
  redistribution, or require attribution that has been lost.
- **Stock photography and video** — almost never redistributable.
- **Copied code** — snippets from Stack Overflow, blog posts, tutorials, or
  another project, carrying their own terms. Vendored dependencies keep their
  original license and notice requirements.
- **Datasets** — frequently carry research-only or non-commercial terms.
- **Model outputs and generated assets** — check the generating service's terms.
- **Trademarks and brand assets** — logos of companies the project integrated
  with, usually usable only under brand guidelines.
- **Dependency licenses** — a copyleft dependency can be incompatible with the
  permissive license the owner intends for their own code. Generate the
  inventory (`npm ls --all`, `pip-licenses`, `cargo license`,
  `go-licenses report`) and check for surprises.
