import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "kham"
LIST_URL = "https://kham.com.tw/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def fetch_events() -> list[Event]:
    try:
        response = requests.get(LIST_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("kham: failed to fetch %s: %s", LIST_URL, exc)
        return []

    try:
        return _parse_events(response.text, response.url)
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("kham: failed to parse activity list: %s", exc)
        return []


def _parse_events(html: str, base_url: str) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: dict[str, Event] = {}

    for link in soup.select("a[href*='PRODUCT_ID=']"):
        title_el = link.select_one("p")
        if title_el is None:
            continue

        title = title_el.get_text(strip=True)
        href = link.get("href", "")
        if not title or "PRODUCT_ID=" not in href:
            continue

        event_id = href.split("PRODUCT_ID=")[-1].split("&")[0].rstrip("#")
        if not event_id or event_id in events:
            continue

        events[event_id] = Event(
            source=SOURCE,
            id=event_id,
            title=title,
            url=urljoin(base_url, href),
            date=None,
            venue=None,
        )

    return list(events.values())
