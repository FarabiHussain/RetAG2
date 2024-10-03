import sys
from icecream import ic
from Database import Mongo
import datetime as dt
import time
from actions import WindowedViewer

def callback(app=None):
    db = Mongo()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    if "--test" in sys.argv:
        filter_staff = "Farabi"
        filter_start_date = "20240901"
        filter_end_date = "20240930"
    else:
        filter_staff = app.components.get("attendance of staff").get()
        filter_start_date = app.components.get("attendance start date").get(formatting="$y%m$d")
        filter_end_date = app.components.get("attendance end date").get(formatting="$y%m$d")

    ic(filter_staff, filter_start_date, filter_end_date)

    retrieved_entries = list(
        collection_name.find({
            "staff_name": filter_staff, 
            "date": {"$gte": filter_start_date, "$lte": filter_end_date}
        }).sort({
            "date":1, 
            "time":1
        })
    )


    timesheet = {}

    for entry in (retrieved_entries):
        if entry.get('date') in timesheet:
            timesheet[entry.get('date')]['in' if entry.get('type') == 1 else 'out'] = entry.get('time')
        else:
            timesheet[entry.get('date')] = {'in' if entry.get('type') == 1 else 'out': entry.get('time')}


    total_seconds = 0

    for dateEntry in timesheet:
        curr_row = timesheet[dateEntry]

        if "in" in curr_row and "out" in curr_row:
            curr_row['tdelta'] = (dt.datetime.strptime(curr_row['out'], '%H:%M:%S') - dt.datetime.strptime(curr_row['in'], '%H:%M:%S')).total_seconds()
        else:
            curr_row['tdelta'] = 0

        total_seconds += int(curr_row['tdelta'])

    tminutes, tseconds = divmod(total_seconds, 60)
    thours, tminutes = divmod(tminutes, 60)
    total_seconds = ("%d:%02d:%02d" % (thours, tminutes, tseconds))

    # ic(list(zip(timesheet.keys(), list(timesheet.values()))))
    ic(dict(timesheet.values()))

    WindowedViewer(
        app, 
        column_names=['client name', 'created by', 'created date', 'application type', 'application fee'],
        entries=[['','','','','']]
    )
    # print(f'clocked {}\ton {entry.get('date')}\tat {entry.get('time')}')
