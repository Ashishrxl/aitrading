import numpy as np

def calculate_pcr(df):
    return df['PE_OI'].sum() / df['CE_OI'].sum()

def max_pain(df):
    pain = []

    for strike in df['strikePrice']:
        total = abs(df['CE_OI']*(df['strikePrice']-strike)).sum() + \
                abs(df['PE_OI']*(strike-df['strikePrice'])).sum()

        pain.append(total)

    return df.iloc[np.argmin(pain)]['strikePrice']