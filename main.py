import customtkinter as ctk
from Path import *
from Img import *
from GUI import *
from App import *
from Subapps import *
from reader import *

imgs = Img("md")
app = App()
app.set_size(w=1640, h=900)

blueprint = app.get_blueprint()
subapp_components = []

# first initialize the subapp frames and buttons so that we can control their visibilty and active status
for subapp_name in blueprint:

    new_subapp = {"name": subapp_name, "frame": None, "button": None}

    new_subapp['frame'] = ctk.CTkFrame(master=app.root, fg_color="white", border_width=0, height=1010, width=1540, corner_radius=0, border_color="gray")
    new_subapp['frame'].place(x=170, y=0)

    new_subapp['button'] = ctk.CTkButton(
        master=app.root,
        text_color="black",
        text=subapp_name.upper(),
        border_width=0,
        corner_radius=0,
        fg_color="lightgray",
        width=170,
        height=50,
        font=ctk.CTkFont(family="Roboto Bold")
    )

    subapp_components.append(new_subapp)

# use the above components and render each subapp
for i, subapp_name in enumerate(blueprint):
    subapp_components[i]['subapp_obj'] = Subapp(subapp_components=subapp_components, blueprint=blueprint[subapp_name], subapp_name=subapp_name, app=app, imgs=imgs, button_position=i, columns_weights=blueprint[subapp_name]['column_weights'])


def test_fill():
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
    app.components['client name'].set(legal_name)


    total_amount = 0
    total_months = random.randint(1,12)
    for i in range(total_months):
        total_amount += 100
        app.components[f'payment {i+1}'].set("100", "2025", "Jan", i+1)

    app.components['application fee'].set(f"${total_amount}", total_months)


# for s in subapp_components:
#     if s.get("name") == "Receipt":
#         s['subapp_obj'].lift_app(subapp_components)

test_fill()

app.start()
