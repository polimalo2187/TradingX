from app.coinw_api import (
    place_market_buy,
    place_market_sell,
    get_price
)
from app.strategy_breakout import get_trade_signal
from app.scanner import scan_market
from app.config import USER_TRADING_CAPITAL


# =======================================
# CALCULAR CANTIDAD DE COMPRA
# =======================================

def calculate_quantity(usdt_amount, price):
    """
    Calcula la cantidad de tokens a comprar según el capital y precio.
    """
    qty = usdt_amount / price
    return round(qty, 6)


# =======================================
# INICIAR OPERACIÓN EN UN PAR
# =======================================

def open_trade(symbol, trade_plan, capital):
    """
    Ejecuta la compra Market y devuelve datos de la operación.
    """

    entry_price = trade_plan["entry_price"]

    qty = calculate_quantity(capital, entry_price)

    print(f"🟢 Ejecutando compra en {symbol} | Cantidad: {qty}")

    order_data = place_market_buy(symbol, qty)

    if not order_data:
        print(f"❌ No se pudo abrir operación en {symbol}")
        return None

    return {
        "symbol": symbol,
        "entry_price": entry_price,
        "qty": qty,
        "tp_min": trade_plan["tp_min"],
        "tp_max": trade_plan["tp_max"],
        "sl_min": trade_plan["sl_min"],
        "sl_max": trade_plan["sl_max"]
    }
