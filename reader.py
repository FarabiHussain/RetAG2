# import csv
# import sys
import importlib.util
import os
import datetime
from icecream import ic
from Database import Database
from Path import resource_path

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


# read records.csv to retrieve the last created receipt id
def read_receipt_id():

    receipt_id = 0

    db = Database()
    retrieved_ids = db.cursor.execute('SELECT receipt_id FROM receipts ORDER BY receipt_id DESC LIMIT 1').fetchall()
    db.close()

    if len(retrieved_ids) > 0:
        receipt_id = int(retrieved_ids[0][0])

    return receipt_id


# read agreements.csv to retrieve the last created id
def read_case_id(get_next=True):
    curr_timestamp = str(datetime.datetime.now().strftime('%Y%m'))
    case_id = f'{curr_timestamp}-000'

    db = Database()
    retrieved_ids = db.cursor.execute('SELECT case_id FROM agreements WHERE document_type = "Retainer Agreement" ORDER BY case_id DESC LIMIT 1').fetchall()
    db.close()

    if len(retrieved_ids) > 0:
        case_id = retrieved_ids[0][0]

    if get_next:
        case_id = f'{case_id.split("-")[0]}-{"{:03}".format(int(case_id.split("-")[1]) + 1)}'

    return case_id
