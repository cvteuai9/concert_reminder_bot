from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    source: str
    id: str
    title: str
    url: str
    date: Optional[str] = None
    venue: Optional[str] = None
