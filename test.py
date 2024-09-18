from cryptography.fernet import Fernet

from src.auth.config import config

token = "123"
f = Fernet(config.CRYPT_KEY)

encrypt_token = f.encrypt(token.encode("utf-8"))
print(f"\nЗашифрованный Токен: {encrypt_token}\n")


decrypted_token = f.decrypt(encrypt_token)

print("Расшифрованный Токен:", decrypted_token.decode("utf-8"))
