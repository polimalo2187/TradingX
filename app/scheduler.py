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


# =======================================
# CICLO AUTOMÁTICO DEL SCHEDULER
# =======================================

def scheduler_loop(interval_seconds=60):
    """
    Ejecuta trading automático cada X segundos.
    60s = 1 minuto (ideal para estrategias rápidas).
    """

    print(f"⏱ Iniciando scheduler automático cada {interval_seconds} segundos...")

    while True:
        active_users = scan_active_users()

        if not active_users:
            print("⚪ No hay usuarios activos para operar.")
        else:
            print(f"🔎 Usuarios activos: {active_users}")

        # Ejecutar ciclo de trading para cada usuario
        for user_id in active_users:
            threading.Thread(target=run_trading_for_user, args=(user_id,)).start()

        time.sleep(interval_seconds)


# =======================================
# INICIAR SCHEDULER EN UN HILO SEPARADO
# =======================================

def start_scheduler():
    """
    Inicia el scheduler en segundo plano.
    Railway puede correrlo junto con el bot de Telegram.
    """

    t = threading.Thread(target=scheduler_loop, args=(60,))
    t.daemon = True
    t.start()

    print("✅ Scheduler automático iniciado en segundo plano.")
