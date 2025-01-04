# import shutil
# import glob
# import json
# from RenderFont import RenderFont
# from docx import Document
import math
import re
import time
import customtkinter as ctk
import datetime
import os
import pywinstyles
import globals

from dotenv import load_dotenv
from Popups import ErrorPopup, InfoPopup, PromptPopup
from Path import *
from tkinter import StringVar
from icecream import ic
from subprocess import DEVNULL, STDOUT, check_call
from dateutil import relativedelta as rd
from typing import Literal
from actions import handle_action
from reader import import_function

family_medium="Roboto Bold"
family_bold="Roboto Bold"


class GUI:
    def __init__(self, master=None, label_text="", left_offset=0, top_offset=0) -> None:
        # no label text was passed
        if label_text == "":
            label_text = f"Component_{datetime.datetime.now().timestamp()}"

        self.stringvar = StringVar(value="")
        self.component = None

        self.label = ctk.CTkLabel(master, width=190, text=label_text, anchor="w", font=ctk.CTkFont(family=family_bold), text_color="white" if globals.set_dark_theme else "black")
        self.label.grid(row=top_offset, column=0, pady=10, padx=5, columnspan=1)

    def get(self) -> str:
        field = self.component
        return field.get().strip()

    def set(self, new_text: str = "") -> None:
        self.stringvar.set(new_text)

    def reset(self) -> None:
        self.stringvar.set("")


class RowBreak():
    def __init__(self, master=None, left_offset=0, top_offset=0, heading="", height=32, width=450, fg_color="#808080", text_color="#ffffff") -> None:
        self.breakline = ctk.CTkLabel(
            master, 
            text=heading.upper(), 
            height=height, 
            width=width, 
            fg_color=fg_color, 
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444", 
            text_color=text_color, 
            corner_radius=3, 
            font=ctk.CTkFont(family=family_bold, weight='bold'),
        )

        self.breakline.grid(row=top_offset, column=0, pady=10, padx=5, columnspan=5)

    def reset(self) -> None:
        return


class RowButton(GUI):
    def __init__(self, master=None, app=None, left_offset=0, top_offset=0, label="", method=None) -> None:

        if type(label) != list:
            label = [label]

        if type(method) != list:
            method = [method]

        if len([label]) > 2:
            print("button count can only be 1, 2, or 3")

        btn_count = len(label)
        self.component = []
        column_offset = 1 if (btn_count % 2 == 0) else 0 # offset needs to be 1 if len(column) is even for the math to work
        column_span = (btn_count*btn_count) - (6*btn_count) + 10
        self.button_frame = ctk.CTkFrame(master=master, fg_color="white" if not globals.set_dark_theme else "#444444", border_width=0, height=32)

        for curr_label in label:
            current_component = ctk.CTkButton(
                self.button_frame, 
                text=curr_label.upper(), 
                height=30, 
                width=(450/btn_count)-5, 
                fg_color="#33008B", 
                text_color="#ffffff", 
                corner_radius=3, 
                font=ctk.CTkFont(family=family_bold, weight='bold'), 
                bg_color="white" if not globals.set_dark_theme else "#444444"
            )

            self.component.append(current_component)

        for i in range(btn_count):
            self.component[i].grid(row=top_offset, column=(btn_count * i) + column_offset, pady=0, padx=2, columnspan=column_span)

        self.assign_command(app, method, 0)

        self.button_frame.grid(row=top_offset, column=0, pady=10, padx=5, columnspan=5)

    def assign_command(self, app, all_commands, curr_command_index):
        if curr_command_index == len(all_commands):
            return

        else:
            self.component[curr_command_index].configure(command=lambda: import_function(all_commands[curr_command_index], "callback")(app))
            self.assign_command(app, all_commands, curr_command_index + 1)
            return

    def reset(self) -> None:
        return


class ComboBox(GUI):
    def __init__(self, master=None, app=None, label_text="", options=None, left_offset=0, top_offset=0, default_string='click to select', default_option=None) -> None:
        """create a new GUI ComboBox object"""

        super().__init__(master, label_text, left_offset, top_offset)

        if type(options) != list:
            if type(options) == str and 'env.' in options:
                load_dotenv()
                options = sorted(os.getenv(options.replace('env.','')).split(','))
            else:
                options=[]

        self.options = options
        self.default_string = default_string
        self.stringvar = StringVar(value="no options added" if options is None else self.default_string)
        self.default_option = None

        self.component = ctk.CTkComboBox(
            master,
            width=250,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            values=options,
            variable=self.stringvar,
            font=ctk.CTkFont(family=family_medium),
            dropdown_font=ctk.CTkFont(family=family_medium),
        )

        if default_option is not None:
            self.default_option = default_option
            self.set(default_option)

        # self.component.place(x=left_offset + 210, y=top_offset + 8)
        self.component.grid(row=top_offset, column=1, pady=10, padx=5, columnspan=3)

    def dropdown_callback(self, choice):
        self.callback(self.app_components)

    def get(self) -> str:
        """returns the first option if nothing was selected"""
        if self.component.get() == self.default_string:
            return self.options[0]
        else:
            return self.component.get().strip()

    def set(self, opt) -> None:
        self.stringvar.set(opt)

    def reset(self) -> None:
        if self.default_option is None:
            self.component.set(self.default_string)
        else:
            self.component.set(self.default_option)

    def add_callback(self, component_name="", app=None, callback=None):
        if callback is None or app is None:
            return

        self.app_components = app.get_all_components()
        self.callback = callback
        self.component.configure(command=self.dropdown_callback)


class Entry(GUI):
    def __init__(self, master=None, app=None, width=250, label_text="", left_offset=0, top_offset=0, placeholder="", default_text=None, is_password=False) -> None:
        """create a new GUI Entry object"""

        super().__init__(master, label_text, left_offset, top_offset)

        self.stringvar = StringVar(value="")
        self.default_text=default_text

        self.component = ctk.CTkEntry(
            master,
            width=width,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            textvariable=self.stringvar,
            font=ctk.CTkFont(family=family_medium),
        )

        if is_password:
            self.component.configure(show="*")

        self.reset()
        self.component.grid(row=top_offset, column=1, pady=10, padx=5, columnspan=3)

    def reset(self) -> None:
        self.stringvar.set(self.default_text if self.default_text is not None else '')

    def stringvar_callback(self, *args):
        self.callback(self.app_components)

    def add_callback(self, component_name="", app=None, callback=None):
        if callback is None or app is None:
            return

        self.app_components = app.get_all_components()
        self.callback = callback
        self.stringvar.trace_add('write', self.stringvar_callback)


class Switch(GUI):
    def __init__(self, master=None, app=None, width=250, label_text="", left_offset=0, top_offset=0, starting_state="on", method=None) -> None:
        super().__init__(master, label_text, left_offset, top_offset)

        self.switchvar = StringVar(value=starting_state)

        self.component = ctk.CTkSwitch(
            master,
            text="",
            switch_width=50,
            switch_height=16,
            border_width=0,
            corner_radius=50,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            variable=self.switchvar,
            font=ctk.CTkFont(family=family_medium),
            onvalue="on", 
            offvalue="off",
            command=lambda: import_function(method, "callback")(app.components),
        )

        self.reset()
        ctk.CTkLabel(master, height=32, width=70, text="").grid(row=top_offset, column=1, pady=10, padx=5)
        ctk.CTkLabel(master, height=32, width=70, text="").grid(row=top_offset, column=2, pady=10, padx=5)
        self.component.grid(row=top_offset, column=3, pady=10, padx=[40,0], columnspan=3)

    def reset(self) -> None:
        return

    def get(self) -> bool:
        return self.component.get()


class TextBox(GUI):
    def __init__(self, master=None, app=None, lines=1, height=200, parent_width=0, label_text="", instructions_text="", left_offset=0, top_offset=0) -> None:
        # super().__init__(master, '', left_offset, top_offset)

        width = parent_width*0.98

        self.instructions = ctk.CTkTextbox(
            master=master,
            width=width,
            height=lines*20,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#444444",
            text_color='#444444' if not globals.set_dark_theme else "#666666", 
            wrap='word', 
            font=ctk.CTkFont(family=family_medium), 
        )

        self.instructions.insert('0.0', instructions_text)
        self.instructions.grid(row=top_offset, column=0, pady=10, padx=5, columnspan=5)
        self.instructions.configure(state='disabled')


        self.component = ctk.CTkTextbox(
            master=master, 
            width=width, 
            height=height, 
            border_width=0, 
            corner_radius=4, 
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            wrap='word', 
            font=ctk.CTkFont(family=family_medium), 
        )

        self.reset()
        self.component.grid(row=top_offset+1, column=0, pady=10, padx=5, columnspan=5)

    def reset(self):
        self.component.delete('0.0', 'end')

    def get(self):
        return (self.component.get('0.0', 'end')).strip()

    def set(self, text):
        self.reset()
        self.component.insert('0.0', text)


class DatePicker(GUI):
    def __init__(self, master=None, label_text="", left_offset=0, top_offset=0, show_day=True, populate_years_with=[]) -> None:
        """create a new GUI DatePicker object"""

        super().__init__(master, label_text, left_offset, top_offset)

        self.today = datetime.datetime.now()
        self.show_day = show_day

        self.stringvar_month = StringVar(value=self.today.strftime("%b"))
        self.stringvar_day = StringVar(value=self.today.strftime("%d"))
        self.stringvar_year = StringVar(value=self.today.strftime("%Y"))

        self.component_day = ctk.CTkComboBox(
            master,
            width=70,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            values=self.populate_days(),
            variable=self.stringvar_day,
            font=ctk.CTkFont(family=family_medium)
        )

        # in some cases, like credit card expirations, the day is not needed
        if show_day is True:
            self.component_day.grid(row=top_offset, column=1, pady=10, padx=5)
        else:
            ctk.CTkLabel(master, height=32, width=70, text="").grid(row=top_offset, column=1, pady=10, padx=5)

        self.component_month = ctk.CTkComboBox(
            master,
            width=80,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            values=self.populate_months(),
            variable=self.stringvar_month,
            command=self.repopulate_days,
            font=ctk.CTkFont(family=family_medium),
        )

        self.component_month.grid(row=top_offset, column=2, pady=10, padx=5)

        self.component_year = ctk.CTkComboBox(
            master,
            width=80,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            values=self.populate_years(populate_years_with),
            variable=self.stringvar_year,
            command=self.repopulate_days,
            font=ctk.CTkFont(family=family_medium),
        )

        self.component_year.grid(row=top_offset, column=3, pady=10, padx=5)


    # returns a list of days depending on the month
    def populate_days(self) -> list:
        days=[]

        months = {
            "Jan": "31",
            "Feb": "29" if (int(self.stringvar_year.get()) % 4 == 0) else "28",
            "Mar": "31",
            "Apr": "30",
            "May": "31",
            "Jun": "30",
            "Jul": "31",
            "Aug": "31",
            "Sep": "30",
            "Oct": "31",
            "Nov": "30",
            "Dec": "31",
        }

        selected_month = months[(self.stringvar_month.get())]

        for i in range(1, int(selected_month)+1):
            days.append(str(i))

        return days


    # returns a list of month names
    def populate_months(self) -> list:
        return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


    # returns a list of years
    def populate_years(self, populate_years_with) -> list:
        if len(populate_years_with) > 0:
            return populate_years_with

        years = []

        for i in range(10):
            next_year = int(self.stringvar_year.get()) - 10 + i
            years.append(str(next_year))

        for i in range(11):
            next_year = int(self.stringvar_year.get()) + i
            years.append(str(next_year))

        return years


    # recalculates the number of days to pick from, based on the month
    def repopulate_days(self, _) -> None:
        self.component_day.configure(values=self.populate_days())


    # set the date picker back to the current date
    def reset(self) -> None:
        self.stringvar_month.set(self.today.strftime("%b"))
        self.stringvar_day.set(("{:02}").format(int(self.today.strftime("%d"))))
        self.stringvar_year.set(self.today.strftime("%Y"))
 

    # return a formatted date
    def get(self, formatting="$m $d, $y") -> str:
        m = self.stringvar_month.get()
        d = int(self.stringvar_day.get())
        y = int(self.stringvar_year.get())

        if self.show_day is False:
            return f"{m}, {y}"

        thedate = formatting.replace("$m", str(m)).replace("$d", ("{:02}").format(d)).replace("$y", str(y))

        if "%m" in formatting:
            try:
                m = ["padding_for_index", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(m)
            except Exception as e:
                print(e)

            thedate = thedate.replace("%m", ("{:02}").format(m))

        return thedate



    # set the date 
    def set(self, m: str|int = None, d: str|int = None, y: str|int = None) -> str:
        if m is None:
            m = self.today.strftime("%b")
        if d is None:
            d = self.today.strftime("%d")
        if y is None:
            y = self.today.strftime("%Y")

        if type(m) is str:
            self.stringvar_month.set(m)
        else:
            monthnames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            self.stringvar_month.set(monthnames[m])

        self.stringvar_day.set(str(d))
        self.stringvar_year.set(str(y))

        return self.get()


class TimePicker(GUI):
    def __init__(self, master=None, label_text="", left_offset=0, top_offset=0) -> None:
        """create a new GUI TimePicker object"""

        super().__init__(master, label_text, left_offset, top_offset)

        self.today = datetime.datetime.now()
        self.stringvar_hour = StringVar(value=self.today.strftime("%H"))
        self.stringvar_min = StringVar(value=self.today.strftime("%M"))

        ctk.CTkLabel(master, height=32, width=70, text="").grid(row=top_offset, column=1, pady=10, padx=5)

        def populate_upto(upperlimit):
            populate_with = []
            for i in range(upperlimit):
                populate_with.append(("{:02}").format(i))
            return populate_with

        self.component_hour = ctk.CTkComboBox(
            master,
            width=80,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            values=populate_upto(24),
            variable=self.stringvar_hour,
            font=ctk.CTkFont(family=family_medium),
        )

        self.component_hour.grid(row=top_offset, column=2, pady=10, padx=5)

        self.component_min = ctk.CTkComboBox(
            master,
            width=80,
            height=32,
            border_width=0,
            corner_radius=3,
            bg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            fg_color="#dddddd" if not globals.set_dark_theme else "#222222",
            values=populate_upto(60),
            variable=self.stringvar_min,
            font=ctk.CTkFont(family=family_medium),
        )

        self.component_min.grid(row=top_offset, column=3, pady=10, padx=5)

    # set the date picker back to the current date
    def reset(self) -> None:
        self.stringvar_hour.set(self.today.strftime("%H"))
        self.stringvar_min.set(self.today.strftime("%M"))

    # return a formatted date
    def get(self) -> str:
        hr = self.stringvar_hour.get()
        min = int(self.stringvar_min.get())

        return f"{hr}:{min}"

    # set the date 
    def set(self, hr: str|int = None, min: str|int = None) -> str:
        if hr is None:
            hr = self.today.strftime("%H")
        if min is None:
            min = self.today.strftime("%M")

        self.stringvar_hour.set(str(hr))
        self.stringvar_min.set(str(min))

        return self.get()


class PaymentSplitter(GUI):
    def __init__(self, master=None, app=None, label_text="", left_offset=0, top_offset=0) -> None:

        super().__init__(master, label_text, left_offset, top_offset)

        self.app = app

        self.pay_amount = Entry(master=master, label_text=label_text, left_offset=10, top_offset=top_offset)
        self.pay_amount.component.configure(width=152)
        self.pay_amount.stringvar.set(value="$")
        self.pay_amount.component.grid(row=top_offset, column=1, pady=10, padx=5, columnspan=2)

        self.split_quantity = ComboBox(
            master=master, 
            label_text=label_text, 
            left_offset=10, 
            top_offset=top_offset, 
            default_string = "number of months", 
            options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        )

        self.split_quantity.component.configure(width=172, command=self.dropdown_callback)
        self.split_quantity.component.grid(row=top_offset, column=3, pady=10, padx=5, columnspan=2)

        # shorten the width of the label to fit the window
        self.label.configure(width=100, text=label_text)

        # get rid of the labels that come with the Entry and DatePicker objects
        self.pay_amount.label.destroy()
        self.split_quantity.label.destroy()


    def reset(self) -> None:
        self.pay_amount.set("$")
        self.split_quantity.set("number of months")


    def get(self, part=None) -> dict[str, str]:
        payment = {
            "amount": float(0) if self.pay_amount.get().replace("$", "") == "" else float(self.pay_amount.get().replace("$", "")),
            "months": int(self.split_quantity.get())
        }

        if part == "amount":
            return payment['amount']
        if part == "months":
            return payment['months']

        return payment


    def set(self, amount, opt) -> None:
        self.pay_amount.set(amount)
        self.split_quantity.set(opt)


    def dropdown_callback(self, choice):
        self.split_payment()


    def split_payment(self) -> None:
        amount = 0 if self.pay_amount.get() == "" else float(self.pay_amount.get().replace("$", ""))
        months = int(self.split_quantity.get())
        amount_per_month = float(amount/months)
        self.pay_amount.set("${:.2f}".format(float(self.pay_amount.get().replace("$", ""))))


        # if there is nothing to pay each month, simply reset each payment widget
        if (amount_per_month == 0):
            components = self.app.get_all_components()

            for i in range(12):
                components.get(f'payment {i+1}').reset()

            return

        # set the amount to be paid each month and change up the colors a bit
        curr_month = 0
        start_point = self.app.components['payment 1'].get('date')
        ic(start_point)
        for component_name, component_obj in zip(self.app.components.keys(), self.app.components.values()):

            if re.search("payment [0-9]", component_name) is not None:
                ic(component_name)
                dt_object = datetime.datetime.strptime(start_point, "%b %d, %Y")
                dt_object = dt_object + rd.relativedelta(days=curr_month*30)

                component_obj.set(
                    "{:.2f}".format(amount_per_month), 
                    month=dt_object.strftime("%b"), 
                    date=dt_object.strftime("%d"), 
                    year=dt_object.strftime("%Y")
                )

                set_text_color = "#000000"
                component_obj.label.configure(text_color="#000000" if not globals.set_dark_theme else "#ffffff")
                component_obj.pay_amount.component.configure(fg_color="light green", text_color=set_text_color)
                component_obj.pay_date.component_day.configure(fg_color="light green", text_color=set_text_color)
                component_obj.pay_date.component_month.configure(fg_color="light green", text_color=set_text_color)
                component_obj.pay_date.component_year.configure(fg_color="light green", text_color=set_text_color)

                curr_month += 1

            if months < curr_month:
                set_fg_color = "#dddddd" if not globals.set_dark_theme else "#222222"
                set_text_color = "#aaaaaa" if not globals.set_dark_theme else "#ffffff"

                component_obj.reset()
                component_obj.label.configure(text_color="#bbb")
                component_obj.pay_amount.component.configure(fg_color=set_fg_color, text_color=set_text_color)
                component_obj.pay_date.component_day.configure(fg_color=set_fg_color, text_color=set_text_color)
                component_obj.pay_date.component_month.configure(fg_color=set_fg_color, text_color=set_text_color)
                component_obj.pay_date.component_year.configure(fg_color=set_fg_color, text_color=set_text_color)

            if curr_month == 12:
                break


class PaymentInfo(GUI):
    def __init__(self, master=None, label_text="", left_offset=0, top_offset=0) -> None:

        super().__init__(master, label_text, left_offset, top_offset)

        self.pay_amount = Entry(master=master, label_text=label_text, left_offset=10, top_offset=top_offset)
        self.pay_amount.component.configure(width=70, fg_color="#dddddd" if not globals.set_dark_theme else "#222222")
        self.pay_amount.stringvar.set(value="$")
        self.pay_amount.component.grid(row=top_offset, column=1, pady=10, padx=5, columnspan=1)

        dt_object_now = datetime.datetime.strftime(datetime.datetime.now(), "%Y")
        dt_object_max = datetime.datetime.strftime(datetime.datetime.now() + rd.relativedelta(months=12), "%Y")

        self.pay_date = DatePicker(master=master, label_text=label_text, left_offset=10, top_offset=top_offset, populate_years_with=[dt_object_now, dt_object_max])
        self.pay_date.component_day.grid(row=top_offset, column=2, pady=10, padx=5)
        self.pay_date.component_month.grid(row=top_offset, column=3, pady=10, padx=5)
        self.pay_date.component_year.grid(row=top_offset, column=4, pady=10, padx=5)

        # shorten the width of the label to fit the window
        self.label.configure(width=100, text=label_text)

        # get rid of the labels that come with the Entry and DatePicker objects
        self.pay_amount.label.destroy()
        self.pay_date.label.destroy()


    def reset(self) -> None:
        set_fg_color = "#dddddd" if not globals.set_dark_theme else "#222222"
        set_text_color = "#aaaaaa" if not globals.set_dark_theme else "#ffffff"

        self.label.configure(text_color="#000000" if not globals.set_dark_theme else "#ffffff")
        self.pay_amount.component.configure(fg_color=set_fg_color, text_color=set_text_color)
        self.pay_date.component_day.configure(fg_color=set_fg_color, text_color=set_text_color)
        self.pay_date.component_month.configure(fg_color=set_fg_color, text_color=set_text_color)
        self.pay_date.component_year.configure(fg_color=set_fg_color, text_color=set_text_color)
        self.pay_amount.stringvar.set("$")
        self.pay_date.reset()


    def get(self, part=None) -> dict[float, int]:
        payment = {
            "amount": float(0) if self.pay_amount.get().replace("$", "") == "" else float(self.pay_amount.get().replace("$", "")),
            "date": self.pay_date.get()
        }

        if part == "amount":
            return payment['amount']
        if part == "date":
            return payment['date']

        return payment


    def set(self, amount, year, month, date) -> None:
        self.pay_amount.set(f"${amount}")
        self.pay_date.set(y=year, m=month, d=date)


class AppButton():
    def __init__(self, app=None, master=None, image=None, left_offset=0, top_offset=0, app_name="", width=72, height=72, desc="", row=0) -> None:

        self.component = ctk.CTkButton(
            master=master,
            text="",
            image=image,
            border_width=0,
            corner_radius=3,
            fg_color="transparent",
            command=lambda:self.__open_app(app_name=app_name, app=app),
            width=width,
            height=height,
        ).grid(row=row, column=0, pady=10, padx=5)

        self.desc_frame = ctk.CTkFrame(
            master=master, 
            corner_radius=8, 
            border_width=1, 
            width=256, 
            height=68, 
            fg_color="#ffffff",
        )

        self.desc_frame.grid(row=row, column=1, pady=10, padx=5)

        self.desc_text = ctk.CTkLabel(master=self.desc_frame, text=app_name, width=240, wraplength=256, anchor="w", font=ctk.CTkFont(family=family_bold, weight='bold')).place(x=10, y=8)
        self.desc_text = ctk.CTkLabel(master=self.desc_frame, text=desc, width=240, wraplength=256, anchor="w", font=ctk.CTkFont(family=family_medium), text_color="#777777").place(x=10, y=32)


    def __open_app(self, app_name, app):
        owd = os.getcwd()

        try:
            os.chdir(f"{os.getcwd()}\\assets\\apps\\{app_name}\\")
            app.hide()
            check_call([f"{app_name}.exe"])
        except Exception as e:
            ErrorPopup(msg=f"Could not find {app_name} in path:\n\n{os.getcwd()}\\assets\\apps\\{app_name}\\")

        app.unhide()
        os.chdir(owd)


class ActionButton():
    def __init__(self, app=None, action="", master=None, image=None, btn_text="", btn_color="transparent", width=81, height=40, row=0, col=0, blueprint={}, subapp_name="") -> None:

        if btn_color == '#ffffff':
            btn_color = "#444444" if globals.set_dark_theme else "#ffffff"

        self.component = ctk.CTkButton(
            master=master,
            text=btn_text,
            image=image,
            border_width=0,
            corner_radius=0,
            fg_color=btn_color,
            command=lambda:handle_action(app=app, action=action, blueprint=blueprint),
            width=width,
            height=height,
            state='disabled' if 'spacer' in action else 'normal',
            hover_color="dark gray" if not globals.set_dark_theme else "#222222"
        )

        self.component.grid(row=row, column=col, pady=[20,5], padx=4)


class TabView():
    def __init__(self, master, app=None, new_tabs=[], parent_width=0, height=0, top_offset=0, tab_components=[]) -> None:

        self.tab_contents={}

        self.component = ctk.CTkTabview(
            master=master, 
            corner_radius=4, 
            bg_color="#dddddd" if not globals.set_dark_theme else "#444444",
            fg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            width=parent_width, 
            height=height, 
            segmented_button_fg_color='white', 
            segmented_button_unselected_color='#E6F1FF', 
            segmented_button_selected_color='#79b2ff', 
            text_color='black',
            border_width=1,
            border_color='#79b2ff'
        )

        self.component.grid(row=top_offset)

        if len(new_tabs) > 0:
            self.tabs = {}
            self.set_tabs(new_tabs)

        for index, each_tab in enumerate(tab_components):
            for offset, comp in enumerate(each_tab):
                comp_type = each_tab[comp]['type']

                if comp_type == "entry":
                    self.tab_contents[comp] = Entry(
                        master=self.tabs[new_tabs[index]], 
                        app=app, 
                        label_text=comp, 
                        top_offset=offset, 
                    )

                elif comp_type == "datepicker":
                    self.tab_contents[comp] = DatePicker(
                        master=self.tabs[new_tabs[index]], 
                        label_text=comp, 
                        top_offset=offset, 
                        show_day=True if each_tab[comp]['show_day'].lower() == "true" else False,
                    )

                elif comp_type == "combo":
                    self.tab_contents[comp] = ComboBox(
                        master=self.tabs[new_tabs[index]], 
                        app=app, 
                        label_text=comp, 
                        left_offset=10, 
                        top_offset=offset, 
                        options=each_tab[comp]['options'], 
                        default_option=(None if 'default' not in each_tab[comp] else each_tab[comp]['default']),
                    )

                elif comp_type == "break":
                   self.tab_contents[comp] = RowBreak(
                        master=self.tabs[new_tabs[index]], 
                        heading=each_tab[comp]['heading']
                    )

                if comp in self.tab_contents and comp_type != 'break':
                    self.tab_contents[comp].label.configure(width=180)

                app.add_component(comp, self.tab_contents[comp])


        for index, button in enumerate(self.component._segmented_button._buttons_dict.values()):
            button.configure(
                width=parent_width/len(new_tabs)*0.9, 
                height=32, 
                corner_radius=0, 
                border_width=0,
                border_color='#fff', 
                font=ctk.CTkFont(family=family_bold, weight='bold'), 
            )

    def set_tabs(self, new_tabs):
        for tab in new_tabs:
            tab_obj = self.component.add(tab)
            self.tabs[tab] = tab_obj

    def get_tabs(self):
        tabs = {}

        for tab_name in self.tabs:
            tabs[tab_name] = self.component.tab(name=tab_name) 

        return tabs

    def reset(self):
        return


class WindowView():
    def __init__(self, window_name="_window_", app=None, width=0, height=0) -> None:
        self.body = ctk.CTkToplevel()

        w = app.get_size('w')*0.5 if width == 0 else width
        h = app.get_size('h')*0.5 if height == 0 else height
        x = (app.get_size('w')/2) - (w/2)
        y = (app.get_size('h')/2) - (h/2)

        self.body.title(window_name)
        self.body.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.body.resizable(False, False)
        self.body.configure(fg_color='#ffffff' if not globals.set_dark_theme else '#444444')
        self.body.after(300, lambda:self.show())

    def show(self) -> None:
        self.body.focus()


class CellWidget():
    def __init__(self, master=None, width=0, height=0, text="", text_color="#000000", fg_color="#ffffff", info=[], font=None, type='label', command=None, hover_color=None, on_enter=None, on_leave=None) -> None:
        self.info = info
        self.width = width
        self.height = height
        self.text = text
        self.cell_type = type

        if type == 'label':
            self.cell = ctk.CTkLabel(
                master=master, 
                width=width, 
                height=height, 
                text=f'{str(text[0:22])}...{str(text[-4:])}' if len(str(text)) > 28 else text,
                text_color=text_color, 
                fg_color=fg_color, 
                bg_color='transparent',
                font=font,
            )

        elif type == 'button':
            self.cell = ctk.CTkButton(
                master=master, 
                width=width, 
                height=height, 
                text=f'{str(text[0:22])}...{str(text[-4:])}' if len(str(text)) > 28 else text, 
                text_color=text_color, 
                fg_color=fg_color, 
                bg_color='transparent',
                font=font,
                corner_radius=0,
                command=command,
                hover_color=hover_color,
            )

            if on_enter is not None or on_leave is not None:
                self.set_hover_methods(None, on_enter, on_leave)


    def set_hover_methods(self, hover_color=None, on_enter=None, on_leave=None):
        if hover_color is not None:
            self.cell.configure(hover_color=hover_color)

        self.cell.bind('<Enter>', on_enter, add='+')
        self.cell.bind('<Leave>', on_leave, add='+')

    def get_cell(self):
        return self.cell

    def get_info(self):
        return self.info

    def destroy(self):
        self.cell.destroy()


class RowWidget():
    def __init__(self, app=None, parent_frame=None, table_obj=None, row_contents=[], row_info=None, row_color="#eeeeee" , row_content_methods=[None, None, None], parent_width=0, row_number=0, mode:Literal["header", "tools", "table"]="table", is_blank = False):

        # no parent means nowhere to put this
        if parent_frame is None:
            return

        if len(row_contents) == 0:
            if is_blank:
                row_contents=[''] * len(table_obj.headers)
            else:
                row_contents=["col_0", "col_1", "col_2", "col_3", "col_4"]

        if mode == "header":
            set_fg_color = "#000000"
        elif mode == "tools":
            set_fg_color = "#ffffff" if not globals.set_dark_theme else "#444444"
        else:
            inverted_colors = {"#eeeeee": "#222222", "#dddddd": "#333333", "#ffd07a": "#cb6600", "#ffaaaa": "#660000", "#ffbbbb": "#440000"}
            set_fg_color = row_color if not globals.set_dark_theme else inverted_colors[row_color]

        self.container = ctk.CTkFrame(master=parent_frame, fg_color=set_fg_color, bg_color='transparent', border_width=0, width=parent_width, height=30)
        self.buttons = []
        self.contents = []
        self.info = {}
        self.selected = False
        self.selectable = table_obj is not None
        table_width = len(table_obj.headers) if table_obj is not None else len(row_contents)

        def highlight_row():
            if self.selectable and (row_contents != table_obj.selected_row) and is_blank is False:
                for c in self.contents:
                    c.cell.configure(fg_color='#7ac8ff')
                self.container.configure(fg_color='#7ac8ff')

        def unhighlight_row():
            if self.selectable and (row_contents != table_obj.selected_row) and is_blank is False:
                for c in self.contents:
                    c.cell.configure(fg_color=set_fg_color)
                self.container.configure(fg_color=set_fg_color)

        def select_row():
            if self.selectable and is_blank is False:
                table_obj.selected_row = row_contents
                table_obj.selected_row_info = row_info
                table_obj.update(table_obj.page)

        # setup the grid system
        for i in range(len(row_contents)+1):
            parent_frame.columnconfigure(index=i, weight=1)

        # set the number of buttons based on the mode
        # 5 in a tools row where all 5 cols are buttons
        for i in range(table_width if mode=="tools" else 0):
            self.buttons.append(
                ctk.CTkButton(
                    master=self.container,
                    text=row_contents[i],
                    text_color="#ffffff", 
                    border_width=0,
                    corner_radius=0,
                    fg_color=set_fg_color,
                    bg_color='transparent',
                    width=(parent_width-61)/table_width,
                    height=38,
                    font=ctk.CTkFont(family=family_bold, size=12, weight='bold'),
                    state="disabled" if row_contents[i] == "" else "normal",
                    command=row_content_methods[i],
                )
            )

            self.buttons[i].grid(row=0, column=i, pady=0, padx=0)

        # row_contents are placed as CTkLabel widgets only in table and header modes
        # tools mode does not place any CTkLabel widgets
        if mode != "tools":
            for i, content in enumerate(row_contents):
                self.contents.append(
                    CellWidget(
                        master=self.container, 
                        type='button' if (not is_blank and mode != 'header') else 'label',
                        width=(parent_width-61)/table_width, 
                        height=38, 
                        text=content, 
                        text_color="#ffffff" if (mode == "header" or globals.set_dark_theme) else "#000000", 
                        fg_color="#000000" if mode == "header" else set_fg_color, 
                        font=ctk.CTkFont(family=family_bold, size=12, weight='bold') if mode == "header" else ctk.CTkFont(family=family_medium, size=12),
                        command=lambda *args: select_row(),
                        on_enter=lambda *args: highlight_row(),
                        on_leave=lambda *args: unhighlight_row(),
                    )
                )

                self.contents[i].get_cell().grid(row=0, column=i + (0 if mode=="header" else 1), pady=0, padx=0)

        # place the entire container with all the stuff above
        self.container.grid(row=row_number, column=0, pady=0, padx=0)


    def set(self, row_contents=["col_0", "col_1", "col_2", "col_3", "col_4"], row_info=None):
        for index, col in enumerate(self.contents):
            col.get_cell().configure(text=row_contents[index])

        if row_info is None:
            return

        elif len(row_info) <= 0:
            self.info = {}
        else:
            self.info = row_info


    def get_cells(self) -> list:
        row_contents = []

        for col in self.contents:
            row_contents.append(col)

        return row_contents


    def get_info(self) -> list:
        return self.info


    def cleanup(self):
        for widget in self.buttons:
            widget.destroy()

        for widget in self.contents:
            widget.destroy()

        self.container.destroy()


class TableWidget():
    def __init__(self, master=None, app=None, headers:list=[], rows:list=[], parent_width=0, parent_height=0, rows_per_page=15, title_text=''):

        self.app = app
        self.rows = rows
        self.headers = headers
        self.parent_frame = master
        self.parent_width = parent_width
        self.parent_height = parent_height
        self.rows_per_page = rows_per_page
        self.rows_rendered = []
        self.next_empty_index = 0
        self.selected_row = None
        self.selected_row_info = None
        self.title_text = title_text
        self.page = 1

        for i in range(3):
            master.columnconfigure(index=i, weight=1)

        self.header_frame = ctk.CTkFrame(
            master=self.parent_frame, 
            bg_color='transparent',
            fg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            border_width=0, 
            width=self.parent_width, 
            height=self.parent_height*0.05, 
        )

        self.header = RowWidget(
            parent_frame=self.header_frame, 
            parent_width=parent_width, 
            mode="header", 
            row_contents=headers, 
            app=self.app, 
            table_obj=self
        )

        self.table_frame = ctk.CTkFrame(
            master=self.parent_frame, 
            bg_color='transparent',
            fg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            border_width=1, 
            width=self.parent_width, 
            height=self.parent_height*0.90, 
        )

        self.tools_frame = ctk.CTkFrame(
            master=self.parent_frame, 
            bg_color='transparent',
            fg_color="#ffffff" if not globals.set_dark_theme else "#444444",
            border_width=0, 
            width=self.parent_width, 
            height=self.parent_height*0.05
        )

        tools_row_contents = [''] * len(self.headers)
        tools_row_contents[0] = 'previous page'
        tools_row_contents[1] = 'next page'

        self.tools = RowWidget(
            parent_frame=self.tools_frame, 
            parent_width=self.parent_width, 
            mode="tools", 
            app=self.app, 
            row_contents=tools_row_contents, 
            row_content_methods=[
                lambda:self.navigate(page=self.page-1),
                lambda:self.navigate(page=self.page+1),
                lambda:None,
                lambda:None,
                lambda:None,
            ],
            table_obj=self
        )

        if self.title_text != '':
            self.title_frame = ctk.CTkFrame(
                master=self.parent_frame, 
                bg_color='transparent',
                fg_color="#ffffff" if not globals.set_dark_theme else "#444444",
                border_width=0, 
                width=self.parent_width, 
                height=self.parent_height*0.05, 
            )

            self.title = RowBreak(
                self.title_frame,
                heading=self.title_text,
                width=self.parent_width*0.93,
                fg_color="#808080",
                text_color="#ffffff"
            )

            self.title_frame.grid(row=0, column=1, pady=[0,0])
            self.header_frame.grid(row=1, column=1, pady=[0,0])
            self.table_frame.grid(row=2, column=1, pady=[0,0])
            self.tools_frame.grid(row=3, column=1, pady=[2,0])
            self.table_row = 2
        else:
            self.header_frame.grid(row=0, column=1, pady=[9,0])
            self.table_frame.grid(row=1, column=1, pady=[0,0])
            self.tools_frame.grid(row=2, column=1, pady=[2,0])
            self.table_row = 1

        self.reset()


    def set_custom_method(self, index, func):
        self.tools.buttons[index+2].configure(command=func)


    def navigate(self, page=0):

        set_fg_color = "#eeeeee" if not globals.set_dark_theme else "#444444"

        if (page == 1):
            self.tools.buttons[0].configure(fg_color=set_fg_color, state="disabled", text="")
            self.tools.buttons[1].configure(fg_color="#000000", state="normal", text=f"page {page+1} ▶")

        elif (page == math.ceil(len(self.rows)/self.rows_per_page)-1):
            self.tools.buttons[0].configure(fg_color="#000000", state="normal", text=f"◀ page {page-1}")
            self.tools.buttons[1].configure(fg_color=set_fg_color, state="disabled", text="")

        else:
            self.tools.buttons[0].configure(fg_color="#000000", state="normal", text=f"◀ page {page-1}")
            self.tools.buttons[1].configure(fg_color="#000000", state="normal", text=f"page {page+1} ▶")

        self.page=page
        self.update(page=page)


    def refresh(self):

        for r in self.rows_rendered:
            r.cleanup()

        self.table_frame.destroy()
        self.table_frame = ctk.CTkFrame(
            master=self.parent_frame, 
            fg_color="#ffffff", 
            border_width=1, 
            width=self.parent_width, 
            height=self.parent_height*0.90, 
        )

        self.table_frame.grid(row=self.table_row, column=1, pady=[2,0])


    def update(self, page=1):

        self.refresh()
        page_offset = self.rows_per_page * (page-1)

        for index in range(self.rows_per_page):
            if (index + page_offset) < len(self.rows):
                row_colr = "#dddddd" if ((index + page_offset) % 2 == 0) else "#eeeeee"

                if (self.rows[index + page_offset].get('row_contents') == self.selected_row):
                    row_colr = '#ffd07a'

                self.rows_rendered.append(
                    RowWidget(
                        parent_frame=self.table_frame, 
                        parent_width=self.rows[index + page_offset].get('parent_width'), 
                        row_number=index, 
                        mode=self.rows[index + page_offset].get('mode'), 
                        row_contents=self.rows[index + page_offset].get('row_contents'),
                        row_info=self.rows[index + page_offset].get('info'),
                        row_color=row_colr,
                        table_obj=self,
                        app=self.app, 
                    )
                )

                # set the next button to be active if the next row is not a blank
                if (index + page_offset) == len(self.rows) - 1:
                    self.tools.buttons[1].configure(fg_color="#ffffff" if not globals.set_dark_theme else "#444444", state="disabled", text="")
                else:
                    self.tools.buttons[1].configure(fg_color="#000000", state="normal", text=f"page {page+1} ▶")

            else:
                RowWidget(
                    parent_frame=self.table_frame, 
                    parent_width=self.parent_width, 
                    row_number=index + page_offset, 
                    row_color="#dddddd" if ((index + page_offset) % 2 == 0) else "#eeeeee",
                    is_blank = True,
                    row_contents=[''] * len(self.headers),
                    mode='table', 
                    app=self.app, 
                    table_obj=self, 
                )

                # set the next button to be active if the last row was blank
                self.tools.buttons[1].configure(fg_color="#ffffff" if not globals.set_dark_theme else "#444444", state="disabled", text="")


    def reset(self) -> None:
        for row in self.rows_rendered:
            row.cleanup()

        self.table_frame.destroy()
        self.table_frame = ctk.CTkFrame(
            master=self.parent_frame, 
            fg_color="#ffffff", 
            border_width=1, 
            width=self.parent_width, 
            height=self.parent_height*0.90, 
        )

        self.table_frame.grid(row=self.table_row, column=1, pady=[2,0])

        self.rows = []
        self.rows_rendered = []
        self.next_empty_index = 0
        self.page = 1

        for i in range(self.rows_per_page):
            RowWidget(
                parent_frame=self.table_frame,
                parent_width=self.parent_width,
                is_blank=True,
                row_color="#dddddd" if i % 2==0 else "#eeeeee",
                row_number=i,
                mode="table",
                table_obj=self,
                app=self.app, 
            )

        set_fg_color = "#ffffff" if not globals.set_dark_theme else "#444444"

        self.tools.buttons[0].configure(fg_color=set_fg_color, state="disabled", text="")

        if len(self.rows) <= self.rows_per_page:
            self.tools.buttons[1].configure(fg_color=set_fg_color, state="disabled", text="")


    def add(self, row_info=[], row_contents=[], row_index=None) -> None:
        for current_row_info, current_row_contents in zip(row_info, row_contents):

            row_to_update = row_index if row_index is not None else self.next_empty_index

            new_row = (
                {
                    'parent_frame': self.table_frame, 
                    'parent_width': self.parent_width, 
                    'row_number': row_to_update, 
                    'mode': "table", 
                    'row_contents': current_row_contents if not None else [''] * len(self.headers),
                    'row_color': "#dddddd" if (row_to_update % 2 == 0) else "#eeeeee",
                    'info': current_row_info,
                }
            )

            if row_index is None:
                self.rows.append(new_row)
                self.next_empty_index += 1
            else:
                self.rows[row_index] = new_row

        self.update(page=self.page)


    def remove(self) -> None:
        rows_after_removal = []

        for row in self.rows:
            if (row['row_contents'] != self.selected_row):
                rows_after_removal.append(row)

        self.rows = rows_after_removal
        self.next_empty_index -= 1
        self.selected_row = None
        self.selected_row_info = None
        self.tools.buttons[0].configure(fg_color="#ffffff", state="disabled", text="")
        self.navigate(page=1)
        self.update()


    def contains(self, row_info=[], compare_keys=[]):
        for row_index in range(self.next_empty_index):

            current_row_match = False

            for k in compare_keys:
                if self.rows[row_index].get('info').get(k) != row_info[k]:
                    current_row_match = False
                    break
                else:
                    current_row_match = True

            if (current_row_match):
                return (row_index, self.rows[row_index].get('info'))

        return (None, None)


    def get(self) -> list:
        return self.rows


    def get_selected_contents(self):
        return self.selected_row


    def get_selected_info(self):
        return self.selected_row_info


    def set_table_title(self, new_title=''):
        if self.title_text != '':
            self.title = RowBreak(
                self.title_frame,
                heading=new_title,
                width=self.parent_width*0.93,
                fg_color="#008127",
                text_color="#ffffff"
            )

            self.title_frame.grid(row=0, column=1, pady=[0,0])


class LoadingSplash():
    def __init__(self, master=None, opacity=1.0, splash_text="loading") -> None:

        set_color = '#ffffff' if not globals.set_dark_theme else '#444444' 
        self.opacity = opacity

        self.component = ctk.CTkFrame(
            master=master,
            height=1010,
            width=1540,
            bg_color=set_color,
            fg_color=set_color,
        )

        self.label = ctk.CTkLabel(
            master=self.component, 
            height=300, 
            width=1500, 
            text=splash_text, 
            font=ctk.CTkFont(family=family_bold, size=300), 
            text_color="#4e4e4e" if globals.set_dark_theme else "#dddddd"
        ).place(x=0, y=205)


    def show(self, task=None, waitfor=0.1):
        self.component.place(x=170, y=0)
        self.component.lift()

        if task is not None:
            import threading

            print(task)
            newThread = threading.Thread(target=task)
            newThread.start()

            while not newThread.is_alive():
                newThread.join(waitfor)


    def stop(self):
        max_opacity = int(self.opacity*100)

        for i in range(max_opacity):
            pywinstyles.set_opacity(
                widget=self.component, 
                value=self.opacity-(self.opacity-i), 
            )

            time.sleep(0.0005)

            if i == (self.opacity*100) - 1:
                self.component.destroy()
