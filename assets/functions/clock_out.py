import os
from icecream import ic
from Database import Database
from Popups import ErrorPopup
from actions import search_attendance
from writer import write_to_database
from datetime import datetime as dt

def callback(app=None):
    if app is None:
        print("app components not provided")
        return

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

    ic(retrieved_entries)

    if len(retrieved_entries) == 0:
        ErrorPopup(f'Unable to clock out {staff_name} without clocking in first')
        return

    if (retrieved_entries[0]['type'] == 0):
        prev_time = retrieved_entries[0]['time']
        prev_date = dt.strptime(retrieved_entries[0]['date'], "%Y%m%d")
        ErrorPopup(f'{staff_name} has previously clocked out at {prev_time} on {dt.strftime(prev_date, '%b %d, %Y')}')
        return

    dt_object = dt.now()
    year = (dt.strftime(dt_object, "%Y"))
    month = (dt.strftime(dt_object, "%m"))
    day = (dt.strftime(dt_object, "%d"))
    hour = (dt.strftime(dt_object, "%H"))
    minute = (dt.strftime(dt_object, "%M"))
    sec = (dt.strftime(dt_object, "%S"))

    write_to_database(
        table_name='attendance', 
        rows_to_write=(
            staff_name,
            dt_object.timestamp(),
            os.environ['COMPUTERNAME'],
            f'{year}{month}{day}',
            f'{hour}:{minute}:{sec}',
            0,
        )
    )

    search_attendance(app)
