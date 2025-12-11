from app.coinw_api import (
    place_market_buy,
    place_market_sell,
    get_price
)
from app.strategy_breakout import get_trade_signal
from app.scanner import scan_market
from app.database import get_user_capital  # ✔ ahora tomamos el capital desde MongoDB

import time


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


# =======================================
# MONITOREO DE OPERACIÓN (TP / SL)
# =======================================

def monitor_trade(position):
    """
    Monitorea la operación activa hasta que se alcance TP o SL.
    """

    symbol = position["symbol"]
    entry = position["entry_price"]
    qty = position["qty"]

    tp_min = position["tp_min"]
    tp_max = position["tp_max"]
    sl_min = position["sl_min"]
    sl_max = position["sl_max"]

    print(f"📡 Monitoreando operación en {symbol}...")

    while True:
        current_price = get_price(symbol)

        if not current_price:
            print("⚠️ Precio no disponible. Reintentando...")
            time.sleep(2)
            continue

        # ============================
        # VERIFICAR TAKE PROFIT
        # ============================

        if current_price >= tp_min:
            print(f"🎯 TP alcanzado en {symbol} | Precio: {current_price}")

            sell_data = place_market_sell(symbol, qty)

            if sell_data:
                print(f"🟢 Operación cerrada en ganancia en {symbol}")
            else:
                print("❌ Error al cerrar operación en TP")

            return "tp_hit"

        # ============================
        # VERIFICAR STOP LOSS
        # ============================

        if current_price <= sl_max:
            print(f"🛑 SL alcanzado en {symbol} | Precio: {current_price}")

            sell_data = place_market_sell(symbol, qty)

            if sell_data:
                print(f"🔴 Operación cerrada en pérdida controlada en {symbol}")
            else:
                print("❌ Error al cerrar operación en SL")

            return "sl_hit"

        time.sleep(2)


# =======================================
# CICLO COMPLETO DE TRADING DEL BOT
# =======================================

def trading_cycle(user_id):
    """
    Ciclo completo de trading:
    1. Obtiene capital del usuario desde MongoDB
    2. Escanea el mercado Spot
    3. Selecciona mejores pares
    4. Abre operación en el mejor
    5. Monitorea operación hasta TP o SL
    """

    print("🚀 Iniciando ciclo de TradingX...")

    # Obtener capital real del usuario desde MongoDB
    capital = get_user_capital(user_id)

    if not capital:
        print("⚠️ Usuario no tiene capital configurado.")
        return "no_capital"

    # Encontrar oportunidades de trading
    opportunities = scan_market()

    if not opportunities:
        print("⚪ No se encontraron oportunidades en este ciclo.")
        return "no_opportunity"

    # Seleccionar el par más fuerte
    best = opportunities[0]
    symbol = best["symbol"]
    plan = best["trade_plan"]

    print(f"🔥 Mejor oportunidad: {symbol} | Fuerza: {plan['strength']}")

    # Abrir operación con el capital real del usuario
    position = open_trade(symbol, plan, capital)

    if not position:
        print("❌ No se pudo abrir la operación.")
        return "failed_open"

    # Monitorear operación hasta cierre
    result = monitor_trade(position)

    print(f"📊 Resultado final de operación: {result}")
    return result
