import datetime
from dateutil import relativedelta as rd
from icecream import ic
from actions import search_payments_button

def callback(app=None):

    if app is None:
        print("app components not provided")
        return

    dt_object = datetime.datetime.now()

    year = (datetime.datetime.strftime(dt_object, "%Y"))
    month = (datetime.datetime.strftime(dt_object, "%b"))
    day = (datetime.datetime.strftime(dt_object, "%d"))

    app.components['show payments on date'].set(y=year, m=month, d=day)

    search_payments_button(app)
