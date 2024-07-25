import customtkinter as ctk
import os
import names
import random
import math
from glob import glob
from icecream import ic
from Popups import ErrorPopup
from dotenv import load_dotenv
from writer import obscure, unobscure
from reader import read_file_as_list, read_case_id


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
                ErrorPopup(msg=f'Wrong password')

    # bring the window forward if found
    else:
        decryptor_window.show()


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
    app.components['client 1 first name'].set(legal_name.split(" ")[0] + " (test)")
    app.components['client 1 last name'].set(legal_name.split(" ")[1] + " (test)")
    app.components['client 1 email'].set(f"{legal_name.lower().replace(" ","")}@gmail.com")
    app.components['client 1 phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['email'].set(f"{legal_name.lower().replace(" ","")}@gmail.com")
    app.components['phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['client 2 first name'].set(legal_name_2.split(" ")[0] + " (test)")
    app.components['client 2 last name'].set(legal_name_2.split(" ")[1] + " (test)")
    app.components['client 2 email'].set(f"{legal_name_2.lower().replace(" ","")}@gmail.com")
    app.components['client 2 phone'].set(f"+1 {random.choice(["(431)", "(204)"])} {str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}")
    app.components['security code'].set(f"{str(random.randint(100, 999))}")
    app.components['case ID'].set(read_case_id())
    app.components['client name'].set(f'{app.components['client 1 first name'].get()} {app.components['client 1 last name'].get()}')
    app.components['client 1 date of birth'].set(y="2000", m="Jan", d="01")
    app.components['client 1 UCI'].set("0123456789")
    app.components['search case ID'].set("202407-001")

    app.components["guest 1 full name"].set(names.get_full_name(gender=random.choice(['male', 'female'])))
    app.components["guest 1 date of birth"].set(y="2000", m="Jan", d="01")
    app.components["guest 1 passport no."].set('XXXXXXXXX')
    app.components["guest 1 address"].set('Hypothetical Address, City, Province, Country, ABC ABC')
    app.components["guest 1 phone number"].set('999-999-9999')
    app.components["guest 1 email address"].set('email@domain.com')
    app.components["guest 1 occupation"].set('occupation')
    app.components["guest 1 country of citizenship"].set('Mars')
    app.components["guest 1 relation to host 1"].set('sibling')
    app.components["purpose of visit"].set('to visit me, their sibling')
    app.components["country of residence"].set('UK')
    app.components["address in Canada"].set('1325 Markhan Rd, Winnipeg, MB, Canada')

    total_amount = 0
    total_months = random.randint(1,12)
    for i in range(total_months):
        total_amount += 100
        app.components[f'payment {i+1}'].set("100", "2024", "Jul", 22+i)

    app.components['application fee'].set(f"${total_amount}", total_months)

    random_row_contents = []
    random_row_infos = []

    for i in range(random.randint(1,3)):
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
    app_components = app.get_all_components()
    cart = app_components.get('cart')

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
            imported_history = read_file_as_list()

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
                if all(keyword in f for keyword in search_filters):
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

