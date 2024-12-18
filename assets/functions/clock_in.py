import os
import globals
from icecream import ic
from Database import Mongo
from Popups import ErrorPopup, PromptPopup
from actions import search_attendance
from datetime import datetime as dt

def callback(app=None, adjusted_datetime=None, adjusted_staffname=None):
    if app is None:
        print("app components not provided")
        return

    if adjusted_staffname is not None:
        staff_name=adjusted_staffname
    else:
        staff_name = app.components['staff name'].get()

    if staff_name == "Select":
        ErrorPopup("Please select an employee")
        return

    dt_object = dt.now()
    db = Mongo()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    retrieved_entries = list(collection_name.find({"staff_name": staff_name}).sort({"date":-1, "time":-1}).limit(1))

    if adjusted_datetime is None:
        if len(retrieved_entries) > 0 and (retrieved_entries[0]['type'] == 1):
            prev_time = retrieved_entries[0]['time']
            prev_date = dt.strptime(retrieved_entries[0]['date'], "%Y%m%d")
            ErrorPopup(f'{staff_name} has previously clocked in at {prev_time} on {dt.strftime(prev_date, '%b %d, %Y')}. Must be clocked out to be able to clock in.')
            return

    if adjusted_datetime is not None:
        dt_object = dt.strptime(adjusted_datetime, "%Y%m%d_%H%M")

    if PromptPopup(f'Clock in {staff_name} at {(dt.strftime(dt_object, "%I:%M %p, %b %d, %Y"))}?').get():
        collection_name.insert_one(
            {
                "staff_name" : staff_name,
                "device" : os.environ['COMPUTERNAME'],
                "date" : dt.strftime(dt_object, "%Y%m%d"),
                "time" : dt.strftime(dt_object, "%H:%M:%S"),
                "type" : 1
            }
        )

        search_attendance(app)

    db.client.close()