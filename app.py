import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Draw Hunter Pro",
    page_icon="🎯",
    layout="wide"
)

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
.main-header {font-size:2.5rem;font-weight:800;text-align:center;color:#1E3A8A}
.verdict-box {padding:20px;border-radius:10px;text-align:center;margin:10px 0}
.strong-draw {background:#d4edda;border:2px solid #28a745}
.moderate-draw {background:#fff3cd;border:2px solid #ffc107}
.avoid {background:#f8d7da;border:2px solid #dc3545}
.layer-box {padding:10px;border-radius:5px;background:white;border-left:5px solid;margin-bottom:6px}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-header">🎯 Draw Hunter Pro</div>', unsafe_allow_html=True)
st.markdown("### Low-Tier Leagues • Draw-Only Model • API Powered")
st.markdown("---")

# =========================================================
# LOW-TIER LEAGUES DATABASE
# =========================================================
LOWER_LEAGUES = {

    # AFRICA
    "South Africa PSL": {"draw_rate": 31, "api_id": 288},
    "Kenya FKF Premier League": {"draw_rate": 30, "api_id": 343},
    "Botswana Premier League": {"draw_rate": 33, "api_id": 362},
    "Zimbabwe Premier League": {"draw_rate": 32, "api_id": 361},

    # CENTRAL AMERICA
    "Costa Rica Primera": {"draw_rate": 29, "api_id": 163},
    "Honduras Liga Nacional": {"draw_rate": 30, "api_id": 164},
    "Guatemala Liga Nacional": {"draw_rate": 31, "api_id": 165},

    # SOUTH AMERICA
    "Uruguay Primera Division": {"draw_rate": 32, "api_id": 268},
    "Paraguay Primera Division": {"draw_rate": 31, "api_id": 269},

    # ASIA
    "Bangladesh Premier League": {"draw_rate": 34, "api_id": 319},
    "Philippines Football League": {"draw_rate": 35, "api_id": 332},
    "Vietnam V-League 1": {"draw_rate": 30, "api_id": 292},
}

# =========================================================
# API UTILITIES
# =========================================================
def get_current_season():
    today = datetime.now()
    return today.year if today.month >= 7 else today.year - 1

def fetch_api(api_key, endpoint, params=None):
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    url = f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}"
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

def get_team_id(api_key, team_name):
    data = fetch_api(api_key, "teams", {"search": team_name})
    if data and data["response"]:
        return data["response"][0]["team"]["id"]
    return None

def get_h2h_draws(api_key, home, away):
    home_id = get_team_id(api_key, home)
    away_id = get_team_id(api_key, away)
    if not home_id or not away_id:
        return 0

    params = {"h2h": f"{home_id}-{away_id}", "last": 5}
    data = fetch_api(api_key, "fixtures/headtohead", params)
    if not data:
        return 0

    draws = 0
    for m in data["response"]:
        if m["goals"]["home"] == m["goals"]["away"]:
            draws += 1
    return draws

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.secrets.get("API_FOOTBALL_KEY") or st.text_input(
        "API-Football Key", type="password"
    )

    if api_key:
        st.success("API key loaded")

    st.markdown("---")

    l1_min = st.slider("League Draw % Min", 25, 35, 30)
    l2_goal_max = st.slider("Avg Goals Max", 0.8, 1.6, 1.2)

# =========================================================
# MAIN INPUT
# =========================================================
col1, col2 = st.columns(2)

with col1:
    league = st.selectbox("Select Low-Tier League", list(LOWER_LEAGUES.keys()))
    home = st.text_input("Home Team")
    away = st.text_input("Away Team")

with col2:
    avg_goals = st.slider("Average Goals", 0.5, 3.0, 1.2, 0.05)
    table_gap = st.slider("Table Position Gap", 0, 20, 3)
    draw_odds = st.slider("Draw Odds", 2.0, 5.0, 3.1, 0.1)

# =========================================================
# RUN ANALYSIS
# =========================================================
if st.button("🚀 Run Draw Analysis", use_container_width=True):

    scores = []
    league_rate = LOWER_LEAGUES[league]["draw_rate"]

    # L1 League Bias
    scores.append(1 if league_rate >= l1_min else 0)

    # L2 Goal Density
    scores.append(1 if avg_goals <= l2_goal_max else 0)

    # L3 Strength Parity
    scores.append(1 if table_gap <= 3 else 0)

    # L4 Market Odds
    scores.append(1 if 2.8 <= draw_odds <= 3.6 else 0)

    # L5 H2H
    h2h_draws = get_h2h_draws(api_key, home, away) if api_key else 0
    scores.append(1 if h2h_draws >= 2 else 0)

    total = sum(scores)

    if total >= 4:
        verdict, css = "🔵 STRONG DRAW", "strong-draw"
    elif total == 3:
        verdict, css = "🟡 MODERATE", "moderate-draw"
    else:
        verdict, css = "🔴 AVOID", "avoid"

    st.markdown(f"""
    <div class="verdict-box {css}">
        <h2>{verdict}</h2>
        <h3>Score: {total}/5</h3>
        <p>H2H Draws (last 5): {h2h_draws}</p>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure(go.Bar(
        x=["League", "Goals", "Parity", "Odds", "H2H"],
        y=scores,
        text=scores,
        textposition="auto"
    ))
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
