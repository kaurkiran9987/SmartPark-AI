import streamlit as st
import json
from src.agent_engine import user_agent, enforcement_agent
from src.rag_engine import find_best_rule
from src.explanation_engine import generate_explanation


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Smart Parking Violation Assistant",
    page_icon="🚗",
    layout="wide"
)


# ==================================================
# LOAD PARKING RULES
# ==================================================

with open("data/parking_rules.json", "r") as file:
    parking_rules = json.load(file)


# ==================================================
# TITLE
# ==================================================

st.title("🚗 AI-Based Smart Parking Violation Assistant")
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fb;
    }

    .stButton > button {
        background-color: #1769aa;
        color: white;
        border-radius: 8px;
        height: 45px;
        font-weight: bold;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #0d4778;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.caption("SMART PARKING • AI • RAG • MULTI-AGENT SYSTEM")

st.write(
    "An intelligent assistant that helps users understand "
    "possible parking violations and available resolution steps."
)
# DASHBOARD METRICS

col1, col2, col3, col4 = st.columns(4)

col1.metric("📚 Total Rules", len(parking_rules))
col2.metric("🧠 AI Model", "MiniLM")
col3.metric("🔎 Retrieval", "Semantic")
col4.metric("🤖 Agents", "2")

# st.divider()
st.divider()


# ==================================================
# USER INPUT
# ==================================================

st.subheader("📝 Describe Your Parking Situation")

situation = st.text_area(
    "Tell us what happened:",
    placeholder=(
        "Example: I parked my car where emergency vehicles "
        "need access."
    )
)


# ==================================================
# ANALYZE BUTTON
# ==================================================

if st.button("🔍 Analyze Violation"):

    if situation.strip() == "":
        st.warning("Please describe your parking situation.")

    else:

        # ==========================================
        # RAG RETRIEVAL
        # ==========================================

        best_rule, score = find_best_rule(situation)
   
        # ==========================================
        # UNKNOWN SITUATION DETECTION
        # ==========================================

        if score < 0.30:

            st.warning(
                "⚠️ No relevant parking rule found!"
            )

            st.info(
                "Your description does not sufficiently match "
                "any parking rule in our knowledge base."
            )

            st.write(
                "Please provide more details about the parking "
                "location, restriction or violation."
            )

            st.stop()

        # ==========================================
        # DETECTED VIOLATION
        # ==========================================

        st.subheader("🚨 Detected Violation")

        st.write(
            best_rule["title"]
        )


        # ==========================================
        # SEVERITY
        # ==========================================

        st.subheader("⚠️ Severity")

        st.write(
            best_rule["severity"]
        )


        # ==========================================
        # APPLICABLE RULE
        # ==========================================

        st.subheader("📖 Applicable Parking Rule")

        st.write(
            best_rule["description"]
        )


        # ==========================================
        # RETRIEVAL EVIDENCE
        # ==========================================

        st.subheader("🔎 Why Was This Rule Selected?")

        st.write(
            "The system compared your parking situation "
            "with all available parking rules using "
            "semantic embeddings."
        )

        st.write(
            f"Best Matching Rule: "
            f"{best_rule['rule_id']} - {best_rule['title']}"
        )

        st.write(
        f"Similarity Score: {score:.3f}"
        )

        # Explain similarity score
        if score >= 0.70:
            match_level = "Strong semantic match"
        elif score >= 0.50:
            match_level = "Moderate semantic match"
        else:
            match_level = "Weak semantic match"

        st.write(
            f"Match Interpretation: {match_level}"
        )

        st.write(
            "This rule was selected because it had the "
            "highest semantic similarity with your parking situation."
        )
        with st.expander("🔍 View Retrieval Details"):

            st.write("User Input:")
            st.write(situation)

            st.write("Retrieved Rule:")
            st.write(
                f"{best_rule['rule_id']} - {best_rule['title']}"
            )

            st.write("Rule Keywords:")
            st.write(
                ", ".join(best_rule["keywords"])
            )

            st.write("Why it matched:")
            st.write(
                "The embedding model compared the meaning of the "
                "user's description with the stored parking rules "
                "and selected the rule with the highest similarity."
            )


        # ==========================================
        # RESOLUTION
        # ==========================================

        st.subheader("✅ Possible Resolution Steps")

        for step in best_rule["resolution"]:

            st.write(
                "➡️",
                step
            )


        # ==========================================
        # GENERATION
        # ==========================================

        st.subheader("🤖 AI-Generated Explanation")

        explanation = generate_explanation(
            situation,
            best_rule
        )

        st.info(explanation)
        
        # MULTI AGENT SYSTEM

        st.divider()
        st.header("🤝 Multi-Agent Analysis")

        # Execute agents
        user_result = user_agent(best_rule)
        enforcement_result = enforcement_agent(best_rule)


        # USER AGENT
        st.subheader("👤 User Agent")

        st.write(user_result["finding"])

        st.markdown("**Suggested Actions:**")

        for action in user_result["suggestions"]:
            st.write("➡️", action)


        # ENFORCEMENT AGENT
        st.subheader("🛡️ Enforcement Agent")

        st.write(enforcement_result["finding"])

        st.write("Severity:", enforcement_result["severity"])

        st.markdown("**Compliance Checks:**")

        for check in enforcement_result["checks"]:
            st.write("➡️", check)

                # ==========================================
        # AGENT COORDINATION
        # ==========================================

        st.divider()
        st.subheader("🔄 Agent Coordination")

        st.write(
            "The User Agent and Enforcement Agent have completed "
            "their individual analysis. Their findings are combined below."
        )

        st.markdown("### 📋 Combined Agent Report")

        st.write("**Parking Issue:**", best_rule["title"])

        st.write("**Rule ID:**", best_rule["rule_id"])

        st.write("**Severity:**", enforcement_result["severity"])

        st.markdown("**User Agent Recommendation:**")

        for action in user_result["suggestions"]:
            st.write("➡️", action)

        st.markdown("**Enforcement Agent Review:**")

        for check in enforcement_result["checks"]:
            st.write("➡️", check)

        st.success("Combined agent report generated successfully.")

        
        
        


        # ==========================================
        # HOW RAG WORKS
        # ==========================================

        st.subheader("🔎 How the AI Retrieved This Rule")

        st.write(
            "The system converted your parking situation "
            "and the parking rules into numerical embeddings. "
            "It then compared their semantic similarity and "
            "selected the most relevant parking rule."
        )


# ==================================================
# KNOWLEDGE BASE INFORMATION
# ==================================================

st.divider()

st.caption(
    f"Parking Knowledge Base: {len(parking_rules)} rules loaded"
)

st.caption(
    "Demo system. Actual parking rules and procedures "
    "depend on the applicable local authority."
)

# ==========================================
# AUTOMATED TESTING MODULE
# ==========================================

st.divider()
st.header("🧪 System Testing")

st.write(
    "Test the parking assistant using predefined situations "
    "and check which parking rule the retrieval system selects."
)

test_cases = [
    {
        "input": "I parked my car in a no parking zone.",
        "expected": "R001"
    },
    {
        "input": "I blocked the emergency fire lane.",
        "expected": "R002"
    },
    {
        "input": "I parked in a disabled parking space.",
        "expected": "R003"
    },
    {
        "input": "I exceeded the allowed parking time.",
        "expected": "R004"
    },
    {
        "input": "I parked against the traffic direction.",
        "expected": "R005"
    },
    {
        "input": "I parked beside another car and blocked it.",
        "expected": "R006"
    },
    {
        "input": "I blocked someone's garage driveway.",
        "expected": "R007"
    }
]

if st.button("▶️ Run All Tests"):

    passed = 0
    failed = 0

    for index, test in enumerate(test_cases):

        predicted_rule, test_score = find_best_rule(
            test["input"]
        )

        is_correct = (
            predicted_rule["rule_id"] == test["expected"]
        )

        if is_correct:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"

        with st.expander(f"Test Case {index + 1}: {status}"):

            st.write("Input:", test["input"])

            st.write("Expected Rule:", test["expected"])

            st.write(
                "Predicted Rule:",
                predicted_rule["rule_id"],
                "-",
                predicted_rule["title"]
            )

            st.write(
                "Similarity Score:",
                round(test_score, 3)
            )

    st.divider()

    st.subheader("📊 Testing Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tests", len(test_cases))
    col2.metric("Passed", passed)
    col3.metric("Failed", failed)

    accuracy = (passed / len(test_cases)) * 100

    st.metric("Test Accuracy", f"{accuracy:.1f}%")
