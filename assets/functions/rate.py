from Popups import ErrorPopup

def callback(app_components=None):

    if app_components is None:
        print("app components not provided")
        return

    try:
        tax_multuplier = 100
        tax_multuplier += float(app_components.get("GST percentage").get())
        tax_multuplier += float(app_components.get("PST percentage").get())
        tax_multuplier = float(tax_multuplier/100)

        price = float(app_components.get("quantity").get()) * float(app_components.get("rate").get().strip().replace("$","")) * tax_multuplier

        app_components.get("price").set(f"{"${:,.2f}".format(price)}")
        app_components.get("price").component.configure(fg_color="light green", text_color="#000000")

        app_components.get("rate").component.configure(fg_color="light gray", text_color="#000000")

    except Exception as e:
        app_components.get("price").set("")
        app_components.get("price").component.configure(fg_color="#dddddd", text_color="#aaaaaa")
        ErrorPopup(e)

