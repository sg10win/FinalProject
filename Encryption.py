from cryptography.fernet import Fernet


class Encryption(object):
    @staticmethod
    def encrypt(data, key):
        f = Fernet(key)
        # print(f.encrypt(data.encode()))
        if isinstance(data, str):
            data = data.encode()
        return f.encrypt(data)

    @staticmethod
    def decrypt(data, key):
        f = Fernet(key)
        return f.decrypt(data)
