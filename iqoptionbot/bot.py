import pandas as pd
import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from iqoptionbot import utils

class BotModular:
    def __init__(self, login_path="login.txt", config_path="config.txt"):

        self.config = utils.cargar_config(config_path)
        login = utils.cargar_config(login_path)

        self.api = IQ_Option(email=login.get("email"), password=login.get("password"))

        self.email = login.get("email")
        self.asset = self.config.get("asset")
        self.expiration_time = int(self.config.get("expiration_time"))
        self.entrada_actual = float(self.config.get("valor_entrada"))
        self.use_mg = self.config.get("usar_martingale") == "S"
        self.nivel_mg = int(self.config.get("niveles_martingala"))
        self.factor_mg = float(self.config.get("factor_martingale"))
        self.use_stop_win = self.config.get("use_stop_win") == "S"
        self.stop_win = int(self.config.get("stop_win"))
        self.use_stop_loss = self.config.get("use_stop_loss") == "S"
        self.stop_loss = float(self.config.get("stop_loss"))
        self.use_media_movil = self.config.get("use_media_movil") == "S"
        self.periodo_medias = int(self.config.get("periodo_medias", 5))

        self.operaciones = []
        self.nivel_actual = 0

    def conectar(self):
        self.api.connect()
        while not self.api.check_connect():
            print(">> Intentando conectar...")
            time.sleep(1)
        print("✅ Conectado correctamente.\n")

    def set_account(self):
        opcion = input(f">> Estás en cuenta {self.api.get_balance_mode()}. ¿Deseas cambiar? (y/n): ").strip().lower()
        opciones_disponibles = []
        if opcion == 'y':
            balances = self.api.get_balances()
            utils.borrar_lineas(1)
            print("📊 BALANCES DISPONIBLES:\n")
            
            for i, balance in enumerate(balances.get("msg", []), start=1):
                tipo = balance.get("type")
                monto = balance.get("amount")
                moneda = balance.get("currency")
                balance_id = balance.get("id")
                torneo_id = balance.get("tournament_id")
                torneo_nombre = balance.get("tournament_name")
                #print(balance)
                tipo_str = {
                    1: "REAL",
                    4: "DEMO",
                    2: "TORNEO"
                }.get(tipo, f"Desconocido ({tipo})")
                print(f"   [{i}] {tipo_str:<8}: {monto:>8.2f} {moneda}")
                opciones_disponibles.append(tipo_str)
                
            while True:
                eleccion = input("\n>> Ingresa el número de la cuenta: ").strip()
                if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones_disponibles):
                    seleccion = opciones_disponibles[int(eleccion) - 1]
                    self.api.change_balance(seleccion)
                    break
                else:
                    print("❌ Opción inválida. Por favor, elige 1 o 2.")

        utils.borrar_lineas(len(opciones_disponibles)+4)
        print(f"{"Bienvenido/a":<17}:{self.email}\n")
        print(f"{"Tipo de cuenta":<17}:{self.api.get_balance_mode()} ${self.api.get_balance()} {self.api.get_currency()}")
        print(f"{"Valor entrada":<17}:{self.entrada_actual}")
        if self.use_stop_win:
            print(f"{"Stop Win":<17}:{stop_win}")
        if self.use_stop_loss:
            print(f"{"Stop Loss":<17}:-{stop_loss}")
        if self.use_mg:
            print(f"{"Niveles MG":<17}:{self.nivel_mg}")
        if self.use_media_movil:
            print(f"{"Periodo":<17}:{self.periodo_medias}")

    def trading_loop(self):
        self.actualizar_entrada()
        strategy, candles_quantity, espera_segundos, opcion = get_estrategia()
        if self.config.get("set_asset") == "S":
            self.asset = self.seleccionar_activo_abierto()

        print(f">> Bot iniciado con activo {self.asset}. Esperando señales...\n")
        print("╔═════╦══════════╦═════════════╦═══════════╦═══════════╦════╦═══════════╦═════════╗")
        print("║ CTD ║   HORA   ║   PARIDAD   ║ DIRECCION ║ RESULTADO ║ MG ║ INVERSION ║  LUCRO  ║")
        print("╠═════╬══════════╬═════════════╬═══════════╬═══════════╬════╬═══════════╬═════════╣")
        print("╚═════╩══════════╩═════════════╩═══════════╬═══════════╩════╩═══════════╬═════════╣")
        print(f"{' ':>43}║{'Ganancias de la sesion':^28}║ {0.0:>7} ║")
        print(f"{' ':>43}╚════════════════════════════╩═════════╝\n\n")

        #fecha_sesion = datetime.now().strftime("%Y-%m-%d")
        #print(api.get_all_ACTIVES_OPCODE())
        #asset_name = check_open(api)
        message = ""
        try:
            while True:
                self.esperar_proxima_vela(espera_segundos, message)
                df = self.obtener_candles(self.asset, int(time.time()) // 60 * 60, 60, 60)
                borrar_lineas(1)
                print(">> Analizando Velas, porfavor espera...⏳")

                senal = strategy(df)
                if senal:
                    precio_entrada = df.iloc[-1]["open"]
                    isValida, info = self.validar_senal(senal, precio_entrada)
                    if isValida:
                        msg = f">>🔔 Señal de {'COMPRA' if senal == 'call' else 'VENTA'} detectada, esperando resultado...⏳"
                        self.ejecutar_operacion(senal, msg, hora_op=datetime.fromtimestamp(int(time.time()) // 60 * 60).strftime('%H:%M:%S'))
                    else:
                        self.operaciones.append({
                            "hora": datetime.fromtimestamp(int(time.time()) // 60 * 60).strftime('%H:%M:%S'),
                            "paridad": self.asset,
                            "direccion": senal.upper(),
                            "inversion": 0,
                            "resultado": info,
                            "mg": None,
                            "lucro": 0
                        })

                        ganancia_total = utils.mostrar_tabla(self.operaciones)   
                else:
                    message = f"{datetime.fromtimestamp(int(time.time()) // 60 * 60).strftime('%H:%M:%S')} - No hay señal en esta vela, "
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido por el usuario.")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        #finally:
            #guardar_operaciones_excel(operaciones)
    
    def actualizar_activo(self, nuevo_activo):
        self.asset = nuevo_activo

    def actualizar_entrada(self):
        balance = self.api.get_balance()
        if self.config.get("usar_porcentaje") == "S":
            porcentaje = float(self.config.get("porcentaje_entrada", 1))  # default 1%
            self.entrada_actual = max(round(balance * (porcentaje / 100), 0), 1)
        else:
            self.entrada = int(self.config.get("valor_entrada", 1))

    def seleccionar_activo_abierto(self):
        print("🕵️‍♂️ Iniciando búsqueda de activos abiertos en la plataforma...")
        activos = self.api.get_all_open_time()
        filtered_assets = []

        if "binary" not in activos:
                utils.borrar_lineas(1)
                print("❌ No hay sección 'binary' en la respuesta.")
                return []
            
        for asset, info in activos["binary"].items():
                if any(symbol in asset for symbol in ["EUR", "JPY"]) and info.get("open"):
                    clean_asset = asset.replace("-op", "")
                    filtered_assets.append((asset, clean_asset))

        if not filtered_assets:
                utils.borrar_lineas(1)
                print("⚠️ No hay activos binarios abiertos.")
                return []

        # Mostrar activos en 4 columnas
        utils.borrar_lineas(1)
        print("📈 Activos binarios abiertos disponibles:\n")
        col_width = 30  # Ajusta el ancho por columna si lo deseas

        for i, asset in enumerate(filtered_assets, start=1):
            text = f"[{i:^2}] {asset[1]}"
            if i % 4 == 0:
                text += "\n"
            else:
                text.ljust(col_width)  # Salto de línea cada 4 columnas
        if len(filtered_assets) % 4 != 0:
            text += "\n"  # Salto final si no termina justo en múltiplo de 4
        print(text)  # Salto final si no termina justo en múltiplo de 4

        # Selección del usuario
        while True:
            try:
                choice = int(input("\nSeleccione un activo (número): "))
                if 1 <= choice <= len(filtered_assets):
                    selected = filtered_assets[choice - 1]
                    utils.borrar_lineas((len(filtered_assets) // 4 + 4))  # borra líneas según filas + extras
                    return selected[1]
                else:
                    print("Número fuera de rango. Intenta de nuevo.")
            except ValueError:
                print("Entrada inválida. Ingresa un número.")

    def esperar_proxima_vela(self, espera, message):
        segundos = int(time.time()) % 60
        tiempo_espera = (60 - segundos + espera - 1) if segundos > espera else (espera - 1 - segundos)
        while tiempo_espera > 0:
            tiempo_espera -= 1
            utils.borrar_lineas(1)
            print(f">>{message}⏳ esperando próxima vela en {tiempo_espera} segundos...")
            time.sleep(1)

    def obtener_candles(self, asset, end_time, offset, period):
        candles = self.api.get_candles(asset, offset, period, end_time)
        df = pd.DataFrame(candles)
        df['Date'] = pd.to_datetime(df['from'], unit='s', utc=True).dt.tz_convert("America/Santiago")
        df = df[['date', 'open', 'max', 'min', 'close']]
        df.columns = ['date', 'open', 'high', 'low', 'close']
        df = df.sort_values('date').reset_index(drop=True)
        return df            

    def validar_senal(self, signal, precio_entrada, duracion=30):
        df = self.obtener_candles(self.asset, int(time.time()), offset=60, period=60)
        if len(df) < 15:
            return False, "⚠️ No hay suficientes velas para calcular SMA"
        
        if self.use_media_movil:
            if not validar_entrada(df, signal, self.periodo_medias):
                return False, "❌ Condición de SMA no cumplida"

        if not precio_entrada:
            return True, None
        tiempo_limite = time.time() + duracion
            
        while time.time() < tiempo_limite:
            vela = self.api.get_candles(self.asset, 60, 1, int(time.time()))
            if not vela:
                utils.borrar_lineas(1)
                print("❌ Error al obtener precio actual.")
                time.sleep(1)
                continue
            precio_actual = vela[0]["close"]
            if (signal == "call" and precio_actual <= precio_entrada) or (signal == "put" and precio_actual >= precio_entrada):
                return True, None
            utils.borrar_lineas(1)    
            print(f"Esperando mejor precio ({signal.upper()}): actual={precio_actual:.5f}, apertura={precio_entrada:.5f}...")
            time.sleep(0.5)
        borrar_lineas(1)
        return False, f"⚠️ No alcanzó precio favorable en {duracion}s"

    def ejecutar_operacion(self, signal, message_check, hora_op=None):
        nivel = 0
        entrada = self.entrada_actual
        hora = hora_op if hora_op else datetime.now().strftime('%H:%M:%S')
        total_profit = 0
        resultado_final = "❌ LOSS"

        while True:
            borrar_lineas(1)
            print(message_check)
            status, id_operacion = self.api.buy(entrada, self.asset, signal, self.expiration_time)
            if not status:
                borrar_lineas(1)
                print("❌ No se pudo ejecutar la operación.")
                return

            profit = self.api.check_win_v3(id_operacion)

            if profit == "error":
                borrar_lineas(1)
                print("❌ Tiempo de espera agotado.")
                return None
                
            total_profit += profit

            if profit > 0:
                resultado_final = "✅ WIN"
                break
            elif profit == 0:
                if self.nivel_actual == 0:
                    resultado_final = "🤝 DRAW"
                    break
                else:
                    pass
            elif not self.use_mg or nivel >= self.nivel_mg:
                resultado_final = "❌ LOSS"
                break
            else:
                nivel += 1
                entrada = round(entrada * self.factor_mg, 0)
                message_check = f">>🔁 Nivel MG {nivel} activado, nueva entrada: {entrada}, esperando resultado..."
                time.sleep(0.5)

        self.operaciones.append({
            "hora": hora,
            "paridad": self.asset,
            "direccion": signal.upper(),
            "inversion": self.entrada_actual,
            "resultado": resultado_final,
            "mg": nivel,
            "lucro": total_profit
        })

        ganancia_total = mostrar_tabla(self.operaciones)

        if self.use_stop_win and ganancia_total >= self.stop_win:
            print("🎯 Stop Win alcanzado. Deteniendo operaciones.")
            return

        if self.use_stop_loss and ganancia_total <= -self.stop_loss:
            print("🛑 Stop Loss alcanzado. Deteniendo operaciones.")
            return

        self.nivel_actual = 0
        self.actualizar_entrada()
        time.sleep(1)





