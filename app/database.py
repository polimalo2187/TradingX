from pymongo import MongoClient
from app.config import MONGO_URI
from app.encryption import encrypt_text, decrypt_text
import datetime


# ======================================================
# CONEXIÓN A MONGO DB
# ======================================================

client = MongoClient(MONGO_URI)
db = client["TradingX_Database"]

users_col = db["users"]
trades_col = db["trades"]


# ======================================================
# CREAR USUARIO
# ======================================================

def create_user(user_id, username):
    user = users_col.find_one({"user_id": user_id})

    if user:
        return user

    new_user = {
        "user_id": user_id,
        "username": username,
        "api_key": None,
        "api_secret": None,
        "capital": 0.0,
        "status": "inactive",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }

    users_col.insert_one(new_user)
    return new_user


# ======================================================
# GUARDAR API KEYS (ENCRIPTADAS)
# ======================================================

def save_api_keys(user_id, api_key, api_secret):
    encrypted_key = encrypt_text(api_key)
    encrypted_secret = encrypt_text(api_secret)

    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "api_key": encrypted_key,
                "api_secret": encrypted_secret,
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    return True


# ======================================================
# OBTENER API KEYS (DESENCRIPTADAS)
# ======================================================

def get_api_keys(user_id):
    user = users_col.find_one({"user_id": user_id})

    if not user or not user.get("api_key"):
        return None

    try:
        return {
            "api_key": decrypt_text(user["api_key"]),
            "api_secret": decrypt_text(user["api_secret"])
        }

    except Exception:
        # Si falla desencriptación, borrar para evitar API corrupta
        users_col.update_one(
            {"user_id": user_id},
            {"$set": {"api_key": None, "api_secret": None}}
        )
        return None


# ======================================================
# GUARDAR CAPITAL
# ======================================================

def save_user_capital(user_id, capital):
    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "capital": float(capital),
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    return True


# ======================================================
# OBTENER CAPITAL
# ======================================================

def get_user_capital(user_id):
    user = users_col.find_one({"user_id": user_id})
    if not user:
        return 0.0

    try:
        return float(user.get("capital", 0))
    except:
        return 0.0


# ======================================================
# ACTIVAR / DESACTIVAR TRADING
# ======================================================

def activate_trading(user_id):
    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "status": "active",
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    return True


def deactivate_trading(user_id):
    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "status": "inactive",
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    return True


# ======================================================
# OBTENER USUARIO COMPLETO
# ======================================================

def get_user(user_id):
    return users_col.find_one({"user_id": user_id})


# ======================================================
# VERIFICAR SI EL USUARIO ESTÁ LISTO PARA OPERAR
# ======================================================

def user_is_ready(user_id):
    user = get_user(user_id)

    if not user:
        return False

    if not user.get("api_key") or not user.get("api_secret"):
        return False

    if float(user.get("capital", 0)) < 5:
        return False

    # ❗ Eliminamos validación de status,
    # porque 'active' se establece DESPUÉS de esta validación
    return True


# ======================================================
# REGISTRAR OPERACIÓN
# ======================================================

def register_trade(user_id, symbol, entry_price, exit_price, qty, result):
    profit_usdt = (exit_price - entry_price) * qty

    trade = {
        "user_id": user_id,
        "symbol": symbol,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "qty": qty,
        "profit_usdt": round(profit_usdt, 6),
        "result": result,
        "timestamp": datetime.datetime.utcnow()
    }

    trades_col.insert_one(trade)
    return trade


# ======================================================
# HISTORIAL
# ======================================================

def get_user_trades(user_id):
    return list(trades_col.find({"user_id": user_id}).sort("timestamp", -1))


# ======================================================
# ESTADÍSTICAS DEL USUARIO
# ======================================================

def get_user_stats(user_id):
    trades = get_user_trades(user_id)

    total_profit = sum(t["profit_usdt"] for t in trades)
    total_trades = len(trades)
    wins = sum(1 for t in trades if t["result"] == "tp_hit")
    losses = sum(1 for t in trades if t["result"] == "sl_hit")

    winrate = (wins / total_trades * 100) if total_trades > 0 else 0

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2),
        "total_profit": round(total_profit, 6)
}
