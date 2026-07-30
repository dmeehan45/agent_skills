#!/usr/bin/env node
/**
 * fidelity_check.mjs — round-trip verification for the extracted design system.
 *
 * Confidence scores say how sure the pipeline is about its own measurements.
 * They cannot say whether the resulting token set actually looks like the brand.
 * This does, by measuring two things:
 *
 *   1. Palette fidelity — decode the source screenshots, take the dominant
 *      colours by pixel share, and measure how close the emitted token palette
 *      gets to each one (OKLab ΔE).
 *   2. Component fidelity — screenshot the real element on the live site and the
 *      token-built equivalent from preview.html, then compare mean colour and
 *      box metrics.
 *
 * Chromium is the image decoder, so there is no image dependency to install.
 *
 * Usage:
 *   node fidelity_check.mjs --out design-system-output
 *   node fidelity_check.mjs --out design-system-output --no-live
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

import { dismissConsent, freezeAnimations, loadPlaywright, settlePage } from './lib/browser.mjs';

/* ------------------------------------------------------------ colour maths */

const srgbToLinear = (c) => {
  const v = c / 255;
  return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
};

function toOklab([r, g, b]) {
  const lr = srgbToLinear(r), lg = srgbToLinear(g), lb = srgbToLinear(b);
  const l = Math.cbrt(0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb);
  const m = Math.cbrt(0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb);
  const s = Math.cbrt(0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb);
  return [
    0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
  ];
}

function deltaE(c1, c2) {
  const a = toOklab(c1), b = toOklab(c2);
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}

function hexToRgb(hex) {
  const m = /^#?([0-9a-f]{6})/i.exec(hex);
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

const rgbToHex = ([r, g, b]) =>
  '#' + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');

/* ------------------------------------------------------- pixel sampling */

/**
 * Decodes a PNG in the browser and returns quantised dominant colours.
 * Runs in-page: `dataUrl` is a base64 PNG, `bucket` the quantisation step.
 */
async function dominantColors(page, dataUrl, bucket = 16, maxSamples = 240000) {
  return page.evaluate(
    async ([url, step, cap]) => {
      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = () => reject(new Error('decode failed'));
        img.src = url;
      });
      const scale = Math.min(1, Math.sqrt(cap / (img.width * img.height)));
      const w = Math.max(1, Math.round(img.width * scale));
      const h = Math.max(1, Math.round(img.height * scale));
      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      ctx.drawImage(img, 0, 0, w, h);
      const { data } = ctx.getImageData(0, 0, w, h);
      const buckets = new Map();
      let counted = 0;
      // Clamp to 255: Math.round(255 / 16) * 16 is 256, which overflows the byte
      // and carries into the next channel, mangling every near-white pixel.
      const quantise = (v) => Math.min(255, Math.round(v / step) * step);
      for (let i = 0; i < data.length; i += 4) {
        if (data[i + 3] < 128) continue;
        const key = (quantise(data[i]) << 16) | (quantise(data[i + 1]) << 8) | quantise(data[i + 2]);
        buckets.set(key, (buckets.get(key) || 0) + 1);
        counted += 1;
      }
      const out = [];
      for (const [key, count] of buckets) {
        out.push({
          rgb: [(key >> 16) & 255, (key >> 8) & 255, key & 255],
          share: count / counted,
        });
      }
      out.sort((a, b) => b.share - a.share);
      return { colors: out.slice(0, 48), pixels: counted, width: img.width, height: img.height };
    },
    [dataUrl, bucket, maxSamples]
  );
}

function toDataUrl(filePath) {
  return 'data:image/png;base64,' + fs.readFileSync(filePath).toString('base64');
}

/* ------------------------------------------------------------------- args */

function parseArgs(argv) {
  const args = { out: 'design-system-output', live: true, minShare: 0.004, timeout: 45000 };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const next = () => argv[(i += 1)];
    switch (key) {
      case '--out': args.out = next(); break;
      case '--min-share': args.minShare = Number(next()); break;
      case '--timeout': args.timeout = Number(next()); break;
      case '--no-live': args.live = false; break;
      case '--help': case '-h': args.help = true; break;
      default: throw new Error(`Unknown argument: ${key}`);
    }
  }
  return args;
}

/* ------------------------------------------------------------------- main */

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    console.log(fs.readFileSync(new URL(import.meta.url), 'utf8').split('*/')[0]);
    return 0;
  }

  const root = path.resolve(args.out);
  const tokensCss = path.join(root, 'tokens', 'tokens.css');
  const previewPath = path.join(root, 'tokens', 'preview.html');
  const manifestPath = path.join(root, 'evidence', 'crawl-manifest.json');
  for (const required of [tokensCss, previewPath, manifestPath]) {
    if (!fs.existsSync(required)) {
      console.error(`ERROR: missing ${required}. Run capture -> aggregate -> emit first.`);
      return 1;
    }
  }

  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const tokensJson = JSON.parse(fs.readFileSync(path.join(root, 'tokens', 'tokens.json'), 'utf8'));

  /* Collect the emitted palette (primitives are the concrete values). */
  const palette = [];
  for (const [name, entry] of Object.entries(tokensJson.color?.primitive || {})) {
    if (name.startsWith('$')) continue;
    const rgb = hexToRgb(entry.$value);
    if (rgb) palette.push({ name, hex: entry.$value, rgb });
  }
  if (!palette.length) {
    console.error('ERROR: no primitive colours in tokens.json');
    return 1;
  }

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ args: ['--disable-dev-shm-usage'] });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const decoder = await context.newPage();
  await decoder.goto('about:blank');

  const report = {
    schema: 'psdsm/fidelity-report@1',
    palette_size: palette.length,
    min_share: args.minShare,
    pages: [],
    components: [],
    summary: {},
  };

  /* ---- 1. palette fidelity against real source pixels ------------------ */
  for (const page of manifest.pages) {
    const shot = page.captures?.desktop_fold_screenshot || page.captures?.desktop_full_screenshot;
    if (!shot) continue;
    const shotPath = path.join(root, shot);
    if (!fs.existsSync(shotPath)) continue;

    let sampled;
    try {
      sampled = await dominantColors(decoder, toDataUrl(shotPath));
    } catch (err) {
      report.pages.push({ page_id: page.page_id, error: String(err).slice(0, 200) });
      continue;
    }

    const significant = sampled.colors.filter((c) => c.share >= args.minShare);
    let weighted = 0;
    let totalShare = 0;
    let covered = 0;
    const worst = [];
    for (const entry of significant) {
      let best = null;
      for (const token of palette) {
        const d = deltaE(entry.rgb, token.rgb);
        if (!best || d < best.delta) best = { delta: d, token };
      }
      weighted += best.delta * entry.share;
      totalShare += entry.share;
      /* ΔE 0.05 in OKLab is around the point two colours stop reading as the
         same swatch side by side. */
      if (best.delta <= 0.05) covered += entry.share;
      worst.push({
        source: rgbToHex(entry.rgb),
        share: Number(entry.share.toFixed(4)),
        nearest_token: best.token.name,
        nearest_hex: best.token.hex,
        delta_e: Number(best.delta.toFixed(4)),
      });
    }
    worst.sort((a, b) => b.delta_e * b.share - a.delta_e * a.share);
    report.pages.push({
      page_id: page.page_id,
      url: page.url,
      screenshot: shot,
      dominant_colors_considered: significant.length,
      mean_delta_e: totalShare ? Number((weighted / totalShare).toFixed(4)) : null,
      pixel_share_covered: Number(covered.toFixed(4)),
      worst_matches: worst.slice(0, 8),
    });
  }

  /* ---- 2. component fidelity: live element vs token-built element ------- */
  const fidelityDir = path.join(root, 'evidence', 'fidelity');
  fs.mkdirSync(fidelityDir, { recursive: true });

  const meanColorOf = async (imagePath) => {
    const sampled = await dominantColors(decoder, toDataUrl(imagePath), 8);
    let r = 0, g = 0, b = 0, total = 0;
    for (const c of sampled.colors) {
      r += c.rgb[0] * c.share; g += c.rgb[1] * c.share; b += c.rgb[2] * c.share;
      total += c.share;
    }
    return {
      mean: total ? [r / total, g / total, b / total] : [0, 0, 0],
      dominant: sampled.colors[0] ? rgbToHex(sampled.colors[0].rgb) : null,
      dominant_share: sampled.colors[0] ? Number(sampled.colors[0].share.toFixed(3)) : 0,
      size: { width: sampled.width, height: sampled.height },
    };
  };

  /* Render our token-built components. */
  const previewPage = await context.newPage();
  await previewPage.goto('file://' + previewPath, { waitUntil: 'networkidle' }).catch(() => {});
  const rebuilt = {};
  for (const [name, selector] of [
    ['button.primary', '#fx-button-primary'],
    ['field.input', '#fx-field'],
    ['surface.card', '#fx-card'],
  ]) {
    const locator = previewPage.locator(selector).first();
    if (!(await locator.isVisible().catch(() => false))) continue;
    const file = path.join(fidelityDir, `rebuilt.${name.replace(/\./g, '-')}.png`);
    await locator.screenshot({ path: file }).catch(() => {});
    if (fs.existsSync(file)) rebuilt[name] = { file, ...(await meanColorOf(file)) };
  }
  await previewPage.close();

  /* Screenshot the equivalent real elements on the live site. */
  if (args.live) {
    const observationsPath = path.join(root, 'evidence', 'component-observations.json');
    const observations = fs.existsSync(observationsPath)
      ? JSON.parse(fs.readFileSync(observationsPath, 'utf8'))
      : { components: [] };

    const pick = (predicate) => (observations.components || []).find(predicate);
    const targets = [
      ['button.primary', pick((c) => /button/.test(c.signature) && !/secondary|ghost|outline/i.test(c.signature))],
      ['field.input', pick((c) => /^input/.test(c.signature))],
    ].filter(([, component]) => component?.selector);

    const sourceUrl = manifest.pages[0]?.url;
    if (sourceUrl && targets.length) {
      const livePage = await context.newPage();
      try {
        await livePage.goto(sourceUrl, { waitUntil: 'domcontentloaded', timeout: args.timeout });
        await livePage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
        // Same page treatment as capture, or we screenshot the cookie banner
        // sitting on top of the component instead of the component.
        await dismissConsent(livePage);
        await settlePage(livePage, 600);
        await freezeAnimations(livePage);
        for (const [name, component] of targets) {
          const locator = livePage.locator(component.selector).first();
          if (!(await locator.isVisible().catch(() => false))) continue;
          await locator.scrollIntoViewIfNeeded().catch(() => {});
          const file = path.join(fidelityDir, `source.${name.replace(/\./g, '-')}.png`);
          await locator.screenshot({ path: file }).catch(() => {});
          if (!fs.existsSync(file)) continue;
          const source = await meanColorOf(file);
          const ours = rebuilt[name];
          report.components.push({
            component: name,
            source_selector: component.selector,
            source: { file: path.relative(root, file), dominant: source.dominant, size: source.size },
            rebuilt: ours
              ? { file: path.relative(root, ours.file), dominant: ours.dominant, size: ours.size }
              : null,
            mean_delta_e: ours ? Number(deltaE(source.mean, ours.mean).toFixed(4)) : null,
            dominant_delta_e:
              ours && source.dominant && ours.dominant
                ? Number(deltaE(hexToRgb(source.dominant), hexToRgb(ours.dominant)).toFixed(4))
                : null,
            height_delta_px: ours ? source.size.height - ours.size.height : null,
          });
        }
      } catch (err) {
        report.components.push({ error: `live capture failed: ${String(err).slice(0, 200)}` });
      } finally {
        await livePage.close();
      }
    }
  }

  await browser.close();

  /* ---- 3. summarise ----------------------------------------------------- */
  const pageScores = report.pages.filter((p) => p.mean_delta_e !== null && p.mean_delta_e !== undefined);
  const meanDelta = pageScores.length
    ? pageScores.reduce((sum, p) => sum + p.mean_delta_e, 0) / pageScores.length
    : null;
  const meanCoverage = pageScores.length
    ? pageScores.reduce((sum, p) => sum + p.pixel_share_covered, 0) / pageScores.length
    : null;

  const grade =
    meanDelta === null ? 'unknown'
      : meanDelta <= 0.03 ? 'high'
      : meanDelta <= 0.07 ? 'moderate'
      : 'low';

  report.summary = {
    pages_scored: pageScores.length,
    mean_palette_delta_e: meanDelta === null ? null : Number(meanDelta.toFixed(4)),
    mean_pixel_share_covered: meanCoverage === null ? null : Number(meanCoverage.toFixed(4)),
    palette_fidelity: grade,
    components_compared: report.components.filter((c) => !c.error).length,
    interpretation:
      'mean_palette_delta_e is the pixel-share-weighted OKLab distance from each dominant ' +
      'source colour to its nearest emitted token. <=0.03 high, <=0.07 moderate, above that ' +
      'the token palette is not reproducing what the site actually renders.',
  };

  fs.writeFileSync(path.join(root, 'evidence', 'fidelity-report.json'), JSON.stringify(report, null, 2), 'utf8');

  /* Human-readable companion report. */
  const lines = [
    '# Fidelity Check',
    '',
    'Round-trip verification: the emitted token set measured back against the pixels',
    'the source site actually renders. This is independent of the confidence scores —',
    'confidence says how sure the measurement was, this says whether the result matches.',
    '',
    '## Palette fidelity',
    '',
    `- Pages scored: **${report.summary.pages_scored}**`,
    `- Mean OKLab ΔE to nearest token: **${report.summary.mean_palette_delta_e ?? 'n/a'}** (${grade})`,
    `- Dominant pixel share within ΔE 0.05 of a token: **${
      meanCoverage === null ? 'n/a' : (meanCoverage * 100).toFixed(1) + '%'
    }**`,
    '',
    '| Page | Mean ΔE | Covered | Worst match |',
    '| --- | --- | --- | --- |',
    ...pageScores.map((p) => {
      const worst = p.worst_matches[0];
      return `| \`${p.page_id}\` | ${p.mean_delta_e} | ${(p.pixel_share_covered * 100).toFixed(1)}% | ${
        worst ? `${worst.source} → \`${worst.nearest_token}\` (ΔE ${worst.delta_e})` : '—'
      } |`;
    }),
    '',
  ];

  const comparedComponents = report.components.filter((c) => !c.error);
  lines.push('## Component fidelity', '');
  if (comparedComponents.length) {
    lines.push(
      'The real element on the live site, screenshotted next to the same component rebuilt',
      'from the emitted tokens alone.',
      '',
      '| Component | Source | Rebuilt | Dominant ΔE | Height delta |',
      '| --- | --- | --- | --- | --- |',
      ...comparedComponents.map(
        (c) =>
          `| \`${c.component}\` | ${c.source.dominant} | ${c.rebuilt?.dominant ?? '—'} | ${
            c.dominant_delta_e ?? '—'
          } | ${c.height_delta_px ?? '—'}px |`
      ),
      ''
    );
  } else {
    lines.push('_No components compared (run without `--no-live`, or no matching selectors were found)._', '');
  }

  const uncovered = pageScores
    .flatMap((p) => p.worst_matches.filter((w) => w.delta_e > 0.05))
    .sort((a, b) => b.share - a.share)
    .slice(0, 10);
  if (uncovered.length) {
    lines.push(
      '## Colours the token set does not cover',
      '',
      'These occupy real screen area on the source but have no close token. They are',
      'usually imagery, gradients, or third-party embeds — confirm before adding them.',
      '',
      '| Source colour | Pixel share | Nearest token | ΔE |',
      '| --- | --- | --- | --- |',
      ...uncovered.map(
        (w) => `| ${w.source} | ${(w.share * 100).toFixed(2)}% | \`${w.nearest_token}\` (${w.nearest_hex}) | ${w.delta_e} |`
      ),
      ''
    );
  }

  const reportsDir = path.join(root, 'reports');
  fs.mkdirSync(reportsDir, { recursive: true });
  fs.writeFileSync(path.join(reportsDir, 'fidelity-check.md'), lines.join('\n'), 'utf8');

  console.error(`[fidelity] palette ΔE ${report.summary.mean_palette_delta_e} (${grade}), ` +
    `coverage ${meanCoverage === null ? 'n/a' : (meanCoverage * 100).toFixed(1) + '%'}, ` +
    `${comparedComponents.length} component(s) compared`);
  console.error('[fidelity] wrote evidence/fidelity-report.json and reports/fidelity-check.md');
  return 0;
}

main().then(
  (code) => process.exit(code),
  (err) => {
    console.error(`[fidelity] fatal: ${err.stack || err}`);
    process.exit(1);
  }
);
