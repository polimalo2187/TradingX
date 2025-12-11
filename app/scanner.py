from app.coinw_api import get_spot_pairs, get_candles
from app.strategy_breakout import get_trade_signal
from app.config import MAX_ACTIVE_PAIRS


# =======================================
# OBTENER LISTA DE PARES VALIDOS
# =======================================

def fetch_pairs():
    """
    Obtiene una lista filtrada de pares Spot de CoinW.
    Solo pares que terminen en USDT (mercado principal).
    """
    all_pairs = get_spot_pairs()

    if not all_pairs:
        print("❌ No se pudo obtener la lista de pares.")
        return []

    usdt_pairs = [pair for pair in all_pairs if pair.endswith("USDT")]

    print(f"🔍 Pares USDT detectados: {len(usdt_pairs)}")
    return usdt_pairs
