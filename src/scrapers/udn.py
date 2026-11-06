import logging

import requests
from bs4 import BeautifulSoup

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "udn"
LIST_URL = "https://tickets.udnfunlife.com/Application/UTK02/UTK0201_.aspx"
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
        logger.warning("udn: failed to fetch %s: %s", LIST_URL, exc)
        return []

    try:
        return _parse_events(response.text)
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("udn: failed to parse activity list: %s", exc)
        return []


def _parse_events(html: str) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: dict[str, Event] = {}

    for card in soup.select("div.yd_card"):
        link = card.select_one("a[href*='PRODUCT_ID=']")
        title_el = card.select_one(".yd_card-title")
        if link is None or title_el is None:
            continue

        href = link.get("href", "")
        event_id = href.split("PRODUCT_ID=")[-1].split("&")[0]
        title = title_el.get_text(strip=True)
        if not event_id or not title or event_id in events:
            continue

        icon_texts = card.select(".yd_card-iconText .ellipsis")
        date = icon_texts[0].get_text(strip=True) if len(icon_texts) > 0 else None
        venue = icon_texts[1].get_text(strip=True) if len(icon_texts) > 1 else None

        events[event_id] = Event(
            source=SOURCE,
            id=event_id,
            title=title,
            url=href,
            date=date,
            venue=venue,
        )

    return list(events.values())
