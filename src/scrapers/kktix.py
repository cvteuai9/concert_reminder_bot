import html
import json
import logging
from datetime import datetime, timezone

from curl_cffi import requests

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "kktix"
LIST_URL = "https://kktix.com/events"


def fetch_events() -> list[Event]:
    try:
        response = requests.get(LIST_URL, impersonate="chrome", timeout=15)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - curl_cffi raises its own exception types
        logger.warning("kktix: failed to fetch %s: %s", LIST_URL, exc)
        return []

    try:
        return _parse_events(response.text)
    except Exception as exc:  # noqa: BLE001 - keep one source from breaking the whole run
        logger.warning("kktix: failed to parse event list: %s", exc)
        return []


def _parse_events(html_text: str) -> list[Event]:
    marker = 'data-react-class="SearchWrapper" data-react-props="'
    start = html_text.find(marker)
    if start == -1:
        return []

    start += len(marker)
    end = html_text.find('"', start)
    if end == -1:
        return []

    raw_props = html.unescape(html_text[start:end])
    data = json.loads(raw_props)
    items = data.get("data", [])

    events: dict[str, Event] = {}
    for item in items:
        event_id = str(item.get("id", ""))
        name = item.get("name")
        url = item.get("public_url")
        if not event_id or not name or not url or event_id in events:
            continue

        events[event_id] = Event(
            source=SOURCE,
            id=event_id,
            title=name,
            url=url,
            date=_format_timestamp(item.get("start_at")),
            venue=None,
        )

    return list(events.values())


def _format_timestamp(start_at) -> str | None:
    if not isinstance(start_at, (int, float)):
        return None
    return datetime.fromtimestamp(start_at, tz=timezone.utc).strftime("%Y-%m-%d")
