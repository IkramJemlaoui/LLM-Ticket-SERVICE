import sys
from pathlib import Path
import sqlite3

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.data_store import (
    create_ticket,
    database_counts,
    get_ticket,
    initialize_database,
    list_tickets,
    record_retrieval_feedback,
    resolve_ticket,
)
from app.retrieval import Retriever


def test_seeded_database_has_articles_cases_and_priority_order(tmp_path):
    db_path = tmp_path / "test-aegisdesk.db"
    initialize_database(db_path)

    counts = database_counts(db_path)
    tickets = list_tickets(db_path)

    assert counts == {"tickets": 27, "articles": 15, "verified_solutions": 16}
    assert tickets[0].priority == "Critical"
    assert tickets[0].status != "Resolved"
    assert tickets[-1].status == "Resolved"


def test_created_ticket_persists_and_can_become_verified_case(tmp_path):
    db_path = tmp_path / "test-aegisdesk.db"
    ticket_id = create_ticket(
        subject="Company-wide production outage",
        description="All users cannot work because the production application is down.",
        reporter="Test Employee",
        channel="Web Portal",
        business_impact="Company-wide",
        urgency="Immediate",
        affected_users=250,
        db_path=db_path,
    )

    created = get_ticket(ticket_id, db_path)
    assert created.priority == "Critical"
    assert created.priority_score == 100

    resolve_ticket(ticket_id, "Restarted the failed approved service after change authorization.", db_path=db_path)
    resolved = get_ticket(ticket_id, db_path)
    assert resolved.status == "Resolved"
    assert resolved.resolution_verified is True

    record_retrieval_feedback(ticket_id, "WF-TEST", ticket_id, "useful", db_path)
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT rating FROM retrieval_feedback").fetchone()[0] == "useful"


def test_rag_returns_article_and_similar_verified_case(tmp_path):
    db_path = tmp_path / "test-aegisdesk.db"
    initialize_database(db_path)
    results = Retriever(db_path).search(
        "VPN authentication failed after password reset cached credential", top_k=5, min_score=0.01
    )

    assert any(result.source_type == "knowledge_article" for result in results)
    assert any(result.source_type == "verified_case" for result in results)
    assert results[0].source_title == "VPN Access After Password Reset"
