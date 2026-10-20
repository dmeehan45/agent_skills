#!/usr/bin/env node
// Write (or merge into) one ledger entry for an agent session.
// Used by agents at wrap-up and by people from the terminal. Metadata and
// the operator's own instructions only; never product or customer content.
//
//   node ledger-append.mjs --task "<one line>" --outcome merged \
//     --correction "no em dashes in copy" --correction "open a PR, do not just push" \
//     --blocked "which design to build; unanswered at close" \
//     --check-failed lint --rule-broken "pushed without a PR" [--pr 1234]
//
// Flags: --task --outcome --agent --model --surface --operator --unattended
//        --session-id --branch --pr --commits --correction* --blocked*
//        --check-failed* --rule-read* --rule-broken* --learned --cost-note
//        --started-at --ended-at --dir --dry-run --quiet
import {
  OUTCOMES, SCHEMA, asArray, currentBranch, entryId, findBySession, findRepoRoot, git, gitUserName,
  ledgerDir, loadEnv, merge, parseArgs, repoName, writeEntry,
} from './ledger-lib.mjs';

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  process.stdout.write(`ledger-append: write one agent-session entry to the ledger.\n` +
    `Required: --task "<one line>" --outcome <${OUTCOMES.join('|')}>\n` +
    `Repeatable: --correction --blocked --check-failed --rule-read --rule-broken\n` +
    `Optional: --agent --model --surface --operator --unattended --session-id --branch --pr --commits\n` +
    `          --learned --cost-note --started-at --ended-at --dir --dry-run --quiet\n`);
  process.exit(0);
}

const repoRoot = findRepoRoot();
const env = loadEnv(repoRoot);
const dir = args.dir ? String(args.dir) : ledgerDir(repoRoot, env);

const task = typeof args.task === 'string' ? args.task.trim() : '';
if (!task) fail('--task "<one line>" is required (the operator\'s words, no customer data).');
const outcome = String(args.outcome || 'unknown');
if (!OUTCOMES.includes(outcome)) fail(`--outcome must be one of ${OUTCOMES.join(', ')}`);

const sessionId = args.session_id || process.env.CLAUDE_SESSION_ID || process.env.RETRO_SESSION_ID || '';
const agent = String(args.agent || process.env.RETRO_AGENT || detectAgent());
const now = new Date().toISOString();
const startedAt = String(args.started_at || process.env.RETRO_SESSION_STARTED_AT || now);
const operator = args.unattended ? 'unattended' : String(args.operator || process.env.RETRO_OPERATOR || gitUserName(repoRoot) || 'unknown');

const existing = findBySession(dir, sessionId);
const incoming = {
  schema: SCHEMA,
  id: existing?.id || entryId(startedAt, agent, sessionId || undefined),
  session_id: sessionId || undefined,
  agent,
  model: args.model ? String(args.model) : undefined,
  surface: args.surface ? String(args.surface) : (process.env.CLAUDE_CODE_REMOTE ? 'web' : undefined),
  operator,
  repo: repoName(repoRoot) || undefined,
  branch: args.branch ? String(args.branch) : currentBranch(repoRoot) || undefined,
  started_at: existing?.started_at || startedAt,
  ended_at: String(args.ended_at || now),
  task,
  outcome,
  pr: args.pr ? Number(args.pr) : undefined,
  commits: args.commits !== undefined ? Number(args.commits) : countCommits(),
  corrections: asArray(args.correction).map(String),
  blocked_on_person: asArray(args.blocked).map(String),
  checks_failed: asArray(args.check_failed).map(String),
  rules_read: asArray(args.rule_read).map(String),
  rules_broken: asArray(args.rule_broken).map(String),
  learned: args.learned ? String(args.learned) : undefined,
  cost_note: args.cost_note ? String(args.cost_note) : undefined,
  source: ['agent'],
};

const entry = existing ? merge(existing, incoming) : merge({}, incoming);
if (args.dry_run) {
  process.stdout.write(JSON.stringify(entry, null, 2) + '\n');
  process.exit(0);
}
const path = writeEntry(dir, entry);
if (!args.quiet) process.stdout.write(`${existing ? 'merged into' : 'wrote'} ${path}\n`);

function detectAgent() {
  if (process.env.CLAUDE_SESSION_ID || process.env.CLAUDE_PROJECT_DIR || process.env.CLAUDECODE) return 'claude-code';
  if (process.env.CODEX_SANDBOX || process.env.CODEX_CI) return 'codex';
  if (process.env.CURSOR_TRACE_ID || process.env.CURSOR_AGENT) return 'cursor';
  return 'agent';
}

function countCommits() {
  // Commits on this branch that the base does not have. Best effort; 0 when unknown.
  const base = env.RETRO_BASE_BRANCH || 'main';
  for (const ref of [`origin/${base}`, base]) {
    const n = git(['rev-list', '--count', `${ref}..HEAD`], repoRoot);
    if (n !== '') return Number(n);
  }
  return 0;
}

function fail(msg) {
  process.stderr.write(`ledger-append: ${msg}\n`);
  process.exit(2);
}
