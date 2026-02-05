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
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    .verdict-box {
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .strong-draw {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 4px solid #28a745;
        color: #155724;
    }
    .moderate-draw {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 4px solid #ffc107;
        color: #856404;
    }
    .avoid {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border: 4px solid #dc3545;
        color: #721c24;
    }
    .layer-card {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        background: white;
        border-left: 6px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 5px 5px 0 0;
        padding: 10px 16px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🔮 DEFENSIVE DRAW PREDICTOR</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">7-Layer Analysis Model • Capital Preservation First • Profit Second</p>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if 'matches' not in st.session_state:
    st.session_state.matches = []

# SIDEBAR - Model Configuration
with st.sidebar:
    st.header("⚙️ MODEL CONFIGURATION")
    
    with st.expander("Layer Thresholds", expanded=True):
        st.subheader("Layer 1: League Baseline")
        col1, col2 = st.columns(2)
        with col1:
            l1_pass_min = st.number_input("PASS Min %", 20, 35, 26, 1)
            l1_pass_max = st.number_input("PASS Max %", 25, 40, 32, 1)
        with col2:
            l1_caution_min = st.number_input("CAUTION Min %", 20, 30, 23, 1)
        
        st.subheader("Layer 2: Goal Density")
        l2_pass = st.number_input("PASS Max Goals", 0.8, 1.5, 1.15, 0.05)
        l2_caution = st.number_input("CAUTION Max Goals", 1.0, 1.8, 1.35, 0.05)
    
    st.markdown("---")
    st.header("📋 MATCH HISTORY")
    
    if st.session_state.matches:
        df_history = pd.DataFrame(st.session_state.matches)
        st.dataframe(
            df_history[['Date', 'Home', 'Away', 'Tier', 'Total_Score']].tail(8),
            use_container_width=True,
            hide_index=True
        )
        
        # Statistics
        strong_count = len(df_history[df_history['Tier'] == "🔵 STRONG DRAW"])
        moderate_count = len(df_history[df_history['Tier'] == "🟡 MODERATE"])
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("🔵 STRONG", strong_count)
        with col_b:
            st.metric("🟡 MODERATE", moderate_count)
        
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.matches = []
            st.rerun()
    else:
        st.info("No matches analyzed yet")
    
    st.markdown("---")
    st.markdown("""
    **🎯 STAKING RULES (NON-NEGOTIABLE)**
    - 🔵 STRONG DRAW: 1.0 unit single
    - 🟡 MODERATE: 0.5 units each (double max)
    - 🔴 AVOID: NO BET
    
    **🚫 NO PROGRESSIVE STAKING**
    > Fibonacci/Martingale systems are REJECTED
    > They contradict "capital preservation first"
    
    **🚨 FINAL RULE**
    > If you feel pressure to recover losses — DO NOT BET
    """)

# MAIN TABS
tab1, tab2, tab3 = st.tabs(["🧠 7-LAYER ANALYSIS", "📊 PERFORMANCE DASHBOARD", "📈 MODEL INFO"])

with tab1:
    st.header("COMPLETE 7-LAYER ANALYSIS")
    
    # Match Details
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 MATCH DETAILS")
            match_date = st.date_input("Match Date", datetime.now())
            league = st.text_input("League", "Premier League", help="Enter league name")
            home_team = st.text_input("Home Team", "Arsenal")
            away_team = st.text_input("Away Team", "Liverpool")
        
        with col2:
            st.subheader("🎲 MARKET ODDS")
            draw_odds = st.slider("Draw Odds (Decimal)", 2.0, 5.0, 3.1, 0.1,
                                help="Market odds for draw")
            st.caption(f"Odds Range: 2.80–3.30 = Healthy | < 2.50 = Suspicious | > 3.60 = Market rejection")
    
    # 7 LAYERS INPUT
    st.subheader("🧱 7-LAYER PARAMETERS")
    
    layers_col1, layers_col2 = st.columns(2)
    
    with layers_col1:
        # LAYER 1: League Draw Baseline
        st.markdown("**📊 LAYER 1: League Draw Rate**")
        league_draw_rate = st.slider(
            "League average draw rate %",
            15.0, 45.0, 28.5, 0.5,
            help="League's current season draw percentage"
        )
        
        # LAYER 2: Goal Density Filter
        st.markdown("**⚽ LAYER 2: Goal Density**")
        home_avg_goals = st.number_input("Home avg goals scored", 0.0, 4.0, 1.2, 0.1)
        away_avg_goals = st.number_input("Away avg goals scored", 0.0, 4.0, 1.1, 0.1)
        avg_goals = (home_avg_goals + away_avg_goals) / 2
        st.caption(f"Average goals: **{avg_goals:.2f}** (≤1.15 = PASS, 1.16-1.35 = CAUTION, >1.35 = REJECT)")
        
        # LAYER 3: Scoreline Distribution (LAST 10 MATCHES)
        st.markdown("**📈 LAYER 3: Recent Scorelines (Last 10 Matches)**")
        col_a, col_b = st.columns(2)
        with col_a:
            scoreline_0_0 = st.number_input("0-0 in last 10", 0, 10, 2, 1,
                                          help="Number of 0-0 draws in team's last 10 matches")
        with col_b:
            scoreline_1_1 = st.number_input("1-1 in last 10", 0, 10, 1, 1,
                                          help="Number of 1-1 draws in team's last 10 matches")
        combined_scorelines = scoreline_0_0 + scoreline_1_1
    
    with layers_col2:
        # LAYER 4: Team Strength Parity
        st.markdown("**⚖️ LAYER 4: Strength Parity**")
        table_gap = st.slider("Table position gap", 0, 20, 2, 1,
                            help="Difference in league positions (≤3 = PASS)")
        
        # LAYER 5: Form Volatility (LAST 5 MATCHES)
        st.markdown("**📉 LAYER 5: Recent Form (Last 5 Matches)**")
        home_wins_last5 = st.number_input(f"{home_team[:12]} wins (last 5)", 0, 5, 2, 1)
        away_wins_last5 = st.number_input(f"{away_team[:12]} wins (last 5)", 0, 5, 1, 1)
        combined_wins = home_wins_last5 + away_wins_last5
        st.caption(f"Combined wins: **{combined_wins}** (≤4 = PASS, 5 = CAUTION, ≥6 = REJECT)")
        
        # NEW: H2H HISTORY (LAST 5 MEETINGS)
        st.markdown("**🤝 H2H History (Last 5 Meetings)**")
        h2h_draws = st.number_input("Draws in last 5 H2H meetings", 0, 5, 1, 1,
                                   help="Number of draws in last 5 head-to-head matches")
        
        # LAYER 6: Motivation & Context
        st.markdown("**🎯 LAYER 6: Match Context**")
        motivation = st.selectbox(
            "Select match context",
            [
                "Neutral / Cautious (PASS)",
                "Derby / Local Rivalry (PASS)",
                "One Team Desperate (CAUTION)",
                "Must-Win Imbalance (REJECT)",
                "End of Season - Nothing to Play For (PASS)",
                "Cup Match - Extra Time Possible (CAUTION)"
            ],
            help="Context affects draw likelihood"
        )
    
    # PROGRESSIVE STAKING WARNING
    st.markdown("---")
    with st.container():
        st.markdown("""
        <div class="warning-box">
            <strong>🚫 PROGRESSIVE STAKING SYSTEMS REJECTED</strong><br>
            Fibonacci, Martingale, D'Alembert, etc. are <strong>BANNED</strong> from this model.<br>
            Reason: They increase risk after losses, contradicting "capital preservation first".
        </div>
        """, unsafe_allow_html=True)
    
    # ANALYZE BUTTON
    if st.button("🚀 RUN 7-LAYER ANALYSIS", type="primary", use_container_width=True):
        
        # ==================== 7-LAYER CALCULATION ====================
        layer_scores = []
        layer_statuses = []
        layer_details = []
        
        # LAYER 1: League Draw Baseline
        if l1_pass_min <= league_draw_rate <= l1_pass_max:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"League draw rate {league_draw_rate}% within optimal 26-32% range")
        elif l1_caution_min <= league_draw_rate < l1_pass_min:
            layer_scores.append(0.5)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"League draw rate {league_draw_rate}% in caution range 23-25%")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"League draw rate {league_draw_rate}% outside acceptable range")
        
        # LAYER 2: Goal Density Filter
        if avg_goals <= l2_pass:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"Avg goals {avg_goals:.2f} ≤ 1.15 (low scoring)")
        elif avg_goals <= l2_caution:
            layer_scores.append(0.5)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"Avg goals {avg_goals:.2f} in 1.16-1.35 range")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"Avg goals {avg_goals:.2f} > 1.35 (too high)")
        
        # LAYER 3: Scoreline Distribution (LAST 10 MATCHES)
        if combined_scorelines >= 4:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"{combined_scorelines} combined 0-0/1-1 in last 10 matches (≥4 required)")
        elif combined_scorelines == 3:
            layer_scores.append(0.5)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"{combined_scorelines} combined 0-0/1-1 in last 10 (3 = caution)")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"Only {combined_scorelines} combined 0-0/1-1 in last 10 matches")
        
        # LAYER 4: Team Strength Parity
        if table_gap <= 3:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"Table gap {table_gap} positions (≤3 = even)")
        elif table_gap <= 6:
            layer_scores.append(0.5)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"Table gap {table_gap} positions (4-6 = moderate)")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"Table gap {table_gap} positions (>6 = too large)")
        
        # LAYER 5: Form Volatility Check (LAST 5 MATCHES)
        if combined_wins <= 4:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"Combined wins {combined_wins} in last 5 (≤4 = low momentum)")
        elif combined_wins == 5:
            layer_scores.append(0.5)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"Combined wins {combined_wins} in last 5 (5 = moderate momentum)")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"Combined wins {combined_wins} in last 5 (≥6 = high momentum ≠ draw)")
        
        # NEW: H2H BONUS LAYER (not part of original 7, but informative)
        h2h_bonus = 0
        if h2h_draws >= 2:
            h2h_bonus = 0.5
            h2h_note = f"H2H Bonus: {h2h_draws} draws in last 5 meetings (positive)"
        elif h2h_draws == 1:
            h2h_bonus = 0
            h2h_note = f"H2H: {h2h_draws} draw in last 5 meetings (neutral)"
        else:
            h2h_bonus = -0.5
            h2h_note = f"H2H Warning: 0 draws in last 5 meetings (negative)"
        
        # LAYER 6: Motivation & Context
        if "PASS" in motivation:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"Context: {motivation.split('(')[0].strip()}")
        elif "CAUTION" in motivation:
            layer_scores.append(0.5)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"Context: {motivation.split('(')[0].strip()}")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"Context: {motivation.split('(')[0].strip()}")
        
        # LAYER 7: Market Sanity Check
        if 2.8 <= draw_odds <= 3.3:
            layer_scores.append(1.0)
            layer_statuses.append("✅ PASS")
            layer_details.append(f"Odds {draw_odds:.2f} in healthy range 2.80-3.30")
        elif draw_odds < 2.5:
            layer_scores.append(0.0)
            layer_statuses.append("❌ REJECT")
            layer_details.append(f"Odds {draw_odds:.2f} < 2.50 (suspiciously low)")
        else:
            layer_scores.append(0.0)
            layer_statuses.append("⚠️ CAUTION")
            layer_details.append(f"Odds {draw_odds:.2f} outside optimal range")
        
        # ==================== FINAL SCORE & VERDICT ====================
        total_score = sum(layer_scores)
        
        # Apply H2H bonus (informative, not part of core 7 layers)
        total_with_h2h = total_score + h2h_bonus
        total_with_h2h = max(0, min(total_with_h2h, 7.0))  # Keep within 0-7 range
        
        # Determine Tier (based on ORIGINAL 7 layers only - H2H is bonus info)
        if total_score >= 6.0:
            tier = "🔵 STRONG DRAW"
            stake = "1.0 unit (Single bet only)"
            css_class = "strong-draw"
            color = "#28a745"
        elif total_score >= 5.0:
            tier = "🟡 MODERATE DRAW"
            stake = "0.5 units each (Double max)"
            css_class = "moderate-draw"
            color = "#ffc107"
        else:
            tier = "🔴 AVOID"
            stake = "NO BET - Model rejects"
            css_class = "avoid"
            color = "#dc3545"
        
        # ==================== DISPLAY RESULTS ====================
        st.markdown("---")
        
        # VERDICT BOX
        st.markdown(f"""
        <div class="verdict-box {css_class}">
            <h1 style="font-size: 2.5rem; margin-bottom: 10px;">{tier}</h1>
            <h2 style="font-size: 3rem; margin: 10px 0;">{total_score:.1f}/7.0</h2>
            <h3 style="font-size: 1.5rem; margin-top: 10px;">{stake}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # H2H BONUS DISPLAY
        if h2h_bonus > 0:
            st.success(f"🤝 **H2H BONUS**: +{h2h_bonus} points ({h2h_draws} draws in last 5 meetings)")
            st.info(f"**Adjusted Score**: {total_score:.1f} + {h2h_bonus} = {total_with_h2h:.1f}/7.0 (H2H considered)")
        elif h2h_bonus < 0:
            st.warning(f"⚠️ **H2H WARNING**: {h2h_bonus} points (No draws in last 5 meetings)")
            st.info(f"**Adjusted Score**: {total_score:.1f} {h2h_bonus} = {total_with_h2h:.1f}/7.0 (H2H considered)")
        else:
            st.info(f"🤝 **H2H**: Neutral ({h2h_draws} draw in last 5 meetings)")
        
        # LAYER BREAKDOWN
        st.subheader("📋 7-LAYER BREAKDOWN")
        
        layer_names = [
            "League Baseline",
            "Goal Density", 
            "Scoreline Dist.",
            "Strength Parity",
            "Form Volatility",
            "Motivation",
            "Market Check"
        ]
        
        # Display layers in 2 columns
        col_left, col_right = st.columns(2)
        
        for i, (name, score, status, detail) in enumerate(zip(layer_names, layer_scores, layer_statuses, layer_details)):
            col = col_left if i < 4 else col_right
            with col:
                border_color = "#28a745" if score == 1.0 else "#ffc107" if score == 0.5 else "#dc3545"
                st.markdown(f"""
                <div class="layer-card" style="border-left-color: {border_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 1rem;">{name}</strong>
                        <span style="font-size: 1.2rem; font-weight: bold; color: {border_color};">{score:.1f}</span>
                    </div>
                    <div style="margin-top: 8px;">
                        <span style="color: {border_color}; font-weight: bold;">{status}</span><br>
                        <small style="color: #666;">{detail}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # H2H CARD
        with col_right:
            h2h_color = "#28a745" if h2h_bonus > 0 else "#ffc107" if h2h_bonus == 0 else "#dc3545"
            st.markdown(f"""
            <div class="layer-card" style="border-left-color: {h2h_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1rem;">H2H History</strong>
                    <span style="font-size: 1.2rem; font-weight: bold; color: {h2h_color};">{h2h_bonus:+.1f}</span>
                </div>
                <div style="margin-top: 8px;">
                    <span style="color: {h2h_color}; font-weight: bold;">{'✅ BONUS' if h2h_bonus > 0 else '⚠️ NEUTRAL' if h2h_bonus == 0 else '❌ WARNING'}</span><br>
                    <small style="color: #666;">{h2h_note}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # VISUALIZATION CHART
        st.subheader("📈 LAYER PERFORMANCE CHART")
        
        # Add H2H to chart for visualization
        chart_names = layer_names + ["H2H History"]
        chart_scores = layer_scores + [h2h_bonus]
        
        fig = go.Figure(data=[
            go.Bar(
                x=chart_names,
                y=chart_scores,
                marker_color=['#28a745' if s == 1.0 else '#ffc107' if s == 0.5 else '#dc3545' for s in layer_scores] + [h2h_color],
                text=[f"{s:.1f}" for s in chart_scores],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            yaxis=dict(
                range=[-0.5, 1.1],
                title="Score",
                tickvals=[-0.5, 0, 0.5, 1.0],
                ticktext=["H2H Penalty", "REJECT (0)", "CAUTION (0.5)", "PASS (1.0)"]
            ),
            xaxis=dict(title="Layer", tickangle=0),
            height=400,
            showlegend=False,
            margin=dict(t=30, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # PROGRESSIVE STAKING REJECTION CONFIRMATION
        st.markdown("""
        <div class="warning-box">
            <strong>💰
