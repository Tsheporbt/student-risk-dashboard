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
    """
    Call st.experimental_rerun() only when Streamlit's ScriptRunContext is available.
    When running the script outside `streamlit run` (e.g. plain python/IDE), this is a no-op.
    """
    if get_script_run_ctx() is not None:
        st.experimental_rerun()
    else:
        # Running in bare mode — do not attempt to rerun; print to stdout for diagnostics.
        print("safe_rerun: skipping st.experimental_rerun() because no ScriptRunContext was found.")

# --------------------------------------------------
# Page config
# --------------------------------------------------

st.set_page_config(
    page_title="The University | Student Analytics",
    page_icon="🎓",
    layout="wide"
)

st.image("assets/ulogo.png", width=120)
st.markdown("## 🎓 The University")
st.markdown("---")


st.set_page_config(
    page_title="Student Engagement Dashboard",
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
# Authentication
# --------------------------------------------------
st.sidebar.header("Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# Initialize expected session keys with safe defaults
for key, default in {
    "authenticated": False,
    "role": None,
    "student_id": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Handle login
if st.sidebar.button("Login"):
    if username in USERS and USERS[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.role = USERS[username]["role"]
        if USERS[username]["role"] == "Student":
            st.session_state.student_id = USERS[username]["id_student"]
        # Rerun so the app picks up the new session state immediately
        safe_rerun()
    else:
        st.sidebar.error("Invalid credentials")

if not st.session_state.authenticated:
    st.warning("Please log in to continue.")
    st.stop()

# Handle logout 
if st.sidebar.button("Logout"): 
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.student_id = None          
    safe_rerun()

role = st.session_state.get("role")

# ==================================================
# 🎓 STUDENT VIEW
# ==================================================
if role == "Student":

    st.title("My Learning Engagement")
    st.caption("Private insights to support your studies")

    student_id = st.session_state.student_id
    student = df[df["id_student"] == student_id].iloc[0]

    # --- Engagement summary ---
    st.subheader("Engagement Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Weeks", student["active_weeks"])
    col2.metric("Active Days", student["active_days"])
    col3.metric("Submissions", student["num_submissions"])

    # --- Engagement trend ---
    st.subheader("Engagement Trend")
    if student["engagement_trend"] > 0:
        st.success("Your engagement is improving over time.")
    else:
        st.warning("Your engagement has declined recently.")

    # --- Study guidance ---
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
# 🧑‍💼 ACADEMIC DEVELOPER VIEW
# ==================================================
elif role == "Academic Developer":

    st.title("Academic Risk Analytics")
    st.caption("Decision-support for targeted student interventions")

    # --- Overview KPIs ---
    st.subheader("Risk Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", df["id_student"].nunique())
    col2.metric("High Risk", (df["risk_level"] == "High Risk").sum())
    col3.metric("Moderate Risk", (df["risk_level"] == "Moderate Risk").sum())
    col4.metric("Low Risk", (df["risk_level"] == "Low Risk").sum())

    # --- Student drill-down ---
    st.subheader("Student Drill-Down")

    selected_student = st.selectbox(
        "Select Student",
        sorted(df["id_student"].unique())
    )

    student = df[df["id_student"] == selected_student].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Probability", round(student["predicted_proba_risk"], 3))
    col2.metric("Risk Level", student["risk_level"])
    col3.metric("Final Result", student["final_result"])

    # --- Engagement drivers ---
    st.subheader("Key Engagement Indicators")

    indicators = {
        "Active Weeks": student["active_weeks"],
        "Engagement Trend": student["engagement_trend"],
        "Submissions": student["num_submissions"],
        "Procrastination Score": student["procrastination_score"]
    }

    st.dataframe(
        pd.DataFrame.from_dict(indicators, orient="index", columns=["Value"])
    )

    # --- Prescriptive actions ---
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

