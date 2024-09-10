import os
from icecream import ic
from Database import Database
from Popups import ErrorPopup, PromptPopup
from actions import search_attendance
from writer import write_to_database
from datetime import datetime as dt

def callback(app=None, adjusted_datetime=None, adjusted_staffname=None):
    if app is None:
        print("app components not provided")
        return

    if adjusted_staffname is not None:
        staff_name=adjusted_staffname
    else:
        staff_name = app.components['staff name'].get()

    db = Database()
    db.database.row_factory = db.dict_factory
    retrieved_entries = db.database.execute(
        f'''
        SELECT *
        FROM attendance
        WHERE staff_name = '{staff_name}'
        ORDER BY timestamp DESC
        LIMIT 1
        '''
    ).fetchall()
    db.close()

    if len(retrieved_entries) > 0 and (retrieved_entries[0]['type'] == 1):
        prev_time = retrieved_entries[0]['time']
        prev_date = dt.strptime(retrieved_entries[0]['date'], "%Y%m%d")
        ErrorPopup(f'{staff_name} has previously clocked in at {prev_time} on {dt.strftime(prev_date, '%b %d, %Y')}. Must be clocked out to be able to clock in.')
        return

    dt_object = dt.now()

    if adjusted_datetime is not None:
        dt_object = dt.strptime(adjusted_datetime, "%Y%m%d_%H%M")

    if PromptPopup(f'Clock in {staff_name} at {(dt.strftime(dt_object, "%I:%M %p, %b %d, %Y"))}?').get():
        write_to_database(
            table_name='attendance', 
            rows_to_write=(
                staff_name,
                dt_object.timestamp(),
                os.environ['COMPUTERNAME'],
                dt.strftime(dt_object, "%Y%m%d"),
                dt.strftime(dt_object, "%H:%M:%S"),
                1,
            )
        )

        search_attendance(app)
