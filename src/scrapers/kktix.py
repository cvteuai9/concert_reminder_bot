import html
import json
import logging
import time
from datetime import datetime, timezone

from curl_cffi import requests

from .base import Event

logger = logging.getLogger(__name__)

SOURCE = "kktix"
LIST_URL = "https://kktix.com/events"
MAX_PAGES = 150
RETRIES_PER_PAGE = 2
RETRY_DELAY_SECONDS = 2


def fetch_events() -> list[Event]:
    events: dict[str, Event] = {}

    for page in range(1, MAX_PAGES + 1):
        items = _fetch_page(page)
        if items is None:
            # This page failed even after retries - skip it, but keep going;
            # a failed page is not the same as "reached the end of the feed".
            continue

        if not items:
            # A successful response with an empty list means we've reached
            # the end of the feed - this is the only valid stop condition.
            break

        for item in items:
            event = _to_event(item)
            if event is not None:
                events[event.id] = event

    return list(events.values())


def _fetch_page(page: int) -> list[dict] | None:
    url = f"{LIST_URL}?page={page}"

    for attempt in range(RETRIES_PER_PAGE + 1):
        try:
            response = requests.get(url, impersonate="chrome", timeout=15)
            response.raise_for_status()
            return _extract_items(response.text)
        except Exception as exc:  # noqa: BLE001 - curl_cffi raises its own exception types
            if attempt < RETRIES_PER_PAGE:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.warning("kktix: failed to fetch page %d after retries: %s", page, exc)

    return None


def _extract_items(html_text: str) -> list[dict]:
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
    return data.get("data", [])


def _to_event(item: dict) -> Event | None:
    event_id = str(item.get("id", ""))
    name = item.get("name")
    url = item.get("public_url")
    if not event_id or not name or not url:
        return None

    return Event(
        source=SOURCE,
        id=event_id,
        title=name,
        url=url,
        date=_format_timestamp(item.get("start_at")),
        venue=None,
    )


def _format_timestamp(start_at) -> str | None:
    if not isinstance(start_at, (int, float)):
        return None
    return datetime.fromtimestamp(start_at, tz=timezone.utc).strftime("%Y-%m-%d")
