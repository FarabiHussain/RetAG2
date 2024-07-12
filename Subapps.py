import customtkinter as ctk
from GUI import *

class Subapp():
    def __init__(self, subapp_components=None, blueprint=None, app=None, imgs=None, subapp_name="Subapp", button_position=0) -> None:

        self.frame = subapp_components[button_position]['frame']
        self.button = subapp_components[button_position]['button']
        self.button.configure(command=lambda:self.lift_app(subapp_components))

        self.subapp_name = subapp_name
        self.button.place(x=0, y=(50*button_position)+10)
        self.blueprint = blueprint

        self.render_app(self.frame, blueprint, app, imgs)

        if button_position == 0:
            self.lift_app(subapp_components)


    def lift_app(self, subapp_components):
        for curr_subapp in subapp_components:
            curr_subapp['button'].configure(text_color="white", fg_color="gray")

        self.button.configure(text_color="black", fg_color="white")
        self.frame.lift()


    def render_app(self, frame, blueprint, app, imgs):
        self.auth_columns = [
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
        ]

        self.auth_columns[0].place(x=25, y=25)
        self.auth_columns[1].place(x=505, y=25)
        self.auth_columns[2].place(x=985, y=25)

        offset = 0

        for specs, label in zip(blueprint.values(), blueprint.keys()):

            new_component = None

            if specs['type'] == "entry":
                new_component = Entry(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
            elif specs['type'] == "datepicker":
                new_component = DatePicker(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, show_day=True if specs['show_day'].lower() == "true" else False)
            elif specs['type'] == "paymentsplitter":
                new_component = PaymentSplitter(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, app=app)
            elif specs['type'] == "paymentinfo":
                new_component = PaymentInfo(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
            elif specs['type'] == "combo":
                new_component = ComboBox(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, options=specs['options'], default_option=(None if 'default' not in specs else specs['default']))
            elif specs['type'] == "break":
                new_component = RowBreak(master=self.auth_columns[specs['column']], left_offset=10, top_offset=offset, heading=specs['heading'])

            app.add_component(label, new_component)

            offset += 1

        btn_frame = ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=50, width=480)
        btn_frame.place(x=25, y=800)

        ActionButton(master=btn_frame, action="reset", app=app, image=imgs.get("reset.png"), btn_color="red", row=0, col=0)
        ActionButton(master=btn_frame, action="retainer", app=app, image=imgs.get("retainer.png"), btn_color="dark blue", row=0, col=1)
        ActionButton(master=btn_frame, action="payments", app=app, image=imgs.get("payments.png"), btn_color="dark blue", row=0, col=2)
        ActionButton(master=btn_frame, action="conduct", app=app, image=imgs.get("conduct.png"), btn_color="dark green", row=0, col=3)
        ActionButton(master=btn_frame, action="decrypt", app=app, image=imgs.get("decrypt.png"), btn_color="gray", row=0, col=4)
        ActionButton(master=btn_frame, action="output", app=app, image=imgs.get("output.png"), btn_color="gray", row=0, col=5)
        ActionButton(master=btn_frame, action="test", app=app, image=imgs.get("test.png"), btn_color="lightgray", row=0, col=6)

