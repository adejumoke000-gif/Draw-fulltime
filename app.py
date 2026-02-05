import streamlit as st

st.set_page_config(page_title="Draw Predictor", layout="wide")
st.title("🔮 Draw Prediction Model")
st.success("App is working! Add full code next.")

league_rate = st.slider("League Draw Rate %", 15.0, 45.0, 28.5)
avg_goals = st.slider("Average Goals", 0.5, 3.0, 1.2)

if league_rate >= 26 and avg_goals <= 1.15:
    st.markdown("### 🔵 POTENTIAL DRAW")
elif league_rate >= 23 and avg_goals <= 1.35:
    st.markdown("### 🟡 POSSIBLE DRAW")
else:
    st.markdown("### 🔴 UNLIKELY")
