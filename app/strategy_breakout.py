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
