from __future__ import annotations

import textwrap
from collections import Counter

import streamlit as st

from app.config import Settings
from app.demo_data import TICKETS, DemoTicket, get_ticket
from app.pipeline import TicketCopilot

st.set_page_config(page_title="LLM Service Desk Copilot", page_icon="🎫", layout="wide", initial_sidebar_state="collapsed")

settings = Settings()
copilot = TicketCopilot(settings)


APP_CSS = """
<style>
    .stApp {
        background: #f4f5f7;
        color: #172b4d;
    }
    [data-testid="stHeader"] {display:none;}
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    .block-container {
        padding-top: 0.4rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .topbar {
        background: #44546a;
        color: white;
        border-radius: 0 0 16px 16px;
        padding: 0.95rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(9,30,66,0.12);
    }
    .topbar-title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .panel {
        background: white;
        border: 1px solid #dfe1e6;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 1px 6px rgba(9,30,66,0.08);
    }
    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .muted {
        color: #6b778c;
        font-size: 0.92rem;
    }
    .badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.2rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 0.35rem;
        border: 1px solid transparent;
    }
    .status-open { background:#deebff; color:#0747a6; }
    .status-progress { background:#eae6ff; color:#5243aa; }
    .status-waiting { background:#fff0b3; color:#7a5d00; }
    .status-resolved { background:#e3fcef; color:#006644; }
    .priority-low { background:#dfe1e6; color:#42526e; }
    .priority-medium { background:#deebff; color:#0747a6; }
    .priority-high { background:#ffebe6; color:#bf2600; }
    .priority-critical { background:#ffebe6; color:#bf2600; border-color:#ff8f73; }
    .category-chip { background:#eae6ff; color:#403294; }
    .metric-chip { background:#f4f5f7; color:#42526e; }
    .small-card {
        background:#fafbfc;
        border:1px solid #dfe1e6;
        border-radius: 14px;
        padding: 0.9rem;
    }
    .summary-card {
        background: #fff7e6;
        border: 1px solid #ffe2a8;
        border-radius: 14px;
        padding: 0.9rem;
        margin-bottom: 0.85rem;
    }
    .pill-list span {
        display:inline-block;
        margin:0 0.35rem 0.35rem 0;
        background:#f4f5f7;
        color:#42526e;
        border:1px solid #dfe1e6;
        border-radius: 999px;
        padding:0.18rem 0.55rem;
        font-size:0.78rem;
    }
    .ticket-desc {
        background:#ffffff;
        border:1px solid #dfe1e6;
        border-radius:14px;
        padding:1rem;
        min-height: 180px;
        line-height:1.55;
    }
    .activity-item {
        padding:0.7rem 0;
        border-bottom:1px solid #ebecf0;
    }
    .activity-item:last-child {border-bottom:none;}
    .right-section-title {
        font-size: 1rem;
        font-weight: 700;
        margin: 0.45rem 0 0.4rem;
    }
    .mono-id {font-weight:700; color:#1d4ed8;}
    .tight p { margin-bottom: 0.35rem; }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #c1c7d0;
        font-weight: 600;
    }
    .queue-button button {
        text-align: left !important;
    }
    .ticket-row {
        background:#ffffff;
        border:1px solid #dfe1e6;
        border-radius:12px;
        padding:0.35rem 0.45rem;
        margin-bottom:0.35rem;
    }
    .selected-row {
        border-color:#4c9aff;
        box-shadow: inset 0 0 0 1px #4c9aff;
        background:#f7fbff;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-weight: 600;
    }
</style>
"""


def badge_html(label: str, kind: str) -> str:
    return f'<span class="badge {kind}">{label}</span>'


def status_class(status: str) -> str:
    lowered = status.lower()
    if "progress" in lowered:
        return "status-progress"
    if "wait" in lowered:
        return "status-waiting"
    if "resolve" in lowered:
        return "status-resolved"
    return "status-open"


def priority_class(priority: str) -> str:
    lowered = priority.lower()
    if lowered == "critical":
        return "priority-critical"
    if lowered == "high":
        return "priority-high"
    if lowered == "medium":
        return "priority-medium"
    return "priority-low"


def render_ticket_filters(tickets: list[DemoTicket]) -> tuple[str, str | None, str | None, str]:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tickets</div>', unsafe_allow_html=True)

    queue_counts = Counter(ticket.queue for ticket in tickets)
    priority_counts = Counter(ticket.priority for ticket in tickets)
    category_counts = Counter(ticket.category for ticket in tickets)

    search = st.text_input("Search Ticket ID", placeholder="SD-1042", label_visibility="collapsed")
    queue = st.radio(
        "Queue",
        ["All", "Open", "In Progress", "Waiting on User", "Resolved"],
        horizontal=False,
        format_func=lambda x: f"{x} ({queue_counts.get(x, len(tickets)) if x != 'All' else len(tickets)})",
    )
    priority = st.selectbox("Priority", ["All", "Critical", "High", "Medium", "Low"])
    category = st.selectbox("Category", ["All"] + sorted(category_counts.keys()))
    st.caption("Tip: select SD-570 to demonstrate guardrails.")
    st.markdown('</div>', unsafe_allow_html=True)
    return search.strip(), None if queue == "All" else queue, None if priority == "All" else priority, "All" if category == "All" else category


@st.cache_data(show_spinner=False)
def run_ticket(ticket_id: str):
    ticket = get_ticket(ticket_id)
    return copilot.run(ticket.to_ticket_input())


def filtered_tickets(search: str, queue: str | None, priority: str | None, category: str | None) -> list[DemoTicket]:
    data = TICKETS
    if search:
        search_lower = search.lower()
        data = [t for t in data if search_lower in t.ticket_id.lower() or search_lower in t.subject.lower()]
    if queue:
        data = [t for t in data if t.queue == queue]
    if priority:
        data = [t for t in data if t.priority == priority]
    if category and category != "All":
        data = [t for t in data if t.category == category]
    return data or TICKETS


def render_queue_table(tickets: list[DemoTicket], selected_ticket_id: str) -> str:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    selected = get_ticket(selected_ticket_id)
    st.markdown(
        f'<div class="section-title"><span class="mono-id">{selected.ticket_id}</span> Service Desk Copilot</div>'
        f'<div class="muted">Jira-style ticket queue with AI assistance embedded in triage and first response.</div>',
        unsafe_allow_html=True,
    )
    header = st.columns([1.2, 3.5, 1.2, 1.6, 1.2])
    header[0].markdown("**Ticket ID**")
    header[1].markdown("**Summary**")
    header[2].markdown("**Priority**")
    header[3].markdown("**Assignee**")
    header[4].markdown("**Status**")

    for ticket in tickets:
        is_selected = ticket.ticket_id == selected_ticket_id
        row_class = "ticket-row selected-row" if is_selected else "ticket-row"
        st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
        cols = st.columns([1.2, 3.5, 1.2, 1.6, 1.2])
        button_type = "primary" if is_selected else "secondary"
        if cols[0].button(ticket.ticket_id, key=f"select_{ticket.ticket_id}", use_container_width=True, type=button_type):
            st.session_state["selected_ticket_id"] = ticket.ticket_id
            st.rerun()
        cols[1].markdown(ticket.subject)
        cols[2].markdown(badge_html(ticket.priority, priority_class(ticket.priority)), unsafe_allow_html=True)
        cols[3].markdown(ticket.assignee)
        cols[4].markdown(badge_html(ticket.status, status_class(ticket.status)), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_ticket_id


def render_ticket_details(ticket: DemoTicket, result) -> None:
    detail_tab, activity_tab, ai_tab = st.tabs(["Details", "Activity", "AI Copilot"])

    with detail_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        chip_row = " ".join(
            [
                badge_html(ticket.status, status_class(ticket.status)),
                badge_html(ticket.priority, priority_class(ticket.priority)),
                badge_html(ticket.category, "category-chip"),
                badge_html(ticket.channel, "metric-chip"),
            ]
        )
        st.markdown(chip_row, unsafe_allow_html=True)

        top = st.columns([2.2, 1.2])
        with top[0]:
            st.markdown(f"### Subject: {ticket.subject}")
            st.markdown(f'<div class="ticket-desc">{ticket.description.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        with top[1]:
            st.markdown('<div class="small-card tight">', unsafe_allow_html=True)
            st.markdown(f"**Reporter**  \n{ticket.reporter}")
            st.markdown(f"**Assignee**  \n{ticket.assignee}")
            st.markdown(f"**Created**  \n{ticket.created_label}")
            st.markdown(f"**SLA due**  \n{ticket.sla_due_label}")
            st.markdown(f"**Risk window**  \n{ticket.sla_breach_label}")
            st.markdown('</div>', unsafe_allow_html=True)
        if ticket.tags:
            st.markdown(
                '<div class="pill-list">' + ''.join(f'<span>{tag}</span>' for tag in ticket.tags) + '</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with activity_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Activity")
        for item in ticket.activity:
            st.markdown(
                f'<div class="activity-item"><strong>{item.time_label}</strong> · {item.author}<br>{item.text}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with ai_tab:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### AI Copilot")
        st.markdown("**Summary**")
        st.markdown(result.summary.replace("\n", "  \n"))
        st.markdown("**Suggested next step**")
        st.markdown(result.grounded_reply.replace("\n", "  \n"))
        if result.citations:
            st.markdown("**Grounding sources**")
            for source in result.citations:
                st.markdown(f"- {source}")
        st.markdown('</div>', unsafe_allow_html=True)


st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(
    '<div class="topbar"><div class="topbar-title">LLM Service Desk Copilot</div>'
    '<div class="muted" style="color:#dfe1e6;">Jira-style triage workspace with responsible GenAI assist for service desk teams.</div></div>',
    unsafe_allow_html=True,
)

if "selected_ticket_id" not in st.session_state:
    st.session_state["selected_ticket_id"] = "SD-1042"

left, center, right = st.columns([1.05, 2.55, 1.2], gap="medium")

with left:
    search_text, queue_filter, priority_filter, category_filter = render_ticket_filters(TICKETS)

visible_tickets = filtered_tickets(search_text, queue_filter, priority_filter, category_filter)
if st.session_state["selected_ticket_id"] not in {t.ticket_id for t in visible_tickets}:
    st.session_state["selected_ticket_id"] = visible_tickets[0].ticket_id

selected_ticket = get_ticket(st.session_state["selected_ticket_id"])
result = run_ticket(selected_ticket.ticket_id)

with center:
    render_queue_table(visible_tickets, selected_ticket.ticket_id)
    render_ticket_details(selected_ticket, result)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Copilot</div>', unsafe_allow_html=True)

    action_cols = st.columns(2)
    if action_cols[0].button("Run Copilot", use_container_width=True, type="primary"):
        run_ticket.clear()
        st.rerun()
    action_cols[1].button("Draft Reply", use_container_width=True)

    st.markdown('<div class="right-section-title">Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-card">{result.summary.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    st.markdown('<div class="right-section-title">Missing Information</div>', unsafe_allow_html=True)
    if result.missing_information:
        for item in result.missing_information:
            st.markdown(f"- {item}")
    else:
        st.markdown("No additional clarification needed.")

    st.markdown('<div class="right-section-title">Suggested Triage</div>', unsafe_allow_html=True)
    st.markdown(badge_html(result.category, "category-chip"), unsafe_allow_html=True)
    st.markdown(badge_html(result.priority, priority_class(result.priority)), unsafe_allow_html=True)
    reason_line = result.grounded_reply.split("Priority reason:")[-1].strip() if "Priority reason:" in result.grounded_reply else result.confidence_note
    st.caption(reason_line)

    st.markdown('<div class="right-section-title">Draft Reply</div>', unsafe_allow_html=True)
    st.text_area(
        "Draft reply",
        value=result.grounded_reply,
        height=220,
        label_visibility="collapsed",
    )

    st.markdown('<div class="right-section-title">Knowledge Grounding</div>', unsafe_allow_html=True)
    if result.citations:
        for source in result.citations:
            st.markdown(f"- {source}")
    else:
        st.markdown("No approved article matched strongly.")

    st.markdown('<div class="right-section-title">Guardrails</div>', unsafe_allow_html=True)
    if result.refused:
        st.error("Unsafe request blocked. The assistant refused to help bypass security or reveal hidden instructions.")
    else:
        st.success("Grounded-answer mode enabled. Replies are constrained to approved internal articles.")
    if result.guardrail_notes:
        for note in result.guardrail_notes:
            st.caption(f"• {note}")
    else:
        st.caption("• No guardrail event triggered for this ticket.")
    st.caption(f"Provider: {settings.llm_provider} · Model: {settings.llm_model} · Retrieval top-k: {settings.retrieval_top_k}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="muted" style="padding:0.5rem 0 0 0.2rem;">Demo note: this build intentionally uses a deterministic mock provider by default for a clean-machine investor demo. Switch to Azure OpenAI or another compatible endpoint only after updating the README and slides to match.</div>',
    unsafe_allow_html=True,
)
