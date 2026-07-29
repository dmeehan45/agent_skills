# Functional audit and repair

Contents:
1. The standard being measured
2. Clean-environment setup
3. The verification matrix
4. Repair policy — what to fix and what to document
5. Dependencies, vulnerabilities, and obsolete runtimes
6. Dead external services
7. Demo mode for projects needing paid infrastructure
8. Tests
9. Reporting results honestly

---

## 1. The standard being measured

One question: **can a stranger clone this and reach a useful state without
undocumented manual intervention?**

Not "is the code good" — that is `handoff-audit`. Not "does the product work
correctly" — that is `qa-sweep`. This is the fork-and-run path, and its failure
mode is specific: the author can run the project because their machine holds
five years of accumulated state — a global package, an env var in their shell
profile, a database that already exists, a service account already authorized.
None of that is in the repo, and none of it is in the README.

A public repo that cannot be run is worse than no repo. It costs strangers an
hour before they conclude it is broken, and it is the most common thing wrong
with published old project work.

## 2. Clean-environment setup

Work in a temporary copy, never in the owner's tree — installs and generators
create files, and a failed install can leave the real repo dirty.

```bash
git clone /path/to/repo /tmp/release-check && cd /tmp/release-check
```

Cloning (rather than `cp -r`) is deliberate: it reproduces what a stranger gets
and excludes untracked and ignored files. If the project only runs because of
an untracked file, the clone reveals it immediately.

Then remove the author's ambient state from the equation as far as the
environment allows: use the declared runtime version (`.nvmrc`, `.python-version`,
`.tool-versions`, `go.mod`, `rust-toolchain.toml`, `engines` in `package.json`)
rather than whatever is installed; install from the committed lockfile with the
frozen/CI flag (`npm ci`, `pnpm install --frozen-lockfile`, `yarn --immutable`,
`pip install -r requirements.txt`, `poetry install --sync`, `bundle install
--deployment`, `go mod download`, `cargo build --locked`); and start with no
project environment variables set, so the failure mode for a missing variable
is observed rather than assumed.

If the repo declares no runtime version anywhere, that is a finding — the next
person gets whatever their machine has.

## 3. The verification matrix

Run what applies. Record the actual command, actual result, and actual output —
trimmed, never invented.

| Check | What it proves | Typical failure worth reporting |
| --- | --- | --- |
| Lockfile install | Dependencies still resolve | Yanked package, dead registry, lockfile/manifest drift |
| Format / lint | Toolchain still works | Config referencing an uninstalled plugin |
| Type check | Source consistent with declared types | Types drifted from an upgraded dependency |
| Unit tests | Core logic behaves | Tests depending on wall-clock time, network, or fixtures long gone |
| Integration tests | Components wire together | Requires a service nobody documented |
| Build | Ships an artifact | Build script referencing a missing env var or file |
| Startup smoke | Process actually boots | Crashes immediately without config the README never mentions |
| **Central user flow** | The project does its thing | The point of the whole exercise |
| Env var handling | Missing config fails legibly | Silent `undefined` propagating into a confusing error |
| Links and assets | Docs are not rotted | Dead links, missing images, moved routes |
| Migrations / seeds | A fresh database can be built | Migrations that only apply in a specific order nobody recorded |
| Deployment config | Config is not a private-infra fossil | Hardcoded internal hostnames, an account ID, a private registry |

**Exercising the central flow matters more than everything above it.** A green
test suite and a successful build routinely coexist with an app that shows a
blank page. Actually drive the primary path: make the request, run the CLI on a
sample input, load the page, submit the form. Record what was observed.

**Environment-variable handling** is worth a deliberate probe: unset everything
and start the project. If it crashes with `Cannot read property 'x' of
undefined`, that is a real defect for a public repo — the first thing every
stranger will hit. A named, legible error (`Missing required env var
DATABASE_URL — see .env.example`) is a small fix with a large effect on whether
anyone gets past minute one.

## 4. Repair policy

Fix defects that prevent the project from installing, starting, building,
testing, or completing its central flow. Prefer small, evidence-backed repairs
over broad modernization.

The temptation here is a rewrite, and it should be resisted. The owner asked to
publish an old project, not to rebuild it. A rewrite also destroys the thing
that makes old project work interesting — that it is a real artifact of a real
moment, with the constraints of that moment visible in it.

| Situation | Treatment |
| --- | --- |
| Install fails | Fix. Nothing else can be verified until it works. |
| Build or start fails | Fix. |
| Central flow broken | Fix, or reduce the project's claims to match what works. |
| Tests fail from bit rot (dates, timezones, network) | Fix if small and local; otherwise document. |
| Tests fail from a real product bug | Fix if in the central path; otherwise a Known Limitation. |
| Lint/format noise | Only if the repo declares a standard it now fails. Do not add one. |
| Peripheral feature broken | Document as a Known Limitation. Do not expand scope. |
| Dependency vulnerability | See §5. |
| Needs paid infrastructure | See §7. |
| Deprecated but working API | Note it. Do not migrate speculatively. |

Every repair earns a line in the final report: what was broken, evidence it was
broken, the fix, and evidence it now works.

## 5. Dependencies, vulnerabilities, and obsolete runtimes

Report the state; upgrade only with justification.

```bash
npm audit --omit=dev        # pip-audit / bundle audit / cargo audit / govulncheck
```

Old repos produce long vulnerability lists, and treating that list as a to-do
is how a publication task turns into a month of dependency work. Triage instead:

- **Upgrade**: a vulnerability reachable from the code the project actually
  runs, or a dependency so broken it blocks install/build. Test it, and describe
  any breaking change.
- **Document**: advisories in dev-only tooling, or in code paths the project
  never exercises. Note them in the README's limitations rather than churning
  the dependency tree.
- **Do not upgrade** merely because a newer version exists. Every upgrade is a
  chance to break a project the owner can no longer debug from memory.

**Obsolete runtimes** deserve an explicit call: a project pinned to a runtime
that no longer receives security updates should say so plainly in the README.
That is honest and useful. Silently bumping it to the current major version and
declaring success is neither — a project that has not been run since then has
not been tested against it.

**Materially unsupported** is different from **old**. A stable library that has
not needed a release in four years is fine. A framework whose entire ecosystem
moved on, whose install now fails, is a finding.

## 6. Dead external services

Old projects integrate with services that changed or disappeared. Check each
external dependency: does the API still exist; did its contract change (v1
retired, auth model replaced, endpoint moved); is registration still open; is
there still a free tier.

When an integration is dead, options in order of preference: adapt to the
current API if small; replace with an equivalent current service; stub behind
an interface with an honest mock and label it clearly; or remove the feature
and note its removal. Never leave code that appears to integrate with a service
it can no longer reach — that is the most misleading state possible for someone
forking it.

## 7. Demo mode

If the project cannot do anything useful without paid or private
infrastructure, its public value drops sharply. Options, best first:

1. **Local substitute** — SQLite for a managed database, a local model for a
   hosted one, a filesystem store for object storage.
2. **Adapter with a fake implementation** — an interface with real and fake
   backends, selected by env var, so the fake is a first-class documented path.
3. **Recorded fixtures** — captured (and sanitized) API responses replayed for
   the demo, letting the real flow run end to end without credentials.
4. **Clearly documented limited demo** — some parts run, some do not, and the
   README says exactly which.

The rule that keeps this honest: **do not present an untested stub as a
complete integration.** A mock the README calls a mock is useful. A mock
presented as working is a trap, and it wastes the time of everyone who forks
the project.

Whatever mode ships must be verified by running it, and any demo data must be
synthetic and reproducible — no demo account tied to a real service, no seed
data derived from real users.

## 8. Tests

If the suite is absent or ineffective, add a small set of meaningful tests
around the fork-and-run path — the things that would tell a stranger their
fork still works:

- The project starts with valid configuration.
- The central flow produces the expected result on a known input.
- Missing required configuration produces a clear error.
- Any pure logic worth trusting behaves on a couple of real cases.

Three tests that would catch a real break beat thirty that assert constants
equal themselves. Do not manufacture coverage numbers with low-value tests, do
not report a coverage percentage as a quality claim, and do not rewrite an
existing suite that works merely because it is not to current taste.

## 9. Reporting results honestly

- A gate not run is **NOT RUN**, with the reason. Never inferred green.
- Environmental failures (a missing browser binary in a container, no network)
  are labeled as such and distinguished from code defects.
- Partial verification says what was and was not covered. No silent sampling.
- Never claim **production-ready**, **secure**, or **fully tested**. For old
  project work being shared as a reference, the accurate framing is usually:
  *"Verified to install, build, and complete <specific flow> on <runtime
  version> as of <date>. Not maintained; not audited for security."*

That sentence is more useful to a reader than any badge, and unlike a badge it
stays true.
