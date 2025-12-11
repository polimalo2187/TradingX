from app.coinw_api import get_candles
from app.config import (
    BREAKOUT_MIN_VOLUME,
    BREAKOUT_CANDLE_BODY,
    BREAKOUT_STRENGTH_THRESHOLD,
    TP_MIN,
    TP_MAX,
    SL_MIN,
    SL_MAX
)


# =======================================
# ANALIZAR VELA PARA DETECTAR BREAKOUT
# =======================================

def analyze_candle(candle):
    """
    candle = [timestamp, open, high, low, close, volume]
    Devuelve métricas limpias para análisis técnico.
    """

    try:
        open_price = float(candle[1])
        high_price = float(candle[2])
        low_price = float(candle[3])
        close_price = float(candle[4])
        volume = float(candle[5])
    except:
        return None

    # Evitar velas inválidas
    if high_price < low_price or open_price <= 0 or close_price <= 0:
        return None

    # Cuerpo real de la vela
    body = abs(close_price - open_price)

    # Longitud total de la vela
    total_range = high_price - low_price
    if total_range == 0:
        return None

    # Tamaño relativo del cuerpo
    body_strength = body / total_range

    # Dirección de la vela
    direction = "bullish" if close_price > open_price else "bearish"

    return {
        "open": open_price,
        "close": close_price,
        "high": high_price,
        "low": low_price,
        "volume": volume,
        "body_strength": body_strength,
        "direction": direction
    }


# =======================================
# DETECTAR BREAKOUT PROFESIONAL
# =======================================

def detect_breakout(symbol, timeframe="1min"):
    """
    Analiza velas recientes y identifica breakouts reales.
    """

    candles = get_candles(symbol, timeframe, limit=5)

    if not candles or len(candles) < 2:
        return {"signal": False}

    # Última vela cerrada
    last = analyze_candle(candles[-1])

    if not last:
        return {"signal": False}

    # ===========================
    # FILTRO 1 - VOLUMEN
    # ===========================
    if last["volume"] < BREAKOUT_MIN_VOLUME:
        return {"signal": False}

    # ===========================
    # FILTRO 2 - CUERPO DE VELA
    # ===========================
    if last["body_strength"] < BREAKOUT_CANDLE_BODY:
        return {"signal": False}

    # ===========================
    # FILTRO 3 - SOLO SPOT BULLISH
    # ===========================
    if last["direction"] != "bullish":
        return {"signal": False}

    # ===========================
    # CALCULAR FUERZA REAL
    # ===========================

    strength = (
        last["body_strength"] * 0.6 +
        min(last["volume"] / BREAKOUT_MIN_VOLUME, 2) * 0.4
    )

    if strength < BREAKOUT_STRENGTH_THRESHOLD:
        return {"signal": False}

    # ===========================
    # BREAKOUT ACEPTADO
    # ===========================

    return {
        "signal": True,
        "strength": round(strength, 4),
        "close_price": last["close"],
        "tp_min": TP_MIN,
        "tp_max": TP_MAX,
        "sl_min": SL_MIN,
        "sl_max": SL_MAX
    }


# =======================================
# GENERAR PLAN DE TRADING
# =======================================

def generate_trade_plan(symbol, breakout):
    """
    Devuelve datos listos para que el motor de trading opere.
    """

    entry = breakout["close_price"]

    tp_min = entry * (1 + breakout["tp_min"])
    tp_max = entry * (1 + breakout["tp_max"])
    sl_min = entry * (1 - breakout["sl_min"])
    sl_max = entry * (1 - breakout["sl_max"])

    return {
        "symbol": symbol,
        "entry_price": entry,
        "tp_min": round(tp_min, 6),
        "tp_max": round(tp_max, 6),
        "sl_min": round(sl_min, 6),
        "sl_max": round(sl_max, 6),
        "strength": breakout["strength"]
    }


# =======================================
# FUNCIÓN FINAL QUE USA EL MOTOR
# =======================================

def get_trade_signal(symbol):
    """
    Devuelve:
    - signal: True / False
    - trade_plan: datos completos TP / SL
    """

    breakout = detect_breakout(symbol)

    if not breakout["signal"]:
        return {"signal": False}

    plan = generate_trade_plan(symbol, breakout)

    return {
        "signal": True,
        "trade_plan": plan
      }
