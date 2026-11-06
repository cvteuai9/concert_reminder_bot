import logging

import requests
from bs4 import BeautifulSoup

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "tixcraft"
LIST_URL = "https://tixcraft.com/activity"
BASE_URL = "https://tixcraft.com"
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
        logger.warning("tixcraft: failed to fetch %s: %s", LIST_URL, exc)
        return []

    try:
        return _parse_events(response.text)
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("tixcraft: failed to parse activity list: %s", exc)
        return []


def _parse_events(html: str) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: dict[str, Event] = {}

    for block in soup.select("div.eventbl"):
        link = block.select_one(".text-bold a[href^='/activity/detail/']")
        if link is None:
            continue

        href = link.get("href", "")
        event_id = href.rsplit("/", 1)[-1]
        if not event_id or event_id in events:
            continue

        title = link.get_text(strip=True)
        if not title:
            continue

        date_el = block.select_one(".date")
        venue_el = block.select_one(".text-med-light")

        events[event_id] = Event(
            source=SOURCE,
            id=event_id,
            title=title,
            url=BASE_URL + href,
            date=date_el.get_text(strip=True) if date_el else None,
            venue=venue_el.get_text(strip=True) if venue_el else None,
        )

    return list(events.values())
