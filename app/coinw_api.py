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
