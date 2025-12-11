import time
from app.coinw_api import (
    place_market_buy,
    place_market_sell,
    get_price
)
from app.strategy_breakout import get_trade_signal
from app.scanner import scan_market
from app.database import get_user_capital, register_trade


# =======================================
# CALCULAR CANTIDAD DE COMPRA
# =======================================

def calculate_quantity(usdt_amount, price):
    """
    Calcula la cantidad de tokens a comprar según el capital y precio.
    """
    if price <= 0:
        return 0
    qty = usdt_amount / price
    return round(qty, 6)


# =======================================
# INICIAR OPERACIÓN EN UN PAR
# =======================================

def open_trade(user_id, symbol, trade_plan):
    """
    Ejecuta la compra Market y devuelve datos de la operación.
    """

    capital = get_user_capital(user_id)

    if capital <= 0:
        print("❌ El usuario no tiene capital configurado.")
        return None

    entry_price = trade_plan["entry_price"]
    qty = calculate_quantity(capital, entry_price)

    print(f"🟢 Ejecutando compra en {symbol} | Cantidad: {qty}")

    order_data = place_market_buy(user_id, symbol, qty)

    if not order_data:
        print(f"❌ No se pudo abrir operación en {symbol}")
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
# MONITOREO DE OPERACIÓN (TP / SL)
# =======================================

def monitor_trade(position):
    """
    Monitorea la operación activa hasta que se alcance TP o SL.
    """

    user_id = position["user_id"]
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
        # TAKE PROFIT
        # ============================

        if current_price >= tp_min:
            print(f"🎯 TP alcanzado en {symbol} | Precio: {current_price}")

            sell_data = place_market_sell(user_id, symbol, qty)

            if sell_data:
                print(f"🟢 Operación cerrada con GANANCIA en {symbol}")
                register_trade(user_id, symbol, entry, current_price, qty, "tp_hit")
            else:
                print("❌ Error al cerrar operación en TP")

            return "tp_hit"

        # ============================
        # STOP LOSS
        # ============================

        if current_price <= sl_max:
            print(f"🛑 SL alcanzado en {symbol} | Precio: {current_price}")

            sell_data = place_market_sell(user_id, symbol, qty)

            if sell_data:
                print(f"🔴 Operación cerrada con PÉRDIDA controlada en {symbol}")
                register_trade(user_id, symbol, entry, current_price, qty, "sl_hit")
            else:
                print("❌ Error al cerrar operación en SL")

            return "sl_hit"

        # ============================
        # ESPERAR PARA SIGUIENTE CICLO
        # ============================

        time.sleep(2)


# =======================================
# CICLO COMPLETO DE TRADING DEL BOT
# =======================================

def trading_cycle(user_id):
    """
    1. Escanea el mercado Spot
    2. Selecciona mejores pares
    3. Abre operación para ese usuario
    4. Monitorea operación hasta TP/SL
    """

    print(f"🚀 Iniciando ciclo de TradingX para usuario {user_id}...")

    # 1. Escanear mercado
    opportunities = scan_market()

    if not opportunities:
        print("⚪ No se encontraron oportunidades.")
        return "no_opportunity"

    # 2. Tomar el par más fuerte
    best = opportunities[0]
    symbol = best["symbol"]
    trade_plan = best["trade_plan"]

    print(f"🔥 Mejor oportunidad: {symbol} | Fuerza: {trade_plan['strength']}")

    # 3. Abrir operación
    position = open_trade(user_id, symbol, trade_plan)

    if not position:
        print("❌ No se pudo abrir la operación.")
        return "failed_open"

    # 4. Monitorear TP / SL
    result = monitor_trade(position)

    print(f"📊 Resultado final: {result}")
    return result
