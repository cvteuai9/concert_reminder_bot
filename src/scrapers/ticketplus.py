import logging

import requests

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "ticketplus"
API_URL = "https://apis.ticketplus.com.tw/config/api/v1/getS3?path=main/mainEvents.json"
DETAIL_URL_TEMPLATE = "https://ticketplus.com.tw/activity/{event_id}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def fetch_events() -> list[Event]:
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("ticketplus: failed to fetch %s: %s", API_URL, exc)
        return []

    try:
        return _parse_events(response.json())
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("ticketplus: failed to parse event data: %s", exc)
        return []


def _parse_events(data: dict) -> list[Event]:
    items = data.get("allEventMainPageInfo", {})
    events: list[Event] = []

    for event_id, item in items.items():
        if item.get("hidden"):
            continue

        title = (item.get("title") or "").strip()
        if not title:
            continue

        events.append(
            Event(
                source=SOURCE,
                id=event_id,
                title=title,
                url=DETAIL_URL_TEMPLATE.format(event_id=event_id),
                date=item.get("start_date"),
                venue=None,
            )
        )

    return events
