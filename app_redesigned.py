import os
import sqlite3
import json
# from datetime import datetime
import streamlit as st
import json
import csv
import io
import html
from datetime import datetime
from collections import Counter

import plotly.express as px
import plotly.graph_objects as go

from src.agent_engine import user_agent, enforcement_agent
from src.rag_engine import find_best_rule
from src.explanation_engine import generate_explanation

# ==============================
# SQLITE DATABASE INTEGRATION
# ==============================

DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "smartpark.db")


def init_db():
    """Create database and cases table if they do not exist."""
    os.makedirs(DB_FOLDER, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                payload TEXT NOT NULL
            )
        """)
        conn.commit()


def save_case(case):
    """Save a complete case as JSON in SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO cases (case_id, payload) VALUES (?, ?)",
            (
                case["case_id"],
                json.dumps(case, ensure_ascii=False)
            )
        )
        conn.commit()


def load_cases():
    """Load all cases, newest first."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT payload FROM cases ORDER BY id DESC"
        ).fetchall()

    return [json.loads(row[0]) for row in rows]
def clear_all_cases():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM cases")
    conn.commit()
    conn.close()


def get_next_case_id():
    """Generate the next unique case number."""
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM cases"
        ).fetchone()

    return f"CASE-{result[0]:03d}"


def get_total_cases():
    """Return total saved cases."""
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM cases"
        ).fetchone()

    return result[0]


# Initialize database when app starts
init_db()


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="SmartPark AI | Parking Intelligence",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# LOAD KNOWLEDGE BASE
# ==================================================

with open("data/parking_rules.json", "r", encoding="utf-8") as file:
    parking_rules = json.load(file)


# ==================================================
# SESSION STATE
# ==================================================
# Load saved cases from SQLite only on first app session
if "case_history" not in st.session_state:
    st.session_state.case_history = load_cases()

# if "latest_case" not in st.session_state:
#     st.session_state.latest_case = (
#         st.session_state.case_history[0]
#         if st.session_state.case_history else None
#     )

if "latest_case" not in st.session_state:
    st.session_state.latest_case = None

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Overview"

if "test_results" not in st.session_state:
    st.session_state.test_results = []


# ==================================================
# THEME AND ANIMATIONS
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(16,185,129,.10), transparent 28%),
        linear-gradient(135deg, #030605 0%, #07110d 55%, #020403 100%);
    color: #ecfdf5;
}

[data-testid="stHeader"] {
    background: rgba(3,6,5,.85);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050a08, #0b1711);
    border-right: 1px solid rgba(16,185,129,.25);
}

[data-testid="stSidebar"] * {
    color: #d1fae5;
}

h1, h2, h3 {
    color: #f0fdf4 !important;
}

p, label, li {
    color: #b7d6c5;
}

.hero {
    padding: 34px;
    border-radius: 24px;
    background: linear-gradient(120deg, #064e3b, #065f46, #022c22);
    border: 1px solid rgba(52,211,153,.4);
    box-shadow: 0 10px 40px rgba(16,185,129,.12);
    animation: fadeIn .8s ease;
    margin-bottom: 25px;
}

.hero-kicker {
    color: #6ee7b7;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-size: clamp(28px, 4vw, 43px);
    font-weight: 800;
    color: white;
    margin: 12px 0;
}

.hero-copy {
    color: #d1fae5;
    font-size: 15px;
}

.metric-card, .panel {
    padding: 21px;
    border-radius: 18px;
    background: linear-gradient(145deg, #101c16, #08110c);
    border: 1px solid rgba(52,211,153,.22);
    transition: all .3s ease;
    animation: fadeIn .7s ease;
}

.metric-card {
    min-height: 125px;
}

.metric-card:hover, .panel:hover {
    transform: translateY(-5px);
    border-color: #10b981;
    box-shadow: 0 10px 30px rgba(16,185,129,.13);
}

.metric-label {
    color: #86a997;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    color: #34d399;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.metric-note, .small-muted {
    color: #91ad9d;
    font-size: 13px;
}

.rule-id {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: rgba(16,185,129,.15);
    color: #6ee7b7;
    font-size: 12px;
    font-weight: 800;
}

div.stButton > button,
div.stDownloadButton > button {
    border-radius: 11px;
    border: 1px solid #10b981;
    background: linear-gradient(100deg, #047857, #10b981);
    color: white;
    font-weight: 700;
    min-height: 43px;
    transition: all .25s ease;
}

div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background: #059669;
    box-shadow: 0 0 18px rgba(16,185,129,.35);
    transform: translateY(-2px);
    color: white;
}

[data-testid="stMetric"] {
    background: #0c1711;
    border: 1px solid rgba(52,211,153,.2);
    border-radius: 15px;
    padding: 16px;
}

[data-testid="stExpander"] {
    background: #0b1510;
    border: 1px solid rgba(52,211,153,.2);
    border-radius: 13px;
}

.stTextArea textarea, .stTextInput input {
    background: #101c16 !important;
    color: white !important;
    border: 1px solid #176b4c !important;
    border-radius: 12px !important;
}

.stSelectbox div[data-baseweb="select"] {
    background: #101c16;
}

hr {
    border-color: rgba(52,211,153,.2);
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# REUSABLE HELPERS
# ==================================================

def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def make_chart_layout(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d1fae5"),
        margin=dict(l=15, r=15, t=45, b=15),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )
    return fig


def run_analysis(situation):
    """Run retrieval, explanation and both agents."""

    best_rule, score = find_best_rule(situation)

    if score < 0.30:
        return None, score

    explanation = generate_explanation(situation, best_rule)

    user_result = user_agent(best_rule)
    enforcement_result = enforcement_agent(best_rule)

    case = {
        # "case_id": f"CASE-{len(st.session_state.case_history) + 1:03d}",
        "case_id": get_next_case_id(),
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "situation": situation,
        "rule_id": best_rule["rule_id"],
        "violation": best_rule["title"],
        "severity": best_rule["severity"],
        "score": float(score),
        "description": best_rule["description"],
        "resolution": best_rule["resolution"],
        "explanation": explanation,
        "user_agent": user_result,
        "enforcement_agent": enforcement_result
    }

   
    save_case(case)

    # Update current Streamlit session
    st.session_state.case_history.insert(0, case)
    st.session_state.latest_case = case

    return case, score


def render_case_result(case):

    st.markdown("### 🚨 Detection Result")

    left, right = st.columns([1.35, 1])

    with left:
        st.markdown(
            f"""
            <div class="panel">
                <span class="rule-id">{html.escape(str(case['rule_id']))}</span>
                <h2>{html.escape(str(case['violation']))}</h2>
                <p class="small-muted">{html.escape(str(case['description']))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.metric("Severity", case["severity"])
        st.metric("Similarity Score", f"{case['score']:.3f}")

    st.markdown("#### 🧭 Suggested Resolution")

    for step in case["resolution"]:
        st.markdown(f"- {step}")

    st.markdown("#### 💡 AI Explanation")
    st.info(case["explanation"])

    with st.expander("🔎 Retrieval Evidence"):
        st.write("User description:", case["situation"])
        st.write("Retrieved rule:", case["rule_id"], "-", case["violation"])
        st.write("Similarity score:", round(case["score"], 3))
        st.caption(
            "Similarity is a model score, not proof that a legal violation occurred."
        )

    with st.expander("🤝 Multi-Agent Analysis"):

        agent_col1, agent_col2 = st.columns(2)

        with agent_col1:
            st.markdown("**👤 User Agent**")
            st.write(case["user_agent"].get("finding", "No finding available."))

            for item in case["user_agent"].get("suggestions", []):
                st.markdown(f"- {item}")

        with agent_col2:
            st.markdown("**🛡️ Enforcement Agent**")
            st.write(
                case["enforcement_agent"].get(
                    "finding", "No finding available."
                )
            )

            st.write(
                "Severity:",
                case["enforcement_agent"].get("severity", case["severity"])
            )

            for item in case["enforcement_agent"].get("checks", []):
                st.markdown(f"- {item}")


def history_csv(history):

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Case ID",
        "Timestamp",
        "Situation",
        "Rule ID",
        "Violation",
        "Severity",
        "Similarity Score"
    ])

    for case in history:
        writer.writerow([
            case["case_id"],
            case["timestamp"],
            case["situation"],
            case["rule_id"],
            case["violation"],
            case["severity"],
            round(case["score"], 4)
        ])

    return output.getvalue()


def case_report(case):

    lines = [
        "SMARTPARK AI - CASE REPORT",
        "=" * 42,
        f"Case ID: {case['case_id']}",
        f"Date: {case['timestamp']}",
        "",
        "PARKING SITUATION",
        case["situation"],
        "",
        "DETECTED VIOLATION",
        case["violation"],
        f"Rule ID: {case['rule_id']}",
        f"Severity: {case['severity']}",
        f"Similarity score: {case['score']:.3f}",
        "",
        "DESCRIPTION",
        case["description"],
        "",
        "SUGGESTED RESOLUTION"
    ]

    lines.extend(f"- {step}" for step in case["resolution"])

    lines.extend([
        "",
        "AI EXPLANATION",
        str(case["explanation"]),
        "",
        "USER AGENT",
        str(case["user_agent"]),
        "",
        "ENFORCEMENT AGENT",
        str(case["enforcement_agent"]),
        "",
        "This is an academic demonstration report, not an official legal decision."
    ])

    return "\n".join(lines)


def render_parking_layout():

    st.markdown("### 🅿️ Parking Layout")
    st.caption(
        "Illustrative demo layout only — these are not live sensor readings."
    )

    slots = [
        ("A1", "Available"),
        ("A2", "Occupied"),
        ("A3", "Available"),
        ("A4", "Occupied"),
        ("A5", "Available"),
        ("B1", "Occupied"),
        ("B2", "Available"),
        ("B3", "Available"),
        ("B4", "Occupied"),
        ("B5", "Available"),
        ("C1", "Available"),
        ("C2", "Occupied"),
        ("C3", "Available"),
        ("C4", "Available"),
        ("C5", "Occupied")
    ]

    for start in range(0, len(slots), 5):

        cols = st.columns(5)

        for col, (slot, status) in zip(cols, slots[start:start + 5]):

            if status == "Available":
                background = "#064e3b"
                border = "#34d399"
                symbol = "✓"
            else:
                background = "#78350f"
                border = "#fbbf24"
                symbol = "●"

            with col:
                st.markdown(
                    f"""
                    <div style="
                        background:{background};
                        border:1px solid {border};
                        border-radius:12px;
                        padding:16px 5px;
                        text-align:center;
                        margin-bottom:10px;
                    ">
                        <div style="color:white;font-size:20px;font-weight:800;">
                            {slot}
                        </div>
                        <div style="color:white;font-size:13px;">
                            {symbol} {status}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown(
        "🟢 Available &nbsp;&nbsp;&nbsp; 🟠 Occupied",
        unsafe_allow_html=True
    )
def go_to_detector():
    st.session_state.selected_page = "Violation Detector"

def go_to_rules():
    st.session_state.selected_page = "Parking Rules"

def go_to_analytics():
    st.session_state.selected_page = "Analytics"

# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:

    st.markdown("# 🚘 SmartPark AI")
    st.caption("PARKING INTELLIGENCE PLATFORM")

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Violation Detector",
            "Parking Rules",
            "Case History",
            "Analytics",
            "AI Agents",
            "System Testing",
            "About Project"
        ],
        key="selected_page"
    )

    st.markdown("---")
    st.markdown("**SYSTEM STATUS**")

    st.success("Knowledge base loaded")

    st.caption(f"{len(parking_rules)} parking rules available")
    st.caption("Model: all-MiniLM-L6-v2")

    st.markdown("---")
    st.caption("Academic demonstration system")


# ==================================================
# PAGE 1: OVERVIEW
# ==================================================

if page == "Overview":

    st.markdown("""
    <div class="hero">
        <div class="hero-kicker">AI-powered parking compliance</div>
        <div class="hero-title">
            Smarter Parking Decisions.<br>
            Clearer Rule Guidance.
        </div>
        <div class="hero-copy">
            An intelligent assistant that interprets parking situations,
            retrieves relevant rules and provides explainable resolution guidance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.case_history

    total_cases = len(history)

    high_cases = sum(
        1 for c in history if c["severity"].lower() == "high"
    )

    avg_score = (
        sum(c["score"] for c in history) / total_cases
        if total_cases else 0
    )

    available_rules = len(parking_rules)

    cols = st.columns(4)

    with cols[0]:
        metric_card("Knowledge Base", available_rules, "Structured parking rules")

    with cols[1]:
        metric_card("Cases Analyzed", total_cases, "Current session")

    with cols[2]:
        metric_card("High Severity", high_cases, "High severity cases")

    with cols[3]:
        metric_card(
            "Average Match",
            f"{avg_score:.2f}" if total_cases else "—",
            "Similarity score"
        )

    st.markdown("### ⚡ Quick Actions")

    st.button(
    "Open Violation Detector",
    use_container_width=True,
    on_click=go_to_detector
    )

    st.button(
        "Explore Parking Rules",
        use_container_width=True,
        on_click=go_to_rules
    )

    st.button(
        "Open Analytics",
        use_container_width=True,
        on_click=go_to_analytics
    )

    # INTERACTIVE CHARTS

    st.markdown("### 📊 Dashboard Analytics")

    if history:

        severity_counts = Counter(c["severity"] for c in history)
        violation_counts = Counter(c["violation"] for c in history)

        chart1, chart2 = st.columns(2)

        with chart1:

            st.markdown("#### Severity Distribution")

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=list(severity_counts.keys()),
                        values=list(severity_counts.values()),
                        hole=0.62,
                        textinfo="label+percent"
                    )
                ]
            )

            fig.update_layout(
                title="Cases by severity",
                showlegend=True
            )

            st.plotly_chart(
                make_chart_layout(fig),
                use_container_width=True
            )

        with chart2:

            st.markdown("#### Detected Violations")

            fig = px.bar(
                x=list(violation_counts.values()),
                y=list(violation_counts.keys()),
                orientation="h",
                labels={"x": "Cases", "y": "Violation"},
                title="Violation frequency"
            )

            fig.update_traces(
                marker_color="#10b981",
                marker_line_color="#6ee7b7",
                marker_line_width=1
            )

            st.plotly_chart(
                make_chart_layout(fig),
                use_container_width=True
            )

    else:
        st.info(
            "Analyze a parking situation to populate your interactive dashboard charts."
        )

    st.markdown("---")

    # DEMO PARKING LAYOUT

    render_parking_layout()

    st.markdown("---")

    # RECENT ACTIVITY

    st.markdown("### 🕘 Recent Activity")

    if history:

        for case in history[:5]:

            st.markdown(
                f"- **{case['case_id']} · {case['violation']}** "
                f"— {case['severity']} · {case['timestamp']}"
            )

    else:
        st.info("No cases analyzed yet. Start with Violation Detector.")


# ==================================================
# PAGE 2: VIOLATION DETECTOR
# ==================================================

elif page == "Violation Detector":

    st.markdown("## 🔍 Violation Detector")

    st.caption(
        "Describe the parking situation in everyday language."
    )

    with st.form("detector_form"):

        situation = st.text_area(
            "Parking Situation",
            placeholder=(
                "Example: My car is parked in front of a garage "
                "and the owner cannot take their vehicle out."
            ),
            height=135
        )

        submitted = st.form_submit_button(
            "🚀 Analyze Parking Situation",
            use_container_width=True
        )

    if submitted:

        if not situation.strip():

            st.warning("Please enter a parking situation first.")

        else:

            with st.spinner(
                "AI is analyzing the situation and retrieving a relevant rule..."
            ):

                try:

                    case, score = run_analysis(situation.strip())

                    if case is None:

                        st.warning(
                            "No sufficiently relevant rule was found."
                        )

                        st.info(
                            "Try adding more details about the location, "
                            "restriction or obstruction."
                        )

                    else:

                        st.success("Analysis completed successfully!")

                        render_case_result(case)

                        st.download_button(
                            "⬇️ Download This Case Report",
                            data=case_report(case),
                            file_name=f"{case['case_id']}_report.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                except Exception as error:

                    st.error(
                        f"Analysis could not be completed: {error}"
                    )

    elif st.session_state.latest_case:

        st.markdown("### Latest Analyzed Case")

        render_case_result(st.session_state.latest_case)


# ==================================================
# PAGE 3: PARKING RULES
# ==================================================

elif page == "Parking Rules":

    st.markdown("## 📚 Parking Rules Library")

    st.caption(
        "Explore the rules stored in the JSON knowledge base."
    )

    search_text = st.text_input(
        "Search Rules",
        placeholder="Search by title, keyword or rule ID..."
    )

    severity_filter = st.multiselect(
        "Filter by Severity",
        options=sorted(
            set(rule["severity"] for rule in parking_rules)
        ),
        default=sorted(
            set(rule["severity"] for rule in parking_rules)
        )
    )

    filtered_rules = []

    for rule in parking_rules:

        searchable = " ".join([
            rule["rule_id"],
            rule["title"],
            rule["description"],
            " ".join(rule["keywords"])
        ]).lower()

        if (
            search_text.lower() in searchable
            and rule["severity"] in severity_filter
        ):
            filtered_rules.append(rule)

    st.caption(
        f"Showing {len(filtered_rules)} of {len(parking_rules)} rules"
    )

    for rule in filtered_rules:

        with st.expander(
            f"{rule['rule_id']} · {rule['title']} · {rule['severity']}"
        ):

            st.write(rule["description"])

            st.markdown("**Keywords**")
            st.write(", ".join(rule["keywords"]))

            st.markdown("**Possible Resolution Steps**")

            for step in rule["resolution"]:
                st.markdown(f"- {step}")


# ==================================================
# PAGE 4: CASE HISTORY
# ==================================================

elif page == "Case History":

    st.title("📁 Case History")
    st.write("Search, filter and manage your saved parking violation cases.")

    # Always load latest records from SQLite
    st.session_state.case_history = load_cases()

    history = st.session_state.case_history

    # SEARCH AND FILTER
    st.subheader("Search & Filter Cases")

    search_text = st.text_input(
        "Search by Case ID or Violation",
        placeholder="Example: CASE-001 or No-Parking"
    )

    severity_options = ["All", "High", "Medium", "Low"]

    selected_severity = st.selectbox(
        "Filter by Severity",
        severity_options
    )

    filtered_history = []

    for case in history:

        matches_search = (
            search_text.lower() in case.get("case_id", "").lower()
            or search_text.lower() in case.get("violation", "").lower()
        )

        matches_severity = (
            selected_severity == "All"
            or case.get("severity", "").lower()
            == selected_severity.lower()
        )

        if matches_search and matches_severity:
            filtered_history.append(case)

    st.caption(
        f"Showing {len(filtered_history)} of {len(history)} cases"
    )

    st.divider()

    # DISPLAY FILTERED CASES
    st.subheader("Saved Violation Records")

    if filtered_history:

        for case in filtered_history:

            with st.expander(
                f"{case.get('case_id', 'N/A')} | "
                f"{case.get('violation', 'Unknown')} | "
                f"{case.get('severity', 'N/A')}"
            ):

                st.write("**Timestamp:**", case.get("timestamp", "N/A"))
                st.write("**Situation:**", case.get("situation", "N/A"))
                st.write("**Rule ID:**", case.get("rule_id", "N/A"))
                st.write("**Severity:**", case.get("severity", "N/A"))
                st.write(
                    "**Similarity Score:**",
                    f"{float(case.get('score', 0)):.3f}"
                )

                st.write("**Description:**", case.get("description", "N/A"))
                st.write("**Resolution:**", case.get("resolution", "N/A"))

                report_text = case_report(case)

                st.download_button(
                    "📄 Download Case Report",
                    data=report_text,
                    file_name=f"{case.get('case_id', 'case')}_report.txt",
                    mime="text/plain",
                    key=f"report_{case.get('case_id')}"
                )

    else:
        st.info("No cases found matching your search or filter.")

    st.divider()

    # CSV EXPORT - FILTERED RECORDS ONLY
    st.subheader("Export Case History")

    if filtered_history:

        csv_data = history_csv(filtered_history)

        st.download_button(
            "📥 Download Filtered CSV",
            data=csv_data,
            file_name="smartpark_filtered_history.csv",
            mime="text/csv",
            key="filtered_history_csv"
        )

    else:
        st.warning("No records available to export.")

    st.divider()

    # CLEAR HISTORY
    st.subheader("Manage Case History")

    confirm_clear = st.checkbox(
        "I understand that all saved cases will be permanently deleted",
        key="confirm_clear_history"
    )

    if st.button(
        "🗑️ Clear All Cases",
        disabled=not confirm_clear,
        key="clear_all_cases_btn"
    ):

        clear_all_cases()

        st.session_state.case_history = []
        st.session_state.latest_case = None

        st.success("All case records deleted successfully!")
        st.rerun()


elif page == "Analytics":

    st.title("📊 SmartPark AI Analytics")
    st.write("Real-time analytics based on saved SQLite case records.")

    # Load records directly from database
    analytics_history = load_cases()

    total_cases = len(analytics_history)

    high_cases = sum(
        1 for c in analytics_history
        if c.get("severity", "").lower() == "high"
    )

    medium_cases = sum(
        1 for c in analytics_history
        if c.get("severity", "").lower() == "medium"
    )

    low_cases = sum(
        1 for c in analytics_history
        if c.get("severity", "").lower() == "low"
    )

    average_score = (
        sum(float(c.get("score", 0)) for c in analytics_history)
        / total_cases if total_cases else 0
    )

    # METRIC CARDS
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cases", total_cases)
    col2.metric("High Severity", high_cases)
    col3.metric("Medium Severity", medium_cases)
    col4.metric("Average Score", f"{average_score:.3f}")

    st.divider()

    if analytics_history:

        # VIOLATION DISTRIBUTION
        st.subheader("🚨 Violation Distribution")

        violation_counts = Counter(
            c.get("violation", "Unknown")
            for c in analytics_history
        )

        violation_df = {
            "Violation": list(violation_counts.keys()),
            "Cases": list(violation_counts.values())
        }

        fig1 = px.bar(
            violation_df,
            x="Violation",
            y="Cases",
            title="Cases by Violation Type",
            template="plotly_dark",
            color="Cases"
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # SEVERITY DISTRIBUTION
        st.subheader("⚠️ Severity Distribution")

        severity_data = {
            "Severity": ["High", "Medium", "Low"],
            "Cases": [high_cases, medium_cases, low_cases]
        }

        fig2 = px.pie(
            severity_data,
            names="Severity",
            values="Cases",
            title="Violation Severity Breakdown",
            hole=0.45,
            template="plotly_dark"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # RULE-WISE ANALYTICS
        st.subheader("📚 Parking Rule Analytics")

        rule_counts = Counter(
            c.get("rule_id", "Unknown")
            for c in analytics_history
        )

        rule_data = {
            "Rule ID": list(rule_counts.keys()),
            "Cases": list(rule_counts.values())
        }

        fig3 = px.bar(
            rule_data,
            x="Rule ID",
            y="Cases",
            title="Cases Detected Under Each Rule",
            template="plotly_dark"
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # RECENT CASES
        st.subheader("🕒 Recent Case Activity")

        for case in analytics_history[:5]:
            st.write(
                f"**{case.get('case_id', 'N/A')}** | "
                f"{case.get('violation', 'Unknown')} | "
                f"{case.get('severity', 'N/A')} | "
                f"{case.get('timestamp', 'N/A')}"
            )

        st.divider()

        # EXPORT
        st.subheader("📥 Export Analytics Data")

        analytics_csv = history_csv(analytics_history)

        st.download_button(
            "Download Complete Analytics CSV",
            data=analytics_csv,
            file_name="smartpark_analytics.csv",
            mime="text/csv",
            key="analytics_export"
        )

    else:
        st.info("No saved cases available. Analyze a parking situation first.")



# ==================================================
# PAGE 6: AI AGENTS
# ==================================================

elif page == "AI Agents":

    st.markdown("## 🤖 Multi-Agent System")

    st.caption(
        "Two specialized agents contribute different perspectives."
    )

    agent1, agent2 = st.columns(2)

    with agent1:

        st.markdown("""
        <div class="panel">
            <h3>👤 User Agent</h3>
            <p class="small-muted">Focus: User Guidance</p>
            <p>
                Reviews the retrieved parking rule and presents
                practical next steps for the user.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with agent2:

        st.markdown("""
        <div class="panel">
            <h3>🛡️ Enforcement Agent</h3>
            <p class="small-muted">Focus: Compliance Perspective</p>
            <p>
                Reviews the rule's severity and presents
                relevant compliance checks.
            </p>
        </div>
        """, unsafe_allow_html=True)
        # Load most recent case from SQLite
    database_cases = load_cases()

    if database_cases:
        st.session_state.latest_case = database_cases[0]

    if st.session_state.latest_case:

        case = st.session_state.latest_case

        st.markdown("### Latest Agent Output")

        x, y = st.columns(2)

        with x:

            st.markdown("**User Agent Finding**")

            st.write(
                case["user_agent"].get("finding", "Not available")
            )

            st.markdown("**Suggested Actions**")

            for item in case["user_agent"].get("suggestions", []):
                st.markdown(f"- {item}")

        with y:

            st.markdown("**Enforcement Agent Finding**")

            st.write(
                case["enforcement_agent"].get(
                    "finding", "Not available"
                )
            )

            st.markdown("**Compliance Checks**")

            for item in case["enforcement_agent"].get("checks", []):
                st.markdown(f"- {item}")

    else:

        st.info(
            "Run a violation analysis to see both agents working together."
        )


# ==================================================
# PAGE 7: SYSTEM TESTING
# ==================================================


elif page == "System Testing":

    st.title("🧪 SmartPark AI - System Testing")
    st.write(
        "Validate AI detection, knowledge base, agents, "
        "SQLite persistence and application functionality."
    )

    st.divider()

    # ==========================================
    # 1. TEST CONFIGURATION
    # ==========================================

    test_results = []

    def add_test(name, status, details):
        test_results.append({
            "Test": name,
            "Status": status,
            "Details": str(details)
        })

    # ==========================================
    # 2. KNOWLEDGE BASE TEST
    # ==========================================

    st.subheader("📚 1. Knowledge Base Testing")

    try:
        with open("data/parking_rules.json", "r", encoding="utf-8") as file:
            rules = json.load(file)

        if len(rules) >= 7:
            add_test(
                "Parking Rules Loading",
                "PASS",
                f"{len(rules)} rules loaded successfully"
            )
            st.success(f"Knowledge Base Loaded: {len(rules)} rules")
        else:
            add_test(
                "Parking Rules Loading",
                "FAIL",
                f"Only {len(rules)} rules found"
            )
            st.error("Expected at least 7 parking rules.")

    except Exception as e:
        rules = []
        add_test("Parking Rules Loading", "FAIL", e)
        st.error(f"Knowledge Base Error: {e}")

    st.divider()

    # ==========================================
    # 3. AI / RAG ENGINE TEST
    # ==========================================

    st.subheader("🧠 2. AI Violation Detection Testing")

    test_inputs = [
        "A car is parked in a no parking zone.",
        "A vehicle is blocking the hospital emergency entrance.",
        "A car is parked in a disabled parking space without permission.",
        "A vehicle has exceeded the allowed parking time.",
        "A car is parked in the wrong traffic direction.",
        "A vehicle is double parked and blocking traffic.",
        "A car is blocking a residential driveway."
    ]

    if rules:
        for i, situation in enumerate(test_inputs, start=1):

            try:
                best_rule, score = find_best_rule(situation)

                if best_rule and score >= 0.30:
                    add_test(
                        f"AI Detection Test {i}",
                        "PASS",
                        f"{best_rule.get('title', 'Unknown')} | Score: {score:.3f}"
                    )
                else:
                    add_test(
                        f"AI Detection Test {i}",
                        "FAIL",
                        f"No suitable rule found | Score: {score:.3f}"
                    )

            except Exception as e:
                add_test(
                    f"AI Detection Test {i}",
                    "FAIL",
                    e
                )

        st.success("AI detection test cases executed.")

    else:
        st.warning("AI detection tests skipped because rules could not load.")

    st.divider()

    # ==========================================
    # 4. AI AGENTS TEST
    # ==========================================

    st.subheader("🤖 3. Multi-Agent System Testing")

    if rules:

        try:
            sample_rule = rules[0]

            user_result = user_agent(sample_rule)

            if user_result:
                add_test(
                    "User Agent",
                    "PASS",
                    "User Agent generated output"
                )
                st.success("User Agent Working")
            else:
                add_test(
                    "User Agent",
                    "FAIL",
                    "Empty agent response"
                )

        except Exception as e:
            add_test("User Agent", "FAIL", e)

        try:
            sample_rule = rules[0]

            enforcement_result = enforcement_agent(sample_rule)

            if enforcement_result:
                add_test(
                    "Enforcement Agent",
                    "PASS",
                    "Enforcement Agent generated output"
                )
                st.success("Enforcement Agent Working")
            else:
                add_test(
                    "Enforcement Agent",
                    "FAIL",
                    "Empty agent response"
                )

        except Exception as e:
            add_test("Enforcement Agent", "FAIL", e)

    st.divider()

    # ==========================================
    # 5. EXPLANATION ENGINE TEST
    # ==========================================

    st.subheader("💡 4. Explanation Engine Testing")

    if rules:

        try:
            sample_explanation = generate_explanation(
                "A vehicle is parked in a restricted parking area.",
                rules[0]
            )

            if sample_explanation:
                add_test(
                    "Explanation Engine",
                    "PASS",
                    "Explanation generated successfully"
                )
                st.success("Explanation Engine Working")
            else:
                add_test(
                    "Explanation Engine",
                    "FAIL",
                    "Empty explanation"
                )

        except Exception as e:
            add_test("Explanation Engine", "FAIL", e)

    st.divider()

    # ==========================================
    # 6. SQLITE DATABASE TEST
    # ==========================================

    st.subheader("🗄️ 5. SQLite Database Testing")

    try:
        init_db()

        db_cases = load_cases()

        add_test(
            "SQLite Connection",
            "PASS",
            "Database initialized and connected"
        )

        add_test(
            "Database Case Loading",
            "PASS",
            f"{len(db_cases)} saved records loaded"
        )

        st.success("SQLite Database Connected Successfully")

        col1, col2 = st.columns(2)

        col1.metric("Persisted Cases", len(db_cases))
        col2.metric(
            "Database File",
            "Available" if os.path.exists(DB_PATH) else "Missing"
        )

        if os.path.exists(DB_PATH):
            add_test(
                "Database File",
                "PASS",
                "SQLite database file exists"
            )
        else:
            add_test(
                "Database File",
                "FAIL",
                "Database file not found"
            )

    except Exception as e:
        add_test("SQLite Database", "FAIL", e)
        st.error(f"Database Test Failed: {e}")

    st.divider()

    # ==========================================
    # 7. CASE HISTORY TEST
    # ==========================================

    st.subheader("📁 6. Case History Testing")

    try:
        history_records = load_cases()

        add_test(
            "Case History Loading",
            "PASS",
            f"{len(history_records)} cases loaded"
        )

        if history_records:
            st.success(
                f"{len(history_records)} saved cases available."
            )
        else:
            st.info("Database is connected, but no cases are saved.")

    except Exception as e:
        add_test("Case History Loading", "FAIL", e)

    st.divider()

    # ==========================================
    # 8. FINAL TEST SUMMARY
    # ==========================================

    st.subheader("📊 7. Final Test Results")

    total_tests = len(test_results)

    passed_tests = sum(
        1 for result in test_results
        if result["Status"] == "PASS"
    )

    failed_tests = total_tests - passed_tests

    success_rate = (
        (passed_tests / total_tests) * 100
        if total_tests else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", total_tests)
    col2.metric("Passed", passed_tests)
    col3.metric("Failed", failed_tests)
    col4.metric("Success Rate", f"{success_rate:.1f}%")

    st.progress(success_rate / 100)

    if failed_tests == 0 and total_tests > 0:
        st.success("All executed system tests passed!")
    else:
        st.warning("Some tests failed. Check the test report below.")

    st.divider()

    # ==========================================
    # 9. DETAILED TEST REPORT
    # ==========================================

    st.subheader("📋 Detailed Test Report")

    if test_results:

        for result in test_results:

            if result["Status"] == "PASS":
                st.success(
                    f"✅ {result['Test']} — {result['Details']}"
                )
            else:
                st.error(
                    f"❌ {result['Test']} — {result['Details']}"
                )

        # CSV EXPORT
        import pandas as pd

        test_df = pd.DataFrame(test_results)

        st.download_button(
            "📥 Download System Test Report",
            data=test_df.to_csv(index=False).encode("utf-8"),
            file_name="smartpark_system_test_report.csv",
            mime="text/csv",
            key="system_test_report_download"
        )

    else:
        st.info("No test results available.")



# ==================================================
# PAGE 8: ABOUT PROJECT
# ==================================================

elif page == "About Project":

    st.markdown("## ℹ️ About SmartPark AI")

    st.markdown("""
    <div class="panel">
        <h3>Project Overview</h3>
        <p>
            SmartPark AI is an academic demonstration of an
            AI-assisted parking rule retrieval system.
            It accepts a natural-language description,
            searches a predefined parking knowledge base
            and presents possible resolution guidance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Technology Stack")

    tech_cols = st.columns(4)

    tech_items = [
        ("Python", "Core Programming"),
        ("Streamlit", "Interactive Interface"),
        ("MiniLM", "Text Embeddings"),
        ("JSON", "Parking Knowledge Base")
    ]

    for col, (name, desc) in zip(tech_cols, tech_items):

        with col:
            metric_card(name, "✓", desc)

    st.markdown("### How the System Works")

    st.markdown("""
    1. **User Input:** A user describes a parking situation.
    2. **Retrieval:** The RAG engine compares the input with stored parking rules.
    3. **Rule Selection:** Keyword matching and semantic similarity help select a relevant rule.
    4. **Explanation:** The explanation engine provides a readable explanation.
    5. **Multi-Agent Analysis:** User and Enforcement agents provide different perspectives.
    6. **Output:** The interface displays the detected rule and possible resolution steps.
    """)

    st.markdown("### Project Capabilities")

    features = [
        "Semantic parking rule retrieval",
        "Explainable AI guidance",
        "Multi-agent analysis",
        "Violation classification",
        "Case history and reports",
        "Interactive analytics",
        "Automated system testing"
    ]

    for feature in features:
        st.markdown(f"✓ {feature}")

    st.warning(
        "This is a demonstration assistant, not an official legal decision system. "
        "Actual parking rules and enforcement procedures depend on the local authority."
    )



# ==================================================
# FOOTER
# ==================================================


# GLOBAL FOOTER

st.markdown("""
<div style="
    background: rgba(30, 35, 40, 0.7);
    padding: 22px;
    border-radius: 12px;
    text-align: center;
    margin-top: 30px;
">
    <p style="font-weight: bold; margin-bottom: 8px;">
        SMARTPARK AI • AI + RAG + MULTI-AGENT PARKING ASSISTANT
    </p>
    <p style="margin: 0; color: #b0b0b0;">
        Intelligent Parking Compliance Demonstration
    </p>
</div>
""", unsafe_allow_html=True)
