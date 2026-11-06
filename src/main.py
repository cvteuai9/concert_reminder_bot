import logging
import os

from .config import load_artists, load_consecutive_empty_threshold
from .health import load_health, record_result, save_health
from .matcher import match_events
from .notifier import send_health_alert, send_notification
from .scrapers import SCRAPERS
from .state import load_seen_ids, save_seen_ids

logger = logging.getLogger(__name__)


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise SystemExit("DISCORD_WEBHOOK_URL environment variable is required")

    artists = load_artists()

    events = []
    source_event_counts: dict[str, int] = {}
    for source, fetch in SCRAPERS:
        source_events = fetch()
        source_event_counts[source] = len(source_events)
        events.extend(source_events)
    logger.info("fetched %d events from %d source(s)", len(events), len(SCRAPERS))

    matches = match_events(artists, events)
    logger.info("%d event(s) matched tracked artists", len(matches))

    seen_ids = load_seen_ids()
    newly_notified: set[str] = set()

    for artist_name, event in matches:
        if event.id in seen_ids:
            continue

        if send_notification(webhook_url, artist_name, event):
            newly_notified.add(event.id)
            logger.info("notified: %s - %s", artist_name, event.title)
        else:
            logger.warning("notification failed, will retry next run: %s", event.title)

    if newly_notified:
        save_seen_ids(seen_ids | newly_notified)
        logger.info("recorded %d newly notified event(s)", len(newly_notified))
    else:
        logger.info("no new events to notify")

    threshold = load_consecutive_empty_threshold()
    health = load_health()
    for source, count in source_event_counts.items():
        if record_result(health, source, had_events=count > 0, threshold=threshold):
            if send_health_alert(webhook_url, source, health[source]["consecutive_empty"]):
                health[source]["alerted"] = True
                logger.warning("sent health alert for source: %s", source)
            else:
                logger.warning("failed to send health alert for source: %s, will retry next run", source)
    save_health(health)


if __name__ == "__main__":
    run()
