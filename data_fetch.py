import requests
import pandas as pd
import time


def get_option_chain(symbol):

    base_url = "https://www.nseindia.com"
    api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json"
    }

    session = requests.Session()

    try:
        # Step 1: Load NSE homepage to get cookies
        session.get(base_url, headers=headers, timeout=10)

        # Small delay helps avoid blocking
        time.sleep(1)

        # Step 2: Fetch Option Chain
        response = session.get(api_url, headers=headers, timeout=10)

        data = response.json()

        # If NSE blocks → retry once
        if "records" not in data:
            time.sleep(2)
            session.get(base_url, headers=headers)
            response = session.get(api_url, headers=headers)
            data = response.json()

        if "records" not in data:
            return pd.DataFrame()

        records = data["records"]["data"]

        df = pd.DataFrame(records)

        df = df.dropna(subset=["CE", "PE"])

        df["CE_OI"] = df["CE"].apply(lambda x: x.get("openInterest", 0))
        df["PE_OI"] = df["PE"].apply(lambda x: x.get("openInterest", 0))

        df["CE_LTP"] = df["CE"].apply(lambda x: x.get("lastPrice", 0))
        df["PE_LTP"] = df["PE"].apply(lambda x: x.get("lastPrice", 0))

        df["CE_IV"] = df["CE"].apply(lambda x: x.get("impliedVolatility", 0))
        df["PE_IV"] = df["PE"].apply(lambda x: x.get("impliedVolatility", 0))

        df = df[
            [
                "strikePrice",
                "CE_OI",
                "PE_OI",
                "CE_LTP",
                "PE_LTP",
                "CE_IV",
                "PE_IV"
            ]
        ]

        return df.sort_values("strikePrice")

    except Exception as e:
        print("NSE Fetch Error:", e)
        return pd.DataFrame()