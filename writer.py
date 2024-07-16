import os
import datetime
import re
import zlib
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from Path import *
from Doc import *
from icecream import ic
from dotenv import load_dotenv
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


def write_auth(doc, components):

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

    client_info_bottom = [
        {
            "label_l": "province",
            "info_l": components["province"].get(),
            "label_r": "city",
            "info_r": components["city"].get(),
        },
        {
            "label_l": "postal code",
            "info_l": components["postal code"].get(),
            "label_r": "",
            "info_r": "",
        },
    ]

    card_info_4col = [
        {
            "label_l": "card type",
            "info_l": components["card type"].get(),
            "label_r": "expiration",
            "info_r": components["expiration"].get(),
        },
    ]

    card_info_2col = [
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
        {
            "label": "billing address",
            "info": components["billing address"].get(),
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

        print(curr_amount, curr_date)

    insert_2col_table(document=doc, table_heading="Client Information".upper(), table_items=client_info_top)
    insert_4col_table(document=doc, table_heading="".upper(), table_items=client_info_bottom)
    insert_4col_table(document=doc, table_heading="\n\n\nCard Information".upper(), table_items=card_info_4col)
    insert_2col_table(document=doc, table_heading="", table_items=card_info_2col)
    insert_4col_table(document=doc, table_heading="\n\nPayment Information (including applicable GST and PST)".upper(), table_items=payment_summary)
    insert_4col_table(document=doc, table_heading="", table_items=payment_info)
    save_doc(doc, components, "Payments")


def obscure(unobscured: str) -> str:
    return b64e(zlib.compress(str.encode(unobscured), 9)).decode()


def unobscure(obscured: str) -> str:
    return zlib.decompress(b64d(str.encode(obscured))).decode()


def write_to_placeholders(doc, components, doctype):
    date_on_document = datetime.datetime.strptime(components['date on document'].get(), "%b %d, %Y")
    tax_multiplier = 1.12 if components['add taxes'].get().lower() == "yes" else 1.00

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
        '[CLIENT1]': f"{components["client 1 first name"].get()} {components["client 1 last name"].get()}",
        '[EMAIL1]': components["client 1 email"].get(),
        '[PHONE1]': components["client 1 phone"].get(),
        '[CLIENT2]': f"{components["client 2 first name"].get()} {components["client 2 last name"].get()}",
        '[EMAIL2]': components["client 2 email"].get(),
        '[PHONE2]': components["client 2 phone"].get(),
        '[APP_TYPE]': components["application type"].get(),
        '[APP_FEE]': "${:.2f}".format(components["application fee"].get('amount') * tax_multiplier),
        '[PAY_PLAN]': format_payments(),
    }

    try:
        for paragraph in doc.paragraphs:
            for key, value in document_data.items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        run.text = run.text.replace(key, value)

        client_signatures = []

        if len(document_data['[CLIENT2]'].strip()) == 0:
            client_signatures = [
                {
                    "label_l": document_data['[CLIENT1]'].strip(),
                    "info_l": "",
                    "label_r": document_data['[CLIENT2]'].strip(),
                    "info_r": "",
                },
            ]

        insert_4col_table(document=doc, table_heading="", table_items=client_signatures)
        save_doc(doc, components, doctype)

    except Exception as e:
        print(e)

