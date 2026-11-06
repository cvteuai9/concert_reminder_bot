from .config import Artist
from .scrapers.base import Event


def _normalize(text: str) -> str:
    return text.strip().lower()


def match_events(artists: list[Artist], events: list[Event]) -> list[tuple[str, Event]]:
    matches: list[tuple[str, Event]] = []

    for event in events:
        title = _normalize(event.title)
        for artist in artists:
            if any(_normalize(keyword) in title for keyword in artist.keywords):
                matches.append((artist.name, event))
                break

    return matches
