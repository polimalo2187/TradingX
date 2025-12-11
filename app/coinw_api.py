import time
import hashlib
import requests
import hmac
import json

from app.config import COINW_BASE_URL
from app.database import get_api_keys


# =========================================
# FIRMA DE SOLICITUD PARA COINW
# =========================================

def sign_request(api_secret: str, params: dict) -> dict:
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


# =========================================
# REQUEST HTTP GENERAL
# =========================================

def make_request(method: str, endpoint: str, api_key=None, params=None):
    if params is None:
        params = {}

    url = COINW_BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

    if api_key:
        headers["X-COINW-APIKEY"] = api_key

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            response = requests.post(url, headers=headers, data=json.dumps(params), timeout=10)

        return response.json()

    except Exception as e:
        print(f"❌ Error de conexión con CoinW: {e}")
        return None


# =========================================
# PRECIO DE UN PAR (PÚBLICO)
# =========================================

def get_price(symbol: str):
    endpoint = "/api/v1/public/market/ticker"
    params = {"symbol": symbol}

    response = make_request("GET", endpoint, None, params)

    if not response or response.get("code") != 0:
        print(f"❌ Error obteniendo precio de {symbol}")
        return None

    try:
        return float(response["data"]["lastPrice"])
    except:
        return None


# =========================================
# VELAS HISTÓRICAS
# =========================================

def get_candles(symbol: str, timeframe="1min", limit=50):
    endpoint = "/api/v1/public/market/kline"
    params = {"symbol": symbol, "limit": limit, "type": timeframe}

    response = make_request("GET", endpoint, None, params)

    if not response or response.get("code") != 0:
        print(f"❌ Error obteniendo velas de {symbol}")
        return []

    return response.get("data", [])


# =========================================
# LISTA DE PARES SPOT
# =========================================

def get_spot_pairs():
    endpoint = "/api/v1/public/symbol/list"
    response = make_request("GET", endpoint)

    if not response or response.get("code") != 0:
        print("❌ No se pudieron obtener los pares SPOT")
        return []

    try:
        return [item["symbol"] for item in response.get("data", [])]
    except:
        return []


# =========================================
# OBTENER BALANCE SPOT DEL USUARIO
# ESTE ES EL ENDPOINT CORRECTO
# =========================================

def get_balance(user_id: int, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ El usuario no tiene API Keys configuradas.")
        return 0

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    # ENDPOINT REAL QUE DEVUELVE LISTA DE BALANCES SPOT
    endpoint = "/api/v1/private/account/balance/list"

    params = {}  # No requiere parámetro 'asset'

    signed = sign_request(api_secret, params)
    response = make_request("GET", endpoint, api_key, signed)

    if not response or response.get("code") != 0:
        print("❌ Error obteniendo balance del usuario.")
        return 0

    try:
        balances = response.get("data", [])
        if not balances:
            return 0

        for b in balances:
            if b.get("asset") == asset:
                return float(b.get("free", 0))

        return 0

    except Exception as e:
        print("⚠ Error leyendo balance:", e)
        return 0


# =========================================
# ORDEN DE COMPRA MARKET
# =========================================

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
    response = make_request("POST", endpoint, api_key, signed)

    if not response or response.get("code") != 0:
        print(f"❌ Error ejecutando compra en {symbol}")
        return None

    print(f"🟢 COMPRA ejecutada en {symbol}: {response['data']}")
    return response["data"]


# =========================================
# ORDEN DE VENTA MARKET
# =========================================

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
    response = make_request("POST", endpoint, api_key, signed)

    if not response or response.get("code") != 0:
        print(f"❌ Error ejecutando venta en {symbol}")
        return None

    print(f"🔴 VENTA ejecutada en {symbol}: {response['data']}")
    return response["data"]


# =========================================
# CONSULTAR ESTADO DE ORDEN
# =========================================

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
    response = make_request("GET", endpoint, api_key, signed)

    if not response or response.get("code") != 0:
        print(f"❌ No se pudo obtener la orden {order_id}")
        return None

    return response["data"]
