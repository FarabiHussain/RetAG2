import importlib.util
import os
import globals
from icecream import ic
from Database import Database


# imports a function pointed by a path
def import_function(function_path=None, function_name=None) -> str:
    if function_path is None or function_name is None:
        return

    file_path = (f"{os.getcwd()}{function_path}").replace('\\', '/')
    module_name = file_path.split('/')[-1].replace(".py", "")

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module_name = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module_name)

    return getattr(module_name, function_name, lambda: None)


def query_attendance():
    db = Database()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    retrieved_entries = collection_name.find().sort([("date", -1), ("time", -1)]).limit(75)
    globals.queried_attendance_entries = list(retrieved_entries)

    return globals.queried_attendance_entries


