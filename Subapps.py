import customtkinter as ctk
from GUI import *
from reader import import_function

class Subapp():
    def __init__(self, subapp_components=None, blueprint=None, app=None, imgs=None, subapp_name="Subapp", button_position=0, columns_weights=[1,1,1]) -> None:

        self.frame = subapp_components[button_position]['frame']
        self.button = subapp_components[button_position]['button']
        self.button.configure(command=lambda:self.lift_app(subapp_components))

        self.subapp_name = subapp_name
        self.button.place(x=0, y=(50*button_position)+10)
        self.blueprint = blueprint

        self.render_app(self.frame, blueprint, app, imgs, columns_weights)
        self.init_app(app, subapp_components)

        if button_position == 0:
            self.lift_app(subapp_components)


    def init_app(self, app, subapp_components):
        if 'init_app' in self.blueprint:
            ic(self.subapp_name)
            function_path = self.blueprint['init_app']

            if not os.path.exists(function_path):
                setup_function = import_function(function_path, "callback")
                setup_function(self, app.get_all_components(), subapp_components)


    def lift_app(self, subapp_components):
        for curr_subapp in subapp_components:
            curr_subapp['button'].configure(text_color="white", fg_color="gray")

        self.button.configure(text_color="black", fg_color="white")
        self.frame.lift()


    def render_app(self, frame, blueprint, app, imgs, columns_weights):
        column_widths = [0, 460, 990, 1380]

        self.page_columns = [
            ctk.CTkFrame(master=frame, fg_color="white", height=728, width=460, border_width=0),
            ctk.CTkFrame(master=frame, fg_color="white", height=728, width=460, border_width=0),
            ctk.CTkFrame(master=frame, fg_color="white", height=728, width=460, border_width=0),
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

            elif specs['type'] == "table":
                new_component = TableWidget(
                    master=self.page_columns[specs['column']], 
                    headers=specs['headers'],
                    parent_width=column_widths[blueprint['column_weights'][specs['column']]]
                )

            app.add_component(label, new_component)

            offset += 1

        btn_frame = ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=50, width=480)
        btn_frame.place(x=25, y=800)

        if "buttons" in blueprint.keys():
            for index, btn in enumerate(blueprint.get("buttons")):
                ActionButton(master=btn_frame, action=btn, app=app, blueprint=blueprint, image=imgs.get(f"{btn}.png"), btn_color=blueprint['buttons'][btn], row=0, col=index)

        if "callbacks" in blueprint.keys():
            for index, component_name in enumerate(blueprint.get("callbacks")):
                current_component = app.get_all_components().get(component_name)
                current_callback = import_function(blueprint['callbacks'][component_name], "callback")

                current_component.add_callback(component_name=component_name, app=app, callback=current_callback)

