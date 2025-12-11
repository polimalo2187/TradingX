import os

# ===============================
# CONFIGURACIÓN DEL BOT TRADINGX
# ===============================

# Token del bot de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# API Key de CoinW del bot (NO se utilizan para trading,
# pero pueden usarse en funciones de consulta si las necesitas).
COINW_API_KEY = os.getenv("COINW_API_KEY")
COINW_SECRET_KEY = os.getenv("COINW_SECRET_KEY")

# Base URL fija de CoinW Spot
COINW_BASE_URL = "https://api.coinw.com"


# ===============================
# CONFIGURACIÓN DE MONGO DB
# ===============================

# Detecta tanto MONGODB_URI como MONGO_URI
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")

# ⚠️ ESTA VARIABLE ES LA QUE REQUIERE database.py
MONGO_URI = MONGODB_URI

DB_NAME = "TradingX"
USERS_COLLECTION = "users"


# ===============================
# CONFIGURACIÓN DE ESTRATEGIA
# ===============================

# Timeframes usados para analizar velas
TIMEFRAMES = ["1min", "3min", "5min"]

# Breakout para SPOT Trading
BREAKOUT_MIN_VOLUME = 15000
BREAKOUT_CANDLE_BODY = 0.60
BREAKOUT_STRENGTH_THRESHOLD = 0.75

# Take Profit dinámico
TP_MIN = 0.03   # 3%
TP_MAX = 0.08   # 8%

# Stop Loss dinámico
SL_MIN = 0.008  # 0.8%
SL_MAX = 0.018  # 1.8%


# ===============================
# ESCANEO Y MOTOR
# ===============================

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 8))  # segundos
MAX_ACTIVE_PAIRS = int(os.getenv("MAX_ACTIVE_PAIRS", 5))


# ===============================
# CONFIGURACIÓN GENERAL
# ===============================

DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

print("⚙️ Configuración cargada correctamente desde config.py")
