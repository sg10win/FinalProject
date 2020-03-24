import time
from tkinter import *
from tkinter.scrolledtext import ScrolledText
#Importing TKinter module
from tkinter import *
from tkinter import ttk
import sys
msg = ""

class NewChatInterface:
    def __init__(self, ChatInterface):
        self.msg = ""
        self.tl_bg = ChatInterface.tl_bg
        self.tl_bg2 = ChatInterface.tl_bg2
        self.tl_fg = ChatInterface.tl_fg
        self.font = ChatInterface.font
        self.added = []
        self.new_chat()




    def filter (self, str):
        if str==None:
            return ""
        while str[0]==" ":
            str = str[1:]
        while str[-1]==" ":
            str = str[:-1]
        return str


    def create (self, nameE, text_boxL, text_boxR, root):
        name = nameE.get()
        added = self.added
        name = self.filter(name)
        if name == "":
            text_boxR.configure(state=NORMAL)
            text_boxR.delete('1.0', END)
            text_boxR.insert(END, "invalid chat name.")
            text_boxR.see(END)
            text_boxR.configure(state=DISABLED)
            return
        if added == None:
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
            global msg
            msg = "create chat%%%"+name+"%%%"+added
            print(msg)
            time.sleep(0.5)
            root.quit()
            root.destroy()


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
                print
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
        print("combobox.get() =|"+combobox.get()+"|")
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
        root.destroy

    def new_chat (self):
        root = Tk()
        root.title("New Chat")
        root.geometry("538x242")
        root.resizable(False, False)

        labelTopL = ttk.Label(root,text="add here: ")
        labelTopL.grid(column=0, row=1)
        comboExampleL = ttk.Combobox(root,width=28,
                                    values=[
                                        "January",
                                        "February",
                                        "March"])
        comboExampleL.grid(column=0, row=2)
        labelTopR = ttk.Label(root, text="remove here: ")
        labelTopR.grid(column=2, row=1)
        comboExampleR = ttk.Combobox(root,width=33,
                                    values=[
                                        "January",
                                        "February",
                                        "April"])
        comboExampleR.grid(column=2, row=2)

        text_frameL = Frame(root, bd=6)
        text_frameL.grid(column=0,row=3, ipadx=20 , ipady=50)

        text_frameR = Frame(root, bd=6)
        text_frameR.grid(column=2, row=3, ipadx=55, ipady=25, pady=0)

        # scrollbar for text box
        text_box_scrollbarL = Scrollbar(text_frameL, bd=0)
        text_box_scrollbarL.pack(fill=Y, side=RIGHT)



        # contains messages
        text_boxL = Text(text_frameL, yscrollcommand=text_box_scrollbarL.set, state=DISABLED,
                             bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                             width=15, height=1)
        text_boxL.pack(expand=True, fill=BOTH)
        text_box_scrollbarL.config(command=text_boxL.yview)

        text_box = Text(text_frameR, state=DISABLED,
                        bd=1, padx=6, pady=6, spacing3=8, wrap=WORD, bg=None, font="Verdana 10", relief=GROOVE,
                        width=5, height=1)
        text_box.pack(expand=True, fill=BOTH)
        createB = Button(root, text="create",relief=GROOVE, bg='white', bd=1, command=lambda: self.create(nameE, text_boxL, text_box, root))
        createB.grid(column=2, row=4)
        cancelB = Button(root, text="cancel",relief=GROOVE, bg='white',
                                  bd=1, command=lambda:self.cancel)
        cancelB.grid(column=0, row=4)
        addB = Button(root, text="add", command=lambda: self.add(text_boxL, comboExampleL, text_box),relief=GROOVE, bg='white', bd=1)
        addB.grid(column=1, row=2)
        removeB = Button(root, text="remove",relief=GROOVE, bg='white', bd=1, command=lambda: self.remove(text_boxL,comboExampleR,text_box))
        removeB.grid(column=4, row=2)

        nameL = Label(text_frameR, text="chat name: ")
        nameE = Entry(text_frameR, width=18)
        nameE.pack(side=BOTTOM)
        nameL.pack(side=BOTTOM)


        #colors and fonts
        root.config(bg=self.tl_bg2)
        text_frameR.config(bg=self.tl_bg2)
        text_frameL.config(bg=self.tl_bg2)
        text_boxL.config(bg=self.tl_bg, fg=self.tl_fg, font=self.font)
        text_box.config(bg=self.tl_bg, fg=self.tl_fg, font=self.font)
        createB.config(bg=self.tl_bg, fg=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg, font=self.font)
        removeB.config(bg=self.tl_bg, fg=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg, font=self.font)
        addB.config(bg=self.tl_bg, fg=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg, font=self.font)
        cancelB.config(bg=self.tl_bg, fg=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg, font=self.font)
        labelTopL.config(background=self.tl_bg, foreground=self.tl_fg, font=self.font)
        labelTopR.config(background=self.tl_bg, foreground=self.tl_fg, font=self.font )
        nameL.config(background=self.tl_bg, foreground=self.tl_fg, font=self.font)
        #comboExampleL.config(background=self.tl_bg, foreground=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg)
        #comboExampleR.config(background=self.tl_bg, foreground=self.tl_fg, activebackground=self.tl_bg, activeforeground=self.tl_fg)
        root.mainloop()

def list_to_str (list,str):
    print(list)
    a = ""
    x=1
    for i in list:
            a = a + i + str
    return a[:-1]