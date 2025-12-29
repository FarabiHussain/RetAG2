from icecream import ic
from Database import Database
from Popups import ErrorPopup
from actions import set_attendance

def callback(app=None):
    if app is None:
        print("app components not provided")
        return

    filter_staff = app.components.get("staff name").get()
    filter_clock_type = app.components.get("clock type").get()
    filter_start_date = app.components.get("attendance start date").get(formatting="$y%m$d")
    filter_end_date = app.components.get("attendance end date").get(formatting="$y%m$d")

    if int(filter_end_date) < int(filter_start_date):
        ErrorPopup("start date must be less than or equal to end date")
        return

    if filter_clock_type.lower() != "clock in" and filter_clock_type.lower() != "clock out" and filter_clock_type.lower() != "any":
        ErrorPopup("Please select an a valid clock type")
        return

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    search_filters = {"date": {"$gte": filter_start_date, "$lte": filter_end_date}}

    if filter_clock_type.lower() != "any":
        search_filters["type"] = 1 if filter_clock_type.lower() == "clock in" else 0

    if filter_staff.lower() != "any":
        search_filters["staff_name"] = filter_staff

    retrieved_entries = list(collection_name.find(search_filters).sort({"date":-1, "staff_name": 1}))

    for entry in (retrieved_entries):
        print(entry)

    set_attendance(app, retrieved_entries)

    db.client.close()

