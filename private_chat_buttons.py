import time
from tkinter import Button
from tkinter import *



class PrivateChatButton(Button):

    def __init__(self, root, chat_name, chat_id, external_id, client):
        Button.__init__(self, root, text=chat_name, command=lambda: self.chat_request(), width=10)
        self.client = client
        self.chat_name = chat_name
        self.chat_id = str(chat_id)
        self.external_id = str(external_id)
        self.new_msgs = 0
        print(f"button id={self.chat_id}")


    def chat_request(self):
        # FIRST THE ID AND THAN THE EXTERNAL
        msg = f"chat request%%%{self.chat_id}%%%{self.external_id}"
        print(f"I want to get the chat id ={self.chat_id}")
        self.configure(bg="SystemButtonFace")
        self.client.messages_to_send.append(msg)
        self.client.send_messages()
        self.client.current_id = self.chat_id
        self.client.current_external_id = self.external_id
        self.client.text_box.config(state=NORMAL)
        self.client.text_box.delete(1.0, END)
        self.client.text_box.config(state=DISABLED)

    def new_msg_arrived(self):
        self.configure(bg="green2")
        time.sleep(0.25)
        self.configure(bg="yellow2")
        time.sleep(0.25)
        self.configure(bg="green2")

