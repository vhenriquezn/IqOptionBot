import requests
import os
import time
import pandas as pd
from datetime import datetime
from estrategias import ma_cross, topbot, momentum


def borrar_lineas(n):
    for _ in range(n):
        print("\033[F\033[K", end="")

def enviar_telegram(token, chat_id, mensaje):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensaje}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

def cargar_config(ruta):
    config = {}
    with open(ruta, "r") as f:
        for linea in f:
            if "=" in linea:
                clave, valor = linea.strip().split("=")
                config[clave.strip()] = valor.strip()
    return config

def get_estrategia():
    estrategias = {
        "1": ("Cruzamiento de medias móviles (SMA)", ma_cross.calcular_senal_ma, 60, 5),
        "2": ("TopBot", topbot.calcular_senal_topbot, 1, 2),
        "3": ("Momentum", momentum.calcular_senal_momentum, 5, 2),
        "4": "Salir"
    }

    print("\n📊 Estrategias disponibles:\n")
    for clave, valor in estrategias.items():
        if clave == "4":
            print(f"   [{clave}] {valor}")
        else:
            print(f"   [{clave}] {valor[0]}")

    while True:
        eleccion = input("\nSeleccione una estrategia (número): ")
        if eleccion in estrategias:
            if eleccion == "4":
                print("🚪 Saliendo de la selección de estrategia.")
                return None
            borrar_lineas(len(estrategias) + 4)
            print(f"✅ Estrategia seleccionada: {estrategias[eleccion][0]}\n")
            return estrategias[eleccion][1], estrategias[eleccion][2], estrategias[eleccion][3], eleccion
        else:
            print("❌ Opción no válida. Intente nuevamente.")

def validar_entrada(df, tipo_senal: str, sma_periodo):
    df['SMA'] = calcular_sma(df, sma_periodo)
    vela_actual = df.iloc[-1]
        
    if tipo_senal == "call" and vela_actual["Close"] > vela_actual["SMA"]:
        return True
    elif tipo_senal == "put" and vela_actual["Close"] < vela_actual["SMA"]:
        return True
    return False
    
def calcular_sma(df, periodos):
    return df['Close'].rolling(window = periodos).mean()

def mostrar_tabla(operaciones, lineas_clr):
    borrar_lineas(lineas_clr)
    ganancia_total = sum(op['lucro'] for op in operaciones)
    for i, op in enumerate(operaciones, start=1):
        if i == len(operaciones):
            print(f"║ {i:^3} ║ {op['hora']:^8} ║ {op['paridad']:^11} ║ {op['direccion']:^9} ║{op['resultado']:^10}║{op['mg']:^4}║ {op['inversion']:^9} ║ {op['lucro']:>7.2f} ║")
    print("╚═════╩══════════╩═════════════╩═══════════╬═══════════╩════╩═══════════╬═════════╣")
    print(f"{' ':>43}║{'Ganancias de la sesion':^28}║ {ganancia_total:>7.2f} ║")
    print(f"{' ':>43}╚════════════════════════════╩═════════╝\n\n")
    return ganancia_total


def guardar_operaciones_excel(operaciones, nombre_archivo="operaciones.xlsx"):
    df_nuevas = pd.DataFrame(operaciones)
    if df_nuevas.empty:
        print("⚠️ No hay operaciones nuevas para guardar.")
        return
    try:
        if os.path.exists(nombre_archivo):
            df_existente = pd.read_excel(nombre_archivo, engine="openpyxl")
            df_total = pd.concat([df_existente, df_nuevas], ignore_index=True)
        else:
            df_total = df_nuevas
        df_total.to_excel(nombre_archivo, index=False, engine="openpyxl")
        print(f"✅ Operaciones añadidas a {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al guardar en Excel: {e}")
