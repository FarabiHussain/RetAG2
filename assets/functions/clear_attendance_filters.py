from actions import search_attendance

def callback(app=None):
    if app is None:
        print("app components not provided")
        return

    search_attendance(app)