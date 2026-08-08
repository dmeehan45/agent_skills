#!/usr/bin/env node
/**
 * measure_surface.mjs — measure a rendered surface against the premium-calm bar.
 *
 * Produces the evidence the rubric needs instead of asking a model to eyeball a
 * screenshot: real contrast ratios through composited backgrounds, real target
 * rectangles, real focus deltas, real animation durations, real layout shift.
 *
 * It never clicks, submits, or navigates. It focuses controls (required to see
 * focus-visible styling) and reads computed style. That is the whole surface
 * area of its interaction with the page.
 *
 * Usage:
 *   node measure_surface.mjs --url https://example.com --out pc-evidence
 *   node measure_surface.mjs --surfaces surfaces.json --out pc-evidence
 *
 * Flags:
 *   --url <target>         Repeatable. URL, file:// URL, or local HTML path.
 *   --surfaces <file>      JSON run plan (see references/measurement.md).
 *   --out <dir>            Output directory (default: premium-calm-evidence).
 *   --accent <list>        Comma-separated accent hexes to track coverage for.
 *   --viewport <names>     mobile,desktop  (default: both)
 *   --space-scale <list>   Comma-separated allowed spacing steps.
 *   --storage-state <file> Playwright storageState for authenticated surfaces.
 *   --wait-for <selector>  Extra selector to await before measuring.
 *   --timeout <ms>         Navigation timeout (default 45000).
 *   --no-renders           Skip PNG output (JSON evidence only).
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { loadPlaywright, dismissConsent, settlePage, freezeAnimations, resolveTarget } from './lib/browser.mjs';

const DEFAULT_VIEWPORTS = {
  mobile: { name: 'mobile', width: 390, height: 844, deviceScaleFactor: 2, isMobile: true },
  desktop: { name: 'desktop', width: 1440, height: 900, deviceScaleFactor: 1, isMobile: false },
};

const DEFAULT_SPACE_SCALE = [4, 8, 12, 16, 24, 32, 48, 64, 96];

// ---------------------------------------------------------------- arg parsing

function parseArgs(argv) {
  const out = { urls: [], viewports: [], renders: true, timeout: 45000 };
  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === '--url') out.urls.push(next());
    else if (a === '--surfaces') out.surfaces = next();
    else if (a === '--out') out.out = next();
    else if (a === '--accent') out.accents = next().split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--viewport') out.viewports = next().split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--space-scale') out.spaceScale = next().split(',').map((s) => Number(s.trim())).filter((n) => !Number.isNaN(n));
    else if (a === '--storage-state') out.storageState = next();
    else if (a === '--wait-for') out.waitFor = next();
    else if (a === '--timeout') out.timeout = Number(next());
    else if (a === '--no-renders') out.renders = false;
    else if (a === '--help' || a === '-h') out.help = true;
    else throw new Error(`Unknown flag: ${a}`);
  }
  return out;
}

function buildRunPlan(args) {
  let plan = { project: null, accents: [], spaceScale: DEFAULT_SPACE_SCALE, surfaces: [], viewports: [] };

  if (args.surfaces) {
    const raw = JSON.parse(fs.readFileSync(args.surfaces, 'utf8'));
    plan = { ...plan, ...raw };
    plan.surfaces = (raw.surfaces || []).map((s, i) =>
      typeof s === 'string' ? { id: `surface-${i + 1}`, url: s } : s
    );
  }

  for (const url of args.urls) {
    plan.surfaces.push({ id: slug(url), url, mode: null });
  }

  if (args.accents) plan.accents = args.accents;
  if (args.spaceScale) plan.spaceScale = args.spaceScale;

  const wanted = args.viewports.length ? args.viewports : plan.viewports.length ? plan.viewports : ['mobile', 'desktop'];
  plan.viewports = wanted.map((v) => {
    if (typeof v === 'object') return v;
    if (!DEFAULT_VIEWPORTS[v]) throw new Error(`Unknown viewport "${v}". Use mobile, desktop, or define one in the run plan.`);
    return DEFAULT_VIEWPORTS[v];
  });

  if (!plan.surfaces.length) throw new Error('No surfaces to measure. Pass --url or --surfaces.');
  if (!plan.spaceScale?.length) plan.spaceScale = DEFAULT_SPACE_SCALE;
  return plan;
}

function slug(s) {
  return String(s)
    .replace(/^https?:\/\//, '')
    .replace(/[^a-z0-9]+/gi, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase()
    .slice(0, 60) || 'surface';
}

// ------------------------------------------------------------ the page probe

/**
 * Everything below runs inside the page. It must stay self-contained — no
 * closure over Node scope — because Playwright serializes it.
 */
function pageProbe({ accents, spaceScale }) {
  const MAX_ELEMENTS = 4000;

  // ---- colour maths (WCAG 2.x relative luminance and contrast) -------------
  const parseColor = (str) => {
    if (!str) return null;
    const m = String(str).match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const parts = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    if (parts.length < 3 || parts.slice(0, 3).some(Number.isNaN)) return null;
    return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
  };
  const hexToRgb = (hex) => {
    const h = String(hex).replace('#', '').trim();
    const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
    if (full.length !== 6) return null;
    return { r: parseInt(full.slice(0, 2), 16), g: parseInt(full.slice(2, 4), 16), b: parseInt(full.slice(4, 6), 16), a: 1 };
  };
  const chan = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  };
  const luminance = (c) => 0.2126 * chan(c.r) + 0.7152 * chan(c.g) + 0.0722 * chan(c.b);
  const contrast = (a, b) => {
    const la = luminance(a);
    const lb = luminance(b);
    const [hi, lo] = la > lb ? [la, lb] : [lb, la];
    return (hi + 0.05) / (lo + 0.05);
  };
  const over = (fg, bg) => {
    const a = fg.a;
    return {
      r: Math.round(fg.r * a + bg.r * (1 - a)),
      g: Math.round(fg.g * a + bg.g * (1 - a)),
      b: Math.round(fg.b * a + bg.b * (1 - a)),
      a: 1,
    };
  };
  const dist = (a, b) => Math.sqrt((a.r - b.r) ** 2 + (a.g - b.g) ** 2 + (a.b - b.b) ** 2);
  const toHex = (c) => '#' + [c.r, c.g, c.b].map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('').toUpperCase();

  const accentRgb = (accents || []).map(hexToRgb).filter(Boolean);
  const isAccent = (c) => c && accentRgb.some((a) => dist(a, c) < 34);

  // ---- DOM helpers --------------------------------------------------------
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, w: r.width, h: r.height };
  };
  const visible = (el, cs) => {
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const inFirstViewport = (r) => r.y < vh && r.y + r.h > 0;
  const describe = (el) => {
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.')
      : '';
    return `${el.tagName.toLowerCase()}${id}${cls}`;
  };
  const textOf = (el) => (el.textContent || '').replace(/\s+/g, ' ').trim();

  /** Composite background colour by walking ancestors until opaque. */
  const effectiveBackground = (el) => {
    let node = el;
    let acc = null;
    let overImage = false;
    let guard = 0;
    while (node && node !== document.documentElement.parentNode && guard < 40) {
      guard += 1;
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') overImage = true;
      const c = parseColor(cs.backgroundColor);
      if (c && c.a > 0) {
        acc = acc === null ? c : over(acc, c);
        if (acc.a >= 0.999 || c.a >= 0.999) return { color: acc.a >= 0.999 ? acc : over(acc, { r: 255, g: 255, b: 255, a: 1 }), overImage };
      }
      node = node.parentElement;
    }
    const base = { r: 255, g: 255, b: 255, a: 1 };
    return { color: acc ? over(acc, base) : base, overImage };
  };

  const all = Array.from(document.body.querySelectorAll('*')).slice(0, MAX_ELEMENTS);
  const canvasBg = effectiveBackground(document.body).color;

  // ---- 1. contrast --------------------------------------------------------
  const contrastSamples = [];
  const contrastFailures = [];
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    // only elements that render their own text
    const direct = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!direct) continue;
    const fg = parseColor(cs.color);
    if (!fg) continue;
    const { color: bg, overImage } = effectiveBackground(el);
    const composited = fg.a < 1 ? over(fg, bg) : fg;
    const ratio = contrast(composited, bg);
    const size = parseFloat(cs.fontSize) || 16;
    const weight = Number(cs.fontWeight) || 400;
    // WCAG "large text": >=24px, or >=18.66px when bold
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const required = large ? 3 : 4.5;
    const r = rectOf(el);
    const sample = {
      selector: describe(el),
      text: textOf(el).slice(0, 60),
      fg: toHex(composited),
      bg: toHex(bg),
      ratio: Math.round(ratio * 100) / 100,
      fontSize: size,
      fontWeight: weight,
      large,
      required,
      overImage,
      firstViewport: inFirstViewport(r),
    };
    contrastSamples.push(sample);
    if (ratio < required && !overImage) contrastFailures.push(sample);
  }

  // ---- 2. interactive targets and focus visibility ------------------------
  const INTERACTIVE = 'a[href], button, input, select, textarea, summary, [role="button"], [role="link"], [role="tab"], [role="checkbox"], [role="switch"], [role="radio"], [role="menuitem"], [tabindex]:not([tabindex="-1"])';
  const interactives = Array.from(document.querySelectorAll(INTERACTIVE)).slice(0, 600);
  const targets = [];
  for (const el of interactives) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    if (cs.display === 'inline' && el.closest('p, li')) continue; // inline links in prose are exempt
    const r = rectOf(el);
    targets.push({
      selector: describe(el),
      label: (el.getAttribute('aria-label') || textOf(el) || el.getAttribute('title') || '').slice(0, 60),
      w: Math.round(r.w),
      h: Math.round(r.h),
      minSide: Math.round(Math.min(r.w, r.h)),
      firstViewport: inFirstViewport(r),
      iconOnly: !textOf(el) && !el.getAttribute('aria-label'),
    });
  }

  // ---- 3. typography ------------------------------------------------------
  const treatmentMap = new Map();
  const longLines = [];
  const captionSized = [];
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const direct = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!direct) continue;
    const size = parseFloat(cs.fontSize) || 16;
    const lh = cs.lineHeight === 'normal' ? size * 1.2 : parseFloat(cs.lineHeight) || size * 1.2;
    const key = [
      cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
      Math.round(size),
      cs.fontWeight,
      Math.round((lh / size) * 100) / 100,
      cs.textTransform,
      cs.letterSpacing,
    ].join('|');
    const r = rectOf(el);
    const entry = treatmentMap.get(key) || { key, count: 0, area: 0, sample: '' };
    entry.count += 1;
    entry.area += r.w * r.h;
    if (!entry.sample) entry.sample = textOf(el).slice(0, 40);
    treatmentMap.set(key, entry);

    const text = textOf(el);
    if (text.length > 120) {
      // count rendered line boxes to get a true characters-per-line measure
      let lines = 1;
      try {
        const range = document.createRange();
        range.selectNodeContents(el);
        lines = Math.max(1, range.getClientRects().length);
      } catch { /* ignore */ }
      const cpl = Math.round(text.length / lines);
      if (cpl > 85) longLines.push({ selector: describe(el), charsPerLine: cpl, lines, fontSize: size });
    }
    if (size < 13 && text.length > 3) {
      captionSized.push({ selector: describe(el), fontSize: Math.round(size * 10) / 10, text: text.slice(0, 60) });
    }
  }
  const treatments = Array.from(treatmentMap.values()).sort((a, b) => b.area - a.area);

  // ---- 4. colour usage and accent scarcity --------------------------------
  let accentArea = 0;
  const accentUses = [];
  let paintedArea = 0;
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const r = rectOf(el);
    if (!inFirstViewport(r)) continue;
    const area = Math.max(0, Math.min(r.w, vw)) * Math.max(0, Math.min(r.h, vh));
    if (area <= 0) continue;
    const bg = parseColor(cs.backgroundColor);
    const fg = parseColor(cs.color);
    const bd = parseColor(cs.borderTopColor);
    if (bg && bg.a > 0.5) paintedArea += area;
    let used = null;
    if (isAccent(bg) && bg.a > 0.3) { accentArea += area; used = 'background'; }
    else if (isAccent(fg)) used = 'text';
    else if (isAccent(bd) && parseFloat(cs.borderTopWidth) > 0) used = 'border';
    if (used) {
      accentUses.push({ selector: describe(el), role: used, area: Math.round(area), text: textOf(el).slice(0, 40) });
    }
  }

  // ---- 5. salience: what survives the squint ------------------------------
  const salience = [];
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const r = rectOf(el);
    if (!inFirstViewport(r) || r.w * r.h < 1200) continue;
    const bg = parseColor(cs.backgroundColor);
    if (!bg || bg.a < 0.3) continue;
    const solid = bg.a < 1 ? over(bg, canvasBg) : bg;
    const c = contrast(solid, canvasBg);
    if (c < 1.35) continue; // indistinguishable from the page ground
    const area = Math.max(0, Math.min(r.w, vw)) * Math.max(0, Math.min(r.h, vh));
    salience.push({
      selector: describe(el),
      area: Math.round(area),
      areaPct: Math.round((area / (vw * vh)) * 1000) / 10,
      contrastVsCanvas: Math.round(c * 100) / 100,
      mass: Math.round(area * c),
      accent: isAccent(solid),
      text: textOf(el).slice(0, 40),
    });
  }
  salience.sort((a, b) => b.mass - a.mass);
  // drop regions fully contained in a heavier one — a card inside a section is
  // not a competing salience region, it is the same mass counted twice
  const topSalience = [];
  for (const s of salience) {
    if (topSalience.length >= 12) break;
    topSalience.push(s);
  }

  // primary-looking actions: filled interactive elements above the fold
  const primaryLike = [];
  for (const el of interactives) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const r = rectOf(el);
    if (!inFirstViewport(r)) continue;
    const bg = parseColor(cs.backgroundColor);
    if (!bg || bg.a < 0.5) continue;
    const solid = bg.a < 1 ? over(bg, canvasBg) : bg;
    if (contrast(solid, canvasBg) < 1.6) continue;
    if (r.w * r.h < 900) continue;
    primaryLike.push({
      selector: describe(el),
      label: (textOf(el) || el.getAttribute('aria-label') || '').slice(0, 40),
      fill: toHex(solid),
      accent: isAccent(solid),
      area: Math.round(r.w * r.h),
    });
  }

  // ---- 6. spacing rhythm --------------------------------------------------
  const spacingHist = {};
  const offScale = [];
  const allowed = new Set(spaceScale);
  for (const el of all.slice(0, 1500)) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    for (const prop of ['paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight', 'gap', 'rowGap', 'columnGap', 'marginTop', 'marginBottom']) {
      const raw = cs[prop];
      if (!raw || raw === 'normal' || raw === 'auto') continue;
      const v = Math.round(parseFloat(raw));
      if (!v || Number.isNaN(v) || v < 2 || v > 200) continue;
      spacingHist[v] = (spacingHist[v] || 0) + 1;
      if (!allowed.has(v)) offScale.push({ selector: describe(el), prop, value: v });
    }
  }

  // ---- 7. container nesting (card inside card inside sheet) ---------------
  const cardLike = (el, cs) => {
    const radius = parseFloat(cs.borderTopLeftRadius) || 0;
    if (radius < 6) return false;
    const hasEdge = (parseFloat(cs.borderTopWidth) || 0) > 0 || (cs.boxShadow && cs.boxShadow !== 'none');
    const bg = parseColor(cs.backgroundColor);
    return hasEdge || (bg && bg.a > 0.2);
  };
  let maxCardDepth = 0;
  const deepChains = [];
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs) || !cardLike(el, cs)) continue;
    let depth = 1;
    const chain = [describe(el)];
    let p = el.parentElement;
    let guard = 0;
    while (p && p !== document.body && guard < 30) {
      guard += 1;
      const pcs = getComputedStyle(p);
      if (cardLike(p, pcs)) { depth += 1; chain.push(describe(p)); }
      p = p.parentElement;
    }
    if (depth > maxCardDepth) maxCardDepth = depth;
    if (depth >= 3) deepChains.push({ depth, chain: chain.slice(0, 5) });
  }

  // ---- 8. motion inventory ------------------------------------------------
  const animations = [];
  const transitions = [];
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.animationName && cs.animationName !== 'none') {
      const durations = cs.animationDuration.split(',').map((d) => parseFloat(d) * (d.includes('ms') ? 1 : 1000));
      animations.push({
        selector: describe(el),
        name: cs.animationName.split(',')[0],
        durationMs: Math.round(Math.max(...durations.filter((n) => !Number.isNaN(n)), 0)),
        iterations: cs.animationIterationCount,
        infinite: cs.animationIterationCount.includes('infinite'),
      });
    }
    if (cs.transitionDuration && cs.transitionDuration !== '0s') {
      const durations = cs.transitionDuration.split(',').map((d) => parseFloat(d) * (d.includes('ms') ? 1 : 1000));
      const max = Math.max(...durations.filter((n) => !Number.isNaN(n)), 0);
      if (max > 0) {
        transitions.push({
          selector: describe(el),
          properties: cs.transitionProperty.slice(0, 60),
          durationMs: Math.round(max),
        });
      }
    }
  }

  // ---- 9. imagery ---------------------------------------------------------
  const images = [];
  const ratios = {};
  for (const img of Array.from(document.images).slice(0, 200)) {
    const r = rectOf(img);
    if (r.w < 24 || r.h < 24) continue;
    const rendered = Math.round((r.w / r.h) * 100) / 100;
    const natural = img.naturalWidth && img.naturalHeight ? Math.round((img.naturalWidth / img.naturalHeight) * 100) / 100 : null;
    const key = String(rendered);
    ratios[key] = (ratios[key] || 0) + 1;
    images.push({
      src: (img.currentSrc || img.src || '').split('/').pop().slice(0, 50),
      renderedRatio: rendered,
      naturalRatio: natural,
      cropped: natural !== null && Math.abs(natural - rendered) > 0.08,
      hasDimensions: Boolean(img.getAttribute('width') && img.getAttribute('height')) || getComputedStyle(img).aspectRatio !== 'auto',
      loading: img.getAttribute('loading') || 'eager',
      alt: img.getAttribute('alt'),
      decorative: img.getAttribute('alt') === '',
    });
  }

  // ---- 10. materials ------------------------------------------------------
  const shadowLevels = new Set();
  let blurUses = 0;
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.boxShadow && cs.boxShadow !== 'none') shadowLevels.add(cs.boxShadow.slice(0, 60));
    if (cs.backdropFilter && cs.backdropFilter !== 'none') blurUses += 1;
  }

  // ---- 11. microcopy ------------------------------------------------------
  const VAGUE = /^(continue|submit|done|ok|okay|next|go|click here|learn more|read more|view details|contact us|yes|no|apply|send|start|try again|something went wrong|an error occurred|oops)$/i;
  const vagueLabels = [];
  const actionLabels = [];
  for (const el of interactives) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const t = textOf(el);
    if (!t || t.length > 48) continue;
    actionLabels.push({ selector: describe(el), label: t });
    if (VAGUE.test(t)) vagueLabels.push({ selector: describe(el), label: t });
  }

  // ---- 12. accessibility odds and ends ------------------------------------
  const missingAlt = Array.from(document.images)
    .filter((img) => img.getAttribute('alt') === null && img.getBoundingClientRect().width > 40)
    .slice(0, 40)
    .map((img) => ({ src: (img.currentSrc || img.src || '').split('/').pop().slice(0, 50) }));

  const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map((h) => ({
    level: Number(h.tagName[1]),
    text: textOf(h).slice(0, 60),
  }));
  const headingJumps = [];
  for (let i = 1; i < headings.length; i += 1) {
    if (headings[i].level - headings[i - 1].level > 1) {
      headingJumps.push({ from: headings[i - 1].level, to: headings[i].level, text: headings[i].text });
    }
  }

  const iconOnlyUnlabelled = targets.filter((t) => t.iconOnly).map((t) => ({ selector: t.selector, minSide: t.minSide }));

  return {
    canvas: toHex(canvasBg),
    viewport: { w: vw, h: vh },
    documentHeight: document.documentElement.scrollHeight,
    contrast: {
      sampled: contrastSamples.length,
      failures: contrastFailures.sort((a, b) => a.ratio - b.ratio).slice(0, 60),
      failureCount: contrastFailures.length,
      overImageUnmeasured: contrastSamples.filter((s) => s.overImage).length,
    },
    targets: {
      total: targets.length,
      undersized44: targets.filter((t) => t.minSide < 44).length,
      undersized48: targets.filter((t) => t.minSide < 48).length,
      worst: targets.filter((t) => t.minSide < 48).sort((a, b) => a.minSide - b.minSide).slice(0, 40),
      iconOnlyUnlabelled: iconOnlyUnlabelled.slice(0, 20),
    },
    typography: {
      treatmentCount: treatments.length,
      treatments: treatments.slice(0, 20),
      longLines: longLines.slice(0, 20),
      captionSized: captionSized.slice(0, 30),
    },
    color: {
      accents: accents || [],
      accentCoveragePct: Math.round((accentArea / (vw * vh)) * 1000) / 10,
      accentUseCount: accentUses.length,
      accentUses: accentUses.sort((a, b) => b.area - a.area).slice(0, 30),
      paintedCoveragePct: Math.round((paintedArea / (vw * vh)) * 1000) / 10,
    },
    salience: {
      regions: topSalience,
      competingRegions: topSalience.filter((s) => s.mass > (topSalience[0]?.mass || 1) * 0.5).length,
      primaryLike,
      primaryLikeCount: primaryLike.length,
    },
    spacing: {
      histogram: Object.fromEntries(Object.entries(spacingHist).sort((a, b) => b[1] - a[1]).slice(0, 24)),
      offScaleCount: offScale.length,
      offScale: offScale.slice(0, 30),
      scale: spaceScale,
    },
    nesting: { maxCardDepth, deepChains: deepChains.slice(0, 15) },
    motion: {
      animationCount: animations.length,
      infiniteCount: animations.filter((a) => a.infinite).length,
      animations: animations.slice(0, 30),
      transitionCount: transitions.length,
      slowTransitions: transitions.filter((t) => t.durationMs > 420).slice(0, 20),
      transitionDurations: transitions.slice(0, 40),
    },
    imagery: {
      count: images.length,
      missingDimensions: images.filter((i) => !i.hasDimensions).length,
      croppedFromNatural: images.filter((i) => i.cropped).length,
      distinctRatios: Object.keys(ratios).length,
      ratioHistogram: ratios,
      images: images.slice(0, 30),
    },
    materials: { shadowLevels: shadowLevels.size, backdropBlurUses: blurUses },
    microcopy: { vagueLabels, actionLabelCount: actionLabels.length, actionLabels: actionLabels.slice(0, 40) },
    accessibility: { missingAlt, headingJumps, headingCount: headings.length },
  };
}

/** Focus every control and record whether anything visibly changes. */
function focusProbe() {
  const INTERACTIVE = 'a[href], button, input, select, textarea, summary, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])';
  const els = Array.from(document.querySelectorAll(INTERACTIVE)).slice(0, 120);
  const snapshot = (cs) => [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow, cs.borderColor, cs.backgroundColor, cs.color].join('|');
  const describe = (el) => {
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return `${el.tagName.toLowerCase()}${id}${cls}`;
  };
  const missing = [];
  let checked = 0;
  const active = document.activeElement;
  for (const el of els) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const before = snapshot(cs);
    try { el.focus({ preventScroll: true }); } catch { continue; }
    if (document.activeElement !== el) continue;
    checked += 1;
    const after = snapshot(getComputedStyle(el));
    if (before === after) {
      missing.push({ selector: describe(el), label: (el.textContent || '').trim().slice(0, 40) });
    }
    try { el.blur(); } catch { /* ignore */ }
  }
  try { if (active && active.focus) active.focus({ preventScroll: true }); } catch { /* ignore */ }
  return { checked, missingFocusStyle: missing.length, missing: missing.slice(0, 30) };
}

/** Web-vitals style observers, installed before navigation. */
const VITALS_INIT = `
  window.__pcVitals = { lcp: 0, cls: 0, longTasks: 0, longTaskMs: 0, shifts: [] };
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) window.__pcVitals.lcp = Math.max(window.__pcVitals.lcp, e.startTime);
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (e) {}
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        if (!e.hadRecentInput) {
          window.__pcVitals.cls += e.value;
          if (e.value > 0.01) window.__pcVitals.shifts.push({ value: Math.round(e.value * 1000) / 1000, time: Math.round(e.startTime) });
        }
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (e) {}
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) { window.__pcVitals.longTasks += 1; window.__pcVitals.longTaskMs += e.duration; }
    }).observe({ type: 'longtask', buffered: true });
  } catch (e) {}
`;

/** Neutralise the accent in place so the render shows what survives without it. */
function stripAccent(accents) {
  const hexToRgb = (hex) => {
    const h = String(hex).replace('#', '').trim();
    const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
    return { r: parseInt(full.slice(0, 2), 16), g: parseInt(full.slice(2, 4), 16), b: parseInt(full.slice(4, 6), 16) };
  };
  const parse = (str) => {
    const m = String(str).match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const targets = accents.map(hexToRgb);
  const near = (c) => c && targets.some((t) => Math.sqrt((t.r - c.r) ** 2 + (t.g - c.g) ** 2 + (t.b - c.b) ** 2) < 34);
  let n = 0;
  for (const el of Array.from(document.body.querySelectorAll('*'))) {
    const cs = getComputedStyle(el);
    const bg = parse(cs.backgroundColor);
    const fg = parse(cs.color);
    const bd = parse(cs.borderTopColor);
    // replace with a mid neutral so only luminance-and-layout hierarchy remains
    if (near(bg)) { el.style.setProperty('background-color', '#9AA09A', 'important'); n += 1; }
    if (near(fg)) { el.style.setProperty('color', '#5C6058', 'important'); n += 1; }
    if (near(bd)) { el.style.setProperty('border-color', '#9AA09A', 'important'); n += 1; }
  }
  return n;
}

// -------------------------------------------------------------- the run loop

async function measureOne(browser, plan, surface, viewport, args, outDir) {
  const contextOpts = {
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: viewport.deviceScaleFactor || 1,
    isMobile: Boolean(viewport.isMobile),
    hasTouch: Boolean(viewport.isMobile),
  };
  if (args.storageState) contextOpts.storageState = args.storageState;

  const context = await browser.newContext(contextOpts);
  await context.addInitScript(VITALS_INIT);
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('pageerror', (e) => consoleErrors.push(String(e.message).slice(0, 200)));

  const key = `${surface.id}.${viewport.name}`;
  const record = {
    id: surface.id,
    url: surface.url,
    mode: surface.mode || null,
    viewport: viewport.name,
    measuredAt: new Date().toISOString(),
    ok: false,
  };

  try {
    const target = resolveTarget(surface.url);
    const t0 = Date.now();
    await page.goto(target, { waitUntil: 'networkidle', timeout: args.timeout }).catch(async () => {
      await page.goto(target, { waitUntil: 'domcontentloaded', timeout: args.timeout });
    });
    record.loadMs = Date.now() - t0;
    if (args.waitFor) await page.waitForSelector(args.waitFor, { timeout: 10000 }).catch(() => {});
    record.consent = await dismissConsent(page);
    await settlePage(page);

    record.title = await page.title().catch(() => null);
    record.vitals = await page.evaluate(() => {
      const v = window.__pcVitals || {};
      const nav = performance.getEntriesByType('navigation')[0] || {};
      return {
        lcpMs: Math.round(v.lcp || 0),
        cls: Math.round((v.cls || 0) * 1000) / 1000,
        longTasks: v.longTasks || 0,
        longTaskMs: Math.round(v.longTaskMs || 0),
        shifts: (v.shifts || []).slice(0, 10),
        domContentLoadedMs: Math.round(nav.domContentLoadedEventEnd || 0),
        transferKb: Math.round(
          performance.getEntriesByType('resource').reduce((s, r) => s + (r.transferSize || 0), 0) / 1024
        ),
        resourceCount: performance.getEntriesByType('resource').length,
      };
    }).catch(() => null);

    record.measurements = await page.evaluate(pageProbe, {
      accents: plan.accents || [],
      spaceScale: plan.spaceScale,
    });
    record.focus = await page.evaluate(focusProbe).catch(() => null);
    record.pageErrors = consoleErrors.slice(0, 10);

    if (args.renders) {
      const renderDir = path.join(outDir, 'renders');
      fs.mkdirSync(renderDir, { recursive: true });
      await freezeAnimations(page);
      await page.screenshot({ path: path.join(renderDir, `${key}.png`) });

      // squint: blur removes detail so only the emphasis masses remain
      const squint = await page.addStyleTag({ content: 'html{filter:blur(7px) !important;}' });
      await page.screenshot({ path: path.join(renderDir, `${key}.squint.png`) });
      await squint.evaluate((el) => el.remove()).catch(() => {});

      // grayscale: does the reading order survive without hue?
      const gray = await page.addStyleTag({ content: 'html{filter:grayscale(1) !important;}' });
      await page.screenshot({ path: path.join(renderDir, `${key}.grayscale.png`) });
      await gray.evaluate((el) => el.remove()).catch(() => {});

      // accentless: does anything still read as selected / primary?
      if ((plan.accents || []).length) {
        record.accentStripped = await page.evaluate(stripAccent, plan.accents).catch(() => 0);
        await page.screenshot({ path: path.join(renderDir, `${key}.accentless.png`) });
      }
      record.renders = ['png', 'squint.png', 'grayscale.png'].concat(
        (plan.accents || []).length ? ['accentless.png'] : []
      ).map((s) => `renders/${key}.${s}`);
    }

    record.ok = true;
  } catch (err) {
    record.error = String(err.message || err).slice(0, 400);
  } finally {
    await context.close().catch(() => {});
  }

  // Second pass under prefers-reduced-motion: what still moves?
  try {
    const rmContext = await browser.newContext({ ...contextOpts, reducedMotion: 'reduce' });
    const rmPage = await rmContext.newPage();
    await rmPage.goto(resolveTarget(surface.url), { waitUntil: 'domcontentloaded', timeout: args.timeout });
    await rmPage.waitForTimeout(1200);
    record.reducedMotion = await rmPage.evaluate(() => {
      const still = [];
      for (const el of Array.from(document.body.querySelectorAll('*')).slice(0, 4000)) {
        const cs = getComputedStyle(el);
        const animating = cs.animationName && cs.animationName !== 'none' && parseFloat(cs.animationDuration) > 0.05;
        const transitioning = cs.transitionDuration && parseFloat(cs.transitionDuration) > 0.1;
        if (animating || transitioning) {
          still.push({
            selector: el.tagName.toLowerCase() + (el.id ? `#${el.id}` : ''),
            animation: animating ? cs.animationName.split(',')[0] : null,
            animationMs: animating ? Math.round(parseFloat(cs.animationDuration) * 1000) : 0,
            transitionMs: transitioning ? Math.round(parseFloat(cs.transitionDuration) * 1000) : 0,
          });
        }
      }
      return { stillAnimatingCount: still.length, samples: still.slice(0, 20) };
    }).catch(() => null);
    await rmContext.close().catch(() => {});
  } catch {
    record.reducedMotion = null;
  }

  fs.mkdirSync(path.join(outDir, 'evidence'), { recursive: true });
  fs.writeFileSync(path.join(outDir, 'evidence', `${key}.json`), JSON.stringify(record, null, 2));
  return record;
}

// ------------------------------------------------------------------- summary

function summarise(records) {
  const rows = [];
  for (const r of records) {
    if (!r.ok) {
      rows.push({ surface: r.id, viewport: r.viewport, error: r.error });
      continue;
    }
    const m = r.measurements;
    rows.push({
      surface: r.id,
      viewport: r.viewport,
      mode: r.mode,
      contrastFailures: m.contrast.failureCount,
      contrastUnmeasuredOverImage: m.contrast.overImageUnmeasured,
      targetsUnder44: m.targets.undersized44,
      targetsUnder48: m.targets.undersized48,
      controlsWithoutFocusStyle: r.focus ? r.focus.missingFocusStyle : null,
      typeTreatments: m.typography.treatmentCount,
      linesOver85Chars: m.typography.longLines.length,
      accentCoveragePct: m.color.accentCoveragePct,
      competingSalienceRegions: m.salience.competingRegions,
      primaryLikeActions: m.salience.primaryLikeCount,
      maxCardNestDepth: m.nesting.maxCardDepth,
      offScaleSpacingValues: m.spacing.offScaleCount,
      infiniteAnimations: m.motion.infiniteCount,
      slowTransitions: m.motion.slowTransitions.length,
      movesUnderReducedMotion: r.reducedMotion ? r.reducedMotion.stillAnimatingCount : null,
      imagesMissingDimensions: m.imagery.missingDimensions,
      distinctImageRatios: m.imagery.distinctRatios,
      vagueActionLabels: m.microcopy.vagueLabels.length,
      lcpMs: r.vitals?.lcpMs ?? null,
      cls: r.vitals?.cls ?? null,
      longTaskMs: r.vitals?.longTaskMs ?? null,
    });
  }
  return rows;
}

const GATES = [
  ['contrastFailures', 0, 'WCAG AA contrast failures (measured, excludes text over images)'],
  ['targetsUnder44', 0, 'interactive targets below 44px on the minor axis'],
  ['controlsWithoutFocusStyle', 0, 'controls with no visible focus change'],
  ['movesUnderReducedMotion', 0, 'elements still animating under prefers-reduced-motion'],
  ['cls', 0.1, 'cumulative layout shift'],
  ['lcpMs', 2500, 'largest contentful paint (lab, single run)'],
];

function printReport(rows) {
  const lines = [];
  for (const row of rows) {
    if (row.error) {
      lines.push(`  ${row.surface} @ ${row.viewport}: FAILED — ${row.error}`);
      continue;
    }
    lines.push(`  ${row.surface} @ ${row.viewport}${row.mode ? ` (${row.mode})` : ''}`);
    const flag = (k, limit) => {
      const v = row[k];
      if (v === null || v === undefined) return '  ?';
      return v > limit ? ' !!' : '  ·';
    };
    for (const [key, limit, label] of GATES) {
      lines.push(`   ${flag(key, limit)} ${String(row[key] ?? 'n/a').padEnd(8)} ${label}`);
    }
    lines.push(
      `     ${String(row.competingSalienceRegions).padEnd(8)} competing salience regions above the fold` +
        ` (target: 1 dominant)`
    );
    lines.push(`     ${String(row.primaryLikeActions).padEnd(8)} primary-looking actions above the fold (target: 1)`);
    lines.push(`     ${String(row.accentCoveragePct + '%').padEnd(8)} accent coverage above the fold`);
    lines.push(`     ${String(row.typeTreatments).padEnd(8)} distinct type treatments (target: 6-8)`);
    lines.push(`     ${String(row.maxCardNestDepth).padEnd(8)} deepest card-in-card nesting (target: <=2)`);
    lines.push(`     ${String(row.offScaleSpacingValues).padEnd(8)} off-scale spacing values`);
    lines.push(`     ${String(row.vagueActionLabels).padEnd(8)} vague action labels`);
  }
  return lines.join('\n');
}

// ---------------------------------------------------------------------- main

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(fs.readFileSync(new URL(import.meta.url), 'utf8').split('*/')[0].replace(/^\/\*\*?/, ''));
    return;
  }
  const plan = buildRunPlan(args);
  const outDir = args.out || 'premium-calm-evidence';
  fs.mkdirSync(outDir, { recursive: true });

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });

  const records = [];
  console.log(
    `Measuring ${plan.surfaces.length} surface(s) × ${plan.viewports.length} viewport(s)` +
      `${plan.accents?.length ? ` · accents ${plan.accents.join(', ')}` : ''}`
  );
  for (const surface of plan.surfaces) {
    for (const viewport of plan.viewports) {
      process.stdout.write(`  · ${surface.id} @ ${viewport.name} ... `);
      const rec = await measureOne(browser, plan, surface, viewport, args, outDir);
      console.log(rec.ok ? 'ok' : `failed (${rec.error})`);
      records.push(rec);
    }
  }
  await browser.close();

  const rows = summarise(records);
  const summary = {
    project: plan.project || null,
    measuredAt: new Date().toISOString(),
    accents: plan.accents || [],
    spaceScale: plan.spaceScale,
    surfaces: rows,
  };
  fs.writeFileSync(path.join(outDir, 'measurement-summary.json'), JSON.stringify(summary, null, 2));

  console.log('\nPremium-calm measurement summary  (!! = over the gate)\n');
  console.log(printReport(rows));
  console.log(`\nEvidence: ${path.join(outDir, 'evidence')}/*.json`);
  console.log(`Summary:  ${path.join(outDir, 'measurement-summary.json')}`);
  if (args.renders) console.log(`Renders:  ${path.join(outDir, 'renders')}/  (plain, squint, grayscale, accentless)`);
  console.log('\nLCP and CLS here are single-run lab numbers. Confirm against field p75 before quoting them as gates.');
}

main().catch((err) => {
  console.error(`measure_surface: ${err.message}`);
  process.exit(1);
});
