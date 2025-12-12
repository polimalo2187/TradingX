import threading
from app.bot import run_bot
from app.scheduler import start_scheduler

if __name__ == "__main__":
    print("🚀 Iniciando TradingX...")

    # ==========================================
    # 1️⃣ INICIAR SCHEDULER EN SEGUNDO PLANO
    # ==========================================
    try:
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
        print("✅ Scheduler iniciado correctamente.")
    except Exception as e:
        print(f"❌ Error iniciando scheduler: {e}")

    # ==========================================
    # 2️⃣ INICIAR BOT DE TELEGRAM (PROCESO PRINCIPAL)
    # ==========================================
    try:
        run_bot()
    except Exception as e:
        print(f"❌ Error ejecutando bot de Telegram: {e}")
