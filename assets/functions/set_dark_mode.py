from icecream import ic
from Database import Database
from Popups import InfoPopup
import os

def callback(app_components=None):

    if app_components is None:
        print("app components not provided")
        return
    
    ic(app_components['dark theme'].get())

    db = Database()
    db.cursor.execute(
        f'''
            UPDATE theme
            SET dark_mode = {0 if app_components['dark theme'].get() == "off" else 1}
            WHERE device_name = '{os.environ['COMPUTERNAME']}'
        '''
    )
    db.commit()

    InfoPopup(f'Dark theme will be set to {app_components['dark theme'].get()} next time RETAG is opened.')

    db.close()