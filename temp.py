from tkinter import *
import os
import socket
import hashlib
import sqlite3
import time
import select
from queue import Queue
from threading import *
from tkinter import filedialog
import base64
from PIL import ImageTk,Image
from tkinter import *
from NewChat import NewChatInterface
from cryptography.fernet import Fernet
from private_chat_buttons import PrivateChatButton

from TopFrame import TopFrameObject
from pygame import mixer  # Load the popular external library


conn_q = Queue()
gui_q = Queue()
message_q = Queue()


class Client():
    def __init__(self, roots):
        self.roots = roots
        self.messages_to_send = []
        self.wlist = []
        self.is_login = False
        self.is_close = False
        self.mode = "ENABLE"
        self.current_id = "public"
        self.current_external_id = "public"
        self.current_chat_name = "public"
        self.username = ""
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect(("127.0.0.1", 8080))
        print('Connected to server')
        self.key = self.my_socket.recv(1024).decode('utf-8').encode()
        print(f"got key{self.key.decode()}")
        self.buttons = []
        self.button_frames = []
        self.big_data = ""
        self.last_right_frame = None



    def get_roots(self):
        return self.roots

    def Signup(self, roots):  # This is the signup definition,
        global emailE
        global pwordE  # These globals just make the variables global to the entire script, meaning any definition can use them
        global re_pwordE
        global nameE

        self.delete_all_in_root(roots)
        ##############################################################################################################

        ##############################################################################################################
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
        #print("befor")

        submit_Button = Button(roots, text='submit', width=25, bg="DodgerBlue2",
                               command=lambda: self.chack_Signup(
                                   roots))  # This creates the button with the text 'signup', when you click it, the command 'fssignup' will run. which is the def
        #print("after")
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
        #print("email = ", email)
        #print("username = ", username)
        #print()
        if password == re_password and username != "" and email != "" and password != "" and re_password != "" and len(
                password) > 0:
            hashed_password = (hashlib.md5(pwordE.get().encode())).hexdigest()
            hashed_re_password = (hashlib.md5(re_pwordE.get().encode())).hexdigest()
            #print("Hashed password = ", hashed_password)
            #print("hashed re-password = ", hashed_re_password)
            msg_to_server = email + "+*!?" + username + "+*!?" + hashed_password
            #print("msg_to_server = ", msg_to_server)
            self.messages_to_send.append(msg_to_server)
            # try:
            #     self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     self.my_socket.connect(("127.0.0.1", 8080))
            # except:
            #     print("line 85")
            self.send_messages()
            # roots.destroy()  # This will destroy the signup window. :)
            # self.Successfully_signin(roots)
            # roots.mainloop()
            # Login()  # This will move us onto the login definition :D
            while 1:
                rlist, wlist, xlist = select.select([self.my_socket], [self.my_socket], [])
                self.wlist = wlist
                if self.my_socket in rlist:
                    data = self.my_socket.recv(1024).decode('utf-8').encode()
                    data = data[0:-7][9:]
                    #data = data.split(b"%%%")
                    #key, data = data
                    data = self.do_decrypt(self.key, data).decode()
                    #print(data)
                    #print("124"+data)
                    dell = Label(roots, text="\n", width=25)
                    dell.grid(row=5, column=0)
                    roots.update()

                    if data == "signed in successfully":
                        notificationL = Label(roots, text=data, bg='SpringGreen2', width=25)
                        notificationL.grid(row=5, column=0)
                        roots.update()
                        time.sleep(0.05)
                        self.delete_all_in_root(roots)  # delete all the item in the window
                        #print("my socket:", self.my_socket)
                        # self.my_socket.close()
                        #print("my socket:", self.my_socket)
                        self.Login(roots)
                        return
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

    def do_decrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        return f.decrypt(data)

    def do_encrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        #print(f.encrypt(data.encode()))
        if isinstance(data, str):
            data = data.encode()
        return f.encrypt(data)


    # def split_msg(self, msg):
    #     max_packeg_size = 1024
    #     i = 0
    #     list_msgs = []
    #     while i < len(msg):
    #         if i % 1024 == 0:
    #             list_msgs.append('')
    #         list_msgs[-1] += msg[i]
    #





    def send_messages(self):
        print("entered to send msgs")
        for message in self.messages_to_send:
            if not self.wlist == None:
                #key = Fernet.generate_key()#generates new key (bytes object) randomly
                # data = key.decode() + "%%%" + self.do_encrypt(key, message).decode()
                data = f"Start_Seg{self.do_encrypt(self.key, message).decode()}End_Seg"
                #print(data)
                #print(type(data))
                #print("really sent:" + data)
                self.my_socket.send(data.encode('utf-8'))
                #print("sent: " + message)

                self.messages_to_send.remove(message)

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

        forgot_pass_Button = Button(roots, text='forgot password?', bg="orange")
        forgot_pass_Button.grid(column=1, row=3)

        loginB = Button(roots, text='Login', bg="green",
                        command=lambda: self.CheckLogin(
                            roots))  # This makes the login button, which will go to the CheckLogin def.
        loginB.grid(columnspan=2, row=3, sticky=W)
        signupB = Button(roots, text="Signup",bg="blue",
                         command=lambda: self.Signup(
                             roots))  # This makes the login button, which will go to the CheckLogin def.
        signupB.grid(columnspan=2, column=2, row=3)

        roots.mainloop()

    def CheckLogin(self, roots):
        username = nameEL.get()
        password = pwordEL.get()
        hashed_password = (hashlib.md5(pwordEL.get().encode())).hexdigest()
        #print("username = ", username)
        #print("password = ", password)
        # try:
        #     self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.my_socket.connect(("127.0.0.1", 8080))
        # except:
        #     print("fail open socket")

        msg_to_server = username + "+*!?" + hashed_password
        #print("msg_to_server = ", msg_to_server)
        self.messages_to_send.append(msg_to_server)
        self.send_messages()

        while 1:
            rlist, wlist, xlist = select.select([self.my_socket], [self.my_socket], [])
            if self.my_socket in rlist:
                data = self.my_socket.recv(1024).decode('utf-8')
                #############################################
                print(f"{data}")
                data = data[0:-7][9:]
                print(f"{data}")
                #############################################
                #data = data.split("%%%")
                #key,data = data
                data = self.do_decrypt(self.key,data.encode())
                #print("231"+data.decode())
                data = data.decode()
                dell = Label(roots, text="\n", width=25)
                dell.grid(row=5, column=0)
                roots.update()

                if data == "loged-in":
                    #print("000")
                    self.username = username
                    notificationL = Label(roots, text=data, bg='SpringGreen2', width=18)
                    notificationL.grid(row=5, column=0)
                    roots.update()
                    time.sleep(0.05)
                    roots.update()
                    #print("every thing is ok")
                    # self.my_socket.close()
                    roots.destroy()
                    # roots2 = Tk()
                    # ChatInterface(roots2)
                    self.is_login = True
                    return

                else:
                    notificationL = Label(roots, text=data, bg='firebrick2', width=18)
                    notificationL.grid(row=5, column=0)
                    return

            try:
                roots.update()
            except:
                continue

    def send_message(self, message):#to swichhhhhh
        self.messages_to_send.append(message)
        self.send_messages()
        #print(message)

    def messages_connected(self):
        print(f"my big big big data = {self.big_data}")
        # self.big_data = self.big_data
        msg_split1 = self.big_data.split("End_Seg")
        print(f"len = {len(msg_split1)}, list = {msg_split1}")

        for i in range(len(msg_split1)-1):
            mini_part = msg_split1[i]
            mini_part = mini_part.split("Start_Seg")[1]
            print(f"mini_part = {mini_part}")
            #key = mini_part.split("%%%")[0]
            data = mini_part#.split("%%%")[1]
            mini_part = self.do_decrypt(self.key, data.encode())
            message_q.put(mini_part)
        self.big_data = msg_split1[len(msg_split1)-1]

    def listen_to_server(self):
        while True:
            rlist, wlist, xlist = select.select([self.my_socket], [self.my_socket], [])
            if self.my_socket in rlist:
                data = self.my_socket.recv(1024).decode('utf-8')
                print(f"data ====== {data}")
                self.big_data = self.big_data + data

                if data == "":
                    #print("connection closed")
                    self.my_socket.close()
                    self.is_close = True
                    return
                self.messages_connected()

                #print(data)


                #message_q.put(data)

                time.sleep(0.05)




class ChatInterface(Frame, Client):

    def __init__(self, master=None):
        self.bool = False
        Client.__init__(self, master)
        self.Login(master)
        ##################################################
        if self.is_login == False:
            self.client_exit()
            return
        commThread = Thread(target=self.listen_to_server)
        commThread.start()




        ##################################################
        master = Tk()
        Frame.__init__(self, master)
        self.master = master
        self.master.geometry("600x350")
        self.master.title(f'IChat;) {self.username} online')
        guiThread = Thread(target=self.updata_gui_loop)
        guiThread.start()
        self.right_frame = Frame(master)

        # sets default bg for top level windows
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.font = "Verdana 10"

        #self.get_args_from_file("args.txt")
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
        file.add_command(label="Logout", command=self.client_exit)

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
        font = Menu(options, tearoff=0)
        options.add_cascade(label="Font", menu=font)
        font.add_command(label="Default", command=self.font_change_default)
        font.add_command(label="Times", command=self.font_change_times)
        # font.add_command(label="System", command=self.font_change_system)
        # font.add_command(label="Helvetica", command=self.font_change_helvetica)
        font.add_command(label="Fixedsys", command=self.font_change_fixedsys)

        # color theme
        color_theme = Menu(options, tearoff=0)
        options.add_cascade(label="Color Theme", menu=color_theme)
        color_theme.add_command(label="Default", command=self.color_theme_default)
        # color_theme.add_command(label="Night", command=self.color_theme_dark)
        # color_theme.add_command(label="Grey", command=self.color_theme_grey)
        color_theme.add_command(label="Blue", command=self.color_theme_dark_blue)
        color_theme.add_command(label="Pink", command=self.color_theme_pink)
        color_theme.add_command(label="Turquoise", command=self.color_theme_turquoise)
        color_theme.add_command(label="Hacker", command=self.color_theme_hacker)

        # all to default
        options.add_command(label="Default layout", command=self.default_format)

        options.add_separator()
        #new chat menu
        new_chat = Menu(menu, tearoff=0)
        menu.add_cascade(label="new chat", menu=new_chat)
        new_chat.add_command(label="open new chat", command=self.open_new_chat_window)


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

        # Chat interface
        # frame containing text box with messages and scrollbar
        self.contacts_frame = Frame(self.master, bd=3)
        self.contacts_frame.pack(fill=BOTH, side=LEFT)
        self.contacts_scrollbar = Scrollbar(self.contacts_frame,orient=VERTICAL)
        self.contacts_scrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self.contacts_frame, bd=0, highlightthickness=0,
                             yscrollcommand=self.contacts_scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.contacts_scrollbar.config(command=self.canvas.yview)

        def _on_mouse(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        self.canvas.bind_all('<MouseWheel>', _on_mouse)

        # reset the view
        #self.canvas.xview_moveto(0)
        #self.canvas.yview_moveto(0)



        # just to show how it will look like
        contacts = ["public"]
        for i in contacts:
            self.button_frame = Frame(self.canvas)
            self.button_frame.pack(fill=BOTH)
            # self.button_frames.append(self.buttons_frame)
            self.button_try = Button(self.button_frame, text=i,width=18 ,bg="gray99" ,relief=FLAT, font=self.font, command=lambda: self.change_to_public_mode())
            self.button_try.pack(padx=10, pady=5, side=TOP)




        self.text_frame = Frame(self.right_frame, bd=0)
        self.text_frame.pack(expand=True, fill=BOTH)
        self.canvas.configure(background=self.tl_bg2)

        # frame contains the current chat name
        # self.chat_name_frame = Frame(self.master, bd=0)
        # self.chat_name_frame.pack(fill=BOTH)


        # object for all the commands of the top_frame buttons
        self.top_frame_object = TopFrameObject(self)

        # top frame
        self.top_frame = Frame(self.text_frame)
        self.top_frame.pack(side=TOP, fill=X)
        self.add_chat_contact = Button(self.top_frame,text="+", command=lambda: a(self), width=4, relief=GROOVE,
                        bg='green',
                        bd=0, activebackground="#FFFFFF",activeforeground="#000000")
        self.exit_chat = Button(self.top_frame, text="exit", command=lambda :self.top_frame_object.exit_chat(), width=4, relief=GROOVE,
                        bg='red',
                        bd=0, activebackground="#FFFFFF",activeforeground="#000000")
        self.chat_info_button = Button(self.top_frame, text=self.current_chat_name, command=lambda :self.top_frame_object.chat_info_request(), width=4, relief=GROOVE,
                        bg='gray99',
                        bd=0, activebackground="#FFFFFF",activeforeground="#000000")
        self.link_chat = Button(self.top_frame, text='link',
                                       command=lambda: self.top_frame_object.link_user_to_chat(), width=4,
                                       relief=GROOVE,
                                       bg='blue',
                                       bd=0, activebackground="#FFFFFF", activeforeground="#000000")
        self.exit_chat.pack(side=RIGHT, padx=1,pady=1)
        self.add_chat_contact.pack(side=RIGHT, padx=1,pady=1)
        self.link_chat.pack(side=RIGHT, padx=1,pady=1)
        self.chat_info_button.pack(side=TOP, padx=1, pady=1, fill=BOTH)





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
        self.entry_frame = Frame(self.right_frame, bd=1)
        self.entry_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # entry field
        self.entry_field = Entry(self.entry_frame, bd=1, justify=LEFT)
        self.entry_field.pack(fill=X, padx=6, pady=6, ipady=3)
        # self.users_message = self.entry_field.get()



        # frame containing send button and choose file to upload
        self.send_button_frame = Frame(self.right_frame, bd=0)
        self.send_button_frame.pack(fill=BOTH)

        # send button
        self.send_button = Button(self.send_button_frame, text="Send", width=5, relief=GROOVE, bg='white',
                                  bd=1, command=self.send_message, activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.send_button.pack(side=LEFT, ipady=2)
        self.master.bind("<Return>", self.send_message_event)
        self.file_button = Button(self.send_button_frame, text="file", width=4, relief=GROOVE, bg='white',
                                                              bd=1, command=self.choose_file, activebackground="#FFFFFF",
                                                              activeforeground="#000000")
        self.file_button.pack(side=RIGHT, padx=6, pady=6, ipady=2)

        # emoticons
        # self.emoji_button = Button(self.send_button_frame, text="*", width=2, relief=GROOVE, bg='white',
        #                           bd=1, command=self.emoji_options, activebackground="#FFFFFF",
        #                           activeforeground="#000000")
        # self.emoji_button.pack(side=RIGHT, padx=6, pady=6, ipady=2)
        # self.color_theme_hacker()
        self.last_sent_label(date="No messages sent.")
        self.bool = True
        self.right_frame.pack(fill=BOTH ,expand=True)
        master.mainloop()
        self.client_exit()
    # def get_args_from_file(self, file_name):
    #     f = open(file_name, "r")
    #     contents = f.readlines()
    #     f.close()
    #     contents = contents[0].split(',')
    #     self.tl_bg = contents[0]
    #     self.tl_bg2 = contents[1]
    #     self.tl_fg = contents[2]
    #     self.font = contents[3]
    #     for i in contents:
    #         print(f"{i}")

    # def write_args_in_file(self, file_name):
    #     f = open(file_name, "w")
    #     f.write(f"{self.tl_bg},{self.tl_bg2},{self.tl_fg},{self.font}\n")

    def change_to_public_mode(self):
        self.mode = 'ENABLE'
        self.current_id = "public"
        self.current_external_id = "public"
        self.current_chat_name = "public"
        if self.last_right_frame:
            self.right_frame.pack_forget()
            self.last_right_frame.pack(fill=BOTH, expand=True)
            self.right_frame = self.last_right_frame
        self.chat_info_button.configure(text="public")
        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

    def disable(self):
        self.mode = "DISABLE"
        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

     #returns button with this id
    def button_by_id(self, chat_id):
        for button in self.buttons:
            if button.chat_id == chat_id:
                return button



    def last_sent_label(self, date):
        try:
            self.sent_label.destroy()
        except AttributeError:
            pass
        self.sent_label = Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)

    def font_change_default(self):
        self.text_box.config(font="Verdana 10")
        self.entry_field.config(font="Verdana 10")
        self.font = "Verdana 10"
        self.set_font_to_chat_buttons()

    def font_change_times(self):
        self.text_box.config(font="Times 11")
        self.entry_field.config(font="Times 11")
        self.font = "Times 11"
        self.set_font_to_chat_buttons()


    def font_change_fixedsys(self):
        self.text_box.config(font="fixedsys")
        self.entry_field.config(font="fixedsys")
        self.font = "fixedsys"
        self.set_font_to_chat_buttons()

    def set_font_to_chat_buttons(self):
        self.button_try.configure(font=self.font)
        for button in self.buttons:
            button.font = self.font
            button.configure(font=button.font)

    def set_color_to_chat_button_frames(self, color):
        for frame in self.button_frames:
            frame.configure(background=color)

    def color_theme_default(self):
        self.contacts_frame.config(bg="#EEEEEE")
        self.canvas.config(bg="#EEEEEE")
        self.master.config(bg="#EEEEEE")
        self.text_frame.config(bg="#EEEEEE")
        self.entry_frame.config(bg="#EEEEEE")
        self.text_box.config(bg="#FFFFFF", fg="#000000")
        self.entry_field.config(bg="#FFFFFF", fg="#000000", insertbackground="#000000")
        self.send_button_frame.config(bg="#EEEEEE")
        self.send_button.config(bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000")
        self.sent_label.config(bg="#EEEEEE", fg="#000000")

        self.tl_bg = "#FFFFFF"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.set_color_to_chat_button_frames("#EEEEEE")
        self.button_frame.configure(background="#EEEEEE")
        self.canvas.configure(background="#EEEEEE")
        #self.write_args_in_file("args.txt")

    def color_theme_turquoise(self):
        self.contacts_frame.config(bg="#003333")
        self.master.config(bg="#003333")
        self.text_frame.config(bg="#003333")
        self.text_box.config(bg="#669999", fg="#FFFFFF")
        self.entry_frame.config(bg="#003333")
        self.entry_field.config(bg="#669999", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#003333")
        self.send_button.config(bg="#669999", fg="#FFFFFF", activebackground="#669999", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#003333", fg="#FFFFFF")

        self.tl_bg = "#669999"
        self.tl_bg2 = "#003333"
        self.tl_fg = "#FFFFFF"
        self.set_color_to_chat_button_frames("#003333")
        self.button_frame.configure(background="#003333")
        self.canvas.configure(background="#003333")
        #self.write_args_in_file("args.txt")

    def color_theme_hacker(self):
        self.contacts_frame.config(bg="#0F0F0F")
        #self.button_try.config(bd=0)
        #self.canvas.config(bg="#0F0F0F")
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
        self.set_color_to_chat_button_frames("#0F0F0F")
        self.button_frame.configure(background="#0F0F0F")
        self.canvas.configure(background="#0F0F0F")
        #self.write_args_in_file("args.txt")

    def color_theme_dark_blue(self):
        self.contacts_frame.config(bg="#263b54")
        self.master.config(bg="#263b54")
        self.text_frame.config(bg="#263b54")
        self.text_box.config(bg="#1c2e44", fg="#FFFFFF")
        self.entry_frame.config(bg="#263b54")
        self.entry_field.config(bg="#1c2e44", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.send_button_frame.config(bg="#263b54")
        self.send_button.config(bg="#1c2e44", fg="#FFFFFF", activebackground="#1c2e44", activeforeground="#FFFFFF")
        self.sent_label.config(bg="#263b54", fg="#FFFFFF")

        self.tl_bg = "#1c2e44"
        self.tl_bg2 = "#263b54"
        self.tl_fg = "#FFFFFF"
        self.set_color_to_chat_button_frames("#263b54")
        self.button_frame.configure(background="#263b54")
        self.canvas.configure(background="#263b54")
        #self.write_args_in_file("args.txt")

    # Pink
    def color_theme_pink(self):
        self.master.config(bg="#ffc1f2")
        self.text_frame.config(bg="#ffc1f2")
        self.text_box.config(bg="#ffe8fa", fg="#000000")
        self.entry_frame.config(bg="#ffc1f2")
        self.entry_field.config(bg="#ffe8fa", fg="#000000", insertbackground="#000000")
        self.send_button_frame.config(bg="#ffc1f2")
        self.send_button.config(bg="#ffe8fa", fg="#000000", activebackground="#ffe8fa", activeforeground="#000000")
        self.sent_label.config(bg="#ffc1f2", fg="#000000")

        self.tl_bg = "#ffe8fa"
        self.tl_bg2 = "#ffc1f2"
        self.tl_fg = "#000000"
        #self.write_args_in_file("args.txt")

    def default_format(self):
        self.font_change_default()
        self.color_theme_default()

    def send_message(self):
        if self.mode == "DISABLE":
            return

        user_input = self.entry_field.get()

        if user_input == "" or user_input is None:
            return

        if self.current_id != "public": # in private chat ...
            msg_to_send = f"private+*!?{self.username}+*!?{self.current_id}+*!?{self.current_external_id}+*!?{user_input}"

            #print(msg_to_send)
        if self.current_id == "public":
            msg_to_send = "public+*!?" + self.username + "+*!?" + user_input

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
        Client.send_message(self, msg_to_send)

    def send_message_insert(self, message):
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, message + '\n')
        self.last_sent_label(str(time.strftime("Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.text_box.see(END)
        self.text_box.configure(state=DISABLED)

    def send_message_event(self, event):
        self.send_message()

    def client_exit(self):
        msg_to_server = "NAK+*!?"+self.username
        for btn in self.buttons:
            msg_to_server = msg_to_server + "+*!?" + str(btn.chat_id) + "+*!?" + str(btn.new_msgs)
        self.messages_to_send.append(msg_to_server)
        self.send_messages()
        exit()
        pass

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            print(file_path)
            with open(file_path, 'rb') as f:
                contents = f.read()
                f.close()
            print(type(contents))
            if self.current_id == "public":
                split = file_path.split('/')
                file_name = len(split)
                file_name = split[file_name-1]
                file_msg = ("public_file+*!?" + self.username + f"+*!?{file_name}$$$").encode()+contents
                self.messages_to_send.append(file_msg)
                self.send_messages()
            else:
                pass
                #file_msg = f"private%%%{self.username}%%%{self.current_id}%%%{self.current_external_id}%%%{user_input}"

    def clear_chat(self):
        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)
    def save_chat(self):
        pass

    def config_message(self, message):
        msg = message.split('+*!?')
        return msg[1] + ': ' + msg[2]

    def open_new_chat_window(self):
        self.last_right_frame = self.right_frame
        NewChatInterface(self)
        #from NewChat import msg
        #msg = msg + "," + self.username
        #print("in temp class :"+msg)
        #self.messages_to_send.append(msg)
        print(self.mode)
        # self.send_messages()

    def updata_gui_loop(self):
        while True:
            if self.is_close:
                return
            if message_q.empty():
                pass
            else:
                message = message_q.get()
                #TODO decipher
                ####################################################
                self.decipher(message)
                self.send_messages()
                ####################################################


    def decipher(self, message):
        print(f"message in decipher = {message}")
        if message.split(b"+*!?")[0] == b"public":
            if self.current_id == "public" and self.current_external_id == "public" and self.mode == "ENABLE":
                message = message.decode()
                self.send_message_insert(self.config_message(message))
        elif message.split(b"+*!?")[0] == b"public_file":
            if b"$$$" in message:
                print("special msg")
                splited = message.split(b'+*!?')[2]

                file_info = splited.split(b"$$$")
                file_name = file_info[0].decode('utf-8')
                file = file_info[1]
                # type_special = splited[0].split(b'%%%')
                with open(file_name, 'wb') as f:
                    f.write(file)
                    f.close()
        elif message.split(b"+*!?")[0] == b"private":

            msg = message.split(b"+*!?")
            username =msg[1].decode()
            id = msg[2].decode()
            #print(f"id clienttt ={id}")
            msg = msg[3].decode()
            print(f"username = {username}, id = {id},msg = {msg}")
            print(f"and the current chat_id the client now = {self.current_id}")
            #TODO: CHECK IF THE CURRENT_ID IS THE SAME AS THE ID FROM THE MSG IF IT IS I NEED TO DISPLAY IT AND IF NOT I NEED TO SIGHN THE CURRENT CHAT
            if str(self.current_id) == str(id) and self.mode == "ENABLE":
               self.send_message_insert(f"{username}: {msg}") # push it to the text box (this is only a confusing name)
               mixer.init()
               mixer.music.load('pics/clearly.mp3')
               mixer.music.play()

            else:
               #pass #TODO I CAN USE A LIST OF BUTTONS AND TO USE IT IN ORDER TO MAKE AN ORDER OR TO COLOR THEM IF THE GOT MSGS OR BOTH
                self.button_by_id(id).new_msg_arrived()
                mixer.init()
                mixer.music.load('pics/msg sound 1.mp3')
                mixer.music.play()

        elif message.split(b'+*!?')[0] == b'chat info':
            print("hereeeeeeeee")
            #msg = f"chat info+*!?{is_manager}+*!?{is_linked}+*!?{num_of_contacts}+*!?{users_he_linked}+*!?{contacts}+*!?{managers}"
            msg = message.split(b'+*!?')
            is_manager = msg[1]
            is_linked = msg[2].decode()
            num_of_contacts = msg[3].decode()
            users_he_linked = msg[4].decode()
            contacts = msg[5].decode()
            managers = msg[6].decode()
            self.display_chat_info(is_manager, is_linked, num_of_contacts, users_he_linked, contacts, managers)

        elif message.split(b"+*!?")[0] == b"new chat":
            msg = message.split(b"+*!?")
            chat_id = msg[1].decode()
            external_id = msg[2].decode()
            chat_name = msg[3].decode()
            contacts = msg[4].decode()
            new_msgs = msg[5].decode()
            print(f"new_msgs = {new_msgs}")
            while self.bool == False: #wait to load the client graphics
                None
            self.buttons_frame = Frame(self.canvas)
            self.buttons_frame.pack(fill=BOTH)
            self.buttons_frame.configure(background=self.tl_bg2)
            b = PrivateChatButton(self.buttons_frame, chat_name, chat_id, external_id, contacts, new_msgs, self)
            print(f"chat_id of the button just created = {b.chat_id}")
            b.pack(padx=10, pady=5, side=TOP)
            print ("chat button created")
            self.button_frames.append(self.buttons_frame)
            self.buttons.append(b)

    def display_chat_info(self, is_manager, is_linked, num_of_contacts, users_he_linked, contacts, managers):
        contacts = contacts.split(",")
        managers = managers.split(",")
        users_he_linked = users_he_linked.split(",")
        managers = '\n'.join(managers)
        contacts = '\n'.join(contacts)
        users_he_linked = '\n'.join(users_he_linked)
        to_display = None
        if is_manager == "False" and is_linked == "False":
            to_display = f"-----Info page:-----\nName: {self.current_chat_name}\n-----Managers:-----\n{managers}\n" \
                     f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                     f"-----Users you linked-----\n{users_he_linked}"

        if is_manager == "True" and is_linked == "False":
            to_display = f"-----Info page:-----\nMame: {self.current_chat_name}\n-----Managers:--(You are a manager)---\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"
        if is_manager == "False" and is_linked == "True":
            to_display = f"-----Info page:-----\nMame: {self.current_chat_name}--(This is a linked chat)---\n-----Managers:-----\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"
        else:
            to_display = f"-----Info page:-----\nMame: {self.current_chat_name}\n-----Managers:--(You are a manager and also have linked chat of this chat)---\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"

        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.insert(END,to_display+"\n")
        self.text_box.config(state=DISABLED)



def a (client):
    pass




def all_children(root):
    _list = root.winfo_children()
    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())
    return _list


if __name__ == '__main__':
    roots = Tk()
    chat = ChatInterface(master=roots)
