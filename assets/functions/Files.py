from icecream import ic

def callback(self, app=None, subapp_components=None):
    for i in range(5):
        app.components.get('search results').tools.buttons[i].configure(fg_color='white', text_color="white", text='', state='disabled')

    app.components.get('search case ID').component.configure(fg_color="light green", text_color="#000")
    app.components.get('search case ID').set('000000-000')

    return