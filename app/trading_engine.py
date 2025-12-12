import time
import threading

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
    Convierte capital USDT → cantidad del par.
    CoinEx permite hasta 6 decimales.
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
    Ejecuta compra en mercado SPOT (API V2)
    """

    capital = get_user_capital(user_id)

    if capital < 5:
        print("❌ Capital insuficiente (mínimo 5 USDT requeridos).")
        return None

    entry_price = trade_plan["entry_price"]
    qty = calculate_quantity(capital, entry_price)

    if qty <= 0:
        print("❌ Cantidad inválida para la compra.")
        return None

    print(f"🟢 Ejecutando COMPRA {symbol} | Cantidad: {qty} | Entrada: {entry_price}")

    order_data = place_market_buy(user_id, symbol, qty)

    if not order_data:
        print(f"❌ Error ejecutando compra en {symbol}.")
        return None

    return {
        "user_id": user_id,
        "symbol": symbol,
        "entry_price": entry_price,
        "qty": qty,
        "tp_price": trade_plan["tp_min"],
        "sl_price": trade_plan["sl_max"]
    }


# ======================================================
# MONITOREAR OPERACIÓN (NO BLOQUEA)
# ======================================================

def monitor_trade(position):
    """
    Monitorea operación hasta cumplir TP o SL.
    EJECUTADO EN HILO PARA NO BLOQUEAR EL BOT.
    """

    user_id = position["user_id"]
    symbol = position["symbol"]
    entry = position["entry_price"]
    qty = position["qty"]

    tp_price = position["tp_price"]
    sl_price = position["sl_price"]

    print(f"📡 Monitoreando operación en {symbol}...")

    while True:

        current_price = get_price(symbol)

        if not current_price:
            print("⚠ Precio no disponible, reintentando...")
            time.sleep(3)
            continue

        # TAKE PROFIT
        if current_price >= tp_price:
            print(f"🎯 TP alcanzado en {symbol} | Precio: {current_price}")

            result = place_market_sell(user_id, symbol, qty)
            if result:
                register_trade(user_id, symbol, entry, current_price, qty, "tp_hit")
                print("🟢 Ganancia registrada")
            return

        # STOP LOSS
        if current_price <= sl_price:
            print(f"🛑 STOP LOSS alcanzado en {symbol} | Precio: {current_price}")

            result = place_market_sell(user_id, symbol, qty)
            if result:
                register_trade(user_id, symbol, entry, current_price, qty, "sl_hit")
                print("🔴 Pérdida controlada registrada")
            return

        time.sleep(2)


# ======================================================
# CICLO COMPLETO DE TRADINGX (NO BLOQUEA)
# ======================================================

def trading_cycle(user_id):
    """
    Ciclo:
    1. Escaneo
    2. Detectar oportunidad
    3. Abrir trade
    4. Monitorear TP/SL
    """

    print(f"\n🚀 INICIANDO CICLO DE TRADING PARA USER {user_id}")

    opportunities = scan_market()

    if not opportunities:
        print("⚪ No hay oportunidades en el mercado.")
        return

    best = opportunities[0]
    symbol = best["symbol"]
    plan = best["trade_plan"]

    print(f"🔥 Oportunidad detectada: {symbol} | Fuerza: {plan['strength']}")

    position = open_trade(user_id, symbol, plan)

    if not position:
        print("❌ No se pudo abrir la operación.")
        return

    # MONITOREO EN HILO PARA EVITAR BLOQUEAR EL BOT
    thread = threading.Thread(target=monitor_trade, args=(position,), daemon=True)
    thread.start()

    print("📡 Monitoreo iniciado en segundo plano.")
