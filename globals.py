from datetime import datetime as dt
import os
from icecream import ic
from Database import Database, Mongo

global defualt_device_user
global attendance_queried_time
global set_dark_theme
global current_lifted_subapp
global queried_attendance_entries
global links_dict
global staff_names

def init():
    db = Database()
    db.init_tables()

    global attendance_queried_time
    attendance_queried_time = None

    global defualt_device_user
    defualt_device_user = None

    global set_dark_theme
    set_dark_theme = False

    global current_lifted_subapp
    current_lifted_subapp = None

    global queried_attendance_entries
    queried_attendance_entries = []

    global staff_names
    staff_names = []

    global links_dict
    links_dict = {}

    mongodb = Mongo()
    mongodb.load_staff_names()

    retreived_devices = db.cursor.execute(f"SELECT * FROM theme WHERE device_name = '{os.environ['COMPUTERNAME']}'").fetchall()

    if len(retreived_devices) > 0:
        set_dark_theme = True if retreived_devices[0][1] == 1 else False
        defualt_device_user = retreived_devices[0][2]
    else:
        db.cursor.execute(f"INSERT INTO theme VALUES (?, ?, ?)", (os.environ['COMPUTERNAME'], 0, "-"))
        db.commit()

    db.close()

    return