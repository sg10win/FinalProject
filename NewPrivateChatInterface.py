import time
from tkinter import *


class NewPrivateChatInterface(object):

    def __init__(self, client):
        self.client = client
        self.last_frame = None
        self.tl_bg = client.tl_bg
        self.tl_bg2 = client.tl_bg2
        self.tl_fg = client.tl_fg
        self.font = client.font
        self.entry = None
        self.root = Frame(self.client.master)
        self.new_private_chat()

    def new_private_chat(self):
        # to make it better
        self.client.mode = "DISABLE"
        self.last_frame = self.client.chat_frame
        self.client.last_right_frame = self.last_frame
        self.client.right_frame = self.root
        self.last_frame.pack_forget()
        frame = Frame(self.root, bg=self.tl_bg)
        title_l = Label(self.root, text="New private chat", font=(self.font, 16), bg=self.tl_bg, fg=self.tl_fg)
        self.entry = Entry(frame, font=self.font)
        create_button = Button(frame, text='Create', relief=FLAT, bg="green2",
                               command=lambda: self.create_private_chat_group())
        cancel_button = Button(frame, text='Cancel', relief=FLAT, bg='red', command=lambda: self.cancel())
        label = Label(frame, text='Enter contact', bg=self.tl_bg, fg=self.tl_fg)

        # title_l.pack(side=TOP)
        # create_button.pack(side=TOP)
        # label.pack(side=TOP)
        # self.entry.pack(side=TOP)
        # cancel_button.pack(side=TOP)

        label.grid(row=1, column=0)
        self.entry.grid(row=1, column=1)

        title_l.grid(sticky="new")
        frame.grid(sticky="ew")
        cancel_button.grid(row=2, column=0)
        create_button.grid(row=2, column=1)

        self.root.pack()

    def create_private_chat_group(self):
        user_to_add = self.entry.get()
        if user_to_add and not '':
            msg = f'create private chat+*!?{self.client.username}+*!?{user_to_add}'
            self.client.messages_to_send.append(msg)
            self.cancel()

    def cancel(self):
        self.client.is_chat_time = True
        self.client.right_frame = self.last_frame
        self.root.pack_forget()
        self.last_frame.pack(fill=BOTH, expand=True)
        self.client.text_box.configure(state=NORMAL)
        self.client.text_box.delete(1.0, END)
        self.client.text_box.configure(state=DISABLED)
