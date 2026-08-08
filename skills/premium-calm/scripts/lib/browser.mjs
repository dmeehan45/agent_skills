/**
 * Browser helpers for the premium-calm measurement stage.
 *
 * Kept deliberately small and dependency-free beyond Playwright itself, so the
 * skill folder can be copied into any project and run without a build step.
 */

import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';

const require = createRequire(import.meta.url);

/**
 * Playwright is usually a global install in agent images and a local devDep in
 * product repos. Try both rather than forcing one layout on the caller.
 */
export function loadPlaywright() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE_PATH) candidates.push(process.env.PLAYWRIGHT_MODULE_PATH);
  candidates.push('playwright');
  try {
    const globalRoot = execSync('npm root -g', {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
    if (globalRoot) candidates.push(path.join(globalRoot, 'playwright'));
  } catch {
    /* npm unavailable; fall through to the remaining candidates */
  }
  candidates.push('/opt/node22/lib/node_modules/playwright');

  const tried = [];
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (err) {
      tried.push(`${candidate}: ${err.code || err.message}`);
    }
  }
  throw new Error(
    'Could not load Playwright. Install it (`npm i -g playwright`) or set ' +
      `PLAYWRIGHT_MODULE_PATH. Tried:\n  ${tried.join('\n  ')}`
  );
}

const CONSENT_SELECTORS = [
  '#onetrust-accept-btn-handler',
  '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
  '.osano-cm-accept-all',
  'button[id*="accept" i]',
  'button[class*="accept" i]',
  '[aria-label*="accept cookies" i]',
];

/**
 * A consent overlay sits on top of the surface being measured and would
 * dominate every salience, contrast, and target-size reading. Dismiss it before
 * anything else runs.
 */
export async function dismissConsent(page) {
  for (const selector of CONSENT_SELECTORS) {
    try {
      const el = page.locator(selector).first();
      if (await el.isVisible({ timeout: 300 })) {
        await el.click({ timeout: 1500 });
        await page.waitForTimeout(350);
        return { dismissed: true, method: `selector:${selector}` };
      }
    } catch {
      /* try the next selector */
    }
  }

  const hidden = await page
    .evaluate(() => {
      let n = 0;
      for (const el of Array.from(document.body.querySelectorAll('*'))) {
        const cs = getComputedStyle(el);
        if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
        const rect = el.getBoundingClientRect();
        const coverage = (rect.width * rect.height) / (window.innerWidth * window.innerHeight);
        const text = (el.textContent || '').toLowerCase();
        if (coverage > 0.25 && /cookie|consent|privacy|gdpr/.test(text)) {
          el.style.setProperty('display', 'none', 'important');
          n += 1;
        }
      }
      return n;
    })
    .catch(() => 0);

  return hidden > 0
    ? { dismissed: true, method: `overlay-hidden:${hidden}` }
    : { dismissed: false, method: null };
}

/** Scroll the full height to trigger lazy content, then return to the top. */
export async function settlePage(page, settleMs = 900) {
  await page
    .evaluate(async () => {
      const step = Math.max(400, window.innerHeight * 0.8);
      const limit = Math.min(document.documentElement.scrollHeight, 24000);
      for (let y = 0; y < limit; y += step) {
        window.scrollTo(0, y);
        await new Promise((r) => setTimeout(r, 80));
      }
      window.scrollTo(0, 0);
      await new Promise((r) => setTimeout(r, 150));
    })
    .catch(() => {});
  await page.waitForTimeout(settleMs);
}

/**
 * Pause animation for the still renders only. Motion is inventoried from
 * computed styles before this runs, so freezing here costs no evidence.
 */
export async function freezeAnimations(page) {
  await page
    .addStyleTag({
      content: `*, *::before, *::after {
        animation-play-state: paused !important;
        animation-delay: 0s !important;
        transition: none !important;
        caret-color: transparent !important;
        scroll-behavior: auto !important;
      }`,
    })
    .catch(() => {});
}

/** Resolve a surface target that may be a URL or a local file path. */
export function resolveTarget(target) {
  if (/^https?:\/\//i.test(target) || target.startsWith('file://')) return target;
  return 'file://' + path.resolve(target);
}
