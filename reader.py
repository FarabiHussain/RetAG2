import importlib.util
import os, csv, sys
from icecream import ic
from Path import resource_path

## read the csv and return as a list
def get_recent() -> dict:
    history_dir = os.getcwd() + "\\write\\"

    if not os.path.exists(history_dir):
        print("path does not exist")
        return None
    elif not os.path.exists(history_dir + "\\history.csv"):
        print("file does not exist")
        return None
    else:
        with open(history_dir + "\\history.csv", mode='r') as infile:
            last_row = list(csv.DictReader(infile))[-1]
            return last_row


def read_retainer_history() -> list:
    history_dir = os.getcwd() + "\\write\\"
    history = []

    if not os.path.exists(history_dir):
        print("path does not exist")
    elif not os.path.exists(history_dir + "\\history.csv"):
        print("file does not exist")
    else:
        with open(history_dir + "\\history.csv", mode='r') as infile:
            temp = list(csv.DictReader(infile))
            temp.reverse()
            history = temp

    return history


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
    records_file = (f'{os.getcwd()}\\write\\receipts.csv').replace('\\write\\write', '\\records')

    try:
        with open(records_file, 'r') as log_file:
            doc_id = log_file.readlines()[-1]
            doc_id = doc_id.split(",")[1]
            doc_id = doc_id.replace("[","").replace("]","")

            return int(doc_id)

    except Exception as e:
        print("no existing IDs - starting with ID 1")

    return 0