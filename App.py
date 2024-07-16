import customtkinter as ctk
import os
import json
import GUI

from Path import *
from icecream import ic
from pprint import pprint
from tkinter import font
from fontTools.ttLib import TTFont



class App():
    def __init__(self) -> None:
        os.system("cls")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.resizable(False, False)
        self.root.configure(fg_color='lightgray')
        self.version = "v0.0.1"
        self.root.title(f"AMCAIM Toolbox {self.version}")
        self.blueprint = self.__read_blueprint()
        self.components = {}
        self.windows = {}
        
        self.app_icon_passed = self.__check_app_ico()
        self.fonts_passed = self.__check_fonts()


    def __check_fonts(self) -> bool:
        missing_fonts = []
        for font_family in ['Poppins Medium', 'Poppins']:
            if font_family not in list(font.families()):
                missing_fonts.append(font_family)

        def open_missing_fonts(missing_fonts):
            for curr_font in missing_fonts:
                os.startfile(resource_path(f"{os.getcwd()}\\assets\\fonts\\{curr_font.replace(" ", "-")}.ttf"))

        if len(missing_fonts) > 0:
            GUI.PromptPopup(
                msg="Font packs needed for the program are not installed.\n\nOpen the files to install them?",
                func=lambda:open_missing_fonts(missing_fonts)
            )
            return False
        
        return True


    def __check_app_ico(self) -> bool:
        try:
            self.root.iconbitmap(f"{os.getcwd()}\\assets\\icons\\app.ico")
            return True
        except Exception as e:
            print(e)

        return False


    def __read_blueprint(self) -> dict:
        try:
            f = open(resource_path("assets\\blueprint.json"))
            loaded = json.load(f)
            f.close()

            return loaded
        except Exception as e:
            print(e)

        return {}


    def __get_position(self, w, h) -> tuple:
        return (
            (self.root.winfo_screenwidth()/2) - (w/2),
            (self.root.winfo_screenheight()/2) - (h/2)
        )


    def get_subapps(self) -> dict:
        return self.subapps


    def get_blueprint(self) -> dict:
        return self.blueprint


    def get_size(self, orientation=None) -> int|tuple[int,int]:
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()

        if orientation == 'w':
            return w
        elif orientation == 'h':
            return h

        return (self.root.winfo_screenwidth(), self.root.winfo_screenheight())


    def set_size(self, w, h):
        x, y = self.__get_position(w, h)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))


    def add_component(self, label, obj) -> None:
        self.components[label] = obj


    def get_component(self, label) -> GUI.Entry | GUI.DatePicker | GUI.ComboBox | GUI.DatePicker | GUI.WindowView | None:
        try:
            return self.components[label]
        except Exception as e:
            print(e)

        return None


    def add_window(self, label, obj) -> None:
        self.windows[label] = obj


    def get_window(self, label) -> GUI.WindowView | None:
        try:
            return self.windows[label]
        except Exception as e:
            print(e)

        return None


    def get_all_components(self) -> dict | None:
        try:
            return self.components
        except Exception as e:
            print(e)

        return None


    def reset_all_components(self) -> None:
        for component in self.components.values():
            component.reset()


    def start(self) -> None:
        if self.fonts_passed:
            self.root.mainloop()


    def hide(self) -> None:
        self.root.withdraw()


    def unhide(self) -> None:
        self.root.deiconify()

