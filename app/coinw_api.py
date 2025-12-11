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
    """
    CoinW exige timestamp + firma HMAC SHA256
    """
    timestamp = str(int(time.time() * 1000))
    params["timestamp"] = timestamp

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
        headers["X-COINW-APIKEY"] = api_key  # HEADER correcto para CoinW

    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            resp = requests.post(url, headers=headers, data=json.dumps(params), timeout=10)

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

    try:
        return float(r["data"]["lastPrice"])
    except:
        return None


# ======================================================
# KLINES / VELAS
# ======================================================

def get_candles(symbol: str, timeframe="1min", limit=50):
    endpoint = "/api/v1/public/market/kline"
    params = {"symbol": symbol, "limit": limit, "type": timeframe}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error obteniendo velas de {symbol}")
        return []

    return r.get("data", [])


# ======================================================
# LISTA DE PARES SPOT
# ======================================================

def get_spot_pairs():
    endpoint = "/api/v1/public/symbol/list"
    r = make_request("GET", endpoint)

    if not r or r.get("code") != 0:
        print("❌ Error obteniendo lista de pares SPOT")
        return []

    try:
        return [i["symbol"] for i in r.get("data", [])]
    except:
        return []


# ======================================================
# BALANCE SPOT REAL – ENDPOINT CORRECTO
# ======================================================

def get_balance(user_id: int, asset="USDT"):
    """
    El endpoint correcto devuelve lista completa de balances SPOT.
    """
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys configuradas.")
        return 0

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/api/v1/private/account/balance/list"

    params = {}  # CoinW no requiere asset aquí
    signed = sign_request(api_secret, params)

    r = make_request("GET", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print("❌ Error consultando balance del usuario.")
        return 0

    balances = r.get("data", [])
    if not balances:
        return 0

    # Buscar USDT exacto dentro de la lista
    for b in balances:
        if b.get("asset") == asset:
            try:
                return float(b.get("free", 0))
            except:
                return 0

    return 0


# ======================================================
# ORDEN MARKET BUY
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
        "qty": quantity
    }

    signed = sign_request(api_secret, params)

    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error comprando {symbol}")
        return None

    print(f"🟢 COMPRA ejecutada: {r['data']}")
    return r["data"]


# ======================================================
# ORDEN MARKET SELL
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
        "qty": quantity
    }

    signed = sign_request(api_secret, params)

    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error vendiendo {symbol}")
        return None

    print(f"🔴 VENTA ejecutada: {r['data']}")
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

    params = {"symbol": symbol, "orderId": order_id}

    signed = sign_request(api_secret, params)
    r = make_request("GET", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error consultando orden {order_id}")
        return None

    return r["data"]
