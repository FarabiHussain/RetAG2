import os
from Database import Database
from Popups import ErrorPopup, PromptPopup
from actions import set_attendance
from datetime import datetime as dt
from icecream import ic

def _delete(params, collection_name):
    if PromptPopup(f'Delete entry for: Clock {"in" if params['new_clock_type'] == 1 else "out"} {params['new_staff_name']} at {(dt.strftime(params['new_dt_object'], "%I:%M %p, %b %d, %Y"))}?').get():
        collection_name.delete_one({"_id": params['new_entry_id']})


def _edit(params, collection_name):
    if PromptPopup(f'Edit entry to the following: Clock {"in" if params['new_clock_type'] == 1 else "out"} {params['new_staff_name']} at {(dt.strftime(params['new_dt_object'], "%I:%M %p, %b %d, %Y"))}?').get():
        collection_name.update_one(
            {"_id": params['new_entry_id']},
            {
                "$set": {
                    "staff_name": params['new_staff_name'],
                    "device": os.environ['COMPUTERNAME'],
                    "date": dt.strftime(params['new_dt_object'], "%Y%m%d"),
                    "time": dt.strftime(params['new_dt_object'], "%H:%M:%S"),
                    "type": params['new_clock_type']
                }
            }
        )


def callback(app=None, *args, **kwargs):
    if app is None:
        return

    params = args[0]

    if params['new_staff_name'] == "Select":
        ErrorPopup("Please select an employee")
        return

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    OPERATIONS = {
        "edit": lambda: _edit(params, collection_name),
        "delete": lambda: _delete(params, collection_name),
    }

    OPERATIONS.get(params['operation_type'])()

    set_attendance(app)
    db.client.close()