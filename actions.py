import globals
import datetime
import customtkinter as ctk
import os
import names
import random
import threading
from datetime import datetime as dt
from Database import Database
from Popups import ErrorPopup, InfoPopup, PromptPopup
from dotenv import load_dotenv
from writer import obscure, write_invitation
from reader import import_function, query_attendance
from docx import Document
from Path import resource_path
from files_helper import retrieve_files




def _reset_button(app=None, blueprint={}, action=""):
    app_components = app.get_all_components()

    for component_name in blueprint.keys():
        if 'tab_components' in blueprint[component_name]:
            for curr_tab in blueprint[component_name]['tab_components']:
                _reset_button(app, curr_tab, action)

        if (component_name in app_components):
            app_components.get(component_name).reset()


def _test_button(app):
    app.reset_all_components()

    legal_name = names.get_full_name(gender=random.choice(['male', 'female']))
    legal_name_2 = names.get_full_name(gender=random.choice(['male', 'female']))

    if globals.current_lifted_subapp == ("Invitation Letter"):
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

    elif globals.current_lifted_subapp == ("Info and Forms"):
        app.components['Principal applicant name'].set("TEST1")
        app.components['Principal applicant application'].set("PR")

        test_applications = ["Sponsorship", "Study Permit", "Work Permit", "Express Entry Profile", "MPNP"]
        for i in range(1,6):
            app.components[f'Dependent {i} name'].set(f"TEST{i}")
            app.components[f'Dependent {i} application'].set(test_applications[i-1])


def _adjust_time_button(app):
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

        frame = ctk.CTkFrame(master=adjust_time_window.body, fg_color='#ffffff' if not globals.set_dark_theme else '#444444')
        frame.place(x=20, y=20)

        RowBreak(frame, heading="details of adjusted clock in/out", top_offset=0)
        staffpicker = ComboBox(frame, label_text="staff name", top_offset=1, options=sorted(globals.staff_names))
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


def _adjust_sources_button(app):
    from GUI import WindowView, RowBreak, Entry, ComboBox

    db = Database()
    collection_name = db.get_database()["links"]

    if globals.links_dict is None or len(globals.links_dict) == 0:
        entries = collection_name.find()

        for row in entries:
            url = row['url']
            globals.links_dict[row['form']] = (url + "&download=1") if not url.endswith("&download=1") else url

    links = globals.links_dict

    # retrieve object from app.components
    adjust_sources_window = app.get_window("adjust sources")

    # check whether the object contains a window
    if (adjust_sources_window is not None) and (not adjust_sources_window.body.winfo_exists()):
        adjust_sources_window = None

    # create a new object if None was found
    if adjust_sources_window is None:
        adjust_sources_window = WindowView(app=app, window_name="Adjusted file sources", width=500, height=300)
        app.add_window("adjust sources", adjust_sources_window)

        frame = ctk.CTkFrame(master=adjust_sources_window.body, fg_color='#ffffff' if not globals.set_dark_theme else '#444444')
        frame.place(x=20, y=20)

        RowBreak(frame, heading="select which form needs to be adjusted", top_offset=0)
        formpicker = ComboBox(frame, label_text="form", top_offset=1, options=sorted(links.keys()))
        new_link = Entry(frame, label_text="new link", top_offset=4)
        adminpass = Entry(frame, label_text="admin password", top_offset=8, is_password=True)

        ctk.CTkButton(frame, text="SAVE", border_width=0, corner_radius=2, fg_color="#23265e", command=lambda:run_decryptor("/assets/functions/clock_in.py"), width=180, height=36).grid(row=9, column=0, columnspan=5, pady=10)

        def run_decryptor(functionpath) -> str:
            input_password = adminpass.get()

            if os.getenv('FILES_PW') == obscure(input_password):
                form_name = formpicker.get()
                updated_link = new_link.get()
                collection_name.update_one({"form": form_name}, {"$set": {"url": updated_link}})
                InfoPopup(msg=f'Link for {form_name} updated successfully')
            else:
                ErrorPopup(msg='Incorrect password')

    # bring the window forward if found
    else:
        adjust_sources_window.show()


def _edit_attendance_button(app, row_to_edit=None):
    table = app.components.get('clocked in today')
    selected_info = table.get_selected_info()

    if table.get_selected_info() is None:
        ErrorPopup(msg="Select table item to perform action.")
        return

    # create a dt object with the date and time in the selected row
    dt_obj = dt.strptime(selected_info["date"] + selected_info["time"], "%Y%m%d%H:%M:%S")

    from GUI import WindowView, DatePicker, TimePicker, RowBreak, Entry, ComboBox
    load_dotenv()

    # retrieve object from app.components
    adjust_time_window = app.get_window("edit attendance")

    # check whether the object contains a window
    if (adjust_time_window is not None) and (not adjust_time_window.body.winfo_exists()):
        adjust_time_window = None

    # create a new object if None was found
    if adjust_time_window is None:
        adjust_time_window = WindowView(app=app, window_name="Edit attendance", width=500, height=400)
        app.add_window("edit attendance", adjust_time_window)

        frame = ctk.CTkFrame(master=adjust_time_window.body, fg_color='#ffffff' if not globals.set_dark_theme else '#444444')
        frame.place(x=20, y=20)

        RowBreak(frame, heading="details of clock entry to modify", top_offset=0)
        staffpicker = ComboBox(frame, label_text="staff name", top_offset=1, options=sorted(globals.staff_names), default_option=selected_info['staff_name'])
        clockpicker = ComboBox(frame, label_text="clock type", top_offset=2, options=["in", "out"], default_option="in" if selected_info['type'] == 1 else "out")
        timepicker = TimePicker(frame, label_text="time (24-hour format)", top_offset=3)
        datepicker = DatePicker(frame, label_text="date", top_offset=4)
        adminpass = Entry(frame, label_text="admin password", top_offset=5, is_password=True)

        timepicker.set(hr=dt_obj.strftime("%H"), min=dt_obj.strftime("%M"))
        datepicker.set(m=int(dt_obj.strftime("%m"))-1, d=int(dt_obj.strftime("%d")), y=int(dt_obj.strftime("%Y")))

        ctk.CTkButton(frame, text="SAVE", border_width=0, corner_radius=2, fg_color="#235e27", command=lambda:run_decryptor("/assets/functions/edit_attendance.py"), width=180, height=36).grid(row=6, column=0, columnspan=2, pady=10)
        ctk.CTkButton(frame, text="DELETE", border_width=0, corner_radius=2, fg_color="#a11111", command=lambda:run_decryptor("/assets/functions/delete_attendance.py"), width=180, height=36).grid(row=6, column=1, columnspan=3, pady=10)

        def run_decryptor(functionpath) -> str:
            input_password = adminpass.get()

            if os.getenv('PW') == obscure(input_password):
                import_function(functionpath, "callback")(
                    app, 
                    staffpicker.get(), 
                    dt_obj, 
                    1 if clockpicker.get() == "in" else 0,
                    selected_info['_id']
                )
            else:
                ErrorPopup(msg='Incorrect password')

    # bring the window forward if found
    else:
        adjust_time_window.show()


def _edit_staff_button(app, row_to_edit=None):
    if len(globals.staff_names) == 0:
        ErrorPopup(msg="No staff names found in database.")
        return

    from GUI import WindowView, RowBreak, Entry, ComboBox
    load_dotenv()

    # retrieve object from app.components
    adjust_time_window = app.get_window("edit staff")

    # check whether the object contains a window
    if (adjust_time_window is not None) and (not adjust_time_window.body.winfo_exists()):
        adjust_time_window = None

    # create a new object if None was found
    if adjust_time_window is None:
        adjust_time_window = WindowView(app=app, window_name="Edit staff", width=500, height=300)
        app.add_window("edit staff", adjust_time_window)

        frame = ctk.CTkFrame(master=adjust_time_window.body, fg_color='#ffffff' if not globals.set_dark_theme else '#444444')
        frame.place(x=20, y=20)

        RowBreak(frame, heading="edit or delete staff members", top_offset=0)
        staffpicker = ComboBox(frame, label_text="staff name", top_offset=1, options=sorted(globals.staff_names))
        new_name = Entry(frame, label_text="rename staff to", top_offset=2, is_password=False)
        adminpass = Entry(frame, label_text="admin password", top_offset=3, is_password=True)

        ctk.CTkButton(frame, text="SAVE", border_width=0, corner_radius=2, fg_color="#235e27", command=lambda:run_decryptor("/assets/functions/edit_staff.py"), width=180, height=36).grid(row=4, column=0, columnspan=2, pady=10)
        ctk.CTkButton(frame, text="DELETE", border_width=0, corner_radius=2, fg_color="#a11111", command=lambda:run_decryptor("/assets/functions/delete_staff.py"), width=180, height=36).grid(row=4, column=1, columnspan=3, pady=10)

        def run_decryptor(functionpath) -> str:
            input_password = adminpass.get()

            if os.getenv('PW') == obscure(input_password):
                import_function(functionpath, "callback")(app, staffpicker.get(), new_name.get(), staffpicker)
            else:
                ErrorPopup(msg='Incorrect password')

    # bring the window forward if found
    else:
        adjust_time_window.show()


def _add_staff_button(app, row_to_edit=None):
    if len(globals.staff_names) == 0:
        ErrorPopup(msg="No staff names found in database.")
        return

    from GUI import WindowView, RowBreak, Entry, ComboBox
    load_dotenv()

    # retrieve object from app.components
    adjust_time_window = app.get_window("add staff")

    # check whether the object contains a window
    if (adjust_time_window is not None) and (not adjust_time_window.body.winfo_exists()):
        adjust_time_window = None

    # create a new object if None was found
    if adjust_time_window is None:
        adjust_time_window = WindowView(app=app, window_name="Add staff", width=500, height=240)
        app.add_window("add staff", adjust_time_window)

        frame = ctk.CTkFrame(master=adjust_time_window.body, fg_color='#ffffff' if not globals.set_dark_theme else '#444444')
        frame.place(x=20, y=20)

        RowBreak(frame, heading="add staff members", top_offset=0)
        new_name = Entry(frame, label_text="name of new staff", top_offset=1, is_password=False)
        adminpass = Entry(frame, label_text="admin password", top_offset=2, is_password=True)

        ctk.CTkButton(frame, text="ADD", border_width=0, corner_radius=2, fg_color="#2711a1", command=lambda:run_decryptor("/assets/functions/add_staff.py"), width=180, height=36).grid(row=4, column=0, columnspan=5, pady=10)

        def run_decryptor(functionpath) -> str:
            input_password = adminpass.get()

            if os.getenv('PW') == obscure(input_password):
                import_function(functionpath, "callback")(app, new_name.get())
            else:
                ErrorPopup(msg='Incorrect password')

    # bring the window forward if found
    else:
        adjust_time_window.show()


def _format_attendance_entries(retrieved_entries):
    
    if retrieved_entries is None or len(retrieved_entries) == 0:
        return [], []

    row_contents_list = []
    row_info_list = []

    for entry in retrieved_entries:
        new_row = [
            entry.get('staff_name'),
            datetime.datetime.strftime(
                datetime.datetime.strptime(entry.get('date'), '%Y%m%d'),
                '%b %d, %Y'
            ),
            datetime.datetime.strftime(
                datetime.datetime.strptime(entry.get('time'), '%H:%M:%S'),
                '%I:%M %p'
            ),
            'Clock in' if int(entry.get('type')) == 1 else 'Clock out'
        ]
        row_contents_list.append(new_row)
        row_info_list.append(entry)

    return row_contents_list, row_info_list


def set_attendance(app, override_entries=None, is_callback=False, is_first_tab=False):

    if is_callback:
        if globals.attendance_queried_time is not None:
            timediff = dt.now() - globals.attendance_queried_time
            if timediff.total_seconds() < 30:
                return

    from GUI import LoadingSplash

    table = app.components.get('clocked in today')
    loadingsplash = LoadingSplash(app.root, opacity=1.0)

    # --- worker thread: DB + processing ONLY (no Tk calls here)
    def worker(override_entries):
        row_contents_list, row_info_list = [], []

        try:
            if override_entries is None:
                row_contents_list, row_info_list = _format_attendance_entries(query_attendance())
            else:
                row_contents_list, row_info_list = _format_attendance_entries(override_entries)

            # --- UI thread update
            def finish_ui():
                try:
                    if len(row_contents_list) > 0 or (override_entries is not None and len(override_entries) == 0):
                        table.selected_row = None
                        table.selected_row_info = None
                        table.reset()

                        if row_contents_list and row_info_list:
                            table.add(row_contents=row_contents_list, row_info=row_info_list)

                    globals.attendance_queried_time = dt.now()
                finally:
                    loadingsplash.stop()

            app.root.after(0, finish_ui)

        except Exception as e:
            def show_error(e):
                loadingsplash.stop()
                ErrorPopup(f'Error when searching for attendance\n{e}')
            app.root.after(0, show_error(e))

    # --- show splash first, then start thread
    def start_thread():
        threading.Thread(target=worker, args=(override_entries,), daemon=True).start()

    # Always show splash before starting the work
    loadingsplash.show(lambda: start_thread())


def handle_action(app=None, action="", blueprint={}):

    # the invitation letter needs special handling as the conclusion is optional, and I need to ask the user if they're sure
    if (action == "create letter"):
        if len(app.components['conclusion content'].get().strip()) == 0:
            if PromptPopup("No conclusion was written. Create letter without one?", func=lambda: None).get() is False:
                return
        elif app.components['conclusion content'].get().strip() == 'loading...':
            return

        try:
            doc = Document(resource_path("assets\\templates\\invitation_1.docx"))
            write_invitation(doc, app.get_all_components())
        except Exception as e:
            ErrorPopup(msg=f'Exception while creating invitation:\n\n{str(e)}')

    # everything else should be handled through lambdas in the `actions` dict
    else:
        actions = {
            "test": lambda: _test_button(app),
            "adjust time": lambda: _adjust_time_button(app),
            "adjust file sources": lambda: _adjust_sources_button(app),
            "edit attendance": lambda: _edit_attendance_button(app),
            "edit staff": lambda: _edit_staff_button(app),
            "add staff": lambda: _add_staff_button(app),
            "create application": lambda: retrieve_files(app.components, app.root),
            "reset fields": lambda: _reset_button(app, blueprint, action),
        }

        try:
            actions.get(action, lambda: InfoPopup(msg="This feature is still under construction."))()
        except Exception as e:
            ErrorPopup(msg=f"Exception while handling '{action}':\n\n{str(e)}")

