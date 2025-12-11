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


# =======================================
# CONFIGURAR API KEYS
# =======================================

# Mensaje inicial del botón
async def config_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *Configuración de API Keys*\n\n"
        "Envíame tu *API KEY* de CoinW.",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_api_key"] = True


# Recepción de API KEY
async def receive_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_key = update.message.text

    context.user_data["api_key"] = api_key
    context.user_data["awaiting_api_key"] = False
    context.user_data["awaiting_api_secret"] = True

    await update.message.reply_text(
        "Perfecto 👍\nAhora envíame tu *API SECRET*.",
        parse_mode="Markdown"
    )


# Recepción de API SECRET
async def receive_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_secret = update.message.text

    api_key = context.user_data.get("api_key")

    save_api_keys(user_id, api_key, api_secret)

    context.user_data["awaiting_api_secret"] = False

    await update.message.reply_text(
        "🔐 Tus API Keys han sido guardadas *de forma segura y encriptada*.\n\n"
        "Ya estás un paso más cerca de activar TradingX 🚀",
        parse_mode="Markdown",
        reply_markup=main_menu
    )
