def callback(app_components=None):

    if app_components is None:
        print("app components not provided")
        return

    service_name = (app_components.get("service").get()).lower()

    service_rates = {
        "immigration": 500.0,
        "invitation letter": 100.0,
        "affidavit": 100.0,
        "notary": 30.0,
    }

    tax_multuplier = 100
    tax_multuplier += float(app_components.get("GST percentage").get())
    tax_multuplier += float(app_components.get("PST percentage").get())
    tax_multuplier = float(tax_multuplier/100)

    price = float(app_components.get("quantity").get()) * service_rates.get(service_name) * tax_multuplier

    app_components.get("rate").set(
        f"{"${:,.2f}".format(service_rates.get(service_name))}"
    )

    app_components.get("price").set(
        f"{"${:,.2f}".format(price)}"
    )

    app_components.get("price").component.configure(fg_color="#ddd", text_color="#000")

