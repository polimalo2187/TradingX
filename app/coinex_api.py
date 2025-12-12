import time
import hashlib
import hmac
import json
import requests

from app.database import get_api_keys


# ==============================
#   COINEX API V2 – BASE URL
# ==============================
COINEX_BASE_URL = "https://api.coinex.com/v2"


# ==============================
#   FIRMA DE PETICIONES V2
# ==============================
def create_signature(secret_key, params: dict):
    """
    Firma oficial de CoinEx API V2 (HMAC-SHA256)
    1. Ordenar parámetros por clave
    2. Convertir a string key=value&...
    3. HMAC-SHA256 con secret_key
    """
    query = "&".join(f"{k}={params[k]}" for k in sorted(params))
    signature = hmac.new(
        secret_key.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


# ==============================
#   PETICIÓN GENERAL A API
# ==============================
def make_request(method, endpoint, api_key=None, params=None):
    if params is None:
        params = {}

    url = COINEX_BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

    if api_key:
        headers["X-COINEX-KEY"] = api_key

    try:
        if method == "GET":
            r = requests.get(url, params=params, headers=headers, timeout=10)
        else:
            r = requests.post(url, data=json.dumps(params), headers=headers, timeout=10)

        return r.json()

    except Exception as e:
        print(f"❌ Error de conexión con CoinEx: {e}")
        return None


# ==============================
#   PRECIO SPOT – V2
# ==============================
def get_price(symbol: str):
    endpoint = "/market/ticker"
    params = {"market": symbol}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        print(f"❌ No se pudo obtener precio de {symbol}")
        return None

    try:
        return float(r["data"]["ticker"]["last"])
    except:
        return None


# ==============================
#   KLINES / CANDLES – V2
# ==============================
def get_candles(symbol: str, timeframe="1min", limit=50):
    endpoint = "/market/kline"
    params = {"market": symbol, "limit": limit, "interval": timeframe}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        return []

    return r.get("data", {}).get("klines", [])


# ==============================
#   LISTA DE MERCADOS SPOT – V2
# ==============================
def get_spot_pairs():
    endpoint = "/market/list"

    r = make_request("GET", endpoint)

    if not r or r.get("code") != 0:
        return []

    return [m["market"] for m in r.get("data", [])]


# ==============================
#   BALANCE – V2
# ==============================
def get_balance(user_id, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return 0

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    timestamp = int(time.time() * 1000)

    params = {"timestamp": timestamp}
    params["signature"] = create_signature(api_secret, params)

    r = make_request("POST", "/balance/query", api_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error obteniendo balance.")
        return 0

    balances = r.get("data", {}).get("balances", {})

    if asset not in balances:
        return 0

    try:
        return float(balances[asset]["available"])
    except:
        return 0


# ==============================
#   MARKET BUY – V2
# ==============================
def place_market_buy(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    timestamp = int(time.time() * 1000)

    params = {
        "market": symbol,
        "side": "buy",
        "amount": quantity,
        "timestamp": timestamp
    }

    params["signature"] = create_signature(api_secret, params)

    r = make_request("POST", "/order/market", api_key, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error comprando {symbol}: {r}")
        return None

    print(f"🟢 COMPRA ejecutada en {symbol}")
    return r["data"]


# ==============================
#   MARKET SELL – V2
# ==============================
def place_market_sell(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    timestamp = int(time.time() * 1000)

    params = {
        "market": symbol,
        "side": "sell",
        "amount": quantity,
        "timestamp": timestamp
    }

    params["signature"] = create_signature(api_secret, params)

    r = make_request("POST", "/order/market", api_key, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error vendiendo {symbol}: {r}")
        return None

    print(f"🔴 VENTA ejecutada en {symbol}")
    return r["data"]


# ==============================
#   CONSULTAR ORDEN – V2
# ==============================
def get_order_status(user_id, order_id, symbol):
    keys = get_api_keys(user_id)
    if not keys:
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    timestamp = int(time.time() * 1000)

    params = {
        "market": symbol,
        "order_id": order_id,
        "timestamp": timestamp
    }

    params["signature"] = create_signature(api_secret, params)

    r = make_request("POST", "/order/status", api_key, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error consultando orden {order_id}")
        return None

    return r["data"]
