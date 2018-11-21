# coding: utf8

"""
MIT License

Copyright (c) 2018, Noryx your fluffy dev ^w^

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import os

from tkinter import *
from tkinter.ttk import Progressbar
from tkinter.messagebox import showerror
from tkinter.filedialog import askdirectory, askopenfilenames

from yiffdex import Yiffdex, YiffdexCache, YiffdexInkbunnyAPI

class YiffdexFrame(Tk):

    def __init__(self):
        super().__init__()

        self.yiffdex = None

        # Main window settings
        self.title("Yiffdex - 1.0b")
        self.resizable(False, False)
        self.maxsize(width=640, height=600)
        self.minsize(width=640, height=600)

        # Variables
        self.filelist = StringVar()

        self.enable_e621 = IntVar(value=1)
        self.enable_inkbunny = IntVar(value=1)
        self.enable_cache = IntVar(value=1)

        self.e621_username = StringVar(value="guest")
        self.inkbunny_username = StringVar(value="guest")
        self.inkbunny_password = StringVar()

        self.progress = DoubleVar(value=0.0)

        self.files = []

        # Protocol handlers
        self.protocol("WM_DELETE_WINDOW", self.event_onclose)

        # Layout build
        self.build()

    def build(self):
        # File / folder list
        list_label_frame = LabelFrame(self, text="File(s) or folder(s) to scan")
        list_label_frame.place(x=5, y=5)
        
        self.list_listbox = Listbox(list_label_frame, listvariable=self.filelist, width=70, height=15)
        self.list_listbox.pack(padx=5, pady=5)

        # List controls
        self.btn_add_folder = Button(self, text="Add folder", width=15, command=self.action_add_folder)
        self.btn_add_folder.place(x=460, y=10)

        self.btn_add_file = Button(self, text="Add file", width=15, command=self.action_add_file)
        self.btn_add_file.place(x=460, y=40)

        self.btn_remove_item = Button(self, text="Remove selected", width=15, command=self.action_remove_item)
        self.btn_remove_item.place(x=460, y=100)

        # e621 settings
        option_e621_labelframe = LabelFrame(self, text="e621 settings")
        option_e621_labelframe.place(x=5, y=290)

        check_e621 = Checkbutton(option_e621_labelframe, text="e621 search", variable=self.enable_e621, command=self.action_check_e621_change)
        check_e621.grid(row=0, column=0, padx=5, pady=5)

        label_e621_username = Label(option_e621_labelframe, text="Username :").grid(row=1, column=0)
        self.input_e621_username = Entry(option_e621_labelframe, textvariable=self.e621_username)
        self.input_e621_username.grid(row=1, column=1, padx=5, pady=5)

        # Inkbunny settings
        option_inkbunny_labelframe = LabelFrame(self, text="Inkbunny settings")
        option_inkbunny_labelframe.place(x=250, y=290)

        check_inkbunny = Checkbutton(option_inkbunny_labelframe, text="Inkbunny search", variable=self.enable_inkbunny, command=self.action_check_inkbunny_change)
        check_inkbunny.grid(row=0, column=0, padx=5, pady=5)

        label_inkbunny_username = Label(option_inkbunny_labelframe, text="Username :").grid(row=1, column=0)
        self.input_inkbunny_username = Entry(option_inkbunny_labelframe, textvariable=self.inkbunny_username)
        self.input_inkbunny_username.grid(row=1, column=1, padx=5, pady=5)

        label_inkbunny_password = Label(option_inkbunny_labelframe, text="Password :").grid(row=2, column=0)
        self.input_inkbunny_password = Entry(option_inkbunny_labelframe, textvariable=self.inkbunny_password, show='*')
        self.input_inkbunny_password.grid(row=2, column=1, padx=5, pady=5)

        # Misc. settings
        option_labelframe = LabelFrame(self, text="Misc.")
        option_labelframe.place(x=520, y=290)

        check_cache = Checkbutton(option_labelframe, text="Cache", variable=self.enable_cache)
        check_cache.grid(row=0, column=0, padx=20, pady=5)

        # Run controls
        self.btn_launch = Button(self, text="Run Yiffdex", command=self.action_launch, width=65, height=3)
        self.btn_launch.place(x=5, y=430)

        self.btn_stop = Button(self, text="Stop", command=self.action_stop, width=20, state=DISABLED, height=3)
        self.btn_stop.place(x=480, y=430)

        # Progress layout
        progress_labelframe = LabelFrame(self, text="Progress")
        progress_labelframe.place(x=5, y=500)

        self.progress_label = Label(progress_labelframe, text="", anchor="w")
        self.progress_label.grid(row=0, column=0, padx=5, pady=3)

        progress_bar = Progressbar(progress_labelframe, orient="horizontal", length=610, variable=self.progress)
        progress_bar.grid(row=1, column=0, padx=5, pady=5)

        # Copyright
        author_label = Label(self, text="developed by Noryx").place(x=520, y=580)
        
    def action_add_file(self, event = None):
        file_tmp = askopenfilenames(title="Select images files", filetypes=[('jpeg files', '.jpg'), ('all files', '*')])
        self.files.extend(file_tmp)
        self.refresh_list()

    def action_add_folder(self, event = None):
        folder_tmp = askdirectory()
        self.files.append(folder_tmp)
        self.refresh_list()

    def action_remove_item(self, event = None):
        items = self.list_listbox.curselection()
        for item in items:
            self.files.remove(self.list_listbox.get(item))
            self.list_listbox.delete(item)

    def action_check_e621_change(self, event = None):
        if self.enable_e621.get() == 1:
            self.input_e621_username['state'] = 'normal'
        else:
            self.input_e621_username['state'] = 'disabled'
    
    def action_check_inkbunny_change(self, event=None):
        if self.enable_inkbunny.get() == 1:
            self.input_inkbunny_username['state'] = 'normal'
            self.input_inkbunny_password['state'] = 'normal'
        else:
            self.input_inkbunny_username['state'] = 'disabled'
            self.input_inkbunny_password['state'] = 'disabled'

    def action_launch(self, event = None):
        self.disable_run()

        # Initialize caching
        cache = YiffdexCache('yiffdex.cache')
        cache.load()

        # Create yiffdex instance
        self.yiffdex = Yiffdex(cache=cache)

        # Get list of all files that will be tagged
        self.yiffdex.files = []
        for f in self.files:
            if os.path.isfile(f):
                self.yiffdex.files.append(f)
            elif os.path.isdir(f):
                self.yiffdex.files.extend([os.path.join(f, filename) for filename in os.listdir(f) if os.path.isfile(os.path.join(f, filename)) and (os.path.splitext(filename)[1].lower() == '.jpg' or os.path.splitext(filename)[1].lower() == '.jpeg')])

        # Accounts credentials
        self.yiffdex.e621 = self.enable_e621.get() == 1
        self.yiffdex.e621_username = self.e621_username.get()

        # Inkbunny API Initialization
        inkbunny_api = None

        if self.enable_inkbunny.get() == 1:
            inkbunny_api = YiffdexInkbunnyAPI()
            login_result = inkbunny_api.login(self.inkbunny_username.get(), self.inkbunny_password.get())
            
            if login_result is False:
                showerror("Yiffdex", "Can't connect to Inkbunny with the specified credentials.")
                self.enable_run()
                return

        self.yiffdex.inkbunny = inkbunny_api

        # Set additionals params
        self.yiffdex.force = self.enable_cache.get() == 0
        self.yiffdex.prescan_callback = [self.event_onprescan]
        self.yiffdex.scan_callback = [self.event_onscan]

        # Run
        self.yiffdex.stop = False
        self.yiffdex.start()

    def action_stop(self, event = None):
        self.yiffdex.stop = True
        try:
            self.yiffdex.join(timeout=3)
        except RuntimeError:
            pass
        self.progress_label['text'] = 'Aborted.'
        self.enable_run()

    def refresh_list(self):
        self.list_listbox.delete(0, END)
        i = 0
        for f in self.files:
            self.list_listbox.insert(i, f)
            i = i + 1

    def event_onprescan(self, file):
        if len(file) > 100:
            file = file[:45] + '...' + file[-45:]
        self.progress_label['text'] = file + ' ...'

    def event_onscan(self, event):
        self.progress.set(self.yiffdex.get_percent_progress())

        # If done
        if self.progress.get() >= 100.0:
            self.progress_label['text'] = 'Done.'
            if self.yiffdex.inkbunny is not None:
                self.yiffdex.inkbunny.logout()
            self.enable_run()

    def event_onclose(self):
        if self.yiffdex is not None and self.yiffdex.isAlive() is True:
            self.yiffdex.stop = True
            self.yiffdex.join(timeout=5)
        self.destroy()

    def disable_run(self):
        self.btn_launch['state'] = 'disabled'
        self.btn_stop['state'] = 'normal'

    def enable_run(self):
        self.btn_launch['state'] = 'normal'
        self.btn_stop['state'] = 'disabled'