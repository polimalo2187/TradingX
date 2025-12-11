from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from app.database import (
    create_user, 
    get_user, 
    save_api_keys, 
    save_user_capital, 
    user_is_ready
)

from app.config import TELEGRAM_BOT_TOKEN
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
    db_user = create_user(user.id, user.username)

    # Verificar si ya tiene API keys configuradas
    if db_user.get("api_key") and db_user.get("api_secret"):
        text = (
            f"👋 Hola {user.first_name}, bienvenido nuevamente.\n\n"
            "🔐 Tus API Keys ya están configuradas.\n"
            "💰 Capital asignado: " + str(db_user.get("capital", 0)) + " USDT\n\n"
            "Selecciona una opción del menú:"
        )
    else:
        text = (
            f"👋 Hola {user.first_name}, bienvenido a TradingX – El Rey del Trading.\n\n"
            "Antes de activar el bot necesitas configurar:\n"
            "• API Keys de CoinW\n"
            "• Capital de operación\n\n"
            "Usa el menú inferior para continuar."
        )

    await update.message.reply_text(text, reply_markup=get_main_menu())


# ======================================================
# MANEJADOR DEL MENÚ
# ======================================================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    await query.answer()

    user = get_user(user_id)

    # --- Configurar API ---
    if data == "config_api":

        if user.get("api_key"):
            await query.edit_message_text(
                "🔐 Ya tienes API Keys configuradas.\n"
                "Si deseas cambiarlas, envía nuevamente:\n\n"
                "`APIKEY|SECRETKEY`",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "🔑 Envía tus API Key y Secret de CoinW.\n\nFormato:\n`APIKEY|SECRETKEY`",
                parse_mode="Markdown"
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
            "🚀 El trading automático se activará cuando completes la configuración.\n"
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
        api_state = "✔️" if user.get("api_key") else "❌"
        cap_state = user.get("capital", 0)

        await query.edit_message_text(
            f"ℹ Estado Actual\n\n"
            f"🔐 API Keys: {api_state}\n"
            f"💰 Capital: {cap_state} USDT\n",
            parse_mode="Markdown"
        )
        return


# ======================================================
# ROUTER DE MENSAJES
# ======================================================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # Si envía APIKEY|SECRETKEY
    if "|" in text:
        try:
            api, secret = text.split("|")
            save_api_keys(user_id, api, secret)

            await update.message.reply_text(
                "🔐 API Keys guardadas correctamente y encriptadas.\n"
                "Ahora puedes configurar tu capital.",
                reply_markup=get_main_menu()
            )
        except:
            await update.message.reply_text("❌ Formato incorrecto. Ejemplo:\n`APIKEY|SECRETKEY`")
        return

    # Si envía su capital
    if text.isdigit():
        capital = float(text)
        save_user_capital(user_id, capital)

        await update.message.reply_text(
            f"💰 Capital configurado: {capital} USDT\n",
            reply_markup=get_main_menu()
        )
        return

    await update.message.reply_text("❗ Comando no reconocido.")


# ======================================================
# INICIO DE LA APLICACIÓN
# ======================================================

def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_router)
    )

    print("🤖 TradingX está corriendo en Telegram...")
    application.run_polling()
