#!/usr/bin/env node
/**
 * walk_journeys.mjs — walk a product's journeys in a real browser and record
 * what a screenshot cannot show.
 *
 * For every named capture, at every viewport, it saves a screenshot and a JSON
 * probe: acknowledgement latency of the last action, cumulative layout shift,
 * controls with no visible focus or hover style, what still animates under
 * reduced motion, horizontal overflow, targets under 44px, fixed-element
 * coverage, primary-looking actions and whether one is above the fold, the
 * container and copy inventory, unlabelled fields, images without alt or
 * dimensions, heading-order skips, waiting indicators still present, and
 * console and network errors.
 *
 * Read-only by default. The allowed steps are goto, scroll, hover, wait,
 * waitFor, and capture. The first click, fill, press, or select stops the
 * journey and says why. Pass --interact only against a staging environment,
 * a local build, or a seeded fixture with a dedicated test account.
 *
 * Usage:
 *   node walk_journeys.mjs --plan journeys.json --out per-evidence
 *   node walk_journeys.mjs --plan journeys.json --out per-evidence --interact --viewport all
 *
 * Flags:
 *   --plan <file>           JSON journey plan (see references/journeys.md).
 *   --out <dir>             Output directory (default: per-evidence).
 *   --interact              Allow click, fill, press, and select steps.
 *   --viewport <names>      phone,tablet,laptop,desktop or "all" (default: phone,laptop).
 *   --journey <id>          Repeatable. Walk only these journey ids.
 *   --base-url <url>        Override the plan's baseUrl.
 *   --storage-state <file>  Playwright storageState for authenticated journeys.
 *   --timeout <ms>          Navigation and selector timeout (default 30000).
 *   --no-full-page          Skip full-page screenshots (viewport only).
 *   --focus-probes <n>      Max Tab presses per capture (default 60).
 *   --hover-probes <n>      Max hover probes per capture on pointer viewports (default 25).
 *   --ack-wait <ms>         How long to wait for an action to be acknowledged (default 3000).
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { loadPlaywright, dismissConsent, resolveTarget } from './lib/browser.mjs';

const VIEWPORTS = {
  phone: { name: 'phone', width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  tablet: { name: 'tablet', width: 820, height: 1180, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  laptop: { name: 'laptop', width: 1280, height: 800, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
  desktop: { name: 'desktop', width: 1728, height: 1117, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
};

const INTERACTION_KEYS = ['click', 'fill', 'press', 'select'];
const STEP_KEYS = ['goto', 'scroll', 'hover', 'wait', 'capture', ...INTERACTION_KEYS];

// ---------------------------------------------------------------- arg parsing

function parseArgs(argv) {
  const out = { out: 'per-evidence', interact: false, viewports: [], journeys: [], timeout: 30000, fullPage: true, focusProbes: 60, hoverProbes: 25, ackWait: 3000 };
  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];
    const next = () => {
      i += 1;
      if (i >= argv.length) throw new Error(`Flag ${a} needs a value`);
      return argv[i];
    };
    if (a === '--plan') out.plan = next();
    else if (a === '--out') out.out = next();
    else if (a === '--interact') out.interact = true;
    else if (a === '--viewport') out.viewports = next().split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--journey') out.journeys.push(next());
    else if (a === '--base-url') out.baseUrl = next();
    else if (a === '--storage-state') out.storageState = next();
    else if (a === '--timeout') out.timeout = Number(next());
    else if (a === '--no-full-page') out.fullPage = false;
    else if (a === '--focus-probes') out.focusProbes = Number(next());
    else if (a === '--hover-probes') out.hoverProbes = Number(next());
    else if (a === '--ack-wait') out.ackWait = Number(next());
    else if (a === '--help' || a === '-h') out.help = true;
    else throw new Error(`Unknown flag: ${a}`);
  }
  return out;
}

function usage() {
  const src = fs.readFileSync(new URL(import.meta.url), 'utf8');
  const m = src.match(/\/\*\*([\s\S]*?)\*\//);
  return m ? m[1].replace(/^ \* ?/gm, '') : 'See the header comment for usage.';
}

// --------------------------------------------------------------- the plan

function loadPlan(args) {
  if (!args.plan) throw new Error('No plan. Pass --plan journeys.json (see assets/journey-plan.example.json).');
  const raw = JSON.parse(fs.readFileSync(args.plan, 'utf8'));
  const plan = {
    project: raw.project || path.basename(args.plan, '.json'),
    baseUrl: args.baseUrl || raw.baseUrl || null,
    journeys: [],
    viewports: [],
  };

  const wantedViewports = args.viewports.length ? args.viewports : raw.viewports?.length ? raw.viewports : ['phone', 'laptop'];
  const names = wantedViewports.includes('all') ? Object.keys(VIEWPORTS) : wantedViewports;
  plan.viewports = names.map((v) => {
    if (typeof v === 'object') return v;
    if (!VIEWPORTS[v]) throw new Error(`Unknown viewport "${v}". Use phone, tablet, laptop, desktop, or all.`);
    return VIEWPORTS[v];
  });

  for (const [i, j] of (raw.journeys || []).entries()) {
    if (!j || typeof j !== 'object') throw new Error(`Journey ${i} is not an object`);
    const id = j.id || `journey-${i + 1}`;
    if (args.journeys.length && !args.journeys.includes(id)) continue;
    const steps = (j.steps || []).map((s, k) => normaliseStep(s, id, k));
    plan.journeys.push({ id, intent: j.intent || '', steps });
  }
  if (!plan.journeys.length) throw new Error('No journeys to walk.');
  return plan;
}

function normaliseStep(step, journeyId, index) {
  if (typeof step === 'string') return { goto: step, capture: slug(step) || `step-${index + 1}` };
  const keys = Object.keys(step).filter((k) => STEP_KEYS.includes(k));
  if (!keys.length) throw new Error(`Journey ${journeyId} step ${index + 1} has no recognised action (${STEP_KEYS.join(', ')})`);
  const action = keys.find((k) => k !== 'capture') || 'capture';
  const out = { action, ...step };
  if (INTERACTION_KEYS.includes(action)) out.interaction = true;
  if (action === 'fill' && (typeof step.fill !== 'object' || !step.fill.selector)) {
    throw new Error(`Journey ${journeyId} step ${index + 1}: fill needs { selector, value }`);
  }
  if (action === 'select' && (typeof step.select !== 'object' || !step.select.selector)) {
    throw new Error(`Journey ${journeyId} step ${index + 1}: select needs { selector, value }`);
  }
  return out;
}

function slug(s) {
  return String(s)
    .replace(/^https?:\/\//, '')
    .replace(/[^a-z0-9]+/gi, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase()
    .slice(0, 50);
}

// -------------------------------------------------------- page instrumentation

/**
 * Installed before any page script in every document. Records layout shift
 * and LCP from navigation, and the first DOM mutation after an armed action,
 * so acknowledgement latency is read from the page's own clock.
 */
const INIT_SCRIPT = `(() => {
  const per = { cls: 0, lcp: null, armedAt: null, firstMutationAt: null };
  window.__per = per;
  per.arm = () => { per.armedAt = performance.now(); per.firstMutationAt = null; };
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) if (!e.hadRecentInput) per.cls += e.value;
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (e) {}
  try {
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const last = entries[entries.length - 1];
      if (last) per.lcp = last.startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (e) {}
  const observe = () => {
    try {
      new MutationObserver(() => {
        if (per.armedAt !== null && per.firstMutationAt === null) per.firstMutationAt = performance.now();
      }).observe(document.documentElement, { childList: true, subtree: true, attributes: true, characterData: true });
    } catch (e) {}
  };
  if (document.documentElement) observe(); else document.addEventListener('readystatechange', observe, { once: true });
})();`;

// ------------------------------------------------------------ the page probe

/**
 * Runs inside the page. Must stay self-contained (no closure over Node scope)
 * because Playwright serialises it.
 */
function pageProbe({ touch }) {
  const MAX = 4000;
  const VAGUE = /^(submit|ok|okay|continue|next|go|yes|no|click here|learn more|read more|more|done|proceed)$/i;
  const INTERACTIVE = 'a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=link], [role=tab], [role=menuitem], [role=checkbox], [role=radio], [role=switch], [tabindex]:not([tabindex="-1"])';

  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const doc = document.documentElement;
  const all = Array.from(document.body ? document.body.querySelectorAll('*') : []).slice(0, MAX);

  const text = (el) => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
  const parseColor = (str) => {
    const m = String(str || '').match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const visible = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const describe = (el) => {
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    const t = text(el).slice(0, 40);
    return `${el.tagName.toLowerCase()}${id}${cls}${t ? ` "${t}"` : ''}`;
  };
  const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    return { x: Math.round(r.left), y: Math.round(r.top + window.scrollY), w: Math.round(r.width), h: Math.round(r.height) };
  };

  // ---- headings and landmarks
  const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).filter(visible);
  let headingOrderSkips = 0;
  let prev = 0;
  const headingList = [];
  for (const h of headings) {
    const level = Number(h.tagName[1]);
    if (prev && level > prev + 1) headingOrderSkips += 1;
    prev = level;
    if (headingList.length < 40) headingList.push({ level, text: text(h).slice(0, 80) });
  }
  const landmarks = {
    main: !!document.querySelector('main, [role=main]'),
    nav: !!document.querySelector('nav, [role=navigation]'),
    header: !!document.querySelector('header, [role=banner]'),
    footer: !!document.querySelector('footer, [role=contentinfo]'),
  };

  // ---- interactive elements
  const interactive = Array.from(document.querySelectorAll(INTERACTIVE)).filter(visible).slice(0, 600);
  const enabled = interactive.filter((el) => !el.disabled && el.getAttribute('aria-disabled') !== 'true');
  const bodyBg = parseColor(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };

  const primaryLike = [];
  const under44 = [];
  for (const el of enabled) {
    const cs = getComputedStyle(el);
    const bg = parseColor(cs.backgroundColor);
    const r = el.getBoundingClientRect();
    const label = text(el) || el.getAttribute('aria-label') || '';
    const filled = bg && bg.a > 0.5 && (Math.abs(bg.r - bodyBg.r) + Math.abs(bg.g - bodyBg.g) + Math.abs(bg.b - bodyBg.b)) > 120;
    const isAction = el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || (el.tagName === 'A' && filled);
    if (filled && isAction && label && r.width >= 60 && r.height >= 28) {
      primaryLike.push({ el: describe(el), rect: rectOf(el), aboveFold: r.top >= 0 && r.bottom <= vh });
    }
    if (r.width < 44 || r.height < 44) {
      if (under44.length < 200) under44.push({ el: describe(el), w: Math.round(r.width), h: Math.round(r.height) });
    }
  }

  // ---- fixed and sticky elements, and how much of the viewport they occupy
  const fixed = [];
  let fixedArea = 0;
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    const ix = Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0));
    const iy = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
    const area = ix * iy;
    if (area <= 0) continue;
    // Skip children of an already-counted fixed ancestor.
    if (fixed.some((f) => f.node.contains(el))) continue;
    fixed.push({ node: el, el: describe(el), position: cs.position, coveragePct: Math.round((area / (vw * vh)) * 1000) / 10 });
    fixedArea += area;
  }

  // ---- containers: what carries the hierarchy
  const isContainer = (el, cs) => {
    const r = el.getBoundingClientRect();
    if (r.width * r.height < 2000) return false;
    const borderW = ['Top', 'Right', 'Bottom', 'Left'].reduce((n, s) => n + parseFloat(cs[`border${s}Width`] || 0), 0);
    const borderC = parseColor(cs.borderTopColor);
    const bordered = borderW > 0 && borderC && borderC.a > 0 && cs.borderTopStyle !== 'none';
    const shadowed = cs.boxShadow && cs.boxShadow !== 'none';
    const bg = parseColor(cs.backgroundColor);
    const parentBg = el.parentElement ? parseColor(getComputedStyle(el.parentElement).backgroundColor) : null;
    const filled = bg && bg.a > 0 && (!parentBg || parentBg.a === 0 || Math.abs(bg.r - parentBg.r) + Math.abs(bg.g - parentBg.g) + Math.abs(bg.b - parentBg.b) > 8);
    const padded = parseFloat(cs.paddingTop || 0) + parseFloat(cs.paddingLeft || 0) > 8;
    return { bordered: !!bordered, shadowed: !!shadowed, card: !!(filled && padded && parseFloat(cs.borderTopLeftRadius || 0) > 0) };
  };
  const containers = { bordered: 0, shadowed: 0, cards: 0, pills: 0, icons: 0, headings: headings.length, maxNestDepth: 0, deepest: null };
  const containerNodes = new Set();
  for (const el of all) {
    if (!visible(el)) continue;
    const cs = getComputedStyle(el);
    const c = isContainer(el, cs);
    if (c) {
      if (c.bordered) containers.bordered += 1;
      if (c.shadowed) containers.shadowed += 1;
      if (c.card) containers.cards += 1;
      if (c.bordered || c.shadowed || c.card) containerNodes.add(el);
    }
    const r = el.getBoundingClientRect();
    const radius = parseFloat(cs.borderTopLeftRadius || 0);
    const bg = parseColor(cs.backgroundColor);
    if (radius >= r.height / 2 - 1 && r.height <= 40 && r.width > r.height && bg && bg.a > 0 && text(el).length > 0 && text(el).length < 30 && el.children.length <= 2) {
      containers.pills += 1;
    }
    if (el.tagName === 'svg' || el.tagName === 'SVG' || (el.tagName === 'IMG' && r.width <= 32 && r.height <= 32) || /\b(icon|lucide|feather|fa-|material-icons)\b/i.test(String(el.className))) {
      containers.icons += 1;
    }
  }
  for (const node of containerNodes) {
    let depth = 1;
    let p = node.parentElement;
    while (p) {
      if (containerNodes.has(p)) depth += 1;
      p = p.parentElement;
    }
    if (depth > containers.maxNestDepth) {
      containers.maxNestDepth = depth;
      containers.deepest = describe(node);
    }
  }

  // ---- copy
  const actions = [];
  const vagueActions = [];
  for (const el of enabled) {
    if (!(el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || el.tagName === 'A' || (el.tagName === 'INPUT' && /submit|button/.test(el.type)))) continue;
    const label = (el.tagName === 'INPUT' ? el.value : text(el)) || el.getAttribute('aria-label') || '';
    if (!label) continue;
    if (actions.length < 60) actions.push(label.slice(0, 60));
    if (VAGUE.test(label.trim())) vagueActions.push(label.trim());
  }
  const helperText = [];
  const placeholders = [];
  let smallText = 0;
  for (const el of all) {
    if (!visible(el)) continue;
    if (el.placeholder && placeholders.length < 30) placeholders.push(el.placeholder.slice(0, 80));
    const hasOwnText = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (!hasOwnText) continue;
    const size = parseFloat(getComputedStyle(el).fontSize || 0);
    if (size && size < 12) smallText += 1;
    if (size && size <= 13 && text(el).length > 24 && !el.closest(INTERACTIVE) && helperText.length < 30) helperText.push(text(el).slice(0, 120));
  }
  const liveRegions = Array.from(document.querySelectorAll('[role=status], [role=alert], [aria-live]'))
    .filter(visible)
    .map((el) => text(el).slice(0, 120))
    .filter(Boolean)
    .slice(0, 10);

  // ---- forms
  const fields = Array.from(document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]), select, textarea')).filter(visible);
  const unlabelled = [];
  for (const f of fields) {
    const labelled =
      (f.id && document.querySelector(`label[for="${CSS.escape(f.id)}"]`)) ||
      f.closest('label') ||
      f.getAttribute('aria-label') ||
      f.getAttribute('aria-labelledby') ||
      f.getAttribute('title');
    if (!labelled && unlabelled.length < 40) unlabelled.push(describe(f) + (f.placeholder ? ` placeholder="${f.placeholder.slice(0, 40)}"` : ''));
  }

  // ---- images
  const imgs = Array.from(document.querySelectorAll('img')).filter(visible);
  const imagesMissingAlt = imgs.filter((i) => !i.hasAttribute('alt') && i.getAttribute('role') !== 'presentation').length;
  const imagesMissingDimensions = imgs.filter((i) => !(i.getAttribute('width') && i.getAttribute('height')) && !/aspect-ratio/.test(getComputedStyle(i).cssText || '') && getComputedStyle(i).aspectRatio === 'auto').length;

  // ---- waiting indicators still present
  const waiting = Array.from(document.querySelectorAll('[role=progressbar], [aria-busy="true"], [class*="skeleton" i], [class*="spinner" i], [class*="loading" i], [class*="shimmer" i], [id*="spinner" i]'))
    .filter(visible)
    .map(describe)
    .slice(0, 10);

  // ---- motion inventory from computed style
  const motion = { animated: 0, longTransitions: 0, infiniteAnimations: 0, samples: [] };
  for (const el of all) {
    const cs = getComputedStyle(el);
    const animName = cs.animationName;
    const animDur = parseFloat(cs.animationDuration || 0) * (String(cs.animationDuration).endsWith('ms') ? 1 : 1000);
    if (animName && animName !== 'none' && animDur > 0) {
      motion.animated += 1;
      if (cs.animationIterationCount === 'infinite' && cs.animationPlayState !== 'paused' && visible(el)) {
        motion.infiniteAnimations += 1;
        if (motion.samples.length < 8) motion.samples.push(`${describe(el)} animation ${animName} infinite`);
      }
    }
    const tDur = String(cs.transitionDuration || '')
      .split(',')
      .map((d) => parseFloat(d) * (d.trim().endsWith('ms') ? 1 : 1000))
      .filter((n) => !Number.isNaN(n));
    const maxT = tDur.length ? Math.max(...tDur) : 0;
    if (maxT > 400) {
      motion.longTransitions += 1;
      if (motion.samples.length < 8) motion.samples.push(`${describe(el)} transition ${Math.round(maxT)}ms`);
    }
  }

  // ---- baseline for focus and hover probing (kept on window for the Node side)
  const snapshot = (el) => {
    const cs = getComputedStyle(el);
    return [cs.outlineWidth, cs.outlineStyle, cs.outlineColor, cs.boxShadow, cs.borderTopColor, cs.backgroundColor, cs.color, cs.textDecorationLine, cs.transform, cs.opacity].join('|');
  };
  window.__perInteractive = enabled;
  window.__perBaseline = enabled.map(snapshot);
  window.__perSnapshot = snapshot;
  window.__perDescribe = describe;

  return {
    url: location.href,
    title: document.title,
    viewportMetrics: { width: vw, height: vh, scrollWidth: doc.scrollWidth, scrollHeight: doc.scrollHeight },
    horizontalOverflow: doc.scrollWidth > vw + 1,
    h1Count: headings.filter((h) => h.tagName === 'H1').length,
    headingOrderSkips,
    headings: headingList,
    landmarks,
    interactiveCount: interactive.length,
    actionableCount: enabled.length,
    primaryLikeActions: primaryLike.slice(0, 12),
    primaryAboveFold: primaryLike.some((p) => p.aboveFold),
    targetsUnder44: { count: under44.length, touchViewport: touch, sample: under44.slice(0, 12) },
    fixedCoveragePct: Math.round((Math.min(fixedArea, vw * vh) / (vw * vh)) * 1000) / 10,
    fixedElements: fixed.map(({ node, ...rest }) => rest).slice(0, 12),
    containers,
    copy: { actions, vagueActions, helperText, placeholders, liveRegions, wordCount: text(document.body).split(/\s+/).filter(Boolean).length },
    smallText,
    unlabelledFields: { count: unlabelled.length, sample: unlabelled.slice(0, 12) },
    imagesMissingAlt,
    imagesMissingDimensions,
    waitingIndicators: waiting,
    motion,
  };
}

// ------------------------------------------------- focus, hover, reduced motion

async function probeFocus(page, maxProbes) {
  const missing = [];
  const seen = new Set();
  let probed = 0;
  let emptyTabs = 0;
  await page.evaluate(() => {
    if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
  });
  for (let i = 0; i < maxProbes + 2; i += 1) {
    await page.keyboard.press('Tab');
    const r = await page
      .evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) return { end: true };
        const idx = (window.__perInteractive || []).indexOf(el);
        return { idx, desc: window.__perDescribe ? window.__perDescribe(el) : el.tagName, snap: window.__perSnapshot ? window.__perSnapshot(el) : null };
      })
      .catch(() => ({ end: true }));
    if (r.end) {
      // Focus may sit outside the document after an earlier probe; allow it to re-enter.
      if (probed === 0 && emptyTabs < 2) {
        emptyTabs += 1;
        continue;
      }
      break;
    }
    if (seen.has(r.desc + r.idx)) break; // wrapped around
    seen.add(r.desc + r.idx);
    probed += 1;
    if (r.idx >= 0 && r.snap !== null) {
      const changed = await page.evaluate((idx) => window.__perBaseline[idx] !== window.__perSnapshot(window.__perInteractive[idx]), r.idx);
      if (!changed) missing.push(r.desc);
    }
  }
  await page.evaluate(() => document.activeElement && document.activeElement.blur()).catch(() => {});
  return { probed, controlsWithoutFocusStyle: missing };
}

async function probeHover(page, maxProbes) {
  const missing = [];
  const count = await page.evaluate(() => (window.__perInteractive || []).length);
  const n = Math.min(count, maxProbes);
  let probed = 0;
  for (let i = 0; i < n; i += 1) {
    const target = await page
      .evaluate((idx) => {
        const el = window.__perInteractive[idx];
        if (!el) return null;
        el.scrollIntoView({ block: 'center', inline: 'center' });
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return null;
        return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      }, i)
      .catch(() => null);
    if (!target) continue;
    await page.mouse.move(target.x, target.y);
    await page.waitForTimeout(80);
    const r = await page
      .evaluate((idx) => {
        const el = window.__perInteractive[idx];
        const r = el.getBoundingClientRect();
        const hit = document.elementFromPoint ? document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2) : null;
        const hovered = hit ? el.contains(hit) || hit.contains(el) : true;
        return { hovered, changed: window.__perBaseline[idx] !== window.__perSnapshot(el), desc: window.__perDescribe(el) };
      }, i)
      .catch(() => null);
    if (!r || !r.hovered) continue;
    probed += 1;
    if (!r.changed) missing.push(r.desc);
  }
  await page.mouse.move(0, 0);
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
  return { probed, controlsWithoutHoverStyle: missing };
}

async function probeReducedMotion(page) {
  const running = () =>
    page.evaluate(() => {
      const anims = (document.getAnimations ? document.getAnimations() : []).filter((a) => a.playState === 'running');
      return {
        count: anims.length,
        sample: anims.slice(0, 8).map((a) => {
          const t = a.effect && a.effect.target;
          const name = a.animationName || a.transitionProperty || a.id || 'animation';
          return `${t ? window.__perDescribe(t) : '?'} ${name}`;
        }),
      };
    });
  const before = await running().catch(() => ({ count: 0, sample: [] }));
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.waitForTimeout(150);
  const after = await running().catch(() => ({ count: 0, sample: [] }));
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  return { runningAnimations: before.count, movesUnderReducedMotion: after.count, sample: after.sample };
}

// ------------------------------------------------------------------ walking

async function performStep(page, step, plan, args, ctx) {
  const t = args.timeout;
  switch (step.action) {
    case 'goto': {
      const url = resolveTarget(step.goto, plan.baseUrl);
      ctx.lastAction = null;
      await page.goto(url, { waitUntil: 'load', timeout: t });
      await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
      const consent = await dismissConsent(page);
      if (consent.dismissed) ctx.notes.push(`consent dismissed (${consent.method})`);
      return;
    }
    case 'scroll': {
      const v = step.scroll;
      await page.evaluate((v) => {
        if (v === 'bottom') window.scrollTo(0, document.documentElement.scrollHeight);
        else if (v === 'top') window.scrollTo(0, 0);
        else window.scrollBy(0, Number(v) || 0);
      }, v);
      await page.waitForTimeout(300);
      return;
    }
    case 'hover':
      await page.hover(step.hover, { timeout: t });
      await page.waitForTimeout(120);
      return;
    case 'wait':
      await page.waitForTimeout(Number(step.wait) || 0);
      return;
    case 'capture':
      return;
    case 'click':
    case 'press':
    case 'select':
    case 'fill': {
      const t0 = Date.now();
      let navAt = null;
      const onNav = (frame) => {
        if (frame === page.mainFrame() && navAt === null) navAt = Date.now();
      };
      page.on('framenavigated', onNav);
      await page.evaluate(() => window.__per && window.__per.arm()).catch(() => {});
      if (step.action === 'click') await page.click(step.click, { timeout: t });
      else if (step.action === 'press') await page.keyboard.press(step.press);
      else if (step.action === 'select') await page.selectOption(step.select.selector, step.select.value, { timeout: t });
      else await page.fill(step.fill.selector, String(step.fill.value), { timeout: t });
      // Poll the page's own clock for the first DOM change after the action, or a navigation.
      let mut = null;
      const deadline = Date.now() + args.ackWait;
      while (step.action !== 'fill' && Date.now() < deadline) {
        mut = await page.evaluate(() => (window.__per ? { armedAt: window.__per.armedAt, first: window.__per.firstMutationAt } : null)).catch(() => null);
        if ((mut && mut.armedAt !== null && mut.first !== null) || navAt !== null) break;
        await page.waitForTimeout(25);
      }
      const settleStart = Date.now();
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      const settleMs = Math.max(0, Date.now() - settleStart - 500);
      page.off('framenavigated', onNav);
      let ackMs = null;
      let ackSource = null;
      if (mut && mut.armedAt !== null && mut.first !== null) {
        ackMs = Math.round(mut.first - mut.armedAt);
        ackSource = 'mutation';
      } else if (navAt !== null) {
        ackMs = navAt - t0;
        ackSource = 'navigation';
      }
      if (step.action === 'fill') {
        ackMs = null;
        ackSource = 'not-measured-for-fill';
      } else if (ackMs === null) {
        ackSource = `none-within-${args.ackWait}ms`;
      }
      ctx.lastAction = { action: step.action, target: step[step.action]?.selector || step[step.action], ackMs, ackSource, settleMs };
      return;
    }
    default:
      throw new Error(`Unknown step action ${step.action}`);
  }
}

async function capture(page, { plan, args, viewport, journey, name, index, ctx, dir }) {
  const stem = `${String(index).padStart(2, '0')}-${slug(name) || 'capture'}`;
  await page.waitForTimeout(200);
  const files = {};
  try {
    await page.screenshot({ path: path.join(dir, `${stem}.png`), fullPage: false });
    files.viewport = path.join(dir, `${stem}.png`);
    if (args.fullPage) {
      await page.screenshot({ path: path.join(dir, `${stem}.full.png`), fullPage: true });
      files.fullPage = path.join(dir, `${stem}.full.png`);
    }
  } catch (err) {
    ctx.notes.push(`screenshot failed at ${stem}: ${err.message}`);
  }

  const probe = await page.evaluate(pageProbe, { touch: viewport.hasTouch });
  const perf = await page.evaluate(() => (window.__per ? { cls: window.__per.cls, lcp: window.__per.lcp } : null)).catch(() => null);
  const focus = await probeFocus(page, args.focusProbes).catch((e) => ({ probed: 0, controlsWithoutFocusStyle: [], error: e.message }));
  const hover = viewport.hasTouch ? { probed: 0, controlsWithoutHoverStyle: [], skipped: 'touch viewport' } : await probeHover(page, args.hoverProbes).catch((e) => ({ probed: 0, controlsWithoutHoverStyle: [], error: e.message }));
  const reduced = await probeReducedMotion(page).catch((e) => ({ runningAnimations: null, movesUnderReducedMotion: null, error: e.message }));

  const record = {
    project: plan.project,
    journey: journey.id,
    intent: journey.intent,
    viewport: viewport.name,
    capture: name,
    index,
    files,
    lastAction: ctx.lastAction,
    ackMs: ctx.lastAction ? ctx.lastAction.ackMs : null,
    cls: perf ? Math.round(perf.cls * 1000) / 1000 : null,
    lcpMs: perf && perf.lcp !== null ? Math.round(perf.lcp) : null,
    focus,
    hover,
    reducedMotion: reduced,
    consoleErrors: ctx.consoleErrors.splice(0),
    failedRequests: ctx.failedRequests.splice(0),
    ...probe,
  };
  fs.writeFileSync(path.join(dir, `${stem}.json`), JSON.stringify(record, null, 2));
  return record;
}

async function walkJourney(context, plan, args, viewport, journey, outDir) {
  const dir = path.join(outDir, journey.id, viewport.name);
  fs.mkdirSync(dir, { recursive: true });
  const page = await context.newPage();
  const ctx = { consoleErrors: [], failedRequests: [], notes: [], lastAction: null };
  page.on('console', (msg) => {
    if (msg.type() === 'error') ctx.consoleErrors.push(msg.text().slice(0, 300));
  });
  page.on('requestfailed', (req) => ctx.failedRequests.push({ url: req.url().slice(0, 200), error: req.failure()?.errorText || 'failed' }));
  page.on('response', (res) => {
    if (res.status() >= 400) ctx.failedRequests.push({ url: res.url().slice(0, 200), status: res.status() });
  });

  const record = { id: journey.id, intent: journey.intent, viewport: viewport.name, mode: args.interact ? 'interact' : 'read-only', steps: [], captures: [], stoppedAt: null, notes: ctx.notes };
  let captureIndex = 0;

  for (const [i, step] of journey.steps.entries()) {
    const stepRecord = { index: i + 1, action: step.action, target: step[step.action], startedAt: new Date().toISOString() };
    if (step.interaction && !args.interact) {
      record.stoppedAt = { step: i + 1, action: step.action, reason: 'read-only mode: pass --interact against staging, a local build, or a seeded fixture' };
      stepRecord.skipped = true;
      record.steps.push(stepRecord);
      break;
    }
    const t0 = Date.now();
    try {
      await performStep(page, step, plan, args, ctx);
      if (step.waitFor) await page.waitForSelector(step.waitFor, { timeout: args.timeout });
      if (ctx.lastAction && step.interaction) Object.assign(stepRecord, { ackMs: ctx.lastAction.ackMs, ackSource: ctx.lastAction.ackSource, settleMs: ctx.lastAction.settleMs });
      if (step.capture) {
        captureIndex += 1;
        const cap = await capture(page, { plan, args, viewport, journey, name: step.capture, index: captureIndex, ctx, dir });
        record.captures.push(summarise(cap));
        stepRecord.capture = step.capture;
      }
    } catch (err) {
      stepRecord.error = err.message.split('\n')[0].slice(0, 300);
      record.steps.push({ ...stepRecord, durationMs: Date.now() - t0 });
      record.stoppedAt = { step: i + 1, action: step.action, reason: `error: ${stepRecord.error}` };
      break;
    }
    stepRecord.durationMs = Date.now() - t0;
    record.steps.push(stepRecord);
  }

  fs.writeFileSync(path.join(dir, 'journey.json'), JSON.stringify(record, null, 2));
  await page.close();
  return record;
}

function summarise(cap) {
  return {
    journey: cap.journey,
    viewport: cap.viewport,
    capture: cap.capture,
    index: cap.index,
    screenshot: cap.files.viewport || null,
    url: cap.url,
    ackMs: cap.ackMs,
    settleMs: cap.lastAction ? cap.lastAction.settleMs : null,
    cls: cap.cls,
    lcpMs: cap.lcpMs,
    focusMissing: cap.focus.controlsWithoutFocusStyle.length,
    focusProbed: cap.focus.probed,
    hoverMissing: cap.hover.controlsWithoutHoverStyle.length,
    hoverProbed: cap.hover.probed,
    movesUnderReducedMotion: cap.reducedMotion.movesUnderReducedMotion,
    longTransitions: cap.motion.longTransitions,
    infiniteAnimations: cap.motion.infiniteAnimations,
    horizontalOverflow: cap.horizontalOverflow,
    targetsUnder44: cap.targetsUnder44.count,
    fixedCoveragePct: cap.fixedCoveragePct,
    primaryLikeActions: cap.primaryLikeActions.length,
    primaryAboveFold: cap.primaryAboveFold,
    actionableCount: cap.actionableCount,
    bordered: cap.containers.bordered,
    cards: cap.containers.cards,
    pills: cap.containers.pills,
    icons: cap.containers.icons,
    maxNestDepth: cap.containers.maxNestDepth,
    headings: cap.containers.headings,
    headingOrderSkips: cap.headingOrderSkips,
    vagueActions: cap.copy.vagueActions.length,
    helperText: cap.copy.helperText.length,
    unlabelledFields: cap.unlabelledFields.count,
    imagesMissingAlt: cap.imagesMissingAlt,
    waitingIndicators: cap.waitingIndicators.length,
    consoleErrors: cap.consoleErrors.length,
    failedRequests: cap.failedRequests.length,
  };
}

function writeSummary(outDir, plan, args, journeyRecords) {
  const captures = journeyRecords.flatMap((j) => j.captures);
  const stopped = journeyRecords.filter((j) => j.stoppedAt).map((j) => ({ journey: j.id, viewport: j.viewport, ...j.stoppedAt }));
  const summary = {
    project: plan.project,
    generatedAt: new Date().toISOString(),
    mode: args.interact ? 'interact' : 'read-only',
    viewports: plan.viewports.map((v) => v.name),
    journeys: journeyRecords.map((j) => ({ id: j.id, viewport: j.viewport, steps: j.steps.length, captures: j.captures.length, stoppedAt: j.stoppedAt, notes: j.notes })),
    stopped,
    captures,
  };
  fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify(summary, null, 2));

  const cols = [
    ['Journey', (c) => c.journey],
    ['Viewport', (c) => c.viewport],
    ['Capture', (c) => c.capture],
    ['Ack ms', (c) => (c.ackMs === null ? '—' : c.ackMs)],
    ['Settle ms', (c) => (c.settleMs === null ? '—' : c.settleMs)],
    ['CLS', (c) => (c.cls === null ? '—' : c.cls)],
    ['Focus missing', (c) => `${c.focusMissing}/${c.focusProbed}`],
    ['Hover missing', (c) => (c.hoverProbed ? `${c.hoverMissing}/${c.hoverProbed}` : '—')],
    ['Moves (reduced)', (c) => (c.movesUnderReducedMotion === null ? '—' : c.movesUnderReducedMotion)],
    ['Overflow', (c) => (c.horizontalOverflow ? 'yes' : 'no')],
    ['<44px', (c) => c.targetsUnder44],
    ['Fixed %', (c) => c.fixedCoveragePct],
    ['Primary-like', (c) => `${c.primaryLikeActions}${c.primaryAboveFold ? ' (fold)' : ''}`],
    ['Bordered', (c) => c.bordered],
    ['Cards', (c) => c.cards],
    ['Pills', (c) => c.pills],
    ['Icons', (c) => c.icons],
    ['Nest', (c) => c.maxNestDepth],
    ['Headings', (c) => `${c.headings}${c.headingOrderSkips ? ` (${c.headingOrderSkips} skip)` : ''}`],
    ['Vague', (c) => c.vagueActions],
    ['Unlabelled', (c) => c.unlabelledFields],
    ['No alt', (c) => c.imagesMissingAlt],
    ['Waiting', (c) => c.waitingIndicators],
    ['Errors', (c) => c.consoleErrors + c.failedRequests],
  ];
  const lines = [];
  lines.push(`# Journey walk — ${plan.project}`);
  lines.push('');
  lines.push(`Generated ${summary.generatedAt} · mode **${summary.mode}** · viewports ${summary.viewports.join(', ')}`);
  lines.push('');
  lines.push(`| ${cols.map((c) => c[0]).join(' | ')} |`);
  lines.push(`| ${cols.map(() => '---').join(' | ')} |`);
  for (const c of captures) lines.push(`| ${cols.map(([, f]) => f(c)).join(' | ')} |`);
  if (stopped.length) {
    lines.push('');
    lines.push('## Stopped journeys');
    lines.push('');
    for (const s of stopped) lines.push(`- **${s.journey}** (${s.viewport}) at step ${s.step} \`${s.action}\`: ${s.reason}`);
  }
  lines.push('');
  lines.push('Readings are proxies that tell you where to look; confirm each against the screenshot and the running product before filing. Hover probing reads computed style on the element itself and may miss treatments drawn on children or pseudo-elements.');
  fs.writeFileSync(path.join(outDir, 'summary.md'), lines.join('\n') + '\n');
}

// --------------------------------------------------------------------- main

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    process.stdout.write(usage());
    return;
  }
  const plan = loadPlan(args);
  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true });
  const journeyRecords = [];
  try {
    for (const viewport of plan.viewports) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        deviceScaleFactor: viewport.deviceScaleFactor,
        isMobile: viewport.isMobile,
        hasTouch: viewport.hasTouch,
        storageState: args.storageState || undefined,
        reducedMotion: 'no-preference',
      });
      await context.addInitScript(INIT_SCRIPT);
      for (const journey of plan.journeys) {
        process.stderr.write(`→ ${journey.id} @ ${viewport.name}\n`);
        try {
          const rec = await walkJourney(context, plan, args, viewport, journey, outDir);
          journeyRecords.push(rec);
          if (rec.stoppedAt) process.stderr.write(`  stopped at step ${rec.stoppedAt.step}: ${rec.stoppedAt.reason}\n`);
        } catch (err) {
          process.stderr.write(`  failed: ${err.message}\n`);
          journeyRecords.push({ id: journey.id, intent: journey.intent, viewport: viewport.name, steps: [], captures: [], stoppedAt: { step: 0, action: null, reason: `error: ${err.message}` }, notes: [] });
        }
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  writeSummary(outDir, plan, args, journeyRecords);
  const captures = journeyRecords.reduce((n, j) => n + j.captures.length, 0);
  process.stderr.write(`\n${captures} captures across ${journeyRecords.length} journey runs → ${outDir}\n`);
  process.stderr.write(`Summary: ${path.join(outDir, 'summary.md')}\n`);
}

main().catch((err) => {
  process.stderr.write(`walk_journeys: ${err.message}\n`);
  process.exit(1);
});
