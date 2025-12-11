from app.coinw_api import get_spot_pairs, get_candles
from app.strategy_breakout import get_trade_signal
from app.config import MAX_ACTIVE_PAIRS


# =======================================
# FILTRAR PARES VÁLIDOS (USDT + LIQUIDEZ)
# =======================================

def fetch_pairs():
    """
    Obtiene pares Spot de CoinW y filtra solo:
    - Pares USDT
    - Pares con velas activas
    """

    all_pairs = get_spot_pairs()

    if not all_pairs:
        print("❌ No se pudo obtener la lista de pares.")
        return []

    # Filtrar solo mercado SPOT USDT
    usdt_pairs = [pair for pair in all_pairs if pair.endswith("USDT")]

    valid_pairs = []

    for p in usdt_pairs:
        try:
            candles = get_candles(p, "1min", limit=2)
            if candles and len(candles) > 0:
                valid_pairs.append(p)
        except:
            continue

    print(f"🔍 Pares USDT válidos con velas activas: {len(valid_pairs)}")
    return valid_pairs


# =======================================
# EVALUAR BREAKOUT EN CADA PAR
# =======================================

def evaluate_pairs(pairs):
    """
    Analiza cada par y detecta Breakouts reales.
    """

    opportunities = []

    for symbol in pairs:
        try:
            signal_data = get_trade_signal(symbol)

            if signal_data["signal"]:
                opportunities.append({
                    "symbol": symbol,
                    "strength": signal_data["trade_plan"]["strength"],
                    "trade_plan": signal_data["trade_plan"]
                })

        except Exception as e:
            print(f"⚠️ Error analizando {symbol}: {e}")

    return opportunities


# =======================================
# SELECCIONAR MEJORES PARES SEGÚN FUERZA
# =======================================

def select_best_pairs(opportunities):
    if not opportunities:
        return []

    # Ordenar de mayor fuerza a menor fuerza
    sorted_ops = sorted(opportunities, key=lambda x: x["strength"], reverse=True)

    best = sorted_ops[:MAX_ACTIVE_PAIRS]

    print(f"⭐ Mejores pares seleccionados: {[p['symbol'] for p in best]}")
    return best


# =======================================
# SCAN COMPLETO DEL MERCADO
# =======================================

def scan_market():
    """
    1. Obtiene pares USDT válidos
    2. Evalúa señales Breakout
    3. Selecciona TOP oportunidades
    """

    print("🔎 Escaneando mercado Spot de CoinW...")

    # 1. Obtener pares activos y válidos
    pairs = fetch_pairs()

    if not pairs:
        print("❌ No hay pares disponibles para analizar.")
        return []

    # 2. Evaluar Breakouts
    opportunities = evaluate_pairs(pairs)

    if not opportunities:
        print("⚪ No se detectaron oportunidades en este ciclo.")
        return []

    # 3. Seleccionar TOP oportunidades
    best = select_best_pairs(opportunities)

    print(f"📈 Oportunidades finales: {[x['symbol'] for x in best]}")
    return best
