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




if __name__ == '__main__':

    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir="C:/Users/USER/PycharmProjects/Newww")
    print("the file path: "+file_path)
    key = Fernet.generate_key()  # generates new key (bytes object) randomly

    s = socket.socket()
    s.connect(("localhost",9999))
    s.send(key)
    print(key)










    f = open (file_path, "rb")
    l = f.read(1024)
    while (l):
        s.send(do_encryption(key,l))
        l = f.read(1024)
    s.close()