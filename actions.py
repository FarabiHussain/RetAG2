import customtkinter as ctk
import os
import names
import random
import math
from icecream import ic
from Popups import ErrorPopup
from dotenv import load_dotenv
from writer import obscure, unobscure
from reader import read_retainer_history


def decrypt_button(app):
    from GUI import WindowView

    # retrieve object from app.components
    decryptor_window = app.get_window("history window")

    # check whether the object contains a window
    if (decryptor_window is not None) and (not decryptor_window.body.winfo_exists()):
        decryptor_window = None

    # create a new object if None was found
    if decryptor_window is None:
        decryptor_window = WindowView(app=app, window_name="", width=300, height=260)
        app.add_window("history window", decryptor_window)

        decryptor_window.__password_strvar = ctk.StringVar(value="")
        decryptor_window.__encrypted_strvar = ctk.StringVar(value="")
        decryptor_window.__decrypted_strvar = ctk.StringVar(value="")

        ctk.CTkLabel(decryptor_window.body, text="Encrypted CVV", bg_color='transparent').place(x=20, y=5)
        decryptor_window.doc_id_search = ctk.CTkEntry(decryptor_window.body, width=260, border_width=1, corner_radius=2, textvariable=decryptor_window.__encrypted_strvar)
        decryptor_window.doc_id_search.place(x=20, y=28)

        ctk.CTkLabel(decryptor_window.body, text="Password", bg_color='transparent').place(x=20, y=70)
        decryptor_window.client_name_search = ctk.CTkEntry(decryptor_window.body, width=260, border_width=1, corner_radius=2, textvariable=decryptor_window.__password_strvar, show="*")
        decryptor_window.client_name_search.place(x=20, y=93)

        ctk.CTkLabel(decryptor_window.body, text="Decrypted CVV", bg_color='transparent').place(x=20, y=135)
        decryptor_window.client_name_search = ctk.CTkEntry(decryptor_window.body, width=260, border_width=1, corner_radius=2, textvariable=decryptor_window.__decrypted_strvar)
        decryptor_window.client_name_search.place(x=20, y=158)

        ctk.CTkButton(decryptor_window.body, text="Run", border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:run_decryptor(decryptor_window), width=72, height=36).place(x=20, y=205)

        decryptor_window.body.after(202, lambda: decryptor_window.body.focus())

        def run_decryptor(decryptor_window) -> str:
            load_dotenv()

            cipher_text=decryptor_window.__encrypted_strvar.get()
            input_password=decryptor_window.__password_strvar.get()
            # input_password="viewp0rt"

            if os.getenv('PW') == obscure(input_password):
                plain_text = unobscure(cipher_text)
                decryptor_window.__decrypted_strvar.set(plain_text)
            else:
                ErrorPopup(msg=f'Wrong password')

    # bring the window forward if found
    else:
        decryptor_window.show()


def test_button(app):

    app.reset_all_components()

    legal_name = names.get_full_name(gender=random.choice(['male', 'female']))
    legal_name_2 = names.get_full_name(gender=random.choice(['male', 'female']))

    app.components['address'].set("Address")
    app.components['billing address'].set("Address, Winnipeg, MB")
    app.components['card number'].set(f"{str(random.randint(1000000000000000, 9999999999999999))}")
    app.components['card type'].set("Visa")
    app.components['cardholder name'].set(legal_name)
    app.components['add taxes'].set("Yes")
    app.components['city'].set("Winnipeg")
    app.components['expiration'].set(y="2026", m="Dec", d="31")
    app.components['client 1 first name'].set(legal_name.split(" ")[0])
    app.components['client 1 last name'].set(legal_name.split(" ")[1])
    app.components['client 1 email'].set(f"{legal_name.lower().replace(" ","")}@gmail.com")
    app.components['client 1 phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['email'].set(f"{legal_name.lower().replace(" ","")}@gmail.com")
    app.components['phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['client 2 first name'].set(legal_name_2.split(" ")[0])
    app.components['client 2 last name'].set(legal_name_2.split(" ")[1])
    app.components['client 2 email'].set(f"{legal_name_2.lower().replace(" ","")}@gmail.com")
    app.components['client 2 phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['postal code'].set(f"X1X Y2Y")
    app.components['province'].set(f"Manitoba")
    app.components['security code'].set(f"{str(random.randint(100, 999))}")

    total_amount = 0
    total_months = random.randint(1,12)
    for i in range(total_months):
        total_amount += 100
        app.components[f'payment {i+1}'].set("100", "2025", "Jan", i+1)

    app.components['application fee'].set(f"${total_amount}", total_months)

    for i in range(1,14):
        new_row, new_row_info = generate_row_contents(
            app_components=app.components, 
            override_row_content={
                'service': random.choice(["Immigration", "Affidavit", "Invitation Letter", "Notary", "EOI", "MPNP", "PR", "Sousal Sponsorship", "SOWP", "PFL", "PGWP", "Study Permit", "Study Permit Extension", "SRI", "LMIA", "Visitor Visa", "Super Visa"]),
                'quantity': f"{str(random.randint(1, 10))}",
                'rate': str(random.choice([100,200,300,400,500])),
                'tax_rate': 12.0,
                'gst': 7.0,
                'pst': 5.0,
            }
        )

    app.components.get('cart').update(
            row_info=new_row,
            row_contents=new_row_info,
    )


def generate_row_contents(quantity_offset=None, app_components=None, override_row_content={}):
    if quantity_offset is None:
        quantity_offset = 0

    if override_row_content:
        service = override_row_content.get("service")
        quantity = float(override_row_content.get("quantity"))
        rate = float(override_row_content.get("rate"))
        tax_rate = float(override_row_content.get("tax_rate"))

        return (
            [
                f'{service[0:22]}...' if len(service) > 22 else service,
                quantity,
                rate,
                "${:,.2f}".format((rate * quantity * (tax_rate/100))),
                "${:,.2f}".format((rate * quantity * (1+(tax_rate/100)))),
            ], 
            {
                'service': service,
                'quantity': quantity,
                'rate': rate,
                'gst': override_row_content.get("gst"),
                'pst': override_row_content.get("pst"),
                'taxes': str(rate * quantity * (tax_rate/100)),
                'price': str(rate * quantity * (1+(tax_rate/100)))
            }
        )


    service = app_components.get("service").get()
    quantity = float(app_components.get("quantity").get()) + quantity_offset
    rate = float(app_components.get("rate").get().replace("$",""))
    tax_rate = float(app_components.get("GST percentage").get()) + float(app_components.get("PST percentage").get())

    return (
        [
            f'{service[0:22]}...' if len(service) > 22 else service,
            quantity,
            rate,
            "${:,.2f}".format((rate * quantity * (tax_rate/100))),
            "${:,.2f}".format((rate * quantity * (1+(tax_rate/100)))),
        ], 
        {
            'service': service,
            'quantity': quantity,
            'rate': rate,
            'gst': app_components.get("GST percentage").get(),
            'pst': app_components.get("PST percentage").get(),
            'taxes': str(rate * quantity * (tax_rate/100)),
            'price': str(rate * quantity * (1+(tax_rate/100)))
        }
    )


def add_item_button(app):
    app_components = app.get_all_components()
    cart = app_components.get('cart')

    new_row, new_row_info = generate_row_contents(app_components=app_components)

    update_index, existing_item_info = cart.contains(
        row_info=new_row_info, 
        compare_keys = [
            'service',
            'rate',
            'gst',
            'pst',
        ]
    )

    # print(new_row_info, existing_item_info)

    if existing_item_info is not None:
        new_row, new_row_info = generate_row_contents(float(existing_item_info.get('quantity')))

    cart.update(
        row_index=update_index, 
        row_info=new_row_info, 
        row_contents=new_row,
    )


class HistoryViewer():

    def __init__(self, app=None, page_number=0, entries=[]):
        from GUI import RowWidget
        from GUI import WindowView

        if app == None:
            ErrorPopup("Exception in history_button()\n\napp==None")

        # retrieve object from app.components
        history_window = app.get_window("history window")
        self.page_number = 0

        # check whether history entries exist
        if entries == []:
            imported_history = read_retainer_history()

            if len(imported_history) == 0:
                ErrorPopup(msg="No entries in history.")
                return

            entries = imported_history

        # check whether the object contains a window
        if (history_window is not None) and (not history_window.body.winfo_exists()):
            history_window = None

        # create a new object if None was found
        if history_window is None:

            self.window_width = 1640*0.9
            self.window_height = 800
            history_window = WindowView(app=app, window_name="history window", width=self.window_width, height=self.window_height)
            app.add_window("history window", history_window)

            for i in range(3):
                history_window.body.columnconfigure(index=i, weight=1)

            self.header_frame = ctk.CTkFrame(master=history_window.body, fg_color="white", border_width=0, width=self.window_width*0.99, height=self.window_height*0.05)
            RowWidget(parent_frame=self.header_frame, parent_width=self.window_width*0.99, mode="header", row_contents=['client name', 'created by', 'created date', 'application type', 'application fee'])

            self.table_frame = ctk.CTkFrame(master=history_window.body, fg_color="white", border_width=0, width=self.window_width*0.99, height=self.window_height*0.9)
            self.history_table(parent_frame=self.table_frame, parent_width=self.window_width*0.99, entries=entries, page_number=page_number)

            self.tools_frame = ctk.CTkFrame(master=history_window.body, fg_color="white", border_width=0, width=self.window_width*0.99, height=self.window_height*0.05)
            self.tools_frame_widgets = RowWidget(
                parent_frame=self.tools_frame, 
                parent_width=self.window_width*0.99, 
                mode="tools", 
                row_contents=[
                    "previous page", 
                    "next page", 
                    "", 
                    "", 
                    ""
                ], 
                row_content_methods=[
                    lambda:self.history_table_nav(app=app, page_number=self.page_number-1, entries=entries),
                    lambda:self.history_table_nav(app=app, page_number=self.page_number+1, entries=entries),
                    lambda:None,
                    lambda:None,
                    lambda:None,
                ])

            self.tools_frame_widgets.buttons[0].configure(fg_color="light gray", state="disabled")

            if len(entries) < 19:
                self.tools_frame_widgets.buttons[1].configure(fg_color="light gray", state="disabled")

            self.header_frame.grid(row=0, column=1, pady=[5,0])
            self.table_frame.grid(row=1, column=1)
            self.tools_frame.grid(row=2, column=1)

            history_window.body.after(20, lambda: history_window.body.focus())

        # bring the window forward if found
        else:
            ic("showing existing window")
            history_window.show()


    def history_table(self, parent_frame=None, parent_width=0, entries=[], page_number=0):
        from GUI import RowWidget

        self.table_rows = []

        # pad the list with empty entries if less than 18 rows in order to keep a constant table size on the UI
        current_page_rows = entries[(page_number*18):((page_number+1)*18)]
        for i in range(18 - len(current_page_rows)):
            current_page_rows.append(
                {
                    'client_1_name': '',
                    'created_by': '',
                    'created_date': '',
                    'application_type': '',
                    'application_fee': '',
                }
            )

        for index, entry in enumerate(current_page_rows):
            self.table_rows.append(
                RowWidget(
                    parent_frame=parent_frame, 
                    parent_width=parent_width, 
                    row_number=index, 
                    mode="table", 
                    row_contents=[
                        f"{entry.get('client_1_name').title().split(";")[0][0:32]}{"..." if len(entry.get('client_1_name').split(";")[0]) > 32 else ""}",
                        entry.get('created_by'),
                        entry.get('created_date'),
                        f"{entry.get('application_type')[0:32]}{"..." if len(entry.get('application_type')) > 32 else ""}",
                        f"{"${:,.2f}".format(float(entry.get('application_fee')))}" if entry.get('application_fee') != "" else entry.get('application_fee'),
                    ],
                    row_color="#ddd" if index%2==0 else "#eee",
                )
            )


    def history_table_nav(self, app=None, page_number=0, entries=[]):

        if (page_number == 0):
            ic(len(entries))
            self.tools_frame_widgets.buttons[0].configure(fg_color="light gray", state="disabled")
            self.tools_frame_widgets.buttons[1].configure(fg_color="black", state="normal")

        elif (page_number == math.ceil(len(entries)/18)-1):
            self.tools_frame_widgets.buttons[0].configure(fg_color="black", state="normal")
            self.tools_frame_widgets.buttons[1].configure(fg_color="light gray", state="disabled")

        else:
            self.tools_frame_widgets.buttons[0].configure(fg_color="black", state="normal")
            self.tools_frame_widgets.buttons[1].configure(fg_color="black", state="normal")

        for table_row in self.table_rows:
            table_row.cleanup()

        self.page_number=page_number
        self.table_frame.destroy()
        self.table_frame = ctk.CTkFrame(master=app.get_window("history window").body, fg_color="white", border_width=0, width=self.window_width*0.99, height=self.window_height*0.9)
        self.history_table(parent_frame=self.table_frame, parent_width=self.window_width*0.99, entries=entries, page_number=page_number)

        self.header_frame.grid(row=0, column=1)
        self.table_frame.grid(row=1, column=1)
        self.tools_frame.grid(row=2, column=1)
