import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Draw Hunter Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    .verdict-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .strong-draw {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .moderate-draw {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .avoid {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .layer-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        background: white;
        border-left: 5px solid;
    }
    .api-section {
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TITLE
# ============================================================================

st.markdown('<h1 class="main-header">🎯 Draw Hunter Pro</h1>', unsafe_allow_html=True)
st.markdown("### **Lower Leagues Focus • H2H Analysis • 7-Layer Model**")
st.markdown("---")

# ============================================================================
# LOWER LEAGUES DATABASE
# ============================================================================

LOWER_LEAGUES = {
    # High Draw Rate Leagues (30-35%)
    "League One (ENG)": {"draw_rate": 32, "country": "England", "tier": "3rd Division", "api_id": 41},
    "League Two (ENG)": {"draw_rate": 33, "country": "England", "tier": "4th Division", "api_id": 42},
    "2. Bundesliga (GER)": {"draw_rate": 31, "country": "Germany", "tier": "2nd Division", "api_id": 33},
    "Serie B (ITA)": {"draw_rate": 30, "country": "Italy", "tier": "2nd Division", "api_id": 136},
    "Ligue 2 (FRA)": {"draw_rate": 30, "country": "France", "tier": "2nd Division", "api_id": 62},
    
    # Medium Draw Rate Leagues (28-30%)
    "Championship (ENG)": {"draw_rate": 29, "country": "England", "tier": "2nd Division", "api_id": 40},
    "Eredivisie (NED)": {"draw_rate": 28, "country": "Netherlands", "tier": "1st Division", "api_id": 88},
    "Primeira Liga (POR)": {"draw_rate": 28, "country": "Portugal", "tier": "1st Division", "api_id": 94},
    
    # Lower Draw Rate (shown for comparison)
    "Premier League (ENG)": {"draw_rate": 27, "country": "England", "tier": "1st Division", "api_id": 39},
    "La Liga (ESP)": {"draw_rate": 26, "country": "Spain", "tier": "1st Division", "api_id": 140},
}

# ============================================================================
# API FUNCTIONS (OPTIONAL)
# ============================================================================

def fetch_api_football_data(api_key, endpoint, params=None):
    """Fetch data from API-Football.com"""
    if not api_key:
        return None
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.warning(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.sidebar.warning(f"API Connection failed: {str(e)}")
        return None

def get_h2h_from_api(api_key, team1, team2):
    """Get H2H history from API"""
    params = {
        "h2h": f"{team1}-{team2}",
        "last": 5
    }
    
    data = fetch_api_football_data(api_key, "fixtures/headtohead", params)
    if data and 'response' in data:
        return data['response']
    return None

def get_todays_fixtures(api_key, league_id):
    """Get today's fixtures for a league"""
    today = datetime.now().strftime("%Y-%m-%d")
    params = {
        "league": league_id,
        "season": 2024,
        "date": today
    }
    
    data = fetch_api_football_data(api_key, "fixtures", params)
    if data and 'response' in data:
        return data['response']
    return None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("⚙️ Model Settings")
    
    with st.expander("Layer Thresholds", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            l1_min = st.number_input("L1 PASS Min %", 20, 35, 26, 1)
            l1_max = st.number_input("L1 PASS Max %", 25, 40, 32, 1)
            l2_pass = st.number_input("L2 PASS Max Goals", 0.8, 1.5, 1.15, 0.05)
        with col2:
            l1_caution = st.number_input("L1 CAUTION Min %", 20, 30, 23, 1)
            l2_caution = st.number_input("L2 CAUTION Max", 1.0, 1.8, 1.35, 0.05)
    
    st.markdown("---")
    
    st.header("🔌 API Integration (Optional)")
    
    api_key = st.text_input("API-Football Key", type="password", 
                           help="Get free key from RapidAPI.com")
    
    if api_key:
        st.success("✅ API key entered")
        
        # Quick API test
        if st.button("Test API Connection"):
            with st.spinner("Testing connection..."):
                test_data = fetch_api_football_data(api_key, "status")
                if test_data:
                    st.success("✅ API Connected Successfully")
                else:
                    st.error("❌ API Connection Failed")
    
    st.markdown("---")
    
    st.header("📋 Match History")
    
    if 'matches' not in st.session_state:
        st.session_state.matches = []
    
    if st.session_state.matches:
        df = pd.DataFrame(st.session_state.matches)
        st.dataframe(df[['Date', 'Home', 'Away', 'Tier', 'Total']].tail(5))
        
        if st.button("Clear History"):
            st.session_state.matches = []
            st.rerun()
    else:
        st.info("No matches analyzed yet")

# ============================================================================
# MAIN APP
# ============================================================================

tab1, tab2, tab3 = st.tabs(["🧠 7-Layer Analysis", "🤝 H2H Focus", "⚡ Quick Scan"])

with tab1:
    st.header("Complete 7-Layer Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Match Details")
        match_date = st.date_input("Date", datetime.now())
        
        # LOWER LEAGUES SELECTOR
        selected_league = st.selectbox(
            "Select League (Focus on Lower Divisions):",
            list(LOWER_LEAGUES.keys()),
            index=0  # Default to League One
        )
        
        league_data = LOWER_LEAGUES[selected_league]
        league_rate = league_data['draw_rate']
        
        st.info(f"**{selected_league}**: {league_rate}% draw rate • {league_data['tier']}")
        
        home = st.text_input("Home Team", "Barnsley")
        away = st.text_input("Away Team", "Bolton")
        
        # API AUTO-FETCH BUTTON
        if api_key and st.button("🔄 Fetch H2H from API", type="secondary"):
            with st.spinner("Fetching H2H data..."):
                # This would use real team IDs in production
                st.info(f"Would fetch H2H for {home} vs {away}")
                # In real app: get_h2h_from_api(api_key, home_team_id, away_team_id)
    
    with col2:
        st.subheader("📊 Team Data")
        
        col_a, col_b = st.columns(2)
        with col_a:
            score_0_0 = st.number_input("0-0 (last 10)", 0, 10, 2, 1)
            wins_home = st.number_input("Home Wins (last 5)", 0, 5, 2, 1)
        with col_b:
            score_1_1 = st.number_input("1-1 (last 10)", 0, 10, 1, 1)
            wins_away = st.number_input("Away Wins (last 5)", 0, 5, 1, 1)
        
        table_gap = st.slider("Table Position Gap", 0, 20, 2, 1)
        draw_odds = st.slider("Draw Odds", 2.0, 5.0, 3.1, 0.1)
        
        motivation = st.selectbox("Match Context", 
            ["Neutral/Cautious", "Derby/Local Rivalry", "One Team Desperate", "Must-Win Imbalance"])
        
        # H2H INPUT (NEW)
        st.subheader("🤝 H2H History (Last 5 Meetings)")
        h2h_draws = st.number_input("Draws in last 5 H2H meetings", 0, 5, 1, 1,
                                   help="Number of draws in last 5 head-to-head matches")
    
    # Analyze Button
    if st.button("🚀 Run 7-Layer Analysis", type="primary", use_container_width=True):
        scores = []
        details = []
        
        # LAYER 1: League Baseline (using lower league data)
        if l1_min <= league_rate <= l1_max:
            scores.append(1.0)
            details.append(("League Baseline", "✅ PASS", f"{league_rate}%"))
        elif l1_caution <= league_rate < l1_min:
            scores.append(0.5)
            details.append(("League Baseline", "⚠️ CAUTION", f"{league_rate}%"))
        else:
            scores.append(0.0)
            details.append(("League Baseline", "❌ REJECT", f"{league_rate}%"))
        
        # LAYER 2: Goal Density
        # This would come from API in automated version
        avg_goals = st.slider("Average Goals (for demo)", 0.5, 3.0, 1.2, 0.05, key="goals_demo")
        
        if avg_goals <= l2_pass:
            scores.append(1.0)
            details.append(("Goal Density", "✅ PASS", f"{avg_goals:.2f}"))
        elif avg_goals <= l2_caution:
            scores.append(0.5)
            details.append(("Goal Density", "⚠️ CAUTION", f"{avg_goals:.2f}"))
        else:
            scores.append(0.0)
            details.append(("Goal Density", "❌ REJECT", f"{avg_goals:.2f}"))
        
        # LAYER 3: Scoreline Distribution
        scorelines = score_0_0 + score_1_1
        if scorelines >= 4:
            scores.append(1.0)
            details.append(("Scorelines", "✅ PASS", f"{scorelines} combined"))
        elif scorelines == 3:
            scores.append(0.5)
            details.append(("Scorelines", "⚠️ CAUTION", f"{scorelines} combined"))
        else:
            scores.append(0.0)
            details.append(("Scorelines", "❌ REJECT", f"{scorelines} combined"))
        
        # LAYER 4: Strength Parity
        if table_gap <= 3:
            scores.append(1.0)
            details.append(("Strength Parity", "✅ PASS", f"{table_gap} pos gap"))
        elif table_gap <= 6:
            scores.append(0.5)
            details.append(("Strength Parity", "⚠️ CAUTION", f"{table_gap} pos gap"))
        else:
            scores.append(0.0)
            details.append(("Strength Parity", "❌ REJECT", f"{table_gap} pos gap"))
        
        # LAYER 5: Form Volatility
        combined_wins = wins_home + wins_away
        if combined_wins <= 4:
            scores.append(1.0)
            details.append(("Form Volatility", "✅ PASS", f"{combined_wins} wins"))
        elif combined_wins == 5:
            scores.append(0.5)
            details.append(("Form Volatility", "⚠️ CAUTION", f"{combined_wins} wins"))
        else:
            scores.append(0.0)
            details.append(("Form Volatility", "❌ REJECT", f"{combined_wins} wins"))
        
        # LAYER 6: H2H HISTORY (NEW)
        if h2h_draws >= 2:
            scores.append(1.0)
            details.append(("H2H History", "✅ PASS", f"{h2h_draws} draws in last 5"))
        elif h2h_draws == 1:
            scores.append(0.5)
            details.append(("H2H History", "⚠️ CAUTION", f"{h2h_draws} draw in last 5"))
        else:
            scores.append(0.0)
            details.append(("H2H History", "❌ REJECT", f"{h2h_draws} draws in last 5"))
        
        # LAYER 7: Market Odds
        if 2.8 <= draw_odds <= 3.6:
            scores.append(1.0)
            details.append(("Market Odds", "✅ PASS", f"{draw_odds:.2f}"))
        else:
            scores.append(0.0)
            details.append(("Market Odds", "⚠️ SUSPICIOUS", f"{draw_odds:.2f}"))
        
        # CALCULATE TOTAL
        total_score = sum(scores)
        
        # DETERMINE VERDICT
        if total_score >= 6.0:
            tier = "🔵 STRONG DRAW"
            stake = "1.0 unit (Single bet)"
            css_class = "strong-draw"
        elif total_score >= 5.0:
            tier = "🟡 MODERATE"
            stake = "0.5 units each (Double max)"
            css_class = "moderate-draw"
        else:
            tier = "🔴 AVOID"
            stake = "NO BET"
            css_class = "avoid"
        
        # DISPLAY RESULTS
        st.markdown("---")
        
        # Verdict Box
        st.markdown(f"""
        <div class="verdict-box {css_class}">
            <h2>{tier}</h2>
            <h3>Total Score: {total_score:.1f}/7.0</h3>
            <h4>💰 Recommendation: {stake}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Layer Breakdown
        st.subheader("📋 7-Layer Breakdown")
        cols = st.columns(4)
        for idx, (layer, status, value) in enumerate(details):
            with cols[idx % 4]:
                border_color = "#28a745" if "✅" in status else "#ffc107" if "⚠️" in status else "#dc3545"
                st.markdown(f"""
                <div class="layer-box" style="border-left-color: {border_color};">
                    <strong>{layer}</strong><br>
                    <span style="color: {border_color}; font-weight: bold;">{status}</span><br>
                    <small>{value}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Visualization
        st.subheader("📊 Layer Performance Chart")
        fig = go.Figure(data=[
            go.Bar(
                x=['L1', 'L2', 'L3', 'L4', 'L5', 'H2H', 'L7'],
                y=scores,
                marker_color=['#28a745' if s == 1.0 else '#ffc107' if s == 0.5 else '#dc3545' for s in scores],
                text=[f"{s:.1f}" for s in scores],
                textposition='auto'
            )
        ])
        fig.update_layout(
            yaxis=dict(range=[0, 1.1]),
            showlegend=False,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Save to history
        match_record = {
            'Date': match_date,
            'League': selected_league,
            'Home': home,
            'Away': away,
            'Total': total_score,
            'Tier': tier,
            'H2H_Draws': h2h_draws
        }
        st.session_state.matches.append(match_record)

with tab2:
    st.header("🤝 H2H Analysis Focus")
    
    st.markdown("""
    **Why H2H matters for draws:**
    
    1. **Historical patterns** - Some teams consistently draw against each other
    2. **Tactical matchups** - Certain playing styles neutralize each other
    3. **Psychological factors** - Derby/rivalry matches often tight
    
    **📊 H2H Scoring Rules:**
    - **2+ draws in last 5 meetings** = ✅ PASS (1.0 point)
    - **1 draw in last 5 meetings** = ⚠️ CAUTION (0.5 point)  
    - **0 draws in last 5 meetings** = ❌ REJECT (0 points)
    """)
    
    # H2H Analysis Tool
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team A")
        team_a_wins = st.number_input("Team A wins in last 5 H2H", 0, 5, 1, 1)
        team_a_goals = st.number_input("Team A avg goals in H2H", 0.0, 4.0, 1.1, 0.1)
    
    with col2:
        st.subheader("Team B")
        team_b_wins = st.number_input("Team B wins in last 5 H2H", 0, 5, 1, 1)
        team_b_goals = st.number_input("Team B avg goals in H2H", 0.0, 4.0, 1.0, 0.1)
    
    draws = 5 - (team_a_wins + team_b_wins)
    avg_goals = (team_a_goals + team_b_goals) / 2
    
    if draws < 0:
        draws = 0
    
    st.metric("📈 Draws in last 5 H2H", draws)
    st.metric("⚽ Average goals in H2H", f"{avg_goals:.2f}")
    
    if draws >= 2:
        st.success("**✅ Strong H2H draw pattern** - This significantly increases draw probability")
    elif draws == 1:
        st.warning("**⚠️ Moderate H2H draw pattern** - Consider with other factors")
    else:
        st.error("**❌ Weak H2H draw pattern** - Draws unlikely based on history")

with tab3:
    st.header("⚡ Quick League Scanner")
    
    st.markdown("Quickly identify which lower leagues have matches today")
    
    # Today's date
    today = datetime.now().strftime("%A, %B %d, %Y")
    st.subheader(f"📅 Today: {today}")
    
    # League scanner
    st.subheader("🔍 Recommended Lower Leagues Today")
    
    recommended_leagues = [
        {"name": "League One", "draw_rate": 32, "matches_today": 6, "avg_odds": 3.2},
        {"name": "League Two", "draw_rate": 33, "matches_today": 7, "avg_odds": 3.1},
        {"name": "2. Bundesliga", "draw_rate": 31, "matches_today": 4, "avg_odds": 3.3},
        {"name": "Serie B", "draw_rate": 30, "matches_today": 5, "avg_odds": 3.0},
    ]
    
    for league in recommended_leagues:
        with st.expander(f"{league['name']} - {league['matches_today']} matches today"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Draw Rate", f"{league['draw_rate']}%")
            with col2:
                st.metric("Matches", league['matches_today'])
            with col3:
                st.metric("Avg Odds", f"{league['avg_odds']:.1f}")
            
            # API fetch button
            if api_key:
                league_id = LOWER_LEAGUES.get(f"{league['name']} (ENG)", {}).get("api_id") or \
                           LOWER_LEAGUES.get(f"{league['name']} (GER)", {}).get("api_id") or \
                           LOWER_LEAGUES.get(f"{league['name']} (ITA)", {}).get("api_id")
                
                if league_id and st.button(f"Fetch {league['name']} fixtures", key=f"fetch_{league['name']}"):
                    with st.spinner("Fetching from API..."):
                        fixtures = get_todays_fixtures(api_key, league_id)
                        if fixtures:
                            st.success(f"Found {len(fixtures)} fixtures")
                            for fix in fixtures[:3]:  # Show first 3
                                st.write(f"• {fix['teams']['home']['name']} vs {fix['teams']['away']['name']}")
                        else:
                            st.info("No fixtures found for today")

# ============================================================================
# API COMMANDS REFERENCE
# ============================================================================

st.markdown("---")
with st.expander("📚 API Commands Reference", expanded=False):
    st.markdown("""
    **API-Football.com Free Tier (100 requests/day):**
    
    ```python
    # 1. Get today's fixtures
    GET /fixtures?league=41&date=2024-03-15
    
    # 2. Get H2H history  
    GET /fixtures/headtohead?h2h=TEAM1_ID-TEAM2_ID&last=5
    
    # 3. Get team statistics
    GET /teams/statistics?team=42&league=41&season=2024
    
    # 4. Get league standings
    GET /standings?league=41&season=2024
    
    # 5. Get odds (premium feature)
    GET /odds?fixture=123456&bookmaker=1
    ```
    
    **Headers required:**
    ```python
    headers = {
        "X-RapidAPI-Key": "your-api-key-here",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    ```
    """)

# ==============
