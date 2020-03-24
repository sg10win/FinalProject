import random

import cryptography
from cryptography.fernet import Fernet


key = Fernet.generate_key()#generates new key (bytes object) randomly
print("key= "+key.decode())

file = open('key.key', 'wb')#write the key in a file
file.write(key) # The key is type bytes still
file.close()

file = open('key.key', 'rb')#reads the key
key = file.read() # The key will be type bytes
file.close()

# now encrypting msgs:
message = "secret".encode()
print('msg=',message.decode())
f = Fernet(key)
encrypted = f.encrypt(message)
print ('encrypted_msg=',encrypted.decode())
# and decrypting:
decoded_msg = f.decrypt(encrypted)
print("decoded_msg=",decoded_msg.decode())

a = "a"
a = "'"+a+"'"
print(a)

from tkinter import *
from tkinter import messagebox
from PIL import ImageTk,Image






import tkinter
import cv2
import PIL.Image, PIL.ImageTk

 # Create a window
window = tkinter.Tk()
window.title("OpenCV and Tkinter")

# Load an image using OpenCV
cv_img = cv2.cvtColor(cv2.imread("C:\\Users\\USER\\Pictures\\Saved Pictures\\Andromeda-Galaxy-Wallpaper-HD-05.jpg"), cv2.COLOR_BGR2RGB)

# Get the image dimensions (OpenCV stores image data as NumPy ndarray)
height, width, no_channels = cv_img.shape
# Create a canvas that can fit the above image
canvas = tkinter.Canvas(window, width = width, height = height)
canvas.pack()

# Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv_img))

# Add a PhotoImage to the Canvas
canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
# Run the window loop
window.mainloop()
# importing only those functions
# which are needed
from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk

# creating tkinter window
root = Tk()
root.geometry("500x500")
frame = Frame(root)
frame.pack()

image = Image.open(r"C:\Users\USER\Pictures\Saved Pictures\Andromeda-Galaxy-Wallpaper-HD-05.jpg")
image_copy = image.copy().resize((500,500), Image.ANTIALIAS)
bacround_img = ImageTk.PhotoImage(image_copy)
lbl = Label(frame, image=bacround_img)
btn = Button(lbl, text="brobondy")

btn.grid(row=0, column=0)
lbl.pack()




root.mainloop()
