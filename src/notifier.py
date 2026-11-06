import logging

import requests

from .scrapers.base import Event

logger = logging.getLogger(__name__)

EMBED_COLOR = 0x5865F2  # Discord blurple


def send_notification(webhook_url: str, artist_name: str, event: Event) -> bool:
    fields = []
    if event.venue:
        fields.append({"name": "場地", "value": event.venue, "inline": True})
    if event.date:
        fields.append({"name": "日期", "value": event.date, "inline": True})

    payload = {
        "embeds": [
            {
                "title": event.title,
                "url": event.url,
                "description": f"🎤 追蹤藝人:{artist_name}",
                "color": EMBED_COLOR,
                "fields": fields,
                "footer": {"text": event.source},
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("notifier: failed to send Discord notification for %s: %s", event.id, exc)
        return False

    return True
