import time
import threading

from app.database import users_col, get_api_keys, get_user, user_is_ready
from app.trading_engine import trading_cycle

# =======================================
# CONTROL DE HILOS POR USUARIO
# =======================================

active_threads = {}  # evita lanzar múltiples hilos por usuario


# =======================================
# EJECUTAR TRADING PARA UN USUARIO
# =======================================

def run_trading_for_user(user_id):
    """
    Ejecuta un ciclo de trading para un usuario específico
    si su cuenta está lista y no tiene hilos duplicados.
    """

    try:
        if not user_is_ready(user_id):
            print(f"⚠️ Usuario {user_id} no está listo para operar.")
            active_threads.pop(user_id, None)
            return

        print(f"🚀 Ejecutando ciclo de TradingX para usuario {user_id}...")

        # PASAR user_id al motor de trading
        result = trading_cycle(user_id)

        print(f"📊 Resultado para usuario {user_id}: {result}")

    except Exception as e:
        print(f"❌ Error ejecutando trading para {user_id}: {e}")

    finally:
        # liberar usuario para permitir siguiente ciclo
        active_threads.pop(user_id, None)


# =======================================
# OBTENER USUARIOS ACTIVOS
# =======================================

def scan_active_users():
    """
    Devuelve lista de usuarios con trading activado.
    """
    active_users = users_col.find({"status": "active"})
    return [u["user_id"] for u in active_users]


# =======================================
# CICLO DEL SCHEDULER
# =======================================

def scheduler_loop(interval_seconds=60):
    """
    Ejecuta trading automático cada X segundos.
    60s recomendado para análisis en velas de 1m.
    """

    print(f"⏱ Scheduler automático cada {interval_seconds} segundos iniciado...")

    while True:
        try:
            active_users = scan_active_users()

            if not active_users:
                print("⚪ No hay usuarios activos.")
            else:
                print(f"🔎 Usuarios activos: {active_users}")

            # Ejecutar ciclo de trading por cada usuario
            for user_id in active_users:
                if user_id not in active_threads:
                    t = threading.Thread(target=run_trading_for_user, args=(user_id,), daemon=True)
                    active_threads[user_id] = t
                    t.start()

        except Exception as e:
            print(f"❌ Error dentro del Scheduler: {e}")

        time.sleep(interval_seconds)


# =======================================
# INICIAR SCHEDULER EN SEGUNDO PLANO
# =======================================

def start_scheduler():
    """Lanza el scheduler en un hilo independiente."""
    t = threading.Thread(target=scheduler_loop, args=(60,), daemon=True)
    t.start()
    print("✅ Scheduler automático iniciado en segundo plano.")
