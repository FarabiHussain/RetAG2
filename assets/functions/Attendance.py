import os
from icecream import ic
from Database import Database
from Popups import ErrorPopup
from actions import search_attendance
from writer import write_to_database
from datetime import datetime as dt

def callback(self, app=None, subapp_components=None):
    return