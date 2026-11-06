from typing import Callable

from .base import Event
from .kham import fetch_events as fetch_kham
from .ticket_com_tw import fetch_events as fetch_ticket_com_tw
from .tixcraft import fetch_events as fetch_tixcraft
from .udn import fetch_events as fetch_udn

SCRAPERS: list[Callable[[], list[Event]]] = [
    fetch_tixcraft,
    fetch_ticket_com_tw,
    fetch_udn,
    fetch_kham,
]
