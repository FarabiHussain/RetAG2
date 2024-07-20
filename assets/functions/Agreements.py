from reader import read_case_id 

def callback(self, app=None, subapp_components=None):
    try:
        app.components.get('case ID').set(read_case_id())
        app.components.get('case ID').component.configure(fg_color="light green", text_color="#000")
    except Exception as e:
        print(e)
