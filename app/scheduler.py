import time
import threading

from app.database import (
    users_col,
    user_is_ready
)

from app.trading_engine import trading_cycle


# ======================================================
# CONTROL DE HILOS POR USUARIO
# ======================================================

# Guarda qué usuarios tienen un ciclo activo
active_threads = {}


def is_thread_running(user_id):
    """
    Verifica si el hilo sigue vivo.
    Si el hilo murió inesperadamente, lo elimina del registro.
    """
    th = active_threads.get(user_id)

    if th and not th.is_alive():
        active_threads.pop(user_id, None)
        return False

    return th is not None


# ======================================================
# EJECUTAR UN CICLO DE TRADING PARA UN USUARIO
# ======================================================

def run_trading_for_user(user_id):
    """
    Ejecuta 1 ciclo completo:
    - Verifica si el usuario está listo
    - Ejecuta trading_cycle()
    - Libera el hilo al terminar
    """

    try:
        if not user_is_ready(user_id):
            print(f"⚠️ Usuario {user_id} NO está listo. Cancelando ciclo…")
            active_threads.pop(user_id, None)
            return

        print(f"🚀 Ejecutando TradingX para usuario: {user_id}")

        result = trading_cycle(user_id)

        print(f"📊 Resultado final para {user_id}: {result}")

    except Exception as e:
        print(f"❌ Error ejecutando trading para {user_id}: {e}")

    finally:
        # Siempre liberar bandera
        active_threads.pop(user_id, None)


# ======================================================
# OBTENER USUARIOS ACTIVOS
# ======================================================

def scan_active_users():
    """
    Obtiene los usuarios con trading activo.
    """
    active_users = users_col.find({"status": "active"})
    return [u["user_id"] for u in active_users]


# ======================================================
# CICLO PRINCIPAL DEL SCHEDULER
# ======================================================

def scheduler_loop(interval_seconds=60):
    """
    Cada X segundos:
    - Escanea usuarios activos
    - Lanza hilos si no están corriendo
    """
    print(f"⏱ Scheduler iniciado | Intervalo: {interval_seconds}s")

    while True:
        try:
            active_users = scan_active_users()

            if not active_users:
                print("⚪ No hay usuarios activos.")
            else:
                print(f"🔎 Usuarios activos: {active_users}")

            for user_id in active_users:

                # Verificar si el usuario SI está listo
                if not user_is_ready(user_id):
                    continue

                # Prevenir ejecuciones duplicadas
                if is_thread_running(user_id):
                    continue

                # Crear hilo nuevo
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


# ======================================================
# INICIAR SCHEDULER DESDE main.py
# ======================================================

def start_scheduler():
    """
    Inicia el scheduler en un hilo separado del bot Telegram.
    """
    t = threading.Thread(target=scheduler_loop, args=(60,), daemon=True)
    t.start()
    print("✅ Scheduler automático iniciado en segundo plano.")
