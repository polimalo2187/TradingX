from app.coinex_api import get_spot_pairs, get_candles
from app.strategy_breakout import get_trade_signal
from app.config import MAX_ACTIVE_PAIRS


# =======================================
# FILTRAR PARES VÁLIDOS (USDT + VELAS ACTIVAS)
# =======================================

def fetch_pairs():
    """
    Obtiene pares Spot de CoinEx y filtra:
    - Pares que terminan en USDT
    - Pares con velas activas
    """

    raw_pairs = get_spot_pairs()

    if not raw_pairs:
        print("❌ No se pudo obtener la lista de mercados desde CoinEx.")
        return []

    # CoinEx devuelve un dict: { "BTCUSDT": {...}, "ETHUSDT": {...}, ... }
    try:
        all_pairs = list(raw_pairs.keys())
    except:
        # En caso extremo: CoinEx cambió la estructura
        all_pairs = raw_pairs

    # Filtrar pares USDT
    usdt_pairs = [m for m in all_pairs if m.endswith("USDT")]

    valid_pairs = []

    for symbol in usdt_pairs:
        try:
            candles = get_candles(symbol, "1min", limit=2)

            # CoinEx velas → [timestamp, open, close, high, low, volume]
            if candles and len(candles) >= 1:
                valid_pairs.append(symbol)

        except Exception as e:
            print(f"⚠️ Error leyendo velas de {symbol}: {e}")
            continue

    print(f"🔍 Pares USDT válidos con velas activas: {len(valid_pairs)}")
    return valid_pairs


# =======================================
# EVALUAR BREAKOUT EN CADA PAR
# =======================================

def evaluate_pairs(pairs):
    """
    Analiza cada par buscando oportunidades reales.
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
# SELECCIONAR LOS MEJORES
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
    print("🔎 Escaneando mercado Spot CoinEx...")

    pairs = fetch_pairs()

    if not pairs:
        print("❌ No hay pares disponibles.")
        return []

    opportunities = evaluate_pairs(pairs)

    if not opportunities:
        print("⚪ No se detectaron oportunidades en este ciclo.")
        return []

    best = select_best_pairs(opportunities)

    print(f"📈 Oportunidades finales: {[x['symbol'] for x in best]}")
    return best
