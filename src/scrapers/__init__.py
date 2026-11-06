from typing import Callable

from . import ibon, kham, kktix, ticket_com_tw, ticketplus, tixcraft, udn
from .base import Event

SCRAPERS: list[tuple[str, Callable[[], list[Event]]]] = [
    (tixcraft.SOURCE, tixcraft.fetch_events),
    (ticket_com_tw.SOURCE, ticket_com_tw.fetch_events),
    (udn.SOURCE, udn.fetch_events),
    (kham.SOURCE, kham.fetch_events),
    (kktix.SOURCE, kktix.fetch_events),
    (ticketplus.SOURCE, ticketplus.fetch_events),
    (ibon.SOURCE, ibon.fetch_events),
]
