import time
from tkinter import Button
from tkinter import *



class PrivateChatButton(Button):

    def __init__(self, root, chat_name, chat_id, external_id, contacts, new_msgs, is_private, client):#todo to add new_msgs parameter to this function
        self.font = client.font
        Button.__init__(self, root, text=chat_name,font=self.font, command=lambda: self.chat_request(), width=18 ,bg="gray99" ,relief=FLAT)
        self.client = client
        self.chat_name = chat_name
        self.chat_id = str(chat_id)
        self.external_id = str(external_id)
        self.contacts = contacts.split(',')
        self.new_msgs = int(new_msgs)
        self.is_private = is_private
        if self.new_msgs != 0:
            print(f"in the boo if, new_msgs = {new_msgs}")
            self.new_msg_arrived()
            self.new_msgs = self.new_msgs-1



    def chat_request(self):
        # FIRST THE ID AND THAN THE EXTERNAL
        msg = f"chat request+*!?{self.chat_id}+*!?{self.external_id}"
        self.client.mode = "ENABLE"
        if self.client.last_right_frame:
            self.client.right_frame.pack_forget()
            self.client.last_right_frame.pack(fill=BOTH, expand=True)
            self.client.right_frame = self.client.last_right_frame
        self.configure(bg="gray99")
        self.client.chat_info_button.configure(text=self.chat_name)
        self.new_msgs = 0
        self.client.messages_to_send.append(msg)
        self.client.current_id = self.chat_id
        self.client.current_external_id = self.external_id
        self.client.current_chat_name = self.chat_name
        self.client.text_box.config(state=NORMAL)
        self.client.text_box.delete(1.0, END)
        self.client.text_box.config(state=DISABLED)
        self.client.file_button.config(state=NORMAL)
        self.client.emoji_button.config(state=NORMAL)
        self.client.add_chat_contact.config(state=NORMAL)
        self.client.exit_chat.config(state=NORMAL)
        self.client.link_chat.config(state=NORMAL)
        if self.is_private == '1':
            self.client.add_chat_contact.config(state=DISABLED)
            self.client.exit_chat.config(state=DISABLED)
            self.client.link_chat.config(state=DISABLED)

    def new_msg_arrived(self):
        self.configure(bg="green2")
        time.sleep(0.12)
        self.configure(bg="yellow2")
        time.sleep(0.12)
        self.configure(bg="green2")
        self.new_msgs += 1
