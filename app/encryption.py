from cryptography.fernet import Fernet
import os

# =======================================
# GENERAR O CARGAR CLAVE DE ENCRIPTACIÓN
# =======================================

# La clave debe venir desde Railway (ENV)
SECRET_ENCRYPTION_KEY = os.getenv("SECRET_ENCRYPTION_KEY")

if not SECRET_ENCRYPTION_KEY:
    raise ValueError("❌ ERROR: Falta SECRET_ENCRYPTION_KEY en Railway.")

try:
    # Cargar clave válida para Fernet
    cipher = Fernet(SECRET_ENCRYPTION_KEY.encode("utf-8"))
except Exception:
    raise ValueError("❌ ERROR: La clave SECRET_ENCRYPTION_KEY NO es válida. "
                     "Debe ser generada con Fernet.generate_key().")

# =======================================
# FUNCIONES DE ENCRIPTACIÓN / DESENCRIPTACIÓN
# =======================================

def encrypt_text(text: str) -> str:
    """Encripta un texto usando AES-256 (Fernet)."""
    return cipher.encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(encrypted_text: str) -> str:
    """Desencripta texto previamente encriptado."""
    return cipher.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
