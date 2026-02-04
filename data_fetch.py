from nsepython import *
import pandas as pd

def get_option_chain(index):
    data = nse_optionchain_scrapper(index)
    records = data['records']['data']

    df = pd.DataFrame(records)
    df = df.dropna(subset=["CE", "PE"])

    df['CE_OI'] = df['CE'].apply(lambda x: x['openInterest'])
    df['PE_OI'] = df['PE'].apply(lambda x: x['openInterest'])

    df['CE_LTP'] = df['CE'].apply(lambda x: x['lastPrice'])
    df['PE_LTP'] = df['PE'].apply(lambda x: x['lastPrice'])

    return df[['strikePrice','CE_OI','PE_OI','CE_LTP','PE_LTP']]