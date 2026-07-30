#!/usr/bin/env python3
"""Discover and select a representative public page set for capture.

Reads robots.txt and sitemap.xml, falls back to a shallow link crawl, classifies
URLs into template types, and selects a diverse sample biased toward template
coverage rather than page count.

Writes `crawl-plan.json`, which `capture_site.mjs --urls` consumes.

Usage:
  python3 discover_urls.py https://example.com --out crawl-plan.json
  python3 discover_urls.py https://example.com --max-pages 12 --no-robots
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Any

USER_AGENT = "design-system-extractor/1.0 (+design-system-extractor)"

# Path patterns -> template type. Order matters: first match wins.
TEMPLATE_PATTERNS: list[tuple[str, str]] = [
    (r"^/?$", "home"),
    (r"/(pricing|plans|price)(/|$)", "pricing"),
    (r"/(docs?|documentation|guide|reference|api)(/|$)", "docs"),
    (r"/(blog|news|articles?|insights|resources/[^/]+)(/|$)", "article"),
    (r"/(contact|demo|sales|get-started|signup|sign-up|request)(/|$)", "contact_form"),
    (r"/(products?|features?|solutions?|platform|use-cases?)(/|$)", "feature"),
    (r"/(customers?|case-stud|success)(/|$)", "case_study"),
    (r"/(about|company|team|mission)(/|$)", "about"),
    (r"/(support|help|faq)(/|$)", "help"),
    (r"/(integrations?|marketplace|apps)(/|$)", "catalog"),
    (r"/(changelog|releases?)(/|$)", "changelog"),
]

# Excluded from brand-voice weighting, but still valuable typography evidence:
# legal pages carry long-form body copy and link styling with no marketing noise.
TYPOGRAPHY_ONLY_PATTERNS = r"/(legal|privacy|terms|cookie|gdpr|dpa|sla|accessibility)(/|$)"

# Never worth capturing: no design signal, or out of scope entirely.
HARD_EXCLUDE_PATTERNS = [
    r"/(login|signin|sign-in|logout|register|account|dashboard|admin)(/|$)",
    r"/(cart|checkout|order)(/|$)",
    r"\.(pdf|zip|csv|xlsx?|docx?|pptx?|dmg|exe|mp4|mp3|svg|png|jpe?g|gif|webp|ico)$",
    r"/(wp-admin|wp-json|cdn-cgi|__)",
    r"/(feed|rss|atom)(/|$)",
]


def build_opener(insecure: bool = False) -> urllib.request.OpenerDirector:
    """Honour proxy env vars and any configured CA bundle."""
    context = ssl.create_default_context()
    ca_bundle = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if ca_bundle and os.path.exists(ca_bundle):
        context.load_verify_locations(ca_bundle)
    if insecure:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    handlers: list[Any] = [urllib.request.HTTPSHandler(context=context)]
    proxies = urllib.request.getproxies()
    if proxies:
        handlers.append(urllib.request.ProxyHandler(proxies))
    opener = urllib.request.build_opener(*handlers)
    opener.addheaders = [("User-Agent", USER_AGENT)]
    return opener


def fetch(opener, url: str, timeout: float = 15.0) -> tuple[bytes | None, str | None]:
    try:
        with opener.open(url, timeout=timeout) as response:
            data = response.read(8_000_000)
            if response.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
                try:
                    data = gzip.decompress(data)
                except OSError:
                    pass
            return data, None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)[:160]


# ------------------------------------------------------------------- robots


class Robots:
    """Minimal robots.txt evaluator for the `*` and our own user-agent groups."""

    def __init__(self) -> None:
        self.disallow: list[str] = []
        self.allow: list[str] = []
        self.sitemaps: list[str] = []
        self.crawl_delay: float | None = None
        self.fetched = False
        self.error: str | None = None

    @classmethod
    def load(cls, opener, base: str) -> "Robots":
        robots = cls()
        body, error = fetch(opener, urllib.parse.urljoin(base, "/robots.txt"))
        if body is None:
            robots.error = error
            return robots
        robots.fetched = True
        applies = False
        for raw_line in body.decode("utf-8", "replace").splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            field, _, value = line.partition(":")
            field, value = field.strip().lower(), value.strip()
            if field == "user-agent":
                applies = value == "*" or "psdsm" in value.lower()
            elif field == "sitemap":
                robots.sitemaps.append(value)
            elif applies and field == "disallow" and value:
                robots.disallow.append(value)
            elif applies and field == "allow" and value:
                robots.allow.append(value)
            elif applies and field == "crawl-delay":
                try:
                    robots.crawl_delay = float(value)
                except ValueError:
                    pass
        return robots

    @staticmethod
    def _matches(pattern: str, path: str) -> bool:
        regex = re.escape(pattern).replace(r"\*", ".*")
        if regex.endswith(r"\$"):
            regex = regex[:-2] + "$"
        return re.match(regex, path) is not None

    def allowed(self, url: str) -> bool:
        path = urllib.parse.urlparse(url).path or "/"
        # Longest matching rule wins, Allow beating Disallow at equal length.
        best_len, verdict = -1, True
        for pattern in self.disallow:
            if self._matches(pattern, path) and len(pattern) > best_len:
                best_len, verdict = len(pattern), False
        for pattern in self.allow:
            if self._matches(pattern, path) and len(pattern) >= best_len:
                best_len, verdict = len(pattern), True
        return verdict


# ------------------------------------------------------------------ sitemap


def parse_sitemap(opener, url: str, depth: int = 0, seen: set[str] | None = None) -> list[str]:
    seen = seen if seen is not None else set()
    if depth > 2 or url in seen or len(seen) > 40:
        return []
    seen.add(url)
    body, _ = fetch(opener, url)
    if not body:
        return []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls: list[str] = []
    for entry in root.findall(".//sm:sitemap/sm:loc", namespace):
        if entry.text:
            urls.extend(parse_sitemap(opener, entry.text.strip(), depth + 1, seen))
    for entry in root.findall(".//sm:url/sm:loc", namespace):
        if entry.text:
            urls.append(entry.text.strip())
    if not urls:  # namespace-less sitemaps
        for entry in root.iter():
            if entry.tag.endswith("loc") and entry.text:
                urls.append(entry.text.strip())
    return urls


# -------------------------------------------------------------- link crawl

LINK_RE = re.compile(rb'<a\b[^>]*href=["\']([^"\'#]+)', re.IGNORECASE)


def shallow_crawl(opener, base: str, max_pages: int, delay: float) -> list[str]:
    """Static link harvest from the homepage plus its first-level pages.

    JS-rendered navigation will not appear here; `capture_site.mjs` records the
    links it sees in a real browser, so a second discovery pass can use those.
    """
    origin = urllib.parse.urlparse(base)
    found: list[str] = []
    queue = [base]
    visited: set[str] = set()
    while queue and len(visited) < min(8, max_pages):
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        body, _ = fetch(opener, current)
        time.sleep(delay)
        if not body:
            continue
        for match in LINK_RE.findall(body):
            href = match.decode("utf-8", "replace")
            absolute = urllib.parse.urljoin(current, href)
            parsed = urllib.parse.urlparse(absolute)
            if parsed.netloc != origin.netloc or parsed.scheme not in ("http", "https"):
                continue
            clean = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/") or "/", "", "", ""))
            if clean not in found:
                found.append(clean)
            if len(found) < 60 and clean not in visited and len(queue) < 12:
                queue.append(clean)
    return found


# ------------------------------------------------------------- classification


def classify(url: str) -> str:
    path = urllib.parse.urlparse(url).path or "/"
    for pattern, template in TEMPLATE_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return template
    return "other"


def is_hard_excluded(url: str) -> bool:
    path = urllib.parse.urlparse(url).path or "/"
    return any(re.search(pattern, path, re.IGNORECASE) for pattern in HARD_EXCLUDE_PATTERNS)


def is_typography_only(url: str) -> bool:
    path = urllib.parse.urlparse(url).path or "/"
    return bool(re.search(TYPOGRAPHY_ONLY_PATTERNS, path, re.IGNORECASE))


def depth_of(url: str) -> int:
    return len([segment for segment in urllib.parse.urlparse(url).path.split("/") if segment])


# Preference order when the budget is tight: these carry the most design signal.
TEMPLATE_PRIORITY = [
    "home", "pricing", "feature", "docs", "contact_form", "article",
    "case_study", "catalog", "help", "about", "changelog", "other",
]


def select_sample(urls: list[str], max_pages: int, per_template: int) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for url in urls:
        buckets[classify(url)].append(url)
    for template in buckets:
        # Shallow, short URLs are canonical templates; deep ones are instances.
        buckets[template].sort(key=lambda u: (depth_of(u), len(u)))

    selected: list[dict[str, Any]] = []
    ordered = sorted(buckets, key=lambda t: TEMPLATE_PRIORITY.index(t) if t in TEMPLATE_PRIORITY else 99)

    # Round-robin so template diversity beats depth in any single bucket.
    for round_index in range(per_template):
        for template in ordered:
            if len(selected) >= max_pages:
                break
            if round_index < len(buckets[template]):
                url = buckets[template][round_index]
                selected.append(
                    {
                        "url": url,
                        "template_guess": template,
                        "selection_reason": (
                            f"{template} template, instance {round_index + 1} of "
                            f"{len(buckets[template])} discovered"
                        ),
                        "evidence_scope": "typography_only" if is_typography_only(url) else "full",
                    }
                )
        if len(selected) >= max_pages:
            break

    for index, entry in enumerate(selected):
        path = urllib.parse.urlparse(entry["url"]).path.strip("/") or "home"
        slug = re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")[:40] or "page"
        entry["page_id"] = f"p_{index:02d}_{slug}"
    return selected


# -------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source_url", help="Public site root, e.g. https://example.com")
    parser.add_argument("--out", default="crawl-plan.json")
    parser.add_argument("--max-pages", type=int, default=14)
    parser.add_argument("--per-template", type=int, default=2, help="max instances per template type")
    parser.add_argument("--delay", type=float, default=0.5, help="seconds between discovery requests")
    parser.add_argument("--no-robots", action="store_true", help="skip robots.txt (requires explicit user authorisation)")
    parser.add_argument("--include-typography-only", action="store_true",
                        help="include legal/terms pages as typography evidence (default on when budget allows)")
    parser.add_argument("--insecure", action="store_true", help="skip TLS verification (diagnostics only)")
    args = parser.parse_args()

    base = args.source_url.rstrip("/") + "/"
    parsed = urllib.parse.urlparse(base)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print(f"ERROR: {args.source_url} is not an http(s) URL")
        return 1

    opener = build_opener(insecure=args.insecure)
    plan: dict[str, Any] = {
        "schema": "psdsm/crawl-plan@1",
        "source_url": base,
        "respect_robots_txt": not args.no_robots,
        "discovery": {},
        "excluded": [],
        "pages": [],
    }

    robots = Robots.load(opener, base)
    plan["discovery"]["robots"] = {
        "fetched": robots.fetched,
        "error": robots.error,
        "disallow_rules": len(robots.disallow),
        "sitemaps_declared": robots.sitemaps,
        "crawl_delay": robots.crawl_delay,
    }
    if args.no_robots:
        print("WARNING: robots.txt is being ignored. Confirm the user authorised this and policy permits it.")

    candidates: list[str] = []
    sitemap_urls = robots.sitemaps or [urllib.parse.urljoin(base, "/sitemap.xml")]
    for sitemap in sitemap_urls[:4]:
        found = parse_sitemap(opener, sitemap)
        if found:
            candidates.extend(found)
        time.sleep(args.delay)
    plan["discovery"]["sitemap_urls_found"] = len(candidates)

    if len(candidates) < 4:
        crawled = shallow_crawl(opener, base, args.max_pages, args.delay)
        plan["discovery"]["link_crawl_urls_found"] = len(crawled)
        candidates.extend(crawled)
    else:
        plan["discovery"]["link_crawl_urls_found"] = 0

    if base not in candidates and base.rstrip("/") not in candidates:
        candidates.insert(0, base)

    # Normalise, dedupe, and filter.
    seen: set[str] = set()
    kept: list[str] = []
    for url in candidates:
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.netloc != parsed.netloc:
            plan["excluded"].append({"url": url, "reason": "different host"})
            continue
        clean = urllib.parse.urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path.rstrip("/") or "/", "", "", "")
        )
        if clean in seen:
            continue
        seen.add(clean)
        if is_hard_excluded(clean):
            plan["excluded"].append({"url": clean, "reason": "no design signal / out of scope"})
            continue
        if not args.no_robots and not robots.allowed(clean):
            plan["excluded"].append({"url": clean, "reason": "disallowed by robots.txt"})
            continue
        if is_typography_only(clean) and not args.include_typography_only:
            plan["excluded"].append(
                {"url": clean, "reason": "legal/policy page — re-add with --include-typography-only for body-copy evidence"}
            )
            continue
        kept.append(clean)

    plan["discovery"]["candidates_after_filtering"] = len(kept)
    plan["pages"] = select_sample(kept, args.max_pages, args.per_template)
    plan["crawl_delay_ms"] = int((robots.crawl_delay or args.delay) * 1000)

    coverage: dict[str, int] = defaultdict(int)
    for page in plan["pages"]:
        coverage[page["template_guess"]] += 1
    plan["template_coverage"] = dict(coverage)
    missing = [t for t in ("home", "pricing", "feature", "docs", "contact_form") if t not in coverage]
    plan["coverage_gaps"] = missing

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2)

    print(f"Discovered {len(kept)} candidate page(s); selected {len(plan['pages'])}")
    print(f"  robots.txt:        {'fetched' if robots.fetched else robots.error}")
    print(f"  sitemap URLs:      {plan['discovery']['sitemap_urls_found']}")
    print(f"  link-crawl URLs:   {plan['discovery']['link_crawl_urls_found']}")
    print(f"  template coverage: {dict(coverage)}")
    if missing:
        print(f"  WARNING missing high-signal templates: {missing}")
    print(f"  excluded:          {len(plan['excluded'])}")
    print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
