import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.data_store import database_counts, initialize_database

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
(LOG_DIR / "app_events.jsonl").touch(exist_ok=True)

database_path = initialize_database()
counts = database_counts()

print("Demo data ready.")
print(f"Runtime database: {database_path}")
print(
    f"Loaded {counts['tickets']} tickets, {counts['articles']} approved articles, "
    f"and {counts['verified_solutions']} verified resolutions."
)
