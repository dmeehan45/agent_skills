#!/usr/bin/env node
/**
 * capture_site.mjs — measurement layer for design-system-extractor.
 *
 * Renders each public URL in a real browser and measures what is actually on the
 * page instead of inferring it from markup or screenshots. Emits one JSON file
 * per page plus screenshots, for `aggregate_tokens.py` to consume.
 *
 * Usage:
 *   node capture_site.mjs --urls crawl-plan.json --out design-system-output
 *   node capture_site.mjs --url https://example.com --out design-system-output
 *
 * Playwright resolution: tries local node_modules, then the global install
 * (PLAYWRIGHT_MODULE_PATH or `npm root -g`). Chromium is expected to be present
 * already; this script never downloads browsers.
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

import { dismissConsent, freezeAnimations, loadPlaywright, settlePage } from './lib/browser.mjs';

/* ------------------------------------------------------------------ setup */

const VIEWPORTS = {
  desktop: { width: 1440, height: 900, isMobile: false },
  tablet: { width: 834, height: 1112, isMobile: false },
  mobile: { width: 390, height: 844, isMobile: true },
};

function parseArgs(argv) {
  const args = {
    url: null,
    urls: null,
    out: 'design-system-output',
    viewports: ['desktop', 'mobile'],
    dark: true,
    states: true,
    consent: true,
    screenshots: true,
    maxPages: 20,
    maxElements: 1500,
    timeout: 45000,
    settleMs: 1200,
    userAgent: null,
  };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = () => argv[(i += 1)];
    switch (key) {
      case '--url': args.url = next(); break;
      case '--urls': args.urls = next(); break;
      case '--out': args.out = next(); break;
      case '--viewports': args.viewports = next().split(',').map((v) => v.trim()).filter(Boolean); break;
      case '--max-pages': args.maxPages = Number(next()); break;
      case '--max-elements': args.maxElements = Number(next()); break;
      case '--timeout': args.timeout = Number(next()); break;
      case '--settle-ms': args.settleMs = Number(next()); break;
      case '--user-agent': args.userAgent = next(); break;
      case '--no-dark': args.dark = false; break;
      case '--no-states': args.states = false; break;
      case '--no-consent': args.consent = false; break;
      case '--no-screenshots': args.screenshots = false; break;
      case '--help': case '-h': args.help = true; break;
      default:
        throw new Error(`Unknown argument: ${key}`);
    }
  }
  return args;
}

function resolveUrls(args) {
  if (args.url) return [{ url: args.url, page_id: 'p_root', template_guess: 'unknown' }];
  if (!args.urls) throw new Error('Provide --url or --urls <crawl-plan.json>');
  const raw = JSON.parse(fs.readFileSync(args.urls, 'utf8'));
  const list = Array.isArray(raw) ? raw : raw.pages || raw.urls || [];
  return list
    .map((entry, index) =>
      typeof entry === 'string'
        ? { url: entry, page_id: `p_${index}`, template_guess: 'unknown' }
        : { url: entry.url, page_id: entry.page_id || `p_${index}`, template_guess: entry.template_guess || 'unknown' }
    )
    .filter((entry) => entry.url);
}

/* ------------------------------------------------- in-page instrumentation */

/**
 * Runs inside the page. Returns a compact census rather than a full DOM dump:
 * per-property value frequencies weighted by rendered area, plus full records
 * for elements that actually carry design signal.
 */
function pageProbe(maxElements) {
  const px = (value) => {
    const n = parseFloat(value);
    return Number.isFinite(n) ? Math.round(n * 100) / 100 : null;
  };
  const isTransparent = (c) => !c || c === 'transparent' || /rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(c);

  /* --- CSSOM harvest ------------------------------------------------- */
  const cssom = {
    custom_properties: {},
    media_queries: [],
    font_faces: [],
    keyframes: [],
    sheets_total: 0,
    sheets_blocked: 0,
    rules_scanned: 0,
  };

  const recordCustomProp = (name, value, selector) => {
    const key = name.trim();
    if (!cssom.custom_properties[key]) {
      cssom.custom_properties[key] = { values: [], selectors: [] };
    }
    const entry = cssom.custom_properties[key];
    const v = value.trim();
    if (!entry.values.includes(v)) entry.values.push(v);
    if (selector && !entry.selectors.includes(selector) && entry.selectors.length < 6) {
      entry.selectors.push(selector);
    }
  };

  const walkRules = (rules, mediaCondition) => {
    for (const rule of rules) {
      cssom.rules_scanned += 1;
      if (cssom.rules_scanned > 60000) return;
      if (rule.type === CSSRule.STYLE_RULE || rule.selectorText) {
        const style = rule.style;
        if (style) {
          for (let i = 0; i < style.length; i += 1) {
            const prop = style[i];
            if (prop.startsWith('--')) {
              recordCustomProp(prop, style.getPropertyValue(prop), rule.selectorText);
            }
          }
        }
      }
      if (rule.media && rule.cssRules) {
        const condition = rule.conditionText || rule.media.mediaText;
        if (condition && !cssom.media_queries.some((m) => m.condition === condition)) {
          const widths = [...condition.matchAll(/(min|max)-width:\s*([\d.]+)(px|em|rem)/g)].map((m) => ({
            bound: m[1],
            value: parseFloat(m[2]),
            unit: m[3],
          }));
          cssom.media_queries.push({ condition, widths, rule_count: rule.cssRules.length });
        }
        walkRules(rule.cssRules, condition);
      } else if (rule.cssRules && !rule.media) {
        // @supports, @layer, nested groupings
        walkRules(rule.cssRules, mediaCondition);
      }
      if (rule.type === CSSRule.FONT_FACE_RULE || (rule.style && rule.constructor.name === 'CSSFontFaceRule')) {
        cssom.font_faces.push({
          family: (rule.style.getPropertyValue('font-family') || '').replace(/['"]/g, '').trim(),
          weight: rule.style.getPropertyValue('font-weight') || 'normal',
          style: rule.style.getPropertyValue('font-style') || 'normal',
          display: rule.style.getPropertyValue('font-display') || '',
          src: (rule.style.getPropertyValue('src') || '').slice(0, 300),
        });
      }
      if (rule.name && rule.cssRules && rule.constructor.name === 'CSSKeyframesRule') {
        if (!cssom.keyframes.includes(rule.name)) cssom.keyframes.push(rule.name);
      }
    }
  };

  for (const sheet of Array.from(document.styleSheets)) {
    cssom.sheets_total += 1;
    try {
      walkRules(Array.from(sheet.cssRules || []), null);
    } catch {
      cssom.sheets_blocked += 1;
    }
  }

  /* --- resolved :root custom properties (the site's own tokens) ------- */
  const rootStyle = getComputedStyle(document.documentElement);
  const resolvedCustomProps = {};
  for (const name of Object.keys(cssom.custom_properties)) {
    const resolved = rootStyle.getPropertyValue(name).trim();
    if (resolved) resolvedCustomProps[name] = resolved;
  }

  /* --- element census -------------------------------------------------- */
  const census = {};
  const bump = (group, value, area, role) => {
    if (value === null || value === undefined || value === '' || value === 'none' || value === 'normal') return;
    const key = String(value);
    if (!census[group]) census[group] = {};
    if (!census[group][key]) census[group][key] = { count: 0, area: 0, roles: {} };
    const slot = census[group][key];
    slot.count += 1;
    slot.area += Math.round(area);
    slot.roles[role] = (slot.roles[role] || 0) + 1;
  };

  const contrastPairs = {};
  const elements = [];
  const zIndexes = {};
  const interactiveSignatures = {};

  const roleOf = (el) => {
    const tag = el.tagName.toLowerCase();
    if (/^h[1-6]$/.test(tag)) return `heading.${tag}`;
    if (tag === 'button') return 'control.button';
    if (tag === 'a') return el.closest('nav') ? 'nav.link' : 'link';
    if (tag === 'input') return `control.input.${(el.getAttribute('type') || 'text').toLowerCase()}`;
    if (tag === 'select' || tag === 'textarea') return `control.${tag}`;
    if (tag === 'label') return 'form.label';
    if (tag === 'p' || tag === 'li' || tag === 'blockquote') return 'text.body';
    if (tag === 'nav' || tag === 'header' || tag === 'footer' || tag === 'main' || tag === 'aside') return `region.${tag}`;
    if (tag === 'svg' || tag === 'img' || tag === 'picture' || tag === 'video') return `media.${tag}`;
    if (tag === 'table' || tag === 'th' || tag === 'td') return `table.${tag}`;
    const role = el.getAttribute('role');
    if (role) return `role.${role}`;
    return `box.${tag}`;
  };

  const hasDirectText = (el) => {
    for (const node of el.childNodes) {
      if (node.nodeType === 3 && node.textContent.trim().length > 0) return true;
    }
    return false;
  };

  const all = Array.from(document.querySelectorAll('body *'));
  const viewportArea = window.innerWidth * window.innerHeight;

  for (const el of all) {
    const rect = el.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    if (width <= 0 || height <= 0) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || cs.opacity === '0') continue;

    const area = width * height;
    const role = roleOf(el);
    const tag = el.tagName.toLowerCase();
    const text = hasDirectText(el);

    /* colors — text color only counts where text actually renders */
    if (text) {
      bump('text_color', cs.color, area, role);
      bump('font_family', cs.fontFamily, area, role);
      bump('font_size', px(cs.fontSize), area, role);
      bump('font_weight', cs.fontWeight, area, role);
      bump('line_height', cs.lineHeight === 'normal' ? 'normal' : px(cs.lineHeight), area, role);
      bump('letter_spacing', cs.letterSpacing === 'normal' ? '0' : px(cs.letterSpacing), area, role);
      if (cs.textTransform !== 'none') bump('text_transform', cs.textTransform, area, role);
    }
    if (!isTransparent(cs.backgroundColor)) {
      bump('background_color', cs.backgroundColor, area, role);
    }
    if (cs.backgroundImage && cs.backgroundImage !== 'none') {
      if (cs.backgroundImage.includes('gradient')) bump('gradient', cs.backgroundImage.slice(0, 220), area, role);
    }
    if (cs.borderTopWidth !== '0px' && !isTransparent(cs.borderTopColor)) {
      bump('border_color', cs.borderTopColor, area, role);
      bump('border_width', px(cs.borderTopWidth), area, role);
      bump('border_style', cs.borderTopStyle, area, role);
    }
    if (cs.borderTopLeftRadius !== '0px') {
      bump('radius', cs.borderTopLeftRadius, area, role);
    }
    if (cs.boxShadow && cs.boxShadow !== 'none') {
      bump('shadow', cs.boxShadow, area, role);
    }
    if (cs.transitionDuration && cs.transitionDuration !== '0s') {
      bump('transition_duration', cs.transitionDuration, area, role);
      bump('transition_timing', cs.transitionTimingFunction, area, role);
      bump('transition_property', cs.transitionProperty, area, role);
    }
    if (cs.animationName && cs.animationName !== 'none') {
      bump('animation', `${cs.animationName} ${cs.animationDuration} ${cs.animationTimingFunction}`, area, role);
    }
    if (cs.zIndex && cs.zIndex !== 'auto') {
      const z = parseInt(cs.zIndex, 10);
      if (Number.isFinite(z)) {
        zIndexes[z] = (zIndexes[z] || 0) + 1;
        bump('z_index', z, area, role);
      }
    }
    if (cs.display === 'flex' || cs.display === 'grid') {
      if (cs.gap && cs.gap !== 'normal') bump('gap', cs.gap, area, role);
      bump('layout_display', cs.display, area, role);
      if (cs.display === 'grid' && cs.gridTemplateColumns && cs.gridTemplateColumns !== 'none') {
        const columns = cs.gridTemplateColumns.split(' ').filter(Boolean).length;
        bump('grid_columns', columns, area, role);
      }
    }
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) {
      const pad = px(cs[`padding${side}`]);
      if (pad) bump('padding', pad, area, role);
      const mar = px(cs[`margin${side}`]);
      if (mar && mar > 0) bump('margin', mar, area, role);
    }
    if (cs.maxWidth && cs.maxWidth !== 'none') bump('max_width', px(cs.maxWidth), area, role);

    /* contrast pairs: resolve the nearest painted ancestor background */
    if (text && cs.color) {
      let bg = null;
      let node = el;
      while (node && node !== document.documentElement) {
        const ncs = getComputedStyle(node);
        if (!isTransparent(ncs.backgroundColor)) { bg = ncs.backgroundColor; break; }
        node = node.parentElement;
      }
      if (!bg) bg = getComputedStyle(document.body).backgroundColor || 'rgb(255, 255, 255)';
      const key = `${cs.color}|${bg}`;
      if (!contrastPairs[key]) {
        contrastPairs[key] = { fg: cs.color, bg, count: 0, area: 0, roles: {}, min_font_px: 9999, max_weight: 0 };
      }
      const pair = contrastPairs[key];
      pair.count += 1;
      pair.area += Math.round(area);
      pair.roles[role] = (pair.roles[role] || 0) + 1;
      const fontPx = px(cs.fontSize) || 16;
      pair.min_font_px = Math.min(pair.min_font_px, fontPx);
      pair.max_weight = Math.max(pair.max_weight, parseInt(cs.fontWeight, 10) || 400);
    }

    /* interactive signature registry — feeds the state-probe pass */
    const interactive =
      tag === 'button' ||
      tag === 'a' ||
      tag === 'input' ||
      tag === 'select' ||
      tag === 'textarea' ||
      el.getAttribute('role') === 'button' ||
      el.hasAttribute('tabindex');
    if (interactive) {
      const classSig = (el.getAttribute('class') || '').split(/\s+/).slice(0, 4).join('.');
      const sig = `${tag}|${el.getAttribute('type') || ''}|${classSig}`;
      if (!interactiveSignatures[sig]) {
        interactiveSignatures[sig] = { signature: sig, tag, role, count: 0, sample_selector: null, area: 0 };
        /* build a stable-ish selector for the first instance */
        const id = el.getAttribute('id');
        if (id && /^[A-Za-z][-\w]*$/.test(id)) {
          interactiveSignatures[sig].sample_selector = `#${id}`;
        } else {
          const classes = (el.getAttribute('class') || '')
            .split(/\s+/)
            .filter((c) => c && /^[A-Za-z][-\w]*$/.test(c))
            .slice(0, 3)
            .map((c) => `.${CSS.escape(c)}`)
            .join('');
          interactiveSignatures[sig].sample_selector = classes ? `${tag}${classes}` : null;
        }
      }
      interactiveSignatures[sig].count += 1;
      interactiveSignatures[sig].area += Math.round(area);
    }

    /* keep full records only for elements carrying real signal */
    const significant =
      text || interactive || area > viewportArea * 0.02 || /^h[1-6]$/.test(tag) || tag === 'svg' || tag === 'img';
    if (significant && elements.length < maxElements) {
      elements.push({
        role,
        tag,
        x: Math.round(rect.x), y: Math.round(rect.y + window.scrollY),
        w: Math.round(width), h: Math.round(height),
        area: Math.round(area),
        color: text ? cs.color : null,
        bg: isTransparent(cs.backgroundColor) ? null : cs.backgroundColor,
        font_family: text ? cs.fontFamily : null,
        font_size: text ? px(cs.fontSize) : null,
        font_weight: text ? cs.fontWeight : null,
        line_height: text ? (cs.lineHeight === 'normal' ? null : px(cs.lineHeight)) : null,
        letter_spacing: text && cs.letterSpacing !== 'normal' ? px(cs.letterSpacing) : null,
        radius: cs.borderTopLeftRadius === '0px' ? null : cs.borderTopLeftRadius,
        border: cs.borderTopWidth === '0px' ? null : `${cs.borderTopWidth} ${cs.borderTopStyle} ${cs.borderTopColor}`,
        shadow: cs.boxShadow === 'none' ? null : cs.boxShadow,
        padding: `${cs.paddingTop} ${cs.paddingRight} ${cs.paddingBottom} ${cs.paddingLeft}`,
        max_width: cs.maxWidth === 'none' ? null : px(cs.maxWidth),
        display: cs.display,
        gap: cs.gap && cs.gap !== 'normal' ? cs.gap : null,
        transition: cs.transitionDuration !== '0s' ? `${cs.transitionProperty} ${cs.transitionDuration} ${cs.transitionTimingFunction}` : null,
        text_sample: text ? el.textContent.trim().slice(0, 120) : null,
        class_name: (el.getAttribute('class') || '').slice(0, 160) || null,
      });
    }
  }

  /* --- layout: real container widths ---------------------------------- */
  const containerWidths = {};
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    const rect = el.getBoundingClientRect();
    if (rect.height < 40 || rect.width < 200) continue;
    const mx = cs.marginLeft === cs.marginRight && cs.marginLeft !== '0px';
    const capped = cs.maxWidth !== 'none';
    if (mx || capped) {
      const w = Math.round(rect.width);
      if (!containerWidths[w]) containerWidths[w] = 0;
      containerWidths[w] += 1;
    }
  }

  /* --- icon system fingerprint ---------------------------------------- */
  const svgs = Array.from(document.querySelectorAll('svg')).slice(0, 200);
  const iconSystem = {
    inline_svg_count: svgs.length,
    sprite_use_count: document.querySelectorAll('svg use').length,
    icon_font_candidates: [],
    view_boxes: {},
    stroke_widths: {},
    stroke_linecaps: {},
    fill_vs_stroke: { fill: 0, stroke: 0 },
    sizes: {},
  };
  for (const svg of svgs) {
    const vb = svg.getAttribute('viewBox');
    if (vb) iconSystem.view_boxes[vb] = (iconSystem.view_boxes[vb] || 0) + 1;
    const rect = svg.getBoundingClientRect();
    if (rect.width > 0 && rect.width < 64) {
      const size = Math.round(rect.width);
      iconSystem.sizes[size] = (iconSystem.sizes[size] || 0) + 1;
    }
    const child = svg.querySelector('path, circle, rect, line, polyline');
    if (child) {
      const ccs = getComputedStyle(child);
      const sw = child.getAttribute('stroke-width') || (ccs.strokeWidth !== '0px' ? ccs.strokeWidth : null);
      const stroke = child.getAttribute('stroke') || ccs.stroke;
      const hasStroke = stroke && stroke !== 'none' && !isTransparent(stroke);
      if (hasStroke) {
        iconSystem.fill_vs_stroke.stroke += 1;
        if (sw) iconSystem.stroke_widths[sw] = (iconSystem.stroke_widths[sw] || 0) + 1;
        const cap = child.getAttribute('stroke-linecap') || ccs.strokeLinecap;
        if (cap) iconSystem.stroke_linecaps[cap] = (iconSystem.stroke_linecaps[cap] || 0) + 1;
      } else {
        iconSystem.fill_vs_stroke.fill += 1;
      }
    }
  }
  for (const el of Array.from(document.querySelectorAll('i, span')).slice(0, 400)) {
    const cls = el.getAttribute('class') || '';
    if (/\b(fa|fas|far|fab|material-icons|icon|bi|glyphicon)\b/.test(cls)) {
      const family = getComputedStyle(el).fontFamily;
      if (family && !iconSystem.icon_font_candidates.includes(family)) {
        iconSystem.icon_font_candidates.push(family);
      }
    }
  }

  /* --- brand asset signals -------------------------------------------- */
  const brand = {
    theme_color: document.querySelector('meta[name="theme-color"]')?.getAttribute('content') || null,
    manifest_href: document.querySelector('link[rel="manifest"]')?.getAttribute('href') || null,
    og_image: document.querySelector('meta[property="og:image"]')?.getAttribute('content') || null,
    icons: Array.from(document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')).map((l) => ({
      rel: l.getAttribute('rel'),
      href: l.getAttribute('href'),
    })),
    logo_candidates: [],
  };
  const logoNodes = Array.from(
    document.querySelectorAll(
      'header img, header svg, [class*="logo" i], [id*="logo" i], a[href="/"] img, a[href="/"] svg'
    )
  ).slice(0, 12);
  for (const node of logoNodes) {
    const rect = node.getBoundingClientRect();
    if (rect.width <= 0) continue;
    const entry = {
      tag: node.tagName.toLowerCase(),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      src: node.getAttribute('src') || null,
      alt: node.getAttribute('alt') || null,
      colors: [],
    };
    if (node.tagName.toLowerCase() === 'svg' || node.querySelector?.('svg')) {
      const svg = node.tagName.toLowerCase() === 'svg' ? node : node.querySelector('svg');
      for (const shape of Array.from(svg.querySelectorAll('path, circle, rect, polygon, stop')).slice(0, 40)) {
        for (const attr of ['fill', 'stroke', 'stop-color']) {
          const v = shape.getAttribute(attr);
          if (v && v !== 'none' && v !== 'currentColor' && !entry.colors.includes(v)) entry.colors.push(v);
        }
      }
      entry.svg_markup = svg.outerHTML.slice(0, 4000);
    }
    brand.logo_candidates.push(entry);
  }

  /* --- framework fingerprint ------------------------------------------ */
  const bodyClasses = document.body.className || '';
  const allClasses = new Set();
  for (const el of all.slice(0, 3000)) {
    for (const c of (el.getAttribute('class') || '').split(/\s+/)) if (c) allClasses.add(c);
  }
  const classList = Array.from(allClasses);
  const framework = {
    tailwind: classList.filter((c) => /^(sm|md|lg|xl|2xl):/.test(c) || /^(bg|text|px|py|mt|mb|flex|grid|gap|rounded|shadow|font|border|w|h)-/.test(c)).length,
    bootstrap: classList.filter((c) => /^(col-|row$|btn-|container(-fluid)?$|navbar|d-flex|mt-\d|px-\d)/.test(c)).length,
    styled_components: classList.filter((c) => /^sc-/.test(c)).length,
    emotion: classList.filter((c) => /^css-[a-z0-9]{6,}/.test(c)).length,
    mui: classList.filter((c) => /^Mui/.test(c)).length,
    chakra: classList.filter((c) => /^chakra-/.test(c)).length,
    bem_like: classList.filter((c) => /__|--/.test(c)).length,
    next_js: Boolean(document.querySelector('#__next, script#__NEXT_DATA__')),
    nuxt: Boolean(document.querySelector('#__nuxt, #__NUXT__')),
    body_classes: bodyClasses.slice(0, 200),
    total_distinct_classes: classList.length,
  };

  /* --- text sample for voice DNA -------------------------------------- */
  const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
    .slice(0, 40)
    .map((h) => ({ level: h.tagName.toLowerCase(), text: h.textContent.trim().slice(0, 200) }))
    .filter((h) => h.text);
  const ctas = Array.from(document.querySelectorAll('button, a[class*="btn" i], a[class*="button" i], [role="button"]'))
    .slice(0, 40)
    .map((b) => b.textContent.trim().slice(0, 80))
    .filter(Boolean);
  const paragraphs = Array.from(document.querySelectorAll('p'))
    .slice(0, 60)
    .map((p) => p.textContent.trim())
    .filter((t) => t.length > 40)
    .slice(0, 30)
    .map((t) => t.slice(0, 400));

  /* --- outbound same-origin links (for URL discovery on SPA sites) ----- */
  const links = Array.from(new Set(
    Array.from(document.querySelectorAll('a[href]'))
      .map((a) => a.href)
      .filter((href) => {
        try {
          const u = new URL(href);
          return u.origin === location.origin && !u.hash;
        } catch { return false; }
      })
  )).slice(0, 300);

  return {
    url: location.href,
    title: document.title,
    lang: document.documentElement.lang || null,
    scroll_height: document.documentElement.scrollHeight,
    viewport: { width: window.innerWidth, height: window.innerHeight },
    color_scheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    cssom,
    resolved_custom_properties: resolvedCustomProps,
    census,
    contrast_pairs: Object.values(contrastPairs).sort((a, b) => b.area - a.area).slice(0, 120),
    elements,
    z_indexes: zIndexes,
    container_widths: containerWidths,
    icon_system: iconSystem,
    brand,
    framework,
    interactive_signatures: Object.values(interactiveSignatures)
      .sort((a, b) => b.count - a.count)
      .slice(0, 40),
    content: { headings, ctas, paragraphs },
    links,
    element_count_total: all.length,
    element_count_recorded: elements.length,
  };
}

/* --------------------------------------------------- page-level behaviours */

/**
 * Measures hover / focus / active deltas. Static HTML and screenshots cannot
 * show these, so without this pass component states are guesswork.
 */
async function probeInteractionStates(page, signatures) {
  const results = [];
  const readStyle = async (locator) =>
    locator.evaluate((el) => {
      const cs = getComputedStyle(el);
      const out = {
        color: cs.color,
        background_color: cs.backgroundColor,
        background_image: cs.backgroundImage === 'none' ? null : cs.backgroundImage.slice(0, 160),
        border_color: cs.borderTopColor,
        border_width: cs.borderTopWidth,
        border_radius: cs.borderTopLeftRadius,
        box_shadow: cs.boxShadow === 'none' ? null : cs.boxShadow,
        outline: cs.outlineStyle === 'none' ? null : `${cs.outlineWidth} ${cs.outlineStyle} ${cs.outlineColor}`,
        outline_offset: cs.outlineOffset,
        opacity: cs.opacity,
        transform: cs.transform === 'none' ? null : cs.transform,
        text_decoration: cs.textDecorationLine,
        cursor: cs.cursor,
        transition: cs.transitionDuration === '0s' ? null : `${cs.transitionProperty} ${cs.transitionDuration} ${cs.transitionTimingFunction}`,
        padding: `${cs.paddingTop} ${cs.paddingRight} ${cs.paddingBottom} ${cs.paddingLeft}`,
        min_height: cs.minHeight,
        height: `${Math.round(el.getBoundingClientRect().height)}px`,
        width: `${Math.round(el.getBoundingClientRect().width)}px`,
        font_size: cs.fontSize,
        font_weight: cs.fontWeight,
      };
      return out;
    });

  const diff = (base, next) => {
    const out = {};
    for (const key of Object.keys(base)) {
      if (base[key] !== next[key]) out[key] = { from: base[key], to: next[key] };
    }
    return out;
  };

  for (const sig of signatures.slice(0, 14)) {
    if (!sig.sample_selector) continue;
    try {
      const locator = page.locator(sig.sample_selector).first();
      if (!(await locator.isVisible({ timeout: 800 }).catch(() => false))) continue;
      await locator.scrollIntoViewIfNeeded({ timeout: 1500 }).catch(() => {});

      const base = await readStyle(locator);

      await locator.hover({ timeout: 1500, force: true }).catch(() => {});
      await page.waitForTimeout(220);
      const hover = await readStyle(locator);

      await page.mouse.move(0, 0);
      await page.waitForTimeout(150);

      /* Keyboard focus, so we capture :focus-visible rings rather than :focus only. */
      const focusApplied = await locator.evaluate((el) => {
        if (typeof el.focus !== 'function') return false;
        el.focus({ preventScroll: true });
        return document.activeElement === el;
      }).catch(() => false);
      let focus = null;
      let focusVisible = null;
      if (focusApplied) {
        focus = await readStyle(locator);
        await page.keyboard.press('Tab').catch(() => {});
        await page.keyboard.press('Shift+Tab').catch(() => {});
        await page.waitForTimeout(150);
        focusVisible = await readStyle(locator);
        await locator.evaluate((el) => el.blur?.()).catch(() => {});
      }

      let active = null;
      const box = await locator.boundingBox().catch(() => null);
      if (box) {
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        await page.mouse.down().catch(() => {});
        await page.waitForTimeout(180);
        active = await readStyle(locator);
        await page.mouse.up().catch(() => {});
        await page.mouse.move(0, 0);
      }

      results.push({
        signature: sig.signature,
        selector: sig.sample_selector,
        role: sig.role,
        instances: sig.count,
        base,
        states: {
          hover: hover ? diff(base, hover) : null,
          focus: focus ? diff(base, focus) : null,
          focus_visible: focusVisible ? diff(base, focusVisible) : null,
          active: active ? diff(base, active) : null,
        },
        has_visible_focus_indicator: Boolean(
          focusVisible &&
            (focusVisible.outline !== base.outline || focusVisible.box_shadow !== base.box_shadow ||
              focusVisible.border_color !== base.border_color)
        ),
      });
    } catch (err) {
      results.push({ signature: sig.signature, selector: sig.sample_selector, error: String(err).slice(0, 200) });
    }
  }

  /* Disabled-state evidence, read declaratively rather than synthesised. */
  const disabled = await page.evaluate(() => {
    const out = [];
    for (const el of Array.from(document.querySelectorAll('[disabled], [aria-disabled="true"]')).slice(0, 8)) {
      const cs = getComputedStyle(el);
      out.push({
        tag: el.tagName.toLowerCase(),
        color: cs.color,
        background_color: cs.backgroundColor,
        opacity: cs.opacity,
        cursor: cs.cursor,
        border_color: cs.borderTopColor,
      });
    }
    return out;
  }).catch(() => []);

  return { probes: results, disabled_samples: disabled };
}

/* ------------------------------------------------------------------- main */

function slug(value) {
  return value.replace(/[^a-z0-9]+/gi, '-').replace(/^-+|-+$/g, '').slice(0, 60).toLowerCase() || 'page';
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(fs.readFileSync(new URL(import.meta.url), 'utf8').split('*/')[0]);
    return 0;
  }

  const { chromium } = loadPlaywright();
  const targets = resolveUrls(args).slice(0, args.maxPages);
  const outRoot = path.resolve(args.out);
  const evidenceDir = path.join(outRoot, 'evidence');
  const pagesDir = path.join(evidenceDir, 'pages');
  const shotsDir = path.join(evidenceDir, 'screenshots');
  fs.mkdirSync(pagesDir, { recursive: true });
  if (args.screenshots) fs.mkdirSync(shotsDir, { recursive: true });

  const browser = await chromium.launch({ args: ['--disable-dev-shm-usage'] });
  const manifest = {
    schema: 'psdsm/crawl-manifest@2',
    generated_by: 'capture_site.mjs',
    source_url: targets[0]?.url || null,
    viewports: args.viewports,
    dark_mode_pass: args.dark,
    state_probe_pass: args.states,
    pages: [],
    errors: [],
  };

  for (const target of targets) {
    const pageId = target.page_id || `p_${slug(target.url)}`;
    const record = {
      page_id: pageId,
      url: target.url,
      template_guess: target.template_guess,
      status: null,
      captures: {},
      warnings: [],
      measurements: {},
    };
    console.error(`[capture] ${pageId} ${target.url}`);

    for (const viewportName of args.viewports) {
      const viewport = VIEWPORTS[viewportName];
      if (!viewport) {
        record.warnings.push(`unknown viewport ${viewportName}`);
        continue;
      }
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        isMobile: viewport.isMobile,
        hasTouch: viewport.isMobile,
        deviceScaleFactor: 1,
        userAgent: args.userAgent || undefined,
        reducedMotion: 'no-preference',
        colorScheme: 'light',
      });
      const page = await context.newPage();
      try {
        const response = await page.goto(target.url, { waitUntil: 'domcontentloaded', timeout: args.timeout });
        record.status = response ? response.status() : null;
        if (response && response.status() >= 400) {
          record.warnings.push(`http ${response.status()} at ${viewportName}`);
        }
        await page.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {
          record.warnings.push(`networkidle timeout at ${viewportName}`);
        });

        if (args.consent) {
          const consent = await dismissConsent(page);
          record.captures[`${viewportName}_consent`] = consent;
        }
        await settlePage(page, args.settleMs);

        /* State probes run before animations are frozen so transitions are real. */
        if (args.states && viewportName === 'desktop') {
          const preSignatures = await page.evaluate(() =>
            Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"]'))
              .slice(0, 400)
              .reduce((acc, el) => {
                const tag = el.tagName.toLowerCase();
                const id = el.getAttribute('id');
                const classes = (el.getAttribute('class') || '')
                  .split(/\s+/).filter((c) => c && /^[A-Za-z][-\w]*$/.test(c)).slice(0, 3);
                const sig = `${tag}|${el.getAttribute('type') || ''}|${classes.join('.')}`;
                if (!acc.map[sig]) {
                  let selector = null;
                  if (id && /^[A-Za-z][-\w]*$/.test(id)) selector = `#${id}`;
                  else if (classes.length) selector = tag + classes.map((c) => `.${CSS.escape(c)}`).join('');
                  else selector = tag;
                  acc.map[sig] = { signature: sig, tag, role: tag, count: 0, sample_selector: selector };
                  acc.list.push(acc.map[sig]);
                }
                acc.map[sig].count += 1;
                return acc;
              }, { map: {}, list: [] }).list
          ).catch(() => []);
          preSignatures.sort((a, b) => b.count - a.count);
          record.measurements.interaction_states = await probeInteractionStates(page, preSignatures);
        }

        // Measure BEFORE freezing: the freeze sets `transition: none`, which
        // zeroes transition-duration and erases the motion tokens entirely.
        const probe = await page.evaluate(pageProbe, args.maxElements);
        record.measurements[viewportName] = probe;

        await freezeAnimations(page);

        if (args.screenshots) {
          const foldPath = path.join(shotsDir, `${pageId}.${viewportName}.fold.png`);
          const fullPath = path.join(shotsDir, `${pageId}.${viewportName}.full.png`);
          await page.screenshot({ path: foldPath }).catch((e) => record.warnings.push(`fold shot failed: ${e.message}`));
          await page.screenshot({ path: fullPath, fullPage: true }).catch((e) =>
            record.warnings.push(`full shot failed: ${e.message}`)
          );
          record.captures[`${viewportName}_fold_screenshot`] = path.relative(outRoot, foldPath);
          record.captures[`${viewportName}_full_screenshot`] = path.relative(outRoot, fullPath);
        }

        if (viewportName === 'desktop') {
          const html = await page.content();
          const htmlDir = path.join(evidenceDir, 'html');
          fs.mkdirSync(htmlDir, { recursive: true });
          const htmlPath = path.join(htmlDir, `${pageId}.html`);
          fs.writeFileSync(htmlPath, html, 'utf8');
          record.captures.html = path.relative(outRoot, htmlPath);
        }
      } catch (err) {
        const message = String(err).slice(0, 300);
        record.warnings.push(`${viewportName}: ${message}`);
        manifest.errors.push({ page_id: pageId, viewport: viewportName, error: message });
      } finally {
        await context.close();
      }
    }

    /* Dark-mode pass: same measurement, prefers-color-scheme: dark. */
    if (args.dark) {
      const context = await browser.newContext({
        viewport: { width: VIEWPORTS.desktop.width, height: VIEWPORTS.desktop.height },
        colorScheme: 'dark',
      });
      const page = await context.newPage();
      try {
        await page.goto(target.url, { waitUntil: 'domcontentloaded', timeout: args.timeout });
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
        if (args.consent) await dismissConsent(page);
        await settlePage(page, Math.min(args.settleMs, 800));
        const probe = await page.evaluate(pageProbe, Math.min(args.maxElements, 600));
        record.measurements.dark = probe;
        await freezeAnimations(page);
        const light = record.measurements.desktop;
        record.measurements.dark_mode_supported = Boolean(
          light &&
            probe &&
            JSON.stringify(Object.keys(probe.census.background_color || {}).slice(0, 8)) !==
              JSON.stringify(Object.keys(light.census.background_color || {}).slice(0, 8))
        );
        if (args.screenshots) {
          const darkPath = path.join(shotsDir, `${pageId}.dark.fold.png`);
          await page.screenshot({ path: darkPath }).catch(() => {});
          record.captures.dark_fold_screenshot = path.relative(outRoot, darkPath);
        }
      } catch (err) {
        record.warnings.push(`dark: ${String(err).slice(0, 200)}`);
      } finally {
        await context.close();
      }
    }

    const pagePath = path.join(pagesDir, `${pageId}.json`);
    fs.writeFileSync(pagePath, JSON.stringify(record, null, 2), 'utf8');
    manifest.pages.push({
      page_id: pageId,
      url: target.url,
      template_guess: target.template_guess,
      status: record.status,
      measurement_file: path.relative(outRoot, pagePath),
      captures: record.captures,
      warnings: record.warnings,
    });
  }

  await browser.close();

  const manifestPath = path.join(evidenceDir, 'crawl-manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');
  console.error(`[capture] wrote ${manifest.pages.length} page measurements -> ${manifestPath}`);
  if (manifest.errors.length) console.error(`[capture] ${manifest.errors.length} error(s) recorded`);
  return 0;
}

main().then(
  (code) => process.exit(code),
  (err) => {
    console.error(`[capture] fatal: ${err.stack || err}`);
    process.exit(1);
  }
);
