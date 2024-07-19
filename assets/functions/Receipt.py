def callback(self, app_components=None, subapp_components=None):
    app_components.get('cart').tools.buttons[2].configure(fg_color='white', text_color="white", text='', state='disabled')
    app_components.get('cart').tools.buttons[3].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
    app_components.get('cart').tools.buttons[4].configure(fg_color='light gray', text_color="white", state='disabled', text="$0.00")
    self.lift_app(subapp_components)
    return