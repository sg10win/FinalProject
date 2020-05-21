from tkinter import *
from tkinter import ttk

msg = ""


class NewChatInterface:
    def __init__(self, ChatInterface):
        self.ChatInterface = ChatInterface
        self.last_frame = None
        self.msg = ""
        self.tl_bg = ChatInterface.tl_bg
        self.tl_bg2 = ChatInterface.tl_bg2
        self.tl_fg = ChatInterface.tl_fg
        self.font = ChatInterface.font
        self.added = []
        self.new_chat()




    def filter (self, str):
        try:
            if str==None:
                return ""
            while str[0]==" ":
                str = str[1:]
            while str[-1]==" ":
                str = str[:-1]
            return str
        except:
            return str


    def create(self, nameE, text_boxL, text_boxR, root):
        name = nameE.get()
        added = self.added
        name = self.filter(name)
        if name == "" or ',' in name:
            text_boxR.configure(state=NORMAL)
            text_boxR.delete('1.0', END)
            text_boxR.insert(END, "Invalid chat name.\nNo ',' allow")
            text_boxR.see(END)
            text_boxR.configure(state=DISABLED)
            return
        elif added is None or added is []:
            text_boxR.configure(state=NORMAL)
            text_boxR.delete('1.0', END)
            text_boxR.insert(END, "no contacts added")
            text_boxR.see(END)
            text_boxR.configure(state=DISABLED)
            return
        else:
            added =  list_to_str(added, ',')
            text_boxR.configure(state=NORMAL)
            text_boxR.delete('1.0', END)
            text_boxR.insert(END, "the chat was created.")
            text_boxR.see(END)
            text_boxR.configure(state=DISABLED)
            msg = "create chat+*!?"+name+"+*!?"+added+","+self.ChatInterface.username
            self.ChatInterface.messages_to_send.append(msg)
            print(self.ChatInterface.messages_to_send)
            print(msg)
            self.cancel(root)



    def remove(self, text_boxL, combobox ,text_boxR):
        if combobox.get() is None or combobox.get() == "":
            return
        contact = combobox.get()
        if contact in self.added:
            self.added.remove(contact)
            text_boxL.configure(state=NORMAL)
            text_boxL.delete("1.0", END)
            try:
                text_boxL.insert(END, "\n".join(self.added))
            except:
                pass
            text_boxL.configure(state=DISABLED)
            text_boxR.configure(state=NORMAL)
            text_boxR.delete("1.0", END)
            text_boxR.insert(INSERT, contact + " removed")
            text_boxR.configure(state=DISABLED)
            combobox.set('')
        else:
            text_boxR.configure(state=NORMAL)
            text_boxR.delete('1.0', END)
            text_boxR.insert(INSERT, contact + " not in the add list")
            text_boxR.configure(state=DISABLED)

    def add(self, text_boxL, combobox, text_boxR):

        if not combobox.get() == "":
            contact = combobox.get()
            if combobox.get() not in self.added:
                self.added.append(contact)
                text_boxL.configure(state=NORMAL)
                text_boxL.insert(END, contact+"\n")
                text_boxL.see(END)
                text_boxL.configure(state=DISABLED)
                text_boxR.configure(state=NORMAL)
                text_boxR.delete('1.0', END)
                text_boxR.insert(INSERT, contact+" added")
                text_boxR.configure(state=DISABLED)
                combobox.set("")
            else:
                text_boxR.configure(state=NORMAL)
                text_boxR.delete('1.0', END)
                text_boxR.insert(INSERT, contact + " already added")
                text_boxR.configure(state=DISABLED)
                combobox.set('')

    def cancel(self, root):
        self.ChatInterface.is_chat_time = True
        #self.nameE.insert(0, "")
        self.ChatInterface.right_frame = self.last_frame
        root.pack_forget()
        self.last_frame.pack(fill=BOTH, expand=True)
        self.ChatInterface.text_box.configure(state=NORMAL)
        self.ChatInterface.text_box.delete(1.0, END)
        self.ChatInterface.text_box.configure(state=DISABLED)

    def new_chat(self):
        self.ChatInterface.mode = "DISABLE"
        self.last_frame = self.ChatInterface.chat_frame
        self.ChatInterface.last_right_frame = self.last_frame
        root = Frame(self.ChatInterface.master)
        self.ChatInterface.right_frame = root
        self.last_frame.pack_forget()
        root.pack(fill=BOTH, expand=True)

        left = Frame(root)
        left.grid(column=0, row=1)

        comboExampleL = ttk.Combobox(left,width=28,
                                    values=[])
        comboExampleL.grid(column=0, row=2)
        comboExampleR = ttk.Combobox(left,width=28,
                                    values=[])
        comboExampleR.grid(column=0, row=3)

        text_frameL = Frame(left, bd=0)
        text_frameL.grid(column=0,row=4, ipadx=20 , ipady=50)

        text_frameR = Frame(root, bd=0)
        text_frameR.grid(column=1, row=1,sticky="w")

        # scrollbar for text box
        text_box_scrollbarL = Scrollbar(text_frameL, bd=0)
        text_box_scrollbarL.pack(fill=Y, side=RIGHT)



        # contains messages
        text_boxL = Text(text_frameL, yscrollcommand=text_box_scrollbarL.set, state=DISABLED,
                             bd=0, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=15, height=1)
        text_boxL.pack(expand=True, fill=BOTH)
        text_box_scrollbarL.config(command=text_boxL.yview)

        text_box = Text(text_frameR, state=DISABLED,
                        width=15,bd=0, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE, height=5)
        text_box.pack()
        createB = Button(left, width=10, text="create",relief=FLAT, bg='green2', bd=0, command=lambda: self.create(nameE, text_boxL, text_box, root))
        createB.grid(column=1, row=6, sticky="w")
        cancelB = Button(left, width=10, text="cancel",relief=FLAT, bg='red',
                                  bd=0, command=lambda:self.cancel(root))
        cancelB.grid(column=0, row=6)
        addB = Button(left, text="add", command=lambda: self.add(text_boxL, comboExampleL, text_box),relief=FLAT, bg="green2", bd=0, width=6)
        addB.grid(column=1, row=2)
        removeB = Button(left, text="remove",relief=FLAT, bg='red', bd=0, command=lambda: self.remove(text_boxL,comboExampleR,text_box))
        removeB.grid(column=1, row=3)

        #nameL = Label(left, text="Chat name: ")
        nameE = Entry(left,width=30,text="Chat name")
        nameE.grid(column=0, row=5, sticky="w")
        #nameL.grid(column=0, row=5,sticky="w")

        title_l = Label(root, text="New group", font=(self.font, 16))
        title_l.grid(column=0, row=0)


        #







        #colors and fonts
        root.config(bg=self.tl_bg2)
        text_frameR.config(bg=self.tl_bg2)
        text_frameL.config(bg=self.tl_bg2)
        text_boxL.config(bg=self.tl_bg, fg=self.tl_fg, font=self.font)
        text_box.config(bg=self.tl_bg, fg=self.tl_fg, font=self.font)
        left.config(bg=self.tl_bg2)
        title_l.config(bg=self.tl_bg, fg=self.tl_fg)
        root.mainloop()

def on_entry_click(event, entry, text):
    """function that gets called whenever entry is clicked"""
    if entry.get() == text:
       entry.delete(0, "end") # delete all the text in the entry
       entry.insert(0, '') #Insert blank for user input
       entry.config(fg = 'black')
def on_focusout(event, entry, text):
    if entry.get() == '':
        entry.insert(0, text)
        entry.config(fg = 'grey')




def list_to_str (list,str):
    print(list)
    a = ""
    x=1
    for i in list:
            a = a + i + str
    return a[:-1]