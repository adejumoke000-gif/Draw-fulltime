import streamlit as st
import math
from datetime import date

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="Draw Hunter Pro (Manual Mode)",
    page_icon="⚽",
    layout="wide"
)

# ============================
# STYLE (NO YELLOW)
# ============================
st.markdown("""
<style>
.verdict-box {padding:18px;border-radius:10px;text-align:center;margin:15px 0}
.strong-draw {background:#1e7f4f;color:white;}
.moderate-draw {background:#0b5ed7;color:white;}
.avoid {background:#a11a1a;color:white;}
.small-box {background:#222;padding:12px;border-radius:8px;margin-top:10px}
</style>
""", unsafe_allow_html=True)

# ============================
# LEAGUES A–Z
# ============================
ALL_LEAGUES = [
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
# POISSON CORE
# ============================
def poisson_prob(k, lam):
    return (lam ** k) * math.exp(-lam) / math.factorial(k)

def draw_probability(lambda_A, lambda_B, max_goals=10):
    prob = 0.0
    for k in range(max_goals + 1):
        prob += poisson_prob(k, lambda_A) * poisson_prob(k, lambda_B)
    return prob

def estimate_lambda(goals):
    return sum(goals) / len(goals) if goals else 0.0

# ============================
# HIDDEN HALFTIME PENALTY (HOTSPOT)
# ============================
HALFTIME_PENALTY = 0.12   # 🔥 internal only – NOT shown on UI

# ============================
# MAIN UI
# ============================
st.title("🎯 Draw Hunter Pro — Manual Prediction Engine")

# --- MATCH INFO ---
st.subheader("📌 Match Information")
league = st.selectbox("Select League", ALL_LEAGUES)
fixture_name = st.text_input("Fixture (Home vs Away)")
match_date = st.date_input("Match Date", value=date.today())

# --- GOALS ---
st.subheader("⚽ Team Goal History (Last 5–8 Matches)")

col1, col2 = st.columns(2)

with col1:
    home_goals = st.text_input("Home goals (comma separated)", "1,1,0,2,1")

with col2:
    away_goals = st.text_input("Away goals (comma separated)", "0,1,1,1,2")

# --- CONTEXT ---
st.subheader("📊 Context")
avg_goals = st.number_input("League average goals", 0.8, 4.0, 2.2, 0.1)
table_gap = st.number_input("Table position gap", 0, 20, 3, 1)
draw_odds = st.number_input("Market draw odds", 1.5, 10.0, 3.10, 0.05)

# ============================
# ANALYSIS
# ============================
if st.button("🔍 Analyze Match"):
    try:
        home_list = [int(x.strip()) for x in home_goals.split(",")]
        away_list = [int(x.strip()) for x in away_goals.split(",")]
    except:
        st.error("❌ Goals must be numbers separated by commas")
        st.stop()

    lambda_home = estimate_lambda(home_list)
    lambda_away = estimate_lambda(away_list)

    # FULL TIME DRAW
    ft_draw_prob = draw_probability(lambda_home, lambda_away)

    # HALFTIME DRAW (penalty applied silently)
    ht_lambda_home = lambda_home * 0.45
    ht_lambda_away = lambda_away * 0.45
    ht_draw_raw = draw_probability(ht_lambda_home, ht_lambda_away)
    ht_draw_prob = max(ht_draw_raw - HALFTIME_PENALTY, 0)

    # ============================
    # SCORING
    # ============================
    score = 0
    if ft_draw_prob >= 0.25: score += 1
    if abs(lambda_home - lambda_away) <= 0.30: score += 1
    if table_gap <= 4: score += 1
    if 2.8 <= draw_odds <= 3.6: score += 1
    if ht_draw_prob >= 0.35: score += 1

    # ============================
    # VERDICT
    # ============================
    if score >= 4:
        verdict, css, advice = "🟢 PLAY DRAW", "strong-draw", "Strong statistical draw profile"
    elif score == 3:
        verdict, css, advice = "🔵 WATCHLIST", "moderate-draw", "Live confirmation recommended"
    else:
        verdict, css, advice = "🔴 NO BET", "avoid", "High volatility or mismatch"

    st.markdown(f"""
    <div class="verdict-box {css}">
        <h2>{verdict}</h2>
        <h3>Score: {score}/5</h3>
        <p>{advice}</p>
        <p><b>League:</b> {league}</p>
        <p><b>Fixture:</b> {fixture_name}</p>
        <p><b>Date:</b> {match_date}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="small-box">
    <h4>📈 Probability Outputs</h4>
    """, unsafe_allow_html=True)

    st.write(f"**Full-Time Draw Probability:** {ft_draw_prob*100:.2f}%")
    st.write(f"**Halftime Draw Probability:** {ht_draw_prob*100:.2f}%")

    st.markdown("</div>", unsafe_allow_html=True)
