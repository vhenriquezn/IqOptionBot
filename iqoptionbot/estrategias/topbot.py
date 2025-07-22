def calculate_topbot(high, low, close):
    if high - low == 0:
        return 0  # evitar división por cero
    return 2 * (high - close) / (high - low) - 1

def calcular_senal_topbot(df):
    if len(df) < 1:
        return None

    row = df.iloc[-1]
    value = calculate_topbot(row["High"], row["Low"], row["Close"])

    if value >= 0.8:
        return "call"
    elif value <= -0.8:
        return "put"
    return None
