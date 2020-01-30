from tkinter import *
import os
import socket
import hashlib
import sqlite3
import time
import select
from queue import Queue
from threading import *


conn_q = Queue()
gui_q = Queue()


class Client():
    def __init__(self, roots):
        self.roots = roots
        self.messages = []
        self.wlist = []
        self.username = ""
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect(("127.0.0.1", 8080))
        print('Connected to server')

    def get_roots(self):
        return self.roots

    def Signup(self, roots):  # This is the signup definition,
        global emailE
        global pwordE  # These globals just make the variables global to the entire script, meaning any definition can use them
        global re_pwordE
        global nameE

        self.delete_all_in_root(roots)
        # This creates the window, just a blank one.
        roots.geometry('360x185')
        roots.resizable(width=False, height=False)
        roots.title('Signup')  # This renames the title of said window to 'signup'
        intruction = Label(roots,
                           text='Please signup\n')  # This puts a label, so just a piece of text saying 'please enter blah'
        intruction.grid(row=0, column=0,
                        sticky=E)  # This just puts it in the window, on row 0, col 0. If you want to learn more look up a tkinter tutorial :)
        emailL = Label(roots, text='Email: ')  # This just does the same as above, instead with the text new username.
        nameL = Label(roots, text='Username: ')  # This just does the same as above, instead with the text new username.
        pwordL = Label(roots, text='Password: ')  # ^^
        re_pwordL = Label(roots, text="Re-Password: ")
        emailL.grid(row=1, column=0,
                    sticky=W)  # Same thing as the instruction var just on different rows. :) Tkinter is like that.
        nameL.grid(row=2, column=0, sticky=W)  # ^^
        pwordL.grid(row=3, column=0, sticky=W)  # ^^
        re_pwordL.grid(row=4, column=0, sticky=W)

        emailE = Entry(roots, width=30)  # This now puts a text box waiting for input.
        nameE = Entry(roots, width=30)  # ^^
        pwordE = Entry(roots, show='*',
                       width=30)  # Same as above, yet 'show="*"' What this does is replace the text with *, like a password box :D
        re_pwordE = Entry(roots, show='*', width=30)  # ^^
        emailE.grid(row=1, column=1)
        nameE.grid(row=2, column=1)  # You know what this does now :D
        pwordE.grid(row=3, column=1)  # ^^
        re_pwordE.grid(row=4, column=1)
        print("befor")

        submit_Button = Button(roots, text='submit', width=25, bg="DodgerBlue2",
                               command=lambda: self.chack_Signup(
                                   roots))  # This creates the button with the text 'signup', when you click it, the command 'fssignup' will run. which is the def
        print("after")
        submit_Button.grid(row=5, column=1, sticky="e")
        loginB = Button(roots, text='Login',
                        command=lambda: self.Login(
                            roots))  # This makes the login button, which will go to the Login def.
        loginB.grid(columnspan=2, sticky=W)
        roots.mainloop()  # This just makes the window keep open, we will destroy it soon

    '''this chacks the user name password and email with the server if it is ok it sign the user in the server's DB'''

    def chack_Signup(self, roots):
        email = emailE.get()
        username = nameE.get()
        password = pwordE.get()
        re_password = re_pwordE.get()
        print("email = ", email)
        print("username = ", username)
        print()
        if password == re_password and username != "" and email != "" and password != "" and re_password != "" and len(
                password) > 5:
            hashed_password = (hashlib.md5(pwordE.get().encode())).hexdigest()
            hashed_re_password = (hashlib.md5(re_pwordE.get().encode())).hexdigest()
            print("Hashed password = ", hashed_password)
            print("hashed re-password = ", hashed_re_password)
            msg_to_server = email + "%%%" + username + "%%%" + hashed_password
            print("msg_to_server = ", msg_to_server)
            self.messages.append(msg_to_server)
            try:
                self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.my_socket.connect(("127.0.0.1", 8080))
            except:
                print("line 85")
            self.send_messages()
            # roots.destroy()  # This will destroy the signup window. :)
            # self.Successfully_signin(roots)
            # roots.mainloop()
            # Login()  # This will move us onto the login definition :D
            while 1:
                rlist, wlist, xlist = select.select([self.my_socket], [self.my_socket], [])
                self.wlist = wlist
                if self.my_socket in rlist:
                    data = self.my_socket.recv(1024).decode('utf-8')
                    print(data)
                    dell = Label(roots, text="\n", width=25)
                    dell.grid(row=5, column=0)
                    roots.update()

                    if data == "signed in successfully":
                        notificationL = Label(roots, text=data, bg='SpringGreen2', width=25)
                        notificationL.grid(row=5, column=0)
                        roots.update()
                        time.sleep(0.1)
                        self.delete_all_in_root(roots)  # delete all the item in the window
                        print("my socket:", self.my_socket)
                        self.my_socket.close()
                        print("my socket:", self.my_socket)
                        self.Login(roots)
                    else:
                        notificationL = Label(roots, text=data, bg='firebrick2', width=25)
                        notificationL.grid(row=5, column=0)
                try:
                    roots.update()
                except:
                    continue
        else:
            dell = Label(roots, text="\n", width=25)
            dell.grid(row=5, column=0)
            roots.update()
            notificationL = Label(roots, text='Fill all and re-password\n(min 6 characters)', bg='firebrick2', width=25)
            notificationL.grid(row=5, column=0)

    def delete_all_in_root(self, roots):
        list = all_children(roots)
        for item in list:
            item.destroy()

    def send_messages(self):
        print(self.messages)
        for message in self.messages:
            if not self.wlist == None:
                self.my_socket.send(str(message).encode('utf-8'))
                print("sent: " + message)
                self.messages.remove(message)
                print("did not send")

    def Login(self, roots):
        global nameEL
        global pwordEL  # More globals :D
        self.delete_all_in_root(roots)

        roots.title('Login')  # This makes the window title 'login'
        intruction = Label(roots, text='Please Login\n')  # More labels to tell us what they do
        intruction.grid(sticky=E)  # Blahdy Blah

        nameL = Label(roots, text='Username: ')  # More labels
        pwordL = Label(roots, text='Password: ')  # ^
        nameL.grid(row=1, sticky=W)
        pwordL.grid(row=2, sticky=W)

        nameEL = Entry(roots)  # The entry input
        pwordEL = Entry(roots, show='*')
        nameEL.grid(row=1, column=1)
        pwordEL.grid(row=2, column=1)

        loginB = Button(roots, text='Login',
                        command=lambda: self.CheckLogin(
                            roots))  # This makes the login button, which will go to the CheckLogin def.
        loginB.grid(columnspan=2, sticky=W)
        signupB = Button(roots, text="Signup",
                         command=lambda: self.Signup(
                             roots))  # This makes the login button, which will go to the CheckLogin def.
        signupB.grid(columnspan=2, column=2, row=3)

        roots.mainloop()

    def CheckLogin(self, roots):
        username = nameEL.get()
        password = pwordEL.get()
        hashed_password = (hashlib.md5(pwordEL.get().encode())).hexdigest()
        print("username = ", username)
        print("password = ", password)
        try:
            self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.my_socket.connect(("127.0.0.1", 8080))
        except:
            print("fail open socket")

        msg_to_server = username + "%%%" + hashed_password
        print("msg_to_server = ", msg_to_server)
        self.messages.append(msg_to_server)
        self.send_messages()

        while 1:
            rlist, wlist, xlist = select.select([self.my_socket], [self.my_socket], [])
            if self.my_socket in rlist:
                data = self.my_socket.recv(1024).decode('utf-8')
                print(data)
                dell = Label(roots, text="\n", width=25)
                dell.grid(row=5, column=0)
                roots.update()

                if data == "loged-in":
                    notificationL = Label(roots, text=data, bg='SpringGreen2', width=18)
                    notificationL.grid(row=5, column=0)
                    roots.update()
                    time.sleep(1)
                    roots.update()
                    print("every thing is ok")
                    # self.my_socket.close()
                    roots.destroy()
                    # roots2 = Tk()
                    # ChatInterface(roots2)
                    return

                else:
                    notificationL = Label(roots, text=data, bg='firebrick2', width=18)
                    notificationL.grid(row=5, column=0)

            try:
                roots.update()
            except:
                continue
        else:
            dell = Label(roots, text="\n", width=25)
            dell.grid(row=5, column=0)
            roots.update()
            notificationL = Label(roots, text='Fill all and re-password\n(min 6 characters)', bg='firebrick2', width=25)
            notificationL.grid(row=5, column=0)

    def send_message(self, message):
        self.my_socket.send(message.encode('utf-8'))
        print(message)


    def listen_to_server(self):
        while True:
            rlist, wlist, xlist = select.select([self.my_socket], [self.my_socket], [])
            if self.my_socket in rlist:
                data = self.my_socket.recv(1024).decode('utf-8')
                print(data)
                if data ==  "":
                    print("the server closed this socket")
                    self.my_socket.close()
                gui_q.put(data)
                time.sleep(0.05)




class ChatInterface(Frame, Client):

    def __init__(self, master=None):
        Client.__init__(self, master)
        self.Signup(master)
        ##################################################
        commThread = Thread(target=self.listen_to_server, args=())
        commThread.start()
        ##################################################
        master = Tk()
        Frame.__init__(self, master)
        self.master = master
        self.master.geometry("600x350")

        # sets default bg for top level windows
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.font = "Verdana 10"

        menu = Menu(self.master)
        self.master.config(menu=menu, bd=5)
        global saved_username
        saved_username = ["You"]
        # Menu bar

        # File
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
        file.add_separator()
        file.add_command(label="Exit", command=self.client_exit)

        # Options
        options = Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=options)

        # username
        username = Menu(options, tearoff=0)
        # options.add_cascade(label="Username", menu=username)
        # username.add_command(label="Change Username", command=lambda: self.change_username(height=80))
        # username.add_command(label="Default Username", command=self.default_username)
        # username.add_command(label="View Username History", command=self.view_username_history)
        # username.add_command(label="Clear Username History", command=self.clear_username_history)

        options.add_separator()

        # font
        # font = Menu(options, tearoff=0)
        # options.add_cascade(label="Font", menu=font)
        # font.add_command(label="Default", command=self.font_change_default)
        # font.add_command(label="Times", command=self.font_change_times)
        # font.add_command(label="System", command=self.font_change_system)
        # font.add_command(label="Helvetica", command=self.font_change_helvetica)
        # font.add_command(label="Fixedsys", command=self.font_change_fixedsys)

        # color theme
        color_theme = Menu(options, tearoff=0)
        options.add_cascade(label="Color Theme", menu=color_theme)
        color_theme.add_command(label="Default", command=self.color_theme_default)
        # color_theme.add_command(label="Night", command=self.color_theme_dark)
        # color_theme.add_command(label="Grey", command=self.color_theme_grey)
        # color_theme.add_command(label="Blue", command=self.color_theme_dark_blue)
        # color_theme.add_command(label="Pink", command=self.color_theme_pink)
        # color_theme.add_command(label="Turquoise", command=self.color_theme_turquoise)
        color_theme.add_command(label="Hacker", command=self.color_theme_hacker)

        # all to default
        options.add_command(label="Default layout", command=self.default_format)

        options.add_separator()

        # change default window size
        # change default window size
        # options.add_command(label="Change Default Window Size", command=self.change_default_window_size)

        # default window size
        # options.add_command(label="Default Window Size", command=self.default_window_size)

        # Help
        # help_option = Menu(menu, tearoff=0)
        # menu.add_cascade(label="Help", menu=help_option)
        # help_option.add_command(label="Features", command=self.features_msg)
        # help_option.add_command(label="About", command=self.about_msg)
        # help_option.add_command(label="Gmail", command=self.src_code_msg)

        # Chat interface
        # frame containing text box with messages and scrollbar
        self.text_frame = Frame(self.master, bd=6)
        self.text_frame.pack(expand=True, fill=BOTH)

        # scrollbar for text box
        self.text_box_scrollbar = Scrollbar(self.text_frame, bd=0)
        self.text_box_scrollbar.pack(fill=Y, side=RIGHT)

        # contains messages
        self.text_box = Text(self.text_frame, yscrollcommand=self.text_box_scrollbar.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=10, height=1)
        self.text_box.pack(expand=True, fill=BOTH)
        self.text_box_scrollbar.config(command=self.text_box.yview)

        # frame containing user entry field
        self.entry_frame = Frame(self.master, bd=1)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()

        # frame containing send button and emoji button
        self.send_button_frame = Frame(self.master, bd=0)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',
                                  bd=1, command=self.send_message, activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.send_button.pack(side=LEFT, ipady=2)
        self.master.bind("<Return>", self.send_message_event)

        # emoticons
        # self.emoji_button = Button(self.send_button_frame, text="*", width=2, relief=GROOVE, bg='white',
        #                           bd=1, command=self.emoji_options, activebackground="#FFFFFF",
        #                           activeforeground="#000000")
        # self.emoji_button.pack(side=RIGHT, padx=6, pady=6, ipady=2)
        self.color_theme_hacker()
        self.last_sent_label(date="No messages sent.")
        master.mainloop()

    def last_sent_label(self, date):

        try:
            self.sent_label.destroy()
        except AttributeError:
            pass

        self.sent_label = Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)

    def color_theme_default(self):
        self.master.config(bg="#EEEEEE")
        self.text_frame.config(bg="#EEEEEE")
        self.entry_frame.config(bg="#EEEEEE")
        self.text_box.config(bg="#FFFFFF", fg="#000000")
        self.entry_field.config(bg="#FFFFFF", fg="#000000", insertbackground="#000000")
        self.send_button_frame.config(bg="#EEEEEE")
        self.send_button.config(bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000")
        # self.emoji_button.config(bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000")
        self.sent_label.config(bg="#EEEEEE", fg="#000000")

        self.tl_bg = "#FFFFFF"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"

    def color_theme_hacker(self):
        self.master.config(bg="#0F0F0F")
        self.text_frame.config(bg="#0F0F0F")
        self.entry_frame.config(bg="#0F0F0F")
        self.text_box.config(bg="#0F0F0F", fg="#33FF33")
        self.entry_field.config(bg="#0F0F0F", fg="#33FF33", insertbackground="#33FF33")
        self.send_button_frame.config(bg="#0F0F0F")
        self.send_button.config(bg="#0F0F0F", fg="#FFFFFF", activebackground="#0F0F0F", activeforeground="#FFFFFF")

        self.tl_bg = "#0F0F0F"
        self.tl_bg2 = "#0F0F0F"
        self.tl_fg = "#33FF33"

    def send_message(self):

        user_input = self.entry_field.get()

        username = saved_username[-1] + ": "
        message = (username, user_input)
        readable_msg = ''.join(message)
        readable_msg.strip('{')
        readable_msg.strip('}')

        # clears entry field, passes formatted msg to send_message_insert
        if user_input != '':
            self.entry_field.delete(0, END)
            self.send_message_insert(readable_msg)

        # inserts user input into text box
        Client.send_message(self, readable_msg)

    def send_message_insert(self, message):
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, message + '\n')
        self.last_sent_label(str(time.strftime("Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.text_box.see(END)
        self.text_box.configure(state=DISABLED)

    def send_message_event(self, event):
        self.send_message()

    def default_format(self):
        pass

    def client_exit(self):
        pass

    def clear_chat(self):
        pass

    def save_chat(self):
        pass


def all_children(root):
    _list = root.winfo_children()
    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())
    return _list


if __name__ == '__main__':
    roots = Tk()
    # c = Client(roots)
    # c.Signup(c.get_roots())
    # roots = Tk()
    # chat = ChatInterface(c.my_socket, master=roots)
    chat = ChatInterface(master=roots)
