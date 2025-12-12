import time
import hashlib
import requests
from app.database import get_api_keys

COINEX_BASE_URL = "https://api.coinex.com/v2"

def sign_request(secret_key: str, method: str, endpoint: str, params: dict):
    timestamp = str(int(time.time() * 1000))
    sorted_params = "&".join(f"{k}={params[k]}" for k in sorted(params)) if params else ""
    raw = secret_key + method + endpoint + sorted_params + timestamp
    signature = hashlib.md5(raw.encode()).hexdigest()
    return signature, timestamp

def make_request(method, endpoint, api_key=None, secret_key=None, params=None):
    if params is None:
        params = {}

    url = COINEX_BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

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
        print(f"❌ Error CoinEx: {e}")
        return None


# ============================================================
#  BALANCE REAL – ÚNICO ENDPOINT VÁLIDO
# ============================================================
def get_balance(user_id, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ Usuario sin API Keys")
        return 0

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    # ✔ CORRECTO
    endpoint = "/balance/query"
    params = {}

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error balance:", r)
        return 0

    balances = r["data"]["balances"]

    if asset not in balances:
        print(f"⚠ {asset} no encontrado en balances")
        return 0

    info = balances[asset]

    # soportar cualquier formato
    available = float(info.get("available", 0) or info.get("available_balance", 0) or 0)

    return available


def get_price(symbol):
    endpoint = "/spot/market/ticker"
    params = {"market": symbol}
    r = make_request("GET", endpoint, None, None, params)
    if not r or r.get("code") != 0 or not r.get("data"):
        return None
    return float(r["data"][0]["last"])

def get_candles(symbol, timeframe="1min", limit=50):
    endpoint = "/spot/market/kline"
    params = {"market": symbol, "limit": limit, "period": timeframe}
    r = make_request("GET", endpoint, None, None, params)
    if not r or r.get("code") != 0:
        return []
    return r["data"]["klines"]

def get_spot_pairs():
    endpoint = "/spot/market/list"
    r = make_request("GET", endpoint)
    if not r or r.get("code") != 0:
        return []
    return [m["name"] for m in r["data"]]

def place_market_buy(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        return None
    api_key = keys["api_key"]
    secret_key = keys["api_secret"]
    endpoint = "/spot/order/put_market"
    params = {"market": symbol, "side": "buy", "amount": quantity}
    r = make_request("POST", endpoint, api_key, secret_key, params)
    if not r or r.get("code") != 0:
        print("❌ Error BUY:", r)
        return None
    return r["data"]

def place_market_sell(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        return None
    api_key = keys["api_key"]
    secret_key = keys["api_secret"]
    endpoint = "/spot/order/put_market"
    params = {"market": symbol, "side": "sell", "amount": quantity}
    r = make_request("POST", endpoint, api_key, secret_key, params)
    if not r or r.get("code") != 0:
        print("❌ Error SELL:", r)
        return None
    return r["data"]
