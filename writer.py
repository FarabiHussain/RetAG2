import os
import datetime
import re
import zlib
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from Path import *
from Doc import *
from icecream import ic
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from dotenv import load_dotenv
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

def write_auth(doc, data):

    client_info_top = [
        {
            "label": "first name",
            "info": data["client 1 first name"],
        },
        {
            "label": "last name",
            "info": data["client 1 last name"],
        },
        {
            "label": "email",
            "info": data["client 1 email"],
        },
        {
            "label": "phone",
            "info": data["client 1 phone"],
        },
        {
            "label": "address",
            "info": data["address"],
        }
    ]

    client_info_bottom = [
        {
            "label_l": "province",
            "info_l": data["province"],
            "label_r": "city",
            "info_r": data["city"],
        },
        {
            "label_l": "postal code",
            "info_l": data["postal code"],
            "label_r": "",
            "info_r": "",
        },
    ]

    card_info_4col = [
        {
            "label_l": "card type",
            "info_l": data["card type"],
            "label_r": "expiration",
            "info_r": data["expiration"],
        },
    ]

    card_info_2col = [
        {
            "label": "card number",
            "info": data["card number"],
        },
        {
            "label": "security code",
            "info": obscure(data["security code"]),
        },
        {
            "label": "cardholder name",
            "info": data["cardholder name"],
        },
        {
            "label": "billing address",
            "info": data["billing address"],
        },
    ]

    tax_multiplier = 1.12 if data['add taxes'] is True else 1.00

    payment_summary = [
        {
            "label_l": "Total of",
            "info_l": "${:.2f}".format(data['total_amount'] * tax_multiplier),
            "label_r": "           paid over",
            "info_r": f"{data['total_months']} {"month" if data['total_months'] == 1 else "months"}",
        }
    ]

    payment_info = []
    for i in range(12):
        curr_amount = f"{"{:.2f}".format(float((data[f"payment {i+1}"]['amount']).replace("$", "")) * tax_multiplier)}" if f"payment {i+1}" in data else "N/A"
        curr_date = data[f"payment {i+1}"]['date'] if f"payment {i+1}" in data else "N/A"

        payment_info.append(
            {
                "label_l": f"payment {i+1}",
                "info_l": f"{"$" if curr_amount is not "N/A" else ""}{curr_amount}",
                "label_r": "           on date",
                "info_r": curr_date,
            }
        )

    insert_2col_table(document=doc, table_heading="Client Information".upper(), table_items=client_info_top)
    insert_4col_table(document=doc, table_heading="".upper(), table_items=client_info_bottom)
    insert_4col_table(document=doc, table_heading="\n\n\nCard Information".upper(), table_items=card_info_4col)
    insert_2col_table(document=doc, table_heading="", table_items=card_info_2col)
    insert_4col_table(document=doc, table_heading="\n\nPayment Information (including applicable GST and PST)".upper(), table_items=payment_summary)
    insert_4col_table(document=doc, table_heading="", table_items=payment_info)
    save_doc(doc, data)


def obscure(unobscured: str) -> str:
    return b64e(zlib.compress(str.encode(unobscured), 9)).decode()

def unobscure(obscured: str) -> str:
    return zlib.decompress(b64d(str.encode(obscured))).decode()


def write_retainer(doc, data):
    try:
        for paragraph in doc.paragraphs:
            for key, value in data['input_data'].items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        run.text = run.text.replace(key, value)
    except Exception as e:
        print(e)

