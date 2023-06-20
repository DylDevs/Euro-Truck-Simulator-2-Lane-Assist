"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="ShowImageTransparent", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="Will show a transparent window of the input image.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="dynamic", # = Panel
    dynamicOrder="before controller",
    noUI=True, # Will not show the UI button
)

import tkinter as tk
from tkinter import ttk
import src.settings as settings
from PIL import Image, ImageTk
import numpy as np


def plugin(data):
    global img
    global root
    
    try:
        if root.winfo_exists() == 0:
            pass
    except:
        x = settings.GetSettings("dxcam", "x")
        y = settings.GetSettings("dxcam", "y")
        width = settings.GetSettings("dxcam", "width")
        height = settings.GetSettings("dxcam", "height")
        print("Creating Window")
        CreateWindow(x,y,width,height)
        print("Window Created")
    
    try:
        frame = data["frame"]

        img = ImageTk.PhotoImage(Image.fromarray(frame))
        root.update()
        
    except Exception as ex:
        print(ex)
        pass
    
    return data
    

def CreateWindow(x,y,w,h):
    global root
    global img
    
    try:
        root.destroy()
    except: pass
    
    root = tk.Tk()
    root.config(bg="black", border=0)
    root.geometry("{}x{}+{}+{}".format(w, h, x, y))

    canvas = tk.Canvas(root, width=600, height=520, border=0, highlightthickness=0)
    canvas.config(bg="black")
    canvas.grid_propagate(0) # Don't fit the canvast to the widgets
    canvas.pack_propagate(0)
    canvas.pack(anchor="center", expand=False)

    img = ImageTk.PhotoImage(Image.fromarray(np.zeros((720,1280,3), np.uint8)))
    label = ttk.Label(root, image=img, bg="black")
    label.pack(anchor="center", expand=False, pady=30)
    
    #root.overrideredirect(True)
    #root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "black")
    print("HI")
    root.update()


#class UI():
#    try: # The panel is in a try loop so that the logger can log errors if they occur
#        
#        def __init__(self, master) -> None:
#            self.master = master # "master" is the mainUI window
#            self.once = False
#            self.exampleFunction()
#        
#        def destroy(self):
#            self.done = True
#            self.root.destroy()
#            del self
#
#        
#        def exampleFunction(self):
#            
#            try:
#                self.root.destroy() # Load the UI each time this plugin is called
#            except: pass
#            
#            self.root = tk.Canvas(self.master, width=600, height=520)
#            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
#            self.root.pack_propagate(0)
#            
#            helpers.MakeButton(self.root, "Enable Picker", lambda: CreateWindow(100,100,1280,720), 0,0, padx=10, pady=10, width=15)
#            helpers.MakeLabel(self.root, "Set this to your screencapture category (default 'dxcam'):", 1,0, font=("Roboto", 8), padx=30, pady=10)
#            
#            entryVar = tk.StringVar()
#            entryVar.set("dxcam")
#            entry = ttk.Entry(self.root, width=15, textvariable=entryVar)
#            entry.grid(row=2, column=0, padx=10, pady=10)
#            
#            helpers.MakeLabel(self.root, "NOTE : You will have to update your screen capture to apply the settings!", 3,0, font=("Roboto", 8), padx=30, pady=10)
#            helpers.MakeButton(self.root, "Save Settings", lambda: SavePickerSettings(entryVar.get()), 4,0, padx=10, pady=10, width=15)
#            helpers.MakeButton(self.root, "Disable Picker", lambda: root.destroy(), 5,0, padx=10, pady=10, width=15)
#            
#            
#            self.root.pack(anchor="center", expand=False)
#            self.root.update()
#        
#        def updateOnce(self):
#            self.once = True
#        
#        def update(self, data): # When the panel is open this function is called each frame 
#            self.root.update()
#            try:
#                root.update()
#            except: pass
#    
#    
#    except Exception as ex:
#        print(ex.args)