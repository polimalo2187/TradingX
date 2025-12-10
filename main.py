import asyncio
from app.telegram_bot import start_telegram_bot
from app.scheduler import start_scheduler

async def main():
    # Iniciar bot de Telegram
    print("🔵 Iniciando TradingX Telegram Bot...")
    telegram_task = asyncio.create_task(start_telegram_bot())

    # Iniciar Scheduler (scanner + motor automático)
    print("🟣 Iniciando Scheduler de TradingX...")
    scheduler_task = asyncio.create_task(start_scheduler())

    # Mantener ambos procesos vivos
    await asyncio.gather(telegram_task, scheduler_task)


if __name__ == "__main__":
    try:
        print("🚀 TradingX – El Rey del Trading está iniciando…")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ TradingX detenido manualmente.")
