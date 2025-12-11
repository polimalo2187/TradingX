from app.bot import run_bot
from app.scheduler import start_scheduler


if __name__ == "__main__":
    print("🚀 Iniciando TradingX...")

    # Iniciar Scheduler de operaciones automáticas
    start_scheduler()

    # Iniciar Bot de Telegram
    run_bot()
