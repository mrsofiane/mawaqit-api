import requests
from fastapi import HTTPException
from urllib.parse import urlparse
from typing import List, Optional

import re
import models.models as models
from config.settings import settings

# first path segments on mawaqit.net that are not mosques
RESERVED_PATHS = {
    "backoffice", "login", "register", "resetting", "faq", "blog", "contact", "about",
    "pricing", "terms", "privacy", "cgu", "legal", "donation", "donate", "mosques", "search", "api",
}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LANG_PATTERN = re.compile(r"^[a-z]{2}$")


def extract_slug(url: str) -> Optional[str]:
    """Return the mosque slug of a mawaqit.net url, e.g. https://mawaqit.net/fr/assalam-argenteuil -> assalam-argenteuil"""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host != "mawaqit.net" and not host.endswith(".mawaqit.net"):
        return None

    parts = [p for p in parsed.path.lower().split("/") if p]
    # /{lang}/{slug} or /{lang}/m/{slug} (mobile) or /{lang}/w/{slug} (widget)
    if parts and LANG_PATTERN.match(parts[0]):
        parts = parts[1:]
    if len(parts) == 2 and parts[0] in ("m", "w"):
        parts = parts[1:]
    if len(parts) != 1:
        return None

    slug = parts[0]
    if slug in RESERVED_PATHS or not SLUG_PATTERN.match(slug):
        return None
    return slug


def clean_title(title: str) -> str:
    """Remove the mawaqit branding from a page title"""
    parts = [p.strip() for p in re.split(r"\s+[-|–]\s+", title)]
    parts = [p for p in parts if p and p.lower() not in ("mawaqit", "mawaqit.net")]
    return " - ".join(parts) or title.strip()


def search_mosques(query: str, limit: int = 10) -> List[dict]:
    if not settings.SEARXNG_URL:
        raise HTTPException(status_code=503, detail="Mosque search is disabled, set SEARXNG_URL to enable it")

    url = f"{settings.SEARXNG_URL.rstrip('/')}/search"
    try:
        r = requests.get(url, params={"q": f"site:mawaqit.net {query}", "format": "json"}, timeout=15)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="something went wrong fetching search results from SearXNG")
    if r.status_code != 200:
        detail = f"SearXNG returned status {r.status_code}, make sure the json format is enabled"
        raise HTTPException(status_code=502, detail=detail)

    mosques = []
    seen = set()
    for result in r.json().get("results", []):
        slug = extract_slug(result.get("url", ""))
        if slug is None or slug in seen:
            continue
        seen.add(slug)
        mosque = models.MosqueSearchResult(
            slug=slug,
            name=clean_title(result.get("title") or slug),
            url=f"https://mawaqit.net/fr/{slug}",
        )
        mosques.append(mosque.model_dump())
        if len(mosques) >= limit:
            break
    return mosques
