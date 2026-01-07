from pathlib import Path
import customtkinter as ctk
import os
import globals
from Path import *
from Img import *
from GUI import *
from App import *
from Popups import InfoPopup
from Subapps import *
from actions import set_attendance
from reader import *
from Database import Database
from updater import search_update_on_startup, swap_updater_if_present

os.system("cls")
globals.init()
imgs = Img("md")
app = App()
app.set_size(w=1640, h=900)

search_update_on_startup(app)
query_attendance()

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
        font=ctk.CTkFont(**globals.font_settings),
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
    def navigate_to_default_page():
        if globals.default_device_user != "":
            app.components['staff name'].set(globals.default_device_user)

        set_attendance(app, is_callback=True, is_first_tab=True, override_entries=globals.queried_attendance_entries)
        app.components['attendance start date'].set(d="01")

        if os.environ['COMPUTERNAME'] in globals.device_settings:
            subapp_components[0]['subapp_obj'].lift_app(subapp_components)
        else:
            subapp_components[3]['subapp_obj'].lift_app(subapp_components)
            InfoPopup("No device settings found for this device.\n\nPlease select the default user from the settings tab")

    def task():
        time.sleep(0.01)
        navigate_to_default_page()
        app.components.get('staff name').add_options(new_options=sorted(globals.staff_names))
        app.components.get('default staff').add_options(new_options=sorted(globals.staff_names))
        swap_updater_if_present()

        if "-test" in sys.argv:
            app.components['attendance start date'].set(d="01", m="Dec", y="2025")

    from GUI import LoadingSplash
    loadingsplash = LoadingSplash(app.root, opacity=1.0, splash_text="RETAG2")
    loadingsplash.show(task=task)


def on_closing():
    Database().close()
    app.root.destroy()


on_startup()
app.root.protocol("WM_DELETE_WINDOW", on_closing)
app.start()
