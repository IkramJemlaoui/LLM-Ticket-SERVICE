from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
(LOG_DIR / "app_events.jsonl").touch(exist_ok=True)

print("Demo data ready.")
print("Knowledge base articles are stored in data/knowledge_base/.")
