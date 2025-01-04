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
from Database import Database


def obscure(unobscured: str) -> str:
    return b64e(zlib.compress(str.encode(unobscured), 9)).decode()


def unobscure(obscured: str) -> str:
    return zlib.decompress(b64d(str.encode(obscured))).decode()


def calculate_taxes(components):
    tax_multiplier = 1.00

    try:
        tax_multiplier += float(components['add taxes'].get().replace("%", "")) * 0.01
    except Exception as e:
        ErrorPopup(msg=f"could not set tax rate as {components['add taxes'].get()}. Tax has been set to 0.0%")

    return tax_multiplier


def write_payment_auth(doc, components):
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Poppins'
    font.size = PT(8)

    payment_info = []
    case_id = components['case ID'].get().strip()
    timestamp_obj = datetime.datetime.now()
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))
    client_name = f'{components["client 1 first name"].get().strip()} - {components["client 1 last name"].get().strip()}'
    output_filename = f"[{formatted_timestamp}] {components['case ID'].get().strip()} - Payments - {client_name}"
    tax_multiplier = calculate_taxes(components)

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
            "info": components["payment type"].get(),
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

    payment_summary = [
        {
            "label_l": "Total of".rjust(10),
            "info_l": "${:.2f}".format(components['application fee'].get('amount') * tax_multiplier),
            "label_r": "paid over".rjust(20),
            "info_r": f"{components['application fee'].get('months')} {"month" if components['application fee'].get('months') == 1 else "months"}",
        }
    ]

    for i in range(12):
        curr_amount = "N/A"
        curr_date = "N/A"

        if components[f"payment {i+1}"].get('amount') > 0:
            curr_amount_float = float(components[f"payment {i+1}"].get('amount')) * tax_multiplier
            curr_amount = "${:.2f}".format(curr_amount_float)
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

    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='agreements')

    if response:
        application_fee = "${:.2f}".format(components['application fee'].get('amount') * tax_multiplier)
        installments = components['application fee'].get('months')

        write_to_database(
            'files', 
            (
                case_id, 
                os.environ['COMPUTERNAME'], 
                components.get('client name').get().strip(), 
                formatted_timestamp, 
                'Payment Authorization', 
                output_filename, 
                f'{application_fee} in {installments} months'
            )
        )


def write_receipt(doc, components):
    cart = components.get('cart')
    cart_items = []
    case_id = components.get('payment for case ID').get()

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Poppins'
    font.size = PT(8)

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
    output_filename = f"[{formatted_timestamp}] {case_id} - Receipt {receipt_id} - {client_name}"

    printed_rows = 0
    rows_per_page = 7

    while printed_rows < len(cart_items):
        insert_invoice_info(doc, receipt_id, client_name, timestamp)
        insert_items_table(doc, cart_items[printed_rows : printed_rows + rows_per_page])
        printed_rows += rows_per_page

        if printed_rows < len(cart_items):
            doc.add_page_break()

    insert_totals_table(doc, cart_items)
    response = save_doc(doc=doc, components=components, folder_name='receipts', override_output_filename=output_filename)

    if response:

        write_to_database('files', (case_id, os.environ['COMPUTERNAME'],components.get('client name').get().strip(), formatted_timestamp, 'Payment Receipt', output_filename, f'#{receipt_id} ({"${:.2f}".format(total)})'))
        write_to_database('receipts', (receipt_id, case_id, os.environ['COMPUTERNAME'], client_name, formatted_timestamp, output_filename))


def write_retainer(doc, components):
    check_case_id_before_submit(components)
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    case_id = components['case ID'].get().strip()
    tax_multiplier = calculate_taxes(components)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Poppins'
    font.size = PT(7)

    # formats the list of data so that it can be displayed on the output document
    def format_payments():
        payments_string = []
        payments_string.append(f"Payment of CAN {'${:.2f}'.format(components[f"payment 1"].get('amount') * tax_multiplier)} to be paid on {components[f"payment 1"].get('date')}, after signing the retainer, is non-refundable.")

        for i in range(2, 13):
            current_amount = components[f"payment {i}"].get('amount')
            current_date = components[f"payment {i}"].get('date')

            if components[f"payment {i}"].get('amount') > 0:
                payments_string.append(f"Payment of CAN {'${:.2f}'.format(current_amount * tax_multiplier)} to be made within {current_date}.")

        return ("\n").join(payments_string)

    document_data = {
        '[CASE_ID]': case_id,
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
        '[APP_FEE]': "${:.2f}".format(components['application fee'].get('amount') * tax_multiplier),
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
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))
    output_filename = f"[{formatted_timestamp}] {case_id} - Retainer - {document_data['[CLIENT1]']}"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='agreements')

    if response:
        new_payments = []
        tax_multiplier = calculate_taxes(components)

        for i in range(12):
            if components[f"payment {i+1}"].get('amount') > 0:
                curr_amount_float = float(components[f"payment {i+1}"].get('amount')) * tax_multiplier
                curr_amount = "${:.2f}".format(curr_amount_float)
                curr_date = components[f"payment {i+1}"].get('date')

                new_payments.append(
                    (
                        components['case ID'].get(),
                        f'{components["client 1 first name"].get()} {components["client 1 last name"].get()}',
                        components["client 1 phone"].get(),
                        curr_amount,
                        datetime.datetime.strftime(datetime.datetime.strptime(curr_date, "%b %d, %Y"), "%Y%m%d"),
                        0,
                        output_filename
                    )
                )

        new_agreement = (
            components['case ID'].get(),
            os.environ['COMPUTERNAME'],
            str(datetime.datetime.now().strftime("%Y-%b-%d %I:%M %p")),
            'Retainer Agreement',
            f"{components['client 1 first name'].get()} {components['client 1 last name'].get()}",
            components['client 1 email'].get(),
            components['client 1 phone'].get(),
            f"{components['client 2 first name'].get()} {components['client 2 last name'].get()}",
            components['client 2 email'].get(),
            components['client 2 phone'].get(),
            components['application type'].get(),
            components['application fee'].get('amount'),
            components['date on document'].get(),
            components['add taxes'].get(),
            output_filename
        )

        new_file = (
            case_id, 
            os.environ['COMPUTERNAME'], 
            document_data['[CLIENT1]'], 
            formatted_timestamp, 
            'Retainer Agreement', 
            output_filename, 
            f'{document_data['[APP_TYPE]']} ({document_data['[APP_FEE]']})'
        )

        write_to_database('agreements', new_agreement)
        write_to_database('payments', new_payments)
        write_to_database('files', new_file)

        return response


def write_conduct(doc, components):
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    case_id = components['case ID'].get().strip()

    document_data = {
        '[DAY]': date_on_document.strftime("%d"),
        '[MONTH]': date_on_document.strftime("%b"),
        '[YEAR]': date_on_document.strftime("%Y"),
        '[CLIENT1]': (f"{components["client 1 first name"].get()} {components["client 1 last name"].get()}").strip(),
        '[APP_TYPE]': components["application type"].get().strip(),
    }

    document_data['[APP_TYPE]'].replace('application', '').replace('Application', '')

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
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))
    output_filename = f"[{formatted_timestamp}] {case_id} - Conduct - {document_data['[CLIENT1]']}"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='agreements')

    if response:
        write_to_database(
            'files',
            (
                case_id, 
                os.environ['COMPUTERNAME'],
                components.get('client name').get().strip(), 
                formatted_timestamp, 
                'Code of Conduct', 
                output_filename, 
                f"for {components['application type'].get()}"
            )
        )


def write_invitation(doc, components):
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    has_second_host = False

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
        '[GUEST_ARRIVAL]': components['arrival date'].get(),
        '[GUEST_DEPARTURE]': components['departure date'].get(),
        '[GUEST_CANADIAN_ADDRESS]': components['address in Canada'].get(),
        '[GUEST_RESIDENCE]': components['country of residence'].get(),
        '[GUEST_NAMES]': [],
        '[GUEST_INFO]': [],
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

        has_second_host = '[HOST2_NAME]' in document_data

    for i in range(1,6):
        if components[f'guest {i} name'].get().strip() != '':
            document_data['[GUEST_NAMES]'].append(components[f'guest {i} name'].get().strip())
            document_data['[GUEST_INFO]'].append(f"{components[f'guest {i} name'].get().strip()}, born {components[f'guest {i} date of birth'].get().strip()}, passport #{components[f'guest {i} passport no.'].get().strip()}")
            document_data[f'[GUEST{i}_NAME]'] = components[f"guest {i} name"].get().strip()
            document_data[f'[GUEST{i}_BIRTH]'] = components[f"guest {i} date of birth"].get().strip()
            document_data[f'[GUEST{i}_PASSPORT]'] = components[f"guest {i} passport no."].get().strip()
            document_data[f'[GUEST{i}_ADDRESS]'] = components[f"guest {i} address"].get().strip()
            document_data[f'[GUEST{i}_PHONE]'] = components[f"guest {i} phone number"].get().strip()
            document_data[f'[GUEST{i}_EMAIL]'] = components[f"guest {i} email address"].get().strip()
            document_data[f'[GUEST{i}_OCCUPATION]'] = components[f"guest {i} occupation"].get().strip()
            document_data[f'[GUEST{i}_CITIZENSHIP]'] = components[f"guest {i} country of citizenship"].get().strip()
            document_data[f'[GUEST{i}_RELATION_TO_HOST1]'] = components[f"guest {i} relation to host 1"].get().strip()

    def replace_last(string, delimiter, replacement):
        start, _, end = string.rpartition(delimiter)
        return start + replacement + end

    document_data['[GUEST_NAMES]'] = replace_last((', ').join(document_data['[GUEST_NAMES]']), (", "), ", and ")
    document_data['[GUEST_INFO]'] = ('\n').join(document_data['[GUEST_INFO]'])

    if has_second_host:
        doc = Document(resource_path("assets\\templates\\invitation_2.docx"))
        intro_text = (f"This letter is to express me and my {document_data[f'[HOST1_RELATION_TO_HOST2]'].lower()}'s interest in inviting {document_data['[GUEST_NAMES]']} to Canada and to furthermore support their Temporary Resident Visa application.")
    else:
        intro_text = (f"This letter is to express my interest in inviting {document_data['[GUEST_NAMES]']} to Canada and to furthermore support their Temporary Resident Visa application.")

    outro_text = (f"\n\n{components['conclusion content'].get()}\nIf any clarification or information is required, please do not hesitate to contact us at our email addresses and phone numbers below.\n\n")

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = PT(10)

    overwrite_placeholders(doc, document_data)
    insert_paragraph(paragraph=doc.add_paragraph(), text=intro_text) # add intro

    for host_number in range(1,3):
        if f'[HOST{host_number}_NAME]' in document_data:
            insert_2col_table(
                document=doc, 
                table_heading="\nMy details are as follows," if host_number == 1 else f"\n\nMy {document_data.get('[HOST2_RELATION_TO_HOST1]', '')}'s details are as follows,", 
                table_items=[
                    {"label": "Full Name", "info": document_data[f'[HOST{host_number}_NAME]']},
                    {"label": "Date of Birth", "info": document_data[f'[HOST{host_number}_BIRTH]']},
                    {"label": "Canadian Status", "info": document_data[f'[HOST{host_number}_STATUS]']},
                    {"label": "Passport Number", "info": document_data[f'[HOST{host_number}_PASSPORT]']},
                    {"label": "Residential Address", "info": document_data[f'[HOST{host_number}_ADDRESS]']},
                    {"label": "Phone Number", "info": document_data[f'[HOST{host_number}_PHONE]']},
                    {"label": "Email Address", "info": document_data[f'[HOST{host_number}_EMAIL]']},
                    {"label": "Current Occupation", "info": document_data[f'[HOST{host_number}_OCCUPATION]']},
                ]
            )

    if has_second_host:
        doc.add_page_break()

    for guest_number in range(1,6):
        if f'[GUEST{guest_number}_NAME]' in document_data:
            insert_2col_table(
                document=doc, 
                table_heading=f"\n\n{document_data[f'[GUEST{guest_number}_NAME]']}'s details are as follows,", 
                table_items=[
                    {"label": "Full Name", "info": document_data[f'[GUEST{guest_number}_NAME]']},
                    {"label": "Date of Birth", "info": document_data[f'[GUEST{guest_number}_BIRTH]']},
                    {"label": "Citizen of", "info": document_data[f'[GUEST{guest_number}_CITIZENSHIP]']},
                    {"label": "Passport Number", "info": document_data[f'[GUEST{guest_number}_PASSPORT]']},
                    {"label": "Residential Address", "info": document_data[f'[GUEST{guest_number}_ADDRESS]']},
                    {"label": "Phone Number", "info": document_data[f'[GUEST{guest_number}_PHONE]']},
                    {"label": "Email Address", "info": document_data[f'[GUEST{guest_number}_EMAIL]']},
                    {"label": "Current Occupation", "info": document_data[f'[GUEST{guest_number}_OCCUPATION]']},
                    {"label": "Relationship to Inviter", "info": document_data[f'[GUEST{guest_number}_RELATION_TO_HOST1]']},
                    {"label": "Arrival Date", "info": document_data[f'[GUEST_ARRIVAL]']},
                    {"label": "Departure Date", "info": document_data[f'[GUEST_DEPARTURE]']},
                    {"label": "Primary Residence in Canada", "info": document_data[f'[GUEST_CANADIAN_ADDRESS]']},
                ]
            )

    insert_paragraph(paragraph=doc.add_paragraph(), text=outro_text) # add conclusion

    # table for hosts to sign
    client_signatures = [
        {
            "label_l": f"{document_data.get('[HOST1_NAME]', '')}\n{document_data.get('[HOST1_EMAIL]', '')}\n{document_data.get('[HOST1_PHONE]', '')}",
            "info_l": "",
            "label_r": f"{document_data.get('[HOST2_NAME]', '')}\n{document_data.get('[HOST2_EMAIL]', '')}\n{document_data.get('[HOST2_PHONE]', '')}",
            "info_r": "",
        },
    ]

    insert_4col_table(document=doc, table_heading="", table_items=client_signatures)

    timestamp_obj = datetime.datetime.now()
    formatted_timestamp = str(timestamp_obj.strftime("%Y.%m.%d-%H.%M.%S"))
    output_filename = f"[{formatted_timestamp}] - {components[f"host 1 name"].get().strip()} - Invitation Letter"
    response = save_doc(doc=doc, components=components, override_output_filename=output_filename, folder_name='invitations')

    if response:
        write_to_database(
            'files',
            (
                '000000-000', 
                os.environ['COMPUTERNAME'],
                components.get('client name').get().strip(), 
                formatted_timestamp, 
                'Invitation Letter', 
                output_filename, 
                components['application type'].get()
            )
        )


def write_imm5476(doc, components):
    date_on_document = datetime.datetime.now()
    case_id = components['case ID'].get().strip()
    is_sponsorship = True if ("sponsorship" in (components['application type'].get()).lower()) else False

    document_data = {
        '[DAY]': date_on_document.strftime("%d"),
        '[MONTH]': date_on_document.strftime("%b"),
        '[YEAR]': date_on_document.strftime("%Y"),
        '[signedDate1]': (f"{components["date on document"].get().strip()}"),
        '[signedDate2]': (f"{components["date on document"].get().strip()}") if is_sponsorship else "",
        '[applicantUCI]': (f"{components["client 1 UCI"].get().strip()}"),
        '[applicantDOB]': (f"{components["client 1 date of birth"].get().strip()}"),
        '[applicantGivenName]': (f"{components["client 1 first name"].get().strip()}"),
        '[applicantSurname]': (f"{components["client 1 last name"].get().strip().ljust(48)}"),
        '[nameOfOffice]': "".ljust(45),
        '[typeOfApplication]': (f""),
    }

    for d in ['[applicantDOB]', '[applicantGivenName]', '[applicantSurname]']:
        if len(document_data[d].strip()) == 0:
            ErrorPopup(msg="Failed to create imm5476.\n\nThe following must not be empty:\n"
                + "- client 1 first name\n"
                + "- client 1 last name\n"
                + "- client 1 date of birth\n"
                + "\n\nclient 1 UCI must be provided if the client has one."
            )

            return False

    document_data["[applicantDOB]"] = datetime.datetime.strptime(document_data["[applicantDOB]"], "%b %d, %Y")
    document_data["[applicantDOB]"] = datetime.datetime.strftime(document_data["[applicantDOB]"], '%Y-%m-%d')

    document_data["[signedDate1]"] = datetime.datetime.strptime(document_data["[signedDate1]"], "%b %d, %Y")
    document_data["[signedDate1]"] = datetime.datetime.strftime(document_data["[signedDate1]"], '%Y-%m-%d')

    if is_sponsorship:
        document_data["[signedDate2]"] = datetime.datetime.strptime(document_data["[signedDate2]"], "%b %d, %Y")
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
        write_to_database(
            'files',
            (
                case_id, 
                os.environ['COMPUTERNAME'],
                components.get('client name').get().strip(), 
                formatted_timestamp, 
                'Use of Representative', 
                output_filename, 
                components['application type'].get()
            )
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


def write_to_database(table_name, rows_to_write):

    def questionmarks(rows):
        columns = len(rows[0])
        temp = []

        if isinstance(rows, tuple):
            columns = len(rows)

        for _ in range(columns):
            temp.append("?")

        temp = f"({(', ').join(temp)})"
        return temp

    query_to_execute = f"INSERT INTO {table_name} VALUES {questionmarks(rows_to_write)}"

    try:
        db = Database()

        if isinstance(rows_to_write, list):
            db.cursor.executemany(query_to_execute, rows_to_write)

        elif isinstance(rows_to_write, tuple):
            db.cursor.execute(query_to_execute, rows_to_write)

        db.commit()
        db.close()
    except Exception as e:
        print(e)
        ErrorPopup(str(e))


def remove_from_database(filename) -> bool:
    filename = filename.replace('.docx', '')
    filetype_match = re.search(r'\b[0-1]{3}\b\s*-\s*(\w+)', filename)
    delete_from_files = f"DELETE FROM files WHERE filename = '{filename}'"
    delete_from_payments = ''

    if filetype_match:
        if filetype_match.group(1) == 'Retainer':
            delete_from_payments = f"DELETE FROM payments WHERE filename = '{filename}'"

    try:
        db = Database()
        db.cursor.execute(delete_from_files)
        db.cursor.execute(delete_from_payments)
        db.commit()
        db.close()

    except Exception as e:
        print(e)
        return False

    return True


def check_case_id_before_submit(components):
    prev_case_id = read_case_id(get_next=False)
    curr_case_id = components['case ID'].get().strip()
    next_case_id = f"{prev_case_id.split('-')[0]}-{"{:03}".format(int(prev_case_id.split('-')[1]) + 1)}"

    if prev_case_id == curr_case_id and '-001' not in curr_case_id:
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

