# from RenderFont import RenderFont
import customtkinter as ctk
from Img import *
from GUI import *
from actions import search_attendance, search_payments_button
from reader import import_function

class Subapp():
    def __init__(self, subapp_components=None, blueprint=None, app=None, imgs=None, subapp_name="Subapp", button_position=0, columns_weights=[1,1,1]) -> None:

        if (subapp_name.lower() == "attendance"):
            callback_function = search_attendance
        elif (subapp_name.lower() == "payment dates"):
            callback_function = search_payments_button
        else:
            callback_function = None

        self.frame = subapp_components[button_position]['frame']
        self.button = subapp_components[button_position]['button']
        self.button.configure(command=lambda:self.lift_app(subapp_components, callback_function, app))
        self.subapp_name = subapp_name
        self.blueprint = blueprint

        if button_position == 0:
            lg_img = Img("lg")

            ctk.CTkButton(
                master=app.root,
                text='',
                border_width=0,
                corner_radius=0,
                fg_color="black",
                width=170,
                height=70,
                hover_color='black',
                image=lg_img.get("a&m.png")
            ).place(x=0, y=1)

        if subapp_name.lower() != 'init':
            self.button.place(x=0, y=(70*(button_position+1)) + 12 + (1*button_position))

        app.subapp_components[subapp_name] = subapp_components
        self.render_app(self.frame, blueprint, app, imgs, columns_weights, subapp_components)

        if button_position == 0:
            self.lift_app(subapp_components)


    def init_app(self, app, subapp_components, function_path):
        function_path = function_path

        if not os.path.exists(function_path):
            setup_function = import_function(function_path, "callback")
            setup_function(self, app, subapp_components)


    def reset(self):
        return


    def lift_app(self, subapp_components=[], callback_function=None, app=None):
        for curr_subapp in subapp_components:
            curr_subapp['button'].configure(text_color="white", fg_color="gray", hover_color="light gray", state='normal')

        self.button.configure(text_color="black", fg_color="white", hover_color="white", state='disabled')
        self.frame.lift()

        if callback_function is not None and app is not None:
            callback_function(app)


    def render_app(self, frame, blueprint, app, imgs, columns_weights, subapp_components, master=None):
        column_widths = [0, 460, 990, 1380]

        if master is None:
            self.page_columns = [
                ctk.CTkFrame(master=frame, fg_color="#ffffff", height=728, width=460, border_width=0),
                ctk.CTkFrame(master=frame, fg_color="#ffffff", height=728, width=460, border_width=0),
                ctk.CTkFrame(master=frame, fg_color="#ffffff", height=728, width=460, border_width=0),
            ]

            if columns_weights == [1,1,1]:
                self.page_columns[0].place(x=25, y=25)
                self.page_columns[1].place(x=505, y=25)
                self.page_columns[2].place(x=985, y=25)

            elif columns_weights == [1,2,0] or columns_weights == [1,0,2]:
                self.page_columns[1].configure(width=940)
                self.page_columns[0].place(x=25, y=25)
                self.page_columns[1].place(x=505, y=25)

            elif columns_weights == [2,1,0] or columns_weights == [2,0,1]:
                self.page_columns[0].configure(width=940)
                self.page_columns[0].place(x=25, y=25)
                self.page_columns[1].place(x=965, y=25)

            elif columns_weights == [1,0,0] or columns_weights == [2,0,0] or columns_weights == [3,0,0]:
                self.page_columns[0].configure(width=1300)
                self.page_columns[0].place(x=25, y=25)

        offset = 0

        for specs, label in zip(blueprint.values(), blueprint.keys()):

            new_component = None

            if 'type' not in specs:
                continue

            elif specs['type'] == "entry":
                new_component = Entry(
                    master=self.page_columns[specs['column']], 
                    app=app, 
                    label_text=label, 
                    left_offset=10, 
                    top_offset=offset, 
                    default_text=(None if 'default' not in specs else specs['default']),
                )

            elif specs['type'] == "textbox":
                new_component = TextBox(
                    master=self.page_columns[specs['column']], 
                    app=app, 
                    label_text=label, 
                    left_offset=0, 
                    lines=specs['lines'], 
                    height=specs['box_height'], 
                    instructions_text=specs['instructions_text'], 
                    parent_width=column_widths[blueprint['column_weights'][specs['column']]], 
                    top_offset=offset, 
                )

                offset += 1

            elif specs['type'] == "datepicker":
                new_component = DatePicker(
                    master=self.page_columns[specs['column']], 
                    label_text=label, 
                    left_offset=10, 
                    top_offset=offset, 
                    show_day=True if specs['show_day'].lower() == "true" else False,
                )

            elif specs['type'] == "paymentsplitter":
                new_component = PaymentSplitter(
                    master=self.page_columns[specs['column']], 
                    label_text=label, 
                    left_offset=10, 
                    top_offset=offset, 
                    app=app,
                )

            elif specs['type'] == "paymentinfo":
                new_component = PaymentInfo(
                    master=self.page_columns[specs['column']], 
                    label_text=label, 
                    left_offset=10, 
                    top_offset=offset,
                )

            elif specs['type'] == "combo":
                new_component = ComboBox(
                    master=self.page_columns[specs['column']], 
                    app=app, 
                    label_text=label, 
                    left_offset=10, 
                    top_offset=offset, 
                    options=specs['options'], 
                    default_option=(None if 'default' not in specs else specs['default']),
                )

            elif specs['type'] == "break":
                new_component = RowBreak(
                    master=self.page_columns[specs['column']], 
                    left_offset=10, 
                    top_offset=offset, 
                    heading=specs['heading'],
                )

            elif specs['type'] == "rowbutton":
                new_component = RowButton(
                    master=self.page_columns[specs['column']], 
                    app=app, 
                    left_offset=10, 
                    top_offset=offset, 
                    label=specs['label'],
                    method=specs['method']
                )

            elif specs['type'] == "table":
                new_component = TableWidget(
                    master=self.page_columns[specs['column']], 
                    headers=specs['headers'],
                    parent_width=column_widths[blueprint['column_weights'][specs['column']]],
                    app=app, 
                    title_text=('' if 'title_text' not in specs else specs['title_text'])
                )

            elif specs['type'] == "tabview":
                new_component = TabView(
                    master=self.page_columns[specs['column']], 
                    app=app, 
                    parent_width=column_widths[blueprint['column_weights'][specs['column']]], 
                    height=670, 
                    new_tabs=specs['tabs'], 
                    tab_components=specs['tab_components'], 
                    top_offset=offset, 
                )

            app.add_component(label, new_component)

            offset += 1

        btn_frame = ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=50, width=480)
        btn_frame.place(x=25, y=800)

        if "buttons" in blueprint.keys():
            app.buttons[self.subapp_name] = {}
            for index, btn in enumerate(blueprint.get("buttons")):
                app.buttons[self.subapp_name][btn] = ActionButton(
                    master=btn_frame, 
                    action=btn, 
                    app=app, 
                    blueprint=blueprint, 
                    image=imgs.get(f"{btn}.png"), 
                    btn_color=blueprint['buttons'][btn], 
                    row=0, 
                    col=index, 
                    subapp_name=self.subapp_name, 
                )

        if "callbacks" in blueprint.keys():
            for index, component_name in enumerate(blueprint.get("callbacks")):
                current_component = app.get_all_components().get(component_name)
                current_callback = import_function(blueprint['callbacks'][component_name], "callback")

                current_component.add_callback(component_name=component_name, app=app, callback=current_callback)

        for blueprint_key in blueprint.keys():
            if "init" in blueprint_key:
                self.init_app(app, subapp_components, blueprint[blueprint_key])


