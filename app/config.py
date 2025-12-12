import os

# ===============================
# CONFIGURACIÓN DEL BOT TRADINGX
# ===============================

# Token del bot de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ===============================
# CONFIGURACIÓN DE COINEX (V2 OFICIAL)
# ===============================
# Las API Keys se obtienen desde MongoDB por usuario.
COINEX_BASE_URL = "https://api.coinex.com/v2"

# ===============================
# CONFIGURACIÓN DE MONGO DB
# ===============================

MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
MONGO_URI = MONGODB_URI  # requerido por database.py

DB_NAME = "TradingX"
USERS_COLLECTION = "users"


# ===============================
# CONFIGURACIÓN DE ESTRATEGIA
# ===============================

TIMEFRAMES = ["1min", "3min", "5min"]

BREAKOUT_MIN_VOLUME = 15000
BREAKOUT_CANDLE_BODY = 0.60
BREAKOUT_STRENGTH_THRESHOLD = 0.75

TP_MIN = 0.03   # 3%
TP_MAX = 0.08   # 8%

SL_MIN = 0.008  # 0.8%
SL_MAX = 0.018  # 1.8%


# ===============================
# ESCANEO Y MOTOR
# ===============================

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 8))
MAX_ACTIVE_PAIRS = int(os.getenv("MAX_ACTIVE_PAIRS", 5))


# ===============================
# CONFIGURACIÓN GENERAL
# ===============================

DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

print("⚙️ Configuración CoinEx V2 cargada correctamente desde config.py")
