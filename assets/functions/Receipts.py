from icecream import ic

def callback(self, app=None, subapp_components=None):
    app.components.get('cart').tools.buttons[3].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
    app.components.get('cart').tools.buttons[4].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
