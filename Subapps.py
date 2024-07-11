import customtkinter as ctk
from GUI import *

class Authorization():
    def __init__(self, frame, frames_list, blueprint, app, imgs) -> None:
        self.button = ctk.CTkButton(
            master=app.root,
            text_color="black",
            text="Authorization",
            border_width=0,
            corner_radius=2,
            fg_color="lightgray",
            command=lambda:self.render_app(frame, frames_list, blueprint, app, imgs),
            width=170,
            height=70,
        )
        
        self.button.place(x=0, y=90)


    def render_app(self, frame, frames_list, blueprint, app, imgs):



        self.button.configure(text_color="white", fg_color="gray")

        self.auth_columns = [
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
            ctk.CTkFrame(master=frame, fg_color="white", border_width=3, height=850, width=430, corner_radius=0),
        ]

        self.auth_columns[0].place(x=25, y=25)
        self.auth_columns[1].place(x=505, y=25)
        self.auth_columns[2].place(x=975, y=25)

        offset = 0

        for specs, label in zip(blueprint['Authorization'].values(), blueprint['Authorization'].keys()):

            new_component = None

            if specs['type'] == "entry":
                new_component = Entry(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
            elif specs['type'] == "datepicker":
                new_component = DatePicker(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, show_day=specs['show_day'])
            elif specs['type'] == "paymentinfo":
                new_component = PaymentInfo(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
            elif specs['type'] == "combo":
                new_component = ComboBox(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, options=specs['options'])

            app.add_component(label, new_component)

            offset += 1

        btn_frame = ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=50, width=480)
        btn_frame.place(x=25, y=900)

        ActionButton(master=btn_frame, action="reset", app=app, image=imgs.get("reset.png"), btn_color="red", row=0, col=0)
        ActionButton(master=btn_frame, action="create", app=app, image=imgs.get("create.png"), btn_color="blue", row=0, col=1)
        ActionButton(master=btn_frame, action="decrypt", app=app, image=imgs.get("decrypt.png"), btn_color="gray", row=0, col=2)
        ActionButton(master=btn_frame, action="import", app=app, image=imgs.get("import.png"), btn_color="gray", row=0, col=3)
        ActionButton(master=btn_frame, action="output", app=app, image=imgs.get("output.png"), btn_color="gray", row=0, col=4)
        ActionButton(master=btn_frame, action="test", app=app, image=imgs.get("test.png"), btn_color="lightgray", row=0, col=5)


class Retainer():
    def __init__(self, frame, frames_list, blueprint, app, imgs) -> None:
        self.button = ctk.CTkButton(
            master=app.root,
            text_color="black",
            text="Retainer",
            border_width=0,
            corner_radius=2,
            fg_color="lightgray",
            command=lambda:self.render_app(frame, frames_list, blueprint, app, imgs),
            width=170,
            height=70,
        )

        self.button.place(x=0, y=20)

    def render_app(self, frame, frames_list, blueprint, app, imgs):



        self.button.configure(text_color="white", fg_color="gray")

        self.auth_columns = [
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
            ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
            ctk.CTkFrame(master=frame, fg_color="white", border_width=3, height=850, width=430, corner_radius=0),
        ]

        self.auth_columns[0].place(x=25, y=25)
        self.auth_columns[1].place(x=505, y=25)
        self.auth_columns[2].place(x=975, y=25)

        offset = 0

        for specs, label in zip(blueprint['Authorization'].values(), blueprint['Authorization'].keys()):

            new_component = None

            if specs['type'] == "entry":
                new_component = Entry(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
            elif specs['type'] == "datepicker":
                new_component = DatePicker(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, show_day=specs['show_day'])
            elif specs['type'] == "paymentinfo":
                new_component = PaymentInfo(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
            elif specs['type'] == "combo":
                new_component = ComboBox(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, options=specs['options'])

            app.add_component(label, new_component)

            offset += 1

        btn_frame = ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=50, width=480)
        btn_frame.place(x=25, y=900)

        ActionButton(master=btn_frame, action="reset", app=app, image=imgs.get("reset.png"), btn_color="red", row=0, col=0)
        ActionButton(master=btn_frame, action="create", app=app, image=imgs.get("create.png"), btn_color="blue", row=0, col=1)
        ActionButton(master=btn_frame, action="decrypt", app=app, image=imgs.get("decrypt.png"), btn_color="gray", row=0, col=2)
        ActionButton(master=btn_frame, action="import", app=app, image=imgs.get("import.png"), btn_color="gray", row=0, col=3)
        ActionButton(master=btn_frame, action="output", app=app, image=imgs.get("output.png"), btn_color="gray", row=0, col=4)
        ActionButton(master=btn_frame, action="test", app=app, image=imgs.get("test.png"), btn_color="lightgray", row=0, col=5)


# class Receipt():
#     def __init__(self, frame, blueprint, app, imgs) -> None:
#         self.button = ctk.CTkButton(
#             master=app.root,
#             text_color="black",
#             text="Receipts",
#             border_width=0,
#             corner_radius=2,
#             fg_color="lightgray",
#             command=lambda:self.render_app(frame, blueprint, app, imgs),
#             width=170,
#             height=70,
#         )

#         self.button.place(x=0, y=160)
#         self.is_rendered = False

#     def render_app(self, frame, blueprint, app, imgs):
#         self.button.configure(text_color="white", fg_color="gray")

#         self.auth_columns = [
#             ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
#             ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=850, width=460, corner_radius=0),
#             ctk.CTkFrame(master=frame, fg_color="white", border_width=3, height=850, width=430, corner_radius=0),
#         ]

#         self.auth_columns[0].place(x=25, y=25)
#         self.auth_columns[1].place(x=505, y=25)
#         self.auth_columns[2].place(x=975, y=25)

#         offset = 0

#         for specs, label in zip(blueprint['Authorization'].values(), blueprint['Authorization'].keys()):

#             new_component = None

#             if specs['type'] == "entry":
#                 new_component = Entry(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
#             elif specs['type'] == "datepicker":
#                 new_component = DatePicker(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, show_day=specs['show_day'])
#             elif specs['type'] == "paymentinfo":
#                 new_component = PaymentInfo(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset)
#             elif specs['type'] == "combo":
#                 new_component = ComboBox(master=self.auth_columns[specs['column']], label_text=label, left_offset=10, top_offset=offset, options=specs['options'])

#             app.add_component(label, new_component)

#             offset += 1

#         btn_frame = ctk.CTkFrame(master=frame, fg_color="white", border_width=0, height=50, width=480)
#         btn_frame.place(x=25, y=900)

#         ActionButton(master=btn_frame, action="reset", app=app, image=imgs.get("reset.png"), btn_color="red", row=0, col=0)
#         ActionButton(master=btn_frame, action="create", app=app, image=imgs.get("create.png"), btn_color="blue", row=0, col=1)
#         ActionButton(master=btn_frame, action="decrypt", app=app, image=imgs.get("decrypt.png"), btn_color="gray", row=0, col=2)
#         ActionButton(master=btn_frame, action="import", app=app, image=imgs.get("import.png"), btn_color="gray", row=0, col=3)
#         ActionButton(master=btn_frame, action="output", app=app, image=imgs.get("output.png"), btn_color="gray", row=0, col=4)
#         ActionButton(master=btn_frame, action="test", app=app, image=imgs.get("test.png"), btn_color="lightgray", row=0, col=5)

#         self.is_rendered = True


