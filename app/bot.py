from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import TELEGRAM_BOT_TOKEN
from app.database import create_user, get_user, user_is_ready, get_user_stats
from app.database import save_api_keys, save_user_capital, activate_trading, deactivate_trading
from app.trading_engine import trading_cycle


# =======================================
# TECLADO PRINCIPAL
# =======================================

main_menu = ReplyKeyboardMarkup(
    [
        ["📌 Configurar API Keys", "💰 Configurar Capital"],
        ["🚀 Activar Trading", "🛑 Desactivar Trading"],
        ["📊 Mis Estadísticas", "ℹ Estado Actual"]
    ],
    resize_keyboard=True
)


# =======================================
# COMANDO /start
# =======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    create_user(user.id, user.username)

    await update.message.reply_text(
        f"👋 Hola {user.first_name}, bienvenido a *TradingX – El Rey del Trading*.\n\n"
        "Tu cuenta ha sido registrada correctamente.\n"
        "Usa el menú inferior para configurar tu bot.",
        parse_mode="Markdown",
        reply_markup=main_menu
    )
