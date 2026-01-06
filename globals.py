import os
from icecream import ic
from Database import Database
from fonts import loadfont

global default_device_user
global attendance_queried_time
global set_dark_theme
global current_lifted_subapp
global queried_attendance_entries
global links_dict
global staff_names
global device_settings
global font_settings

def init():
    global attendance_queried_time
    attendance_queried_time = None

    global default_device_user
    default_device_user = None

    global current_lifted_subapp
    current_lifted_subapp = None

    global queried_attendance_entries
    queried_attendance_entries = []

    global staff_names
    staff_names = []

    global links_dict
    links_dict = {}

    global device_settings
    device_settings = {}

    global set_dark_theme
    set_dark_theme = False

    global font_settings
    font_settings = {'family': "Roboto Condensed Bold", 'size': 13}

    loadfont(
        fontpath=os.path.join(os.getcwd(), "assets", "fonts", f"{font_settings}.ttf"),
        private=False,
        enumerable=True
    )

    mongodb = Database()
    mongodb.init_staff_names()
    mongodb.init_device_settings()

    if len(device_settings) > 0 and os.environ['COMPUTERNAME'] in device_settings:
        set_dark_theme = True if device_settings[os.environ['COMPUTERNAME']]['dark_mode'] == 1 else False
        default_device_user = device_settings[os.environ['COMPUTERNAME']]['username']
