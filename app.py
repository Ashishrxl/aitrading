import streamlit as st
import pandas as pd
import requests
import traceback
import yfinance as yf
import google.generativeai as genai
from streamlit.components.v1 import html


html(
  """
  <script>
  try {
    const sel = window.top.document.querySelectorAll('[href*="streamlit.io"], [href*="streamlit.app"]');
    sel.forEach(e => e.style.display='none');
  } catch(e) { console.warn('parent DOM not reachable', e); }
  </script>
  """,
  height=0
)

disable_footer_click = """
    <style>
    footer {pointer-events: none;}
    </style>
"""
st.markdown(disable_footer_click, unsafe_allow_html=True)


# --- CSS: Hide all unwanted items but KEEP sidebar toggle ---
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stStatusWidget"] {display: none;}
[data-testid="stToolbar"] {display: none;}
a[href^="https://github.com"] {display: none !important;}
a[href^="https://streamlit.io"] {display: none !important;}

/* The following specifically targets and hides all child elements of the header's right side,
   while preserving the header itself and, by extension, the sidebar toggle button. */
header > div:nth-child(2) {
    display: none;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Options Analyzer", layout="wide")

st.title("📊 AI Option Chain Analyzer")

# Debug Toggle
debug_mode = st.toggle("🐞 Debug Mode", value=True)

def debug_log(msg):
    if debug_mode:
        st.sidebar.write(msg)

# -----------------------------
# GOOGLE GEMINI SETUP
# -----------------------------
GOOGLE_API_KEY = st.secrets.get("KEY_1", "")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# -----------------------------
# INDEX SELECTION
# -----------------------------
index_choice = st.selectbox(
    "Select Index",
    ["NIFTY", "BANKNIFTY"]
)

symbol_map = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

# -----------------------------
# FETCH OPTION CHAIN NSE
# -----------------------------
def get_nse_option_chain(symbol):

    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()

        # First request to get cookies
        session.get("https://www.nseindia.com", headers=headers)

        response = session.get(url, headers=headers)

        debug_log(f"NSE Status Code: {response.status_code}")

        data = response.json()

        records = data["records"]["data"]

        rows = []

        for item in records:
            strike = item["strikePrice"]

            ce = item.get("CE", {})
            pe = item.get("PE", {})

            rows.append({
                "Strike": strike,
                "Call OI": ce.get("openInterest"),
                "Call IV": ce.get("impliedVolatility"),
                "Put OI": pe.get("openInterest"),
                "Put IV": pe.get("impliedVolatility"),
            })

        df = pd.DataFrame(rows)

        return df

    except Exception as e:
        debug_log("NSE Error:")
        debug_log(traceback.format_exc())
        return None


# -----------------------------
# FALLBACK OPTION DATA USING YFINANCE
# -----------------------------
def get_yfinance_options(symbol):

    try:
        ticker = yf.Ticker(symbol)

        expiries = ticker.options
        debug_log(f"Expiry Dates: {expiries}")

        if len(expiries) == 0:
            return None

        opt = ticker.option_chain(expiries[0])

        calls = opt.calls[["strike", "openInterest", "impliedVolatility"]]
        puts = opt.puts[["strike", "openInterest", "impliedVolatility"]]

        df = calls.merge(puts, on="strike", suffixes=(" Call", " Put"))

        df.rename(columns={"strike": "Strike"}, inplace=True)

        return df

    except Exception:
        debug_log("YFinance Error:")
        debug_log(traceback.format_exc())
        return None


# -----------------------------
# GET VIX
# -----------------------------
def get_vix():

    try:
        vix = yf.Ticker("^INDIAVIX")
        data = vix.history(period="1d")
        return float(data["Close"].iloc[-1])

    except Exception:
        debug_log("VIX Error:")
        debug_log(traceback.format_exc())
        return None


# -----------------------------
# NEWS FETCH
# -----------------------------
def get_news():

    try:
        url = "https://newsapi.org/v2/top-headlines?category=business&country=in&apiKey=demo"
        res = requests.get(url)

        articles = res.json().get("articles", [])[:5]

        news_text = "\n".join([a["title"] for a in articles])

        return news_text

    except Exception:
        debug_log("News Error:")
        debug_log(traceback.format_exc())
        return "No News"


# -----------------------------
# AI ANALYSIS
# -----------------------------
def ai_analysis(option_df, vix, news):

    if not GOOGLE_API_KEY:
        return "⚠️ Add Google API Key in secrets."

    try:
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
        You are an options trading expert.

        Analyze following option chain summary:
        {option_df.head(20).to_string()}

        VIX: {vix}

        News:
        {news}

        Provide:
        - Market Bias
        - Key Support Resistance
        - Risk Warning
        """

        response = model.generate_content(prompt)

        return response.text

    except Exception:
        debug_log("AI Error:")
        debug_log(traceback.format_exc())
        return "AI Analysis Failed"


# -----------------------------
# FETCH DATA
# -----------------------------
st.header(f"📈 {index_choice} Option Chain")

df = get_nse_option_chain(index_choice)

if df is None:
    st.warning("⚠️ NSE failed. Trying backup source...")
    df = get_yfinance_options(symbol_map[index_choice])

if df is None:
    st.error("❌ All Data Sources Failed")
    st.stop()

st.dataframe(df)

# -----------------------------
# CALCULATIONS
# -----------------------------
st.subheader("📊 Derived Metrics")

df["PCR"] = df["Put OI"] / df["Call OI"]

st.line_chart(df.set_index("Strike")[["Call OI", "Put OI"]])

# -----------------------------
# VIX DISPLAY
# -----------------------------
vix = get_vix()

if vix:
    st.metric("India VIX", round(vix, 2))

# -----------------------------
# NEWS
# -----------------------------
st.subheader("📰 Market News")
news = get_news()
st.write(news)

# -----------------------------
# AI OUTPUT
# -----------------------------
st.subheader("🤖 AI Trading Guidance")

analysis = ai_analysis(df, vix, news)

st.info(analysis)

# -----------------------------
# USER EDUCATION
# -----------------------------
st.subheader("📘 Trading Guidance")

st.markdown("""
✔ High PCR → Bullish Sentiment  
✔ Low PCR → Bearish Sentiment  
✔ High VIX → Market Volatility  
✔ Rising OI → Strong Trend  
✔ Falling OI → Weak Trend  
""")