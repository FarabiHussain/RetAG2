import customtkinter as ctk
from Path import *
from Img import *
from GUI import *
from App import *
from Subapps import *
from reader import *

imgs = Img("md")
app = App()
app.set_size(w=1640, h=900)

blueprint = app.get_blueprint()
subapp_components = []

# first initialize the subapp frames and buttons so that we can control their visibilty and active status
for subapp_name in blueprint:

    new_subapp = {"frame": None, "button": None}

    new_subapp['frame'] = ctk.CTkFrame(master=app.root, fg_color="white", border_width=0, height=1010, width=1540, corner_radius=0, border_color="gray")
    new_subapp['frame'].place(x=170, y=0)

    new_subapp['button'] = ctk.CTkButton(
        master=app.root,
        text_color="black",
        text=subapp_name,
        border_width=0,
        corner_radius=0,
        fg_color="lightgray",
        width=170,
        height=70,
        font=ctk.CTkFont(family="Roboto Bold")
    )

    subapp_components.append(new_subapp)

# use the above components and render each subapp
for i, subapp_name in enumerate(blueprint):
    Subapp(subapp_components=subapp_components, blueprint=blueprint[subapp_name], subapp_name=subapp_name, app=app, imgs=imgs, button_position=i)

app.start()
