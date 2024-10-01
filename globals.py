from datetime import datetime as dt
from icecream import ic

global attendance_queried_time

def init():
    global attendance_queried_time
    attendance_queried_time = None

    ic(attendance_queried_time)

    return