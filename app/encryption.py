from cryptography.fernet import Fernet
import os

# =======================================
# CARGAR CLAVE DE ENCRIPTACIÓN DESDE ENV
# =======================================

SECRET_ENCRYPTION_KEY = os.getenv("SECRET_ENCRYPTION_KEY")

if not SECRET_ENCRYPTION_KEY:
    raise ValueError(
        "❌ ERROR FATAL: Falta SECRET_ENCRYPTION_KEY en variables de entorno.\n"
        "Debes generar una clave con Fernet.generate_key() y ponerla en Railway."
    )

try:
    cipher = Fernet(SECRET_ENCRYPTION_KEY.encode("utf-8"))
except Exception:
    raise ValueError(
        "❌ ERROR FATAL: SECRET_ENCRYPTION_KEY no es válida.\n"
        "Debe ser una clave generada por Fernet.generate_key()."
    )

# =======================================
# FUNCIONES DE ENCRIPTACIÓN
# =======================================

def encrypt_text(text: str) -> str:
    """
    Encripta un texto usando AES-256 (Fernet).
    Devuelve texto seguro en formato string.
    """
    return cipher.encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(encrypted_text: str) -> str:
    """
    Desencripta texto previamente encriptado.
    Maneja cualquier error de descifrado.
    """
    return cipher.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
