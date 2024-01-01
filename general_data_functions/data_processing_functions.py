
def vwap_vanilla(df):
    q = df.amount.values
    p = df.price.values
    return df.assign(vwap=(p * q).cumsum() / q.cumsum())

def vwap(df):
    df = df.groupby(df.index.date, group_keys=False).apply(vwap_vanilla)
    return df