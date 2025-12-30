from icecream import ic
from Popups import InfoPopup
from Database import Database
import os

def callback(app_components=None):

    if app_components is None:
        print("app components not provided")
        return

    ic(app_components['dark theme'].get())

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["settings"]

    respose = collection_name.update_one(
        {"device_name": os.environ['COMPUTERNAME']},
        {"$set": {"dark_mode": 1 if app_components['dark theme'].get() == 'on' else 0}}
    )

    if respose.modified_count == 0:
        collection_name.insert_one(
            {
                "device_name": os.environ['COMPUTERNAME'],
                "dark_mode": 1 if app_components['dark theme'].get() == 'on' else 0,
                "username": ""
            }
        )

    InfoPopup(f'Dark theme will be set to {app_components["dark theme"].get()} next time RETAG is opened.')
