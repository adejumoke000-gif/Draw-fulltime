import streamlit as st
import requests

# ============================
# CONFIG
# ============================
st.set_page_config(
    page_title="Draw Hunter Pro",
    page_icon="⚽",
    layout="wide"
)

# ============================
# CUSTOM CSS
# ============================
st.markdown("""
<style>
.verdict-box {padding:18px;border-radius:10px;text-align:center;margin:15px 0}
.strong-draw {background:#1e7f4f;color:white;}
.moderate-draw {background:#0b5ed7;color:white;}
.avoid {background:#a11a1a;color:white;}
</style>
""", unsafe_allow_html=True)

# ============================
# API HELPERS
# ============================
API_HOST = "https://api-football-v1.p.rapidapi.com/v3"

def fetch_api(api_key, endpoint, params=None):
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    try:
        r = requests.get(f"{API_HOST}/{endpoint}", headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

def get_fixture_by_id(api_key, fixture_id):
    data = fetch_api(api_key, f"fixtures/{fixture_id}")
    if data and data.get("response"):
        return data["response"][0]
    return None

def get_team_id(api_key, team_name):
    data = fetch_api(api_key, "teams", {"search": team_name})
    if data and data.get("response"):
        return data["response"][0]["team"]["id"]
    return None

def get_h2h_draws(api_key, home, away):
    home_id = get_team_id(api_key, home)
    away_id = get_team_id(api_key, away)
    if not home_id or not away_id:
        return None
    data = fetch_api(api_key, "fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "last": 5})
    if not data or not data.get("response"):
        return None
    draws = 0
    for m in data["response"]:
        if m["goals"]["home"] == m["goals"]["away"]:
            draws += 1
    return draws

def api_status_badge(used_api):
    if used_api:
        st.success("📡 Live API data used")
    else:
        st.warning("⚠️ API not used or failed")

# ============================
# FULL COUNTRY LIST (A–Z)
# ============================
ALL_COUNTRIES = [
    "Albania","Algeria","Andorra","Argentina","Australia","Austria","Azerbaijan","Bahrain",
    "Belgium","Brazil","Bulgaria","Burundi","Chile","Colombia","Costa Rica","Croatia","Cyprus",
    "Czechia","Denmark","Denmark Amateur","Egypt","El Salvador","England","England Amateur",
    "Ethiopia","France","Germany","Germany Amateur","Greece","Guatemala","Honduras","Hungary",
    "Iceland","Indonesia","International","International Clubs","International Youth","Iran","Iraq",
    "Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kuwait","Lebanon","Luxembourg","Malaysia",
    "Malta","Mexico","Netherlands","Nicaragua","Northern Ireland","Oman","Panama","Paraguay",
    "Peru","Poland","Portugal","Qatar","Romania","Russia","Rwanda","Saudi Arabia","Scotland",
    "Serbia","Singapore","Slovakia","Slovenia","South Africa","Spain","Spain Amateur","Sweden",
    "Switzerland","Tanzania","Thailand","Trinidad and Tobago","Turkiye","United Arab Emirates",
    "Uruguay","USA","Venezuela","Vietnam","Wales"
]

# ============================
# SIDEBAR
# ============================
st.sidebar.header("⚙️ Settings / API Key")
api_key = st.sidebar.text_input("API-Football Key", type="password", value=st.secrets.get("API_FOOTBALL_KEY",""))
st.sidebar.markdown("🔹 Paste your key above to enable live data")

if "api_calls" not in st.session_state:
    st.session_state["api_calls"] = 0
st.sidebar.metric("API Calls Today", st.session_state["api_calls"])

st.sidebar.markdown("---")
st.sidebar.subheader("Country Leagues (A–Z)")
st.sidebar.write(", ".join(ALL_COUNTRIES))

# ============================
# MAIN UI
# ============================
st.title("🎯 Draw Hunter Pro – Full League Support")

fixture_id = st.text_input("📌 Enter MATCH Fixture ID (API-Football Match ID)")

home = st.text_input("Home Team Name (text)")
away = st.text_input("Away Team Name (text)")

avg_goals = st.number_input("Average goals (both teams)", 0.3, 5.0, 1.20, 0.05)
table_gap = st.number_input("Table position gap", 0, 20, 3, 1)
draw_odds = st.number_input("Market draw odds", 1.5, 10.0, 3.10, 0.05)

manual_h2h = st.number_input("Manual H2H draws (0–5)", 0, 5, 2, 1)

if st.button("🔍 Analyze Draw"):
    used_api = False
    h2h_draws = manual_h2h

    # -- FETCH FIXTURE INFO IF ID PROVIDED --
    if api_key and fixture_id.strip():
        fixture_data = get_fixture_by_id(api_key, fixture_id.strip())
        st.session_state["api_calls"] += 1
        if fixture_data:
            used_api = True
            st.markdown(f"**Match found:** {fixture_data['teams']['home']['name']} vs {fixture_data['teams']['away']['name']} | {fixture_data['league']['name']}")
        else:
            st.error("❌ No match found with that fixture ID")

    # -- H2H API --
    if api_key and home and away:
        api_h2h = get_h2h_draws(api_key, home, away)
        st.session_state["api_calls"] += 1
        if api_h2h is not None:
            h2h_draws = api_h2h
            used_api = True

    # -- SCORE MODEL --
    score = 0
    if avg_goals <= 1.6:
        score += 1
    if table_gap <= 4:
        score += 1
    if 2.8 <= draw_odds <= 3.6:
        score += 1
    if h2h_draws >= 2:
        score += 1
    if avg_goals <= 1.4 and table_gap <= 2:
        score += 1

    # -- VERDICT (NO YELLOW) --
    if score >= 4:
        verdict = "🟢 PLAY DRAW"
        css = "strong-draw"
        advice = "Single bet recommended"
    elif score == 3:
        verdict = "🔵 WATCHLIST"
        css = "moderate-draw"
        advice = "Observe live only"
    else:
        verdict = "🔴 NO BET"
        css = "avoid"
        advice = "Skip"

    st.markdown(f"""
    <div class="verdict-box {css}">
        <h2>{verdict}</h2>
        <h3>Score: {score}/5</h3>
        <p>{advice}</p>
        <p>H2H Draws (last 5): {h2h_draws}</p>
    </div>
    """, unsafe_allow_html=True)

    api_status_badge(used_api)
