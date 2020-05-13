from cryptography.fernet import Fernet


class Encryption(object):
    @staticmethod
    def encrypt(data, key):
        f = Fernet(key)
        if isinstance(data, str):
            data = data.encode()
        return f.encrypt(data)

    @staticmethod
    def decrypt(data, key):
        f = Fernet(key)
        if isinstance(data, str):
            data = data.encode()
        return f.decrypt(data)
