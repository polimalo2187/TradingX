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

    # ORDEN CORRECTO SEGÚN DOCUMENTACIÓN:
    # secret + method + endpoint + timestamp + sorted_params
    raw = secret_key + method + endpoint + timestamp + sorted_params
    signature = hashlib.md5(raw.encode()).hexdigest()

    return signature, timestamp


# ======================================================
# PETICIÓN GENERAL
# ======================================================
def make_request(method, endpoint, api_key=None, secret_key=None, params=None):
    if params is None:
        params = {}

    url = COINEX_BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

    if api_key and secret_key:
        signature, timestamp = sign_request(secret_key, method, endpoint, params)
        headers.update({
            "X-COINEX-KEY": api_key,
            "X-COINEX-SIGN": signature,
            "X-COINEX-TIMESTAMP": timestamp
        })

    try:
        if method == "GET":
            r = requests.get(url, params=params, headers=headers, timeout=10)
        else:
            r = requests.post(url, json=params, headers=headers, timeout=10)

        return r.json()
    except Exception as e:
        print("❌ Error CoinEx:", e)
        return None


# ======================================================
# BALANCE REAL (CORREGIDO)
# ======================================================
def get_balance(user_id, asset="USDT"):
    keys = get_api_keys(user_id)
    if not keys:
        return 0

    api_key = keys["api_key"]
    secret_key = keys["api_secret"]

    endpoint = "/spot/balance/query"
    params = {}

    r = make_request("POST", endpoint, api_key, secret_key, params)

    if not r or r.get("code") != 0:
        print("❌ Error balance:", r)
        return 0

    balances = r["data"]["balances"]

    if asset not in balances:
        return 0

    info = balances[asset]

    return float(info.get("available", 0) or info.get("available_balance", 0) or 0)
