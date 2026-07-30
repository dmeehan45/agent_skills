/**
 * Shared browser helpers for the capture and fidelity stages.
 *
 * Both stages must treat the page identically — if capture dismisses a cookie
 * banner and fidelity_check does not, the fidelity comparison measures the
 * banner instead of the component.
 */

import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';

const require = createRequire(import.meta.url);

export function loadPlaywright() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE_PATH) candidates.push(process.env.PLAYWRIGHT_MODULE_PATH);
  candidates.push('playwright');
  try {
    const globalRoot = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
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
  '#CybotCookiebotDialogBodyButtonAccept',
  '.osano-cm-accept-all',
  'button[id*="accept" i]',
  'button[class*="accept" i]',
  'button[data-testid*="accept" i]',
  '[aria-label*="accept" i]',
];

const CONSENT_TEXTS = [
  /^accept all/i, /^accept cookies/i, /^accept$/i, /^allow all/i, /^i agree/i,
  /^agree$/i, /^got it/i, /^ok, got it/i, /^understood/i, /^continue$/i,
];

/**
 * Consent overlays wreck screenshots and obscure the components we measure.
 * Tries known vendor selectors, then button text, then hides any large fixed
 * overlay whose text looks like a consent notice.
 */
export async function dismissConsent(page) {
  for (const selector of CONSENT_SELECTORS) {
    try {
      const el = page.locator(selector).first();
      if (await el.isVisible({ timeout: 400 })) {
        await el.click({ timeout: 1500 });
        await page.waitForTimeout(400);
        return { dismissed: true, method: `selector:${selector}` };
      }
    } catch {
      /* try the next selector */
    }
  }
  try {
    const buttons = await page.locator('button, [role="button"], a[role="button"]').all();
    for (const button of buttons.slice(0, 60)) {
      const text = ((await button.textContent().catch(() => '')) || '').trim();
      if (text && CONSENT_TEXTS.some((re) => re.test(text))) {
        if (await button.isVisible().catch(() => false)) {
          await button.click({ timeout: 1500 }).catch(() => {});
          await page.waitForTimeout(400);
          return { dismissed: true, method: `text:${text.slice(0, 40)}` };
        }
      }
    }
  } catch {
    /* fall through to the overlay sweep */
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

/** Scroll through the page to trigger lazy-loading, then return to the top. */
export async function settlePage(page, settleMs = 1200) {
  await page
    .evaluate(async () => {
      const step = Math.max(400, window.innerHeight * 0.8);
      const limit = Math.min(document.documentElement.scrollHeight, 30000);
      for (let y = 0; y < limit; y += step) {
        window.scrollTo(0, y);
        await new Promise((r) => setTimeout(r, 90));
      }
      window.scrollTo(0, 0);
      await new Promise((r) => setTimeout(r, 150));
    })
    .catch(() => {});
  await page.waitForTimeout(settleMs);
  await page
    .evaluate(() => {
      for (const img of Array.from(document.querySelectorAll('img[loading="lazy"]'))) {
        img.loading = 'eager';
      }
    })
    .catch(() => {});
}

/** Pause animations and transitions so screenshots are deterministic. */
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
