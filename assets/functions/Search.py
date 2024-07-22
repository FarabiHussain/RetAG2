from icecream import ic

def callback(self, app=None, subapp_components=None):
    app.components.get('search results').tools.buttons[2].configure(fg_color='white', text_color="white", text='', state='disabled')
    app.components.get('search results').tools.buttons[3].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
    app.components.get('search results').tools.buttons[4].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
    app.components.get('search case ID').component.configure(fg_color="light green", text_color="#000")

    return