import customtkinter as ctk
from Path import *
from Img import *
from GUI import *
from App import *
from Subapps import *
from reader import *

imgs = Img("md")
app = App()
app.set_size(w=1600, h=1000)

blueprint = app.get_blueprint()

frames = [
    ctk.CTkFrame(master=app.root, fg_color="white", border_width=3, height=1010, width=1440, corner_radius=0, border_color="red"),
    ctk.CTkFrame(master=app.root, fg_color="white", border_width=3, height=1010, width=1440, corner_radius=0, border_color="blue"),
    ctk.CTkFrame(master=app.root, fg_color="white", border_width=3, height=1010, width=1440, corner_radius=0, border_color="green"),
]

frames[0].place(x=170, y=0)

Retainer(frames[0], frames, blueprint, app, imgs)
Authorization(frames[1], frames, blueprint, app, imgs)
# Receipt(frames[2], frames, blueprint, app, imgs)


if '--import' in sys.argv:
    import_recent(app)

app.start()
