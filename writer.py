import os
import datetime
import re
import zlib
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from Path import *
from Doc import *
from icecream import ic
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from reader import read_case_id, read_receipt_id


def obscure(unobscured: str) -> str:
    return b64e(zlib.compress(str.encode(unobscured), 9)).decode()


def unobscure(obscured: str) -> str:
    return zlib.decompress(b64d(str.encode(obscured))).decode()


def write_payments(doc, components):
    client_info_top = [
        {
            "label": "first name",
            "info": components["client 1 first name"].get(),
        },
        {
            "label": "last name",
            "info": components["client 1 last name"].get(),
        },
        {
            "label": "email",
            "info": components["client 1 email"].get(),
        },
        {
            "label": "phone",
            "info": components["client 1 phone"].get(),
        },
        {
            "label": "address",
            "info": components["address"].get(),
        }
    ]

    card_info_2col = [
        {
            "label": "card type",
            "info": components["card type"].get(),
        },
        {
            "label": "expiration",
            "info": components["expiration"].get(),
        },
        {
            "label": "card number",
            "info": components["card number"].get(),
        },
        {
            "label": "security code",
            "info": obscure(components["security code"].get()),
        },
        {
            "label": "cardholder name",
            "info": components["cardholder name"].get(),
        },
    ]

    tax_multiplier = 1.12 if components['add taxes'].get().lower() == "yes" else 1.00

    payment_summary = [
        {
            "label_l": "Total of".rjust(10),
            "info_l": "${:.2f}".format(components['application fee'].get('amount') * tax_multiplier),
            "label_r": "paid over".rjust(20),
            "info_r": f"{components['application fee'].get('months')} {"month" if components['application fee'].get('months') == 1 else "months"}",
        }
    ]

    payment_info = []
    for i in range(12):
        curr_amount = "N/A"
        curr_date = "N/A"

        if (components[f"payment {i+1}"].get('amount')) > 0:
            curr_amount = float(components[f"payment {i+1}"].get('amount')) * tax_multiplier
            curr_amount = "${:.2f}".format(curr_amount)
            curr_date = components[f"payment {i+1}"].get('date')

        payment_info.append(
            {
                "label_l": f"payment {i+1}".rjust(10),
                "info_l": curr_amount,
                "label_r": "on date".rjust(20),
                "info_r": curr_date,
            }
        )

    insert_2col_table(document=doc, table_heading="Client Information".upper(), table_items=client_info_top)
    insert_2col_table(document=doc, table_heading="\n\nCard Information".upper(), table_items=card_info_2col)
    doc.add_page_break()
    insert_4col_table(document=doc, table_heading="Payment Information (including applicable GST and PST)".upper(), table_items=payment_summary)
    insert_4col_table(document=doc, table_heading="", table_items=payment_info)

    client_name = f'{components["client 1 first name"].get().strip()} - {components["client 1 last name"].get().strip()}'

    timestamp_obj = datetime.datetime.now()
    timestamp = str(timestamp_obj.strftime("%H:%M - %B %d %Y"))
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))

    output_filename = f"[{formatted_timestamp}] {components['case ID'].get().strip()} - Payments - {client_name}"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='agreements')

    if response:
        application_fee = "${:.2f}".format(components['application fee'].get('amount') * tax_multiplier)
        installments = components['application fee'].get('months')

        write_file_to_history(
            case_id=components['case ID'].get().strip(), 
            document_type='Payment Authorization', 
            timestamp=timestamp, 
            remarks=f'{application_fee} in {installments} months',
            client_name=components.get('client name').get().strip(), 
            filename=output_filename, 
        )


def write_receipt(doc, components):
    cart = components.get('cart')
    cart_items = []
    case_id = components.get('payment for case ID').get()

    current_serial = 1
    total = 0
    for current_item in cart.get():
        if current_item:
            current_item['info']['serial'] = current_serial
            cart_items.append(current_item['info'])
            total += float(cart_items[current_serial-1].get('price'))
            current_serial += 1

    if len(cart_items) <= 0:
        ErrorPopup('Add at least one item to create a document.')
        return False

    if len(case_id.strip()) == 0:
        case_id = '000000-000'

    receipt_id = "{:010}".format((read_receipt_id() + 1))
    client_name = components.get('client name').get().strip()

    timestamp_obj = datetime.datetime.now()
    timestamp = str(timestamp_obj.strftime("%H:%M - %B %d %Y"))
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))

    filename = f"[{formatted_timestamp}] {case_id} - Receipt {receipt_id} - {client_name}"

    printed_rows = 0
    rows_per_page = 7

    while printed_rows < len(cart_items):
        insert_invoice_info(doc, receipt_id, client_name, timestamp)
        insert_items_table(doc, cart_items[printed_rows : printed_rows + rows_per_page])
        printed_rows += rows_per_page

        if printed_rows < len(cart_items):
            doc.add_page_break()

    insert_totals_table(doc, cart_items)
    response = save_doc(doc=doc, components=components, folder_name='receipts', override_output_filename=filename)

    if response:
        write_receipt_to_history(receipt_id, client_name, components.get('case ID').get())

        write_file_to_history(
            case_id=case_id if len(case_id) > 0 else "000000-000", 
            document_type='Payment Receipt', 
            timestamp=timestamp, 
            remarks=f'#{receipt_id} ({"${:.2f}".format(total)})',
            client_name=components.get('client name').get().strip(),
            filename=filename
        )


def write_retainer(doc, components):
    check_case_id_before_submit(components)
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    tax_multiplier = 1.12 if components['add taxes'].get().lower() == "yes" else 1.00
    case_id = components['case ID'].get().strip()

    # formats the list of data so that it can be displayed on the output document
    def format_payments():
        payments_string = []
        payments_string.append(f"Payment of CAN {'${:.2f}'.format(components[f"payment 1"].get('amount') * tax_multiplier)} to be paid in {components[f"payment 1"].get('date')}, after signing the retainer, is non-refundable.")

        for i in range(2, 13):
            current_amount = components[f"payment {i}"].get('amount')
            current_date = components[f"payment {i}"].get('date')

            if components[f"payment {i}"].get('amount') > 0:
                payments_string.append(f"Payment of CAN {'${:.2f}'.format(current_amount * tax_multiplier)} to be made within {current_date}.")

        return ("\n").join(payments_string)

    document_data = {
        '[DAY]': date_on_document.strftime("%d"),
        '[MONTH]': date_on_document.strftime("%b"),
        '[YEAR]': date_on_document.strftime("%Y"),
        '[CLIENT1]': (f"{components["client 1 first name"].get()} {components["client 1 last name"].get()}").strip(),
        '[EMAIL1]': components["client 1 email"].get(),
        '[PHONE1]': components["client 1 phone"].get(),
        '[CLIENT2]': (f"{components["client 2 first name"].get()} {components["client 2 last name"].get()}").strip(),
        '[EMAIL2]': components["client 2 email"].get(),
        '[PHONE2]': components["client 2 phone"].get(),
        '[APP_TYPE]': components["application type"].get(),
        '[APP_FEE]': "${:.2f}".format(components["application fee"].get('amount') * tax_multiplier),
        '[PAY_PLAN]': format_payments(),
    }

    for d in ['[CLIENT1]', '[EMAIL1]', '[PHONE1]', '[APP_TYPE]', '[APP_FEE]', '[PAY_PLAN]']:
        if len(document_data[d].strip()) == 0:
            ErrorPopup(msg="Failed to create retainer.\n\nThe following must not be empty:\n"
                + "- client 1 first name\n"
                + "- client 1 last name\n"
                + "- client 1 phone number\n"
                + "- client 1 email\n"
                + "- application type\n"
                + "- application fee\n"
                + "- payment plan"
            )

            return False

    overwrite_placeholders(doc, document_data)

    client_signatures = [
        {
            "label_l": f"{document_data['[CLIENT1]']}\n{document_data['[PHONE1]']}\n{document_data['[EMAIL1]']}",
            "info_l": "",
            "label_r": f"{document_data['[CLIENT2]']}\n{document_data['[PHONE2]']}\n{document_data['[EMAIL2]']}",
            "info_r": "",
        },
    ]

    insert_4col_table(document=doc, table_heading="", table_items=client_signatures)

    timestamp_obj = datetime.datetime.now()
    timestamp = str(timestamp_obj.strftime("%H:%M - %B %d %Y"))
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))

    output_filename = f"[{formatted_timestamp}] {case_id} - Retainer - {document_data['[CLIENT1]']}"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='agreements')

    if response:
        write_agreement_to_history(components)

        write_file_to_history(
            case_id=case_id, 
            document_type='Retainer Agreement', 
            timestamp=timestamp, 
            remarks=f'{components['application type'].get()} ({"${:.2f}".format(components['application fee'].get('amount') * tax_multiplier)})',
            client_name=components.get('client name').get().strip(), 
            filename=output_filename, 
        )

        components['service'].set(components['application type'].get())
        components['quantity'].set('1')
        components['PST percentage'].set('5.0')
        components['PST percentage'].set('7.0')
        components['rate'].set(f'${components['payment 1'].get('amount')}')
        components['price'].set("${:,.2f}".format(float(components['payment 1'].get('amount')) * 1.12))
        components['cart'].tools.buttons[3].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
        components['cart'].tools.buttons[4].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
        components['cart'].reset()

        return response


def write_conduct(doc, components):
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    case_id = components['case ID'].get().strip()

    document_data = {
        '[DAY]': date_on_document.strftime("%d"),
        '[MONTH]': date_on_document.strftime("%b"),
        '[YEAR]': date_on_document.strftime("%Y"),
        '[CLIENT1]': (f"{components["client 1 first name"].get()} {components["client 1 last name"].get()}").strip(),
        '[APP_TYPE]': components["application type"].get(),
    }

    for d in ['[CLIENT1]', '[APP_TYPE]']:
        if len(document_data[d].strip()) == 0:
            ErrorPopup(msg="Failed to create code of conduct.\n\nThe following must not be empty:\n"
                + "- client 1 first name\n"
                + "- client 1 last name\n"
                + "- client 1 phone number\n"
                + "- client 1 email\n"
                + "- application type\n"
            )

            return False

    overwrite_placeholders(doc, document_data)

    timestamp_obj = datetime.datetime.now()
    timestamp = str(timestamp_obj.strftime("%H:%M - %B %d %Y"))
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))

    output_filename = f"[{formatted_timestamp}] {case_id} - Conduct - {document_data['[CLIENT1]']}"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='agreements')

    if response:
        write_file_to_history(
            case_id=components['case ID'].get().strip(), 
            document_type='Code of Conduct', 
            timestamp=timestamp, 
            remarks=components['application type'].get(),
            client_name=components.get('client name').get().strip(),
            filename=output_filename, 
        )


def write_invitation(doc, components):
    case_id = components['case ID'].get().strip()
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    bearer_of_expenses = {
        'host(s)': "paid for by me and will be my responsibility",
        'guest(s)': "their own responsibility and will be paid for by themselves. I will provide additional support if any assistance is needed",
    }

    document_data = {
        '[DAY]': date_on_document.strftime("%d"),
        '[MONTH]': date_on_document.strftime("%b"),
        '[YEAR]': date_on_document.strftime("%Y"),
        '[BEARER]': bearer_of_expenses.get(components["bearer of expenses"].get(), bearer_of_expenses['host(s)']),
        '[GUEST_PURPOSE]': components['purpose of visit'].get(),
        '[GUEST_CANADIAN_ADDRESS]': components['address in Canada'].get(),
        '[GUEST_ARRIVAL]': components['arrival date'].get(),
        '[GUEST_DEPARTURE]': components['departure date'].get(),
        '[GUEST_RESIDENCE]': components['country of residence'].get(),
    }

    for i in range(1,3):
        if components[f'host {i} name'].get().strip() != '':
            other_host = "2" if i==1 else "1"
            document_data[f'[HOST{i}_NAME]'] = components[f"host {i} name"].get().strip()
            document_data[f'[HOST{i}_BIRTH]'] = components[f"host {i} date of birth"].get().strip()
            document_data[f'[HOST{i}_PASSPORT]'] = components[f"host {i} passport no."].get().strip()
            document_data[f'[HOST{i}_ADDRESS]'] = components[f"host {i} address"].get().strip()
            document_data[f'[HOST{i}_PHONE]'] = components[f"host {i} phone number"].get().strip()
            document_data[f'[HOST{i}_EMAIL]'] = components[f"host {i} email address"].get().strip()
            document_data[f'[HOST{i}_OCCUPATION]'] = components[f"host {i} occupation"].get().strip()
            document_data[f'[HOST{i}_STATUS]'] = components[f"host {i} status in Canada"].get().strip()
            document_data[f'[HOST{i}_RELATION_TO_HOST{other_host}]'] = components[f'relationship to host {other_host}'].get().lower().strip()

    for i in range(1,6):
        if components[f'guest {i} name'].get().strip() != '':
            document_data[f'[GUEST{i}_BIRTH]'] = components[f"guest {i} date of birth"].get().strip()
            document_data[f'[GUEST{i}_PASSPORT]'] = components[f"guest {i} passport no."].get().strip()
            document_data[f'[GUEST{i}_ADDRESS]'] = components[f"guest {i} address"].get().strip()
            document_data[f'[GUEST{i}_PHONE]'] = components[f"guest {i} phone number"].get().strip()
            document_data[f'[GUEST{i}_EMAIL]'] = components[f"guest {i} email address"].get().strip()
            document_data[f'[GUEST{i}_OCCUPATION]'] = components[f"guest {i} occupation"].get().strip()
            document_data[f'[GUEST{i}_CITIZENSHIP]'] = components[f"guest {i} country of citizenship"].get().strip()

    ic(document_data)


def write_imm5476(doc, components):
    date_on_document = datetime.datetime.now()
    case_id = components['case ID'].get().strip()

    document_data = {
        '[DAY]': date_on_document.strftime("%d"),
        '[MONTH]': date_on_document.strftime("%b"),
        '[YEAR]': date_on_document.strftime("%Y"),
        '[signedDate1]': (f"{components["date on document"].get().strip()}"),
        '[signedDate2]': (f"{components["date on document"].get().strip()}"),
        '[applicantUCI]': (f"{components["client 1 UCI"].get().strip()}"),
        '[applicantDOB]': (f"{components["client 1 date of birth"].get().strip()}"),
        '[applicantGivenName]': (f"{components["client 1 first name"].get().strip()}"),
        '[applicantSurname]': (f"{components["client 1 last name"].get().strip().ljust(48)}"),
        '[nameOfOffice]': "".ljust(45),
        '[typeOfApplication]': (f""),
    }

    for d in ['[applicantUCI]', '[applicantDOB]', '[applicantGivenName]', '[applicantSurname]']:
        if len(document_data[d].strip()) == 0:
            ErrorPopup(msg="Failed to create imm5476.\n\nThe following must not be empty:\n"
                + "- client 1 first name\n"
                + "- client 1 last name\n"
                + "- client 1 UCI\n"
                + "- client 1 date of birth\n"
            )

            return False

    document_data["[applicantDOB]"] = datetime.datetime.strptime(document_data["[applicantDOB]"], "%b %d, %Y")
    document_data["[signedDate1]"] = datetime.datetime.strptime(document_data["[signedDate1]"], "%b %d, %Y")
    document_data["[signedDate2]"] = datetime.datetime.strptime(document_data["[signedDate2]"], "%b %d, %Y")
    document_data["[applicantDOB]"] = datetime.datetime.strftime(document_data["[applicantDOB]"], '%Y-%m-%d')
    document_data["[signedDate1]"] = datetime.datetime.strftime(document_data["[signedDate1]"], '%Y-%m-%d')
    document_data["[signedDate2]"] = datetime.datetime.strftime(document_data["[signedDate2]"], '%Y-%m-%d')

    if components["client 2 first name"].get().strip() == "" and components["client 2 last name"].get().strip() == "":
        document_data["[signedDate2]"] = ""

    overwrite_placeholders(doc, document_data)

    timestamp_obj = datetime.datetime.now()
    timestamp = str(timestamp_obj.strftime("%H:%M - %B %d %Y"))
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))

    output_filename = f"[{formatted_timestamp}] {case_id} - {document_data['[applicantSurname]'].strip()} - {document_data['[applicantGivenName]'].strip()} - imm5476"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='imm5476')

    if response:
        write_file_to_history(
            case_id=components['case ID'].get().strip(), 
            document_type='Use of Representative', 
            timestamp=timestamp, 
            remarks=components['application type'].get(),
            client_name = components.get('client name').get().strip(),
            filename=output_filename, 
        )


def overwrite_placeholders(doc, document_data):
    try:
        for paragraph in doc.paragraphs:
            for key, value in document_data.items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        run.text = run.text.replace(key, value)

    except Exception as e:
        print(e)


def write_agreement_to_history(app_components=None):

    if app_components is None:
        return

    csv_columns = ['case_id', 'created_by', 'created_date', 'document_type', 'date_on_document', 'client_1_name', 'client_1_email', 'client_1_phone', 'client_2_name', 'client_2_email', 'client_2_phone', 'application_type', 'application_fee', 'add_taxes']

    # set up csv_columns
    for i in range(1,13):
        csv_columns.append(f"amount_{str(i)}")
        csv_columns.append(f"date_{str(i)}")

    check_history_dir_and_file(f"{os.getcwd()}\\write", "agreements.csv", csv_columns)

    # things to enter into the new entry
    history_entry = [app_components['case ID'].get().strip()]
    history_entry.append(os.environ['COMPUTERNAME'])
    history_entry.append(str(datetime.datetime.now().strftime("%Y-%b-%d %I:%M %p")))
    history_entry.append('Retainer Agreement')
    history_entry.append(app_components.get('date on document').get())
    history_entry.append(f"{app_components.get('client 1 first name').get().strip()} {app_components.get('client 1 last name').get().strip()}".strip())
    history_entry.append(app_components.get('client 1 email').get().strip())
    history_entry.append(app_components.get('client 1 phone').get().strip())
    history_entry.append(f"{app_components.get('client 2 first name').get().strip()} {app_components.get('client 2 last name').get().strip()}".strip())
    history_entry.append(app_components.get('client 2 email').get().strip())
    history_entry.append(app_components.get('client 2 phone').get().strip())
    history_entry.append(app_components.get('application type').get())
    history_entry.append(app_components.get('application fee').get('amount'))
    history_entry.append(app_components.get('add taxes').get())

    for i in range(1,13):
        current_amount = (app_components.get(f'payment {i}').get('amount'))
        current_date = (app_components.get(f'payment {i}').get('date'))

        if int(current_amount) == 0:
            history_entry.append("")
            history_entry.append("")
            continue

        history_entry.append(str(current_amount))
        history_entry.append(str(current_date))

    # remove commas from strings as it interferes with the csv
    for index, col in enumerate(history_entry):
        history_entry[index] = re.sub("[,]\\s*", "_", str(col))

    with open(f"{os.getcwd()}\\write\\agreements.csv", "r") as history:
        readlines = history.readlines()

    with open(f"{os.getcwd()}\\write\\agreements.csv", "a+") as history:
        readlines = history.readlines()
        sorted_lines = []
        print(readlines)

        if len(readlines) > 1:
            sorted_lines = [readlines[0]] + sorted(readlines[1:])

        sorted_lines += ["\n" + (',').join(history_entry)]
        history.write(('').join(sorted_lines))


def write_receipt_to_history(doc_id="", client_name="", case_id=""):
    client_name = client_name.strip()

    check_history_dir_and_file(f'{os.getcwd()}\\write\\', 'receipts.csv', (['case_id', 'created_by', 'created_date', 'document_id', 'client_name']))

    records_file = (f'{os.getcwd()}\\write\\receipts.csv').replace('\\write\\write', '\\receipts')
    doc_id = str('[{:010}]'.format(doc_id))
    timestamp = datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%I]")

    try:
        with open(records_file, 'a') as log_file:
            log_file.write((",").join([case_id, os.environ['COMPUTERNAME'], timestamp, doc_id, client_name]))
            log_file.write("\n")

    except Exception as e:
        print(e)


def write_file_to_history(case_id="", document_type="", timestamp="", remarks="", client_name="", filename="") -> bool:
    check_history_dir_and_file(f'{os.getcwd()}\\write\\', 'files.csv', (['case_id', 'document_type', 'created_by', 'created_date', 'remarks', 'client_name', 'filename']))
    records_file = (f'{os.getcwd()}\\write\\files.csv').replace('\\write\\write', '\\files')

    try:
        with open(records_file, 'r') as log_file:
            all_lines = log_file.readlines()
            prev_entry_list = all_lines[-1].strip().split(',')

            new_entry_list = [case_id, document_type, os.environ['COMPUTERNAME'], timestamp, remarks, client_name, filename]
            header_columns = all_lines[0].strip().split(',')
            new_entry_dict = {}
            prev_entry_dict = {}

            for idx, col in enumerate(header_columns):
                if col == 'created_date':
                    continue

                new_entry_dict[col] = new_entry_list[idx]
                prev_entry_dict[col] = prev_entry_list[idx]

            new_entry_string = (",").join(new_entry_list)

        if(new_entry_dict == prev_entry_dict):
            with open(records_file, 'w') as log_file:
                all_lines = all_lines[0:-1]
                log_file.writelines(all_lines)
                log_file.write(new_entry_string+'\n')

        else:
            with open(records_file, 'a') as log_file:
                log_file.write(new_entry_string+'\n')

    except Exception as e:
        print(e)
        return False

    return True


def remove_file_from_history(filename) -> bool:
    check_history_dir_and_file(f'{os.getcwd()}\\write\\', 'files.csv', (['case_id', 'document_type', 'created_by', 'created_date', 'remarks', 'client_name', 'filename']))
    records_file = (f'{os.getcwd()}\\write\\files.csv').replace('\\write\\write', '\\files')
    keep_lines = []
    matched_line = None
    filename  = filename.replace('.docx', '')

    try:
        with open(records_file, 'r') as log_file:
            all_lines = log_file.readlines()

        for curr_line in all_lines:
            if filename in curr_line.strip():
                matched_line = curr_line.strip()
            else:
                keep_lines.append(curr_line)

        if matched_line is not None:
            with open(records_file, 'w') as log_file:
                log_file.writelines(keep_lines)
        else:
            return False

    except Exception as e:
        print(e)
        return False

    return True


def check_history_dir_and_file(check_dir, check_file, csv_columns):
    # set up write directory
    if not os.path.exists(check_dir):
        os.makedirs(check_dir)

    if not os.path.exists(f"{check_dir}\\{check_file}"):
        # write the header csv_columns to file
        with open(f"{check_dir}\\{check_file}", "x") as history:
            history.write(",".join(csv_columns))
            history.write("\n")
            history.close()


def check_case_id_before_submit(components):
    prev_case_id = read_case_id(get_next=False)
    curr_case_id = components['case ID'].get().strip()
    next_case_id = f"{prev_case_id.split('-')[0]}-{"{:03}".format(int(prev_case_id.split('-')[1]) + 1)}"

    if prev_case_id == curr_case_id:
        InfoPopup(msg=f"current case ID {curr_case_id} is already occupied, next available case ID {next_case_id} will be used for this case.")
        components.get('case ID').set(next_case_id)

def get_prompt_response(prompt="") -> str:
    import google.generativeai as genai
    from dotenv import load_dotenv

    if prompt.strip() == "":
        return ""

    load_dotenv()
    genai.configure(api_key=os.getenv('API_KEY'))

    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)

    return(response.text)
