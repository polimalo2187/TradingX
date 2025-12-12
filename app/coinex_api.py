import time
import hashlib
import hmac
import json
import requests

from app.database import get_api_keys


# ======================================================
#  COINEX API V2 (OFICIAL)
# ======================================================
COINEX_BASE_URL = "https://api.coinex.com/v2"


# ======================================================
#  FUNCIONES DE FIRMA (REGLAS OFICIALES V2)
# ======================================================
def sign_request(secret_key: str, method: str, endpoint: str, params: dict):
    """
    CoinEx API V2 firma oficial:
    md5(secret + method + endpoint + sorted_params + timestamp)
    """

    timestamp = str(int(time.time() * 1000))

    # Ordenar parámetros
    sorted_params = "&".join([f"{k}={params[k]}" for k in sorted(params)]) if params else ""

    # Cadena a firmar
    raw = secret_key + method + endpoint + sorted_params + timestamp

    signature = hashlib.md5(raw.encode()).hexdigest()

    return signature, timestamp


# ======================================================
#  REQUEST GENERAL
# ======================================================
def make_request(method, endpoint, api_key=None, params=None):
    if params is None:
        params = {}

    url = COINEX_BASE_URL + endpoint

    # Firma solo si el endpoint requiere autenticación
    headers = {"Content-Type": "application/json"}

    if api_key:
        secret = get_api_keys_from_key(api_key)
        if not secret:
            print("❌ Error obteniendo secret_key.")
            return None

    try:
        if api_key:
            signature, timestamp = sign_request(secret, method, endpoint, params)
            headers["X-COINEX-KEY"] = api_key
            headers["X-COINEX-SIGN"] = signature
            headers["X-COINEX-TIMESTAMP"] = timestamp

        if method == "GET":
            r = requests.get(url, params=params, headers=headers, timeout=10)
        else:
            r = requests.post(url, json=params, headers=headers, timeout=10)

        return r.json()

    except Exception as e:
        print(f"❌ Error de comunicación con CoinEx: {e}")
        return None


def get_api_keys_from_key(api_key):
    """ Busca el secret_key de ese api_key (para firma interna). """
    from app.database import users_col

    user = users_col.find_one({"api_key": {"$regex": api_key}})
    if not user:
        return None
    return user["api_secret"]  # desencriptado ya lo entrega database.py


# ======================================================
#  PRECIO ACTUAL (TICKER)
# ======================================================
def get_price(symbol):
    endpoint = "/market/ticker"
    params = {"market": symbol}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error obteniendo precio de {symbol}")
        return None

    try:
        return float(r["data"]["ticker"]["last"])
    except:
        return None


# ======================================================
#  KLINES / CANDLES
# ======================================================
def get_candles(symbol, timeframe="1min", limit=50):
    endpoint = "/market/kline"
    params = {"market": symbol, "limit": limit, "period": timeframe}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        return []

    return r["data"]["klines"]


# ======================================================
#  LISTA DE PARES SPOT
# ======================================================
def get_spot_pairs():
    endpoint = "/market/list"
    r = make_request("GET", endpoint)

    if not r or r.get("code") != 0:
        return []

    return [m["market"] for m in r["data"]]


# ======================================================
#  BALANCE SPOT REAL
# ======================================================
def get_balance(user_id, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return 0

    api_key = keys["api_key"]
    secret = keys["api_secret"]

    endpoint = "/balance/query"
    params = {}

    signature, timestamp = sign_request(secret, "POST", endpoint, params)

    headers = {
        "Content-Type": "application/json",
        "X-COINEX-KEY": api_key,
        "X-COINEX-SIGN": signature,
        "X-COINEX-TIMESTAMP": timestamp
    }

    url = COINEX_BASE_URL + endpoint

    try:
        r = requests.post(url, json=params, headers=headers).json()
    except:
        print("❌ Error consultando balance.")
        return 0

    if r.get("code") != 0:
        print("❌ Error en balance:", r)
        return 0

    balances = r["data"]["balances"]

    if asset not in balances:
        return 0

    return float(balances[asset]["available"])


# ======================================================
#  ORDEN MARKET BUY
# ======================================================
def place_market_buy(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    secret = keys["api_secret"]

    endpoint = "/order/market"

    params = {
        "market": symbol,
        "side": "buy",
        "amount": quantity
    }

    signature, timestamp = sign_request(secret, "POST", endpoint, params)

    headers = {
        "Content-Type": "application/json",
        "X-COINEX-KEY": api_key,
        "X-COINEX-SIGN": signature,
        "X-COINEX-TIMESTAMP": timestamp
    }

    try:
        r = requests.post(COINEX_BASE_URL + endpoint, json=params, headers=headers).json()
    except:
        print("❌ Error ejecutando compra.")
        return None

    if r.get("code") != 0:
        print(f"❌ Error compra {symbol}: {r}")
        return None

    print(f"🟢 COMPRA ejecutada {symbol}")
    return r["data"]


# ======================================================
#  ORDEN MARKET SELL
# ======================================================
def place_market_sell(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    secret = keys["api_secret"]

    endpoint = "/order/market"

    params = {
        "market": symbol,
        "side": "sell",
        "amount": quantity
    }

    signature, timestamp = sign_request(secret, "POST", endpoint, params)

    headers = {
        "Content-Type": "application/json",
        "X-COINEX-KEY": api_key,
        "X-COINEX-SIGN": signature,
        "X-COINEX-TIMESTAMP": timestamp
    }

    try:
        r = requests.post(COINEX_BASE_URL + endpoint, json=params, headers=headers).json()
    except:
        print("❌ Error ejecutando venta.")
        return None

    if r.get("code") != 0:
        print(f"❌ Error venta {symbol}: {r}")
        return None

    print(f"🔴 VENTA ejecutada {symbol}")
    return r["data"]
