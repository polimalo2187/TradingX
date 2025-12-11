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
    Recibe una vela con formato:
    [timestamp, open, high, low, close, volume]
    
    Devuelve un diccionario con métricas de fuerza.
    """
    open_price = float(candle[1])
    high_price = float(candle[2])
    low_price = float(candle[3])
    close_price = float(candle[4])
    volume = float(candle[5])

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
# DETECTAR BREAKOUT (SEÑAL DE ENTRADA)
# =======================================

def detect_breakout(symbol, timeframe="1min"):
    """
    Analiza velas recientes y determina si existe un breakout válido.
    Devuelve un objeto con datos y recomendación.
    """

    candles = get_candles(symbol, timeframe, limit=5)

    if len(candles) < 2:
        return {"signal": False}

    # Tomar la última vela cerrada
    last_candle = analyze_candle(candles[-1])

    if not last_candle:
        return {"signal": False}

    # REGLA 1: volumen mínimo para considerar breakout
    if last_candle["volume"] < BREAKOUT_MIN_VOLUME:
        return {"signal": False}

    # REGLA 2: cuerpo fuerte (vela de impulso)
    if last_candle["body_strength"] < BREAKOUT_CANDLE_BODY:
        return {"signal": False}

    # REGLA 3: breakout debe ser alcista (para Spot)
    if last_candle["direction"] != "bullish":
        return {"signal": False}

    # Calcular "fuerza" total
    strength = (
        (last_candle["body_strength"] * 0.6) +
        (last_candle["volume"] / BREAKOUT_MIN_VOLUME * 0.4)
    )

    # REGLA 4: fuerza mínima total
    if strength < BREAKOUT_STRENGTH_THRESHOLD:
        return {"signal": False}

    # Breakout válido: retornamos parámetros
    return {
        "signal": True,
        "strength": strength,
        "close_price": last_candle["close"],
        "tp": TP_MIN,
        "tp_max": TP_MAX,
        "sl": SL_MIN,
        "sl_max": SL_MAX
    }


# =======================================
# CREAR PLAN DE OPERACIÓN (TP / SL)
# =======================================

def generate_trade_plan(symbol, breakout_data):
    """
    Genera un plan completo de operación basado en la señal.
    """
    
    entry_price = breakout_data["close_price"]

    # TP dinámico
    tp_min = entry_price * (1 + breakout_data["tp"])
    tp_max = entry_price * (1 + breakout_data["tp_max"])

    # SL dinámico
    sl_min = entry_price * (1 - breakout_data["sl"])
    sl_max = entry_price * (1 - breakout_data["sl_max"])

    return {
        "symbol": symbol,
        "entry_price": entry_price,
        "tp_min": round(tp_min, 6),
        "tp_max": round(tp_max, 6),
        "sl_min": round(sl_min, 6),
        "sl_max": round(sl_max, 6),
        "strength": breakout_data["strength"]
    }


# =======================================
# FUNCIÓN PRINCIPAL DE ESTRATEGIA
# (LO QUE EL MOTOR LLAMA DIRECTAMENTE)
# =======================================

def get_trade_signal(symbol):
    """
    Devuelve un objeto final con:
    - Si hay señal
    - Plan de operación (TP / SL)
    - Datos de fuerza
    """

    breakout = detect_breakout(symbol)

    if not breakout["signal"]:
        return {
            "signal": False
        }

    # Crear plan operativo completo
    plan = generate_trade_plan(symbol, breakout)

    return {
        "signal": True,
        "trade_plan": plan
    }
