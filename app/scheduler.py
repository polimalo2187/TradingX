import time
import threading

from app.database import (
    users_col,
    user_is_ready
)

from app.trading_engine import trading_cycle


# =======================================
# CONTROL DE HILOS POR USUARIO
# =======================================

# Guarda qué usuarios tienen un ciclo activo
active_threads = {}


# =======================================
# EJECUTAR TRADING PARA UN USUARIO
# =======================================

def run_trading_for_user(user_id):
    """
    Ejecuta un ciclo completo de trading para un usuario
    asegurando que:
    - El usuario esté listo (API Keys, capital, activo)
    - No existan hilos duplicados
    """

    try:
        if not user_is_ready(user_id):
            print(f"⚠️ Usuario {user_id} NO está listo. Cancelando hilo…")
            active_threads.pop(user_id, None)
            return

        print(f"🚀 Ejecutando TradingX para usuario: {user_id}")

        result = trading_cycle(user_id)

        print(f"📊 Resultado del ciclo para {user_id}: {result}")

    except Exception as e:
        print(f"❌ Error ejecutando trading para {user_id}: {e}")

    finally:
        # liberar bandera del usuario (permitir siguiente ejecución)
        active_threads.pop(user_id, None)


# =======================================
# OBTENER USUARIOS ACTIVOS
# =======================================

def scan_active_users():
    """
    Retorna los user_id de los usuarios que tienen
    el trading en estado ACTIVO.
    """
    active_users = users_col.find({"status": "active"})
    return [u["user_id"] for u in active_users]


# =======================================
# CICLO PRINCIPAL DEL SCHEDULER
# =======================================

def scheduler_loop(interval_seconds=60):
    """
    Revisa cada X segundos los usuarios activos.
    Si hay oportunidades, ejecutará trading_cycle(user_id)
    pero sin duplicar hilos.
    """
    print(f"⏱ Scheduler iniciado. Intervalo: {interval_seconds}s")

    while True:
        try:
            active_users = scan_active_users()

            if not active_users:
                print("⚪ No hay usuarios activos.")
            else:
                print(f"🔎 Usuarios activos: {active_users}")

            # Lanzar hilo por usuario si no hay uno activo ya
            for user_id in active_users:
                if user_id not in active_threads:
                    th = threading.Thread(
                        target=run_trading_for_user,
                        args=(user_id,),
                        daemon=True
                    )
                    active_threads[user_id] = th
                    th.start()

        except Exception as e:
            print(f"❌ Error dentro del Scheduler: {e}")

        time.sleep(interval_seconds)


# =======================================
# INICIAR SCHEDULER EN SEGUNDO PLANO
# =======================================

def start_scheduler():
    """
    Inicia el scheduler en un hilo independiente.
    Este hilo vive aparte del bot de Telegram.
    """
    t = threading.Thread(target=scheduler_loop, args=(60,), daemon=True)
    t.start()
    print("✅ Scheduler automático iniciado en segundo plano.")
