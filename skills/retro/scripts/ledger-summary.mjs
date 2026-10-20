#!/usr/bin/env node
// Pass C numbers from the ledger, over a window, as markdown (or --json).
//
//   node ledger-summary.mjs [--since 14d|YYYY-MM-DD] [--until YYYY-MM-DD]
//                           [--dir <ledger dir>] [--json] [--by-operator]
//
// --dir may point at a cross-repo roll-up folder; the script only reads.
import { findRepoRoot, ledgerDir, loadEnv, parseArgs, parseWindow, readAll } from './ledger-lib.mjs';

const args = parseArgs(process.argv.slice(2));
const repoRoot = findRepoRoot();
const env = loadEnv(repoRoot);
const dir = args.dir ? String(args.dir) : ledgerDir(repoRoot, env);
const { since, until } = parseWindow(args);
const byOperator = Boolean(args.by_operator) || env.RETRO_MODE === 'team';

const all = readAll(dir);
const entries = all.filter((e) => {
  const t = new Date(e.started_at || 0).getTime();
  return t >= since.getTime() && t <= until.getTime();
});

const s = summarise(entries);
s.window = { since: since.toISOString().slice(0, 10), until: until.toISOString().slice(0, 10) };
s.ledger_dir = dir;
s.entries_total_in_ledger = all.length;

if (args.json) {
  process.stdout.write(JSON.stringify(s, null, 2) + '\n');
} else {
  process.stdout.write(render(s, byOperator));
}

function summarise(es) {
  const count = (arr, key) => {
    const m = new Map();
    for (const v of arr) m.set(key(v), (m.get(key(v)) || 0) + 1);
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  };
  const turns = { operator: 0, agent: 0, automated: 0 };
  let toolCalls = 0;
  const perSessionTurns = [];
  const perSessionTools = [];
  let withHook = 0;
  let withAgent = 0;
  let automatedSessions = 0;
  const blocked = [];
  const corrections = new Map();
  const checks = new Map();
  const rulesBroken = new Map();
  const learned = [];
  let noTask = 0;
  for (const e of es) {
    const t = e.turns || {};
    turns.operator += t.operator || 0;
    turns.agent += t.agent || 0;
    turns.automated += t.automated || 0;
    if ((t.automated || 0) > 0) automatedSessions++;
    toolCalls += e.tool_calls || 0;
    if (t.operator !== undefined) perSessionTurns.push((t.operator || 0) + (t.automated || 0));
    if (e.tool_calls !== undefined) perSessionTools.push(e.tool_calls);
    const src = e.source || [];
    if (src.includes('hook')) withHook++;
    if (src.includes('agent') || src.includes('manual')) withAgent++;
    if (!e.task || e.task.startsWith('(no wrap-up')) noTask++;
    for (const b of e.blocked_on_person || []) blocked.push({ id: e.id, text: String(b), unanswered: /unanswered|not answered|no answer|still waiting/i.test(String(b)) });
    for (const c of e.corrections || []) {
      const k = normalise(c);
      const cur = corrections.get(k) || { text: String(c), sessions: new Set() };
      cur.sessions.add(e.id);
      corrections.set(k, cur);
    }
    for (const c of e.checks_failed || []) checks.set(String(c), (checks.get(String(c)) || 0) + 1);
    for (const r of e.rules_broken || []) rulesBroken.set(normalise(r), { text: String(r), n: (rulesBroken.get(normalise(r))?.n || 0) + 1 });
    if (e.learned) learned.push({ id: e.id, text: String(e.learned) });
  }
  const repeated = [...corrections.values()].filter((c) => c.sessions.size >= 2)
    .map((c) => ({ text: c.text, sessions: c.sessions.size })).sort((a, b) => b.sessions - a.sessions);
  return {
    sessions: es.length,
    by_agent: count(es, (e) => e.agent || 'unknown'),
    by_operator: count(es, (e) => e.operator || 'unknown'),
    by_outcome: count(es, (e) => e.outcome || 'unknown'),
    by_surface: count(es, (e) => e.surface || 'unknown'),
    turns,
    automated_share: turns.operator + turns.automated ? turns.automated / (turns.operator + turns.automated) : 0,
    sessions_with_automated_turns: automatedSessions,
    tool_calls: toolCalls,
    median_turns_per_session: median(perSessionTurns),
    median_tool_calls_per_session: median(perSessionTools),
    coverage: { with_hook: withHook, with_agent_or_manual: withAgent, counts_only_no_task: noTask },
    blocked_on_person: { sessions: new Set(blocked.map((b) => b.id)).size, items: blocked.length, unanswered_at_close: blocked.filter((b) => b.unanswered).length, list: blocked },
    corrections_total: [...corrections.values()].reduce((n, c) => n + c.sessions.size, 0),
    corrections_distinct: corrections.size,
    repeated_corrections: repeated,
    checks_failed: [...checks.entries()].sort((a, b) => b[1] - a[1]),
    rules_broken: [...rulesBroken.values()].sort((a, b) => b.n - a.n),
    learned,
    pushed_no_pr: es.filter((e) => e.outcome === 'pushed-no-pr').map((e) => e.id),
  };
}

function normalise(s) {
  return String(s).toLowerCase().replace(/^(re-?stated|repeated|again)\s*:\s*/, '').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function median(xs) {
  if (!xs.length) return null;
  const a = [...xs].sort((x, y) => x - y);
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function pct(x) { return `${Math.round(x * 100)}%`; }

function render(s, showOperators) {
  const L = [];
  L.push(`# Ledger summary: ${s.window.since} to ${s.window.until}`);
  L.push('');
  L.push(`Ledger: \`${s.ledger_dir}\` (${s.entries_total_in_ledger} entries in total, ${s.sessions} in the window)`);
  L.push('');
  if (!s.sessions) {
    L.push('No sessions in the window. If agents ran, the ledger is not being written: that is the first finding.');
    return L.join('\n') + '\n';
  }
  L.push('## Sessions');
  L.push(`- By agent: ${fmt(s.by_agent)}`);
  if (showOperators) L.push(`- By operator: ${fmt(s.by_operator)}`);
  L.push(`- By outcome: ${fmt(s.by_outcome)}`);
  L.push(`- By surface: ${fmt(s.by_surface)}`);
  L.push(`- Pushed with no PR: ${s.pushed_no_pr.length}${s.pushed_no_pr.length ? ` (${s.pushed_no_pr.join(', ')})` : ''}`);
  L.push('');
  L.push('## Coverage (is the ledger being written?)');
  L.push(`- Entries with hook counts: ${s.coverage.with_hook} of ${s.sessions}`);
  L.push(`- Entries with an agent or manual wrap-up: ${s.coverage.with_agent_or_manual} of ${s.sessions}`);
  L.push(`- Counts only, no task line: ${s.coverage.counts_only_no_task}`);
  L.push('');
  L.push('## Turns and tools');
  L.push(`- Operator turns ${s.turns.operator}, agent turns ${s.turns.agent}, automated turns ${s.turns.automated} (${pct(s.automated_share)} of non-agent turns; ${s.sessions_with_automated_turns} sessions had any)`);
  L.push(`- Tool calls ${s.tool_calls}; median per session ${s.median_tool_calls_per_session ?? 'n/a'}; median operator+automated turns per session ${s.median_turns_per_session ?? 'n/a'}`);
  L.push('');
  L.push('## Blocked on a person');
  L.push(`- ${s.blocked_on_person.sessions} sessions, ${s.blocked_on_person.items} questions, ${s.blocked_on_person.unanswered_at_close} marked unanswered at close`);
  for (const b of s.blocked_on_person.list.slice(0, 15)) L.push(`  - ${b.id}: ${b.text}`);
  L.push('');
  L.push('## Corrections (what operators had to say)');
  L.push(`- ${s.corrections_total} corrections across sessions, ${s.corrections_distinct} distinct, ${s.repeated_corrections.length} repeated in 2+ sessions`);
  for (const c of s.repeated_corrections.slice(0, 10)) L.push(`  - ${c.sessions} sessions: ${c.text}`);
  L.push('');
  L.push('## Checks failed, by step');
  L.push(s.checks_failed.length ? s.checks_failed.map(([k, n]) => `- ${k}: ${n}`).join('\n') : '- none recorded');
  L.push('');
  L.push('## Rules broken (self-reported; pass D cross-checks)');
  L.push(s.rules_broken.length ? s.rules_broken.map((r) => `- ${r.n}: ${r.text}`).join('\n') : '- none recorded');
  L.push('');
  if (s.learned.length) {
    L.push('## Learned');
    for (const l of s.learned) L.push(`- ${l.id}: ${l.text}`);
    L.push('');
  }
  return L.join('\n') + '\n';
}

function fmt(pairs) {
  return pairs.length ? pairs.map(([k, n]) => `${k} ${n}`).join(', ') : 'none';
}
