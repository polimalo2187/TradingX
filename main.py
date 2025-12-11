import threading
from app.bot import run_bot
from app.scheduler import start_scheduler

if __name__ == "__main__":
    print("🚀 Iniciando TradingX...")

    # Iniciar scheduler en un hilo independiente
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    # Iniciar Bot de Telegram (bloqueante)
    run_bot()
