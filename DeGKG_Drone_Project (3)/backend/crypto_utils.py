# crypto_utils.py
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# ================= KEY GENERATION =================
def derive_key(key):
    return hashlib.sha256(key.encode()).digest()  # 256-bit key

# ================= AES ENCRYPTION =================
def encrypt_data(key, text):
    key = derive_key(key)
    iv = get_random_bytes(16)  # Initialization Vector

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(text.encode(), 16))

    # Return iv + encrypted data
    return base64.b64encode(iv + encrypted).decode()

# ================= AES DECRYPTION =================
def decrypt_data(key, encrypted_text):
    key = derive_key(key)
    data = base64.b64decode(encrypted_text)

    iv = data[:16]
    encrypted = data[16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), 16)

    return decrypted.decode()
