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

# <<< YA MIGRADO A COINEX >>>
from app.coinex_api import get_balance

from app.config import TELEGRAM_BOT_TOKEN
from app.trading_engine import trading_cycle
from app.encryption import decrypt_text


# ======================================================
# BOTÓN DE REGRESAR
# ======================================================

def get_back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Volver al Menú", callback_data="go_back")]
    ])


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
# /START
# ======================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = create_user(user.id, user.username)

    text = (
        f"👋 Hola {user.first_name}, bienvenido a TradingX.\n\n"
        "Configura tus API Keys y tu capital para comenzar."
        if not db_user.get("api_key") else
        f"👋 Hola {user.first_name}, ya tienes tu cuenta configurada.\n"
        f"Capital asignado: {db_user.get('capital', 0)} USDT\n"
        "Selecciona una opción del menú:"
    )

    await update.message.reply_text(text, reply_markup=get_main_menu())



# ======================================================
# /VERAPIKEY — DEBUG PROFESIONAL
# ======================================================

async def verapikey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if not user or not user.get("api_key"):
        await update.message.reply_text("❌ No tienes API Keys configuradas.")
        return

    api_key = decrypt_text(user["api_key"])
    api_secret = decrypt_text(user["api_secret"])

    await update.message.reply_text(
        f"🔍 *API Keys almacenadas:*\n\n"
        f"👉 API Key: `{api_key}`\n"
        f"👉 Secret Key: `{api_secret}`",
        parse_mode="Markdown"
    )



# ======================================================
# MENÚ CALLBACKS
# ======================================================

async def go_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📋 Menú principal", reply_markup=get_main_menu())


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    await query.answer()
    user = get_user(user_id)

    if data == "go_back":
        return await go_back_handler(update, context)

    # CONFIGURAR API
    if data == "config_api":
        txt = (
            "🔑 Envía tus API Key y Secret en formato:\n`APIKEY|SECRETKEY`"
            if not user.get("api_key") else
            "🔐 Ya tienes API Keys configuradas.\n"
            "Si deseas sustituirlas, envía nuevamente:\n`APIKEY|SECRETKEY`"
        )
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=get_back_button())
        return

    # CONFIGURAR CAPITAL
    if data == "config_capital":
        await query.edit_message_text(
            "💰 Ingresa el capital que deseas asignar al bot.\nEjemplo: `5`",
            reply_markup=get_back_button()
        )
        return

    # ACTIVAR TRADING
    if data == "activate_trading":

        if not user_is_ready(user_id):
            await query.edit_message_text(
                "❌ El usuario NO está listo para operar.\n"
                "Verifique:\n"
                "• API Keys configuradas\n"
                "• Capital >= 5 USDT\n"
                "• Saldo real suficiente\n",
                reply_markup=get_back_button()
            )
            return

        balance = get_balance(user_id)

        if balance is None:
            await query.edit_message_text(
                "❌ Error leyendo el balance.\nCoinEx no respondió correctamente.",
                reply_markup=get_back_button()
            )
            return

        if balance < user.get("capital", 0):
            await query.edit_message_text(
                f"❌ Saldo insuficiente.\n"
                f"Capital: {user.get('capital')} USDT\n"
                f"Balance real: {balance} USDT",
                reply_markup=get_back_button()
            )
            return

        await query.edit_message_text(
            "🚀 *Trading automático ACTIVADO.*\n"
            "El bot comenzará a operar cuando detecte oportunidades.",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )

        trading_cycle(user_id)
        return

    # DESACTIVAR
    if data == "deactivate_trading":
        await query.edit_message_text(
            "⛔ Trading DESACTIVADO.",
            reply_markup=get_back_button()
        )
        return

    # ESTADÍSTICAS TEMPORAL
    if data == "stats":
        await query.edit_message_text(
            "📊 Estadísticas próximamente.",
            reply_markup=get_back_button()
        )
        return

    # ESTADO
    if data == "status":
        await query.edit_message_text(
            f"ℹ Estado actual:\n\n"
            f"🔐 API Keys: {'✔️' if user.get('api_key') else '❌'}\n"
            f"💰 Capital: {user.get('capital', 0)} USDT\n",
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
        return



# ======================================================
# MENSAJES (APIKEY|SECRET y capital)
# ======================================================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # API Keys
    if "|" in text:
        try:
            api, secret = text.split("|")
            save_api_keys(user_id, api, secret)

            await update.message.reply_text(
                "🔐 API Keys guardadas correctamente.\nAhora configura tu capital.",
                reply_markup=get_main_menu()
            )
        except:
            await update.message.reply_text("❌ Formato incorrecto. Usa: `APIKEY|SECRETKEY`")
        return

    # Capital
    if text.isdigit():
        capital = float(text)
        save_user_capital(user_id, capital)

        await update.message.reply_text(
            f"💰 Capital configurado: {capital} USDT",
            reply_markup=get_main_menu()
        )
        return

    await update.message.reply_text("❗ Comando no reconocido.")



# ======================================================
# ARRANQUE DEL BOT
# ======================================================

def run_bot():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verapikey", verapikey))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_router)
    )

    print("🤖 TradingX está corriendo en Telegram...")
    application.run_polling()
