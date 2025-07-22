import numpy as np

def wma(data, period):
    return data.rolling(window=period).apply(
        lambda x: np.average(x, weights=np.arange(1, len(x)+1)), raw=True
        )

def calcular_senal_ma(df, fast=1, slow=34, signal=5):
    df["HL2"] = (df["High"] + df["Low"]) / 2
    df["MA_Fast"] = df["HL2"].rolling(window=fast).mean()
    df["MA_Slow"] = df["HL2"].rolling(window=slow).mean()
    df["Buffer1"] = df["MA_Fast"] - df["MA_Slow"]
    df["Buffer2"] = wma(df["Buffer1"], signal)

    df.dropna(subset=["Buffer2"], inplace=True)

    df["Buy_Signal"] = np.where((df["Buffer1"] > df["Buffer2"]) & (df["Buffer1"].shift(1) <= df["Buffer2"].shift(1)), 1, 0)
    df["Sell_Signal"] = np.where((df["Buffer1"] < df["Buffer2"]) & (df["Buffer1"].shift(1) >= df["Buffer2"].shift(1)), 1, 0)

    if len(df) < 2:
        return None

    ultima_fila = df.iloc[-1]
    UMBRAL_RUIDO = sugerir_umbral_ruido(df)
    #if abs(ultima_fila["Buffer1"] - ultima_fila["Buffer2"]) < UMBRAL_RUIDO:
       #return None  # Descartar señal por ruido

    if ultima_fila['Buy_Signal'] == 1:
        return "call"
    if ultima_fila['Sell_Signal'] == 1:
        return "put"
    return None

def detectar_tendencia(df):
    if len(df) < 21:
        return "indefinida"
    
    ema_actual = df["EMA20"].iloc[-1]
    ema_anterior = df["EMA20"].iloc[-2]

    if ema_actual > ema_anterior:
        return "alcista"
    elif ema_actual < ema_anterior:
        return "bajista"
    else:
        return "lateral"

def sugerir_umbral_ruido(df):
    df["diferencia"] = abs(df["Buffer1"] - df["Buffer2"])

    stats = df["diferencia"].describe()

    mean_diff = stats["mean"]
    if mean_diff < 0.00015:
        sugerencia = 0.00005
    elif mean_diff < 0.00030:
        sugerencia = 0.00010
    elif mean_diff < 0.00060:
        sugerencia = 0.00020
    else:
        sugerencia = 0.00030

    return sugerencia
