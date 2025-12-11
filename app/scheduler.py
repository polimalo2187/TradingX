import time
import threading

from app.database import users_col, get_api_keys, get_user, user_is_ready
from app.trading_engine import trading_cycle


# =======================================
# EJECUTAR TRADING PARA UN USUARIO
# =======================================

def run_trading_for_user(user_id):
    """
    Ejecuta un ciclo de trading para un usuario específico
    si su cuenta está lista.
    """

    if not user_is_ready(user_id):
        print(f"⚠️ Usuario {user_id} no está listo para operar.")
        return

    print(f"🚀 Ejecutando ciclo de TradingX para usuario {user_id}...")
    result = trading_cycle()

    print(f"📊 Resultado para {user_id}: {result}")


# =======================================
# EJECUTAR TRADING PARA TODOS LOS USUARIOS ACTIVOS
# =======================================

def scan_active_users():
    """
    Busca todos los usuarios con trading activo.
    """

    active_users = users_col.find({"status": "active"})

    return [u["user_id"] for u in active_users]
