from datetime import datetime as dt
import os
from icecream import ic
from Database import Database


global attendance_queried_time
global set_dark_theme

def init():
    global attendance_queried_time
    attendance_queried_time = None

    global set_dark_theme
    set_dark_theme = False

    db = Database()

    retreived_devices = db.cursor.execute(f"SELECT * FROM theme WHERE device_name = '{os.environ['COMPUTERNAME']}'").fetchall()

    if len(retreived_devices) > 0:
        set_dark_theme = True if retreived_devices[0][1] == 1 else False
    else:
        db.cursor.execute(f"INSERT INTO theme VALUES (?, ?)", (os.environ['COMPUTERNAME'], 0))
        db.commit()

    db.close()

    return