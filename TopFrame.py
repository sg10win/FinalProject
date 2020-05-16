from tkinter import *
from tkinter import messagebox




class TopFrameObject(object):

    def __init__(self, client):
        self.client = client

    # this function is for the info button
    def chat_info_request(self):
        if self.client.current_id == "public":
            public_chat_info_msg = "This is a public chat.\nAll the system's clients can get and send msgs here"
            self.client.text_box.config(state=NORMAL)
            self.client.text_box.delete(1.0, END)
            self.client.text_box.insert(END, public_chat_info_msg+'\n')
            self.client.text_box.config(state=DISABLED)
            self.client.mode = "DISABLE"
            return
        self.client._disable()
        msg = "chat info+*!?"+f"{self.client.current_id}"
        self.client.messages_to_send.append(msg)
        #self.client.send_messages()
        print("done")

    def exit_chat(self):
        # starts with a warning msg
        ans = messagebox.askokcancel("IChat", "Are you sure you want to leave this chat?")
        if ans:
            msg = f"exit chat+*!?{self.client.username}+*!?{self.client.current_external_id}+*!?{self.client.current_id}"
            self.client.messages_to_send.append(msg)
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
        root.config(bg=self.client.tl_bg2)
        title = Label(root, text="link contact", bg=self.client.tl_bg, font=self.client.font, fg=self.client.tl_fg)
        title.pack(side=TOP)
        frame = Frame(root, bg=self.client.tl_bg2)
        frame.pack(side=TOP)
        entry = Entry(frame)
        entry.pack(side=RIGHT)
        label = Label(frame, text="enter contact", bg=self.client.tl_bg, font=self.client.font, fg=self.client.tl_fg)
        label.pack(side=LEFT)
        add_btn = Button(root, relief=FLAT, bg="green2", text="link", command=lambda: self.send_the_link_msg(entry, root))
        cancel_btn = Button(root, text="cancel", relief=FLAT, bg='red', command=lambda: self.cancel(root))
        add_btn.pack(side=RIGHT)
        cancel_btn.pack(side=LEFT)


    def send_the_link_msg(self, entry, root):
        username_to_link = entry.get()
        print(username_to_link)
        if username_to_link and self.client.current_id != 'public':
            chat_external_id = self.client.current_external_id
            manager_chat_id = self.client.current_id
            msg = f"new link+*!?{chat_external_id}+*!?{manager_chat_id}+*!?{username_to_link}"
            self.client.messages_to_send.append(msg)
            print(f'{msg}')
            root.destroy()


    def add_contact_to_chat(self):
        root = Tk()
        root.config(bg=self.client.tl_bg2)
        title = Label(root, text="Add contact", bg=self.client.tl_bg, font=self.client.font, fg=self.client.tl_fg)
        title.pack(side=TOP)
        frame = Frame(root, bg=self.client.tl_bg2)
        frame.pack(side=TOP)
        entry = Entry(frame)
        entry.pack(side=RIGHT)
        label = Label(frame,text="enter contact", bg=self.client.tl_bg, font=self.client.font, fg=self.client.tl_fg)
        label.pack(side=LEFT)
        add_btn = Button(root, text="add", relief=FLAT, bg="green2", command=lambda: self.add(entry, root))
        cancel_btn = Button(root, text="cancel", relief=FLAT, bg='red', command=lambda: self.cancel(root))
        add_btn.pack(side=RIGHT)
        cancel_btn.pack(side=LEFT)

    def add(self, entry, root):
        contact = entry.get()
        if contact == "" or contact is None:
            return
        msg = f"add_contact+*!?{self.client.username}+*!?{self.client.current_id}+*!?{contact}"
        self.client.messages_to_send.append(msg)
        print(msg)
        root.destroy()

    @staticmethod
    def cancel(root):
        root.destroy()