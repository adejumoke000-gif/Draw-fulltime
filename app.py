import streamlit as st
import math

# ============================
# CONFIG
# ============================
st.set_page_config(
    page_title="Draw Hunter Pro",
    page_icon="⚽",
    layout="wide"
)

# ============================
# CUSTOM CSS (NO YELLOW)
# ============================
st.markdown("""
<style>
.verdict-box {padding:18px;border-radius:10px;text-align:center;margin:15px 0}
.play {background:#1e7f4f;color:white;}
.watch {background:#0b5ed7;color:white;}
.avoid {background:#a11a1a;color:white;}
</style>
""", unsafe_allow_html=True)

# ============================
# FULL A–Z LEAGUE LIST
# ============================
LEAGUES = [
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
# POISSON FUNCTIONS
# ============================
def poisson_prob(k, lam):
    return (lam ** k) * math.exp(-lam) / math.factorial(k)

def draw_probability(lambda_A, lambda_B, max_goals=10):
    prob_draw = 0.0
    for k in range(max_goals + 1):
        prob_draw += poisson_prob(k, lambda_A) * poisson_prob(k, lambda_B)
    return prob_draw

def estimate_lambda(goals):
    if not goals:
        return 0
    return sum(goals) / len(goals)

# ============================
# MAIN UI
# ============================
st.title("🎯 Draw Hunter Pro – Enhanced Draw Model")

league = st.selectbox("🌍 Select League / Country", LEAGUES)

fixture_text = st.text_input("📌 Match Fixture (e.g. Rangers vs Hearts)")
match_date = st.text_input("📅 Match Date (YYYY-MM-DD)")

st.markdown("### 🔢 Historical Goals (Last Matches)")

col1, col2 = st.columns(2)

with col1:
    home_goals_input = st.text_input(
        "Home Team Goals (comma-separated)",
        placeholder="e.g. 1,0,2,1,1"
    )

with col2:
    away_goals_input = st.text_input(
        "Away Team Goals (comma-separated)",
        placeholder="e.g. 0,1,1,2,0"
    )

draw_odds = st.number_input("Market Draw Odds (+ / -)", -10.0, 20.0, 3.10, 0.05)
table_gap = st.number_input("Table Position Gap (+ / -)", -20, 20, 3, 1)

# ✅ NEW HALFTIME INPUT
ht_draw_pct = st.number_input(
    "⏱️ Estimated Halftime Draw % (league/team behavior)",
    0, 100, 35, 1
)

# ============================
# ANALYSIS
# ============================
if st.button("🔍 Analyze Draw"):
    try:
        home_goals = [int(x.strip()) for x in home_goals_input.split(",") if x.strip().isdigit()]
        away_goals = [int(x.strip()) for x in away_goals_input.split(",") if x.strip().isdigit()]

        lambda_home = estimate_lambda(home_goals)
        lambda_away = estimate_lambda(away_goals)
        prob_draw = draw_probability(lambda_home, lambda_away) * 100

        score = 0

        # Core draw strength
        if prob_draw >= 25:
            score += 2
        if table_gap <= 4:
            score += 1
        if 2.8 <= draw_odds <= 3.6:
            score += 1
        if abs(lambda_home - lambda_away) <= 0.30:
            score += 1

        # ⏱️ HALFTIME DROP PENALTY
        ht_penalty_note = "No HT penalty applied"
        if ht_draw_pct < 30:
            score -= 1
            ht_penalty_note = "Strong HT volatility penalty"
        elif 30 <= ht_draw_pct < 40:
            score -= 0.5
            ht_penalty_note = "Mild HT draw drop penalty"

        # Verdict
        if score >= 4:
            verdict = "🟢 PLAY DRAW"
            css = "play"
            advice = "Strong full-time draw structure"
        elif 3 <= score < 4:
            verdict = "🔵 WATCHLIST"
            css = "watch"
            advice = "Draw possible, watch in-play"
        else:
            verdict = "🔴 NO BET"
            css = "avoid"
            advice = "Draw profile weakened"

        st.markdown(f"""
        <div class="verdict-box {css}">
            <h2>{verdict}</h2>
            <p><strong>League:</strong> {league}</p>
            <p><strong>Fixture:</strong> {fixture_text}</p>
            <p><strong>Date:</strong> {match_date}</p>
            <hr>
            <p>λ Home: {lambda_home:.2f}</p>
            <p>λ Away: {lambda_away:.2f}</p>
            <p><strong>Draw Probability:</strong> {prob_draw:.2f}%</p>
            <p><strong>HT Draw Est.:</strong> {ht_draw_pct}%</p>
            <p><em>{ht_penalty_note}</em></p>
            <p><strong>Final Model Score:</strong> {score}/5</p>
            <p>{advice}</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Input error: {e}")
