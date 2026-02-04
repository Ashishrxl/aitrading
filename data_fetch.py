import requests
import pandas as pd

def get_option_chain(symbol):

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    session = requests.Session()

    # First hit homepage to get cookies
    session.get("https://www.nseindia.com", headers=headers)

    response = session.get(url, headers=headers)

    data = response.json()

    # -------- SAFETY CHECK --------
    if "records" not in data:
        raise Exception("NSE blocked request or API changed")

    records = data['records']['data']

    df = pd.DataFrame(records)
    df = df.dropna(subset=["CE","PE"])

    df['CE_OI'] = df['CE'].apply(lambda x: x['openInterest'])
    df['PE_OI'] = df['PE'].apply(lambda x: x['openInterest'])

    df['CE_LTP'] = df['CE'].apply(lambda x: x['lastPrice'])
    df['PE_LTP'] = df['PE'].apply(lambda x: x['lastPrice'])

    return df[['strikePrice','CE_OI','PE_OI','CE_LTP','PE_LTP']]