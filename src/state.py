import json
from pathlib import Path

DEFAULT_STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "seen_events.json"


def load_seen_ids(state_path: Path = DEFAULT_STATE_PATH) -> set[str]:
    if not state_path.exists():
        return set()

    with open(state_path, encoding="utf-8") as f:
        return set(json.load(f))


def save_seen_ids(seen_ids: set[str], state_path: Path = DEFAULT_STATE_PATH) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(sorted(seen_ids), f, ensure_ascii=False, indent=2)
