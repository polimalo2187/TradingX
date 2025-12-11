import time
import hashlib
import requests
import hmac
import json
from app.config import COINW_API_KEY, COINW_SECRET_KEY, COINW_BASE_URL


# ================================
# FUNCIÓN DE FIRMA PARA COINW SPOT
# ================================

def sign_request(params: dict) -> dict:
    """
    Firma las solicitudes para CoinW usando HMAC SHA256.
    """
    timestamp = str(int(time.time() * 1000))
    params["timestamp"] = timestamp

    # Convertir diccionario en formato "clave=valor&clave=valor"
    query_string = "&".join([f"{k}={params[k]}" for k in sorted(params)])

    # Crear firma
    signature = hmac.new(
        COINW_SECRET_KEY.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    params["signature"] = signature
    return params


# ================================
# SOLICITUD HTTP A COINW
# ================================

def make_request(method: str, endpoint: str, params=None):
    """
    Realiza solicitudes HTTP a CoinW.
    """
    if params is None:
        params = {}

    url = COINW_BASE_URL + endpoint

    headers = {
        "X-COINW-APIKEY": COINW_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=5)
        else:
            response = requests.post(url, headers=headers, data=json.dumps(params), timeout=5)

        return response.json()

    except Exception as e:
        print(f"❌ Error de conexión con CoinW: {e}")
        return None

    # ========================================
# OBTENER TODOS LOS PARES DISPONIBLES SPOT
# ========================================

def get_spot_pairs():
    """
    Devuelve una lista de pares disponibles en CoinW Spot.
    """
    endpoint = "/api/v1/public/symbol/list"
    response = make_request("GET", endpoint)

    if not response or response.get("code") != 0:
        print("❌ No se pudieron obtener los pares de Spot.")
        return []

    return [item["symbol"] for item in response["data"]]


# ========================================
# OBTENER PRECIO ACTUAL DE UN PAR
# ========================================

def get_price(symbol: str):
    """
    Obtiene el precio actual del par solicitado.
    """
    endpoint = "/api/v1/public/market/ticker"
    params = {"symbol": symbol}

    response = make_request("GET", endpoint, params)

    if not response or response.get("code") != 0:
        print(f"❌ No se pudo obtener el precio de {symbol}")
        return None

    return float(response["data"]["lastPrice"])


# ========================================
# OBTENER VELAS (CANDLESTICKS)
# ========================================

def get_candles(symbol: str, timeframe="1min", limit=50):
    """
    Obtiene velas para análisis técnico.
    timeframes válidos: 1min, 3min, 5min, 15min, etc.
    """
    endpoint = "/api/v1/public/market/kline"

    params = {
        "symbol": symbol,
        "limit": limit,
        "type": timeframe
    }

    response = make_request("GET", endpoint, params)

    if not response or response.get("code") != 0:
        print(f"❌ Error al obtener velas de {symbol}")
        return []

    # Formato CoinW: [timestamp, open, high, low, close, volume]
    return response["data"]


# ========================================
# VALIDAR SI UN PAR EXISTE EN SPOT
# ========================================

def pair_exists(symbol: str):
    """
    Valida si el par existe en CoinW Spot.
    """
    pairs = get_spot_pairs()
    return symbol in pairs
