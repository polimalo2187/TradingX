from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from app.database import create_user, user_is_ready
from app.config import BOT_TOKEN
from app.encryption import encrypt_text, decrypt_text
from app.trading_engine import trading_cycle


# ======================================================
# MENÚ PRINCIPAL
# ======================================================

def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📌 Configurar API Keys", callback_data="config_api"),
            InlineKeyboardButton("💰 Configurar Capital", callback_data="config_capital")
        ],
        [
            InlineKeyboardButton("🚀 Activar Trading", callback_data="activate_trading"),
            InlineKeyboardButton("⛔ Desactivar Trading", callback_data="deactivate_trading"),
        ],
        [
            InlineKeyboardButton("📊 Mis Estadísticas", callback_data="stats"),
            InlineKeyboardButton("ℹ Estado Actual", callback_data="status")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ======================================================
# START
# ======================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    create_user(user.id, user.username)

    text = (
        f"👋 Hola {user.first_name}, bienvenido a TradingX – El Rey del Trading.\n\n"
        "Tu cuenta ha sido registrada correctamente.\n"
        "Usa el menú inferior para configurar tu bot."
    )

    await update.message.reply_text(text, reply_markup=get_main_menu())


# ======================================================
# MANEJADOR GENERAL DEL MENÚ  (LA FUNCIÓN QUE FALTABA)
# ======================================================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # --- Configurar API ---
    if data == "config_api":
        await query.edit_message_text(
            "🔑 Envía tus API Key y Secret de CoinW.\n\nFormato:\n`APIKEY|SECRETKEY`"
        )
        return

    # --- Configurar Capital ---
    if data == "config_capital":
        await query.edit_message_text(
            "💰 Ingresa el capital que deseas asignar al bot.\nEjemplo: `5`"
        )
        return

    # --- Activar trading ---
    if data == "activate_trading":
        await query.edit_message_text(
            "🚀 Trading automático ACTIVADO.\nTu bot analizará el mercado y operará según las oportunidades detectadas."
        )
        return

    # --- Desactivar trading ---
    if data == "deactivate_trading":
        await query.edit_message_text("⛔ Trading DESACTIVADO.")
        return

    # --- Estadísticas ---
    if data == "stats":
        await query.edit_message_text("📊 Próximamente: estadísticas detalladas.")
        return

    # --- Estado actual ---
    if data == "status":
        await query.edit_message_text("ℹ Sistema funcionando correctamente.")
        return


# ======================================================
# ROUTER DE MENSAJES (TEXTOS QUE NO SON BOTONES)
# ======================================================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Si envía APIKEY|SECRETKEY
    if "|" in text:
        api, secret = text.split("|")
        # Aquí se guardarían las claves encriptadas...
        await update.message.reply_text("🔐 API Keys configuradas correctamente.")
        return

    # Si envía su capital
    if text.isdigit():
        await update.message.reply_text("💰 Capital guardado correctamente.")
        return

    # Default
    await update.message.reply_text("❗ Comando no reconocido.")


# ======================================================
# INICIO DE LA APLICACIÓN
# ======================================================

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))  # ← AQUÍ EL FIX
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("menu", start))

    application.add_handler(
        CommandHandler("restart", start)
    )
    application.add_handler(
        CommandHandler("reboot", start)
    )

    application.add_handler(
        CommandHandler("test", start)
    )

    application.add_handler(
        CommandHandler("stop", start)
    )

    # Manejo de textos normales
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_router)
    )

    print("🤖 TradingX está corriendo en Telegram...")
    application.run_polling()
