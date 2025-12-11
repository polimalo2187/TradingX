import time
import hashlib
import requests
import hmac
import json

from app.config import COINW_BASE_URL
from app.database import get_api_keys


# ======================================================
# FIRMA DE SOLICITUD – COINW
# ======================================================

def sign_request(api_secret: str, params: dict) -> dict:
    timestamp = str(int(time.time() * 1000))
    params["timestamp"] = timestamp

    # CoinW requiere ordenar y firmar TODO el query
    query_string = "&".join([f"{k}={params[k]}" for k in sorted(params)])

    signature = hmac.new(
        api_secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    params["signature"] = signature
    return params


# ======================================================
# SOLICITUD HTTP
# ======================================================

def make_request(method: str, endpoint: str, api_key=None, params=None):
    if params is None:
        params = {}

    url = COINW_BASE_URL + endpoint

    headers = {"Content-Type": "application/json"}

    if api_key:
        headers["X-COINW-APIKEY"] = api_key

    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            resp = requests.post(url, headers=headers, data=json.dumps(params), timeout=10)

        # CoinW siempre devuelve JSON válido
        return resp.json()

    except Exception as e:
        print(f"❌ Error de conexión a CoinW: {e}")
        return None


# ======================================================
# PRECIO SPOT
# ======================================================

def get_price(symbol: str):
    endpoint = "/api/v1/public/market/ticker"
    params = {"symbol": symbol}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error obteniendo precio de {symbol}")
        return None

    return float(r["data"]["lastPrice"])


# ======================================================
# VELAS / KLINES
# ======================================================

def get_candles(symbol: str, timeframe="1min", limit=50):
    endpoint = "/api/v1/public/market/kline"
    params = {"symbol": symbol, "limit": limit, "type": timeframe}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        return []

    return r.get("data", [])


# ======================================================
# LISTA PARES SPOT
# ======================================================

def get_spot_pairs():
    endpoint = "/api/v1/public/symbol/list"
    r = make_request("GET", endpoint)

    if not r or r.get("code") != 0:
        return []

    return [i["symbol"] for i in r.get("data", [])]


# ======================================================
# BALANCE SPOT – 100% CORREGIDO
# ======================================================

def get_balance(user_id: int, asset="USDT"):
    """
    Se agrega 'accountType = 1' (Spot Account).
    Sin esto CoinW devuelve LISTA VACÍA.
    """
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys configuradas.")
        return 0

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/api/v1/private/account/balance/list"

    params = {
        "accountType": 1   # 🔥 OBLIGATORIO (SPOT)
    }

    signed = sign_request(api_secret, params)
    r = make_request("GET", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print("❌ Error consultando balance.")
        return 0

    balances = r.get("data", [])

    for b in balances:
        if b.get("asset") == asset:
            return float(b.get("free", 0))

    return 0


# ======================================================
# MARKET BUY
# ======================================================

def place_market_buy(user_id: int, symbol: str, quantity: float):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/api/v1/private/trade/order"

    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "qty": quantity,
        "accountType": 1
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error comprando {symbol}: {r}")
        return None

    return r["data"]


# ======================================================
# MARKET SELL
# ======================================================

def place_market_sell(user_id: int, symbol: str, quantity: float):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/api/v1/private/trade/order"

    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "qty": quantity,
        "accountType": 1
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error vendiendo {symbol}: {r}")
        return None

    return r["data"]


# ======================================================
# ESTADO DE ORDEN
# ======================================================

def get_order_status(user_id: int, order_id: str, symbol: str):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/api/v1/private/trade/order/detail"

    params = {
        "symbol": symbol,
        "orderId": order_id,
        "accountType": 1
    }

    signed = sign_request(api_secret, params)
    r = make_request("GET", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error consultando orden {order_id}")
        return None

    return r["data"]
