import time
from tkinter import *
from tkinter import Frame
from tkinter import Button


class FileButton(Button):
    def __init__(self, client, frame, file_id, name, sender):
        self.client = client
        self.frame = frame
        super(FileButton, self).__init__(self.frame, width=23, bg="gray99", relief=FLAT, text=sender + f": {name}",
                                         command=lambda: self.get_file_value())
        self.file_id = file_id
        self.name = name
        self.sender = sender

        self.pack()

    def get_file_value(self):
        if self.name == "":
            return
        msg = f'get_file_value+*!?{self.client.current_id}+*!?{self.file_id}'
        self.client.messages_to_send.append(msg)
        self.configure(background='firebrick2', text='downloading...')
        self.update()
        time.sleep(1)
        self.configure(bg='gray99', text=self.sender + f": {self.name}")


class FilesFrame(Frame):
    def __init__(self, client, root, ids, file_names, senders):
        super(FilesFrame, self).__init__(root, bg=client.tl_bg2)
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
        self.canvas = Canvas(self, bd=0, highlightthickness=0, bg=self.client.tl_bg)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.contacts_scrollbar.config(command=self.canvas.yview)
        self.canvas.focus_set()

        def _on_mouse(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        self.canvas.bind_all('<MouseWheel>', _on_mouse)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=interior, anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar

        self.interior.bind('<Configure>', self._configure_interior)

        self.canvas.bind('<Configure>', self._configure_canvas)

        ids = self.ids.split(',')
        files_names = self.file_names.split(',')
        senders = self.senders.split(',')
        if ids == []:
            label = Label(self.canvas, text="now files sent yet")
            label.pack(side=TOP)
        else:
            self.contacts_scrollbar.config(command=self.canvas.yview)
            for i in range(len(ids)):
                f = Frame(self.canvas, bg=self.client.tl_bg2)
                self.files_buttons.append(FileButton(self.client, f, ids[i], files_names[i], senders[i]))
                f.pack(padx=10, pady=5, side=TOP)

    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

