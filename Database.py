import sys
import globals


class Database:
    def __init__(self) -> None:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        import os

        load_dotenv()

        CONNECTION_STRING = os.getenv('CONNECTION_STRING')
        self.client = MongoClient(CONNECTION_STRING)

    def get_database(self):
        if '--test' in sys.argv:
            return self.client['retag-test']

        return self.client['retag-test']

    def init_staff_names(self):
        db = self.get_database()
        collection = db["staff"]

        # Fetch names where show == True
        staff = collection.find({"show": True}, {"name": 1, "_id": 0})
        globals.staff_names = [s["name"] for s in staff]

    def init_device_settings(self):
        db = self.get_database()
        collection = db["settings"]
        theme = collection.find()

        for row in theme:
            globals.device_settings[row['device_name']] = {
                'dark_mode': row['dark_mode'],
                'username': row['username']
            }

    def close(self):
        self.client.close()
