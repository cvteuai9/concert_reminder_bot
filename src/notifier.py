import logging

import requests

from .scrapers.base import Event

logger = logging.getLogger(__name__)

EMBED_COLOR = 0x5865F2  # Discord blurple
ALERT_COLOR = 0xED4245  # Discord red


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

    return _post(webhook_url, payload, error_context=event.id)


def send_health_alert(webhook_url: str, source: str, consecutive_empty: int) -> bool:
    payload = {
        "embeds": [
            {
                "title": f"⚠️ {source} 連續 {consecutive_empty} 次沒有抓到任何活動",
                "description": "可能被改版或擋住,建議檢查對應的 scraper",
                "color": ALERT_COLOR,
                "footer": {"text": source},
            }
        ]
    }

    return _post(webhook_url, payload, error_context=f"health-alert:{source}")


def _post(webhook_url: str, payload: dict, error_context: str) -> bool:
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("notifier: failed to send Discord message for %s: %s", error_context, exc)
        return False

    return True
