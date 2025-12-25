import os
from Database import Mongo
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

        if new_staff_name == "Select":
            ErrorPopup("Please select an employee")
            return

    dt_object = dt.now()
    db = Mongo()
    dbname = db.get_database()
    collection_name = dbname["staff"]

    if PromptPopup(f"Rename {selected_staff} to {new_staff_name}?").get():
        collection_name.update_one(
            {"name": selected_staff},
            {
                "$set": {
                    "name": new_staff_name,
                }
            },
        )

        db.load_staff_names()

    db.client.close()
