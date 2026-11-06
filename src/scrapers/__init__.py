from typing import Callable

from .base import Event
from .ibon import fetch_events as fetch_ibon
from .kham import fetch_events as fetch_kham
from .kktix import fetch_events as fetch_kktix
from .ticket_com_tw import fetch_events as fetch_ticket_com_tw
from .ticketplus import fetch_events as fetch_ticketplus
from .tixcraft import fetch_events as fetch_tixcraft
from .udn import fetch_events as fetch_udn

SCRAPERS: list[Callable[[], list[Event]]] = [
    fetch_tixcraft,
    fetch_ticket_com_tw,
    fetch_udn,
    fetch_kham,
    fetch_kktix,
    fetch_ticketplus,
    fetch_ibon,
]
