import os
import datetime as dt
from icecream import ic
from Database import Database
from Popups import ErrorPopup
from GUI import WindowedViewer


def parsetime(t, format):
    return dt.datetime.strptime(t, format)

def formattime(t, parse, format):
    return dt.datetime.strftime(dt.datetime.strptime(t, parse), format)


def callback(app=None):
    os.system('cls')

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    filter_staff = app.components.get("staff name").get()
    filter_start_date = app.components.get("attendance start date").get(formatting="$y%m$d")
    filter_end_date = app.components.get("attendance end date").get(formatting="$y%m$d")

    if filter_staff.strip().lower() == "any":
        ErrorPopup("Please select a staff member")
        return

    retrieved_entries = list(
        collection_name.find({
            "staff_name": filter_staff, 
            "date": {"$gte": filter_start_date, "$lte": filter_end_date}
        }).sort({
            "date":1, 
            "time":1
        })
    )

    if len(retrieved_entries) == 0:
        ErrorPopup(f"No hours recorded for {filter_staff} within the selected dates")
        return

    timesheet = {}
    dateCounters = {} # how many times does the same date come up in the list?

    for entry in (retrieved_entries):
        clock_state = 'in' if entry.get('type') == 1 else 'out'
        curr_date = entry.get('date')
        curr_date_count = dateCounters.get(curr_date, '1')

        # a certain date already exists in the timesheet
        if (f"{curr_date}{curr_date_count}") in timesheet:
            if clock_state in timesheet[f"{curr_date}{curr_date_count}"]:
                dateCounters[curr_date] += 1
                timesheet[f'{curr_date}{dateCounters[curr_date]}'] = {clock_state: entry.get('time')}
            else:
                timesheet[f"{curr_date}{curr_date_count}"][clock_state] = entry.get('time')

        # no duplicates for the current date so far
        else:
            dateCounters[curr_date] = 1
            timesheet[f"{curr_date}{dateCounters[curr_date]}"] = {clock_state: entry.get('time')}


    total_seconds = 0
    table_contents = []

    for key, val in zip(timesheet.keys(), timesheet.values()):

        val['tdelta'] = 0

        # the current date has both a 'clock-in' and 'clock-out', so the difference can be calculated
        if "in" in val and "out" in val:
            val['tdelta'] = (parsetime(val['out'], '%H:%M:%S') - parsetime(val['in'], '%H:%M:%S')).total_seconds()

        total_seconds += int(val['tdelta'])

        total_min, _ = divmod(total_seconds, 60)
        total_hrs, total_min = divmod(total_min, 60)
        day_mins, _ = divmod(val['tdelta'], 60)
        day_hrs, day_mins = divmod(day_mins, 60)

        if (day_hrs == 0):
            hrs_in_date = ("%d min" % (day_mins)) if (day_mins > 0) else "-"
        else:
            hrs_in_date = ("%d hr %d min" % (day_hrs, day_mins)) if (day_hrs + day_mins > 0) else "-"

        curr_row = [
            formattime(key[0:8], '%Y%m%d', '%a, %b %d, %Y'),
            val.get('in', '-')[0:5],
            val.get('out', '-')[0:5],
            hrs_in_date,
            ("%d hr %d min" % (total_hrs, total_min))
        ]

        table_contents.append(curr_row)

    WindowedViewer(
        app, 
        column_names=['date', 'clocked in at', 'clocked out at', 'hours in date', 'cumulative hours'],
        entries=table_contents,
        add_cell_formatting=False,
        window_title=f'attendance breakdown: {filter_staff}, between {formattime(filter_start_date, '%Y%m%d', '%b %d, %Y')} and {formattime(filter_end_date, '%Y%m%d', '%b %d, %Y')}',
        highlight_weekends=True
    )
