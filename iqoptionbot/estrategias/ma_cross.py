import numpy as np

def wma(data, period):
    return data.rolling(window=period).apply(
        lambda x: np.average(x, weights=np.arange(1, len(x)+1)), raw=True
    )

def calcular_senal_ma(df, fast=1, slow=34, signal=5):
    if len(df) < max(fast, slow, signal):
        return None
    df["HL2"] = (df["high"] + df["low"]) / 2
    df["MA_Fast"] = df["HL2"].rolling(window=fast).mean()
    df["MA_Slow"] = df["HL2"].rolling(window=slow).mean()
    df["Buffer1"] = df["MA_Fast"] - df["MA_Slow"]
    df["Buffer2"] = wma(df["Buffer1"], signal)

    df.dropna(subset=["Buffer2"], inplace=True)

    df["Buy_Signal"] = np.where((df["Buffer1"] > df["Buffer2"]) & (df["Buffer1"].shift(1) <= df["Buffer2"].shift(1)), 1, 0)
    df["Sell_Signal"] = np.where((df["Buffer1"] < df["Buffer2"]) & (df["Buffer1"].shift(1) >= df["Buffer2"].shift(1)), 1, 0)

    ultima_fila = df.iloc[-1]

    if ultima_fila['Buy_Signal'] == 1:
        return "call"
    if ultima_fila['Sell_Signal'] == 1:
        return "put"
    return None
