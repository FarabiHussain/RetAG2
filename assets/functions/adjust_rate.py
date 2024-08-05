from Popups import ErrorPopup

def callback(app=None):
    try:
        total = float(app.components.get("price").get().strip().replace("$", ""))
        qty = float(app.components.get("quantity").get())
        taxes = (float(app.components.get("GST percentage").get()) + float(app.components.get("PST percentage").get())) / 100

        rate = 0
        rate += (total / (1 + taxes)) / qty

        app.components.get("rate").set(f"{"${:,.2f}".format(rate)}")
        app.components.get("price").set(f"{"${:,.2f}".format(total)}")

        app.components.get("rate").component.configure(fg_color="light green", text_color="#000000")
        app.components.get("price").component.configure(fg_color="light gray", text_color="#000000")

    except Exception as e:
        ErrorPopup(e)