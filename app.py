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

    # ---- session state for nav and selected student ----
    if "av_page" not in st.session_state:
        st.session_state.av_page = "overview"
    if "av_selected_student" not in st.session_state:
        st.session_state.av_selected_student = None

    # ---- shared CSS ----
    st.markdown("""
    <style>
    .av-label{font-size:11px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:#aaa;margin:0 0 12px;}
    .av-metric{background:#f8f8f6;border-radius:8px;padding:14px 16px;}
    .av-metric .lbl{font-size:11px;color:#888;margin:0 0 4px;}
    .av-metric .val{font-size:22px;font-weight:600;color:#1a1a1a;margin:0;}
    .av-card{background:#fff;border:1px solid #e8e8e4;border-radius:12px;padding:16px 18px;}
    .bar-track{height:6px;background:#f0f0ed;border-radius:3px;overflow:hidden;margin-top:5px;}
    .bar-fill{height:100%;border-radius:3px;}
    .risk-hi{background:#FCEBEB;color:#A32D2D;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}
    .risk-md{background:#FAEEDA;color:#633806;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}
    .risk-lo{background:#EAF3DE;color:#27500A;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}
    .int-card-urgent{padding:10px 12px;background:#fff8f8;border-radius:8px;border-left:3px solid #E24B4A;margin-bottom:8px;}
    .int-card-advisory{padding:10px 12px;background:#fffbf5;border-radius:8px;border-left:3px solid #EF9F27;margin-bottom:8px;}
    .int-badge-urgent{background:#FCEBEB;color:#A32D2D;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}
    .int-badge-advisory{background:#FAEEDA;color:#633806;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;}
    </style>
    """, unsafe_allow_html=True)

    # ---- sidebar navigation ----
    with st.sidebar:
        st.markdown("<hr style='border:none;border-top:1px solid #e8e8e4;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown('<p class="sidebar-section-label">Navigation</p>', unsafe_allow_html=True)
        if st.button("Cohort overview", use_container_width=True):
            st.session_state.av_page = "overview"
            safe_rerun()
        if st.button("Student detail", use_container_width=True):
            st.session_state.av_page = "detail"
            safe_rerun()

    # ============================================================
    # PAGE 1 — COHORT OVERVIEW
    # ============================================================
    if st.session_state.av_page == "overview":

        total   = df["id_student"].nunique()
        n_high  = int((df["risk_level"] == "High Risk").sum())
        n_mod   = int((df["risk_level"] == "Moderate Risk").sum())
        n_low   = int((df["risk_level"] == "Low Risk").sum())
        pct_hi  = round(n_high / total * 100)
        pct_md  = round(n_mod  / total * 100)
        pct_lo  = round(n_low  / total * 100)

        st.markdown(f"""
        <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:24px;">
            <div>
                <p style="margin:0;font-size:20px;font-weight:600;color:#1a1a1a;">Cohort overview</p>
                <p style="margin:2px 0 0;font-size:13px;color:#888;">Academic risk analytics — all students</p>
            </div>
        </div>

        <p class="av-label">Cohort stats</p>
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:28px;">
            <div class="av-metric"><p class="lbl">Total students</p><p class="val">{total}</p></div>
            <div class="av-metric"><p class="lbl">High risk</p><p class="val" style="color:#A32D2D;">{n_high}</p></div>
            <div class="av-metric"><p class="lbl">Moderate risk</p><p class="val" style="color:#854F0B;">{n_mod}</p></div>
            <div class="av-metric"><p class="lbl">Low risk</p><p class="val" style="color:#3B6D11;">{n_low}</p></div>
        </div>

        <p class="av-label">Risk distribution</p>
        <div class="av-card" style="margin-bottom:28px;">
            <div style="display:flex;gap:3px;height:24px;border-radius:6px;overflow:hidden;margin-bottom:12px;">
                <div style="width:{pct_hi}%;background:#E24B4A;"></div>
                <div style="width:{pct_md}%;background:#EF9F27;"></div>
                <div style="width:{pct_lo}%;background:#639922;"></div>
            </div>
            <div style="display:flex;gap:20px;font-size:12px;">
                <span style="display:flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:2px;background:#E24B4A;display:inline-block;"></span><span style="color:#888;">High risk {pct_hi}%</span></span>
                <span style="display:flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:2px;background:#EF9F27;display:inline-block;"></span><span style="color:#888;">Moderate {pct_md}%</span></span>
                <span style="display:flex;align-items:center;gap:5px;"><span style="width:10px;height:10px;border-radius:2px;background:#639922;display:inline-block;"></span><span style="color:#888;">Low risk {pct_lo}%</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---- filters ----
        st.markdown('<p class="av-label">All students</p>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        filter_risk   = fc1.selectbox("Risk level",   ["All"] + ["High Risk", "Moderate Risk", "Low Risk"], label_visibility="collapsed")
        filter_module = fc2.selectbox("Module",       ["All modules"] + sorted(df["code_module"].dropna().unique().tolist()), label_visibility="collapsed")
        filter_region = fc3.selectbox("Region",       ["All regions"] + sorted(df["region"].dropna().unique().tolist()), label_visibility="collapsed")

        filtered = df.copy()
        if filter_risk   != "All":           filtered = filtered[filtered["risk_level"]   == filter_risk]
        if filter_module != "All modules":   filtered = filtered[filtered["code_module"]  == filter_module]
        if filter_region != "All regions":   filtered = filtered[filtered["region"]       == filter_region]

        # ---- student table ----
        display_cols = {
            "id_student":           "Student ID",
            "code_module":          "Module",
            "code_presentation":    "Presentation",
            "risk_level":           "Risk",
            "predicted_proba_risk": "Probability",
            "final_result":         "Result",
        }
        table_df = filtered[list(display_cols.keys())].copy()
        table_df = table_df.rename(columns=display_cols)
        table_df["Probability"] = table_df["Probability"].round(3)
        table_df = table_df.sort_values("Probability", ascending=False).reset_index(drop=True)

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Student ID": st.column_config.TextColumn("Student ID"),
                "Probability": st.column_config.ProgressColumn(
                    "Probability", min_value=0, max_value=1, format="%.3f"
                ),
            }
        )
        st.caption("Select a student in the sidebar → Student detail to drill down.")

    # ============================================================
    # PAGE 2 — STUDENT DETAIL
    # ============================================================
    elif st.session_state.av_page == "detail":

        selected_id = st.selectbox(
            "Select student",
            options=sorted(df["id_student"].unique()),
            index=0
        )
        student = df[df["id_student"] == selected_id].iloc[0]

        # ---- risk helpers ----
        risk_prob = round(float(student["predicted_proba_risk"]), 2)
        rl = student["risk_level"]
        if rl == "High Risk":
            rb_bg, rb_text = "#FCEBEB", "#A32D2D"
        elif rl == "Moderate Risk":
            rb_bg, rb_text = "#FAEEDA", "#633806"
        else:
            rb_bg, rb_text = "#EAF3DE", "#27500A"

        # ---- engagement helpers ----
        active_weeks   = int(student["active_weeks"])
        proc_score     = round(float(student["procrastination_score"]), 2)
        late_ratio     = round(float(student["late_submission_ratio"]) * 100) if float(student["late_submission_ratio"]) <= 1 else round(float(student["late_submission_ratio"]))
        early_eng      = round(float(student["early_engagement"]))
        assess_eng     = round(float(student["assessment_week_engagement"]))
        early_eng_bar  = min(early_eng, 100)
        assess_eng_bar = min(assess_eng, 100)
        num_subs       = int(student["num_submissions"])
        eng_trend      = float(student["engagement_trend"])
        trend_label    = "Improving" if eng_trend > 0 else "Declining"
        trend_color    = "#1D9E75" if eng_trend > 0 else "#E24B4A"

        # ---- activity breakdown ----
        activity_cols = ["homepage","oucontent","resource","quiz","forumng","ouwiki",
                         "page","url","subpage","glossary","repeatactivity","dataplus"]
        act_data = []
        for col in activity_cols:
            if col in student.index:
                val = int(student[col]) if pd.notna(student[col]) else 0
                if val > 0:
                    act_data.append((col.replace("ou","").replace("ng","").capitalize(), val))
        act_data.sort(key=lambda x: x[1], reverse=True)
        act_max = act_data[0][1] if act_data else 1

        def act_color(name, val, max_val):
            pct = val / max_val
            if pct > 0.5: return "#378ADD"
            if pct > 0.2: return "#EF9F27"
            return "#E24B4A"

        act_html = ""
        for name, val in act_data[:8]:
            pct = round(val / act_max * 100)
            col = act_color(name, val, act_max)
            act_html += (
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
                f'<span style="font-size:12px;color:#555;width:80px;flex-shrink:0;">{name}</span>'
                f'<div style="flex:1;background:#f0f0ed;border-radius:3px;height:5px;overflow:hidden;">'
                f'<div style="width:{pct}%;height:100%;background:{col};border-radius:3px;"></div></div>'
                f'<span style="font-size:12px;color:#1a1a1a;font-weight:600;width:36px;text-align:right;">{val:,}</span>'
                f'</div>'
            )

        # ---- interventions ----
        urgent, advisory = [], []
        if active_weeks < 5:
            urgent.append("Wellbeing or access-related outreach — fewer than 5 active weeks.")
        if num_subs < 3:
            urgent.append("Academic check-in regarding assessment participation.")
        if eng_trend < 0:
            advisory.append("Offer academic coaching or tutoring support — engagement is declining.")
        if proc_score > 0.4:
            advisory.append("Refer to time-management or study skills support.")
        if late_ratio > 50:
            advisory.append("Discuss submission planning — over half of submissions have been late.")
        if assess_eng < 40:
            advisory.append("Encourage platform activity during assessment weeks.")

        int_html = ""
        for msg in urgent:
            int_html += f'<div class="int-card-urgent"><span class="int-badge-urgent">Urgent</span><p style="font-size:12px;color:#1a1a1a;margin:6px 0 0;line-height:1.5;">{msg}</p></div>'
        for msg in advisory:
            int_html += f'<div class="int-card-advisory"><span class="int-badge-advisory">Advisory</span><p style="font-size:12px;color:#1a1a1a;margin:6px 0 0;line-height:1.5;">{msg}</p></div>'
        if not urgent and not advisory:
            int_html = '<p style="font-size:13px;color:#3B6D11;background:#EAF3DE;padding:10px 14px;border-radius:8px;margin:0;">No interventions required — student is on track.</p>'

        # ---- pre-compute all conditionals so no ternary sits inside the f-string ----
        avatar_initial   = str(student['gender'])[0].upper() if pd.notna(student['gender']) else '?'
        prev_attempts    = int(student['num_of_prev_attempts']) if pd.notna(student['num_of_prev_attempts']) else 0
        credits_studied  = int(student['studied_credits']) if pd.notna(student['studied_credits']) else '—'

        aw_pct           = min(round(active_weeks / 12 * 100), 100)
        aw_color         = "#639922" if active_weeks >= 8 else "#E24B4A"
        ee_color         = "#639922" if early_eng >= 60 else "#E24B4A"
        ae_color         = "#639922" if assess_eng >= 50 else "#EF9F27"
        lr_color         = "#E24B4A" if late_ratio > 50 else "#639922"
        trend_pct        = min(round(abs(eng_trend) * 100), 100)
        if proc_score > 0.6:
            ps_color = "#E24B4A"
        elif proc_score > 0.35:
            ps_color = "#EF9F27"
        else:
            ps_color = "#639922"

        # ---- render ----
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">
            <div>
                <p style="margin:0;font-size:20px;font-weight:600;color:#1a1a1a;">Student {selected_id}</p>
                <p style="margin:2px 0 0;font-size:13px;color:#888;">{student['code_module']} · {student['code_presentation']} · Individual detail</p>
            </div>
            <span style="background:{rb_bg};color:{rb_text};padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">{rl} · {risk_prob}</span>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">

            <div class="av-card">
                <p class="av-label" style="margin-bottom:14px;">Student profile</p>
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;padding-bottom:14px;border-bottom:0.5px solid #f0f0ed;">
                    <div style="width:40px;height:40px;border-radius:50%;background:#dbeafe;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:#1d4ed8;flex-shrink:0;">{avatar_initial}</div>
                    <div>
                        <p style="margin:0;font-size:14px;font-weight:600;color:#1a1a1a;">Student {selected_id}</p>
                        <p style="margin:0;font-size:12px;color:#888;">Prev. attempts: {prev_attempts}</p>
                    </div>
                </div>
                <table style="width:100%;font-size:12px;border-collapse:collapse;">
                    <tr><td style="color:#888;padding:4px 0;">Gender</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['gender']}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">Age band</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['age_band']}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">Region</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['region']}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">Education</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['highest_education']}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">IMD band</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['imd_band']}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">Disability</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['disability']}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">Credits studied</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{credits_studied}</td></tr>
                    <tr><td style="color:#888;padding:4px 0;">Final result</td><td style="text-align:right;color:#1a1a1a;font-weight:500;">{student['final_result']}</td></tr>
                </table>
            </div>

            <div class="av-card">
                <p class="av-label" style="margin-bottom:14px;">Engagement deep-dive</p>
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;"><span style="font-size:12px;color:#888;">Active weeks</span><span style="font-size:12px;font-weight:600;color:#1a1a1a;">{active_weeks}</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width:{aw_pct}%;background:{aw_color};"></div></div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;"><span style="font-size:12px;color:#888;">Early engagement</span><span style="font-size:12px;font-weight:600;color:#1a1a1a;">{early_eng}%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width:{early_eng_bar}%;background:{ee_color};"></div></div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;"><span style="font-size:12px;color:#888;">Engagement trend</span><span style="font-size:12px;font-weight:600;color:{trend_color};">{trend_label}</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width:{trend_pct}%;background:{trend_color};"></div></div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;"><span style="font-size:12px;color:#888;">Assessment week engagement</span><span style="font-size:12px;font-weight:600;color:#1a1a1a;">{assess_eng}%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width:{assess_eng_bar}%;background:{ae_color};"></div></div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;"><span style="font-size:12px;color:#888;">Late submission ratio</span><span style="font-size:12px;font-weight:600;color:#1a1a1a;">{late_ratio}%</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width:{late_ratio}%;background:{lr_color};"></div></div>
                </div>
                <div>
                    <div style="display:flex;justify-content:space-between;"><span style="font-size:12px;color:#888;">Procrastination score</span><span style="font-size:12px;font-weight:600;color:#1a1a1a;">{proc_score}</span></div>
                    <div class="bar-track"><div class="bar-fill" style="width:{int(proc_score*100)}%;background:{ps_color};"></div></div>
                </div>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="av-card">
                <p class="av-label" style="margin-bottom:14px;">Activity breakdown</p>
                {act_html}
            </div>
            <div class="av-card">
                <p class="av-label" style="margin-bottom:14px;">Recommended interventions</p>
                {int_html}
            </div>
        </div>
        """, unsafe_allow_html=True)