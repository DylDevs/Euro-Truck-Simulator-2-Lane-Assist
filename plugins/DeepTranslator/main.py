"""
This is an example of a panel (type="static"), they will be updated if they are open.
If you need to make a plugin that is updated in the bg then check the Plugin example!
"""


from plugins.plugin import PluginInformation
from src.logger import print

PluginInfo = PluginInformation(
    name="DeepTranslator", # This needs to match the folder name under plugins (this would mean plugins\Panel\main.py)
    description="DeepTranslator control panel.",
    version="0.1",
    author="Tumppi066",
    url="https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist",
    type="static" # = Panel
)

import tkinter as tk
from tkinter import ttk
import src.helpers as helpers
import src.mainUI as mainUI
import src.variables as variables
import src.settings as settings
import src.translator as translator
import os

class UI():
    try: # The panel is in a try loop so that the logger can log errors if they occur
        
        def __init__(self, master) -> None:
            self.master = master # "master" is the mainUI window
            self.exampleFunction()
        
        def destroy(self):
            self.done = True
            self.root.destroy()
            del self

        def changeLanguage(self, language):
            settings.CreateSettings("User Interface", "DestinationLanguage", translator.FindCodeFromLanguage(language))
            translator.MakeTranslator("google")
            translator.dest = translator.FindCodeFromLanguage(language)
            variables.RELOAD = True
        
        def exampleFunction(self):
            
            try:
                self.root.destroy() # Load the UI each time this plugin is called
            except: pass
            
            self.root = tk.Canvas(self.master, width=600, height=520, border=0, highlightthickness=0)
            self.root.grid_propagate(0) # Don't fit the canvast to the widgets
            self.root.pack_propagate(0)
            
            self.languages = translator.AVAILABLE_LANGUAGES
            
            languagesToDisplay = [string for string in self.languages if string not in ["auto"]]
            # Make a picker of the languages
            helpers.MakeLabel(self.root, "Application language : ", 0,0)
            self.language = ttk.Combobox(self.root, values=languagesToDisplay, width=20)
            currentLanguage = translator.FindLanguageFromCode(settings.GetSettings("User Interface", "DestinationLanguage"))
            indexOfCurrentLanguage = languagesToDisplay.index(currentLanguage)
            self.language.current(indexOfCurrentLanguage)
            self.language.grid(row=0, column=1, padx=10, pady=10)
            
            helpers.MakeButton(self.root, "Apply", lambda: self.changeLanguage(self.language.get()), 0,2, padx=10, pady=10, width=20)
            
            self.root.pack(anchor="center", expand=False)
            self.root.update()
        
        
        def update(self, data): # When the panel is open this function is called each frame 
            self.root.update()
    
    
    except Exception as ex:
        print(ex.args)