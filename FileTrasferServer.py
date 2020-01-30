import socket
from tkinter import filedialog
from tkinter import *
import sys
from tkinter.filedialog import FileDialog
import sys
from cryptography.fernet import Fernet


def do_decryption(key,data):
    f = Fernet(key)
    decoded_data = f.decrypt(data)
    return decoded_data


s = socket.socket()
s.bind(("localhost",9999))
s.listen(10) # Acepta hasta 10 conexiones entrantes.
sc, address = s.accept()

print (address)

key = sc.recv(1024) #byte object
print(key)
i=1
f = open('C:/Users/USER/PycharmProjects/Newww/transfered/file_'+ str(i)+".jpeg",'wb') # Open in binary
i=i+1


while (True):

    # Recibimos y escribimos en el fichero
    global l
    l = sc.recv(1024)
    while (l):

        f.write(do_decryption(key, l))
        l = sc.recv(1024)
f.close()

sc.close()
s.close()
sys.exit()