import globals
from Database import Database
from Popups import ErrorPopup, PromptPopup
from icecream import ic


def _add(app, db, collection_name, params):
    if PromptPopup(f"Add staff member {params['new_name']}?").get():
        collection_name.insert_one({"name": params['new_name'], "show": True})

        db.init_staff_names()
        app.components["staff name"].add_options(globals.staff_names)

    db.client.close()


def _delete(app, db, collection_name, params):
    if PromptPopup(f"Delete staff member {params['selected_staff']}?").get():
        collection_name.delete_one({"name": params['selected_staff']})

        db.init_staff_names()
        app.components["staff name"].add_options(globals.staff_names)
        params['staffpicker'].add_options(globals.staff_names)
        params['staffpicker'].set('click to select')

    db.client.close()


def _edit(app, db, collection_name, params):
    if PromptPopup(f"Rename {params['selected_staff']} to {params['new_name']}?").get():
        collection_name.update_one(
            {"name": params['selected_staff']},
            {"$set": {"name": params['new_name'],}},
        )

        db.init_staff_names()
        app.components["staff name"].add_options(globals.staff_names)
        params['staffpicker'].add_options(globals.staff_names)
        params['staffpicker'].set(params['new_name'])

    db.client.close()


def callback(app=None, *args, **kwargs):
    if app is None:
        print("app components not provided")
        return

    params = args[0]

    if params['new_name'] == "Select":
        ErrorPopup("Please select an employee")
        return

    db = Database()
    dbname = db.get_database()
    collection_name = dbname["staff"]
    
    OPERATIONS = {
        "add": lambda: _add(app, db, collection_name, params),
        "delete": lambda: _delete(app, db, collection_name, params),
        "edit": lambda: _edit(app, db, collection_name, params),
    }

    OPERATIONS.get(params['operation_type'])()
