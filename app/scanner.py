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


# =======================================
# EVALUAR FUERZA DE MERCADO EN CADA PAR
# =======================================

def evaluate_pairs(pairs):
    """
    Recorre cada par, analiza si hay señal Breakout
    y crea una lista de pares con fuerza.
    """

    active_opportunities = []

    for symbol in pairs:
        try:
            signal_data = get_trade_signal(symbol)

            if signal_data["signal"]:
                opportunity = {
                    "symbol": symbol,
                    "strength": signal_data["trade_plan"]["strength"],
                    "trade_plan": signal_data["trade_plan"]
                }
                active_opportunities.append(opportunity)

        except Exception as e:
            print(f"⚠️ Error analizando {symbol}: {e}")

    return active_opportunities


# =======================================
# ORDENAR PARES POR FUERZA DE OPORTUNIDAD
# =======================================

def select_best_pairs(opportunities):
    """
    Ordena los pares por fuerza y toma los mejores.
    """

    if not opportunities:
        return []

    # Ordenar por fuerza de mayor a menor
    sorted_ops = sorted(opportunities, key=lambda x: x["strength"], reverse=True)

    # Seleccionar solo los mejores pares según configuración
    best_pairs = sorted_ops[:MAX_ACTIVE_PAIRS]

    print(f"⭐ Mejores pares seleccionados: {[p['symbol'] for p in best_pairs]}")
    return best_pairs


# =======================================
# FUNCIÓN FINAL DEL SCANNER (LLAMADA POR EL MOTOR)
# =======================================

def scan_market():
    """
    Función principal del scanner.
    1. Obtiene pares USDT
    2. Evalúa oportunidades (Breakout)
    3. Selecciona los mejores pares
    4. Devuelve lista final para operar
    """

    print("🔎 Escaneando mercado Spot de CoinW...")

    # 1. Obtener pares válidos
    pairs = fetch_pairs()
    if not pairs:
        print("❌ No hay pares disponibles para analizar.")
        return []

    # 2. Evaluar señales de Breakout
    opportunities = evaluate_pairs(pairs)

    if not opportunities:
        print("⚪ No se detectaron oportunidades en este ciclo.")
        return []

    # 3. Seleccionar los mejores pares según fuerza
    strongest_pairs = select_best_pairs(opportunities)

    print(f"📈 Oportunidades elegidas: {[x['symbol'] for x in strongest_pairs]}")

    return strongest_pairs
