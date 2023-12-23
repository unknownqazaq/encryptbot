# encryption_utils.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

def encrypt(text, key):
    cipher = AES.new(key.to_bytes(16, byteorder='big'), AES.MODE_CBC)

    plaintext = text.encode('utf-8')
    plaintext = pad(plaintext, AES.block_size)

    ciphertext = cipher.encrypt(plaintext)

    ciphertext_base64 = base64.b64encode(cipher.iv + ciphertext).decode('utf-8')
    return ciphertext_base64

def decrypt(ciphertext, key):
    ciphertext = base64.b64decode(ciphertext)

    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]

    cipher = AES.new(key.to_bytes(16, byteorder='big'), AES.MODE_CBC, iv)

    decrypted_text = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
    return decrypted_text
