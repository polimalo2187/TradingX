import time
import hashlib
import requests
import hmac
import json

from app.database import get_api_keys


# ======================================================
# BASE URL OFICIAL DE COINEX
# ======================================================

COINEX_BASE_URL = "https://api.coinex.com/v1"


# ======================================================
# FUNCIÓN DE FIRMA – COINEX (HMAC-SHA256)
# ======================================================

def sign_request(api_secret: str, params: dict) -> dict:
    """
    CoinEx firma: 
    1. ordena parámetros
    2. concatena en formato query
    3. aplica HMAC SHA256
    """

    sorted_params = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    signature = hmac.new(
        api_secret.encode(),
        sorted_params.encode(),
        hashlib.sha256
    ).hexdigest()

    params["signature"] = signature
    return params


# ======================================================
# REQUEST GENÉRICO A LA API
# ======================================================

def make_request(method: str, endpoint: str, api_key=None, params=None):
    if params is None:
        params = {}

    url = COINEX_BASE_URL + endpoint

    headers = {"Content-Type": "application/json"}

    if api_key:
        headers["X-COINEX-KEY"] = api_key

    try:
        if method.upper() == "GET":
            r = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            r = requests.post(url, headers=headers, data=json.dumps(params), timeout=10)

        return r.json()

    except Exception as e:
        print(f"❌ Error de conexión CoinEx: {e}")
        return None


# ======================================================
# PRECIO SPOT – TICKER
# ======================================================

def get_price(symbol: str):
    """
    Ejemplo símbolo CoinEx → BTCUSDT, ETHUSDT, etc.
    """
    endpoint = "/market/ticker"
    params = {"market": symbol}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        print(f"❌ Error obteniendo precio de {symbol}")
        return None

    try:
        return float(r["data"]["last"])
    except:
        return None


# ======================================================
# OBTENER VELAS / KLINES
# ======================================================

def get_candles(symbol: str, timeframe="1min", limit=50):
    endpoint = "/market/kline"
    params = {"market": symbol, "limit": limit, "type": timeframe}

    r = make_request("GET", endpoint, None, params)

    if not r or r.get("code") != 0:
        return []

    return r.get("data", [])


# ======================================================
# LISTA DE MERCADOS SPOT
# ======================================================

def get_spot_pairs():
    endpoint = "/market/list"
    r = make_request("GET", endpoint)

    if not r or r.get("code") != 0:
        return []

    try:
        return r.get("data", [])
    except:
        return []


# ======================================================
# BALANCE SPOT REAL DEL USUARIO
# ======================================================

def get_balance(user_id: int, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return 0

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/balance/info"
    params = {}

    signed = sign_request(api_secret, params)

    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print("❌ Error consultando balance.")
        return 0

    balances = r.get("data", {})

    if asset not in balances:
        return 0

    try:
        return float(balances[asset]["available"])
    except:
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

    endpoint = "/order/put_market"

    params = {
        "market": symbol,
        "type": "buy",
        "amount": quantity
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error comprando {symbol}: {r}")
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

    endpoint = "/order/put_market"

    params = {
        "market": symbol,
        "type": "sell",
        "amount": quantity
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error vendiendo {symbol}: {r}")
        return None

    print(f"🔴 VENTA ejecutada: {r['data']}")
    return r["data"]


# ======================================================
# CONSULTAR ORDEN
# ======================================================

def get_order_status(user_id: int, order_id: str, symbol: str):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    endpoint = "/order/status"

    params = {
        "market": symbol,
        "id": order_id
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", endpoint, api_key, signed)

    if not r or r.get("code") != 0:
        print(f"❌ Error consultando orden {order_id}")
        return None

    return r["data"]
