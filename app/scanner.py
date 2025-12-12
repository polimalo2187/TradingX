from app.coinex_api import get_spot_pairs, get_candles
from app.strategy_breakout import get_trade_signal
from app.config import MAX_ACTIVE_PAIRS


# ======================================================
# OBTENER LISTA DE PARES COMPATIBLES (USDT)
# ======================================================

def fetch_pairs():
    """
    Obtiene pares Spot del endpoint oficial CoinEx V2.
    Luego filtra pares en USDT y pares que tengan velas activas.
    """

    raw = get_spot_pairs()

    if not raw:
        print("❌ No se pudo obtener la lista de mercados desde CoinEx.")
        return []

    # CoinEx V2 devuelve:  [{ "name": "BTCUSDT", ... }, ... ]
    try:
        all_pairs = [m["name"] for m in raw]
    except:
        all_pairs = raw

    # Filtrar USDT
    usdt_pairs = [p for p in all_pairs if p.endswith("USDT")]

    valid_pairs = []

    for symbol in usdt_pairs:
        try:
            candles = get_candles(symbol, timeframe="1min", limit=2)

            # CoinEx devuelve velas → [timestamp, open, close, high, low, volume]
            if isinstance(candles, list) and len(candles) > 0:
                valid_pairs.append(symbol)

        except Exception as e:
            print(f"⚠️ Error leyendo velas de {symbol}: {e}")

    print(f"🔍 Pares USDT válidos con velas activas: {len(valid_pairs)}")
    return valid_pairs


# ======================================================
# ANALIZAR TODOS LOS PARES
# ======================================================

def evaluate_pairs(pairs):
    """
    Evalúa cada par para ver si hay oportunidades (breakout).
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


# ======================================================
# SELECCIONAR LOS MEJORES
# ======================================================

def select_best_pairs(opportunities):
    if not opportunities:
        return []

    sorted_ops = sorted(opportunities, key=lambda x: x["strength"], reverse=True)

    best = sorted_ops[:MAX_ACTIVE_PAIRS]

    print(f"⭐ Mejores pares seleccionados: {[p['symbol'] for p in best]}")
    return best


# ======================================================
# ESCANEO COMPLETO DEL MERCADO
# ======================================================

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
