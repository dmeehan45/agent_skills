// Shared helpers for the agent action ledger. Used by ledger-append.mjs,
// ledger-from-transcript.mjs and ledger-summary.mjs. No message text ever
// passes through here: the ledger holds metadata and the operator's own
// instructions, paraphrased, and nothing else.
import { createHash, randomBytes } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

export const SCHEMA = 1;

export const OUTCOMES = [
  'merged', 'pr-open', 'pushed-no-pr', 'local-only', 'abandoned', 'question-only', 'unknown',
];

export function git(args, cwd) {
  try {
    return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return '';
  }
}

export function findRepoRoot(start = process.cwd()) {
  const root = git(['rev-parse', '--show-toplevel'], start);
  return root || resolve(start);
}

// Parses .agents/retro.env: KEY=value lines, optional quotes, # comments.
export function loadEnv(repoRoot) {
  const file = join(repoRoot, '.agents', 'retro.env');
  const env = {};
  if (!existsSync(file)) return env;
  for (const raw of readFileSync(file, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const m = line.match(/^(?:export\s+)?([A-Z0-9_]+)=(.*)$/);
    if (!m) continue;
    let v = m[2].trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    env[m[1]] = v;
  }
  return env;
}

export function ledgerDir(repoRoot, env = loadEnv(repoRoot)) {
  return resolve(repoRoot, env.RETRO_LEDGER_DIR || '.agents/ledger');
}

export function hex4(sessionId) {
  if (sessionId) return createHash('sha1').update(String(sessionId)).digest('hex').slice(0, 4);
  return randomBytes(2).toString('hex');
}

// 2026-10-20T02:15:33Z -> 2026-10-20T0215Z
export function compactTime(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) throw new Error(`bad timestamp: ${iso}`);
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}T${p(d.getUTCHours())}${p(d.getUTCMinutes())}Z`;
}

export function entryId(startedAt, agent, sessionId) {
  return `${compactTime(startedAt)}-${slug(agent)}-${hex4(sessionId)}`;
}

export function slug(s) {
  return String(s || 'agent').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'agent';
}

export function entryPath(dir, id) {
  return join(dir, id.slice(0, 4), `${id}.json`);
}

export function readAll(dir) {
  const out = [];
  if (!existsSync(dir)) return out;
  const walk = (d) => {
    for (const name of readdirSync(d)) {
      const p = join(d, name);
      const st = statSync(p);
      if (st.isDirectory()) walk(p);
      else if (name.endsWith('.json')) {
        try {
          const e = JSON.parse(readFileSync(p, 'utf8'));
          if (e && typeof e === 'object') out.push({ ...e, _path: p });
        } catch (err) {
          process.stderr.write(`ledger: skipping unreadable ${p}: ${err.message}\n`);
        }
      }
    }
  };
  walk(dir);
  return out;
}

// The hook and the agent may both write an entry for one session. The agent
// knows what happened; the hook knows the counts. Find by session id first,
// then by the id's hex suffix.
export function findBySession(dir, sessionId) {
  if (!sessionId) return null;
  const suffix = `-${hex4(sessionId)}.json`;
  for (const e of readAll(dir)) {
    if (e.session_id === sessionId) return e;
    if (e._path.endsWith(suffix)) return e;
  }
  return null;
}

const ARRAY_FIELDS = ['corrections', 'blocked_on_person', 'checks_failed', 'rules_read', 'rules_broken', 'source'];

export function merge(existing, incoming) {
  const out = { ...existing };
  for (const [k, v] of Object.entries(incoming)) {
    if (k === '_path') continue;
    if (v === undefined || v === null || v === '') continue;
    if (ARRAY_FIELDS.includes(k)) {
      const seen = new Set((out[k] || []).map((x) => JSON.stringify(x)));
      out[k] = [...(out[k] || [])];
      for (const item of v) if (!seen.has(JSON.stringify(item))) { out[k].push(item); seen.add(JSON.stringify(item)); }
    } else if (k === 'turns' && typeof v === 'object') {
      out.turns = { ...(out.turns || {}), ...v };
    } else if (k === 'outcome' && out.outcome && out.outcome !== 'unknown' && v === 'unknown') {
      // never downgrade a known outcome
    } else if (k === 'task' && out.task && !v) {
      // keep the agent's task line
    } else {
      out[k] = v;
    }
  }
  return out;
}

export function writeEntry(dir, entry) {
  const { _path, ...clean } = entry;
  const ordered = orderKeys(clean);
  const path = _path || entryPath(dir, ordered.id);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(ordered, null, 2) + '\n');
  return path;
}

const KEY_ORDER = [
  'schema', 'id', 'session_id', 'agent', 'model', 'surface', 'operator', 'repo', 'branch',
  'started_at', 'ended_at', 'task', 'outcome', 'pr', 'commits', 'turns', 'tool_calls',
  'corrections', 'blocked_on_person', 'checks_failed', 'rules_read', 'rules_broken',
  'learned', 'cost_note', 'source',
];

function orderKeys(e) {
  const out = {};
  for (const k of KEY_ORDER) if (e[k] !== undefined) out[k] = e[k];
  for (const k of Object.keys(e)) if (!(k in out)) out[k] = e[k];
  return out;
}

export function repoName(repoRoot) {
  const url = git(['remote', 'get-url', 'origin'], repoRoot);
  const m = url.match(/[:/]([^/:]+\/[^/]+?)(?:\.git)?$/);
  return m ? m[1] : '';
}

export function currentBranch(repoRoot) {
  return git(['rev-parse', '--abbrev-ref', 'HEAD'], repoRoot);
}

export function gitUserName(repoRoot) {
  return git(['config', 'user.name'], repoRoot);
}

// Words that are not the operator's instructions: tool results and harness
// envelopes. The hook uses this to tell a person's turn from an automated one.
export const AUTOMATED_PATTERNS = [
  /<wake\s+reason=/i,
  /<task-notification/i,
  /<webhook-payload/i,
  /<child-session-event/i,
  /scheduled (task|trigger)/i,
  /<<autonomous-loop/i,
];

export function parseWindow(args, defaultDays = 14) {
  const sinceArg = args.since;
  const untilArg = args.until;
  const until = untilArg ? new Date(untilArg) : new Date();
  let since;
  if (!sinceArg) since = new Date(until.getTime() - defaultDays * 86400000);
  else if (/^\d+d$/.test(sinceArg)) since = new Date(until.getTime() - parseInt(sinceArg, 10) * 86400000);
  else since = new Date(sinceArg);
  if (Number.isNaN(since.getTime()) || Number.isNaN(until.getTime())) throw new Error('bad --since/--until');
  return { since, until };
}

export function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2).replace(/-/g, '_');
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) out[key] = true;
      else {
        if (out[key] === undefined) out[key] = next;
        else if (Array.isArray(out[key])) out[key].push(next);
        else out[key] = [out[key], next];
        i++;
      }
    } else out._.push(a);
  }
  return out;
}

export function asArray(v) {
  if (v === undefined || v === true) return [];
  return Array.isArray(v) ? v : [v];
}
