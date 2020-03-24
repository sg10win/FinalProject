from tkinter import Button
from tkinter import *



class PrivateChatButton(Button):

    def __init__(self, root, chat_name, id, external_id, client):
        Button.__init__(self, root, text=chat_name, command=lambda: self.chat_request(), width=10)
        self.client = client
        self.chat_name = chat_name
        self.id = str(id)
        self.external_id = str(external_id)


    def chat_request(self):
        # FIRST THE ID AND THAN THE EXTERNAL
        msg = f"chat request%%%{self.id}%%%{self.external_id}"
        self.client.messages_to_send.append(msg)
        self.client.send_messages()
        self.client.current_id = self.id
        self.client.current_external_id = self.external_id
        self.client.text_box.config(state=NORMAL)
        self.client.text_box.delete(1.0, END)
        self.client.text_box.config(state=DISABLED)


