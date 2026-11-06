import json
from pathlib import Path

DEFAULT_HEALTH_PATH = Path(__file__).resolve().parent.parent / "data" / "source_health.json"


def load_health(health_path: Path = DEFAULT_HEALTH_PATH) -> dict:
    if not health_path.exists():
        return {}

    with open(health_path, encoding="utf-8") as f:
        return json.load(f)


def save_health(health: dict, health_path: Path = DEFAULT_HEALTH_PATH) -> None:
    health_path.parent.mkdir(parents=True, exist_ok=True)
    with open(health_path, "w", encoding="utf-8") as f:
        json.dump(health, f, ensure_ascii=False, indent=2)


def record_result(health: dict, source: str, had_events: bool, threshold: int) -> bool:
    entry = health.setdefault(source, {"consecutive_empty": 0, "alerted": False})

    if had_events:
        entry["consecutive_empty"] = 0
        entry["alerted"] = False
        return False

    entry["consecutive_empty"] += 1
    return entry["consecutive_empty"] >= threshold and not entry["alerted"]
