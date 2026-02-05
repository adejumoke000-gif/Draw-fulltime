import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time

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
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    .league-card {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        background: white;
        border-left: 6px solid;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .high-draw {
        border-left-color: #28a745;
        background: linear-gradient(90deg, #d4edda20 0%, white 100%);
    }
    .medium-draw {
        border-left-color: #ffc107;
        background: linear-gradient(90deg, #fff3cd20 0%, white 100%);
    }
    .match-card {
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    .api-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 2px;
    }
    .api-success {
        background-color: #d4edda;
        color: #155724;
    }
    .api-warning {
        background-color: #fff3cd;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TITLE
# ============================================================================

st.markdown('<h1 class="main-title">🎯 DRAW HUNTER PRO</h1>', unsafe_allow_html=True)
st.markdown("### **Real API Integration • Lower Leagues Focus • Automated Analysis**")
st.markdown("---")

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Try to get API key from secrets
try:
    API_KEY = st.secrets["API_KEY"]
    st.sidebar.success("✅ API key loaded from secrets")
except:
    # Fallback to input
    API_KEY = st.sidebar.text_input("Enter your RapidAPI Key:", type="password")
    if not API_KEY:
        st.sidebar.warning("Please enter your API key")
        API_KEY = None

# API Configuration
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

# ============================================================================
# FOCUS ON HIGH-DRAW LOWER LEAGUES
# ============================================================================

HIGH_DRAW_LEAGUES = [
    # TOP PRIORITY: Very High Draw Rate (30-35%)
    {"name": "League One", "id": 41, "country": "England", "draw_rate": 32, "tier": "3rd Division"},
    {"name": "League Two", "id": 42, "country": "England", "draw_rate": 33, "tier": "4th Division"},
    {"name": "2. Bundesliga", "id": 33, "country": "Germany", "draw_rate": 31, "tier": "2nd Division"},
    {"name": "Serie B", "id": 136, "country": "Italy", "draw_rate": 30, "tier": "2nd Division"},
    {"name": "Ligue 2", "id": 62, "country": "France", "draw_rate": 30, "tier": "2nd Division"},
    
    # SECOND PRIORITY: High Draw Rate (28-30%)
    {"name": "Championship", "id": 40, "country": "England", "draw_rate": 29, "tier": "2nd Division"},
    {"name": "Eredivisie", "id": 88, "country": "Netherlands", "draw_rate": 28, "tier": "1st Division"},
    {"name": "Primeira Liga", "id": 94, "country": "Portugal", "draw_rate": 28, "tier": "1st Division"},
]

# ============================================================================
# API FUNCTIONS
# ============================================================================

def make_api_request(endpoint, params=None):
    """Make API request with error handling"""
    if not API_KEY:
        return None
    
    try:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error(f"API Error {response.status_code}")
            return None
    except Exception as e:
        st.sidebar.error(f"Request failed: {str(e)}")
        return None

def get_todays_fixtures(league_id):
    """Get today's fixtures for a league"""
    today = datetime.now().strftime("%Y-%m-%d")
    params = {
        "league": league_id,
        "season": 2024,
        "date": today,
        "timezone": "Europe/London"
    }
    
    data = make_api_request("fixtures", params)
    
    if data and 'response' in data:
        fixtures = []
        for fixture in data['response']:
            # Only include matches that haven't started
            if fixture['fixture']['status']['short'] in ('NS', 'TBD'):
                fixtures.append({
                    'fixture_id': fixture['fixture']['id'],
                    'date': fixture['fixture']['date'],
                    'home_id': fixture['teams']['home']['id'],
                    'home_name': fixture['teams']['home']['name'],
                    'away_id': fixture['teams']['away']['id'],
                    'away_name': fixture['teams']['away']['name'],
                    'home_logo': fixture['teams']['home']['logo'],
                    'away_logo': fixture['teams']['away']['logo'],
                })
        return fixtures
    return []

def get_team_form(team_id, league_id):
    """Get team's recent form"""
    params = {
        "team": team_id,
        "league": league_id,
        "season": 2024,
        "last": 10  # Last 10 matches
    }
    
    data = make_api_request("fixtures", params)
    if data and 'response' in data:
        return data['response']
    return []

def get_h2h_history(team1_id, team2_id):
    """Get head-to-head history"""
    params = {
        "h2h": f"{team1_id}-{team2_id}",
        "last": 5  # Last 5 meetings
    }
    
    data = make_api_request("fixtures/headtohead", params)
    if data and 'response' in data:
        return data['response']
    return []

def get_league_standings(league_id):
    """Get current league standings"""
    params = {
        "league": league_id,
        "season": 2024
    }
    
    data = make_api_request("standings", params)
    if data and 'response' in data:
        return data['response'][0]['league']['standings'][0]
    return []

# ============================================================================
# 7-LAYER ANALYSIS FUNCTIONS
# ============================================================================

def analyze_league_layer(league_draw_rate):
    """Layer 1: League Draw Baseline"""
    if 26 <= league_draw_rate <= 32:
        return 1.0, f"✅ League: {league_draw_rate}% (optimal 26-32%)"
    elif 23 <= league_draw_rate <= 25:
        return 0.5, f"⚠️ League: {league_draw_rate}% (caution 23-25%)"
    else:
        return 0.0, f"❌ League: {league_draw_rate}% (outside range)"

def analyze_goals_layer(home_form, away_form):
    """Layer 2: Goal Density Estimate"""
    # Count goals in last 5 matches
    home_goals = sum([m['goals']['home'] for m in home_form[:5]]) if home_form else 5
    away_goals = sum([m['goals']['away'] for m in away_form[:5]]) if away_form else 5
    
    avg_goals = (home_goals + away_goals) / 10  # Average per match
    
    if avg_goals <= 1.15:
        return 1.0, f"✅ Goals: {avg_goals:.2f} avg (≤1.15)"
    elif avg_goals <= 1.35:
        return 0.5, f"⚠️ Goals: {avg_goals:.2f} avg (1.16-1.35)"
    else:
        return 0.0, f"❌ Goals: {avg_goals:.2f} avg (>1.35)"

def analyze_scorelines_layer(home_form, away_form):
    """Layer 3: Scoreline Distribution"""
    scorelines = []
    
    for match in home_form[:10] + away_form[:10]:
        if match['goals']['home'] == 0 and match['goals']['away'] == 0:
            scorelines.append("0-0")
        elif match['goals']['home'] == 1 and match['goals']['away'] == 1:
            scorelines.append("1-1")
    
    count = len(scorelines)
    
    if count >= 4:
        return 1.0, f"✅ Scorelines: {count} 0-0/1-1 in last 10"
    elif count == 3:
        return 0.5, f"⚠️ Scorelines: {count} 0-0/1-1 in last 10"
    else:
        return 0.0, f"❌ Scorelines: Only {count} 0-0/1-1 in last 10"

def analyze_parity_layer(standings, home_id, away_id):
    """Layer 4: Strength Parity"""
    home_pos = next((team['rank'] for team in standings if team['team']['id'] == home_id), 10)
    away_pos = next((team['rank'] for team in standings if team['team']['id'] == away_id), 12)
    
    gap = abs(home_pos - away_pos)
    
    if gap <= 3:
        return 1.0, f"✅ Parity: {gap} pos gap (≤3)"
    elif gap <= 6:
        return 0.5, f"⚠️ Parity: {gap} pos gap (4-6)"
    else:
        return 0.0, f"❌ Parity: {gap} pos gap (>6)"

def analyze_form_layer(home_form, away_form):
    """Layer 5: Form Volatility"""
    # Count wins in last 5
    home_wins = sum(1 for m in home_form[:5] if m['teams']['home']['id'] == home_form[0]['teams']['home']['id'] 
                   and m['teams']['home']['winner'] is True) if home_form else 2
    away_wins = sum(1 for m in away_form[:5] if m['teams']['away']['id'] == away_form[0]['teams']['away']['id'] 
                   and m['teams']['away']['winner'] is True) if away_form else 1
    
    combined_wins = home_wins + away_wins
    
    if combined_wins <= 4:
        return 1.0, f"✅ Form: {combined_wins} wins last 5 (≤4)"
    elif combined_wins == 5:
        return 0.5, f"⚠️ Form: {combined_wins} wins last 5 (5)"
    else:
        return 0.0, f"❌ Form: {combined_wins} wins last 5 (≥6)"

def analyze_h2h_layer(h2h_matches):
    """Layer 6: H2H History"""
    if not h2h_matches:
        return 0.5, "⚠️ H2H: No history available"
    
    draws = sum(1 for match in h2h_matches 
                if match['teams']['home']['winner'] is False 
                and match['teams']['away']['winner'] is False)
    
    if draws >= 2:
        return 1.0, f"✅ H2H: {draws} draws in last 5"
    elif draws == 1:
        return 0.5, f"⚠️ H2H: {draws} draw in last 5"
    else:
        return 0.0, f"❌ H2H: 0 draws in last 5"

def analyze_odds_layer(fixture_id):
    """Layer 7: Market Odds"""
    # This is a placeholder - actual odds require premium API
    # For free tier, we'll use a reasonable assumption
    return 0.5, "⚠️ Odds: Using league average (premium API needed for real odds)"

# ============================================================================
# MAIN APP
# ============================================================================

# Initialize session state
if 'fetched_data' not in st.session_state:
    st.session_state.fetched_data = {}

# SIDEBAR
with st.sidebar:
    st.header("🌍 SELECT LEAGUES")
    
    selected_leagues = []
    for league in HIGH_DRAW_LEAGUES:
        if st.checkbox(f"{league['name']} ({league['draw_rate']}% draws)", 
                      value=league['name'] in ['League One', 'League Two']):
            selected_leagues.append(league)
    
    st.markdown("---")
    
    if API_KEY and selected_leagues:
        if st.button("🔄 FETCH TODAY'S MATCHES", type="primary", use_container_width=True):
            with st.spinner("Fetching data from API..."):
                for league in selected_leagues:
                    fixtures = get_todays_fixtures(league['id'])
                    if fixtures:
                        st.session_state.fetched_data[league['name']] = {
                            'league': league,
                            'fixtures': fixtures
                        }
                
                if st.session_state.fetched_data:
                    st.success(f"Found {sum(len(d['fixtures']) for d in st.session_state.fetched_data.values())} matches")
                else:
                    st.warning("No matches found for today")

# MAIN CONTENT
tab1, tab2, tab3 = st.tabs(["🤖 LIVE ANALYSIS", "📊 DASHBOARD", "⚙️ SETUP"])

with tab1:
    st.header("LIVE MATCH ANALYSIS")
    
    if not API_KEY:
        st.error("❌ Please enter your API key in the sidebar")
        st.info("Get free key from: rapidapi.com/api-sports/api/api-football")
        
    elif not st.session_state.fetched_data:
        st.info("👈 Select leagues and click 'Fetch Today's Matches'")
        
        # Show league cards
        st.subheader("🎯 HIGH-DRAW LEAGUES READY FOR ANALYSIS")
        for league in HIGH_DRAW_LEAGUES[:4]:
            with st.container():
                st.markdown(f"""
                <div class='league-card high-draw'>
                    <h4>{league['name']}</h4>
                    <p>📊 <strong>{league['draw_rate']}%</strong> draw rate • {league['tier']} • {league['country']}</p>
                    <span class='api-badge api-success'>API READY</span>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Display fetched matches
        total_matches = sum(len(d['fixtures']) for d in st.session_state.fetched_data.values())
        st.success(f"✅ **Live Matches Found:** {total_matches} matches ready for analysis")
        
        for league_name, data in st.session_state.fetched_data.items():
            league = data['league']
            fixtures = data['fixtures']
            
            st.subheader(f"{league_name} ({len(fixtures)} matches)")
            
            for fixture in fixtures:
                with st.expander(f"🏠 {fixture['home_name']} vs 🛫 {fixture['away_name']}"):
                    # Fetch additional data for this match
                    with st.spinner("Loading match data..."):
                        # Get team form
                        home_form = get_team_form(fixture['home_id'], league['id'])
                        away_form = get_team_form(fixture['away_id'], league['id'])
                        
                        # Get H2H
                        h2h = get_h2h_history(fixture['home_id'], fixture['away_id'])
                        
                        # Get standings
                        standings = get_league_standings(league['id'])
                        
                        # Run 7-layer analysis
                        layers = []
                        details = []
                        
                        # Layer 1
                        score1, detail1 = analyze_league_layer(league['draw_rate'])
                        layers.append(score1)
                        details.append(detail1)
                        
                        # Layer 2
                        score2, detail2 = analyze_goals_layer(home_form, away_form)
                        layers.append(score2)
                        details.append(detail2)
                        
                        # Layer 3
                        score3, detail3 = analyze_scorelines_layer(home_form, away_form)
                        layers.append(score3)
                        details.append(detail3)
                        
                        # Layer 4
                        score4, detail4 = analyze_parity_layer(standings, fixture['home_id'], fixture['away_id'])
                        layers.append(score4)
                        details.append(detail4)
                        
                        # Layer 5
                        score5, detail5 = analyze_form_layer(home_form, away_form)
                        layers.append(score5)
                        details.append(detail5)
                        
                        # Layer 6
                        score6, detail6 = analyze_h2h_layer(h2h)
                        layers.append(score6)
                        details.append(detail6)
                        
                        # Layer 7
                        score7, detail7 = analyze_odds_layer(fixture['fixture_id'])
                        layers.append(score7)
                        details.append(detail7)
                        
                        # Calculate total
                        total_score = sum(layers)
                        
                        # Display results
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if total_score >= 6.0:
                                st.markdown("""
                                <div style='padding: 20px; background-color: #d4edda; border-radius: 10px; border: 3px solid #28a745;'>
                                    <h2>🔵 STRONG DRAW</h2>
                                    <h3>Score: {:.1f}/7.0</h3>
                                    <p><strong>💰 Stake: 1.0 unit (Single)</strong></p>
                                </div>
                                """.format(total_score), unsafe_allow_html=True)
                            elif total_score >= 5.0:
                                st.markdown("""
                                <div style='padding: 20px; background-color: #fff3cd; border-radius: 10px; border: 3px solid #ffc107;'>
                                    <h2>🟡 MODERATE</h2>
                                    <h3>Score: {:.1f}/7.0</h3>
                                    <p><strong>💰 Stake: 0.5 units (Double max)</strong></p>
                                </div>
                                """.format(total_score), unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style='padding: 20px; background-color: #f8d7da; border-radius: 10px; border: 3px solid #dc3545;'>
                                    <h2>🔴 AVOID</h2>
                                    <h3>Score: {:.1f}/7.0</h3>
                                    <p><strong>💰 NO BET - Model rejects</strong></p>
                                </div>
                                """.format(total_score), unsafe_allow_html=True)
                        
                        with col2:
                            # Layer breakdown
                            st.subheader("Layer Breakdown")
                            for i, (score, detail) in enumerate(zip(layers, details), 1):
                                color = "#28a745" if score == 1.0 else "#ffc107" if score == 0.5 else "#dc3545"
                                st.markdown(f"""
                                <div style='padding: 8px; margin: 5px 0; border-left: 4px solid {color};'>
                                    <strong>Layer {i}:</strong> {detail}
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Visualization
                        st.subheader("📊 Layer Performance")
                        fig = go.Figure(data=[
                            go.Bar(
                                x=['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'],
                                y=layers,
                                marker_color=['#28a745' if s == 1.0 else '#ffc107' if s == 0.5 else '#dc3545' for s in layers]
                            )
                        ])
                        fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("ANALYSIS DASHBOARD")
    
    if st.session_state.fetched_data:
        # Show summary
        summary_data = []
        for league_name, data in st.session_state.fetched_data.items():
            for fixture in data['fixtures']:
                summary_data.append({
