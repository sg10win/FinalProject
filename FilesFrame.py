import time
from tkinter import *
from tkinter import Frame
from tkinter import Button


class FileButton(Button):
    def __init__(self, client, frame, file_id, name, sender):
        self.client = client
        self.frame = frame
        super(FileButton, self).__init__(self.frame, width=23 ,bg="gray99" ,relief=FLAT, text=sender+f": {name}",
                                         command=lambda: self.get_file_value())
        self.file_id = file_id
        self.name = name
        self.sender = sender
        try:
             t = int(file_id)
        except:
            return
        self.pack()

    def get_file_value(self):
        msg = f'get_file_value+*!?{self.client.current_id}+*!?{self.file_id}'
        self.client.messages_to_send.append(msg)
        self.configure(background='firebrick2', text='downloading...')
        self.update()
        time.sleep(5)
        self.configure(bg='gray99', text=self.sender+f": {self.name}")


class FilesFrame(Frame):
    def __init__(self, client, root, ids, file_names, senders):
        super(FilesFrame, self).__init__(root)
        self.client = client
        self.ids = ids
        self.file_names = file_names
        self.senders = senders
        self.files_buttons = []
        self.buttons_frames = []
        self.msg_spliter()

    def msg_spliter(self):
        self.pack()
        self.contacts_scrollbar = Scrollbar(self, orient=VERTICAL)
        self.contacts_scrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

        ids = self.ids.split(',')
        files_names = self.file_names.split(',')
        senders = self.senders.split(',')
        if ids == []:
            label = Label(self.canvas, text="now files sent yet")
            label.pack(side=TOP)
        else:
            self.contacts_scrollbar.config(command=self.canvas.yview)
            for i in range(len(ids)):
                f = Frame(self.canvas)
                self.files_buttons.append(FileButton(self.client, f, ids[i], files_names[i], senders[i]))
                f.pack(padx=10, pady=5, side=TOP)
