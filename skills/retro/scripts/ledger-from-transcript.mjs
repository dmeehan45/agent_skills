#!/usr/bin/env node
// Session-end hook: fill in the counts nobody remembers.
//
// Reads the Claude Code hook payload on stdin ({session_id, transcript_path,
// cwd, ...}), or --transcript <path> [--session-id <id>] [--cwd <dir>] when
// run by hand. Counts operator turns, agent turns, automated turns (scheduled
// wake-ups and events), tool calls and duration; reads the model and branch;
// merges those into the session's ledger entry, creating it if the agent did
// not write one. It stores NO message text. Read this file before installing
// it as a hook and keep it that way.
//
// Always exits 0: a hook must never break the session it reports on.
import { existsSync, readFileSync } from 'node:fs';
import {
  AUTOMATED_PATTERNS, SCHEMA, currentBranch, entryId, findBySession, findRepoRoot, gitUserName,
  ledgerDir, loadEnv, merge, parseArgs, repoName, writeEntry,
} from './ledger-lib.mjs';

main().catch((err) => {
  process.stderr.write(`ledger-from-transcript: ${err.message}\n`);
  process.exit(0);
});

async function main() {
  const args = parseArgs(process.argv.slice(2));
  let payload = {};
  if (!args.transcript && !process.stdin.isTTY) {
    const raw = await readStdin();
    if (raw.trim()) {
      try { payload = JSON.parse(raw); } catch { /* not JSON; fall through to flags */ }
    }
  }
  const transcript = String(args.transcript || payload.transcript_path || '');
  const sessionId = String(args.session_id || payload.session_id || '');
  const cwd = String(args.cwd || payload.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd());
  if (!transcript || !existsSync(transcript)) {
    process.stderr.write('ledger-from-transcript: no transcript to read; nothing written\n');
    return;
  }

  const counts = countTranscript(readFileSync(transcript, 'utf8'));
  if (!counts.first) {
    process.stderr.write('ledger-from-transcript: transcript held no timestamped turns; nothing written\n');
    return;
  }

  const repoRoot = findRepoRoot(cwd);
  const env = loadEnv(repoRoot);
  const dir = args.dir ? String(args.dir) : ledgerDir(repoRoot, env);
  const agent = 'claude-code';
  const existing = findBySession(dir, sessionId);

  const incoming = {
    schema: SCHEMA,
    id: existing?.id || entryId(counts.first, agent, sessionId || undefined),
    session_id: sessionId || undefined,
    agent,
    model: counts.model || undefined,
    surface: process.env.CLAUDE_CODE_REMOTE ? 'web' : 'cli',
    operator: existing?.operator || (counts.automated > 0 && counts.operator === 0 ? 'unattended' : gitUserName(repoRoot) || 'unknown'),
    repo: repoName(repoRoot) || undefined,
    branch: counts.branch || currentBranch(repoRoot) || undefined,
    started_at: existing?.started_at || counts.first,
    ended_at: counts.last,
    task: existing?.task || '',
    outcome: existing?.outcome || 'unknown',
    turns: { operator: counts.operator, agent: counts.agent, automated: counts.automated },
    tool_calls: counts.toolCalls,
    source: ['hook'],
  };
  if (!existing) {
    incoming.task = '(no wrap-up entry; counts only)';
    incoming.corrections = [];
    incoming.blocked_on_person = [];
    incoming.checks_failed = [];
    incoming.rules_broken = [];
  }
  const entry = merge(existing || {}, incoming);
  const path = writeEntry(dir, entry);
  if (!args.quiet) process.stderr.write(`ledger-from-transcript: ${existing ? 'merged counts into' : 'wrote'} ${path}\n`);
}

// Counts only. Nothing from message content leaves this function except a
// yes/no on whether a turn matched an automation envelope.
export function countTranscript(text) {
  const c = { operator: 0, agent: 0, automated: 0, toolCalls: 0, first: null, last: null, model: '', branch: '' };
  for (const line of text.split('\n')) {
    if (!line.trim()) continue;
    let ev;
    try { ev = JSON.parse(line); } catch { continue; }
    if (!ev || typeof ev !== 'object') continue;
    if (ev.timestamp) {
      const t = new Date(ev.timestamp);
      if (!Number.isNaN(t.getTime())) {
        const iso = t.toISOString();
        if (!c.first || iso < c.first) c.first = iso;
        if (!c.last || iso > c.last) c.last = iso;
      }
    }
    if (ev.gitBranch && !c.branch) c.branch = String(ev.gitBranch);
    const msg = ev.message;
    if (ev.type === 'assistant' && msg) {
      c.agent++;
      if (msg.model && !c.model) c.model = String(msg.model);
      for (const block of blocks(msg.content)) if (block?.type === 'tool_use') c.toolCalls++;
    } else if (ev.type === 'user' && msg && !ev.isMeta) {
      const content = msg.content;
      const bs = blocks(content);
      const hasToolResult = bs.some((b) => b?.type === 'tool_result');
      const texts = typeof content === 'string' ? [content] : bs.filter((b) => b?.type === 'text').map((b) => String(b.text || ''));
      if (hasToolResult && texts.length === 0) continue; // a tool result, not a turn
      if (texts.length === 0) continue;
      const joined = texts.join('\n');
      if (AUTOMATED_PATTERNS.some((re) => re.test(joined))) c.automated++;
      else c.operator++;
    }
  }
  return c;
}

function blocks(content) {
  return Array.isArray(content) ? content : [];
}

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (d) => { data += d; });
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', () => resolve(data));
    setTimeout(() => resolve(data), 2000).unref();
  });
}
