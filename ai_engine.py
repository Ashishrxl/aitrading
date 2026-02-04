import google.generativeai as genai
import streamlit as st

genai.configure(api_key=st.secrets["KEY_1"])

model = genai.GenerativeModel("gemini-pro")

def ai_analysis(pcr, vix, news):

    prompt = f"""
    Analyze market condition:

    PCR: {pcr}
    VIX: {vix}
    News: {news}

    Provide:
    - Market Sentiment
    - Trading Guidance
    - Risk Warning
    - Beginner Explanation
    """

    response = model.generate_content(prompt)

    return response.text