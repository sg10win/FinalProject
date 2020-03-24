import socket
import sys
from tkinter import filedialog

from cryptography.fernet import Fernet
from tkinter.filedialog import FileDialog, Tk

#str msg to bite object encryption the key is bite object
def do_encryption(key, data):
    f = Fernet(key)
    encrypted = f.encrypt(data)
    return encrypted


def do_decrypt(key, data):  # the params are byte object. return byte object
    f = Fernet(key)
    return f.decrypt(data)

def do_encrypt(key, data):  # the params are byte object. return byte object
    f = Fernet(key)
    return f.encrypt(data)

if __name__ == '__main__':

    #root = Tk()
    #root.withdraw()
    #file_path = filedialog.askopenfilename(initialdir="C:/Users/USER/PycharmProjects/Newww")
    #print("the file path: "+file_path)
    #key = Fernet.generate_key()  # generates new key (bytes object) randomly

    #s = socket.socket()
    #s.connect(("localhost",9999))
    #s.send(key)
    #print(key)

    key = b'bPrL-6eVHP82FTrBe9hNPPirr93TXu-FgucQRzcJQOE='
    data = b'gAAAAABeUlzoEAp1k-QjRsiYKyNCbjXsRyqbhOcgJJRe5JWZqGy9lhVzb2vxOHym1wFkmosNf6Gpkn1rQmagmSNQPN76IikvvQ=='

    print(do_decrypt(key, data))

key = Fernet.generate_key()#generates new key (bytes object) randomly
print(str(key.decode()))
print(key)

print(key.decode().encode())



   # f = open (file_path, "rb")
    #l = f.read(1024)
   # while (l):
    #    s.send(do_encryption(key,l))
    #    l = f.read(1024)
   # s.close()