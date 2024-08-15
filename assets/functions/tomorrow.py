import datetime
from dateutil import relativedelta as rd
from icecream import ic

def callback(app=None):

    if app is None:
        print("app components not provided")
        return

    search_in_date = app.components['show payments on date'].get().strip()
    dt_object = datetime.datetime.strptime(search_in_date, "%b %d, %Y")
    dt_object = dt_object + rd.relativedelta(days=1)

    year = (datetime.datetime.strftime(dt_object, "%Y"))
    month = (datetime.datetime.strftime(dt_object, "%b"))
    day = (datetime.datetime.strftime(dt_object, "%d"))

    app.components['show payments on date'].set(y=year, m=month, d=day)
