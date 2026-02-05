import pandas as pd
import requests


def get_option_chain(symbol):

    try:
        # NSE CDN endpoint (More stable)
        url = f"https://cdn.nseindia.com/api/option-chain-indices?symbol={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=10)

        data = response.json()

        # Safety check
        if "records" not in data:
            print("Invalid response from NSE CDN")
            return pd.DataFrame()

        records = data["records"]["data"]

        rows = []

        for item in records:

            strike = item["strikePrice"]

            ce = item.get("CE")
            pe = item.get("PE")

            if ce and pe:
                rows.append({
                    "strikePrice": strike,
                    "CE_OI": ce.get("openInterest", 0),
                    "PE_OI": pe.get("openInterest", 0),
                    "CE_LTP": ce.get("lastPrice", 0),
                    "PE_LTP": pe.get("lastPrice", 0),
                    "CE_IV": ce.get("impliedVolatility", 0),
                    "PE_IV": pe.get("impliedVolatility", 0),
                })

        df = pd.DataFrame(rows)

        return df.sort_values("strikePrice")

    except Exception as e:
        print("CDN Fetch Error:", e)
        return pd.DataFrame()