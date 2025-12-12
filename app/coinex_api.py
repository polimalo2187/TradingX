import time
import hashlib
import requests
from app.database import get_api_keys


# ======================================================
#  COINEX API V2 – BASE
# ======================================================
COINEX_BASE_URL = "https://api.coinex.com/v2"


# ======================================================
# FIRMA OFICIAL COINEX V2
# ======================================================
def sign_request(secret_key: str, method: str, endpoint: str, params: dict):
    """
    Firma oficial CoinEx API V2:
    md5(secret_key + method + endpoint + sorted_params + timestamp)
    """
    timestamp = str(int(time.time() * 1000))
    sorted_params = "&".join([f"{k}={params[k]}" for k in sorted(params)]) if params else ""

    raw = secret_key + method + endpoint + sorted_params + timestamp
    signature = hashlib.md5(raw.encode()).hexdigest()

    return signature, timestamp


# ======================================================
# REQUEST GENERAL
# ======================================================
def make_request(method, endpoint, api_key=None, secret_key=None, params=None):
    if params is None:
        params = {}

    url = COINEX_BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

    # Si requiere firma (API protegida)
    if api_key and secret_key:
        signature, timestamp = sign_request(secret_key, method, endpoint, params)
        headers["X-COINEX-KEY"] = api_key
        headers["X-COINEX-SIGN"] = signature
        headers["X-COINEX-TIMESTAMP"] = timestamp

    try:
        if method == "GET":
            res = requests.get(url, params=params, headers=headers, timeout=10)
        else:
            res = requests.post(url, json=params, headers=headers, timeout=10)

        return res.json()

    except Exception as e:
        print(f"❌ Error de comunicación con CoinEx: {e}")
        return None


# ======================================================
# PRECIO SPOT
# ======================================================
def get_price(symbol):
    endpoint = "/market/ticker"
    params = {"market": symbol}

    r = make_request("GET", endpoint, None, None, params)

    if not r or r.get("code") != 0:
        print(f"❌ No se pudo obtener precio de {symbol}")
        return None

    return float(r["data"]["ticker"]["last"])


# ======================================================
# CANDLES (KLINES)
# ======================================================
def get_candles(symbol, timeframe="1min", limit=50):
    endpoint = "/market/kline"
    params = {"market": symbol, "limit": limit, "interval": timeframe}

    r = make_request("GET", endpoint, None, None, params)
    if not r or r.get("code") != 0:
        return []

    return r["data"]["klines"]


# ======================================================
# LISTA DE MERCADOS SPOT
# ======================================================
def get_spot_pairs():
    endpoint = "/market/list"
    r = make_request("GET", endpoint)

    if not r or r.get("code") != 0:
        return []

    return [m["market"] for m in r["data"]]


# ======================================================
# CONSULTAR BALANCE REAL
# ======================================================
def get_balance(user_id, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return 0

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/balance/query"
    params = {}

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error leyendo balance:", r)
        return 0

    balances = r["data"]["balances"]

    if asset not in balances:
        return 0

    return float(balances[asset]["available"])


# ======================================================
# MARKET BUY
# ======================================================
def place_market_buy(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/order/market"
    params = {
        "market": symbol,
        "side": "buy",
        "amount": quantity
    }

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error al comprar {symbol}: {r}")
        return None

    print(f"🟢 COMPRA ejecutada en {symbol}")
    return r["data"]


# ======================================================
# MARKET SELL
# ======================================================
def place_market_sell(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/order/market"
    params = {
        "market": symbol,
        "side": "sell",
        "amount": quantity
    }

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error al vender {symbol}: {r}")
        return None

    print(f"🔴 VENTA ejecutada en {symbol}")
    return r["data"]
