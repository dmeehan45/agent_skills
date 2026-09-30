/**
 * Browser helpers for the journey walker.
 *
 * Deliberately small and dependency-free beyond Playwright itself, so the
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
    const globalRoot = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    if (globalRoot) candidates.push(path.join(globalRoot, 'playwright'));
  } catch {
    /* npm unavailable; fall through */
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
 * A consent overlay sits on top of the surface being walked and would dominate
 * every screenshot and reading. Dismiss it before anything else runs. This is
 * the one click the walker makes on its own; it is confined to consent
 * controls and never touches product actions.
 */
export async function dismissConsent(page) {
  for (const selector of CONSENT_SELECTORS) {
    try {
      const el = page.locator(selector).first();
      if (await el.isVisible({ timeout: 300 })) {
        await el.click({ timeout: 1500 });
        await page.waitForTimeout(300);
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

  return hidden > 0 ? { dismissed: true, method: `overlay-hidden:${hidden}` } : { dismissed: false, method: null };
}

/** Resolve a step target that may be a URL, a path on a base URL, or a local file. */
export function resolveTarget(target, baseUrl) {
  if (/^https?:\/\//i.test(target) || target.startsWith('file://')) return target;
  if (baseUrl) return new URL(target, baseUrl.endsWith('/') ? baseUrl : baseUrl + '/').toString();
  return 'file://' + path.resolve(target);
}
