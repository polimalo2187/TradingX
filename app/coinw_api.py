import time
import hashlib
import requests
import hmac

from app.config import COINW_BASE_URL
from app.database import get_api_keys


# ============================================
# FIRMA COINW
# ============================================

def sign_request(secret, params: dict):
    params["timestamp"] = str(int(time.time() * 1000))
    query = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params


# ============================================
# REQUEST REAL COMPATIBLE CON COINW
# ============================================

def make_request(method: str, endpoint: str, api_key=None, params=None):
    if params is None:
        params = {}

    url = COINW_BASE_URL + endpoint

    headers = {}

    if api_key:
        headers["X-COINW-APIKEY"] = api_key

    try:
        if method.upper() == "GET":
            resp = requests.get(url, params=params, headers=headers, timeout=10)

        else:  # POST debe ir FORM DATA SIEMPRE
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            resp = requests.post(url, data=params, headers=headers, timeout=10)

        return resp.json()

    except Exception as e:
        print(f"❌ Error HTTP CoinW:", e)
        return None


# ============================================
# PRECIO
# ============================================

def get_price(symbol: str):
    r = make_request("GET", "/api/v1/public/market/ticker", None, {"symbol": symbol})
    if not r or r.get("code") != 0:
        return None
    return float(r["data"]["lastPrice"])


# ============================================
# VELAS
# ============================================

def get_candles(symbol: str, timeframe="1min", limit=50):
    params = {"symbol": symbol, "limit": limit, "type": timeframe}
    r = make_request("GET", "/api/v1/public/market/kline", None, params)
    if not r or r.get("code") != 0:
        return []
    return r.get("data", [])


# ============================================
# LISTA PARES SPOT
# ============================================

def get_spot_pairs():
    r = make_request("GET", "/api/v1/public/symbol/list")
    if not r or r.get("code") != 0:
        return []
    return [i["symbol"] for i in r.get("data", [])]


# ============================================
# BALANCE SPOT REAL
# ============================================

def get_balance(user_id: int, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        return 0

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    params = {"accountType": 1}
    signed = sign_request(api_secret, params)

    r = make_request("GET", "/api/v1/private/account/balance/list", api_key, signed)

    if not r or r.get("code") != 0:
        print("❌ Error balance CoinW:", r)
        return 0

    for coin in r.get("data", []):
        if coin["asset"] == asset:
            return float(coin["free"])

    return 0


# ============================================
# MARKET BUY
# ============================================

def place_market_buy(user_id: int, symbol: str, qty: float):
    keys = get_api_keys(user_id)
    if not keys:
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "qty": qty,
        "accountType": 1
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", "/api/v1/private/trade/order", api_key, signed)

    return r


# ============================================
# MARKET SELL
# ============================================

def place_market_sell(user_id: int, symbol: str, qty: float):
    keys = get_api_keys(user_id)
    if not keys:
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "qty": qty,
        "accountType": 1
    }

    signed = sign_request(api_secret, params)
    r = make_request("POST", "/api/v1/private/trade/order", api_key, signed)

    return r


# ============================================
# ESTADO ORDEN
# ============================================

def get_order_status(user_id: int, order_id: str, symbol: str):
    keys = get_api_keys(user_id)
    if not keys:
        return None

    api_key = keys["api_key"]
    api_secret = keys["api_secret"]

    params = {"symbol": symbol, "orderId": order_id, "accountType": 1}
    signed = sign_request(api_secret, params)

    return make_request("GET", "/api/v1/private/trade/order/detail", api_key, signed)
