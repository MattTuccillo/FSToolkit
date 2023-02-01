#To Do List
# -add video controls bar
# -sorting listbox for directory (try to fix numerical sorting in default sort operation)

# BUGS
# -can't change directory during mid video play (while stopped might be different)      add video controls first
# -can't rename while playing video(while stopped might be different)                   add video controls first
import os, vlc
import tkinter as tk
from TkinterDnD2 import *
from PIL import Image, ImageTk
from send2trash import send2trash

class MainWindow:
    def __init__(self, master):
        # Master Frame
        #   [   Top Frame,
        #       Bottom Frame    ]
        self.master = master
        self.master.title("File Sampler Toolkit")
        self.master.minsize(int(master.winfo_screenwidth() * .4), int(master.winfo_screenheight() * .4))
        self.centerScreenX = int((master.winfo_screenwidth() / 2.0) - (master.winfo_screenwidth() * .2))
        self.centerScreenY = int((master.winfo_screenheight() / 2.0) - (master.winfo_screenheight() * .2))
        self.master.geometry("+" + str(self.centerScreenX) + "+" + str(self.centerScreenY))

        # Top Frame 
        #   [   Directory Display Frame,
        #       Display Frame               ]
        self.top_Frame = tk.Frame(self.master)
        self.top_Frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Directory Frame
        #   [   Directory Search Bar,
        #       Directory ListBox,
        #       Directory Scrollbar  ]
        self.dir_Frame = tk.Frame(self.top_Frame, bg = "white")
        self.dir_Frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # Directory Search Bar
        self.search_bar = tk.StringVar()
        self.search_bar.trace('w', self.updateDirListBox)
        self.search_bar_Entry = tk.Entry(self.dir_Frame, font=("Arial", 12), textvariable=self.search_bar, bg="light blue")
        self.search_bar_Entry.pack(side=tk.TOP, fill=tk.X)
        self.search_bar_Entry.bind("<FocusIn>", self.DisableButtonBinds)
        self.search_bar_Entry.bind("<FocusOut>", self.EnableButtonBinds)
        self.lb_reverse_tickbox=False
        self.sort_algorithm=sortAlphabetical
        
        # Directory List Box
        self.dir_ListBox = tk.Listbox(self.dir_Frame, width=35, bg = "light yellow", selectmode=tk.SINGLE, exportselection=False)
        self.curr_dir = ''
        self.curr_fext = ''
        self.curr_fp = ''
        self.supportedEXTs = ['.txt', '.jpg', '.png', '.jpeg', '.bmp', '.mp4', '.avi', '.flv', '.m4v', '.mkv', '.mov', '.wmv', '.webm']
        self.dir_ListBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dir_ListBox.bind("<Down>", self.OnLBUpDown)
        self.dir_ListBox.bind("<Up>", self.OnLBUpDown)
        self.dir_ListBox.bind("<Left>", lambda event: "break")
        self.dir_ListBox.bind("<Right>", lambda event: "break")
        self.dir_ListBox.bind("<<ListboxSelect>>", self.listbox_selection_change)

        # Directory Scrollbar
        self.dir_Scrollbar = tk.Scrollbar(self.dir_Frame, orient=tk.VERTICAL) 
        self.dir_Scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.dir_ListBox.configure(yscrollcommand=self.dir_Scrollbar.set)
        self.dir_Scrollbar.config(command=self.dir_ListBox.yview)

        # Display Frame
        #   [   File Display Textbox,
        #       File Display Scrollbar,
        #       Error Message Display,
        #       File Image Display,
        #       File Video Display  ]
        self.display_Frame = tk.Frame(self.top_Frame, bg = "white")
        self.display_Frame.drop_target_register(DND_FILES)
        self.display_Frame.dnd_bind("<<Drop>>", self.display_directory)
        self.display_Frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.display_Frame.pack_propagate(False)

        # File Display Textbox
        self.display_Textbox = tk.Text(self.display_Frame, bg = "white")
        self.display_Textbox.drop_target_register(DND_FILES)
        self.display_Textbox.dnd_bind("<<Drop>>", self.display_directory)
        self.display_Textbox.bind("<FocusIn>", self.DisableButtonBinds)
        self.display_Textbox.bind("<FocusOut>", self.EnableButtonBinds)

        # File Textbox Scrollbar
        self.display_Scrollbar = tk.Scrollbar(self.display_Frame, orient=tk.VERTICAL) 
        self.display_Textbox.configure(yscrollcommand=self.display_Scrollbar.set)
        self.display_Scrollbar.config(command=self.display_Textbox.yview)

        # Error Message Display
        self.error_Label = tk.Label(self.display_Frame, bg = "white", text="Drag a Directory Here To Open It", justify=tk.CENTER, anchor=tk.CENTER)
        self.error_Label.drop_target_register(DND_FILES)
        self.error_Label.dnd_bind("<<Drop>>", self.display_directory)
        self.error_Label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # File Image Display
        self.display_Canvas = tk.Canvas(self.display_Frame, bg = "black")
        self.display_Canvas.drop_target_register(DND_FILES)
        self.display_Canvas.dnd_bind("<<Drop>>", self.display_directory)
        self.display_Canvas.bind("<Configure>", self.IMGcanvasResize)
        self.img_fopen = None
        self.img_photoimage = None
        self.curr_image = None

        # File Video Display
        self.video_Frame = tk.Frame(self.display_Frame, bg = "black")
        self.video_Frame.drop_target_register(DND_FILES)
        self.video_Frame.dnd_bind("<<Drop>>", self.display_directory)
        self.video_instance = None
        self.video_player = None
        self.video_media = None

        # Bottom Frame
        #   [   Open File Button,
        #       Clear Display Button,  
        #       Rename File Button,
        #       Delete File Button     ]
        self.bottom_Frame = tk.Frame(self.master, bg="gray")
        self.bottom_Frame.pack(side=tk.TOP, fill=tk.X)

        # Open File Button
        self.openFile_Button = tk.Button(self.bottom_Frame, text="Open", width=12, height=2, command=self.openFile)
        self.openFile_Button.pack(side=tk.LEFT)
        
        # Clear Display Button
        self.clearLB_Button = tk.Button(self.bottom_Frame, text="Clear", width=12, height=2, command=self.clearAll)
        self.clearLB_Button.pack(side=tk.LEFT)

        # Rename File Button
        self.renameFile_Button = tk.Button(self.bottom_Frame, text="Rename", width=12, height=2, command=self.renamePopUp)
        self.renameFile_Button.pack(side=tk.LEFT)

        # Delete File Button
        self.deleteFile_Button = tk.Button(self.bottom_Frame, text="Delete", width=12, height=2, command=self.deleteFile)
        self.deleteFile_Button.pack(side=tk.LEFT)

        self.DisableAllButtons()


    # Displays Files Within The Directory That is Dropped onto File Display Label
    def display_directory(self, event=None):
        fp = ""
        if event==None:
            fp = self.curr_dir + "/" + self.curr_fp
        else:
            fp = event.data
        if fp[0] == '{' and fp[-1] == '}':
            fp = fp[1:-1]
        if self.curr_dir == fp:
            return
        else:
            if os.path.isdir(fp):
                self.clearAll()
                self.curr_dir = fp
                dir_list=self.sort_algorithm(os.listdir(fp), self.lb_reverse_tickbox)
                for f in dir_list:
                    self.dir_ListBox.insert(tk.END, f)
                if self.dir_ListBox.size() == 0:
                    self.DisableAllButtons()
                    self.clearLB_Button.configure(state='normal')
                    self.error_Label.configure(text="Directory is Empty")
                else:
                    self.dir_ListBox.select_set(0)
                    self.listbox_selection_change(event=NONE)
                    self.EnableAllButtons()
                self.dir_ListBox.focus()
    
    # Listbox Up/Down Arrow Key Navigation Event
    def OnLBUpDown(self, event):
        selection = event.widget.curselection()[0]
        if event.keysym == 'Up':
            selection += -1
        if event.keysym == 'Down':
            selection += 1
        if 0 <= selection < event.widget.size():
            event.widget.selection_clear(0, tk.END)
            event.widget.select_set(selection)
        self.listbox_selection_change(event='<<ListboxSelect>>')

    # Listbox selection change
    def listbox_selection_change(self, event):
        fp = ''
        for i in self.dir_ListBox.curselection():
            fp = str(self.dir_ListBox.get(i))
        self.master.title("File Sampler Toolkit: " + fp)
        if fp == self.curr_fp:
            return
        self.check_file_type(os.path.splitext(fp))

    # Check File Type
    def check_file_type(self, fp):
        self.EnableButtonBinds()
        if (str(fp[1]).lower() == ".txt"):
            self.openTXT(fp)
        elif (str(fp[1]).lower() in [".jpg", ".png", ".jpeg", ".bmp"]):
            self.openIMG(fp, float(self.display_Frame.winfo_width()), float(self.display_Frame.winfo_height()))
        elif (str(fp[1]).lower() in [".mp4", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".wmv", ".webm"]):
            self.openVIDEO(fp)
        else:
            self.openERROR(fp)

    # Open Text File
    def openTXT(self, fp):
        self.DisableButtonBinds()
        fileDir = str(self.curr_dir) + "/" + str(fp[0] + fp[1])
        f = open(fileDir, "r+")
        data = f.read()
        if str(self.curr_fext).lower() != ".txt":
            self.clear_display()
            self.display_Textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.display_Scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.clear_textbox()
        self.display_Textbox.insert('end', data)
        self.curr_fp = str(fp[0] + fp[1])
        self.curr_fext = str(fp[1])
   
    # Open IMG File
    def openIMG(self, fp, winWidth, winHeight):
        fileDir = str(self.curr_dir) + "/" + str(fp[0] + fp[1])
        if (str(self.curr_fext)).lower() not in [".jpg", ".png", ".jpeg", ".bmp"]:
            self.clear_display()
            self.display_Canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.curr_image = self.display_Canvas.create_image(((self.display_Frame.winfo_width()/2), (self.display_Frame.winfo_height()/2)))
        imgFile = self.resizeIMG(Image.open(fileDir), winWidth, winHeight)
        img = ImageTk.PhotoImage(imgFile)
        self.img_fopen = imgFile
        self.img_photoimage = img
        self.display_Canvas.itemconfig(self.curr_image, image=self.img_photoimage)
        self.curr_fp = str(fp[0] + fp[1])
        self.curr_fext = str(fp[1])

    def openVIDEO(self, fp):
        self.clear_video()
        fileDir = str(self.curr_dir) + "/" + str(fp[0] + fp[1])
        if str(self.curr_fext).lower() not in [".mp4", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".wmv", ".webm"]:
            self.clear_display()
            self.video_Frame.pack(fill=tk.BOTH, expand=True)
            self.video_Frame.bind('<Enter>', self.videoControls)
            self.video_Frame.bind('<Leave>', lambda e: self.vControls_Window.destroy())
        self.video_instance = vlc.Instance()
        self.video_player = self.video_instance.media_player_new()
        self.video_media = self.video_instance.media_new(fileDir)
        self.video_player.set_hwnd(self.video_Frame.winfo_id())
        self.video_player.set_media(self.video_media)
        self.curr_fp = str(fp[0] + fp[1])
        self.curr_fext = str(fp[1])
        self.video_player.play()
    
    # Open Video Controls
    def videoControls(self, event=None):
        try:
            if self.vControls_Window.winfo_exists(): return
        except: pass
        self.master.bind("<Configure>", self.sync_vcontrols)
        width = str(int(self.display_Frame.winfo_width()))
        height = str(int(self.bottom_Frame.winfo_height() * 2.0))
        xPosition = str(int(self.display_Frame.winfo_rootx()))
        yPosition = str(int(self.display_Frame.winfo_rooty() + self.display_Frame.winfo_height() - float(height)))

        self.vControls_Window = tk.Toplevel(self.master, pady = 10, bg="black")
        self.vControls_ButtonFrame = tk.Frame(self.vControls_Window, bg="black")
        self.vControls_PlayButton = tk.Button(self.vControls_ButtonFrame, text="Play", width=8, height=1, command=self.renamePopUp_Confirm)
        self.vControls_StopButton = tk.Button(self.vControls_ButtonFrame, text="Stop", width=8, height=1, command=self.renamePopUp_Cancel)
        self.vControls_ButtonFrame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.vControls_PlayButton.pack(padx=12)
        self.vControls_StopButton.pack(padx=12)
        self.vControls_Window.geometry(width + "x" + height + "+" + xPosition + "+" + yPosition)
        self.vControls_Window.overrideredirect(True)
        self.vControls_Window.bind('<Enter>', self.videoControls)
        self.vControls_Window.bind('<Leave>', lambda e: self.vControls_Window.destroy())

    # Display Invalid File Message
    def openERROR(self, fp):
        if fp[1] not in self.supportedEXTs:
            self.clear_display()
            self.error_Label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.error_Label.configure(text="Choose a compatible file type to display")
        self.curr_fp = str(fp[0] + fp[1])
        self.curr_fext = str(fp[1])
        
    # Clears the Current Directory Information
    def clear_directory(self):
        if self.curr_dir != "":
            self.dir_ListBox.delete("0",tk.END)
            self.curr_dir = ""
            self.curr_fp = ""
            self.curr_fext = ""
            self.search_bar_Entry.delete(0, tk.END)
            self.master.title("File Sampler Toolkit")
            self.DisableAllButtons()

    # Clears the display window widgets
    def clear_display(self):
        self.clear_textbox()
        self.clear_image()
        self.clear_video()
        self.display_Textbox.pack_forget()
        self.display_Scrollbar.pack_forget()
        self.display_Canvas.pack_forget()
        self.video_Frame.pack_forget()
        self.error_Label.pack_forget()

    # Clears the Textbox Display
    def clear_textbox(self):
        self.display_Textbox.delete('1.0', tk.END)

    # Clears the Image Canvas
    def clear_image(self):
        self.img_fopen = None
        self.img_photoimage = None
        self.display_Canvas.itemconfig(self.curr_image, image = '')

    # Clears the Video Canvas
    def clear_video(self):
        if self.video_player is not None:
            self.video_player.stop()
        self.video_instance = None
        self.video_player = None
        self.video_media = None

    # Clears All Fields
    def clearAll(self):
        self.clear_display()
        self.clear_directory()
        self.error_Label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.error_Label.configure(text="Drag a Directory Here To Open It")
    
    # Open Rename File PopUp
    def renamePopUp(self, event=None):
        self.master.bind("<Configure>", self.sync_popups)
        width = str(int(self.display_Frame.winfo_width()))
        height = str(int(self.bottom_Frame.winfo_height() * 2.0))
        xPosition = str(int(self.display_Frame.winfo_rootx()))
        yPosition = str(int(self.display_Frame.winfo_rooty() + self.display_Frame.winfo_height() - float(height)))
        self.confirm_rename = tk.StringVar()
        self.confirm_rename.trace('w', self.checkForInvalidEntry)

        self.renameFile_Window = tk.Toplevel(self.master, pady = 10, bg="black")
        self.renameFile_InputFrame = tk.Frame(self.renameFile_Window, bg="black")
        self.renameFile_ButtonFrame = tk.Frame(self.renameFile_Window, bg="black")
        self.renameFile_Entry = tk.Entry(self.renameFile_InputFrame, font=("Arial", 12), textvariable=self.confirm_rename)
        self.renameFile_StatusLabel = tk.Label(self.renameFile_ButtonFrame, bg="light yellow", font=("Arial", 12), fg="black", anchor=tk.W)
        self.renameFile_ConfirmButton = tk.Button(self.renameFile_ButtonFrame, text="Confirm", width=8, height=1, command=self.renamePopUp_Confirm)
        self.renameFile_CancelButton = tk.Button(self.renameFile_ButtonFrame, text="Cancel", width=8, height=1, command=self.renamePopUp_Cancel)
        self.renameFile_Window.pack(fill=tk.X, expand=True)
        self.renameFile_InputFrame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.renameFile_ButtonFrame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.renameFile_Window.overrideredirect(True)
        self.renameFile_Entry.pack(fill=tk.X, padx=12)
        self.renameFile_ConfirmButton.pack(side=tk.LEFT, padx=12)
        self.renameFile_CancelButton.pack(side=tk.LEFT, padx=12)
        self.renameFile_StatusLabel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)
        self.renameFile_Window.geometry(width + "x" + height + "+" + xPosition + "+" + yPosition)
        self.renameFile_Window.grab_set()
        self.DisableAllButtons()
        self.dir_ListBox.configure(state='disabled')
        self.renameFile_Entry.insert(0, os.path.splitext(self.curr_fp)[0])
        self.renameFile_safeFlag = True
        self.renameFile_Entry.focus()
        self.renameFile_Entry.selection_range(0, tk.END)
        self.renameFile_Window.bind("<Escape>", self.renamePopUp_Cancel)
        self.renameFile_Window.bind("<Return>", self.renamePopUp_Confirm)

    # Make Sure Rename Text Entry Is Valid
    def checkForInvalidEntry(self, *args):
        illegal_list = ['#', '<', '$', '+', '%', '>', '!', '`', '&', '*', '|', '{', '}', '?', '"', '=', '/', ':', '\\', '@']
        chars_found = "[ "
        counter=0
        txt = self.confirm_rename.get()
        if txt == "":
            err_msg = "Cannot leave blank."
            self.renameFile_StatusLabel.config(text=err_msg)
            self.renameFile_safeFlag = False
            return
        if txt[0].isspace():
            txt = txt[1:]
            self.renameFile_Entry.delete(0, tk.END)
            self.renameFile_Entry.insert(0, txt)
            return
        if txt.lower() != os.path.splitext(self.curr_fp)[0].lower() and (txt.lower() + self.curr_fext.lower()) in (f.lower() for f in os.listdir(self.curr_dir)):
            err_msg = "Duplicate file name."
            self.renameFile_StatusLabel.config(text=err_msg)
            self.renameFile_safeFlag = False
            return
        for x in illegal_list:
            if txt.count(x) > 0:
                counter+=txt.count(x)
                chars_found += x + ", "
        if counter > 0:
            chars_found = chars_found[:len(chars_found)-2]
            chars_found += " ]"
            err_msg = str(counter) + " illegal characters found.\t" + chars_found
            self.renameFile_StatusLabel.config(text=err_msg)
            self.renameFile_safeFlag = False
            return
        self.renameFile_StatusLabel.config(text="Acceptable Name")
        self.renameFile_safeFlag = True

    # Rename File On Confirmation, Check For Duplicate Names
    def renamePopUp_Confirm(self, event=None):
        if self.renameFile_Entry.get() == os.path.splitext(self.curr_fp)[0]:
            self.renamePopUp_Cancel()
            return
        if self.renameFile_safeFlag == True:
            currfp = str(self.curr_dir + "/" + self.curr_fp)
            newfp = str(self.curr_dir + "/" + self.confirm_rename.get() + self.curr_fext)
            self.clear_video()
            os.rename(currfp, newfp)
            self.dir_ListBox.configure(state='normal')
            self.dir_ListBox.delete("0",tk.END)
            count=0
            dir_list=self.sort_algorithm(os.listdir(self.curr_dir), self.lb_reverse_tickbox)
            for f in dir_list:
                if f == str(self.confirm_rename.get() + self.curr_fext):
                    index = count
                self.dir_ListBox.insert(tk.END, f)
                count+=1
            if self.curr_fext in [".mp4", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".wmv"]:
                self.video_Frame.pack(fill=tk.BOTH, expand=True)
            fp = (str(self.confirm_rename.get()), str(self.curr_fext))
            self.master.title("File Sampler Toolkit: " + str(self.confirm_rename.get()) + str(self.curr_fext))
            self.dir_ListBox.selection_set(index)
            self.check_file_type(fp)
            self.renameFile_Window.destroy()
            self.EnableAllButtons()
            self.master.unbind("<Configure>")
    
    # Destroy Rename File PopUp Window And Re-Enable Buttons
    def renamePopUp_Cancel(self, event=None):
        self.renameFile_Window.destroy()
        self.EnableAllButtons()
        self.dir_ListBox.configure(state='normal')
        self.master.unbind("<Configure>")

    # Sends A File To Recycle Bin
    def deleteFile(self, event=None):
        if self.curr_fp != "":
            currdir = str(self.curr_dir)
            currfp = str(self.curr_fp)
            index = self.dir_ListBox.curselection()[0]
            self.dir_ListBox.delete(index)
            if index == self.dir_ListBox.size():
                index = index-1
            self.dir_ListBox.selection_set(index)
            self.listbox_selection_change(event=None)
            os.chdir(currdir)
            send2trash(currfp)
        if self.dir_ListBox.size() == 0:
            self.DisableAllButtons()
            self.clearLB_Button.configure(state='normal')
            self.error_Label.configure(text="Directory is Empty")

    def openFile(self, event=None):
        fileDir=self.curr_dir + "/" + self.curr_fp
        if os.path.isdir(fileDir):
            self.display_directory()
        else:
            os.startfile(fileDir)

    # Enable shortcut button binds
    def EnableButtonBinds(self, event=None):
        self.master.bind('<Return>', self.openFile)
        self.master.bind('r', self.renamePopUp)
        self.master.bind('d', self.deleteFile)
        self.master.bind('c', self.clearAll)

    # Disable shortcut button binds while a text file is open
    def DisableButtonBinds(self, event=None):
        self.master.bind('<Return>')
        self.master.unbind('r')
        self.master.unbind('d')
        self.master.unbind('c')

    # Change All Bottom Frame Buttons To Disabled State
    def DisableAllButtons(self, event=None):
        self.DisableButtonBinds()
        self.openFile_Button.configure(state='disabled')
        self.clearLB_Button.configure(state='disabled')
        self.renameFile_Button.configure(state='disabled')
        self.deleteFile_Button.configure(state='disabled')

    # Change All Bottom Frame Buttons To Active State
    def EnableAllButtons(self, event=None):
        self.EnableButtonBinds()
        self.openFile_Button.configure(state='normal')
        self.clearLB_Button.configure(state='normal')
        self.renameFile_Button.configure(state='normal')
        self.deleteFile_Button.configure(state='normal')

    # Image File Resize
    def resizeIMG(self, pic, winWidth, winHeight):
        picWidth = float(pic.width)
        picHeight = float(pic.height)
        wScale = winWidth / picWidth
        hScale = winHeight / picHeight
        minScale = min(wScale, hScale)
        minRes = min(winWidth, winHeight)
        if picWidth != picHeight:
            return pic.resize((int(picWidth * minScale), int(picHeight * minScale)))
        else:
            return pic.resize((int(minRes), int(minRes)))
    
    # Resize Image on Canvas Resize
    def IMGcanvasResize(self, event):
        drop = len(self.curr_fp) - len(self.curr_fext)
        fp = (self.curr_fp[:drop], self.curr_fext)
        self.openIMG(fp, event.width, event.height)

    # Keep PopUp Windows Attached To Window
    def sync_popups(self, event):
        #sync rename popup
        width = str(int(self.display_Frame.winfo_width()))
        height = str(int(self.bottom_Frame.winfo_height() * 2.0))
        xPosition = str(int(self.display_Frame.winfo_rootx()))
        yPosition = str(int(self.display_Frame.winfo_rooty() + self.display_Frame.winfo_height() - float(height)))
        self.renameFile_Window.geometry(width + "x" + height + "+" + xPosition + "+" + yPosition)
    
    # Keep PopUp Windows Attached To Window
    def sync_vcontrols(self, event):
        #sync rename popup
        width = str(int(self.display_Frame.winfo_width()))
        height = str(int(self.bottom_Frame.winfo_height() * 2.0))
        xPosition = str(int(self.display_Frame.winfo_rootx()))
        yPosition = str(int(self.display_Frame.winfo_rooty() + self.display_Frame.winfo_height() - float(height)))
        self.vControls_Window.geometry(width + "x" + height + "+" + xPosition + "+" + yPosition)

    # Update Directory Listbox On Search Bar Text Entry
    def updateDirListBox(self, *args):
        txt = self.search_bar.get()
        if txt == "":
            dir_list=self.sort_algorithm(os.listdir(self.curr_dir), self.lb_reverse_tickbox)
            for f in dir_list:
                self.dir_ListBox.insert(tk.END, f)
            return
        if txt[0].isspace():
            txt = txt[1:]
            self.search_bar_Entry.delete(0, tk.END)
            self.search_bar_Entry.insert(0, txt)
            return
        if self.curr_dir == '':
            return
        self.dir_ListBox.delete("0",tk.END)
        if txt != "":
            dir_list=self.sort_algorithm(os.listdir(self.curr_dir), self.lb_reverse_tickbox)
            for f in dir_list:
                if txt.lower() in f.lower():
                    self.dir_ListBox.insert(tk.END, f)
            return

# Sort Alphabetical
def sortAlphabetical(file_list, rev):
    return sorted(file_list, reverse=rev, key=lowerCase)

def lowerCase(string):
    return string.lower()

# Sort Size

# Sort Date Added
        
                        



def main():
    root = TkinterDnD.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()