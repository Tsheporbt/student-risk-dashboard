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
    
    # Fill NaN values with safe defaults
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(0)
    
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
# Helper: Safe value display
# --------------------------------------------------
def safe_display(value, default="—"):
    """Safely display values, handling NaN and None"""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return value
    except:
        return default

def safe_numeric(value, default=0):
    """Safely convert to numeric, handling NaN and None"""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return float(value)
    except:
        return default

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
# Custom CSS — colour system & styling
# --------------------------------------------------
st.markdown("""
<style>
:root {
    /* Background & Surfaces */
    --bg-primary: #0A0F1E;
    --bg-card: rgba(255,255,255,0.04);
    
    /* Borders & Dividers */
    --border: rgba(255,255,255,0.08);
    
    /* Accent & Interactive */
    --accent: #00D4B8;
    --blue: #0080FF;
    
    /* Risk Levels */
    --risk-high: #FF4D6D;
    --risk-mod: #FFB347;
    --risk-low: #00D4B8;
    
    /* Text & Content */
    --text-primary: #FFFFFF;
    --text-muted: rgba(255,255,255,0.45);
    --text-label: rgba(255,255,255,0.30);
}

/* Typography Hierarchy */
.app-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.01em;
}

.section-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-label);
}

.section-subtitle {
    font-size: 13px;
    font-weight: 400;
    color: var(--text-muted);
}

.body-text {
    font-size: 13px;
    font-weight: 400;
    color: var(--text-muted);
    line-height: 1.5;
}

.data-number {
    font-size: 24px;
    font-weight: 700;
    font-family: 'Monaco', 'Courier New', monospace;
    color: var(--text-primary);
}

/* Card System */
.app-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}

/* Sidebar Styling */
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

/* Form Inputs */
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="password"] {
    padding: 10px 14px !important;
    border: 1px solid #e8e8e4 !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    margin-bottom: 12px !important;
}

[data-testid="stSidebar"] input[type="text"]:focus,
[data-testid="stSidebar"] input[type="password"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,212,184,0.1) !important;
    outline: none !important;
}

.user-chip {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 12px 14px;
    background: #fff;
    border: 1px solid #e8e8e4;
    border-radius: 8px;
    margin-top: 16px;
}

.user-avatar {
    width: 32px;
    height: 32px;
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

/* Sidebar Controls */
[data-testid="stSidebar"] label {
    font-size: 12px !important;
    color: #555 !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--accent), #00B8A6) !important;
    color: #1a1a1a !important;
    border: none !important;
    border-radius: 7px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 38px !important;
    margin-top: 8px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #00B8A6, #00A39A) !important;
    border: none !important;
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
            # Explicit cleanup
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.student_id = None
            st.session_state.username = None
            st.session_state.clear()
            safe_rerun()

# --------------------------------------------------
# Gate: stop if not logged in
# --------------------------------------------------
if not st.session_state.authenticated:
    st.warning("Please sign in to continue.")
    st.stop()

role = st.session_state.role

# --------------------------------------------------
# App Header Bar
# --------------------------------------------------
import os
from datetime import datetime

# Get last modified time of data file
data_file_path = "data/dashboard.csv"
if os.path.exists(data_file_path):
    last_modified = datetime.fromtimestamp(os.path.getmtime(data_file_path))
    last_updated_text = f"Last updated: {last_modified.strftime('%Y-%m-%d %H:%M')}"
else:
    last_updated_text = "Last updated: Unknown"

header_html = f"""
<div style="background:var(--bg-card);border-bottom:1px solid var(--border);padding:16px 24px;margin:-24px -24px 24px;display:flex;align-items:center;justify-content:space-between;">
    <div style="display:flex;align-items:center;gap:12px;">
        <span style="font-size:28px;">🎓</span>
        <div>
            <p class="app-title" style="margin:0;">Student Risk Dashboard</p>
            <p class="section-subtitle" style="margin:2px 0 0;">The University — Real-Time Analytics</p>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;">
        <div style="text-align:right;">
            <p style="margin:0;font-size:12px;font-weight:600;color:var(--text-primary);">{st.session_state.username}</p>
            <p style="margin:2px 0 0;font-size:11px;color:var(--text-muted);">{role}</p>
        </div>
        <div style="width:36px;height:36px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;color:#1a1a1a;font-weight:600;font-size:12px;">{st.session_state.username[:2].upper()}</div>
    </div>
</div>
<div style="display:flex;justify-content:flex-end;padding:0 0 16px;font-size:11px;color:var(--text-muted);">
    {last_updated_text}
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ==================================================
# STUDENT VIEW
# ==================================================
if role == "Student":

    student_id = st.session_state.student_id
    # Get all records for this student
    student_records = df[df["id_student"] == student_id]
    
    # Module selector if student has multiple enrollments
    if len(student_records) > 1:
        st.markdown('<p class="section-label">Select Module</p>', unsafe_allow_html=True)
        module_options = student_records[["code_module", "code_presentation"]].drop_duplicates()
        module_list = [f"{row['code_module']} - {row['code_presentation']}" for _, row in module_options.iterrows()]
        
        selected_module_str = st.selectbox("Which module would you like to view?", module_list)
        selected_module, selected_presentation = selected_module_str.split(" - ")
        student = student_records[(student_records["code_module"] == selected_module) & 
                                  (student_records["code_presentation"] == selected_presentation)].iloc[0]
    else:
        student = student_records.iloc[0]
    
    st.markdown("")  # Add spacing

    # ---- helpers ----
    risk_prob = round(float(student["predicted_proba_risk"]), 2)
    
    # Determine risk tier for color coding
    if risk_prob >= 0.7:
        risk_tier = "high"
    elif risk_prob >= 0.4:
        risk_tier = "mod"
    else:
        risk_tier = "low"
    
    # ---- Risk gauge SVG animation ----
    risk_percentage = int(risk_prob * 100)
    
    # Determine colors and label
    if risk_prob >= 0.7:
        risk_label = "HIGH RISK"
        arc_color = "#FF4D6D"
    elif risk_prob >= 0.4:
        risk_label = "MODERATE RISK"
        arc_color = "#FFB347"
    else:
        risk_label = "LOW RISK"
        arc_color = "#00D4B8"
    
    # SVG gauge with animation
    gauge_svg = f'''
    <svg viewBox="0 0 200 120" style="width:100%;height:auto;max-width:300px;margin:0 auto;display:block;">
        <!-- Background arc -->
        <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="12" stroke-linecap="round" stroke-dasharray="251.33" stroke-dashoffset="251.33"/>
        
        <!-- Animated arc -->
        <circle cx="100" cy="100" r="80" fill="none" stroke="{arc_color}" stroke-width="12" stroke-linecap="round" 
                stroke-dasharray="251.33" stroke-dashoffset="{{251.33 * (1 - {risk_prob})}}"
                style="transition: stroke-dashoffset 1.5s cubic-bezier(0.34, 1.56, 0.64, 1);transform-origin:100px 100px;"/>
        
        <!-- Center text -->
        <text x="100" y="95" text-anchor="middle" font-size="48" font-weight="700" fill="var(--text-primary)">{risk_percentage}%</text>
        <text x="100" y="115" text-anchor="middle" font-size="12" font-weight="600" fill="var(--text-muted)">{risk_label}</text>
    </svg>
    '''
    
    st.markdown(f"""
    <style>
    .gauge-container {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 24px 16px;
        margin-bottom: 28px;
    }}
    .gauge-subtitle {{
        font-size: 12px;
        font-weight: 600;
        color: var(--text-muted);
        text-align: center;
        margin-top: 12px;
    }}
    .trend-indicator {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 12px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        margin-bottom: 28px;
    }}
    </style>
    
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:28px;">
        <div class="gauge-container">
            <p class="section-label" style="margin:0 0 16px;text-align:center;">Your Risk Score</p>
            {gauge_svg}
            <p class="gauge-subtitle">Based on your engagement patterns</p>
        </div>
        <div>
            <div class="app-card">
                <p class="section-label" style="margin:0 0 16px;">Engagement Trend</p>
                <div style="display:flex;align-items:center;justify-content:center;height:140px;">
                    <div style="text-align:center;">
                        <div style="font-size:48px;margin-bottom:8px;">
                            {'📈' if trend > 0 else '↔️' if abs(trend) < 0.05 else '📉'}
                        </div>
                        <p style="margin:0;font-size:13px;color:var(--text-muted);">
                            {'Your activity is <strong>Increasing</strong>' if trend > 0 else 'Your activity is <strong>Stable</strong>' if abs(trend) < 0.05 else 'Your activity is <strong>Decreasing</strong>'}
                        </p>
                        <p style="margin:8px 0 0;font-size:11px;color:var(--text-muted);">
                            {f'Change: {trend:+.2%}' if abs(trend) >= 0.05 else 'No significant change'}
                        </p>
                    </div>
                </div>
                <p style="font-size:11px;color:var(--text-muted);margin:0;line-height:1.4;text-align:center;">
                    Your activity has {'increased' if trend > 0 else 'decreased' if trend < -0.05 else 'remained consistent'} over recent weeks. Keep this momentum going!
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    early_eng = round(float(student["early_engagement"]))
    early_eng_bar = min(early_eng, 100)
    last_week = round(float(student["last_week_activity"]) * 100) if student["last_week_activity"] <= 1 else round(float(student["last_week_activity"]))
    trend = float(student["engagement_trend"])
    trend_label = "Improving" if trend > 0 else "Declining"
    trend_pct = min(max(round(abs(trend) * 100), 5), 100)
    trend_color = "var(--risk-low)" if trend > 0 else "var(--risk-high)"
    trend_text_color = "#085041" if trend > 0 else "#A32D2D"
    trend_bg = "#E1F5EE" if trend > 0 else "#FCEBEB"

    # Click variability (activity consistency)
    click_variability = safe_numeric(student.get("click_variability", 0.5))
    # Normalize variability (lower = more consistent)
    # Assuming variability ranges from 0-5 typically
    variability_score = max(0, min(100, 100 - (click_variability / 5 * 100)))
    
    if variability_score >= 70:
        variability_label = "Consistent"
        variability_color = "var(--risk-low)"
        variability_message = "Your study pattern is steady and predictable"
    elif variability_score >= 40:
        variability_label = "Moderate"
        variability_color = "var(--risk-mod)"
        variability_message = "Variable activity — some weeks more active than others"
    else:
        variability_label = "Bursty"
        variability_color = "var(--risk-high)"
        variability_message = "Your activity is concentrated in short bursts (cramming)"

    late_ratio = round(float(student["late_submission_ratio"]) * 100) if student["late_submission_ratio"] <= 1 else round(float(student["late_submission_ratio"]))
    assess_eng = round(float(student["assessment_week_engagement"]))
    assess_eng_bar = min(assess_eng, 100)
    proc_score = round(float(student["procrastination_score"]), 2)
    if proc_score >= 0.6:
        proc_label = "High"
        proc_bg = "#FCEBEB"
        proc_text = "#A32D2D"
        proc_bar = "var(--risk-high)"
    elif proc_score >= 0.35:
        proc_label = "Moderate"
        proc_bg = "#FAEEDA"
        proc_text = "#633806"
        proc_bar = "var(--risk-mod)"
    else:
        proc_label = "Low"
        proc_bg = "#EAF3DE"
        proc_text = "#27500A"
        proc_bar = "var(--risk-low)"

    # ---- study tips ----
    tips = []
    
    # Build data-driven tips with specific metrics
    if student["procrastination_score"] > 0.4:
        tips.append((f"Your procrastination score is {proc_score} (High) — try breaking assessments into smaller steps.", "Based on your procrastination score", "var(--risk-high)"))
    else:
        tips.append((f"Your procrastination score is {proc_score} (Low) — great time management!", "Based on your procrastination score", "var(--risk-low)"))
    
    if student["early_engagement"] < 50:
        tips.append((f"Your early engagement is {early_eng}% — students above 60% are significantly less likely to withdraw.", "Based on your early engagement pattern", "var(--blue)"))
    else:
        tips.append((f"Your early engagement is {early_eng}% — excellent start to the module!", "Based on your early engagement pattern", "var(--risk-low)"))
    
    if student["late_submission_ratio"] > 0.5:
        late_pct = int(student["late_submission_ratio"] * 100)
        tips.append((f"{late_pct}% of your submissions have been late — late submission is one of the top 3 risk predictors.", "Based on your submission pattern", "var(--risk-high)"))
    
    if student["resource_diversity"] < 0.4:
        tips.append((f"Your content exploration score is {diversity_pct}% (Narrow) — try different resource types.", "Based on your resource diversity", "var(--risk-low)"))
    
    if student["assessment_week_engagement"] < 0.5:
        tips.append((f"Your assessment week engagement is {assess_eng}% — staying active during assessments is crucial.", "Based on your assessment week activity", "var(--risk-mod)"))
    
    if not tips or len(tips) < 4:
        if not tips:
            tips.append(("You are on track — keep up the great work!", "No concerns identified", "var(--risk-low)"))
    
    # Calculate explainability scores - what matters most
    explainability_factors = {}
    
    # Late submission ratio (0-1, higher is worse)
    explainability_factors["Late Submission Ratio"] = min(student.get("late_submission_ratio", 0), 1.0)
    
    # Procrastination score (0-1, higher is worse)
    explainability_factors["Procrastination Score"] = student.get("procrastination_score", 0)
    
    # Early engagement (0-100, lower is worse, so invert)
    early_eng_score = max(0, 1 - (student.get("early_engagement", 50) / 100))
    explainability_factors["Early Engagement Gap"] = early_eng_score
    
    # Last week activity (0-1, lower is worse)
    last_week_activity = student.get("last_week_activity", 0.5)
    if last_week_activity > 1:
        last_week_activity = 0.5  # Normalize if it's a count
    explainability_factors["Last Week Activity"] = max(0, 1 - last_week_activity)
    
    # Assessment week engagement (0-100, lower is worse, invert)
    assess_eng_score = max(0, 1 - (student.get("assessment_week_engagement", 50) / 100))
    explainability_factors["Assessment Week Gap"] = assess_eng_score
    
    # Resource diversity (0-1, lower is worse, invert)
    resource_div = student.get("resource_diversity", 0.5)
    explainability_factors["Limited Content Exploration"] = max(0, 1 - resource_div)
    
    # Sort by severity and get top 4
    top_factors = sorted(explainability_factors.items(), key=lambda x: x[1], reverse=True)[:4]
    
    tips_html = ""
    for i, (tip_text, tip_meta, tip_color) in enumerate(tips):
        border = "none" if i == len(tips) - 1 else "0.5px solid var(--border)"
        tips_html += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:{border};">'
            f'<div style="width:6px;height:6px;border-radius:50%;background:{tip_color};flex-shrink:0;margin-top:6px;"></div>'
            f'<div>'
            f'<p style="font-size:13px;color:var(--text-primary);line-height:1.5;margin:0;">{tip_text}</p>'
            f'<p style="font-size:11px;color:var(--text-muted);margin:2px 0 0;">{tip_meta}</p>'
            f'</div></div>'
        )
    
    # Build explainability HTML
    explainability_html = '<div class="app-card" style="margin-bottom:28px;"><p class="section-label" style="margin:0 0 14px;">Why is your risk {risk_percentage}%?</p>'
    explainability_html += '<p style="font-size:11px;color:var(--text-muted);margin:0 0 12px;">Top contributing factors:</p>'
    for idx, (factor_name, factor_score) in enumerate(top_factors, 1):
        bar_width = int(factor_score * 100)
        explainability_html += f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;"><span style="font-size:12px;color:var(--text-muted);">{idx}. {factor_name}</span><span style="font-size:11px;font-weight:600;color:var(--text-primary);">{bar_width}%</span></div><div class="bar-track"><div class="bar-fill" style="width:{bar_width}%;background:var(--risk-high);"></div></div></div>'
    explainability_html += '</div>'

    st.markdown(f"""
    <style>
    .sv-label {{font-size:11px;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:var(--text-label);margin:0 0 12px;}}
    .sv-metric {{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:16px 18px;}}
    .sv-metric .lbl {{font-size:11px;color:var(--text-muted);margin:0 0 4px;}}
    .sv-metric .val {{font-size:22px;font-weight:600;color:var(--text-primary);margin:0;}}
    .sv-metric .sub {{font-size:11px;color:var(--text-muted);margin:2px 0 0;}}
    .sv-card {{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:20px 24px;box-shadow:0 2px 12px rgba(0,0,0,0.25);margin-bottom:0;}}
    .bar-track {{height:6px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden;margin-top:6px;}}
    .bar-fill {{height:100%;border-radius:3px;}}
    </style>

    <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:24px;">
        <div>
            <p style="margin:0;font-size:22px;font-weight:700;color:var(--text-primary);">My learning engagement</p>
            <p style="margin:2px 0 0;font-size:13px;color:var(--text-muted);">Private insights to support your studies</p>
        </div>
        <span style="background:var(--risk-{'high' if risk_prob >= 0.7 else 'mod' if risk_prob >= 0.4 else 'low'});color:var(--text-primary);padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600;">Risk: {risk_prob}</span>
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
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;">
            <div>
                <p style="font-size:12px;color:var(--text-muted);margin:0 0 4px;">Early engagement</p>
                <p style="font-size:15px;font-weight:600;color:var(--text-primary);margin:0;">{early_eng}%</p>
                <div class="bar-track"><div class="bar-fill" style="width:{early_eng_bar}%;background:var(--blue);"></div></div>
                <p style="font-size:11px;color:var(--text-muted);margin:5px 0 0;">{'Good start to the module' if early_eng >= 60 else 'Engaged late in the module'}</p>
            </div>
            <div>
                <p style="font-size:12px;color:var(--text-muted);margin:0 0 4px;">Recent trend</p>
                <p style="font-size:15px;font-weight:600;color:var(--text-primary);margin:0;">{trend_label}</p>
                <div class="bar-track"><div class="bar-fill" style="width:{trend_pct}%;background:{trend_color};"></div></div>
                <p style="font-size:11px;color:var(--text-muted);margin:5px 0 0;"><span style="background:{trend_bg};color:{trend_text_color};padding:1px 6px;border-radius:10px;font-size:10px;">{'+' if trend > 0 else ''}{round(trend, 3)}</span></p>
            </div>
            <div>
                <p style="font-size:12px;color:var(--text-muted);margin:0 0 4px;">Last week activity</p>
                <p style="font-size:15px;font-weight:600;color:var(--text-primary);margin:0;">{last_week}%</p>
                <div class="bar-track"><div class="bar-fill" style="width:{min(last_week,100)}%;background:var(--risk-low);"></div></div>
                <p style="font-size:11px;color:var(--text-muted);margin:5px 0 0;">{'Active last week' if last_week >= 50 else 'Low activity last week'}</p>
            </div>
            <div>
                <p style="font-size:12px;color:var(--text-muted);margin:0 0 4px;">Activity consistency</p>
                <p style="font-size:15px;font-weight:600;color:var(--text-primary);margin:0;">{variability_label}</p>
                <div class="bar-track"><div class="bar-fill" style="width:{variability_score}%;background:{variability_color};"></div></div>
                <p style="font-size:11px;color:var(--text-muted);margin:5px 0 0;font-style:italic;">{variability_message}</p>
            </div>
        </div>
    </div>

    # ---- resource engagement calculation ----
    resource_cols = ['dataplus', 'dualpane', 'externalquiz', 'folder', 'forumng', 'glossary', 'homepage', 
                     'htmlactivity', 'oucollaborate', 'oucontent', 'oucolluminate', 'ouwiki', 'page', 
                     'questionnaire', 'quiz', 'repeatactivity', 'resource', 'sharedsubpage', 'subpage', 'url']
    
    # Categories
    assessment = sum([student.get(col, 0) for col in ['quiz', 'externalquiz', 'questionnaire']])
    content = sum([student.get(col, 0) for col in ['page', 'htmlactivity', 'oucontent', 'resource', 'url']])
    collaboration = sum([student.get(col, 0) for col in ['forumng', 'ouwiki', 'oucollaborate', 'oucolluminate']])
    organization = sum([student.get(col, 0) for col in ['folder', 'subpage', 'sharedsubpage', 'homepage']])
    practice = sum([student.get(col, 0) for col in ['repeatactivity', 'dataplus', 'dualpane', 'glossary']])
    
    total_resource_clicks = assessment + content + collaboration + organization + practice
    if total_resource_clicks == 0:
        total_resource_clicks = 1  # Prevent division by zero
    
    assessment_pct = int((assessment / total_resource_clicks) * 100)
    content_pct = int((content / total_resource_clicks) * 100)
    collaboration_pct = int((collaboration / total_resource_clicks) * 100)
    organization_pct = int((organization / total_resource_clicks) * 100)
    practice_pct = int((practice / total_resource_clicks) * 100)
    
    # Zero-engagement alert
    assessment_alert = "⚠️ You haven't attempted any assessments yet this module." if assessment == 0 else ""
    
    # Resource diversity
    diversity = round(float(student.get("resource_diversity", 0)), 2)
    diversity_pct = int(diversity * 100)
    if diversity >= 0.6:
        diversity_label = "Broad"
        diversity_message = "✓ Excellent content exploration — you're engaging with diverse resources."
    elif diversity >= 0.3:
        diversity_label = "Moderate"
        diversity_message = "Good variety of resources — consider exploring additional content types."
    else:
        diversity_label = "Narrow"
        diversity_message = "Try exploring different content types — quizzes, wikis, and forums alongside readings."
    
    st.markdown(f"""
    <p class="sv-label">Assessment habits</p>
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:28px;">
        <div class="app-card">
            <p style="font-size:12px;color:var(--text-muted);margin:0 0 12px;">Submission behaviour</p>
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;">
                <span style="font-size:13px;color:var(--text-primary);">Late submission ratio</span>
                <span style="font-size:13px;font-weight:600;color:{proc_bar};">{late_ratio}%</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:{late_ratio}%;background:{proc_bar};"></div></div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin:14px 0 4px;">
                <span style="font-size:13px;color:var(--text-primary);">Assessment week engagement</span>
                <span style="font-size:13px;font-weight:600;color:var(--blue);">{assess_eng}%</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:{assess_eng_bar}%;background:var(--blue);"></div></div>
        </div>
        <div class="app-card">
            <p style="font-size:12px;color:var(--text-muted);margin:0 0 10px;">Procrastination score</p>
            <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:8px;">
                <span style="font-size:28px;font-weight:600;color:var(--text-primary);">{proc_score}</span>
                <span style="font-size:12px;color:{proc_text};background:{proc_bg};padding:2px 8px;border-radius:20px;">{proc_label}</span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:{int(proc_score*100)}%;background:{proc_bar};"></div></div>
            <p style="font-size:12px;color:var(--text-muted);margin:10px 0 0;line-height:1.5;">
                {'You tend to start assessments close to the deadline.' if proc_score > 0.4 else 'You generally start assessments with good lead time.'}
            </p>
        </div>
    </div>

    <p class="sv-label">Resource engagement breakdown</p>
    <div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-bottom:28px;">
        <div class="app-card">
            <p class="section-label" style="margin:0 0 8px;">Assessment</p>
            <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{int(assessment)}</p>
            <div class="bar-track"><div class="bar-fill" style="width:{assessment_pct}%;background:var(--risk-high);"></div></div>
            <p style="font-size:10px;color:var(--text-muted);margin:6px 0 0;">{assessment_pct}% of activity</p>
        </div>
        <div class="app-card">
            <p class="section-label" style="margin:0 0 8px;">Content</p>
            <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{int(content)}</p>
            <div class="bar-track"><div class="bar-fill" style="width:{content_pct}%;background:var(--blue);"></div></div>
            <p style="font-size:10px;color:var(--text-muted);margin:6px 0 0;">{content_pct}% of activity</p>
        </div>
        <div class="app-card">
            <p class="section-label" style="margin:0 0 8px;">Collaboration</p>
            <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{int(collaboration)}</p>
            <div class="bar-track"><div class="bar-fill" style="width:{collaboration_pct}%;background:var(--accent);"></div></div>
            <p style="font-size:10px;color:var(--text-muted);margin:6px 0 0;">{collaboration_pct}% of activity</p>
        </div>
        <div class="app-card">
            <p class="section-label" style="margin:0 0 8px;">Organization</p>
            <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{int(organization)}</p>
            <div class="bar-track"><div class="bar-fill" style="width:{organization_pct}%;background:var(--text-label);"></div></div>
            <p style="font-size:10px;color:var(--text-muted);margin:6px 0 0;">{organization_pct}% of activity</p>
        </div>
        <div class="app-card">
            <p class="section-label" style="margin:0 0 8px;">Practice</p>
            <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{int(practice)}</p>
            <div class="bar-track"><div class="bar-fill" style="width:{practice_pct}%;background:var(--risk-mod);"></div></div>
            <p style="font-size:10px;color:var(--text-muted);margin:6px 0 0;">{practice_pct}% of activity</p>
        </div>
    </div>
    
    <div class="app-card" style="margin-bottom:28px;">
        <p class="section-label" style="margin:0 0 12px;">Content Exploration Score</p>
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;">
            <span style="font-size:13px;color:var(--text-muted);">Resource Diversity</span>
            <span style="font-size:16px;font-weight:600;color:var(--text-primary);">{diversity_pct}%</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:{diversity_pct}%;background:{'var(--risk-low)' if diversity >= 0.6 else 'var(--risk-mod)' if diversity >= 0.3 else 'var(--risk-high)'};"></div></div>
        <p style="font-size:12px;color:var(--text-muted);margin:8px 0 0;line-height:1.4;">
            {diversity_label} — {diversity_message}
        </p>
    </div>
    
    {'<div class="app-card" style="background:rgba(255,77,109,0.1);border:1px solid var(--risk-high);margin-bottom:28px;"><p style="color:var(--risk-high);font-weight:600;margin:0;">' + assessment_alert + '</p></div>' if assessment_alert else ''}
    
    <p class="sv-label">Study suggestions</p>
    <div class="app-card">
        {tips_html}
    </div>
    
    {explainability_html}
    """, unsafe_allow_html=True)

# ==================================================
# ACADEMIC DEVELOPER VIEW
# ==================================================
elif role == "Academic Developer":
 
<<<<<<< HEAD
    # ---- cohort stats ----
    total  = df["id_student"].nunique()
    n_high = int((df["risk_level"] == "High Risk").sum())
    n_mod  = int((df["risk_level"] == "Moderate Risk").sum())
    n_low  = int((df["risk_level"] == "Low Risk").sum())
    pct_hi = round(n_high / total * 100)
    pct_md = round(n_mod  / total * 100)
    pct_lo = round(n_low  / total * 100)
 
    # ---- header section ----
    st.markdown('<p class="app-title">Academic Risk Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Decision-support for targeted student interventions</p>', unsafe_allow_html=True)
    st.markdown("")
    
    # ---- 6.2: Bulk action summary ----
    st.markdown('<p class="section-label">Action Summary</p>', unsafe_allow_html=True)
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        st.markdown(f"""
        <div class="app-card" style="border-left:3px solid var(--risk-high);">
            <p class="section-label" style="margin:0 0 8px;color:var(--risk-high);">Immediate Outreach</p>
            <p class="data-number" style="margin:0;color:var(--risk-high);">{n_high}</p>
            <p style="font-size:11px;color:var(--text-muted);margin:6px 0 0;">High risk students</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📥 Download High Risk List"):
            high_risk_export = df[df["risk_level"] == "High Risk"][["id_student", "code_module", "predicted_proba_risk", "active_weeks", "num_submissions"]].to_csv(index=False)
            st.download_button("Download CSV", high_risk_export, "high_risk_students.csv", "text/csv")
    
    with action_col2:
        st.markdown(f"""
        <div class="app-card" style="border-left:3px solid var(--risk-mod);">
            <p class="section-label" style="margin:0 0 8px;color:var(--risk-mod);">Monitor & Support</p>
            <p class="data-number" style="margin:0;color:var(--risk-mod);">{n_mod}</p>
            <p style="font-size:11px;color:var(--text-muted);margin:6px 0 0;">Moderate risk students</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📥 Download Moderate Risk List"):
            mod_risk_export = df[df["risk_level"] == "Moderate Risk"][["id_student", "code_module", "predicted_proba_risk", "active_weeks", "num_submissions"]].to_csv(index=False)
            st.download_button("Download CSV", mod_risk_export, "moderate_risk_students.csv", "text/csv")
    
    with action_col3:
        st.markdown(f"""
        <div class="app-card" style="border-left:3px solid var(--risk-low);">
            <p class="section-label" style="margin:0 0 8px;color:var(--risk-low);">Maintain Progress</p>
            <p class="data-number" style="margin:0;color:var(--risk-low);">{n_low}</p>
            <p style="font-size:11px;color:var(--text-muted);margin:6px 0 0;">Low risk students</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ---- risk overview cards ----
    st.markdown('<p class="section-label">Risk Overview</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:8px;">Total Students</p>
            <p class="data-number" style="margin:0;color:var(--text-primary);">{total}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:8px;color:var(--risk-high);">High Risk</p>
            <p class="data-number" style="margin:0;color:var(--risk-high);">{n_high}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:8px;color:var(--risk-mod);">Moderate Risk</p>
            <p class="data-number" style="margin:0;color:var(--risk-mod);">{n_mod}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:8px;color:var(--risk-low);">Low Risk</p>
            <p class="data-number" style="margin:0;color:var(--risk-low);">{n_low}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
 
    # ---- risk distribution bar ----
    dist_html = (
        '<div class="app-card" style="margin-bottom:24px;">'
        '<p class="section-label" style="margin:0 0 12px;">Risk Distribution</p>'
        '<div style="display:flex;gap:3px;height:24px;border-radius:6px;overflow:hidden;margin-bottom:12px;">'
        '<div style="width:' + str(pct_hi) + '%;background:var(--risk-high);"></div>'
        '<div style="width:' + str(pct_md) + '%;background:var(--risk-mod);"></div>'
        '<div style="width:' + str(pct_lo) + '%;background:var(--risk-low);"></div>'
        '</div>'
        '<div style="display:flex;gap:20px;font-size:12px;">'
        '<span style="display:flex;align-items:center;gap:5px;">'
        '<span style="width:10px;height:10px;border-radius:2px;background:var(--risk-high);display:inline-block;"></span>'
        '<span style="color:var(--text-muted);">High risk ' + str(pct_hi) + '%</span></span>'
        '<span style="display:flex;align-items:center;gap:5px;">'
        '<span style="width:10px;height:10px;border-radius:2px;background:var(--risk-mod);display:inline-block;"></span>'
        '<span style="color:var(--text-muted);">Moderate ' + str(pct_md) + '%</span></span>'
        '<span style="display:flex;align-items:center;gap:5px;">'
        '<span style="width:10px;height:10px;border-radius:2px;background:var(--risk-low);display:inline-block;"></span>'
        '<span style="color:var(--text-muted);">Low risk ' + str(pct_lo) + '%</span></span>'
        '</div></div>'
    )
    st.markdown(dist_html, unsafe_allow_html=True)
    
    # ---- 5.2: Cohort equity breakdown panel ----
    st.markdown('<p class="section-label" style="margin-top:24px;">Equity Snapshot</p>', unsafe_allow_html=True)
    
    # IMD band analysis
    imd_dist = df["imd_band"].value_counts(dropna=False).to_dict()
    imd_html = '<div class="app-card" style="margin-bottom:12px;"><p style="font-size:12px;font-weight:600;color:var(--text-primary);margin:0 0 10px;">Deprivation (IMD Band)</p>'
    for band, count in sorted(imd_dist.items()):
        pct = int(count / len(df) * 100)
        # Flag high-deprivation bands
        is_high_dep = band in ['0-20%', '20-40%']
        imd_html += f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;"><span style="font-size:11px;color:var(--text-muted);">{band or "Unknown"}</span><span style="font-size:11px;font-weight:600;color:{"var(--risk-high)" if is_high_dep else "var(--text-primary)"};">{pct}%</span></div>'
    imd_html += '</div>'
    st.markdown(imd_html, unsafe_allow_html=True)
    
    # Risk by IMD band heatmap
    imd_risk = df.groupby("imd_band")["predicted_proba_risk"].mean().sort_values(ascending=False)
    imd_risk_html = '<div class="app-card" style="margin-bottom:12px;"><p style="font-size:12px;font-weight:600;color:var(--text-primary);margin:0 0 10px;">Average Risk by IMD Band</p>'
    for band, avg_risk in imd_risk.items():
        bar_width = int(avg_risk * 100)
        band_color = "var(--risk-high)" if avg_risk >= 0.7 else "var(--risk-mod)" if avg_risk >= 0.4 else "var(--risk-low)"
        imd_risk_html += f'<div style="margin-bottom:8px;"><div style="display:flex;justify-content:space-between;margin-bottom:2px;"><span style="font-size:11px;color:var(--text-muted);">{band or "Unknown"}</span><span style="font-size:11px;font-weight:600;color:{band_color};">{round(avg_risk, 2)}</span></div><div class="bar-track"><div class="bar-fill" style="width:{bar_width}%;background:{band_color};"></div></div></div>'
    imd_risk_html += '</div>'
    st.markdown(imd_risk_html, unsafe_allow_html=True)
    
    # Previous attempts breakdown
    attempts_dist = df["num_of_prev_attempts"].value_counts(sort=False).sort_index()
    first_attempt_pct = int(attempts_dist.get(0, 0) / len(df) * 100)
    repeat_pct = 100 - first_attempt_pct
    st.markdown(f"""
    <div class="app-card">
        <p style="font-size:12px;font-weight:600;color:var(--text-primary);margin:0 0 10px;">First Attempt vs. Repeat</p>
        <div style="display:flex;gap:3px;height:20px;border-radius:4px;overflow:hidden;margin-bottom:8px;">
            <div style="width:{first_attempt_pct}%;background:var(--risk-low);"></div>
            <div style="width:{repeat_pct}%;background:var(--risk-high);"></div>
        </div>
        <div style="display:flex;gap:12px;font-size:11px;">
            <span style="color:var(--text-muted);">First attempt: <strong>{first_attempt_pct}%</strong></span>
            <span style="color:var(--text-muted);">Repeat: <strong>{repeat_pct}%</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    # ---- filters (enhanced 5.4) ----
    st.markdown('<p class="section-label">Filter Students</p>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    filter_risk   = fc1.selectbox("Risk level",  ["All"] + ["High Risk", "Moderate Risk", "Low Risk"])
    filter_module = fc2.selectbox("Module",      ["All modules"] + sorted(df["code_module"].dropna().unique().tolist()))
    filter_region = fc3.selectbox("Region",      ["All regions"] + sorted(df["region"].dropna().unique().tolist()))
    
    # Additional equity filters
    fc4, fc5, fc6 = st.columns(3)
    filter_attempts = fc4.selectbox("Attempt type", ["All", "First attempt", "Repeat attempts"])
    filter_disability = fc5.selectbox("Disability status", ["All", "Declared (Y)", "Not declared (N)"])
    filter_age = fc6.selectbox("Age band", ["All"] + sorted([str(x) for x in df["age_band"].dropna().unique()]))
    
    # 8.2: Apply filters with loading state
    with st.spinner("Applying filters..."):
        filtered = df.copy()
        if filter_risk   != "All":         filtered = filtered[filtered["risk_level"]  == filter_risk]
        if filter_module != "All modules": filtered = filtered[filtered["code_module"] == filter_module]
        if filter_region != "All regions": filtered = filtered[filtered["region"]      == filter_region]
        if filter_attempts == "First attempt":
            filtered = filtered[filtered["num_of_prev_attempts"] == 0]
        elif filter_attempts == "Repeat attempts":
            filtered = filtered[filtered["num_of_prev_attempts"] > 0]
        if filter_disability == "Declared (Y)":
            filtered = filtered[filtered["disability"] == "Y"]
        elif filter_disability == "Not declared (N)":
            filtered = filtered[filtered["disability"] == "N"]
        if filter_age != "All":
            filtered = filtered[filtered["age_band"] == float(filter_age)]
    
    # ---- student table ----
    st.markdown('<p class="section-label">All Students</p>', unsafe_allow_html=True)
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
    
    with st.spinner("Loading student table..."):
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Student ID":  st.column_config.TextColumn("Student ID"),
                "Probability": st.column_config.ProgressColumn(
                    "Probability", min_value=0, max_value=1, format="%.3f"
                ),
            }
        )
    
    # ---- 5.3: Module-level risk heatmap ----
    st.markdown('<p class="section-label" style="margin-top:24px;">Module × Presentation Risk Heatmap</p>', unsafe_allow_html=True)
    
    heatmap_data = df.pivot_table(
        values="predicted_proba_risk",
        index="code_module",
        columns="code_presentation",
        aggfunc="mean"
    )
    
    heatmap_html = '<div class="app-card"><table style="width:100%;border-collapse:collapse;"><tr><th style="padding:8px;text-align:left;font-size:11px;color:var(--text-label);border-bottom:1px solid var(--border);">Module</th>'
    
    for col in heatmap_data.columns:
        heatmap_html += f'<th style="padding:8px;text-align:center;font-size:11px;color:var(--text-label);border-bottom:1px solid var(--border);">{col}</th>'
    
    heatmap_html += '</tr>'
    
    for idx, row in heatmap_data.iterrows():
        heatmap_html += f'<tr><td style="padding:8px;font-size:11px;color:var(--text-muted);border-bottom:1px solid var(--border);">{idx}</td>'
        for val in row:
            if pd.isna(val):
                cell_color = "rgba(255,255,255,0.04)"
                cell_text = "—"
            else:
                val_pct = int(val * 100)
                if val >= 0.7:
                    cell_color = "rgba(255,77,109,0.3)"
                elif val >= 0.4:
                    cell_color = "rgba(255,179,71,0.3)"
                else:
                    cell_color = "rgba(0,212,184,0.3)"
                cell_text = f"{val:.2f}"
            heatmap_html += f'<td style="padding:8px;text-align:center;background:{cell_color};border-bottom:1px solid var(--border);font-size:11px;font-weight:600;color:var(--text-primary);">{cell_text}</td>'
        heatmap_html += '</tr>'
    
    heatmap_html += '</table></div>'
    st.markdown(heatmap_html, unsafe_allow_html=True)
 
    st.divider()
=======
    st.title("Academic Risk Analytics")
    st.caption("Decision-support for targeted student interventions")
 
    st.subheader("Risk Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", df["id_student"].nunique())
    col2.metric("High Risk", (df["risk_level"] == "High Risk").sum())
    col3.metric("Moderate Risk", (df["risk_level"] == "Moderate Risk").sum())
    col4.metric("Low Risk", (df["risk_level"] == "Low Risk").sum())
>>>>>>> parent of 63933a2 (update again)
 
    # ---- student drill-down ----
    st.markdown('<p class="section-label">Student Profile</p>', unsafe_allow_html=True)
    selected_student = st.selectbox("Select Student", sorted(df["id_student"].unique()), help="Choose a student to view their profile and engagement metrics")
    student = df[df["id_student"] == selected_student].iloc[0]
 
    risk_prob = round(float(safe_numeric(student["predicted_proba_risk"])), 3)
    if risk_prob >= 0.7:
        risk_color = "var(--risk-high)"
        risk_icon = "🔴"
        risk_label = "High Risk"
    elif risk_prob >= 0.4:
        risk_color = "var(--risk-mod)"
        risk_icon = "🟡"
        risk_label = "Moderate Risk"
    else:
        risk_color = "var(--risk-low)"
        risk_icon = "🟢"
        risk_label = "Low Risk"
    
    st.markdown(f"""
    <div class="app-card" style="margin-bottom:24px;">
        <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;">
            <div>
                <p class="section-label" style="margin-bottom:8px;">Risk Probability</p>
                <p class="data-number" style="margin:0;color:{risk_color};">{risk_icon} {risk_prob}</p>
            </div>
            <div>
                <p class="section-label" style="margin-bottom:8px;">Risk Level</p>
                <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{safe_display(student.get('risk_level', 'Unknown'))}</p>
            </div>
            <div>
                <p class="section-label" style="margin-bottom:8px;">Final Result</p>
                <p style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0;">{safe_display(student.get('final_result', '—'))}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ---- 5.1: Demographic context panel ----
    imd_band = safe_display(student.get("imd_band", "—"))
    num_attempts = int(safe_numeric(student.get("num_of_prev_attempts", 0)))
    disability = safe_display(student.get("disability", "—"))
    age_band = safe_display(student.get("age_band", "—"))
    
    demographic_notes = []
    
    if imd_band in ["0-20%", "20-40%"]:
        demographic_notes.append(f"📍 <strong>High deprivation area ({imd_band})</strong> — Consider access/connectivity barriers before intervention.")
    
    if num_attempts > 1:
        demographic_notes.append(f"🔄 <strong>Repeat attempt (#{num_attempts})</strong> — Repeated attempts increase risk independent of engagement.")
    
    if disability == "Y":
        demographic_notes.append("♿ <strong>Disability declared</strong> — Ensure outreach via agreed support channels.")
    
    if age_band and str(age_band) not in ["—", "NaN"]:
        try:
            age_val = float(age_band)
            if age_val >= 55:
                demographic_notes.append(f"👥 <strong>Mature student ({int(age_val)}+)</strong> — Work/care commitments may affect engagement.")
        except:
            pass
    
    if demographic_notes:
        st.markdown('<p class="section-label">Demographic Context</p>', unsafe_allow_html=True)
        demo_html = '<div class="app-card" style="margin-bottom:24px;border-left:3px solid var(--accent);">'
        for note in demographic_notes:
            demo_html += f'<p style="font-size:12px;color:var(--text-muted);margin:8px 0;line-height:1.4;">{note}</p>'
        demo_html += '</div>'
        st.markdown(demo_html, unsafe_allow_html=True)
 
    st.markdown('<p class="section-label">Key Engagement Indicators</p>', unsafe_allow_html=True)
    ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)
    
    with ind_col1:
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:6px;">Active Weeks</p>
            <p style="font-size:18px;font-weight:600;color:var(--text-primary);margin:0;">{int(safe_numeric(student.get('active_weeks', 0)))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with ind_col2:
        trend_val = round(float(safe_numeric(student.get("engagement_trend", 0))), 3)
        trend_color = "var(--risk-low)" if trend_val > 0 else "var(--risk-high)"
        trend_icon = "↑" if trend_val > 0 else "↓"
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:6px;">Engagement Trend</p>
            <p style="font-size:18px;font-weight:600;color:{trend_color};margin:0;">{trend_icon} {abs(trend_val)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with ind_col3:
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:6px;">Submissions</p>
            <p style="font-size:18px;font-weight:600;color:var(--text-primary);margin:0;">{int(safe_numeric(student.get('num_submissions', 0)))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with ind_col4:
        proc_score = round(float(safe_numeric(student.get("procrastination_score", 0))), 2)
        st.markdown(f"""
        <div class="app-card">
            <p class="section-label" style="margin-bottom:6px;">Procrastination Score</p>
            <p style="font-size:18px;font-weight:600;color:var(--text-primary);margin:0;">{proc_score}</p>
        </div>
        """, unsafe_allow_html=True)
 
    # ---- 6.1: Stratified recommendations by risk tier & context ----
    st.markdown('<p class="section-label">Recommended Interventions</p>', unsafe_allow_html=True)
    
    # Collect context factors
    is_first_attempt = num_attempts == 0
    is_high_deprivation = imd_band in ["0-20%", "20-40%"]
    is_disabled = disability == "Y"
    is_mature = False
    try:
        age_val = float(age_band)
        is_mature = age_val >= 55
    except:
        pass
    
    low_engagement = safe_numeric(student.get("early_engagement", 50)) < 50
    negative_trend = safe_numeric(student.get("engagement_trend", 0)) < 0
    low_submissions = safe_numeric(student.get("num_submissions", 0)) < 3
    high_procrastination = safe_numeric(student.get("procrastination_score", 0)) > 0.4
    low_activity_weeks = safe_numeric(student.get("active_weeks", 0)) < 5
    low_diversity = safe_numeric(student.get("resource_diversity", 0)) < 0.4
    
    # Build stratified interventions
    interventions = []
    
    if risk_prob >= 0.7:  # HIGH RISK
        if is_first_attempt and is_high_deprivation:
            interventions.append(("🚨", "URGENT: Immediate personal outreach", "First attempt + high deprivation area. Likely disengagement or access barriers."))
        elif is_first_attempt:
            interventions.append(("🔴", "Personal outreach required", "High risk on first attempt. Immediate academic check-in needed."))
        
        if num_attempts > 1:
            interventions.append(("🔄", "Academic counselling", "Systematic issue with repeated attempts. Consider deeper intervention."))
        
        if is_disabled:
            interventions.append(("♿", "Coordinate with disability support", "Work with disability services to ensure appropriate accommodations."))
        
        if is_mature:
            interventions.append(("👥", "Flexible deadline discussion", "Mature student — consider workload/care commitments."))
        
        if high_procrastination or negative_trend:
            interventions.append(("⏰", "Study skills + coaching", "Procrastination/engagement decline. Offer time-management support."))
    
    elif risk_prob >= 0.4:  # MODERATE RISK
        if low_diversity:
            interventions.append(("📚", "Content recommendation email", "Limited resource diversity. Send targeted content suggestions."))
        
        if high_procrastination and low_submissions:
            interventions.append(("✅", "Assessment encouragement", "Late submission pattern + few submissions. Encourage early engagement."))
        
        if negative_trend:
            interventions.append(("📈", "Engagement monitoring", "Declining activity. Monitor closely and follow up in 2 weeks."))
    
    else:  # LOW RISK
        interventions.append(("✓", "Monitor only", "No immediate action required. Continue routine monitoring."))
    
    if interventions:
        interventions_html = '<div class="app-card" style="border-left:4px solid var(--accent);">'
        for icon, title, desc in interventions:
            color = "var(--risk-high)" if "URGENT" in title else "var(--accent)"
            interventions_html += f'''
            <div style="margin-bottom:14px;padding:10px;background:rgba(255,255,255,0.02);border-radius:6px;">
                <p style="font-size:12px;font-weight:600;color:{color};margin:0;">{icon} {title}</p>
                <p style="font-size:11px;color:var(--text-muted);margin:4px 0 0;">{desc}</p>
            </div>
            '''
        interventions_html += '</div>'
        st.markdown(interventions_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="app-card" style="background:rgba(0,212,184,0.1);border:1px solid var(--risk-low);">
            <p style="color:var(--risk-low);font-weight:600;margin:0;">✓ No interventions needed at this time.</p>
        </div>
        """, unsafe_allow_html=True)