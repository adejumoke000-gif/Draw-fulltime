import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Draw Predictor Pro",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .verdict-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .strong-draw {
        background-color: #d4edda;
        border: 3px solid #28a745;
        color: #155724;
    }
    .moderate-draw {
        background-color: #fff3cd;
        border: 3px solid #ffc107;
        color: #856404;
    }
    .avoid {
        background-color: #f8d7da;
        border: 3px solid #dc3545;
        color: #721c24;
    }
    .layer-box {
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        background: white;
        border-left: 5px solid;
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🔮 DEFENSIVE DRAW PREDICTION MODEL</h1>', unsafe_allow_html=True)
st.markdown("### **🎯 Capital Preservation First • Profit Second**")
st.markdown("---")

# Initialize session state
if 'matches' not in st.session_state:
    st.session_state.matches = []

# SIDEBAR
with st.sidebar:
    st.header("⚙️ MODEL SETTINGS")
    
    with st.expander("Layer Thresholds", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            l1_pass_min = st.number_input("L1 PASS Min %", 20, 40, 26, 1)
            l2_pass = st.number_input("L2 PASS Max Goals", 0.8, 2.0, 1.15, 0.05)
        with col2:
            l1_pass_max = st.number_input("L1 PASS Max %", 25, 45, 32, 1)
            l2_caution = st.number_input("L2 CAUTION Max", 1.0, 2.5, 1.35, 0.05)
    
    st.markdown("---")
    st.header("📋 MATCH HISTORY")
    
    if st.session_state.matches:
        df = pd.DataFrame(st.session_state.matches)
        st.dataframe(df[['Home', 'Away', 'Tier', 'Score']].tail(8), use_container_width=True)
        
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.matches = []
            st.rerun()
    else:
        st.info("No matches analyzed yet")
    
    st.markdown("---")
    st.markdown("""
    **🚨 DISCIPLINE RULES:**
    1. 🔵 = 1.0 unit single
    2. 🟡 = 0.5 units (double max)
    3. 🔴 = NO BET
    4. Odds < 2.50 → AVOID
    5. Pressure to recover → STOP
    """)

# MAIN TABS
tab1, tab2, tab3 = st.tabs(["🧠 ANALYZE MATCH", "📊 DASHBOARD", "⚡ QUICK SCREEN"])

with tab1:
    st.header("COMPLETE MATCH ANALYSIS")
    
    # Input Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 MATCH DETAILS")
        match_date = st.date_input("Date", datetime.now())
        league = st.selectbox("League", [
            "Premier League", "La Liga", "Serie A", "Bundesliga", 
            "Ligue 1", "Championship", "Eredivisie", "Primeira Liga"
        ])
        home = st.text_input("Home Team", "Manchester United")
        away = st.text_input("Away Team", "Chelsea")
        
        st.subheader("📈 STATISTICAL LAYERS")
        league_rate = st.slider(f"League Draw Rate %", 15.0, 45.0, 28.5, 0.5)
        avg_goals = st.slider("Average Goals (Home + Away)/2", 0.5, 3.0, 1.2, 0.05)
    
    with col2:
        st.subheader("📊 TEAM FORM")
        col_a, col_b = st.columns(2)
        with col_a:
            score_0_0 = st.number_input("0-0 (last 10)", 0, 10, 2, 1, 
                                        help="Number of 0-0 draws in last 10 matches")
            wins_home = st.number_input(f"{home[:10]} Wins (last 5)", 0, 5, 2, 1)
        with col_b:
            score_1_1 = st.number_input("1-1 (last 10)", 0, 10, 1, 1,
                                        help="Number of 1-1 draws in last 10 matches")
            wins_away = st.number_input(f"{away[:10]} Wins (last 5)", 0, 5, 1, 1)
        
        table_gap = st.slider("Table Position Gap", 0, 20, 2, 1,
                             help="Difference in league positions")
        draw_odds = st.slider("Market Draw Odds", 2.0, 5.0, 3.1, 0.1)
        
        motivation = st.selectbox("Match Context / Motivation", 
            ["Neutral/Cautious", "Derby/Local Rivalry", "One Team Desperate", 
             "Must-Win for Both", "End of Season/Dead Rubber"])
    
    # Analyze Button
    if st.button("🚀 ANALYZE MATCH", type="primary", use_container_width=True):
        # Convert percentage to decimal
        league_rate_dec = league_rate / 100
        
        # Calculate scores
        scores = []
        details = []
        
        # LAYER 1: League Baseline
        if l1_pass_min <= league_rate <= l1_pass_max:
            scores.append(1.0)
            details.append(("League", "✅ PASS", f"{league_rate}%"))
        elif 23 <= league_rate < l1_pass_min:
            scores.append(0.5)
            details.append(("League", "⚠️ CAUTION", f"{league_rate}%"))
        else:
            scores.append(0.0)
            details.append(("League", "❌ REJECT", f"{league_rate}%"))
        
        # LAYER 2: Goal Density
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
            details.append(("Scorelines", "✅ PASS", f"{scorelines}"))
        elif scorelines == 3:
            scores.append(0.5)
            details.append(("Scorelines", "⚠️ CAUTION", f"{scorelines}"))
        else:
            scores.append(0.0)
            details.append(("Scorelines", "❌ REJECT", f"{scorelines}"))
        
        # LAYER 4: Strength Parity
        if table_gap <= 3:
            scores.append(1.0)
            details.append(("Parity", "✅ PASS", f"{table_gap}"))
        elif table_gap <= 6:
            scores.append(0.5)
            details.append(("Parity", "⚠️ CAUTION", f"{table_gap}"))
        else:
            scores.append(0.0)
            details.append(("Parity", "❌ REJECT", f"{table_gap}"))
        
        # LAYER 5: Form Volatility
        combined_wins = wins_home + wins_away
        if combined_wins <= 4:
            scores.append(1.0)
            details.append(("Form", "✅ PASS", f"{combined_wins}"))
        elif combined_wins == 5:
            scores.append(0.5)
            details.append(("Form", "⚠️ CAUTION", f"{combined_wins}"))
        else:
            scores.append(0.0)
            details.append(("Form", "❌ REJECT", f"{combined_wins}"))
        
        # LAYER 6: Motivation
        if motivation in ["Neutral/Cautious", "Derby/Local Rivalry"]:
            scores.append(1.0)
            details.append(("Context", "✅ PASS", motivation[:20]))
        elif motivation == "One Team Desperate":
            scores.append(0.5)
            details.append(("Context", "⚠️ CAUTION", motivation[:20]))
        else:
            scores.append(0.0)
            details.append(("Context", "❌ REJECT", motivation[:20]))
        
        # LAYER 7: Market Odds
        if 2.8 <= draw_odds <= 3.6:
            scores.append(1.0)
            details.append(("Odds", "✅ PASS", f"{draw_odds:.2f}"))
        else:
            scores.append(0.0)
            details.append(("Odds", "⚠️ WARNING", f"{draw_odds:.2f}"))
        
        # CALCULATE TOTAL
        total_score = sum(scores)
        
        # DETERMINE VERDICT
        if total_score >= 6.0:
            tier = "🔵 STRONG DRAW"
            stake = "1.0 unit (Single bet only)"
            color = "#28a745"
            css_class = "strong-draw"
        elif total_score >= 5.0:
            tier = "🟡 MODERATE DRAW"
            stake = "0.5 units each (Double max)"
            color = "#ffc107"
            css_class = "moderate-draw"
        else:
            tier = "🔴 AVOID"
            stake = "NO BET - Model rejects"
            color = "#dc3545"
            css_class = "avoid"
        
        # DISPLAY RESULTS
        st.markdown("---")
        
        # Verdict Box
        st.markdown(f"""
        <div class="verdict-box {css_class}">
            <h2>{tier}</h2>
            <h3>Total Score: {total_score:.1f}/7.0</h3>
            <h4>💰 {stake}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Layer Breakdown
        st.subheader("📋 LAYER BREAKDOWN")
        cols = st.columns(4)
        colors = {"✅": "#28a745", "⚠️": "#ffc107", "❌": "#dc3545"}
        
        for idx, (layer, status, value) in enumerate(details):
            with cols[idx % 4]:
                status_color = colors.get(status[:1], "#666")
                st.markdown(f"""
                <div class="layer-box" style="border-left-color: {status_color};">
                    <strong>{layer}</strong><br>
                    <span style="color: {status_color}; font-weight: bold;">{status}</span><br>
                    <small>{value}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Visualization
        st.subheader("📊 LAYER PERFORMANCE CHART")
        fig = go.Figure(data=[
            go.Bar(
                x=['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'],
                y=scores,
                marker_color=['#28a745' if s == 1.0 else '#ffc107' if s == 0.5 else '#dc3545' for s in scores],
                text=[f"{s:.1f}" for s in scores],
                textposition='auto'
            )
        ])
        fig.update_layout(
            yaxis=dict(range=[0, 1.1], title="Score"),
            xaxis=dict(title="Layer"),
            showlegend=False,
            height=350,
            margin=dict(t=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Save to history
        match_record = {
            'Date': str(match_date),
            'League': league,
            'Home': home,
            'Away': away,
            'Score': f"{total_score:.1f}",
            'Tier': tier,
            'Odds': draw_odds
        }
        st.session_state.matches.append(match_record)
        
        st.success(f"✅ Analysis saved to history! {home} vs {away} = {tier}")

with tab2:
    st.header("📊 PERFORMANCE DASHBOARD")
    
    if st.session_state.matches:
        df = pd.DataFrame(st.session_state.matches)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Matches", len(df))
        with col2:
            strong = len(df[df['Tier'].str.contains('🔵')])
            st.metric("🔵 STRONG", strong)
        with col3:
            moderate = len(df[df['Tier'].str.contains('🟡')])
            st.metric("🟡 MODERATE", moderate)
        with col4:
            avoid = len(df[df['Tier'].str.contains('🔴')])
            st.metric("🔴 AVOID", avoid)
        
        # Distribution Chart
        st.subheader("Score Distribution")
        if 'Score' in df.columns:
            df['Score_num'] = df['Score'].astype(float)
            fig = go.Figure(data=[go.Histogram(x=df['Score_num'], nbinsx=14, 
                                             marker_color='#1E3A8A')])
            fig.update_layout(
                xaxis_title="Total Score",
                yaxis_title="Frequency",
                height=300,
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent Matches
        st.subheader("Recent Analyses")
        st.dataframe(df.sort_values('Date', ascending=False).head(10), 
                    use_container_width=True, hide_index=True)
        
        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 EXPORT TO CSV",
            data=csv,
            file_name=f"draw_predictions_{datetime.now().date()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("👈 Analyze matches in the first tab to populate dashboard")

with tab3:
    st.header("⚡ QUICK SCREENING")
    st.markdown("Rapid pre-analysis to filter matches worth detailed look")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quick_league = st.selectbox("League Draw Rate", 
            ["Very High (30%+)", "High (27-30%)", "Average (24-27%)", 
             "Low (21-24%)", "Very Low (<21%)"])
        
        quick_goals = st.select_slider("Goal Density",
            options=["Very Low (<1.0)", "Low (1.0-1.2)", "Medium (1.2-1.4)", 
                    "High (1.4-1.6)", "Very High (>1.6)"])
    
    with col2:
        quick_parity = st.radio("Team Parity", 
            ["Very Even (0-2 pos)", "Close (3-4 pos)", "Moderate Gap (5-6 pos)", 
             "Large Gap (7+ pos)"])
        
        quick_context = st.selectbox("Match Context",
            ["Neutral/Cautious", "Derby/Rivalry", "One Team Motivated", 
             "Must-Win Situation"])
    
    if st.button("🔍 QUICK ASSESS", use_container_width=True):
        score = 0
        details = []
        
        # League scoring
        if "Very High" in quick_league or "High" in quick_league:
            score += 1
            details.append("✅ League: Good draw rate")
        elif "Average" in quick_league:
            score += 0.5
            details.append("⚠️ League: Average rate")
        else:
            details.append("❌ League: Low draw rate")
        
        # Goal density
        if "Very Low" in quick_goals or "Low" in quick_goals:
            score += 1
            details.append("✅ Goals: Low scoring")
        elif "Medium" in quick_goals:
            score += 0.5
            details.append("⚠️ Goals: Medium scoring")
        else:
            details.append("❌ Goals: High scoring")
        
        # Parity
        if "Very Even" in quick_parity:
            score += 1
            details.append("✅ Parity: Very even")
        elif "Close" in quick_parity:
            score += 0.5
            details.append("⚠️ Parity: Close match")
        else:
            details.append("❌ Parity: Gap too large")
        
        # Context
        if quick_context in ["Neutral/Cautious", "Derby/Rivalry"]:
            score += 1
            details.append(f"✅ Context: {quick_context}")
        elif quick_context == "One Team Motivated":
            score += 0.5
            details.append("⚠️ Context: One team motivated")
        else:
            details.append("❌ Context: Must-win imbalance")
        
        # Result
        st.markdown("---")
        if score >= 3.5:
            st.markdown('<div class="verdict-box strong-draw"><h3>🎯 WORTH DETAILED ANALYSIS</h3><p>High draw potential - proceed to full analysis</p></div>', 
                       unsafe_allow_html=True)
        elif score >= 2.5:
            st.markdown('<div class="verdict-box moderate-draw"><h3>🤔 CONSIDER ANALYSIS</h3><p>Moderate potential - check recent form</p></div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="verdict-box avoid"><h3>⏭️ SKIP</h3><p>Low draw probability - focus elsewhere</p></div>', 
                       unsafe_allow_html=True)
        
        st.markdown("**Details:**")
        for detail in details:
            st.write(f"- {detail}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px;">
    <p><strong>DEFENSIVE DRAW MODEL v2.1</strong> • 7-Layer Analysis • Track Every Bet • Never Chase Losses</p>
    <p style="font-size: 0.8rem;">Remember: This tool aids decision-making. You are responsible for your bets.</p>
</div>
""", unsafe_allow_html=True)
