from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3

from .models import TicketInput


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "aegisdesk.db"
SEED_PATH = PROJECT_ROOT / "data" / "synthetic_tickets.json"
KB_DIR = PROJECT_ROOT / "data" / "knowledge_base"

PRIORITY_WEIGHT = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

SUPPORT_TEAMS = [
    "Enterprise Service Desk",
    "Identity & Access Team",
    "Workplace Technology Team",
    "Infrastructure & Network Team",
    "Security & Privacy Team",
    "Business Applications Team",
    "Ecommerce & Customer Experience Team",
    "Data & Analytics Team",
    "Operations & Fulfillment Team",
    "Finance & Procurement Team",
    "People & HR Team",
    "Facilities & Workplace Team",
]


@dataclass(frozen=True)
class ActivityItem:
    time_label: str
    author: str
    text: str
    kind: str = "note"


@dataclass(frozen=True)
class ServiceTicket:
    ticket_id: str
    subject: str
    description: str
    reporter: str
    assignee: str
    status: str
    priority: str
    category: str
    channel: str
    created_label: str
    sla_due_label: str
    sla_breach_label: str
    queue: str
    tags: list[str] = field(default_factory=list)
    activity: list[ActivityItem] = field(default_factory=list)
    business_impact: str = "Single user"
    urgency: str = "Normal"
    affected_users: int = 1
    priority_score: int = 0
    resolution: str = ""
    resolution_verified: bool = False
    updated_at: str = ""

    def to_ticket_input(self) -> TicketInput:
        context = (
            f"\n\nOperational context: business impact={self.business_impact}; "
            f"urgency={self.urgency}; affected users={self.affected_users}."
        )
        return TicketInput(
            subject=self.subject,
            description=self.description + context,
            requester=self.reporter,
            channel=self.channel,
        )


def _connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> Path:
    """Create the local PoC database and idempotently load transparent synthetic fixtures."""
    with _connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                reporter TEXT NOT NULL,
                assignee TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                channel TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                sla_due_at TEXT,
                queue TEXT NOT NULL,
                tags_json TEXT NOT NULL DEFAULT '[]',
                business_impact TEXT NOT NULL DEFAULT 'Single user',
                urgency TEXT NOT NULL DEFAULT 'Normal',
                affected_users INTEGER NOT NULL DEFAULT 1,
                priority_score INTEGER NOT NULL DEFAULT 0,
                resolution TEXT NOT NULL DEFAULT '',
                resolution_verified INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'user'
            );

            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                author TEXT NOT NULL,
                text TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'note',
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS knowledge_articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'approved',
                version TEXT NOT NULL DEFAULT '1.0',
                last_reviewed_at TEXT NOT NULL,
                source_path TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS retrieval_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                workflow_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                rating TEXT NOT NULL CHECK(rating IN ('useful', 'not_relevant')),
                created_at TEXT NOT NULL,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE
            );
            """
        )
        _seed_articles(connection)
        _seed_tickets(connection)
    return db_path


def _seed_articles(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for path in sorted(KB_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = raw.splitlines()[0].lstrip("# ").strip() if raw else path.stem
        article_id = "KA-" + path.stem.upper().replace("_", "-")
        connection.execute(
            """
            INSERT INTO knowledge_articles
                (article_id, title, content, category, status, version, last_reviewed_at, source_path)
            VALUES (?, ?, ?, ?, 'approved', '1.0', ?, ?)
            ON CONFLICT(source_path) DO UPDATE SET title=excluded.title, content=excluded.content
            """,
            (article_id, title, raw, _infer_category(raw), now, str(path.relative_to(PROJECT_ROOT))),
        )


def _seed_tickets(connection: sqlite3.Connection) -> None:
    if not SEED_PATH.exists():
        return
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    for item in payload:
        connection.execute(
            """
            INSERT OR IGNORE INTO tickets
                (ticket_id, subject, description, reporter, assignee, status, priority, category,
                 channel, created_at, updated_at, sla_due_at, queue, tags_json, business_impact,
                 urgency, affected_users, priority_score, resolution, resolution_verified, source)
            VALUES
                (:ticket_id, :subject, :description, :reporter, :assignee, :status, :priority,
                 :category, :channel, :created_at, :updated_at, :sla_due_at, :queue, :tags_json,
                 :business_impact, :urgency, :affected_users, :priority_score, :resolution,
                 :resolution_verified, 'synthetic')
            """,
            {
                **item,
                "tags_json": json.dumps(item.get("tags", [])),
                "updated_at": item.get("updated_at", item["created_at"]),
                "sla_due_at": item.get("sla_due_at"),
                "business_impact": item.get("business_impact", "Single user"),
                "urgency": item.get("urgency", "Normal"),
                "affected_users": int(item.get("affected_users", 1)),
                "priority_score": int(item.get("priority_score", 0)),
                "resolution": item.get("resolution", ""),
                "resolution_verified": int(bool(item.get("resolution_verified", False))),
            },
        )
        if connection.execute("SELECT COUNT(*) FROM activities WHERE ticket_id = ?", (item["ticket_id"],)).fetchone()[0] == 0:
            for activity in item.get("activity", []):
                connection.execute(
                    "INSERT INTO activities (ticket_id, created_at, author, text, kind) VALUES (?, ?, ?, ?, ?)",
                    (
                        item["ticket_id"],
                        activity.get("created_at", item["created_at"]),
                        activity["author"],
                        activity["text"],
                        activity.get("kind", "note"),
                    ),
                )


def _infer_category(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("leave balance", "leave request", "employee record", "people & hr")):
        return "People & HR"
    if any(word in lowered for word in ("invoice", "purchase order", "procurement", "supplier")):
        return "Finance & Procurement"
    if any(word in lowered for word in ("power bi", "dashboard", "kpi", "semantic model")):
        return "Data & Analytics"
    if any(word in lowered for word in ("pipeline", "warehouse", "data lake", "schema drift")):
        return "Data & Analytics"
    if any(word in lowered for word in ("checkout", "payment", "order", "fulfillment", "inventory")):
        return "Ecommerce & Customer Experience"
    if any(word in lowered for word in ("vpn", "password", "mfa", "access")):
        return "Identity & Access"
    if any(word in lowered for word in ("outlook", "email", "teams", "calendar")):
        return "Workplace Technology"
    if any(word in lowered for word in ("wi-fi", "network", "dns", "latency")):
        return "Network & Connectivity"
    if any(word in lowered for word in ("phishing", "malware", "security")):
        return "Security & Privacy"
    if any(word in lowered for word in ("laptop", "printer", "device")):
        return "Workplace Technology"
    return "Business Applications"


def _relative_time(value: str) -> str:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        seconds = max(int((now - moment).total_seconds()), 0)
        if seconds < 60:
            return "Just now"
        if seconds < 3600:
            return f"{seconds // 60} min ago"
        if seconds < 86400:
            return f"{seconds // 3600} hours ago"
        return f"{seconds // 86400} days ago"
    except ValueError:
        return value


def _sla_label(value: str | None, status: str) -> str:
    if status == "Resolved":
        return "Resolved"
    if not value:
        return "Not set"
    try:
        due = datetime.fromisoformat(value.replace("Z", "+00:00"))
        minutes = int((due - datetime.now(timezone.utc)).total_seconds() / 60)
        if minutes < 0:
            return f"Breached by {abs(minutes)} min"
        if minutes < 60:
            return f"{minutes} min"
        return f"{minutes // 60}h {minutes % 60}m"
    except ValueError:
        return value


def _row_to_ticket(connection: sqlite3.Connection, row: sqlite3.Row) -> ServiceTicket:
    activity_rows = connection.execute(
        "SELECT created_at, author, text, kind FROM activities WHERE ticket_id = ? ORDER BY id",
        (row["ticket_id"],),
    ).fetchall()
    return ServiceTicket(
        ticket_id=row["ticket_id"],
        subject=row["subject"],
        description=row["description"],
        reporter=row["reporter"],
        assignee=row["assignee"],
        status=row["status"],
        priority=row["priority"],
        category=row["category"],
        channel=row["channel"],
        created_label=_relative_time(row["created_at"]),
        sla_due_label=_sla_label(row["sla_due_at"], row["status"]),
        sla_breach_label="-",
        queue=row["queue"],
        tags=json.loads(row["tags_json"]),
        activity=[
            ActivityItem(_relative_time(item["created_at"]), item["author"], item["text"], item["kind"])
            for item in activity_rows
        ],
        business_impact=row["business_impact"],
        urgency=row["urgency"],
        affected_users=row["affected_users"],
        priority_score=row["priority_score"],
        resolution=row["resolution"],
        resolution_verified=bool(row["resolution_verified"]),
        updated_at=row["updated_at"],
    )


def list_tickets(db_path: Path = DEFAULT_DB_PATH) -> list[ServiceTicket]:
    initialize_database(db_path)
    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM tickets
            ORDER BY
                CASE status WHEN 'Resolved' THEN 1 ELSE 0 END,
                priority_score DESC,
                CASE priority WHEN 'Critical' THEN 4 WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END DESC,
                created_at ASC
            """
        ).fetchall()
        return [_row_to_ticket(connection, row) for row in rows]


def get_ticket(ticket_id: str, db_path: Path = DEFAULT_DB_PATH) -> ServiceTicket:
    initialize_database(db_path)
    with _connect(db_path) as connection:
        row = connection.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown ticket: {ticket_id}")
        return _row_to_ticket(connection, row)


def _next_ticket_id(connection: sqlite3.Connection) -> str:
    rows = connection.execute("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'SD-%'").fetchall()
    numbers = [int(row[0].split("-")[1]) for row in rows if row[0].split("-")[1].isdigit()]
    return f"SD-{max(numbers, default=1000) + 1}"


def score_priority(subject: str, description: str, business_impact: str, urgency: str, affected_users: int) -> tuple[str, int, int]:
    text = f"{subject} {description}".lower()
    score = {"Low": 10, "Normal": 25, "High": 45, "Immediate": 65}.get(urgency, 25)
    score += {"Single user": 5, "Team": 15, "Department": 25, "Company-wide": 35}.get(business_impact, 5)
    score += min(max(affected_users, 1), 100) // 5
    if any(term in text for term in ("phishing", "malware", "breach", "ransomware", "data leak")):
        score += 35
    if any(term in text for term in ("cannot work", "outage", "all users", "production down", "security incident")):
        score += 25
    score = min(score, 100)
    priority = "Critical" if score >= 80 else "High" if score >= 55 else "Medium" if score >= 30 else "Low"
    sla_minutes = {"Critical": 30, "High": 120, "Medium": 480, "Low": 1440}[priority]
    return priority, score, sla_minutes


def create_ticket(
    subject: str,
    description: str,
    reporter: str,
    channel: str,
    business_impact: str,
    urgency: str,
    affected_users: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    initialize_database(db_path)
    now = datetime.now(timezone.utc)
    priority, score, sla_minutes = score_priority(
        subject, description, business_impact, urgency, affected_users
    )
    with _connect(db_path) as connection:
        ticket_id = _next_ticket_id(connection)
        connection.execute(
            """
            INSERT INTO tickets
                (ticket_id, subject, description, reporter, assignee, status, priority, category,
                 channel, created_at, updated_at, sla_due_at, queue, tags_json, business_impact,
                 urgency, affected_users, priority_score, source)
            VALUES (?, ?, ?, ?, 'Smart Triage Queue', 'Open', ?, 'Pending AI triage', ?, ?, ?, ?,
                    'Open', '[]', ?, ?, ?, ?, 'user')
            """,
            (
                ticket_id, subject.strip(), description.strip(), reporter.strip() or "Anonymous requester",
                priority, channel, now.isoformat(), now.isoformat(),
                (now + timedelta(minutes=sla_minutes)).isoformat(), business_impact, urgency,
                int(affected_users), score,
            ),
        )
        connection.execute(
            "INSERT INTO activities (ticket_id, created_at, author, text, kind) VALUES (?, ?, ?, ?, 'customer')",
            (ticket_id, now.isoformat(), reporter.strip() or "Anonymous requester", "Created this request in the company portal."),
        )
        connection.execute(
            "INSERT INTO activities (ticket_id, created_at, author, text, kind) VALUES (?, ?, 'Priority Engine', ?, 'ai')",
            (ticket_id, now.isoformat(), f"Placed at {priority} priority with queue score {score}/100."),
        )
    return ticket_id


def update_ai_classification(
    ticket_id: str,
    category: str,
    priority: str,
    assigned_team: str | None = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    with _connect(db_path) as connection:
        current = connection.execute(
            "SELECT category, priority, priority_score, assignee FROM tickets WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
        if current is None:
            return
        final_priority = max((current["priority"], priority), key=lambda item: PRIORITY_WEIGHT.get(item, 0))
        score = max(current["priority_score"], {"Low": 20, "Medium": 45, "High": 70, "Critical": 95}.get(final_priority, 20))
        final_assignee = assigned_team or current["assignee"]
        if (
            current["category"] == category
            and current["priority"] == final_priority
            and current["priority_score"] == score
            and current["assignee"] == final_assignee
        ):
            return
        now = datetime.now(timezone.utc).isoformat()
        connection.execute(
            "UPDATE tickets SET category = ?, priority = ?, priority_score = ?, assignee = ?, updated_at = ? WHERE ticket_id = ?",
            (category, final_priority, score, final_assignee, now, ticket_id),
        )
        connection.execute(
            "INSERT INTO activities (ticket_id, created_at, author, text, kind) VALUES (?, ?, 'Triage Agent', ?, 'ai')",
            (ticket_id, now, f"Assigned to {final_assignee}; classified as {category}; queue priority {final_priority} ({score}/100)."),
        )


def resolve_ticket(ticket_id: str, resolution: str, reviewer: str = "Human support agent", db_path: Path = DEFAULT_DB_PATH) -> None:
    if not resolution.strip():
        raise ValueError("A verified resolution cannot be empty.")
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as connection:
        connection.execute(
            """
            UPDATE tickets SET status='Resolved', queue='Resolved', resolution=?,
                resolution_verified=1, updated_at=? WHERE ticket_id=?
            """,
            (resolution.strip(), now, ticket_id),
        )
        connection.execute(
            "INSERT INTO activities (ticket_id, created_at, author, text, kind) VALUES (?, ?, ?, ?, 'agent')",
            (ticket_id, now, reviewer, "Resolution verified and added to reusable case knowledge."),
        )


def reassign_ticket(
    ticket_id: str,
    assigned_team: str,
    reviewer: str = "Human support agent",
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    if assigned_team not in SUPPORT_TEAMS:
        raise ValueError("Team is outside the approved routing list.")
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as connection:
        connection.execute(
            "UPDATE tickets SET assignee=?, updated_at=? WHERE ticket_id=?",
            (assigned_team, now, ticket_id),
        )
        connection.execute(
            "INSERT INTO activities (ticket_id, created_at, author, text, kind) VALUES (?, ?, ?, ?, 'agent')",
            (ticket_id, now, reviewer, f"Reassigned the ticket to {assigned_team}."),
        )


def get_approved_articles(db_path: Path = DEFAULT_DB_PATH) -> list[sqlite3.Row]:
    initialize_database(db_path)
    with _connect(db_path) as connection:
        return connection.execute(
            "SELECT article_id, title, content, category, version, last_reviewed_at FROM knowledge_articles WHERE status='approved' ORDER BY article_id"
        ).fetchall()


def get_verified_resolutions(db_path: Path = DEFAULT_DB_PATH) -> list[sqlite3.Row]:
    initialize_database(db_path)
    with _connect(db_path) as connection:
        return connection.execute(
            """
            SELECT ticket_id, subject, description, category, resolution, updated_at
            FROM tickets WHERE status='Resolved' AND resolution_verified=1 AND resolution <> ''
            ORDER BY updated_at DESC
            """
        ).fetchall()


def database_counts(db_path: Path = DEFAULT_DB_PATH) -> dict[str, int]:
    initialize_database(db_path)
    with _connect(db_path) as connection:
        return {
            "tickets": connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0],
            "articles": connection.execute("SELECT COUNT(*) FROM knowledge_articles WHERE status='approved'").fetchone()[0],
            "verified_solutions": connection.execute("SELECT COUNT(*) FROM tickets WHERE resolution_verified=1").fetchone()[0],
        }


def record_retrieval_feedback(
    ticket_id: str,
    workflow_id: str,
    source_id: str,
    rating: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    if rating not in {"useful", "not_relevant"}:
        raise ValueError("Unsupported feedback rating.")
    with _connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO retrieval_feedback (ticket_id, workflow_id, source_id, rating, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticket_id, workflow_id, source_id, rating, datetime.now(timezone.utc).isoformat()),
        )
