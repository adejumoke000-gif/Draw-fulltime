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
# LEAGUE LIST (A–Z)
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
# POISSON MODEL FUNCTIONS
# ============================
def poisson_prob(k, lam):
    return (lam ** k) * math.exp(-lam) / math.factorial(k)

def draw_probability(lambda_A, lambda_B, max_goals=10):
    prob_draw = 0.0
    for k in range(max_goals + 1):
        prob_draw += poisson_prob(k, lambda_A) * poisson_prob(k, lambda_B)
    return prob_draw

def estimate_lambda(goals):
    if len(goals) == 0:
        return 0
    return sum(goals) / len(goals)

# ============================
# SIDEBAR
# ============================
st.sidebar.header("⚙️ Match Context")
league = st.sidebar.selectbox("Select League", LEAGUES)

# ============================
# MAIN UI
# ============================
st.title("🎯 Draw Hunter Pro – Poisson Draw Engine")

fixture_text = st.text_input("📌 Match Fixture (e.g. Arsenal vs Everton)")
match_date = st.text_input("📅 Match Date (YYYY-MM-DD)")

st.markdown("### 🔢 Historical Goals Input (Last Matches)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Home Team Goals (comma-separated)**")
    home_goals_input = st.text_input("Example: 1,0,2,1,1")

with col2:
    st.markdown("**Away Team Goals (comma-separated)**")
    away_goals_input = st.text_input("Example: 0,1,1,2,0")

draw_odds = st.number_input("Market Draw Odds (+/-)", -10.0, 20.0, 3.10, 0.05)
table_gap = st.number_input("Table Position Gap (+/-)", -20, 20, 3, 1)

# ============================
# ANALYZE BUTTON
# ============================
if st.button("🔍 Analyze Draw"):
    try:
        home_goals = [int(x.strip()) for x in home_goals_input.split(",") if x.strip().isdigit()]
        away_goals = [int(x.strip()) for x in away_goals_input.split(",") if x.strip().isdigit()]

        lambda_home = estimate_lambda(home_goals)
        lambda_away = estimate_lambda(away_goals)

        prob_draw = draw_probability(lambda_home, lambda_away)
        prob_percent = prob_draw * 100

        # ============================
        # SCORING LOGIC
        # ============================
        score = 0
        if prob_percent >= 25:
            score += 2
        if table_gap <= 4:
            score += 1
        if 2.8 <= draw_odds <= 3.6:
            score += 1
        if abs(lambda_home - lambda_away) <= 0.3:
            score += 1

        # ============================
        # VERDICT
        # ============================
        if score >= 4:
            verdict = "🟢 PLAY DRAW"
            css = "play"
            advice = "Strong statistical draw profile"
        elif score == 3:
            verdict = "🔵 WATCHLIST"
            css = "watch"
            advice = "Monitor live match conditions"
        else:
            verdict = "🔴 NO BET"
            css = "avoid"
            advice = "Low draw confidence"

        st.markdown(f"""
        <div class="verdict-box {css}">
            <h2>{verdict}</h2>
            <p><strong>League:</strong> {league}</p>
            <p><strong>Fixture:</strong> {fixture_text}</p>
            <p><strong>Date:</strong> {match_date}</p>
            <hr>
            <p>λ Home: {lambda_home:.2f}</p>
            <p>λ Away: {lambda_away:.2f}</p>
            <p><strong>Draw Probability:</strong> {prob_percent:.2f}%</p>
            <p><strong>Model Score:</strong> {score}/5</p>
            <p>{advice}</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Input error: {e}")
