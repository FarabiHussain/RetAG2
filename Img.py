import customtkinter as ctk, os
from PIL import Image
from Path import *
from glob import glob


class Img():
    def __init__(self, size="md") -> None:

        coefficient = {
            "sm": 16,
            "md": 28,
            "lg": 72,
        }

        self.images = {}
        self.size = coefficient[size] if size in coefficient else coefficient["md"]
        self.__read_images()


    def __read_images(self) -> None:
        owd = os.getcwd()

        try:
            os.chdir(f"{os.getcwd()}\\assets\\icons")
            for f in glob("*"):
                self.images[f] = None
        except Exception as e:
            print(e)

        for icon_name in list(self.images.keys()):
            try:
                self.images[icon_name] = Image.open(resource_path(f"{icon_name}"))
                img_size = self.images[icon_name].size
                img_ratio = img_size[0]/img_size[1]

                self.images[icon_name] = ctk.CTkImage(
                    light_image=None,
                    dark_image=self.images[icon_name],
                    size=(self.size*img_ratio, self.size),
                )
            except Exception as e:
                print(e)

        os.chdir(owd)


    def get_names(self) -> list:
        return list(self.images.keys())


    def get(self, icon_name) -> dict:
        if icon_name in self.images:
            return self.images[icon_name]

        return self.images["Null.png"]
