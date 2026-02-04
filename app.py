import streamlit as st
import plotly.express as px
import pandas as pd

from data_fetch import get_option_chain
from analysis import calculate_pcr, max_pain
from news import get_market_news
from ai_engine import ai_analysis

st.set_page_config(layout="wide")

st.title("📊 AI Options Trading Mentor")

index = st.selectbox("Select Index", ["NIFTY","BANKNIFTY"])

df = get_option_chain(index)

# -------- Charts --------

fig = px.bar(df, x="strikePrice", y=["CE_OI","PE_OI"],
             title="Open Interest Distribution")

st.plotly_chart(fig)

# -------- PCR --------

pcr = calculate_pcr(df)
st.metric("Put Call Ratio", round(pcr,2),
          help="PCR shows market sentiment")

# -------- Max Pain --------

mp = max_pain(df)
st.metric("Max Pain", mp,
          help="Expiry price magnet level")

# -------- VIX (Static placeholder) --------
vix = 15
st.metric("India VIX", vix,
          help="Market volatility indicator")

# -------- Education --------

with st.expander("📘 Why These Metrics Matter"):
    st.write("""
    PCR indicates market sentiment.
    High PCR suggests bullish positioning.
    Max Pain shows likely expiry level.
    VIX measures volatility risk.
    """)

# -------- News --------

news = get_market_news()

st.subheader("📰 Market News")

for n in news:
    st.write("•", n)

# -------- AI Analysis --------

if st.button("🤖 Run AI Market Guidance"):
    result = ai_analysis(pcr, vix, news)
    st.success(result)

# -------- Beginner Toggle --------

if st.checkbox("Beginner Mode"):
    st.info("""
    Delta → Direction sensitivity  
    Gamma → Breakout risk  
    Theta → Time decay  
    Vega → Volatility effect  
    """)
