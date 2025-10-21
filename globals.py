from datetime import datetime as dt
import os
from icecream import ic
from Database import Database

global defualt_device_user
global attendance_queried_time
global set_dark_theme

def init():
    db = Database()

    global attendance_queried_time
    attendance_queried_time = None

    global defualt_device_user
    defualt_device_user = None

    global set_dark_theme
    set_dark_theme = False

    global current_lifted_subapp
    current_lifted_subapp = None

    global staff_names
    staff_names = []

    retreived_devices = db.cursor.execute(f"SELECT * FROM theme WHERE device_name = '{os.environ['COMPUTERNAME']}'").fetchall()

    if len(retreived_devices) > 0:
        set_dark_theme = True if retreived_devices[0][1] == 1 else False
        defualt_device_user = retreived_devices[0][2]
    else:
        db.cursor.execute(f"INSERT INTO theme VALUES (?, ?, ?)", (os.environ['COMPUTERNAME'], 0, ""))
        db.commit()

    db.close()

    return