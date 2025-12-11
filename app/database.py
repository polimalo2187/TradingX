from pymongo import MongoClient
from app.config import MONGO_URI
from app.encryption import encrypt_text, decrypt_text


# =======================================
# CONEXIÓN PRINCIPAL A MONGO DB
# =======================================

client = MongoClient(MONGO_URI)
db = client["TradingX_Database"]

# Colecciones principales
users_col = db["users"]
trades_col = db["trades"]


# =======================================
# CREAR USUARIO
# =======================================

def create_user(user_id, username):
    """
    Crea un usuario nuevo en la base de datos.
    Evita duplicados.
    """
    exists = users_col.find_one({"user_id": user_id})

    if exists:
        return exists

    user_data = {
        "user_id": user_id,
        "username": username,
        "api_key": None,
        "api_secret": None,
        "capital": 0,
        "status": "inactive"  # inactive / active
    }

    users_col.insert_one(user_data)
    return user_data


# =======================================
# GUARDAR API KEYS ENCRIPTADAS
# =======================================

def save_api_keys(user_id, api_key, api_secret):
    encrypted_key = encrypt_text(api_key)
    encrypted_secret = encrypt_text(api_secret)

    users_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "api_key": encrypted_key,
            "api_secret": encrypted_secret
        }}
    )

    return True


# =======================================
# OBTENER API KEYS (DESENCRIPTADAS)
# =======================================

def get_api_keys(user_id):
    user = users_col.find_one({"user_id": user_id})

    if not user or not user["api_key"]:
        return None

    return {
        "api_key": decrypt_text(user["api_key"]),
        "api_secret": decrypt_text(user["api_secret"])
    }
