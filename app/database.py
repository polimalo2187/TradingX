from pymongo import MongoClient
from app.config import MONGODB_URI
from app.encryption import encrypt_text, decrypt_text
import datetime

# =======================================
# CONEXIÓN PRINCIPAL A MONGO DB
# =======================================

client = MongoClient(MONGODB_URI)
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


# =======================================
# GUARDAR CAPITAL DEL USUARIO
# =======================================

def save_user_capital(user_id, capital):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"capital": capital}}
    )
    return True


# =======================================
# OBTENER CAPITAL DEL USUARIO
# =======================================

def get_user_capital(user_id):
    """
    Devuelve el capital configurado por el usuario.
    Si no existe, devuelve 0.
    """
    user = users_col.find_one({"user_id": user_id})

    if not user:
        return 0

    capital = user.get("capital", 0)

    try:
        return float(capital)
    except:
        return 0


# =======================================
# ACTIVAR TRADING PARA EL USUARIO
# =======================================

def activate_trading(user_id):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"status": "active"}}
    )
    return True


# =======================================
# DESACTIVAR TRADING PARA EL USUARIO
# =======================================

def deactivate_trading(user_id):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"status": "inactive"}}
    )
    return True


# =======================================
# OBTENER DATOS COMPLETOS DEL USUARIO
# =======================================

def get_user(user_id):
    return users_col.find_one({"user_id": user_id})


# =======================================
# VERIFICAR SI EL USUARIO ESTÁ LISTO PARA OPERAR
# =======================================

def user_is_ready(user_id):
    user = get_user(user_id)

    if not user:
        return False

    if not user.get("api_key") or not user.get("api_secret"):
        return False

    if user.get("capital", 0) <= 0:
        return False

    if user.get("status") != "active":
        return False

    return True


# =======================================
# REGISTRAR OPERACIÓN
# =======================================

def register_trade(user_id, symbol, entry_price, exit_price, qty, result):
    """
    Guarda en la base de datos una operación completada.
    result = 'tp_hit' o 'sl_hit'
    """
    profit_usdt = (exit_price - entry_price) * qty

    trade_data = {
        "user_id": user_id,
        "symbol": symbol,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "qty": qty,
        "profit_usdt": round(profit_usdt, 6),
        "result": result,
        "timestamp": datetime.datetime.utcnow()
    }

    trades_col.insert_one(trade_data)
    return trade_data


# =======================================
# OBTENER HISTORIAL COMPLETO DEL USUARIO
# =======================================

def get_user_trades(user_id):
    """
    Devuelve todas las operaciones del usuario ordenadas del más reciente al más viejo.
    """
    return list(trades_col.find({"user_id": user_id}).sort("timestamp", -1))


# =======================================
# ESTADÍSTICAS BÁSICAS DEL USUARIO
# =======================================

def get_user_stats(user_id):
    trades = get_user_trades(user_id)

    total_profit = sum(t["profit_usdt"] for t in trades)
    total_trades = len(trades)
    wins = sum(1 for t in trades if t["result"] == "tp_hit")
    losses = sum(1 for t in trades if t["result"] == "sl_hit")

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "winrate": (wins / total_trades * 100) if total_trades > 0 else 0,
        "total_profit": round(total_profit, 6)
  }
