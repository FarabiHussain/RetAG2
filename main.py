import customtkinter as ctk
import glob
import os
from Path import *
from Img import *
from GUI import *
from App import *
from Subapps import *
from actions import test_button
from reader import *
from RenderFont import RenderFont
from tkinter import messagebox
from Database import Database

imgs = Img("md")
app = App()
app.set_size(w=1640, h=900)
rf = RenderFont(f"{os.getcwd()}\\assets\\fonts\\Product Sans.ttf", '#000')

blueprint = app.get_blueprint()
subapp_components = []


# first initialize the subapp frames and buttons so that we can control their visibilty and active status
for subapp_name in blueprint:

    new_subapp = {"name": subapp_name, "frame": None, "button": None}
    new_subapp['frame'] = ctk.CTkFrame(master=app.root, fg_color="white", border_width=0, height=1010, width=1540, corner_radius=0, border_color="gray")
    new_subapp['frame'].place(x=170, y=0)

    new_subapp['button'] = ctk.CTkButton(
        master=app.root,
        text_color="black",
        text=subapp_name.upper(),
        border_width=0,
        corner_radius=0,
        fg_color="lightgray",
        width=170,
        height=70,
        font=ctk.CTkFont(family="Roboto Bold"),
        hover_color='#ddd'
    )

    subapp_components.append(new_subapp)


# use the above components and render each subapp
for i, subapp_name in enumerate(blueprint):
    subapp_components[i]['subapp_obj'] = Subapp(
        subapp_components=subapp_components, 
        blueprint=blueprint[subapp_name], 
        subapp_name=subapp_name, 
        app=app, 
        imgs=imgs, 
        button_position=i, 
        columns_weights=blueprint[subapp_name]['column_weights'] if 'column_weights' in blueprint[subapp_name] else None, 
    )

    app.add_component(subapp_name, subapp_components[i]['subapp_obj'])


def on_startup():
    if "--test" in sys.argv:
        # test_button(app)
        # subapp_components[5]['subapp_obj'].lift_app(subapp_components)
        pass


def on_closing():
    if "--test" in sys.argv:
        Database().close()

        for dir in ['write', 'output/agreements','output/receipts','output/invitations','output/imm5476']:
            for f in glob(f"./{dir}/*"):
                os.remove(f)

        app.root.destroy()

    elif messagebox.askokcancel("Quit", "Do you want to quit?"):
        Database().close()
        app.root.destroy()

on_startup()
app.root.protocol("WM_DELETE_WINDOW", on_closing)
app.start()
