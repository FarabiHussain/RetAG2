import importlib.util
import os, csv, sys, datetime
from icecream import ic
from Path import resource_path

## read the csv and return as a list
def get_recent() -> dict:
    history_dir = os.getcwd() + "\\write\\"

    if not os.path.exists(history_dir):
        print("path does not exist")
        return None
    elif not os.path.exists(history_dir + "\\agreements.csv"):
        print("file does not exist")
        return None
    else:
        with open(history_dir + "\\agreements.csv", mode='r') as infile:
            last_row = list(csv.DictReader(infile))[-1]
            return last_row


def read_file_as_list(filename='agreements.csv') -> list:
    history_dir = f"{os.getcwd()}\\write\\"
    filepath = f'{history_dir}\\{filename}{'.csv' if '.csv' not in filename else ''}'
    history = []

    if not os.path.exists(history_dir):
        print("path does not exist")
    elif not os.path.exists(filepath):
        print("file does not exist")
    else:
        with open(filepath, mode='r') as infile:
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
    records_file = (f'{os.getcwd()}\\write\\receipts.csv').replace('\\write\\write', '\\receipts')

    try:
        with open(records_file, 'r') as log_file:
            doc_id = log_file.readlines()[-1]
            doc_id = doc_id.split(",")[3]
            doc_id = doc_id.replace("[","").replace("]","")

            return int(doc_id)

    except Exception as e:
        print("no existing IDs - starting with ID 1")

    return 0

# read agreements.csv to retrieve the last created id
def read_case_id():
    records_file = (f'{os.getcwd()}\\write\\agreements.csv').replace('\\write\\write', '\\agreements')
    curr_timestamp = str(datetime.datetime.now().strftime('%Y%m'))
    doc_id = f'{curr_timestamp}-001'


    # fix this to use CSV columns instead of split()
    try:
        with open(records_file, 'r') as log_file:
            prev_doc_id = log_file.readlines()[-1]

        prev_doc_id = prev_doc_id.split(",")[0]
        prev_timestamp = (prev_doc_id.split('-')[0])
        prev_number = (prev_doc_id.split('-')[1])

        if curr_timestamp == prev_timestamp:
            curr_number = "{:03}".format(int(prev_number) + 1)
        else:
            curr_number = "001"

        doc_id = f"{curr_timestamp}-{curr_number}"

    except Exception as e:
        print(f"Error when reading ID, returning {doc_id}\n\n{e}")

    return doc_id