import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "ticket.com.tw"
LIST_URL = "https://ticket.com.tw/application/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=205"
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
        logger.warning("ticket.com.tw: failed to fetch %s: %s", LIST_URL, exc)
        return []

    try:
        return _parse_events(response.text, response.url)
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("ticket.com.tw: failed to parse activity list: %s", exc)
        return []


def _parse_events(html: str, base_url: str) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: dict[str, Event] = {}

    for card in soup.select("div.moreBox"):
        link = card.select_one("a[href*='PRODUCT_ID=']")
        title_el = card.select_one(".list-group-item-heading")
        if link is None or title_el is None:
            continue

        href = link.get("href", "")
        event_id = href.split("PRODUCT_ID=")[-1].split("&")[0]
        title = title_el.get_text(strip=True)
        if not event_id or not title or event_id in events:
            continue

        date_el = card.select_one(".list-group-item-date")

        events[event_id] = Event(
            source=SOURCE,
            id=event_id,
            title=title,
            url=urljoin(base_url, href),
            date=date_el.get_text(strip=True) if date_el else None,
            venue=None,
        )

    return list(events.values())
