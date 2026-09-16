"""Backward-compatible imports for integrations built against the original demo module.

Runtime data now lives in the SQLite-backed :mod:`app.data_store` module. New code
should import from there directly.
"""

from .data_store import (
    ActivityItem,
    ServiceTicket as DemoTicket,
    get_ticket,
    list_tickets,
)


# Kept only for older imports. The Streamlit UI calls list_tickets() on each rerun so
# newly created and updated tickets are visible immediately.
TICKETS = list_tickets()

__all__ = ["ActivityItem", "DemoTicket", "TICKETS", "get_ticket", "list_tickets"]
