from cryptography.fernet import Fernet
import base64
import os

# =======================================
# GENERAR O CARGAR CLAVE DE ENCRIPTACIÓN
# =======================================

# La clave debe venir desde Railway (variable ENV)
SECRET_ENCRYPTION_KEY = os.getenv("SECRET_ENCRYPTION_KEY")

if not SECRET_ENCRYPTION_KEY:
    raise ValueError("❌ ERROR: Falta SECRET_ENCRYPTION_KEY en las variables de entorno.")

# Convertir la clave a formato válido para Fernet
key = base64.urlsafe_b64encode(SECRET_ENCRYPTION_KEY.encode("utf-8"))
cipher = Fernet(key)

# =======================================
# FUNCIONES DE ENCRIPTACIÓN Y DESENCRIPTACIÓN
# =======================================

def encrypt_text(text: str) -> str:
    """Encripta un string usando AES-256 (Fernet)."""
    encrypted = cipher.encrypt(text.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_text(encrypted_text: str) -> str:
    """Desencripta un string encriptado."""
    decrypted = cipher.decrypt(encrypted_text.encode("utf-8"))
    return decrypted.decode("utf-8")
