import threading
import sys
import time
from datetime import datetime
from tkinter import filedialog

import tk

from ClientInterface import Client
from tkinter import *

from FilesFrame import FilesFrame
from NewChat import NewChatInterface
from NewPrivateChatInterface import NewPrivateChatInterface
from TopFrame import TopFrameObject
from private_chat_buttons import PrivateChatButton
from pygame import mixer

class Interface(Client):

    def __init__(self, roots):
        Client.__init__(self, ip='127.0.0.1', port=8080)

        self.master = roots

        self.right_frame = None
        self.last_right_frame = None
        self.last_last_right_frame = None
        self.chat_frame = None
        self.is_chat_time = True

        self.is_loaded = False

        # colors and fonts
        self.tl_bg = None
        self.tl_bg2 = None
        self.tl_fg = None
        self.font = None

        self.contacts_frame = None
        self.contacts_scrollbar = None
        self.canvas = None
        self.text_frame = None
        self.top_frame_object = None
        self.top_frame = None
        self.add_chat_contact = None
        self.exit_chat = None
        self.chat_info_button = None
        self.link_chat = None
        self.text_box_scrollbar = None
        self.text_box = None
        self.entry_frame = None
        self.entry_field = None
        self.send_button_frame = None
        self.send_button = None
        self.file_button = None
        self.emoji_button = None
        self.sent_label = None
        self.interior = None
        self.button_frame = None

        # login variables
        self.nameEL = None
        self.pwordEL = None

        # signup variables
        self.emailE = None
        self.nameE = None
        self.pwordE = None
        self.re_pwordE = None
        self.notification_l = None

        self.button_frames = []
        self.buttons = []

        self.log_in_time()

    def sign_up_time(self):
        self.delete_all_in_root()
        # This creates the window, just a blank one.
        self.master.geometry('420x200')
        #self.master.resizable(width=False, height=False)
        self.master.title('Signup')  # This renames the title of said window to 'signup'
        intruction = Label(self.master,
                           text='Please signup\n')  # This puts a label, so just a piece of text saying 'please enter blah'
        intruction.grid(row=0, column=0,
                        sticky=E)  # This just puts it in the window, on row 0, col 0. If you want to learn more look up a tkinter tutorial :)
        emailL = Label(self.master,
                       text='Email: ')  # This just does the same as above, instead with the text new username.
        nameL = Label(self.master,
                      text='Username: ')  # This just does the same as above, instead with the text new username.
        pwordL = Label(self.master, text='Password: ')  # ^^
        re_pwordL = Label(self.master, text="Re-Password: ")
        emailL.grid(row=1, column=0,
                    sticky=W)  # Same thing as the instruction var just on different rows. :) Tkinter is like that.
        nameL.grid(row=2, column=0, sticky=W)  # ^^
        pwordL.grid(row=3, column=0, sticky=W)  # ^^
        re_pwordL.grid(row=4, column=0, sticky=W)

        self.emailE = Entry(self.master, width=30)  # This now puts a text box waiting for input.
        self.nameE = Entry(self.master, width=30)  # ^^
        self.pwordE = Entry(self.master, show='*',
                       width=30)  # Same as above, yet 'show="*"' What this does is replace the text with *, like a password box :D
        self.re_pwordE = Entry(self.master, show='*', width=30)  # ^^
        self.emailE.grid(row=1, column=1)
        self.nameE.grid(row=2, column=1)
        self.pwordE.grid(row=3, column=1)
        self.re_pwordE.grid(row=4, column=1)

        submit_Button = Button(self.master, text='submit', width=25, bg="DodgerBlue2",
                               command=lambda: self._sign_up())
        # This creates the button with the text 'signup', when you click it, the command 'fssignup' will run. which is the def
        # print("after")
        submit_Button.grid(row=5, column=1, sticky="e")
        loginB = Button(self.master, text='Login',command=lambda: self.log_in_time())
        # This makes the login button, which will go to the Login def.
        loginB.grid(columnspan=2, sticky=W)
        self.master.mainloop()  # This just makes the window keep open, we will destroy it soon

    def log_in_time(self):
        self.delete_all_in_root()
        intruction = Label(self.master, text='Please Login\n')  # More labels to tell us what they do
        intruction.grid(sticky=E)  # Blahdy Blah

        nameL = Label(self.master, text='Username: ')  # More labels
        pwordL = Label(self.master, text='Password: ')  # ^
        nameL.grid(row=1, sticky=W)
        pwordL.grid(row=2, sticky=W)

        self.nameEL = Entry(self.master)  # The entry input
        self.pwordEL = Entry(self.master, show='*')
        self.nameEL.grid(row=1, column=1)
        self.pwordEL.grid(row=2, column=1)

        forgot_pass_button = Button(self.master, text='forgot password?', bg="orange")
        forgot_pass_button.grid(column=1, row=3)

        login_b = Button(self.master, text='Login', bg="green", command= self._log_in)
        login_b.grid(columnspan=2, row=3, sticky=W)
        signup_b = Button(self.master, text="Signup", bg="blue", command=lambda: self.sign_up_time())
        signup_b.grid(columnspan=2, column=2, row=3)

    def chat_time(self):
        self.master.tk.call('wm', 'iconphoto', self.master._w, PhotoImage(file='pics\\chat logo.png'))
        self.master.geometry("600x350")
        self.master.title(f'ChatIt;) {self.username} online')
        self.right_frame = Frame(self.master)

        # sets default bg for top level windows
        self.tl_bg = "#EEEEEE"
        self.tl_bg2 = "#EEEEEE"
        self.tl_fg = "#000000"
        self.font = "Verdana 10"

        # self.get_args_from_file("args.txt")
        menu = Menu(self.master)
        self.master.config(menu=menu, bd=5)
        global saved_username
        saved_username = ["You"]
        # Menu bar

        # File
        file = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file)
        #file.add_command(label="Save Chat Log", command=self.save_chat)
        file.add_command(label="Clear Chat", command=self.clear_chat)
        file.add_separator()
        file.add_command(label="Logout", command=self._client_exit)
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
        color_theme.add_command(label="Turquoise", command=self.color_theme_turquoise)
        color_theme.add_command(label="Hacker", command=self.color_theme_hacker)

        # all to default
        options.add_command(label="Default layout", command=self.default_format)

        options.add_separator()
        # new chat menu
        new_chat = Menu(menu, tearoff=0)
        menu.add_cascade(label="new chat", menu=new_chat)
        new_chat.add_command(label="new group", command=self.open_new_chat_window)
        new_chat.add_command(label="new private chat", command=self.open_new_private_chat_window)
        self.contacts_frame = Frame(self.master, bd=3)
        self.contacts_frame.pack(fill=BOTH, side=LEFT)
        self.contacts_scrollbar = Scrollbar(self.contacts_frame, orient=VERTICAL)
        self.contacts_scrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self.contacts_frame, bd=0, highlightthickness=0,
                             yscrollcommand=self.contacts_scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.contacts_scrollbar.config(command=self.canvas.yview)

        self.canvas.bind_all('<MouseWheel>', self._on_mouse)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.interior = interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar


        interior.bind('<Configure>', self._configure_interior)



        self.canvas.bind('<Configure>', self._configure_canvas)

        # just to show how it will look like
        contacts = ["public"]
        for i in contacts:
            self.button_frame = Frame(self.interior)
            self.button_frame.pack(fill=BOTH)
            self.button_frames.append(self.interior)
            self.button_try = Button(self.interior, text=i, width=18, bg="gray99", relief=FLAT, font=self.font,
                                     command=lambda: self._public_mode())
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
        self.add_chat_contact = Button(self.top_frame, text="+", command=lambda: self.top_frame_object.
                                       add_contact_to_chat(), width=4, relief=FLAT,
                                       bg='green',
                                       bd=0, activebackground="#FFFFFF", activeforeground="#000000")
        self.exit_chat = Button(self.top_frame, text="exit", command=lambda: self.top_frame_object.exit_chat(), width=4,
                                relief=FLAT,
                                bg='red',
                                bd=0, activebackground="#FFFFFF", activeforeground="#000000")
        self.chat_info_button = Button(self.top_frame, text=self.current_chat_name,
                                       command=lambda: self.top_frame_object.chat_info_request(), width=4, relief=FLAT,
                                       bg='gray99',
                                       bd=0, activebackground="#FFFFFF", activeforeground="#000000")
        self.link_chat = Button(self.top_frame, text='link',
                                command=lambda: self.top_frame_object.link_user_to_chat(), width=4,
                                relief=FLAT,
                                bg='blue',
                                bd=0, activebackground="#FFFFFF", activeforeground="#000000")
        self.exit_chat.pack(side=RIGHT, padx=1, pady=1)
        self.add_chat_contact.pack(side=RIGHT, padx=1, pady=1)
        self.link_chat.pack(side=RIGHT, padx=1, pady=1)
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
        self.send_button = Button(self.send_button_frame, text="Send", width=6, relief=GROOVE, bg='white',
                                  bd=1, command=lambda: self._send(), activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.send_button.pack(side=LEFT, ipady=2)
        self.master.bind("<Return>", lambda: self.send_message_event())
        self.file_button = Button(self.send_button_frame, text="file", width=4, relief=GROOVE, bg='white',
                                  bd=1, command=self.choose_file, activebackground="#FFFFFF",
                                  activeforeground="#000000")
        self.file_button.pack(side=RIGHT, padx=6, pady=6, ipady=2)

        # emoticons
        self.emoji_button = Button(self.send_button_frame, text="drive", width=4, relief=GROOVE, bg='white',
                                   bd=1, activebackground="#FFFFFF", command=lambda: self.emoji_options(),
                                   activeforeground="#000000")
        self.emoji_button.pack(side=RIGHT, padx=6, pady=6, ipady=2)
        # self.color_theme_hacker()
        self.last_sent_label(date="No messages sent.")

        self.right_frame.pack(fill=BOTH, expand=True)

        self._public_mode()
        self.is_loaded = True

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def last_sent_label(self, date):
        try:
            self.sent_label.destroy()
        except AttributeError:
            pass
        self.sent_label = Label(self.entry_frame, font="Verdana 7", text=date, bg=self.tl_bg2, fg=self.tl_fg)
        self.sent_label.pack(side=LEFT, fill=X, padx=3)

    def got_new_chat(self, chat_id, external_id, chat_name, contacts, new_msgs, is_private):
        buttons_frame = Frame(self.interior)
        buttons_frame.pack(fill=BOTH)
        buttons_frame.configure(background=self.tl_bg2)
        b = PrivateChatButton(buttons_frame, chat_name, chat_id, external_id, contacts, new_msgs, is_private, self)
        print(f"chat_id of the button just created = {b.chat_id}")
        b.pack(padx=10, pady=5, side=TOP)
        print("chat button created")
        self.button_frames.append(buttons_frame)
        self.buttons.append(b)


    def got_chat_info(self, is_manager, is_linked, num_of_contacts, users_he_linked, contacts, managers, is_private):
        contacts = contacts.split(",")
        managers = managers.split(",")
        users_he_linked = users_he_linked.split(",")
        managers = '\n'.join(managers)
        contacts = '\n'.join(contacts)
        users_he_linked = '\n'.join(users_he_linked)
        # to_display = None
        if is_manager == "False" and is_linked == "False" and is_private == "False":
            to_display = f"-----Info page:-----\nName: {self.current_chat_name}\n-----Managers:-----\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"

        elif is_manager == "False" and is_linked == "False" and is_private == "True":
            to_display = f"-----Info page:-----\nName: {self.current_chat_name}---(This is a private chat)--\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n"

        elif is_manager == "True" and is_linked == "False":
            to_display = f"-----Info page:-----\nName: {self.current_chat_name}\n-----Managers:--(You are a manager)---\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"
        elif is_manager == "False" and is_linked == "True":
            to_display = f"-----Info page:-----\nName: {self.current_chat_name}--(This is a linked chat)---\n-----Managers:-----\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"
        else:
            to_display = f"-----Info page:-----\nName: {self.current_chat_name}\n-----Managers:-----\n{managers}\n" \
                         f"-----Contacts:--({num_of_contacts})---\n{contacts}\n" \
                         f"-----Users you linked-----\n{users_he_linked}"

        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.insert(END, to_display + "\n")
        self.text_box.config(state=DISABLED)

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
        self.interior.config(bg="#EEEEEE")
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
        # self.write_args_in_file("args.txt")

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
        self.interior.config(bg="#003333")
        # self.write_args_in_file("args.txt")

    def color_theme_hacker(self):
        self.contacts_frame.config(bg="#0F0F0F")
        # self.button_try.config(bd=0)
        # self.canvas.config(bg="#0F0F0F")
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
        self.interior.config(bg="#0F0F0F")

        # self.write_args_in_file("args.txt")

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
        self.interior.config(bg="#263b54")

        # self.write_args_in_file("args.txt")

    def default_format(self):
        self.font_change_default()
        self.color_theme_default()

    def delete_all_in_root(self):
        list = self.all_children(self.master)
        for item in list:
            item.destroy()

    def all_children(self, root):
        _list = root.winfo_children()
        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())
        return _list

    def signed_up(self):
        if self.notification_l:
            self.notification_l.destroy()
        self.notification_l = Label(self.master, text="signed_in successfully", bg='SpringGreen2', width=25)
        self.notification_l.grid(row=5, column=0)
        self.master.update()
        time.sleep(0.25)
        self.delete_all_in_root()
        self.log_in_time()

    def basic_signup_errors(self):
        if self.notification_l:
            self.notification_l.destroy()
        self.notification_l = Label(self.master, text="make sure you filed all\n"
                                                "and the password is\n"
                                                "same as the re_password ", bg='firebrick2', width=25)
        self.notification_l.grid(row=5, column=0)

    def failed_sign_up(self, command):
        text = command.decode('utf-8')
        if self.notification_l:
            self.notification_l.destroy()
        self.notification_l = Label(self.master, text=text, bg='firebrick2', width=25)
        self.notification_l.grid(row=5, column=0)

    def get_username_and_password(self):
        self.username = self.nameEL.get()
        self.password = self.pwordEL.get()
        return self.username, self.password

    def get_username_passwords_and_mail(self):
        email = self.emailE.get()
        username = self.nameE.get()
        password = self.pwordE.get()
        re_password = self.re_pwordE.get()
        if email is not "" and username is not "" and len(password) > 5 and password == re_password:
            return username, password, re_password, email
        else:
            self.basic_signup_errors()
            return None


    def loged_in(self):
        notificationL = Label(self.master, text="log-in ", bg='SpringGreen2', width=18)
        notificationL.grid(row=5, column=0)
        self.delete_all_in_root()
        self.chat_time()

    def failed_log_in(self):
        notificationL = Label(self.master, text='try again', bg='firebrick2', width=25)
        notificationL.grid(row=5, column=0)



    def save_chat(self):
        pass

    def clear_chat(self):
        pass

    # returns the entry value and clears it
    def get_msg(self):
        message = self.entry_field.get()  # the entry value
        msg_to_display = f'{self.local_username}: {message}'
        self.entry_field.delete(0, END)
        if self.mode == 'ENABLE':
            self.insert_to_text_box(msg_to_display)
        if self.mode == 'DISABLE':
            pass
        return message  # the entry value only

    def got_files_in_chat(self, ids, file_names, senders):
        self.files_selection_window = Toplevel(bg=self.tl_bg, )

        self.files_selection_window.bind("<Return>", self.send_message_event)
        selection_frame = Frame(self.files_selection_window, bd=4, bg=self.tl_bg)
        selection_frame.pack()
        self.files_selection_window.focus_set()
        self.files_selection_window.grab_set()

        close_frame = Frame(self.files_selection_window)
        close_frame.pack(side=BOTTOM)
        close_button = Button(close_frame, text="Close", font="Verdana 9", relief=FLAT, bg=self.tl_bg2,
                              fg=self.tl_fg, activebackground=self.tl_bg,
                              activeforeground=self.tl_fg, command=self.close_emoji)
        close_button.pack(side=BOTTOM)

        title = Label(self.files_selection_window, text='Files', bg=self.tl_bg, font="Verdana 16")
        title.pack(side=TOP)

        root_width = self.master.winfo_width()
        root_pos_x = self.master.winfo_x()
        root_pos_y = self.master.winfo_y()
        selection_width_x = self.files_selection_window.winfo_reqwidth()
        selection_height_y = self.files_selection_window.winfo_reqheight()

        position = '250x320' + '+' + str(root_pos_x + root_width - 250) + '+' + str(root_pos_y)
        self.files_selection_window.geometry(position)
        self.files_selection_window.resizable(width=False, height=False)
        # self.emoji_selection_window.minsize(180, 320)
        # self.emoji_selection_window.maxsize(200, 520)

        FilesFrame(self, self.files_selection_window, ids, file_names, senders)

    def open_new_chat_window(self):
        if not self.is_chat_time:
            return
        self.is_chat_time = False
        self.last_right_frame = self.right_frame
        self.chat_frame = self.right_frame
        NewChatInterface(self)

    def open_new_private_chat_window(self):
        if not self.is_chat_time:
            return
        self.is_chat_time = False
        self.last_right_frame = self.right_frame
        self.chat_frame = self.right_frame
        NewPrivateChatInterface(self)

    def _on_mouse(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        if file_path != '':
            split = file_path.split('/')
            file_name = len(split)
            file_name = split[file_name - 1]
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            file_name = "[" + current_time + "]" + file_name
            message_to_display = f'{self.local_username}: sent a file {file_name}'
            self.insert_to_text_box(message_to_display)
            self._choose_file(file_path, file_name)

    def close_emoji(self):
        pass

    def is_exit(self):
        if not self.master:
            self._client_exit()

    @staticmethod
    def run(ip='127.0.0.1', port=8880):
        roots = Tk()
        temp = Interface(roots)
        thread = threading.Thread(target=temp._run)
        thread.start()
        roots.mainloop()
        temp._client_exit()

    def public_mode(self):
        if self.chat_frame:
            self.right_frame.pack_forget()
            self.chat_frame.pack(fill=BOTH, expand=True)
            self.right_frame = self.chat_frame
        self.chat_info_button.configure(text="public")
        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)
        self.file_button.config(state=DISABLED)
        self.emoji_button.config(state=DISABLED)
        self.add_chat_contact.config(state=DISABLED)
        self.exit_chat.config(state=DISABLED)
        self.link_chat.config(state=DISABLED)



    def disable(self):
        self.text_box.config(state=NORMAL)
        self.text_box.delete(1.0, END)
        self.text_box.config(state=DISABLED)

    def send_message_event(self, event):
        self._send()


    def got_public_message(self, message):
        if self.mode == "ENABLE" and self.current_id == 'public':
            self.insert_to_text_box(message)

    def got_private_message(self, message):
        sender = message[1].decode()
        self.chat_id = message[2].decode()
        msg = message[3].decode()
        if self.mode == "ENABLE" and self.current_id == self.chat_id:
            message = f'{sender}: {msg}'
            self.insert_to_text_box(message)
            self.play_message_in_chat_sound()
        else:
            self.button_by_id(self.chat_id).new_msg_arrived()
            self.play_message_out_of_chat_sound()

    def insert_to_text_box(self, message):
        self.text_box.configure(state=NORMAL)
        self.text_box.insert(END, f'{message}\n')
        self.last_sent_label(str(time.strftime("Last message sent: " + '%B %d, %Y' + ' at ' + '%I:%M %p')))
        self.text_box.see(END)
        self.text_box.configure(state=DISABLED)

    def button_by_id(self, chat_id):
        for button in self.buttons:
            if button.chat_id == chat_id:
                return button

    def play_message_in_chat_sound(self):
        mixer.init()
        mixer.music.load('pics/clearly.mp3')
        mixer.music.play()

    def play_message_out_of_chat_sound(self):
        mixer.init()
        mixer.music.load('pics/msg sound 1.mp3')
        mixer.music.play()


if __name__ == '__main__':
    Interface.run()

