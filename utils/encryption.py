import logging
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet


def create_jwtoken(
    data: dict,
    expires_delta: timedelta,
    encode_key: str,
    algorithm: str = "HS256",
):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    logging.debug(f"JWT data: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, encode_key, algorithm)
    return encoded_jwt


class Encryption:
    def __init__(self, key):
        self.key = key
        self.fernet = Fernet(self.key)

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data):
        return self.fernet.decrypt(data).decode()
