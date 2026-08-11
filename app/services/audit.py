"""Website health audit engine.

Runs a full site integrity audit (SEO, accessibility, links, security,
performance, content) against a URL and persists the results using the
AuditResult / AuditIssue models.
"""
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from flask import request
from werkzeug.user_agent import UserAgent  # noqa: F401  (kept for parity)

from app.extensions import db
from app.models import AuditResult, AuditIssue

USER_AGENT = "ImpactBridgeAudit/1.0"
TIMEOUT = 12
MAX_ISSUE_TITLE = 255


# ── HTTP helpers ────────────────────────────────────────────────────
def _fetch(url, timeout=TIMEOUT):
    try:
        return requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
    except Exception:
        return None


def _resolve(base_url, href):
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    try:
        return urljoin(base_url, href)
    except Exception:
        return None


def _is_internal(url, netloc):
    try:
        return urlparse(url).netloc == netloc
    except Exception:
        return False


def _check_url_ok(url, timeout=8):
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={"User-Agent": USER_AGENT})
        if r.status_code < 400:
            return True
        # Some servers block HEAD – fall back to GET
        r2 = requests.get(url, timeout=timeout, allow_redirects=True,
                          headers={"User-Agent": USER_AGENT}, stream=True)
        r2.close()
        return r2.status_code < 400
    except Exception:
        return False


# ── Scoring helpers ─────────────────────────────────────────────────
def _grade(score):
    if score >= 90:
        return "A+ (Excellent)"
    if score >= 80:
        return "A (Great)"
    if score >= 70:
        return "B (Good)"
    if score >= 60:
        return "C (Fair)"
    if score >= 50:
        return "D (Poor)"
    return "F (Critical)"


def _clamp(n, lo=0, hi=100):
    return max(lo, min(hi, n))


# ── Category audit functions ────────────────────────────────────────
def audit_seo(soup, issues):
    """SEO: title, meta description, headings, image alt text."""
    score = 100
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if not title:
        score -= 25
        issues.append(("seo", "HIGH", "Missing <title> tag",
                       "Add a descriptive <title> (30–60 chars) to every page."))
    else:
        if not 30 <= len(title) <= 60:
            issues.append(("seo", "LOW", "Title length outside 30–60 chars",
                           f"Current title is {len(title)} chars: '{title[:60]}…'."))

    desc = None
    for meta in soup.find_all("meta"):
        if (meta.get("name") or "").lower() == "description":
            desc = (meta.get("content") or "").strip()
            break
    if not desc:
        score -= 20
        issues.append(("seo", "HIGH", "Missing meta description",
                       "Add a meta description (50–160 chars) summarising the page."))
    else:
        if not 50 <= len(desc) <= 160:
            issues.append(("seo", "LOW", "Meta description length outside 50–160 chars",
                           f"Current description is {len(desc)} chars."))

    h1s = soup.find_all("h1")
    if not h1s:
        score -= 20
        issues.append(("seo", "HIGH", "Missing <h1> heading",
                       "Add exactly one <h1> that describes the page's primary topic."))
    elif len(h1s) > 1:
        score -= 10
        issues.append(("seo", "LOW", "Multiple <h1> headings",
                       f"Found {len(h1s)} <h1> tags – use one h1 per page."))

    if not soup.find_all("h2"):
        score -= 10
        issues.append(("seo", "LOW", "No <h2> sub-headings",
                       "Use <h2> headings to structure content sections."))

    imgs = soup.find_all("img")
    missing_alt = [i for i in imgs if not (i.get("alt") or "").strip()]
    if missing_alt:
        score -= min(10 + len(missing_alt), 20)
        issues.append(("seo", "HIGH", f"{len(missing_alt)} image(s) missing alt text",
                       "Add descriptive alt attributes to all images."))

    return _clamp(score)


def audit_accessibility(soup, issues):
    """Accessibility: alt text, form labels, links, text size."""
    score = 100
    imgs = soup.find_all("img")
    missing_alt = [i for i in imgs if not (i.get("alt") or "").strip()]
    if missing_alt:
        score -= min(10 * len(missing_alt), 40)
        issues.append(("accessibility", "HIGH",
                       f"{len(missing_alt)} image(s) missing alt text",
                       "Screen readers rely on alt text. Add it to every image."))

    for form in soup.find_all("form"):
        inputs = [i for i in form.find_all("input") if i.get("type") != "hidden"]
        for inp in inputs:
            label = None
            if inp.get("aria-label"):
                continue
            if inp.get("id"):
                label = soup.find("label", attrs={"for": inp["id"]})
            if not label and not inp.get("placeholder"):
                score -= 10
                issues.append(("accessibility", "HIGH",
                               "Form input missing accessible label",
                               f"Add a <label for='{inp.get('id') or ''}'> or aria-label to input."))
                break

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        if not text and not a.get("aria-label") and not a.get("title"):
            score -= 5
            issues.append(("accessibility", "MEDIUM",
                           "Link with no discernible text",
                           "Add text, aria-label, or title to every anchor."))
            break

    return _clamp(score)


def audit_links(soup, issues, base_url):
    """Links: check internal links for broken / 404 responses."""
    netloc = urlparse(base_url).netloc
    links = []
    for a in soup.find_all("a", href=True):
        resolved = _resolve(base_url, a["href"])
        if resolved and _is_internal(resolved, netloc):
            links.append(resolved)

    broken = []
    checked = set()
    for url in links:
        if url in checked:
            continue
        checked.add(url)
        if not _check_url_ok(url):
            broken.append(url)

    score = _clamp(100 - 12 * len(broken))
    if broken:
        issues.append(("links", "HIGH" if len(broken) > 2 else "MEDIUM",
                       f"{len(broken)} broken internal link(s)",
                       "Fix or remove: " + ", ".join(broken[:4]) +
                       ("…" if len(broken) > 4 else "")))
    if not links:
        score -= 10
        issues.append(("links", "LOW", "No internal links found",
                       "Add internal links to help navigation and indexing."))
    return score


def audit_security(resp, soup, issues):
    """Security: HTTPS, mixed content, security headers."""
    score = 100
    url = resp.url if hasattr(resp, "url") else ""
    if not url.startswith("https://"):
        score -= 40
        issues.append(("security", "HIGH", "Site not served over HTTPS",
                       "Enable TLS / HTTPS to protect user data."))

    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("http://"):
            score -= 10
            issues.append(("security", "HIGH", "Mixed-content (HTTP) resource",
                           f"Image loaded over insecure HTTP: {src[:80]}…"))
            break

    headers = getattr(resp, "headers", {}) or {}
    if not headers.get("X-Frame-Options"):
        score -= 15
        issues.append(("security", "MEDIUM", "Missing X-Frame-Options header",
                       "Add X-Frame-Options: DENY or SAMEORIGIN to prevent clickjacking."))
    if not headers.get("Content-Security-Policy"):
        score -= 10
        issues.append(("security", "LOW", "Missing Content-Security-Policy header",
                       "A CSP header reduces XSS risk."))

    for script in soup.find_all("script", src=True):
        if script["src"].startswith("http://"):
            score -= 10
            issues.append(("security", "HIGH", "Insecure script loaded over HTTP",
                           f"Script: {script['src'][:80]}…"))
            break

    return _clamp(score)


def audit_performance(resp, soup, issues):
    """Performance: page size, script count, compression."""
    score = 100
    content = (resp.content or b"") if hasattr(resp, "content") else b""
    size_kb = len(content) / 1024
    if size_kb > 2048:
        score -= 30
        issues.append(("performance", "HIGH",
                       f"Page size very large ({size_kb:.0f} KB)",
                       "Optimise images and minify CSS/JS."))
    elif size_kb > 512:
        score -= 15
        issues.append(("performance", "MEDIUM",
                       f"Page size large ({size_kb:.0f} KB)",
                       "Consider compressing assets and lazy-loading images."))

    scripts = soup.find_all("script", src=True)
    if len(scripts) > 10:
        score -= 10
        issues.append(("performance", "LOW",
                       f"{len(scripts)} external scripts",
                       "Bundle and minify scripts to reduce requests."))

    encoding = (resp.headers.get("Content-Encoding") or "") if hasattr(resp, "headers") else ""
    if "gzip" not in encoding and "br" not in encoding:
        score -= 10
        issues.append(("performance", "LOW", "Response not compressed",
                       "Enable gzip / brotli compression."))
    return _clamp(score)


def audit_content(soup, issues):
    """Content: word count, text ratio, links, structure."""
    score = 100
    text = soup.get_text(" ", strip=True)
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    if word_count < 100:
        score -= 40
        issues.append(("content", "HIGH",
                       f"Very little content ({word_count} words)",
                       "Add meaningful text content to the page."))
    elif word_count < 300:
        score -= 20
        issues.append(("content", "MEDIUM",
                       f"Thin content ({word_count} words)",
                       "Aim for at least 300 words of unique content."))

    internal_links = len([1 for a in soup.find_all("a", href=True)
                          if (a["href"] or "").startswith("/")])
    if internal_links == 0:
        score -= 20
        issues.append(("content", "MEDIUM", "No internal navigation links",
                       "Add links to other pages on the site."))

    external_links = len([1 for a in soup.find_all("a", href=True)
                          if (a["href"] or "").startswith("http")])
    if external_links == 0:
        score -= 10
        issues.append(("content", "LOW", "No external reference links",
                       "Cite sources with external links to improve trust."))

    imgs = soup.find_all("img")
    if imgs and len([i for i in imgs if (i.get("alt") or "").strip()]) < len(imgs):
        score -= 10
        issues.append(("content", "LOW", "Images missing descriptive captions",
                       "Add alt text or captions to images."))

    return _clamp(score)


# ── AI summary (fallback-aware) ─────────────────────────────────────
def _build_summary(scores, grade, issue_count):
    return (
        f"Audit grade {grade}. SEO {scores['seo']}/100, accessibility "
        f"{scores['accessibility']}/100, links {scores['links']}/100, security "
        f"{scores['security']}/100, performance {scores['performance']}/100, content "
        f"{scores['content']}/100. {issue_count} issue(s) found. "
        "Recommended: fix high-severity issues first, then re-run the audit."
    )


# ── Main entry point ────────────────────────────────────────────────
def run_audit(target_url=None):
    """Run a full site integrity audit against `target_url`.

    Defaults to the current request's base URL when called from a route.
    Persists an AuditResult + AuditIssue rows and returns the result.
    """
    base = target_url or request.host_url.rstrip("/")
    if not base.startswith(("http://", "https://")):
        base = "http://" + base

    resp = _fetch(base)
    if resp is None:
        raise RuntimeError(f"Could not reach {base} – the audit failed to connect.")

    soup = BeautifulSoup(resp.text or "", "html.parser")

    issues = []  # list of (category, severity, title, detail)

    seo = audit_seo(soup, issues)
    a11y = audit_accessibility(soup, issues)
    links = audit_links(soup, issues, base)
    sec = audit_security(resp, soup, issues)
    perf = audit_performance(resp, soup, issues)
    content = audit_content(soup, issues)

    # Weighted overall score
    overall = round(
        seo * 0.20 + a11y * 0.20 + links * 0.10 +
        sec * 0.20 + perf * 0.15 + content * 0.15
    )
    grade = _grade(overall)
    summary = _build_summary(
        {"seo": seo, "accessibility": a11y, "links": links,
         "security": sec, "performance": perf, "content": content},
        grade, len(issues),
    )

    result = AuditResult(
        url=base,
        overall_score=overall,
        seo_score=seo,
        accessibility_score=a11y,
        links_score=links,
        security_score=sec,
        performance_score=perf,
        content_score=content,
        grade=grade,
        ai_summary=summary,
    )
    db.session.add(result)
    db.session.flush()  # get result.id

    for category, severity, title, detail in issues:
        db.session.add(AuditIssue(
            audit_id=result.id,
            category=category,
            severity=severity,
            title=title[:MAX_ISSUE_TITLE],
            detail=detail[:500],
        ))

    db.session.commit()
    return result