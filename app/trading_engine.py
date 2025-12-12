import time
from app.coinex_api import (
    place_market_buy,
    place_market_sell,
    get_price
)

from app.scanner import scan_market
from app.database import (
    get_user_capital,
    register_trade
)


# ======================================================
# CALCULAR CANTIDAD DE COMPRA (COINEX)
# ======================================================

def calculate_quantity(usdt_amount, price):
    """
    CoinEx requiere especificar 'amount' = cantidad del activo base.
    """
    if price <= 0:
        return 0

    qty = usdt_amount / price
    return round(qty, 6)  # CoinEx permite 6 decimales


# ======================================================
# ABRIR OPERACIÓN (COINEX MARKET BUY)
# ======================================================

def open_trade(user_id, symbol, trade_plan):
    """
    Ejecuta una COMPRA MARKET real usando CoinEx.
    CoinEx requiere: market, amount, symbol, side.
    """

    capital = get_user_capital(user_id)

    if capital < 5:
        print("❌ Capital insuficiente (mínimo 5 USDT).")
        return None

    entry_price = trade_plan["entry_price"]
    qty = calculate_quantity(capital, entry_price)

    if qty <= 0:
        print("❌ Qty inválida (0).")
        return None

    print(f"🟢 Ejecutando COMPRA MARKET en {symbol} | Qty={qty}")

    order = place_market_buy(user_id, symbol, qty)

    if not order:
        print("❌ Error ejecutando compra en CoinEx.")
        return None

    return {
        "user_id": user_id,
        "symbol": symbol,
        "entry_price": entry_price,
        "qty": qty,
        "tp_min": trade_plan["tp_min"],
        "tp_max": trade_plan["tp_max"],
        "sl_min": trade_plan["sl_min"],
        "sl_max": trade_plan["sl_max"]
    }


# ======================================================
# MONITOREO PARA TP / SL
# ======================================================

def monitor_trade(position):
    """
    CoinEx no tiene OCO ni SL automático, por eso
    el bot monitorea cada 2 segundos.
    """

    user_id = position["user_id"]
    symbol = position["symbol"]
    entry = position["entry_price"]
    qty = position["qty"]

    tp_min = position["tp_min"]
    sl_max = position["sl_max"]

    print(f"📡 Monitoreando operación en {symbol}...")

    while True:
        current_price = get_price(symbol)

        if not current_price:
            print("⚠ No se pudo obtener precio.")
            time.sleep(2)
            continue

        # TAKE PROFIT
        if current_price >= tp_min:
            print(f"🎯 TP alcanzado: {current_price}")

            sell = place_market_sell(user_id, symbol, qty)
            if sell:
                register_trade(user_id, symbol, entry, current_price, qty, "tp_hit")
                print("🟢 GANANCIA registrada")
            return "tp_hit"

        # STOP LOSS
        if current_price <= sl_max:
            print(f"🛑 SL alcanzado: {current_price}")

            sell = place_market_sell(user_id, symbol, qty)
            if sell:
                register_trade(user_id, symbol, entry, current_price, qty, "sl_hit")
                print("🔴 PÉRDIDA controlada registrada")
            return "sl_hit"

        time.sleep(2)


# ======================================================
# CICLO COMPLETO TRADINGX (COINEX)
# ======================================================

def trading_cycle(user_id):
    """
    Escaneo → Selección → Compra → Monitoreo
    """

    print(f"\n🚀 INICIANDO CICLO PARA USUARIO {user_id}")

    opportunities = scan_market()

    if not opportunities:
        print("⚪ No se detectaron oportunidades.")
        return "no_opportunity"

    best = opportunities[0]
    symbol = best["symbol"]
    plan = best["trade_plan"]

    print(f"🔥 Mejor oportunidad: {symbol} | Fuerza: {plan['strength']}")

    position = open_trade(user_id, symbol, plan)

    if not position:
        print("❌ No se pudo abrir la operación.")
        return "failed_open"

    result = monitor_trade(position)

    print(f"📊 Resultado final: {result}")
    return result
