from icecream import ic
from Popups import PromptPopup
from Database import Database
import os


def callback(app=None):
    if app is None:
        print("app components not provided")
        return

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["settings"]

    new_default_user = app.components["default staff"].get()

    if PromptPopup(f"Set default user to {new_default_user}?").get():
        collection_name.update_one(
            {"device_name": os.environ["COMPUTERNAME"]},
            {"$set": {"username": new_default_user}},
        )

        app.components["staff name"].set(new_default_user)
