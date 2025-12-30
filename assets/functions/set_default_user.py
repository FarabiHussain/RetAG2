import threading
from GUI import LoadingSplash
from icecream import ic
from Popups import PromptPopup
from Database import Database
import os


def _write_to_db(new_default_user, loadingsplash):
    db = Database()
    dbname = db.get_database()
    collection_name = dbname["settings"]

    collection_name.update_one(
        {"device_name": os.environ["COMPUTERNAME"]},
        {
            "$set": {"username": new_default_user},
            "$setOnInsert": {"dark_mode": 0},  # only applied if inserted
        },
        upsert=True,
    )

    db.client.close()
    loadingsplash.stop()


def callback(app=None):
    if app is None:
        print("app components not provided")
        return


    new_default_user = app.components["default staff"].get()

    if PromptPopup(f"Set default user to {new_default_user}?").get():
        loadingsplash = LoadingSplash(app.root, opacity=1.0, splash_text="validating")

        def start_write_to_db():
            threading.Thread(
                target=_write_to_db,
                args=(new_default_user, loadingsplash),
                daemon=True
            ).start()

        app.components["staff name"].set(new_default_user)
