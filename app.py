import streamlit as st
import streamlit.components.v1 as components
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
        """, height=1400, scrolling=True)

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

    student_id = st.session_state.student_id
    student = df[df["id_student"] == student_id].iloc[0]

    # ---- helpers ----
    risk_prob = round(float(student["predicted_proba_risk"]), 2)
    if risk_prob >= 0.7:
        risk_color_bg = "#FCEBEB"
        risk_color_text = "#A32D2D"
    elif risk_prob >= 0.4:
        risk_color_bg = "#FAEEDA"
        risk_color_text = "#633806"
    else:
        risk_color_bg = "#EAF3DE"
        risk_color_text = "#27500A"

    early_eng = round(float(student["early_engagement"]))
    early_eng_bar = min(early_eng, 100)
    last_week = round(float(student["last_week_activity"]) * 100) if student["last_week_activity"] <= 1 else round(float(student["last_week_activity"]))
    trend = float(student["engagement_trend"])
    trend_label = "Improving" if trend > 0 else "Declining"
    trend_pct = min(max(round(abs(trend) * 100), 5), 100)
    trend_color = "#1D9E75" if trend > 0 else "#E24B4A"
    trend_text_color = "#085041" if trend > 0 else "#A32D2D"
    trend_bg = "#E1F5EE" if trend > 0 else "#FCEBEB"

    late_ratio = round(float(student["late_submission_ratio"]) * 100) if student["late_submission_ratio"] <= 1 else round(float(student["late_submission_ratio"]))
    assess_eng = round(float(student["assessment_week_engagement"]))
    assess_eng_bar = min(assess_eng, 100)
    proc_score = round(float(student["procrastination_score"]), 2)
    if proc_score >= 0.6:
        proc_label = "High"
        proc_bg = "#FCEBEB"
        proc_text = "#A32D2D"
        proc_bar = "#E24B4A"
    elif proc_score >= 0.35:
        proc_label = "Moderate"
        proc_bg = "#FAEEDA"
        proc_text = "#633806"
        proc_bar = "#EF9F27"
    else:
        proc_label = "Low"
        proc_bg = "#EAF3DE"
        proc_text = "#27500A"
        proc_bar = "#639922"

    # ---- study tips ----
    tips = []
    if student["procrastination_score"] > 0.4:
        tips.append(("Try starting assignments earlier and breaking them into smaller steps.", "Based on your procrastination score", "#E24B4A"))
    if student["early_engagement"] < 50:
        tips.append(("Engaging with course materials earlier each week may reduce deadline pressure.", "Based on your early engagement pattern", "#378ADD"))
    if student["num_submissions"] < 3:
        tips.append(("Review upcoming assessment deadlines — you have fewer submissions than expected.", "Based on your submission count", "#E24B4A"))
    if student["resource_diversity"] < 0.4:
        tips.append(("Try exploring different content types — quizzes, wikis, and forums alongside readings.", "Based on your resource diversity", "#1D9E75"))
    if student["assessment_week_engagement"] < 0.5:
        tips.append(("Stay active on the platform during assessment weeks to keep on top of requirements.", "Based on your assessment week activity", "#EF9F27"))
    if not tips:
        tips.append(("You are on track — keep up the great work!", "No concerns identified", "#1D9E75"))

    tips_html = ""
    for i, (tip_text, tip_meta, tip_color) in enumerate(tips):
        border = "none" if i == len(tips) - 1 else "0.5px solid #e8e8e4"
        tips_html += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:{border};">'
            f'<div style="width:6px;height:6px;border-radius:50%;background:{tip_color};flex-shrink:0;margin-top:6px;"></div>'
            f'<div>'
            f'<p style="font-size:13px;color:#1a1a1a;line-height:1.5;margin:0;">{tip_text}</p>'
            f'<p style="font-size:11px;color:#aaa;margin:2px 0 0;">{tip_meta}</p>'
            f'</div></div>'
        )

    st.markdown(f"""
    <style>
    .sv-label {{font-size:11px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:#aaa;margin:0 0 12px;}}
    .sv-metric {{background:#f8f8f6;border-radius:8px;padding:14px 16px;}}
    .sv-metric .lbl {{font-size:11px;color:#888;margin:0 0 4px;}}
    .sv-metric .val {{font-size:22px;font-weight:600;color:#1a1a1a;margin:0;}}
    .sv-metric .sub {{font-size:11px;color:#bbb;margin:2px 0 0;}}
    .sv-card {{background:#fff;border:1px solid #e8e8e4;border-radius:12px;padding:16px 18px;margin-bottom:0;}}
    .bar-track {{height:6px;background:#f0f0ed;border-radius:3px;overflow:hidden;margin-top:6px;}}
    .bar-fill {{height:100%;border-radius:3px;}}
    </style>

    <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:24px;">
        <div>
            <p style="margin:0;font-size:20px;font-weight:600;color:#1a1a1a;">My learning engagement</p>
            <p style="margin:2px 0 0;font-size:13px;color:#888;">Private insights to support your studies</p>
        </div>
        <span style="background:{risk_color_bg};color:{risk_color_text};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">Risk: {risk_prob}</span>
    </div>

    <p class="sv-label">Engagement snapshot</p>
    <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:28px;">
        <div class="sv-metric"><p class="lbl">Total activity</p><p class="val">{int(student['total_clicks']):,}</p><p class="sub">clicks</p></div>
        <div class="sv-metric"><p class="lbl">Active weeks</p><p class="val">{int(student['active_weeks'])}</p><p class="sub">this module</p></div>
        <div class="sv-metric"><p class="lbl">Active days</p><p class="val">{int(student['active_days'])}</p><p class="sub">this module</p></div>
        <div class="sv-metric"><p class="lbl">Submissions</p><p class="val">{int(student['num_submissions'])}</p><p class="sub">submitted</p></div>
    </div>

    <p class="sv-label">Activity trend</p>
    <div class="sv-card" style="margin-bottom:28px;">
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;">
            <div>
                <p style="font-size:12px;color:#888;margin:0 0 4px;">Early engagement</p>
                <p style="font-size:15px;font-weight:600;color:#1a1a1a;margin:0;">{early_eng}%</p>
                <div class="bar-track"><div class="bar-fill" style="width:{early_eng_bar}%;background:#378ADD;"></div></div>
                <p style="font-size:11px;color:#aaa;margin:5px 0 0;">{'Good start to the module' if early_eng >= 60 else 'Engaged late in the module'}</p>
            </div>
            <div>
                <p style="font-size:12px;color:#888;margin:0 0 4px;">Recent trend</p>
                <p style="font-size:15px;font-weight:600;color:#1a1a1a;margin:0;">{trend_label}</p>
                <div class="bar-track"><div class="bar-fill" style="width:{trend_pct}%;background:{trend_color};"></div></div>
                <p style="font-size:11px;color:#aaa;margin:5px 0 0;"><span style="background:{trend_bg};color:{trend_text_color};padding:1px 6px;border-radius:10px;font-size:10px;">{'+' if trend > 0 else ''}{round(trend, 3)}</span></p>
            </div>
            <div>
                <p style="font-size:12px;color:#888;margin:0 0 4px;">Last week activity</p>
                <p style="font-size:15px;font-weight:600;color:#1a1a1a;margin:0;">{last_week}%</p>
                <div class="bar-track"><div class="bar-fill" style="width:{min(last_week,100)}%;background:#1D9E75;"></div></div>
                <p style="font-size:11px;color:#aaa;margin:5px 0 0;">{'Active last week' if last_week >= 50 else 'Low activity last week'}</p>
            </div>
        </div>
    </div>

    <p class="sv-label">Assessment habits</p>
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:28px;">
        <div class="sv-card">
            <p style="font-size:12px;color:#888;margin:0 0 12px;">Submission behaviour</p>
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">
                <span style="font-size:13px;color:#1a1a1a;">Late submission ratio</span>
                <span style="font-size:13px;font-weight:600;color:{'#A32D2D' if late_ratio > 50 else '#27500A'};">{late_ratio}%</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:{late_ratio}%;background:{'#E24B4A' if late_ratio > 50 else '#639922'};"></div></div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin:14px 0 4px;">
                <span style="font-size:13px;color:#1a1a1a;">Assessment week engagement</span>
                <span style="font-size:13px;font-weight:600;color:#185FA5;">{assess_eng}%</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:{assess_eng_bar}%;background:#378ADD;"></div></div>
        </div>
        <div class="sv-card">
            <p style="font-size:12px;color:#888;margin:0 0 10px;">Procrastination score</p>
            <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:8px;">
                <span style="font-size:28px;font-weight:600;color:#1a1a1a;">{proc_score}</span>
                <span style="font-size:12px;color:{proc_text};background:{proc_bg};padding:2px 8px;border-radius:20px;">{proc_label}</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:{int(proc_score*100)}%;background:{proc_bar};"></div></div>
            <p style="font-size:12px;color:#aaa;margin:10px 0 0;line-height:1.5;">
                {'You tend to start assessments close to the deadline.' if proc_score > 0.4 else 'You generally start assessments with good lead time.'}
            </p>
        </div>
    </div>

    <p class="sv-label">Study suggestions</p>
    <div class="sv-card">
        {tips_html}
    </div>
    """, unsafe_allow_html=True)

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