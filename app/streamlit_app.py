from __future__ import annotations

from collections import Counter
from html import escape
import re

import streamlit as st

from app.agents import record_human_decision, record_self_service_outcome
from app.config import Settings
from app.data_store import (
    ServiceTicket,
    SUPPORT_TEAMS,
    create_ticket,
    database_counts,
    get_approved_articles,
    get_ticket,
    initialize_database,
    list_tickets,
    record_retrieval_feedback,
    reassign_ticket,
    resolve_ticket,
    score_priority,
    update_ai_classification,
)
from app.pipeline import TicketCopilot
from app.llm import LLMConfigurationError, filter_missing_information
from app.models import TicketInput


st.set_page_config(
    page_title="AegisDesk · Agentic Service Operations",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ANALYSIS_VERSION = "2026-09-16-v4"
AUTO_ROUTE_OPTION = "Not sure — let AegisDesk recommend"

initialize_database()
settings = Settings()
try:
    copilot = TicketCopilot(settings)
    llm_setup_error = ""
except LLMConfigurationError as exc:
    copilot = None
    llm_setup_error = str(exc)


APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root {
    --ink: #e8eef9;
    --muted: #8fa2bd;
    --navy: #07111f;
    --panel: rgba(14, 30, 51, 0.88);
    --panel-2: rgba(20, 40, 65, 0.82);
    --line: rgba(148, 176, 214, 0.16);
    --mint: #2dd4bf;
    --violet: #8b5cf6;
    --amber: #f59e0b;
}

html, body, [class*="css"] { font-family: "DM Sans", sans-serif; font-size: 16px; }
.stApp {
    color: var(--ink);
    background:
        radial-gradient(circle at 88% 2%, rgba(45,212,191,.14), transparent 26rem),
        radial-gradient(circle at 8% 22%, rgba(124,58,237,.16), transparent 28rem),
        linear-gradient(145deg, #050b14 0%, #081524 48%, #07111f 100%);
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 1.1rem 1.7rem 2.5rem; max-width: 1600px; }

h1, h2, h3, .brand, .metric-value { font-family: "Manrope", sans-serif; }
.hero {
    position: relative;
    overflow: hidden;
    padding: 1.3rem 1.45rem;
    border: 1px solid rgba(148,176,214,.18);
    border-radius: 24px;
    background: linear-gradient(115deg, rgba(15,31,52,.96), rgba(10,27,47,.76));
    box-shadow: 0 24px 70px rgba(0,0,0,.28);
    margin-bottom: 1rem;
}
.hero:after {
    content: "";
    position: absolute;
    width: 260px; height: 260px; right: -80px; top: -150px;
    border-radius: 50%; background: rgba(45,212,191,.13); filter: blur(5px);
}
.eyebrow { color: var(--mint); text-transform: uppercase; letter-spacing: .14em; font-size: .72rem; font-weight: 800; }
.brand { font-size: 2rem; line-height: 1.05; font-weight: 800; letter-spacing: -.04em; margin: .35rem 0; }
.hero-sub { color: #d4deeb; max-width: 920px; font-size: 1rem; line-height: 1.5; }
.live-pill {
    display: inline-flex; align-items: center; gap: .45rem; float: right;
    color: #b9fff3; background: rgba(45,212,191,.10); border: 1px solid rgba(45,212,191,.28);
    padding: .42rem .7rem; border-radius: 999px; font-size: .76rem; font-weight: 700;
}
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--mint); box-shadow: 0 0 14px var(--mint); }

.metric-card {
    min-height: 106px; padding: .95rem 1rem; border-radius: 18px;
    border: 1px solid var(--line); background: var(--panel);
    box-shadow: 0 14px 35px rgba(0,0,0,.18);
}
.metric-label { color: #b9c8da; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }
.metric-value { color: #f8fbff; font-size: 1.65rem; font-weight: 800; margin: .25rem 0 .1rem; }
.metric-note { color: #afbed1; font-size: .8rem; line-height: 1.35; }
.accent-mint { color: var(--mint); }
.accent-violet { color: #a78bfa; }
.accent-amber { color: #fbbf24; }

.glass {
    border: 1px solid var(--line); background: var(--panel); border-radius: 20px;
    padding: 1rem; box-shadow: 0 16px 42px rgba(0,0,0,.20); margin-bottom: .8rem;
}
.section-kicker { color: var(--mint); font-size: .69rem; text-transform: uppercase; letter-spacing: .1em; font-weight: 800; }
.section-title { font-family: "Manrope", sans-serif; color: #f5f8fd; font-size: 1.18rem; font-weight: 800; margin: .2rem 0 .65rem; }
.muted { color: #b1c0d3; }
.tiny { color: #a9b9cd; font-size: .78rem; line-height: 1.4; }

.purpose-grid {
    display:grid; grid-template-columns:repeat(3,1fr); gap:.75rem;
    margin:0 0 1rem;
}
.purpose-item {
    padding:.8rem .9rem; border-radius:15px; background:rgba(18,39,65,.78);
    border:1px solid rgba(148,176,214,.20); color:#dce7f5; font-size:.88rem; line-height:1.45;
}
.purpose-label {
    display:block; color:#5eead4; font-size:.72rem; font-weight:900;
    letter-spacing:.1em; margin-bottom:.22rem;
}

.ticket-head { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; }
.ticket-id { color: var(--mint); font-family: monospace; font-weight: 800; letter-spacing: .04em; }
.ticket-subject { font-family:"Manrope",sans-serif; color:#f8fbff; font-size:1.35rem; font-weight:800; margin:.2rem 0; }
.ticket-copy { color:#d8e2ef; font-size:.92rem; line-height:1.65; padding:.8rem 0; }
.ticket-meta { display:grid; grid-template-columns:repeat(4,1fr); gap:.65rem; margin-top:.7rem; }
.meta-cell { padding:.65rem .7rem; border-radius:12px; background:rgba(143,162,189,.08); border:1px solid rgba(148,176,214,.22); color:#e5edf7; font-size:.84rem; }
.meta-label { display:block; color:#afc0d4; font-size:.68rem; font-weight:800; letter-spacing:.08em; margin-bottom:.25rem; }
.triage-grid { display:grid; grid-template-columns:1fr 1fr; gap:.65rem; margin:.75rem 0; }
.triage-cell { padding:.6rem .7rem; border-radius:12px; background:rgba(143,162,189,.05); border:1px solid var(--line); }
.tag { display:inline-block; margin:.15rem .3rem .15rem 0; padding:.28rem .58rem; border-radius:999px; background:rgba(143,162,189,.13); border:1px solid rgba(148,176,214,.25); color:#d0dbea; font-size:.77rem; }
.badge { display:inline-block; border-radius:999px; padding:.28rem .62rem; font-size:.76rem; font-weight:800; margin:.1rem .25rem .1rem 0; }
.b-high, .b-critical { background:rgba(251,113,133,.14); color:#fda4af; border:1px solid rgba(251,113,133,.22); }
.b-medium { background:rgba(245,158,11,.14); color:#fbbf24; border:1px solid rgba(245,158,11,.22); }
.b-low { background:rgba(45,212,191,.12); color:#5eead4; border:1px solid rgba(45,212,191,.2); }
.b-status { background:rgba(139,92,246,.13); color:#c4b5fd; border:1px solid rgba(139,92,246,.2); }
.b-category { background:rgba(59,130,246,.13); color:#93c5fd; border:1px solid rgba(59,130,246,.2); }

.summary-box { padding:.9rem; border-radius:16px; background:linear-gradient(135deg,rgba(45,212,191,.10),rgba(59,130,246,.08)); border:1px solid rgba(45,212,191,.16); color:#dce8f7; line-height:1.55; }
.control-box { padding:.75rem .85rem; border-radius:14px; background:rgba(245,158,11,.08); border:1px solid rgba(245,158,11,.2); color:#f8d793; font-size:.82rem; }
.success-box { padding:.75rem .85rem; border-radius:14px; background:rgba(45,212,191,.09); border:1px solid rgba(45,212,191,.22); color:#9ff3e6; font-size:.82rem; }

.agent-step { display:grid; grid-template-columns:38px 1fr auto; gap:.75rem; align-items:start; padding:.8rem .15rem; border-bottom:1px solid var(--line); }
.agent-step:last-child { border-bottom:none; }
.agent-num { width:32px; height:32px; display:grid; place-items:center; border-radius:10px; color:#07111f; background:linear-gradient(135deg,var(--mint),#60a5fa); font-weight:900; }
.agent-name { color:#f4f8ff; font-weight:800; font-size:.9rem; }
.agent-role { color:#afbed1; font-size:.8rem; margin:.12rem 0 .35rem; line-height:1.4; }
.agent-decision { color:#d0dbea; font-size:.84rem; line-height:1.45; }
.agent-state { font-size:.68rem; text-transform:uppercase; letter-spacing:.06em; padding:.22rem .45rem; border-radius:999px; background:rgba(45,212,191,.1); color:#75ead9; }
.agent-state.blocked, .agent-state.block, .agent-state.escalated, .agent-state.escalate { background:rgba(251,113,133,.1); color:#fda4af; }

.evidence { padding:.75rem 0; border-bottom:1px solid var(--line); }
.evidence:last-child { border-bottom:none; }
.evidence-title { color:#dbeafe; font-weight:700; }
.evidence-score { color:var(--mint); font-family:monospace; }
.activity { padding:.7rem 0; border-bottom:1px solid var(--line); color:#adbbcd; font-size:.82rem; }

div[data-testid="stTabs"] button[role="tab"] { color:#b7c6d9; font-size:.84rem; font-weight:800; padding-top:.8rem; padding-bottom:.8rem; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#5eead4; }
.stButton > button {
    border-radius:12px !important; font-size:.84rem !important; font-weight:800 !important;
    min-height:44px; color:#edf5ff !important; background:#122944 !important;
    border:1px solid #355372 !important;
}
.stButton > button:hover { color:#ffffff !important; background:#1a3b60 !important; border-color:#5f84ac !important; }
.stButton > button[kind="primary"] { color:#031421 !important; background:linear-gradient(135deg,#36d8c4,#6aaeff) !important; border:none !important; }
.stButton > button[kind="primary"]:hover { color:#031421 !important; background:linear-gradient(135deg,#58e5d3,#84bcff) !important; }
.stButton > button:disabled { color:#9bacc0 !important; background:#16263a !important; border-color:#2a4059 !important; opacity:.82 !important; }
div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea { background:#0c1b2e; color:#dce7f5; border-color:rgba(148,176,214,.18); }
input::placeholder, textarea::placeholder { color:#91a4bc !important; opacity:1 !important; }
label, .stRadio label { color:#d0dbea !important; font-size:.86rem !important; }
.stMarkdown p, .stMarkdown li { color:#d8e2ef; font-size:.88rem; line-height:1.5; }
[data-testid="stCaptionContainer"] p { color:#aebed1 !important; font-size:.78rem !important; line-height:1.45; }
.stTextArea textarea { font-size:.86rem !important; line-height:1.5 !important; }
.footer-note { margin-top:1rem; padding:.85rem 1rem; color:#aebed1; font-size:.76rem; line-height:1.5; border-top:1px solid var(--line); }

/* Light sky workspace: high contrast without the previous dark-on-dark effect. */
:root {
    --ink:#17324d; --muted:#5f7690; --navy:#eaf5ff; --panel:rgba(255,255,255,.88);
    --panel-2:#edf7ff; --line:rgba(36,104,157,.18); --mint:#078f91;
    --violet:#6857d9; --amber:#b86508;
}
.stApp {
    color:var(--ink);
    background:
        radial-gradient(circle at 92% 3%, rgba(70,190,223,.23), transparent 28rem),
        radial-gradient(circle at 5% 28%, rgba(129,173,255,.20), transparent 30rem),
        linear-gradient(145deg,#eef9ff 0%,#deeffc 48%,#edf7ff 100%);
}
.hero {
    background:linear-gradient(115deg,rgba(255,255,255,.96),rgba(219,243,255,.94));
    border-color:rgba(51,125,178,.22); box-shadow:0 20px 55px rgba(49,102,145,.15);
}
.hero:after { background:rgba(31,171,194,.15); }
.brand,.section-title,.ticket-subject,.metric-value { color:#123354; }
.metric-value.accent-mint { color:#078f91; }
.metric-value.accent-violet { color:#6857d9; }
.metric-value.accent-amber { color:#b86508; }
.hero-sub,.ticket-copy { color:#38536d; }
.live-pill { color:#08696e; background:rgba(31,184,181,.10); border-color:rgba(7,143,145,.26); }
.metric-card,.glass {
    background:rgba(255,255,255,.88); border-color:rgba(51,125,178,.18);
    box-shadow:0 13px 32px rgba(49,102,145,.11);
}
.metric-label,.metric-note,.muted,.tiny { color:#5b7189; }
.purpose-item { background:rgba(255,255,255,.75); border-color:rgba(51,125,178,.18); color:#36536e; }
.purpose-label,.section-kicker { color:#087f83; }
.meta-cell,.triage-cell { background:rgba(235,246,255,.88); border-color:rgba(51,125,178,.19); color:#25455f; }
.meta-label { color:#60758c; }
.triage-grid { grid-template-columns:repeat(3,1fr); }
.tag { background:#edf6ff; border-color:#c8deee; color:#31516b; }
.b-high,.b-critical { background:#fff0f2; color:#bb2944; border-color:#f1bcc7; }
.b-medium { background:#fff6df; color:#986000; border-color:#efd494; }
.b-low { background:#e6f9f5; color:#08756f; border-color:#a9dfd6; }
.b-status { background:#f0edff; color:#5946b5; border-color:#ccc3f4; }
.b-category { background:#e8f2ff; color:#245f9d; border-color:#bdd7f1; }
.summary-box { background:linear-gradient(135deg,#e5fbf7,#eaf5ff); border-color:#a8ddd7; color:#183f59; }
.control-box { background:#fff7e7; border-color:#ebcc8f; color:#794a08; }
.success-box { background:#e7f9f3; border-color:#9dd9c8; color:#11634f; }
.agent-name,.agent-decision,.evidence-title { color:#173b5b; }
.agent-role,.activity { color:#5d7185; }
.agent-state { background:#ddf6f1; color:#08756f; }
div[data-testid="stTabs"] button[role="tab"] { color:#587089; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#087f83; }
.stButton > button { color:#21445f !important; background:#f8fcff !important; border-color:#aac9df !important; }
.stButton > button:hover { color:#123554 !important; background:#e5f4ff !important; border-color:#63a4ce !important; }
.stButton > button[kind="primary"] { color:#082b3a !important; background:linear-gradient(135deg,#56d8cf,#7dbdff) !important; }
.stButton > button[kind="primary"]:hover { color:#082b3a !important; background:linear-gradient(135deg,#70e2d9,#96caff) !important; }
.stButton > button:disabled { color:#8295a8 !important; background:#e7eef4 !important; border-color:#c7d6e1 !important; }
div[data-baseweb="select"] > div,.stTextInput input,.stTextArea textarea {
    background:#ffffff; color:#17324d; border-color:#abc9df;
}
input::placeholder,textarea::placeholder { color:#7890a6 !important; }
label,.stRadio label,.stMarkdown p,.stMarkdown li { color:#294861 !important; }
[data-testid="stCaptionContainer"] p { color:#60758a !important; }
.footer-note { color:#5c748b; }

.assist-kicker { margin-top:1rem; margin-bottom:.45rem; }
.intelligence-card {
    padding:1rem 1.05rem; border-radius:16px; margin:.55rem 0;
    background:rgba(255,255,255,.94); border:1px solid #b8d5e8;
    box-shadow:0 10px 25px rgba(52,104,145,.10);
}
.case-card { border-left:5px solid #12a7a2; background:linear-gradient(120deg,#f4fffd,#f2f8ff); }
.doc-card { border-left:5px solid #528de0; background:linear-gradient(120deg,#f7fbff,#eef6ff); }
.no-match { border-left:5px solid #d29a35; background:#fffaf0; }
.intel-top { display:flex; align-items:center; justify-content:space-between; gap:.7rem; }
.intel-label { color:#087f83; font-weight:900; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; }
.intel-title { color:#153a59; font-family:"Manrope",sans-serif; font-size:1rem; font-weight:800; margin:.32rem 0; }
.intel-subtitle { color:#55728c; font-size:.76rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; margin:.55rem 0 .18rem; }
.intel-copy { color:#294c66; font-size:.87rem; line-height:1.55; }
.match-chip { white-space:nowrap; color:#215878; background:#e4f3fb; border:1px solid #b6d7e8; border-radius:999px; padding:.24rem .52rem; font-size:.7rem; font-weight:800; }
.safety-note { color:#637b90; border-top:1px solid #d5e6f0; margin-top:.7rem; padding-top:.55rem; font-size:.72rem; font-weight:700; }

@media (max-width: 1100px) {
    .block-container { padding: .8rem 1rem 2rem; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 320px !important; width: auto !important; min-width: 300px !important;
    }
    .purpose-grid { grid-template-columns:1fr; }
    .hero .live-pill { float:none; margin-bottom:.5rem; }
}

@media (max-width: 650px) {
    .brand { font-size:1.65rem; }
    .hero-sub { font-size:.92rem; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width:100% !important; }
    .ticket-meta, .triage-grid { grid-template-columns:1fr; }
}
</style>
"""


def badge(label: str, kind: str) -> str:
    return f'<span class="badge {kind}">{escape(label)}</span>'


def priority_kind(priority: str) -> str:
    value = priority.lower()
    return f"b-{value}" if value in {"low", "medium", "high", "critical"} else "b-medium"


def _plain_evidence(text: str, limit: int = 620) -> str:
    cleaned = re.sub(r"(?m)^#{1,6}\s*", "", text)
    cleaned = re.sub(r"(?m)^[-*]\s+", "• ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1].rstrip() + "…"


def _verified_resolution(text: str) -> str:
    marker = "Verified resolution:"
    resolution = text.split(marker, 1)[1] if marker in text else text
    return _plain_evidence(resolution)


def filtered_tickets(
    tickets: list[ServiceTicket], search: str, queue: str | None, priority: str | None
) -> list[ServiceTicket]:
    if search:
        lowered = search.lower()
        tickets = [ticket for ticket in tickets if lowered in ticket.ticket_id.lower() or lowered in ticket.subject.lower()]
    if queue:
        tickets = [ticket for ticket in tickets if ticket.queue == queue]
    if priority:
        tickets = [ticket for ticket in tickets if ticket.priority == priority]
    return tickets


@st.cache_data(show_spinner=False)
def run_ticket(ticket_id: str, updated_at: str):
    if copilot is None:
        raise LLMConfigurationError(llm_setup_error)
    return copilot.run(get_ticket(ticket_id).to_ticket_input())


@st.cache_data(show_spinner=False)
def analyze_employee_request(
    subject: str,
    description: str,
    reporter: str,
    channel: str,
    business_impact: str,
    urgency: str,
    affected_users: int,
    requested_team: str,
    analysis_version: str,
):
    if copilot is None:
        raise LLMConfigurationError(llm_setup_error)
    operational_context = (
        f"\n\nOperational context: business impact={business_impact}; "
        f"urgency={urgency}; affected users={affected_users}."
    )
    result = copilot.run(
        TicketInput(
            subject=subject,
            description=description + operational_context,
            requester=reporter,
            channel=channel,
        )
    )
    if requested_team != AUTO_ROUTE_OPTION and not result.refused:
        result.assigned_team = requested_team
    return result


@st.dialog("Create a smart service ticket")
def create_ticket_dialog() -> None:
    st.caption("Describe the issue in plain language. The priority engine places urgent, high-impact work first; agents then validate the classification and propose an evidence-backed response.")
    with st.form("create-ticket-form", clear_on_submit=False):
        subject = st.text_input("Short summary", placeholder="Example: VPN access blocked before a client meeting")
        description = st.text_area(
            "What happened?",
            placeholder="Include the error, when it started, who is affected, and what you already tried.",
            height=145,
        )
        reporter = st.text_input("Your name or work email", placeholder="name@company.com")
        left, right = st.columns(2)
        with left:
            business_impact = st.selectbox(
                "Business impact", ["Single user", "Team", "Department", "Company-wide"]
            )
            urgency = st.selectbox("Urgency", ["Normal", "High", "Immediate", "Low"])
        with right:
            affected_users = st.number_input("People affected", min_value=1, max_value=10000, value=1)
            channel = st.selectbox("Contact channel", ["Web Portal", "Email", "Teams", "Slack", "Phone"])
        submitted = st.form_submit_button("Create and run agents", type="primary", use_container_width=True)
    if submitted:
        if len(subject.strip()) < 5 or len(description.strip()) < 15:
            st.error("Please provide a clear summary and at least 15 characters of issue detail.")
            return
        ticket_id = create_ticket(
            subject=subject,
            description=description,
            reporter=reporter,
            channel=channel,
            business_impact=business_impact,
            urgency=urgency,
            affected_users=int(affected_users),
        )
        st.session_state["selected_ticket_id"] = ticket_id
        run_ticket.clear()
        st.rerun()


def render_employee_portal() -> None:
    model_badge = (
        f"LIVE LLM · {escape(settings.llm_model)}"
        if settings.llm_provider != "mock"
        else "EXPLICIT TEST MODE"
    )
    st.markdown(
        f"""
        <div class="hero employee-hero">
          <div class="live-pill"><span class="live-dot"></span> {model_badge}</div>
          <div class="eyebrow">Page 1 · Company request portal</div>
          <div class="brand">Employee Request <span class="accent-mint">Portal</span></div>
          <div class="hero-sub">One front door for requests between every company department. Describe what you need; AegisDesk clarifies it, finds approved help, and routes it to the right team.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-kicker">Step 1</div><div class="section-title">Tell us what you need</div>', unsafe_allow_html=True)
    with st.form("employee-help-request"):
        subject = st.text_input(
            "Short summary",
            placeholder="Example: Yesterday's sales total differs from the Finance report",
        )
        description = st.text_area(
            "Describe the problem",
            placeholder="What did you expect, what happened, when did it start, who is affected, and what did you already check?",
            height=150,
        )
        reporter = st.text_input("Your name or work email", placeholder="name@company.com")
        form_left, form_right = st.columns(2)
        with form_left:
            business_impact = st.selectbox(
                "Who or what is affected?", ["Single user", "Team", "Department", "Company-wide"]
            )
            urgency = st.selectbox("How urgent is it?", ["Normal", "High", "Immediate", "Low"])
        with form_right:
            affected_users = st.number_input("People affected", min_value=1, max_value=10000, value=1)
            channel = st.selectbox(
                "How should we contact you?",
                ["Web Portal", "Email", "Teams", "Slack", "Phone"],
                help="Choose where you want to receive status updates or follow-up questions.",
            )
        requested_team = st.selectbox(
            "Which department should receive this ticket?",
            [AUTO_ROUTE_OPTION, *SUPPORT_TEAMS],
            help="Choose a department when you know the owner. Otherwise, AegisDesk recommends one from the request context.",
        )
        analyse = st.form_submit_button("Analyse before submitting", type="primary", use_container_width=True)

    signature = (
        subject.strip(), description.strip(), reporter.strip(), channel,
        business_impact, urgency, int(affected_users), requested_team, ANALYSIS_VERSION,
    )
    if analyse:
        if len(subject.strip()) < 5 or len(description.strip()) < 15:
            st.error("Please provide a clear summary and at least 15 characters of detail.")
        else:
            try:
                with st.spinner("The specialist agents are checking routing, solved cases, and approved guidance…"):
                    result = analyze_employee_request(*signature)
            except Exception as exc:
                st.error(f"The live LLM could not complete this analysis: {exc}")
                st.info("No simulated answer was substituted. Check the model connection and try again.")
                return
            st.session_state["employee_analysis"] = {"signature": signature, "result": result}
            st.session_state.pop("employee_outcome", None)

    analysis = st.session_state.get("employee_analysis")
    if not analysis or analysis["signature"] != signature:
        st.markdown(
            '<div class="intelligence-card doc-card"><div class="intel-label">Nothing is submitted yet</div>'
            '<div class="intel-copy">Select <strong>Analyse before submitting</strong>. You will see the likely team, similar solved cases, safe steps, documentation, and missing details before deciding whether a ticket is necessary.</div></div>',
            unsafe_allow_html=True,
        )
        return

    result = analysis["result"]
    intake_priority, intake_score, _ = score_priority(
        subject, description, business_impact, urgency, int(affected_users)
    )
    st.markdown('<div class="section-kicker assist-kicker">Step 2 · Analysis result</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="triage-grid">'
        f'<div class="triage-cell"><span class="meta-label">REQUEST TYPE</span><strong>{escape(result.issue_type)}</strong><br>{badge(result.category, "b-category")}</div>'
        f'<div class="triage-cell"><span class="meta-label">DESTINATION TEAM</span><strong>{escape(result.assigned_team)}</strong></div>'
        f'<div class="triage-cell"><span class="meta-label">INTAKE PRIORITY</span>{badge(intake_priority, priority_kind(intake_priority))}<br><span class="tiny">Score {intake_score}/100</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    similar_cases = [item for item in result.retrieved_evidence if item.source_type == "verified_case"]
    articles = [item for item in result.retrieved_evidence if item.source_type == "knowledge_article"]
    if result.refused:
        st.markdown('<div class="control-box"><strong>Safety review required.</strong> No automated troubleshooting is shown. The request can only be submitted to Security Operations.</div>', unsafe_allow_html=True)
    elif similar_cases:
        best_case = similar_cases[0]
        st.markdown(
            f"""
            <div class="intelligence-card case-card">
              <div class="intel-top"><span class="intel-label">A similar request was solved</span><span class="match-chip">{best_case.score:.0%} relevance</span></div>
              <div class="intel-title">{escape(best_case.source_title)}</div>
              <div class="intel-subtitle">Safe solution to try</div>
              <div class="intel-copy">{escape(_verified_resolution(best_case.text))}</div>
              <div class="safety-note">Try only steps you are authorized to perform. Never share passwords, payment data, or bypass company controls.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="intelligence-card no-match"><div class="intel-label">No sufficiently similar solved case</div><div class="intel-copy">We will not invent a fix. Approved documentation and the destination team are shown instead.</div></div>', unsafe_allow_html=True)

    if articles:
        article = articles[0]
        st.markdown(
            f"""
            <div class="intelligence-card doc-card">
              <div class="intel-top"><span class="intel-label">Why it may happen · approved documentation</span><span class="match-chip">{article.score:.0%} relevance</span></div>
              <div class="intel-title">{escape(article.source_title)}</div>
              <div class="intel-copy">{escape(_plain_evidence(article.text, 760))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    visible_questions = filter_missing_information(
        TicketInput(
            subject=subject,
            description=(
                f"{description}\nOperational context: business impact={business_impact}; "
                f"urgency={urgency}; affected users={int(affected_users)}."
            ),
        ),
        result.category,
        result.missing_information,
    )
    st.markdown('<div class="intelligence-card"><div class="intel-label">Questions still missing</div>', unsafe_allow_html=True)
    if visible_questions:
        for item in visible_questions:
            st.markdown(f"- {item}")
    else:
        st.write("Your request contains the main diagnostic details.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("employee_outcome") == "solved":
        st.success("Great—this request is marked as solved through self-service. No ticket was created.")
        return

    action_left, action_right = st.columns(2)
    with action_left:
        if st.button("The suggested solution worked", use_container_width=True, disabled=result.refused):
            st.session_state["employee_outcome"] = "solved"
            record_self_service_outcome(result.workflow_id, result.category, "solved_without_ticket")
            st.rerun()
    with action_right:
        submit_label = "Submit to Security Operations" if result.refused else "Submit ticket"
        if st.button(submit_label, type="primary", use_container_width=True):
            final_team = (
                "Security Operations"
                if result.refused
                else requested_team if requested_team != AUTO_ROUTE_OPTION else result.assigned_team
            )
            ticket_id = create_ticket(
                subject=subject,
                description=description,
                reporter=reporter,
                channel=channel,
                business_impact=business_impact,
                urgency=urgency,
                affected_users=int(affected_users),
            )
            update_ai_classification(
                ticket_id,
                result.category,
                result.priority,
                assigned_team=final_team,
            )
            record_self_service_outcome(result.workflow_id, result.category, "ticket_submitted")
            st.session_state["selected_ticket_id"] = ticket_id
            st.session_state["submission_confirmation"] = (ticket_id, final_team)
            st.session_state["page_route"] = "Support Workspace"
            st.session_state.pop("employee_analysis", None)
            run_ticket.clear()
            st.rerun()


def render_header() -> None:
    model_badge = (
        f"LIVE LLM · {escape(settings.llm_model)}"
        if settings.llm_provider != "mock"
        else "EXPLICIT TEST MODE"
    )
    st.markdown(
        f"""
        <div class="hero">
          <div class="live-pill"><span class="live-dot"></span> {model_badge}</div>
          <div class="eyebrow">Page 2 · Cross-department resolution workspace</div>
          <div class="brand">AegisDesk <span class="accent-mint">AI</span></div>
          <div class="hero-sub">Requests can move between IT, Data, Operations, Finance, HR, Security, Ecommerce, and other specialist teams—with visible evidence, clear ownership, and accountable resolution.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(counts: dict[str, int]) -> None:
    cards = [
        ("Smart queue", str(counts["tickets"]), "Company requests in one prioritised feed", "accent-mint"),
        ("Grounding corpus", str(counts["articles"]), "Approved company articles", "accent-mint"),
        ("Case memory", str(counts["verified_solutions"]), "Human-verified reusable resolutions", "accent-amber"),
    ]
    columns = st.columns(3)
    for column, (label, value, note, accent) in zip(columns, cards):
        with column:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value {accent}">{value}</div><div class="metric-note">{note}</div></div>',
                unsafe_allow_html=True,
            )


def render_purpose() -> None:
    st.markdown(
        """
        <div class="purpose-grid">
          <div class="purpose-item"><span class="purpose-label">WHO IT SERVES</span>Every company department can request help or resolve work: IT, Data, Operations, Finance, HR, Security, Ecommerce, and specialist teams.</div>
          <div class="purpose-item"><span class="purpose-label">WHAT APPEARS AFTER SUBMISSION</span>The responsible team, priority, closest verified solution, approved documentation, missing facts, and an editable response.</div>
          <div class="purpose-item"><span class="purpose-label">WHY IT IS SMARTER</span>It reuses reviewed experience and explains likely causes while safety controls and accountable humans retain the final word.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filters(tickets: list[ServiceTicket]) -> tuple[list[ServiceTicket], str]:
    queue_counts = Counter(ticket.queue for ticket in tickets)
    with st.container():
        st.markdown('<div class="section-kicker">Portfolio</div><div class="section-title">Service queue</div>', unsafe_allow_html=True)
        search = st.text_input("Search", placeholder="Search ID or subject", label_visibility="collapsed")
        queue = st.radio(
            "Queue",
            ["All", "Open", "In Progress", "Waiting on User", "Resolved"],
            format_func=lambda value: f"{value} · {len(tickets) if value == 'All' else queue_counts.get(value, 0)}",
        )
        priority = st.selectbox("Impact", ["All", "Critical", "High", "Medium", "Low"])
    visible = filtered_tickets(
        tickets,
        search.strip(),
        None if queue == "All" else queue,
        None if priority == "All" else priority,
    )
    if not visible:
        st.warning("No exact match. Showing the full demonstration queue.")
        visible = list(tickets)

    selected_id = st.session_state.get("selected_ticket_id", visible[0].ticket_id)
    if selected_id not in {ticket.ticket_id for ticket in visible}:
        selected_id = visible[0].ticket_id
        st.session_state["selected_ticket_id"] = selected_id

    st.markdown('<div class="section-kicker" style="margin-top:1rem">Cases</div>', unsafe_allow_html=True)
    show_all_cases = st.toggle("Show all cases", value=False)
    displayed = list(visible) if show_all_cases else list(visible[:6])
    if not show_all_cases and selected_id not in {item.ticket_id for item in displayed}:
        selected_ticket = next(item for item in visible if item.ticket_id == selected_id)
        displayed = [selected_ticket, *[item for item in displayed if item.ticket_id != selected_id]][:6]
    for ticket in displayed:
        label = f"{ticket.ticket_id}  ·  {ticket.priority}  ·  {ticket.priority_score}/100\n{ticket.subject}"
        if st.button(
            label,
            key=f"ticket-{ticket.ticket_id}",
            type="primary" if ticket.ticket_id == selected_id else "secondary",
            use_container_width=True,
        ):
            st.session_state["selected_ticket_id"] = ticket.ticket_id
            st.rerun()
    if not show_all_cases and len(visible) > len(displayed):
        st.caption(f"Showing {len(displayed)} priority cases. Enable 'Show all cases' to browse {len(visible)} cases.")
    st.caption("The feed is sorted by open status, priority score, severity and age. Select SD-1036 to demonstrate a stopped unsafe workflow.")
    return visible, selected_id


def render_ticket(ticket: ServiceTicket) -> None:
    tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in ticket.tags)
    st.markdown(
        f"""
        <div class="glass">
          <div class="ticket-head">
            <div>
              <div class="ticket-id">{escape(ticket.ticket_id)}</div>
              <div class="ticket-subject">{escape(ticket.subject)}</div>
              {badge(ticket.status, 'b-status')}{badge(ticket.priority, priority_kind(ticket.priority))}{badge(ticket.category, 'b-category')}
            </div>
            <div class="tiny">SLA due<br><strong style="color:#173b5b">{escape(ticket.sla_due_label)}</strong></div>
          </div>
          <div class="ticket-copy">{escape(ticket.description).replace(chr(10), '<br>')}</div>
          <div>{tags}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="ticket-meta">
          <div class="meta-cell"><span class="meta-label">REPORTER</span>{escape(ticket.reporter)}</div>
          <div class="meta-cell"><span class="meta-label">OWNER</span>{escape(ticket.assignee)}</div>
          <div class="meta-cell"><span class="meta-label">CHANNEL</span>{escape(ticket.channel)}</div>
          <div class="meta-cell"><span class="meta-label">QUEUE SCORE</span>{ticket.priority_score}/100 · {escape(ticket.business_impact)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_copilot(ticket: ServiceTicket, result) -> None:
    st.markdown('<div class="section-kicker">Decision workspace</div><div class="section-title">Agent recommendation</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{escape(result.summary).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="triage-grid">'
        f'<div class="triage-cell"><span class="meta-label">ISSUE TYPE</span>{escape(result.issue_type)}</div>'
        f'<div class="triage-cell"><span class="meta-label">RECOMMENDED TEAM</span><strong>{escape(result.assigned_team)}</strong></div>'
        f'<div class="triage-cell"><span class="meta-label">PRIORITY</span>{badge(result.priority, priority_kind(result.priority))}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    similar_cases = [item for item in result.retrieved_evidence if item.source_type == "verified_case"]
    articles = [item for item in result.retrieved_evidence if item.source_type == "knowledge_article"]
    st.markdown('<div class="section-kicker assist-kicker">Smart assistance · shown immediately</div>', unsafe_allow_html=True)
    if result.refused:
        st.markdown('<div class="control-box"><strong>No solution displayed.</strong> Unsafe input was stopped and routed to Security Operations.</div>', unsafe_allow_html=True)
    elif similar_cases:
        best_case = similar_cases[0]
        match_label = "Strong prior-case match" if best_case.score >= 0.35 else "Closest verified case"
        st.markdown(
            f"""
            <div class="intelligence-card case-card">
              <div class="intel-top"><span class="intel-label">{match_label}</span><span class="match-chip">{best_case.score:.0%} relevance</span></div>
              <div class="intel-title">{escape(best_case.source_title)}</div>
              <div class="intel-subtitle">What worked previously</div>
              <div class="intel-copy">{escape(_verified_resolution(best_case.text))}</div>
              <div class="safety-note">Suggestion only · confirm the same conditions before applying · human approval required</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="intelligence-card no-match"><div class="intel-label">No verified identical case found</div>'
            '<div class="intel-copy">The agents will use approved documentation and ask for missing facts. They will not invent a previous solution.</div></div>',
            unsafe_allow_html=True,
        )

    if articles:
        best_article = articles[0]
        st.markdown(
            f"""
            <div class="intelligence-card doc-card">
              <div class="intel-top"><span class="intel-label">Approved documentation & diagnostic tips</span><span class="match-chip">{best_article.score:.0%} relevance</span></div>
              <div class="intel-title">{escape(best_article.source_title)}</div>
              <div class="intel-copy">{escape(_plain_evidence(best_article.text))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    feedback_source = similar_cases[0] if similar_cases else articles[0] if articles else None
    if feedback_source and not result.refused:
        feedback_key = f"retrieval-feedback-{result.workflow_id}"
        if st.session_state.get(feedback_key):
            st.caption("Feedback recorded for the reviewed evaluation dataset.")
        else:
            st.caption("WAS THIS MATCH USEFUL?")
            if st.button("Useful match", key=f"useful-{result.workflow_id}", use_container_width=True):
                record_retrieval_feedback(
                    ticket.ticket_id, result.workflow_id, feedback_source.source_id, "useful"
                )
                st.session_state[feedback_key] = "useful"
                st.rerun()
            if st.button("Not relevant", key=f"irrelevant-{result.workflow_id}", use_container_width=True):
                record_retrieval_feedback(
                    ticket.ticket_id, result.workflow_id, feedback_source.source_id, "not_relevant"
                )
                st.session_state[feedback_key] = "not_relevant"
                st.rerun()

def render_response_workspace(ticket: ServiceTicket, result) -> None:
    st.markdown(
        '<div class="section-kicker assist-kicker">Employee response</div>'
        '<div class="section-title">Review and send the answer</div>',
        unsafe_allow_html=True,
    )
    if result.missing_information:
        with st.expander("Information still needed", expanded=False):
            for item in result.missing_information:
                st.markdown(f"- {item}")

    st.caption("FINAL RESPONSE TO THE EMPLOYEE · EDITABLE AND GROUNDED")
    draft = st.text_area(
        "Draft",
        value=result.grounded_reply,
        height=245,
        label_visibility="collapsed",
        key=f"draft-{result.workflow_id}",
    )

    # The approval belongs to the ticket, so it survives a classification update/rerun.
    approval_key = f"approval-{ticket.ticket_id}"
    decision = st.session_state.get(approval_key)
    if result.refused:
        st.markdown('<div class="control-box">Workflow stopped. Security review is mandatory; no customer reply can be approved.</div>', unsafe_allow_html=True)
    elif decision == "approved":
        st.markdown('<div class="success-box">Human checkpoint completed. You can now resolve the case and publish this reviewed solution to reusable case memory.</div>', unsafe_allow_html=True)
    elif decision == "revision_requested":
        st.markdown('<div class="control-box">Revision/escalation requested. The draft remains blocked from release.</div>', unsafe_allow_html=True)
    elif decision == "rejected":
        st.markdown('<div class="control-box">The suggested response was rejected. It cannot be released or added to reusable case memory.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="control-box"><strong>Approval required.</strong> {escape(result.human_review_reason)}</div>', unsafe_allow_html=True)

    if st.button("Approve draft", type="primary", use_container_width=True, disabled=result.refused):
        st.session_state[approval_key] = "approved"
        record_human_decision(result.workflow_id, ticket.ticket_id, "approved")
        update_ai_classification(
            ticket.ticket_id, result.category, result.priority, assigned_team=result.assigned_team
        )
        st.rerun()
    if decision == "approved" and ticket.status != "Resolved":
        if st.button("Resolve ticket + reuse verified solution", use_container_width=True):
            resolve_ticket(ticket.ticket_id, draft)
            record_human_decision(result.workflow_id, ticket.ticket_id, "resolved_and_published")
            run_ticket.clear()
            st.rerun()
    if st.button("Reject suggested response", use_container_width=True, disabled=result.refused):
        st.session_state[approval_key] = "rejected"
        record_human_decision(result.workflow_id, ticket.ticket_id, "rejected")
        st.rerun()
    if st.button("Escalate for specialist review", use_container_width=True):
        st.session_state[approval_key] = "revision_requested"
        record_human_decision(result.workflow_id, ticket.ticket_id, "revision_requested")
        st.rerun()
    default_team = result.assigned_team if result.assigned_team in SUPPORT_TEAMS else "Enterprise Service Desk"
    assigned_team = st.selectbox(
        "Reassign ticket",
        SUPPORT_TEAMS,
        index=SUPPORT_TEAMS.index(default_team),
        key=f"team-{ticket.ticket_id}",
    )
    if st.button("Confirm reassignment", use_container_width=True):
        reassign_ticket(ticket.ticket_id, assigned_team)
        record_human_decision(result.workflow_id, ticket.ticket_id, f"reassigned:{assigned_team}")
        run_ticket.clear()
        st.rerun()
    if st.button("Re-run agent workflow", use_container_width=True):
        run_ticket.clear()
        st.rerun()


def render_agent_trace(result) -> None:
    st.markdown(
        f'<div class="glass"><div class="section-kicker">Workflow {escape(result.workflow_id)}</div>'
        f'<div class="section-title">Bounded orchestration trace</div>'
        f'<div class="muted">State: {escape(result.workflow_status.replace("_", " ").title())} · '
        f'Quality: {result.quality_score:.0%} · Retrieval: {result.retrieval_confidence:.0%}</div></div>',
        unsafe_allow_html=True,
    )
    for index, step in enumerate(result.agent_trace, start=1):
        status_class = escape(step.status.lower())
        st.markdown(
            f"""
            <div class="agent-step">
              <div class="agent-num">{index}</div>
              <div><div class="agent-name">{escape(step.agent)}</div><div class="agent-role">{escape(step.role)}</div><div class="agent-decision">{escape(step.decision)}</div></div>
              <div><span class="agent-state {status_class}">{escape(step.status)}</span><div class="tiny" style="text-align:right;margin-top:.3rem">{step.latency_ms:.1f} ms</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="control-box" style="margin-top:1rem"><strong>Autonomy boundary:</strong> maximum six steps, no arbitrary tools, one approved knowledge domain, and no autonomous customer send.</div>',
        unsafe_allow_html=True,
    )


def render_evidence_controls(result) -> None:
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="section-kicker">Evidence</div><div class="section-title">Approved grounding</div>', unsafe_allow_html=True)
        st.caption("DEMO DISCLOSURE · The seeded article and case corpus is synthetic. User-published cases remain local to this PoC.")
        if result.citations:
            for source in result.citations:
                source_kind = "Human-verified resolved case" if source.startswith("Verified case ") else "Approved company knowledge article"
                st.markdown(
                    f'<div class="evidence"><span class="evidence-title">{escape(source)}</span><br><span class="tiny">{source_kind}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.warning("No knowledge source met the configured confidence threshold.")
        st.caption(result.confidence_note)
        st.progress(min(max(int(result.retrieval_confidence * 100), 0), 100), text="Top retrieval confidence")
        with st.expander("Browse the complete approved article catalog"):
            for article in get_approved_articles():
                st.markdown(f"**{article['article_id']} · {article['title']}**  \n{article['category']} · version {article['version']}")
    with right:
        st.markdown('<div class="section-kicker">Governance</div><div class="section-title">Release controls</div>', unsafe_allow_html=True)
        controls = [
            ("Input safety", "Passed" if not result.refused else "Blocked"),
            ("PII minimization", "Before cloud + logs"),
            ("Knowledge boundary", "Approved KB only"),
            ("Output quality", f"{result.quality_score:.0%}"),
            ("Human accountability", "Mandatory"),
        ]
        for name, value in controls:
            st.markdown(f"**{name}**  \n<span class='muted'>{value}</span>", unsafe_allow_html=True)
        if result.guardrail_notes:
            st.caption("WORKFLOW NOTES")
            for note in result.guardrail_notes:
                st.markdown(f"- {note}")


def render_activity(ticket: ServiceTicket) -> None:
    st.markdown('<div class="section-kicker">Audit trail</div><div class="section-title">Case activity</div>', unsafe_allow_html=True)
    for item in ticket.activity:
        st.markdown(
            f'<div class="activity"><strong>{escape(item.time_label)}</strong> · {escape(item.author)}<br>{escape(item.text)}</div>',
            unsafe_allow_html=True,
        )


def render_support_workspace_page() -> None:
    render_header()
    render_purpose()
    counts = database_counts()
    render_metrics(counts)
    confirmation = st.session_state.pop("submission_confirmation", None)
    if confirmation:
        ticket_id, assigned_team = confirmation
        st.success(f"{ticket_id} was submitted successfully and assigned to {assigned_team}.")

    if "selected_ticket_id" not in st.session_state:
        st.session_state["selected_ticket_id"] = "SD-1041"

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    tickets = list_tickets()
    navigation, workspace = st.columns([0.78, 3.22], gap="large")
    with navigation:
        _, selected_ticket_id = render_filters(tickets)

    ticket = get_ticket(selected_ticket_id)
    try:
        result = run_ticket(ticket.ticket_id, ticket.updated_at)
    except Exception as exc:
        st.error(f"The live LLM workflow could not complete: {exc}")
        st.info("No simulated recommendation was substituted. Check the model connection and retry.")
        return

    with workspace:
        work_tab, trace_tab, controls_tab, activity_tab = st.tabs(
            ["Decision workspace", "Agent orchestration", "Evidence & controls", "Case activity"]
        )
        with work_tab:
            ticket_col, copilot_col = st.columns([1.08, 0.92], gap="large")
            with ticket_col:
                render_ticket(ticket)
                render_response_workspace(ticket, result)
            with copilot_col:
                render_copilot(ticket, result)
        with trace_tab:
            render_agent_trace(result)
        with controls_tab:
            render_evidence_controls(result)
        with activity_tab:
            render_activity(ticket)

    st.markdown(
        f'<div class="footer-note">CURRENT PoC · Streamlit · SQLite persistence · {escape(result.raw_provider)} / {escape(settings.llm_model)} · TF-IDF RAG over approved articles + verified cases · privacy-safe JSONL telemetry &nbsp;&nbsp;|&nbsp;&nbsp; ROADMAP · enterprise SSO/RBAC · Jira/ITSM API · managed monitoring</div>',
        unsafe_allow_html=True,
    )


st.markdown(APP_CSS, unsafe_allow_html=True)
if copilot is None:
    setup_hint = (
        "LLM_PROVIDER=ollama\nOLLAMA_BASE_URL=http://localhost:11434/v1\n"
        "OLLAMA_MODEL=qwen2.5:0.5b-instruct"
        if settings.llm_provider == "ollama"
        else "LLM_PROVIDER=openai\nOPENAI_API_KEY=your-secret-key\n"
        "OPENAI_BASE_URL=https://api.openai.com/v1\nOPENAI_MODEL=your-model-id"
    )
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Secure model connection required</div>
          <div class="brand">Connect the <span class="accent-mint">live LLM</span></div>
          <div class="hero-sub">AegisDesk does not silently replace live AI with simulated answers. Start the configured local Ollama model or connect an approved cloud provider to activate cross-department triage and evidence-grounded drafting.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.error(llm_setup_error)
    st.code(setup_hint, language="text")
    st.caption("Save these values in a local .env file. The .env file is ignored by Git and must never be committed.")
    st.stop()

routes = ["Employee Help Portal", "Support Workspace"]
current_route = st.session_state.get("page_route", routes[0])
selected_route = st.radio(
    "Choose your view",
    routes,
    index=routes.index(current_route),
    horizontal=True,
)
if selected_route != current_route:
    st.session_state["page_route"] = selected_route
    st.rerun()

if current_route == "Employee Help Portal":
    render_employee_portal()
else:
    render_support_workspace_page()
