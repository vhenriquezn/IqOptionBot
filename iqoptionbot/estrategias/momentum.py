def calcular_senal_momentum(df):
    if len(df) < 4:
        return None
    v1 = df.iloc[ - 3]
    v2 = df.iloc[- 2]
    v3 = df.iloc[- 1]
    # 3 velas bajistas
    if v1['close'] < v1['open'] and v2['close'] < v2['open'] and v3['close'] < v3['open']:
        return "call"
    # 3 velas alcistas
    elif v1['close'] > v1['open'] and v2['close'] > v2['open'] and v3['close'] > v3['open']:
        return "put"
    return None
