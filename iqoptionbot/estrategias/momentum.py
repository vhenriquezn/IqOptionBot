def calcular_senal_momentum(df):
    if len(df) < 4:
        return None
    v1 = df.iloc[ - 3]
    v2 = df.iloc[- 2]
    v3 = df.iloc[- 1]
    # 3 velas bajistas
    if v1['Close'] < v1['Open'] and v2['Close'] < v2['Open'] and v3['Close'] < v3['Open']:
        return "call"
    # 3 velas alcistas
    elif v1['Close'] > v1['Open'] and v2['Close'] > v2['Open'] and v3['Close'] > v3['Open']:
        return "put"
    return None
        

