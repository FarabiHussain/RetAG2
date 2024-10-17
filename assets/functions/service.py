from icecream import ic

def callback(app_components=None):

    if app_components is None:
        print("app components not provided")
        return

    service_name = (app_components.get("service").get()).lower()

    service_rates = {
        "immigration": (500.0, 5.0, 0.0),
        "invitation letter": (100.0, 5.0, 7.0),
        "affidavit": (100.0, 5.0, 7.0),
        "notary": (30.0, 5.0, 7.0),
    }

    app_components.get("rate").set(f"{"${:,.2f}".format(service_rates.get(service_name)[0])}")
    app_components.get("GST percentage").set(f"{"{:,.1f}".format(service_rates.get(service_name)[1])}")
    app_components.get("PST percentage").set(f"{"{:,.1f}".format(service_rates.get(service_name)[2])}")

    tax_multuplier = 100
    tax_multuplier += float(app_components.get("GST percentage").get())
    tax_multuplier += float(app_components.get("PST percentage").get())
    tax_multuplier = float(tax_multuplier/100)

    price = float(app_components.get("quantity").get()) * service_rates.get(service_name)[0] * tax_multuplier

    app_components.get("price").set(f"{"${:,.2f}".format(price)}")
    app_components.get("price").component.configure(fg_color="#dddddd", text_color="#000000")

