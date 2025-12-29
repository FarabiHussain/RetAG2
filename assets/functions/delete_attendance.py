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
        new_staff_name = args[0]
        new_dt_object = args[1]
        new_clock_type = args[2]
        new_entry_id = args[3]

        if new_staff_name == "Select":
            ErrorPopup("Please select an employee")
            return

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    if PromptPopup(f'Delete entry for: Clock {"in" if new_clock_type == 1 else "out"} {new_staff_name} at {(dt.strftime(new_dt_object, "%I:%M %p, %b %d, %Y"))}?').get():
        collection_name.delete_one({"_id": new_entry_id})
        set_attendance(app)

    db.client.close()