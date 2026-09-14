from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

LOG_PATH = Path("logs/app_events.jsonl")

def log_event(payload: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
