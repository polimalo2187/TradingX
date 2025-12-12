from app.coinex_api import get_spot_pairs, get_candles
from app.strategy_breakout import get_trade_signal
from app.config import MAX_ACTIVE_PAIRS


# =======================================
# FILTRAR PARES VÁLIDOS (USDT + VELAS ACTIVAS)
# =======================================

def fetch_pairs():
    """
    Obtiene pares Spot de CoinEx y filtra:
    - Pares USDT
    - Pares con velas correctas
    """

    all_pairs = get_spot_pairs()

    if not all_pairs:
        print("❌ No se pudo obtener la lista de pares desde CoinEx.")
        return []

    # CoinEx usa mismo formato: BTCUSDT, ETHUSDT...
    usdt_pairs = [p for p in all_pairs if p.endswith("USDT")]

    valid_pairs = []

    for symbol in usdt_pairs:
        try:
            candles = get_candles(symbol, "1min", limit=2)

            # CoinEx devuelve velas como listas tipo:
            # [timestamp, open, close, high, low, volume]
            if candles and len(candles) >= 1:
                valid_pairs.append(symbol)

        except Exception as e:
            print(f"⚠️ Error obteniendo velas de {symbol}: {e}")
            continue

    print(f"🔍 Pares USDT válidos con velas activas: {len(valid_pairs)}")
    return valid_pairs


# =======================================
# EVALUAR BREAKOUT EN CADA PAR
# =======================================

def evaluate_pairs(pairs):
    """
    Analiza los pares y detecta Breakouts.
    """

    opportunities = []

    for symbol in pairs:
        try:
            signal = get_trade_signal(symbol)

            if signal["signal"]:
                opportunities.append({
                    "symbol": symbol,
                    "strength": signal["trade_plan"]["strength"],
                    "trade_plan": signal["trade_plan"]
                })

        except Exception as e:
            print(f"⚠️ Error analizando {symbol}: {e}")

    return opportunities


# =======================================
# SELECCIONAR MEJORES OPORTUNIDADES
# =======================================

def select_best_pairs(opportunities):
    if not opportunities:
        return []

    sorted_ops = sorted(opportunities, key=lambda x: x["strength"], reverse=True)

    best = sorted_ops[:MAX_ACTIVE_PAIRS]

    print(f"⭐ Mejores pares seleccionados: {[p['symbol'] for p in best]}")
    return best


# =======================================
# ESCANEO COMPLETO DEL MERCADO
# =======================================

def scan_market():
    """
    PASOS:
    1. Obtener pares activos
    2. Analizar señales
    3. Seleccionar mejores oportunidades
    """

    print("🔎 Escaneando mercado Spot de CoinEx...")

    pairs = fetch_pairs()

    if not pairs:
        print("❌ No hay pares válidos disponibles.")
        return []

    opportunities = evaluate_pairs(pairs)

    if not opportunities:
        print("⚪ No se detectaron oportunidades este ciclo.")
        return []

    best = select_best_pairs(opportunities)

    print(f"📈 Oportunidades finales: {[x['symbol'] for x in best]}")
    return best
