import cryptography
from cryptography.fernet import Fernet


key = Fernet.generate_key()#generates new key (bytes object) randomly
print(key.decode())

file = open('key.key', 'wb')#write the key in a file
file.write(key) # The key is type bytes still
file.close()

file = open('key.key', 'rb')#reads the key
key = file.read() # The key will be type bytes
file.close()


# now encrypting msgs:
message = "secret".encode()
print('msg= ',message.decode())
f = Fernet(key)
encrypted = f.encrypt(message)
print ('encrypted= ',encrypted.decode())
# and decrypting:
decoded_msg = f.decrypt(encrypted)
print("decoded_msg= ",decoded_msg.decode())

def do_decrypt(key, data): # the params are byte object. return byte object
    f = Fernet(key)
    return f.decrypt(data)
def do_encrypt(key, data): # the params are byte object. return byte object
    f = Fernet(key)
    return f.encrypt(data)


print("-----------------------------")
data = "10".encode()
key = Fernet.generate_key()#generates new key (bytes object) randomly
print("key= ",key)
encrypt = do_encrypt(key, data)
print("encrypt= ", encrypt)
decrypt = do_decrypt(key, encrypt)
print("decrypt", decrypt)
print('------------------------------')


