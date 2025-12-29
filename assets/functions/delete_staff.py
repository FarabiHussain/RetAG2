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
        # staff_name = app.components['staff name'].get()
        selected_staff = args[0]
        new_staff_name = args[1]
        staff_picker = args[2]

        if new_staff_name == "Select":
            ErrorPopup("Please select an employee")
            return

    dt_object = dt.now()
    db = Database()
    dbname = db.get_database()
    collection_name = dbname["staff"]

    if PromptPopup(f"Rename {selected_staff} to {new_staff_name}?").get():
        collection_name.delete_one({"name": selected_staff})

        db.init_staff_names()
        app.components["staff name"].add_options(globals.staff_names)
        staff_picker.add_options(globals.staff_names)
        staff_picker.set('click to select')

    db.client.close()
