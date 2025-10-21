import customtkinter as ctk
import glob
import os
from Path import *
from Img import *
from GUI import *
from App import *
from Subapps import *
from actions import test_button, search_attendance
from reader import *
from RenderFont import RenderFont
from tkinter import messagebox
from Database import Database, Mongo
from writer import unobscure, write_to_database
import globals

globals.init()
imgs = Img("md")
app = App()
app.set_size(w=1640, h=900)
rf = RenderFont(f"{os.getcwd()}\\assets\\fonts\\Product Sans.ttf", '#000')

blueprint = app.get_blueprint()
subapp_components = []


# first initialize the subapp frames and buttons so that we can control their visibilty and active status
for subapp_name in blueprint:
    new_subapp = {"name": subapp_name, "frame": None, "button": None}
    new_subapp['frame'] = ctk.CTkFrame(master=app.root, fg_color="#444444" if globals.set_dark_theme else "#ffffff", border_width=0, height=1010, width=1540, corner_radius=0, border_color="gray")
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
        hover_color='#dddddd'
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
        pass

    def set_home_as_default():
        subapp_components[0]['subapp_obj'].lift_app(subapp_components)

    def set_attendance_as_default():
        ic(globals.defualt_device_user)

        if globals.defualt_device_user != "":
            app.components['staff name'].set(globals.defualt_device_user)

        app.components['attendance start date'].set(d="01")
        search_attendance(app, is_callback=True, is_first_tab=True)
        subapp_components[0]['subapp_obj'].lift_app(subapp_components)

    def disable_buttons_while_loading():
        for curr_subapp in subapp_components:
            curr_subapp['button'].configure(state='disabled')

    def task():
        time.sleep(0.01)
        set_attendance_as_default()
        Mongo().load_staff_names()
        app.components.get('staff name').add_options(new_options=sorted(globals.staff_names))

    from GUI import LoadingSplash
    loadingsplash = LoadingSplash(app.root, opacity=1.0, splash_text="RETAG2")
    loadingsplash.show(task=task)


def on_closing():
    if "--test" not in sys.argv or messagebox.askokcancel("Quit", "Do you want to quit?"):
        Database().close()
        app.root.destroy()


on_startup()
app.root.protocol("WM_DELETE_WINDOW", on_closing)
app.start()
