import streamlit as st
import pandas as pd
from credentials import USERS

# Attempt to import Streamlit's script run context getter; provide a safe fallback.
try:
    from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
except Exception:
    def get_script_run_ctx():
        return None

def safe_rerun():
    if get_script_run_ctx() is not None:
        st.experimental_rerun()
    else:
        print("safe_rerun: skipping st.experimental_rerun() because no ScriptRunContext was found.")

# --------------------------------------------------
# Page config (only call this ONCE)
# --------------------------------------------------
st.set_page_config(
    page_title="The University | Student Analytics",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/dashboard.csv")
    df.columns = df.columns.str.lower()
    df["id_student"] = df["id_student"].astype(str)
    return df

df = load_data()

# --------------------------------------------------
# Risk banding
# --------------------------------------------------
def assign_risk(prob):
    if prob >= 0.7:
        return "High Risk"
    elif prob >= 0.4:
        return "Moderate Risk"
    else:
        return "Low Risk"

df["risk_level"] = df["predicted_proba_risk"].apply(assign_risk)

# --------------------------------------------------
# Session state defaults
# --------------------------------------------------
for key, default in {
    "authenticated": False,
    "role": None,
    "student_id": None,
    "username": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------------------------------
# Custom CSS — clean minimal sidebar
# --------------------------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #f8f8f6;
    border-right: 1px solid #e8e8e4;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 0 24px 0;
    border-bottom: 1px solid #e8e8e4;
    margin-bottom: 24px;
}
.sidebar-brand .name {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
    line-height: 1.2;
}
.sidebar-brand .sub {
    font-size: 11px;
    color: #888;
    margin: 0;
}
.sidebar-section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 14px;
}
.user-chip {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 10px 12px;
    background: #fff;
    border: 1px solid #e8e8e4;
    border-radius: 8px;
    margin-top: 8px;
}
.user-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #dbeafe;
    color: #1d4ed8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    flex-shrink: 0;
}
.user-info .user-name {
    font-size: 12px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
}
.user-info .user-role {
    font-size: 11px;
    color: #888;
    margin: 0;
}
[data-testid="stSidebar"] label {
    font-size: 12px !important;
    color: #555 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background-color: #1a1a1a;
    color: #fff;
    border: none;
    border-radius: 7px;
    font-size: 13px;
    font-weight: 500;
    height: 36px;
    margin-top: 4px;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #333;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:

    # Brand lockup
    st.markdown("""
    <div class="sidebar-brand">
        <div>
            <p class="name">🎓 The University</p>
            <p class="sub">Student Analytics</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- LOGGED OUT ----
    if not st.session_state.authenticated:
        st.markdown('<p class="sidebar-section-label">Sign in</p>', unsafe_allow_html=True)

        username_input = st.text_input("Username", placeholder="Enter username")
        password_input = st.text_input("Password", type="password", placeholder="••••••••")

        if st.button("Sign in"):
            if username_input in USERS and USERS[username_input]["password"] == password_input:
                st.session_state.authenticated = True
                st.session_state.username = username_input
                st.session_state.role = USERS[username_input]["role"]
                if USERS[username_input]["role"] == "Student":
                    st.session_state.student_id = USERS[username_input]["id_student"]
                safe_rerun()
            else:
                st.error("Invalid credentials")

    # ---- LOGGED IN ----
    else:
        stored_username = st.session_state.username or st.session_state.role
        initials = stored_username[:2].upper()
        role = st.session_state.role

        st.markdown(f"""
        <div class="user-chip">
            <div class="user-avatar">{initials}</div>
            <div class="user-info">
                <p class="user-name">{stored_username}</p>
                <p class="user-role">{role}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign out"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.student_id = None
            st.session_state.username = None
            safe_rerun()

# --------------------------------------------------
# Gate: stop if not logged in
# --------------------------------------------------
if not st.session_state.authenticated:
    st.warning("Please sign in to continue.")
    st.stop()

role = st.session_state.role

# ==================================================
# STUDENT VIEW
# ==================================================
if role == "Student":

    st.title("My Learning Engagement")
    st.caption("Private insights to support your studies")

    student_id = st.session_state.student_id
    student = df[df["id_student"] == student_id].iloc[0]

    st.subheader("Engagement Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Weeks", student["active_weeks"])
    col2.metric("Active Days", student["active_days"])
    col3.metric("Submissions", student["num_submissions"])

    st.subheader("Engagement Trend")
    if student["engagement_trend"] > 0:
        st.success("Your engagement is improving over time.")
    else:
        st.warning("Your engagement has declined recently.")

    st.subheader("Study Suggestions")
    tips = []
    if student["num_submissions"] < 3:
        tips.append("Review upcoming assessment deadlines.")
    if student["procrastination_score"] > 0.4:
        tips.append("Try starting assignments earlier and breaking tasks into steps.")
    if student["early_engagement"] < 50:
        tips.append("Engaging earlier with course materials may reduce pressure.")

    if tips:
        for t in tips:
            st.write(f"• {t}")
    else:
        st.success("You are on track — keep up the good work!")

# ==================================================
# ACADEMIC DEVELOPER VIEW
# ==================================================
elif role == "Academic Developer":

    st.title("Academic Risk Analytics")
    st.caption("Decision-support for targeted student interventions")

    st.subheader("Risk Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", df["id_student"].nunique())
    col2.metric("High Risk", (df["risk_level"] == "High Risk").sum())
    col3.metric("Moderate Risk", (df["risk_level"] == "Moderate Risk").sum())
    col4.metric("Low Risk", (df["risk_level"] == "Low Risk").sum())

    st.subheader("Student Drill-Down")
    selected_student = st.selectbox("Select Student", sorted(df["id_student"].unique()))
    student = df[df["id_student"] == selected_student].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Probability", round(student["predicted_proba_risk"], 3))
    col2.metric("Risk Level", student["risk_level"])
    col3.metric("Final Result", student["final_result"])

    st.subheader("Key Engagement Indicators")
    indicators = {
        "Active Weeks": student["active_weeks"],
        "Engagement Trend": student["engagement_trend"],
        "Submissions": student["num_submissions"],
        "Procrastination Score": student["procrastination_score"]
    }
    st.dataframe(pd.DataFrame.from_dict(indicators, orient="index", columns=["Value"]))

    st.subheader("Recommended Interventions")
    actions = []
    if student["num_submissions"] < 3:
        actions.append("Academic check-in regarding assessment participation.")
    if student["engagement_trend"] < 0:
        actions.append("Offer academic coaching or tutoring support.")
    if student["procrastination_score"] > 0.4:
        actions.append("Refer to time-management or study skills support.")
    if student["active_weeks"] < 5:
        actions.append("Wellbeing or access-related outreach recommended.")

    if actions:
        for a in actions:
            st.write(f"• {a}")
    else:
        st.success("No immediate intervention required.")