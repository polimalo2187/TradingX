import time
from app.coinw_api import (
    place_market_buy,
    place_market_sell,
    get_price
)
from app.scanner import scan_market
from app.database import (
    get_user_capital,
    register_trade
)


# =======================================
# CANTIDAD SEGÚN CAPITAL Y PRECIO
# =======================================

def calculate_quantity(usdt_amount, price):
    """
    Calcula cantidad de tokens según capital disponible.
    """
    if price <= 0:
        return 0
    qty = usdt_amount / price
    return round(qty, 6)


# =======================================
# ABRIR OPERACIÓN
# =======================================

def open_trade(user_id, symbol, trade_plan):
    """
    Ejecuta una compra Market real usando CoinW.
    """

    capital = get_user_capital(user_id)

    # Validación crítica de seguridad
    if capital < 5:
        print("❌ Capital insuficiente (mínimo 5 USDT).")
        return None

    entry_price = trade_plan["entry_price"]
    qty = calculate_quantity(capital, entry_price)

    print(f"🟢 COMPRANDO {symbol} | Qty: {qty} | Precio: {entry_price}")

    order_data = place_market_buy(user_id, symbol, qty)

    if not order_data:
        print(f"❌ Error al abrir operación en {symbol}")
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


# =======================================
# MONITOREO HASTA TP O SL
# =======================================

def monitor_trade(position):
    """
    Monitorea cada 2 segundos hasta alcanzar TP o SL.
    """

    user_id = position["user_id"]
    symbol = position["symbol"]
    entry = position["entry_price"]
    qty = position["qty"]

    tp_min = position["tp_min"]
    sl_max = position["sl_max"]

    print(f"📡 Monitoreando operación activa en {symbol}...")

    while True:

        current_price = get_price(symbol)

        if not current_price:
            print("⚠ Error obteniendo precio, reintentando...")
            time.sleep(2)
            continue

        # TAKE PROFIT
        if current_price >= tp_min:
            print(f"🎯 TP alcanzado en {symbol} | Precio actual: {current_price}")

            sell_data = place_market_sell(user_id, symbol, qty)

            if sell_data:
                register_trade(user_id, symbol, entry, current_price, qty, "tp_hit")
                print("🟢 Operación finalizada con GANANCIA")
            return "tp_hit"

        # STOP LOSS
        if current_price <= sl_max:
            print(f"🛑 SL alcanzado en {symbol} | Precio actual: {current_price}")

            sell_data = place_market_sell(user_id, symbol, qty)

            if sell_data:
                register_trade(user_id, symbol, entry, current_price, qty, "sl_hit")
                print("🔴 Operación finalizada con PÉRDIDA controlada")
            return "sl_hit"

        time.sleep(2)


# =======================================
# CICLO COMPLETO DEL BREAKOUT AGRESIVO
# =======================================

def trading_cycle(user_id):
    """
    1. Escanea mercado CoinW
    2. Elige las mejores oportunidades (Breakout agresivo)
    3. Ejecuta compra
    4. Monitorea hasta TP/SL
    """

    print(f"\n🚀 INICIANDO CICLO DE TRADINGX PARA {user_id}")

    # 1. Escaneo
    opportunities = scan_market()

    if not opportunities:
        print("⚪ No hay oportunidades en este ciclo.")
        return "no_opportunity"

    # 2. Seleccionar mejor par
    best = opportunities[0]
    symbol = best["symbol"]
    trade_plan = best["trade_plan"]

    print(f"🔥 Mejor oportunidad encontrada: {symbol} | Fuerza: {trade_plan['strength']}")

    # 3. Abrir operación
    position = open_trade(user_id, symbol, trade_plan)

    if not position:
        print("❌ No se pudo abrir la operación.")
        return "failed_open"

    # 4. Monitoreo activo
    result = monitor_trade(position)

    print(f"📊 Resultado final del ciclo: {result}")
    return result
