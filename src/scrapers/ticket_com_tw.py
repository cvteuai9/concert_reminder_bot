import logging

import requests
from bs4 import BeautifulSoup

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "ticket.com.tw"
LIST_URL = "https://ticket.com.tw/application/UTK02/UTK0201_.aspx"
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
        return _parse_events(response.text)
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("ticket.com.tw: failed to parse activity list: %s", exc)
        return []


def _parse_events(html: str) -> list[Event]:
    soup = BeautifulSoup(html, "html.parser")
    events: dict[str, Event] = {}

    for link in soup.select("div.portfolio-item a.portfolio-link[href*='PRODUCT_ID=']"):
        _add_event(events, link, title_el=link.select_one("h4"), date_el=link.select_one("p.text-muted"))

    for link in soup.select("div.wrap a[href*='PRODUCT_ID=']"):
        caption = link.find_next_sibling("div", class_="caption")
        title_el = caption.select_one("h3") if caption else None
        date_el = caption.select_one("p") if caption else None
        _add_event(events, link, title_el=title_el, date_el=date_el)

    return list(events.values())


def _add_event(events: dict[str, Event], link, title_el, date_el) -> None:
    href = link.get("href", "")
    if "PRODUCT_ID=" not in href:
        return

    event_id = href.split("PRODUCT_ID=")[-1].split("&")[0]
    if not event_id or event_id in events:
        return

    title = title_el.get_text(strip=True) if title_el else None
    if not title:
        return

    events[event_id] = Event(
        source=SOURCE,
        id=event_id,
        title=title,
        url=href,
        date=date_el.get_text(strip=True) if date_el else None,
        venue=None,
    )
