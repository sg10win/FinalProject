import tkinter as tk
from PIL import Image
import os

def execute_file(file_name):
    os.startfile(file_name)

def add_image():
    #text.image_create(tk.END, image = img) # Example 1
    text.window_create(tk.END, window = tk.Button(text, image = img, command=lambda: execute_file("Andromeda-Galaxy.gif"))) # Example 2


    text.insert(1.0,"new image", tk.END)

root = tk.Tk()

text = tk.Text(root)
text.pack(padx = 2, pady = 2)

tk.Button(root, text = "Insert", command = add_image).pack()

img = tk.PhotoImage(file = "Andromeda-Galaxy1.gif")

basewidth = 300
img2 = Image.open('Andromeda-Galaxy.gif')
wpercent = (basewidth / float(img2.size[0]))
hsize = int((float(img2.size[1]) * float(wpercent)))
img2 = img2.resize((basewidth, hsize), Image.ANTIALIAS)
img2.save('Andromeda-Galaxy1.gif')
root.mainloop()