def callback(app_components=None):

    if app_components is None:
        print("app components not provided")
        return

    try:
        first_name = app_components.get("client 1 first name").get().strip()
        last_name = app_components.get("client 1 last name").get().strip()
        full_name = f"{first_name} {last_name}"

        app_components.get("client name").set(full_name)
        app_components.get("client name").component.configure(fg_color="light green", text_color="#000000")

    except Exception as e:
        app_components.get("client name").set("")
        app_components.get("client name").component.configure(fg_color="#dddddd", text_color="#aaaaaa")
