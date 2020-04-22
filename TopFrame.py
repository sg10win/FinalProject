from tkinter import *
from tkinter import messagebox




class TopFrameObject():

    def __init__(self, client):
        self.client = client

    # this function is for the info button
    def chat_info_request(self):
        # TODO here I can make a better graphics option then to desplay it on the textbox

        # for now i write the info in the textbox
        self.client.disable()
        msg = "chat info%%%"+f"{self.client.current_external_id}"
        self.client.messages_to_send.append(msg)
        self.client.send_messages()
        print("done")

    def exit_chat(self):
        # starts with a warning msg
        ans = messagebox.askokcancel("IChat", "Are you sure you want to leave this chat?")
        if ans:
            msg = f"exit chat%%%{self.client.username}%%%{self.client.current_external_id}%%%{self.client.current_id}"
            self.client.messages_to_send.append(msg)
            self.client.send_messages()
            self.client.text_box.config(state=NORMAL)
            self.client.text_box.delete(1.0, END)
            self.client.text_box.config(state=DISABLED)
            print("done")
            button = self.client.button_by_id(self.client.current_id)
            # the buttons and the frames of them organized that way they have the same index

            try :
                index = self.client.buttons.index(button)
                self.client.button_frames[index].pack_forget()
                self.client.buttons.remove(button)
                self.client.button_frames.remove(self.client.button_frames[index])
            except:
                raise ("this button not in buttons list it is maybe public_chat_button and it is undeleteable")

            self.client.current_id = "public"
            self.client.current_external_id = "public"
            self.client.chat_info_button.configure(text="PUBLIC")

    def link_user_to_chat(self):
        root = Tk()
        frame = Frame(root)
        entry = Entry(frame)
        entry.pack(side=LEFT)
        link_btn = Button(frame, text="link", command=lambda: self.send_the_link_msg(entry))
        link_btn.pack(side=RIGHT)
        frame.pack(side=TOP)
        mainloop()

    def send_the_link_msg(self, entry):
        username_to_link = entry.get()
        if username_to_link:
            chat_external_id = self.client.current_external_id
            manager_chat_id = self.client.current_id
            msg = f"new link%%%{chat_external_id}%%%{manager_chat_id}%%%{username_to_link}"
            self.client.messages_to_send.append(msg)
            self.client.send_messages()
            print(f'{msg}')