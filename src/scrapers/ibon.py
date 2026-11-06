import logging
from urllib.parse import urljoin

import requests

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "ibon"
API_URL = "https://ticket.ibon.com.tw/api/ActivityInfo/GetIndexData?pattern=entertainment"
BASE_URL = "https://ticket.ibon.com.tw/"
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
        logger.warning("ibon: failed to fetch %s: %s", API_URL, exc)
        return []

    try:
        return _parse_events(response.json())
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("ibon: failed to parse event data: %s", exc)
        return []


def _parse_events(data: dict) -> list[Event]:
    items = data.get("Item", {}).get("List", [])
    events: dict[str, Event] = {}

    for item in items:
        event_id = str(item.get("ActivityID", ""))
        title = (item.get("ActivityName") or "").strip()
        ticket_path = item.get("GameTicketURL")
        if not event_id or not title or not ticket_path or event_id in events:
            continue

        events[event_id] = Event(
            source=SOURCE,
            id=event_id,
            title=title,
            url=urljoin(BASE_URL, ticket_path),
            date=item.get("ActivitySDate"),
            venue=None,
        )

    return list(events.values())
