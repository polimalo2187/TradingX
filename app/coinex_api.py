import time
import hashlib
import requests
from app.database import get_api_keys

COINEX_BASE_URL = "https://api.coinex.com/v2"


# ======================================================
# FIRMA OFICIAL CORRECTA (CoinEx V2)
# ======================================================
def sign_request(secret_key: str, method: str, endpoint: str, params: dict):
    timestamp = str(int(time.time() * 1000))

    sorted_params = "&".join(
        f"{k}={params[k]}" for k in sorted(params)
    ) if params else ""

    # ORDEN CORRECTO:
    raw = secret_key + method + endpoint + timestamp + sorted_params
    signature = hashlib.md5(raw.encode()).hexdigest()

    return signature, timestamp


# ======================================================
# REQUEST GENERAL V2
# ======================================================
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
        print("❌ Error CoinEx:", e)
        return None


# ======================================================
# BALANCE REAL
# ======================================================
def get_balance(user_id, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ No API Keys.")
        return 0

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/spot/balance/query"
    params = {}

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error en balance:", r)
        return 0

    balances = r["data"]["balances"]

    if asset not in balances:
        return 0

    info = balances[asset]

    return float(info.get("available", 0) or info.get("available_balance", 0) or 0)


# ======================================================
# MARKET BUY
# ======================================================
def place_market_buy(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ No API Keys")
        return None

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/spot/order/put_market"
    params = {
        "market": symbol,
        "side": "buy",
        "amount": quantity
    }

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error en BUY:", r)
        return None

    return r["data"]


# ======================================================
# MARKET SELL
# ======================================================
def place_market_sell(user_id, symbol, quantity):
    keys = get_api_keys(user_id)
    if not keys:
        print("❌ No API Keys")
        return None

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/spot/order/put_market"
    params = {
        "market": symbol,
        "side": "sell",
        "amount": quantity
    }

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error en SELL:", r)
        return None

    return r["data"]
