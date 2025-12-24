from actions import set_attendance

def callback(app=None):
    if app is None:
        print("app components not provided")
        return

    set_attendance(app)