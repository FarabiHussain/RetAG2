import os, csv
from icecream import ic
from GUI import InfoPopup

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

def import_recent(app=None) -> bool:

    if app is None:
        return False

    last_row = get_recent()

    add_taxes = True if last_row['add_taxes'] == 'TRUE' else False
    ic(last_row['add_taxes'] == 'TRUE')
    client1_name = last_row['client_name'].split(';')[0]
    client1_email = last_row['email'].split(';')[0]
    client1_phone = last_row['phone'].split(';')[0].replace("'", "")

    try:
        client2_name = {last_row['client_name'].split(';')[1]}
        client2_name = f" ({(" ").join(client2_name.split(' ')[0:-1])})"
        first_names = f"{(" ").join(client1_name.split(' ')[0:-1])}{client2_name}"
        last_names = f"{client1_name.split(' ')[-1]} ({client2_name.split(' ')[-1]})"
    except Exception as e:
        first_names = f"{(" ").join(client1_name.split(' ')[0:-1])}"
        last_names = f"{client1_name.split(' ')[-1]}"

    try:
        client2_email = f" ({last_row['email'].split(';')[1]})"
    except Exception as e:
        client2_email = ""

    try:
        client2_phone = f" ({last_row['phone'].split(';')[1].replace("'", "")})"
    except Exception as e:
        client2_phone = ""

    app.components['first name'].set(first_names)
    app.components['last name'].set(last_names)
    app.components['email'].set(f"{client1_email}{client2_email}")
    app.components['phone'].set(f"{client1_phone}{client2_phone}")
    app.components['city'].set("Winnipeg")
    app.components['province'].set(f"Manitoba")

    for i in range(1,13):

        # ensure both fields are filled out, otherwise leave blank
        if len(last_row[f"date_{i}"]) > 0 and len(last_row[f"amount_{i}"]) > 0:
            curr_amount = last_row[f"amount_{i}"]

            if add_taxes is True:
                curr_amount = ("{:.2f}".format(float(curr_amount) * 1.12)) 

            curr_day = last_row[f"date_{i}"].split("/")[0]
            curr_month = last_row[f"date_{i}"].split("/")[1]
            curr_year = last_row[f"date_{i}"].split("/")[2]
            
            ic(curr_amount,curr_day,curr_month,curr_year)

            app.components[f'payment {i}'].set(
                amount=curr_amount, 
                year=curr_year, 
                month=int(curr_month)-1, 
                date=f"0{curr_day}" if len(curr_day)==0 else curr_day
            )

    InfoPopup(msg="Successfully imported most recent RetAG entry.\n\nPlease fill in address and card information.")
    return True


