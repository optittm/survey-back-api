from cryptography.fernet import Fernet

class Encryption:
    def __init__(self, key):
        self.key = key
        self.fernet = Fernet(self.key)

    @staticmethod
    def generate_key():
        return Fernet.generate_key()
    
    def encrypt(self, data):
        return self.fernet.encrypt(data.encode())

    def decrypt(self, data):
        return self.fernet.decrypt(data).decode()
