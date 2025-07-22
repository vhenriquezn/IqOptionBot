from .bot import BotModular

def main():
    run_bot()

async def run_bot():
    bot = BotModular()
    bot.conectar()
    bot.set_account()
    bot.trading_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")