import globals
from Database import Database
from Popups import ErrorPopup, PromptPopup
from actions import set_attendance
from datetime import datetime as dt


def callback(app=None, *args, **kwargs):
    if app is None:
        print("app components not provided")
        return
    else:
        new_staff_name = args[0]

        if new_staff_name == "Select":
            ErrorPopup("Please select an employee")
            return

    dt_object = dt.now()
    db = Database()
    dbname = db.get_database()
    collection_name = dbname["staff"]

    if PromptPopup(f"Add staff member {new_staff_name}?").get():
        collection_name.insert_one({"name": new_staff_name})

        db.init_staff_names()
        app.components["staff name"].add_options(globals.staff_names)

    db.client.close()
