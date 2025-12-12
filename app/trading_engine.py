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
# CALCULAR CANTIDAD A COMPRAR
# ======================================================

def calculate_quantity(usdt_amount, price):
    """
    Calcula la cantidad de tokens según el capital disponible.
    CoinEx acepta cantidades con hasta 6 decimales.
    """
    if price <= 0:
        return 0
    qty = usdt_amount / price
    return round(qty, 6)


# ======================================================
# ABRIR OPERACIÓN REAL
# ======================================================

def open_trade(user_id, symbol, trade_plan):
    """
    Ejecuta la compra MARKET en CoinEx.
    """

    capital = get_user_capital(user_id)

    if capital < 5:
        print("❌ Capital insuficiente (mínimo 5 USDT requeridos).")
        return None

    entry_price = trade_plan["entry_price"]
    qty = calculate_quantity(capital, entry_price)

    if qty <= 0:
        print("❌ Cantidad calculada inválida (qty=0).")
        return None

    print(f"🟢 Ejecutando COMPRA {symbol} | Qty: {qty} | Precio entrada: {entry_price}")

    order_data = place_market_buy(user_id, symbol, qty)

    if not order_data:
        print(f"❌ Error al ejecutar compra en {symbol}")
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
# MONITOREO DE OPERACIÓN (TP / SL DINÁMICO)
# ======================================================

def monitor_trade(position):
    """
    Monitorea una operación activa hasta ejecutar el TP o SL.
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
            print("⚠️ Precio no disponible, reintentando...")
            time.sleep(2)
            continue

        # TAKE PROFIT
        if current_price >= tp_min:
            print(f"🎯 TP alcanzado en {symbol} | Precio actual: {current_price}")

            sell_data = place_market_sell(user_id, symbol, qty)
            if sell_data:
                register_trade(user_id, symbol, entry, current_price, qty, "tp_hit")
                print("🟢 Operación cerrada con GANANCIA")
            return "tp_hit"

        # STOP LOSS
        if current_price <= sl_max:
            print(f"🛑 SL alcanzado en {symbol} | Precio actual: {current_price}")

            sell_data = place_market_sell(user_id, symbol, qty)
            if sell_data:
                register_trade(user_id, symbol, entry, current_price, qty, "sl_hit")
                print("🔴 Operación cerrada con PÉRDIDA controlada")
            return "sl_hit"

        time.sleep(2)


# ======================================================
# CICLO COMPLETO DE TRADINGX
# ======================================================

def trading_cycle(user_id):
    """
    1. Escanea mercado CoinEx
    2. Detecta oportunidad
    3. Ejecuta compra
    4. Monitorea TP/SL
    """

    print(f"\n🚀 INICIANDO CICLO DE TRADINGX PARA EL USUARIO {user_id}")

    opportunities = scan_market()

    if not opportunities:
        print("⚪ No se detectaron oportunidades.")
        return "no_opportunity"

    best = opportunities[0]
    symbol = best["symbol"]
    trade_plan = best["trade_plan"]

    print(f"🔥 Oportunidad detectada: {symbol} | Fuerza: {trade_plan['strength']}")

    position = open_trade(user_id, symbol, trade_plan)

    if not position:
        print("❌ No se pudo abrir la operación.")
        return "failed_open"

    result = monitor_trade(position)

    print(f"📊 Resultado final: {result}")
    return result
