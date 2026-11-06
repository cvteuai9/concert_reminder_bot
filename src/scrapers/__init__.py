from typing import Callable

from .base import Event
from .tixcraft import fetch_events as fetch_tixcraft

SCRAPERS: list[Callable[[], list[Event]]] = [
    fetch_tixcraft,
]
