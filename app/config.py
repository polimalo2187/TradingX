import os

# ===============================
# CONFIGURACIÓN DEL BOT TRADINGX
# ===============================

# Token del bot de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# API Key de CoinW del bot (NO de los usuarios)
COINW_API_KEY = os.getenv("COINW_API_KEY")
COINW_SECRET_KEY = os.getenv("COINW_SECRET_KEY")

# Base URL de CoinW Spot
COINW_BASE_URL = os.getenv("API_BASE_URL", "https://api.coinw.com")

# URL de MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "TradingX"
USERS_COLLECTION = "users"

# ===============================
# CONFIGURACIÓN DE ESTRATEGIA
# ===============================

# Timeframes usados para analizar velas
TIMEFRAMES = ["1min", "3min", "5min"]

# Parámetros de Breakout para SPOT Trading
BREAKOUT_MIN_VOLUME = 15000
BREAKOUT_CANDLE_BODY = 0.60
BREAKOUT_STRENGTH_THRESHOLD = 0.75

# Take Profit dinámico
TP_MIN = 0.03   # 3%
TP_MAX = 0.08   # 8%

# Stop Loss dinámico basado en retroceso
SL_MIN = 0.008   # 0.8%
SL_MAX = 0.018   # 1.8%

# ===============================
# ESCANEO Y MOTOR
# ===============================

# Frecuencia de escaneo en segundos
SCAN_INTERVAL = 8

# Máximo de pares operando simultáneamente
MAX_ACTIVE_PAIRS = int(os.getenv("MAX_ACTIVE_PAIRS", 5))

# ===============================
# CONFIGURACIÓN GENERAL DEL SISTEMA
# ===============================

DEBUG_MODE = True  # Cambiar a False en producción

print("⚙️ Configuración cargada correctamente desde config.py")
