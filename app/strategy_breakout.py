from app.coinex_api import get_candles
from app.config import (
    BREAKOUT_MIN_VOLUME,
    BREAKOUT_CANDLE_BODY,
    BREAKOUT_STRENGTH_THRESHOLD,
    TP_MIN,
    TP_MAX,
    SL_MIN,
    SL_MAX
)


# ======================================================
# ANALIZAR UNA VELA INDIVIDUAL
# ======================================================

def analyze_candle(candle):
    """
    Formato esperado CoinEx V2:
    [timestamp, open, close, high, low, volume]
    """

    if not isinstance(candle, list) or len(candle) < 6:
        return None

    try:
        open_price = float(candle[1])
        close_price = float(candle[2])
        high_price = float(candle[3])
        low_price = float(candle[4])
        volume = float(candle[5])
    except:
        return None

    if open_price <= 0 or close_price <= 0 or high_price < low_price:
        return None

    body = abs(close_price - open_price)
    total_range = high_price - low_price
    if total_range <= 0:
        return None

    body_strength = body / total_range
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


# ======================================================
# DETECTAR BREAKOUT REAL
# ======================================================

def detect_breakout(symbol, timeframe="1min"):

    candles = get_candles(symbol, timeframe, limit=5)

    if not candles or len(candles) < 2:
        return {"signal": False}

    # Ordenar velas por timestamp por seguridad
    try:
        candles = sorted(candles, key=lambda x: x[0])
    except:
        pass

    last = analyze_candle(candles[-1])

    if not last:
        return {"signal": False}

    # FILTROS
    if last["volume"] < BREAKOUT_MIN_VOLUME:
        return {"signal": False}

    if last["body_strength"] < BREAKOUT_CANDLE_BODY:
        return {"signal": False}

    if last["direction"] != "bullish":
        return {"signal": False}

    # FUERZA
    strength = (
        last["body_strength"] * 0.6 +
        min(last["volume"] / BREAKOUT_MIN_VOLUME, 2) * 0.4
    )

    if strength < BREAKOUT_STRENGTH_THRESHOLD:
        return {"signal": False}

    # Señal válida
    return {
        "signal": True,
        "strength": round(strength, 4),
        "close_price": last["close"],
        "tp_min": TP_MIN,
        "tp_max": TP_MAX,
        "sl_min": SL_MIN,
        "sl_max": SL_MAX
    }


# ======================================================
# GENERAR PLAN COMPLETO
# ======================================================

def generate_trade_plan(symbol, breakout):

    entry = breakout["close_price"]

    return {
        "symbol": symbol,
        "entry_price": entry,
        "tp_min": round(entry * (1 + breakout["tp_min"]), 6),
        "tp_max": round(entry * (1 + breakout["tp_max"]), 6),
        "sl_min": round(entry * (1 - breakout["sl_min"]), 6),
        "sl_max": round(entry * (1 - breakout["sl_max"]), 6),
        "strength": breakout["strength"]
    }


# ======================================================
# FUNCIÓN PRINCIPAL PARA EL SCANNER
# ======================================================

def get_trade_signal(symbol):
    breakout = detect_breakout(symbol)

    if not breakout["signal"]:
        return {"signal": False}

    return {
        "signal": True,
        "trade_plan": generate_trade_plan(symbol, breakout)
  }
