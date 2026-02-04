import requests
import pandas as pd


def get_option_chain(symbol):
    """
    Fetch NSE Option Chain Data Safely
    """

    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json"
    }

    try:
        session = requests.Session()

        # Step 1: Visit NSE homepage (required to get cookies)
        session.get("https://www.nseindia.com", headers=headers, timeout=10)

        # Step 2: Fetch option chain data
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise Exception(f"NSE API Error: {response.status_code}")

        data = response.json()

        # Safety check
        if "records" not in data:
            raise Exception("NSE response format changed or request blocked")

        records = data["records"]["data"]

        df = pd.DataFrame(records)

        # Remove rows where CE or PE missing
        df = df.dropna(subset=["CE", "PE"])

        # Extract required values
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
        print("Error fetching NSE data:", e)
        return pd.DataFrame()