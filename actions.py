import sys
import globals
import datetime
import customtkinter as ctk
import os
import names
import random
import math
from datetime import datetime as dt
from dateutil import relativedelta as rd
from Database import Database, Mongo
from glob import glob
from icecream import ic
from Popups import ErrorPopup
from dotenv import load_dotenv
from writer import obscure, unobscure, remove_from_database, write_conduct, write_imm5476, write_invitation, write_payment_auth, write_receipt, write_retainer
from reader import import_function, read_case_id
from docx import Document
from Path import resource_path
from Popups import ErrorPopup, InfoPopup, PromptPopup


def decrypt_button(app):
    from GUI import WindowView

    # retrieve object from app.components
    decryptor_window = app.get_window("cvv decryptor")

    # check whether the object contains a window
    if (decryptor_window is not None) and (not decryptor_window.body.winfo_exists()):
        decryptor_window = None

    # create a new object if None was found
    if decryptor_window is None:
        decryptor_window = WindowView(app=app, window_name="CVV Decryptor", width=300, height=260)
        app.add_window("cvv decryptor", decryptor_window)

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

            if os.getenv('PW') == obscure(input_password):
                plain_text = unobscure(cipher_text)
                decryptor_window.__decrypted_strvar.set(plain_text)
            else:
                ErrorPopup(msg=f'Incorrect password')

    # bring the window forward if found
    else:
        decryptor_window.show()


def adjust_time_button(app):
    from GUI import WindowView, DatePicker, TimePicker, RowBreak, Entry, ComboBox
    from datetime import datetime as dt
    load_dotenv()

    # retrieve object from app.components
    adjust_time_window = app.get_window("adjust time")

    # check whether the object contains a window
    if (adjust_time_window is not None) and (not adjust_time_window.body.winfo_exists()):
        adjust_time_window = None

    # create a new object if None was found
    if adjust_time_window is None:
        adjust_time_window = WindowView(app=app, window_name="Adjusted clock in/out", width=500, height=360)
        app.add_window("adjust time", adjust_time_window)

        frame = ctk.CTkFrame(master=adjust_time_window.body, fg_color='#ffffff' if '--dark' not in sys.argv else '#444444')
        frame.place(x=20, y=20)

        RowBreak(frame, heading="details of adjusted clock in/out", top_offset=0)
        staffpicker = ComboBox(frame, label_text="staff name", top_offset=1, options=sorted(os.getenv('STAFF').split(',')))
        timepicker = TimePicker(frame, label_text="time (24-hour format)", top_offset=2)
        datepicker = DatePicker(frame, label_text="date", top_offset=3)
        adminpass = Entry(frame, label_text="admin password", top_offset=4, is_password=True)

        ctk.CTkButton(frame, text="CLOCK IN", border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:run_decryptor("/assets/functions/clock_in.py"), width=180, height=36).grid(row=5, column=0, columnspan=2, pady=10)
        ctk.CTkButton(frame, text="CLOCK OUT", border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:run_decryptor("/assets/functions/clock_out.py"), width=180, height=36).grid(row=5, column=1, columnspan=3, pady=10)

        def run_decryptor(functionpath) -> str:
            input_password = adminpass.get()

            if os.getenv('PW') == obscure(input_password):
                staff_name = staffpicker.get()
                adjusted_time = f'{dt.strftime(dt.strptime(datepicker.get(), "%b %d, %Y"), "%Y%m%d")}_{dt.strftime(dt.strptime(timepicker.get(), "%H:%M"), "%H%M")}'
                import_function(functionpath, "callback")(app, adjusted_time, staff_name)
            else:
                ErrorPopup(msg='Incorrect password')

    # bring the window forward if found
    else:
        adjust_time_window.show()


def reset_button(app=None, blueprint={}, action=""):
    app_components = app.get_all_components()

    for component_name in blueprint.keys():
        if 'tab_components' in blueprint[component_name]:
            for curr_tab in blueprint[component_name]['tab_components']:
                reset_button(app, curr_tab, action)

        if (component_name in app_components):
            app_components.get(component_name).reset()

            if component_name == 'case ID':
                app.components.get('case ID').set(read_case_id())

    if ("receipt" in action):
        app.components.get('cart').tools.buttons[3].configure(fg_color='white', text_color="white", state='disabled', text="$0.00")
        app.components.get('cart').tools.buttons[4].configure(fg_color='white', text_color="white", state='disabled', text="$0.00")


def test_button(app):

    app.reset_all_components()

    legal_name = names.get_full_name(gender=random.choice(['male', 'female']))
    legal_name_2 = names.get_full_name(gender=random.choice(['male', 'female']))

    app.components['address'].set("Address")
    app.components['card number'].set(f"{str(random.randint(1000000000000000, 9999999999999999))}")
    app.components['card type'].set("Visa")
    app.components['cardholder name'].set(legal_name)
    app.components['add taxes'].set("Yes")
    app.components['expiration'].set(y="2026", m="Dec", d="31")
    app.components['client 1 first name'].set(legal_name.split(" ")[0] + " (TEST)")
    app.components['client 1 last name'].set(legal_name.split(" ")[1] + " (TEST)")
    app.components['client 1 email'].set(f"{legal_name.lower().replace(" ","")}@gmail.com")
    app.components['client 1 phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['email'].set(f"{legal_name.lower().replace(" ","")}@gmail.com")
    app.components['phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['client 2 first name'].set(legal_name_2.split(" ")[0] + " (TEST)")
    app.components['client 2 last name'].set(legal_name_2.split(" ")[1] + " (TEST)")
    app.components['client 2 email'].set(f"{legal_name_2.lower().replace(" ","")}@gmail.com")
    app.components['client 2 phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['security code'].set(f"{str(random.randint(100, 999))}")
    app.components['case ID'].set(read_case_id())
    app.components['client name'].set(f'{app.components['client 1 first name'].get()} {app.components['client 1 last name'].get()}')
    app.components['client 1 date of birth'].set(y=f"199{random.randint(0,9)}", m=random.randint(0,11), d=random.randint(1,28))
    app.components['client 1 UCI'].set("0123456789")
    # app.components['search case ID'].set("202407-001")

    for i in range(1,random.randint(2,3)):
        other_host = "2" if i==1 else "1"
        host_name = legal_name if i == 1 else legal_name_2
        app.components[f"host {i} name"].set(host_name)
        app.components[f"host {i} date of birth"].set(y=f"199{random.randint(0,9)}", m=random.randint(0,11), d=random.randint(1,28))
        app.components[f"host {i} passport no."].set('XXXXXXXXX')
        app.components[f"host {i} address"].set("999 St Mary\'s Rd, Winnipeg, MB R3C 0C4")
        app.components[f"host {i} phone number"].set('999-999-9999')
        app.components[f"host {i} email address"].set('email@domain.com')
        app.components[f"host {i} occupation"].set('occupation')
        app.components[f"host {i} status in Canada"].set('citizen')
        app.components[f'relationship to host {other_host}'].set('spouse')

    for i in range(1,random.randint(2,6)):
        app.components[f"guest {i} name"].set(names.get_full_name(gender=random.choice(['male', 'female'])) + " (TEST)")
        app.components[f"guest {i} date of birth"].set(y=f"{random.randint(1990,2006)}", m=random.randint(0,11), d=random.randint(1,31))
        app.components[f"guest {i} passport no."].set('XXXXXXXXX')
        app.components[f"guest {i} address"].set('3310 Evergreen Lane, Los Angeles, California, USA 90017')
        app.components[f"guest {i} phone number"].set(f'{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}')
        app.components[f"guest {i} email address"].set(f'guest{i}@domain.com')
        app.components[f"guest {i} occupation"].set('occupation')
        app.components[f"guest {i} country of citizenship"].set('USA')
        app.components[f"guest {i} relation to host 1"].set('sibling')

    app.components["arrival date"].set(y=f"2024", m=random.randint(8,9), d=random.randint(1,15))
    app.components["departure date"].set(y=f"2024", m=random.randint(9,11), d=random.randint(1,15))
    app.components["purpose of visit"].set('to visit me, their sibling')
    app.components["country of residence"].set('USA')
    app.components["address in Canada"].set('1325 Markham Rd, Winnipeg, MB, Canada')

    total_amount = 0
    total_months = random.randint(1,12)
    now = dt.now()

    for i in range(total_months):
        total_amount += 100

        dt_object = now + rd.relativedelta(days=i)
        year = (datetime.datetime.strftime(dt_object, "%Y"))
        month = (datetime.datetime.strftime(dt_object, "%b"))
        day = (datetime.datetime.strftime(dt_object, "%d"))

        app.components[f'payment {i+1}'].set("100", year, month, day)

    app.components['application fee'].set(f"${total_amount}", total_months)

    random_row_contents = []
    random_row_infos = []

    for i in range(random.randint(2,6)):
        new_row, new_row_info = generate_row_contents(
            app_components=app.components, 
            override_row_content={
                'service': f'item_{i+1}',
                'quantity': f"{str(random.randint(1, 3))}",
                'rate': str(random.choice([100,200,300,400,500])),
                'tax_rate': 12.0,
                'gst': 7.0,
                'pst': 5.0,
            }
        )

        random_row_contents.append(new_row)
        random_row_infos.append(new_row_info)

    app.components.get('cart').add(
        row_contents=random_row_contents,
        row_info=random_row_infos,
    )

    update_total_row(cart=app.components.get('cart'))


def search_files_button(app):
    search_case_id = app.components['search case ID'].get()
    search_name = app.components['search client name'].get()
    search_category = app.components['search category'].get()
    search_table = app.components['search results']
    search_table.reset()

    row_contents_list = []
    row_info_list = []

    db = Database()
    db.database.row_factory = db.dict_factory

    retrieved_entries = db.database.execute(
        f'''
        SELECT
            *
        FROM
            files
        WHERE
            case_id = '{search_case_id}'
            {f"AND client_name LIKE '%{search_name}%'" if len(search_name) > 0 else ""}
            {f"AND document_type = '{search_category}'" if search_category.lower() != "all" else ""}
        '''
    ).fetchall()

    db.close()

    for entry in retrieved_entries:
        new_row = [entry.get('document_type'), entry.get('client_name'), entry.get('created_date'), entry.get('created_by'), entry.get('remarks')]
        row_contents_list.append(new_row)
        row_info_list.append(entry)

    if len(retrieved_entries) > 0:
        search_table.add(
            row_contents=row_contents_list,
            row_info=row_info_list,
        )


def search_payments_button(app, is_callback=False):
    from GUI import LoadingSplash
    loadingsplash = LoadingSplash(app.root, opacity=1.0)

    search_in_date = app.components['show payments on date'].get()
    payment_status = app.components['payment status'].get()
    payments_table = app.components.get('due payments')
    row_contents_list = []
    row_info_list = []

    def task():
        payments_table.reset()
        payments_table.set_table_title(new_title = f'Showing payments due on {search_in_date}')

        db = Database()
        db.database.row_factory = db.dict_factory

        retrieved_entries = db.database.execute(
            f'''
            SELECT
                *
            FROM
                payments
            WHERE
                payment_date = '{datetime.datetime.strftime(datetime.datetime.strptime(search_in_date, "%b %d, %Y"), "%Y%m%d")}'
                {'' if payment_status.lower() == "all" else ('AND payment_made = 1' if payment_status.lower() == "paid" else 'AND payment_made = 0')}
            '''
        ).fetchall()

        db.close()

        for entry in retrieved_entries:
            new_row = [entry.get('case_id'), entry.get('client_name'), entry.get('contact_info'), entry.get('payment_amount'), 'Yes' if entry.get('payment_made') == 1 else 'No']
            row_contents_list.append(new_row)
            row_info_list.append(entry)

        if len(row_contents_list) > 0:
            payments_table.selected_row = None
            payments_table.selected_row_info = None

            payments_table.add(
                row_contents=row_contents_list,
                row_info=row_info_list,
            )

        loadingsplash.stop()

    loadingsplash.show(task)


def search_attendance(app, override_entries=None, is_callback=False):

    if is_callback:
        if globals.attendance_queried_time is not None:
            timediff = dt.now() - globals.attendance_queried_time
            if timediff.total_seconds() < 30:
                return

    row_contents_list = []
    row_info_list = []
    table = app.components.get('clocked in today')

    from GUI import LoadingSplash
    loadingsplash = LoadingSplash(app.root, opacity=1.0)

    db = Mongo()
    dbname = db.get_database()
    collection_name = dbname["attendance"]

    def task():
        try:
            if override_entries is not None:
                retrieved_entries = override_entries
            else:
                retrieved_entries = collection_name.find().sort({"date":-1, "staff_name": 1})

            for entry in (retrieved_entries):
                new_row = [
                    entry.get('staff_name'), 
                    datetime.datetime.strftime(datetime.datetime.strptime(entry.get('date'), '%Y%m%d'), '%b %d, %Y'), 
                    datetime.datetime.strftime(datetime.datetime.strptime(entry.get('time'), '%H:%M:%S'), '%I:%M %p'),
                    'Clock in' if int(entry.get('type')) == 1 else 'Clock out'
                ]

                row_contents_list.append(new_row)
                row_info_list.append(entry)

            if len(row_contents_list) > 0 or len(override_entries) == 0:
                table.selected_row = None
                table.selected_row_info = None
                table.reset()

                if len(row_contents_list) > 0 and len(row_info_list) > 0:
                    table.add(row_contents=row_contents_list, row_info=row_info_list)

            db.client.close()
            loadingsplash.stop()
            globals.attendance_queried_time = dt.now()

        except Exception as e:
            ErrorPopup(f'Error when searching for attendance\n{e}')

    loadingsplash.show(task)


def switch_payment_status_button(app):
    payments_table = app.components.get('due payments')
    selected_payment_info = payments_table.get_selected_info()

    db = Database()
    db.cursor.execute(
        f'''
        UPDATE payments 
        SET payment_made = {0 if selected_payment_info['payment_made'] == 1 else 1} 
        WHERE filename = '{selected_payment_info['filename']}' and payment_date = '{selected_payment_info['payment_date']}'
        '''
    )
    db.commit()
    db.close()

    search_payments_button(app)


def generate_row_contents(quantity_offset=None, app_components=None, override_row_content={}):
    if app_components is None:
        return (None, None)

    if quantity_offset is None:
        quantity_offset = 0

    if override_row_content:
        service = override_row_content.get("service")
        quantity = float(override_row_content.get("quantity"))
        rate = float(override_row_content.get("rate"))
        tax_rate = float(override_row_content.get("tax_rate"))
        gst = override_row_content.get("gst")
        pst = override_row_content.get("pst")
    else:
        service = app_components.get("service").get()
        quantity = float(app_components.get("quantity").get()) + quantity_offset
        rate = float(app_components.get("rate").get().replace("$",""))
        tax_rate = float(app_components.get("GST percentage").get()) + float(app_components.get("PST percentage").get())
        gst = app_components.get("GST percentage").get()
        pst = app_components.get("PST percentage").get()

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
            'gst': gst,
            'pst': pst,
            'taxes': str(rate * quantity * (tax_rate/100)),
            'price': str(rate * quantity * (1+(tax_rate/100))),
        }
    )


def add_item_button(app):
    app_components = app.get_all_components()
    cart = app_components.get('cart')

    new_row, new_row_info = generate_row_contents(app_components=app_components)

    update_index, existing_item_info = cart.contains(
        row_info=new_row_info, 
        compare_keys = ['service', 'rate', 'gst', 'pst']
    )

    if existing_item_info is not None:
        new_row, new_row_info = generate_row_contents(
            quantity_offset=float(existing_item_info.get('quantity')),
            app_components=app_components,
        )

    cart.add(
        row_info=[new_row_info], 
        row_contents=[new_row],
        row_index=update_index
    )

    update_total_row(cart=cart)


def remove_item_button(app):

    cart = app.components['cart']

    selected_row = cart.get_selected_contents()
    selected_info = cart.get_selected_info()

    if selected_row is None or selected_info is None:
        ErrorPopup(msg="Select table item to perform action.")
        return

    cart.remove()

    update_total_row(cart=cart)


def update_total_row(cart):
    cart_items = cart.get()
    font = ctk.CTkFont(family='Roboto Bold', size=12, weight='bold')
    total_taxes = 0
    total_price = 0
    for item in cart_items:
        total_taxes += float(item['info']['taxes'])
        total_price += float(item['info']['price'])

    cart.tools.buttons[3].configure(fg_color='#325882', text_color="white", text="${:,.2f}".format(total_taxes), font=font, state='normal')
    cart.tools.buttons[4].configure(fg_color='#325882', text_color="white", text="${:,.2f}".format(total_price), font=font, state='normal')


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
            db = Database()
            imported_history = db.cursor.execute(
                '''
                    SELECT 
                        client_1_name, created_by, created_date, application_type, application_fee
                    FROM 
                        agreements
                '''
            ).fetchall()

            print(imported_history)

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

            self.tools_frame_widgets.buttons[0].configure(fg_color="light gray" if "--dark" not in sys.argv else "#444444", state="disabled")

            if len(entries) < 19:
                self.tools_frame_widgets.buttons[1].configure(fg_color="light gray" if "--dark" not in sys.argv else "#444444", state="disabled")

            self.header_frame.grid(row=0, column=1, pady=[5,0])
            self.table_frame.grid(row=1, column=1)
            self.tools_frame.grid(row=2, column=1)

            history_window.body.after(20, lambda: history_window.body.focus())

        # bring the window forward if found
        else:
            history_window.show()


    def history_table(self, parent_frame=None, parent_width=0, entries=[], page_number=0):
        from GUI import RowWidget

        self.table_rows = []

        # pad the list with empty entries if less than 18 rows in order to keep a constant table size on the UI
        current_page_rows = entries[(page_number*18):((page_number+1)*18)]
        for i in range(18 - len(current_page_rows)):
            current_page_rows.append(
                # client_1_name, created_by, created_date, application_type, application_fee,
                ('', '', '', '', '')
            )

        for index, entry in enumerate(current_page_rows):
            self.table_rows.append(
                RowWidget(
                    parent_frame=parent_frame, 
                    parent_width=parent_width, 
                    row_number=index, 
                    mode="table", 
                    row_contents=[
                        f"{entry[0].title().split(";")[0][0:32]}{"..." if len(entry[0].split(";")[0]) > 32 else ""}",
                        entry[1],
                        entry[2],
                        f"{entry[3][0:32]}{"..." if len(entry[3]) > 32 else ""}",
                        f"{"${:,.2f}".format(float(entry[4]))}" if entry[4] != "" else entry[4],
                    ],
                    row_color="#ddd" if index%2==0 else "#eee",
                )
            )


    def history_table_nav(self, app=None, page_number=0, entries=[]):

        if (page_number == 0):
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


class ReceiptFinder():

    # display the popup which allows users to search for existing documents
    def __init__(self, app):

        receipt_finder = app.get_window("receipt finder")

        if (receipt_finder is None or not receipt_finder.winfo_exists()): 
            receipt_finder = ctk.CTkToplevel()

            w = 300
            h = 230
            x = (app.get_size('w')/2) - (w/2)
            y = (app.get_size('h')/2) - (w/2)
            f = ctk.CTkFont(family='Roboto Bold', size=12, weight='bold')

            ctk.CTkFrame(receipt_finder, corner_radius=2, border_width=1, width=260, height=70, fg_color='white').place(x=20, y=140)

            ctk.CTkLabel(receipt_finder, text="Document ID", bg_color='#E5E5E5', font=f).place(x=20, y=5)
            self.doc_id_search = ctk.CTkEntry(receipt_finder, width=260, border_width=1, corner_radius=2, placeholder_text="leading zeros are optional")
            self.doc_id_search.place(x=20, y=30)

            ctk.CTkLabel(receipt_finder, text="Client Name", bg_color='#E5E5E5', font=f).place(x=20, y=65)
            self.client_name_search = ctk.CTkEntry(receipt_finder, width=260, border_width=1, corner_radius=2, placeholder_text="full or partial name")
            self.client_name_search.place(x=20, y=90)

            ctk.CTkLabel(receipt_finder, text="Documents to open", bg_color='#E5E5E5', font=f).place(x=40, y=145)
            self.qty_of_docs_to_open = ctk.CTkLabel(receipt_finder, width=28, height=28, corner_radius=2, text="05", fg_color='#DDDDDD', font=f)
            self.qty_of_docs_to_open.place(x=80, y=170)

            self.minus_button = ctk.CTkButton(receipt_finder, text="-", border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:self.change_doc_count(-1), height=28, width=30)
            self.minus_button.place(x=40, y=170)

            self.plus_button = ctk.CTkButton(receipt_finder, text="+", border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:self.change_doc_count(+1), height=28, width=30)
            self.plus_button.place(x=120, y=170)

            ctk.CTkButton(receipt_finder, text='open', border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:self.open_doc_by_filter(), width=72, height=42).place(x=188, y=156)

            ## render the popup
            receipt_finder.geometry('%dx%d+%d+%d' % (w, h, x, y))
            receipt_finder.resizable(False, False)
            receipt_finder.configure(fg_color='white')

            receipt_finder.title("Receipts Finder")
            receipt_finder.after(202, lambda: receipt_finder.focus())

        else:
            receipt_finder.focus()


    # open documents
    def open_doc_by_filter(self):

        file_found = False
        doc_id = self.doc_id_search.get()
        client_name = self.client_name_search.get()

        if (len(doc_id) == 0 and len(client_name) == 0):
            ErrorPopup('Nothing entered into search fields')
            return False

        search_filters = []

        try:
            # remove surrounding whitespace, and ensure it is 10-digits long
            doc_id = "{:010}".format(int((self.doc_id_search.get()).strip()))
            search_filters.append(doc_id)
        except:
            print("doc_id not entered")

        try:
            # remove surrounding whitespace, convert to lowercase, replace spaces with underscores 
            client_name = (self.client_name_search.get()).strip().lower().replace(" ", "_")
            search_filters.append(client_name)
        except:
            print("client_name not entered")

        # try to find all matches and open them
        try:
            open_counter = 0
            open_limit = int(self.qty_of_docs_to_open.cget('text'))
            for f in sorted(glob(f"{os.getcwd()}\\output\\receipts\\*.docx"), key=os.path.getmtime, reverse=True):
                if all(keyword in f.lower() for keyword in search_filters):
                    os.startfile(f)
                    open_counter += 1
                    file_found = True

                if (open_counter == open_limit):
                    return True

        except Exception as e:
            print(e)

        # no match was found so display a popup message
        if not file_found:
            ErrorPopup('No match found')


    # change the number of documents to be opened
    def change_doc_count(self, amount):
        new_qty = int(self.qty_of_docs_to_open.cget('text')) + amount

        if (new_qty <= 1):
            new_qty = 1
            self.minus_button.configure(state='disabled', fg_color='#EEEEEE')
        elif new_qty >= 10:
            new_qty = 10
            self.plus_button.configure(state='disabled', fg_color='#EEEEEE')
        else:
            self.minus_button.configure(state='normal', fg_color="#23265e")
            self.plus_button.configure(state='normal', fg_color="#23265e")

        new_qty = "{:02}".format(new_qty)

        self.qty_of_docs_to_open.configure(text=new_qty)


def find_file(app):
        search_table = app.components['search results']
        filename = (search_table.get_selected_info().get('filename', None))
        document_type = (search_table.get_selected_info().get('document_type', None))

        if filename is None or document_type is None:
            ErrorPopup(msg="Select table item to perform action.")
            return (None, None)

        folder_paths = {
            'Payment Receipt': (f'{os.getcwd()}\\output\\receipts\\'),
            'Use of Representative': (f'{os.getcwd()}\\output\\imm5476\\'),
            'Code of Conduct': (f'{os.getcwd()}\\output\\agreements\\'),
            'Retainer Agreement': (f'{os.getcwd()}\\output\\agreements\\'),
            'Payment Authorization': (f'{os.getcwd()}\\output\\agreements\\'),
        }

        return (
            f'{folder_paths.get(document_type)}\\{filename}.docx'.replace('\\\\', '\\'),
            f'{filename}.docx'
        )


def handle_action(app=None, action="", blueprint={}):
    if ("reset" in action):
            PromptPopup(msg="Are you sure you want to reset all fields?", func=lambda: reset_button(app, blueprint, action))

    elif (action == "payments"):
            try:
                doc = Document(resource_path("assets\\templates\\payments.docx"))
                write_payment_auth(doc, app.get_all_components())
            except Exception as e:
                ErrorPopup(msg=f'Exception while writing payment authorization:\n\n{str(e)}')

    elif (action == "retainer"):
        try:
            doc = Document(resource_path("assets\\templates\\retainer.docx"))
            response = write_retainer(doc, app.get_all_components())

            date_now = datetime.datetime.now()
            date_today = f"{date_now.strftime('%b')} {int(date_now.strftime('%d'))}, {date_now.strftime('%Y')}"
            date_of_first_payment = app.components.get('payment 1').get('date')

            if response == True and date_today == date_of_first_payment:
                PromptPopup("The first payment is to be made today. Create receipt?", func=lambda: app.components['Receipts'].lift_app(app.subapp_components['Receipts']))
                app.focus()
        except Exception as e:
            ErrorPopup(msg=f'Exception while writing retainer:\n\n{str(e)}')

    elif (action == "conduct"):
        try:
            doc = Document(resource_path("assets\\templates\\conduct.docx"))
            write_conduct(doc, app.get_all_components())
        except Exception as e:
            ErrorPopup(msg=f'Exception while writing code of conduct:\n\n{str(e)}')

    elif (action == "create receipt"):
        try:
            doc = Document(resource_path("assets\\templates\\receipt.docx"))
            write_receipt(doc, app.get_all_components())
        except Exception as e:
            ErrorPopup(msg=f'Exception while writing receipt:\n\n{str(e)}')

    elif (action == "create letter"):

        if len(app.components['conclusion content'].get().strip()) == 0:
            if PromptPopup("No conclusion was written. Create letter without one?", func=lambda: None).get() is False:
                return

        elif app.components['conclusion content'].get().strip() == 'loading...':
            InfoPopup('Conclusion content is still loading. Please wait.')
            return

        try:
            doc = Document(resource_path("assets\\templates\\invitation_1.docx"))
            write_invitation(doc, app.get_all_components())
        except Exception as e:
            ErrorPopup(msg=f'Exception while writing invitation:\n\n{str(e)}')

    elif (action == "generate case ID"):
        app.components.get('case ID').set(read_case_id())

    elif (action == "retainer history"):
        HistoryViewer(app)

    elif (action == "find receipt"):
        ReceiptFinder(app)

    elif (action == "test"):
        test_button(app)

    elif (action == "decrypt"):
        decrypt_button(app)

    elif (action == "add item"):
        add_item_button(app)

    elif (action == "remove item"):
        remove_item_button(app)

    elif (action == "search files"):
        search_files_button(app)

    elif (action == "search payments"):
        search_payments_button(app)

    elif (action == "switch payment status"):
        switch_payment_status_button(app)

    elif (action == "adjust time"):
        adjust_time_button(app)

    elif (action == "open selected"):
        searched_filepath, searched_filename = find_file(app=app)

        try:
            os.startfile(searched_filepath)
        except Exception as e:
            print(e)
            ErrorPopup(msg=f"Could not open {searched_filename}")

    elif ("output" in action):
        try:
            os.startfile(f'{os.getcwd()}\\output\\{action.split(' ')[0]}\\')
        except Exception as e:
            ErrorPopup(msg=f'Output folder not found')

    elif (action == 'representative'):
        try:
            doc = Document(resource_path("assets\\templates\\imm5476.docx"))
            write_imm5476(doc, app.get_all_components())
        except Exception as e:
            ErrorPopup(msg=f'Exception while writing receipt:\n\n{str(e)}')

    elif (action == "cancel selected"):
        searched_filepath, searched_filename = find_file(app=app)

        confirmation = PromptPopup(msg=f'Would you like to cancel {searched_filename}', func=lambda:None).get()

        if confirmation:
            try:
                os.remove(searched_filepath)
                successfully_removed = remove_from_database(searched_filename)
                if not successfully_removed:
                    ErrorPopup(msg=f'Could not remove {searched_filename}.')
                else:
                    search_files_button(app)
            except Exception as e:
                ErrorPopup(msg=f'Exception while attempting to remove {searched_filename}: {e}')

    else:
        InfoPopup(msg='This feature is still under construction.')