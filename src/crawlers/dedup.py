import hashlib
import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


def canonicalize_url(url: str) -> str:
    """Normalize URL: strip tracking params, trailing slash, lowercase scheme+host."""
    parsed = urlparse(url)
    # Remove tracking params
    skip_params = {"utm_source", "utm_medium", "utm_campaign", "utm_term",
                   "utm_content", "fbclid", "gclid", "ref", "source"}
    qs = parse_qs(parsed.query, keep_blank_values=True)
    clean_qs = {k: v for k, v in qs.items() if k.lower() not in skip_params}
    # Rebuild
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    query = urlencode(clean_qs, doseq=True) if clean_qs else ""
    fragment = ""
    return urlunparse((scheme, netloc, path, parsed.params, query, fragment))


def normalize_title(title: str) -> str:
    """Strip extra whitespace and lowercase for comparison."""
    return re.sub(r"\s+", " ", title).strip().lower()


def content_hash(title: str, url: str) -> str:
    """SHA256 hash of normalized title + canonical URL."""
    raw = f"{normalize_title(title)}|{canonicalize_url(url)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
