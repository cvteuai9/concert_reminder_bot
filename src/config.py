from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


@dataclass
class Artist:
    name: str
    keywords: list[str]


def load_artists(config_path: Path = DEFAULT_CONFIG_PATH) -> list[Artist]:
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return [
        Artist(name=item["name"], keywords=list(item["keywords"]))
        for item in data.get("artists", [])
    ]


def load_consecutive_empty_threshold(config_path: Path = DEFAULT_CONFIG_PATH, default: int = 3) -> int:
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data.get("monitoring", {}).get("consecutive_empty_threshold", default)
