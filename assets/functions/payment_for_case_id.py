from reader import read_case_id 

def callback(app_components=None):
    try:
        app_components.get('payment for case ID').component.configure(fg_color="light green", text_color="#000")
        app_components.get('payment for case ID').set(app_components.get('case ID').get())
        app_components.get('case ID').component.configure(fg_color="light green", text_color="#000")
    except Exception as e:
        print(e)
