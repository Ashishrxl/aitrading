import streamlit as st
import plotly.express as px
import pandas as pd

from data_fetch import get_option_chain
from analysis import calculate_pcr, max_pain
from news import get_market_news
from ai_engine import ai_analysis


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Options Trading Mentor",
    layout="wide"
)

st.title("📊 AI Options Trading Mentor")


# ---------------------------------------------------
# DISCLAIMER
# ---------------------------------------------------
st.warning(
    "⚠️ This tool provides analytical insights only. "
    "It is NOT financial advice. Trading involves risk."
)


# ---------------------------------------------------
# INDEX SELECTION
# ---------------------------------------------------
index = st.selectbox(
    "Select Index",
    ["NIFTY", "BANKNIFTY", "FINNIFTY"]
)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# ---------------------------------------------------
# CACHE DATA
# ---------------------------------------------------
@st.cache_data(ttl=300)
def load_option_data(symbol):
    return get_option_chain(symbol)


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
try:
    df = load_option_data(index)

    if df.empty:
        st.error("⚠️ NSE data unavailable. Try again later.")
        st.stop()

except Exception as e:
    st.error("Data fetch failed")
    st.write(e)
    st.stop()


# ---------------------------------------------------
# OPTION CHAIN TABLE
# ---------------------------------------------------
st.subheader("📋 Option Chain Data")
st.dataframe(df, use_container_width=True)


# ---------------------------------------------------
# OI CHART
# ---------------------------------------------------
st.subheader("📊 Open Interest Distribution")

fig = px.bar(
    df,
    x="strikePrice",
    y=["CE_OI", "PE_OI"],
    barmode="group"
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------
# METRICS CALCULATION
# ---------------------------------------------------
pcr = calculate_pcr(df)
mp = max_pain(df)

# Simple placeholder VIX
vix = 15


# ---------------------------------------------------
# METRICS DISPLAY
# ---------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Put Call Ratio",
        round(pcr, 2),
        help="PCR indicates market sentiment. Higher PCR suggests bullish positioning."
    )

with col2:
    st.metric(
        "Max Pain",
        mp,
        help="Max Pain is the strike where maximum option sellers benefit."
    )

with col3:
    st.metric(
        "India VIX",
        vix,
        help="VIX measures market volatility. Higher VIX means higher uncertainty."
    )


# ---------------------------------------------------
# IMPLIED VOLATILITY CHART
# ---------------------------------------------------
st.subheader("📉 Implied Volatility")

iv_fig = px.line(
    df,
    x="strikePrice",
    y=["CE_IV", "PE_IV"]
)

st.plotly_chart(iv_fig, use_container_width=True)


# ---------------------------------------------------
# EDUCATION PANEL
# ---------------------------------------------------
with st.expander("📘 Why These Metrics Matter"):
    st.write("""
    • **PCR** → Shows market sentiment  
    • **Max Pain** → Possible expiry magnet level  
    • **VIX** → Measures market volatility  
    • **Implied Volatility** → Shows premium pricing
    """)


# ---------------------------------------------------
# BEGINNER MODE
# ---------------------------------------------------
if st.checkbox("🧑‍🎓 Beginner Mode"):
    st.info("""
    **Delta** → Option price sensitivity to index movement  
    **Gamma** → Speed of delta change  
    **Theta** → Time decay of options  
    **Vega** → Sensitivity to volatility  
    """)


# ---------------------------------------------------
# NEWS PANEL
# ---------------------------------------------------
st.subheader("📰 Market News")

try:
    news_list = get_market_news()

    for news in news_list:
        st.write("•", news)

except:
    news_list = []
    st.write("News unavailable")


# ---------------------------------------------------
# AI ANALYSIS PANEL
# ---------------------------------------------------
st.subheader("🤖 AI Market Guidance")

if st.button("Run AI Analysis"):

    try:
        ai_result = ai_analysis(pcr, vix, news_list)

        st.success(ai_result)

    except Exception as e:
        st.error("AI analysis failed")
        st.write(e)


# ---------------------------------------------------
# STRATEGY GUIDANCE
# ---------------------------------------------------
st.subheader("📌 Trading Guidance")

if pcr > 1.2:
    st.success("Market Bias: Bullish")
elif pcr < 0.8:
    st.error("Market Bias: Bearish")
else:
    st.info("Market Bias: Neutral")


# ---------------------------------------------------
# RISK GUIDANCE
# ---------------------------------------------------
st.subheader("⚠️ Risk Guidance")

st.write("""
• Never risk more than 2% capital per trade  
• Avoid trading during major news events  
• Use stop loss in option buying  
• Option selling carries unlimited risk without hedge  
""")


# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.caption("Built with Streamlit + NSE Data + Google Gemini AI")