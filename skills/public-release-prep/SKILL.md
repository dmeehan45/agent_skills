---
name: public-release-prep
description: >-
  Prepare a private repository for public release as a functional, forkable
  reference project — audit first, clean up only after the owner approves.
  Use when asked to open-source a repo, make a private repo public, "share
  this old project on my GitHub", turn past project work into a public
  template or portfolio piece, sanitize a repo before publishing, check
  whether a repo is safe to open-source, scrub secrets and internal material
  before going public, or write the README and pick a license for a first
  public release. It scans the working tree AND all reachable git history for
  credentials, personal data, client or employer material, and third-party
  assets; treats ownership and licensing as publication gates rather than
  findings; verifies the project actually installs, builds, tests, and runs
  from a clean checkout and repairs what is broken; rewrites the README
  honestly in the owner's voice; and recommends whether to sanitize existing
  history, export a fresh-history snapshot, or stay private. It never
  publishes, never changes repository visibility, never pushes or force-pushes,
  never rewrites history, and never rotates credentials — it hands back the
  exact commands for the owner to run. Not a general code-health report
  (handoff-audit), not a product QA pass (qa-sweep), not a single-diff review
  (/code-review or /security-review).
---

# Preparing a private repo to go public

An old private repo is about to become a public artifact with the owner's name
on it, permanently, in front of strangers and search engines. Three things go
wrong when that is rushed: a live credential ships in a commit from 2021 that
nobody remembers making; the code turns out to belong to a former employer;
or the project is published in a state where nobody — including its author in
two years — can actually run it.

This skill exists to catch all three before the visibility toggle is flipped.
It runs in two phases with a human approval gate between them, because the
irreversible decisions here belong to the owner, not the agent.

> Applies to any stack. Commands below are examples — read the repo's own
> manifests, lockfiles, CI config, and agent instructions to learn the real
> ones, and use those.

## The stop line (read before anything else)

These actions are outside this skill under all circumstances, including when
the owner says "go ahead" mid-run. If they are wanted, they are the owner's to
perform with the exact commands this skill hands back:

- **Never publish or change visibility.** No repo creation, no
  private→public flip, no pushing to a public remote, no releases, no gists.
- **Never push, force-push, or rewrite history.** No `git push`, no `filter-repo`,
  no `filter-branch`, no `rebase` of shared history, no amending published
  commits. Work stays local, on a branch, uncommitted or committed but unpushed.
- **Never delete branches, tags, or remotes.** They are part of the evidence.
- **Never rotate, revoke, or regenerate a credential.** Report what must be
  rotated and where; the owner does it. Rotating a key can break live systems
  the repo does not describe.
- **Never print a secret.** Not in chat, not in a report, not in a commit
  message, not "partially masked". Report credential *type*, *location*, and
  *required remediation*. The same restraint applies to personal data,
  customer records, and confidential business content — describe the category
  and the file, never the contents.
- **Never delete an ambiguous file without approval.** Obvious build output is
  fair game once cleanup is approved; anything with judgment attached goes on
  the proposed-removal list first.

Beyond that: preserve unrelated working changes. Check `git status` before
touching anything, and if the tree is dirty, say so and leave those changes
alone. Read `AGENTS.md` / `CLAUDE.md` / `CONTRIBUTING.md` first — repo-specific
instructions outrank this skill's defaults.

Do destructive-looking diagnostics (installing dependencies, running
generators, building) in a temporary copy — `git clone /path/to/repo /tmp/xyz`
or `git worktree add` — so a failed install cannot dirty the real tree.

## Phase 1 — Audit

Nothing is deleted, fixed, or rewritten in this phase. The deliverable is a
report and a short list of questions.

### 1.1 Understand what this actually is

Read the code, not the README — the README is frequently the least accurate
file in an abandoned repo. Establish: what the project does; whether the
implementation matches its stated purpose; the languages, frameworks, package
managers, runtime versions, external services, databases, and deployment
assumptions; the intended install / dev / test / build / run commands; and
which user paths are central rather than incidental.

Then classify it honestly, because everything downstream depends on it:
a **reusable template** (someone forks and adapts it), a **reference
implementation** (someone reads it to learn a technique), a **demo** (someone
runs it once to see the idea), or an **archival example** (someone finds it
interesting as a historical artifact). Most old project work is the third or
fourth thing. Publishing an archival example as a template is the most common
way these releases mislead people.

### 1.2 Sweep for sensitive material

Scan the **working tree and all reachable history** — tracked, untracked, and
ignored files, every branch and tag, LFS objects, and submodules. Material
deleted from HEAD is still public if it is reachable in history; that is the
single most common leak.

Start with the bundled scanner, which inventories the repo, matches
high-signal paths, and greps content across the tree and history while
reporting only rule + location + a non-reversible fingerprint:

```bash
bash scripts/scan-release-surface.sh --repo /path/to/repo --out /tmp/release-audit
```

It uses `gitleaks` for history when installed and falls back to a blob walk
otherwise. Read `references/scan-playbook.md` for what the scanner cannot see
and must be checked by hand: hosted surfaces (issues, PRs, wikis, releases,
Actions logs and artifacts, project boards, forks), binary and document
metadata, encoded or bespoke credential formats, and the judgment calls the
tiers deliberately leave open.

The scanner is a lead generator, never a verdict. Every hit is triaged by a
human-equivalent read: a `sk_live_` string in a test fixture may be a
documented fake, and a repo full of `example.com` addresses is fine. Equally,
its silence proves nothing — a custom internal token format matches no rule.

**If a real credential ever reached a commit, treat it as compromised.**
Not "probably fine because the repo was private" — private repos are visible
to collaborators, forks, CI logs, and anyone who cloned. Removing it from HEAD
does not help; the commit still contains it. Report the credential type, where
it lives, that rotation is required, and what history remediation the chosen
release method implies. Do not rotate anything.

### 1.3 Ownership and licensing — these are gates, not findings

An unresolved ownership question blocks release entirely, no matter how clean
everything else is. Do not assume the owner may publish code they wrote.

Look for evidence in the repo and report what it suggests without concluding:
commit author identities and email domains (a work address across the history
is a strong signal), copyright headers, employer or client names, `LICENSE`
files, dependency licenses incompatible with the intended outcome (copyleft
where a permissive license is planned), vendored third-party code, and assets
that are usually licensed rather than owned — fonts, icon sets, stock imagery,
sound, datasets, and model outputs.

The absence of a `LICENSE` file is itself a finding: a public repo without one
grants no reuse rights, so "public template" and "no license" are contradictory
goals. Do not add a license until ownership and preference are both confirmed —
see `references/publication-docs.md` for the MIT/Apache-2.0 comparison to
present.

### 1.4 Establish the functional baseline

Verify from a clean checkout in a temporary copy, with the declared runtime and
package-manager versions and the committed lockfile. The question is not "does
this code look right" — it is "can a stranger clone this and reach a useful
state". Presence of a script proves nothing; run it.

`references/functional-audit.md` has the full verification matrix, the repair
policy, dependency and vulnerability triage, demo-mode patterns for projects
that need paid services, and the rules for adding tests. Record every result
honestly now — a gate that could not be run is reported as NOT RUN with the
reason, never inferred green.

### 1.5 Triage the artifacts

Classify before proposing removal. Confidence that something is deletable comes
from what it *is*, not from what its filename resembles:

- **Remove**: build output, caches, coverage reports, logs, local databases,
  editor residue, debug captures, dependency directories, stale deployment
  artifacts, temporary exports.
- **Remove**: internal planning material with no public value — private
  roadmaps, scratchpads, agent transcripts, meeting notes, build-process
  ephemera.
- **Preserve and rewrite**: architecture and design explanations that would
  genuinely help a public reader, once sanitized. Good design notes are often
  the most valuable thing in an old repo, and they are exactly what a careless
  sweep deletes for containing the word "plan".
- **Replace**: sample data, fixtures, and seeds derived from real people or
  real accounts, swapped for clearly synthetic equivalents.
- **Never delete on filename alone.** "spec", "plan", "prompt", "notes", and
  "internal" appear in both throwaway scratch files and the best documentation
  in the repo. Open it.

Update `.gitignore` so removed local artifacts do not return.

### 1.6 Choose a release method

Compare all three and recommend one:

1. **Sanitize in place, preserve history.** Honest provenance and contributor
   attribution survive. Only viable when history is genuinely clean, because
   sanitizing history means rewriting it.
2. **Fresh-history snapshot into a new public repo**, original private repo
   untouched. Every historical leak becomes irrelevant in one step.
3. **Stay private.** The correct answer when ownership, confidentiality,
   dependency, or functional risk cannot be resolved responsibly. Recommending
   this is a success, not a failure.

For an old project shared mainly as a template or portfolio piece, **prefer
option 2** — the commit history of abandoned work is rarely the value, and it
is usually where the risk lives. Flag when a fresh-history export would be
inappropriate: multiple contributors whose attribution would be erased, an
inbound license requiring preserved notices, or history that is itself the
point (a tutorial repo built commit by commit). Exact command sequences for
each method are in `references/report-templates.md` — to hand back, not to run.

### 1.7 Ask only what the repo cannot answer

Never ask what an hour of reading would tell you. Ask what only the owner
knows — and keep the list short, because a wall of questions gets abandoned:

- **Ownership**: written outright by the owner, or created for an employer,
  client, collaborator, or school, or under any agreement? *(Always ask. Never
  infer from commit metadata alone.)*
- **Framing**: maintained project, occasionally-maintained template, or
  archived historical example? This sets the maintenance promise.
- **Audience and reuse**: who should find this useful, and what should they be
  able to borrow?
- **Backstory**: what prompted building it? This becomes the README's opening,
  and it is the difference between a repo someone reads and one they scroll past.
- **The interesting part**: what was fun, surprising, or instructive? What is
  still worth sharing?
- **Attribution**: organizations, collaborators, source projects, datasets, or
  assets needing credit or permission?
- **License**: which one — noting that making a repo public grants no reuse
  rights by itself.
- **Demo mode**: should users reach something useful without paid accounts?
- **The never-publish list**: anything the owner knows must not appear, even
  paraphrased? *(Always ask. The agent cannot infer this.)*

### 1.8 Deliver the audit and stop

Use the Phase 1 structure in `references/report-templates.md`: plain-language
description of the project, the readiness table (severity, evidence, risk,
proposed treatment), blockers separated from findings, the question list, the
cleanup and repair plan, the release-method recommendation, and a verdict of
**not ready** / **conditionally ready** / **ready for implementation work**.

Then stop and wait. Do not begin cleanup, do not delete ambiguous files, do
not start "obvious" fixes while waiting.

## Phase 2 — Implement (only after approval)

Work the approved plan, and only the approved plan. New problems found along
the way get surfaced, not silently fixed and not silently skipped.

**Cleanup**: remove what was approved, replace sensitive fixtures with
synthetic ones, update `.gitignore`, sanitize and rewrite the documentation
worth keeping.

**Repairs**: follow the repair policy in `references/functional-audit.md`.
Small, evidence-backed fixes that restore install / start / build / test /
central flow come first. Do not modernize dependencies wholesale because newer
versions exist; apply security and compatibility upgrades with justification,
test them, and describe breaking changes.

**Documentation**: rewrite the README so the project is presented honestly and
the first run is straightforward, plus `.env.example`, `LICENSE`, and any other
lightweight public file that earns its place. Full structure, the license
comparison, and the rule against ceremonial files are in
`references/publication-docs.md`.

The backstory goes in the owner's voice, from their answers — not inflated, not
turned into a product launch. "I built this in a weekend to stop hand-copying
invoice numbers" is better than "a robust automation platform". Understating is
safer than overstating: readers forgive a modest repo that works and resent an
impressive one that does not.

**Honesty constraints, non-negotiable**: never call the project
production-ready, secure, or fully tested unless the evidence supports it.
No invented benchmarks or coverage numbers. No stub described as a complete
integration. Stale badges, broken screenshots, dead roadmap promises, and
references to internal infrastructure come out.

## Verification

Re-verify rather than assuming the changes worked:

- Re-run the sensitive-material scan on the **proposed public snapshot** and on
  the **history that snapshot will carry**. A fresh-history export must be
  scanned as the new repo, not the old one.
- Repeat clean install and verification with no reliance on existing caches,
  untracked files, globally installed packages, or undeclared environment
  variables. A fresh temporary clone is the only trustworthy way to test this.
- Run every applicable gate: lint, type check, tests, build, migrations, smoke.
- **Follow the README literally, as a stranger would**, copy-pasting its
  commands in order. This catches the step that lives only in the author's
  muscle memory.
- Read the final diff for accidental deletions, private language that survived,
  generated noise, and unsupported claims.
- Confirm `.env.example` holds names and placeholders only, that no test or
  demo touches production data, and that asset and dependency redistribution
  rights still hold after any changes.
- State plainly which checks could not be performed and why.

## Final response

Use the Phase 2 structure in `references/report-templates.md`: public-facing
description, material changes, files removed or replaced and why, defects found
and how they were fixed, verification commands with real results, remaining
limitations and unresolved risks, credentials requiring rotation, manual checks
the owner must perform on the hosting platform, a direct recommendation of
**safe to publish** / **publish only after these actions** / **do not publish**,
and the exact release steps — written out, not executed.

## Preflight before handing back

- [ ] Working tree state checked; unrelated changes preserved; repo agent
      instructions read and followed.
- [ ] Scan covered working tree *and* reachable history, including untracked,
      ignored, branches, tags, LFS, submodules.
- [ ] Zero secret values, personal data, or confidential content anywhere in
      the output — types and locations only.
- [ ] Every credential found in history reported as requiring rotation.
- [ ] Ownership and license treated as gates; nothing licensed without
      confirmed ownership and stated preference.
- [ ] Every functional claim backed by a command that was actually run;
      un-run gates marked NOT RUN with a reason.
- [ ] Ambiguous files proposed for removal, not deleted.
- [ ] README verified by following it literally from a clean checkout.
- [ ] No "production-ready" / "secure" / "fully tested" claim beyond evidence.
- [ ] Nothing published, pushed, rewritten, deleted, or rotated; release steps
      handed back as commands.
